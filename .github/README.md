# GitHub Configuration

This directory contains all GitHub-specific configuration for the tender360-data-engine project.

## 📁 Directory Structure

```
.github/
├── agents/                    # AI Copilot agent instructions
│   ├── alpha.md              # Agent ALPHA - API Scraping
│   ├── beta.md               # Agent BETA - Browser Automation
│   ├── gamma.md              # Agent GAMMA - Database
│   ├── delta.md              # Agent DELTA - Pipeline
│   ├── epsilon.md            # Agent EPSILON - DevOps
│   └── WORKFLOW_GUIDE.md     # Complete development workflow guide
│
├── workflows/                 # GitHub Actions workflows
│   ├── ci.yml                # CI pipeline (test, lint, security)
│   └── codeql.yml            # CodeQL security analysis
│
├── ISSUE_TEMPLATE/           # Issue templates
│   ├── agent-task.md         # Template for agent tasks
│   └── bug-report.md         # Template for bug reports
│
├── PULL_REQUEST_TEMPLATE.md  # PR template
├── CODEOWNERS                # Code ownership rules
├── dependabot.yml            # Dependabot configuration
├── SECURITY.md               # Security policy and guidelines
├── BRANCH_PROTECTION_GUIDE.md # Branch protection setup guide
└── REPO_SETUP_GUIDE.md       # Complete repository setup guide
```

## 🚀 Quick Start

### For First-Time Setup
Read: **[REPO_SETUP_GUIDE.md](REPO_SETUP_GUIDE.md)**

### For Daily Development
Read: **[agents/WORKFLOW_GUIDE.md](agents/WORKFLOW_GUIDE.md)**

### For Security Questions
Read: **[SECURITY.md](SECURITY.md)**

### For Branch Protection
Read: **[BRANCH_PROTECTION_GUIDE.md](BRANCH_PROTECTION_GUIDE.md)**

---

## 🤖 AI Agents

This project uses 5 specialized AI agents for development:

| Agent | Role | Files Owned |
|-------|------|-------------|
| **ALPHA** | API Scraping | `src/scrapers/api_scraper.py`, `config/constants.py` |
| **BETA** | Browser Automation | `src/scrapers/selenium_scraper.py`, `src/scrapers/hybrid_scraper.py` |
| **GAMMA** | Database | `src/database/`, `src/services/` |
| **DELTA** | Pipeline & Testing | `src/pipeline/`, `tests/` |
| **EPSILON** | DevOps | `scripts/`, `docs/04_DEPLOYMENT.md` |

**See:** [agents/](agents/) directory for detailed agent instructions.

---

## 🔄 CI/CD Workflows

### CI Pipeline (`workflows/ci.yml`)
Runs on: Push to main/develop, Pull Requests

**Jobs:**
- ✅ Test (Python 3.10, 3.11)
- ✅ Lint (Ruff)
- ✅ Type Check (mypy)
- ✅ Security Scan (Bandit, Safety, TruffleHog)
- ✅ Dependency Review

**Status:** Non-blocking (helps catch issues, doesn't block merge)

### CodeQL Analysis (`workflows/codeql.yml`)
Runs on: Push, PR, Weekly schedule (Monday 6 AM)

**Purpose:** Deep security analysis for vulnerabilities

**Status:** Non-blocking

---

## 🛡️ Security Features

### Enabled Features
- ✅ **Dependabot:** Weekly dependency updates (Mondays 6 AM)
- ✅ **Secret Scanning:** Prevents committing secrets
- ✅ **CodeQL:** Advanced security analysis
- ✅ **Dependency Review:** Checks PRs for vulnerable dependencies

### Security Policy
See: [SECURITY.md](SECURITY.md) for:
- How to report vulnerabilities
- Security best practices
- Agent-specific security guidelines

---

## 📋 Templates

### Issue Templates

1. **Agent Task** ([ISSUE_TEMPLATE/agent-task.md](ISSUE_TEMPLATE/agent-task.md))
   - Use for: Assigning work to AI agents
   - Includes: Priority, sprint, acceptance criteria

2. **Bug Report** ([ISSUE_TEMPLATE/bug-report.md](ISSUE_TEMPLATE/bug-report.md))
   - Use for: Reporting bugs
   - Includes: Reproduction steps, environment info

### PR Template ([PULL_REQUEST_TEMPLATE.md](PULL_REQUEST_TEMPLATE.md))
- Agent assignment
- Testing checklist
- Security checklist
- Documentation checklist

---

## 🔧 Configuration Files

### Dependabot ([dependabot.yml](dependabot.yml))
**What it does:**
- Checks for dependency updates weekly
- Groups related updates together
- Opens PRs automatically

**Groups:**
- `patch-updates`: All patch version updates
- `testing`: pytest, coverage, mock
- `scraping`: selenium, requests, beautifulsoup4

### Code Owners ([CODEOWNERS](CODEOWNERS))
**What it does:**
- Defines who owns which files
- Auto-requests reviews from owners
- Shows ownership in GitHub UI

---

## 📚 Documentation

### Essential Reads

1. **[REPO_SETUP_GUIDE.md](REPO_SETUP_GUIDE.md)** - Complete setup instructions
2. **[agents/WORKFLOW_GUIDE.md](agents/WORKFLOW_GUIDE.md)** - Development workflow
3. **[SECURITY.md](SECURITY.md)** - Security guidelines
4. **[BRANCH_PROTECTION_GUIDE.md](BRANCH_PROTECTION_GUIDE.md)** - Git workflow

### Agent-Specific

- [agents/alpha.md](agents/alpha.md) - API scraping specialist
- [agents/beta.md](agents/beta.md) - Browser automation expert
- [agents/gamma.md](agents/gamma.md) - Database architect
- [agents/delta.md](agents/delta.md) - Pipeline engineer
- [agents/epsilon.md](agents/epsilon.md) - DevOps engineer

---

## 🎯 Workflow Summary

### For Solo Development (Current Setup)

```bash
# 1. Create feature branch (optional)
git checkout -b copilot/agent-alpha-1-fix

# 2. Make changes and test
pytest tests/ -v

# 3. Commit and push
git add .
git commit -m "[ALPHA] Issue #1: Description"
git push origin copilot/agent-alpha-1-fix

# 4. Create PR (for history/visibility)
gh pr create --fill

# 5. Merge (no approval needed - you're the admin)
gh pr merge --squash
```

### For Team Development

Same as above, but:
- PR requires 1 approval
- CI must pass before merge
- Code owners auto-requested as reviewers

---

## 🔍 Monitoring & Maintenance

### Weekly Tasks
- [ ] Review Dependabot PRs
- [ ] Check CodeQL analysis results
- [ ] Update agent instructions if needed

### Monthly Tasks
- [ ] Review security advisories
- [ ] Update workflows if needed
- [ ] Review and update documentation

---

## 🆘 Getting Help

### Troubleshooting
See: [REPO_SETUP_GUIDE.md#troubleshooting](REPO_SETUP_GUIDE.md#troubleshooting)

### Common Issues
1. **CI not running:** Check Actions settings
2. **Can't push to main:** Check branch protection
3. **Dependabot not working:** Verify it's enabled

### Resources
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Dependabot Docs](https://docs.github.com/en/code-security/dependabot)
- [GitHub CLI Docs](https://cli.github.com/)

---

## 📊 Project Status

**Current Configuration:**
- ✅ CI/CD workflows configured
- ✅ Security scanning enabled
- ✅ Dependabot configured
- ✅ Templates created
- ✅ Agent instructions updated
- ✅ Documentation complete

**Next Steps:**
1. Enable GitHub features (Settings → Code security)
2. Configure branch protection (Settings → Branches)
3. Start using workflows!

---

**Last Updated:** October 30, 2025  
**Maintainer:** @vinaybeerelli

