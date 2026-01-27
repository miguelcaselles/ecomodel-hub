"""
Flexible Markov Model Engine
Modelo de Markov configurable con n estados

Permite definir modelos Markov personalizados con cualquier número de estados,
transiciones y payoffs (costes, utilidades).
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class StateType(str, Enum):
    """Tipo de estado en el modelo"""
    TRANSIENT = "transient"  # Estado transitorio (puede salir)
    ABSORBING = "absorbing"  # Estado absorbente (no puede salir)
    TUNNEL = "tunnel"  # Estado túnel (tiempo limitado)


@dataclass
class State:
    """Definición de un estado en el modelo Markov"""
    name: str
    state_type: StateType = StateType.TRANSIENT
    cost: float = 0.0  # Coste por ciclo en este estado
    utility: float = 1.0  # Utilidad (QALY weight) en este estado
    one_time_cost: float = 0.0  # Coste de entrada al estado
    tunnel_length: Optional[int] = None  # Duración si es tunnel state

    def __hash__(self):
        return hash(self.name)


@dataclass
class Transition:
    """Definición de una transición entre estados"""
    from_state: str
    to_state: str
    probability: float
    cost: float = 0.0  # Coste de transición
    time_dependent: bool = False  # Si la probabilidad varía con el tiempo
    probability_function: Optional[str] = None  # Función para prob dependiente del tiempo


@dataclass
class FlexibleMarkovConfig:
    """Configuración del modelo Markov flexible"""
    name: str
    time_horizon: int
    cycle_length: float = 1.0  # En años
    discount_rate_costs: float = 0.03
    discount_rate_outcomes: float = 0.03
    half_cycle_correction: bool = True
    cohort_size: int = 1000
    currency: str = "EUR"


@dataclass
class StrategyConfig:
    """Configuración de una estrategia de tratamiento"""
    name: str
    transitions: List[Transition]
    state_costs: Optional[Dict[str, float]] = None  # Override de costes por estado
    state_utilities: Optional[Dict[str, float]] = None  # Override de utilidades


@dataclass
class CycleResults:
    """Resultados de un ciclo"""
    cycle: int
    state_occupancy: Dict[str, float]
    cycle_cost: float
    cycle_qaly: float
    cycle_ly: float
    discounted_cost: float
    discounted_qaly: float


@dataclass
class StrategyResults:
    """Resultados completos de una estrategia"""
    strategy_name: str
    total_cost: float
    total_qalys: float
    total_lys: float
    undiscounted_cost: float
    undiscounted_qalys: float
    state_trace: Dict[str, List[float]]  # state_name -> [occupancy per cycle]
    cycle_results: List[CycleResults]


@dataclass
class ICERResults:
    """Resultados de comparación ICER"""
    comparator: str
    intervention: str
    delta_cost: float
    delta_qaly: float
    delta_ly: float
    icer: Optional[float]
    icur: Optional[float]  # ICER usando LY en lugar de QALY
    is_dominated: bool
    is_extended_dominated: bool
    quadrant: str  # NE, NW, SE, SW


class FlexibleMarkovModel:
    """
    Modelo de Markov flexible con n estados configurables

    Características:
    - Cualquier número de estados
    - Estados absorbentes, transitorios y túnel
    - Costes y utilidades por estado
    - Costes de transición
    - Corrección de medio ciclo
    - Probabilidades dependientes del tiempo
    """

    def __init__(
        self,
        config: FlexibleMarkovConfig,
        states: List[State],
        initial_distribution: Optional[Dict[str, float]] = None
    ):
        self.config = config
        self.states = {s.name: s for s in states}
        self.state_names = [s.name for s in states]
        self.n_states = len(states)
        self.n_cycles = int(config.time_horizon / config.cycle_length)

        # Distribución inicial (por defecto: todos en primer estado)
        if initial_distribution is None:
            self.initial_distribution = np.zeros(self.n_states)
            self.initial_distribution[0] = config.cohort_size
        else:
            self.initial_distribution = np.array([
                initial_distribution.get(s, 0) for s in self.state_names
            ])

    def build_transition_matrix(
        self,
        transitions: List[Transition],
        cycle: int = 0
    ) -> np.ndarray:
        """
        Construir matriz de transición a partir de lista de transiciones

        Args:
            transitions: Lista de transiciones definidas
            cycle: Ciclo actual (para probabilidades dependientes del tiempo)

        Returns:
            Matriz de transición n_states x n_states
        """
        matrix = np.zeros((self.n_states, self.n_states))

        # Crear índice de estados
        state_idx = {name: i for i, name in enumerate(self.state_names)}

        # Llenar matriz con probabilidades definidas
        for trans in transitions:
            from_idx = state_idx.get(trans.from_state)
            to_idx = state_idx.get(trans.to_state)

            if from_idx is None or to_idx is None:
                continue

            # Calcular probabilidad (puede depender del tiempo)
            prob = trans.probability
            if trans.time_dependent and trans.probability_function:
                prob = self._evaluate_probability_function(
                    trans.probability_function, prob, cycle
                )

            matrix[from_idx, to_idx] = prob

        # Asegurar que las filas sumen 1.0
        for i in range(self.n_states):
            row_sum = matrix[i].sum()

            # Si el estado es absorbente, prob de quedarse = 1
            if self.states[self.state_names[i]].state_type == StateType.ABSORBING:
                matrix[i] = np.zeros(self.n_states)
                matrix[i, i] = 1.0
            elif row_sum < 1.0:
                # Añadir probabilidad de quedarse en el mismo estado
                matrix[i, i] += (1.0 - row_sum)
            elif row_sum > 1.0:
                # Normalizar
                matrix[i] = matrix[i] / row_sum

        return matrix

    def _evaluate_probability_function(
        self,
        func_str: str,
        base_prob: float,
        cycle: int
    ) -> float:
        """Evaluar función de probabilidad dependiente del tiempo"""
        # Funciones predefinidas
        if func_str == "linear_increase":
            return min(1.0, base_prob * (1 + 0.05 * cycle))
        elif func_str == "exponential_increase":
            return min(1.0, base_prob * (1.02 ** cycle))
        elif func_str == "weibull":
            # Aproximación Weibull (shape=1.5, scale=10)
            shape, scale = 1.5, 10
            t = cycle * self.config.cycle_length
            hazard = (shape / scale) * ((t / scale) ** (shape - 1))
            return 1 - np.exp(-hazard)
        else:
            return base_prob

    def run_simulation(
        self,
        strategy: StrategyConfig
    ) -> StrategyResults:
        """
        Ejecutar simulación de cohorte para una estrategia

        Args:
            strategy: Configuración de la estrategia

        Returns:
            Resultados completos de la estrategia
        """
        # Inicializar trace
        trace = np.zeros((self.n_cycles + 1, self.n_states))
        trace[0] = self.initial_distribution

        cycle_results = []
        total_cost = 0.0
        total_qaly = 0.0
        total_ly = 0.0
        undiscounted_cost = 0.0
        undiscounted_qaly = 0.0

        # Override de costes y utilidades por estado
        state_costs = strategy.state_costs or {}
        state_utilities = strategy.state_utilities or {}

        for cycle in range(1, self.n_cycles + 1):
            # Construir matriz para este ciclo
            matrix = self.build_transition_matrix(strategy.transitions, cycle)

            # Avanzar cohorte
            trace[cycle] = trace[cycle - 1] @ matrix

            # Calcular factores de descuento
            time = cycle * self.config.cycle_length
            discount_cost = 1 / ((1 + self.config.discount_rate_costs) ** time)
            discount_qaly = 1 / ((1 + self.config.discount_rate_outcomes) ** time)

            # Calcular payoffs del ciclo
            cycle_cost = 0.0
            cycle_qaly = 0.0
            cycle_ly = 0.0

            state_occupancy = {}

            for i, state_name in enumerate(self.state_names):
                state = self.states[state_name]
                occupancy = trace[cycle, i]
                state_occupancy[state_name] = occupancy

                # Usar override si existe, sino valor del estado
                cost = state_costs.get(state_name, state.cost)
                utility = state_utilities.get(state_name, state.utility)

                # Costes
                cycle_cost += occupancy * cost

                # Solo contar QALY/LY para estados no-muerte
                if state.state_type != StateType.ABSORBING or state.utility > 0:
                    cycle_qaly += occupancy * utility
                    cycle_ly += occupancy

            # Aplicar corrección de medio ciclo
            if self.config.half_cycle_correction:
                if cycle == 1:
                    cycle_cost *= 0.5
                    cycle_qaly *= 0.5
                    cycle_ly *= 0.5
                elif cycle == self.n_cycles:
                    cycle_cost *= 0.5
                    cycle_qaly *= 0.5
                    cycle_ly *= 0.5

            # Acumular
            undiscounted_cost += cycle_cost
            undiscounted_qaly += cycle_qaly
            total_cost += cycle_cost * discount_cost
            total_qaly += cycle_qaly * discount_qaly
            total_ly += cycle_ly * discount_qaly

            cycle_results.append(CycleResults(
                cycle=cycle,
                state_occupancy=state_occupancy,
                cycle_cost=cycle_cost,
                cycle_qaly=cycle_qaly / self.config.cohort_size,
                cycle_ly=cycle_ly / self.config.cohort_size,
                discounted_cost=cycle_cost * discount_cost,
                discounted_qaly=cycle_qaly * discount_qaly / self.config.cohort_size
            ))

        # Construir trace por estado
        state_trace = {
            name: trace[:, i].tolist()
            for i, name in enumerate(self.state_names)
        }

        return StrategyResults(
            strategy_name=strategy.name,
            total_cost=total_cost,
            total_qalys=total_qaly / self.config.cohort_size,
            total_lys=total_ly / self.config.cohort_size,
            undiscounted_cost=undiscounted_cost,
            undiscounted_qalys=undiscounted_qaly / self.config.cohort_size,
            state_trace=state_trace,
            cycle_results=cycle_results
        )

    def calculate_icer(
        self,
        comparator: StrategyResults,
        intervention: StrategyResults
    ) -> ICERResults:
        """
        Calcular ICER entre dos estrategias

        Args:
            comparator: Resultados del comparador (generalmente SOC)
            intervention: Resultados de la intervención (nuevo tratamiento)

        Returns:
            Resultados del análisis ICER
        """
        delta_cost = intervention.total_cost - comparator.total_cost
        delta_qaly = intervention.total_qalys - comparator.total_qalys
        delta_ly = intervention.total_lys - comparator.total_lys

        # Determinar cuadrante
        if delta_cost >= 0 and delta_qaly >= 0:
            quadrant = "NE"  # Más caro, más efectivo
        elif delta_cost < 0 and delta_qaly >= 0:
            quadrant = "SE"  # Más barato, más efectivo (dominante)
        elif delta_cost >= 0 and delta_qaly < 0:
            quadrant = "NW"  # Más caro, menos efectivo (dominado)
        else:
            quadrant = "SW"  # Más barato, menos efectivo

        # Calcular ICER
        is_dominated = quadrant == "NW"
        is_extended_dominated = False  # Requiere análisis con >2 estrategias

        if delta_qaly == 0:
            icer = float('inf') if delta_cost > 0 else float('-inf')
        else:
            icer = delta_cost / delta_qaly

        if delta_ly == 0:
            icur = None
        else:
            icur = delta_cost / delta_ly

        return ICERResults(
            comparator=comparator.strategy_name,
            intervention=intervention.strategy_name,
            delta_cost=delta_cost,
            delta_qaly=delta_qaly,
            delta_ly=delta_ly,
            icer=icer if abs(icer) != float('inf') else None,
            icur=icur,
            is_dominated=is_dominated,
            is_extended_dominated=is_extended_dominated,
            quadrant=quadrant
        )


def run_flexible_markov_analysis(params: Dict) -> Dict:
    """
    Punto de entrada principal para análisis Markov flexible

    Args:
        params: Diccionario con configuración del modelo

    Returns:
        Resultados como diccionario para serialización JSON
    """
    # Configuración del modelo
    config = FlexibleMarkovConfig(
        name=params.get("model_name", "Custom Markov Model"),
        time_horizon=params.get("time_horizon", 10),
        cycle_length=params.get("cycle_length", 1.0),
        discount_rate_costs=params.get("discount_rate", 0.03),
        discount_rate_outcomes=params.get("discount_rate", 0.03),
        half_cycle_correction=params.get("half_cycle_correction", True),
        cohort_size=params.get("cohort_size", 1000)
    )

    # Definir estados
    states_data = params.get("states", [])
    if not states_data:
        # Estados por defecto (modelo 3 estados estándar)
        states_data = [
            {"name": "Stable", "cost": 200, "utility": 0.85},
            {"name": "Progression", "cost": 4500, "utility": 0.50},
            {"name": "Death", "state_type": "absorbing", "cost": 0, "utility": 0}
        ]

    states = [
        State(
            name=s["name"],
            state_type=StateType(s.get("state_type", "transient")),
            cost=s.get("cost", 0),
            utility=s.get("utility", 1.0),
            one_time_cost=s.get("one_time_cost", 0)
        )
        for s in states_data
    ]

    # Distribución inicial
    initial_dist = params.get("initial_distribution", None)

    model = FlexibleMarkovModel(config, states, initial_dist)

    # Definir estrategias
    strategies_data = params.get("strategies", [])
    results_list = []

    for strat_data in strategies_data:
        transitions = [
            Transition(
                from_state=t["from"],
                to_state=t["to"],
                probability=t["probability"],
                time_dependent=t.get("time_dependent", False),
                probability_function=t.get("probability_function", None)
            )
            for t in strat_data.get("transitions", [])
        ]

        strategy = StrategyConfig(
            name=strat_data["name"],
            transitions=transitions,
            state_costs=strat_data.get("state_costs"),
            state_utilities=strat_data.get("state_utilities")
        )

        results = model.run_simulation(strategy)
        results_list.append(results)

    # Calcular ICERs si hay múltiples estrategias
    icer_results = []
    if len(results_list) >= 2:
        comparator = results_list[0]  # Primera estrategia como comparador
        for intervention in results_list[1:]:
            icer = model.calculate_icer(comparator, intervention)
            icer_results.append({
                "comparator": icer.comparator,
                "intervention": icer.intervention,
                "delta_cost": round(icer.delta_cost, 2),
                "delta_qaly": round(icer.delta_qaly, 4),
                "delta_ly": round(icer.delta_ly, 4),
                "icer": round(icer.icer, 2) if icer.icer else None,
                "quadrant": icer.quadrant,
                "is_dominated": icer.is_dominated
            })

    # Formatear resultados
    return {
        "status": "success",
        "config": {
            "model_name": config.name,
            "time_horizon": config.time_horizon,
            "cycle_length": config.cycle_length,
            "discount_rate": config.discount_rate_costs,
            "cohort_size": config.cohort_size,
            "n_states": model.n_states,
            "n_cycles": model.n_cycles,
            "states": [s.name for s in states]
        },
        "strategies": [
            {
                "name": r.strategy_name,
                "total_cost": round(r.total_cost, 2),
                "total_qalys": round(r.total_qalys, 4),
                "total_lys": round(r.total_lys, 4),
                "undiscounted_cost": round(r.undiscounted_cost, 2),
                "undiscounted_qalys": round(r.undiscounted_qalys, 4),
                "state_trace": {
                    k: [round(v, 2) for v in vals]
                    for k, vals in r.state_trace.items()
                }
            }
            for r in results_list
        ],
        "icer_analysis": icer_results
    }
