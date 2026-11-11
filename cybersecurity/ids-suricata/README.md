# Network IDS with Suricata

## Objective

Run Suricata as a network intrusion detection system on a Kali workstation, monitor both the wireless interface and
the Docker bridge where lab containers live, and analyze the alerts it raises.

## Setup

- Suricata 8.0.7 as a systemd service, AF_PACKET capture mode
- Interfaces: `wlan1` (LAN) and `docker0` (lab containers such as DVWA)
- `HOME_NET` set to the private ranges `192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12`
- Rules loaded from `suricata.rules` (Emerging Threats Open rule set)
- Output: `fast.log` for quick review and `eve.json` for SIEM ingestion

Relevant part of the configuration ([full example](config/suricata.yaml.example)):

```yaml
af-packet:
  - interface: wlan1
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
  - interface: docker0
    cluster-id: 98
    cluster-type: cluster_flow
    defrag: yes
```

Verify the service and the capture interfaces:

```bash
sudo systemctl status suricata
sudo suricatasc -c "iface-list"
# {"message":{"count":2,"ifaces":["wlan1","docker0"]},"return":"OK"}
```

![Suricata running on wlan1 and docker0](screenshots/suricata-running.png)

## Test and alert analysis

While Suricata was running, a TCP SYN scan was started against the workstation from a second terminal, and the
alert log was watched live:

```bash
sudo nmap -sS -Pn -p 1-1000 192.168.0.101
sudo tail -f /var/log/suricata/fast.log
```

Example alert captured during the session:

```text
[**] [1:2022973:1] ET INFO Possible Kali Linux hostname in DHCP Request Packet [**]
[Classification: Potential Corporate Privacy Violation] [Priority: 1] {UDP} 192.168.0.101:68 -> 192.168.0.1:67
```

![fast.log alert next to the Nmap scan](screenshots/suricata-alerts.png)

**Triage:** the workstation announced the hostname `kali` in its DHCP request. In a corporate network this is a
useful signal — an offensive-security distribution appearing on the LAN — and should be checked against the asset
inventory. Here it is the analyst's own lab machine, so the alert is a **true positive with an expected cause**
and can be tuned (suppressed for this host) rather than escalated.

## Key learnings

- Monitoring `docker0` is required to see traffic between lab containers; the physical interface alone misses it
- Informational rules (`ET INFO`) produce context, not attacks — triage means deciding *expected vs unexpected*
- Port scans need dedicated scan-detection rules or thresholds; they are not guaranteed to alert by default

## Next steps

- Write and test a local rule with a threshold for SYN scans against `HOME_NET`
- Ship `eve.json` to the Wazuh manager to correlate network and host alerts in one place

## Related

- [SIEM with Wazuh](../SIEM/)
- [Nmap full scan](../nmap-scan/)
