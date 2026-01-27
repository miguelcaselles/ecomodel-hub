#!/bin/bash

# Script de deployment para Railway con funcionalidad completa
# Autor: EcoModel Hub Team

echo "🚂 Deployment en Railway - Funcionalidad Completa"
echo "=================================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Railway CLI
echo -e "${BLUE}📦 Verificando Railway CLI...${NC}"
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI no está instalado${NC}"
    echo ""
    echo "Instálalo con:"
    echo "  npm install -g @railway/cli"
    echo ""
    echo "O con Homebrew:"
    echo "  brew install railway"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Railway CLI instalado${NC}"
echo ""

# Login
echo -e "${BLUE}🔐 Verificando autenticación...${NC}"
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  No estás autenticado en Railway${NC}"
    echo "Abriendo navegador para login..."
    railway login

    if ! railway whoami &> /dev/null; then
        echo -e "${RED}❌ Login falló o fue cancelado${NC}"
        exit 1
    fi
fi

USER=$(railway whoami 2>&1)
echo -e "${GREEN}✓ Autenticado como: $USER${NC}"
echo ""

# Información del proyecto
echo -e "${BLUE}📋 Información del Proyecto${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Nombre: EcoModel Hub"
echo "  Repositorio: https://github.com/miguelcaselles/ecomodel-hub"
echo "  Stack: Python (FastAPI) + PostgreSQL + Redis"
echo "  Funcionalidad: COMPLETA (NumPy, SciPy, Pandas)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Elegir método de deployment
echo -e "${BLUE}🚀 Método de Deployment${NC}"
echo ""
echo "Railway ofrece dos formas de desplegar:"
echo ""
echo "1) Desde GitHub (RECOMENDADO)"
echo "   - Deployments automáticos en cada push"
echo "   - Mejor integración con CI/CD"
echo "   - Rollbacks fáciles"
echo ""
echo "2) Desde CLI (Directo)"
echo "   - Deploy inmediato desde tu máquina"
echo "   - Útil para testing rápido"
echo ""
read -p "Selecciona una opción (1 o 2): " DEPLOY_METHOD

if [ "$DEPLOY_METHOD" = "1" ]; then
    echo ""
    echo -e "${GREEN}📦 Deployment desde GitHub${NC}"
    echo ""
    echo "Pasos a seguir:"
    echo ""
    echo "1. Ve a: https://railway.app/new"
    echo ""
    echo "2. Haz clic en 'Deploy from GitHub repo'"
    echo ""
    echo "3. Busca y selecciona: 'miguelcaselles/ecomodel-hub'"
    echo ""
    echo "4. Railway detectará automáticamente Python/FastAPI"
    echo ""
    echo "5. Haz clic en 'Deploy Now'"
    echo ""
    echo "6. Añade PostgreSQL:"
    echo "   - Click en '+ New'"
    echo "   - 'Database' → 'PostgreSQL'"
    echo ""
    echo "7. Añade Redis:"
    echo "   - Click en '+ New'"
    echo "   - 'Database' → 'Redis'"
    echo ""
    echo "8. Configura variables de entorno:"
    echo "   - SECRET_KEY: $(openssl rand -hex 32)"
    echo "   - ALGORITHM: HS256"
    echo "   - ACCESS_TOKEN_EXPIRE_MINUTES: 30"
    echo "   - PYTHONPATH: backend"
    echo ""
    echo "9. Espera a que el deploy complete (~5 min primera vez)"
    echo ""
    echo "10. Ejecuta migraciones:"
    echo "    railway run bash -c 'cd backend && alembic upgrade head'"
    echo ""
    echo -e "${YELLOW}¿Quieres abrir Railway en el navegador ahora?${NC}"
    read -p "(s/n): " OPEN_BROWSER

    if [ "$OPEN_BROWSER" = "s" ] || [ "$OPEN_BROWSER" = "S" ]; then
        open "https://railway.app/new"
        echo ""
        echo -e "${GREEN}✓ Navegador abierto${NC}"
    fi

elif [ "$DEPLOY_METHOD" = "2" ]; then
    echo ""
    echo -e "${GREEN}🚀 Deployment Directo desde CLI${NC}"
    echo ""

    # Inicializar proyecto
    echo -e "${BLUE}📦 Inicializando proyecto...${NC}"

    cd "/Users/miguelcaselles/Desktop/PROYECTOS PROGRAMACIÓN /Innovación HSCS/Farmacoeconomia"

    # Crear nuevo proyecto
    echo "Creando nuevo proyecto en Railway..."
    railway init

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error al inicializar proyecto${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Proyecto inicializado${NC}"
    echo ""

    # Configurar variables de entorno
    echo -e "${BLUE}🔐 Configurando variables de entorno...${NC}"

    SECRET_KEY=$(openssl rand -hex 32)

    railway variables set SECRET_KEY="$SECRET_KEY"
    railway variables set ALGORITHM="HS256"
    railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"
    railway variables set PYTHONPATH="backend"

    echo -e "${GREEN}✓ Variables configuradas${NC}"
    echo ""

    # Desplegar
    echo -e "${BLUE}🚀 Desplegando aplicación...${NC}"
    echo "Esto tomará unos 5-10 minutos (primera vez)..."
    echo ""

    railway up --detach

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ ¡Deployment exitoso!${NC}"
        echo ""

        # Obtener URL
        echo -e "${BLUE}🌐 Obteniendo URL...${NC}"
        railway open &

        echo ""
        echo -e "${YELLOW}📋 Próximos pasos IMPORTANTES:${NC}"
        echo ""
        echo "1. Añadir PostgreSQL:"
        echo "   railway add postgresql"
        echo ""
        echo "2. Añadir Redis (opcional):"
        echo "   railway add redis"
        echo ""
        echo "3. Ejecutar migraciones:"
        echo "   railway run bash -c 'cd backend && alembic upgrade head'"
        echo ""
        echo "4. Cargar datos de demo:"
        echo "   railway run bash -c 'cd backend && python seed_data.py'"
        echo ""

    else
        echo ""
        echo -e "${RED}❌ Error en el deployment${NC}"
        echo "Revisa los logs con: railway logs"
        exit 1
    fi

else
    echo -e "${RED}❌ Opción inválida${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ¡Deployment en progreso! 🚂🚀${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📚 Documentación completa en: DEPLOYMENT_RAILWAY.md"
echo "🛠️  Comandos útiles:"
echo "  railway logs        - Ver logs en tiempo real"
echo "  railway status      - Ver estado del deployment"
echo "  railway open        - Abrir app en navegador"
echo "  railway vars        - Ver variables de entorno"
echo ""
echo "🔧 Para más ayuda:"
echo "  https://docs.railway.app"
echo ""
