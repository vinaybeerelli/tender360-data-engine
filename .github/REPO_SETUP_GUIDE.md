# GitHub Repository Setup Guide
## Complete Configuration for tender360-data-engine

---

## 🎯 Overview

This guide walks you through setting up your GitHub repository with:
- ✅ Automated security scanning (non-blocking)
- ✅ Dependency management (Dependabot)
- ✅ CI/CD pipelines
- ✅ Flexible branch protection
- ✅ Code ownership structure
- ✅ Issue and PR templates

---

## 📋 Quick Setup Checklist

### Phase 1: Enable GitHub Features (5 minutes)

1. **Enable Dependabot**
   - Go to: `Settings` → `Code security and analysis`
   - Enable: "Dependabot alerts"
   - Enable: "Dependabot security updates"
   - Dependabot version updates are already configured via `.github/dependabot.yml`

2. **Enable CodeQL Scanning**
   - Go to: `Settings` → `Code security and analysis`
   - Enable: "CodeQL analysis"
   - The workflow is already in `.github/workflows/codeql.yml`

3. **Enable Secret Scanning**
   - Go to: `Settings` → `Code security and analysis`
   - Enable: "Secret scanning"
   - Enable: "Push protection"

4. **Enable Discussions (Optional)**
   - Go to: `Settings` → `General`
   - Under "Features", enable: "Discussions"

### Phase 2: Configure Branch Protection (10 minutes)

See detailed instructions in `.github/BRANCH_PROTECTION_GUIDE.md`

**Recommended Minimal Setup:**

1. Go to: `Settings` → `Branches` → `Add rule`
2. Branch name pattern: `main`
3. Configure:
   ```
   ☐ Require a pull request before merging (DISABLED for solo dev)
   ☑ Require status checks to pass (OPTIONAL, not blocking)
       Status checks: CI Pipeline, CodeQL
   ☐ Include administrators (DISABLED so you can bypass)
   ☑ Allow force pushes (For admins only)
   ☐ Allow deletions (DISABLED)
   ```
4. Click "Create"

**Result:** You can push directly to main, CI runs but doesn't block, security scans in background.

### Phase 3: Set Up GitHub Actions Secrets (5 minutes)

If you need environment variables for CI/CD:

1. Go to: `Settings` → `Secrets and variables` → `Actions`
2. Click: `New repository secret`
3. Add secrets as needed:
   ```
   AWS_ACCESS_KEY_ID (if using AWS in CI)
   AWS_SECRET_ACCESS_KEY (if using AWS in CI)
   DATABASE_URL (for integration tests)
   ```

**Note:** For security, use GitHub Environments for production secrets.

### Phase 4: Configure Issue Labels (5 minutes)

Create/update labels for better organization:

```
bug - Red - Something isn't working
enhancement - Green - New feature or request
documentation - Blue - Documentation updates
agent-task - Purple - Task for AI agents
dependencies - Yellow - Dependency updates
python - Orange - Python related
github-actions - Dark Blue - CI/CD related
security - Red - Security related
P0 - Dark Red - Critical priority
P1 - Orange - High priority
P2 - Yellow - Medium priority
```

Create via:
- UI: `Issues` → `Labels` → `New label`
- CLI: `gh label create "label-name" --color "hexcode" --description "description"`

---

## 🤖 Copilot Agent Configuration

### GitHub Copilot Features to Enable

1. **Copilot in CLI** (for terminal assistance)
   ```bash
   gh extension install github/gh-copilot
   gh copilot --help
   ```

2. **Copilot in PRs** (for PR descriptions)
   - Already works automatically with Copilot subscription

3. **Copilot in Issues** (for issue templates)
   - Use templates in `.github/ISSUE_TEMPLATE/`

### Agent Workspace Setup

Each agent should have access to:
- `.github/agents/<agent-name>.md` - Agent instructions
- `.github/agents/WORKFLOW_GUIDE.md` - Development workflow
- `.github/SECURITY.md` - Security guidelines
- `.github/BRANCH_PROTECTION_GUIDE.md` - Git workflow

**Suggested Agent Prompt:**
```
I am working on the tender360-data-engine project as Agent [NAME].

Please read my instructions at .github/agents/[agent].md
Follow the workflow guide at .github/agents/WORKFLOW_GUIDE.md
Adhere to security policy at .github/SECURITY.md

Current task: [describe task]

Please help me implement this following all guidelines.
```

---

## 🔧 GitHub CLI Setup

Install and configure GitHub CLI for faster workflows:

```bash
# Install (macOS)
brew install gh

# Install (Linux)
curl -sS https://webi.sh/gh | sh

# Authenticate
gh auth login

# Configure
gh config set git_protocol ssh
gh config set editor "code --wait"  # or vim, nano, etc.
```

### Useful Commands

```bash
# Issues
gh issue list --assignee @me
gh issue create --title "..." --body "..."
gh issue close 123

# Pull Requests
gh pr create --title "..." --body "..."
gh pr list --author @me
gh pr view 123
gh pr merge 123 --squash
gh pr checks

# Workflows
gh workflow list
gh workflow run ci.yml
gh run list
gh run view 123456

# Repository
gh repo view
gh repo sync
```

---

## 🚀 CI/CD Workflows

### Workflows Included

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on: Push to main/develop, PRs
   - Jobs: Test, Lint, Security Scan, Dependency Review
   - Status: Non-blocking (continues on error)

2. **CodeQL Security** (`.github/workflows/codeql.yml`)
   - Runs on: Push, PR, Weekly schedule
   - Purpose: Deep security analysis
   - Status: Non-blocking

### Customizing Workflows

Edit workflow files to adjust:

```yaml
# Run on different branches
on:
  push:
    branches: [ main, develop, staging ]

# Change Python versions
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']

# Make checks required (blocking)
continue-on-error: false  # Change to false to block on failure
```

### Viewing Workflow Results

- **GitHub UI:** `Actions` tab → Select workflow run
- **CLI:** `gh run list` → `gh run view <id>`
- **Badges:** Add to README.md:
  ```markdown
  ![CI](https://github.com/vinaybeerelli/tender360-data-engine/workflows/CI%20Pipeline/badge.svg)
  ```

---

## 🛡️ Security Configuration

### Dependabot Configuration

Located at `.github/dependabot.yml`

**Current Settings:**
- Checks: Weekly (Monday 6 AM)
- Groups: patch updates, testing deps, scraping deps
- Auto-merge: Disabled (manual review required)

**To Auto-Merge Patch Updates:**
```bash
# Enable auto-merge for a Dependabot PR
gh pr review <pr-number> --approve
gh pr merge <pr-number> --auto --squash
```

### Secret Scanning

Prevents committing secrets like:
- API keys
- Passwords
- AWS credentials
- SSH keys
- OAuth tokens

**If secret detected:**
1. Remove from code immediately
2. Rotate the secret
3. Update secret in secure location (.env, GitHub Secrets)
4. Add pattern to `.gitignore`

### Security Advisories

If vulnerability is found in your project:

1. Go to: `Security` → `Advisories` → `New draft security advisory`
2. Fill in details (private, not public)
3. Request CVE if needed
4. Publish after fix is ready

---

## 📊 Project Management

### GitHub Projects

Create a project board:

1. Go to: `Projects` → `New project`
2. Choose template: "Kanban"
3. Add columns:
   - 📋 Backlog
   - 📝 To Do
   - 🔄 In Progress
   - 👀 In Review
   - ✅ Done
   - 🚫 Blocked

4. Link issues to project:
   ```bash
   gh issue list | gh project item-add <project-id> --owner vinaybeerelli
   ```

### Milestones

Create milestones for sprints:

```bash
gh api repos/:owner/:repo/milestones -f title="Sprint 1" -f due_on="2025-11-15T00:00:00Z"
```

Or via UI: `Issues` → `Milestones` → `New milestone`

---

## 📝 Templates Usage

### Creating Issues

**Using Template:**
```bash
# Via UI
Issues → New issue → Choose template

# Via CLI with template
gh issue create --template agent-task.md
```

**Quick Issue (No Template):**
```bash
gh issue create --title "[ALPHA] Issue #1: Fix API scraper" \
  --body "Description here" \
  --label "agent-task,P0" \
  --assignee vinaybeerelli
```

### Creating PRs

**Using Template:**
```bash
gh pr create --fill  # Uses .github/PULL_REQUEST_TEMPLATE.md
```

**Custom PR:**
```bash
gh pr create \
  --title "[ALPHA] Issue #1: Fix API scraper" \
  --body "See issue #1" \
  --label "agent-task" \
  --reviewer vinaybeerelli
```

---

## 🔍 Code Owners

Located at `.github/CODEOWNERS`

**How it Works:**
- Automatically requests reviews from code owners
- Blocks merge if owner hasn't approved (if configured)
- Shows ownership in GitHub UI

**Update for Team:**
```
# Add team
/src/scrapers/ @vinaybeerelli @teammate

# Add multiple owners
/config/ @vinaybeerelli @teammate1 @teammate2
```

---

## 🎨 Best Practices

### Commit Message Format

```
[AGENT] Issue #N: Brief description (50 chars)

More detailed explanation (72 chars per line)
- Change 1
- Change 2

Testing:
- Test 1: Passed
- Test 2: Passed

Closes #N
```

### Branch Naming

```
copilot/<agent>-<issue-number>-<description>

Examples:
copilot/alpha-1-fix-api-scraper
copilot/gamma-3-database-schema
copilot/epsilon-5-aws-deployment
```

### PR Title Format

```
[AGENT] Issue #N: Brief description

Examples:
[ALPHA] Issue #1: Fix API scraper session management
[GAMMA] Issue #3: Implement database schema
[DELTA] Issue #8: Create end-to-end pipeline
```

---

## 🚦 Workflow Example

### Solo Developer Workflow (Recommended)

```bash
# 1. Sync with remote
git checkout main
git pull origin main

# 2. Create feature branch (optional but recommended)
git checkout -b copilot/alpha-1-fix-api-scraper

# 3. Make changes
# ... code ...

# 4. Test locally
pytest tests/ -v

# 5. Commit
git add .
git commit -m "[ALPHA] Issue #1: Fix API scraper"

# 6. Push
git push origin copilot/alpha-1-fix-api-scraper

# 7. Create PR (for visibility/history)
gh pr create --fill

# 8. Wait for CI (optional)
gh pr checks

# 9. Merge (bypass approval since it's your repo)
gh pr merge --squash

# OR push directly to main (if no branch protection)
git checkout main
git merge copilot/alpha-1-fix-api-scraper
git push origin main
```

### Team Workflow

```bash
# Same as above, but:
# 7. Create PR and request review
gh pr create --fill --reviewer teammate

# 8. Wait for CI and approval
gh pr checks
gh pr view  # Check review status

# 9. Merge after approval
gh pr merge --squash  # Only after approved
```

---

## 🐛 Troubleshooting

### Issue: CI Workflows Not Running

**Solution:**
1. Check: `Settings` → `Actions` → `General` → "Allow all actions"
2. Verify workflow file syntax: `gh workflow list`
3. Check workflow logs: `gh run list` → `gh run view <id>`

### Issue: Dependabot Not Creating PRs

**Solution:**
1. Verify: `Settings` → `Code security` → Dependabot enabled
2. Check `.github/dependabot.yml` syntax
3. Force check: `Settings` → `Code security` → "Check for updates now"

### Issue: Can't Push to Main

**Solution:**
1. Check branch protection: `Settings` → `Branches`
2. Verify you're admin: `Settings` → `Manage access`
3. Disable "Include administrators" in branch protection
4. Or create PR instead: `gh pr create`

### Issue: Secret Scanning Blocking Commit

**Solution:**
1. Remove secret from code
2. Add to `.gitignore`
3. Use environment variable instead
4. Commit again
5. Rotate the exposed secret

---

## 📚 Additional Resources

### Documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Dependabot Docs](https://docs.github.com/en/code-security/dependabot)
- [Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [CodeQL Docs](https://codeql.github.com/docs/)

### Tools
- [GitHub CLI](https://cli.github.com/)
- [Act (Run Actions Locally)](https://github.com/nektos/act)
- [Dependabot Preview](https://github.com/dependabot/dependabot-core)

### Project-Specific
- Agent Workflow: `.github/agents/WORKFLOW_GUIDE.md`
- Security Policy: `.github/SECURITY.md`
- Branch Protection: `.github/BRANCH_PROTECTION_GUIDE.md`

---

## ✅ Verification Checklist

After completing setup, verify:

### GitHub Features
- [ ] Dependabot alerts enabled
- [ ] Dependabot security updates enabled
- [ ] CodeQL scanning enabled
- [ ] Secret scanning enabled
- [ ] Push protection enabled

### Branch Protection
- [ ] Main branch has protection rule
- [ ] Protection allows you to push (admin bypass)
- [ ] Status checks configured (optional)
- [ ] Force push restricted to admins

### Workflows
- [ ] CI workflow file exists
- [ ] CodeQL workflow file exists
- [ ] Workflows run on push/PR
- [ ] Workflow badges added to README (optional)

### Templates
- [ ] Issue templates exist
- [ ] PR template exists
- [ ] CODEOWNERS file exists
- [ ] Security policy exists

### Agents
- [ ] All 5 agent files updated
- [ ] Workflow guide created
- [ ] Each agent knows their responsibilities

### Testing
- [ ] Push to main works
- [ ] CI workflow runs
- [ ] Dependabot creates PR (wait 1 day)
- [ ] CodeQL scan completes

---

## 🎉 Next Steps

1. **Commit these changes:**
   ```bash
   git add .github/
   git commit -m "chore: Add GitHub repository configuration
   
   - Add CI/CD workflows
   - Configure Dependabot
   - Add issue/PR templates
   - Update agent instructions
   - Add security policy
   - Add branch protection guide"
   
   git push origin main
   ```

2. **Enable GitHub features** (follow Phase 1 above)

3. **Configure branch protection** (follow Phase 2 above)

4. **Start using templates** for issues and PRs

5. **Monitor workflows** in the Actions tab

6. **Review Dependabot PRs** weekly

---

**Questions?** Check the troubleshooting section or open an issue!

**Ready to code?** Follow the agent workflow guide! 🚀

