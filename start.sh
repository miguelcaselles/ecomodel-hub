#!/bin/bash

# Script de inicio que ejecuta migraciones y luego inicia el servidor

echo "🔄 Ejecutando migraciones de base de datos..."
echo "DATABASE_URL: ${DATABASE_URL:0:30}..." # Show first 30 chars for debugging

cd /app/backend

# Export DATABASE_URL to ensure alembic can read it
export DATABASE_URL="${DATABASE_URL}"

alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migraciones completadas"

    # Run seed script if it exists
    if [ -f "/app/seed-remote.sh" ]; then
        bash /app/seed-remote.sh
        # Remove seed script after execution so it doesn't run again
        rm -f /app/seed-remote.sh
    fi
else
    echo "⚠️  Error en migraciones, continuando de todos modos..."
fi

echo "🚀 Iniciando servidor..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
