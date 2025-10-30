# Database Migrations Guide

This directory contains database migration scripts managed by [Alembic](https://alembic.sqlalchemy.org/).

## Overview

Database migrations allow you to version control your database schema changes, making it easy to:
- Track schema changes over time
- Apply changes to different environments (development, staging, production)
- Roll back changes if needed
- Collaborate with team members on schema changes

## Directory Structure

```
migrations/
├── versions/               # Migration scripts
│   └── YYYYMMDD_HHMM-{revision}_description.py
├── env.py                 # Alembic environment configuration
├── script.py.mako         # Template for new migrations
└── README.md              # This file
```

## Quick Start

### Apply All Pending Migrations

```bash
# Using the helper script (recommended)
python scripts/migrate_db.py upgrade

# Or using alembic directly
alembic upgrade head
```

### Check Current Migration Version

```bash
python scripts/migrate_db.py current
# Or: alembic current
```

### View Migration History

```bash
python scripts/migrate_db.py history
# Or: alembic history --verbose
```

### Rollback One Migration

```bash
python scripts/migrate_db.py downgrade
# Or: alembic downgrade -1
```

## Creating New Migrations

When you modify database models in `src/database/models.py`, you need to create a migration:

### Auto-generate Migration (Recommended)

```bash
python scripts/migrate_db.py create "Add user_email column"
# Or: alembic revision --autogenerate -m "Add user_email column"
```

This will:
1. Compare your models with the current database schema
2. Generate a migration script with the detected changes
3. Save it in `migrations/versions/`

⚠️ **Always review auto-generated migrations** before applying them. Alembic may not detect all changes (like column renames or data migrations).

### Manual Migration

For complex changes (data migrations, column renames, etc.):

```bash
alembic revision -m "Migrate old_field to new_field"
```

Then edit the generated file to add your custom logic.

## Migration File Structure

Each migration file contains two functions:

```python
def upgrade() -> None:
    """Apply the migration changes."""
    # Your schema changes here
    pass

def downgrade() -> None:
    """Revert the migration changes."""
    # Reverse operations here
    pass
```

### Example Migration

```python
def upgrade() -> None:
    op.add_column('tenders', sa.Column('status', sa.String(50)))
    op.create_index('ix_tenders_status', 'tenders', ['status'])

def downgrade() -> None:
    op.drop_index('ix_tenders_status', 'tenders')
    op.drop_column('tenders', 'status')
```

## Common Operations

### Add a Column

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('table_name', sa.Column('column_name', sa.String(100)))

def downgrade():
    op.drop_column('table_name', 'column_name')
```

### Create an Index

```python
def upgrade():
    op.create_index('ix_table_column', 'table_name', ['column_name'])

def downgrade():
    op.drop_index('ix_table_column', 'table_name')
```

### Rename a Column

```python
def upgrade():
    op.alter_column('table_name', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('table_name', 'new_name', new_column_name='old_name')
```

### Data Migration

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Get connection
    connection = op.get_bind()
    
    # Update data
    connection.execute(
        sa.text("UPDATE tenders SET status = 'ACTIVE' WHERE status IS NULL")
    )

def downgrade():
    pass  # Usually no need to reverse data migrations
```

## Best Practices

### 1. Always Review Auto-generated Migrations

```bash
# After creating a migration, review it
cat migrations/versions/YYYYMMDD_HHMM-{revision}_description.py
```

### 2. Test Migrations Before Production

```bash
# Test on a copy of production data
alembic upgrade head

# Verify the changes (check tables exist and have correct structure)
python -c "
from src.database.connection import init_database
from sqlalchemy import inspect
engine = init_database()
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
"

# Test rollback
alembic downgrade -1

# Re-apply
alembic upgrade head
```

### 3. Never Edit Applied Migrations

Once a migration is applied to production, **never edit it**. Instead, create a new migration to fix issues.

### 4. Keep Migrations Small and Focused

One migration should handle one logical change. This makes it easier to:
- Review changes
- Rollback if needed
- Debug issues

### 5. Add Comments for Complex Migrations

```python
def upgrade():
    # Step 1: Add new column with nullable=True to avoid errors
    op.add_column('tenders', sa.Column('status', sa.String(50), nullable=True))
    
    # Step 2: Set default values for existing rows
    op.execute("UPDATE tenders SET status = 'ACTIVE' WHERE status IS NULL")
    
    # Step 3: Make column non-nullable
    op.alter_column('tenders', 'status', nullable=False)
```

## Troubleshooting

### Migration Fails to Apply

If a migration fails:

1. Check the error message
2. Manually fix the issue in the database
3. Mark the migration as applied:
   ```bash
   alembic stamp head
   ```

### Database Out of Sync

If your database schema doesn't match migrations:

1. **Option A**: Create a migration to fix differences
   ```bash
   alembic revision --autogenerate -m "Sync database"
   ```

2. **Option B**: Reset database (development only)
   ```bash
   # Backup data if needed
   alembic downgrade base
   alembic upgrade head
   ```

### Merge Conflicts in Migration Files

If two developers create migrations simultaneously:

1. Keep both migrations
2. Order them correctly using `down_revision`
3. Or merge them into one migration

## Environment-Specific Migrations

### Development

```bash
# Use local SQLite database
DATABASE_URL=sqlite:///data/tender_scraper.db alembic upgrade head
```

### Production

```bash
# Use production PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/dbname alembic upgrade head
```

## Backup Before Migration

Always backup production databases before running migrations:

```bash
# PostgreSQL
pg_dump -h hostname -U username dbname > backup.sql

# SQLite
cp data/tender_scraper.db data/backups/tender_scraper_$(date +%Y%m%d_%H%M%S).db
```

## Integration with Deployment

Add to your deployment script:

```bash
#!/bin/bash
set -e

echo "Running database migrations..."
python scripts/migrate_db.py upgrade

echo "Verifying database..."
python scripts/verify_db.py

echo "Starting application..."
python main.py
```

## Further Reading

- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Support

For questions or issues with migrations:
1. Check the Alembic documentation
2. Review existing migrations for examples
3. Ask in the team chat
4. Create an issue in the repository
