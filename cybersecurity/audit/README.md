# Botium Toys — Internal Security Audit

## 📋 Overview

This project is a completed **internal security audit** for **Botium Toys**, a fictional U.S.-based toy company with a growing online presence. The audit was conducted as part of the **Google Cybersecurity Professional Certificate** program and demonstrates practical skills in:

- Security auditing
- Risk assessment
- NIST Cybersecurity Framework (CSF) application
- Controls and compliance evaluation
- Regulatory compliance (PCI DSS, GDPR, SOC)

## 🎯 Objective

The goal of this audit was to assess Botium Toys' existing security posture and determine which controls and compliance best practices need to be implemented to:

- Protect critical assets
- Reduce risks, threats, and vulnerabilities
- Ensure compliance with U.S. and international regulations
- Improve overall business continuity

## 🔍 Audit Scope

**Scope:** The entire security program at Botium Toys — all assets, internal processes, and procedures related to the implementation of controls and compliance best practices.

**Framework:** NIST Cybersecurity Framework (CSF)

**Risk Score:** 8 / 10 (high)

## 📊 Key Findings

### Controls Assessment

| Control | Status | Notes |
|---|---|---|
| Least Privilege | ❌ Not implemented | All employees have access to all data |
| Disaster Recovery Plans | ❌ Not implemented | No plans in place |
| Password Policies | ⚠️ Partial | Policy exists, but requirements are nominal |
| Separation of Duties | ❌ Not implemented | — |
| Firewall | ✅ Implemented | Blocks traffic based on security rules |
| Intrusion Detection System (IDS) | ❌ Not implemented | — |
| Backups | ❌ Not implemented | No backups of critical data |
| Antivirus Software | ✅ Implemented | Installed and regularly monitored |
| Legacy Systems Monitoring | ⚠️ Partial | Monitored, but no regular schedule |
| Encryption | ❌ Not implemented | Cardholder data is not encrypted |
| Password Management System | ❌ Not implemented | No centralized system |
| Locks | ✅ Implemented | Sufficient physical locks |
| CCTV Surveillance | ✅ Implemented | Up-to-date |
| Fire Detection/Prevention | ✅ Implemented | Functioning systems |

### Compliance Assessment

| Regulation | Status | Key Gaps |
|---|---|---|
| **PCI DSS** | ❌ Non-compliant | No encryption, unauthorized access to cardholder data, weak password policy |
| **GDPR** | ⚠️ Partial | Privacy policies enforced and 72-hour breach notification in place, but data is not properly classified/inventoried |
| **SOC 1 / SOC 2** | ⚠️ Partial | Data integrity and availability ensured, but access controls and confidentiality are missing |

## 🛠️ Skills Demonstrated

- **Security Auditing** — Conducted an internal audit using NIST CSF
- **Risk Assessment** — Analyzed risks, threats, and vulnerabilities to critical assets
- **Controls Evaluation** — Classified controls by category (Administrative, Technical, Physical) and type (Preventative, Detective, Corrective, Deterrent)
- **Compliance Analysis** — Evaluated adherence to PCI DSS, GDPR, and SOC standards
- **Documentation** — Produced a professional controls and compliance checklist
- **Recommendations** — Provided prioritized remediation recommendations to improve security posture

## 📝 Recommendations Summary

Based on the audit findings, the following actions are recommended for Botium Toys:

1. **Implement Least Privilege and Separation of Duties** — Reduce risk of insider threats and accidental data exposure.
2. **Implement Encryption for Cardholder Data** — Required for PCI DSS compliance.
3. **Install an Intrusion Detection System (IDS)** — Detect and respond to anomalous traffic.
4. **Develop a Disaster Recovery Plan and Backups** — Ensure business continuity.
5. **Implement Centralized Password Management** — Enforce password policy and reduce password fatigue.
6. **Conduct Asset Inventory and Classification** — Establish a foundation for asset management.
7. **Establish Regular Maintenance for Legacy Systems** — Reduce risk from end-of-life systems.
8. **Strengthen Password Policy** — Minimum 8 characters with letters, numbers, and special characters.
9. **Encrypt All Sensitive Data (PII/SPII)** — Ensure confidentiality and compliance with GDPR/SOC.

## 🎓 Learning Outcomes

Through this audit, I gained hands-on experience with:

- Applying the **NIST Cybersecurity Framework (CSF)** in a real-world scenario
- Identifying gaps in security controls and compliance
- Understanding the difference between **control categories** (Administrative, Technical, Physical) and **control types** (Preventative, Detective, Corrective, Deterrent)
- Evaluating compliance with **PCI DSS**, **GDPR**, and **SOC 1/2**
- Producing professional audit documentation suitable for stakeholders

## 📜 Certificate

This project was completed as part of the **Google Cybersecurity Professional Certificate** on Coursera.

## 🔗 Related Projects

- [Network Traffic Capture (FTP)](../network-capture/)
- [Nmap Full Scan](../nmap-scan/)
- [Python SSH Monitor + Telegram](../purplebot/)
- [Web Vulnerabilities (SQLi, XSS)](../web-vulns/)
- [SIEM with Wazuh + DVWA](../SIEM/)
- [IDS/IPS with Suricata](../suricata/) *(in progress)*

## 📬 Contact

**Danil (Rezzodan)**
- GitHub: [https://github.com/Rezzodan/Portfolio](https://github.com/Rezzodan/Portfolio)
- Telegram: [@rezzodan](https://t.me/rezzodan)
- Email: malooyy6@gmail.com

---

*This project is for educational and portfolio purposes only. Botium Toys is a fictional company.*
