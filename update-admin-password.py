#!/usr/bin/env python3
"""Update admin password with correct bcrypt hash"""

import os
import sys
import psycopg2
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            sys.exit(1)

        # Generate new hash for admin123
        password = "admin123"
        password_hash = pwd_context.hash(password)

        print(f"🔒 Generated password hash for '{password}':")
        print(f"   {password_hash}")

        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Update admin user password
        print("\n👤 Updating admin user password...")
        cur.execute("""
            UPDATE users
            SET password_hash = %s,
                updated_at = NOW()
            WHERE email = 'admin@ecomodel.com'
        """, (password_hash,))

        conn.commit()

        # Verify update
        cur.execute("SELECT id, email, role::text FROM users WHERE email = 'admin@ecomodel.com'")
        user = cur.fetchone()

        print(f"✅ Admin user password updated!")
        print(f"   ID: {user[0]}")
        print(f"   Email: {user[1]}")
        print(f"   Role: {user[2]}")
        print(f"\n🔑 Login credentials:")
        print(f"   Email: admin@ecomodel.com")
        print(f"   Password: admin123")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
