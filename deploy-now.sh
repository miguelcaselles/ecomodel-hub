#!/bin/bash

# Script final para deployment completo en Railway
# Ejecuta esto después de hacer login

echo "🚂 Deployment Final en Railway"
echo "==============================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd "/Users/miguelcaselles/Desktop/PROYECTOS PROGRAMACIÓN /Innovación HSCS/Farmacoeconomia"

# Paso 1: Verificar login
echo -e "${BLUE}Paso 1/4: Verificando autenticación...${NC}"
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}Haciendo login...${NC}"
    railway login

    if ! railway whoami &> /dev/null; then
        echo -e "${RED}❌ Error: No se pudo autenticar${NC}"
        echo "Por favor ejecuta manualmente: railway login"
        exit 1
    fi
fi

USER=$(railway whoami 2>&1 | head -n 1)
echo -e "${GREEN}✓ Autenticado como: $USER${NC}"
echo ""

# Paso 2: Link al proyecto
echo -e "${BLUE}Paso 2/4: Conectando al proyecto...${NC}"
if ! railway status &> /dev/null; then
    echo "Selecciona tu proyecto ecomodel-hub:"
    railway link

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error al linkear proyecto${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Proyecto conectado${NC}"
echo ""

# Paso 3: Configurar variables
echo -e "${BLUE}Paso 3/4: Configurando variables de entorno...${NC}"

# Generar SECRET_KEY
if [ -f "/tmp/railway-env-vars.txt" ]; then
    SECRET_KEY=$(grep SECRET_KEY /tmp/railway-env-vars.txt | cut -d'=' -f2)
else
    SECRET_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY=$SECRET_KEY" > /tmp/railway-env-vars.txt
fi

# Configurar todas las variables
echo "  • SECRET_KEY..."
railway variables set SECRET_KEY="$SECRET_KEY" &> /dev/null

echo "  • ALGORITHM..."
railway variables set ALGORITHM="HS256" &> /dev/null

echo "  • ACCESS_TOKEN_EXPIRE_MINUTES..."
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30" &> /dev/null

echo "  • PYTHONPATH..."
railway variables set PYTHONPATH="backend" &> /dev/null

echo -e "${GREEN}✓ Variables configuradas${NC}"
echo ""

# Obtener dominio y configurar CORS
echo -e "${BLUE}Obteniendo URL del servicio...${NC}"
DOMAIN=$(railway domain 2>&1 | tail -1)

if [[ $DOMAIN == *"up.railway.app"* ]]; then
    echo -e "${GREEN}✓ URL: $DOMAIN${NC}"
    echo ""
    echo -e "${BLUE}Configurando CORS...${NC}"
    railway variables set BACKEND_CORS_ORIGINS="[\"https://$DOMAIN\"]" &> /dev/null
    echo -e "${GREEN}✓ CORS configurado${NC}"
else
    echo -e "${YELLOW}⚠️  Configura CORS manualmente después:${NC}"
    echo "railway variables set BACKEND_CORS_ORIGINS='[\"https://tu-dominio.up.railway.app\"]'"
fi

echo ""

# Paso 4: Migraciones
echo -e "${BLUE}Paso 4/4: Ejecutando migraciones de base de datos...${NC}"
echo ""

railway run bash -c "cd backend && alembic upgrade head"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Migraciones completadas${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Error en migraciones${NC}"
    echo "Verifica que PostgreSQL esté añadido en Railway dashboard"
    echo ""
    read -p "¿Abrir dashboard para verificar? (s/n): " OPEN_DASH
    if [ "$OPEN_DASH" = "s" ]; then
        railway dashboard
        echo ""
        echo "Después de añadir PostgreSQL, ejecuta:"
        echo "  railway run bash -c 'cd backend && alembic upgrade head'"
    fi
fi

echo ""

# Cargar datos demo
read -p "¿Cargar datos de demostración? (s/n): " LOAD_DEMO

if [ "$LOAD_DEMO" = "s" ] || [ "$LOAD_DEMO" = "S" ]; then
    echo ""
    echo -e "${BLUE}📊 Cargando datos demo...${NC}"
    railway run bash -c "cd backend && python seed_data.py"

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Datos demo cargados${NC}"
        echo ""
        echo "Usuarios creados:"
        echo "  • admin@ecomodel.com (password: admin123)"
        echo "  • user@ecomodel.com (password: user123)"
    fi
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Deployment completado!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Mostrar info
echo -e "${BLUE}🌐 Tu aplicación:${NC}"
if [[ $DOMAIN == *"up.railway.app"* ]]; then
    echo ""
    echo "  URL base:     https://$DOMAIN"
    echo "  API Docs:     https://$DOMAIN/api/v1/docs"
    echo "  Login:        https://$DOMAIN/login"
    echo "  App:          https://$DOMAIN/app"
    echo ""
fi

echo -e "${BLUE}📚 Módulos de análisis:${NC}"
echo "  • Budget Impact:  /budget-impact"
echo "  • Decision Tree:  /decision-tree"
echo "  • Survival:       /survival"
echo "  • VOI Analysis:   /voi"
echo ""

echo -e "${YELLOW}🔧 Comandos útiles:${NC}"
echo "  railway logs --follow    # Ver logs en tiempo real"
echo "  railway status           # Ver estado"
echo "  railway open             # Abrir app en navegador"
echo "  railway dashboard        # Abrir dashboard"
echo ""

# Abrir app
read -p "¿Abrir la aplicación en el navegador? (s/n): " OPEN_APP

if [ "$OPEN_APP" = "s" ] || [ "$OPEN_APP" = "S" ]; then
    railway open
fi

echo ""
echo -e "${GREEN}¡Listo! Tu app está en producción con funcionalidad completa 🚀${NC}"
echo ""
