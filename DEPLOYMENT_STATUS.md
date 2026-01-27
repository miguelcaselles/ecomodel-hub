# 🚀 Estado del Deployment en Vercel

## ✅ Deployment Exitoso

Tu aplicación EcoModel Hub ha sido desplegada exitosamente en Vercel!

### 🌐 URLs de la Aplicación

#### Preview (Desarrollo/Testing)
- **URL Principal**: https://ecomodel-8w357k74w-miguel-caselles-projects.vercel.app
- **API Docs**: https://ecomodel-8w357k74w-miguel-caselles-projects.vercel.app/api/v1/docs
- **Login**: https://ecomodel-8w357k74w-miguel-caselles-projects.vercel.app/login
- **App**: https://ecomodel-8w357k74w-miguel-caselles-projects.vercel.app/app

#### Producción (Próximamente)
Para desplegar a producción con un dominio permanente:
```bash
vercel --prod
```

La URL de producción será: **https://ecomodel-hub.vercel.app**

---

## 📋 Próximos Pasos IMPORTANTES

### 1. Configurar Base de Datos ⚠️ CRÍTICO

La aplicación necesita una base de datos PostgreSQL para funcionar. Sin esto, la app NO funcionará.

#### Opción A: Neon (Recomendado - Gratis)
1. Ve a [neon.tech](https://neon.tech)
2. Crea una cuenta y un nuevo proyecto
3. Copia la connection string
4. Ejecuta:
   ```bash
   vercel env add DATABASE_URL production
   # Pega tu connection string cuando te lo pida
   ```

#### Opción B: Supabase (También gratis)
1. Ve a [supabase.com](https://supabase.com)
2. Crea un proyecto
3. Ve a Settings > Database
4. Copia la connection string (URI mode)
5. Ejecuta el mismo comando de arriba

### 2. Configurar Variables de Entorno

Puedes usar el script automatizado:
```bash
./configure-vercel-env.sh
```

O configurar manualmente:
```bash
# Secret key (genera uno con: openssl rand -hex 32)
vercel env add SECRET_KEY production

# Database
vercel env add DATABASE_URL production

# CORS origins
vercel env add BACKEND_CORS_ORIGINS production
# Valor: ["https://ecomodel-hub.vercel.app"]

# Otros
vercel env add ALGORITHM production  # Valor: HS256
vercel env add ACCESS_TOKEN_EXPIRE_MINUTES production  # Valor: 30
```

### 3. Ejecutar Migraciones de Base de Datos

Una vez tengas la base de datos configurada:

```bash
cd backend
# Actualiza .env con tu DATABASE_URL de producción
DATABASE_URL="tu-url-aqui" alembic upgrade head
```

O ejecuta el SQL directamente en Neon/Supabase:
- Ve al SQL Editor de tu proveedor de base de datos
- Copia y pega los archivos de migración de `backend/alembic/versions/`

### 4. Cargar Datos de Demo (Opcional)

```bash
cd backend
DATABASE_URL="tu-url-aqui" python seed_data.py
```

### 5. Desplegar a Producción

```bash
vercel --prod
```

---

## 📊 Características del Deployment

### ✅ Funcionalidades Disponibles

- ✅ Frontend completo (HTML estático)
- ✅ API REST con FastAPI
- ✅ Autenticación con JWT
- ✅ Generación de PDFs (reportlab)
- ✅ Generación de Excel (openpyxl)
- ✅ Gestión de escenarios
- ✅ CRUD completo

### ⚠️ Limitaciones (Debido a restricciones de Vercel Serverless)

- ❌ **Análisis científicos complejos**: NumPy, SciPy y Pandas se eliminaron por tamaño
  - Los endpoints de análisis complejos NO funcionarán hasta que se implemente una solución alternativa
  - Opciones:
    1. Migrar análisis complejos a un microservicio separado
    2. Usar Railway/Render para hosting completo
    3. Implementar análisis simplificados sin dependencias pesadas

- ❌ **Celery/Redis**: No disponible en serverless
  - Las tareas en background no funcionarán
  - Todas las operaciones son síncronas

- ⏱️ **Timeout**: 10 segundos máximo por request (plan gratuito)
  - Análisis que tomen más tiempo fallarán
  - Considera Vercel Pro (60s timeout) si necesitas más tiempo

### 📦 Archivos Importantes Creados

- `vercel.json` - Configuración de deployment
- `api/index.py` - Entry point para Vercel
- `requirements.txt` - Dependencias optimizadas para Vercel
- `requirements-full.txt` - Dependencias completas (para desarrollo local)
- `deploy.sh` - Script de deployment interactivo
- `configure-vercel-env.sh` - Script para configurar variables de entorno
- `DEPLOYMENT_VERCEL.md` - Guía completa de deployment

---

## 🛠️ Comandos Útiles

```bash
# Ver logs en tiempo real
vercel logs --follow

# Ver logs de un deployment específico
vercel logs [deployment-url]

# Redeploy
vercel --prod

# Ver deployments
vercel ls

# Rollback (volver a versión anterior)
vercel rollback [deployment-url]

# Ver información del proyecto
vercel inspect

# Abrir dashboard en el navegador
vercel dashboard
```

---

## 🐛 Troubleshooting

### La API no responde
1. Verifica que las variables de entorno estén configuradas: `vercel env ls`
2. Revisa los logs: `vercel logs --follow`
3. Asegúrate de que DATABASE_URL esté configurada correctamente

### Errores de base de datos
1. Verifica la connection string (debe incluir `?sslmode=require` para Neon)
2. Confirma que las migraciones se ejecutaron
3. Verifica que la base de datos esté activa

### 500 Internal Server Error
1. Revisa los logs de Vercel
2. Verifica que todas las variables de entorno estén configuradas
3. Asegúrate de que SECRET_KEY tenga al menos 32 caracteres

### Funciones timeout
- Las funciones serverless gratuitas tienen timeout de 10s
- Considera Vercel Pro para 60s de timeout
- O migra análisis pesados a otro servicio

---

## 🚀 Alternativas de Hosting (Si Vercel no es suficiente)

Si necesitas todas las funcionalidades científicas completas:

### Railway (Recomendado para este proyecto)
- ✅ Soporte completo para Python científico
- ✅ Sin límites de tamaño de dependencias
- ✅ Soporte para workers/celery
- ✅ PostgreSQL y Redis incluidos
- 💰 $5/mes después del trial

```bash
# Deployment en Railway
railway login
railway init
railway up
```

### Render
- ✅ Similar a Railway
- ✅ Buen free tier
- ✅ Fácil de configurar
- 💰 Gratis para empezar

### Fly.io
- ✅ Deployment global
- ✅ Full control
- ✅ Buen pricing

---

## 📞 Soporte

- **Dashboard de Vercel**: https://vercel.com/dashboard
- **Documentación**: https://vercel.com/docs
- **Status**: https://www.vercel-status.com/

---

## ✅ Checklist Final

Antes de usar la app en producción, asegúrate de:

- [ ] Configurar DATABASE_URL
- [ ] Configurar SECRET_KEY
- [ ] Ejecutar migraciones
- [ ] Cargar datos de seed (opcional)
- [ ] Probar login en /api/v1/docs
- [ ] Verificar que los PDFs se generen correctamente
- [ ] Configurar dominio personalizado (opcional)
- [ ] Habilitar Vercel Analytics (opcional)
- [ ] Configurar alertas de errores (Sentry, etc.)

---

**¡Tu aplicación está lista para usarse!** 🎉

Recuerda que para funcionalidad completa de análisis científicos, considera migrar a Railway o Render.
