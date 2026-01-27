#!/bin/bash

echo "🚀 Iniciando EcoModel Hub..."

cd "$(dirname "$0")/backend"

# Activar entorno virtual
source venv/bin/activate

# Crear base de datos si no existe
if [ ! -f "ecomodel.db" ]; then
    echo "📊 Creando base de datos..."
    python3 -c "
from app.db.base import Base
from app.db.session import engine
from app.models import *

Base.metadata.create_all(bind=engine)
print('✓ Base de datos creada')
"

    echo "🌱 Cargando datos de demo..."
    python3 seed_data.py
fi

echo ""
echo "✅ Servidor iniciado en: http://localhost:8001"
echo "📚 Documentación: http://localhost:8001/api/v1/docs"
echo ""

# Iniciar servidor
uvicorn app.main:app --reload --port 8001
