# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Issue: `pip install` fails

**Error:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions:**
```bash
# Upgrade pip
pip install --upgrade pip

# Use specific Python version
python3.10 -m pip install -r requirements.txt

# Install with verbose output
pip install -r requirements.txt -v
```

---

#### Issue: Virtual environment not activating

**Solutions:**
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# If still fails, recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

---

### Scraping Issues

#### Issue: API returns empty data

**Error:**
```
Empty aaData in API response
```

**Root Cause:** Session not established

**Solution:**
```python
# Visit main page first to get session cookie
session = requests.Session()
session.get(BASE_URL + "/TenderDetailsHome.html")

# Then call API
response = session.post(API_ENDPOINT, data=payload, headers=headers)
```

---

#### Issue: 403 Forbidden error

**Error:**
```
HTTP 403: Forbidden
```

**Solutions:**

1. **Check Headers:**
```python
headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://tender.telangana.gov.in/TenderDetailsHome.html",
    "User-Agent": "Mozilla/5.0..."
}
```

2. **Check Session Cookie:**
```python
print(session.cookies)  # Should have JSESSIONID
```

3. **AWS IP Blocked:**
```bash
# Use VPN or proxy
# Or switch to Selenium mode
python main.py --mode selenium
```

---

#### Issue: Selenium times out

**Error:**
```
TimeoutException: Message: 
```

**Solutions:**

1. **Increase wait time:**
```python
from selenium.webdriver.support.ui import WebDriverWait
wait = WebDriverWait(driver, 30)  # Increase from 10 to 30
```

2. **Wait for specific element:**
```python
# Wait for table to have data, not just exist
wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#pagetable13 tbody tr")) > 1)
```

3. **Check Chrome/ChromeDriver version:**
```bash
google-chrome --version
chromedriver --version
# Versions should match
```

---

#### Issue: Chrome crashes on AWS

**Error:**
```
selenium.common.exceptions.WebDriverException: chrome not reachable
```

**Solutions:**

1. **Increase shared memory:**
```bash
sudo mount -o remount,size=2G /dev/shm
```

2. **Add Chrome options:**
```python
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
```

---

### Database Issues

#### Issue: Database locked

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**

1. **Check for other processes:**
```bash
ps aux | grep python
# Kill other instances
kill -9 PID
```

2. **Use timeout:**
```python
engine = create_engine(
    DATABASE_URL,
    connect_args={"timeout": 30}
)
```

3. **Switch to PostgreSQL** (for production)

---

#### Issue: Foreign key constraint failed

**Error:**
```
FOREIGN KEY constraint failed
```

**Solution:**
```python
# Ensure parent record exists first
tender = db.query(Tender).filter(Tender.tender_id == "12345").first()
if not tender:
    # Create tender first
    tender = Tender(tender_id="12345", ...)
    db.add(tender)
    db.commit()

# Then create child record
detail = TenderDetail(tender_id=tender.id, ...)
```

---

### Parsing Issues

#### Issue: PDF text extraction returns gibberish

**Error:**
```
EMD: ���������
```

**Solutions:**

1. **Try pdfplumber instead of PyPDF2:**
```python
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    text = pdf.pages[0].extract_text()
```

2. **Check encoding:**
```python
text = text.encode('utf-8', errors='ignore').decode('utf-8')
```

3. **OCR for scanned PDFs:**
```bash
pip install pytesseract
# Use Tesseract OCR
```

---

#### Issue: Regex not matching EMD

**Error:**
```
EMD field not found in document
```

**Solutions:**

1. **Test regex pattern:**
```python
import re
pattern = r"EMD[:\s]*(?:Rs\.?|INR)?[\s]*([0-9,]+(?:\.[0-9]{2})?)"
text = "EMD: Rs. 50,000.00"
match = re.search(pattern, text, re.IGNORECASE)
print(match.group(1) if match else "Not found")
```

2. **Try variations:**
```python
patterns = [
    r"EMD[:\s]*(?:Rs\.?|INR)?[\s]*([0-9,]+)",
    r"Earnest Money[:\s]*([0-9,]+)",
    r"Bank Guarantee[:\s]*([0-9,]+)"
]
```

---

### Deployment Issues

#### Issue: Cron job not running

**Solutions:**

1. **Check crontab:**
```bash
crontab -l
```

2. **Check cron logs:**
```bash
grep CRON /var/log/syslog
```

3. **Test script manually:**
```bash
/opt/tender-scraper/scripts/run_daily.sh
```

4. **Check permissions:**
```bash
chmod +x scripts/run_daily.sh
```

5. **Use absolute paths in crontab:**
```
0 9 * * * /opt/tender-scraper/scripts/run_daily.sh
```

---

#### Issue: Environment variables not loaded

**Error:**
```
KeyError: 'DATABASE_URL'
```

**Solutions:**

1. **Check .env file exists:**
```bash
ls -la /opt/tender-scraper/.env
```

2. **Source .env in script:**
```bash
#!/bin/bash
set -a
source /opt/tender-scraper/.env
set +a
python main.py
```

3. **Use absolute path for .env:**
```python
from pathlib import Path
load_dotenv(Path(__file__).parent / '.env')
```

---

### Performance Issues

#### Issue: Scraping is very slow

**Solutions:**

1. **Reduce delays:**
```python
# In .env
MIN_DELAY=1
MAX_DELAY=2
```

2. **Use API mode:**
```bash
python main.py --mode api  # Faster than selenium
```

3. **Parallel processing:**
```python
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(download_document, document_urls)
```

---

#### Issue: High memory usage

**Solutions:**

1. **Limit batch size:**
```python
# Process in smaller batches
for i in range(0, len(tenders), 10):
    batch = tenders[i:i+10]
    process_batch(batch)
```

2. **Close browser between tenders:**
```python
for tender in tenders:
    driver = webdriver.Chrome()
    # ... scrape ...
    driver.quit()  # Free memory
```

3. **Monitor memory:**
```bash
# Check memory usage
free -h
# Restart if needed
```

---

### Network Issues

#### Issue: Connection timeout

**Error:**
```
requests.exceptions.ConnectTimeout
```

**Solutions:**

1. **Increase timeout:**
```python
response = requests.get(url, timeout=60)  # 60 seconds
```

2. **Check network connectivity:**
```bash
ping tender.telangana.gov.in
curl -I https://tender.telangana.gov.in
```

3. **Use proxy:**
```python
proxies = {"http": "http://proxy:port", "https": "https://proxy:port"}
response = requests.get(url, proxies=proxies)
```

---

#### Issue: SSL certificate error

**Error:**
```
SSLError: certificate verify failed
```

**Solutions:**

1. **Update CA certificates:**
```bash
sudo apt install ca-certificates
sudo update-ca-certificates
```

2. **Temporary bypass (not recommended for production):**
```python
response = requests.get(url, verify=False)
```

---

## Debugging Tips

### Enable Verbose Logging

```bash
python main.py --verbose
```

### Check Logs

```bash
# Latest log
tail -f data/logs/scraper.log

# Search for errors
grep ERROR data/logs/scraper.log

# View last 100 lines
tail -n 100 data/logs/scraper.log
```

### Test Individual Components

```python
# Test scraper only
from src.scrapers.api_scraper import APIScraper
scraper = APIScraper()
tenders = scraper.scrape_tender_list(limit=5)
print(tenders)

# Test database only
from src.database.operations import create_tender
create_tender(db, tender_data)

# Test parser only
from src.services.parser import parse_pdf
fields = parse_pdf("document.pdf")
print(fields)
```

### Take Screenshots (Selenium)

```python
try:
    driver.get(url)
except Exception as e:
    driver.save_screenshot('error.png')
    raise
```

### Profile Performance

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
pipeline.run()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Getting Help

### Before Asking for Help

1. ✅ Check this troubleshooting guide
2. ✅ Review error logs
3. ✅ Test with `--verbose` flag
4. ✅ Search GitHub issues
5. ✅ Try on local machine first

### Creating a Bug Report

**Include:**
- Error message (full stack trace)
- Python version: `python --version`
- OS: `uname -a` (Linux) or system info
- Steps to reproduce
- Expected vs actual behavior
- Logs (relevant portion)

**Template:**
```markdown
## Environment
- OS: Ubuntu 22.04
- Python: 3.10.12
- Mode: API

## Error
```
[Full error message]
```

## Steps to Reproduce
1. ...
2. ...

## Expected Behavior
Should scrape 100 tenders successfully

## Actual Behavior
Fails after 10 tenders with timeout error

## Logs
```
[Relevant log entries]
```
```

### Where to Get Help

- **GitHub Issues**: https://github.com/YOUR_USERNAME/tender360-scrape-application/issues
- **Documentation**: https://github.com/YOUR_USERNAME/tender360-scrape-application/docs
- **Email**: support@yourcompany.com

## Quick Reference

### Common Commands

```bash
# Test with 5 tenders
python main.py --limit 5 --verbose

# Use Selenium mode
python main.py --mode selenium --visible

# View logs
tail -f data/logs/scraper.log

# Check database
sqlite3 data/tender_scraper.db "SELECT COUNT(*) FROM tenders;"

# Restart services
pkill -f "python main.py"
python main.py &

# Check disk space
df -h

# Check memory
free -h

# Monitor process
htop

# Test connectivity
curl -I https://tender.telangana.gov.in
```

### Useful SQL Queries

```sql
-- Count tenders
SELECT COUNT(*) FROM tenders;

-- Recent scrapes
SELECT * FROM scrape_logs ORDER BY run_date DESC LIMIT 5;

-- Failed tenders
SELECT tender_id, work_name FROM tenders WHERE scraped_at IS NULL;

-- Documents by status
SELECT download_status, COUNT(*) FROM documents GROUP BY download_status;

-- Success rate
SELECT 
    (COUNT(CASE WHEN scraped_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*)) as success_rate
FROM tenders;
```

## Still Stuck?

If none of these solutions work:

1. Create a GitHub issue with full details
2. Include logs, error messages, environment info
3. Describe what you've tried
4. Tag with appropriate labels (bug, help wanted)

We'll help you resolve the issue! 🚀

