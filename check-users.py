#!/usr/bin/env python3
"""Check all users in the database"""

import os
import sys
import psycopg2

def main():
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            sys.exit(1)

        print(f"🔌 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Get all users
        cur.execute("""
            SELECT id, email, full_name, role, is_active, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        users = cur.fetchall()

        print(f"\n👥 Found {len(users)} user(s) in database:\n")
        for user in users:
            print(f"  📧 Email: {user[1]}")
            print(f"     Name: {user[2]}")
            print(f"     Role: {user[3]}")
            print(f"     Active: {user[4]}")
            print(f"     Created: {user[5]}")
            print()

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
