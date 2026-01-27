#!/bin/bash

# Script para conectar Vercel con GitHub
# Este script te ayudará a conectar tu repositorio de GitHub con Vercel

echo "🚀 Conectando EcoModel Hub con Vercel desde GitHub..."
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}✓ Repositorio en GitHub:${NC}"
echo "  https://github.com/miguelcaselles/ecomodel-hub"
echo ""

echo -e "${BLUE}📋 Pasos para conectar con Vercel:${NC}"
echo ""
echo "1. Ve a: https://vercel.com/new"
echo ""
echo "2. Selecciona 'Import Git Repository'"
echo ""
echo "3. Busca y selecciona: 'miguelcaselles/ecomodel-hub'"
echo ""
echo "4. Configura el proyecto:"
echo "   - Framework Preset: Other"
echo "   - Root Directory: ./"
echo "   - Build Command: (dejar vacío)"
echo "   - Output Directory: (dejar vacío)"
echo ""
echo "5. Añade las variables de entorno:"
echo "   - DATABASE_URL: [tu-connection-string-de-neon]"
echo "   - SECRET_KEY: [genera con: openssl rand -hex 32]"
echo "   - ALGORITHM: HS256"
echo "   - ACCESS_TOKEN_EXPIRE_MINUTES: 30"
echo "   - BACKEND_CORS_ORIGINS: [\"https://ecomodel-hub.vercel.app\"]"
echo ""
echo "6. Haz clic en 'Deploy'"
echo ""
echo -e "${YELLOW}⚡ Nota importante:${NC}"
echo "  Una vez conectado, cada push a 'main' desplegará automáticamente"
echo ""
echo -e "${BLUE}🔧 Configuración recomendada de base de datos:${NC}"
echo ""
echo "Opción 1: Neon (Recomendado)"
echo "  1. Ve a: https://neon.tech"
echo "  2. Crea una cuenta y proyecto"
echo "  3. Copia la connection string"
echo "  4. Añádela como DATABASE_URL en Vercel"
echo ""
echo "Opción 2: Supabase"
echo "  1. Ve a: https://supabase.com"
echo "  2. Crea un proyecto"
echo "  3. Ve a Settings > Database"
echo "  4. Copia la connection string (URI mode)"
echo "  5. Añádela como DATABASE_URL en Vercel"
echo ""
echo -e "${GREEN}¿Quieres abrir Vercel en el navegador ahora?${NC}"
read -p "(s/n): " OPEN_BROWSER

if [ "$OPEN_BROWSER" = "s" ] || [ "$OPEN_BROWSER" = "S" ]; then
    open "https://vercel.com/new/miguelcaselles/import?s=https%3A%2F%2Fgithub.com%2Fmiguelcaselles%2Fecomodel-hub"
    echo ""
    echo -e "${GREEN}✓ Navegador abierto en Vercel${NC}"
fi

echo ""
echo -e "${BLUE}📚 Documentación:${NC}"
echo "  - DEPLOYMENT_VERCEL.md - Guía completa de deployment"
echo "  - DEPLOYMENT_STATUS.md - Estado actual y próximos pasos"
echo ""
echo "¡Buena suerte con el deployment! 🎉"
