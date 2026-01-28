#!/usr/bin/env python3
"""Create admin user using raw SQL to bypass enum issues"""

import os
import sys
import psycopg2

# Import backend password hashing
sys.path.insert(0, '/app/backend')
from app.core.security import get_password_hash

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

        # Delete old admin users if they exist
        old_emails = ['miguel.caselles@ecomodelhub.com', 'admin@ecomodel.com', 'admin@ecomodelhub.com']
        for old_email in old_emails:
            cur.execute("DELETE FROM users WHERE email = %s", (old_email,))
            if cur.rowcount > 0:
                print(f"🗑️  Deleted old user: {old_email}")
        conn.commit()

        # Check if admin user already exists
        cur.execute("SELECT id, email, role FROM users WHERE email = 'spain@ecomodel.com'")
        existing = cur.fetchone()

        if existing:
            print(f"✅ Admin user already exists:")
            print(f"   ID: {existing[0]}")
            print(f"   Email: {existing[1]}")
            print(f"   Role: {existing[2]}")

            # Update password with correct hash
            print("🔄 Updating password with correct hash...")
            password_hash = get_password_hash("spain123")
            cur.execute("""
                UPDATE users
                SET password_hash = %s,
                    updated_at = NOW()
                WHERE email = 'spain@ecomodel.com'
            """, (password_hash,))
            conn.commit()
            print("✅ Password updated")
        else:
            print("👤 Creating admin user...")
            # Generate password hash using backend security module
            password_hash = get_password_hash("spain123")

            # Insert admin user
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
                    'spain@ecomodel.com',
                    %s,
                    'Spain Admin',
                    'global_admin',
                    true,
                    NULL,
                    NOW(),
                    NOW()
                )
            """, (password_hash,))
            conn.commit()

            # Verify creation
            cur.execute("SELECT id, email, role FROM users WHERE email = 'spain@ecomodel.com'")
            new_user = cur.fetchone()

            print(f"✅ Admin user created successfully!")
            print(f"   ID: {new_user[0]}")
            print(f"   Email: {new_user[1]}")
            print(f"   Role: {new_user[2]}")

        print(f"\n🔑 Login credentials:")
        print(f"   Email: spain@ecomodel.com")
        print(f"   Password: spain123")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
