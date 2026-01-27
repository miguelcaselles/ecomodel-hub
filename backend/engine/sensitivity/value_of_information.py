"""
Value of Information Analysis
Análisis del Valor de la Información para decisiones de investigación

Implementa:
- EVPI (Expected Value of Perfect Information)
- EVPPI (Expected Value of Partial Perfect Information)
- Análisis de priorización de investigación futura

El valor de información cuantifica cuánto valdría eliminar la incertidumbre
en los parámetros del modelo antes de tomar una decisión.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings


@dataclass
class VOIConfig:
    """Configuración para análisis de valor de información"""
    wtp_threshold: float = 30000.0  # Willingness-to-pay por QALY
    n_outer_samples: int = 1000  # Muestras externas (EVPPI)
    n_inner_samples: int = 1000  # Muestras internas (EVPPI)
    population_size: int = 100000  # Población afectada por la decisión
    decision_horizon: int = 10  # Años de horizonte de decisión
    annual_discount_rate: float = 0.035  # Tasa de descuento anual
    currency: str = "EUR"


@dataclass
class PSAIteration:
    """Resultado de una iteración PSA"""
    parameters: Dict[str, float]
    costs: Dict[str, float]  # strategy -> cost
    qalys: Dict[str, float]  # strategy -> QALY
    nmb: Dict[str, float]  # strategy -> Net Monetary Benefit
    optimal_strategy: str


@dataclass
class EVPIResult:
    """Resultado del análisis EVPI"""
    evpi_per_patient: float
    evpi_population: float
    evpi_decision_horizon: float
    optimal_strategy_current: str
    probability_optimal: Dict[str, float]
    ceac_data: Dict[str, List[float]]  # WTP thresholds -> prob cost-effective


@dataclass
class EVPPIResult:
    """Resultado del análisis EVPPI para un parámetro"""
    parameter_name: str
    evppi_per_patient: float
    evppi_population: float
    contribution_to_evpi: float  # Porcentaje del EVPI explicado


class ValueOfInformation:
    """
    Clase para análisis del valor de información

    Calcula EVPI y EVPPI para priorizar investigación futura
    basándose en resultados de análisis probabilístico (PSA).
    """

    def __init__(self, config: VOIConfig):
        self.config = config
        self.psa_results: List[PSAIteration] = []
        self.strategies: List[str] = []

    def add_psa_results(self, results: List[PSAIteration]):
        """Añadir resultados de PSA"""
        self.psa_results = results
        if results:
            self.strategies = list(results[0].costs.keys())

    def calculate_nmb(
        self,
        cost: float,
        qaly: float,
        wtp: float = None
    ) -> float:
        """Calcular Net Monetary Benefit"""
        wtp = wtp or self.config.wtp_threshold
        return qaly * wtp - cost

    def calculate_evpi(self, wtp_range: Optional[List[float]] = None) -> EVPIResult:
        """
        Calcular Expected Value of Perfect Information

        EVPI = E[max(NMB)] - max(E[NMB])

        El EVPI representa el valor máximo que valdría obtener información
        perfecta sobre todos los parámetros antes de decidir.

        Args:
            wtp_range: Rango de umbrales WTP para CEAC

        Returns:
            Resultado EVPI con métricas por paciente y población
        """
        if not self.psa_results:
            raise ValueError("No PSA results available")

        wtp = self.config.wtp_threshold
        n_iter = len(self.psa_results)

        # Calcular NMB para cada iteración y estrategia
        nmb_matrix = np.zeros((n_iter, len(self.strategies)))

        for i, iteration in enumerate(self.psa_results):
            for j, strategy in enumerate(self.strategies):
                nmb_matrix[i, j] = self.calculate_nmb(
                    iteration.costs[strategy],
                    iteration.qalys[strategy],
                    wtp
                )

        # E[max(NMB)] - valor esperado del máximo NMB con información perfecta
        max_nmb_per_iter = np.max(nmb_matrix, axis=1)
        expected_max_nmb = np.mean(max_nmb_per_iter)

        # max(E[NMB]) - máximo del valor esperado (decisión actual)
        expected_nmb = np.mean(nmb_matrix, axis=0)
        max_expected_nmb = np.max(expected_nmb)
        optimal_idx = np.argmax(expected_nmb)
        optimal_strategy = self.strategies[optimal_idx]

        # EVPI per patient
        evpi_per_patient = max(0, expected_max_nmb - max_expected_nmb)

        # Probabilidad de que cada estrategia sea óptima
        optimal_counts = np.argmax(nmb_matrix, axis=1)
        prob_optimal = {
            self.strategies[j]: np.mean(optimal_counts == j)
            for j in range(len(self.strategies))
        }

        # CEAC (Cost-Effectiveness Acceptability Curve)
        if wtp_range is None:
            wtp_range = list(np.linspace(0, 100000, 21))

        ceac_data = {strategy: [] for strategy in self.strategies}

        for wtp_val in wtp_range:
            nmb_at_wtp = np.zeros((n_iter, len(self.strategies)))
            for i, iteration in enumerate(self.psa_results):
                for j, strategy in enumerate(self.strategies):
                    nmb_at_wtp[i, j] = self.calculate_nmb(
                        iteration.costs[strategy],
                        iteration.qalys[strategy],
                        wtp_val
                    )

            optimal_at_wtp = np.argmax(nmb_at_wtp, axis=1)
            for j, strategy in enumerate(self.strategies):
                ceac_data[strategy].append(float(np.mean(optimal_at_wtp == j)))

        # Escalar a población y horizonte de decisión
        discount_factor = sum(
            1 / (1 + self.config.annual_discount_rate) ** t
            for t in range(self.config.decision_horizon)
        )

        evpi_population = evpi_per_patient * self.config.population_size
        evpi_decision_horizon = evpi_population * discount_factor

        return EVPIResult(
            evpi_per_patient=evpi_per_patient,
            evpi_population=evpi_population,
            evpi_decision_horizon=evpi_decision_horizon,
            optimal_strategy_current=optimal_strategy,
            probability_optimal=prob_optimal,
            ceac_data={
                'wtp_thresholds': wtp_range,
                **ceac_data
            }
        )

    def calculate_evppi_single(
        self,
        parameter_name: str,
        evpi_result: EVPIResult
    ) -> EVPPIResult:
        """
        Calcular EVPPI para un solo parámetro

        EVPPI representa el valor de conocer perfectamente un parámetro
        específico, manteniendo la incertidumbre en los demás.

        Método: Two-level Monte Carlo (computacionalmente intensivo)
        Aproximación: Regresión no paramétrica (más eficiente)

        Args:
            parameter_name: Nombre del parámetro
            evpi_result: Resultado EVPI previo

        Returns:
            Resultado EVPPI para el parámetro
        """
        if not self.psa_results:
            raise ValueError("No PSA results available")

        wtp = self.config.wtp_threshold
        n_iter = len(self.psa_results)

        # Extraer valores del parámetro y NMB
        param_values = np.array([
            r.parameters.get(parameter_name, 0) for r in self.psa_results
        ])

        nmb_matrix = np.zeros((n_iter, len(self.strategies)))
        for i, iteration in enumerate(self.psa_results):
            for j, strategy in enumerate(self.strategies):
                nmb_matrix[i, j] = self.calculate_nmb(
                    iteration.costs[strategy],
                    iteration.qalys[strategy],
                    wtp
                )

        # Método de regresión: GAM-like usando bins
        # Dividir el parámetro en cuantiles y calcular E[max(NMB)|θ]

        n_bins = min(20, n_iter // 50)
        if n_bins < 5:
            n_bins = 5

        try:
            bins = np.percentile(param_values, np.linspace(0, 100, n_bins + 1))
            bin_indices = np.digitize(param_values, bins[1:-1])

            conditional_max_nmb = []
            for b in range(n_bins):
                mask = bin_indices == b
                if np.sum(mask) > 0:
                    nmb_in_bin = nmb_matrix[mask]
                    # E[max(NMB)|θ in bin]
                    max_per_iter = np.max(nmb_in_bin, axis=1)
                    conditional_max_nmb.append(np.mean(max_per_iter))

            # E[E[max(NMB)|θ]] ≈ EVPPI component
            expected_conditional_max = np.mean(conditional_max_nmb)

            # max(E[NMB]) - decisión actual sin información adicional
            max_expected_nmb = np.max(np.mean(nmb_matrix, axis=0))

            evppi_per_patient = max(0, expected_conditional_max - max_expected_nmb)

        except Exception:
            # Fallback si hay problemas con binning
            evppi_per_patient = 0.0

        # Escalar a población
        evppi_population = evppi_per_patient * self.config.population_size

        # Contribución al EVPI total
        contribution = 0.0
        if evpi_result.evpi_per_patient > 0:
            contribution = (evppi_per_patient / evpi_result.evpi_per_patient) * 100

        return EVPPIResult(
            parameter_name=parameter_name,
            evppi_per_patient=evppi_per_patient,
            evppi_population=evppi_population,
            contribution_to_evpi=min(contribution, 100)  # Cap at 100%
        )

    def calculate_evppi_all(self) -> Tuple[EVPIResult, List[EVPPIResult]]:
        """
        Calcular EVPI y EVPPI para todos los parámetros

        Returns:
            Tuple de (EVPIResult, lista de EVPPIResult por parámetro)
        """
        evpi = self.calculate_evpi()

        # Obtener lista de parámetros
        if self.psa_results:
            parameters = list(self.psa_results[0].parameters.keys())
        else:
            parameters = []

        evppi_results = []
        for param in parameters:
            try:
                evppi = self.calculate_evppi_single(param, evpi)
                evppi_results.append(evppi)
            except Exception:
                continue

        # Ordenar por contribución al EVPI
        evppi_results.sort(key=lambda x: x.contribution_to_evpi, reverse=True)

        return evpi, evppi_results


def run_voi_analysis(params: Dict) -> Dict:
    """
    Punto de entrada principal para análisis de valor de información

    Args:
        params: Diccionario con resultados PSA y configuración

    Returns:
        Resultados del análisis VOI
    """
    config = VOIConfig(
        wtp_threshold=params.get("wtp_threshold", 30000),
        population_size=params.get("population_size", 100000),
        decision_horizon=params.get("decision_horizon", 10),
        annual_discount_rate=params.get("discount_rate", 0.035),
        currency=params.get("currency", "EUR")
    )

    voi = ValueOfInformation(config)

    # Cargar resultados PSA
    psa_data = params.get("psa_results", [])

    if psa_data:
        psa_results = [
            PSAIteration(
                parameters=r.get("parameters", {}),
                costs=r.get("costs", {}),
                qalys=r.get("qalys", {}),
                nmb=r.get("nmb", {}),
                optimal_strategy=r.get("optimal", "")
            )
            for r in psa_data
        ]
        voi.add_psa_results(psa_results)
    else:
        # Generar datos de ejemplo
        np.random.seed(42)
        n_iter = 1000
        strategies = ["Drug A", "Drug B"]

        psa_results = []
        for _ in range(n_iter):
            # Parámetros con incertidumbre
            cost_a = np.random.gamma(100, 35)
            cost_b = np.random.gamma(100, 28)
            eff_a = np.random.beta(85, 15)
            eff_b = np.random.beta(75, 25)

            costs = {"Drug A": cost_a * 10, "Drug B": cost_b * 10}
            qalys = {"Drug A": eff_a * 8, "Drug B": eff_b * 8}

            nmb = {
                s: qalys[s] * config.wtp_threshold - costs[s]
                for s in strategies
            }

            optimal = max(nmb, key=nmb.get)

            psa_results.append(PSAIteration(
                parameters={
                    "cost_drug_a": cost_a * 10,
                    "cost_drug_b": cost_b * 10,
                    "effectiveness_a": eff_a,
                    "effectiveness_b": eff_b
                },
                costs=costs,
                qalys=qalys,
                nmb=nmb,
                optimal_strategy=optimal
            ))

        voi.add_psa_results(psa_results)

    # Calcular EVPI y EVPPI
    evpi_result, evppi_results = voi.calculate_evppi_all()

    # Formatear resultados
    return {
        "status": "success",
        "config": {
            "wtp_threshold": config.wtp_threshold,
            "population_size": config.population_size,
            "decision_horizon": config.decision_horizon,
            "currency": config.currency
        },
        "evpi": {
            "per_patient": round(evpi_result.evpi_per_patient, 2),
            "population": round(evpi_result.evpi_population, 0),
            "decision_horizon": round(evpi_result.evpi_decision_horizon, 0),
            "optimal_strategy": evpi_result.optimal_strategy_current,
            "probability_optimal": {
                k: round(v, 3) for k, v in evpi_result.probability_optimal.items()
            }
        },
        "ceac": {
            "wtp_thresholds": evpi_result.ceac_data.get('wtp_thresholds', []),
            "probabilities": {
                k: [round(p, 3) for p in v]
                for k, v in evpi_result.ceac_data.items()
                if k != 'wtp_thresholds'
            }
        },
        "evppi": [
            {
                "parameter": r.parameter_name,
                "per_patient": round(r.evppi_per_patient, 2),
                "population": round(r.evppi_population, 0),
                "contribution_pct": round(r.contribution_to_evpi, 1)
            }
            for r in evppi_results
        ],
        "interpretation": {
            "total_value_of_research": round(evpi_result.evpi_decision_horizon, 0),
            "research_priorities": [
                r.parameter_name for r in evppi_results[:3]
            ] if evppi_results else [],
            "recommendation": _generate_recommendation(evpi_result, evppi_results)
        }
    }


def _generate_recommendation(evpi: EVPIResult, evppi: List[EVPPIResult]) -> str:
    """Generar recomendación basada en resultados VOI"""
    if evpi.evpi_per_patient < 100:
        return "Low value of additional research. Current evidence sufficient for decision."
    elif evpi.evpi_per_patient < 1000:
        return "Moderate value of additional research. Consider targeted studies."
    else:
        if evppi:
            top_param = evppi[0].parameter_name
            return f"High value of additional research. Priority: reduce uncertainty in {top_param}."
        return "High value of additional research. Consider comprehensive clinical trial."
