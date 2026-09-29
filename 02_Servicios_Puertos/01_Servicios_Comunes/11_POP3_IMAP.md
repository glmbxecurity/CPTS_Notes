---
title: POP3 & IMAP (Protocolos de Correo - Puertos 110, 143, 993, 995)
pubDate: '2026-08-26'
---

## ¿Qué son POP3 e IMAP?
* **POP3 (Post Office Protocol 3 - Puertos 110 TCP / 995 SSL):** Protocolo para descargar correos electrónicos del servidor al cliente local (por defecto elimina el correo del servidor tras la descarga).
* **IMAP (Internet Message Access Protocol - Puertos 143 TCP / 993 SSL):** Permite acceder, organizar en carpetas y gestionar correos directamente en el servidor manteniendo la sincronización entre múltiples dispositivos.

---

## ⚙️ Ficheros de Configuración y Directivas Críticas (Dovecot / Courier)

| Ajuste en `dovecot.conf` | Impacto de Seguridad |
| :--- | :--- |
| `auth_debug_passwords = yes` | **Crítico:** Registra las contraseñas enviadas en texto claro dentro de los logs del sistema. |
| `auth_verbose = yes` | Registra todos los intentos fallidos de autenticación. |
| `auth_anonymous_username` | Permite inicio de sesión sin contraseña utilizando el mecanismo SASL `ANONYMOUS`. |

---

## 🔎 1. Enumeración y Scripts Nmap

```bash
# Escaneo de puertos y scripts de capacidades / fuerza bruta
sudo nmap <TARGET_IP> -sV -p110,143,993,995 --script=pop3-capabilities,pop3-brute,imap-capabilities,imap-brute
```

---

## 📬 2. Interacción con IMAP (Puerto 143 / 993)

> **Regla Crítica de Interacción IMAP:** Cada comando que se envía al servidor IMAP **debe comenzar con un identificador único o número secuencial** (ej. `1 LOGIN ...`, `2 LIST ...`, `3 SELECT ...`), de lo contrario el servidor ignorará la petición.

### Conexión Interactiva (Texto Claro y Cifrado SSL)
```bash
# Conexión cifrada IMAPS (Puerto 993)
openssl s_client -connect <TARGET_IP>:imaps -crlf -quiet
openssl s_client -connect <TARGET_IP>:143 -starttls imap

# Enumeración automática de correos con cURL si dispones de credenciales
curl -k 'imaps://<TARGET_IP>' --user usuario:password -v
```

### Flujo de Lectura de Correos en IMAP:
```text
1 LOGIN <usuario> <password>     # Iniciar sesión
2 LIST "" *                      # Listar todos los buzones y carpetas disponibles
3 SELECT INBOX                   # Seleccionar la bandeja de entrada
4 FETCH 1 BODY[]                 # Volcar el contenido completo (cabeceras y cuerpo) del correo con ID 1
5 LOGOUT                         # Cerrar la sesión
```

### Tabla de Comandos IMAP:
| Comando | Descripción |
| :--- | :--- |
| `1 LOGIN username password` | Autenticación del usuario en el servidor. |
| `1 LIST "" *` | Lista todas las carpetas y directorios del buzón. |
| `1 SELECT <INBOX>` | Selecciona un buzón para leer sus mensajes. |
| `1 FETCH <ID> BODY[]` | Recupera el contenido íntegro del mensaje con el ID indicado. |
| `1 CREATE "Carpeta"` | Crea una nueva carpeta de buzón. |
| `1 DELETE "Carpeta"` | Elimina una carpeta de buzón. |
| `1 CLOSE` | Elimina definitivamente los correos marcados como `Deleted`. |
| `1 LOGOUT` | Cierra la sesión de forma limpia. |

---

## ✉️ 3. Interacción con POP3 (Puerto 110 / 995)

### Conexión Interactiva
```bash
# Texto plano (Puerto 110)
nc -nv <TARGET_IP> 110
telnet <TARGET_IP> 110

# Cifrado POP3S (Puerto 995)
openssl s_client -connect <TARGET_IP>:pop3s -crlf -quiet
```

### Flujo de Trabajo en POP3:
```text
USER admin
PASS secret123
STAT                  # Devuelve: +OK <numero_mensajes> <tamaño_total_bytes>
LIST                  # Muestra el ID y tamaño de cada mensaje
RETR 1                # Descarga y muestra el mensaje con ID 1
DELE 1                # Marca para borrar el mensaje 1 (opcional)
QUIT                  # Guarda cambios y cierra la sesión
```

### Tabla de Comandos POP3:
| Comando | Descripción |
| :--- | :--- |
| `USER <nombre>` | Especifica el usuario de la cuenta. |
| `PASS <clave>` | Especifica la contraseña para autenticar. |
| `STAT` | Solicita el número total de correos almacenados y su tamaño. |
| `LIST` | Lista todos los correos con su respectivo ID y tamaño en bytes. |
| `RETR <id>` | Solicita al servidor la entrega completa del mensaje `<id>`. |
| `DELE <id>` | Marca el mensaje `<id>` para ser eliminado al cerrar sesión. |
| `CAPA` | Muestra la lista de capacidades y extensiones del servidor POP3. |
| `RSET` | Restablece las marcas de borrado previas sin cerrar la conexión. |
| `QUIT` | Cierra la sesión y purga los mensajes marcados para borrado. |
