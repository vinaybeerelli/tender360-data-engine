"""
Unit tests for database migrations.

Tests for Alembic migration functionality and migration scripts.
"""

import pytest
from pathlib import Path


class TestMigrations:
    """Tests for database migrations."""
    
    def test_migration_exists(self):
        """Test that the initial migration file exists."""
        project_root = Path(__file__).parent.parent.parent
        migrations_dir = project_root / "migrations" / "versions"
        
        assert migrations_dir.exists(), "Migrations directory should exist"
        
        migration_files = list(migrations_dir.glob("*_initial_database_schema.py"))
        assert len(migration_files) > 0, "Initial migration file should exist"
    
    def test_alembic_config_exists(self):
        """Test that alembic.ini configuration file exists."""
        project_root = Path(__file__).parent.parent.parent
        alembic_ini = project_root / "alembic.ini"
        
        assert alembic_ini.exists(), "alembic.ini should exist"
        
        # Check that it contains database URL configuration
        content = alembic_ini.read_text()
        assert "sqlalchemy.url" in content, "alembic.ini should contain sqlalchemy.url"
    
    def test_env_py_configured(self):
        """Test that migrations/env.py is properly configured."""
        project_root = Path(__file__).parent.parent.parent
        env_py = project_root / "migrations" / "env.py"
        
        assert env_py.exists(), "migrations/env.py should exist"
        
        # Check that it imports our models
        content = env_py.read_text()
        assert "from src.database.models import" in content, "env.py should import models"
        assert "from config.settings import Settings" in content, "env.py should import Settings"
        assert "target_metadata = Base.metadata" in content, "env.py should set target_metadata"


class TestMigrationScripts:
    """Tests for migration helper scripts."""
    
    def test_migrate_script_exists(self):
        """Test that migrate_db.py script exists."""
        project_root = Path(__file__).parent.parent.parent
        script_path = project_root / "scripts" / "migrate_db.py"
        
        assert script_path.exists(), "migrate_db.py script should exist"
    
    def test_migration_readme_exists(self):
        """Test that migration documentation exists."""
        project_root = Path(__file__).parent.parent.parent
        readme_path = project_root / "migrations" / "README.md"
        
        assert readme_path.exists(), "Migration README should exist"
        
        # Check that README contains important sections
        content = readme_path.read_text()
        assert "Quick Start" in content, "README should have Quick Start section"
        assert "Creating New Migrations" in content, "README should explain how to create migrations"
        assert "upgrade" in content.lower(), "README should mention upgrade command"
        assert "downgrade" in content.lower(), "README should mention downgrade command"
