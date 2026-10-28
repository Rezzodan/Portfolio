# DNS / ICMP Traffic Analysis — Incident Report

## 📋 Overview

This project is a **network traffic analysis** of a cybersecurity incident involving a DNS service failure. It demonstrates the ability to use packet analysis tools (`tcpdump`) to identify the root cause of a network outage and document it in a professional incident report.

This project was completed as part of the **Google Cybersecurity Professional Certificate** (Course 3: Connect and Protect: Networks and Network Security).

## 🎯 Objective

Analyze network traffic captured with `tcpdump` to:
- Identify which network protocols were involved in the incident.
- Determine why the website `www.yummyrecipesforme.com` was unreachable.
- Provide a likely root cause and recommendations for resolution.

## 🔍 Incident Summary

| Item | Details |
|---|---|
| **Website** | `www.yummyrecipesforme.com` |
| **Error** | "Destination port unreachable" |
| **Protocols Involved** | UDP (DNS query), ICMP (error response) |
| **Affected Port** | 53 (DNS) |
| **DNS Server IP** | `203.0.113.2` |
| **Client IP** | `192.51.100.15` |

## 📊 Analysis

The `tcpdump` log showed:
1. The client sent a **UDP** query to port 53 on the DNS server to resolve the domain name.
2. Instead of a DNS response, the server returned an **ICMP** error: `Destination port unreachable`.
3. This indicates that the DNS service on the server was not running or was blocked by a firewall.

## 🛠 Tools Used

- **`tcpdump`** — packet capture and analysis
- **Wireshark** (optional) — for visual packet inspection
- **Linux CLI** — for log analysis and filtering

## 💡 Root Cause

The most likely cause is that the **DNS service** on the server `203.0.113.2` had crashed, stopped, or was misconfigured. Alternatively, a **firewall rule** may have been blocking UDP port 53, preventing DNS queries from being processed.

## 📝 Recommendations

1. **Restart the DNS service** on the server (`systemctl restart bind9` or equivalent).
2. **Verify firewall rules** to ensure UDP port 53 is open for incoming queries.
3. **Implement DNS monitoring** to detect service failures before they impact users.
4. **Set up redundant DNS servers** for high availability.

## 🎓 Learning Outcomes

Through this project, I gained hands-on experience with:
- Capturing and analyzing network traffic using `tcpdump`.
- Identifying DNS and ICMP protocols in packet captures.
- Diagnosing a network outage caused by a service failure.
- Writing a professional incident report suitable for stakeholders.

*This project is for educational and portfolio purposes only.*
