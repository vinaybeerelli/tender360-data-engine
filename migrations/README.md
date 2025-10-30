# Database Migrations

This directory contains Alembic database migrations for the Tender Scraper Engine.

## Usage

### Initialize Database
To create the database schema from scratch:
```bash
python scripts/setup_db.py
```

To force recreation of the database:
```bash
python scripts/setup_db.py --force
```

### Create a New Migration
When you modify database models in `src/database/models.py`:
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
To upgrade to the latest schema:
```bash
alembic upgrade head
```

To upgrade to a specific version:
```bash
alembic upgrade <revision_id>
```

### Rollback Migrations
To downgrade one version:
```bash
alembic downgrade -1
```

To downgrade to a specific version:
```bash
alembic downgrade <revision_id>
```

### View Migration History
```bash
alembic history
```

### View Current Version
```bash
alembic current
```

## Migration Files

- `env.py` - Alembic environment configuration
- `script.py.mako` - Template for new migrations
- `versions/` - Directory containing all migration scripts

## Notes

- Always review auto-generated migrations before applying them
- Test migrations on a development database first
- Keep migrations small and focused on specific changes
- Include both upgrade() and downgrade() functions