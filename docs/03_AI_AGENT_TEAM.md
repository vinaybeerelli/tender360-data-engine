Perfect! Let me create a **complete, production-ready project structure** from scratch with AI agent team specifications.

---

# 🚀 NEW PROJECT: tender-scraper-engine

## 📁 COMPLETE PROJECT STRUCTURE --- complete_project_structure.py

## 🤖 AI AGENT TEAM STRUCTURE

### **Team Composition: 5 Specialized AI Agents**

```
PROJECT MANAGER (You/Me)
    ↓
    ├── Agent ALPHA (Scraping Specialist)
    ├── Agent BETA (Browser Automation Expert)
    ├── Agent GAMMA (Database Architect)
    ├── Agent DELTA (Pipeline Engineer)
    └── Agent EPSILON (DevOps Engineer)
```

---

### **🤖 AGENT ALPHA - API Scraping Specialist**

**Role:** Core scraping logic  
**Primary Responsibility:** API-based data extraction  
**Skills:** HTTP, JSON, Session management, Headers

**Assigned Issues:**
- Issue #1: Fix API Scraper Session Management (P0)
- Issue #5: Document Link Extraction (P1)
- Issue #9: Error Handling & Retry Logic (P1)

**Files Owned:**
- `src/scrapers/api_scraper.py`
- `src/scrapers/base_scraper.py`
- `config/constants.py`

**Communication Protocol:**
```
Input: Requirements document + DevTools screenshots
Output: Working API scraper with >90% success rate
Updates: Daily progress reports
Blockers: Report immediately to Project Manager
```

**Agent Prompt Template:**
```
You are Agent ALPHA, API Scraping Specialist.

Your mission: Create a reliable API scraper for Telangana eTender portal.

Context:
- Site uses AJAX/DataTables for data loading
- Requires session establishment
- Needs complete AJAX headers
- Running on AWS Mumbai

Your tasks:
1. Establish session properly (visit main page first)
2. Use complete headers from DevTools
3. Parse JSON response correctly
4. Extract onclick parameters
5. Handle errors gracefully

Success criteria:
- 90%+ success rate
- No 403 errors
- Clean, documented code
- Comprehensive error messages

Current issue: [Provide specific issue details]

Deliver: Python code + test results
```

---

### **🤖 AGENT BETA - Browser Automation Expert**

**Role:** Selenium-based scraping  
**Primary Responsibility:** Fallback scraper when API fails  
**Skills:** Selenium, undetected-chromedriver, JavaScript handling

**Assigned Issues:**
- Issue #2: Implement Selenium Fallback Scraper (P1)
- Issue #4: Tender Detail Page Extraction (P1)
- Issue #8: End-to-End Pipeline (P0)

**Files Owned:**
- `src/scrapers/selenium_scraper.py`
- `src/scrapers/hybrid_scraper.py`

**Agent Prompt Template:**
```
You are Agent BETA, Browser Automation Expert.

Your mission: Create robust Selenium scraper as fallback.

Critical requirements:
1. Wait for AJAX data to load (not just table element)
2. Use undetected-chromedriver
3. Handle window switching for details
4. Add human-like delays
5. Extract all tender fields

The challenge: DataTable loads via JavaScript
Solution: Wait for actual data rows, not empty table

Current task: [Provide specific task]

Deliver: Selenium scraper with 95%+ reliability
```

---

### **🤖 AGENT GAMMA - Database Architect**

**Role:** Data persistence  
**Primary Responsibility:** Database design and operations  
**Skills:** SQLAlchemy, Database design, Data modeling

**Assigned Issues:**
- Issue #3: Database Schema & Models (P0)
- Issue #6: Document Downloader (P2)
- Issue #7: Document Parser (P2)

**Files Owned:**
- `src/database/models.py`
- `src/database/operations.py`
- `src/database/connection.py`
- `src/services/downloader.py`
- `src/services/parser.py`

**Agent Prompt Template:**
```
You are Agent GAMMA, Database Architect.

Your mission: Design optimal database schema for tender data.

Requirements:
- Store tenders (basic info)
- Store tender_details (extended info)
- Store documents (file metadata)
- Store extracted_fields (parsed data)
- Store scrape_logs (audit trail)

Relationships:
- One tender → Many documents
- One tender → Many extracted fields
- One document → Many extracted fields

Indexes needed:
- tender_id (unique)
- published_date
- bid_close_date

Current task: [Provide specifics]

Deliver: SQLAlchemy models + migration script
```

---

### **🤖 AGENT DELTA - Pipeline Engineer**

**Role:** Workflow orchestration  
**Primary Responsibility:** Integrate all components  
**Skills:** Python, Testing, Integration

**Assigned Issues:**
- Issue #8: End-to-End Pipeline (shared with Beta)
- Issue #13: Unit Tests (P2)
- Issue #14: Integration Tests (P2)

**Files Owned:**
- `src/pipeline/orchestrator.py`
- `src/pipeline/tasks.py`
- `tests/unit/*.py`
- `tests/integration/*.py`

**Agent Prompt Template:**
```
You are Agent DELTA, Pipeline Engineer.

Your mission: Orchestrate complete tender extraction workflow.

Pipeline stages:
1. Scrape tender list
2. For each tender:
   a. Get details
   b. Extract document URLs
   c. Download documents
   d. Parse documents
   e. Save to database
3. Log results

Error handling:
- Retry transient failures (3x)
- Continue on single failure
- Log all errors
- Generate summary report

Testing requirements:
- Unit tests for each function
- Integration test for full pipeline
- 70%+ code coverage

Current task: [Provide specifics]

Deliver: Working pipeline + test suite
```

---

### **🤖 AGENT EPSILON - DevOps Engineer**

**Role:** Infrastructure & deployment  
**Primary Responsibility:** AWS setup and automation  
**Skills:** AWS, Linux, Bash, Monitoring

**Assigned Issues:**
- Issue #5: AWS Deployment Setup (P0)
- Issue #11: Cron Job Scheduling (P1)
- Issue #12: Monitoring & Alerting (P1)
- Issue #15: Documentation (shared)

**Files Owned:**
- `scripts/deploy.sh`
- `scripts/run_daily.sh`
- `scripts/health_check.py`
- `docs/04_DEPLOYMENT.md`

**Agent Prompt Template:**
```
You are Agent EPSILON, DevOps Engineer.

Your mission: Deploy scraper to AWS Mumbai and automate.

Infrastructure:
- EC2 instance in ap-south-1 (Mumbai)
- t3.medium (2 vCPU, 4 GB RAM)
- Ubuntu 22.04
- 30 GB storage

Setup tasks:
1. Install Python 3.10
2. Install Chrome browser
3. Setup virtual environment
4. Install dependencies
5. Configure security groups
6. Setup cron job (9 AM IST daily)
7. Configure CloudWatch logs
8. Setup email alerts

Monitoring:
- Health check endpoint
- Success rate metrics
- Email on failure
- Log rotation

Current task: [Provide specifics]

Deliver: Deployment scripts + documentation
```

---

## 📋 AGENT COLLABORATION WORKFLOW

### **Daily Standup (Async)**

Each agent reports:
1. ✅ **Completed yesterday:** Issue #X done
2. 🔄 **Working today:** Issue #Y in progress
3. 🚧 **Blockers:** Waiting for Z from Agent W

**Format:**
```
Agent: ALPHA
Date: 2025-10-29
Completed: ✅ Issue #1 - API Scraper session management fixed
In Progress: 🔄 Issue #5 - Document link extraction (80% done)
Blockers: ⚠️ Need database schema from Agent GAMMA
Next: Continue Issue #5, start Issue #9
```

---

### **Issue Assignment Matrix**

| Sprint | Agent ALPHA | Agent BETA | Agent GAMMA | Agent DELTA | Agent EPSILON |
|--------|-------------|------------|-------------|-------------|---------------|
| **Sprint 1** | Issue #1 | - | Issue #3 | - | Issue #10 |
| **Sprint 2** | Issue #5 | Issue #2, #4 | - | Issue #8 | - |
| **Sprint 3** | Issue #9 | - | Issue #6, #7 | Issue #8 | - |
| **Sprint 4** | - | - | - | Issue #13 | Issue #11, #12 |
| **Sprint 5** | - | - | - | Issue #14 | Issue #15 |

---

### **Pull Request Protocol**

**PR Title Format:**
```
[AGENT-X] Issue #N: Brief description
```

**Example:**
```
[ALPHA] Issue #1: Fix API scraper session management
```

**PR Description Template:**
```markdown
## Issue
Closes #1

## Changes
- Added session establishment before API call
- Implemented complete AJAX headers
- Added retry logic with exponential backoff

## Testing
- ✅ Tested with 100 tenders
- ✅ Success rate: 95%
- ✅ No 403 errors on AWS Mumbai

## Screenshots
[Attach screenshots if applicable]

## Agent
Agent ALPHA

## Dependencies
None / Requires PR #X to be merged first
```

---

### **Communication Channels**

**GitHub Issues:** Primary async communication  
**PR Comments:** Code review and technical discussions  
**Project Board:** Visual progress tracking  
**README Updates:** Milestone completion announcements

---

## 🚀 STEP-BY-STEP IMPLEMENTATION PLAN

### **PHASE 1: Repository Setup (Day 1)**

**Tasks:**
1. Create new GitHub repository: `tender-scraper-engine`
2. Initialize with README
3. Create project structure (from artifact above)
4. Setup GitHub Project board
5. Create all 15 issues
6. Assign issues to agents

**Deliverable:** Empty repo with complete structure

---

### **PHASE 2: Sprint 1 Execution (Week 1-2)**

**Agent ALPHA:**
```bash
# Branch: feature/issue-1-api-scraper
# File: src/scrapers/api_scraper.py

Task: Implement session-aware API scraper
Success: Can scrape 100 tenders with 90%+ success
```

**Agent GAMMA:**
```bash
# Branch: feature/issue-3-database-schema
# File: src/database/models.py

Task: Create SQLAlchemy models
Success: Database created, can insert/query tenders
```

**Agent EPSILON:**
```bash
# Branch: feature/issue-10-aws-deployment
# Files: scripts/deploy.sh, docs/04_DEPLOYMENT.md

Task: Deploy to AWS Mumbai
Success: Scraper runs on EC2 without errors
```

---

### **PHASE 3: Integration (End of Sprint 1)**

**Agent DELTA** creates `feature/sprint1-integration` branch:
- Merges ALPHA's scraper
- Merges GAMMA's database
- Tests end-to-end on AWS (coordinated with EPSILON)
- Creates integration PR

---

## 📊 PROJECT BOARD STRUCTURE

```
GitHub Project: Tender Scraper Engine

Columns:
├── 📋 Backlog (All unassigned issues)
├── 📝 To Do (Sprint issues)
├── 🔄 In Progress (Actively being worked)
├── 👀 In Review (PR submitted)
├── ✅ Done (Merged and deployed)
└── 🚫 Blocked (Waiting on dependencies)
```

---

## 🎯 YOUR ROLE AS PROJECT MANAGER

### **Daily Tasks:**
1. Check agent status updates
2. Review PRs and approve merges
3. Unblock agents (answer questions)
4. Update project board
5. Ensure agents stay coordinated

### **Weekly Tasks:**
1. Sprint planning (assign next sprint's issues)
2. Demo to stakeholders
3. Retrospective (what went well/poorly)
4. Update documentation

### **Tools You'll Use:**
- GitHub Issues (track work)
- GitHub Projects (visualize progress)
- Pull Requests (code review)
- AWS Console (monitor production)

---

## 📦 NEXT IMMEDIATE STEPS

### **Step 1: Create Repository** ✅
```bash
# On your local machine
git init tender-scraper-engine
cd tender-scraper-engine

# Copy the project structure from artifact
# Create all files and folders

git add .
git commit -m "Initial project structure"
git remote add origin https://github.com/YOUR_USERNAME/tender-scraper-engine.git
git push -u origin main
```

### **Step 2: Create GitHub Issues** ✅

I'll provide you the **exact issue templates** for all 15 issues. Would you like me to:

**A)** Generate all 15 GitHub issue templates in markdown format (you copy-paste into GitHub)

**B)** Create a script that auto-creates all issues via GitHub API

**C)** Provide a CSV you can import into GitHub

### **Step 3: AWS Deployment Guide** ✅

Share your AWS deployment file, and I'll:
- Review current setup
- Provide exact deployment script
- Create `scripts/deploy.sh` tailored to your instance

---

## ❓ IMMEDIATE QUESTIONS FOR YOU

1. **GitHub username?** (So I can format repo URLs correctly)
2. **Prefer which issue creation method?** (A, B, or C above)
3. **Share AWS deployment file now?** (So I can create deployment script)
4. **Want me to be one of the AI agents?** (Which role? I suggest Project Manager + Agent ALPHA to start)

**Let me know and I'll generate everything you need to start immediately! 🚀**