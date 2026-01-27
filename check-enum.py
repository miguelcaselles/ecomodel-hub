#!/usr/bin/env python3
"""Check how the userrole enum is defined in PostgreSQL"""

import os
import psycopg2

def main():
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    # Check enum definition in PostgreSQL
    cur.execute("""
        SELECT enumlabel
        FROM pg_enum
        WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'userrole')
        ORDER BY enumsortorder;
    """)

    print("📊 PostgreSQL enum 'userrole' values:")
    for row in cur.fetchall():
        print(f"   - '{row[0]}'")

    # Check admin user
    print("\n👤 Admin user in database:")
    cur.execute("SELECT id, email, role::text, is_active FROM users WHERE email = 'admin@ecomodel.com'")
    user = cur.fetchone()
    if user:
        print(f"   ID: {user[0]}")
        print(f"   Email: {user[1]}")
        print(f"   Role (as text): {user[2]}")
        print(f"   Active: {user[3]}")
    else:
        print("   No admin user found")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
