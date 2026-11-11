# Brute Force → Malicious Redirect — Incident Report

Completed as part of the **Google Cybersecurity Professional Certificate**. The company and domains are fictional.

## Summary

| Item | Details |
|------|---------|
| Affected site | `yummyrecipesforme.com` (`203.0.113.22`) |
| Malicious site | `greatrecipesforme.com` (`192.0.2.172`) |
| Initial access | Brute force of the admin panel — the account still used a default password |
| Impact | Injected JavaScript prompted visitors to download and run a file that redirected them to the malicious site; the owner was locked out after the attacker changed the admin password |
| Protocols | DNS, HTTP |

## How it was discovered

Customers contacted the help desk: the site asked them to download a file for "free recipes", after which their
browser opened a different website and their computers slowed down.

## Investigation

The site was visited from a sandbox while `tcpdump` captured traffic. Key lines from the
[capture](tcpdump-log.pdf):

```text
14:18:32  your.machine > dns.google.domain   A? yummyrecipesforme.com.   → A 203.0.113.22
14:18:36  your.machine > yummyrecipesforme.com.http   HTTP: GET / HTTP/1.1
          ... executable downloaded and run ...
14:20:32  your.machine > dns.google.domain   A? greatrecipesforme.com.   → A 192.0.2.172
14:25:29  your.machine > greatrecipesforme.com.http   new HTTP session to the malicious host
```

1. DNS resolves the legitimate site and the browser loads it over HTTP.
2. After the downloaded file runs, a **second DNS lookup** appears for a lookalike domain the user never typed.
3. The browser then opens an HTTP session to the malicious IP — the redirect.

A senior analyst confirmed the compromise by finding injected JavaScript in the site's source code.

## Root cause

A default password on the administrative account, with no lockout policy or MFA to slow down brute force.

## Recommendations

1. **MFA for all administrative accounts** — a guessed password alone no longer grants access.
2. **Account lockout and rate limiting** on the login page after repeated failures.
3. **Remove default credentials** and enforce a strong password policy.
4. **Integrity monitoring** of website source files to detect injected scripts quickly.

## Files

- [`incident-report.pdf`](incident-report.pdf) — full incident report
- [`tcpdump-log.pdf`](tcpdump-log.pdf) — annotated tcpdump capture
