# ☁️ AWS Deployment Guide

## Deployment to AWS Mumbai (ap-south-1)

### Prerequisites

- AWS Account
- SSH key pair
- Basic AWS knowledge

## EC2 Instance Setup

### 1. Launch EC2 Instance

**Instance Configuration:**
- **Region**: ap-south-1 (Mumbai)
- **AMI**: Ubuntu 22.04 LTS
- **Instance Type**: t3.medium (2 vCPU, 4 GB RAM)
- **Storage**: 30 GB gp3
- **Security Group**: 
  - SSH (22) - Your IP only
  - HTTP (8000) - For health check

### 2. Connect to Instance

```bash
# Save your key pair
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@YOUR_INSTANCE_IP
```

### 3. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1)
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}
DRIVER_VERSION=$(cat LATEST_RELEASE_${CHROME_VERSION})
wget https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Install git
sudo apt install -y git
```

### 4. Deploy Application

```bash
# Create project directory
sudo mkdir -p /opt/tender-scraper
sudo chown ubuntu:ubuntu /opt/tender-scraper

# Clone repository
cd /opt/tender-scraper
git clone https://github.com/YOUR_USERNAME/tender360-scrape-application.git .

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
```

**Edit .env:**
```
DATABASE_URL=sqlite:///data/tender_scraper.db
BASE_URL=https://tender.telangana.gov.in
SCRAPER_MODE=api
HEADLESS=true
LOG_LEVEL=INFO
```

### 5. Initialize Database

```bash
python scripts/setup_db.py
```

### 6. Test Deployment

```bash
# Test with 5 tenders
python main.py --limit 5 --verbose

# Check logs
tail -f data/logs/scraper.log
```

## Automated Scheduling

### 1. Create Cron Script

```bash
# Edit cron script
nano scripts/run_daily.sh
```

**Content:**
```bash
#!/bin/bash
set -e

# Activate virtual environment
cd /opt/tender-scraper
source venv/bin/activate

# Run scraper
python main.py --mode hybrid >> data/logs/cron_$(date +\%Y\%m\%d).log 2>&1

# Send email notification (optional)
# echo "Scraper completed" | mail -s "Tender Scraper - Daily Run" alerts@yourcompany.com
```

```bash
# Make executable
chmod +x scripts/run_daily.sh
```

### 2. Setup Cron Job

```bash
# Edit crontab
crontab -e
```

**Add line:**
```
# Run daily at 9 AM IST
0 9 * * * /opt/tender-scraper/scripts/run_daily.sh
```

**Verify:**
```bash
crontab -l
```

## Monitoring Setup

### 1. Health Check Endpoint

```bash
# Start health check server
nohup python scripts/health_check.py &
```

**Test:**
```bash
curl http://localhost:8000/health
```

### 2. CloudWatch Logs (Optional)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure CloudWatch
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/tender-scraper/config/cloudwatch-config.json \
  -s
```

### 3. Email Alerts

Configure in `.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL=alerts@yourcompany.com
```

## Backup Strategy

### 1. Database Backups

```bash
# Create backup script
nano scripts/backup_db.sh
```

**Content:**
```bash
#!/bin/bash
BACKUP_DIR="/opt/tender-scraper/data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup database
cp data/tender_scraper.db ${BACKUP_DIR}/tender_scraper_${TIMESTAMP}.db

# Keep only last 7 days
find ${BACKUP_DIR} -name "tender_scraper_*.db" -mtime +7 -delete
```

```bash
chmod +x scripts/backup_db.sh
```

**Add to crontab:**
```
# Daily backup at midnight
0 0 * * * /opt/tender-scraper/scripts/backup_db.sh
```

### 2. Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/tender-scraper
```

**Content:**
```
/opt/tender-scraper/data/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 ubuntu ubuntu
}
```

## Troubleshooting

### Issue: Chrome crashes on AWS

**Solution:** Increase shared memory
```bash
sudo mount -o remount,size=2G /dev/shm
```

Add to `/etc/fstab`:
```
tmpfs /dev/shm tmpfs defaults,size=2G 0 0
```

### Issue: Cron job not running

**Solution:** Check cron logs
```bash
sudo grep CRON /var/log/syslog
```

### Issue: Database locked

**Solution:** Check for running processes
```bash
ps aux | grep python
# Kill if necessary
kill -9 PID
```

### Issue: Disk space full

**Solution:** Clean old logs and backups
```bash
# Check disk space
df -h

# Clean old logs
find data/logs -name "*.log" -mtime +30 -delete

# Clean old backups
find data/backups -name "*.db" -mtime +30 -delete
```

## Security Best Practices

1. **SSH Key Only**: Disable password authentication
2. **Security Groups**: Restrict access to your IP
3. **Regular Updates**: `sudo apt update && sudo apt upgrade`
4. **Firewall**: Use AWS Security Groups + UFW
5. **Backups**: Enable automated backups
6. **Monitoring**: Setup CloudWatch alarms

## Performance Optimization

1. **Database**: Use PostgreSQL for production
2. **Caching**: Cache frequently accessed data
3. **Parallel Processing**: Process multiple tenders
4. **Resource Monitoring**: Track CPU/Memory usage

## Scaling

### Horizontal Scaling

Deploy multiple instances:
- Instance 1: API scraping
- Instance 2: Selenium scraping
- Instance 3: Document processing

Use shared PostgreSQL RDS database.

### Vertical Scaling

Upgrade instance type:
- t3.large (2 vCPU, 8 GB) - Moderate load
- t3.xlarge (4 vCPU, 16 GB) - Heavy load

## Maintenance

### Weekly Tasks
- Check logs for errors
- Monitor success rates
- Review disk space
- Backup database

### Monthly Tasks
- Update dependencies
- Review performance metrics
- Optimize database
- Security audit

## Support

For deployment issues:
- Check logs: `tail -f data/logs/scraper.log`
- Review cron logs: `grep CRON /var/log/syslog`
- Test manually: `python main.py --limit 5 --verbose`

