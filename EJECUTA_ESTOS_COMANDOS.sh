#!/bin/bash

# ════════════════════════════════════════════════════════════════
# COPIA Y PEGA ESTOS COMANDOS EN TU TERMINAL
# ════════════════════════════════════════════════════════════════

# 1. Ir al directorio del proyecto
cd "/Users/miguelcaselles/Desktop/PROYECTOS PROGRAMACIÓN /Innovación HSCS/Farmacoeconomia"

# 2. Login en Railway (se abrirá tu navegador - solo toma 30 segundos)
railway login

# 3. Ejecutar el deployment completo automático
./DEPLOYMENT_COMMANDS.sh

# ════════════════════════════════════════════════════════════════
# ESO ES TODO - El script hará automáticamente:
# ✅ Link al proyecto
# ✅ Generar SECRET_KEY
# ✅ Configurar todas las variables de entorno
# ✅ Configurar CORS automáticamente
# ✅ Ejecutar migraciones de base de datos
# ✅ Cargar datos demo
# ✅ Abrir tu app en el navegador
#
# Tiempo total: ~3 minutos
# ════════════════════════════════════════════════════════════════
