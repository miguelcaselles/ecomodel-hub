#!/bin/bash

# Script temporal para cargar datos demo en Railway
# Se ejecutará como parte del start.sh solo una vez

cd /app/backend

echo "📊 Cargando datos de demostración..."
python seed_data.py

if [ $? -eq 0 ]; then
    echo "✅ Datos demo cargados exitosamente"
    echo ""
    echo "Usuarios disponibles:"
    echo "  • admin@ecomodel.com (password: admin123)"
    echo "  • user@ecomodel.com (password: user123)"
else
    echo "⚠️  Error al cargar datos demo (puede que ya existan)"
fi
