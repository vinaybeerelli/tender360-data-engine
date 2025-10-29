#!/usr/bin/env python3
"""
Database initialization script

Creates all tables in the database.

Usage:
    python scripts/setup_db.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import init_database, create_tables
from src.utils.logger import log


def main():
    """Initialize database and create tables."""
    try:
        log.info("="*80)
        log.info("DATABASE INITIALIZATION")
        log.info("="*80)
        
        # Initialize database engine
        log.info("Initializing database engine...")
        engine = init_database()
        log.info(f"Database URL: {engine.url}")
        
        # Create all tables
        log.info("Creating tables...")
        create_tables()
        
        log.info("="*80)
        log.info("✅ DATABASE INITIALIZED SUCCESSFULLY")
        log.info("="*80)
        log.info("Tables created:")
        log.info("  - tenders")
        log.info("  - tender_details")
        log.info("  - documents")
        log.info("  - extracted_fields")
        log.info("  - scrape_logs")
        log.info("="*80)
        
        return 0
        
    except Exception as e:
        log.error(f"❌ Database initialization failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

