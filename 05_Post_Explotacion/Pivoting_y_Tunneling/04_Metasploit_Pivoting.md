---
title: Pivoting con Metasploit (Autoroute)
pubDate: 2026-05-22
---

## ¿Qué es el Pivoting en Metasploit?
Es la capacidad de Metasploit para utilizar una sesión activa de **Meterpreter** como puente para atacar otros sistemas en redes internas. Metasploit permite gestionar rutas de forma interna para que sus módulos (scanners, exploits) puedan alcanzar objetivos que no son visibles desde el exterior.

---

## 🚀 1. Configurar Rutas (Autoroute)
Una vez tengas tu sesión de Meterpreter, debes informar a Metasploit sobre la existencia de la red interna.

```bash
# Dentro de la sesión Meterpreter:
run autoroute -s 192.168.1.0/24   # Añade la red interna
run autoroute -p                  # Verifica que la ruta se ha creado
```

---

## ⛓️ 2. Servidor SOCKS (Proxy)
Para usar herramientas externas (ej: Nmap o el Navegador) a través de la sesión de Metasploit.

1.  Manda la sesión al fondo: `background`.
2.  Usa el módulo de proxy:
    ```bash
    use auxiliary/server/socks_proxy
    set SRVPORT 1080
    set VERSION 5
    run
    ```
3.  Configura **Proxychains** en tu Kali para usar el puerto 1080.

---

## 🎯 3. Port Forwarding (Mapeo Individual)
Útil para traer un servicio específico (ej: una base de datos) a tu propia máquina.

```bash
# Dentro de Meterpreter:
# Trae el puerto 80 de la IP interna .10 al puerto 8080 de tu Kali
portfwd add -l 8080 -p 80 -r 192.168.1.10

# Listar mapeos activos
portfwd list
```

---

## 🔎 4. Escaneo desde Metasploit
Con las rutas configuradas en `autoroute`, ya puedes lanzar módulos de escaneo internos:

```bash
# Escaneo de puertos TCP interno
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set THREADS 10
run
```

> **Tip:** Las rutas de `autoroute` solo afectan a los módulos internos de Metasploit. Si quieres usar herramientas externas, **debes** levantar el servidor SOCKS.
