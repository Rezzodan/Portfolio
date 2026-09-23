## 🎯 Objective
Understand how SQL Injection and XSS work by exploiting DVWA (Damn Vulnerable Web Application) in an isolated lab.

## 🛠️ Lab Setup
- **QEMU** + Metasploitable 2
- **DVWA** (Security Level: Low)
- **Kali Linux**
- **Port forwarding:** 8080 → 80

## 🔴 SQL Injection

### Test 1: Normal Query
**Input:** `1`
**Result:** Single user (admin/admin)

### Test 2: Authentication Bypass
**Input:** `1' OR '1'='1`
**Result:** All users returned

**Why it works:**
- Query becomes: `SELECT * FROM users WHERE id = '1' OR '1'='1'`
- `'1'='1'` is always true → all rows returned

![Authentication Bypass](sqli/01-auth-bypass.png)

### Test 3: UNION-based (Extract Passwords)
**Input:** `1' UNION SELECT user, password FROM users-- `
**Result:** All usernames and password hashes

**Why it works:**
- `UNION` combines two queries
- `-- ` (with space!) comments out the rest

![UNION Passwords](sqli/02-union-passwords.png)

## 🔴 XSS (Reflected)

### Test 1: Cookie Theft
**Input:** `<script>alert(document.cookie)</script>`
**Result:** Session cookie exposed

**Why it works:**
- Site inserts input into HTML without encoding
- Browser executes the script

![XSS Cookie Theft](xss/01-cookie-theft.png)

## 🛡️ Defense (Blue Team)

### SQL Injection
- **Prepared statements** (parameterized queries)
- **Input validation** (only digits for ID)
- **WAF** (ModSecurity)
- **Least privilege** (DB user with SELECT only)

### XSS
- **Output encoding** (`<` → `&lt;`)
- **Content Security Policy** (CSP)
- **HttpOnly cookies** (JS cannot read)
- **SameSite cookies**

## 📚 Key Learnings
- User input must **never** be trusted
- DVWA demonstrates real-world vulnerabilities
- **Purple Team:** attack to understand, defend to protect
- Both SQLi and XSS are in **OWASP Top 10**

## 🔗 Related
- [Day 4: Python SSH Monitor](../purplebot/)
- [Day 3: Nmap Scan](../nmap-scan/)
- [Portfolio](https://github.com/Rezzodan/purple-team-lab)

---

