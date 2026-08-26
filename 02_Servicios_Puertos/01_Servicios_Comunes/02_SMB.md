---
title: SMB (Server Message Block - Puertos 139, 445)
pubDate: '2026-08-26'
---

## ¿Qué es SMB?
**Server Message Block (SMB)** es el protocolo estándar de Windows para compartir archivos e impresoras, además de facilitar la comunicación entre procesos (Named Pipes). En sistemas Linux, su implementación se realiza mediante **Samba**.

### Riesgos principales
1. **Exposición de archivos:** Comparticiones con acceso anónimo (Null Session) que contienen backups, archivos de configuración o llaves.
2. **Vulnerabilidades críticas:** EternalBlue (MS17-010) permite ejecución de comandos (RCE) como SYSTEM sin credenciales.
3. **Movimiento lateral:** Con credenciales válidas, es posible ejecutar comandos remotamente en la máquina víctima.

---

## ⚙️ Ficheros de Configuración y Directivas Críticas (Samba)

### Ruta Clave: `/etc/samba/smb.conf`
| Ajuste en `smb.conf` | Descripción e Impacto de Seguridad |
| :--- | :--- |
| `browseable = yes` | ¿Permite listar los recursos compartidos disponibles? |
| `read only = no` / `writable = yes` | Permite a los usuarios crear, modificar y subir archivos al share. |
| `guest ok = yes` | ¿Permite la conexión anónima al servicio sin utilizar contraseña? |
| `enable privileges = yes` | Respeta los privilegios asignados a un SID específico. |
| `create mask = 0777` | Permisos asignados por defecto a los archivos recién creados. |
| `directory mask = 0777` | Permisos asignados por defecto a los directorios recién creados. |
| `logon script = script.sh` | Script ejecutado automáticamente en el inicio de sesión del usuario. |
| `magic script = script.sh` | Script ejecutado automáticamente al cerrarse la sesión. |

---

## 🔎 1. Enumeración Inicial (Null Session y Reconocimiento)

### NetBIOS y Nmap Scripts
```bash
# Identificación NetBIOS
nmblookup -A <TARGET_IP>
nbtscan <TARGET_IP>

# Scripts Nmap de Enumeración y Detección de OS
nmap -p 137,138,139,445 --script=nbstat,smb-os-discovery,smb-enum-shares,smb-enum-users <TARGET_IP>
nmap -p 445 --script=smb-null-session,smb2-capabilities,smb2-security-mode <TARGET_IP>

# Detección de Vulnerabilidades SMB en Nmap
nmap -p 445 --script="smb-vuln-*" <TARGET_IP>
```

### Enumeración de Recursos Compartidos (Shares)
```bash
# Listar recursos compartidos con sesión nula (smbclient)
smbclient -L \\\\<TARGET_IP>\\ -N
smbclient -m=SMB2 -L \\\\<TARGET_IP>\\ -N

# Smbmap (Muestra permisos de lectura/escritura de forma visual)
smbmap -H <TARGET_IP>
smbmap -u DoesNotExist -H <TARGET_IP>

# CrackMapExec / NetExec (Listar shares anónimamente)
crackmapexec smb <TARGET_IP> --shares -u '' -p ''
nxc smb <TARGET_IP> -u '' -p '' --shares

# Frameworks de enumeración exhaustiva
enum4linux -a <TARGET_IP>
./enum4linux-ng.py <TARGET_IP> -A
```

---

## 👥 2. Enumeración con RPCCLIENT y Fuerza Bruta de RIDs

```bash
# Conexión nula con rpcclient
rpcclient -U "" -N <TARGET_IP>
```

### Consultas Clave dentro de `rpcclient`:
| Consulta | Descripción |
| :--- | :--- |
| `srvinfo` | Información general del servidor y versión de Windows/Samba. |
| `enumdomains` | Enumera todos los dominios desplegados en la red. |
| `querydominfo` | Información detallada de dominio, servidor y controladores. |
| `netshareenumall` | Enumera todos los recursos compartidos disponibles. |
| `netsharegetinfo <share>` | Muestra información y permisos del recurso indicado. |
| `enumdomusers` | Enumera todos los usuarios del dominio. |
| `queryuser <RID>` | Muestra información detallada de un usuario por su RID. |

### Fuerza Bruta de RIDs de Usuarios (Oneliner imprescindible):
Extrae automáticamente los nombres de usuario y grupos asociados probando RIDs secuenciales del 500 al 1100:
```bash
for i in $(seq 500 1100); do rpcclient -N -U "" <TARGET_IP> -c "queryuser 0x$(printf '%x\n' $i)" | grep "User Name\|user_rid\|group_rid" && echo ""; done
```

### Otras Herramientas de Mapeo de SIDs/RIDs:
```bash
# Dump automático de SAMR
samrdump.py <TARGET_IP>

# Impacket lookupsid (Fuerza bruta de SIDs/RIDs con o sin credenciales)
impacket-lookupsid <DOMAIN>/<USERNAME>:<PASSWORD>@<TARGET_IP>
impacket-lookupsid anonymous@<TARGET_IP> -no-pass
```

---

## 🚀 3. Interacción y Gestión de Archivos SMB

### Conectar a un Recurso Específico
```bash
# Conexión anónima
smbclient \\\\<TARGET_IP>\\<RECURSO> -N

# Conexión con credenciales
smbclient \\\\<TARGET_IP>\\<RECURSO> -U "usuario%password"
smbclient \\\\<TARGET_IP>\\<RECURSO> -U "DOMINIO\\usuario%password"
```

### Comandos dentro de `smbclient`:
```bash
ls                  # Listar contenido
showacls            # Mostrar permisos de ACLs detallados
recurse ON          # Activar descarga recursiva
prompt OFF          # Desactivar confirmaciones interactivas
mget *              # Descargar todos los archivos y carpetas
put archivo.txt     # Subir un archivo al recurso
```

### Operaciones con `smbmap` (Descargas/Subidas Rápidas):
```bash
# Listado recursivo completo del contenido de los shares
smbmap -R -H <TARGET_IP>
smbmap -R <SHARE_NAME> -H <TARGET_IP>

# Descargar o subir un archivo específico
smbmap -H <TARGET_IP> --download '<SHARE_NAME>\\archivo.txt'
smbmap -H <TARGET_IP> --upload archivo.txt '<SHARE_NAME>/archivo.txt'
```

### Montar Recurso en Linux
```bash
mkdir -p /mnt/smb_share
sudo mount -t cifs //<TARGET_IP>/<RECURSO> /mnt/smb_share -o guest,domain=,sec=ntlm
```

---

## 🔑 4. Ataques con Credenciales

### CrackMapExec / NetExec
```bash
# Validar credenciales (Muestra 'Pwn3d!' si es Administrador local)
crackmapexec smb <TARGET_IP> -u usuario -p password
crackmapexec smb <TARGET_IP> -u usuario -p password --shares
```

### Obtención de Shells (Impacket)
Si el usuario cuenta con permisos administrativos en la máquina objetivo:
```bash
# PsExec: Shell directa como SYSTEM (Sube binario a ADMIN$)
impacket-psexec dominio/usuario:password@<TARGET_IP>

# Smbexec: Shell sigilosa nativa (Sin subir binarios)
impacket-smbexec dominio/usuario:password@<TARGET_IP>
```

---

## ⚠️ 5. Vulnerabilidades Críticas

### EternalBlue (MS17-010)
Afecta a Windows 7, Server 2008 y versiones vulnerables de Windows 10:
```bash
# Detección con Nmap
nmap -p 445 --script smb-vuln-ms17-010 <TARGET_IP>

# Metasploit
use exploit/windows/smb/ms17_010_eternalblue
```

> **Tip de Auditoría:** Busca siempre en los shares archivos como `web.config`, `groups.xml`, `settings.json`, backups `.bak`/`.sql` o scripts `.ps1` que contengan contraseñas hardcodeadas.
