# 🚀 Guía de Inicio Rápido - EcoModel Hub

## Paso 1: Verificar Prerrequisitos

Asegúrate de tener instalado:
- **Docker Desktop** (https://www.docker.com/products/docker-desktop)
- **Make** (opcional, para comandos rápidos)

Verifica la instalación:
```bash
docker --version
docker compose version
```

## Paso 2: Iniciar la Aplicación

### Opción A: Con Make (Recomendado)

```bash
# Ver comandos disponibles
make help

# Levantar todos los servicios
make up

# Esperar ~30 segundos para que PostgreSQL esté listo

# Ejecutar migraciones
make migrate

# Cargar datos de demo
make seed
```

### Opción B: Con Docker Compose

```bash
# Levantar servicios
cd docker
docker compose up -d

# Esperar a que PostgreSQL esté listo
docker compose logs -f db
# Presiona Ctrl+C cuando veas "database system is ready to accept connections"

# Ejecutar migraciones
docker compose exec backend alembic upgrade head

# Cargar datos de demo
docker compose exec backend python seed_data.py
```

## Paso 3: Verificar que Todo Funciona

### 3.1 Verificar API

Abre en tu navegador:
- **Swagger UI**: http://localhost:8001/api/v1/docs

Deberías ver la documentación interactiva de la API.

### 3.2 Probar el Login

En Swagger UI:
1. Despliega el endpoint `POST /api/v1/auth/login`
2. Haz clic en "Try it out"
3. Usa estas credenciales:
```json
{
  "email": "spain@ecomodel.com",
  "password": "spain123"
}
```
4. Haz clic en "Execute"
5. Deberías recibir un `access_token`

### 3.3 Autorizar Requests

1. Copia el `access_token` de la respuesta
2. Haz clic en el botón "Authorize" (candado) en la parte superior de Swagger
3. Pega el token en el campo "Value" (con prefijo `Bearer `)
4. Haz clic en "Authorize" y luego "Close"

### 3.4 Ejecutar una Simulación

1. Primero, obtén un `scenario_id`:
   - Conéctate a la base de datos:
     ```bash
     make db-shell
     ```
   - Ejecuta:
     ```sql
     SELECT id, name FROM scenarios;
     ```
   - Copia el UUID del escenario "Spain Base Case"

2. En Swagger, despliega `POST /api/v1/simulations/deterministic`
3. Haz clic en "Try it out"
4. Pega el `scenario_id`:
```json
{
  "scenario_id": "TU-SCENARIO-UUID-AQUI",
  "simulation_type": "deterministic"
}
```
5. Haz clic en "Execute"

### 3.5 Ver Resultados

Deberías recibir una respuesta como:
```json
{
  "id": "...",
  "status": "completed",
  "results": {
    "summary": {
      "icer": 25432.12,
      "delta_cost": 122000,
      "delta_qaly": 4.8,
      "conclusion": "Cost-Effective",
      "is_dominated": false
    },
    "drug_a_results": {
      "total_cost": 352000,
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

¡Felicidades! 🎉 La aplicación está funcionando correctamente.

## Paso 4: Probar Análisis de Sensibilidad

### Tornado Diagram

```json
{
  "scenario_id": "TU-SCENARIO-UUID",
  "simulation_type": "tornado"
}
```

Endpoint: `POST /api/v1/simulations/tornado`

### Análisis Probabilístico (PSA)

```json
{
  "scenario_id": "TU-SCENARIO-UUID",
  "simulation_type": "psa",
  "iterations": 1000,
  "seed": 42
}
```

Endpoint: `POST /api/v1/simulations/psa`

**Nota**: PSA con 1000 iteraciones puede tardar ~10-30 segundos.

## Usuarios de Prueba

| Email                  | Password   | Rol           | Descripción |
|------------------------|------------|---------------|-------------|
| admin@ecomodel.com     | admin123   | Global Admin  | Puede crear modelos y ver todo |
| spain@ecomodel.com     | spain123   | Local User    | Usuario de España, puede editar escenarios españoles |
| germany@ecomodel.com   | germany123 | Local User    | Usuario de Alemania |
| viewer@ecomodel.com    | viewer123  | Viewer        | Solo lectura |

## Comandos Útiles

```bash
# Ver logs en tiempo real
make logs

# Ver solo logs del backend
make logs-backend

# Abrir shell en el contenedor backend
make shell

# Conectar a PostgreSQL
make db-shell

# Reiniciar servicios
make restart

# Parar todos los servicios
make down

# Limpiar todo (¡cuidado! elimina datos)
make clean
```

## Estructura de Datos

### Modelos Disponibles
- **Oncology Treatment Model**: Modelo de Markov de 3 estados

### Escenarios Precargados
1. **Spain Base Case**: Precios españoles
2. **Spain Optimistic**: Precios negociados
3. **Germany Base Case**: Precios alemanes

### Parámetros Editables

**Costes** (varían por país):
- Coste anual Drug A: 2,800 - 3,800 EUR
- Coste anual Drug B: 450 - 550 EUR
- Coste seguimiento: 180 - 220 EUR
- Coste progresión: 4,200 - 5,000 EUR

**Probabilidades** (basadas en evidencia clínica):
- Progresión Drug A: 10%
- Progresión Drug B: 25%
- Mortalidad estable: 2%
- Mortalidad progresión: 15%

**Utilidades**:
- Estado estable: 0.85
- Estado progresión: 0.50

## Interpretación de Resultados

### ICER (Incremental Cost-Effectiveness Ratio)

```
ICER = (Coste Drug A - Coste Drug B) / (QALY Drug A - QALY Drug B)
```

**Interpretación**:
- **< 30,000 EUR/QALY**: Cost-Effective (España)
- **30,000 - 50,000 EUR/QALY**: Umbral de decisión
- **> 50,000 EUR/QALY**: Not Cost-Effective

### Dominancia

- **Dominante**: Drug A es más barata Y más efectiva (ICER negativo o no aplicable)
- **Dominada**: Drug A es más cara Y menos efectiva
- **En el cuadrante NE**: Más cara pero más efectiva (calcular ICER)

## Troubleshooting

### Error: "Connection refused" al conectar a PostgreSQL

**Solución**: Espera un poco más para que PostgreSQL termine de inicializarse.
```bash
make logs-db
# Espera hasta ver "database system is ready to accept connections"
```

### Error: "Table does not exist"

**Solución**: Ejecuta las migraciones.
```bash
make migrate
```

### Error: "Scenario not found"

**Solución**: Ejecuta el script de seed para cargar datos de demo.
```bash
make seed
```

### Error: "Invalid authentication credentials"

**Solución**:
1. Verifica que copiaste el token correctamente
2. El token expira en 30 minutos, haz login nuevamente
3. Asegúrate de incluir el prefijo `Bearer ` en la autorización

## Próximos Pasos

1. **Explorar la API**: Prueba diferentes combinaciones de parámetros
2. **Comparar Escenarios**: Ejecuta simulaciones con diferentes valores
3. **Análisis de Sensibilidad**: Prueba Tornado y PSA para ver qué parámetros tienen más impacto
4. **Frontend**: (Próximamente) Interfaz gráfica para usuarios no técnicos

## Recursos

- **Documentación API**: http://localhost:8001/api/v1/docs
- **README completo**: [README.md](README.md)
- **Especificación técnica**: Ver PRD original

## Feedback y Soporte

Si encuentras problemas o tienes sugerencias, documéntalos para discusión con el equipo de desarrollo.

---

¡Disfruta explorando EcoModel Hub! 🏥📊
