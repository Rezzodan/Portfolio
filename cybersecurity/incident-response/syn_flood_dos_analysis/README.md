# SYN Flood DoS Attack — Incident Analysis

## 📋 Overview
This project is a **network traffic analysis** of a Denial of Service (DoS) incident. It demonstrates the ability to analyze packet captures (Wireshark logs) to identify a SYN flood attack, understand its impact on a web server, and document the findings in a professional incident report.

This project was completed as part of the **Google Cybersecurity Professional Certificate** (Course 3: Connect and Protect: Networks and Network Security).

## 🎯 Objective
Analyze the provided Wireshark TCP/HTTP log to:
- Identify the type of network attack.
- Explain how the TCP three-way handshake is exploited.
- Determine the root cause of the service interruption.

## 🔍 Incident Summary
| Item | Details |
|---|---|
| **Target** | Company Web Server (`192.0.2.1`) |
| **Attack Type** | Direct Denial of Service (DoS) — SYN Flood |
| **Attacker IP** | `203.0.113.0` |
| **Impact** | Web server overwhelmed, legitimate users received `HTTP 504 Gateway Time-out` errors. |

## 📊 Analysis
The Wireshark log showed:
1. A single IP address (`203.0.113.0`) sending an abnormal volume of TCP `[SYN]` packets.
2. The server responded with `[SYN, ACK]` packets, allocating resources for each request.
3. Because the attacker never completed the handshake with an `[ACK]`, the server's connection table filled up (half-open connections).
4. Eventually, the server could no longer respond to legitimate employee traffic, resulting in connection resets (`RST, ACK`) and timeouts.

## 🛠 Tools Used
- **Wireshark** — packet analysis (TCP/HTTP logs)
- **TCP/IP Model** — understanding of the transport layer and three-way handshake

## 📝 Recommendations
1. **Implement SYN Cookies** on the web server to prevent resource exhaustion.
2. **Rate limiting** on the firewall to block IPs sending excessive SYN requests.
3. **Deploy a WAF (Web Application Firewall)** or DDoS protection service.
4. **Blackhole routing** for the attacking IP (as a temporary mitigation).
