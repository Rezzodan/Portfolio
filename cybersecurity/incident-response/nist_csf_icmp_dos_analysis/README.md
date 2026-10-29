# NIST CSF Incident Report: ICMP Flood DoS Attack

## 📋 Overview
This project demonstrates the application of the **NIST Cybersecurity Framework (CSF)** to analyze and respond to a Denial of Service (DoS) attack caused by an ICMP flood. The incident occurred due to a misconfigured firewall and disrupted internal network services for two hours.

## 🎯 Framework Applied (NIST CSF)
*   **Identify:** Audited the network to find the misconfigured firewall lacking rate limiting and IP verification.
*   **Protect:** Implemented firewall rules, anti-spoofing verification, and an IPS to filter malicious traffic.
*   **Detect:** Deployed network monitoring software and IDS to alert on abnormal traffic patterns.
*   **Respond:** Contained the attack by blocking ICMP traffic and offlining non-critical services. Updated the response playbook.
*   **Recover:** Restored critical services and outlined a Disaster Recovery Plan (DRP) for future events.

## 🛠️ Key Takeaways
- Learned how to map a real-world security incident to the 5 core functions of the NIST CSF.
- Developed a comprehensive plan to improve network security posture against future DoS attacks.
