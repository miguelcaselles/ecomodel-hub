#!/bin/bash

# Deployment Automático en Railway
# Este script hace el deployment lo más automático posible

echo "🚂 Deployment Automático en Railway"
echo "===================================="
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Generar SECRET_KEY
echo -e "${BLUE}🔐 Generando SECRET_KEY...${NC}"
SECRET_KEY=$(openssl rand -hex 32)
echo -e "${GREEN}✓ SECRET_KEY generado${NC}"
echo ""

# Información que el usuario necesitará
echo -e "${YELLOW}📋 Variables de Entorno (cópialas):${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "SECRET_KEY=$SECRET_KEY"
echo "ALGORITHM=HS256"
echo "ACCESS_TOKEN_EXPIRE_MINUTES=30"
echo "PYTHONPATH=backend"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Guardar en archivo temporal
cat > /tmp/railway-env-vars.txt <<EOF
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PYTHONPATH=backend
EOF

echo -e "${GREEN}✓ Variables guardadas en: /tmp/railway-env-vars.txt${NC}"
echo ""

# Abrir Railway con el repo pre-seleccionado
echo -e "${BLUE}🌐 Abriendo Railway en el navegador...${NC}"
echo ""
echo "Pasos a seguir en Railway:"
echo ""
echo "1. ✅ Click en 'Deploy from GitHub repo'"
echo ""
echo "2. ✅ Busca y selecciona: 'miguelcaselles/ecomodel-hub'"
echo ""
echo "3. ✅ Railway detectará Python automáticamente → 'Deploy Now'"
echo ""
echo "4. ✅ Añade PostgreSQL:"
echo "   • Click '+ New' → 'Database' → 'PostgreSQL'"
echo ""
echo "5. ✅ Añade Redis (opcional):"
echo "   • Click '+ New' → 'Database' → 'Redis'"
echo ""
echo "6. ✅ Configura Variables (pestaña 'Variables'):"
echo "   • Copia/pega las variables de arriba"
echo "   • O desde el archivo: /tmp/railway-env-vars.txt"
echo ""
echo "7. ⏳ Espera ~5 minutos al deployment"
echo ""
echo "8. ✅ Obtén tu URL (pestaña 'Settings' → 'Domains')"
echo ""
echo "9. ✅ Ejecuta migraciones:"
echo "   railway run bash -c 'cd backend && alembic upgrade head'"
echo ""

# Copiar variables al clipboard si está disponible
if command -v pbcopy &> /dev/null; then
    cat /tmp/railway-env-vars.txt | pbcopy
    echo -e "${GREEN}✓ Variables copiadas al clipboard!${NC}"
    echo ""
fi

# Abrir Railway
open "https://railway.app/new" 2>/dev/null || echo "Abre manualmente: https://railway.app/new"

echo ""
echo -e "${YELLOW}📝 Después del deployment, ejecuta:${NC}"
echo ""
echo "# 1. Link al proyecto"
echo "railway link"
echo ""
echo "# 2. Ejecutar migraciones"
echo "railway run bash -c 'cd backend && alembic upgrade head'"
echo ""
echo "# 3. Cargar datos demo (opcional)"
echo "railway run bash -c 'cd backend && python seed_data.py'"
echo ""
echo "# 4. Ver logs"
echo "railway logs --follow"
echo ""
echo "# 5. Abrir app"
echo "railway open"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  🚀 Railway está listo para deployment!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
