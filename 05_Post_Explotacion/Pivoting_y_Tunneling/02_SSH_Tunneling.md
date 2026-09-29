---
title: Túneles SSH y Redirección de Puertos
pubDate: 2026-05-22
---

## ¿Qué es el SSH Tunneling?
Es el uso del protocolo SSH para encapsular otro tráfico de red. Permite "saltar" firewalls que bloquean ciertos puertos, redirigiendo el tráfico a través de una conexión SSH cifrada y permitida.

### Beneficios
*   **Seguridad:** El tráfico viaja cifrado dentro de SSH.
*   **Evasión:** Permite acceder a servicios internos (ej: MySQL) que no están expuestos a Internet.
*   **Estabilidad:** SSH es un protocolo muy robusto y común en servidores.

---

## 🚀 1. Local Port Forwarding (`-L`)
**Uso:** Traer un puerto que solo escucha en la víctima (o en su red interna) a tu propia máquina Kali.

```bash
# Sintaxis: -L [Puerto_Local]:[IP_Remota]:[Puerto_Remoto]
ssh -L 8080:127.0.0.1:80 usuario@<IP_VICTIMA>
```
*   **Resultado:** Ahora puedes abrir tu navegador en `http://localhost:8080` y estarás viendo la web que corre internamente en el puerto 80 de la víctima.

---

## 🚀 2. Remote Port Forwarding (`-R`)
**Uso:** Hacer que un puerto de tu Kali sea accesible desde la máquina víctima. Muy útil para recibir Reverse Shells cuando la víctima no puede conectar directamente a tu IP.

```bash
# Sintaxis: -R [Puerto_En_Victima]:[IP_Atacante]:[Puerto_Atacante]
ssh -R 4444:127.0.0.1:4444 usuario@<IP_VICTIMA>
```
*   **Resultado:** Si la víctima ejecuta un comando hacia su propio puerto `localhost:4444`, el tráfico será redirigido a tu puerto 4444 local.

---

## 🚀 3. Dynamic Port Forwarding (`-D`)
**Uso:** Crear un túnel SOCKS que te permite navegar por **toda** la red a la que el servidor SSH tiene acceso.

```bash
# Crea un proxy SOCKS5 local en el puerto 1080
ssh -D 1080 usuario@<IP_VICTIMA>
```
*   **Resultado:** Configura **Proxychains** (en el puerto 1080) y podrás usar cualquier herramienta para atacar la red interna.

---

## 🛠️ 4. Tips para Túneles Persistentes

### Ejecución en segundo plano (Background)
Si no quieres que la terminal se quede bloqueada por la sesión SSH:
```bash
ssh -L 8080:127.0.0.1:80 usuario@<IP> -N -f
```
*   **-N:** Indica que no quieres ejecutar comandos remotos (solo abrir el túnel).
*   **-f:** Envía el proceso al segundo plano inmediatamente después de autenticar.

### Cerrar túneles en background
Si has lanzado un túnel con `-f` y quieres cerrarlo:
```bash
ps aux | grep ssh
kill <PID>
```

> **Tip:** Si el servidor SSH tiene deshabilitado el redireccionamiento de puertos (`AllowTcpForwarding no`), estos comandos fallarán.
