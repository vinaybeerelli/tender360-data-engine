#!/usr/bin/env python3
"""
Database initialization script

Creates all tables in the database using Alembic migrations.

Usage:
    python scripts/setup_db.py [--force]
    
Options:
    --force    Drop existing database and recreate from scratch
"""

import sys
import argparse
from pathlib import Path
from sqlalchemy import inspect, text

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import init_database
from src.utils.logger import log
from alembic.config import Config
from alembic import command


def check_database_exists(engine):
    """Check if database tables exist."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return len(tables) > 0


def drop_all_tables(engine):
    """Drop all tables from the database."""
    log.warning("Dropping all existing tables...")
    with engine.connect() as connection:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Drop all tables
        for table in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
            log.info(f"  Dropped table: {table}")
        connection.commit()


def run_migrations():
    """Run Alembic migrations to create/update database schema."""
    log.info("Running database migrations...")
    
    # Get the alembic.ini path
    alembic_ini = Path(__file__).parent.parent / "alembic.ini"
    
    # Create Alembic config
    alembic_cfg = Config(str(alembic_ini))
    
    # Run migrations
    command.upgrade(alembic_cfg, "head")
    log.info("✓ Migrations completed successfully")


def verify_tables(engine):
    """Verify all expected tables exist."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    
    expected_tables = {
        'tenders',
        'tender_details', 
        'documents',
        'extracted_fields',
        'scrape_logs',
        'alembic_version'
    }
    
    missing_tables = expected_tables - tables
    if missing_tables:
        log.error(f"Missing tables: {missing_tables}")
        return False
    
    log.info("All expected tables exist:")
    for table in sorted(expected_tables - {'alembic_version'}):
        log.info(f"  ✓ {table}")
    
    return True


def get_migration_version(engine):
    """Get current migration version."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            return version
    except Exception:
        return None


def main():
    """Initialize database and create tables."""
    parser = argparse.ArgumentParser(description='Initialize database schema')
    parser.add_argument('--force', action='store_true', 
                       help='Drop existing database and recreate from scratch')
    args = parser.parse_args()
    
    try:
        log.info("="*80)
        log.info("DATABASE INITIALIZATION")
        log.info("="*80)
        
        # Initialize database engine
        log.info("Initializing database engine...")
        engine = init_database()
        log.info(f"Database URL: {engine.url}")
        
        # Check if database exists
        db_exists = check_database_exists(engine)
        
        if db_exists and not args.force:
            log.info("Database already exists")
            current_version = get_migration_version(engine)
            if current_version:
                log.info(f"Current migration version: {current_version}")
                log.info("Running migrations to ensure schema is up to date...")
                run_migrations()
            else:
                log.warning("No migration tracking found. Run with --force to recreate.")
        else:
            if args.force and db_exists:
                drop_all_tables(engine)
            
            log.info("Creating database schema...")
            run_migrations()
        
        # Verify tables
        log.info("Verifying database schema...")
        if not verify_tables(engine):
            log.error("Schema verification failed")
            return 1
        
        # Show final status
        current_version = get_migration_version(engine)
        
        log.info("="*80)
        log.info("✅ DATABASE INITIALIZED SUCCESSFULLY")
        log.info("="*80)
        log.info(f"Migration version: {current_version}")
        log.info("="*80)
        
        return 0
        
    except Exception as e:
        log.error(f"❌ Database initialization failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

