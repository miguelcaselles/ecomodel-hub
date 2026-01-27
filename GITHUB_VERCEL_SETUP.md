# ✅ GitHub & Vercel Setup Completado

## 🎉 ¡Tu aplicación está en GitHub y lista para Vercel!

### 📦 Repositorio GitHub

**URL**: [https://github.com/miguelcaselles/ecomodel-hub](https://github.com/miguelcaselles/ecomodel-hub)

El código completo de EcoModel Hub ha sido subido a GitHub con:
- ✅ 109 archivos
- ✅ 26,353 líneas de código
- ✅ Configuración completa de Vercel
- ✅ Scripts de deployment automatizado
- ✅ Documentación detallada

---

## 🚀 Próximo Paso: Conectar con Vercel desde GitHub

### Opción 1: Automático (Recomendado)

Ejecuta el script:
```bash
./setup-vercel-github.sh
```

Esto abrirá Vercel en tu navegador listo para importar el repositorio.

### Opción 2: Manual

1. **Ve a Vercel**: [https://vercel.com/new](https://vercel.com/new)

2. **Import Git Repository**
   - Selecciona "Import Git Repository"
   - Busca: `miguelcaselles/ecomodel-hub`
   - Haz clic en "Import"

3. **Configura el Proyecto**
   ```
   Framework Preset: Other
   Root Directory: ./
   Build Command: (dejar vacío)
   Output Directory: (dejar vacío)
   ```

4. **Añade Variables de Entorno** (IMPORTANTE)

   Antes de hacer deploy, añade estas variables:

   | Variable | Valor | Dónde Obtenerlo |
   |----------|-------|-----------------|
   | `DATABASE_URL` | `postgresql://user:pass@host/db` | [Neon](https://neon.tech) o [Supabase](https://supabase.com) |
   | `SECRET_KEY` | `[32+ caracteres aleatorios]` | Genera con: `openssl rand -hex 32` |
   | `ALGORITHM` | `HS256` | Valor fijo |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Valor fijo |
   | `BACKEND_CORS_ORIGINS` | `["https://ecomodel-hub.vercel.app"]` | Ajusta según tu dominio |

5. **Deploy**
   - Haz clic en "Deploy"
   - Espera 2-3 minutos
   - ¡Tu app estará en línea!

---

## 🔐 Setup de Base de Datos (CRÍTICO)

Sin base de datos, la aplicación NO funcionará. Sigue estos pasos:

### Opción A: Neon (Recomendado - Más rápido)

1. Ve a [https://neon.tech](https://neon.tech)
2. Crea una cuenta (gratis)
3. Crea un nuevo proyecto
4. Copia la **Connection String**:
   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
5. Pégala como `DATABASE_URL` en Vercel

### Opción B: Supabase (Alternativa)

1. Ve a [https://supabase.com](https://supabase.com)
2. Crea un proyecto
3. Ve a: Settings → Database
4. Copia la **Connection String** (URI mode)
5. Pégala como `DATABASE_URL` en Vercel

---

## 📋 Después del Primer Deploy

Una vez que el deploy complete exitosamente:

### 1. Ejecutar Migraciones

```bash
# Desde tu máquina local
cd backend
DATABASE_URL="postgresql://..." alembic upgrade head
```

O ejecuta el SQL directamente en Neon/Supabase usando su SQL Editor.

### 2. (Opcional) Cargar Datos de Demo

```bash
cd backend
DATABASE_URL="postgresql://..." python seed_data.py
```

### 3. Verificar que Funciona

Accede a estas URLs (reemplaza con tu dominio de Vercel):

- **API Docs**: `https://ecomodel-hub.vercel.app/api/v1/docs`
- **Login**: `https://ecomodel-hub.vercel.app/login`
- **App**: `https://ecomodel-hub.vercel.app/app`

### 4. Probar Login

En `/api/v1/docs`, prueba el endpoint `/api/v1/auth/login` con:
```json
{
  "email": "admin@ecomodel.com",
  "password": "admin123"
}
```

---

## 🔄 Deployments Automáticos

¡Ahora cada vez que hagas `git push` a la rama `main`, Vercel desplegará automáticamente!

```bash
# Hacer cambios
git add .
git commit -m "Tu mensaje"
git push

# Vercel despliega automáticamente 🚀
```

---

## 📊 Estructura del Proyecto en GitHub

```
ecomodel-hub/
├── api/                    # Entry point para Vercel
│   └── index.py
├── backend/                # Código Python FastAPI
│   ├── app/                # Aplicación principal
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Seguridad y auth
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── services/       # Lógica de negocio
│   │   └── static/         # Frontend (HTML)
│   ├── engine/             # Motores de análisis
│   │   ├── budget_impact/
│   │   ├── decision_tree/
│   │   ├── markov/
│   │   ├── sensitivity/
│   │   └── survival/
│   └── alembic/            # Migraciones de BD
├── docker/                 # Dockerfiles
├── requirements.txt        # Dependencias (optimizado para Vercel)
├── requirements-full.txt   # Dependencias completas (desarrollo local)
├── vercel.json             # Configuración de Vercel
├── deploy.sh               # Script de deployment
├── setup-vercel-github.sh  # Script de setup
└── README.md               # Documentación principal
```

---

## ⚠️ Limitaciones Importantes (Vercel Serverless)

Debido a las restricciones de las funciones serverless de Vercel:

### ❌ NO Disponible:
- **NumPy, SciPy, Pandas**: Removidos por exceder límite de 250MB
- **Análisis científicos complejos**: No funcionarán hasta implementar alternativa
- **Celery/Redis**: No hay soporte para workers en background
- **Timeout**: Máximo 10 segundos por request (plan gratuito)

### ✅ SÍ Disponible:
- Frontend completo (HTML estático)
- API REST con FastAPI
- Autenticación JWT
- CRUD de escenarios
- Generación de PDFs (reportlab)
- Generación de Excel (openpyxl)
- Base de datos PostgreSQL

---

## 🔧 Alternativa para Funcionalidad Completa

Si necesitas **todos los análisis científicos** con NumPy/SciPy/Pandas:

### Railway (Recomendado)

Railway soporta aplicaciones completas sin restricciones:

```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**Ventajas de Railway:**
- ✅ Sin límites de tamaño de dependencias
- ✅ Soporta NumPy, SciPy, Pandas completos
- ✅ PostgreSQL y Redis incluidos
- ✅ Workers/Celery soportados
- 💰 $5/mes después del trial

**URL Railway**: [https://railway.app](https://railway.app)

### Render (Alternativa)

Similar a Railway, buen free tier:

```bash
# Solo necesitas conectar tu repo de GitHub
# Render se encarga del resto
```

**URL Render**: [https://render.com](https://render.com)

---

## 📚 Documentación Disponible

| Archivo | Descripción |
|---------|-------------|
| [README.md](README.md) | Overview del proyecto |
| [QUICK_START.md](QUICK_START.md) | Inicio rápido para desarrollo local |
| [DEPLOYMENT_VERCEL.md](DEPLOYMENT_VERCEL.md) | Guía completa de deployment en Vercel |
| [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md) | Estado actual del deployment |
| [GITHUB_VERCEL_SETUP.md](GITHUB_VERCEL_SETUP.md) | Este archivo |

---

## 🛠️ Comandos Útiles

```bash
# Ver el repositorio en GitHub
gh repo view --web

# Ver deployments en Vercel (después de conectar)
vercel ls

# Ver logs en tiempo real
vercel logs --follow

# Redeploy
vercel --prod

# Rollback a versión anterior
vercel rollback [deployment-url]
```

---

## ✅ Checklist Final

Antes de considerar el deployment completo:

- [x] Código subido a GitHub
- [x] Repositorio público creado
- [ ] Vercel conectado con GitHub
- [ ] Variables de entorno configuradas en Vercel
- [ ] Base de datos PostgreSQL creada (Neon/Supabase)
- [ ] DATABASE_URL configurada
- [ ] Primer deployment exitoso
- [ ] Migraciones ejecutadas
- [ ] Login probado y funcionando
- [ ] API Docs accesibles
- [ ] PDFs generándose correctamente

---

## 🆘 Troubleshooting

### No puedo conectar con GitHub en Vercel
- Asegúrate de estar logueado en Vercel
- Verifica que el repositorio es público o que Vercel tiene acceso

### El deployment falla con error de dependencias
- Revisa que `requirements.txt` esté en la raíz
- Verifica que no hay dependencias que excedan el límite

### La API responde 500
- Verifica que DATABASE_URL esté configurada
- Revisa los logs: `vercel logs --follow`
- Asegúrate de que SECRET_KEY tenga al menos 32 caracteres

### No puedo hacer login
- Verifica que las migraciones se ejecutaron
- Asegúrate de haber cargado los datos de seed
- Revisa que la base de datos esté activa

---

## 🎯 Próximos Pasos Recomendados

1. **Conectar Vercel con GitHub** (siguiente paso inmediato)
2. **Configurar base de datos en Neon**
3. **Ejecutar primer deployment**
4. **Correr migraciones**
5. **Probar la aplicación**
6. **Configurar dominio personalizado** (opcional)
7. **Añadir Vercel Analytics** (opcional)
8. **Considerar migrar a Railway** si necesitas análisis científicos completos

---

## 📞 Recursos

- **GitHub Repo**: [github.com/miguelcaselles/ecomodel-hub](https://github.com/miguelcaselles/ecomodel-hub)
- **Vercel Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)
- **Neon (Database)**: [neon.tech](https://neon.tech)
- **Railway (Alternative)**: [railway.app](https://railway.app)

---

**¡Tu aplicación está lista para el mundo! 🌍🚀**

El código está en GitHub y solo falta conectarlo con Vercel para tener tu app en producción.
