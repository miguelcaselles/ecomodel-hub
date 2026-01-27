# Guía de Deployment en Vercel

Esta guía te ayudará a desplegar EcoModel Hub en Vercel paso por paso.

## Prerequisitos

1. Cuenta en [Vercel](https://vercel.com)
2. Cuenta en [Neon](https://neon.tech) o [Supabase](https://supabase.com) para PostgreSQL
3. (Opcional) Cuenta en [Upstash](https://upstash.com) para Redis
4. Vercel CLI instalado: `npm install -g vercel`

## Paso 1: Preparar la Base de Datos

### Opción A: Neon (Recomendado)

1. Ve a [neon.tech](https://neon.tech) y crea una cuenta
2. Crea un nuevo proyecto
3. Copia la connection string (debe verse así):
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```

### Opción B: Supabase

1. Ve a [supabase.com](https://supabase.com) y crea un proyecto
2. Ve a Settings > Database
3. Copia la connection string (modo URI)

## Paso 2: Preparar Redis (Opcional)

1. Ve a [upstash.com](https://upstash.com) y crea una cuenta
2. Crea una base de datos Redis
3. Copia la connection string

## Paso 3: Configurar el Proyecto

### 3.1 Login en Vercel

```bash
vercel login
```

### 3.2 Inicializar el Proyecto

Desde la raíz del proyecto:

```bash
vercel
```

Responde las preguntas:
- Set up and deploy? **Y**
- Which scope? (Selecciona tu cuenta)
- Link to existing project? **N**
- What's your project's name? `ecomodel-hub`
- In which directory is your code located? `./`

## Paso 4: Configurar Variables de Entorno

### 4.1 Desde la línea de comandos:

```bash
# Database
vercel env add DATABASE_URL production
# Pega tu connection string de Neon/Supabase

# Secret Key (genera uno con: openssl rand -hex 32)
vercel env add SECRET_KEY production

# CORS Origins (tu dominio de Vercel)
vercel env add BACKEND_CORS_ORIGINS production
# Valor: ["https://ecomodel-hub.vercel.app","https://ecomodel-hub-*.vercel.app"]

# Algorithm
vercel env add ALGORITHM production
# Valor: HS256

# Token expiration
vercel env add ACCESS_TOKEN_EXPIRE_MINUTES production
# Valor: 30

# Redis (opcional)
vercel env add REDIS_URL production
# Pega tu connection string de Upstash
```

### 4.2 O desde el Dashboard de Vercel:

1. Ve a tu proyecto en [vercel.com](https://vercel.com)
2. Ve a Settings > Environment Variables
3. Añade todas las variables necesarias

## Paso 5: Ejecutar Migraciones

Después del primer deployment, necesitas ejecutar las migraciones:

```bash
# Conéctate a tu base de datos Neon/Supabase
# Opción 1: Usar el cliente psql
psql "postgresql://user:password@host/db?sslmode=require"

# Opción 2: Usar el SQL Editor de Neon/Supabase
# Copia y pega el contenido de los archivos de migración
```

O desde tu máquina local:

```bash
cd backend
# Actualiza DATABASE_URL en .env con tu URL de producción
alembic upgrade head
```

## Paso 6: Seed de Datos (Opcional)

Para cargar datos de demostración:

```bash
cd backend
# Asegúrate de que DATABASE_URL apunte a producción
python seed_data.py
```

## Paso 7: Desplegar

```bash
vercel --prod
```

## Paso 8: Verificar el Deployment

1. Ve a la URL que te proporciona Vercel
2. Accede a la documentación de la API: `https://tu-dominio.vercel.app/api/v1/docs`
3. Prueba el login y otros endpoints

## URLs Importantes

Después del deployment, tu aplicación estará disponible en:
- **Frontend/App**: `https://ecomodel-hub.vercel.app/app`
- **API Docs**: `https://ecomodel-hub.vercel.app/api/v1/docs`
- **Login**: `https://ecomodel-hub.vercel.app/login`
- **Budget Impact**: `https://ecomodel-hub.vercel.app/budget-impact`
- **Decision Tree**: `https://ecomodel-hub.vercel.app/decision-tree`
- **Survival Analysis**: `https://ecomodel-hub.vercel.app/survival`
- **VOI Analysis**: `https://ecomodel-hub.vercel.app/voi`

## Troubleshooting

### Error: "Module not found"
- Verifica que `vercel.json` esté configurado correctamente
- Asegúrate de que todos los imports usen rutas relativas correctas

### Error: "Database connection failed"
- Verifica que DATABASE_URL esté configurada correctamente
- Asegúrate de incluir `?sslmode=require` en la connection string
- Verifica que las migraciones se hayan ejecutado

### Error: "Function timeout"
- Las funciones serverless de Vercel tienen un timeout de 10s (plan gratuito)
- Si necesitas más tiempo, considera upgrading a Vercel Pro

### PDFs no se generan correctamente
- Vercel serverless functions tienen limitaciones de memoria y tiempo
- Considera usar un servicio externo para generación de PDFs en producción

## Comandos Útiles

```bash
# Ver logs en tiempo real
vercel logs

# Ver deployments
vercel ls

# Rollback a deployment anterior
vercel rollback [deployment-url]

# Remover deployment
vercel remove [deployment-url]
```

## Consideraciones de Producción

1. **Rate Limiting**: Considera añadir rate limiting para APIs públicas
2. **Caching**: Usa Redis (Upstash) para cachear resultados de análisis
3. **Monitoreo**: Configura Vercel Analytics y Sentry para tracking
4. **Backups**: Configura backups automáticos en Neon/Supabase
5. **Custom Domain**: Configura un dominio personalizado en Vercel

## Alternativas a Vercel

Si Vercel no funciona bien para tu caso de uso:
- **Railway**: Mejor para aplicaciones stateful y workers
- **Render**: Soporte nativo para FastAPI
- **Fly.io**: Deployment global con mejor control
- **AWS Elastic Beanstalk**: Más control pero más complejo

---

¡Tu aplicación EcoModel Hub está lista para producción! 🚀
