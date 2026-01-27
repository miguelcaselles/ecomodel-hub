"""
AI Assistant for Pharmacoeconomic Analysis
Asistente de IA para análisis farmacoeconómicos

Proporciona:
- Interpretación de resultados en lenguaje natural
- Guía para configuración de modelos
- Generación de resúmenes ejecutivos
- Respuestas a preguntas sobre análisis
- Recomendaciones basadas en mejores prácticas HTA
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import httpx
from abc import ABC, abstractmethod


class LLMProvider(str, Enum):
    """Proveedores de LLM soportados"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"  # Para modelos locales (Ollama, etc.)


@dataclass
class AssistantConfig:
    """Configuración del asistente"""
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4o-mini"  # Modelo por defecto (económico y rápido)
    api_key: Optional[str] = None
    temperature: float = 0.3  # Bajo para respuestas más consistentes
    max_tokens: int = 2000
    language: str = "es"  # Español por defecto


class BaseLLMClient(ABC):
    """Clase base para clientes LLM"""

    @abstractmethod
    async def complete(self, messages: List[Dict], **kwargs) -> str:
        pass


class OpenAIClient(BaseLLMClient):
    """Cliente para OpenAI API"""

    def __init__(self, config: AssistantConfig):
        self.config = config
        self.api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def complete(self, messages: List[Dict], **kwargs) -> str:
        if not self.api_key:
            return self._fallback_response(messages)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": kwargs.get("model", self.config.model),
                        "messages": messages,
                        "temperature": kwargs.get("temperature", self.config.temperature),
                        "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                return self._fallback_response(messages, str(e))

    def _fallback_response(self, messages: List[Dict], error: str = None) -> str:
        """Respuesta de fallback cuando no hay API disponible"""
        return PharmacoeconomicsExpert.generate_offline_response(messages, error)


class AnthropicClient(BaseLLMClient):
    """Cliente para Anthropic API (Claude)"""

    def __init__(self, config: AssistantConfig):
        self.config = config
        self.api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def complete(self, messages: List[Dict], **kwargs) -> str:
        if not self.api_key:
            return PharmacoeconomicsExpert.generate_offline_response(messages)

        # Convertir formato OpenAI a Anthropic
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        conversation = [m for m in messages if m["role"] != "system"]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers={
                        "x-api-key": self.api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": kwargs.get("model", "claude-3-haiku-20240307"),
                        "system": system_msg,
                        "messages": conversation,
                        "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
            except Exception:
                return PharmacoeconomicsExpert.generate_offline_response(messages)


class PharmacoeconomicsExpert:
    """
    Experto en farmacoeconomía basado en reglas
    Funciona sin conexión a LLM externo
    """

    SYSTEM_PROMPT = """Eres un experto en farmacoeconomía y evaluación de tecnologías sanitarias (HTA).
Tu rol es ayudar a usuarios a:
1. Interpretar resultados de análisis coste-efectividad
2. Configurar modelos económicos correctamente
3. Entender conceptos como ICER, QALY, PSA, BIA
4. Cumplir con requisitos de agencias HTA (NICE, AEMPS, etc.)

Responde siempre en español de forma clara y accesible.
Usa ejemplos concretos cuando sea posible.
Si detectas valores inusuales, advierte al usuario."""

    # Base de conocimiento para respuestas offline
    KNOWLEDGE_BASE = {
        "icer": {
            "definition": "El ICER (Incremental Cost-Effectiveness Ratio) representa el coste adicional por cada unidad adicional de efectividad (generalmente QALY) ganada con el nuevo tratamiento.",
            "interpretation": {
                "negative_cost_positive_effect": "Dominante: el nuevo tratamiento es más barato Y más efectivo. Decisión clara a favor.",
                "positive_cost_positive_effect": "Cuadrante NE: más caro pero más efectivo. Comparar ICER con umbral de disponibilidad a pagar.",
                "positive_cost_negative_effect": "Dominado: más caro Y menos efectivo. No recomendable.",
                "negative_cost_negative_effect": "Cuadrante SW: más barato pero menos efectivo. Decisión depende del trade-off aceptable."
            },
            "thresholds": {
                "spain": "20,000-30,000 €/QALY (AEMPS)",
                "uk": "20,000-30,000 £/QALY (NICE)",
                "who": "1-3x PIB per cápita"
            }
        },
        "qaly": {
            "definition": "QALY (Quality-Adjusted Life Year) combina cantidad y calidad de vida. 1 QALY = 1 año de vida en perfecta salud.",
            "range": "0 (muerte) a 1 (salud perfecta). Valores negativos posibles para estados peores que muerte."
        },
        "psa": {
            "definition": "El PSA (Probabilistic Sensitivity Analysis) evalúa la incertidumbre del modelo mediante simulaciones Monte Carlo.",
            "interpretation": "Genera miles de escenarios variando parámetros según sus distribuciones de probabilidad.",
            "outputs": ["Scatter plot en plano coste-efectividad", "CEAC (curva de aceptabilidad)", "Intervalos de confianza"]
        },
        "bia": {
            "definition": "El BIA (Budget Impact Analysis) estima el impacto financiero de introducir un nuevo tratamiento en el sistema sanitario.",
            "time_horizon": "Típicamente 3-5 años",
            "perspective": "Generalmente perspectiva del pagador (SNS)"
        }
    }

    @classmethod
    def generate_offline_response(cls, messages: List[Dict], error: str = None) -> str:
        """Genera respuesta sin LLM externo usando base de conocimiento"""
        user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        user_msg_lower = user_msg.lower()

        # Detectar intención
        if any(word in user_msg_lower for word in ["icer", "coste-efectividad", "incremental"]):
            return cls._explain_icer(user_msg_lower)
        elif any(word in user_msg_lower for word in ["qaly", "avac", "utilidad"]):
            return cls._explain_qaly()
        elif any(word in user_msg_lower for word in ["psa", "probabilístico", "monte carlo"]):
            return cls._explain_psa()
        elif any(word in user_msg_lower for word in ["bia", "impacto presupuestario", "budget"]):
            return cls._explain_bia()
        elif any(word in user_msg_lower for word in ["resultado", "interpretar", "significa"]):
            return cls._interpret_results_generic()
        elif any(word in user_msg_lower for word in ["configur", "parámetro", "cómo"]):
            return cls._configuration_guide()
        else:
            return cls._general_help(error)

    @classmethod
    def _explain_icer(cls, context: str) -> str:
        kb = cls.KNOWLEDGE_BASE["icer"]
        response = f"""## ICER (Ratio Coste-Efectividad Incremental)

**Definición:** {kb['definition']}

**Fórmula:** ICER = (Coste_nuevo - Coste_comparador) / (Efectividad_nuevo - Efectividad_comparador)

### Interpretación según cuadrante:

| Situación | Interpretación |
|-----------|----------------|
| Más barato + Más efectivo | ✅ **Dominante** - Decisión clara |
| Más caro + Más efectivo | ⚖️ Comparar con umbral WTP |
| Más caro + Menos efectivo | ❌ **Dominado** - No recomendable |
| Más barato + Menos efectivo | 🔄 Trade-off a evaluar |

### Umbrales de referencia:
- **España (AEMPS):** {kb['thresholds']['spain']}
- **Reino Unido (NICE):** {kb['thresholds']['uk']}
- **OMS:** {kb['thresholds']['who']}

💡 **Consejo:** Un ICER por debajo del umbral sugiere que el tratamiento es coste-efectivo."""
        return response

    @classmethod
    def _explain_qaly(cls) -> str:
        kb = cls.KNOWLEDGE_BASE["qaly"]
        return f"""## QALY (Año de Vida Ajustado por Calidad)

**Definición:** {kb['definition']}

**Rango:** {kb['range']}

### Ejemplos de utilidades típicas:
| Estado de salud | Utilidad |
|-----------------|----------|
| Salud perfecta | 1.00 |
| Diabetes controlada | 0.80-0.85 |
| Cáncer en remisión | 0.70-0.80 |
| Insuficiencia cardíaca | 0.50-0.70 |
| Enfermedad terminal | 0.20-0.40 |

### Cómo calcular QALYs:
**QALYs = Tiempo × Utilidad**

Ejemplo: 5 años con utilidad 0.8 = 4 QALYs

💡 **Consejo:** Usa valores de utilidad de la literatura publicada (EQ-5D, SF-6D) para mayor credibilidad ante agencias HTA."""

    @classmethod
    def _explain_psa(cls) -> str:
        kb = cls.KNOWLEDGE_BASE["psa"]
        return f"""## PSA (Análisis de Sensibilidad Probabilístico)

**Definición:** {kb['definition']}

**Cómo funciona:** {kb['interpretation']}

### Distribuciones recomendadas:
| Tipo de parámetro | Distribución |
|-------------------|--------------|
| Probabilidades | Beta |
| Costes | Gamma o Log-normal |
| Utilidades | Beta |
| Hazard ratios | Log-normal |
| Conteos | Poisson |

### Outputs principales:
- **Scatter plot:** Muestra dispersión de resultados en plano CE
- **CEAC:** Probabilidad de ser coste-efectivo según umbral WTP
- **Intervalos de confianza:** IC 95% para ICER

💡 **Consejo:** Usa al menos 1,000 iteraciones. Para publicación, 10,000 es más robusto."""

    @classmethod
    def _explain_bia(cls) -> str:
        kb = cls.KNOWLEDGE_BASE["bia"]
        return f"""## BIA (Análisis de Impacto Presupuestario)

**Definición:** {kb['definition']}

**Horizonte temporal:** {kb['time_horizon']}
**Perspectiva:** {kb['perspective']}

### Componentes clave:
1. **Población elegible:** Prevalencia × Diagnóstico × Elegibilidad
2. **Cuotas de mercado:** Escenario actual vs. nuevo
3. **Costes por paciente:** Fármaco + Administración + Monitorización
4. **Curva de adopción:** Cómo penetra el nuevo tratamiento

### Escenarios típicos:
- **Conservador:** Adopción lenta (10-20% en 5 años)
- **Base:** Adopción moderada (30% en 5 años)
- **Optimista:** Adopción rápida (50%+ en 5 años)

💡 **Consejo:** Las agencias HTA esperan ver impacto por año y acumulado. Incluye análisis de sensibilidad sobre tasa de adopción."""

    @classmethod
    def _interpret_results_generic(cls) -> str:
        return """## Guía de Interpretación de Resultados

### Para Análisis Coste-Efectividad:
1. **Revisa el ICER:** ¿Está por debajo del umbral de tu país?
2. **Mira los QALYs:** ¿La ganancia es clínicamente relevante?
3. **Evalúa la incertidumbre:** ¿Qué dice el PSA?

### Para Budget Impact:
1. **Impacto año 1:** ¿Es manejable?
2. **Impacto acumulado:** ¿Sostenible a 5 años?
3. **Pico de gasto:** ¿Cuándo ocurre?

### Preguntas clave:
- ¿Los resultados son sensibles a algún parámetro?
- ¿La probabilidad de ser coste-efectivo supera 50%?
- ¿El impacto presupuestario es asumible?

📊 **Comparte tus resultados** y te ayudo a interpretarlos en detalle."""

    @classmethod
    def _configuration_guide(cls) -> str:
        return """## Guía de Configuración de Modelos

### Modelo Markov (3 estados):
| Parámetro | Típico | Fuente |
|-----------|--------|--------|
| Horizonte | 10-20 años | Guías HTA |
| Tasa descuento | 3-3.5% | País específico |
| Tamaño cohorte | 1,000 | Convención |

### Probabilidades de transición:
- **De ensayo clínico:** Convertir tasas a probabilidades
- **Fórmula:** p = 1 - exp(-rate × time)

### Costes:
- Usar **costes unitarios oficiales** (BOT, tarifas SNS)
- Incluir: fármaco + administración + monitorización + eventos adversos

### Utilidades:
- Preferir **EQ-5D** (aceptado por NICE, AEMPS)
- Si no disponible, SF-6D o mapeo

💡 **Consejo:** Documenta TODAS las fuentes. Las agencias HTA valoran la transparencia."""

    @classmethod
    def _general_help(cls, error: str = None) -> str:
        msg = """## 👋 ¡Hola! Soy tu asistente de farmacoeconomía

Puedo ayudarte con:

1. **📊 Interpretar resultados** - Explico qué significan ICER, QALYs, etc.
2. **⚙️ Configurar modelos** - Te guío en los parámetros correctos
3. **📝 Generar informes** - Creo resúmenes ejecutivos
4. **❓ Resolver dudas** - Respondo preguntas sobre HTA

### Ejemplos de preguntas:
- "¿Qué significa un ICER de 25,000 €/QALY?"
- "¿Cómo configuro un análisis de impacto presupuestario?"
- "¿Qué distribución uso para costes en el PSA?"
- "Interpreta estos resultados: [pega tus datos]"

**Escribe tu pregunta y te ayudo.**"""

        if error:
            msg += f"\n\n⚠️ *Nota: Funcionando en modo offline. {error}*"

        return msg


class PharmEconAssistant:
    """
    Asistente principal de farmacoeconomía

    Combina LLM externo (cuando disponible) con base de conocimiento local.
    """

    def __init__(self, config: Optional[AssistantConfig] = None):
        self.config = config or AssistantConfig()
        self.conversation_history: List[Dict] = []
        self.analysis_context: Dict = {}

        # Inicializar cliente según proveedor
        if self.config.provider == LLMProvider.OPENAI:
            self.client = OpenAIClient(self.config)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            self.client = AnthropicClient(self.config)
        else:
            self.client = None

    def set_analysis_context(self, context: Dict):
        """Establecer contexto del análisis actual"""
        self.analysis_context = context

    def clear_history(self):
        """Limpiar historial de conversación"""
        self.conversation_history = []

    async def chat(self, user_message: str) -> str:
        """
        Procesar mensaje del usuario y generar respuesta

        Args:
            user_message: Mensaje del usuario

        Returns:
            Respuesta del asistente
        """
        # Construir mensajes con contexto
        messages = self._build_messages(user_message)

        # Añadir a historial
        self.conversation_history.append({"role": "user", "content": user_message})

        # Obtener respuesta
        if self.client:
            response = await self.client.complete(messages)
        else:
            response = PharmacoeconomicsExpert.generate_offline_response(messages)

        # Guardar respuesta en historial
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def _build_messages(self, user_message: str) -> List[Dict]:
        """Construir lista de mensajes con sistema y contexto"""
        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]

        # Añadir contexto del análisis si existe
        if self.analysis_context:
            context_msg = f"Contexto del análisis actual:\n```json\n{json.dumps(self.analysis_context, indent=2, ensure_ascii=False)}\n```"
            messages.append({"role": "system", "content": context_msg})

        # Añadir historial reciente (últimos 10 mensajes)
        messages.extend(self.conversation_history[-10:])

        # Añadir mensaje actual
        messages.append({"role": "user", "content": user_message})

        return messages

    def _build_system_prompt(self) -> str:
        """Construir prompt de sistema"""
        return f"""{PharmacoeconomicsExpert.SYSTEM_PROMPT}

Información adicional:
- Idioma preferido: {self.config.language}
- Plataforma: EcoModel Hub v2.0
- Módulos disponibles: Markov, Decision Tree, BIA, PSA, Tornado, Survival Analysis, EVPI/EVPPI

Cuando interpretes resultados:
1. Sé específico con los números
2. Compara con umbrales estándar
3. Destaca incertidumbres
4. Sugiere próximos pasos

Formato de respuesta:
- Usa markdown para mejor legibilidad
- Incluye tablas cuando sea útil
- Usa emojis con moderación para destacar puntos clave"""

    async def interpret_results(self, results: Dict, analysis_type: str) -> str:
        """
        Interpretar resultados de un análisis

        Args:
            results: Resultados del análisis
            analysis_type: Tipo de análisis (markov, bia, psa, etc.)

        Returns:
            Interpretación en lenguaje natural
        """
        self.set_analysis_context(results)

        prompts = {
            "markov": "Interpreta estos resultados de análisis Markov coste-efectividad. Explica el ICER, si es coste-efectivo, y qué significa para la toma de decisiones.",
            "bia": "Interpreta este análisis de impacto presupuestario. Explica el impacto por año, el impacto acumulado, y si es asumible para el sistema sanitario.",
            "psa": "Interpreta estos resultados del análisis de sensibilidad probabilístico. Explica la incertidumbre, la probabilidad de ser coste-efectivo, y qué parámetros generan más variabilidad.",
            "tornado": "Interpreta este diagrama tornado. Identifica los parámetros más influyentes y qué significa para la robustez de los resultados.",
            "decision_tree": "Interpreta estos resultados del árbol de decisión. Explica la estrategia óptima y el valor esperado.",
            "survival": "Interpreta este análisis de supervivencia. Explica el ajuste del modelo, la mediana de supervivencia, y las implicaciones para el modelo económico.",
            "voi": "Interpreta estos resultados del valor de información. Explica el EVPI, qué parámetros priorizar para investigación futura, y si vale la pena invertir en más estudios."
        }

        prompt = prompts.get(analysis_type, "Interpreta estos resultados y explica qué significan.")

        return await self.chat(prompt)

    async def generate_executive_summary(self, all_results: Dict) -> str:
        """
        Generar resumen ejecutivo de todos los análisis

        Args:
            all_results: Diccionario con todos los resultados

        Returns:
            Resumen ejecutivo en formato markdown
        """
        self.set_analysis_context(all_results)

        prompt = """Genera un RESUMEN EJECUTIVO profesional de estos análisis farmacoeconómicos.

El resumen debe incluir:
1. **Conclusión principal** (1-2 frases)
2. **Resultados clave** (bullet points)
3. **Incertidumbre** (¿qué tan seguros estamos?)
4. **Recomendación** (¿qué debería hacer el decisor?)
5. **Limitaciones** (¿qué no captura el modelo?)

Formato: profesional pero accesible, apto para directivos no técnicos.
Extensión: máximo 500 palabras."""

        return await self.chat(prompt)

    async def suggest_parameters(self, disease_area: str, treatment_type: str) -> str:
        """
        Sugerir parámetros basados en área terapéutica

        Args:
            disease_area: Área de enfermedad (oncología, cardiovascular, etc.)
            treatment_type: Tipo de tratamiento (oral, IV, etc.)

        Returns:
            Sugerencias de parámetros
        """
        prompt = f"""Sugiere parámetros típicos para un modelo farmacoeconómico en:
- Área terapéutica: {disease_area}
- Tipo de tratamiento: {treatment_type}

Incluye:
1. Horizonte temporal recomendado
2. Estados del modelo Markov típicos
3. Rangos de utilidades esperados
4. Tipos de costes a incluir
5. Fuentes de datos recomendadas

Basa tus sugerencias en literatura publicada y guías HTA."""

        return await self.chat(prompt)


# Instancia global del asistente
_assistant_instance: Optional[PharmEconAssistant] = None


def get_assistant() -> PharmEconAssistant:
    """Obtener instancia del asistente (singleton)"""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = PharmEconAssistant()
    return _assistant_instance


async def quick_interpret(results: Dict, analysis_type: str) -> str:
    """Función de conveniencia para interpretación rápida"""
    assistant = get_assistant()
    return await assistant.interpret_results(results, analysis_type)
