#!/bin/bash

# Script de deployment para Vercel
# Autor: EcoModel Hub Team

echo "🚀 Iniciando deployment en Vercel..."
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "vercel.json" ]; then
    echo -e "${RED}❌ Error: vercel.json no encontrado${NC}"
    echo "Asegúrate de ejecutar este script desde la raíz del proyecto"
    exit 1
fi

# Verificar que Vercel CLI está instalado
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Error: Vercel CLI no está instalado${NC}"
    echo "Instálalo con: npm install -g vercel"
    exit 1
fi

# Verificar login en Vercel
echo -e "${BLUE}📝 Verificando autenticación en Vercel...${NC}"
if ! vercel whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  No estás autenticado en Vercel${NC}"
    echo "Ejecuta: vercel login"
    exit 1
fi

USER=$(vercel whoami 2>&1 | head -n 1)
echo -e "${GREEN}✓ Autenticado como: $USER${NC}"
echo ""

# Preguntar si es production o preview
echo -e "${BLUE}🎯 Tipo de deployment:${NC}"
echo "1) Preview (desarrollo/testing)"
echo "2) Production (producción)"
read -p "Selecciona una opción (1 o 2): " DEPLOY_TYPE

if [ "$DEPLOY_TYPE" = "2" ]; then
    DEPLOY_CMD="vercel --prod"
    ENV_TYPE="production"
    echo -e "${YELLOW}⚠️  Vas a desplegar a PRODUCCIÓN${NC}"
else
    DEPLOY_CMD="vercel"
    ENV_TYPE="preview"
    echo -e "${BLUE}ℹ️  Vas a desplegar a PREVIEW${NC}"
fi

echo ""

# Verificar variables de entorno
echo -e "${BLUE}🔐 Verificando variables de entorno...${NC}"
echo ""
echo "Asegúrate de haber configurado las siguientes variables en Vercel:"
echo "  • DATABASE_URL"
echo "  • SECRET_KEY"
echo "  • ALGORITHM"
echo "  • ACCESS_TOKEN_EXPIRE_MINUTES"
echo "  • BACKEND_CORS_ORIGINS"
echo ""
read -p "¿Has configurado todas las variables? (s/n): " VARS_READY

if [ "$VARS_READY" != "s" ] && [ "$VARS_READY" != "S" ]; then
    echo -e "${YELLOW}⚠️  Configura las variables de entorno primero:${NC}"
    echo "  vercel env add VARIABLE_NAME $ENV_TYPE"
    echo "O desde el dashboard: https://vercel.com/dashboard"
    exit 0
fi

echo ""
echo -e "${BLUE}🏗️  Ejecutando deployment...${NC}"
echo "Comando: $DEPLOY_CMD"
echo ""

# Ejecutar deployment
$DEPLOY_CMD

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ ¡Deployment exitoso!${NC}"
    echo ""
    echo -e "${BLUE}📍 URLs importantes:${NC}"
    echo "  • API Docs: [tu-dominio]/api/v1/docs"
    echo "  • Login: [tu-dominio]/login"
    echo "  • App: [tu-dominio]/app"
    echo "  • Budget Impact: [tu-dominio]/budget-impact"
    echo "  • Decision Tree: [tu-dominio]/decision-tree"
    echo "  • Survival Analysis: [tu-dominio]/survival"
    echo "  • VOI Analysis: [tu-dominio]/voi"
    echo ""
    echo -e "${YELLOW}📋 Próximos pasos:${NC}"
    echo "1. Verifica que la API funciona correctamente"
    echo "2. Ejecuta las migraciones de base de datos si es necesario"
    echo "3. Carga los datos de seed si es el primer deployment"
    echo ""
    echo "Ver documentación completa en: DEPLOYMENT_VERCEL.md"
else
    echo ""
    echo -e "${RED}❌ Error en el deployment${NC}"
    echo "Revisa los logs con: vercel logs"
    exit 1
fi
