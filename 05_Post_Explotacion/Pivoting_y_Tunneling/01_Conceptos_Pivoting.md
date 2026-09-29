---
title: Conceptos de Pivoting y Proxychains
pubDate: 2026-05-22
---

## ¿Qué es el Pivoting?
El **Pivoting** consiste en usar una máquina ya comprometida (conocida como *Pivot* o *Jump Host*) para atacar otras máquinas en redes internas a las que no tienes acceso directo desde tu equipo de ataque.

### Tipos de redirección:
*   **Port Forwarding:** Mapeas un puerto de la red interna a un puerto local de tu Kali (ej: el puerto 80 del servidor interno aparece en tu localhost:8080).
*   **Dynamic Forwarding (SOCKS):** Creas un túnel que funciona como un "túnel ciego" para que tus herramientas (Nmap, Burp, Navegador) puedan navegar por toda la red remota a través de él.

---

## 🔎 1. Descubrimiento de Hosts Internos
Antes de pivotar, necesitas saber qué hay en la red interna. Si no tienes herramientas como Nmap en el host pivot, usa este script de Bash:

```bash
#!/bin/bash
# Barrido de ping manual para la red 10.10.10.0/24
for i in {1..254}; do
    timeout 1 bash -c "ping -c 1 10.10.10.$i" >/dev/null
    if [ $? -eq 0 ]; then
        echo "Host 10.10.10.$i is UP"
    fi
done
```

---

## ⛓️ 2. Configuración de Proxychains
**Proxychains** permite redirigir el tráfico de casi cualquier herramienta a través de un proxy SOCKS.

### Pasos para configurar:
1.  **Editar archivo:** `sudo nano /etc/proxychains4.conf`
2.  **Modo:** Comenta `strict_chain` y descomenta `dynamic_chain` (esto evita que el túnel se rompa si un proxy falla).
3.  **Configurar Proxy:** Al final del archivo, añade la IP y puerto de tu túnel:
    ```text
    # Ejemplo para un túnel SOCKS5 local en el puerto 1080
    socks5  127.0.0.1 1080
    ```

### Uso de herramientas:
```bash
# NOTA: Nmap a través de proxychains NO soporta SYN scan (-sS). Usa -sT (TCP Connect).
proxychains nmap -sT -Pn -p 445 10.10.10.5
```

---

## 🗺️ 3. Manipulación de Rutas (Network Routing)
Si tienes control total del sistema operativo y puedes crear interfaces virtuales o túneles VPN (como con Ligolo), puedes añadir rutas directamente a tu kernel:

```bash
# Añadir ruta estática en Linux (Atacante)
# Dice: "Para ir a la red .20.0, pasa por la IP del pivot .10.5"
sudo ip route add 10.10.20.0/24 via 10.10.10.5

# Verificar rutas activas
ip route show
```

> **Tip:** Proxychains solo funciona con conexiones **TCP**. No intentes hacer Pings (ICMP) o escaneos UDP a través de proxychains porque fallarán silenciosamente.
