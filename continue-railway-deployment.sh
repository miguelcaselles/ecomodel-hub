#!/bin/bash

# Script para continuar con el deployment en Railway
# Ya que el proyecto está conectado, ahora vamos a completar la configuración

echo "🚂 Continuando Deployment en Railway"
echo "====================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI no está instalado${NC}"
    echo "Instálalo con: npm install -g @railway/cli"
    exit 1
fi

echo -e "${BLUE}📦 Verificando autenticación...${NC}"

# Login si es necesario
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}Necesitas hacer login en Railway${NC}"
    echo "Ejecuta: railway login"
    echo ""
    read -p "¿Ya hiciste login? (s/n): " LOGGED_IN

    if [ "$LOGGED_IN" != "s" ] && [ "$LOGGED_IN" != "S" ]; then
        echo "Por favor ejecuta: railway login"
        exit 1
    fi
fi

USER=$(railway whoami 2>&1 | head -n 1)
echo -e "${GREEN}✓ Autenticado como: $USER${NC}"
echo ""

# Link al proyecto si es necesario
echo -e "${BLUE}🔗 Verificando link al proyecto...${NC}"

cd "/Users/miguelcaselles/Desktop/PROYECTOS PROGRAMACIÓN /Innovación HSCS/Farmacoeconomia"

if ! railway status &> /dev/null; then
    echo -e "${YELLOW}⚠️  No hay proyecto linkeado en este directorio${NC}"
    echo ""
    echo "Voy a linkear al proyecto..."
    railway link

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error al linkear proyecto${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Proyecto linkeado${NC}"
echo ""

# Mostrar servicios actuales
echo -e "${BLUE}📊 Servicios actuales en Railway:${NC}"
railway status

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Verificar si hay PostgreSQL y Redis
echo -e "${YELLOW}📋 Checklist de Servicios:${NC}"
echo ""
echo "Verifica en el dashboard de Railway (railway dashboard) que tengas:"
echo ""
echo "  [ ] Servicio Web (ecomodel-hub)"
echo "  [ ] PostgreSQL database"
echo "  [ ] Redis database (opcional)"
echo ""
read -p "¿Están todos los servicios añadidos? (s/n): " SERVICES_OK

if [ "$SERVICES_OK" != "s" ] && [ "$SERVICES_OK" != "S" ]; then
    echo ""
    echo -e "${YELLOW}Para añadir servicios:${NC}"
    echo ""
    echo "1. Abre el dashboard:"
    echo "   railway dashboard"
    echo ""
    echo "2. Click '+ New' → 'Database'"
    echo ""
    echo "3. Añade PostgreSQL (obligatorio)"
    echo ""
    echo "4. Añade Redis (recomendado)"
    echo ""
    exit 0
fi

echo ""
echo -e "${GREEN}✓ Servicios verificados${NC}"
echo ""

# Verificar variables de entorno
echo -e "${BLUE}🔐 Verificando variables de entorno...${NC}"
echo ""

# Leer SECRET_KEY desde archivo temporal si existe
if [ -f "/tmp/railway-env-vars.txt" ]; then
    SECRET_KEY=$(grep SECRET_KEY /tmp/railway-env-vars.txt | cut -d'=' -f2)
    echo -e "${GREEN}✓ SECRET_KEY encontrado en cache${NC}"
else
    echo -e "${YELLOW}Generando nuevo SECRET_KEY...${NC}"
    SECRET_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY=$SECRET_KEY" > /tmp/railway-env-vars.txt
fi

echo ""
echo -e "${BLUE}Configurando variables de entorno...${NC}"

# Configurar variables
railway variables set SECRET_KEY="$SECRET_KEY" 2>&1
railway variables set ALGORITHM="HS256" 2>&1
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30" 2>&1
railway variables set PYTHONPATH="backend" 2>&1

echo ""
echo -e "${GREEN}✓ Variables de entorno configuradas${NC}"
echo ""

# Obtener URL del servicio
echo -e "${BLUE}🌐 Obteniendo URL del servicio...${NC}"
railway domain 2>&1

echo ""

# CORS
echo -e "${YELLOW}⚠️  IMPORTANTE: Configurar CORS${NC}"
echo ""
echo "Necesitas añadir manualmente la variable BACKEND_CORS_ORIGINS"
echo "con la URL de tu servicio."
echo ""
echo "Ejecuta:"
echo '  railway variables set BACKEND_CORS_ORIGINS='"'"'["https://tu-dominio.up.railway.app"]'"'"
echo ""
read -p "Presiona Enter cuando hayas configurado CORS..."

# Verificar deployment
echo ""
echo -e "${BLUE}📦 Verificando deployment...${NC}"
railway status

echo ""
echo -e "${BLUE}🗄️  Ejecutando migraciones de base de datos...${NC}"
echo ""

railway run bash -c "cd backend && alembic upgrade head"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Migraciones ejecutadas correctamente${NC}"
else
    echo ""
    echo -e "${RED}❌ Error al ejecutar migraciones${NC}"
    echo "Verifica que PostgreSQL esté configurado y DATABASE_URL exista"
    exit 1
fi

# Cargar datos de demo
echo ""
read -p "¿Quieres cargar datos de demostración? (s/n): " LOAD_SEED

if [ "$LOAD_SEED" = "s" ] || [ "$LOAD_SEED" = "S" ]; then
    echo ""
    echo -e "${BLUE}📊 Cargando datos de demo...${NC}"
    railway run bash -c "cd backend && python seed_data.py"

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Datos de demo cargados${NC}"
    fi
fi

# Ver logs
echo ""
echo -e "${BLUE}📋 Últimos logs:${NC}"
railway logs --limit 20

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Deployment completado!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Abrir app
echo -e "${BLUE}🌐 Abriendo aplicación...${NC}"
railway open

echo ""
echo -e "${YELLOW}📚 Próximos pasos:${NC}"
echo ""
echo "1. Verifica que la app funcione en el navegador"
echo "2. Prueba el login en /api/v1/docs"
echo "3. Prueba los análisis científicos"
echo ""
echo "Comandos útiles:"
echo "  railway logs --follow     # Ver logs en tiempo real"
echo "  railway status            # Ver estado"
echo "  railway open              # Abrir app"
echo "  railway dashboard         # Abrir dashboard"
echo ""
