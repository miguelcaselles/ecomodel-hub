"""
Wrapper for R heemod package - Professional Markov models
"""
import logging
from typing import Dict, List, Optional
import numpy as np

try:
    import rpy2.robjects as ro
    from rpy2.robjects.packages import importr

    # Try to activate converters if available (pandas not required)
    try:
        from rpy2.robjects import numpy2ri
        numpy2ri.activate()
    except (ImportError, Exception):
        pass

    try:
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
    except (ImportError, Exception):
        pass

    R_AVAILABLE = True
except ImportError as e:
    R_AVAILABLE = False
    logging.warning(f"rpy2 not available. R integration disabled. Error: {e}")

logger = logging.getLogger(__name__)


class HeemodWrapper:
    """
    Wrapper for R heemod package to create professional Markov models.
    Provides Python interface to R's powerful HEOR modeling capabilities.
    """

    def __init__(self):
        if not R_AVAILABLE:
            raise RuntimeError("rpy2 is not installed. Cannot use R integration.")

        try:
            # Import R packages
            self.heemod = importr('heemod')
            self.base = importr('base')
            self.stats = importr('stats')
            logger.info("R heemod package loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load R packages: {e}")
            raise RuntimeError(f"R package 'heemod' not available: {e}")

    def create_state(self, name: str, cost: float, utility: float) -> ro.vectors.ListVector:
        """Create a health state with cost and utility"""
        state_def = ro.r(f'''
            define_state(
                cost = {cost},
                utility = {utility}
            )
        ''')
        return state_def

    def create_transition_matrix(self,
                                  prob_dict: Dict[str, Dict[str, float]],
                                  state_names: List[str]) -> ro.vectors.Matrix:
        """
        Create transition probability matrix.

        Args:
            prob_dict: Nested dict {from_state: {to_state: probability}}
            state_names: List of state names in order

        Returns:
            R matrix object
        """
        # Build matrix string for R
        n_states = len(state_names)
        matrix_values = []

        for from_state in state_names:
            for to_state in state_names:
                prob = prob_dict.get(from_state, {}).get(to_state, 0.0)
                matrix_values.append(prob)

        # Create R matrix
        r_code = f'''
            matrix(
                c({', '.join(map(str, matrix_values))}),
                nrow = {n_states},
                ncol = {n_states},
                byrow = TRUE,
                dimnames = list(
                    c({', '.join(f'"{s}"' for s in state_names)}),
                    c({', '.join(f'"{s}"' for s in state_names)})
                )
            )
        '''

        return ro.r(r_code)

    def run_markov_model(self,
                        states: Dict[str, Dict[str, float]],
                        transitions: Dict[str, Dict[str, float]],
                        cycles: int,
                        discount_rate: float = 0.03,
                        init_pop: Optional[List[int]] = None) -> Dict:
        """
        Run a complete Markov model using heemod.

        Args:
            states: {state_name: {cost: float, utility: float}}
            transitions: {from_state: {to_state: probability}}
            cycles: Number of cycles to simulate
            discount_rate: Annual discount rate (default 3%)
            init_pop: Initial population distribution

        Returns:
            Dict with results: costs, qalys, traces
        """
        try:
            state_names = list(states.keys())

            # Create states
            state_defs = {}
            for name, values in states.items():
                state_defs[name] = self.create_state(
                    name,
                    values['cost'],
                    values['utility']
                )

            # Create transition matrix
            trans_mat = self.create_transition_matrix(transitions, state_names)

            # Set initial population
            if init_pop is None:
                init_pop = [1000] + [0] * (len(state_names) - 1)

            # Run model using heemod
            # Build transition matrix as individual values (not vectors)
            mat_values = []
            for from_state in state_names:
                for to_state in state_names:
                    prob = transitions.get(from_state, {}).get(to_state, 0.0)
                    mat_values.append(str(prob))

            r_code = f'''
            library(heemod)

            # Define states
            {self._generate_state_definitions(states)}

            # Define transition matrix
            mat <- define_transition(
                state_names = c({', '.join(f'"{s}"' for s in state_names)}),
                {', '.join(mat_values)}
            )

            # Create strategy
            mod <- define_strategy(
                transition = mat,
                {', '.join(f'{name} = state_{name}' for name in state_names)}
            )

            # Run model
            result <- run_model(
                mod,
                cycles = {cycles},
                cost = cost,
                effect = utility,
                init = c({', '.join(map(str, init_pop))})
            )

            result
            '''

            result = ro.r(r_code)

            # Extract results
            return self._extract_results(result)

        except Exception as e:
            logger.error(f"Error running heemod model: {e}")
            raise

    def _generate_state_definitions(self, states: Dict[str, Dict[str, float]]) -> str:
        """Generate R code for state definitions"""
        code_lines = []
        for name, values in states.items():
            code_lines.append(
                f"state_{name} <- define_state(cost = {values['cost']}, utility = {values['utility']})"
            )
        return '\n'.join(code_lines)

    def _matrix_to_r_string(self, transitions: Dict[str, Dict[str, float]],
                           state_names: List[str]) -> str:
        """Convert transition dict to R matrix string with proper heemod format"""
        n = len(state_names)

        # Build matrix row by row for heemod
        matrix_rows = []
        for from_state in state_names:
            row = []
            for to_state in state_names:
                prob = transitions.get(from_state, {}).get(to_state, 0.0)
                row.append(str(prob))
            matrix_rows.append(f"c({', '.join(row)})")

        # Create transition matrix for heemod
        return f'''define_transition(
            {',\n            '.join(matrix_rows)},
            state_names = c({', '.join(f'"{s}"' for s in state_names)})
        )'''

    def _extract_results(self, r_result) -> Dict:
        """Extract results from R heemod output"""
        try:
            # heemod returns a complex object, let's extract key summary statistics
            # Get summary statistics
            summary_cmd = '''
            list(
                total_cost = sum(result[[1]]$cost, na.rm=TRUE),
                total_qaly = sum(result[[1]]$effect, na.rm=TRUE),
                total_ly = sum(result[[1]]$life_year, na.rm=TRUE)
            )
            '''
            summary = ro.r(summary_cmd)

            return {
                "total_cost": float(summary.rx2('total_cost')[0]) if summary.rx2('total_cost')[0] is not None else 0.0,
                "total_qaly": float(summary.rx2('total_qaly')[0]) if summary.rx2('total_qaly')[0] is not None else 0.0,
                "total_ly": float(summary.rx2('total_ly')[0]) if summary.rx2('total_ly')[0] is not None else 0.0,
                "engine": "heemod (R)"
            }
        except Exception as e:
            logger.error(f"Error extracting results: {e}")
            import traceback
            traceback.print_exc()
            # Return basic structure even on error
            return {
                "total_cost": 0.0,
                "total_qaly": 0.0,
                "total_ly": 0.0,
                "engine": "heemod (R)",
                "error": str(e)
            }

    def generate_r_code(self,
                       states: Dict[str, Dict[str, float]],
                       transitions: Dict[str, Dict[str, float]],
                       cycles: int,
                       discount_rate: float = 0.03) -> str:
        """
        Generate standalone R code for the model.
        This code can be exported for transparency and auditing.
        """
        state_names = list(states.keys())

        code = f'''# EcoModel Hub - Generated Markov Model Code
# Model can be audited and modified independently

library(heemod)

# Define health states
{self._generate_state_definitions(states)}

# Define transition matrix
mat <- {self._matrix_to_r_string(transitions, state_names)}

# Create strategy
strategy <- define_strategy(
    transition = mat,
    {', '.join(f'{name} = state_{name}' for name in state_names)}
)

# Run model
result <- run_model(
    strategy,
    cycles = {cycles},
    cost = cost,
    effect = utility,
    method = "life-table",
    disc_cost = {discount_rate},
    disc_effect = {discount_rate}
)

# View results
summary(result)
plot(result)

# Export results
write.csv(result$values, "markov_results.csv")
'''
        return code


def is_r_available() -> bool:
    """Check if R integration is available"""
    return R_AVAILABLE


def get_heemod_wrapper() -> Optional[HeemodWrapper]:
    """Get heemod wrapper instance if available"""
    if not R_AVAILABLE:
        logger.warning("R integration not available")
        return None

    try:
        return HeemodWrapper()
    except Exception as e:
        logger.error(f"Failed to initialize heemod wrapper: {e}")
        return None
