# 📊 Estado Actual de Funcionalidades - EcoModel Hub

## ✅ IMPLEMENTADO Y FUNCIONANDO

### 1. Backend Completo
- ✅ **41 API endpoints** implementados y documentados
- ✅ **Multi-tenancy**: Sistema de organizaciones con permisos
- ✅ **Autenticación JWT**: Login, logout, refresh tokens
- ✅ **RBAC**: 3 roles (global_admin, local_user, viewer)
- ✅ **Base de datos**: SQLite con 6 tablas relacionales
- ✅ **Motor de cálculo dual**:
  - Motor Python (NumPy) - Rápido
  - Motor R (heemod) - Profesional HEOR
- ✅ **Análisis de sensibilidad**:
  - Determinístico
  - Tornado (one-way SA)
  - PSA (Monte Carlo)

### 2. Interfaz Visual Básica
- ✅ **Diseño profesional minimalista**: Blanco/gris/azul corporativo
- ✅ **Responsive**: Móvil, tablet, desktop
- ✅ **Tabs organizadas**: Costs, Clinical, Settings
- ✅ **Sliders interactivos**: Con valores en tiempo real
- ✅ **Gráfico CE Plane**: Con línea WTP threshold
- ✅ **Tabla comparativa**: Drug A vs Drug B
- ✅ **KPI cards**: ICER, ΔQALYs, ΔCosts, Conclusión

### 3. Motor R Integration
- ✅ **rpy2 instalado y funcional**
- ✅ **Paquetes R**: heemod, flexsurv, survival, dplyr, ggplot2
- ✅ **Wrapper Python → R**: HeemodWrapper completo
- ✅ **Generador de código R auditable**: Para transparencia

---

## ❌ FALTA PARA SER OPERATIVO EN PHARMA

### Crítico (Bloqueantes para uso real)

#### 1. ❌ Gestión de Modelos en UI
**Estado**: Backend completo, UI sin implementar

**Lo que falta**:
- Panel para crear nuevos modelos
- Lista de modelos disponibles
- Selector de modelo activo
- Editor de parámetros del modelo
- Publicar/despublicar modelos

**Impacto**: Sin esto, solo hay UN modelo fijo. Pharma necesita múltiples modelos.

**Endpoints disponibles**:
```
✅ GET    /api/v1/models              # Listar
✅ POST   /api/v1/models              # Crear
✅ GET    /api/v1/models/{id}         # Ver detalles
✅ PATCH  /api/v1/models/{id}         # Editar
✅ POST   /api/v1/models/{id}/publish # Publicar
```

#### 2. ❌ Gestión de Escenarios en UI
**Estado**: Backend completo, UI sin implementar

**Lo que falta**:
- Guardar configuraciones actuales como escenario
- Listar escenarios guardados
- Cargar escenario guardado
- Clonar escenario (base case → optimistic)
- Comparar múltiples escenarios

**Impacto**: No se puede guardar trabajo. Cada análisis se pierde al refrescar.

**Endpoints disponibles**:
```
✅ GET    /api/v1/scenarios           # Listar
✅ POST   /api/v1/scenarios           # Crear
✅ GET    /api/v1/scenarios/{id}      # Ver
✅ PATCH  /api/v1/scenarios/{id}      # Editar
✅ POST   /api/v1/scenarios/{id}/clone # Clonar
```

#### 3. ❌ Análisis PSA Completo en UI
**Estado**: Backend funcional, UI parcial

**Lo que falta**:
- Botón "Run PSA" (1000+ iterations)
- CEAC Curve (Cost-Effectiveness Acceptability Curve)
- Scatter plot PSA (nube de puntos)
- Percentiles (P2.5, P50, P97.5)
- Progress bar para PSA largo

**Impacto**: PSA es OBLIGATORIO para agencias HTA (NICE, GHEOR).

**Endpoint disponible**:
```
✅ POST /api/v1/simulations/psa
```

#### 4. ❌ Generación de Reportes PDF
**Estado**: No implementado

**Lo que falta**:
- Generar PDF con WeasyPrint
- Template Jinja2 profesional
- Incluir todos los gráficos (CE Plane, Tornado, CEAC, PSA scatter)
- Incluir código R auditable
- Logo de organización
- Footer con metadata

**Impacto**: CRÍTICO. Reportes PDF son entregable final para reguladores.

**Necesita implementar**:
```
❌ POST /api/v1/reports/generate
❌ GET  /api/v1/reports/{id}/download
```

#### 5. ❌ Autenticación en UI
**Estado**: Backend completo, UI sin login

**Lo que falta**:
- Página de login
- Almacenar JWT token
- Headers Authorization en requests
- Logout
- Refresh token automático

**Impacto**: Multi-tenancy inútil sin login. Todos ven todo.

**Endpoints disponibles**:
```
✅ POST /api/v1/auth/login
✅ POST /api/v1/auth/logout
```

---

### Importante (Reducen valor pero no bloqueantes)

#### 6. ❌ Diseñador Visual Drag & Drop
**Estado**: No implementado

**Lo que falta**:
- Canvas para arrastrar estados
- Conectar estados con flechas (transiciones)
- Edit properties de estados (cost, utility)
- Edit probabilities de transiciones
- Validación (suma probabilidades = 1)
- Export a JSON structure

**Impacto**: Sin esto, usuario debe editar JSON manualmente. Menos user-friendly.

**Tecnología sugerida**: React Flow o Cytoscape.js

#### 7. ❌ Tornado Diagram en UI
**Estado**: Backend funcional, UI sin implementar

**Lo que falta**:
- Botón "Run Tornado"
- Gráfico horizontal bar chart
- Ranking de parámetros por impacto
- Valores high/low para cada parámetro

**Impacto**: Tornado es estándar en HEOR. Falta dificulta análisis.

**Endpoint disponible**:
```
✅ POST /api/v1/simulations/tornado
```

#### 8. ❌ Export Excel
**Estado**: No implementado

**Lo que falta**:
- Botón "Export to Excel"
- Tablas formateadas con openpyxl
- Múltiples sheets (Results, Parameters, PSA, Tornado)
- Conditional formatting

**Impacto**: Excel es universal en pharma. Facilita integración con workflows existentes.

#### 9. ❌ Budget Impact Model (BIM)
**Estado**: No implementado

**Lo que falta**:
- Módulo BIM separado
- Market share scenarios
- Patient flow modeling
- Multi-year projections
- Epidemiology inputs

**Impacto**: BIM es REQUERIDO por muchas agencias HTA además de CEA.

#### 10. ❌ Digitalizador de Curvas KM
**Estado**: No implementado

**Lo que falta**:
- Upload imagen de curva Kaplan-Meier
- OCR/click para marcar puntos
- Fit paramétrico (Weibull, Gompertz, etc.)
- Export survival parameters

**Impacto**: Ahorra mucho tiempo en data entry de curvas publicadas.

---

## 🎯 Priorización para Hacer Operativo

### Sprint 1 (1-2 semanas) - MVP Operativo
1. ✅ Autenticación en UI (login page, JWT storage)
2. ✅ Gestión de escenarios (guardar, cargar, listar)
3. ✅ PSA completo en UI (CEAC curve, scatter plot)
4. ✅ Export código R auditable desde UI

**Resultado**: Plataforma usable por pharma, puede guardar trabajo, ejecutar PSA completo.

### Sprint 2 (2 semanas) - Reportes y Análisis Completo
5. ✅ Generación de reportes PDF (WeasyPrint + Jinja2)
6. ✅ Tornado diagram en UI
7. ✅ Gestión de modelos en UI (crear, listar, seleccionar)
8. ✅ Comparación de escenarios (side-by-side)

**Resultado**: Plataforma completa para CEA, genera entregables profesionales.

### Sprint 3 (2-3 semanas) - Features Avanzados
9. ✅ Export Excel completo
10. ✅ BIM module básico
11. ✅ Diseñador visual drag & drop (React Flow)
12. ✅ Validación cruzada Python/R

**Resultado**: Plataforma best-in-class con features diferenciadores.

### Sprint 4 (1-2 semanas) - Polish
13. ✅ Digitalizador de curvas KM
14. ✅ Dashboard ejecutivo
15. ✅ Audit trail (log de cambios)
16. ✅ Colaboración (comentarios, versioning)

**Resultado**: Plataforma enterprise-ready.

---

## 📊 Matriz de Decisión

| Feature | Criticidad | Complejidad | Tiempo | Prioridad |
|---------|-----------|-------------|---------|-----------|
| Autenticación UI | 🔴 Alta | 🟢 Baja | 1 día | **1** |
| Gestión escenarios UI | 🔴 Alta | 🟡 Media | 2 días | **2** |
| PSA completo UI | 🔴 Alta | 🟡 Media | 2 días | **3** |
| Export código R | 🔴 Alta | 🟢 Baja | 1 día | **4** |
| Reportes PDF | 🔴 Alta | 🟡 Media | 3 días | **5** |
| Tornado UI | 🟡 Media | 🟢 Baja | 1 día | **6** |
| Gestión modelos UI | 🟡 Media | 🟡 Media | 2 días | **7** |
| Export Excel | 🟡 Media | 🟢 Baja | 1 día | **8** |
| BIM module | 🟡 Media | 🔴 Alta | 5 días | **9** |
| Diseñador visual | 🟢 Baja | 🔴 Alta | 7 días | **10** |
| Digitalizador KM | 🟢 Baja | 🔴 Alta | 5 días | **11** |

🔴 Alta | 🟡 Media | 🟢 Baja

---

## 🚀 Recomendación Inmediata

**Implementar AHORA (Sprint 1)**:

1. **Login page + JWT storage** (1 día)
   - Permite multi-tenancy real
   - Cada usuario ve solo sus modelos

2. **Guardar/Cargar escenarios** (2 días)
   - Botón "Save Scenario"
   - Dropdown "Load Scenario"
   - No perder trabajo al refrescar

3. **PSA completo** (2 días)
   - Botón "Run PSA (1000 iterations)"
   - CEAC curve chart
   - PSA scatter plot
   - Percentiles table

4. **Export código R** (1 día)
   - Botón "Export R Code"
   - Download .R file
   - Ejecutable en RStudio

**Total**: ~6 días de desarrollo

**Resultado**: Plataforma MVP+ operativa para pharma.

---

## 📝 Notas Adicionales

### ¿Por qué estas 4 features primero?

1. **Autenticación**: Sin esto, multi-tenancy es inútil
2. **Escenarios**: Sin esto, no se puede guardar trabajo
3. **PSA**: Sin esto, análisis incompleto (agencias HTA lo requieren)
4. **Export R**: Sin esto, no hay transparencia (requisito regulatorio)

### ¿Qué pasa con el diseñador visual?

Es **nice-to-have**, no **must-have**. Razones:

- Usuarios HEOR están acostumbrados a Excel/código
- Editar JSON parameters es aceptable para MVP
- Diseñador visual toma ~1 semana de desarrollo
- Mejor priorizar funcionalidad core primero

Se puede añadir en Sprint 3 cuando core esté completo.

---

**Última actualización**: 2026-01-19
**Estado**: Documentación completa - Listo para implementar Sprint 1
