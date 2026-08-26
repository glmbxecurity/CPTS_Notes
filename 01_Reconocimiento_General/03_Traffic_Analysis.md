---
title: Análisis de Tráfico y Archivos PCAP
pubDate: '2025-11-26'
---

Guía para analizar capturas de tráfico `.pcap` (Post-Explotación o CTF) y sniffing en tiempo real.

## 🔍 1. Búsqueda de Archivos (Post-Explotación)
Si tienes acceso a la máquina, busca capturas olvidadas. Suelen contener credenciales de servicios que el administrador estaba testeando o tráfico de otros usuarios.

```bash
find / -name "*.pcap*" 2>/dev/null
```

---

## 📡 2. Sniffing en tiempo real (Tcpdump)
Imprescindible para ver qué pasa "por debajo" cuando lanzas un exploit o esperas una conexión.

```bash
# Ver tráfico en interfaz local (Loopback) - Ideal para servicios internos o DBs locales
tcpdump -i lo -v

# Capturar tráfico de un puerto específico (ej: SMB) y guardarlo para Wireshark
tcpdump -i eth0 port 445 -w captura.pcap

# Leer fichero pcap filtrando por IP de origen
tcpdump -r captura.pcap src 10.10.10.5
```

---

## 🦈 3. Wireshark (Filtros y Trucos)

### Filtros Esenciales
| Filtro | Descripción |
| :--- | :--- |
| `http.request.method == "POST"` | Ver formularios enviados (logins). |
| `ip.addr == 10.10.10.5` | Filtrar por IP específica. |
| `tcp.port == 445` | Tráfico SMB (Archivos compartidos). |
| `frame contains "password"` | Busca la cadena literal en todo el paquete. |
| `http contains ".zip"` | Busca paquetes que mencionen archivos comprimidos. |

### Análisis Rápido
*   **Follow TCP Stream:** Click derecho -> **Follow -> TCP Stream**. Reconstruye toda la conversación. Ideal para leer chats, telnet o contraseñas FTP.
*   **Exportar Objetos:** *File -> Export Objects -> HTTP*. Permite descargar los archivos que la víctima se bajó por el navegador (ej: un .exe, un .zip, etc.).

---

## 💻 4. Tshark (Wireshark por terminal)
Si estás en una shell SSH sin entorno gráfico, `tshark` es indispensable.

```bash
# Leer un pcap y extraer solo las contraseñas de formularios POST
tshark -r captura.pcap -Y 'http.request.method == "POST"' -T fields -e http.file_data

# Extraer peticiones GET (URLs visitadas)
tshark -r captura.pcap -Y 'http.request.method == "GET"' -T fields -e http.host -e http.request.uri
```

---

## 🛠️ 5. Trucos rápidos (Sin herramientas pesadas)
```bash
# Ver texto legible dentro de un PCAP (Muy útil en CTFs para flag hunting)
strings captura.pcap | grep -iE "pass|pwd|login|user"

# Ver estadísticas rápidas del archivo (tamaño, duración, cantidad de paquetes)
capinfos captura.pcap
```
