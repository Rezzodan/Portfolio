# Incident Response Reports

Five investigations written as stakeholder-ready reports: what happened, the evidence, the root cause and what to
fix. Scenarios come from the Google Cybersecurity Professional Certificate; organizations and IPs are fictional.

| Report | Incident | Evidence & tools | Framework |
|--------|----------|------------------|-----------|
| [SYN flood DoS](syn_flood_dos_analysis/) | Web server overwhelmed by half-open TCP connections | Wireshark TCP/HTTP log | — |
| [ICMP flood DoS](nist_csf_icmp_dos_analysis/) | Internal network down for two hours via a misconfigured firewall | Incident narrative | NIST CSF |
| [DNS outage](dns_icmp_traffic_analysis/) | Website unreachable: UDP 53 answered with ICMP "port unreachable" | tcpdump | — |
| [Brute force → malicious redirect](malicious_redirect_bruteforce/) | Default admin password, injected JavaScript, redirect to a lookalike domain | tcpdump in a sandbox | — |
| [Network hardening after a breach](social_media_network_hardening/) | Four vulnerabilities behind a data breach | Risk assessment | MFA, password policy, firewall |

Every folder has a README summary and the full report as PDF.
