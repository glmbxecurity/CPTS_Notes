---
title: Diccionarios y Wordlists
pubDate: '2025-11-26'
---

> **Tip:** Si una ruta no funciona, localiza el diccionario con: `locate nombre_del_diccionario`

## 📂 Rutas Confirmadas (Kali/Parrot)

### 🔑 Contraseñas (Passwords)
*   **Rockyou:** `/usr/share/wordlists/rockyou.txt`
*   **Seclists 1M:** `/usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords-1000000.txt`


### 🔎 Fuzzing Web (Directorios y Archivos)
*   **Dirbuster Medium (Recomendado):** `/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt`
*   **Common (Rápido):** `/usr/share/wordlists/dirb/common.txt`
*   **Raft Large Files:** `/usr/share/seclists/Discovery/Web-Content/raft-large-files.txt`

### 👤 Usuarios (Usernames)
*   **Genérico:** `/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt`
*   **Nombres comunes:** `/usr/share/seclists/Usernames/Names/names.txt`

### 🌐 Dominios y Subdominios
*   **Subdominios Top 110k:** `/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt`
*   **Deepmagic (Vhosts):** `/usr/share/seclists/Discovery/DNS/deepmagic.com-prefixes-top500.txt`

### 🎯 Específicos (LFI / SQLi / Parámetros)
*   **Parámetros LFI:** `/usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt`
*   **Inyección SQL:** `/usr/share/seclists/Fuzzing/Databases/SQLi/Generic-SQLi.txt`
*   **Nombres de Parámetros:** `/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt`

---

## 🛠️ Comandos de Utilidad
```bash
# Descomprimir rockyou (obligatorio en instalaciones nuevas)
sudo gunzip /usr/share/wordlists/rockyou.txt.gz

# Filtrar un diccionario para que solo tenga palabras de 8+ caracteres
awk 'length($0) >= 8' diccionario.txt > filtrado.txt

# Combinar dos diccionarios y quitar duplicados
cat dict1.txt dict2.txt | sort -u > nuevo_dict.txt
```
