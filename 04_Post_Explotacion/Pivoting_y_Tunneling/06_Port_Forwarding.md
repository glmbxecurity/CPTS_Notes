---
title: Herramientas de Redirección (Port Forwarding)
pubDate: 2026-05-22
---

## ¿Qué es la Redirección de Puertos?
El **Port Forwarding** es una técnica que permite reenviar peticiones de red de un puerto a otro, ya sea dentro del mismo equipo o hacia un servidor remoto. Es la pieza fundamental para exponer servicios ocultos tras un firewall durante un pentest.

---

## 🐚 1. Socat (La navaja suiza de Linux)
Es extremadamente potente y permite redirecciones rápidas sin necesidad de configurar complejos túneles.

```bash
# Redirigir el puerto 80 local al puerto 80 de una IP interna
# fork: permite múltiples conexiones
# reuseaddr: permite reiniciar el comando sin esperar a que el socket se libere
socat TCP-LISTEN:80,fork,reuseaddr TCP:10.10.20.5:80
```

---

## 🪟 2. Plink.exe (SSH para Windows CMD)
Es la versión de línea de comandos de PuTTY. Es ideal para realizar túneles SSH desde servidores Windows que no tienen un cliente SSH nativo.

```bash
# Redirigir un puerto interno reverso hacia tu Kali
plink.exe -R 80:127.0.0.1:80 -ssh root@<TU_IP_KALI>
```

---

## 🌐 3. Rpivot (SOCKS reverso sobre HTTP)
Rpivot permite crear un proxy SOCKS a través de una conexión HTTP. Es perfecto para saltar firewalls que inspeccionan el tráfico y solo permiten navegación web saliente.

1.  **En tu Kali (Servidor):**
    ```bash
    python2.7 server.py --proxy-port 1080 --server-port 9999
    ```
2.  **En la víctima (Cliente):**
    ```bash
    python2.7 client.py --server-addr <TU_IP_KALI> --server-port 9999
    ```
3.  **Uso:** Configura **Proxychains** para usar el puerto 1080 local.

---

## 🛠️ 4. Otras Herramientas Útiles
*   **FPipe:** Herramienta clásica de Windows para redirección de puertos simple.
    `fpipe -l 8080 -r 80 10.10.10.5`
*   **Gost:** Una alternativa moderna y multi-protocolo escrita en Go que permite encadenar múltiples proxies y túneles.

> **Tip:** Antes de elegir una herramienta, verifica si puedes usar herramientas nativas como **SSH** o **Netsh**, ya que tienen menos probabilidades de ser detectadas por el equipo de defensa (Blue Team).
