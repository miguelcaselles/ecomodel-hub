"""
Parametric Survival Analysis Engine
Análisis de Supervivencia Paramétrico para evaluaciones farmacoeconómicas

Implementa distribuciones de supervivencia comunes:
- Exponencial
- Weibull
- Log-normal
- Log-logística
- Gompertz
- Gamma generalizada

Funcionalidades:
- Ajuste de curvas paramétricas
- Extrapolación más allá del horizonte de ensayo
- Conversión a probabilidades de transición para Markov
- Comparación de tratamientos con hazard ratios
"""

import numpy as np
from scipy import stats
from scipy.optimize import minimize
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


class SurvivalDistribution(str, Enum):
    """Distribuciones de supervivencia soportadas"""
    EXPONENTIAL = "exponential"
    WEIBULL = "weibull"
    LOGNORMAL = "lognormal"
    LOGLOGISTIC = "loglogistic"
    GOMPERTZ = "gompertz"
    GAMMA = "gamma"


@dataclass
class SurvivalParams:
    """Parámetros de distribución de supervivencia"""
    distribution: SurvivalDistribution
    # Parámetros comunes
    scale: float = 1.0  # lambda (exponencial), scale (otros)
    shape: float = 1.0  # k (Weibull), sigma (lognormal), etc.
    # Parámetros adicionales para algunas distribuciones
    location: float = 0.0
    # Hazard ratio para comparaciones
    hazard_ratio: float = 1.0


@dataclass
class SurvivalData:
    """Datos de supervivencia (puede ser censurado)"""
    time: List[float]  # Tiempos de evento/censura
    event: List[int]  # 1 = evento, 0 = censurado
    group: Optional[List[str]] = None  # Grupo de tratamiento


@dataclass
class SurvivalCurve:
    """Curva de supervivencia"""
    times: List[float]
    survival_prob: List[float]
    hazard: List[float]
    cumulative_hazard: List[float]
    confidence_lower: Optional[List[float]] = None
    confidence_upper: Optional[List[float]] = None


@dataclass
class FitResult:
    """Resultado del ajuste de modelo"""
    distribution: SurvivalDistribution
    parameters: Dict[str, float]
    aic: float
    bic: float
    log_likelihood: float
    rmst: float  # Restricted Mean Survival Time
    median_survival: Optional[float] = None


class ParametricSurvival:
    """
    Clase para análisis de supervivencia paramétrico

    Permite ajustar datos de supervivencia a distribuciones paramétricas
    y extrapolar más allá del periodo de observación.
    """

    def __init__(self, distribution: SurvivalDistribution):
        self.distribution = distribution
        self.params: Optional[SurvivalParams] = None
        self._fitted = False

    def survival_function(self, t: np.ndarray, params: SurvivalParams) -> np.ndarray:
        """
        Calcular S(t) - probabilidad de supervivencia en tiempo t

        Args:
            t: Array de tiempos
            params: Parámetros de la distribución

        Returns:
            Array de probabilidades de supervivencia
        """
        t = np.asarray(t)
        scale = params.scale
        shape = params.shape

        if self.distribution == SurvivalDistribution.EXPONENTIAL:
            # S(t) = exp(-λt)
            return np.exp(-t / scale)

        elif self.distribution == SurvivalDistribution.WEIBULL:
            # S(t) = exp(-(t/λ)^k)
            return np.exp(-np.power(t / scale, shape))

        elif self.distribution == SurvivalDistribution.LOGNORMAL:
            # S(t) = 1 - Φ((log(t) - μ) / σ)
            mu = np.log(scale)
            sigma = shape
            return 1 - stats.norm.cdf((np.log(np.maximum(t, 1e-10)) - mu) / sigma)

        elif self.distribution == SurvivalDistribution.LOGLOGISTIC:
            # S(t) = 1 / (1 + (t/α)^β)
            alpha = scale
            beta = shape
            return 1 / (1 + np.power(t / alpha, beta))

        elif self.distribution == SurvivalDistribution.GOMPERTZ:
            # S(t) = exp(-(b/a)(exp(at) - 1))
            a = shape  # rate of aging
            b = 1 / scale  # initial hazard
            return np.exp(-(b / a) * (np.exp(a * t) - 1))

        elif self.distribution == SurvivalDistribution.GAMMA:
            # S(t) = 1 - F(t; k, θ) donde F es CDF gamma
            return 1 - stats.gamma.cdf(t, a=shape, scale=scale)

        return np.ones_like(t)

    def hazard_function(self, t: np.ndarray, params: SurvivalParams) -> np.ndarray:
        """
        Calcular h(t) - función de riesgo (hazard)

        Args:
            t: Array de tiempos
            params: Parámetros de la distribución

        Returns:
            Array de tasas de riesgo instantáneo
        """
        t = np.asarray(t)
        scale = params.scale
        shape = params.shape

        # Evitar división por cero
        t = np.maximum(t, 1e-10)

        if self.distribution == SurvivalDistribution.EXPONENTIAL:
            # h(t) = λ (constante)
            return np.full_like(t, 1 / scale)

        elif self.distribution == SurvivalDistribution.WEIBULL:
            # h(t) = (k/λ)(t/λ)^(k-1)
            return (shape / scale) * np.power(t / scale, shape - 1)

        elif self.distribution == SurvivalDistribution.LOGNORMAL:
            # h(t) = f(t) / S(t)
            mu = np.log(scale)
            sigma = shape
            z = (np.log(t) - mu) / sigma
            pdf = stats.norm.pdf(z) / (t * sigma)
            survival = self.survival_function(t, params)
            return pdf / np.maximum(survival, 1e-10)

        elif self.distribution == SurvivalDistribution.LOGLOGISTIC:
            # h(t) = (β/α)(t/α)^(β-1) / (1 + (t/α)^β)
            alpha = scale
            beta = shape
            numerator = (beta / alpha) * np.power(t / alpha, beta - 1)
            denominator = 1 + np.power(t / alpha, beta)
            return numerator / denominator

        elif self.distribution == SurvivalDistribution.GOMPERTZ:
            # h(t) = b * exp(at)
            a = shape
            b = 1 / scale
            return b * np.exp(a * t)

        elif self.distribution == SurvivalDistribution.GAMMA:
            # h(t) = f(t) / S(t)
            pdf = stats.gamma.pdf(t, a=shape, scale=scale)
            survival = self.survival_function(t, params)
            return pdf / np.maximum(survival, 1e-10)

        return np.zeros_like(t)

    def cumulative_hazard(self, t: np.ndarray, params: SurvivalParams) -> np.ndarray:
        """Calcular H(t) = -log(S(t))"""
        survival = self.survival_function(t, params)
        return -np.log(np.maximum(survival, 1e-10))

    def fit(self, data: SurvivalData) -> FitResult:
        """
        Ajustar modelo a datos de supervivencia

        Args:
            data: Datos de supervivencia (tiempos y eventos)

        Returns:
            Resultado del ajuste con parámetros y métricas
        """
        times = np.array(data.time)
        events = np.array(data.event)
        n = len(times)

        def neg_log_likelihood(params_array):
            """Función de verosimilitud negativa"""
            if len(params_array) == 1:
                p = SurvivalParams(
                    distribution=self.distribution,
                    scale=np.exp(params_array[0])
                )
            else:
                p = SurvivalParams(
                    distribution=self.distribution,
                    scale=np.exp(params_array[0]),
                    shape=np.exp(params_array[1])
                )

            # Log-likelihood = Σ[δᵢ log h(tᵢ) - H(tᵢ)]
            hazard = self.hazard_function(times, p)
            cum_hazard = self.cumulative_hazard(times, p)

            ll = np.sum(events * np.log(np.maximum(hazard, 1e-10)) - cum_hazard)

            if np.isnan(ll) or np.isinf(ll):
                return 1e10

            return -ll

        # Valores iniciales
        if self.distribution == SurvivalDistribution.EXPONENTIAL:
            x0 = [np.log(np.mean(times))]
            n_params = 1
        else:
            x0 = [np.log(np.mean(times)), 0]  # shape = exp(0) = 1
            n_params = 2

        # Optimizar
        result = minimize(neg_log_likelihood, x0, method='Nelder-Mead')

        # Extraer parámetros
        if n_params == 1:
            scale = np.exp(result.x[0])
            shape = 1.0
        else:
            scale = np.exp(result.x[0])
            shape = np.exp(result.x[1])

        self.params = SurvivalParams(
            distribution=self.distribution,
            scale=scale,
            shape=shape
        )
        self._fitted = True

        # Calcular métricas de ajuste
        log_likelihood = -result.fun
        aic = 2 * n_params - 2 * log_likelihood
        bic = n_params * np.log(n) - 2 * log_likelihood

        # Calcular RMST (Restricted Mean Survival Time)
        max_time = np.max(times)
        t_grid = np.linspace(0, max_time, 100)
        survival_curve = self.survival_function(t_grid, self.params)
        rmst = np.trapz(survival_curve, t_grid)

        # Mediana de supervivencia
        median = self._find_median(self.params)

        return FitResult(
            distribution=self.distribution,
            parameters={'scale': scale, 'shape': shape},
            aic=aic,
            bic=bic,
            log_likelihood=log_likelihood,
            rmst=rmst,
            median_survival=median
        )

    def _find_median(self, params: SurvivalParams) -> Optional[float]:
        """Encontrar tiempo mediano de supervivencia (S(t) = 0.5)"""
        from scipy.optimize import brentq

        def objective(t):
            return self.survival_function(np.array([t]), params)[0] - 0.5

        try:
            median = brentq(objective, 0.001, 1000)
            return median
        except ValueError:
            return None

    def predict(
        self,
        times: List[float],
        hazard_ratio: float = 1.0
    ) -> SurvivalCurve:
        """
        Predecir curva de supervivencia

        Args:
            times: Tiempos para predicción
            hazard_ratio: Factor multiplicativo del hazard (para comparaciones)

        Returns:
            Curva de supervivencia
        """
        if not self._fitted or self.params is None:
            raise ValueError("Model not fitted")

        t = np.array(times)

        # Aplicar hazard ratio
        params_modified = SurvivalParams(
            distribution=self.params.distribution,
            scale=self.params.scale,
            shape=self.params.shape,
            hazard_ratio=hazard_ratio
        )

        # Para aplicar HR, modificamos el hazard acumulado
        base_cum_hazard = self.cumulative_hazard(t, self.params)
        modified_cum_hazard = base_cum_hazard * hazard_ratio
        survival = np.exp(-modified_cum_hazard)

        hazard = self.hazard_function(t, self.params) * hazard_ratio

        return SurvivalCurve(
            times=times,
            survival_prob=survival.tolist(),
            hazard=hazard.tolist(),
            cumulative_hazard=modified_cum_hazard.tolist()
        )

    def to_transition_probabilities(
        self,
        cycle_length: float = 1.0,
        n_cycles: int = 10,
        hazard_ratio: float = 1.0
    ) -> List[float]:
        """
        Convertir curva de supervivencia a probabilidades de transición
        para uso en modelos Markov

        Args:
            cycle_length: Duración del ciclo en años
            n_cycles: Número de ciclos
            hazard_ratio: Factor para modificar hazard

        Returns:
            Lista de probabilidades de transición por ciclo
        """
        if not self._fitted or self.params is None:
            raise ValueError("Model not fitted")

        probs = []

        for cycle in range(n_cycles):
            t_start = cycle * cycle_length
            t_end = (cycle + 1) * cycle_length

            # S(t_start) y S(t_end)
            s_start = self.survival_function(
                np.array([t_start]), self.params
            )[0]
            s_end = self.survival_function(
                np.array([t_end]), self.params
            )[0]

            # Aplicar hazard ratio
            if hazard_ratio != 1.0:
                h_start = self.cumulative_hazard(np.array([t_start]), self.params)[0]
                h_end = self.cumulative_hazard(np.array([t_end]), self.params)[0]
                s_start = np.exp(-h_start * hazard_ratio)
                s_end = np.exp(-h_end * hazard_ratio)

            # Probabilidad de transición (salir del estado)
            if s_start > 0:
                p_transition = 1 - (s_end / s_start)
            else:
                p_transition = 1.0

            probs.append(min(max(p_transition, 0), 1))

        return probs


def compare_distributions(data: SurvivalData) -> Dict[str, FitResult]:
    """
    Comparar ajuste de múltiples distribuciones

    Args:
        data: Datos de supervivencia

    Returns:
        Diccionario con resultados de cada distribución
    """
    results = {}

    for dist in SurvivalDistribution:
        try:
            model = ParametricSurvival(dist)
            fit_result = model.fit(data)
            results[dist.value] = fit_result
        except Exception as e:
            results[dist.value] = None

    return results


def run_survival_analysis(params: Dict) -> Dict:
    """
    Punto de entrada principal para análisis de supervivencia

    Args:
        params: Diccionario con datos y configuración

    Returns:
        Resultados del análisis
    """
    # Datos de supervivencia
    times = params.get("times", [])
    events = params.get("events", [])

    # Si no hay datos, usar ejemplo
    if not times:
        # Datos simulados de ejemplo
        np.random.seed(42)
        n = 100
        # Weibull con scale=5, shape=1.5
        times = list(np.random.weibull(1.5, n) * 5)
        # 80% eventos, 20% censurados
        events = list(np.random.binomial(1, 0.8, n))

    data = SurvivalData(time=times, event=events)

    # Distribución a usar
    distribution = SurvivalDistribution(
        params.get("distribution", "weibull")
    )

    # Ajustar modelo
    model = ParametricSurvival(distribution)
    fit_result = model.fit(data)

    # Predicciones
    max_time = params.get("max_time", max(times) * 1.5)
    time_points = list(np.linspace(0.1, max_time, 50))
    curve = model.predict(time_points)

    # Comparar con hazard ratio si se especifica
    hr = params.get("hazard_ratio", 1.0)
    comparison_curve = None
    if hr != 1.0:
        comparison_curve = model.predict(time_points, hazard_ratio=hr)

    # Convertir a probabilidades de transición Markov
    cycle_length = params.get("cycle_length", 1.0)
    n_cycles = params.get("n_cycles", int(max_time / cycle_length))
    transition_probs = model.to_transition_probabilities(
        cycle_length=cycle_length,
        n_cycles=n_cycles
    )

    # Comparar distribuciones si se solicita
    distribution_comparison = None
    if params.get("compare_distributions", False):
        comparison_results = compare_distributions(data)
        distribution_comparison = {
            dist: {
                "aic": r.aic,
                "bic": r.bic,
                "log_likelihood": r.log_likelihood,
                "median_survival": r.median_survival,
                "rmst": r.rmst,
                "parameters": r.parameters
            }
            for dist, r in comparison_results.items()
            if r is not None
        }

    return {
        "status": "success",
        "fit": {
            "distribution": fit_result.distribution.value,
            "parameters": fit_result.parameters,
            "aic": round(fit_result.aic, 2),
            "bic": round(fit_result.bic, 2),
            "log_likelihood": round(fit_result.log_likelihood, 2),
            "median_survival": round(fit_result.median_survival, 2) if fit_result.median_survival else None,
            "rmst": round(fit_result.rmst, 2)
        },
        "survival_curve": {
            "times": time_points,
            "survival": [round(s, 4) for s in curve.survival_prob],
            "hazard": [round(h, 4) for h in curve.hazard]
        },
        "comparison_curve": {
            "hazard_ratio": hr,
            "survival": [round(s, 4) for s in comparison_curve.survival_prob]
        } if comparison_curve else None,
        "markov_transition_probabilities": {
            "cycle_length": cycle_length,
            "probabilities": [round(p, 4) for p in transition_probs]
        },
        "distribution_comparison": distribution_comparison
    }
