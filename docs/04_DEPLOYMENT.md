# ☁️ AWS Deployment Guide

## Deployment to AWS Mumbai (ap-south-1)

This guide covers deploying the Tender Scraper Engine on AWS EC2 in the Mumbai region.

### Prerequisites

- AWS Account with EC2 access
- SSH key pair created in AWS
- Basic Linux and AWS knowledge
- Git installed locally (for cloning if needed)

---

## 🚀 Quick Start (Automated Deployment)

### 1. Launch EC2 Instance

**Instance Configuration:**
- **Region**: ap-south-1 (Mumbai)
- **AMI**: Ubuntu 22.04 LTS (ami-0f58b397bc5c1f2e8 or latest)
- **Instance Type**: t3.medium (2 vCPU, 4 GB RAM)
- **Storage**: 30 GB gp3
- **Security Group**: 
  - SSH (22) - Your IP only
  - HTTP (8000) - For health check endpoint
- **IAM Role**: Optional, for CloudWatch access

### 2. Connect to Instance

```bash
# Save your key pair (one-time)
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@YOUR_INSTANCE_IP
```

### 3. Run Automated Deployment

```bash
# Clone repository
git clone https://github.com/vinaybeerelli/tender360-data-engine.git
cd tender360-data-engine

# Run deployment script
sudo bash scripts/deploy.sh
```

The deployment script will automatically:
- ✅ Update system packages
- ✅ Install Python 3.10
- ✅ Install Google Chrome and ChromeDriver
- ✅ Setup virtual environment
- ✅ Install all dependencies
- ✅ Initialize database
- ✅ Configure security settings
- ✅ Run validation tests

**Deployment time:** ~10-15 minutes

### 4. Configure Environment

```bash
cd /opt/tender-scraper
sudo nano .env
```

Update key settings:
```bash
# Required settings
DATABASE_URL=sqlite:///data/tender_scraper.db
BASE_URL=https://tender.telangana.gov.in
SCRAPER_MODE=hybrid
HEADLESS=true

# Optional: Email notifications
SEND_EMAIL=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL=alerts@yourcompany.com
```

### 5. Test Deployment

```bash
cd /opt/tender-scraper
source venv/bin/activate
python main.py --limit 5 --verbose
```

**Expected output:**
```
================================================================================
TENDER SCRAPER ENGINE - Starting
================================================================================
Mode: hybrid
Limit: 5
...
✅ Successfully scraped 5 tenders
```

---

## 📅 Setup Automated Scheduling

### Daily Cron Job (9 AM IST)

```bash
# Edit crontab
crontab -e

# Add this line:
0 9 * * * /opt/tender-scraper/scripts/run_daily.sh
```

The `run_daily.sh` script handles:
- ✅ Lock file management (prevents overlapping runs)
- ✅ Disk space checks
- ✅ Automatic cleanup
- ✅ Error logging
- ✅ Email notifications
- ✅ Database backups
- ✅ Summary generation

**Verify cron job:**
```bash
crontab -l
```

---

## 🏥 Setup Health Monitoring

### Start Health Check Service

```bash
cd /opt/tender-scraper
source venv/bin/activate
nohup python scripts/health_check.py > data/logs/health_check.log 2>&1 &
```

### Test Health Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/health/detailed

# Prometheus metrics
curl http://localhost:8000/metrics
```

### Make Health Check Persistent (Systemd)

Create service file:
```bash
sudo nano /etc/systemd/system/tender-health-check.service
```

Add content:
```ini
[Unit]
Description=Tender Scraper Health Check Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/tender-scraper
Environment="PATH=/opt/tender-scraper/venv/bin"
ExecStart=/opt/tender-scraper/venv/bin/python /opt/tender-scraper/scripts/health_check.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tender-health-check
sudo systemctl start tender-health-check
sudo systemctl status tender-health-check
```

---

## 🔒 Security Configuration

### Firewall Setup (UFW)

The deployment script configures UFW automatically, but you can verify:

```bash
# Check status
sudo ufw status

# Should show:
# 22/tcp    ALLOW    (SSH)
# 8000/tcp  ALLOW    (Health check)
```

### Security Group Settings

In AWS Console, configure Security Group:

**Inbound Rules:**
- SSH (22): Your IP address only
- Custom TCP (8000): Your monitoring system IP (optional)

**Outbound Rules:**
- All traffic: 0.0.0.0/0 (required for scraping)

### SSH Key Only Access

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config

# Set these values:
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart sshd
```

---

## 📊 CloudWatch Integration (Optional)

### Install CloudWatch Agent

```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### Configure CloudWatch

Create config file:
```bash
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/config.json
```

Add configuration:
```json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/opt/tender-scraper/data/logs/scraper.log",
            "log_group_name": "/aws/tender-scraper/application",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/opt/tender-scraper/data/logs/cron_*.log",
            "log_group_name": "/aws/tender-scraper/cron",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "TenderScraper",
    "metrics_collected": {
      "disk": {
        "measurement": [
          {
            "name": "used_percent",
            "rename": "DiskUsage"
          }
        ],
        "metrics_collection_interval": 300
      },
      "mem": {
        "measurement": [
          {
            "name": "mem_used_percent",
            "rename": "MemoryUsage"
          }
        ],
        "metrics_collection_interval": 300
      }
    }
  }
}
```

Start agent:
```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json \
  -s
```

---

## 📦 Backup Strategy

### Automatic Backups

The `run_daily.sh` script automatically:
- Creates daily database backups
- Keeps last 7 days of backups
- Rotates logs (30 days)

### Manual Backup

```bash
# Backup database
cd /opt/tender-scraper
cp data/tender_scraper.db data/backups/manual_backup_$(date +%Y%m%d).db

# Backup to S3 (if configured)
aws s3 cp data/tender_scraper.db s3://your-bucket/backups/tender_scraper_$(date +%Y%m%d).db
```

### Restore from Backup

```bash
cd /opt/tender-scraper
cp data/backups/tender_scraper_YYYYMMDD.db data/tender_scraper.db
```


---

## 🔧 Troubleshooting

### Chrome/ChromeDriver Issues

**Issue:** Chrome crashes with "DevToolsActivePort file doesn't exist"

**Solution:** Increase shared memory
```bash
sudo mount -o remount,size=2G /dev/shm
```

Make permanent:
```bash
sudo nano /etc/fstab
# Add line:
tmpfs /dev/shm tmpfs defaults,size=2G 0 0
```

**Issue:** Chrome won't start in headless mode

**Solution:** Add Chrome arguments in code or use Xvfb
```bash
# Install Xvfb
sudo apt install -y xvfb

# Run with Xvfb
xvfb-run --auto-servernum python main.py
```

### Cron Job Not Running

**Check cron logs:**
```bash
sudo grep CRON /var/log/syslog | tail -20
```

**Verify cron is running:**
```bash
sudo systemctl status cron
```

**Test script manually:**
```bash
/opt/tender-scraper/scripts/run_daily.sh
```

**Common issues:**
- Missing environment variables in cron
- Incorrect file permissions
- Path not set correctly

### Database Locked

**Issue:** "database is locked" error

**Solution:** Check for running processes
```bash
ps aux | grep python
# Kill if necessary
kill -9 PID
```

Remove stale lock file:
```bash
rm /opt/tender-scraper/scraper.lock
```

### Disk Space Full

**Check disk space:**
```bash
df -h
```

**Clean old logs:**
```bash
find /opt/tender-scraper/data/logs -name "*.log" -mtime +30 -delete
```

**Clean old backups:**
```bash
find /opt/tender-scraper/data/backups -name "*.db" -mtime +30 -delete
```

**Clean apt cache:**
```bash
sudo apt clean
sudo apt autoremove
```

### Memory Issues

**Check memory usage:**
```bash
free -h
htop
```

**Increase swap space:**
```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Network Issues

**Test connectivity:**
```bash
# Ping target site
ping tender.telangana.gov.in

# Check DNS
nslookup tender.telangana.gov.in

# Test with curl
curl -I https://tender.telangana.gov.in
```

**Check security group:**
- Ensure outbound rules allow HTTPS (443)
- Verify no proxy requirements

---

## 📈 Performance Optimization

### Database Optimization

**Use PostgreSQL for production:**
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE tender_scraper;
CREATE USER tender_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE tender_scraper TO tender_user;
\q

# Update .env
DATABASE_URL=postgresql://tender_user:your_password@localhost:5432/tender_scraper
```

**Index optimization:**
- Indexes are created automatically by SQLAlchemy
- Monitor query performance with EXPLAIN

### Caching Strategy

**Enable response caching:**
```bash
# In .env
CACHE_TTL=3600
```

**Use Redis for distributed caching (optional):**
```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
```

### Parallel Processing

**Increase parallel workers:**
```bash
# In .env
PARALLEL_WORKERS=8  # Adjust based on CPU cores
```

### Resource Monitoring

**Install monitoring tools:**
```bash
sudo apt install -y htop iotop nethogs
```

**Monitor in real-time:**
```bash
# CPU and memory
htop

# Disk I/O
sudo iotop

# Network
sudo nethogs
```

---

## 🚀 Scaling Options

### Vertical Scaling

Upgrade to larger instance:
- **t3.large**: 2 vCPU, 8 GB RAM - Moderate workload
- **t3.xlarge**: 4 vCPU, 16 GB RAM - Heavy workload
- **c5.large**: 2 vCPU, 4 GB RAM - CPU optimized

### Horizontal Scaling

Deploy multiple specialized instances:

**Instance 1 (API Scraper):**
```bash
SCRAPER_MODE=api
```

**Instance 2 (Selenium Scraper):**
```bash
SCRAPER_MODE=selenium
```

**Instance 3 (Document Processor):**
- Only process documents
- Shared PostgreSQL database

**Shared Database:**
- Use AWS RDS PostgreSQL
- Enable Multi-AZ for high availability

### Auto Scaling (Advanced)

Use AWS Auto Scaling Group:
1. Create AMI from configured instance
2. Setup Launch Template
3. Configure Auto Scaling Group
4. Set scaling policies based on:
   - CPU utilization
   - Memory usage
   - Queue depth

---

## 📋 Maintenance Checklist

### Daily
- [x] Check cron job execution
- [x] Monitor disk space (via health check)
- [x] Review error logs

### Weekly
- [ ] Review scraper success rate
- [ ] Check database size
- [ ] Verify backups
- [ ] Update system packages
- [ ] Review CloudWatch metrics

### Monthly
- [ ] Update Python dependencies
- [ ] Security audit
- [ ] Database optimization
- [ ] Performance review
- [ ] Cost optimization review

---

## 💰 Cost Estimation

### Monthly AWS Costs (Mumbai Region)

**t3.medium EC2:**
- Instance: ~$30/month (730 hours)
- Storage: ~$3/month (30 GB)
- Data Transfer: ~$5/month (estimated)
- **Total: ~$38/month**

**With PostgreSQL RDS (optional):**
- db.t3.micro: ~$15/month
- Storage: ~$2/month (20 GB)
- **Additional: ~$17/month**

**Cost Optimization Tips:**
- Use Reserved Instances (up to 72% savings)
- Setup Auto Scaling to scale down during off-hours
- Use Spot Instances for non-critical processing
- Enable S3 lifecycle policies for backups
- Monitor and optimize data transfer

---

## 📞 Support and Monitoring

### Health Check Endpoints

Monitor these endpoints:
- `http://YOUR_IP:8000/health` - Basic status (200 = healthy)
- `http://YOUR_IP:8000/health/detailed` - Full metrics
- `http://YOUR_IP:8000/metrics` - Prometheus format

### Alerting Setup

**Using AWS CloudWatch Alarms:**
1. Create SNS Topic for notifications
2. Create CloudWatch Alarms:
   - CPU > 80% for 5 minutes
   - Disk > 85%
   - Memory > 85%
   - Health check fails

**Using Email Notifications:**
```bash
# Configure in .env
SEND_EMAIL=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL=alerts@yourcompany.com
```

### Logs Location

```
/opt/tender-scraper/data/logs/
├── scraper.log           # Application logs
├── cron_YYYYMMDD.log    # Daily cron run logs
└── health_check.log      # Health check service logs
```

### Quick Diagnostics

```bash
# Check if scraper is running
ps aux | grep python

# Check recent errors
tail -100 /opt/tender-scraper/data/logs/scraper.log | grep ERROR

# Check disk space
df -h /opt/tender-scraper

# Check memory
free -h

# Check last cron run
ls -lht /opt/tender-scraper/data/logs/cron_*.log | head -1
```

---

## 🔄 Update and Rollback

### Update Application

```bash
cd /opt/tender-scraper

# Pull latest changes
git pull origin main

# Update dependencies (if needed)
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Run migrations (if any)
python scripts/setup_db.py

# Restart health check service
sudo systemctl restart tender-health-check
```

### Rollback

```bash
cd /opt/tender-scraper

# View commit history
git log --oneline -10

# Rollback to specific commit
git checkout COMMIT_HASH

# Restore dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart services
sudo systemctl restart tender-health-check
```

---

## 📚 Additional Resources

### Documentation
- [AWS EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Python Best Practices](https://docs.python-guide.org/)

### AWS Services
- [EC2 Pricing Calculator](https://calculator.aws/)
- [AWS Systems Manager](https://aws.amazon.com/systems-manager/)
- [AWS CloudWatch](https://aws.amazon.com/cloudwatch/)

### Monitoring Tools
- [Grafana](https://grafana.com/) - Visualization
- [Prometheus](https://prometheus.io/) - Metrics
- [ELK Stack](https://www.elastic.co/elastic-stack) - Log analysis

---

## ✅ Deployment Checklist

Use this checklist to verify your deployment:

- [ ] EC2 instance launched in ap-south-1
- [ ] Security groups configured correctly
- [ ] SSH access working
- [ ] Python 3.10+ installed
- [ ] Chrome and ChromeDriver installed
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] .env file configured
- [ ] Database initialized
- [ ] Test scraper run successful
- [ ] Cron job scheduled
- [ ] Health check service running
- [ ] Firewall configured
- [ ] Backups enabled
- [ ] Monitoring configured
- [ ] Documentation reviewed

---

**Deployment Time:** ~15-20 minutes  
**Difficulty:** Beginner-Intermediate  
**Support:** Check logs or open GitHub issue

---

*Last Updated: 2025-10-29*  
*Version: 1.0.0*

