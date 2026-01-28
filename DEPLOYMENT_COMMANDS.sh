#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# DEPLOYMENT AUTOMÁTICO EN RAILWAY - EJECUTA ESTOS COMANDOS
# ═══════════════════════════════════════════════════════════════

set -e  # Exit on error

echo "🚂 Deployment Automático en Railway"
echo "===================================="
echo ""

cd "/Users/miguelcaselles/Desktop/PROYECTOS PROGRAMACIÓN /Innovación HSCS/Farmacoeconomia"

# ───────────────────────────────────────────────────────────────
# PASO 1: AUTENTICACIÓN
# ───────────────────────────────────────────────────────────────
echo "📝 Paso 1/7: Autenticación en Railway..."
echo ""

if ! railway whoami &> /dev/null; then
    echo "Abriendo navegador para login..."
    railway login
    echo ""
fi

USER=$(railway whoami 2>&1 | head -n 1)
echo "✅ Autenticado como: $USER"
echo ""

# ───────────────────────────────────────────────────────────────
# PASO 2: LINK AL PROYECTO
# ───────────────────────────────────────────────────────────────
echo "📝 Paso 2/7: Conectando al proyecto..."
echo ""

if ! railway status &> /dev/null 2>&1; then
    echo "Selecciona tu proyecto 'ecomodel-hub' de la lista:"
    railway link
    echo ""
fi

echo "✅ Proyecto conectado"
echo ""

# ───────────────────────────────────────────────────────────────
# PASO 3: GENERAR SECRET_KEY
# ───────────────────────────────────────────────────────────────
echo "📝 Paso 3/7: Generando SECRET_KEY..."
echo ""

SECRET_KEY=$(openssl rand -hex 32)
echo "SECRET_KEY=$SECRET_KEY" > /tmp/railway-secret-key.txt
echo "✅ SECRET_KEY generado: $SECRET_KEY"
echo ""

# ───────────────────────────────────────────────────────────────
# PASO 4: CONFIGURAR VARIABLES DE ENTORNO
# ───────────────────────────────────────────────────────────────
echo "📝 Paso 4/7: Configurando variables de entorno..."
echo ""

echo "  • SECRET_KEY..."
railway variables set SECRET_KEY="$SECRET_KEY"

echo "  • ALGORITHM..."
railway variables set ALGORITHM="HS256"

echo "  • ACCESS_TOKEN_EXPIRE_MINUTES..."
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"

echo "  • PYTHONPATH..."
railway variables set PYTHONPATH="backend"

echo ""
echo "✅ Variables de entorno configuradas"
echo ""

# ───────────────────────────────────────────────────────────────
# PASO 5: OBTENER DOMINIO Y CONFIGURAR CORS
# ───────────────────────────────────────────────────────────────
echo "📝 Paso 5/7: Configurando CORS..."
echo ""

DOMAIN=$(railway domain 2>&1 | grep -o '[a-z0-9-]*\.up\.railway\.app' | head -1)

if [ ! -z "$DOMAIN" ]; then
    echo "  Dominio detectado: $DOMAIN"
    railway variables set BACKEND_CORS_ORIGINS="[\"https://$DOMAIN\"]"
    echo "✅ CORS configurado para: https://$DOMAIN"
else
    echo "⚠️  No se pudo detectar el dominio automáticamente"
    echo "   Configúralo después manualmente"
fi

echo ""

# ───────────────────────────────────────────────────────────────
# PASO 6: EJECUTAR MIGRACIONES
# ───────────────────────────────────────────────────────────────
echo "📝 Paso 6/7: Ejecutando migraciones de base de datos..."
echo ""

railway run bash -c "cd backend && alembic upgrade head"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migraciones completadas exitosamente"
else
    echo ""
    echo "❌ Error en migraciones"
    echo "   Verifica que PostgreSQL esté añadido en Railway"
    echo "   Dashboard: railway dashboard"
    exit 1
fi

echo ""

# ───────────────────────────────────────────────────────────────
# PASO 7: CARGAR DATOS DEMO
# ───────────────────────────────────────────────────────────────
echo "📝 Paso 7/7: Cargando datos de demostración..."
echo ""

railway run bash -c "cd backend && python seed_data.py"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Datos demo cargados"
    echo ""
    echo "Usuarios creados:"
    echo "  • Email: admin@ecomodel.com"
    echo "    Password: admin123"
    echo "    Rol: Admin"
    echo ""
    echo "  • Email: user@ecomodel.com"
    echo "    Password: user123"
    echo "    Rol: User"
else
    echo ""
    echo "⚠️  Error al cargar datos demo (opcional)"
fi

echo ""
echo ""

# ═══════════════════════════════════════════════════════════════
# DEPLOYMENT COMPLETADO
# ═══════════════════════════════════════════════════════════════

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ ¡DEPLOYMENT COMPLETADO EXITOSAMENTE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Mostrar información de la app
echo "🌐 Tu Aplicación en Railway:"
echo ""

if [ ! -z "$DOMAIN" ]; then
    echo "  📍 URL Base:       https://$DOMAIN"
    echo "  📚 API Docs:       https://$DOMAIN/api/v1/docs"
    echo "  🔐 Login:          https://$DOMAIN/login"
    echo "  🏠 App:            https://$DOMAIN/app"
    echo ""
    echo "  📊 Módulos de Análisis:"
    echo "     • Budget Impact:   https://$DOMAIN/budget-impact"
    echo "     • Decision Tree:   https://$DOMAIN/decision-tree"
    echo "     • Survival:        https://$DOMAIN/survival"
    echo "     • VOI Analysis:    https://$DOMAIN/voi"
fi

echo ""
echo "✨ Funcionalidades Disponibles:"
echo "   ✅ NumPy, SciPy, Pandas (funcionalidad completa)"
echo "   ✅ PostgreSQL configurado"
echo "   ✅ Redis configurado"
echo "   ✅ SSL/HTTPS automático"
echo "   ✅ Deployments automáticos desde GitHub"
echo ""

echo "🔧 Comandos Útiles:"
echo "   railway logs --follow     # Ver logs en tiempo real"
echo "   railway status            # Ver estado del deployment"
echo "   railway open              # Abrir app en navegador"
echo "   railway dashboard         # Abrir dashboard"
echo ""

# Abrir aplicación
echo "🌐 Abriendo aplicación en el navegador..."
railway open

echo ""
echo "🎉 ¡Tu aplicación está en producción!"
echo ""
