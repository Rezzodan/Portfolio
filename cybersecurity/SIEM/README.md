# SIEM with Wazuh — Detecting Web Attacks on DVWA

## Objective

Deploy Wazuh SIEM, ship web server logs from a vulnerable test application (DVWA) through a Wazuh agent, and detect
web attacks (XSS, SQL injection) in near real time.

## Lab setup

- Wazuh 4.10.0 single-node in Docker (manager, indexer, dashboard)
- Wazuh agent 4.9.0 on Kali Linux
- DVWA in Docker on port 8080, Apache access logs mounted to the host

```text
┌──────────────┐   access.log   ┌──────────────┐   1514/tcp   ┌──────────────┐
│ DVWA         │ ─────────────▶ │ Wazuh agent  │ ───────────▶ │ Wazuh        │
│ (Docker)     │   (volume)     │ (Kali)       │              │ manager      │
└──────────────┘                └──────────────┘              └──────┬───────┘
                                                                     │
                                                              ┌──────▼───────┐
                                                              │ Indexer +    │
                                                              │ Dashboard    │
                                                              └──────────────┘
```

## Setup

### 1. Wazuh stack

```bash
git clone https://github.com/wazuh/wazuh-docker.git -b v4.10.0
cd wazuh-docker/single-node
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d
```

Default passwords were changed before first use: `INDEXER_PASSWORD` and `API_PASSWORD` in `docker-compose.yml`,
user hashes in `config/wazuh_indexer/internal_users.yml`, and the API password in
`config/wazuh_dashboard/wazuh.yml`.

### 2. DVWA with logs on a host volume

```bash
docker run -d -p 8080:80 --name dvwa \
  -v /mnt/data/dvwa-logs:/var/log/apache2 \
  vulnerables/web-dvwa
```

### 3. Agent on Kali

```bash
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo gpg --dearmor -o /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
  | sudo tee /etc/apt/sources.list.d/wazuh.list
sudo apt update && sudo apt install wazuh-agent -y
```

`/var/ossec/etc/ossec.conf`:

```xml
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
```

## Test traffic

Payloads sent to DVWA (security level: low):

```text
SQL injection:   1' OR '1'='1
Reflected XSS:   <script>alert('XSS')</script>
                 <script>alert(document.cookie)</script>
```

## Results

Wazuh decoded the Apache logs (`web-accesslog`) and raised rule **31106** — *"A web attack returned code 200
(success)"*, level 6, groups `web, accesslog, attack`. Code 200 matters: the request was not blocked, so the
analyst should treat it as a likely successful attack, not just a probe.

| Evidence | Payload | Rule | Files |
|----------|---------|------|-------|
| Reflected XSS | `<script>alert('XSS')</script>` | 31106, level 6 | [`xss-alert-basic.json`](xss-alert-basic.json), [`xss-alert-basic.png`](xss-alert-basic.png) |
| Reflected XSS, cookie access | `<script>alert(document.cookie)</script>` | 31106, level 6 | [`xss-alert-cookie.json`](xss-alert-cookie.json), [`xss-alert-cookie.png`](xss-alert-cookie.png) |

The dashboard showed 189 alerts in the last 24 hours (46 medium, 143 low). The SQL injection request was detected
as well; its alert is not exported here yet.

![Wazuh dashboard overview](dashboard.png)

![Alert details for the cookie-stealing XSS payload](xss-alert-cookie.png)

### Compliance tags from Wazuh rule metadata

Wazuh attaches these tags to rule 31106 automatically: PCI DSS 6.5 and 11.4, NIST 800-53 SA.11 and SI.4,
GDPR IV_35.7.d, TSC CC6.1 / CC6.6 / CC6.8 / CC7.1 – CC7.3 / CC8.1.

## Triage notes

1. **Is it real?** Payload is a known XSS pattern and the response code is 200 — the page reflected it.
2. **Scope:** single source IP (`172.17.0.1`, the Docker bridge), one endpoint (`/vulnerabilities/xss_r/`).
3. **Response in a real environment:** block or rate-limit the source, fix output encoding on the endpoint, add a
   Content Security Policy, set `HttpOnly` on session cookies, and check for session reuse after the alert time.

## Key learnings

- Container logs must be exposed through a volume for the agent to read them
- `log_format` must be `apache` for the web attack rules to match
- A status code in the alert changes priority: 200 means the attack reached the application

## Related

- [How these attacks work and how to fix them](../web-vulns/)
- [Network IDS with Suricata](../ids-suricata/)
