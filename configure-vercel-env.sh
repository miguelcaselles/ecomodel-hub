#!/bin/bash

# Script para configurar variables de entorno en Vercel
# Ejecuta este script para configurar todas las variables necesarias

echo "🔐 Configurando variables de entorno en Vercel..."
echo ""

# Generar SECRET_KEY
echo "Generando SECRET_KEY..."
SECRET_KEY=$(openssl rand -hex 32)

# DATABASE_URL
echo ""
echo "📊 DATABASE_URL"
echo "Necesitas una base de datos PostgreSQL."
echo "Opciones recomendadas:"
echo "  1. Neon (https://neon.tech) - Gratis para empezar"
echo "  2. Supabase (https://supabase.com) - Gratis para empezar"
echo ""
read -p "Pega tu DATABASE_URL (postgresql://...): " DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL es requerido"
    exit 1
fi

# CORS Origins
echo ""
echo "🌐 CORS Origins"
echo "Se configurará para aceptar requests desde tu dominio de Vercel"
CORS_ORIGINS='["https://ecomodel-hub.vercel.app","https://ecomodel-hub-git-main-miguel-caselles-projects.vercel.app","https://ecomodel-*.vercel.app"]'

echo ""
echo "📝 Configurando variables en Vercel..."
echo ""

# Configurar variables de entorno
vercel env add DATABASE_URL production <<EOF
$DATABASE_URL
EOF

vercel env add SECRET_KEY production <<EOF
$SECRET_KEY
EOF

vercel env add ALGORITHM production <<EOF
HS256
EOF

vercel env add ACCESS_TOKEN_EXPIRE_MINUTES production <<EOF
30
EOF

vercel env add BACKEND_CORS_ORIGINS production <<EOF
$CORS_ORIGINS
EOF

echo ""
echo "✅ Variables de entorno configuradas!"
echo ""
echo "🔑 IMPORTANTE: Guarda tu SECRET_KEY:"
echo "   $SECRET_KEY"
echo ""
echo "📋 Próximos pasos:"
echo "1. Ejecuta las migraciones de base de datos"
echo "2. Despliega a producción: vercel --prod"
echo "3. Carga datos de seed si es necesario"
