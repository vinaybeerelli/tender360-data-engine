# 🎯 Tender Scraper Engine

**Automated extraction system for Telangana eTender portal data**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📋 Overview

The Tender Scraper Engine is a production-ready system designed to automatically extract tender data from the Telangana eTender portal. It supports multiple scraping methods (API and Selenium), handles document downloads, parses PDF/Excel/Word files, and stores structured data in a database.

### Key Features

✅ **Dual Scraping Methods**: API-based (fast) with Selenium fallback (reliable)  
✅ **Multi-Level Extraction**: List → Details → Documents → Parsed Fields  
✅ **Document Processing**: Downloads and parses PDF, Excel, Word documents  
✅ **Robust Error Handling**: Retry logic, graceful degradation  
✅ **Production Ready**: Deployed on AWS Mumbai with automated scheduling  
✅ **AI Agent Architecture**: Designed for collaborative AI development  

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Git
- Chrome browser (for Selenium mode)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/tender360-scrape-application.git
cd tender360-scrape-application

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Initialize database
python scripts/setup_db.py

# 6. Run scraper
python main.py --limit 10
```

### Basic Usage

```bash
# Scrape 10 tenders (API mode)
python main.py --limit 10

# Use Selenium mode with visible browser
python main.py --limit 5 --mode selenium --visible

# Verbose logging
python main.py --limit 10 --verbose

# Hybrid mode (try API, fallback to Selenium)
python main.py --mode hybrid
```

---

## 🏗️ Architecture

```
User/Cron → Main Pipeline → Scraper (API/Selenium) → Database
                          ↓
                    Document Downloader
                          ↓
                    Document Parser
                          ↓
                    Extracted Fields
```

### Project Structure

```
tender360-scrape-application/
├── config/              # Configuration files
│   ├── settings.py      # Settings management
│   └── constants.py     # URLs, patterns, constants
├── src/                 # Source code
│   ├── scrapers/        # Scraping modules
│   │   ├── api_scraper.py
│   │   ├── selenium_scraper.py
│   │   └── hybrid_scraper.py
│   ├── database/        # Database layer
│   │   ├── models.py
│   │   └── operations.py
│   ├── services/        # Business logic
│   │   ├── downloader.py
│   │   ├── parser.py
│   │   └── validator.py
│   ├── pipeline/        # Orchestration
│   │   └── orchestrator.py
│   └── utils/           # Utilities
│       ├── logger.py
│       ├── helpers.py
│       └── exceptions.py
├── tests/               # Test suite
│   ├── unit/
│   └── integration/
├── scripts/             # Utility scripts
├── data/                # Data storage (gitignored)
├── docs/                # Documentation
└── main.py             # Entry point
```

---

## 🤖 AI Agent Team

This project is designed for collaborative AI development:

- **Agent ALPHA**: API Scraping (Issues #1, #5, #9)
- **Agent BETA**: Browser Automation (Issues #2, #4)
- **Agent GAMMA**: Database & Services (Issues #3, #6, #7)
- **Agent DELTA**: Pipeline & Testing (Issues #8, #13, #14)
- **Agent EPSILON**: DevOps (Issues #10, #11, #12)

See [AI Agent Team Structure](docs/03_AI_AGENT_TEAM.md) for details.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Project Manager Guide](docs/00_PROJECT_MANAGER_GUIDE.md) | PM roles and responsibilities |
| [Project Breakdown](docs/01_PROJECT_BREAKDOWN.md) | Milestones, issues, sprints |
| [GitHub Issues](docs/02_GITHUB_ISSUES.md) | All 15 issue templates |
| [AI Agent Team](docs/03_AI_AGENT_TEAM.md) | Agent roles and workflows |
| [Setup Guide](docs/04_SETUP.md) | Installation and configuration |
| [Deployment](docs/05_DEPLOYMENT.md) | AWS deployment guide |
| [Architecture](docs/06_ARCHITECTURE.md) | System design and data flow |
| [Troubleshooting](docs/07_TROUBLESHOOTING.md) | Common issues and solutions |

---

## 📊 Project Status

### Milestones

- ⏳ **Milestone 1**: Foundation (Week 1-2)
- ⏳ **Milestone 2**: Detail Extraction (Week 3-4)
- ⏳ **Milestone 3**: Document Processing (Week 5-6)
- ⏳ **Milestone 4**: Automation (Week 7-8)
- ⏳ **Milestone 5**: Production Ready (Week 9-10)

### Sprint Progress

**Current Sprint**: Sprint 1  
**Issues**: 15 total (3 in progress, 12 pending)  
**Completion**: 0%

See [GitHub Issues](https://github.com/YOUR_USERNAME/tender360-scrape-application/issues) for details.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_scrapers.py

# Run integration tests only
pytest -m integration
```

---

## 🚀 Deployment

### AWS Mumbai (ap-south-1)

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_INSTANCE_IP

# Deploy
cd /opt/tender-scraper
git pull
source venv/bin/activate
pip install -r requirements.txt
python main.py --limit 10 --verbose
```

See [Deployment Guide](docs/05_DEPLOYMENT.md) for complete instructions.

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=sqlite:///data/tender_scraper.db

# Scraper
BASE_URL=https://tender.telangana.gov.in
SCRAPER_MODE=api
HEADLESS=true
MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/scraper.log
```

---

## 🤝 Contributing

We welcome contributions! This project uses an AI agent collaboration model.

1. Check [GitHub Issues](../../issues) for available tasks
2. Claim an issue by commenting
3. Create a feature branch: `git checkout -b feature/issue-N-description`
4. Make your changes and add tests
5. Submit a PR using the template

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📈 Performance

- **Success Rate**: Target 90%+
- **Speed**: 100 tenders in ~10 minutes (API mode)
- **Coverage**: All tenders from Telangana portal
- **Accuracy**: 80%+ for parsed fields (EMD, dates)

---

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **Web Scraping**: requests, BeautifulSoup4, Selenium
- **Database**: SQLAlchemy, SQLite/PostgreSQL
- **Document Processing**: pdfplumber, python-docx, pandas
- **Testing**: pytest, pytest-cov
- **Deployment**: AWS EC2, CloudWatch
- **CI/CD**: GitHub Actions

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **GitHub Issues**: [Issues](../../issues)
- **Project Board**: [Projects](../../projects)

---

## 📞 Support

- **Issues**: https://github.com/YOUR_USERNAME/tender360-scrape-application/issues
- **Email**: support@yourcompany.com
- **Documentation**: [docs/](docs/)

---

## 🙏 Acknowledgments

- Telangana Government for maintaining the eTender portal
- Open source community for the amazing tools and libraries

---

## 🗺️ Roadmap

### Phase 1: Foundation (Current)
- [x] Project structure
- [ ] API scraper
- [ ] Database schema
- [ ] AWS deployment

### Phase 2: Enhancement
- [ ] Selenium fallback
- [ ] Document processing
- [ ] Automated scheduling

### Phase 3: Production
- [ ] Monitoring & alerts
- [ ] Performance optimization
- [ ] Complete documentation

### Phase 4: Future
- [ ] Real-time scraping
- [ ] ML-based parsing
- [ ] REST API
- [ ] Web dashboard

---

**Built with ❤️ by the AI Agent Team**