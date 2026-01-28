#!/usr/bin/env python3
"""Verify all test users can login"""

import os
import sys
import psycopg2

sys.path.insert(0, '/app/backend')
from app.core.security import verify_password, get_password_hash

def main():
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            sys.exit(1)

        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Test credentials
        test_users = [
            ('spain@ecomodel.com', 'spain123', 'Admin'),
            ('user@ecomodelhub.com', 'User2026!Test#', 'User'),
            ('viewer@ecomodel.com', 'viewer123', 'Viewer')
        ]

        print("📋 Verifying all test accounts:\n")

        for email, password, label in test_users:
            cur.execute("""
                SELECT id, email, password_hash, role, is_active
                FROM users
                WHERE email = %s
            """, (email,))

            user = cur.fetchone()

            if user:
                user_id, user_email, password_hash, role, is_active = user

                # Test password
                password_valid = verify_password(password, password_hash)

                print(f"✅ {label}:")
                print(f"   Email: {user_email}")
                print(f"   Role: {role}")
                print(f"   Active: {is_active}")
                print(f"   Password Valid: {'✅ YES' if password_valid else '❌ NO'}")

                # If password invalid, update it
                if not password_valid:
                    print(f"   🔄 Updating password...")
                    new_hash = get_password_hash(password)
                    cur.execute("""
                        UPDATE users
                        SET password_hash = %s, updated_at = NOW()
                        WHERE email = %s
                    """, (new_hash, email))
                    conn.commit()
                    print(f"   ✅ Password updated!")

                print()
            else:
                print(f"❌ {label}: NOT FOUND (email: {email})\n")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
