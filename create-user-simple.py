import os
import sys

# Set Python path
sys.path.insert(0, '/app/backend')

# Import after setting path
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from sqlalchemy import text

def create_admin():
    db = SessionLocal()
    try:
        # Create admin user using raw SQL to avoid ORM issues
        password_hash = get_password_hash("admin123")

        db.execute(text("""
            INSERT INTO users (email, password_hash, full_name, role, is_active, created_at, updated_at)
            VALUES (:email, :password_hash, :full_name, :role, :is_active, NOW(), NOW())
            ON CONFLICT (email) DO UPDATE
            SET password_hash = :password_hash,
                updated_at = NOW()
        """), {
            "email": "admin@ecomodel.com",
            "password_hash": password_hash,
            "full_name": "Administrator",
            "role": "admin",
            "is_active": True
        })

        db.commit()
        print("✅ Usuario admin creado/actualizado: admin@ecomodel.com")
        print("   Password: admin123")

        # Verify
        result = db.execute(text("SELECT email, full_name, role FROM users WHERE email = 'admin@ecomodel.com'"))
        user = result.fetchone()
        if user:
            print(f"✅ Verificado: {user[0]} - {user[1]} ({user[2]})")
        else:
            print("❌ No se pudo verificar el usuario")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
