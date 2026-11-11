# FTP Traffic Capture — Plaintext Credentials

## Objective

Capture FTP traffic in an isolated lab and show why legacy cleartext protocols are a risk: anyone on the network
path can read the credentials.

## Lab setup

- Kali Linux (analyst machine)
- Metasploitable 2 in QEMU (target, `vsftpd 2.3.4`)
- tcpdump, Wireshark

## Steps

1. Start the target VM with FTP and SSH forwarded to the host:

   ```bash
   qemu-system-x86_64 -m 512 -accel tcg \
     -netdev user,id=net0,hostfwd=tcp::2223-:22,hostfwd=tcp::2121-:21 \
     -device e1000,netdev=net0 \
     -drive file="Metasploitable.vmdk",format=vmdk
   ```

2. Capture traffic on the target:

   ```bash
   sudo tcpdump -i eth0 -s 0 -w /tmp/ftp_capture.pcap
   ```

3. Log in over FTP from Kali (default lab account `msfadmin`):

   ```bash
   ftp localhost 2121
   ```

4. Copy the capture to Kali and open it in Wireshark:

   ```bash
   scp -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedKeyTypes=+ssh-rsa \
     -P 2223 msfadmin@localhost:/tmp/ftp_capture.pcap ~/
   wireshark ~/ftp_capture.pcap
   ```

5. Filter `tcp.port == 21`, then **Follow → TCP Stream**.

## Result

The FTP control channel carries the username and password in cleartext:

```text
220 (vsFTPd 2.3.4)
USER msfadmin
331 Please specify the password.
PASS msfadmin
230 Login successful.
```

![Wireshark TCP stream with USER and PASS in cleartext](wireshark-tcp-stream.jpg)

![Packet list for the FTP session](wireshark-packets.jpg)

## Detection and mitigation

| Risk | Mitigation |
|------|------------|
| Credentials readable on the wire | Replace FTP with SFTP or FTPS |
| Legacy service exposed | Disable FTP where not needed, restrict by firewall |
| Credential reuse | Unique passwords, MFA on remote access |
| No visibility | Alert on cleartext auth protocols (IDS rules for FTP `USER`/`PASS`) |

## Files

- [`ftp_capture.pcap`](ftp_capture.pcap) — raw capture (lab traffic only)
- [`wireshark-tcp-stream.jpg`](wireshark-tcp-stream.jpg), [`wireshark-packets.jpg`](wireshark-packets.jpg) — screenshots
