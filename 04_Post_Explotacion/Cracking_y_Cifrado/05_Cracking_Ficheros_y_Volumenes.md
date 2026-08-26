---
title: "Cracking de Archivos Protegidos y Volúmenes BitLocker"
pubDate: '2026-08-26'
---

Guía para localizar, extraer hashes y descifrar archivos protegidos (PDF, ZIP, SSH Keys, GZIP con OpenSSL) y volúmenes de disco cifrados con BitLocker.

---

## 🔎 1. Búsqueda de Archivos Cifrados en el Sistema

### Localización de Documentos Ofimáticos y Backups Protegidos:
```bash
for ext in $(echo ".xls .xls* .xltx .od* .doc .doc* .pdf .pot .pot* .pp* .zip .7z .rar .kdbx"); do 
    echo -e "\n[+] Buscando extension: " $ext
    find / -name "*$ext" 2>/dev/null | grep -v "lib\|fonts\|share\|core\|/usr"
done
```

### Localización de Claves Privadas SSH Expuestas:
```bash
# Búsqueda por expresión regular de cabeceras de llaves privadas
grep -rnE '^\-{5}BEGIN [A-Z0-9]+ PRIVATE KEY\-{5}$' /* 2>/dev/null
```

### Comprobar si una Llave SSH requiere Passphrase:
```bash
# Si solicita 'Enter passphrase', la llave está protegida. Si devuelve la clave pública, no tiene contraseña.
ssh-keygen -yf ~/.ssh/id_ed25519
```

---

## 🛠️ 2. Conversores `*2john` para Archivos Protegidos

Para localizar todos los extractores instalados en el sistema: `locate *2john*`

```bash
# Claves Privadas SSH (RSA, ECDSA, Ed25519)
ssh2john id_rsa > id_rsa.hash
john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.hash

# Documentos PDF
pdf2john documento.pdf > pdf.hash
john --wordlist=/usr/share/wordlists/rockyou.txt pdf.hash

# Archivos Comprimidos ZIP / RAR / 7z
zip2john archivo.zip > zip.hash
rar2john archivo.rar > rar.hash
7z2john archivo.7z > 7z.hash
john --wordlist=/usr/share/wordlists/rockyou.txt zip.hash

# Bases de Datos de Contraseñas KeePass (.kdbx)
keepass2john BaseDeDatos.kdbx > keepass.hash
john --wordlist=/usr/share/wordlists/rockyou.txt keepass.hash
```

---

## 🗜️ 3. Ficheros GZIP / Tar Cifrados con OpenSSL

Si el comando `file` devuelve `openssl enc'd data with salted password`:
```bash
file backup.gzip
# Salida: backup.gzip: openssl enc'd data with salted password
```

### Bucle de Fuerza Bruta para Descifrado Automático:
Prueba contraseñas del diccionario en un bucle; cuando una funciona, descifra y descomprime el contenido automáticamente:
```bash
for i in $(cat /usr/share/wordlists/rockyou.txt); do 
    openssl enc -aes-256-cbc -d -in backup.gzip -k "$i" 2>/dev/null | tar xz && echo "[+] Contraseña encontrada: $i" && break
done
```

---

## 🔐 4. Descifrado y Montaje de Unidades BitLocker (`.vhd`, `.img`, Discos)

Aplica tanto a imágenes virtuales (`.vhd`, `.vhdx`, `.img`) como a particiones físicas de Windows protegidas con BitLocker.

### Paso 1: Extracción del Hash de BitLocker
```bash
# Extraer hashes de la imagen
bitlocker2john -i Backup.vhd > backup.hashes

# Filtrar exclusivamente el hash correspondiente a la contraseña de usuario ($bitlocker$0)
grep "bitlocker\$0" backup.hashes > backup.hash
```

### Paso 2: Cracking con Hashcat (Modo 22100)
```bash
hashcat -a 0 -m 22100 backup.hash /usr/share/wordlists/rockyou.txt
```

### Paso 3: Montaje de la Unidad Descifrada en Linux (`dislocker`)
Una vez obtenida la contraseña en texto plano:

```bash
# 1. Instalar utilidades y crear puntos de montaje
sudo apt-get install dislocker -y
sudo mkdir -p /media/bitlocker /media/bitlockermount

# 2. Asociar la imagen a un dispositivo loopback
sudo losetup -f -P Backup.vhd
# (Comprobar qué dispositivo loop se asignó con: losetup -a, ej. /dev/loop0)

# 3. Descifrar el volumen con dislocker usando la contraseña rota
sudo dislocker /dev/loop0p1 -u'PASSWORD_OBTENIDA' -- /media/bitlocker

# 4. Montar el archivo descifrado (dislocker-file) en el sistema de archivos
sudo mount -o loop /media/bitlocker/dislocker-file /media/bitlockermount

# 5. Navegar por los archivos descifrados
cd /media/bitlockermount/
ls -la
```
