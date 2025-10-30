#!/bin/bash
##############################################################################
# AWS EC2 Deployment Script for Tender Scraper Engine
#
# This script automates the deployment of the tender scraper on AWS EC2
# Ubuntu 22.04 instance in Mumbai region (ap-south-1)
#
# Usage:
#   sudo ./scripts/deploy.sh
#
# Prerequisites:
#   - Fresh Ubuntu 22.04 EC2 instance
#   - Run as root or with sudo
##############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/tender-scraper"
APP_USER="ubuntu"
PYTHON_VERSION="3.10"
REPO_URL="https://github.com/vinaybeerelli/tender360-data-engine.git"

##############################################################################
# Utility Functions
##############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
}

##############################################################################
# System Setup
##############################################################################

update_system() {
    log_info "Updating system packages..."
    apt update -y
    apt upgrade -y
    log_success "System updated"
}

install_python() {
    log_info "Installing Python ${PYTHON_VERSION}..."
    apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python3-pip
    
    # Verify installation
    python${PYTHON_VERSION} --version
    log_success "Python ${PYTHON_VERSION} installed"
}

install_chrome() {
    log_info "Installing Google Chrome..."
    
    # Download and install Chrome
    cd /tmp
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    apt install -y ./google-chrome-stable_current_amd64.deb
    
    # Verify installation
    google-chrome --version
    log_success "Google Chrome installed"
}

install_chromedriver() {
    log_info "Installing ChromeDriver..."
    
    # Get Chrome version
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1)
    log_info "Chrome version: ${CHROME_VERSION}"
    
    # Install ChromeDriver via apt (Ubuntu 22.04 has chromium-chromedriver)
    apt install -y chromium-chromedriver
    
    # Create symlink if needed
    if [ ! -f /usr/local/bin/chromedriver ]; then
        ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver 2>/dev/null || true
    fi
    
    # Verify installation
    chromedriver --version 2>/dev/null || log_warning "ChromeDriver version check failed, but may still work"
    log_success "ChromeDriver installed"
}

install_dependencies() {
    log_info "Installing system dependencies..."
    apt install -y \
        git \
        curl \
        wget \
        unzip \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        sqlite3 \
        xvfb \
        libxi6 \
        libgconf-2-4 \
        libnss3 \
        libxss1 \
        libasound2 \
        fonts-liberation \
        libappindicator3-1 \
        libgbm1
    
    log_success "System dependencies installed"
}

configure_shm() {
    log_info "Configuring shared memory for Chrome..."
    
    # Increase shared memory size
    mount -o remount,size=2G /dev/shm || log_warning "Could not remount /dev/shm"
    
    # Make persistent
    if ! grep -q "/dev/shm" /etc/fstab; then
        echo "tmpfs /dev/shm tmpfs defaults,size=2G 0 0" >> /etc/fstab
        log_success "Shared memory configured (persistent)"
    else
        log_info "Shared memory already configured in /etc/fstab"
    fi
}

##############################################################################
# Application Deployment
##############################################################################

create_app_directory() {
    log_info "Creating application directory..."
    mkdir -p "$APP_DIR"
    chown "$APP_USER:$APP_USER" "$APP_DIR"
    log_success "Application directory created: $APP_DIR"
}

clone_repository() {
    log_info "Cloning repository..."
    
    if [ -d "$APP_DIR/.git" ]; then
        log_warning "Repository already exists. Pulling latest changes..."
        cd "$APP_DIR"
        sudo -u "$APP_USER" git pull
    else
        sudo -u "$APP_USER" git clone "$REPO_URL" "$APP_DIR"
    fi
    
    cd "$APP_DIR"
    log_success "Repository cloned/updated"
}

setup_virtualenv() {
    log_info "Setting up Python virtual environment..."
    cd "$APP_DIR"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        sudo -u "$APP_USER" python${PYTHON_VERSION} -m venv venv
    fi
    
    # Activate and upgrade pip
    sudo -u "$APP_USER" bash -c "source venv/bin/activate && pip install --upgrade pip setuptools wheel"
    
    log_success "Virtual environment created"
}

install_python_dependencies() {
    log_info "Installing Python dependencies..."
    cd "$APP_DIR"
    
    sudo -u "$APP_USER" bash -c "source venv/bin/activate && pip install -r requirements.txt"
    
    log_success "Python dependencies installed"
}

setup_environment() {
    log_info "Setting up environment configuration..."
    cd "$APP_DIR"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            sudo -u "$APP_USER" cp .env.example .env
            log_warning "Created .env from .env.example. Please edit with your settings."
        else
            # Create basic .env file
            sudo -u "$APP_USER" cat > .env << 'EOF'
# Database
DATABASE_URL=sqlite:///data/tender_scraper.db

# Scraper Configuration
BASE_URL=https://tender.telangana.gov.in
SCRAPER_MODE=api
HEADLESS=true

# Rate Limiting
MIN_DELAY=2
MAX_DELAY=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/scraper.log

# AWS Configuration
AWS_REGION=ap-south-1

# Monitoring
HEALTH_CHECK_PORT=8000
EOF
            log_warning "Created basic .env file. Please review and update settings."
        fi
    else
        log_info ".env file already exists"
    fi
    
    log_success "Environment configuration ready"
}

initialize_database() {
    log_info "Initializing database..."
    cd "$APP_DIR"
    
    sudo -u "$APP_USER" bash -c "source venv/bin/activate && python scripts/setup_db.py"
    
    log_success "Database initialized"
}

create_data_directories() {
    log_info "Creating data directories..."
    cd "$APP_DIR"
    
    sudo -u "$APP_USER" mkdir -p data/{logs,downloads,backups}
    sudo -u "$APP_USER" touch data/logs/.gitkeep data/downloads/.gitkeep data/backups/.gitkeep
    
    log_success "Data directories created"
}

##############################################################################
# Security Configuration
##############################################################################

configure_firewall() {
    log_info "Configuring firewall (UFW)..."
    
    # Install UFW if not present
    apt install -y ufw
    
    # Configure rules
    ufw --force enable
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 8000/tcp comment "Health check endpoint"
    
    log_success "Firewall configured"
}

set_permissions() {
    log_info "Setting file permissions..."
    cd "$APP_DIR"
    
    # Set ownership
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    
    # Make scripts executable
    chmod +x scripts/*.sh 2>/dev/null || true
    
    # Secure .env file
    chmod 600 .env 2>/dev/null || true
    
    log_success "Permissions configured"
}

##############################################################################
# Testing
##############################################################################

test_deployment() {
    log_info "Testing deployment..."
    cd "$APP_DIR"
    
    # Test Python import
    log_info "Testing Python imports..."
    sudo -u "$APP_USER" bash -c "source venv/bin/activate && python -c 'import requests, selenium, bs4; print(\"✓ Core dependencies OK\")'"
    
    # Test Chrome
    log_info "Testing Chrome..."
    google-chrome --version
    
    # Test database
    log_info "Testing database..."
    sudo -u "$APP_USER" bash -c "source venv/bin/activate && python -c 'from src.database.connection import get_db; next(get_db()); print(\"✓ Database OK\")'"
    
    log_success "All tests passed"
}

##############################################################################
# Deployment Summary
##############################################################################

print_summary() {
    echo ""
    echo "=========================================================================="
    echo -e "${GREEN}DEPLOYMENT COMPLETED SUCCESSFULLY${NC}"
    echo "=========================================================================="
    echo ""
    echo "Application Details:"
    echo "  Location: $APP_DIR"
    echo "  User: $APP_USER"
    echo "  Python: $(python${PYTHON_VERSION} --version)"
    echo "  Chrome: $(google-chrome --version)"
    echo ""
    echo "Next Steps:"
    echo "  1. Review and update configuration:"
    echo "     sudo nano $APP_DIR/.env"
    echo ""
    echo "  2. Test the scraper:"
    echo "     cd $APP_DIR"
    echo "     source venv/bin/activate"
    echo "     python main.py --limit 5 --verbose"
    echo ""
    echo "  3. Setup cron job for daily runs:"
    echo "     crontab -e -u $APP_USER"
    echo "     Add: 0 9 * * * $APP_DIR/scripts/run_daily.sh"
    echo ""
    echo "  4. Start health check service:"
    echo "     cd $APP_DIR"
    echo "     source venv/bin/activate"
    echo "     nohup python scripts/health_check.py &"
    echo ""
    echo "=========================================================================="
}

##############################################################################
# Main Execution
##############################################################################

main() {
    log_info "Starting AWS EC2 deployment..."
    log_info "Target: Ubuntu 22.04 on AWS Mumbai (ap-south-1)"
    echo ""
    
    check_root
    
    # System setup
    update_system
    install_dependencies
    install_python
    install_chrome
    install_chromedriver
    configure_shm
    
    # Application deployment
    create_app_directory
    clone_repository
    create_data_directories
    setup_virtualenv
    install_python_dependencies
    setup_environment
    initialize_database
    
    # Security
    configure_firewall
    set_permissions
    
    # Testing
    test_deployment
    
    # Summary
    print_summary
}

# Run main function
main
