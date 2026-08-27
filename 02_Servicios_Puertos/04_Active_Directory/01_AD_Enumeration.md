---
title: Enumeración de Active Directory
pubDate: '2025-11-26'
---

## 🏗️ Conceptos Básicos
En una red de Active Directory (AD), el objetivo final suele ser comprometer el **Domain Controller (DC)** para obtener el control total de la infraestructura. La enumeración es el paso más crítico: permite encontrar usuarios, grupos, relaciones de confianza y posibles rutas de ataque hacia los privilegios de Administrador de Dominio.

---

## 🔎 1. Enumeración Sin Credenciales (Externo)
Si acabas de llegar a la red y solo tienes la IP del DC.

### Kerberos (Puerto 88) - Kerbrute
Es el método más silencioso para validar usuarios, ya que no genera logs de fallo de inicio de sesión (Logon Failure).
```bash
# Enumerar usuarios válidos a partir de una lista
./kerbrute userenum -d dominio.local --dc <IP_DC> users.txt

# Password Spraying (Probar UNA contraseña contra todos los usuarios)
# Es la técnica más segura para evitar bloqueos de cuenta por intentos fallidos.
./kerbrute passwordspray -d dominio.local --dc <IP_DC> users_validos.txt "Welcome123!"
```

### LDAP (Puerto 389/636)
Si el servidor permite el acceso anónimo (Anonymous Bind), puedes extraer toda la base de datos del AD.
```bash
# Volcado rápido en HTML (Genera tablas muy legibles en una carpeta local)
ldapdomaindump -u "" -p "" <IP_DC>

# Consulta manual con ldapsearch
ldapsearch -x -H ldap://<IP_DC> -b "DC=dominio,DC=local"
```

---

## 🎯 2. Enumeración Con Credenciales (Interno)
Una vez obtienes un usuario válido (aunque sea uno con pocos privilegios).

### NetExec (El estándar actual)
Es la herramienta más rápida para mapear el dominio desde Linux.
```bash
# Listar usuarios y sus descripciones (¡Busca contraseñas en las notas!)
nxc smb <IP_DC> -u 'usuario' -p 'password' --users

# Listar grupos y sus miembros
nxc smb <IP_DC> -u 'usuario' -p 'password' --groups

# Ver quién tiene sesión iniciada actualmente (Útil para buscar objetivos de sniffing/spoofing)
nxc smb <IP_DC> -u 'usuario' -p 'password' --loggedon-users
```

### BloodHound (El Mapa del Tesoro)
Esencial para visualizar relaciones de confianza complejas y rutas de escalada.
```bash
# Ingestor desde Linux (Python)
bloodhound-python -u 'usuario' -p 'password' -d dominio.local -ns <IP_DC> -c All

# Ingestor desde Windows (SharpHound.exe)
.\SharpHound.exe -c All
```
*   **Análisis:** En la interfaz de BloodHound, busca "Shortest Paths to Domain Admins".

---

## 🐚 3. PowerView (Enumeración desde PowerShell)
Si has ganado acceso a una máquina Windows unida al dominio.
```powershell
Import-Module .\PowerView.ps1

Get-NetDomain                       # Información general del dominio
Get-NetUser | select cn,description # Listar usuarios y sus descripciones
Get-NetComputer                     # Listar todos los equipos del dominio
Get-NetGroupMember "Domain Admins"  # Listar los administradores del dominio
Find-LocalAdminAccess               # Comprobar si tienes permisos de Admin Local en otras máquinas
```

---

## 🌐 4. DNS Interno
El DC suele actuar como servidor DNS. Puedes intentar descubrir nombres de otros servidores internos.
```bash
# Intentar transferencia de zona (AXFR)
dig axfr @<IP_DC> dominio.local

# Enumerar subdominios comunes
nmap -p 53 --script dns-brute --script-args dns-brute.domain=dominio.local <IP_DC>
```

> **Tip:** Presta mucha atención al campo **"description"** de los usuarios. Es muy común encontrar contraseñas temporales o pistas dejadas por administradores en las notas de los usuarios.
