import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class MarkovConfig:
    """Configuration for Markov model"""
    time_horizon: int  # years
    cycle_length: int = 1  # years
    discount_rate_costs: float = 0.03
    discount_rate_outcomes: float = 0.03
    cohort_size: int = 1000


@dataclass
class StrategyResults:
    """Results for a single strategy"""
    total_cost: float
    total_qalys: float
    life_years: float
    state_trace: List[List[float]]  # [cycle][state]


@dataclass
class ComparisonResults:
    """Comparison between two strategies"""
    strategy_a: StrategyResults
    strategy_b: StrategyResults
    delta_cost: float
    delta_qaly: float
    icer: float
    is_dominated: bool
    conclusion: str


class MarkovModel:
    """
    Three-state Markov model for pharmacoeconomic evaluation
    States: Stable (S), Progression (P), Death (D)
    """

    def __init__(self, config: MarkovConfig):
        self.config = config
        self.states = ["Stable", "Progression", "Death"]
        self.n_states = len(self.states)
        self.n_cycles = config.time_horizon // config.cycle_length

    def build_transition_matrix(self, params: Dict) -> np.ndarray:
        """
        Build transition probability matrix

        Matrix structure (From rows -> To columns):
                   Stable  Progression  Death
        Stable       p_ss      p_sp       p_sd
        Progression  0.00      p_pp       p_pd
        Death        0.00      0.00       1.00
        """
        p_sp = params.get("prob_s_to_p", 0.10)
        p_sd = params.get("prob_s_to_d", 0.02)
        p_pd = params.get("prob_p_to_d", 0.15)

        # Validate probabilities
        if p_sp + p_sd > 1.0:
            raise ValueError("Transition probabilities from Stable exceed 1.0")

        p_ss = 1.0 - p_sp - p_sd  # Probability of staying stable
        p_pp = 1.0 - p_pd  # Probability of staying in progression

        matrix = np.array([
            [p_ss, p_sp, p_sd],  # From Stable
            [0.00, p_pp, p_pd],  # From Progression
            [0.00, 0.00, 1.00],  # From Death (absorbing state)
        ])

        return matrix

    def run_cohort_simulation(
        self,
        transition_matrix: np.ndarray,
        initial_distribution: np.ndarray = None
    ) -> np.ndarray:
        """
        Simulate cohort through Markov model

        Returns:
            trace: np.ndarray of shape (n_cycles + 1, n_states)
        """
        if initial_distribution is None:
            # All patients start in Stable state
            initial_distribution = np.array([self.config.cohort_size, 0, 0])

        trace = np.zeros((self.n_cycles + 1, self.n_states))
        trace[0] = initial_distribution

        # Run Markov process
        for cycle in range(1, self.n_cycles + 1):
            trace[cycle] = trace[cycle - 1] @ transition_matrix

        return trace

    def calculate_outcomes(
        self,
        trace: np.ndarray,
        params: Dict
    ) -> StrategyResults:
        """
        Calculate costs and QALYs from state trace
        """
        # Extract cost parameters
        cost_drug = params.get("cost_drug", 0)
        cost_state_s = params.get("cost_state_s", 200)
        cost_state_p = params.get("cost_state_p", 4500)

        # Extract utility parameters
        utility_stable = params.get("utility_stable", 0.85)
        utility_progression = params.get("utility_progression", 0.50)

        total_cost = 0.0
        total_qalys = 0.0
        total_life_years = 0.0

        for cycle in range(1, self.n_cycles + 1):
            # Discount factor
            discount_factor_cost = 1 / ((1 + self.config.discount_rate_costs) ** cycle)
            discount_factor_qaly = 1 / ((1 + self.config.discount_rate_outcomes) ** cycle)

            # Number of patients in each state
            n_stable = trace[cycle][0]
            n_progression = trace[cycle][1]
            n_death = trace[cycle][2]
            n_alive = n_stable + n_progression

            # Costs for this cycle
            cycle_cost = (
                (n_stable + n_progression) * cost_drug +  # Drug cost for alive patients
                n_stable * cost_state_s +  # Monitoring cost stable
                n_progression * cost_state_p  # Event cost progression
            )
            total_cost += cycle_cost * discount_factor_cost

            # QALYs for this cycle
            cycle_qalys = (
                n_stable * utility_stable +
                n_progression * utility_progression
            )
            total_qalys += cycle_qalys * discount_factor_qaly

            # Life years
            total_life_years += n_alive

        # Convert life years to actual years (divide by cohort size)
        total_life_years = total_life_years / self.config.cohort_size

        return StrategyResults(
            total_cost=round(total_cost, 2),
            total_qalys=round(total_qalys / self.config.cohort_size, 4),
            life_years=round(total_life_years, 2),
            state_trace=trace.tolist()
        )

    def compare_strategies(
        self,
        params_a: Dict,
        params_b: Dict
    ) -> ComparisonResults:
        """
        Compare two treatment strategies (Drug A vs Drug B)
        """
        # Run simulations for both strategies
        matrix_a = self.build_transition_matrix(params_a)
        trace_a = self.run_cohort_simulation(matrix_a)
        results_a = self.calculate_outcomes(trace_a, params_a)

        matrix_b = self.build_transition_matrix(params_b)
        trace_b = self.run_cohort_simulation(matrix_b)
        results_b = self.calculate_outcomes(trace_b, params_b)

        # Calculate incremental values
        delta_cost = results_a.total_cost - results_b.total_cost
        delta_qaly = results_a.total_qalys - results_b.total_qalys

        # Calculate ICER
        if delta_qaly == 0:
            icer = float('inf')
            is_dominated = delta_cost > 0
        else:
            icer = delta_cost / delta_qaly
            is_dominated = delta_cost > 0 and delta_qaly < 0

        # Determine conclusion based on WTP threshold (e.g., 30,000 EUR/QALY)
        wtp_threshold = 30000
        if is_dominated:
            conclusion = "Dominated"
        elif icer < wtp_threshold:
            conclusion = "Cost-Effective"
        else:
            conclusion = "Not Cost-Effective"

        return ComparisonResults(
            strategy_a=results_a,
            strategy_b=results_b,
            delta_cost=round(delta_cost, 2),
            delta_qaly=round(delta_qaly, 4),
            icer=round(icer, 2) if icer != float('inf') else None,
            is_dominated=is_dominated,
            conclusion=conclusion
        )


def run_markov_analysis(params: Dict) -> Dict:
    """
    Main entry point for Markov analysis
    Returns results as dictionary for JSON serialization
    """
    config = MarkovConfig(
        time_horizon=params.get("time_horizon", 10),
        discount_rate_costs=params.get("discount_rate", 0.03),
        discount_rate_outcomes=params.get("discount_rate", 0.03),
        cohort_size=params.get("cohort_size", 1000)
    )

    model = MarkovModel(config)

    # Extract parameters for Drug A and Drug B
    params_a = {
        "prob_s_to_p": params.get("prob_s_to_p_a", 0.10),
        "prob_s_to_d": params.get("prob_s_to_d", 0.02),
        "prob_p_to_d": params.get("prob_p_to_d", 0.15),
        "cost_drug": params.get("cost_drug_a", 3500),
        "cost_state_s": params.get("cost_state_s", 200),
        "cost_state_p": params.get("cost_state_p", 4500),
        "utility_stable": params.get("utility_stable", 0.85),
        "utility_progression": params.get("utility_progression", 0.50),
    }

    params_b = {
        "prob_s_to_p": params.get("prob_s_to_p_b", 0.25),
        "prob_s_to_d": params.get("prob_s_to_d", 0.02),
        "prob_p_to_d": params.get("prob_p_to_d", 0.15),
        "cost_drug": params.get("cost_drug_b", 500),
        "cost_state_s": params.get("cost_state_s", 200),
        "cost_state_p": params.get("cost_state_p", 4500),
        "utility_stable": params.get("utility_stable", 0.85),
        "utility_progression": params.get("utility_progression", 0.50),
    }

    results = model.compare_strategies(params_a, params_b)

    return {
        "status": "success",
        "summary": {
            "icer": float(results.icer) if results.icer is not None else None,
            "delta_cost": float(results.delta_cost),
            "delta_qaly": float(results.delta_qaly),
            "conclusion": str(results.conclusion),
            "is_dominated": bool(results.is_dominated)
        },
        "drug_a_results": {
            "total_cost": float(results.strategy_a.total_cost),
            "total_qalys": float(results.strategy_a.total_qalys),
            "life_years": float(results.strategy_a.life_years),
            "state_trace": [[float(x) for x in row] for row in results.strategy_a.state_trace]
        },
        "drug_b_results": {
            "total_cost": float(results.strategy_b.total_cost),
            "total_qalys": float(results.strategy_b.total_qalys),
            "life_years": float(results.strategy_b.life_years),
            "state_trace": [[float(x) for x in row] for row in results.strategy_b.state_trace]
        }
    }
