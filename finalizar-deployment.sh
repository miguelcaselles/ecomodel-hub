#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# FINALIZAR DEPLOYMENT - Añadir PostgreSQL y ejecutar migraciones
# ═══════════════════════════════════════════════════════════════

echo "🚂 Finalizando Deployment en Railway"
echo "====================================="
echo ""

cd "/Users/miguelcaselles/Desktop/PROYECTOS PROGRAMACIÓN /Innovación HSCS/Farmacoeconomia"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}IMPORTANTE: Necesitas añadir PostgreSQL manualmente${NC}"
echo ""
echo "Tu aplicación ya está desplegada y corriendo en:"
echo "  https://web-production-f4a6.up.railway.app"
echo ""
echo "Pero necesita PostgreSQL para funcionalidad completa."
echo ""
echo -e "${YELLOW}Por favor, sigue estos pasos:${NC}"
echo ""
echo "1. Abre el dashboard de Railway (se abrirá automáticamente)"
echo "2. Click en tu proyecto 'genuine-fulfillment'"
echo "3. Click el botón '+ New' o 'Add Service'"
echo "4. Selecciona 'Database' → 'PostgreSQL'"
echo "5. Espera 30 segundos a que se configure"
echo ""
echo -e "${BLUE}Una vez añadido PostgreSQL, este script continuará automáticamente...${NC}"
echo ""

# Abrir dashboard
railway dashboard &

# Esperar a que PostgreSQL esté disponible
echo -e "${YELLOW}Esperando a que añadas PostgreSQL...${NC}"
echo "(Este script verificará cada 10 segundos)"
echo ""

COUNTER=0
while true; do
    # Verificar si DATABASE_URL existe
    if railway variables 2>&1 | grep -q "DATABASE_URL"; then
        echo ""
        echo -e "${GREEN}✓ PostgreSQL detectado!${NC}"
        break
    fi

    COUNTER=$((COUNTER + 1))
    if [ $COUNTER -gt 30 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Llevamos esperando mucho tiempo...${NC}"
        echo "¿Ya añadiste PostgreSQL desde el dashboard?"
        echo ""
        read -p "Presiona Enter después de añadirlo, o Ctrl+C para cancelar: "
        COUNTER=0
    fi

    sleep 10
    echo -n "."
done

# PostgreSQL está disponible, continuar con migraciones
echo ""
echo ""
echo -e "${BLUE}Paso 1/3: Ejecutando migraciones de base de datos...${NC}"
echo ""

railway run bash -c "cd backend && alembic upgrade head"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Migraciones completadas${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Error en migraciones${NC}"
    echo "Ejecuta manualmente:"
    echo "  railway run bash -c 'cd backend && alembic upgrade head'"
    exit 1
fi

# Cargar datos demo
echo ""
echo -e "${BLUE}Paso 2/3: ¿Cargar datos de demostración?${NC}"
read -p "(s/n): " LOAD_DEMO

if [ "$LOAD_DEMO" = "s" ] || [ "$LOAD_DEMO" = "S" ]; then
    echo ""
    echo -e "${BLUE}Cargando datos demo...${NC}"
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

# Abrir aplicación
echo ""
echo -e "${BLUE}Paso 3/3: Abriendo aplicación...${NC}"
railway open

echo ""
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ ¡DEPLOYMENT COMPLETADO!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Mostrar información
echo -e "${BLUE}🌐 Tu Aplicación:${NC}"
echo ""
echo "  URL base:     https://web-production-f4a6.up.railway.app"
echo "  API Docs:     https://web-production-f4a6.up.railway.app/api/v1/docs"
echo "  Login:        https://web-production-f4a6.up.railway.app/login"
echo ""
echo -e "${BLUE}📚 Módulos de análisis:${NC}"
echo "  • Budget Impact:  /budget-impact"
echo "  • Decision Tree:  /decision-tree"
echo "  • Survival:       /survival"
echo "  • VOI Analysis:   /voi"
echo ""

echo -e "${YELLOW}🔧 Comandos útiles:${NC}"
echo "  railway logs         # Ver logs"
echo "  railway status       # Ver estado"
echo "  railway open         # Abrir app"
echo "  railway dashboard    # Abrir dashboard"
echo ""
echo -e "${GREEN}¡Tu app está en producción con funcionalidad completa! 🚀${NC}"
echo ""
