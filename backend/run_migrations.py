#!/usr/bin/env python3
"""
Migration runner that handles existing databases without alembic_version table.

For databases created before alembic was introduced, this script will:
1. Check if alembic_version table exists
2. If not, stamp the database with the baseline revision
3. Then run all pending migrations
"""
import subprocess
import sys
from sqlalchemy import create_engine, text
from config import settings

def main():
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # Check if alembic_version table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'alembic_version'
            )
        """))
        alembic_exists = result.scalar()

        # Check if users table exists (to determine if this is an existing database)
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'users'
            )
        """))
        users_exists = result.scalar()

    if not alembic_exists and users_exists:
        # Existing database without alembic - stamp with baseline
        print("Existing database detected without alembic_version table.")
        print("Stamping database with baseline revision...")
        subprocess.run(["alembic", "stamp", "000_baseline"], check=True)
        print("Database stamped with baseline.")

    # Run migrations
    print("Running migrations...")
    result = subprocess.run(["alembic", "upgrade", "head"])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
