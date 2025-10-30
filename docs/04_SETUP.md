# 🚀 Setup Guide - Tender Scraper Engine

## Prerequisites

- Python 3.10 or higher
- Git
- Chrome browser (for Selenium mode)

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/tender360-scrape-application.git
cd tender360-scrape-application
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Key Settings:**
```
DATABASE_URL=sqlite:///data/tender_scraper.db
BASE_URL=https://tender.telangana.gov.in
SCRAPER_MODE=api
HEADLESS=true
LOG_LEVEL=INFO
```

### 5. Initialize Database

```bash
# First time setup or normal initialization
python scripts/setup_db.py

# Force recreation (drops and recreates all tables)
python scripts/setup_db.py --force
```

**Note:** The database uses Alembic for migrations. See `migrations/README.md` for advanced usage.

### 6. Test the Scraper

```bash
# Test with 10 tenders
python main.py --limit 10 --verbose

# Test with visible browser
python main.py --limit 5 --mode selenium --visible
```

## AWS Deployment Setup

See [docs/05_DEPLOYMENT.md](./05_DEPLOYMENT.md) for AWS deployment instructions.

## Development Tools

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_scrapers.py

# With coverage
pytest --cov=src --cov-report=html
```

### Code Formatting

```bash
# Format code
black src/

# Check style
flake8 src/

# Sort imports
isort src/
```

### Type Checking

```bash
mypy src/
```

## Troubleshooting

### Issue: Import errors

**Solution:** Make sure virtual environment is activated
```bash
source venv/bin/activate
```

### Issue: Database errors

**Solution:** Reinitialize database using the force flag
```bash
python scripts/setup_db.py --force
```

Or use Alembic commands:
```bash
alembic downgrade base
alembic upgrade head
```

### Issue: Chrome driver errors

**Solution:** Install/update Chrome browser
```bash
# On Ubuntu
sudo apt update
sudo apt install google-chrome-stable
```

### Issue: Permission denied on data/ directory

**Solution:** Create directories manually
```bash
mkdir -p data/logs data/downloads data/backups
chmod -R 755 data/
```

## Directory Structure

```
tender360-scrape-application/
├── config/              # Configuration files
├── src/                # Source code
│   ├── scrapers/       # Scraping modules
│   ├── database/       # Database models
│   ├── services/       # Business logic
│   ├── pipeline/       # Orchestration
│   └── utils/          # Utilities
├── tests/              # Test suite
├── scripts/            # Utility scripts
├── data/               # Data storage
├── docs/               # Documentation
└── main.py            # Entry point
```

## Next Steps

1. Read [Architecture Documentation](./06_ARCHITECTURE.md)
2. Review [GitHub Issues](./02_GITHUB_ISSUES.md)
3. Check [AI Agent Team Structure](./03_AI_AGENT_TEAM.md)
4. Start contributing! See [CONTRIBUTING.md](../CONTRIBUTING.md)

## Support

- **Issues**: https://github.com/YOUR_USERNAME/tender360-scrape-application/issues
- **Documentation**: https://github.com/YOUR_USERNAME/tender360-scrape-application/docs

