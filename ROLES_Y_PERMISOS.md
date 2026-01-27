# 🔐 Roles y Permisos - EcoModel Hub

## Resumen de Roles

EcoModel Hub implementa un sistema de control de acceso basado en roles (RBAC) con 3 niveles de permisos:

---

## 👑 Global Admin (Administrador Global)

### Identificación Visual
- **Badge**: Rojo con icono 👑
- **Color**: `#DC2626` (rojo)
- **Label**: "ADMIN"

### Permisos y Acceso

✅ **Acceso Completo:**
- Crear y gestionar organizaciones
- Crear modelos económicos (Model Builder)
- Publicar/despublicar modelos
- Crear y editar parámetros de modelos
- Gestionar usuarios (crear, editar, eliminar)
- Acceder a datos de todas las organizaciones
- Ver y gestionar todos los escenarios
- Ejecutar simulaciones
- Generar reportes PDF/Excel

✅ **Funcionalidades Exclusivas:**
- **Model Builder** visible en el header
- Acceso a `/model-builder`
- Endpoint `/api/v1/models` (POST, PATCH, DELETE)
- Endpoint `/api/v1/organizations` (CRUD completo)
- Endpoint `/api/v1/users` (CRUD completo)

### Banner en la Interfaz
```
┌──────────────────────────────────────────────────────┐
│ 👑  Administrator Mode                               │
│                                                      │
│ Full access: You can create models, manage          │
│ organizations, and perform all actions. Use the     │
│ Model Builder to create new economic models.        │
└──────────────────────────────────────────────────────┘
```

### Usuario de Prueba
- **Email**: `admin@ecomodel.com`
- **Password**: `admin123`

---

## 💼 Local User (Usuario Local)

### Identificación Visual
- **Badge**: Azul con icono 💼
- **Color**: `#3B82F6` (azul)
- **Label**: "USER"

### Permisos y Acceso

✅ **Puede:**
- Ver modelos económicos publicados
- Crear escenarios para su organización
- Editar sus propios escenarios
- Ejecutar simulaciones (Determinística, Tornado, PSA)
- Generar reportes PDF/Excel
- Descargar resultados
- Clonar escenarios existentes
- Ver datos de su organización únicamente

❌ **NO Puede:**
- Crear modelos económicos
- Acceder al Model Builder
- Ver datos de otras organizaciones
- Gestionar usuarios
- Crear organizaciones
- Modificar parámetros de modelos globales

### Banner en la Interfaz
```
┌──────────────────────────────────────────────────────┐
│ 💼  Local User Mode                                  │
│                                                      │
│ You can create scenarios, run simulations, and     │
│ generate reports for your organization.             │
└──────────────────────────────────────────────────────┘
```

### Usuario de Prueba
- **Email**: `spain@ecomodel.com`
- **Password**: `spain123`
- **Organización**: Spain HTA

---

## 👁️ Viewer (Observador)

### Identificación Visual
- **Badge**: Gris con icono 👁️
- **Color**: `#6B7280` (gris)
- **Label**: "VIEWER"

### Permisos y Acceso

✅ **Puede:**
- Ver modelos económicos publicados
- Ver escenarios de su organización
- Ver resultados de simulaciones
- Descargar reportes PDF/Excel
- Ver gráficos y visualizaciones

❌ **NO Puede:**
- Crear escenarios
- Editar escenarios
- Eliminar escenarios
- Ejecutar simulaciones
- Modificar parámetros
- Guardar cambios
- Acceder al Model Builder
- Ver datos de otras organizaciones

### Restricciones en la Interfaz
- Todos los botones de "Save", "Delete", "Run" están **deshabilitados**
- Opacidad reducida (0.5) en controles no permitidos
- Tooltip: "Viewers cannot modify data"
- Cursor: `not-allowed`

### Banner en la Interfaz
```
┌──────────────────────────────────────────────────────┐
│ 👁️  Viewer Mode                                      │
│                                                      │
│ You can view results and download reports, but     │
│ cannot create or modify scenarios.                  │
└──────────────────────────────────────────────────────┘
```

### Usuario de Prueba
- **Email**: `viewer@ecomodel.com`
- **Password**: `viewer123`
- **Organización**: Spain HTA

---

## 🔒 Multi-Tenancy (Aislamiento de Datos)

### Principio de Organización
- Cada usuario pertenece a **una organización**
- Los datos están **aislados por organización**
- Los usuarios solo ven datos de su organización

### Excepciones
- **Global Admin** puede ver datos de **todas las organizaciones** (para soporte técnico)

### Implementación Backend
```python
# Ejemplo de filtro automático por organización
def get_scenarios(db: Session, current_user: User):
    query = db.query(Scenario)

    if current_user.role != "global_admin":
        # Filtrar solo escenarios de la organización del usuario
        query = query.filter(
            Scenario.organization_id == current_user.organization_id
        )

    return query.all()
```

---

## 📊 Matriz de Permisos Completa

| Funcionalidad | Global Admin | Local User | Viewer |
|---------------|--------------|------------|--------|
| **Organizaciones** |
| Crear organizaciones | ✅ | ❌ | ❌ |
| Ver su organización | ✅ | ✅ | ✅ |
| Editar organizaciones | ✅ | ❌ | ❌ |
| Ver todas las organizaciones | ✅ | ❌ | ❌ |
| **Modelos Económicos** |
| Crear modelos | ✅ | ❌ | ❌ |
| Editar modelos | ✅ | ❌ | ❌ |
| Publicar modelos | ✅ | ❌ | ❌ |
| Ver modelos publicados | ✅ | ✅ | ✅ |
| Acceder al Model Builder | ✅ | ❌ | ❌ |
| **Parámetros** |
| Crear parámetros globales | ✅ | ❌ | ❌ |
| Editar parámetros globales | ✅ | ❌ | ❌ |
| Ver parámetros | ✅ | ✅ | ✅ |
| **Escenarios** |
| Crear escenarios | ✅ | ✅ | ❌ |
| Editar escenarios | ✅ | ✅ | ❌ |
| Eliminar escenarios | ✅ | ✅ | ❌ |
| Ver escenarios (org) | ✅ | ✅ | ✅ |
| Ver escenarios (todas) | ✅ | ❌ | ❌ |
| Clonar escenarios | ✅ | ✅ | ❌ |
| **Simulaciones** |
| Ejecutar Determinística | ✅ | ✅ | ❌ |
| Ejecutar Tornado | ✅ | ✅ | ❌ |
| Ejecutar PSA | ✅ | ✅ | ❌ |
| Ver resultados | ✅ | ✅ | ✅ |
| **Reportes** |
| Generar PDF | ✅ | ✅ | ✅ |
| Generar Excel | ✅ | ✅ | ✅ |
| Descargar reportes | ✅ | ✅ | ✅ |
| **Usuarios** |
| Crear usuarios | ✅ | ❌ | ❌ |
| Editar usuarios | ✅ | ❌ | ❌ |
| Eliminar usuarios | ✅ | ❌ | ❌ |
| Ver usuarios (org) | ✅ | ✅ | ✅ |
| Ver usuarios (todos) | ✅ | ❌ | ❌ |

---

## 🧪 Cómo Probar los Diferentes Roles

### Paso 1: Cerrar Sesión Actual
1. Si ya estás logueado, haz clic en "Logout"
2. Serás redirigido a `/login`

### Paso 2: Login con Diferentes Usuarios

#### Opción A: Login Manual
1. Ir a http://localhost:8001/login
2. Introducir email y password
3. Hacer clic en "Iniciar Sesión"

#### Opción B: Quick Login (Recomendado)
En la página de login, hay 3 botones de acceso rápido:

**Usuario Admin:**
```
┌─────────────────────────────────────────┐
│ Admin [ADMIN]                           │
│ admin@ecomodel.com / admin123           │
└─────────────────────────────────────────┘
```

**Usuario Local:**
```
┌─────────────────────────────────────────┐
│ Local User Spain [USER]                 │
│ spain@ecomodel.com / spain123           │
└─────────────────────────────────────────┘
```

**Usuario Viewer:**
```
┌─────────────────────────────────────────┐
│ Viewer [VIEWER]                         │
│ viewer@ecomodel.com / viewer123         │
└─────────────────────────────────────────┘
```

### Paso 3: Verificar Diferencias Visuales

Una vez logueado, verás:

#### 1. Badge de Rol en el Header
```
┌────────────────────────────────────────────┐
│ EcoModel Hub    user@example.com [BADGE]  │
└────────────────────────────────────────────┘
```

#### 2. Banner Informativo (color diferente por rol)
- **Admin**: Banner rojo
- **User**: Banner azul
- **Viewer**: Banner amarillo

#### 3. Botón Model Builder (solo Admin)
- Visible solo para Global Admin
- Ubicación: Header, junto a "Demo" y "API"

#### 4. Botones Deshabilitados (Viewer)
- "Save Scenario" → Deshabilitado
- "Delete Scenario" → Deshabilitado
- "Run Analysis" → Deshabilitado (si se implementa check)

---

## 🎯 Casos de Uso por Rol

### Caso 1: Farmacéutica Crea Modelo (Admin)
1. Login como `admin@ecomodel.com`
2. Hacer clic en "Model Builder" en el header
3. Crear modelo "Oncology Drug X"
4. Añadir 10 parámetros (costes, probabilidades, utilidades)
5. Publicar modelo

### Caso 2: Hospital Evalúa Fármaco (Local User)
1. Login como `spain@ecomodel.com`
2. Seleccionar modelo publicado "Oncology Drug X"
3. Crear escenario "Spain Base Case"
4. Introducir valores de parámetros para España
5. Ejecutar simulación determinística
6. Generar reporte PDF

### Caso 3: Regulador Revisa Análisis (Viewer)
1. Login como `viewer@ecomodel.com`
2. Ver escenarios de la organización
3. Ver resultados de simulaciones
4. Descargar reportes PDF
5. **NO puede** modificar ni ejecutar nuevas simulaciones

---

## 🔐 Seguridad Implementada

### Frontend
- ✅ Verificación de token en localStorage
- ✅ Redirect a `/login` si no hay token
- ✅ Mostrar rol en la interfaz
- ✅ Deshabilitar botones según rol
- ✅ Ocultar funcionalidades no permitidas

### Backend (Pendiente de Verificar)
- ⚠️ Verificar decoradores `@require_role()` en endpoints
- ⚠️ Verificar filtros por organización en queries
- ⚠️ Verificar validación de permisos en operaciones CRUD

---

## 📝 Endpoints API por Rol

### Global Admin Exclusivos
```
POST   /api/v1/models
PATCH  /api/v1/models/{id}
DELETE /api/v1/models/{id}
POST   /api/v1/models/{id}/publish
POST   /api/v1/organizations
POST   /api/v1/users
```

### Local User + Admin
```
POST   /api/v1/scenarios
PATCH  /api/v1/scenarios/{id}
DELETE /api/v1/scenarios/{id}
POST   /api/v1/simulations/deterministic
POST   /api/v1/simulations/tornado
POST   /api/v1/simulations/psa
```

### Todos los Roles (Read-Only para Viewer)
```
GET    /api/v1/models
GET    /api/v1/models/{id}
GET    /api/v1/scenarios
GET    /api/v1/scenarios/{id}
GET    /api/v1/simulations/{id}
GET    /api/v1/reports/{id}/download
```

---

## 🚀 Próximos Pasos

1. **Verificar en el navegador** las diferencias visuales:
   - Login con cada usuario
   - Comparar badges, banners y botones

2. **Testing de permisos**:
   - Intentar crear escenario como Viewer → Debería estar deshabilitado
   - Intentar acceder a Model Builder como User → Debería no estar visible
   - Verificar que Admin puede acceder a todo

3. **Implementar en Backend**:
   - Añadir decoradores de permisos en endpoints
   - Implementar filtros por organización
   - Testing de autorización

---

**Última actualización**: Enero 2026
**Estado**: ✅ Frontend implementado | ⚠️ Backend pendiente de verificación
