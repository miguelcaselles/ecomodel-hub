#!/bin/bash
set -e  # Exit on error

echo "="
echo "= Railway Deployment Start"
echo "="

# Change to backend directory
cd /app/backend || { echo "Failed to cd to /app/backend"; exit 1; }

# Verify database state - if alembic_version exists but users doesn't, reset alembic
echo ""
echo "🔍 Verificando estado de la base de datos..."
TABLES_SQL="SELECT COUNT(*) FROM information_schema.tables WHERE table_name='users' AND table_schema='public';"
ALEMBIC_SQL="SELECT COUNT(*) FROM information_schema.tables WHERE table_name='alembic_version' AND table_schema='public';"

# This will be executed inside the container where psql is available
python -c "
import os
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check if tables exist
    users_exists = conn.execute(text(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='users' AND table_schema='public')\")).scalar()
    alembic_exists = conn.execute(text(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='alembic_version' AND table_schema='public')\")).scalar()

    print(f'Users table exists: {users_exists}')
    print(f'Alembic version table exists: {alembic_exists}')

    # If alembic_version exists but users doesn't, drop alembic_version
    if alembic_exists and not users_exists:
        print('⚠️  PROBLEMA: alembic_version existe pero users no')
        print('🔧 Eliminando alembic_version para forzar re-ejecución...')
        conn.execute(text('DROP TABLE alembic_version'))
        conn.commit()
        print('✅ alembic_version eliminada - migraciones se ejecutarán desde cero')
    elif users_exists:
        print('✅ Base de datos ya configurada correctamente')
    else:
        print('📝 Base de datos vacía - lista para migraciones iniciales')
"

# Run migrations
echo ""
echo "🔄 Running database migrations..."
echo "Current revision:"
alembic current || echo "No current revision (fresh database)"
echo ""
echo "Available migrations:"
alembic heads
echo ""
echo "Executing upgrade..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
    echo "New revision:"
    alembic current
else
    echo "❌ Migrations failed"
    exit 1
fi

# Create admin user using raw SQL
echo ""
echo "👤 Creating admin user..."
cd /app || { echo "Failed to cd to /app"; exit 1; }
python create-admin-sql.py || echo "⚠️  Admin user creation skipped (may already exist)"

# Create test users with different roles
echo ""
echo "👥 Creating test users..."
python create-test-users.py || echo "⚠️  Test users creation skipped (may already exist)"

# Start server
echo ""
echo "🚀 Starting server..."
cd /app/backend || { echo "Failed to cd to /app/backend"; exit 1; }
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
