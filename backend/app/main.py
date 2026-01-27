from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from datetime import datetime
import traceback

from app.config import settings
from app.api.v1.router import api_router
from app.services.report_service import report_service
from engine.markov.core import run_markov_analysis
from engine.markov.flexible import run_flexible_markov_analysis
from engine.sensitivity.probabilistic import run_psa
from engine.sensitivity.deterministic import tornado_analysis
from engine.sensitivity.value_of_information import run_voi_analysis
from engine.budget_impact import run_budget_impact_analysis
from engine.decision_tree import run_decision_tree_analysis
from engine.survival import run_survival_analysis
from app.services.ai import get_assistant, quick_interpret

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


class CalculationRequest(BaseModel):
    time_horizon: int
    discount_rate: float
    cohort_size: int
    cost_drug_a: float
    cost_drug_b: float
    cost_state_s: float
    cost_state_p: float
    prob_s_to_p_a: float
    prob_s_to_p_b: float
    prob_s_to_d: float
    prob_p_to_d: float
    utility_stable: float
    utility_progression: float


@app.get("/")
async def root():
    """Serve the professional landing page"""
    return FileResponse('static/landing.html')

@app.get("/login")
async def login_page():
    """Serve login page"""
    return FileResponse('static/login.html')

@app.get("/app")
async def app_page():
    """Serve authenticated app (requires JWT token check in frontend)"""
    return FileResponse('static/app.html')

@app.get("/demo")
async def demo():
    """Serve the original demo interface"""
    return FileResponse('static/index.html')

@app.get("/model-builder")
async def model_builder():
    """Serve the Model Builder wizard (admin only)"""
    return FileResponse('static/model-builder.html')


@app.get("/demo-guidance")
async def demo_guidance():
    """Serve the Model Builder Guidance Demo page"""
    return FileResponse('static/demo-guidance.html')


@app.get("/welcome")
async def welcome_page():
    """Serve the onboarding/welcome page for new users"""
    return FileResponse('static/onboarding.html')


@app.get("/getting-started")
async def getting_started():
    """Alias for welcome page"""
    return FileResponse('static/onboarding.html')


@app.get("/budget-impact")
async def budget_impact_page():
    """Serve the Budget Impact Analysis page"""
    return FileResponse('static/budget-impact.html')


@app.get("/decision-tree")
async def decision_tree_page():
    """Serve the Decision Tree Analysis page"""
    return FileResponse('static/decision-tree.html')


@app.get("/survival")
async def survival_page():
    """Serve the Survival Analysis page"""
    return FileResponse('static/survival-analysis.html')


@app.get("/voi")
async def voi_page():
    """Serve the Value of Information Analysis page"""
    return FileResponse('static/voi-analysis.html')


@app.post("/api/calculate")
async def calculate(request: CalculationRequest):
    """Endpoint público para cálculos sin autenticación"""
    params = request.model_dump()
    result = run_markov_analysis(params)
    return result


@app.post("/api/psa")
async def calculate_psa(request: CalculationRequest, iterations: int = 1000):
    """Endpoint público para PSA sin autenticación"""
    params = request.model_dump()

    # Define distributions for PSA
    distributions = {
        "cost_drug_a": {"type": "gamma", "shape": 10, "scale": params.get("cost_drug_a", 3500) / 10},
        "cost_drug_b": {"type": "gamma", "shape": 10, "scale": params.get("cost_drug_b", 2800) / 10},
        "prob_s_to_p_a": {"type": "beta", "alpha": 10, "beta": 90},
        "prob_s_to_p_b": {"type": "beta", "alpha": 15, "beta": 85},
        "utility_stable": {"type": "beta", "alpha": 85, "beta": 15},
        "utility_progression": {"type": "beta", "alpha": 65, "beta": 35},
    }

    psa_results = run_psa(params, distributions, n_iterations=iterations, seed=42)
    base_results = run_markov_analysis(params)

    return {
        "status": "success",
        "base_case": base_results,
        "psa_results": psa_results,
        "iterations": iterations
    }


@app.post("/api/tornado")
async def calculate_tornado(request: CalculationRequest):
    """Endpoint público para Tornado sin autenticación"""
    params = request.model_dump()

    # Define parameter ranges for sensitivity (±20%)
    param_ranges = {
        "cost_drug_a": (params["cost_drug_a"] * 0.8, params["cost_drug_a"] * 1.2),
        "cost_drug_b": (params["cost_drug_b"] * 0.8, params["cost_drug_b"] * 1.2),
        "prob_s_to_p_a": (max(0, params["prob_s_to_p_a"] * 0.8), min(1, params["prob_s_to_p_a"] * 1.2)),
        "prob_s_to_p_b": (max(0, params["prob_s_to_p_b"] * 0.8), min(1, params["prob_s_to_p_b"] * 1.2)),
        "utility_stable": (max(0, params["utility_stable"] * 0.9), min(1, params["utility_stable"] * 1.1)),
        "utility_progression": (max(0, params["utility_progression"] * 0.9), min(1, params["utility_progression"] * 1.1)),
        "discount_rate": (params["discount_rate"] * 0.5, params["discount_rate"] * 1.5),
    }

    tornado_results = tornado_analysis(params, param_ranges)
    base_results = run_markov_analysis(params)

    return {
        "status": "success",
        "base_case": base_results,
        "tornado_results": tornado_results
    }


@app.post("/api/export/pdf")
async def export_pdf_quick(request: CalculationRequest):
    """Export PDF from quick analysis results (no authentication required)"""
    try:
        params = request.model_dump()
        results = run_markov_analysis(params)

        pdf_bytes = report_service.generate_pdf_report(
            scenario_name="Quick Analysis",
            user_email="anonymous@ecomodel.com",
            organization="Demo",
            parameters=params,
            results_drug_a=results["drug_a_results"],
            results_drug_b=results["drug_b_results"]
        )

        # Return PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=EcoModel_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/export/excel")
async def export_excel_quick(request: CalculationRequest):
    """Export Excel from quick analysis results (no authentication required)"""
    try:
        params = request.model_dump()
        results = run_markov_analysis(params)

        excel_bytes = report_service.generate_excel_report(
            scenario_name="Quick Analysis",
            user_email="anonymous@ecomodel.com",
            parameters={
                "Time Horizon": f"{params.get('time_horizon', 10)} years",
                "Discount Rate": f"{params.get('discount_rate', 0.03) * 100}%",
                "Drug A Cost": f"€{params.get('cost_drug_a', 3500):,.0f}",
                "Drug B Cost": f"€{params.get('cost_drug_b', 2800):,.0f}",
                "Stable State Cost": f"€{params.get('cost_state_s', 200):,.0f}",
                "Progression State Cost": f"€{params.get('cost_state_p', 4500):,.0f}",
                "Progression Risk Drug A": f"{params.get('prob_s_to_p_a', 0.1) * 100:.1f}%",
                "Progression Risk Drug B": f"{params.get('prob_s_to_p_b', 0.25) * 100:.1f}%",
                "Utility Stable": f"{params.get('utility_stable', 0.85):.2f}",
                "Utility Progression": f"{params.get('utility_progression', 0.5):.2f}",
            },
            results_drug_a=results["drug_a_results"],
            results_drug_b=results["drug_b_results"],
            psa_results=None,
            tornado_results=None
        )

        # Return Excel
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=EcoModel_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ============================================================================
# NUEVOS ENDPOINTS PARA FUNCIONALIDADES AVANZADAS
# ============================================================================

@app.post("/api/budget-impact")
async def calculate_budget_impact(request: dict):
    """
    Budget Impact Analysis (BIA)

    Analiza el impacto presupuestario de introducir un nuevo tratamiento.
    Requerido por agencias HTA como AEMPS, NICE, SMC.
    """
    try:
        result = run_budget_impact_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BIA calculation failed: {str(e)}")


@app.post("/api/decision-tree")
async def calculate_decision_tree(request: dict):
    """
    Decision Tree Analysis

    Análisis de árbol de decisión con roll-back y cálculo de ICER.
    Soporta múltiples estrategias y análisis de sensibilidad.
    """
    try:
        result = run_decision_tree_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision tree analysis failed: {str(e)}")


@app.post("/api/survival")
async def calculate_survival(request: dict):
    """
    Parametric Survival Analysis

    Ajusta datos de supervivencia a distribuciones paramétricas
    (Exponencial, Weibull, Log-normal, Log-logística, Gompertz, Gamma).
    Convierte a probabilidades de transición para modelos Markov.
    """
    try:
        result = run_survival_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Survival analysis failed: {str(e)}")


@app.post("/api/markov-flexible")
async def calculate_markov_flexible(request: dict):
    """
    Flexible Markov Model

    Modelo Markov con n estados configurables.
    Soporta estados absorbentes, transitorios y túnel.
    Permite probabilidades dependientes del tiempo.
    """
    try:
        result = run_flexible_markov_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flexible Markov analysis failed: {str(e)}")


@app.post("/api/voi")
async def calculate_voi(request: dict):
    """
    Value of Information Analysis (EVPI/EVPPI)

    Calcula el valor de la información perfecta (EVPI) y parcial (EVPPI).
    Permite priorizar investigación futura basándose en la incertidumbre
    de los parámetros del modelo.
    """
    try:
        result = run_voi_analysis(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VOI analysis failed: {str(e)}")


@app.get("/api/capabilities")
async def get_capabilities():
    """
    Lista de capacidades y módulos disponibles en la plataforma
    """
    return {
        "platform": "EcoModel Hub",
        "version": "2.0.0",
        "modules": {
            "markov_basic": {
                "name": "Basic Markov Model",
                "description": "3-state Markov model (Stable, Progression, Death)",
                "endpoint": "/api/calculate",
                "status": "active"
            },
            "markov_flexible": {
                "name": "Flexible Markov Model",
                "description": "N-state configurable Markov model with time-dependent transitions",
                "endpoint": "/api/markov-flexible",
                "status": "active"
            },
            "decision_tree": {
                "name": "Decision Tree Analysis",
                "description": "Decision tree with roll-back analysis and ICER calculation",
                "endpoint": "/api/decision-tree",
                "status": "active"
            },
            "budget_impact": {
                "name": "Budget Impact Analysis",
                "description": "Budget impact model following ISPOR guidelines",
                "endpoint": "/api/budget-impact",
                "status": "active"
            },
            "survival_analysis": {
                "name": "Parametric Survival Analysis",
                "description": "Fit survival data to parametric distributions (Weibull, Gompertz, etc.)",
                "endpoint": "/api/survival",
                "status": "active"
            },
            "psa": {
                "name": "Probabilistic Sensitivity Analysis",
                "description": "Monte Carlo simulation with multiple distributions",
                "endpoint": "/api/psa",
                "status": "active"
            },
            "tornado": {
                "name": "Deterministic Sensitivity Analysis",
                "description": "One-way sensitivity analysis (Tornado diagram)",
                "endpoint": "/api/tornado",
                "status": "active"
            },
            "voi": {
                "name": "Value of Information",
                "description": "EVPI and EVPPI analysis for research prioritization",
                "endpoint": "/api/voi",
                "status": "active"
            }
        },
        "exports": ["pdf", "excel"],
        "hta_compliance": ["NICE", "AEMPS", "SMC", "HAS", "G-BA", "ISPOR"],
        "ai_assistant": {
            "name": "PharmEcon AI Assistant",
            "description": "AI-powered assistant for interpreting results and guiding analysis",
            "endpoint": "/api/assistant/chat",
            "status": "active"
        }
    }


# ============================================================================
# ASISTENTE DE IA PARA FARMACOECONOMÍA
# ============================================================================

class ChatRequest(BaseModel):
    """Request para el chat del asistente"""
    message: str
    context: dict = None
    session_id: str = None


class InterpretRequest(BaseModel):
    """Request para interpretación de resultados"""
    results: dict
    analysis_type: str  # markov, bia, psa, tornado, decision_tree, survival, voi


@app.post("/api/assistant/chat")
async def assistant_chat(request: ChatRequest):
    """
    Chat con el asistente de IA de farmacoeconomía

    El asistente puede:
    - Explicar conceptos (ICER, QALY, PSA, etc.)
    - Guiar en la configuración de modelos
    - Responder preguntas sobre HTA
    - Interpretar resultados

    Funciona con OpenAI/Anthropic si hay API key, o en modo offline con
    base de conocimiento local.
    """
    try:
        assistant = get_assistant()

        if request.context:
            assistant.set_analysis_context(request.context)

        response = await assistant.chat(request.message)

        return {
            "status": "success",
            "response": response,
            "session_id": request.session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assistant error: {str(e)}")


@app.post("/api/assistant/interpret")
async def assistant_interpret(request: InterpretRequest):
    """
    Interpretación automática de resultados por el asistente IA

    Genera explicación en lenguaje natural de los resultados del análisis.
    """
    try:
        interpretation = await quick_interpret(request.results, request.analysis_type)

        return {
            "status": "success",
            "interpretation": interpretation,
            "analysis_type": request.analysis_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interpretation error: {str(e)}")


@app.post("/api/assistant/executive-summary")
async def assistant_executive_summary(request: dict):
    """
    Genera un resumen ejecutivo de todos los análisis

    Ideal para presentar a directivos o comités de decisión.
    """
    try:
        assistant = get_assistant()
        summary = await assistant.generate_executive_summary(request)

        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation error: {str(e)}")


@app.post("/api/assistant/suggest-parameters")
async def assistant_suggest_parameters(request: dict):
    """
    Sugiere parámetros típicos basados en área terapéutica

    Útil para usuarios que empiezan un nuevo modelo y no conocen
    los rangos típicos de parámetros.
    """
    try:
        assistant = get_assistant()
        disease_area = request.get("disease_area", "general")
        treatment_type = request.get("treatment_type", "oral")

        suggestions = await assistant.suggest_parameters(disease_area, treatment_type)

        return {
            "status": "success",
            "suggestions": suggestions,
            "disease_area": disease_area,
            "treatment_type": treatment_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion error: {str(e)}")


@app.get("/api/assistant/help")
async def assistant_help():
    """
    Muestra la ayuda del asistente y ejemplos de uso
    """
    assistant = get_assistant()
    help_text = await assistant.chat("ayuda")

    return {
        "status": "success",
        "help": help_text,
        "examples": [
            {
                "category": "Conceptos",
                "questions": [
                    "¿Qué es el ICER?",
                    "¿Cómo se calculan los QALYs?",
                    "¿Qué distribución uso para costes en el PSA?"
                ]
            },
            {
                "category": "Configuración",
                "questions": [
                    "¿Qué horizonte temporal uso para oncología?",
                    "¿Cómo configuro un análisis de impacto presupuestario?",
                    "¿Qué estados necesito en un modelo Markov de diabetes?"
                ]
            },
            {
                "category": "Interpretación",
                "questions": [
                    "¿Qué significa un ICER de 25,000 €/QALY?",
                    "¿Mi tratamiento es coste-efectivo?",
                    "¿Cómo interpreto el diagrama tornado?"
                ]
            },
            {
                "category": "HTA",
                "questions": [
                    "¿Qué requisitos tiene NICE para submissions?",
                    "¿Qué tasa de descuento usa la AEMPS?",
                    "¿Cómo justifico mi horizonte temporal?"
                ]
            }
        ]
    }


# ============================================================================
# QUICK-START TEMPLATES
# ============================================================================

@app.get("/api/templates")
async def get_templates():
    """
    Returns pre-configured templates for common analysis scenarios.
    Users can load these as starting points for their analyses.
    """
    return {
        "status": "success",
        "templates": [
            {
                "id": "oncology_nsclc",
                "name": "Oncology - NSCLC",
                "description": "Non-small cell lung cancer with immunotherapy vs chemotherapy",
                "disease_area": "Oncology",
                "parameters": {
                    "time_horizon": 20,
                    "discount_rate": 3.0,
                    "cost_drug_a": 8500,
                    "cost_drug_b": 1200,
                    "cost_stable": 300,
                    "cost_progression": 4500,
                    "prob_progression_a": 8,
                    "prob_progression_b": 15,
                    "utility_stable": 0.78,
                    "utility_progression": 0.45,
                    "wtp_threshold": 30000
                },
                "notes": "Based on typical NSCLC immunotherapy trial data. Adjust progression rates based on specific trial results."
            },
            {
                "id": "oncology_breast",
                "name": "Oncology - Breast Cancer",
                "description": "HER2+ breast cancer with targeted therapy",
                "disease_area": "Oncology",
                "parameters": {
                    "time_horizon": 25,
                    "discount_rate": 3.0,
                    "cost_drug_a": 6000,
                    "cost_drug_b": 800,
                    "cost_stable": 250,
                    "cost_progression": 3800,
                    "prob_progression_a": 6,
                    "prob_progression_b": 12,
                    "utility_stable": 0.82,
                    "utility_progression": 0.50,
                    "wtp_threshold": 30000
                },
                "notes": "HER2+ breast cancer model. Consider adding adverse event costs for targeted therapy."
            },
            {
                "id": "diabetes_t2dm",
                "name": "Diabetes - Type 2",
                "description": "SGLT2 inhibitor vs standard of care in T2DM",
                "disease_area": "Metabolic",
                "parameters": {
                    "time_horizon": 40,
                    "discount_rate": 3.0,
                    "cost_drug_a": 1500,
                    "cost_drug_b": 200,
                    "cost_stable": 150,
                    "cost_progression": 2500,
                    "prob_progression_a": 3,
                    "prob_progression_b": 5,
                    "utility_stable": 0.88,
                    "utility_progression": 0.65,
                    "wtp_threshold": 25000
                },
                "notes": "Long-term T2DM model. Progression represents complications (nephropathy, cardiovascular events)."
            },
            {
                "id": "cardiovascular_hf",
                "name": "Cardiovascular - Heart Failure",
                "description": "Novel therapy for HFrEF",
                "disease_area": "Cardiovascular",
                "parameters": {
                    "time_horizon": 15,
                    "discount_rate": 3.0,
                    "cost_drug_a": 2200,
                    "cost_drug_b": 300,
                    "cost_stable": 400,
                    "cost_progression": 5000,
                    "prob_progression_a": 10,
                    "prob_progression_b": 18,
                    "utility_stable": 0.72,
                    "utility_progression": 0.45,
                    "wtp_threshold": 30000
                },
                "notes": "Heart failure with reduced ejection fraction. Includes hospitalization costs in progression state."
            },
            {
                "id": "autoimmune_ra",
                "name": "Autoimmune - Rheumatoid Arthritis",
                "description": "JAK inhibitor vs biologic DMARD in RA",
                "disease_area": "Autoimmune",
                "parameters": {
                    "time_horizon": 30,
                    "discount_rate": 3.0,
                    "cost_drug_a": 3500,
                    "cost_drug_b": 2800,
                    "cost_stable": 200,
                    "cost_progression": 1800,
                    "prob_progression_a": 5,
                    "prob_progression_b": 8,
                    "utility_stable": 0.80,
                    "utility_progression": 0.55,
                    "wtp_threshold": 30000
                },
                "notes": "Rheumatoid arthritis with active disease. Consider adding joint replacement costs."
            },
            {
                "id": "rare_disease_sma",
                "name": "Rare Disease - SMA",
                "description": "Gene therapy for spinal muscular atrophy",
                "disease_area": "Rare Disease",
                "parameters": {
                    "time_horizon": 50,
                    "discount_rate": 3.0,
                    "cost_drug_a": 150000,
                    "cost_drug_b": 5000,
                    "cost_stable": 2000,
                    "cost_progression": 15000,
                    "prob_progression_a": 2,
                    "prob_progression_b": 12,
                    "utility_stable": 0.70,
                    "utility_progression": 0.35,
                    "wtp_threshold": 100000
                },
                "notes": "Rare disease with one-time gene therapy. Higher WTP threshold often applied for rare diseases."
            }
        ]
    }


@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """
    Returns a specific template by ID
    """
    templates = (await get_templates())["templates"]
    template = next((t for t in templates if t["id"] == template_id), None)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    return {
        "status": "success",
        "template": template
    }


# ============================================================================
# EXPORT PDF ENDPOINTS FOR ALL ANALYSIS TYPES
# ============================================================================

@app.post("/api/export/budget-impact/pdf")
async def export_budget_impact_pdf(request: dict):
    """
    Export Budget Impact Analysis results to professional PDF report
    """
    try:
        # Run BIA
        results = run_budget_impact_analysis(request)

        # Generate PDF
        pdf_bytes = report_service.generate_budget_impact_pdf(
            scenario_name=request.get('scenario_name', 'Budget Impact Analysis'),
            user_email=request.get('user_email', 'anonymous@ecomodel.com'),
            organization=request.get('organization', 'Demo Organization'),
            parameters=request,
            results=results
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=BIA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        print(f"BIA PDF Export Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/export/decision-tree/pdf")
async def export_decision_tree_pdf(request: dict):
    """
    Export Decision Tree Analysis results to professional PDF report
    """
    try:
        # Run Decision Tree Analysis
        results = run_decision_tree_analysis(request)

        # Generate PDF
        pdf_bytes = report_service.generate_decision_tree_pdf(
            scenario_name=request.get('scenario_name', 'Decision Tree Analysis'),
            user_email=request.get('user_email', 'anonymous@ecomodel.com'),
            organization=request.get('organization', 'Demo Organization'),
            parameters=request,
            results=results
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=DecisionTree_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        print(f"Decision Tree PDF Export Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/export/survival/pdf")
async def export_survival_pdf(request: dict):
    """
    Export Survival Analysis results to professional PDF report
    """
    try:
        # Run Survival Analysis
        results = run_survival_analysis(request)

        # Generate PDF
        pdf_bytes = report_service.generate_survival_analysis_pdf(
            scenario_name=request.get('scenario_name', 'Survival Analysis'),
            user_email=request.get('user_email', 'anonymous@ecomodel.com'),
            organization=request.get('organization', 'Demo Organization'),
            parameters=request,
            results=results
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Survival_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        print(f"Survival PDF Export Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/export/voi/pdf")
async def export_voi_pdf(request: dict):
    """
    Export Value of Information Analysis results to professional PDF report
    """
    try:
        # Run VOI Analysis
        results = run_voi_analysis(request)

        # Generate PDF
        pdf_bytes = report_service.generate_voi_analysis_pdf(
            scenario_name=request.get('scenario_name', 'Value of Information Analysis'),
            user_email=request.get('user_email', 'anonymous@ecomodel.com'),
            organization=request.get('organization', 'Demo Organization'),
            parameters=request,
            results=results
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=VOI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        print(f"VOI PDF Export Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/export/markov-flexible/pdf")
async def export_markov_flexible_pdf(request: dict):
    """
    Export Flexible Markov Model results to professional PDF report
    """
    try:
        # Run Flexible Markov Analysis
        results = run_flexible_markov_analysis(request)

        # Generate PDF
        pdf_bytes = report_service.generate_markov_flexible_pdf(
            scenario_name=request.get('scenario_name', 'Flexible Markov Analysis'),
            user_email=request.get('user_email', 'anonymous@ecomodel.com'),
            organization=request.get('organization', 'Demo Organization'),
            parameters=request,
            results=results
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=MarkovFlex_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        print(f"Markov Flexible PDF Export Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
