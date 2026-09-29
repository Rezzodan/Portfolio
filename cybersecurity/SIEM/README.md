## SIEM with Wazuh + DVWA Attack Detection

## 🎯 Objective
Deploy Wazuh SIEM, connect a Wazuh agent, and detect web attacks (SQL Injection, XSS) against DVWA in real time.

## 🛠️ Lab Setup
- **Wazuh v4.10.0** (Docker: manager, indexer, dashboard)
- **DVWA** (Docker, port 8080)
- **Kali Linux** (Wazuh agent v4.9.0)
- **Docker Root Dir:** `/mnt/data/docker` (HDD)

## 📋 Architecture

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ DVWA │────▶│ Wazuh Agent │────▶│ Wazuh │
│ (Docker) │ │ (Kali) │ │ Manager │
└──────────────┘ └──────────────┘ └──────┬───────┘
│
┌──────▼───────┐
│ Wazuh │
│ Indexer │
└──────┬───────┘
│
┌──────▼───────┐
│ Dashboard │
└──────────────┘

## 🚀 Installation

### 1. Wazuh Docker Setup
```bash
git clone https://github.com/wazuh/wazuh-docker.git -b v4.10.0
cd wazuh-docker/single-node
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d

### 2. Configure Passwords

    docker-compose.yml: set INDEXER_PASSWORD, API_PASSWORD

    config/wazuh_indexer/internal_users.yml: set admin and wazuh-wui hashes

    config/wazuh_dashboard/wazuh.yml: set API password

### 3. Wazuh Agent on Kali
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo gpg --dearmor -o /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee /etc/apt/sources.list.d/wazuh.list
sudo apt update
sudo apt install wazuh-agent -y

### 4. Agent Configuration (/var/ossec/etc/ossec.conf)

<client>
  <server>
    <address>localhost</address>
    <port>1514</port>
    <protocol>tcp</protocol>
  </server>
</client>

<localfile>
  <log_format>apache</log_format>
  <location>/mnt/data/dvwa-logs/access.log</location>
</localfile>

### 5. DVWA with Log Volume

docker run -d -p 8080:80 --name dvwa \
  -v /mnt/data/dvwa-logs:/var/log/apache2 \
  vulnerables/web-dvwa


### 🎮 Usage
Access Dashboard

    URL: https://localhost:443

    Login: (your login)

    Password: (your password)

### Attack DVWA
# SQL Injection
1' OR '1'='1

# XSS (Reflected)
<script>alert('XSS')</script>
<script>alert(document.cookie)</script>

#📊 Results

Wazuh Alert (XSS detected)
rule.description: A web attack returned code 200 (success).
rule.id: 31106
rule.level: 6
data.url: /vulnerabilities/xss_r/?name=%3Cscript%3Ealert%28document.cookie%29%3C%2Fscript%3E
decoder.name: web-accesslog
location: /mnt/data/dvwa-logs/access.log

###Dashboard Stats
    Total alerts: 208

    Rule.id 31106: Web attack

    XSS hits: 2

    SQLi hits: 1

### 🛡️ MITRE ATT&CK Mapping
    rule.gdpr: IV_35.7.d

    rule.nist_800_53: SA.11, SI.4

    rule.pci_dss: 6.5, 11.4

    rule.tsc: CC6.6, CC7.1, CC8.1, CC6.1, CC6.8, CC7.2, CC7.3

### 🔍 Key Learnings
    Wazuh SIEM detects SQLi and XSS in real time

    Docker logs must be exposed via volume for agent to read

    log_format=apache is required for web attack detection

    Rule.id 31106 — built-in rule for web attacks

    Dashboard shows MITRE ATT&CK mapping for each alert

### Files

    docker-compose.yml — Wazuh stack

    internal_users.yml — user hashes

    wazuh.yml — Dashboard API config

    ossec.conf — Agent config

    screenshots/ — Dashboard screenshots

