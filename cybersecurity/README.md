# 🛡️ Cybersecurity Labs

Hands-on security work in an isolated home lab, built while working full-time as a developer. Focus: **detection and
response** (Blue Team), with attack practice used to understand what the alerts mean.

**Lab environment:** Kali Linux workstation, Metasploitable 2 in QEMU, DVWA in Docker, Wazuh SIEM in Docker,
Suricata IDS on the host. All offensive testing targeted only these lab machines.

## Detection & monitoring

| Project | What it shows |
|---------|---------------|
| [SIEM with Wazuh](SIEM/) | Web-log shipping, XSS alert triage, a gap in default rules for SQL injection closed with a custom rule tested in `wazuh-logtest` |
| [Network IDS with Suricata](ids-suricata/) | IDS on LAN and Docker interfaces, alert analysis and tuning decision |
| [SSH brute-force monitor](purplebot/) | Python log parser with thresholds, GeoIP enrichment, Telegram alerts, tests and CI |

## Incident response & GRC

| Project | What it shows |
|---------|---------------|
| [Incident reports (5)](incident-response/) | Packet and log analysis (Wireshark, tcpdump), root cause, remediation |
| [Security audit — Botium Toys](audit/) | Controls and compliance assessment: NIST CSF, PCI DSS, GDPR, SOC 2 |

## Understanding attacks

| Project | What it shows |
|---------|---------------|
| [Web vulnerabilities](web-vulns/) | SQL injection and reflected XSS on DVWA, with the code-level fixes |
| [Nmap full scan](nmap-scan/) | Service discovery, version detection, Python XML report parser |
| [FTP traffic capture](network-capture/) | Why cleartext protocols leak credentials, and what to use instead |
| [Linux system info script](https://github.com/Rezzodan/sys-info-script) | Bash script collecting users, ports, processes and logs for a quick host audit |

## Skills

Wazuh · Suricata · Wireshark · tcpdump · Nmap · log analysis · incident reporting · NIST CSF · OWASP Top 10 ·
Linux · Bash · Python · Docker · QEMU
