# GITHUB ISSUES - COPY EACH TO CREATE IN YOUR REPO

## ============================================================================
## ISSUE #1: Fix API Scraper Session Management
## ============================================================================

**Title:** [ALPHA] Fix API Scraper Session Management

**Labels:** `P0-critical`, `epic-1-core-scraping`, `agent-alpha`, `sprint-1`

**Assignees:** @vinaybeerelli

**Milestone:** Milestone 1: Foundation

**Description:**

### 🎯 Problem
Current API scraper fails because it doesn't establish session properly before making API calls to `TenderDetailsHomeJson.html`.

**Error:** API returns empty data or 403 Forbidden

**Root Cause:** 
- No session cookie obtained
- Missing critical AJAX headers
- Direct API call without visiting main page first

### 📋 Tasks
- [ ] Visit main page (`/TenderDetailsHome.html`) to get session cookie
- [ ] Add complete headers from DevTools screenshot
- [ ] Include `X-Requested-With: XMLHttpRequest` header
- [ ] Implement proper parameter format (all 30+ params)
- [ ] Test with 100 tenders on AWS Mumbai
- [ ] Verify 90%+ success rate
- [ ] Add error logging and retry logic

### ✅ Acceptance Criteria
- Session cookie is obtained before API call
- API returns non-empty tender list (`aaData` not empty)
- No 403 errors when running on AWS Mumbai
- Logs show successful session establishment
- Can extract tender ID, work name, dates from response
- Success rate >= 90% over 100 tenders

### 📁 Files Changed
- `src/scrapers/api_scraper.py`
- `config/constants.py`

### 🔗 Related Issues
- Blocks #4 (Tender Detail Page Extraction)
- Blocks #5 (Document Link Extraction)

### 📸 Reference
See DevTools screenshots showing proper headers and parameters.

---

## ============================================================================
## ISSUE #2: Implement Selenium Fallback Scraper
## ============================================================================

**Title:** [BETA] Implement Selenium Fallback Scraper

**Labels:** `P1-high`, `epic-1-core-scraping`, `agent-beta`, `sprint-2`

**Assignees:** (Assign to Agent BETA)

**Milestone:** Milestone 2: Detail Extraction

**Description:**

### 🎯 Goal
Create browser-based scraper as fallback when API method fails or is blocked.

### 📋 Tasks
- [ ] Setup undetected-chromedriver
- [ ] Load tender listing page
- [ ] Wait for table element (`#pagetable13`)
- [ ] **CRITICAL:** Wait for AJAX data to populate (not just empty table)
- [ ] Extract tender rows from DataTable
- [ ] Parse all 10 columns correctly
- [ ] Handle window switching for detail pages
- [ ] Add human-like delays (2-5 seconds)
- [ ] Screenshot on errors for debugging

### ✅ Acceptance Criteria
- Opens browser and loads tender page successfully
- Waits for table to populate with actual data
- Extracts all tender fields correctly (dept, ID, dates, etc.)
- Can click "View Details" and switch to new window
- Success rate > 95% on AWS Mumbai
- Handles missing data gracefully
- Takes screenshot on failure

### 📁 Files Changed
- `src/scrapers/selenium_scraper.py`
- `src/scrapers/base_scraper.py`

### 🔗 Related Issues
- Depends on #1 (API Scraper as primary method)
- Related to #4 (Detail page navigation)

---

## ============================================================================
## ISSUE #3: Database Schema & Models
## ============================================================================

**Title:** [GAMMA] Database Schema & Models

**Labels:** `P0-critical`, `epic-1-core-scraping`, `agent-gamma`, `sprint-1`

**Assignees:** (Assign to Agent GAMMA)

**Milestone:** Milestone 1: Foundation

**Description:**

### 🎯 Goal
Design and implement complete database schema for tender data storage.

### 📊 Schema Design

**Table 1: `tenders`** (Basic tender info)
```sql
- id (PK, autoincrement)
- tender_id (TEXT, UNIQUE, NOT NULL)
- department (TEXT)
- notice_number (TEXT)
- category (TEXT)
- work_name (TEXT)
- tender_value (TEXT)
- published_date (TEXT)
- bid_start_date (TEXT)
- bid_close_date (TEXT)
- detail_url (TEXT)
- scraped_at (TIMESTAMP)
- last_updated (TIMESTAMP)
```

**Table 2: `tender_details`** (Extended info)
```sql
- id (PK)
- tender_id (FK → tenders.tender_id, UNIQUE)
- eligibility (TEXT)
- general_terms (TEXT)
- legal_terms (TEXT)
- technical_terms (TEXT)
- submission_procedure (TEXT)
- scraped_at (TIMESTAMP)
```

**Table 3: `documents`** (File metadata)
```sql
- id (PK)
- tender_id (FK → tenders.id)
- filename (TEXT)
- file_path (TEXT)
- file_type (TEXT)
- file_size (INTEGER)
- download_url (TEXT)
- download_status (TEXT)
- downloaded_at (TIMESTAMP)
```

**Table 4: `extracted_fields`** (Parsed data)
```sql
- id (PK)
- tender_id (FK → tenders.id)
- document_id (FK → documents.id)
- field_name (TEXT)
- field_value (TEXT)
- field_type (TEXT)
- extraction_method (TEXT)
- extracted_at (TIMESTAMP)
```

**Table 5: `scrape_logs`** (Audit trail)
```sql
- id (PK)
- run_date (TIMESTAMP)
- method (TEXT)
- tenders_found (INTEGER)
- tenders_scraped (INTEGER)
- errors (INTEGER)
- status (TEXT)
- notes (TEXT)
```

### 📋 Tasks
- [ ] Create SQLAlchemy models
- [ ] Define relationships (One-to-Many, etc.)
- [ ] Add indexes on tender_id, dates
- [ ] Create migration script
- [ ] Write database initialization script
- [ ] Add CRUD operations
- [ ] Test insert/query operations

### ✅ Acceptance Criteria
- All 5 tables created successfully
- Foreign key relationships work
- Can insert and query tenders
- Indexes improve query performance
- Migration script runs without errors
- CRUD operations tested

### 📁 Files Changed
- `src/database/models.py`
- `src/database/operations.py`
- `src/database/connection.py`
- `scripts/setup_db.py`

### 🔗 Related Issues
- Required by #1 (API Scraper needs to save data)
- Required by #8 (Pipeline integration)

---

## ============================================================================
## ISSUE #4: Tender Detail Page Extraction
## ============================================================================

**Title:** [BETA] Tender Detail Page Extraction

**Labels:** `P1-high`, `epic-2-multi-level`, `agent-beta`, `sprint-2`

**Milestone:** Milestone 2: Detail Extraction

**Description:**

### 🎯 Goal
Extract detailed information from individual tender pages (Level 2 scraping).

### 📋 Tasks
- [ ] Parse onclick parameters from table: `viewIDim(596471,101,596461)`
- [ ] Build detail page URL with parameters
- [ ] Navigate to detail page
- [ ] Extract "Current Tender Details" section
- [ ] Extract "Eligibility Particulars"
- [ ] Extract "General Terms and Conditions"
- [ ] Extract "Legal Terms & Conditions"
- [ ] Extract "Technical Terms"
- [ ] Extract "Enquiry Forms" table
- [ ] Handle missing sections gracefully
- [ ] Save to `tender_details` table

### ✅ Acceptance Criteria
- Extracts `viewIDim` parameters correctly from HTML
- Constructs proper detail page URL
- Opens detail pages successfully
- Parses all major sections
- Handles pages with missing data
- Saves details to database
- No crashes on malformed pages

### 📁 Files Changed
- `src/scrapers/api_scraper.py`
- `src/scrapers/selenium_scraper.py`

### 🔗 Related Issues
- Depends on #1 or #2 (Need scraper working first)
- Blocks #5 (Document links are on detail page)

---

## ============================================================================
## ISSUE #5: Document Link Extraction
## ============================================================================

**Title:** [ALPHA] Document Link Extraction

**Labels:** `P1-high`, `epic-2-multi-level`, `agent-alpha`, `sprint-2`

**Milestone:** Milestone 2: Detail Extraction

**Description:**

### 🎯 Goal
Find and extract all document download links from detail pages (Level 3 scraping).

### 📋 Tasks
- [ ] Locate "Tender Documents" section
- [ ] Find "Corrigendum" links (if exist)
- [ ] Extract PDF download links
- [ ] Extract Excel/Word document links
- [ ] Extract file types from URLs or extensions
- [ ] Generate clean, descriptive filenames
- [ ] Store document metadata in database
- [ ] Handle pages with no documents
- [ ] Handle multiple documents per tender

### ✅ Acceptance Criteria
- Finds all document links on page
- Identifies file types correctly (PDF/Excel/Word)
- Creates descriptive filenames (no special chars)
- Stores URLs and metadata in `documents` table
- Handles missing documents gracefully
- Handles multiple documents per tender
- Links are valid and downloadable

### 📁 Files Changed
- `src/scrapers/api_scraper.py`
- `src/services/downloader.py`

### 🔗 Related Issues
- Depends on #4 (Detail page extraction)
- Blocks #6 (Document downloader needs URLs)

---

## ============================================================================
## ISSUE #6: Document Downloader
## ============================================================================

**Title:** [GAMMA] Document Downloader

**Labels:** `P2-medium`, `epic-3-documents`, `agent-gamma`, `sprint-3`

**Milestone:** Milestone 3: Document Processing

**Description:**

### 🎯 Goal
Download tender documents (PDFs, Excel, Word) to local storage.

### 📋 Tasks
- [ ] Create directory structure: `data/downloads/{tender_id}/`
- [ ] Implement download function with retry logic (3 attempts)
- [ ] Add rate limiting (1-2 second delay between downloads)
- [ ] Verify file integrity (check file size > 0)
- [ ] Update `download_status` in database
- [ ] Skip already downloaded files
- [ ] Handle download failures gracefully
- [ ] Log all download attempts

### ✅ Acceptance Criteria
- Downloads PDFs, Excel, Word files successfully
- Organizes files by tender ID
- Retries on failure (up to 3 times)
- Updates database status (`downloading`, `downloaded`, `failed`)
- Doesn't re-download existing files
- Handles network errors gracefully
- Logs all activities

### 📁 Files Changed
- `src/services/downloader.py`

### 🔗 Related Issues
- Depends on #5 (Need document URLs)
- Blocks #7 (Parser needs downloaded files)

---

## ============================================================================
## ISSUE #7: Document Parser (PDF/Excel/Word)
## ============================================================================

**Title:** [GAMMA] Document Parser

**Labels:** `P2-medium`, `epic-3-documents`, `agent-gamma`, `sprint-3`

**Milestone:** Milestone 3: Document Processing

**Description:**

### 🎯 Goal
Parse documents to extract key tender information using regex patterns.

### 📋 Tasks
- [ ] PDF parser using pdfplumber (primary) and PyPDF2 (fallback)
- [ ] Excel parser using pandas
- [ ] Word parser using python-docx
- [ ] Extract EMD amounts using regex
- [ ] Extract eligibility criteria
- [ ] Extract submission deadlines
- [ ] Extract estimated costs/contract values
- [ ] Store extracted fields in `extracted_fields` table
- [ ] Handle corrupt/unreadable files
- [ ] Log parsing success/failures

### ✅ Acceptance Criteria
- Parses all three file types (PDF, Excel, Word)
- Extracts EMD with >80% accuracy
- Extracts dates correctly (various formats)
- Handles corrupt files without crashing
- Stores fields in structured format
- Logs which fields were extracted
- Returns empty dict on parsing failure

### 📁 Files Changed
- `src/services/parser.py`

### 🔗 Related Issues
- Depends on #6 (Need downloaded files)
- Part of #8 (Pipeline integration)

---

## ============================================================================
## ISSUE #8: End-to-End Pipeline
## ============================================================================

**Title:** [DELTA] End-to-End Pipeline Orchestration

**Labels:** `P0-critical`, `epic-4-pipeline`, `agent-delta`, `sprint-3`

**Milestone:** Milestone 3: Document Processing

**Description:**

### 🎯 Goal
Orchestrate complete tender extraction workflow from scraping to parsed data.

### 📊 Pipeline Flow
```
1. Scrape tender list (API or Selenium)
   ↓
2. For each tender:
   a. Get tender details
   b. Save basic info to database
   c. Extract document URLs
   d. Download documents
   e. Parse documents
   f. Save parsed fields
   ↓
3. Log results (success/failure counts)
4. Generate summary report
```

### 📋 Tasks
- [ ] Create `TenderPipeline` orchestrator class
- [ ] Integrate API scraper → database
- [ ] Integrate Selenium fallback logic
- [ ] Integrate document downloader
- [ ] Integrate document parser
- [ ] Add transaction management (rollback on error)
- [ ] Add progress tracking (X of Y tenders)
- [ ] Log each pipeline step
- [ ] Generate success/failure summary
- [ ] Handle partial failures gracefully

### ✅ Acceptance Criteria
- Runs complete workflow for one tender successfully
- Rolls back database changes on error
- Logs each step with timestamps
- Generates summary: tenders found, scraped, failed
- Can process 100 tenders end-to-end
- Continues processing remaining tenders after single failure
- Summary report saved to database

### 📁 Files Changed
- `src/pipeline/orchestrator.py`
- `src/pipeline/tasks.py`
- `main.py`

### 🔗 Related Issues
- Depends on #1, #2, #3, #4, #5, #6, #7
- Required for production deployment

---

## ============================================================================
## ISSUE #9: Error Handling & Retry Logic
## ============================================================================

**Title:** [ALPHA] Error Handling & Retry Logic

**Labels:** `P1-high`, `epic-4-pipeline`, `agent-alpha`, `sprint-4`

**Milestone:** Milestone 4: Automation

**Description:**

### 🎯 Goal
Implement robust error handling and retry logic throughout the system.

### 📋 Tasks
- [ ] Define custom exceptions (`ScraperException`, `DatabaseException`, etc.)
- [ ] Create retry decorator with exponential backoff
- [ ] Add error logging with full context (stack trace, parameters)
- [ ] Save failed tenders to separate table for manual review
- [ ] Create error summary report
- [ ] Test with intentional failures
- [ ] Handle network timeouts
- [ ] Handle database connection errors
- [ ] Handle parsing errors

### ✅ Acceptance Criteria
- Retries transient failures (network, timeout) 3 times
- Uses exponential backoff (2s, 4s, 8s)
- Logs errors with full context
- Doesn't crash entire pipeline on single failure
- Continues processing remaining tenders
- Reports all failures in summary
- Failed tenders logged for retry

### 📁 Files Changed
- `src/utils/exceptions.py`
- `src/utils/helpers.py`
- `src/pipeline/orchestrator.py`

### 🔗 Related Issues
- Enhances #1 (API scraper reliability)
- Enhances #8 (Pipeline robustness)

---

## ============================================================================
## ISSUE #10: AWS Deployment Setup
## ============================================================================

**Title:** [EPSILON] AWS Mumbai Deployment

**Labels:** `P0-critical`, `epic-5-deployment`, `agent-epsilon`, `sprint-1`

**Milestone:** Milestone 1: Foundation

**Description:**

### 🎯 Goal
Deploy scraper to AWS EC2 in Mumbai region (ap-south-1).

### ☁️ AWS Configuration
- **Region:** ap-south-1 (Mumbai)
- **Instance Type:** t3.medium (2 vCPU, 4 GB RAM)
- **OS:** Ubuntu 22.04 LTS
- **Storage:** 30 GB

### 📋 Tasks
- [ ] Verify EC2 instance in Mumbai region
- [ ] SSH into instance
- [ ] Update system: `sudo apt update && sudo apt upgrade`
- [ ] Install Python 3.10+
- [ ] Install Chrome browser
- [ ] Install ChromeDriver
- [ ] Create project directory: `/opt/tender-scraper`
- [ ] Setup virtual environment
- [ ] Clone repository
- [ ] Install dependencies from `requirements.txt`
- [ ] Configure environment variables (`.env`)
- [ ] Test scraper runs successfully
- [ ] Configure security groups (allow SSH, HTTP for health check)
- [ ] Document deployment steps

### ✅ Acceptance Criteria
- EC2 instance accessible via SSH
- Python 3.10+ installed
- Chrome browser installed and working
- Virtual environment created
- All dependencies installed
- Scraper runs without errors
- Can access from Indian IP (no geo-blocking)
- Security groups configured correctly

### 📁 Files Changed
- `scripts/deploy.sh`
- `docs/04_DEPLOYMENT.md`

### 🔗 Related Issues
- Required for #1 (API scraper testing)
- Required for #11 (Cron scheduling)

---

## ============================================================================
## ISSUE #11: Cron Job Scheduling
## ============================================================================

**Title:** [EPSILON] Cron Job Scheduling

**Labels:** `P1-high`, `epic-5-deployment`, `agent-epsilon`, `sprint-4`

**Milestone:** Milestone 4: Automation

**Description:**

### 🎯 Goal
Schedule daily automated scraping at 9 AM IST.

### 📋 Tasks
- [ ] Create cron script: `scripts/run_daily.sh`
- [ ] Add shebang and proper error handling
- [ ] Activate virtual environment in script
- [ ] Run main.py with proper parameters
- [ ] Redirect output to log file
- [ ] Add email notification on completion/failure
- [ ] Configure crontab: `0 9 * * *` (9 AM IST)
- [ ] Test cron execution manually
- [ ] Verify logs are created
- [ ] Document how to enable/disable

### ✅ Acceptance Criteria
- Cron script executes successfully
- Runs daily at 9 AM IST
- Logs output to `data/logs/daily_run.log`
- Sends email summary on completion
- Can be easily enabled/disabled
- Handles scraper failures gracefully
- Rotates logs (keeps last 30 days)

### 📁 Files Changed
- `scripts/run_daily.sh`
- Crontab configuration

### 🔗 Related Issues
- Depends on #10 (AWS deployment)
- Depends on #8 (Pipeline must work)

---

## ============================================================================
## ISSUE #12: Monitoring & Alerting
## ============================================================================

**Title:** [EPSILON] Monitoring & Alerting

**Labels:** `P1-high`, `epic-5-deployment`, `agent-epsilon`, `sprint-4`

**Milestone:** Milestone 4: Automation

**Description:**

### 🎯 Goal
Monitor system health and send alerts on failures.

### 📋 Tasks
- [ ] Setup CloudWatch Logs for EC2
- [ ] Create health check endpoint (FastAPI)
- [ ] Endpoint returns: status, last run time, success rate
- [ ] Configure email alerts for failures
- [ ] Track success rate metrics
- [ ] Setup log rotation (weekly)
- [ ] Create simple dashboard (optional)
- [ ] Test alert triggers
- [ ] Document monitoring setup

### ✅ Acceptance Criteria
- Logs sent to CloudWatch automatically
- Email sent on scraper failure
- Health endpoint accessible: `http://instance:8000/health`
- Returns JSON with status
- Logs rotated weekly
- Can view metrics easily
- Alerts tested and working

### 📁 Files Changed
- `scripts/health_check.py`
- CloudWatch configuration
- Email alert configuration

### 🔗 Related Issues
- Depends on #10 (AWS deployment)
- Enhances #11 (Cron monitoring)

---

## ============================================================================
## ISSUE #13: Unit Tests
## ============================================================================

**Title:** [DELTA] Unit Tests

**Labels:** `P2-medium`, `epic-6-testing`, `agent-delta`, `sprint-5`

**Milestone:** Milestone 5: Production Ready

**Description:**

### 🎯 Goal
Write comprehensive unit tests for core functions.

### 📋 Tasks
- [ ] Setup pytest configuration
- [ ] Test API scraper functions (session, parsing)
- [ ] Test Selenium scraper functions
- [ ] Test database operations (CRUD)
- [ ] Test document parser functions
- [ ] Mock external API calls
- [ ] Mock file system operations
- [ ] Test error handling
- [ ] Achieve >70% code coverage
- [ ] Add pytest to CI/CD

### ✅ Acceptance Criteria
- All tests pass
- Code coverage > 70%
- Tests run in < 2 minutes
- Can run with `pytest` command
- Mocks external dependencies
- Tests edge cases
- CI/CD runs tests automatically

### 📁 Files Changed
- `tests/unit/test_scrapers.py`
- `tests/unit/test_database.py`
- `tests/unit/test_services.py`
- `pytest.ini`

### 🔗 Related Issues
- Tests all components from #1-#9

---

## ============================================================================
## ISSUE #14: Integration Tests
## ============================================================================

**Title:** [DELTA] Integration Tests

**Labels:** `P2-medium`, `epic-6-testing`, `agent-delta`, `sprint-5`

**Milestone:** Milestone 5: Production Ready

**Description:**

### 🎯 Goal
End-to-end testing of complete workflow with real data.

### 📋 Tasks
- [ ] Test scraping → database flow
- [ ] Test document download flow
- [ ] Test parser accuracy with real documents
- [ ] Test error handling scenarios
- [ ] Test with 10 real tenders
- [ ] Measure success rate
- [ ] Validate parser accuracy
- [ ] Document test results
- [ ] Create test report

### ✅ Acceptance Criteria
- Complete workflow tested end-to-end
- Success rate measured and documented
- Parser accuracy validated (>80% for EMD)
- Error scenarios tested
- Test report created: `docs/TEST_RESULTS.md`
- Real tender data tested
- No manual intervention needed

### 📁 Files Changed
- `tests/integration/test_pipeline.py`
- `docs/TEST_RESULTS.md`

### 🔗 Related Issues
- Tests complete system from #1-#9

---

## ============================================================================
## ISSUE #15: Documentation
## ============================================================================

**Title:** [ALL] Comprehensive Documentation

**Labels:** `P2-medium`, `epic-6-testing`, `all-agents`, `sprint-5`

**Milestone:** Milestone 5: Production Ready

**Description:**

### 🎯 Goal
Create comprehensive documentation for the project.

### 📋 Tasks
- [ ] Write README with quick start guide
- [ ] Document installation steps
- [ ] Document configuration options
- [ ] Create architecture diagrams
- [ ] Write troubleshooting guide
- [ ] Document common issues and solutions
- [ ] Add code comments to all functions
- [ ] Create API documentation
- [ ] Document deployment process
- [ ] Create video walkthrough (optional)

### ✅ Acceptance Criteria
- New developer can setup in < 30 minutes
- All functions have docstrings
- Common issues documented
- Architecture diagram clear
- Examples provided
- README professional and complete
- All docs folder files completed

### 📁 Files Changed
- `README.md`
- `docs/01_SETUP.md`
- `docs/02_ARCHITECTURE.md`
- `docs/03_API.md`
- `docs/04_DEPLOYMENT.md`
- `docs/05_TROUBLESHOOTING.md`
- `docs/06_AI_AGENTS.md`

### 🔗 Related Issues
- Documents all components from #1-#14

---

## ============================================================================
## END OF ISSUES
## ============================================================================

**Next Steps:**
1. Copy each issue above into GitHub (go to Issues → New Issue)
2. Create labels: P0-critical, P1-high, P2-medium, agent-alpha, etc.
3. Create milestones: Milestone 1-5
4. Create project board with these columns: Backlog, To Do, In Progress, Review, Done
5. Add all issues to project board
