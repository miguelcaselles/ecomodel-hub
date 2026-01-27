#!/bin/bash

# Script de inicio que ejecuta migraciones y luego inicia el servidor

echo "🔄 Ejecutando migraciones de base de datos..."
cd backend && alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migraciones completadas"
else
    echo "⚠️  Error en migraciones, continuando de todos modos..."
fi

echo "🚀 Iniciando servidor..."
cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
