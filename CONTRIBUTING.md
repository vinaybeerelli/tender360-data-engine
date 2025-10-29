# Contributing to Tender Scraper Engine

Thank you for your interest in contributing to the Tender Scraper Engine!

## 🤖 AI Agent Collaboration

This project is designed for AI agent collaboration. Each agent has specific responsibilities:

- **Agent ALPHA**: API Scraping (Issues #1, #5, #9)
- **Agent BETA**: Browser Automation (Issues #2, #4)
- **Agent GAMMA**: Database & Services (Issues #3, #6, #7)
- **Agent DELTA**: Pipeline & Testing (Issues #8, #13, #14)
- **Agent EPSILON**: DevOps (Issues #10, #11, #12)

## 📋 Development Workflow

### 1. Issue Assignment

1. Check the [GitHub Issues](../../issues) page
2. Find an issue assigned to your agent
3. Comment on the issue to claim it
4. Move the issue to "In Progress" on the project board

### 2. Branch Naming

Create a feature branch:
```bash
git checkout -b feature/issue-N-short-description
```

Example:
```bash
git checkout -b feature/issue-1-api-scraper
```

### 3. Development

- Follow Python PEP 8 style guidelines
- Add docstrings to all functions
- Write unit tests for new code
- Update documentation as needed

### 4. Testing

Run tests before submitting:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_scrapers.py

# Run with coverage
pytest --cov=src
```

### 5. Pull Request

Create a PR with this format:

**Title:**
```
[AGENT-X] Issue #N: Brief description
```

**Description:**
```markdown
## Issue
Closes #N

## Changes
- Change 1
- Change 2

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Tested on AWS Mumbai

## Screenshots
[If applicable]
```

### 6. Code Review

- Wait for review from Project Manager
- Address feedback
- Ensure CI/CD passes

## 🧪 Testing Guidelines

### Unit Tests
- Test individual functions
- Mock external dependencies
- Aim for >70% coverage

### Integration Tests
- Test complete workflows
- Use real test data
- Document edge cases

## 📝 Documentation

Update these files as needed:
- `README.md` - For major features
- `docs/*.md` - For detailed documentation
- Docstrings - For all functions/classes

## 🚀 Deployment

Only Agent EPSILON should modify:
- `scripts/deploy.sh`
- AWS configurations
- Cron jobs

## ❓ Questions

- **Technical Questions**: Comment on the relevant issue
- **Blockers**: Create an issue with "BLOCKER" label
- **Architecture Decisions**: Tag Project Manager

## 📊 Code Quality

Before submitting:
```bash
# Format code
black src/

# Check style
flake8 src/

# Sort imports
isort src/
```

## 🎯 Agent-Specific Guidelines

### Agent ALPHA (API Scraping)
- Always test with real tender data
- Log all API requests
- Handle session management carefully
- Report success rates

### Agent BETA (Browser Automation)
- Use undetected-chromedriver
- Add human-like delays
- Take screenshots on errors
- Handle window switching carefully

### Agent GAMMA (Database)
- Write migrations for schema changes
- Add indexes for performance
- Test CRUD operations
- Document relationships

### Agent DELTA (Pipeline)
- Test error handling thoroughly
- Log all pipeline steps
- Generate summary reports
- Ensure transaction safety

### Agent EPSILON (DevOps)
- Test on AWS Mumbai
- Document deployment steps
- Setup monitoring
- Configure alerts

## 📞 Communication

- **Daily Updates**: Comment on your assigned issues
- **Blockers**: Create "BLOCKER" issue immediately
- **Questions**: Use issue comments
- **Coordination**: Tag other agents if needed

Thank you for contributing! 🚀

