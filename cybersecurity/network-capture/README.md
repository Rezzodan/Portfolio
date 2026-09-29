## Objective
Capture FTP traffic to see how insecure protocols transmit passwords in plaintext.

## Tools
- QEMU + Metasploitable 2
- tcpdump / Wireshark
- FTP

## Process

### 1. Start VM with port forwarding
```bash
qemu-system-x86_64 -m 512 -accel tcg \
  -netdev user,id=net0,hostfwd=tcp::2223-:22,hostfwd=tcp::2121-:21 \
  -device e1000,netdev=net0 \
  -drive file="Metasploitable.vmdk",format=vmdk
```

### 2. Start packet capture (on Metasploitable)
```bash
sudo tcpdump -i eth0 -s 0 -w /tmp/ftp_capture.pcap
```

### 3. Connect via FTP (from Kali)
```bash
ftp localhost 2121
# Login: msfadmin
# Password: msfadmin
```

### 4. Transfer capture to Kali
```bash
scp -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedKeyTypes=+ssh-rsa -P 2223 msfadmin@localhost:/tmp/ftp_capture.pcap ~/
```

### 5. Analyze in Wireshark
```bash
wireshark ~/ftp_capture.pcap
```
Filter: `tcp.port == 21` → Follow → TCP Stream

## Result

Captured FTP credentials in plaintext:

```
USER msfadmin
PASS msfadmin
```

## Screenshot
![FTP password in plaintext](wireshark_ftp.png)

## Key Takeaway
FTP transmits passwords in **plaintext**. Anyone on the same network can intercept them. Always use SFTP or SSH for secure file transfer.

## Files
- `ftp_capture.pcap` — raw network capture
- `wireshark_ftp.png` — screenshot of captured password
