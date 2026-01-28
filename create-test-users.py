#!/usr/bin/env python3
"""Create test users with different roles"""

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

        # Delete old viewer if exists
        cur.execute("DELETE FROM users WHERE email = 'viewer@ecomodelhub.com'")
        if cur.rowcount > 0:
            print(f"🗑️  Deleted old viewer: viewer@ecomodelhub.com")
        conn.commit()

        # Test users to create
        test_users = [
            {
                'email': 'user@ecomodelhub.com',
                'password': 'User2026!Test#',
                'full_name': 'Test User',
                'role': 'local_user'
            },
            {
                'email': 'viewer@ecomodel.com',
                'password': 'viewer123',
                'full_name': 'Test Viewer',
                'role': 'viewer'
            }
        ]

        for user_data in test_users:
            # Check if user already exists
            cur.execute("SELECT id, email, role FROM users WHERE email = %s", (user_data['email'],))
            existing = cur.fetchone()

            if existing:
                print(f"\n✅ User already exists: {user_data['email']}")
                print(f"   ID: {existing[0]}")
                print(f"   Role: {existing[2]}")

                # Update password with correct hash
                print("🔄 Updating password...")
                password_hash = get_password_hash(user_data['password'])
                cur.execute("""
                    UPDATE users
                    SET password_hash = %s,
                        updated_at = NOW()
                    WHERE email = %s
                """, (password_hash, user_data['email']))
                conn.commit()
                print("✅ Password updated")
            else:
                print(f"\n👤 Creating user: {user_data['email']}")
                # Generate password hash
                password_hash = get_password_hash(user_data['password'])

                # Insert user
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
                        %s,
                        %s,
                        %s,
                        %s,
                        true,
                        NULL,
                        NOW(),
                        NOW()
                    )
                """, (user_data['email'], password_hash, user_data['full_name'], user_data['role']))
                conn.commit()

                # Verify creation
                cur.execute("SELECT id, email, role FROM users WHERE email = %s", (user_data['email'],))
                new_user = cur.fetchone()

                print(f"✅ User created successfully!")
                print(f"   ID: {new_user[0]}")
                print(f"   Email: {new_user[1]}")
                print(f"   Role: {new_user[2]}")

        print(f"\n🔑 Login credentials:")
        print(f"\n  Admin:")
        print(f"   Email: spain@ecomodel.com")
        print(f"   Password: spain123")
        print(f"\n  Local User:")
        print(f"   Email: user@ecomodelhub.com")
        print(f"   Password: User2026!Test#")
        print(f"\n  Viewer:")
        print(f"   Email: viewer@ecomodel.com")
        print(f"   Password: viewer123")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
