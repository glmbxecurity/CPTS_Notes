---
title: SSH (Secure Shell - Puerto 22)
pubDate: '2026-08-26'
---

## ¿Qué es SSH?
**Secure Shell (SSH)** es el protocolo estándar para la administración remota de sistemas Linux de forma segura. Utiliza cifrado para proteger la sesión, pero su seguridad depende totalmente de la fortaleza de las contraseñas o de la protección de las llaves privadas.

### Riesgos principales
1. **Credenciales débiles:** Vulnerable a ataques de fuerza bruta si no hay protección contra intrusos (Fail2Ban).
2. **Llaves privadas expuestas:** Si un atacante obtiene un archivo `id_rsa`, puede acceder al sistema sin contraseña.
3. **Algoritmos obsoletos:** Versiones antiguas de SSH pueden permitir ataques de degradación o robo de sesión.

---

## 🔎 1. Enumeración y Auditoría del Servicio

### Nmap Scripts para SSH
```bash
nmap -p 22 -sV --script=ssh-hostkey,ssh-auth-methods,sshv1,ssh2-enum-algos,ssh-brute <TARGET_IP>
```

### Auditoría de Seguridad con `ssh-audit`
Herramienta de referencia para detectar algoritmos criptográficos débiles, intercambio de claves obsoleto y CVEs del daemon SSH:
```bash
# Vía paquete o repositorio
git clone https://github.com/jtesta/ssh-audit.git && cd ssh-audit
./ssh-audit.py <TARGET_IP>
```

### Verificación y Forzado de Métodos de Autenticación
```bash
# Ver con modo verbose (-v) los métodos que permite el servidor (publickey, password, etc.)
ssh -v usuario@<TARGET_IP>

# Forzar autenticación directa por contraseña (evita fallos si intenta claves locales primero)
ssh -v usuario@<TARGET_IP> -o PreferredAuthentications=password
```

---

## 🔑 2. Ataques de Credenciales

### Fuerza Bruta (Hydra)
```bash
# -t 4: Pocos hilos para evitar bloqueos por fail2ban o rate-limiting
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://<TARGET_IP> -t 4
```

### Cracking de Llaves Privadas Cifradas (Passphrase)
```bash
# 1. Extraer el hash de la llave id_rsa
ssh2john id_rsa > hash_ssh.txt

# 2. Crackear la passphrase con John the Ripper
john --wordlist=/usr/share/wordlists/rockyou.txt hash_ssh.txt
```

---

## 🚀 3. Conexión y Tips Tácticos

### Permisos y Uso de Llave Privada
SSH requiere que el archivo de la llave tenga permisos exclusivos `600`, de lo contrario rechazará la conexión:
```bash
chmod 600 id_rsa
ssh -i id_rsa usuario@<TARGET_IP>
```

### Conexión a Servidores Legados (Legacy Ciphers / KEX)
Si recibes errores como *"no matching key exchange method found"* o *"no matching host key type"*:
```bash
ssh -oHostKeyAlgorithms=+ssh-rsa -oPubkeyAcceptedAlgorithms=+ssh-rsa usuario@<TARGET_IP>
```

---

## 🔄 4. Túneles SSH (Pivoting Local)
Traer un puerto de la máquina víctima (ej. MySQL en el 3306) accesible solo localmente a tu máquina atacante:
```bash
ssh -L 3306:127.0.0.1:3306 usuario@<TARGET_IP> -i id_rsa
```

> **Tip:** Busca siempre en el directorio home del usuario carpetas `.ssh/` (ficheros `authorized_keys`, `known_hosts`) o archivos `.bash_history`, que suelen revelar conexiones previas hacia otros activos de la red interna.
