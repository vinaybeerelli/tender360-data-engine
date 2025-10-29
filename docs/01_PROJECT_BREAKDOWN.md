# 🎯 PROJECT BREAKDOWN - Tender Scraping System

You're absolutely right. Let me structure this properly as a **standalone, production-ready project** before integrating with your main application.

---

## 📋 PROJECT OVERVIEW

**Project Name:** Tender Scraping Engine  
**Purpose:** Automated extraction of tender data from Telangana eTender portal  
**Status:** Foundation for larger tender management system  
**Deployment:** AWS Mumbai (India region)

---

## 👥 TEAM ROLES & RESPONSIBILITIES

### **Role 1: Backend Developer (Python)**
**Responsibilities:**
- Web scraping logic (API + Selenium)
- Database schema design
- ETL pipeline orchestration
- Error handling & retry logic
- API endpoint development

**Skills Required:**
- Python (requests, BeautifulSoup, Selenium)
- SQLAlchemy ORM
- FastAPI
- Error handling & logging

---

### **Role 2: DevOps Engineer**
**Responsibilities:**
- AWS infrastructure setup (EC2, RDS)
- Cron job scheduling
- Monitoring & alerting
- Log aggregation
- CI/CD pipeline

**Skills Required:**
- AWS (EC2, CloudWatch, S3)
- Linux server management
- Docker (optional)
- Shell scripting

---

### **Role 3: QA/Testing Engineer**
**Responsibilities:**
- Test scraper reliability
- Verify data accuracy
- Monitor success rates
- Document edge cases
- Create test datasets

**Skills Required:**
- Manual testing
- Python (for automated tests)
- SQL queries
- Documentation

---

## 🗂️ PROJECT STRUCTURE

```
tender-scraper/
│
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── settings.py               # Configuration management
│   └── constants.py              # URL endpoints, patterns
│
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py           # Abstract base class
│   ├── api_scraper.py            # API-based scraper (PRIMARY)
│   ├── selenium_scraper.py       # Browser-based scraper (FALLBACK)
│   └── hybrid_scraper.py         # Combines both methods
│
├── database/
│   ├── __init__.py
│   ├── connection.py             # Database connection
│   ├── models.py                 # SQLAlchemy models
│   └── operations.py             # CRUD operations
│
├── services/
│   ├── __init__.py
│   ├── downloader.py             # Document downloader
│   ├── parser.py                 # Document parser (PDF/Excel/Word)
│   └── validator.py              # Data validation
│
├── pipeline/
│   ├── __init__.py
│   ├── orchestrator.py           # Main pipeline controller
│   ├── tasks.py                  # Individual pipeline tasks
│   └── scheduler.py              # Cron job management
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                 # Logging configuration
│   ├── helpers.py                # Utility functions
│   └── exceptions.py             # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── test_scrapers.py
│   ├── test_database.py
│   ├── test_pipeline.py
│   └── fixtures/                 # Test data
│
├── scripts/
│   ├── setup_db.py               # Initialize database
│   ├── run_once.py               # One-time scrape
│   ├── run_daily.sh              # Cron script
│   └── health_check.py           # System health monitoring
│
├── data/
│   ├── logs/                     # Application logs
│   ├── downloads/                # Downloaded documents
│   └── backups/                  # Database backups
│
├── docs/
│   ├── SETUP.md                  # Installation guide
│   ├── API.md                    # API documentation
│   ├── TROUBLESHOOTING.md        # Common issues
│   └── ARCHITECTURE.md           # System design
│
└── main.py                       # Entry point
```

---

## 📅 PROJECT MILESTONES

### **MILESTONE 1: Foundation (Week 1-2)**
**Goal:** Basic scraping works reliably on AWS Mumbai

**Deliverables:**
- ✅ Database schema designed and tested
- ✅ API scraper working (gets tender list)
- ✅ Session management fixed
- ✅ Error handling implemented
- ✅ Basic logging setup

**Success Criteria:**
- Can scrape 100 tenders with 90%+ success rate
- Data saves correctly to database
- Runs on AWS Mumbai without errors

---

### **MILESTONE 2: Detail Extraction (Week 3-4)**
**Goal:** Extract complete tender information

**Deliverables:**
- ✅ Tender detail page scraping
- ✅ Document URL extraction
- ✅ Multi-level navigation working
- ✅ Data validation rules
- ✅ Retry logic for failures

**Success Criteria:**
- Extracts all fields from detail pages
- Handles pagination correctly
- Validates data quality
- Recovers from errors gracefully

---

### **MILESTONE 3: Document Processing (Week 5-6)**
**Goal:** Download and parse tender documents

**Deliverables:**
- ✅ Document downloader (PDF/Excel/Word)
- ✅ Parser for extracting EMD, eligibility, etc.
- ✅ File storage organization
- ✅ Parser accuracy > 80%
- ✅ Handle corrupt/missing files

**Success Criteria:**
- Downloads all document types
- Extracts key fields (EMD, deadlines, amounts)
- Stores parsed data in database
- Handles missing/corrupt files

---

### **MILESTONE 4: Automation (Week 7-8)**
**Goal:** Fully automated daily scraping

**Deliverables:**
- ✅ Cron job setup
- ✅ Scheduling logic (daily at 9 AM IST)
- ✅ Monitoring & alerts
- ✅ Health check endpoint
- ✅ Failure notifications

**Success Criteria:**
- Runs daily without manual intervention
- Sends email/Slack alerts on failures
- Logs all activities
- Self-recovers from transient errors

---

### **MILESTONE 5: Production Ready (Week 9-10)**
**Goal:** Robust, maintainable, documented system

**Deliverables:**
- ✅ Comprehensive documentation
- ✅ Unit tests (>70% coverage)
- ✅ Integration tests
- ✅ Performance optimizations
- ✅ Security review

**Success Criteria:**
- All tests passing
- Documentation complete
- Code reviewed
- Ready for handoff to main project

---

## 🎫 GITHUB ISSUES BREAKDOWN

### **Epic 1: Core Scraping Infrastructure**

#### Issue #1: Fix API Scraper Session Management
**Priority:** P0 (Critical)  
**Assignee:** Backend Developer  
**Story Points:** 5

**Description:**
Current API scraper fails because it doesn't establish session properly.

**Tasks:**
- [ ] Visit main page to get session cookie
- [ ] Add complete headers from DevTools screenshot
- [ ] Include `X-Requested-With: XMLHttpRequest`
- [ ] Test with 100 tenders
- [ ] Verify 90%+ success rate

**Acceptance Criteria:**
- Session cookie is obtained before API call
- API returns non-empty tender list
- No 403 errors on AWS Mumbai
- Logs show successful requests

**Files Changed:**
- `scrapers/api_scraper.py`

---

#### Issue #2: Implement Selenium Fallback Scraper
**Priority:** P1 (High)  
**Assignee:** Backend Developer  
**Story Points:** 8

**Description:**
Create browser-based scraper as fallback when API fails.

**Tasks:**
- [ ] Setup undetected-chromedriver
- [ ] Wait for AJAX to load data (not just table)
- [ ] Extract tender rows from DataTable
- [ ] Handle window switching for details
- [ ] Add human-like delays

**Acceptance Criteria:**
- Opens browser and loads tender page
- Waits for table to populate with data
- Extracts all tender fields correctly
- Can open detail pages
- Success rate > 95%

**Files Changed:**
- `scrapers/selenium_scraper.py`

---

#### Issue #3: Database Schema & Models
**Priority:** P0 (Critical)  
**Assignee:** Backend Developer  
**Story Points:** 5

**Description:**
Design and implement database schema for tenders.

**Tasks:**
- [ ] Create `tenders` table schema
- [ ] Create `tender_details` table
- [ ] Create `documents` table
- [ ] Create `extracted_fields` table
- [ ] Create `scrape_logs` table
- [ ] Write migration script
- [ ] Add indexes for performance

**Acceptance Criteria:**
- All tables created successfully
- Foreign key relationships defined
- Can insert and query data
- Indexes on tender_id and dates

**Files Changed:**
- `database/models.py`
- `scripts/setup_db.py`

---

### **Epic 2: Multi-Level Scraping**

#### Issue #4: Tender Detail Page Extraction
**Priority:** P1 (High)  
**Assignee:** Backend Developer  
**Story Points:** 8

**Description:**
Extract detailed information from individual tender pages.

**Tasks:**
- [ ] Parse onclick parameters from table
- [ ] Navigate to detail pages
- [ ] Extract eligibility section
- [ ] Extract general terms
- [ ] Extract legal terms
- [ ] Extract technical specs
- [ ] Handle missing sections gracefully

**Acceptance Criteria:**
- Extracts viewIDim parameters correctly
- Opens detail pages successfully
- Parses all major sections
- Handles pages with missing data
- Saves details to database

**Files Changed:**
- `scrapers/api_scraper.py`
- `scrapers/selenium_scraper.py`

---

#### Issue #5: Document Link Extraction
**Priority:** P1 (High)  
**Assignee:** Backend Developer  
**Story Points:** 5

**Description:**
Find and extract all document download links.

**Tasks:**
- [ ] Locate "Tender Documents" section
- [ ] Extract PDF links
- [ ] Extract Excel/Word links
- [ ] Extract Corrigendum links
- [ ] Generate clean filenames
- [ ] Store in database

**Acceptance Criteria:**
- Finds all document links on page
- Identifies file types correctly
- Creates descriptive filenames
- Stores URLs in database
- Handles missing documents

**Files Changed:**
- `scrapers/api_scraper.py`
- `services/downloader.py`

---

### **Epic 3: Document Processing**

#### Issue #6: Document Downloader
**Priority:** P2 (Medium)  
**Assignee:** Backend Developer  
**Story Points:** 5

**Description:**
Download tender documents to local storage.

**Tasks:**
- [ ] Setup download directory structure
- [ ] Implement retry logic (3 attempts)
- [ ] Add rate limiting (delay between downloads)
- [ ] Verify file integrity
- [ ] Update download status in DB
- [ ] Skip already downloaded files

**Acceptance Criteria:**
- Downloads PDFs, Excel, Word files
- Organizes by tender ID
- Retries on failure
- Updates database status
- Doesn't re-download existing files

**Files Changed:**
- `services/downloader.py`

---

#### Issue #7: Document Parser (PDF/Excel/Word)
**Priority:** P2 (Medium)  
**Assignee:** Backend Developer  
**Story Points:** 8

**Description:**
Parse documents to extract key information.

**Tasks:**
- [ ] PDF parser using pdfplumber
- [ ] Excel parser using pandas
- [ ] Word parser using python-docx
- [ ] Extract EMD amounts
- [ ] Extract eligibility criteria
- [ ] Extract deadlines
- [ ] Extract estimated costs
- [ ] Store extracted fields in DB

**Acceptance Criteria:**
- Parses all three file types
- Extracts EMD with >80% accuracy
- Extracts dates correctly
- Handles corrupt files gracefully
- Stores fields in structured format

**Files Changed:**
- `services/parser.py`

---

### **Epic 4: Pipeline Orchestration**

#### Issue #8: End-to-End Pipeline
**Priority:** P0 (Critical)  
**Assignee:** Backend Developer  
**Story Points:** 8

**Description:**
Orchestrate complete scraping workflow.

**Tasks:**
- [ ] Integrate scraper → database
- [ ] Integrate scraper → downloader
- [ ] Integrate downloader → parser
- [ ] Add transaction management
- [ ] Add rollback on failure
- [ ] Log all pipeline steps
- [ ] Generate summary report

**Acceptance Criteria:**
- Runs complete workflow for one tender
- Rolls back on errors
- Logs each step
- Generates success/failure summary
- Can process 100 tenders end-to-end

**Files Changed:**
- `pipeline/orchestrator.py`
- `main.py`

---

#### Issue #9: Error Handling & Retry Logic
**Priority:** P1 (High)  
**Assignee:** Backend Developer  
**Story Points:** 5

**Description:**
Robust error handling throughout system.

**Tasks:**
- [ ] Define custom exceptions
- [ ] Implement retry decorator
- [ ] Add exponential backoff
- [ ] Log all errors with context
- [ ] Save failed tenders for manual review
- [ ] Create error summary report

**Acceptance Criteria:**
- Retries transient failures (3x)
- Logs errors with full context
- Doesn't crash on single failure
- Continues processing remaining tenders
- Reports failures at end

**Files Changed:**
- `utils/exceptions.py`
- `utils/helpers.py`

---

### **Epic 5: Automation & Deployment**

#### Issue #10: AWS Deployment Setup
**Priority:** P0 (Critical)  
**Assignee:** DevOps Engineer  
**Story Points:** 8

**Description:**
Deploy scraper to AWS Mumbai.

**Tasks:**
- [ ] Launch EC2 instance in ap-south-1
- [ ] Install Python 3.10+
- [ ] Install Chrome browser
- [ ] Setup virtual environment
- [ ] Install dependencies
- [ ] Configure security groups
- [ ] Setup SSH access
- [ ] Test scraper runs successfully

**Acceptance Criteria:**
- EC2 running in Mumbai region
- All dependencies installed
- Scraper runs without errors
- Can SSH into server
- Chrome browser available

**Documentation:**
- `docs/SETUP.md`

---

#### Issue #11: Cron Job Scheduling
**Priority:** P1 (High)  
**Assignee:** DevOps Engineer  
**Story Points:** 3

**Description:**
Schedule daily automated scraping.

**Tasks:**
- [ ] Create cron script
- [ ] Schedule for 9 AM IST daily
- [ ] Redirect output to logs
- [ ] Test cron execution
- [ ] Add email notification on completion

**Acceptance Criteria:**
- Runs daily at 9 AM IST
- Logs all output
- Sends email summary
- Can be enabled/disabled easily

**Files Changed:**
- `scripts/run_daily.sh`
- Crontab configuration

---

#### Issue #12: Monitoring & Alerting
**Priority:** P1 (High)  
**Assignee:** DevOps Engineer  
**Story Points:** 5

**Description:**
Monitor system health and alert on failures.

**Tasks:**
- [ ] Setup CloudWatch logs
- [ ] Create health check endpoint
- [ ] Configure email alerts for failures
- [ ] Track success rate metrics
- [ ] Create dashboard (optional)
- [ ] Setup log rotation

**Acceptance Criteria:**
- Logs sent to CloudWatch
- Email sent on failure
- Health endpoint returns status
- Logs rotated weekly
- Can view metrics easily

**Files Changed:**
- `scripts/health_check.py`
- CloudWatch configuration

---

### **Epic 6: Testing & Documentation**

#### Issue #13: Unit Tests
**Priority:** P2 (Medium)  
**Assignee:** Backend Developer  
**Story Points:** 5

**Description:**
Write unit tests for core functions.

**Tasks:**
- [ ] Test API scraper functions
- [ ] Test database operations
- [ ] Test parser functions
- [ ] Mock external API calls
- [ ] Achieve >70% code coverage
- [ ] Setup pytest

**Acceptance Criteria:**
- All tests pass
- Coverage > 70%
- Tests run in < 2 minutes
- Can run with `pytest`

**Files Changed:**
- `tests/test_scrapers.py`
- `tests/test_database.py`
- `tests/test_pipeline.py`

---

#### Issue #14: Integration Tests
**Priority:** P2 (Medium)  
**Assignee:** QA Engineer  
**Story Points:** 5

**Description:**
End-to-end testing of complete workflow.

**Tasks:**
- [ ] Test scraping → database flow
- [ ] Test document download flow
- [ ] Test parser accuracy
- [ ] Test error handling
- [ ] Test with real tender data
- [ ] Document test results

**Acceptance Criteria:**
- Complete workflow tested
- Success rate measured
- Parser accuracy validated
- Error scenarios tested
- Test report documented

**Files Changed:**
- `tests/test_integration.py`
- `docs/TEST_RESULTS.md`

---

#### Issue #15: Documentation
**Priority:** P2 (Medium)  
**Assignee:** All Team Members  
**Story Points:** 5

**Description:**
Comprehensive project documentation.

**Tasks:**
- [ ] Write README with quick start
- [ ] Document installation steps
- [ ] Document configuration
- [ ] API documentation
- [ ] Troubleshooting guide
- [ ] Architecture diagrams
- [ ] Code comments

**Acceptance Criteria:**
- New developer can setup in < 30 min
- All functions documented
- Common issues covered
- Architecture clear
- Examples provided

**Files Changed:**
- `README.md`
- `docs/SETUP.md`
- `docs/TROUBLESHOOTING.md`
- `docs/ARCHITECTURE.md`

---

## 📊 SPRINT PLANNING (2-Week Sprints)

### **Sprint 1 (Week 1-2): Foundation**
**Goal:** Working scraper on AWS

**Issues:**
- #1: Fix API Scraper (P0)
- #3: Database Schema (P0)
- #10: AWS Deployment (P0)

**Outcome:** Can scrape tender list and save to database

---

### **Sprint 2 (Week 3-4): Detail Extraction**
**Goal:** Extract complete tender details

**Issues:**
- #2: Selenium Fallback (P1)
- #4: Detail Page Extraction (P1)
- #5: Document Links (P1)

**Outcome:** Complete tender information in database

---

### **Sprint 3 (Week 5-6): Document Processing**
**Goal:** Download and parse documents

**Issues:**
- #6: Document Downloader (P2)
- #7: Document Parser (P2)
- #8: Pipeline Integration (P0)

**Outcome:** Documents downloaded and parsed

---

### **Sprint 4 (Week 7-8): Automation**
**Goal:** Fully automated system

**Issues:**
- #9: Error Handling (P1)
- #11: Cron Scheduling (P1)
- #12: Monitoring (P1)

**Outcome:** Runs automatically every day

---

### **Sprint 5 (Week 9-10): Production Ready**
**Goal:** Polish and documentation

**Issues:**
- #13: Unit Tests (P2)
- #14: Integration Tests (P2)
- #15: Documentation (P2)

**Outcome:** Production-ready, documented system

---

## ✅ DEFINITION OF DONE

Each issue is "Done" when:

1. ✅ Code written and tested locally
2. ✅ Code reviewed by peer
3. ✅ Unit tests written (if applicable)
4. ✅ Tested on AWS Mumbai
5. ✅ Documentation updated
6. ✅ Merged to main branch
7. ✅ Acceptance criteria met

---

## 🚀 NEXT STEPS

**What I need from you:**

1. **Share your current Git repo structure**
   - Show me your existing folders and files
   - I'll map them to this structure

2. **Confirm team setup**
   - Who's doing what role?
   - Solo developer or team?

3. **Confirm priorities**
   - Do you agree with milestone order?
   - Any changes needed?

4. **Deployment details**
   - Already have AWS Mumbai instance?
   - Need help with setup?

**Then I'll:**
- Map your existing code to this structure
- Create detailed implementation plan for Issue #1
- Provide deployment guide for AWS Mumbai
- Create project board with all issues

**Ready to share your repo structure?**