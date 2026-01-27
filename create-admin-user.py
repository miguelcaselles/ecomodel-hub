#!/usr/bin/env python3
"""Create admin user for Railway deployment"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def create_admin():
    """Create admin user"""
    try:
        from app.db.session import SessionLocal
        from app.crud import crud_user
        from app.schemas.user import UserCreate
        from sqlalchemy import text

        db = SessionLocal()

        # Check if any users exist
        result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        print(f"📊 Usuarios existentes en la base de datos: {result}")

        # Check if admin already exists
        existing = crud_user.get_by_email(db, email="admin@ecomodel.com")
        if existing:
            print(f"✅ Usuario admin ya existe: {existing.email}")
            print(f"   Role: {existing.role}")
            print(f"   Active: {existing.is_active}")
            print(f"\n🔑 Credenciales:")
            print(f"   Email: admin@ecomodel.com")
            print(f"   Password: admin123")
            db.close()
            return

        # Create admin user
        print("\n🔨 Creando usuario admin...")
        user_in = UserCreate(
            email="admin@ecomodel.com",
            password="admin123",
            full_name="Administrator",
            role="global_admin"
        )
        user = crud_user.create(db, obj_in=user_in)
        print(f"✅ Usuario admin creado exitosamente!")
        print(f"   Email: {user.email}")
        print(f"   Full name: {user.full_name}")
        print(f"   Role: {user.role}")
        print(f"\n🔑 Credenciales de acceso:")
        print(f"   Email: admin@ecomodel.com")
        print(f"   Password: admin123")

        db.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    create_admin()
