# 🚀 Cómo Usar EcoModel Hub

## 🌐 ENLACE DIRECTO A LA APLICACIÓN

### Abre este enlace en tu navegador:
```
http://127.0.0.1:8000
```

👆 **¡Es todo lo que necesitas!** No requiere login ni autenticación.

---

## 📊 ¿Qué hace esta aplicación?

Es una **calculadora de análisis farmacoeconómico** que compara dos tratamientos:
- **Fármaco A** (Nuevo)
- **Fármaco B** (Estándar)

Y calcula si el Fármaco A es **coste-efectivo** comparado con el estándar.

---

## 🎮 Cómo Usarla

### 1. Ajusta los Parámetros (Panel Izquierdo)

Puedes modificar:

**💰 Costes:**
- Coste anual del Fármaco Nuevo
- Coste anual del Fármaco Estándar
- Coste de seguimiento
- Coste de progresión/hospitalización

**📈 Eficacia Clínica:**
- Tasa de progresión con Fármaco A (10% = mejor)
- Tasa de progresión con Fármaco B (25% = peor)

**⏱️ Horizonte Temporal:**
- 5, 10, 15 o 20 años

### 2. Haz Click en "🚀 Ejecutar Análisis"

La aplicación calculará automáticamente.

### 3. Ve los Resultados (Panel Derecho)

Obtendrás:

**ICER** (Ratio Coste-Efectividad Incremental)
- Es el coste adicional por cada año de vida con calidad ganado
- **Si ICER < 30,000 EUR/QALY** → ✅ Coste-Efectivo
- **Si ICER > 30,000 EUR/QALY** → ⚠️ No Coste-Efectivo

**Coste Incremental**
- Cuánto dinero extra cuesta el Fármaco A vs B

**QALYs Ganados**
- Años de vida ajustados por calidad que se ganan

**Comparación Detallada**
- Costes totales de ambos tratamientos
- QALYs totales de ambos tratamientos

---

## 📖 Ejemplo de Interpretación

Imagina que obtienes:

```
ICER: 26,450 EUR/QALY
Coste Incremental: +122,000 EUR
QALYs Ganados: +4.61

Conclusión: ✅ Coste-Efectivo
```

**Esto significa:**
- El Fármaco A cuesta 122,000 EUR más por paciente
- Pero proporciona 4.61 años más de vida con calidad
- Cada año de vida con calidad ganado cuesta 26,450 EUR
- Como está por debajo de 30,000 EUR/QALY, es **coste-efectivo** en España

---

## 🎯 Casos de Uso

### Ejemplo 1: Fármaco muy caro
- Coste Drug A: **10,000 €/año**
- Coste Drug B: **500 €/año**
- Resultado: Probablemente **NO coste-efectivo** (ICER alto)

### Ejemplo 2: Fármaco moderado con buena eficacia
- Coste Drug A: **3,500 €/año**
- Tasa progresión A: **8%**
- Tasa progresión B: **25%**
- Resultado: Probablemente **SÍ coste-efectivo** (mejor beneficio clínico)

### Ejemplo 3: Fármaco barato
- Coste Drug A: **2,000 €/año**
- Coste Drug B: **500 €/año**
- Resultado: Muy probablemente **SÍ coste-efectivo**

---

## ⚙️ Parámetros Técnicos Fijos

Estos valores están fijos en el modelo (puedes cambiarlos en el código si necesitas):

- **Utilidad Estado Estable**: 0.85 (calidad de vida buena)
- **Utilidad Estado Progresión**: 0.50 (calidad de vida deteriorada)
- **Mortalidad desde Estable**: 2% anual
- **Mortalidad desde Progresión**: 15% anual
- **Tasa de Descuento**: 3% anual (estándar en España)
- **Tamaño de Cohorte**: 1,000 pacientes

---

## 🔄 Para Volver a Ejecutar

Simplemente ajusta los sliders y vuelve a hacer click en **"Ejecutar Análisis"**.

Los cálculos son instantáneos (menos de 1 segundo).

---

## 🛑 Para Cerrar la Aplicación

En la terminal donde ejecutaste el servidor, presiona `Ctrl+C`

O simplemente cierra la ventana del navegador y ya está.

---

## 🎨 Características de la Interfaz

✨ **Sin login**: No necesitas crear cuenta ni autenticarte
✨ **Interfaz visual**: Sliders y colores para facilitar el uso
✨ **Resultados en tiempo real**: Cálculos instantáneos
✨ **Responsive**: Funciona en móvil, tablet y ordenador
✨ **Fácil de entender**: Números grandes y conclusiones claras

---

## 💡 Tips

1. **Prueba diferentes escenarios** moviendo los sliders
2. **Observa cómo cambia el ICER** al variar costes y eficacia
3. **El horizonte temporal** afecta significativamente los resultados
4. **Tasa de progresión más baja** (mejor eficacia) → mejor ICER

---

## 📧 ¿Necesitas Ayuda?

Si tienes dudas sobre cómo interpretar los resultados, consulta la documentación de farmacoeconomía o contacta con tu equipo de HEOR.

---

**¡Disfruta analizando modelos farmacoeconómicos!** 🏥💊📊
