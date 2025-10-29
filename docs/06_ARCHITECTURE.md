# 🏗️ Architecture Documentation

## System Overview

The Tender Scraper Engine is designed as a modular, scalable system for extracting tender data from the Telangana eTender portal.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER / CRON JOB                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      MAIN PIPELINE                          │
│                  (pipeline/orchestrator.py)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ API SCRAPER  │  │   SELENIUM   │  │   HYBRID     │
    │   (Primary)  │  │  (Fallback)  │  │ (Auto-switch)│
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    DATABASE     │
                    │   (SQLAlchemy)  │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │ DOWNLOADER │  │   PARSER   │  │ VALIDATOR  │
        └────────────┘  └────────────┘  └────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  EXTRACTED DATA │
                    └─────────────────┘
```

## Component Details

### 1. Scrapers (`src/scrapers/`)

#### API Scraper (Primary Method)
- **Purpose**: Fast data extraction via AJAX endpoints
- **Advantages**: Fast, efficient, reliable
- **Challenges**: Requires session management
- **Implementation**: `api_scraper.py`

**Flow:**
```
1. Visit main page → Get session cookie
2. POST to JSON API → Get tender list
3. Parse JSON response → Extract tender data
4. For each tender → Get detail page
5. Save to database
```

#### Selenium Scraper (Fallback)
- **Purpose**: Browser-based scraping when API fails
- **Advantages**: Handles JavaScript, simulates human
- **Challenges**: Slower, resource-intensive
- **Implementation**: `selenium_scraper.py`

**Flow:**
```
1. Launch Chrome browser (headless)
2. Load tender listing page
3. Wait for DataTable to populate
4. Extract data from table rows
5. Click "View Details" → New window
6. Extract detail page data
7. Close browser
```

#### Hybrid Scraper
- **Purpose**: Automatically switch between methods
- **Logic**: Try API first, fallback to Selenium on failure
- **Implementation**: `hybrid_scraper.py`

### 2. Database Layer (`src/database/`)

#### Models (`models.py`)

**Entity Relationship:**
```
tenders (1) ──< (M) documents
   │
   ├──< (1:1) tender_details
   │
   └──< (M) extracted_fields

documents (1) ──< (M) extracted_fields
```

**Tables:**

1. **tenders**: Basic tender information
2. **tender_details**: Extended tender information
3. **documents**: Document metadata and download status
4. **extracted_fields**: Parsed data from documents
5. **scrape_logs**: Audit trail and metrics

#### Operations (`operations.py`)

- `create_tender()`: Insert new tender
- `get_tender()`: Retrieve tender by ID
- `update_tender()`: Update tender info
- `save_document()`: Save document metadata
- `get_pending_downloads()`: Get documents to download
- `log_scrape_run()`: Log scraping session

### 3. Services (`src/services/`)

#### Document Downloader
- Downloads PDF, Excel, Word files
- Implements retry logic (3 attempts)
- Rate limiting (2-5 second delays)
- Verifies file integrity

#### Document Parser
- Extracts structured data from documents
- Uses regex patterns for EMD, dates, amounts
- Handles multiple file formats
- Returns structured fields

#### Data Validator
- Validates extracted data
- Checks date formats
- Validates amounts
- Ensures data completeness

### 4. Pipeline (`src/pipeline/`)

#### Orchestrator
Coordinates the complete workflow:

```python
def run_full_pipeline(limit=None):
    1. scrape_tender_list()
    2. for each tender:
        a. scrape_tender_details()
        b. save_to_database()
        c. extract_document_urls()
        d. download_documents()
        e. parse_documents()
        f. save_extracted_fields()
    3. log_results()
    4. generate_summary()
```

#### Task Manager
- Manages individual pipeline tasks
- Handles task dependencies
- Tracks task status

#### Scheduler
- Manages cron job execution
- Handles scheduling logic
- Monitors execution

### 5. Utilities (`src/utils/`)

#### Logger
- Structured logging
- Multiple log levels
- File and console output
- Log rotation

#### Helpers
- Retry decorator with exponential backoff
- Date parsing utilities
- String sanitization
- File utilities

#### Custom Exceptions
- `ScraperException`: Scraping errors
- `DatabaseException`: Database errors
- `ParserException`: Parsing errors
- `NetworkException`: Network errors

## Data Flow

### Complete Tender Extraction Flow

```
1. START
   │
   ├─→ Visit main page (get session)
   │
   ├─→ Call API endpoint (get tender list)
   │   └─→ Parse JSON response
   │
   ├─→ For each tender:
   │   │
   │   ├─→ Extract basic info
   │   │   └─→ Save to `tenders` table
   │   │
   │   ├─→ Navigate to detail page
   │   │   └─→ Extract extended info
   │   │       └─→ Save to `tender_details` table
   │   │
   │   ├─→ Find document links
   │   │   └─→ Save to `documents` table
   │   │
   │   ├─→ Download documents
   │   │   └─→ Update download status
   │   │
   │   └─→ Parse documents
   │       └─→ Save to `extracted_fields` table
   │
   └─→ Log results to `scrape_logs`
   │
2. END
```

## Error Handling Strategy

### Retry Logic

```python
@retry(max_attempts=3, backoff=exponential)
def scrape_tender(tender_id):
    # Transient errors retry automatically
    # Network timeouts
    # 5xx server errors
    pass
```

### Failure Recovery

1. **Single Tender Failure**: Continue with next tender
2. **API Failure**: Switch to Selenium
3. **Database Error**: Rollback transaction
4. **Document Download Failure**: Mark for manual review

### Logging Strategy

```
ERROR: Failed to scrape tender 12345
  - Reason: Network timeout
  - Attempts: 3
  - Next action: Skip and continue
  - Logged to: scrape_logs table
```

## Performance Considerations

### Optimization Strategies

1. **Connection Pooling**: Reuse HTTP sessions
2. **Batch Processing**: Process tenders in batches
3. **Parallel Downloads**: Download multiple documents simultaneously
4. **Caching**: Cache frequently accessed data
5. **Indexing**: Database indexes on tender_id, dates

### Resource Management

- **Memory**: Limit concurrent operations
- **CPU**: Balance between threads
- **Disk**: Rotate logs, clean old downloads
- **Network**: Rate limiting, respect robots.txt

## Security Considerations

### Data Security

1. **Environment Variables**: Sensitive configs in .env
2. **Database**: Encrypted connections (production)
3. **Credentials**: Never commit to git
4. **API Keys**: Rotate regularly

### Scraping Ethics

1. **Rate Limiting**: 2-5 second delays between requests
2. **User Agent**: Identify as scraper
3. **Robots.txt**: Respect crawl rules
4. **Terms of Service**: Comply with site policies

## Scalability

### Horizontal Scaling

**Distributed Architecture:**
```
Load Balancer
    │
    ├─→ Scraper Instance 1 (API)
    ├─→ Scraper Instance 2 (Selenium)
    └─→ Scraper Instance 3 (Parser)
         │
         └─→ Shared PostgreSQL Database
```

### Vertical Scaling

- Upgrade EC2 instance type
- Increase database resources
- Add more workers per instance

## Monitoring & Observability

### Metrics Tracked

1. **Scraping Metrics**
   - Tenders scraped per day
   - Success rate
   - Average scraping time
   - Error rate by type

2. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk space
   - Network bandwidth

3. **Business Metrics**
   - Documents downloaded
   - Fields extracted
   - Data quality score
   - Parser accuracy

### Alerting

- **Critical**: Scraper completely down
- **High**: Success rate < 80%
- **Medium**: Disk space > 80%
- **Low**: Parser accuracy < 70%

## Testing Strategy

### Unit Tests
- Test individual functions
- Mock external dependencies
- Fast execution (<2 min)

### Integration Tests
- Test complete workflows
- Use test database
- Real-world scenarios

### End-to-End Tests
- Test on staging environment
- Real tender data
- Complete pipeline

## Deployment Architecture

### Production Setup (AWS Mumbai)

```
Internet
    │
    └─→ Security Group (22, 8000)
         │
         └─→ EC2 Instance (t3.medium)
              ├─→ Application (Python)
              ├─→ Database (SQLite/PostgreSQL)
              ├─→ Cron Jobs (Daily at 9 AM)
              └─→ CloudWatch Logs
```

### CI/CD Pipeline

```
GitHub Push
    │
    ├─→ GitHub Actions
    │    ├─→ Run tests
    │    ├─→ Check code quality
    │    └─→ Build artifacts
    │
    └─→ Deploy to AWS
         ├─→ Pull latest code
         ├─→ Install dependencies
         ├─→ Restart services
         └─→ Verify deployment
```

## Future Enhancements

1. **Real-time Scraping**: WebSocket support
2. **Advanced Parsing**: ML-based extraction
3. **API Endpoints**: Expose data via REST API
4. **Web Dashboard**: Monitor progress in real-time
5. **Multi-site Support**: Scrape multiple tender portals
6. **Data Enrichment**: Add external data sources

## Troubleshooting Guide

### Common Issues

1. **Session Expired**: Re-establish session
2. **Rate Limited**: Increase delays
3. **Parsing Errors**: Update regex patterns
4. **Memory Leaks**: Restart scraper
5. **Database Locks**: Check concurrent access

## Appendix

### Technology Stack

- **Language**: Python 3.10+
- **Web Scraping**: requests, BeautifulSoup, Selenium
- **Database**: SQLAlchemy, SQLite/PostgreSQL
- **Document Parsing**: pdfplumber, python-docx, pandas
- **Testing**: pytest
- **Deployment**: AWS EC2, CloudWatch
- **CI/CD**: GitHub Actions

### Key Dependencies

- `requests`: HTTP client
- `selenium`: Browser automation
- `sqlalchemy`: ORM
- `beautifulsoup4`: HTML parsing
- `pdfplumber`: PDF extraction
- `pandas`: Data processing
- `loguru`: Logging

### References

- [Telangana eTender Portal](https://tender.telangana.gov.in)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Selenium Documentation](https://selenium-python.readthedocs.io)

