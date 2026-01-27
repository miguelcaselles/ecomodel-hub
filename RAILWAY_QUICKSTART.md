# 🚂 Railway Quick Start - 5 Minutos hasta Producción

## ✨ Funcionalidad Completa Garantizada

Railway soporta **TODAS** las dependencias científicas:
- ✅ NumPy
- ✅ SciPy
- ✅ Pandas
- ✅ PostgreSQL
- ✅ Redis
- ✅ Sin timeouts
- ✅ Sin límites de tamaño

---

## 🚀 Opción 1: Deployment desde Dashboard (Recomendado - 5 minutos)

### Paso 1: Crear Proyecto

1. **Ve a Railway**: [https://railway.app/new](https://railway.app/new)

2. **Click en**: "Deploy from GitHub repo"

3. **Busca**: `miguelcaselles/ecomodel-hub`

4. **Click**: "Deploy Now"

   Railway detectará automáticamente que es Python y comenzará el deployment.

### Paso 2: Añadir Base de Datos

**PostgreSQL** (Obligatorio):
```
1. En tu proyecto → Click "+ New"
2. Database → PostgreSQL
3. Done! Railway auto-configura DATABASE_URL
```

**Redis** (Opcional pero recomendado):
```
1. En tu proyecto → Click "+ New"
2. Database → Redis
3. Done! Railway auto-configura REDIS_URL
```

### Paso 3: Configurar Variables

En la pestaña "Variables" de tu servicio web:

```bash
SECRET_KEY=<pegar-el-de-abajo>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PYTHONPATH=backend
BACKEND_CORS_ORIGINS=["https://tu-dominio.up.railway.app"]
```

**Generar SECRET_KEY:**
```bash
openssl rand -hex 32
```

Copia el resultado y pégalo como `SECRET_KEY`.

### Paso 4: Esperar

- Primera vez: ~5 minutos
- Railway instala NumPy, SciPy, Pandas automáticamente
- Verás el progreso en la pestaña "Deployments"

### Paso 5: Ejecutar Migraciones

**Opción A: Desde CLI**
```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Link al proyecto (selecciona tu proyecto)
railway link

# Ejecutar migraciones
railway run bash -c "cd backend && alembic upgrade head"

# Cargar datos demo (opcional)
railway run bash -c "cd backend && python seed_data.py"
```

**Opción B: Desde tu máquina**
```bash
# Copia DATABASE_URL desde Railway (Variables tab)
cd backend
DATABASE_URL="postgresql://..." alembic upgrade head
DATABASE_URL="postgresql://..." python seed_data.py
```

### Paso 6: Verificar

Tu app estará en: `https://ecomodel-hub-production.up.railway.app`

Prueba:
- **API Docs**: `/api/v1/docs`
- **Login**: `/login`
- **App**: `/app`

---

## 🚀 Opción 2: Deployment desde CLI (3 comandos)

### Instalar CLI

```bash
npm install -g @railway/cli
```

### Ejecutar Script Automático

```bash
./deploy-railway.sh
```

El script te guiará paso a paso de forma interactiva.

### O Manual

```bash
# Login
railway login

# Inicializar
railway init

# Configurar variables
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"
railway variables set PYTHONPATH="backend"

# Deploy
railway up

# Añadir PostgreSQL
railway add postgresql

# Añadir Redis
railway add redis

# Migraciones
railway run bash -c "cd backend && alembic upgrade head"

# Abrir app
railway open
```

---

## 📊 Después del Deployment

### Ver Logs

```bash
railway logs --follow
```

### Ver Variables

```bash
railway vars
```

### Añadir Variable

```bash
railway vars set KEY=value
```

### Redeploy

```bash
# Automático desde GitHub
git push

# O manual
railway up
```

### Ejecutar Comando

```bash
railway run <comando>
```

### Shell Interactivo

```bash
railway shell
```

---

## ⚡ Deployments Automáticos

Después de conectar con GitHub:

```bash
# Cualquier cambio que hagas
git add .
git commit -m "Mi cambio"
git push

# Railway despliega automáticamente
# ~3-5 minutos
```

---

## 🌐 Tu App Funcionará En

- **Base URL**: `https://ecomodel-hub-production.up.railway.app`
- **API**: `https://ecomodel-hub-production.up.railway.app/api/v1/docs`
- **Login**: `https://ecomodel-hub-production.up.railway.app/login`
- **App**: `https://ecomodel-hub-production.up.railway.app/app`
- **Budget Impact**: `.../budget-impact`
- **Decision Tree**: `.../decision-tree`
- **Survival Analysis**: `.../survival`
- **VOI Analysis**: `.../voi`

---

## ✅ Funcionalidades que FUNCIONAN

- ✅ **Todos los análisis científicos** (NumPy, SciPy, Pandas)
- ✅ **Budget Impact Analysis**
- ✅ **Decision Tree Analysis**
- ✅ **Survival Analysis** (Parametric)
- ✅ **VOI Analysis** (EVPI, EVPPI)
- ✅ **Markov Models**
- ✅ **PSA (Monte Carlo)**
- ✅ **Sensitivity Analysis**
- ✅ **PDF Generation** (ReportLab)
- ✅ **Excel Generation**
- ✅ **Authentication** (JWT)
- ✅ **Multi-tenant**
- ✅ **RBAC**
- ✅ **PostgreSQL**
- ✅ **Redis** (opcional)
- ✅ **Sin timeouts**
- ✅ **Sin límites de tamaño**

---

## 💰 Costos

### Trial
- **$5 gratis** al crear cuenta
- ~2-3 semanas de testing

### Production
- **~$15-20/mes total**:
  - Web app: $5/mes
  - PostgreSQL: $5/mes
  - Redis: $5/mes

Mucho más barato que la infraestructura propia y sin mantenimiento.

---

## 🐛 Problemas Comunes

### "Build failed"
**Solución**: Railway toma tiempo en instalar NumPy/SciPy. Espera 5-10 min la primera vez.

```bash
# Ver logs
railway logs
```

### "Application failed to respond"
**Solución**: Verifica que estés usando `$PORT`:

```bash
# En Procfile (ya está correcto):
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### "500 Internal Server Error"
**Solución**: Verifica variables de entorno:

```bash
railway vars | grep SECRET_KEY
railway vars | grep DATABASE_URL
```

### "Can't connect to database"
**Solución**:

```bash
# Verifica que PostgreSQL esté añadido
railway list

# Ejecuta migraciones
railway run bash -c "cd backend && alembic upgrade head"
```

---

## 📚 Recursos

- **Dashboard**: [railway.app](https://railway.app)
- **Docs**: [docs.railway.app](https://docs.railway.app)
- **CLI Docs**: [docs.railway.app/develop/cli](https://docs.railway.app/develop/cli)
- **Guía Completa**: [DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md)

---

## ✅ Checklist

- [ ] Cuenta Railway creada
- [ ] Proyecto creado desde GitHub
- [ ] PostgreSQL añadido
- [ ] Redis añadido
- [ ] Variables configuradas
- [ ] Deploy completado
- [ ] Migraciones ejecutadas
- [ ] API funciona
- [ ] Login funciona
- [ ] Análisis científicos funcionan

---

**¡Listo! Tu app con funcionalidad completa está en producción! 🚂🚀**

Railway es perfecto para EcoModel Hub porque soporta todas las capacidades científicas sin restricciones.

---

## 🔗 Links Útiles

- **GitHub Repo**: [github.com/miguelcaselles/ecomodel-hub](https://github.com/miguelcaselles/ecomodel-hub)
- **Railway Dashboard**: [railway.app/dashboard](https://railway.app/dashboard)
- **Deploy Now**: [railway.app/new](https://railway.app/new)

---

¿Preguntas? Revisa [DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md) para documentación completa.
