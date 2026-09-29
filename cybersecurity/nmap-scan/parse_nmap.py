#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import sys

def parse_nmap_xml(xml_file):
    """
    Parse Nmap XML output and display discovered services.
    """
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
        # Get IP address
        addr = host.find('address')
        ip = addr.get('addr') if addr is not None else "Unknown"

        # Get hostname
        hostnames = host.find('hostnames')
        hostname = ""
        if hostnames is not None:
            hn = hostnames.find('hostname')
            if hn is not None:
                hostname = hn.get('name')

        print(f"\n📡 Host: {ip} ({hostname})")
        print("-" * 40)

        # Get ports
        ports = host.find('ports')
        if ports is None:
            print("  No open ports found.")
            continue

        open_ports = 0
        risky_services = 0
        for port in ports.findall('port'):
            state = port.find('state')
            if state is not None and state.get('state') == 'open':
                open_ports += 1
                port_id = port.get('portid')
                protocol = port.get('protocol')
                service = port.find('service')

                service_name = service.get('name') if service is not None else "unknown"
                if service_name in ['ftp', 'ssh','telnet','http']:
                    risky_services += 1
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
        print(f"  ⚠️  Potentially risky services: {risky_services}")

    print("\n" + "="*50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_nmap.py <nmap_xml_file>")
        sys.exit(1)

    parse_nmap_xml(sys.argv[1])
