import numpy as np
from typing import Dict, List, Callable
# from scipy import stats  # Not needed - using numpy distributions
from engine.markov.core import run_markov_analysis


def sample_from_distribution(dist_config: Dict, rng: np.random.Generator) -> float:
    """
    Sample a value from a statistical distribution

    Supported distributions:
    - beta: for probabilities
    - gamma: for costs
    - normal: for utilities
    """
    dist_type = dist_config.get("type", "normal")

    if dist_type == "beta":
        alpha = dist_config.get("alpha", 1)
        beta = dist_config.get("beta", 1)
        return rng.beta(alpha, beta)

    elif dist_type == "gamma":
        shape = dist_config.get("shape", 1)
        scale = dist_config.get("scale", 1)
        return rng.gamma(shape, scale)

    elif dist_type == "normal":
        mean = dist_config.get("mean", 0)
        std = dist_config.get("std", 1)
        return rng.normal(mean, std)

    elif dist_type == "lognormal":
        mean = dist_config.get("mean", 0)
        std = dist_config.get("std", 1)
        return rng.lognormal(mean, std)

    else:
        raise ValueError(f"Unsupported distribution type: {dist_type}")


def run_psa(
    base_params: Dict,
    distributions: Dict[str, Dict],
    n_iterations: int = 1000,
    seed: int = None,
    progress_callback: Callable = None
) -> Dict:
    """
    Run Probabilistic Sensitivity Analysis (Monte Carlo simulation)

    Args:
        base_params: Base case parameters
        distributions: Dict mapping param names to distribution configs
        n_iterations: Number of Monte Carlo iterations
        seed: Random seed for reproducibility
        progress_callback: Optional callback function(iteration, total)

    Returns:
        Dict with PSA results including scatter cloud and CEAC data
    """
    rng = np.random.default_rng(seed)

    psa_iterations = []

    for i in range(n_iterations):
        # Sample parameters from their distributions
        sampled_params = base_params.copy()

        for param_name, dist_config in distributions.items():
            if param_name in base_params:
                sampled_params[param_name] = sample_from_distribution(dist_config, rng)

        # Run model with sampled parameters
        try:
            result = run_markov_analysis(sampled_params)

            psa_iterations.append({
                "iteration": i + 1,
                "delta_cost": result["summary"]["delta_cost"],
                "delta_qaly": result["summary"]["delta_qaly"],
                "icer": result["summary"]["icer"]
            })

        except Exception as e:
            # Skip invalid parameter combinations
            continue

        # Progress callback
        if progress_callback and i % 50 == 0:
            progress_callback(i + 1, n_iterations)

    # Calculate statistics
    icers = [it["icer"] for it in psa_iterations if it["icer"] is not None]
    delta_costs = [it["delta_cost"] for it in psa_iterations]
    delta_qalys = [it["delta_qaly"] for it in psa_iterations]

    mean_icer = np.mean(icers) if icers else None
    median_icer = np.median(icers) if icers else None

    # Calculate 95% confidence interval
    if icers:
        ci_lower = np.percentile(icers, 2.5)
        ci_upper = np.percentile(icers, 97.5)
    else:
        ci_lower = None
        ci_upper = None

    # Calculate CEAC (Cost-Effectiveness Acceptability Curve)
    wtp_range = np.linspace(0, 100000, 100)  # Willingness-to-pay thresholds
    ceac_data = calculate_ceac(psa_iterations, wtp_range)

    return {
        "n_iterations": len(psa_iterations),
        "statistics": {
            "mean_icer": round(mean_icer, 2) if mean_icer else None,
            "median_icer": round(median_icer, 2) if median_icer else None,
            "ci_lower": round(ci_lower, 2) if ci_lower else None,
            "ci_upper": round(ci_upper, 2) if ci_upper else None
        },
        "psa_iterations": psa_iterations[:1000],  # Limit to 1000 for response size
        "ceac_data": ceac_data
    }


def calculate_ceac(
    psa_iterations: List[Dict],
    wtp_range: np.ndarray
) -> List[Dict]:
    """
    Calculate Cost-Effectiveness Acceptability Curve

    For each WTP threshold, calculate % of iterations where treatment is cost-effective
    """
    ceac_data = []

    for wtp in wtp_range:
        cost_effective_count = 0

        for iteration in psa_iterations:
            icer = iteration.get("icer")
            delta_cost = iteration.get("delta_cost")
            delta_qaly = iteration.get("delta_qaly")

            # Treatment is cost-effective if:
            # 1. ICER < WTP threshold
            # 2. OR it's dominant (lower cost, higher QALY)
            is_cost_effective = False

            if delta_cost < 0 and delta_qaly > 0:
                # Dominant: cheaper and more effective
                is_cost_effective = True
            elif icer is not None and icer < wtp:
                is_cost_effective = True

            if is_cost_effective:
                cost_effective_count += 1

        prob_cost_effective = cost_effective_count / len(psa_iterations)

        ceac_data.append({
            "wtp": round(wtp, 2),
            "prob_ce": round(prob_cost_effective, 4)
        })

    return ceac_data
