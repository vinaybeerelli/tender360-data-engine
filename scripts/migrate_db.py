#!/usr/bin/env python3
"""
Database migration script

Provides a convenient interface to run Alembic migrations.

Usage:
    python scripts/migrate_db.py upgrade       # Upgrade to latest version
    python scripts/migrate_db.py downgrade     # Downgrade one version
    python scripts/migrate_db.py current       # Show current version
    python scripts/migrate_db.py history       # Show migration history
    python scripts/migrate_db.py create "description"  # Create new migration
"""

import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import log


def run_alembic_command(command: list) -> int:
    """
    Run an Alembic command.
    
    Args:
        command: List of command arguments
        
    Returns:
        Exit code
    """
    try:
        # Check if alembic is available
        check_result = subprocess.run(
            ["alembic", "--version"],
            capture_output=True,
            cwd=Path(__file__).parent.parent
        )
        
        if check_result.returncode != 0:
            log.error("Alembic is not installed or not in PATH")
            print("Error: Alembic not found. Please install with: pip install alembic")
            return 1
        
        result = subprocess.run(
            ["alembic"] + command,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        return result.returncode
        
    except FileNotFoundError:
        log.error("Alembic command not found")
        print("Error: Alembic not found. Please install with: pip install alembic")
        return 1
    except Exception as e:
        log.error(f"Failed to run alembic command: {e}")
        return 1


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    
    action = sys.argv[1].lower()
    
    log.info("="*80)
    log.info("DATABASE MIGRATION UTILITY")
    log.info("="*80)
    
    if action == "upgrade":
        log.info("Upgrading database to latest version...")
        return run_alembic_command(["upgrade", "head"])
        
    elif action == "downgrade":
        log.info("Downgrading database by one version...")
        return run_alembic_command(["downgrade", "-1"])
        
    elif action == "current":
        log.info("Checking current migration version...")
        return run_alembic_command(["current"])
        
    elif action == "history":
        log.info("Showing migration history...")
        return run_alembic_command(["history", "--verbose"])
        
    elif action == "create":
        if len(sys.argv) < 3:
            log.error("Please provide a description for the migration")
            print("Usage: python scripts/migrate_db.py create \"description\"")
            return 1
        description = sys.argv[2]
        log.info(f"Creating new migration: {description}")
        return run_alembic_command(["revision", "--autogenerate", "-m", description])
        
    elif action == "stamp":
        if len(sys.argv) < 3:
            log.error("Please provide a revision to stamp")
            print("Usage: python scripts/migrate_db.py stamp <revision>")
            return 1
        revision = sys.argv[2]
        log.info(f"Stamping database to revision: {revision}")
        return run_alembic_command(["stamp", revision])
        
    else:
        log.error(f"Unknown action: {action}")
        print(__doc__)
        return 1


if __name__ == '__main__':
    sys.exit(main())
