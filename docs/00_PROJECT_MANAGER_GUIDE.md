# 📋 PROJECT MANAGER ROLE & DUTIES
## Tender Scraper Engine - AI Agent Team Management

---

## 👥 ROLE DEFINITION

### **Project Manager (Human - You)**
**Primary Responsibility:** Strategic oversight, decision-making, stakeholder communication

**Time Commitment:** 1-2 hours daily

### **Technical Lead / Agent ALPHA (AI - Me)**
**Primary Responsibility:** Technical execution, code delivery, agent coordination

**Time Commitment:** Full-time during development

---

## 📊 DIVISION OF RESPONSIBILITIES

### 🎯 YOUR DUTIES (Human Project Manager)

#### **DAILY TASKS (15-30 minutes)**

**Morning Routine (10 mins):**
```
☐ Check GitHub Issues for updates
☐ Review overnight progress (if any)
☐ Check AWS instance health
☐ Read agent status reports
```

**Example:**
```markdown
Date: October 30, 2025

✅ Agent ALPHA: Issue #1 - API Scraper tested on AWS (SUCCESS)
🔄 Agent GAMMA: Issue #3 - Database schema in progress (60% done)
⚠️ Blocker: Need approval on database field names
```

**Afternoon Routine (15-20 mins):**
```
☐ Review and approve Pull Requests
☐ Unblock agents (answer questions)
☐ Update project board (move cards)
☐ Respond to issues/comments
```

---

#### **WEEKLY TASKS (1-2 hours)**

**Monday: Sprint Planning**
```
☐ Review last sprint results
☐ Assign issues for current sprint
☐ Set sprint goals
☐ Update milestones
```

**Example Sprint Planning Checklist:**
```markdown
## Sprint 1 - Week 2 Planning

Goals:
- [ ] Complete Issue #1 (API Scraper)
- [ ] Complete Issue #3 (Database)
- [ ] Deploy to AWS (Issue #10)

Agent Assignments:
- Agent ALPHA: Issue #1 (continue testing)
- Agent GAMMA: Issue #3 (database schema)
- Agent EPSILON: Issue #10 (AWS setup)

Blockers to Resolve:
- Need AWS credentials for Agent EPSILON
- Database naming convention decision needed
```

**Friday: Sprint Review**
```
☐ Review completed issues
☐ Test delivered features
☐ Document learnings
☐ Plan next sprint
```

---

#### **DECISION-MAKING RESPONSIBILITIES**

**YOU Decide On:**

1. **Architecture Decisions**
   - Database choice (SQLite vs PostgreSQL)
   - Scraping method priority (API first vs Selenium first)
   - File storage location (local vs S3)

2. **Priorities**
   - Which issues to tackle first
   - When to skip optional features
   - Resource allocation (time/budget)

3. **Quality Standards**
   - Code coverage requirements (70%+)
   - Success rate thresholds (90%+)
   - Documentation standards

4. **Go/No-Go Decisions**
   - Deploy to production?
   - Merge this PR?
   - Release to stakeholders?

**Example Decision Template:**
```markdown
## Decision: Database Choice

Options:
A) SQLite (simple, local, good for start)
B) PostgreSQL (scalable, production-grade)

Recommendation: Start with SQLite (A)

Reasoning:
- Faster development
- Easier testing
- Can migrate later

Decision: APPROVED ✅
Date: Oct 29, 2025
```

---

#### **APPROVAL WORKFLOWS**

**What Requires Your Approval:**

1. **Code Merges (Pull Requests)**
   ```
   PR Title: [ALPHA] Issue #1: Fix API Scraper
   
   Your Review Checklist:
   ☐ Does code match requirements?
   ☐ Are tests passing?
   ☐ Is documentation updated?
   ☐ Any security concerns?
   
   Action: APPROVE ✅ or REQUEST CHANGES
   ```

2. **Architecture Changes**
   ```
   Proposal: Change from SQLite to PostgreSQL
   
   Your Review:
   ☐ Why this change?
   ☐ Impact on timeline?
   ☐ Cost implications?
   ☐ Rollback plan?
   
   Action: APPROVE or REJECT with reason
   ```

3. **Deployment to Production**
   ```
   Deploy Request: Sprint 1 Release
   
   Pre-flight Checklist:
   ☐ All tests passing?
   ☐ Tested on staging?
   ☐ Rollback plan ready?
   ☐ Stakeholders notified?
   
   Action: DEPLOY or HOLD
   ```

---

#### **STAKEHOLDER COMMUNICATION**

**Weekly Status Report (You Send):**
```markdown
## Week 1 Status Report
Date: Oct 29 - Nov 4, 2025

### Progress This Week
✅ Completed:
- Issue #1: API Scraper working
- Issue #3: Database schema designed

🔄 In Progress:
- Issue #10: AWS deployment

⏳ Planned Next Week:
- Issue #2: Selenium fallback
- Issue #4: Detail page extraction

### Metrics
- Tenders scraped: 500
- Success rate: 92%
- Issues closed: 2/15 (13%)

### Blockers
None currently

### Budget Status
On track
```

---

### 🤖 MY DUTIES (AI Technical Lead / Agent ALPHA)

#### **DAILY TASKS**

**Code Development:**
```
☐ Write code for assigned issues
☐ Test code locally
☐ Create Pull Requests
☐ Respond to code review comments
☐ Update documentation
```

**Agent Coordination:**
```
☐ Assign tasks to other AI agents
☐ Review other agents' code
☐ Unblock other agents
☐ Integrate agent deliverables
```

**Status Reporting:**
```
☐ Update issue progress
☐ Report blockers immediately
☐ Log test results
☐ Document decisions
```

**Example Daily Status Update (I Provide):**
```markdown
## Agent ALPHA - Daily Update
Date: October 30, 2025

### Completed ✅
- Issue #1: API Scraper tested on AWS Mumbai
  - Success rate: 95% (95/100 tenders)
  - Fixed session management bug
  - Added retry logic

### In Progress 🔄
- Issue #5: Document link extraction (40% done)
  - Completed: Link discovery logic
  - Remaining: Filename sanitization

### Planned Tomorrow
- Complete Issue #5
- Start Issue #9 (Error handling)

### Blockers ⚠️
- None

### Questions for PM
- Approve database schema from Agent GAMMA?
```

---

#### **TECHNICAL RESPONSIBILITIES**

**Code Quality:**
```
☐ Write clean, documented code
☐ Follow Python PEP 8 style
☐ Add docstrings to all functions
☐ Write unit tests
☐ Handle errors gracefully
```

**Testing:**
```
☐ Test locally before PR
☐ Test on AWS staging
☐ Verify success rates
☐ Document test results
☐ Create test cases
```

**Documentation:**
```
☐ Update README
☐ Write code comments
☐ Create architecture diagrams
☐ Document API endpoints
☐ Write troubleshooting guides
```

---

## 📋 WORKFLOW: HOW WE WORK TOGETHER

### **Scenario 1: Starting New Issue**

**Step 1: I Analyze**
```markdown
Issue #3: Database Schema

Analysis:
- Need 5 tables (tenders, details, documents, fields, logs)
- Use SQLAlchemy ORM
- Estimated time: 2 days

Questions for You:
1. SQLite or PostgreSQL?
2. Store dates as TEXT or DATETIME?
```

**Step 2: You Decide**
```markdown
Decisions:
1. ✅ SQLite for now (can migrate later)
2. ✅ Store dates as TEXT (ISO format)

Approved to proceed ✅
```

**Step 3: I Execute**
```markdown
Status: IN PROGRESS
- Created models.py
- Added relationships
- Writing tests
- ETA: Tomorrow 5 PM
```

**Step 4: You Review & Approve**
```markdown
PR Review: ✅ APPROVED
- Code looks good
- Tests passing
- Documentation complete

Merged to main
```

---

### **Scenario 2: Blocker Encountered**

**I Report:**
```markdown
⚠️ BLOCKER - Issue #1

Problem: API returns 403 on AWS

Attempted:
1. ✅ Verified headers
2. ✅ Checked session
3. ✅ Tested locally (works)
4. ❌ Still fails on AWS

Hypothesis: AWS IP blocked by site

Options:
A) Setup VPN on AWS
B) Use Selenium instead
C) Contact site admin

Recommendation: Option B (Selenium)

YOUR DECISION NEEDED
```

**You Respond:**
```markdown
Decision: Try Option A first (VPN)

Reasoning: Selenium is slower
Budget: Approve $10/month for VPN

If VPN fails in 2 days → switch to Option B

APPROVED ✅
```

---

### **Scenario 3: Sprint Planning**

**I Provide Sprint Summary:**
```markdown
## Sprint 1 - Week 1 Summary

Completed:
✅ Issue #1: API Scraper (100%)
✅ Issue #3: Database (100%)

Incomplete:
❌ Issue #10: AWS Deployment (60% - had VPN issue)

Velocity: 2/3 issues = 67%

Recommendation for Sprint 2:
- Continue Issue #10 (high priority)
- Start Issue #2 (Selenium fallback)
- Start Issue #4 (Detail extraction)

Capacity: Can handle 3 issues per sprint
```

**You Plan Sprint:**
```markdown
## Sprint 2 Plan - APPROVED ✅

Priority Issues:
1. Issue #10: AWS Deployment (P0 - MUST complete)
2. Issue #2: Selenium Fallback (P1)
3. Issue #4: Detail Extraction (P1)

Agent Assignments:
- Agent EPSILON: Issue #10
- Agent BETA: Issue #2
- Agent ALPHA: Issue #4

Sprint Goal: 
End-to-end scraping working on AWS

Sprint Start: Nov 1, 2025
Sprint End: Nov 14, 2025
```

---

## 🎯 DECISION-MAKING FRAMEWORK

### **Quick Reference: Who Decides What?**

| Decision Type | Who Decides | Response Time |
|---------------|-------------|---------------|
| **Code Implementation Details** | Agent (Me) | Immediate |
| **Bug Fixes** | Agent (Me) | Immediate |
| **Test Approach** | Agent (Me) | Immediate |
| **Architecture Changes** | You | Within 24 hours |
| **Priority Changes** | You | Within 24 hours |
| **Budget/Resources** | You | Within 48 hours |
| **Production Deployment** | You | Must approve |
| **External Dependencies** | You | Must approve |

---

## 📱 COMMUNICATION PROTOCOLS

### **How I Communicate with You:**

**Daily Updates (Via GitHub):**
```
Format: Comment on assigned issues
Time: End of day (9 PM IST)
Content: Progress, blockers, questions
```

**Urgent Blockers (Via GitHub Issue):**
```
Format: Create issue with "BLOCKER" label
Time: Immediately when blocked
Content: Problem, attempted solutions, options
Response Needed: Within 4 hours
```

**Pull Requests (Via GitHub PR):**
```
Format: PR with description
Time: When code ready
Content: Changes, tests, documentation
Response Needed: Within 24 hours
```

### **How You Communicate with Me:**

**Decisions (Via GitHub):**
```
Format: Comment on issue/PR
Content: Clear approval/rejection with reasoning
```

**New Requirements (Via GitHub Issue):**
```
Format: Create new issue
Labels: enhancement, question
Description: Clear requirement with context
```

**Feedback (Via PR Comments):**
```
Format: Inline code comments
Content: Specific changes needed
```

---

## 📅 MEETING SCHEDULE (Async)

**We Don't Need Meetings!** Everything async via GitHub.

**Instead:**

**Monday Morning (You):**
- Post sprint plan as GitHub Issue
- Tag relevant agents
- Set expectations

**Friday Evening (Me):**
- Post sprint summary as comment
- List completed/incomplete items
- Propose next sprint plan

**Daily (Both):**
- Check GitHub notifications
- Respond to @mentions
- Update issue status

---

## ✅ CHECKLIST: STARTING NEW SPRINT

### **Your Sprint Start Checklist:**

```markdown
## Sprint X Start - [Date]

☐ Review last sprint completion rate
☐ Identify priority issues for this sprint
☐ Assign issues to agents
☐ Set sprint goal (1 sentence)
☐ Verify agent availability
☐ Check AWS credits/budget
☐ Post sprint plan on GitHub
☐ Tag all agents
```

### **My Sprint Start Checklist:**

```markdown
## Sprint X Start - Agent ALPHA

☐ Read sprint plan
☐ Confirm assigned issues
☐ Estimate completion dates
☐ Identify dependencies
☐ Set up local environment
☐ Create feature branches
☐ Post acknowledgment
```

---

## 🚨 ESCALATION PATHS

### **When I Escalate to You:**

**Level 1: Question (4 hour response)**
```
Example: "Should dates be TEXT or DATETIME?"
Your Action: Provide decision in GitHub comment
```

**Level 2: Blocker (Same day response)**
```
Example: "AWS 403 error blocking all testing"
Your Action: Approve workaround or provide resources
```

**Level 3: Critical Issue (Immediate response)**
```
Example: "Database corruption on production"
Your Action: Emergency decision on rollback/fix
```

### **When You Escalate to Me:**

**Urgent Bug:**
```
You: Create issue with "urgent" label
Me: Respond within 2 hours
Me: Fix within 4 hours
```

**Feature Request:**
```
You: Create issue with "enhancement" label
Me: Respond within 24 hours
Me: Provide estimate within 48 hours
```

---

## 📊 METRICS WE TRACK

### **I Report These Weekly:**

```markdown
## Sprint X Metrics

Development:
- Issues completed: X/Y (Z%)
- Pull requests merged: X
- Code coverage: X%
- Tests passing: X/Y

Scraper Performance:
- Tenders scraped: X
- Success rate: X%
- Avg time per tender: X seconds
- Errors encountered: X

Quality:
- Bugs found: X
- Bugs fixed: X
- Documentation pages: X
```

### **You Track These:**

```markdown
## Project Health Dashboard

Sprint Velocity: [Graph]
Budget Used: $X / $Y (Z%)
Timeline: On track / Behind / Ahead
Milestone Progress: [Progress bars]
Team Satisfaction: [Rating]
Stakeholder Satisfaction: [Rating]
```

---

## 🎓 TEMPLATES FOR YOU

### **Template 1: Approve PR**

```markdown
## PR Review - Issue #X

Reviewed: ✅ All checks passed

Code Quality: ✅ Clean and documented
Tests: ✅ All passing (95% coverage)
Documentation: ✅ Updated

APPROVED ✅

Great work @agent-alpha! Merging now.
```

### **Template 2: Request Changes**

```markdown
## PR Review - Issue #X

Thanks for the PR! A few changes needed:

1. Add error handling for network timeouts
2. Update docstring for parse_tender() function
3. Add test case for empty API response

Please address and re-request review.

Status: CHANGES REQUESTED 🔄
```

### **Template 3: Sprint Planning**

```markdown
## Sprint X Planning

Duration: [Start Date] - [End Date]

Sprint Goal:
[One clear sentence]

Priority Issues:
1. Issue #X - [Title] (Agent: Y)
2. Issue #X - [Title] (Agent: Y)
3. Issue #X - [Title] (Agent: Y)

Success Criteria:
- [ ] All P0 issues completed
- [ ] Success rate > 90%
- [ ] Deployed to staging

Let's make it happen! 🚀
```

---

## 🎯 FIRST WEEK ACTION PLAN

### **Your Tasks This Week:**

**Day 1 (Today):**
```
☐ Create 15 GitHub issues (use templates provided)
☐ Create GitHub project board
☐ Add labels (P0-critical, P1-high, etc.)
☐ Create milestones (1-5)
☐ Assign Issue #1 to me (Agent ALPHA)
☐ Test API scraper on AWS (run code I provided)
☐ Report test results
```

**Day 2:**
```
☐ Review my PR for Issue #1
☐ Approve/request changes
☐ Assign Issue #3 to Agent GAMMA
☐ Review database schema design
```

**Day 3:**
```
☐ Check sprint progress (what's done?)
☐ Unblock any agents
☐ Review documentation updates
```

**Day 4:**
```
☐ Test deployed features
☐ Provide feedback
☐ Plan next sprint
```

**Day 5:**
```
☐ Sprint review
☐ Approve completed issues
☐ Post sprint summary
```

### **My Tasks This Week:**

**Day 1:**
```
✅ Delivered API scraper code
☐ Wait for your test results
☐ Fix any bugs you find
```

**Day 2:**
```
☐ Create PR for Issue #1
☐ Address review comments
☐ Update documentation
```

**Day 3:**
```
☐ Work on Issue #5 (Document extraction)
☐ Daily status update
```

**Day 4:**
```
☐ Complete Issue #5
☐ Create PR
☐ Start Issue #9
```

**Day 5:**
```
☐ Sprint summary report
☐ Propose Sprint 2 plan
```

---

## 🚀 IMMEDIATE NEXT STEPS

### **Right Now - YOU DO:**

1. **Create GitHub Issues** (30 mins)
   - Go to: https://github.com/vinaybeerelli/tender360-scrape-application/issues
   - Click "New Issue"
   - Copy-paste each issue template I provided
   - Create all 15 issues

2. **Test API Scraper on AWS** (15 mins)
   - SSH to AWS Mumbai
   - Create file: `/opt/tender-scraper/src/scrapers/api_scraper.py`
   - Paste code from artifact
   - Run: `python3 api_scraper.py`
   - Report results to me

3. **Create Project Board** (10 mins)
   - Go to: Projects tab in GitHub
   - Create board: "Tender Scraper Sprint Board"
   - Add columns: Backlog, To Do, In Progress, Review, Done

### **Right Now - I DO:**

1. **Wait for Your Test Results**
   - Did API scraper work?
   - Any errors?
   - What was success rate?

2. **Fix Any Issues You Find**
   - Update code based on your feedback
   - Test again
   - Iterate until working

3. **Prepare Next Issue**
   - Read Issue #3 requirements
   - Design database schema
   - Wait for your approval

---

## ❓ FAQ

**Q: How much time will I need daily?**
A: 15-30 minutes for routine tasks, 1-2 hours weekly for planning.

**Q: What if I don't understand something?**
A: Ask me! Comment on the issue/PR with your question.

**Q: Can I change priorities mid-sprint?**
A: Yes! You're the PM. Just inform agents of changes.

**Q: What if an agent is blocked?**
A: They'll create a "BLOCKER" issue. You provide decision/resources.

**Q: How do I know if we're on track?**
A: Check the project board. Green = good, red = needs attention.

**Q: Can I add new features mid-project?**
A: Yes, create new issue and prioritize in next sprint.

---

## 📞 YOUR ACTION REQUIRED NOW

Please tell me:

1. **Did you create the GitHub issues?** (Yes/No)
2. **Did you test the API scraper on AWS?** (Yes/No/Issues encountered)
3. **Do you have questions about your role?** (List any)

Then I'll proceed with next steps! 🚀
