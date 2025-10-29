# AWS Mumbai Testing Guide

## Overview

This document provides instructions for testing the API scraper with 100 tenders on AWS Mumbai (ap-south-1 region).

## Prerequisites

- AWS EC2 instance in Mumbai region (ap-south-1)
- Python 3.10 or higher
- Dependencies installed from requirements.txt

## Setup on AWS Mumbai

### 1. Connect to EC2 Instance

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 2. Clone and Setup Repository

```bash
# Clone repository
git clone https://github.com/vinaybeerelli/tender360-data-engine.git
cd tender360-data-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit configuration (optional)
nano .env
```

## Running Tests

### Quick Test (10 Tenders)

Test basic functionality with a small dataset:

```bash
pytest tests/integration/test_api_scraper_aws.py::TestAPIScraperAWSMumbai::test_scrape_10_tenders -v
```

### Full Test (100 Tenders)

Run the complete acceptance test with 100 tenders:

```bash
pytest tests/integration/test_api_scraper_aws.py::TestAPIScraperAWSMumbai::test_scrape_100_tenders_success_rate -v -s
```

### Test All AWS Integration Tests

```bash
pytest tests/integration/test_api_scraper_aws.py -v -s
```

### Using the Standalone Test Script

```bash
python scripts/test_100_tenders.py
```

## Success Criteria

The tests verify the following requirements:

✅ **Session Establishment**
- Session cookie (JSESSIONID) is obtained successfully
- Main page is visited before API calls

✅ **No 403 Errors**
- No Forbidden errors when running on AWS Mumbai
- Proper headers are sent with requests

✅ **Data Quality**
- API returns non-empty tender list
- All required fields are present
- HTML content is properly cleaned

✅ **Success Rate >= 90%**
- At least 90% of tenders have all required fields
- Valid tender IDs, work names, and notice numbers

## Expected Output

### Successful Run

```
================================ test session starts ================================
tests/integration/test_api_scraper_aws.py::TestAPIScraperAWSMumbai::test_scrape_100_tenders_success_rate

Results:
  Total tenders: 100
  Valid tenders: 95
  Success rate: 95.00%

Sample tenders:
  1. NOTICE-001 - Construction of Road Works in District XYZ
  2. NOTICE-002 - Supply of Medical Equipment for Hospital
  3. NOTICE-003 - Development of Water Supply Infrastructure
  4. NOTICE-004 - Renovation of School Buildings
  5. NOTICE-005 - IT Infrastructure Procurement

PASSED [100%]
```

## Troubleshooting

### 403 Forbidden Error

If you encounter 403 errors:

1. **Check Session Establishment**
   - Verify that main page is visited first
   - Check that JSESSIONID cookie is set

2. **Verify Headers**
   - Ensure all required headers are present
   - Check User-Agent string matches browser

3. **Check Rate Limiting**
   - Add delays between requests if needed
   - Verify MIN_DELAY and MAX_DELAY settings

### Empty Response

If no tenders are returned:

1. **Verify API Endpoint**
   - Check BASE_URL is correct
   - Verify TENDER_LIST_API path

2. **Check Request Payload**
   - Verify all DataTables parameters are included
   - Check iDisplayStart and iDisplayLength values

3. **Inspect Response**
   - Check for error messages in response
   - Verify JSON structure matches expected format

### Low Success Rate

If success rate is below 90%:

1. **Check Data Parsing**
   - Verify HTML cleaning logic
   - Check field extraction logic

2. **Review Failed Tenders**
   - Log tenders that fail validation
   - Identify common patterns in failures

3. **Adjust Validation**
   - Review required fields list
   - Consider data quality variations

## Performance Benchmarks

Expected performance on AWS Mumbai EC2 (t2.medium):

- **10 tenders**: ~5-10 seconds
- **100 tenders**: ~30-60 seconds
- **Success rate**: 90-95%

## Monitoring

### Logs

Logs are saved to `data/logs/scraper.log`:

```bash
tail -f data/logs/scraper.log
```

### Key Metrics to Monitor

- Success rate percentage
- Total tenders scraped
- Failed tender count
- Average response time
- Error types and frequencies

## Continuous Integration

The integration tests can be run in CI/CD pipeline:

```yaml
# .github/workflows/test.yml
test-aws:
  runs-on: self-hosted  # AWS Mumbai runner
  steps:
    - uses: actions/checkout@v2
    - name: Run integration tests
      run: |
        pytest tests/integration/test_api_scraper_aws.py -v
```

## Next Steps

After successful testing:

1. ✅ Verify 90%+ success rate achieved
2. ✅ Confirm no 403 errors occur
3. → Proceed to Issue #4: Tender Detail Page Extraction
4. → Implement document download functionality (Issue #5)

## Support

For issues or questions:

- Review logs in `data/logs/scraper.log`
- Check [Troubleshooting Guide](docs/07_TROUBLESHOOTING.md)
- Create GitHub issue with logs and error details
