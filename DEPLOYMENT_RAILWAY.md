# 🚂 Deployment en Railway - Funcionalidad Completa

Railway es la plataforma perfecta para EcoModel Hub porque soporta todas las dependencias científicas (NumPy, SciPy, Pandas) sin restricciones.

## 🎯 ¿Por qué Railway?

✅ **Sin límites de tamaño** - NumPy, SciPy, Pandas funcionan perfectamente
✅ **PostgreSQL incluido** - Base de datos automática
✅ **Redis incluido** - Para caché y Celery
✅ **Workers soportados** - Celery funciona
✅ **$5 crédito gratis** - Suficiente para empezar
✅ **Deployments automáticos** - Desde GitHub
✅ **Sin timeout** - Análisis largos funcionan

---

## 🚀 Guía Rápida de Deployment

### Paso 1: Crear Cuenta en Railway

1. Ve a [https://railway.app](https://railway.app)
2. Haz clic en "Start a New Project"
3. Login con GitHub (recomendado)

### Paso 2: Crear Proyecto desde GitHub

1. En el dashboard de Railway, haz clic en **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Busca y selecciona: **`miguelcaselles/ecomodel-hub`**
4. Railway detectará automáticamente que es una aplicación Python

### Paso 3: Añadir PostgreSQL

1. En tu proyecto Railway, haz clic en **"+ New"**
2. Selecciona **"Database"** → **"Add PostgreSQL"**
3. Railway creará automáticamente la base de datos
4. La variable `DATABASE_URL` se configurará automáticamente

### Paso 4: Añadir Redis (Opcional pero recomendado)

1. En tu proyecto Railway, haz clic en **"+ New"**
2. Selecciona **"Database"** → **"Add Redis"**
3. Railway creará automáticamente Redis
4. La variable `REDIS_URL` se configurará automáticamente

### Paso 5: Configurar Variables de Entorno

En la pestaña **"Variables"** de tu servicio web, añade:

```bash
# Estos Railway los configura automáticamente:
# DATABASE_URL=postgresql://... (ya configurado)
# REDIS_URL=redis://... (ya configurado si añadiste Redis)
# PORT=... (ya configurado)

# Debes añadir manualmente:
SECRET_KEY=<genera-con-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PYTHONPATH=backend
```

**Generar SECRET_KEY:**
```bash
openssl rand -hex 32
```

### Paso 6: Configurar CORS

Después del primer deploy, Railway te dará una URL como:
`https://ecomodel-hub-production.up.railway.app`

Añade esta variable:
```bash
BACKEND_CORS_ORIGINS=["https://ecomodel-hub-production.up.railway.app","https://ecomodel-hub-production-*.up.railway.app"]
```

### Paso 7: Deploy

1. Railway desplegará automáticamente
2. Espera 3-5 minutos (primera vez toma más)
3. Railway instalará todas las dependencias incluyendo NumPy, SciPy, Pandas

### Paso 8: Ejecutar Migraciones

Una vez que el deploy complete, ejecuta las migraciones:

**Opción A: Desde Railway CLI**
```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Link al proyecto
railway link

# Ejecutar migraciones
railway run bash -c "cd backend && alembic upgrade head"
```

**Opción B: Desde tu máquina local**
```bash
# Obtén el DATABASE_URL desde Railway (copia desde la pestaña Variables)
cd backend
DATABASE_URL="postgresql://..." alembic upgrade head
```

**Opción C: Shell interactivo de Railway**
```bash
railway shell
cd backend
alembic upgrade head
exit
```

### Paso 9: Cargar Datos de Demo (Opcional)

```bash
# Con Railway CLI
railway run bash -c "cd backend && python seed_data.py"

# O desde local
cd backend
DATABASE_URL="postgresql://..." python seed_data.py
```

### Paso 10: Verificar

Accede a tu aplicación:
- **Base URL**: `https://tu-proyecto.up.railway.app`
- **API Docs**: `https://tu-proyecto.up.railway.app/api/v1/docs`
- **App**: `https://tu-proyecto.up.railway.app/app`

---

## 📋 Comandos de Railway CLI

### Instalación

```bash
npm install -g @railway/cli
```

### Comandos Básicos

```bash
# Login
railway login

# Link al proyecto
railway link

# Ver variables de entorno
railway vars

# Añadir variable
railway vars set KEY=value

# Ver logs en tiempo real
railway logs

# Ejecutar comando en producción
railway run <comando>

# Shell interactivo
railway shell

# Redeploy
railway up

# Ver status
railway status
```

---

## 🔧 Configuración del Proyecto

### Estructura para Railway

```
ecomodel-hub/
├── backend/                # Código Python
│   ├── app/               # FastAPI app
│   │   └── main.py        # Entry point
│   ├── alembic/           # Migraciones
│   └── requirements.txt   # (usa el de la raíz)
├── requirements.txt       # Dependencias COMPLETAS
├── Procfile              # Comando de inicio
├── railway.json          # Configuración Railway
└── .python-version       # (opcional) Versión Python
```

### Procfile

Railway usa el `Procfile` para saber cómo iniciar la app:

```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### railway.json

Configuración adicional de Railway:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

## 🌐 Configurar Dominio Personalizado

### Desde Railway Dashboard

1. Ve a tu servicio en Railway
2. Pestaña **"Settings"**
3. Sección **"Domains"**
4. Haz clic en **"Generate Domain"** (dominio gratuito de Railway)
5. O haz clic en **"Custom Domain"** para usar tu propio dominio

### Actualizar CORS

Una vez tengas tu dominio, actualiza `BACKEND_CORS_ORIGINS`:

```bash
railway vars set BACKEND_CORS_ORIGINS='["https://tu-dominio.up.railway.app"]'
```

---

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
railway logs --follow
```

### Ver Métricas

1. Dashboard de Railway
2. Pestaña **"Metrics"**
3. Ver CPU, RAM, Network

### Alertas

Railway enviará alertas por email si:
- El servicio falla
- Se excede el uso de recursos
- Errores de deployment

---

## 💰 Costos de Railway

### Plan Gratuito (Trial)

- **$5 de crédito gratis** al crear cuenta
- Suficiente para ~2-3 semanas de testing
- Todos los features disponibles

### Plan Developer ($5/mes por servicio)

- **$5 fijos por servicio** (web app, PostgreSQL, Redis = $15/mes)
- 512 MB RAM garantizados por servicio
- Deployments ilimitados
- Sin límite de tiempo de ejecución

### Plan Team ($20/mes + uso)

- Mejor para producción
- Más RAM y CPU
- Mejor soporte
- Staging environments

**Costo estimado para EcoModel Hub**: ~$15-20/mes
- Web service: $5/mes
- PostgreSQL: $5/mes
- Redis: $5/mes

---

## 🔄 Deployments Automáticos desde GitHub

Una vez conectado, Railway desplegará automáticamente cuando:

```bash
# Haces push a main
git add .
git commit -m "Mi cambio"
git push

# Railway despliega automáticamente en ~3-5 minutos
```

### Configurar Branch de Deployment

Por defecto usa `main`, pero puedes cambiarlo:

1. Settings → **"Service"**
2. **"Source"** → **"Configure"**
3. Cambiar branch

---

## ⚙️ Variables de Entorno Necesarias

### Automáticas (Railway las configura)

```bash
DATABASE_URL=postgresql://...  # Auto-configurado
REDIS_URL=redis://...          # Auto-configurado si añadiste Redis
PORT=...                       # Auto-configurado
RAILWAY_ENVIRONMENT=production  # Auto-configurado
```

### Manuales (debes añadirlas)

```bash
SECRET_KEY=<openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["https://tu-dominio.up.railway.app"]
PYTHONPATH=backend
```

### Opcional

```bash
# Para modo debug (solo desarrollo)
DEBUG=False

# Para logging
LOG_LEVEL=INFO

# Para background workers (si usas Celery)
CELERY_BROKER_URL=$REDIS_URL
CELERY_RESULT_BACKEND=$REDIS_URL
```

---

## 🐛 Troubleshooting

### El deploy falla con error de dependencias

**Solución**: Railway toma ~5 minutos en instalar NumPy/SciPy la primera vez. Si falla:
```bash
# Ver logs
railway logs

# Redeploy
railway up --detach
```

### "Application failed to respond"

**Solución**: Verifica que el comando de inicio use `$PORT`:
```bash
# Debe ser:
uvicorn app.main:app --host 0.0.0.0 --port $PORT

# NO:
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Errores de base de datos

**Solución**:
```bash
# Verifica que DATABASE_URL esté configurado
railway vars | grep DATABASE_URL

# Ejecuta migraciones
railway run bash -c "cd backend && alembic upgrade head"
```

### La app funciona pero la API da 500

**Solución**:
```bash
# Verifica SECRET_KEY
railway vars | grep SECRET_KEY

# Si no existe, añádela
railway vars set SECRET_KEY=$(openssl rand -hex 32)
```

### Problemas con CORS

**Solución**:
```bash
# Actualiza CORS origins con tu dominio Railway
railway vars set BACKEND_CORS_ORIGINS='["https://tu-dominio.up.railway.app"]'
```

---

## 🔒 Seguridad en Producción

### Checklist de Seguridad

- [ ] SECRET_KEY único y aleatorio (32+ caracteres)
- [ ] DEBUG=False en producción
- [ ] CORS configurado solo para tu dominio
- [ ] PostgreSQL con contraseña fuerte (Railway lo hace automáticamente)
- [ ] HTTPS habilitado (Railway lo hace automáticamente)
- [ ] Variables de entorno no committed al repo (.env en .gitignore)
- [ ] Backups de base de datos configurados

### Habilitar Backups de PostgreSQL

1. Dashboard → PostgreSQL service
2. Settings → **"Backups"**
3. Enable automatic backups

---

## 📈 Escalabilidad

### Aumentar Recursos

Si tu app necesita más recursos:

1. Dashboard → Tu servicio
2. Settings → **"Resources"**
3. Aumentar CPU/RAM (disponible en plan Pro)

### Añadir Workers

Para tareas en background con Celery:

1. Crear nuevo servicio en el mismo proyecto
2. Mismo repo de GitHub
3. Comando de inicio diferente:
   ```
   cd backend && celery -A app.celery worker --loglevel=info
   ```

---

## 🎯 Comparación: Railway vs Vercel

| Feature | Railway | Vercel |
|---------|---------|--------|
| NumPy/SciPy/Pandas | ✅ Completo | ❌ Limitado |
| Timeout | ✅ Sin límite | ⚠️ 10s (Free), 60s (Pro) |
| PostgreSQL | ✅ Incluido | ❌ Externo necesario |
| Redis | ✅ Incluido | ❌ Externo necesario |
| Celery/Workers | ✅ Soportado | ❌ No soportado |
| Precio | 💰 $15-20/mes | 💰 $0-20/mes |
| Deployment | ✅ Desde GitHub | ✅ Desde GitHub |
| Mejor para | Apps completas | Sitios estáticos/API ligeras |

**Recomendación**: Railway para EcoModel Hub por las capacidades científicas completas.

---

## 📚 Recursos

- **Railway Dashboard**: [railway.app](https://railway.app)
- **Documentación**: [docs.railway.app](https://docs.railway.app)
- **GitHub Repo**: [github.com/miguelcaselles/ecomodel-hub](https://github.com/miguelcaselles/ecomodel-hub)
- **CLI Docs**: [docs.railway.app/develop/cli](https://docs.railway.app/develop/cli)

---

## ✅ Checklist de Deployment

- [ ] Cuenta en Railway creada
- [ ] Proyecto creado desde GitHub
- [ ] PostgreSQL añadido
- [ ] Redis añadido (opcional)
- [ ] Variables de entorno configuradas
- [ ] Primer deploy completado
- [ ] Migraciones ejecutadas
- [ ] Datos de seed cargados (opcional)
- [ ] API Docs accesible
- [ ] Login funciona
- [ ] Análisis científicos funcionan
- [ ] PDFs se generan correctamente
- [ ] Dominio personalizado configurado (opcional)

---

**¡Tu aplicación con funcionalidad completa está lista para Railway! 🚂🚀**

Todos los análisis científicos (NumPy, SciPy, Pandas) funcionarán sin restricciones.
