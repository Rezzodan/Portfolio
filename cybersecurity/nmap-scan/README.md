## 🎯 Objective
Perform a comprehensive network scan of Metasploitable 2 to discover open ports, identify running services, and extract version information. Then parse the XML output using Python to create a human-readable report.

---

## 🛠️ Tools Used
- **Nmap** — Network scanning and service detection
- **Python 3** — XML parsing with `xml.etree.ElementTree`
- **Metasploitable 2** — Vulnerable Linux VM
- **QEMU** — Virtual machine emulator

---

## 📋 Process

### Step 1: Full Port Scan
Scan all 65,535 TCP ports to discover open services.

```bash
nmap -p- -T4 127.0.0.1

##Flags Explained:

    -p- — Scan all ports (1-65535)

    -T4 — Aggressive timing for faster scanning

Result:
PORT     STATE SERVICE
2121/tcp open  ftp
2223/tcp open  ssh

###Step 2: Service Version Detection

Identify the exact versions of running services.

nmap -sV -p 2121,2223 127.0.0.1

Flags Explained:

    -sV — Service/version detection

    -p — Specify ports to scan

Result:
PORT     STATE SERVICE VERSION
2121/tcp open  ftp     vsftpd 2.3.4
2223/tcp open  ssh     OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)

###Step 3: Save Scan Results to XML

Export scan results in XML format for programmatic parsing.
nmap -sV -p- -oX scan_results.xml 127.0.0.1

lags Explained:

    -oX — Output in XML format

###Step 4: Parse XML with Python
Create a Python script to read the XML and display results in a clean format.

Python Parser (parse_nmap.py):

#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import sys

def parse_nmap_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"[!] Error parsing XML: {e}")
        sys.exit(1)

    print("\n" + "="*50)
    print("  NMAP SCAN RESULTS PARSER")
    print("="*50)

    for host in root.findall('host'):
        addr = host.find('address')
        ip = addr.get('addr') if addr is not None else "Unknown"

        hostnames = host.find('hostnames')
        hostname = ""
        if hostnames is not None:
            hn = hostnames.find('hostname')
            if hn is not None:
                hostname = hn.get('name')

        print(f"\n📡 Host: {ip} ({hostname})")
        print("-" * 40)

        ports = host.find('ports')
        if ports is None:
            print("  No open ports found.")
            continue

        open_ports = 0
        for port in ports.findall('port'):
            state = port.find('state')
            if state is not None and state.get('state') == 'open':
                open_ports += 1
                port_id = port.get('portid')
                protocol = port.get('protocol')
                service = port.find('service')

                service_name = service.get('name') if service is not None else "unknown"
                product = service.get('product') if service is not None else ""
                version = service.get('version') if service is not None else ""
                extra = service.get('extrainfo') if service is not None else ""

                version_str = f"{product} {version}".strip()
                if extra:
                    version_str += f" ({extra})"

                print(f"  🔹 {port_id}/{protocol} - {service_name}")
                if version_str:
                    print(f"     📦 {version_str}")

        print(f"\n  ✅ Total open ports: {open_ports}")

    print("\n" + "="*50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_nmap.py <nmap_xml_file>")
        sys.exit(1)

    parse_nmap_xml(sys.argv[1])

Run the parser:
python3 parse_nmap.py scan_results.xml


###Results

Discovered Services
Port	Service	Version	Known Vulnerabilities
2121	FTP	vsftpd 2.3.4	✅ Backdoor vulnerability (CVE-2011-2523)
2223	SSH	OpenSSH 4.7p1	✅ Outdated, multiple CVEs

Parser Output
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

==================================================


### Key Learnings
##1. Nmap is a Powerful Tool

    Can scan all 65,535 ports quickly

    Identifies service versions with high accuracy

    Outputs structured data (XML) for automation

##2. Legacy Systems Are Vulnerable

    Metasploitable 2 runs outdated software (2008)

    vsftpd 2.3.4 has a known backdoor (port 6200)

    OpenSSH 4.7p1 is susceptible to multiple exploits

##3. Automation is Essential

    XML parsing allows integration with other tools

    Python scripts can extend Nmap functionality

    Automation reduces manual effort


###📂 Files

    scan_results.xml — Raw Nmap XML output

    parse_nmap.py — Python parser script

    README.md — This documentation
