# 🚀 Próximos Pasos - Railway Deployment

Ya tienes el proyecto conectado con Railway. Ahora vamos a completar la configuración.

---

## ⚡ Opción Rápida: Script Automático

```bash
cd "/Users/miguelcaselles/Desktop/PROYECTOS PROGRAMACIÓN /Innovación HSCS/Farmacoeconomia"
./continue-railway-deployment.sh
```

Este script te guiará paso a paso de forma interactiva.

---

## 🔧 Opción Manual: Paso a Paso

### Paso 1: Login en Railway (Si no lo has hecho)

```bash
railway login
```

Esto abrirá tu navegador para autenticarte.

### Paso 2: Link al Proyecto

```bash
cd "/Users/miguelcaselles/Desktop/PROYECTOS PROGRAMACIÓN /Innovación HSCS/Farmacoeconomia"
railway link
```

Selecciona tu proyecto cuando te lo pida.

### Paso 3: Verificar Estado

```bash
railway status
```

Esto te mostrará los servicios actuales.

### Paso 4: Verificar/Añadir Servicios

Abre el dashboard:

```bash
railway dashboard
```

Verifica que tengas:
- ✅ Servicio Web (tu app)
- ✅ PostgreSQL
- ✅ Redis (opcional pero recomendado)

**Si falta alguno:**
1. Click "+ New"
2. Database → PostgreSQL/Redis

### Paso 5: Configurar Variables de Entorno

```bash
# Generar SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# Configurar variables
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"
railway variables set PYTHONPATH="backend"
```

### Paso 6: Obtener URL y Configurar CORS

```bash
# Ver tu URL
railway domain
```

Copia la URL y configura CORS:

```bash
# Reemplaza con tu URL real
railway variables set BACKEND_CORS_ORIGINS='["https://tu-dominio.up.railway.app"]'
```

### Paso 7: Ejecutar Migraciones

```bash
railway run bash -c "cd backend && alembic upgrade head"
```

### Paso 8: Cargar Datos Demo (Opcional)

```bash
railway run bash -c "cd backend && python seed_data.py"
```

### Paso 9: Verificar Logs

```bash
railway logs --follow
```

Presiona Ctrl+C para salir cuando veas que todo funciona.

### Paso 10: Abrir App

```bash
railway open
```

O visita tu URL en el navegador.

---

## 🧪 Probar la Aplicación

### 1. Verificar API Docs

Visita: `https://tu-dominio.up.railway.app/api/v1/docs`

### 2. Probar Login

En la API Docs, prueba el endpoint `/api/v1/auth/login`:

```json
{
  "email": "admin@ecomodel.com",
  "password": "admin123"
}
```

### 3. Probar Análisis

Visita cada módulo:
- `/app` - Dashboard principal
- `/budget-impact` - Budget Impact Analysis
- `/decision-tree` - Decision Tree Analysis
- `/survival` - Survival Analysis
- `/voi` - VOI Analysis

### 4. Probar Exportación de PDFs

En cualquier módulo, ejecuta un análisis y luego click en "Export PDF".

---

## 📊 Verificar Funcionalidad Completa

Verifica que estos análisis funcionen (requieren NumPy/SciPy):

### Budget Impact Analysis
```
✓ Debe calcular impacto presupuestario año por año
✓ Debe generar PDFs profesionales
```

### VOI Analysis
```
✓ Debe calcular EVPI (Value of Perfect Information)
✓ Debe calcular EVPPI por parámetro
✓ Debe ejecutar simulaciones Monte Carlo
```

### Survival Analysis
```
✓ Debe ajustar distribuciones paramétricas (Weibull, etc.)
✓ Debe calcular AIC, BIC
✓ Debe recomendar mejor distribución
```

---

## 🔍 Troubleshooting

### Error: "Unauthorized"

```bash
railway login
```

### Error: "Not linked to a project"

```bash
railway link
```

Selecciona tu proyecto.

### Error: "DATABASE_URL not found"

Verifica que PostgreSQL esté añadido:

```bash
railway dashboard
```

Si no está, añádelo: "+ New" → "Database" → "PostgreSQL"

### Error: "Module not found: numpy"

Verifica que `requirements.txt` esté en la raíz y tenga NumPy:

```bash
cat requirements.txt | grep numpy
```

Si no está, ya lo corregí en el último commit. Haz redeploy:

```bash
railway up
```

### Error 500 en la API

Ver logs:

```bash
railway logs --follow
```

Verifica variables de entorno:

```bash
railway variables
```

### La app no responde

Verifica el deployment:

```bash
railway status
```

Si dice "crashed", ver logs:

```bash
railway logs
```

---

## 🎯 Checklist de Verificación

Marca cada item cuando lo completes:

### Configuración
- [ ] Login en Railway (`railway login`)
- [ ] Proyecto linkeado (`railway link`)
- [ ] PostgreSQL añadido
- [ ] Redis añadido (opcional)
- [ ] Variables de entorno configuradas
- [ ] CORS configurado con tu dominio

### Deployment
- [ ] Deployment exitoso (ver `railway status`)
- [ ] Migraciones ejecutadas
- [ ] Datos demo cargados (opcional)
- [ ] Sin errores en logs

### Funcionalidad
- [ ] API Docs accesible (`/api/v1/docs`)
- [ ] Login funciona
- [ ] Dashboard principal carga (`/app`)
- [ ] Budget Impact Analysis funciona
- [ ] Decision Tree Analysis funciona
- [ ] Survival Analysis funciona
- [ ] VOI Analysis funciona
- [ ] PDFs se generan correctamente
- [ ] Excel se exporta correctamente

---

## 📱 Comandos Útiles

```bash
# Ver estado
railway status

# Ver logs en tiempo real
railway logs --follow

# Ver variables
railway variables

# Añadir variable
railway variables set KEY=value

# Ver dominio/URL
railway domain

# Abrir dashboard
railway dashboard

# Abrir app en navegador
railway open

# Ejecutar comando en Railway
railway run <comando>

# Shell interactivo
railway shell

# Redeploy
railway up

# Ver servicios
railway list
```

---

## 🌐 URLs Importantes

Una vez desplegado, tu app estará en:

- **Base**: Tu dominio Railway (ej: `ecomodel-hub-production.up.railway.app`)
- **API Docs**: `/api/v1/docs`
- **Login**: `/login`
- **App**: `/app`
- **Budget Impact**: `/budget-impact`
- **Decision Tree**: `/decision-tree`
- **Survival**: `/survival`
- **VOI**: `/voi`

---

## 🆘 ¿Necesitas Ayuda?

1. **Ver logs**: `railway logs --follow`
2. **Ver estado**: `railway status`
3. **Dashboard**: `railway dashboard`
4. **Documentación**: [docs.railway.app](https://docs.railway.app)
5. **Discord**: [discord.gg/railway](https://discord.gg/railway)

---

## 🎉 Una Vez Todo Funcione

### Deployments Automáticos

Cada vez que hagas `git push`, Railway desplegará automáticamente:

```bash
git add .
git commit -m "Mi cambio"
git push

# Railway despliega automáticamente en ~3-5 minutos
```

### Monitoreo

Ver logs en tiempo real:

```bash
railway logs --follow
```

Ver métricas en el dashboard:

```bash
railway dashboard
```

---

**¡Ya casi está! Solo necesitas ejecutar los comandos de arriba y tu app estará completamente funcional en Railway! 🚂🚀**

Todos los análisis científicos (NumPy, SciPy, Pandas) funcionarán perfectamente.
