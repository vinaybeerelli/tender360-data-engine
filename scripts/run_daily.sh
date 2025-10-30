#!/bin/bash
##############################################################################
# Daily Cron Job Script for Tender Scraper Engine
#
# This script runs the tender scraper daily and handles logging and notifications
#
# Usage:
#   ./scripts/run_daily.sh
#
# Cron Setup (run at 9 AM IST daily):
#   0 9 * * * /opt/tender-scraper/scripts/run_daily.sh
##############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
APP_DIR="/opt/tender-scraper"
LOG_DIR="$APP_DIR/data/logs"
DATE=$(date +%Y%m%d)
TIMESTAMP=$(date +%Y-%m-%d\ %H:%M:%S)
LOG_FILE="$LOG_DIR/cron_${DATE}.log"
LOCK_FILE="$APP_DIR/scraper.lock"

# Email notification (set in .env if needed)
SEND_EMAIL=${SEND_EMAIL:-false}

##############################################################################
# Utility Functions
##############################################################################

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$TIMESTAMP] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

send_notification() {
    local subject="$1"
    local message="$2"
    
    if [ "$SEND_EMAIL" = "true" ]; then
        # Use Python script to send email (requires SMTP settings in .env)
        cd "$APP_DIR"
        source venv/bin/activate
        python -c "
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
smtp_port = int(os.getenv('SMTP_PORT', '587'))
smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')
alert_email = os.getenv('ALERT_EMAIL')

if smtp_user and smtp_password and alert_email:
    msg = MIMEText('$message')
    msg['Subject'] = '$subject'
    msg['From'] = smtp_user
    msg['To'] = alert_email
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print('Email notification sent')
    except Exception as e:
        print(f'Failed to send email: {e}')
else:
    print('Email settings not configured')
" 2>&1 | tee -a "$LOG_FILE"
    else
        log "Email notifications disabled"
    fi
}

check_lock() {
    if [ -f "$LOCK_FILE" ]; then
        log_error "Previous scraper process still running (lock file exists)"
        log_error "Lock file: $LOCK_FILE"
        
        # Check if process is actually running
        if [ -s "$LOCK_FILE" ]; then
            PID=$(cat "$LOCK_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                log_error "Process $PID is still running. Aborting."
                exit 1
            else
                log "Lock file exists but process is dead. Removing stale lock."
                rm -f "$LOCK_FILE"
            fi
        else
            log "Empty lock file found. Removing."
            rm -f "$LOCK_FILE"
        fi
    fi
}

create_lock() {
    echo $$ > "$LOCK_FILE"
    log "Created lock file with PID: $$"
}

remove_lock() {
    rm -f "$LOCK_FILE"
    log "Removed lock file"
}

cleanup() {
    remove_lock
    log "Cleanup completed"
}

##############################################################################
# Pre-run Checks
##############################################################################

check_environment() {
    log "Checking environment..."
    
    # Check if app directory exists
    if [ ! -d "$APP_DIR" ]; then
        log_error "Application directory not found: $APP_DIR"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$APP_DIR/venv" ]; then
        log_error "Virtual environment not found: $APP_DIR/venv"
        exit 1
    fi
    
    # Check if main.py exists
    if [ ! -f "$APP_DIR/main.py" ]; then
        log_error "main.py not found: $APP_DIR/main.py"
        exit 1
    fi
    
    # Create log directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    
    log "Environment checks passed"
}

check_disk_space() {
    log "Checking disk space..."
    
    DISK_USAGE=$(df -h "$APP_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$DISK_USAGE" -gt 90 ]; then
        log_error "Disk usage is above 90%: ${DISK_USAGE}%"
        
        # Clean old logs
        log "Cleaning old log files (older than 30 days)..."
        find "$LOG_DIR" -name "*.log" -mtime +30 -delete
        
        # Clean old backups
        log "Cleaning old backups (older than 30 days)..."
        find "$APP_DIR/data/backups" -name "*.db" -mtime +30 -delete 2>/dev/null || true
        
        DISK_USAGE_AFTER=$(df -h "$APP_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
        log "Disk usage after cleanup: ${DISK_USAGE_AFTER}%"
    else
        log "Disk usage: ${DISK_USAGE}% (OK)"
    fi
}

##############################################################################
# Scraper Execution
##############################################################################

run_scraper() {
    log "=========================================================================="
    log "STARTING DAILY SCRAPER RUN"
    log "=========================================================================="
    log "Date: $DATE"
    log "Time: $TIMESTAMP"
    log "Log file: $LOG_FILE"
    log ""
    
    # Change to app directory
    cd "$APP_DIR"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run scraper in hybrid mode (try API first, fallback to Selenium)
    log "Running scraper in hybrid mode..."
    START_TIME=$(date +%s)
    
    if python main.py --mode hybrid >> "$LOG_FILE" 2>&1; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        MINUTES=$((DURATION / 60))
        SECONDS=$((DURATION % 60))
        
        log ""
        log "=========================================================================="
        log "SCRAPER COMPLETED SUCCESSFULLY"
        log "=========================================================================="
        log "Duration: ${MINUTES}m ${SECONDS}s"
        log ""
        
        # Send success notification
        send_notification \
            "Tender Scraper - Daily Run Success" \
            "Scraper completed successfully on $DATE\nDuration: ${MINUTES}m ${SECONDS}s\nLog: $LOG_FILE"
        
        return 0
    else
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        MINUTES=$((DURATION / 60))
        SECONDS=$((DURATION % 60))
        
        log_error ""
        log_error "=========================================================================="
        log_error "SCRAPER FAILED"
        log_error "=========================================================================="
        log_error "Duration: ${MINUTES}m ${SECONDS}s"
        log_error "Check log file for details: $LOG_FILE"
        log_error ""
        
        # Send failure notification
        send_notification \
            "Tender Scraper - Daily Run FAILED" \
            "Scraper failed on $DATE\nDuration: ${MINUTES}m ${SECONDS}s\nLog: $LOG_FILE\nPlease check the logs for details."
        
        return 1
    fi
}

##############################################################################
# Post-run Tasks
##############################################################################

backup_database() {
    log "Creating database backup..."
    
    BACKUP_DIR="$APP_DIR/data/backups"
    mkdir -p "$BACKUP_DIR"
    
    DB_FILE="$APP_DIR/data/tender_scraper.db"
    if [ -f "$DB_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/tender_scraper_${DATE}_$(date +%H%M%S).db"
        cp "$DB_FILE" "$BACKUP_FILE"
        log "Database backed up to: $BACKUP_FILE"
        
        # Keep only last 7 days of backups
        find "$BACKUP_DIR" -name "tender_scraper_*.db" -mtime +7 -delete
        log "Old backups cleaned (kept last 7 days)"
    else
        log "Database file not found: $DB_FILE"
    fi
}

generate_summary() {
    log "Generating summary..."
    
    cd "$APP_DIR"
    source venv/bin/activate
    
    # Generate summary using Python
    python -c "
import sqlite3
import os
from datetime import datetime, timedelta

db_path = 'data/tender_scraper.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total tenders
    cursor.execute('SELECT COUNT(*) FROM tenders')
    total = cursor.fetchone()[0]
    
    # Today's tenders
    today = datetime.now().date().isoformat()
    cursor.execute('SELECT COUNT(*) FROM tenders WHERE DATE(created_at) = ?', (today,))
    today_count = cursor.fetchone()[0]
    
    # Last 7 days
    week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
    cursor.execute('SELECT COUNT(*) FROM tenders WHERE DATE(created_at) >= ?', (week_ago,))
    week_count = cursor.fetchone()[0]
    
    print(f'Total tenders in database: {total}')
    print(f'Tenders added today: {today_count}')
    print(f'Tenders added last 7 days: {week_count}')
    
    conn.close()
else:
    print('Database not found')
" 2>&1 | tee -a "$LOG_FILE"
}

##############################################################################
# Main Execution
##############################################################################

main() {
    # Setup cleanup trap
    trap cleanup EXIT INT TERM
    
    # Pre-run checks
    check_environment
    check_disk_space
    check_lock
    
    # Create lock file
    create_lock
    
    # Run scraper
    if run_scraper; then
        # Post-run tasks
        backup_database
        generate_summary
        exit 0
    else
        log_error "Scraper run failed"
        exit 1
    fi
}

# Run main function
main
