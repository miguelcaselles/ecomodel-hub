#!/usr/bin/env python3
"""Script to check database tables in Railway"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, inspect, text
from app.core.config import settings

def check_database():
    """Check what tables exist in the database"""
    try:
        # Create engine
        engine = create_engine(str(settings.DATABASE_URL))

        # Get inspector
        inspector = inspect(engine)

        # Get all tables
        tables = inspector.get_table_names()

        print("\n📊 Tables in database:")
        print("=" * 50)
        if tables:
            for table in tables:
                print(f"  ✓ {table}")
                # Get columns for each table
                columns = inspector.get_columns(table)
                print(f"    Columns: {len(columns)}")
                for col in columns[:3]:  # Show first 3 columns
                    print(f"      - {col['name']} ({col['type']})")
                if len(columns) > 3:
                    print(f"      ... and {len(columns) - 3} more")
        else:
            print("  ❌ No tables found!")
        print("=" * 50)

        # Check alembic_version
        print("\n📋 Alembic version:")
        print("=" * 50)
        with engine.connect() as conn:
            try:
                result = conn.execute(text("SELECT * FROM alembic_version"))
                for row in result:
                    print(f"  Current version: {row[0]}")
            except Exception as e:
                print(f"  ❌ Error reading alembic_version: {e}")
        print("=" * 50)

        engine.dispose()

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
