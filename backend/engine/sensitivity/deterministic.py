import numpy as np
from typing import Dict, List
from engine.markov.core import run_markov_analysis


def tornado_analysis(base_params: Dict, param_ranges: Dict) -> Dict:
    """
    Perform tornado diagram analysis (one-way sensitivity analysis)

    Args:
        base_params: Base case parameter values
        param_ranges: Dict of {param_name: (low_value, high_value)}

    Returns:
        Dict with tornado chart data sorted by impact
    """
    base_result = run_markov_analysis(base_params)
    base_icer = base_result["summary"]["icer"]

    tornado_data = []

    for param_name, (low_val, high_val) in param_ranges.items():
        # Test low value
        params_low = base_params.copy()
        params_low[param_name] = low_val
        result_low = run_markov_analysis(params_low)
        icer_low = result_low["summary"]["icer"]

        # Test high value
        params_high = base_params.copy()
        params_high[param_name] = high_val
        result_high = run_markov_analysis(params_high)
        icer_high = result_high["summary"]["icer"]

        # Calculate impact (range of ICER)
        impact = abs(icer_high - icer_low)

        tornado_data.append({
            "parameter": param_name,
            "base_value": base_params[param_name],
            "low_value": low_val,
            "high_value": high_val,
            "icer_low": round(icer_low, 2) if icer_low else None,
            "icer_high": round(icer_high, 2) if icer_high else None,
            "impact": round(impact, 2) if impact else 0
        })

    # Sort by impact (descending)
    tornado_data.sort(key=lambda x: x["impact"], reverse=True)

    return {
        "base_icer": base_icer,
        "tornado_data": tornado_data
    }


def one_way_sensitivity(
    base_params: Dict,
    param_name: str,
    values: List[float]
) -> Dict:
    """
    One-way sensitivity analysis for a single parameter

    Args:
        base_params: Base case parameters
        param_name: Name of parameter to vary
        values: List of values to test

    Returns:
        Dict with parameter values and corresponding ICERs
    """
    results = []

    for value in values:
        params = base_params.copy()
        params[param_name] = value
        result = run_markov_analysis(params)

        results.append({
            "parameter_value": value,
            "icer": result["summary"]["icer"],
            "delta_cost": result["summary"]["delta_cost"],
            "delta_qaly": result["summary"]["delta_qaly"]
        })

    return {
        "parameter": param_name,
        "results": results
    }
