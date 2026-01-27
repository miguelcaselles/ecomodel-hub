#!/bin/bash

# Script de setup rápido - Asume que ya hiciste railway login y railway link

echo "🚂 Setup Rápido de Railway"
echo "=========================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "/Users/miguelcaselles/Desktop/PROYECTOS PROGRAMACIÓN /Innovación HSCS/Farmacoeconomia"

# Generar SECRET_KEY
echo -e "${BLUE}🔐 Generando SECRET_KEY...${NC}"
if [ -f "/tmp/railway-env-vars.txt" ]; then
    SECRET_KEY=$(grep SECRET_KEY /tmp/railway-env-vars.txt | cut -d'=' -f2)
    echo -e "${GREEN}✓ Usando SECRET_KEY existente${NC}"
else
    SECRET_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY=$SECRET_KEY" > /tmp/railway-env-vars.txt
    echo -e "${GREEN}✓ Nuevo SECRET_KEY generado${NC}"
fi

echo ""
echo -e "${BLUE}⚙️  Configurando variables de entorno...${NC}"

# Configurar variables
railway variables set SECRET_KEY="$SECRET_KEY" 2>&1
railway variables set ALGORITHM="HS256" 2>&1
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30" 2>&1
railway variables set PYTHONPATH="backend" 2>&1

echo ""
echo -e "${GREEN}✓ Variables configuradas${NC}"

echo ""
echo -e "${BLUE}🌐 Obteniendo URL del servicio...${NC}"
DOMAIN=$(railway domain 2>&1 | grep "up.railway.app" || echo "")

if [ ! -z "$DOMAIN" ]; then
    echo -e "${GREEN}✓ URL: $DOMAIN${NC}"

    # Configurar CORS
    echo ""
    echo -e "${BLUE}🔧 Configurando CORS...${NC}"
    railway variables set BACKEND_CORS_ORIGINS="[\"https://$DOMAIN\"]" 2>&1
    echo -e "${GREEN}✓ CORS configurado${NC}"
else
    echo -e "${YELLOW}⚠️  No se pudo obtener el dominio automáticamente${NC}"
    echo "Configúralo manualmente después con:"
    echo '  railway variables set BACKEND_CORS_ORIGINS='"'"'["https://tu-dominio.up.railway.app"]'"'"
fi

echo ""
echo -e "${BLUE}🗄️  Ejecutando migraciones...${NC}"
railway run bash -c "cd backend && alembic upgrade head"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Migraciones completadas${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Verifica que PostgreSQL esté añadido${NC}"
fi

echo ""
echo -e "${BLUE}📊 ¿Cargar datos de demostración?${NC}"
echo "Esto creará usuarios y escenarios de ejemplo"
read -p "(s/n): " LOAD_DEMO

if [ "$LOAD_DEMO" = "s" ] || [ "$LOAD_DEMO" = "S" ]; then
    echo ""
    echo -e "${BLUE}📦 Cargando datos...${NC}"
    railway run bash -c "cd backend && python seed_data.py"
    echo -e "${GREEN}✓ Datos cargados${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Setup completado!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Ver logs recientes
echo -e "${BLUE}📋 Logs recientes:${NC}"
railway logs --limit 10

echo ""
echo -e "${BLUE}🌐 Abriendo aplicación...${NC}"
railway open

echo ""
echo -e "${YELLOW}📚 Comandos útiles:${NC}"
echo "  railway logs --follow    # Ver logs en tiempo real"
echo "  railway status           # Ver estado"
echo "  railway dashboard        # Abrir dashboard"
echo "  railway open             # Abrir app"
echo ""
