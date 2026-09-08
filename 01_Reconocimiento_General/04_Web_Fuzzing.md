---
title: Metodología Web y Fuzzing
pubDate: '2025-11-26'
---

## 📋 Checklist Rápido
1.  **Tecnologías:** `whatweb`, Wappalyzer.
2.  **Fuzzing Directorios:** `gobuster`, `feroxbuster`, `ffuf`.
3.  **Fuzzing Subdominios/VHosts:** `wfuzz`, `gobuster vhost`.
4.  **Archivos Sensibles:** `robots.txt`, `sitemap.xml`, `.git/`, `.env`.
5.  **Parámetros:** Buscar `?id=`, `?file=`, `?url=`, `?cmd=`.

---

## 🛠️ Fuzzing Cheatsheet

### 1. Gobuster (Directorios y VHosts)
Ideal por su sencillez y rapidez en enumeración inicial.
```bash
# Enumeración de directorios con extensiones
gobuster dir -u http://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html,bak,sh,old

# Enumeración de VHosts (Virtual Hosting)
gobuster vhost -u http://target.com -w /usr/share/wordlists/seclists/Discovery/DNS/namelist.txt
```

### 2. FFuf (El más potente y versátil)
FFuf es el estándar actual por su capacidad de filtrado y velocidad.

```bash
# Directorios (Recursivo)
ffuf -u http://target.com/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -recursion

# VHosts con filtrado de tamaño (Para evitar falsos positivos)
# Cambia {size} por el valor que se repita constantemente
ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/namelist.txt -H "Host: FUZZ.target.com" -u http://target.com -fs {size}

# Fuzzing de parámetros GET
ffuf -u http://target.com/admin.php?FUZZ=test -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt

# Fuzzing de valores en POST (Login Bruteforce)
# -fr: Filtra respuestas que contengan "Login failed"
ffuf -u http://target.com/login.php -X POST -d "username=admin&password=FUZZ" -w /usr/share/wordlists/rockyou.txt -fr "Login failed"
```

### 3. Wfuzz (Clásico para VHosts y parámetros)
```bash
# Subdominios/VHosts
wfuzz -c -f sub-fighter -w subdomains.txt -u http://target.com -H "Host: FUZZ.target.com" --hc 403,404

# Directorios con recursividad (Profundidad 2)
wfuzz -c -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -u http://target.com/FUZZ --hc 404 -R 2
```

### 4. Feroxbuster (El mejor para recursividad)
Si quieres lanzar un comando y olvidarte, feroxbuster es el más inteligente gestionando la recursividad.
```bash
feroxbuster -u http://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt -t 50
```

---

## 💡 Técnicas Avanzadas

### Bypass de User-Agent
A veces el servidor bloquea escáneres conocidos (como el propio Nmap o Gobuster). Prueba simulando un navegador real:
```bash
curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" http://target.com
```

### Enumeración de Emails
```bash
# Script de nmap para recolectar emails de la web
nmap -p80 --script http-email-harvest <target>
```

### Extensiones recomendadas para Fuzzing (`-x`)
*   **Web:** `php, html, aspx, jsp, js`
*   **Archivos de texto:** `txt, pdf, docx, xlsx`
*   **Configuración y Backups:** `bak, old, zip, gz, tar, conf, env, sql`
