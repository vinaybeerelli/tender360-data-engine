# Security Policy

## 🔒 Supported Versions

We currently support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| develop | :white_check_mark: |
| < 1.0   | :x:                |

---

## 🚨 Reporting a Vulnerability

### Where to Report
**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security issues via:
- **Email:** [your-email@example.com]
- **GitHub Security Advisories:** Use the "Security" tab → "Report a vulnerability"

### What to Include
1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** (what could an attacker do?)
4. **Affected versions/components**
5. **Suggested fix** (if you have one)

### Response Timeline
- **Initial Response:** Within 48 hours
- **Status Update:** Within 7 days
- **Fix Timeline:** Depends on severity
  - Critical: 24-48 hours
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Best effort

---

## 🛡️ Security Best Practices

### For Developers

#### 1. Secrets Management
- **NEVER** commit secrets, API keys, or passwords to the repository
- Use environment variables for sensitive data
- Keep `.env` files in `.gitignore`
- Use `.env.example` for documentation only

```python
# ❌ BAD
api_key = "abc123xyz789"

# ✅ GOOD
import os
api_key = os.getenv("API_KEY")
```

#### 2. Input Validation
- Always validate and sanitize user input
- Use parameterized queries for database operations
- Validate file uploads (type, size, content)

```python
# ✅ GOOD - Parameterized query
cursor.execute("SELECT * FROM tenders WHERE id = ?", (tender_id,))

# ❌ BAD - SQL injection risk
cursor.execute(f"SELECT * FROM tenders WHERE id = {tender_id}")
```

#### 3. Error Handling
- Don't expose sensitive information in error messages
- Log errors securely
- Return generic errors to users

```python
# ❌ BAD
except Exception as e:
    return f"Database error: {str(e)}"  # May expose DB structure

# ✅ GOOD
except Exception as e:
    logger.error(f"Database error: {str(e)}")
    return "An error occurred. Please try again later."
```

#### 4. Dependencies
- Keep dependencies up to date
- Review Dependabot alerts weekly
- Use `pip-audit` to scan for vulnerabilities
- Pin critical dependency versions

```bash
# Scan for vulnerabilities
pip-audit

# Update dependencies safely
pip install --upgrade package-name
```

#### 5. Authentication & Authorization
- Use strong session management
- Implement rate limiting
- Validate all inputs from external APIs
- Use HTTPS for all external communications

---

## 🔍 Security Scanning

### Automated Tools
This repository uses:

1. **CodeQL** - Static code analysis (weekly)
2. **Dependabot** - Dependency vulnerability scanning (daily)
3. **Bandit** - Python security linter (on every push)
4. **Safety** - Dependency security checks (on every push)
5. **TruffleHog** - Secret scanning (on every push)

### Manual Security Checks
Run these before committing:

```bash
# Check for secrets
git diff | grep -iE "(password|api[_-]?key|secret|token)"

# Python security scan
bandit -r src/

# Dependency vulnerabilities
safety check

# Type checking (helps catch some security issues)
mypy src/
```

---

## 🚫 Common Vulnerabilities to Avoid

### 1. Command Injection
```python
# ❌ BAD
os.system(f"wget {user_url}")

# ✅ GOOD
subprocess.run(["wget", user_url], check=True)
```

### 2. Path Traversal
```python
# ❌ BAD
file_path = os.path.join(base_dir, user_input)

# ✅ GOOD
file_path = os.path.abspath(os.path.join(base_dir, user_input))
if not file_path.startswith(base_dir):
    raise ValueError("Invalid path")
```

### 3. Insecure Deserialization
```python
# ❌ BAD
import pickle
data = pickle.loads(user_data)

# ✅ GOOD
import json
data = json.loads(user_data)
```

### 4. XXE (XML External Entity)
```python
# ❌ BAD
import xml.etree.ElementTree as ET
tree = ET.parse(user_file)

# ✅ GOOD
import defusedxml.ElementTree as ET
tree = ET.parse(user_file)
```

---

## 📋 Security Checklist for PRs

Before submitting a PR, ensure:

- [ ] No secrets or credentials in code
- [ ] All inputs are validated
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies are up to date
- [ ] Security scans pass (Bandit, Safety)
- [ ] No hardcoded URLs or paths
- [ ] Logging doesn't include sensitive data
- [ ] All external requests use HTTPS
- [ ] SQL queries are parameterized
- [ ] File operations validate paths

---

## 🎯 Agent-Specific Security Guidelines

### Agent ALPHA (API Scraper)
- Respect robots.txt
- Implement rate limiting
- Handle authentication securely
- Validate all API responses

### Agent BETA (Selenium)
- Keep ChromeDriver updated
- Don't store browser state persistently
- Clear cookies/cache regularly
- Validate all scraped data

### Agent GAMMA (Database)
- Use parameterized queries always
- Implement proper access controls
- Encrypt sensitive data at rest
- Regular backups with encryption

### Agent DELTA (Pipeline)
- Validate all pipeline inputs
- Implement proper error boundaries
- Log security events
- Rate limit external calls

### Agent EPSILON (DevOps)
- Secure AWS credentials properly
- Use IAM roles, not access keys
- Enable CloudWatch logging
- Implement proper firewall rules
- Keep EC2 instances patched

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [GitHub Security Features](https://docs.github.com/en/code-security)

---

## 📞 Contact

For security concerns, contact:
- **Project Manager:** @vinaybeerelli
- **Email:** [your-email@example.com]

---

**Remember:** Security is everyone's responsibility! 🛡️

