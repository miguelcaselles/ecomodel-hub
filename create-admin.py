#!/usr/bin/env python3
"""Script to create admin user in Railway deployment"""

import sys
sys.path.append('/app/backend')

from app.db.session import SessionLocal
from app.crud import crud_user
from app.schemas.user import UserCreate

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = crud_user.get_by_email(db, email="admin@ecomodel.com")
        if existing:
            print(f"✅ Usuario admin ya existe: {existing.email}")
            return

        # Create admin user
        user_in = UserCreate(
            email="admin@ecomodel.com",
            password="admin123",
            full_name="Administrator",
            role="admin"
        )
        user = crud_user.create(db, obj_in=user_in)
        print(f"✅ Usuario admin creado exitosamente: {user.email}")
        print(f"   Password: admin123")

        # Create regular user
        user_in = UserCreate(
            email="user@ecomodel.com",
            password="user123",
            full_name="Regular User",
            role="user"
        )
        user = crud_user.create(db, obj_in=user_in)
        print(f"✅ Usuario regular creado: {user.email}")
        print(f"   Password: user123")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
