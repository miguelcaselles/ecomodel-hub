#!/bin/bash

echo "🚀 Iniciando EcoModel Hub en modo local..."

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navegar al directorio backend
cd "$(dirname "$0")/backend"

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creando entorno virtual...${NC}"
    python3 -m venv venv
fi

# Activar entorno virtual
echo -e "${BLUE}🔧 Activando entorno virtual...${NC}"
source venv/bin/activate

# Instalar dependencias
echo -e "${BLUE}📥 Instalando dependencias...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements-local.txt

# Copiar archivo .env
if [ ! -f ".env" ]; then
    echo -e "${BLUE}⚙️  Configurando variables de entorno...${NC}"
    cp .env.local .env
fi

# Crear base de datos si no existe
if [ ! -f "ecomodel.db" ]; then
    echo -e "${BLUE}🗄️  Creando base de datos...${NC}"

    # Crear tablas
    python3 -c "
from app.db.base import Base
from app.db.session import engine
from app.models import *

Base.metadata.create_all(bind=engine)
print('✓ Tablas creadas')
"

    # Seed data
    echo -e "${BLUE}🌱 Cargando datos de demo...${NC}"
    python3 seed_data.py
fi

echo ""
echo -e "${GREEN}✅ Configuración completa!${NC}"
echo ""
echo -e "${GREEN}🌐 Abriendo aplicación en:${NC}"
echo -e "   ${BLUE}http://localhost:8001/api/v1/docs${NC}"
echo ""
echo -e "${YELLOW}Usuarios de prueba:${NC}"
echo -e "   📧 admin@ecomodel.com / admin123 (Global Admin)"
echo -e "   📧 spain@ecomodel.com / spain123 (Local User)"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener el servidor${NC}"
echo ""

# Iniciar servidor
uvicorn app.main:app --reload --port 8001
