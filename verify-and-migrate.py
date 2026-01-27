#!/usr/bin/env python3
"""Verify database tables exist and reset migrations if needed"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, inspect, text
from app.core.config import settings

def main():
    """Check if tables exist, reset alembic if needed"""
    try:
        print("🔍 Verificando estado de la base de datos...")

        # Create engine
        engine = create_engine(str(settings.DATABASE_URL))

        # Get inspector
        inspector = inspect(engine)

        # Check if users table exists
        tables = inspector.get_table_names()

        print(f"📊 Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"  ✓ {table}")

        users_exists = 'users' in tables
        alembic_exists = 'alembic_version' in tables

        if not users_exists and alembic_exists:
            print("\n⚠️  PROBLEMA DETECTADO:")
            print("  - Tabla alembic_version existe")
            print("  - Tabla users NO existe")
            print("  - Esto indica que la migración no se ejecutó correctamente")
            print("\n🔧 Limpiando alembic_version para forzar re-ejecución de migraciones...")

            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
                conn.commit()
                print("  ✅ Tabla alembic_version eliminada")

            print("\n✅ Base de datos lista para ejecutar migraciones desde cero")
            sys.exit(0)  # Exit code 0 = success, continue with migrations

        elif users_exists:
            print("\n✅ Tabla users existe - base de datos configurada correctamente")
            sys.exit(0)

        else:
            print("\n📝 Base de datos vacía - lista para migraciones")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
