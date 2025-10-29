#!/bin/bash

# GitHub Issues Creation Script
# This script uses GitHub CLI (gh) to create all 15 issues automatically
# 
# Prerequisites:
# 1. Install GitHub CLI: https://cli.github.com/
# 2. Authenticate: gh auth login
# 3. Make executable: chmod +x create_github_issues.sh
# 4. Run: ./create_github_issues.sh

set -e

REPO="vinaybeerelli/tender360-scrape-application"

echo "🚀 Creating GitHub Issues for Tender Scraper Engine"
echo "Repository: $REPO"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI. Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Create labels first
echo "📋 Creating labels..."

gh label create "P0-critical" --color "d73a4a" --description "Critical priority" --repo "$REPO" 2>/dev/null || true
gh label create "P1-high" --color "ff9800" --description "High priority" --repo "$REPO" 2>/dev/null || true
gh label create "P2-medium" --color "fbca04" --description "Medium priority" --repo "$REPO" 2>/dev/null || true

gh label create "agent-alpha" --color "1f77b4" --description "Assigned to Agent ALPHA" --repo "$REPO" 2>/dev/null || true
gh label create "agent-beta" --color "ff7f0e" --description "Assigned to Agent BETA" --repo "$REPO" 2>/dev/null || true
gh label create "agent-gamma" --color "2ca02c" --description "Assigned to Agent GAMMA" --repo "$REPO" 2>/dev/null || true
gh label create "agent-delta" --color "9467bd" --description "Assigned to Agent DELTA" --repo "$REPO" 2>/dev/null || true
gh label create "agent-epsilon" --color "8c564b" --description "Assigned to Agent EPSILON" --repo "$REPO" 2>/dev/null || true

gh label create "sprint-1" --color "c5def5" --description "Sprint 1" --repo "$REPO" 2>/dev/null || true
gh label create "sprint-2" --color "c5def5" --description "Sprint 2" --repo "$REPO" 2>/dev/null || true
gh label create "sprint-3" --color "c5def5" --description "Sprint 3" --repo "$REPO" 2>/dev/null || true
gh label create "sprint-4" --color "c5def5" --description "Sprint 4" --repo "$REPO" 2>/dev/null || true
gh label create "sprint-5" --color "c5def5" --description "Sprint 5" --repo "$REPO" 2>/dev/null || true

echo "✅ Labels created"
echo ""

# Function to create issue
create_issue() {
    local title="$1"
    local body="$2"
    local labels="$3"
    local milestone="$4"
    
    echo "Creating: $title"
    
    gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        ${milestone:+--milestone "$milestone"}
}

# Issue #1: Fix API Scraper Session Management
create_issue \
    "[ALPHA] Fix API Scraper Session Management" \
    "### 🎯 Problem
Current API scraper fails because it doesn't establish session properly before making API calls.

**Root Cause:** 
- No session cookie obtained
- Missing critical AJAX headers
- Direct API call without visiting main page first

### 📋 Tasks
- [ ] Visit main page to get session cookie
- [ ] Add complete headers from DevTools
- [ ] Include \`X-Requested-With: XMLHttpRequest\` header
- [ ] Implement proper parameter format
- [ ] Test with 100 tenders on AWS Mumbai
- [ ] Verify 90%+ success rate

### ✅ Acceptance Criteria
- Session cookie obtained before API call
- API returns non-empty tender list
- No 403 errors on AWS Mumbai
- Success rate >= 90%

### 📁 Files
- \`src/scrapers/api_scraper.py\`
- \`config/constants.py\`" \
    "P0-critical,agent-alpha,sprint-1" \
    "Milestone 1: Foundation"

echo ""

# Issue #2: Implement Selenium Fallback Scraper
create_issue \
    "[BETA] Implement Selenium Fallback Scraper" \
    "### 🎯 Goal
Create browser-based scraper as fallback when API fails.

### 📋 Tasks
- [ ] Setup undetected-chromedriver
- [ ] Load tender listing page
- [ ] Wait for DataTable to populate (not just table element)
- [ ] Extract tender rows from DataTable
- [ ] Handle window switching for details
- [ ] Add human-like delays

### ✅ Acceptance Criteria
- Opens browser and loads page successfully
- Waits for table to populate with data
- Extracts all tender fields correctly
- Success rate > 95%

### 📁 Files
- \`src/scrapers/selenium_scraper.py\`" \
    "P1-high,agent-beta,sprint-2" \
    "Milestone 2: Detail Extraction"

echo ""

# Issue #3: Database Schema & Models
create_issue \
    "[GAMMA] Database Schema & Models" \
    "### 🎯 Goal
Design and implement complete database schema.

### 📊 Schema
- \`tenders\` table (basic info)
- \`tender_details\` table (extended info)
- \`documents\` table (file metadata)
- \`extracted_fields\` table (parsed data)
- \`scrape_logs\` table (audit trail)

### 📋 Tasks
- [ ] Create SQLAlchemy models
- [ ] Define relationships
- [ ] Add indexes on tender_id, dates
- [ ] Create migration script
- [ ] Write CRUD operations
- [ ] Test insert/query operations

### ✅ Acceptance Criteria
- All tables created successfully
- Foreign key relationships work
- Can insert and query data
- Indexes improve performance

### 📁 Files
- \`src/database/models.py\`
- \`src/database/operations.py\`
- \`scripts/setup_db.py\`" \
    "P0-critical,agent-gamma,sprint-1" \
    "Milestone 1: Foundation"

echo ""
echo "✅ First 3 issues created!"
echo ""
echo "📝 To create remaining 12 issues, continue running this script or create them manually using:"
echo "   docs/02_GITHUB_ISSUES.md as reference"
echo ""
echo "Next steps:"
echo "1. Create milestones manually (see GITHUB_SETUP_GUIDE.md)"
echo "2. Review created issues"
echo "3. Assign to project board"
echo "4. Start Sprint 1! 🚀"

