"""
Budget Impact Analysis (BIA) Engine
Análisis de Impacto Presupuestario para evaluaciones HTA

Este módulo implementa el análisis de impacto presupuestario según las guías
ISPOR (International Society for Pharmacoeconomics and Outcomes Research)
y requisitos de agencias HTA como NICE, AEMPS, SMC.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class PopulationGrowthType(str, Enum):
    """Tipo de crecimiento poblacional"""
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


class MarketUptakeType(str, Enum):
    """Tipo de curva de adopción de mercado"""
    LINEAR = "linear"
    S_CURVE = "s_curve"
    IMMEDIATE = "immediate"
    CUSTOM = "custom"


@dataclass
class PopulationConfig:
    """Configuración de población objetivo"""
    total_population: int  # Población total del país/región
    prevalence_rate: float  # Tasa de prevalencia de la enfermedad
    incidence_rate: float  # Tasa de incidencia anual (nuevos casos)
    diagnosis_rate: float = 1.0  # % de pacientes diagnosticados
    treatment_eligible_rate: float = 1.0  # % elegibles para tratamiento
    growth_type: PopulationGrowthType = PopulationGrowthType.CONSTANT
    annual_growth_rate: float = 0.0  # Crecimiento anual de población


@dataclass
class TreatmentOption:
    """Opción de tratamiento (nuevo o actual)"""
    name: str
    annual_cost: float  # Coste anual por paciente
    administration_cost: float = 0.0  # Coste de administración
    monitoring_cost: float = 0.0  # Coste de monitorización
    adverse_event_cost: float = 0.0  # Coste de eventos adversos
    discontinuation_rate: float = 0.0  # Tasa de discontinuación anual

    @property
    def total_annual_cost(self) -> float:
        """Coste total anual por paciente"""
        return (self.annual_cost +
                self.administration_cost +
                self.monitoring_cost +
                self.adverse_event_cost)


@dataclass
class MarketShareScenario:
    """Escenario de cuotas de mercado"""
    year: int
    shares: Dict[str, float]  # treatment_name -> market_share (0-1)

    def validate(self) -> bool:
        """Validar que las cuotas sumen 1.0"""
        total = sum(self.shares.values())
        return abs(total - 1.0) < 0.001


@dataclass
class BIAConfig:
    """Configuración del análisis de impacto presupuestario"""
    time_horizon: int = 5  # años (típicamente 3-5 para BIA)
    perspective: str = "payer"  # payer, healthcare_system, societal
    currency: str = "EUR"
    discount_rate: float = 0.0  # BIA típicamente sin descuento
    include_indirect_costs: bool = False


@dataclass
class BIAResults:
    """Resultados del análisis de impacto presupuestario"""
    # Por año
    yearly_costs_current: List[float]
    yearly_costs_new: List[float]
    yearly_budget_impact: List[float]
    yearly_patients_treated: List[Dict[str, int]]

    # Totales
    total_budget_impact: float
    cumulative_budget_impact: List[float]

    # Por tratamiento
    costs_by_treatment: Dict[str, List[float]]
    patients_by_treatment: Dict[str, List[int]]

    # Métricas adicionales
    average_annual_impact: float
    peak_annual_impact: float
    peak_year: int


class BudgetImpactModel:
    """
    Modelo de Impacto Presupuestario

    Compara el impacto presupuestario de introducir un nuevo tratamiento
    versus mantener el mix de tratamientos actual.
    """

    def __init__(
        self,
        config: BIAConfig,
        population: PopulationConfig,
        treatments: List[TreatmentOption]
    ):
        self.config = config
        self.population = population
        self.treatments = {t.name: t for t in treatments}
        self.n_years = config.time_horizon

    def calculate_eligible_population(self, year: int) -> int:
        """Calcular población elegible para tratamiento en un año dado"""
        base_pop = self.population.total_population

        # Aplicar crecimiento poblacional
        if self.population.growth_type == PopulationGrowthType.LINEAR:
            growth_factor = 1 + (self.population.annual_growth_rate * year)
        elif self.population.growth_type == PopulationGrowthType.EXPONENTIAL:
            growth_factor = (1 + self.population.annual_growth_rate) ** year
        else:
            growth_factor = 1.0

        total_pop = base_pop * growth_factor

        # Calcular población elegible
        prevalent_cases = total_pop * self.population.prevalence_rate
        eligible = (prevalent_cases *
                   self.population.diagnosis_rate *
                   self.population.treatment_eligible_rate)

        return int(eligible)

    def generate_market_shares(
        self,
        new_treatment: str,
        uptake_type: MarketUptakeType,
        max_share: float,
        current_shares: Dict[str, float],
        displaced_treatments: Optional[List[str]] = None
    ) -> List[MarketShareScenario]:
        """
        Generar escenarios de cuotas de mercado para cada año

        Args:
            new_treatment: Nombre del nuevo tratamiento
            uptake_type: Tipo de curva de adopción
            max_share: Cuota máxima a alcanzar
            current_shares: Cuotas actuales (año 0)
            displaced_treatments: Tratamientos que pierden cuota
        """
        scenarios = []

        # Año 0: situación actual
        scenarios.append(MarketShareScenario(year=0, shares=current_shares.copy()))

        # Si no se especifican tratamientos desplazados, distribuir proporcionalmente
        if displaced_treatments is None:
            displaced_treatments = [t for t in current_shares.keys()
                                   if t != new_treatment]

        for year in range(1, self.n_years + 1):
            # Calcular cuota del nuevo tratamiento según tipo de adopción
            if uptake_type == MarketUptakeType.LINEAR:
                new_share = min(max_share, max_share * year / self.n_years)
            elif uptake_type == MarketUptakeType.S_CURVE:
                # Curva S (logística)
                midpoint = self.n_years / 2
                steepness = 1.5
                new_share = max_share / (1 + np.exp(-steepness * (year - midpoint)))
            elif uptake_type == MarketUptakeType.IMMEDIATE:
                new_share = max_share
            else:
                new_share = max_share * year / self.n_years

            # Calcular cuotas de tratamientos desplazados
            shares = current_shares.copy()
            shares[new_treatment] = new_share

            # Reducir cuotas de tratamientos desplazados proporcionalmente
            total_displaced_share = sum(current_shares.get(t, 0)
                                        for t in displaced_treatments)

            if total_displaced_share > 0:
                for treatment in displaced_treatments:
                    original_share = current_shares.get(treatment, 0)
                    proportion = original_share / total_displaced_share
                    reduction = new_share * proportion
                    shares[treatment] = max(0, original_share - reduction)

            # Normalizar para que sumen 1.0
            total = sum(shares.values())
            if total > 0:
                shares = {k: v / total for k, v in shares.items()}

            scenarios.append(MarketShareScenario(year=year, shares=shares))

        return scenarios

    def calculate_costs(
        self,
        scenarios_current: List[MarketShareScenario],
        scenarios_new: List[MarketShareScenario]
    ) -> BIAResults:
        """
        Calcular costes e impacto presupuestario

        Args:
            scenarios_current: Escenarios sin nuevo tratamiento
            scenarios_new: Escenarios con nuevo tratamiento
        """
        yearly_costs_current = []
        yearly_costs_new = []
        yearly_budget_impact = []
        cumulative_impact = []
        yearly_patients = []

        costs_by_treatment = {t: [] for t in self.treatments.keys()}
        patients_by_treatment = {t: [] for t in self.treatments.keys()}

        cumulative = 0.0

        for year in range(self.n_years + 1):
            eligible_pop = self.calculate_eligible_population(year)

            # Costes en escenario actual (sin nuevo tratamiento)
            cost_current = 0.0
            for treatment_name, share in scenarios_current[year].shares.items():
                if treatment_name in self.treatments:
                    treatment = self.treatments[treatment_name]
                    patients = int(eligible_pop * share)
                    cost = patients * treatment.total_annual_cost
                    cost_current += cost

            # Costes en escenario nuevo (con nuevo tratamiento)
            cost_new = 0.0
            patients_year = {}
            for treatment_name, share in scenarios_new[year].shares.items():
                if treatment_name in self.treatments:
                    treatment = self.treatments[treatment_name]
                    patients = int(eligible_pop * share)
                    cost = patients * treatment.total_annual_cost
                    cost_new += cost

                    costs_by_treatment[treatment_name].append(cost)
                    patients_by_treatment[treatment_name].append(patients)
                    patients_year[treatment_name] = patients

            # Impacto presupuestario
            impact = cost_new - cost_current
            cumulative += impact

            yearly_costs_current.append(cost_current)
            yearly_costs_new.append(cost_new)
            yearly_budget_impact.append(impact)
            cumulative_impact.append(cumulative)
            yearly_patients.append(patients_year)

        # Calcular métricas adicionales
        total_impact = sum(yearly_budget_impact)
        avg_impact = total_impact / (self.n_years + 1)
        peak_impact = max(yearly_budget_impact, key=abs)
        peak_year = yearly_budget_impact.index(peak_impact)

        return BIAResults(
            yearly_costs_current=yearly_costs_current,
            yearly_costs_new=yearly_costs_new,
            yearly_budget_impact=yearly_budget_impact,
            yearly_patients_treated=yearly_patients,
            total_budget_impact=total_impact,
            cumulative_budget_impact=cumulative_impact,
            costs_by_treatment=costs_by_treatment,
            patients_by_treatment=patients_by_treatment,
            average_annual_impact=avg_impact,
            peak_annual_impact=peak_impact,
            peak_year=peak_year
        )


def run_budget_impact_analysis(params: Dict) -> Dict:
    """
    Punto de entrada principal para análisis de impacto presupuestario

    Args:
        params: Diccionario con parámetros del análisis

    Returns:
        Resultados como diccionario para serialización JSON
    """
    # Configuración
    config = BIAConfig(
        time_horizon=params.get("time_horizon", 5),
        perspective=params.get("perspective", "payer"),
        currency=params.get("currency", "EUR"),
        discount_rate=params.get("discount_rate", 0.0)
    )

    # Población
    population = PopulationConfig(
        total_population=params.get("total_population", 47_000_000),  # España
        prevalence_rate=params.get("prevalence_rate", 0.001),
        incidence_rate=params.get("incidence_rate", 0.0001),
        diagnosis_rate=params.get("diagnosis_rate", 0.85),
        treatment_eligible_rate=params.get("treatment_eligible_rate", 0.70),
        growth_type=PopulationGrowthType(params.get("growth_type", "constant")),
        annual_growth_rate=params.get("annual_growth_rate", 0.005)
    )

    # Tratamientos
    treatments = []
    for t_data in params.get("treatments", []):
        treatments.append(TreatmentOption(
            name=t_data["name"],
            annual_cost=t_data.get("annual_cost", 0),
            administration_cost=t_data.get("administration_cost", 0),
            monitoring_cost=t_data.get("monitoring_cost", 0),
            adverse_event_cost=t_data.get("adverse_event_cost", 0),
            discontinuation_rate=t_data.get("discontinuation_rate", 0)
        ))

    # Si no hay tratamientos definidos, usar valores por defecto
    if not treatments:
        treatments = [
            TreatmentOption(
                name="Standard of Care",
                annual_cost=params.get("cost_soc", 2800),
                monitoring_cost=params.get("monitoring_cost_soc", 500)
            ),
            TreatmentOption(
                name="New Treatment",
                annual_cost=params.get("cost_new", 15000),
                administration_cost=params.get("admin_cost_new", 200),
                monitoring_cost=params.get("monitoring_cost_new", 800)
            )
        ]

    model = BudgetImpactModel(config, population, treatments)

    # Cuotas de mercado actuales
    current_shares = params.get("current_market_shares", {
        "Standard of Care": 1.0,
        "New Treatment": 0.0
    })

    # Generar escenarios
    new_treatment_name = params.get("new_treatment_name", "New Treatment")
    max_share = params.get("max_market_share", 0.30)
    uptake_type = MarketUptakeType(params.get("uptake_type", "s_curve"))

    # Escenario actual (sin cambios)
    scenarios_current = [
        MarketShareScenario(year=y, shares=current_shares.copy())
        for y in range(config.time_horizon + 1)
    ]

    # Escenario con nuevo tratamiento
    scenarios_new = model.generate_market_shares(
        new_treatment=new_treatment_name,
        uptake_type=uptake_type,
        max_share=max_share,
        current_shares=current_shares
    )

    # Calcular resultados
    results = model.calculate_costs(scenarios_current, scenarios_new)

    # Formatear para JSON
    return {
        "status": "success",
        "config": {
            "time_horizon": config.time_horizon,
            "perspective": config.perspective,
            "currency": config.currency,
            "eligible_population_year_0": model.calculate_eligible_population(0),
            "eligible_population_year_final": model.calculate_eligible_population(config.time_horizon)
        },
        "summary": {
            "total_budget_impact": round(results.total_budget_impact, 2),
            "average_annual_impact": round(results.average_annual_impact, 2),
            "peak_annual_impact": round(results.peak_annual_impact, 2),
            "peak_year": results.peak_year
        },
        "yearly_results": {
            "years": list(range(config.time_horizon + 1)),
            "costs_current_scenario": [round(c, 2) for c in results.yearly_costs_current],
            "costs_new_scenario": [round(c, 2) for c in results.yearly_costs_new],
            "budget_impact": [round(c, 2) for c in results.yearly_budget_impact],
            "cumulative_impact": [round(c, 2) for c in results.cumulative_budget_impact],
            "patients_treated": results.yearly_patients_treated
        },
        "market_shares": {
            "current_scenario": [s.shares for s in scenarios_current],
            "new_scenario": [s.shares for s in scenarios_new]
        },
        "by_treatment": {
            "costs": {k: [round(c, 2) for c in v]
                     for k, v in results.costs_by_treatment.items()},
            "patients": results.patients_by_treatment
        }
    }
