# EcoModel Hub 🏥

[![GitHub](https://img.shields.io/badge/GitHub-miguelcaselles%2Fecomodel--hub-blue?logo=github)](https://github.com/miguelcaselles/ecomodel-hub)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/miguelcaselles/ecomodel-hub)

> Plataforma SaaS B2B para gestión centralizada y visualización de modelos farmacoeconómicos (HEOR)

## 🌐 Links

- **GitHub Repository**: [github.com/miguelcaselles/ecomodel-hub](https://github.com/miguelcaselles/ecomodel-hub)
- **Documentation**: Ver [DEPLOYMENT_VERCEL.md](DEPLOYMENT_VERCEL.md) para deployment en Vercel
- **Quick Start**: Ver [QUICK_START.md](QUICK_START.md) para desarrollo local

## 🎯 Características Principales

- **Motor de Cálculo Markov**: Modelo de 3 estados (Estable, Progresión, Muerte)
- **Análisis de Sensibilidad**: Determinístico (Tornado) y Probabilístico (Monte Carlo PSA)
- **Multi-Tenant**: Organizaciones independientes con datos aislados
- **RBAC**: 3 roles (Global Admin, Local User, Viewer)
- **Adaptación Local**: Parámetros editables por país (precios, costes)
- **Visualizaciones**: Plano Coste-Efectividad, Tornado Charts, Curvas CEAC
- **Cálculos Asíncronos**: Celery + Redis para simulaciones pesadas

## 🏗️ Arquitectura

```
Backend:  Python 3.11 + FastAPI + SQLAlchemy + PostgreSQL
Frontend: React 18 + TypeScript + Material UI + Recharts
Queue:    Celery + Redis
Docker:   Docker Compose para desarrollo y producción
```

## 📦 Stack Tecnológico

### Backend
- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para PostgreSQL
- **Alembic**: Migraciones de base de datos
- **NumPy/SciPy**: Cálculos científicos y distribuciones estadísticas
- **Celery**: Cola de tareas para procesamiento asíncrono
- **Redis**: Broker de mensajes y caché
- **JWT**: Autenticación mediante tokens
- **WeasyPrint**: Generación de reportes PDF

### Frontend
- **React 18**: Librería UI
- **TypeScript**: Tipado estático
- **Material UI**: Componentes UI corporativos
- **Recharts/Plotly**: Gráficos interactivos
- **Axios**: Cliente HTTP
- **React Router**: Navegación

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker & Docker Compose
- Python 3.11+ (para desarrollo local)
- Node.js 20+ (para desarrollo frontend)

### Instalación

```bash
# 1. Clonar el repositorio
cd Farmacoeconomia

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Levantar servicios con Docker
cd docker
docker compose up -d

# 4. Esperar a que PostgreSQL esté listo
docker compose logs -f db

# 5. Ejecutar migraciones (en otra terminal)
docker compose exec backend alembic upgrade head

# 6. Cargar datos de demo
docker compose exec backend python seed_data.py
```

### Acceso

- **API Docs**: http://localhost:8001/api/v1/docs
- **Frontend**: http://localhost:3001 (cuando esté implementado)

### Usuarios Demo

| Email                  | Password   | Rol           | Organización |
|------------------------|------------|---------------|--------------|
| admin@ecomodel.com     | admin123   | Global Admin  | -            |
| spain@ecomodel.com     | spain123   | Local User    | Spain        |
| germany@ecomodel.com   | germany123 | Local User    | Germany      |
| viewer@ecomodel.com    | viewer123  | Viewer        | -            |

## 🧪 Testing

### Test Manual con API

1. **Login**:
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"spain@ecomodel.com","password":"spain123"}'
```

Respuesta:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "spain@ecomodel.com",
    "role": "local_user"
  }
}
```

2. **Ejecutar Simulación Determinística**:
```bash
# Obtener scenario_id de la base de datos o de GET /scenarios
SCENARIO_ID="<uuid-del-scenario>"
TOKEN="<access_token-del-login>"

curl -X POST http://localhost:8001/api/v1/simulations/deterministic \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"scenario_id\":\"$SCENARIO_ID\"}"
```

Respuesta:
```json
{
  "id": "simulation-uuid",
  "scenario_id": "scenario-uuid",
  "status": "completed",
  "results": {
    "status": "success",
    "summary": {
      "icer": 25000.50,
      "delta_cost": 120000,
      "delta_qaly": 4.8,
      "conclusion": "Cost-Effective"
    },
    "drug_a_results": {
      "total_cost": 350000,
      "total_qalys": 7.2,
      "life_years": 8.5
    },
    "drug_b_results": {
      "total_cost": 230000,
      "total_qalys": 2.4,
      "life_years": 3.2
    }
  }
}
```

3. **Ejecutar Análisis Tornado**:
```bash
curl -X POST http://localhost:8001/api/v1/simulations/tornado \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"scenario_id\":\"$SCENARIO_ID\"}"
```

4. **Ejecutar PSA (Monte Carlo)**:
```bash
curl -X POST http://localhost:8001/api/v1/simulations/psa \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"scenario_id\":\"$SCENARIO_ID\",\"iterations\":1000,\"seed\":42}"
```

## 📊 Modelo Farmacoeconómico

### Estados de Markov

```
┌─────────┐     prob_s_to_p    ┌─────────────┐
│ Stable  │ ──────────────────► │ Progression │
│         │                     │             │
└─────────┘                     └─────────────┘
     │                                 │
     │ prob_s_to_d                     │ prob_p_to_d
     │                                 │
     ▼                                 ▼
┌──────────────────────────────────────────┐
│              Death (Absorbing)            │
└──────────────────────────────────────────┘
```

### Parámetros Clave

**Costes** (editables por país):
- `cost_drug_a`: Coste anual del fármaco nuevo
- `cost_drug_b`: Coste anual del fármaco estándar
- `cost_state_s`: Coste de seguimiento en estado estable
- `cost_state_p`: Coste de evento de progresión

**Utilidades** (calidad de vida):
- `utility_stable`: 0.85 (muy buena calidad de vida)
- `utility_progression`: 0.50 (deterioro significativo)

**Probabilidades de Transición**:
- `prob_s_to_p_a`: Tasa de progresión con Fármaco A (10%)
- `prob_s_to_p_b`: Tasa de progresión con Fármaco B (25%)
- `prob_s_to_d`: Mortalidad desde estado estable (2%)
- `prob_p_to_d`: Mortalidad desde progresión (15%)

### Outputs

- **ICER** (Incremental Cost-Effectiveness Ratio): EUR/QALY
- **Delta Cost**: Diferencia de costes entre tratamientos
- **Delta QALY**: Diferencia de QALYs (años de vida ajustados por calidad)
- **Conclusión**: Cost-Effective si ICER < 30,000 EUR/QALY

## 🗂️ Estructura del Proyecto

```
├── backend/
│   ├── alembic/              # Migraciones DB
│   ├── app/
│   │   ├── api/v1/           # Endpoints REST
│   │   ├── core/             # Seguridad, permisos
│   │   ├── db/               # Sesión database
│   │   ├── models/           # Modelos SQLAlchemy
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── tasks/            # Tareas Celery
│   │   └── main.py           # Entry point FastAPI
│   ├── engine/
│   │   ├── markov/           # Motor de cálculo Markov
│   │   └── sensitivity/      # Análisis de sensibilidad
│   └── seed_data.py          # Script de datos demo
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── Dockerfile.worker
└── frontend/                 # (Pendiente implementación completa)
```

## 🔐 Seguridad

- **JWT Tokens**: Access tokens (30 min) + Refresh tokens (7 días)
- **RBAC**: Role-Based Access Control con 3 niveles
- **Password Hashing**: bcrypt
- **CORS**: Configurado para orígenes permitidos
- **Isolation**: Multi-tenant con filtros a nivel de organización

## 🧩 API Endpoints

### Autenticación
- `POST /api/v1/auth/login` - Login con email/password
- `POST /api/v1/auth/logout` - Logout

### Simulaciones
- `POST /api/v1/simulations/deterministic` - Caso base
- `POST /api/v1/simulations/tornado` - Análisis tornado
- `POST /api/v1/simulations/psa` - Monte Carlo PSA
- `GET /api/v1/simulations/{id}` - Obtener resultados

### (Próximamente)
- `/api/v1/models` - CRUD modelos económicos
- `/api/v1/scenarios` - CRUD escenarios
- `/api/v1/reports` - Generación de PDFs

## 🛠️ Desarrollo

### Backend Local (sin Docker)

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
export DATABASE_URL="postgresql://ecomodel:ecomodel_pass@localhost:5433/ecomodel"
export REDIS_URL="redis://localhost:6380/0"

# Ejecutar migraciones
alembic upgrade head

# Seed data
python seed_data.py

# Ejecutar servidor
uvicorn app.main:app --reload --port 8000
```

### Celery Worker

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

### Frontend Local (cuando se implemente)

```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentación API

La documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8001/api/v1/docs
- **ReDoc**: http://localhost:8001/api/v1/redoc

## 🐛 Troubleshooting

### PostgreSQL no se conecta

```bash
# Verificar que el contenedor está corriendo
docker compose ps

# Ver logs
docker compose logs db

# Reiniciar servicios
docker compose restart
```

### Migraciones fallan

```bash
# Entrar al contenedor
docker compose exec backend bash

# Verificar estado de migraciones
alembic current
alembic history

# Forzar upgrade
alembic upgrade head
```

### Celery no procesa tareas

```bash
# Verificar worker está corriendo
docker compose logs celery_worker

# Reiniciar worker
docker compose restart celery_worker
```

## 🚧 Roadmap

### ✅ Fase 1 - MVP Backend (Completado)
- [x] Infraestructura Docker
- [x] Modelos de base de datos
- [x] Autenticación JWT
- [x] Motor de cálculo Markov
- [x] API endpoints básicos
- [x] Análisis de sensibilidad (Tornado, PSA)

### 🔄 Fase 2 - Frontend (En Progreso)
- [ ] React app con TypeScript
- [ ] Login y autenticación
- [ ] Input Workspace (formularios dinámicos)
- [ ] Visualization Dashboard
- [ ] Gráficos interactivos (CE Plane, Tornado, CEAC)

### 📅 Fase 3 - Características Avanzadas
- [ ] Upload de scripts Python custom
- [ ] Generación de reportes PDF
- [ ] WebSocket para progreso en tiempo real
- [ ] Model Builder UI para Global Admin
- [ ] Comparación de múltiples escenarios
- [ ] Export a Excel/CSV

### 🔮 Fase 4 - Optimizaciones
- [ ] Cache de resultados
- [ ] Optimización de consultas DB
- [ ] Tests automatizados (pytest)
- [ ] CI/CD pipeline
- [ ] Deployment a producción

## 📝 Licencia

Proyecto propietario - Todos los derechos reservados

## 👥 Equipo

Desarrollado para la industria farmacéutica con el objetivo de facilitar la toma de decisiones en farmacoeconomía.

## 📧 Contacto

Para consultas sobre el proyecto, contactar al equipo de desarrollo.
