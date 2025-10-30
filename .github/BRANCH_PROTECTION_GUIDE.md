# Branch Protection Rules Configuration Guide

## 🎯 Goal
Set up branch protection that provides security WITHOUT blocking your workflow, especially for Copilot agent development.

---

## 📋 Recommended Settings for `main` Branch

### ✅ What to Enable

#### 1. **Require Pull Request Reviews** (Optional - Use with care)
```
Setting: DISABLED for solo developer
Reason: You don't want to block yourself
Alternative: Enable only if working with a team
```

#### 2. **Require Status Checks to Pass**
```
Setting: ENABLED (but not required for pushing)
☑️ Require branches to be up to date before merging
☑️ Status checks that are required:
   - CI Pipeline (Test & Lint) - OPTIONAL
   - CodeQL Security Analysis - OPTIONAL
```

**Configuration:**
- Go to: `Settings` → `Branches` → `Branch protection rules` → `Add rule`
- Branch name pattern: `main`
- Check: "Require status checks to pass before merging"
- **IMPORTANT:** Do NOT check "Require branches to be up to date" if you want to push directly

#### 3. **Require Conversation Resolution**
```
Setting: DISABLED
Reason: Blocks merging if there are unresolved comments
Use only if: Working with a team
```

#### 4. **Require Signed Commits**
```
Setting: OPTIONAL
Reason: Good security practice but requires GPG setup
```

#### 5. **Require Linear History**
```
Setting: DISABLED
Reason: Prevents merge commits, requires rebase
Use only if: You want clean history and understand rebasing
```

#### 6. **Include Administrators**
```
Setting: DISABLED
Reason: Allows you (as admin) to bypass rules when needed
```

#### 7. **Restrict Who Can Push**
```
Setting: DISABLED
Reason: You want to push directly
Use only if: Multi-user repo
```

#### 8. **Allow Force Pushes**
```
Setting: ENABLED (with restrictions)
Options:
  - Everyone: DISABLED
  - Specify who can force push: ENABLED (Add yourself)
Reason: Lets you fix mistakes but prevents accidents
```

#### 9. **Allow Deletions**
```
Setting: DISABLED
Reason: Prevents accidental branch deletion
```

---

## 🚀 Workflow-Friendly Configuration

### **Option A: Minimal Protection (Recommended for Solo Dev)**

```yaml
Branch: main

✅ Require status checks (optional, not blocking)
✅ Allow force pushes (for admins only)
❌ Require pull request reviews
❌ Require conversation resolution
❌ Include administrators (so you can bypass)
❌ Restrict pushes
✅ Prevent deletions
```

**Result:** You can push directly to main, but CI runs to check code quality.

---

### **Option B: Moderate Protection (Team Development)**

```yaml
Branch: main

✅ Require status checks (CI must pass)
✅ Require 1 pull request review (can be waived for admins)
✅ Require conversation resolution
❌ Include administrators (so you can bypass when needed)
✅ Restrict pushes (specify allowed users/teams)
✅ Prevent deletions
✅ Allow force pushes (admins only)
```

**Result:** Normal workflow uses PRs, but admins can bypass for urgent fixes.

---

### **Option C: No Protection (Maximum Flexibility)**

```yaml
Branch: main

❌ All rules disabled
```

**Result:** Complete freedom, rely on CI workflows and code review discipline.

---

## 🔧 Step-by-Step Setup

### 1. Navigate to Repository Settings
```
GitHub → Repository → Settings → Branches
```

### 2. Add Branch Protection Rule
```
Click: "Add rule" or "Add branch protection rule"
Branch name pattern: main
```

### 3. Configure Rules (Recommended for Solo Dev)
```
☐ Require a pull request before merging
   ☐ Require approvals: 0
   
☑ Require status checks to pass before merging
   ☐ Require branches to be up to date before merging
   Status checks found in the last week:
      ☐ CI Pipeline (optional)
      ☐ CodeQL (optional)
   
☐ Require conversation resolution before merging

☐ Require signed commits

☐ Require linear history

☐ Include administrators
   (Leave UNCHECKED so you can bypass rules)
   
☐ Restrict who can push to matching branches

☑ Allow force pushes
   ☑ Specify who can force push
      Add: your-username
   
☐ Allow deletions
```

### 4. Save Changes
```
Click: "Create" or "Save changes"
```

---

## 🛡️ `develop` Branch Settings

For a development branch that feeds into main:

```yaml
Branch: develop

✅ Require status checks (CI must pass)
❌ Require pull request reviews (optional)
❌ Include administrators (you can bypass)
✅ Allow force pushes (admins only)
✅ Prevent deletions
```

**Workflow:**
```
feature-branch → develop → main
                   ↓         ↓
               (CI checks) (Protected)
```

---

## 🤖 Agent-Friendly Workflow

### Recommended Git Workflow for Copilot Agents

```bash
# Agent creates a feature branch
git checkout -b copilot/agent-alpha-issue-1

# Agent makes changes
# ... coding ...

# Agent commits
git add .
git commit -m "[ALPHA] Issue #1: Fix API scraper"

# Agent pushes to feature branch
git push origin copilot/agent-alpha-issue-1

# Create PR from GitHub UI or CLI
gh pr create --title "[ALPHA] Issue #1: Fix API scraper" \
             --body "..." \
             --base main

# After CI passes and review (if required), merge
gh pr merge --squash
```

### Direct Push Workflow (No Protection)

```bash
# Work directly on main
git checkout main
git pull origin main

# Make changes
# ... coding ...

# Commit and push
git add .
git commit -m "[ALPHA] Issue #1: Fix API scraper"
git push origin main
```

---

## 🔍 Testing Your Configuration

### Test 1: Can You Push Directly?
```bash
echo "test" > test.txt
git add test.txt
git commit -m "test: check branch protection"
git push origin main
```

**Expected:**
- If protected: Error message or requires PR
- If not protected: Push succeeds

### Test 2: Can You Force Push? (Be Careful!)
```bash
git push --force origin main
```

**Expected:**
- Should fail unless you're in the allowed list
- Good security practice

### Test 3: Do CI Checks Run?
```bash
git push origin main
# Check GitHub Actions tab
```

**Expected:**
- Workflows run automatically
- You can see results in the "Actions" tab

---

## ⚠️ Common Issues and Solutions

### Issue 1: "You're not authorized to push to main"
**Solution:**
- Go to Settings → Branches → Edit rule
- Uncheck "Include administrators"
- Or add yourself to "Allow specific actors to bypass"

### Issue 2: "Required status check has not run"
**Solution:**
- Push a commit to trigger the workflow
- Or in Settings → Branches, uncheck the specific required check
- Or uncheck "Require status checks to pass"

### Issue 3: "Pull request required"
**Solution:**
- Either create a PR
- Or go to Settings → Branches → Edit rule
- Uncheck "Require a pull request before merging"

### Issue 4: CI Blocks Merging
**Solution:**
- Fix the failing tests
- Or go to Settings → Branches → Edit rule
- Change required checks from "Required" to "Optional"
- Or use "Merge without waiting for requirements to pass" (admin override)

---

## 📊 Rule Sets (GitHub's New Feature)

As of 2024, GitHub introduced "Rulesets" as a more flexible alternative to branch protection rules.

### Benefits of Rulesets
- More granular control
- Can target multiple branches with patterns
- Better bypass controls
- More comprehensive rules

### How to Access
```
Repository → Settings → Rules → Rulesets
```

### Recommended Ruleset for Your Project

```yaml
Ruleset Name: "Main Branch Protection"
Enforcement: Active
Bypass: Allow administrators to bypass

Target:
  - Branch: main
  - Branch: develop

Rules:
  ☑ Require a pull request before merging (Disabled)
  ☑ Require status checks
     Status checks: CI Pipeline (optional)
  ☑ Block force pushes (with exceptions)
     Exceptions: Repository administrators
  ☑ Require signed commits (optional)
  ☐ Require deployments to succeed
```

---

## 🎯 Best Practices for Your Use Case

### For Solo Development with Copilot Agents

1. **Don't block yourself** - Keep branch protection minimal
2. **Use CI for quality** - Let workflows run but don't require them to pass
3. **Create PRs for visibility** - Good for tracking, not enforcement
4. **Enable security scanning** - CodeQL, Dependabot (non-blocking)
5. **Use feature branches** - Good practice even if not required

### For Team Development

1. **Require PRs** - At least 1 reviewer
2. **Require CI to pass** - Quality gate
3. **Use CODEOWNERS** - Auto-assign reviewers
4. **Protect main and develop** - Different rules for each
5. **Document exceptions** - When/why to bypass rules

---

## 📚 Additional Resources

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Rulesets Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)

---

## 🚀 Quick Start Commands

### View Current Protection Rules
```bash
# Using GitHub CLI
gh api repos/:owner/:repo/branches/main/protection
```

### Remove All Protection (Emergency)
```bash
# Via GitHub UI
Settings → Branches → Delete protection rule

# Via API
gh api -X DELETE repos/:owner/:repo/branches/main/protection
```

### Enable Basic Protection via CLI
```bash
gh api -X PUT repos/:owner/:repo/branches/main/protection \
  -F required_status_checks='{"strict":false,"contexts":[]}' \
  -F enforce_admins=false \
  -F required_pull_request_reviews=null \
  -F restrictions=null
```

---

**Remember:** Start simple, add protection as needed. Don't let rules slow you down! 🚀

