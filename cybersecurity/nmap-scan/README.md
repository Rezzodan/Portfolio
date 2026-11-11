# Nmap Full Scan + Python Report Parser

## Objective

Scan a lab target (Metasploitable 2) for open ports and service versions, export the results to XML and turn them
into a readable report with a small Python parser.

## Lab setup

- Metasploitable 2 in QEMU, FTP and SSH forwarded to `127.0.0.1:2121` and `127.0.0.1:2223`
- Nmap, Python 3 (standard library only)

## Steps

### 1. Full port scan

```bash
nmap -p- -T4 127.0.0.1
```

`-p-` scans all 65,535 TCP ports, `-T4` uses faster timing.

```text
PORT     STATE SERVICE
2121/tcp open  ftp
2223/tcp open  ssh
```

### 2. Service and version detection

```bash
nmap -sV -p 2121,2223 127.0.0.1
```

```text
PORT     STATE SERVICE VERSION
2121/tcp open  ftp     vsftpd 2.3.4
2223/tcp open  ssh     OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)
```

### 3. Export to XML

```bash
nmap -sV -p- -oX scan_results.xml 127.0.0.1
```

### 4. Parse the XML

```bash
python3 parse_nmap.py scan_results.xml
```

```text
==================================================
  NMAP SCAN RESULTS PARSER
==================================================

📡 Host: 127.0.0.1 (localhost)
----------------------------------------
  🔹 2121/tcp - ftp
     📦 vsftpd 2.3.4
  🔹 2223/tcp - ssh
     📦 OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)

  ✅ Total open ports: 2
  ⚠️  Potentially risky services: 2
```

The parser uses `xml.etree.ElementTree`, prints every open port with product and version, and counts services that
are commonly risky when exposed (`ftp`, `ssh`, `telnet`, `http`). Source: [`parse_nmap.py`](parse_nmap.py).

## Findings

| Port | Service | Version | Why it matters |
|------|---------|---------|----------------|
| 2121 | FTP | vsftpd 2.3.4 | This release shipped with a known backdoor (CVE-2011-2523); FTP also sends credentials in cleartext |
| 2223 | SSH | OpenSSH 4.7p1 | Released in 2008, many known CVEs; should be upgraded |

## Recommendations

- Remove or upgrade vsftpd 2.3.4; prefer SFTP
- Upgrade OpenSSH, disable password login, allow keys only
- Keep an inventory of exposed services and rescan after every change

## Files

- [`scan_results.xml`](scan_results.xml) — raw Nmap XML output
- [`parse_nmap.py`](parse_nmap.py) — XML report parser
