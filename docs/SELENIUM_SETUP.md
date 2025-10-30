# Selenium Setup with undetected-chromedriver

This document describes the setup and configuration of undetected-chromedriver for the Selenium fallback scraper.

## Overview

The Selenium scraper uses `undetected-chromedriver` (v3.5.4) to avoid detection by anti-bot mechanisms on the tender portal. This library patches the ChromeDriver binary to remove automation detection signatures.

## How It Works

1. **Auto-detection**: On first run, the scraper looks for a system-installed ChromeDriver
2. **Local Copy**: If found, it creates a local writable copy in `data/drivers/chromedriver`
3. **Patching**: undetected-chromedriver patches this local copy to avoid detection
4. **Reuse**: Subsequent runs use the patched local copy

## Requirements

- **Chrome/Chromium Browser**: Version 108 or higher
- **ChromeDriver**: Matching the installed Chrome version
- **Python Package**: `undetected-chromedriver==3.5.4`

## Installation

### 1. Install Chrome/Chromium

On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

On other systems, download from https://www.google.com/chrome/

### 2. Install ChromeDriver

ChromeDriver should match your Chrome version. On Ubuntu:
```bash
sudo apt-get install -y chromium-chromedriver
```

Or download manually from https://chromedriver.chromium.org/

### 3. Install Python Package

Already included in `requirements.txt`:
```bash
pip install undetected-chromedriver==3.5.4
```

## Usage

### Basic Usage

```python
from src.scrapers.selenium_scraper import SeleniumScraper

# Create scraper (headless mode)
scraper = SeleniumScraper(headless=True)

# Scrape tender list
tenders = scraper.scrape_tender_list(limit=10)

# Always clean up
scraper.cleanup()
```

### With Visible Browser (for debugging)

```python
scraper = SeleniumScraper(headless=False)
# Browser window will be visible
```

## Configuration

The scraper automatically handles ChromeDriver setup. Key paths:

- **Local ChromeDriver**: `data/drivers/chromedriver`
- **Screenshots**: `data/screenshots/` (taken on errors)
- **System ChromeDriver**: `/usr/bin/chromedriver` (copied from here)

## Troubleshooting

### "No system chromedriver found"

**Solution**: Install ChromeDriver:
```bash
sudo apt-get install chromium-chromedriver
# or
sudo apt-get install google-chrome-stable chromium-chromedriver
```

### "Chrome driver initialization failed"

**Possible causes**:
1. Chrome/Chromium not installed
2. Chrome version mismatch with ChromeDriver
3. Insufficient permissions

**Solution**: 
```bash
# Check Chrome version
google-chrome --version

# Check ChromeDriver version (should match)
chromedriver --version

# Reinstall if versions don't match
```

### Network Issues in Restricted Environments

If undetected-chromedriver can't download ChromeDriver automatically (network restrictions):

1. **Manually install ChromeDriver** to system PATH
2. The scraper will automatically copy it to `data/drivers/`
3. Or manually place ChromeDriver in `data/drivers/chromedriver`

### Permission Denied

If you see "Permission denied: '/usr/bin/chromedriver'":

This is expected! The scraper automatically creates a local copy in `data/drivers/` which can be modified. No action needed.

## Architecture

### Initialization Flow

```
SeleniumScraper.__init__()
  ↓
_setup_chromedriver()
  ↓
  Check: data/drivers/chromedriver exists?
    Yes → Use it
    No  → Copy from /usr/bin/chromedriver
  ↓
_init_driver()
  ↓
  Create undetected_chromedriver.Chrome
    with driver_executable_path=data/drivers/chromedriver
  ↓
  Driver ready for use
```

### Key Methods

- `_setup_chromedriver()`: Ensures local ChromeDriver copy exists
- `_init_driver()`: Creates undetected-chromedriver instance
- `cleanup()`: Closes browser and releases resources

## Testing

### Unit Tests
```bash
pytest tests/unit/test_selenium_scraper.py -v
```

### Integration Tests
```bash
pytest tests/integration/test_selenium_setup.py -v
```

### Manual Verification
```bash
python -c "
from src.scrapers.selenium_scraper import SeleniumScraper
scraper = SeleniumScraper(headless=True)
print('✓ Setup successful!')
scraper.cleanup()
"
```

## Environment Variables

Relevant settings in `.env`:

```bash
# Browser mode (for selenium)
HEADLESS=true

# Scraper mode
SCRAPER_MODE=selenium  # or 'api' or 'hybrid'
```

## Performance

- **Initialization**: ~2-3 seconds (first time with patching)
- **Subsequent runs**: ~1-2 seconds (uses patched copy)
- **Page load**: ~5-10 seconds (depends on network/page)

## Security Notes

1. **Anti-Detection**: undetected-chromedriver patches ChromeDriver to avoid detection
2. **Human-like Behavior**: Random delays (2-5 seconds) between actions
3. **User Agent**: Configurable user agent string
4. **Screenshots**: Error screenshots saved for debugging (no sensitive data)

## Known Limitations

1. **Version Matching**: Chrome and ChromeDriver versions must match
2. **Network Required**: First-time setup may need internet for ChromeDriver download (if not system-installed)
3. **Resource Usage**: Chrome uses ~200-500MB RAM per instance
4. **Single Instance**: Only one scraper instance per process recommended

## Maintenance

### Updating ChromeDriver

When Chrome updates:

1. Update system ChromeDriver to match
2. Delete `data/drivers/chromedriver`
3. Restart scraper (will create new patched copy)

```bash
# Remove old local copy
rm data/drivers/chromedriver

# Update system ChromeDriver
sudo apt-get update
sudo apt-get install --only-upgrade chromium-chromedriver

# Scraper will auto-copy new version on next run
```

## Support

For issues with undetected-chromedriver:
- GitHub: https://github.com/ultrafunkamsterdam/undetected-chromedriver
- Documentation: https://github.com/ultrafunkamsterdam/undetected-chromedriver/blob/master/README.md

For project-specific issues:
- See docs/07_TROUBLESHOOTING.md
- Check GitHub Issues
