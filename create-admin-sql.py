#!/usr/bin/env python3
"""Create admin user using raw SQL to bypass enum issues"""

import os
import sys
import psycopg2

def main():
    try:
        # Get DATABASE_URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            sys.exit(1)

        print(f"🔌 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Check if admin user already exists
        cur.execute("SELECT id, email, role FROM users WHERE email = 'admin@ecomodel.com'")
        existing = cur.fetchone()

        if existing:
            print(f"✅ Admin user already exists:")
            print(f"   ID: {existing[0]}")
            print(f"   Email: {existing[1]}")
            print(f"   Role: {existing[2]}")
        else:
            print("👤 Creating admin user...")
            # Insert admin user with bcrypt hash for 'admin123'
            cur.execute("""
                INSERT INTO users (
                    id,
                    email,
                    password_hash,
                    full_name,
                    role,
                    is_active,
                    organization_id,
                    created_at,
                    updated_at
                ) VALUES (
                    gen_random_uuid(),
                    'admin@ecomodel.com',
                    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqj98kN/x2',
                    'Administrator',
                    'global_admin',
                    true,
                    NULL,
                    NOW(),
                    NOW()
                )
            """)
            conn.commit()

            # Verify creation
            cur.execute("SELECT id, email, role FROM users WHERE email = 'admin@ecomodel.com'")
            new_user = cur.fetchone()

            print(f"✅ Admin user created successfully!")
            print(f"   ID: {new_user[0]}")
            print(f"   Email: {new_user[1]}")
            print(f"   Role: {new_user[2]}")
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
