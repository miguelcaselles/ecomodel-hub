#!/bin/bash
set -e  # Exit on error

echo "="
echo "= Railway Deployment Start"
echo "="

# Change to backend directory
cd /app/backend || { echo "Failed to cd to /app/backend"; exit 1; }

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

# Start server
echo ""
echo "🚀 Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
