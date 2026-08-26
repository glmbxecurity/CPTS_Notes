---
title: "Cracking de Hashes, Modos y Reglas (John & Hashcat)"
pubDate: '2026-08-26'
---

Guía técnica de cracking de hashes offline, modos de ataque en GPU/CPU (diccionario, combinatorio, máscara), modo Single de John, reglas y generación de diccionarios con CeWL.

---

## 🔎 1. Identificación del Tipo de Hash

Antes de lanzar cualquier ataque, identifica la firma del algoritmo:
```bash
# Con Hash-ID
hashid 193069ceb0461e1d40d216e32c79c704
hashid -j 193069ceb0461e1d40d216e32c79c704          # Muestra el modo correspondiente de John/Hashcat

# Con Hash Identifier de Python
hash-identifier
```

---

## 🛠️ 2. John the Ripper (CPU Cracking)

### Modo Single (Basado en Contexto del Usuario)
Diseñado específicamente para cuentas de Linux. Genera candidatos de contraseña basados en el nombre de usuario, carpeta home y campos GECOS (nombre completo) aplicando mutaciones rápidas (ej. para `Bob Smith` prueba `Smith1`, `bob2026`):
```bash
# Aislar la línea del archivo passwd/shadow objetivo
echo 'r0lf:$6$ues25dIanlctrWxg$nZHVz2z4kCy1760Ee28M1xtHdGoy0C2cYzZ8l2sVa1kIa8K9gAcdBP.GI6ng/qA4oaMrgElZ1Cb9OeXO4Fvy3/:0:0:Rolf Sebastian:/home/r0lf:/bin/bash' > passwd_single

# Ejecutar modo single
john --single passwd_single
```

### Modo Wordlist y Especificación de Formato
```bash
# Ataque por diccionario estándar
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Forzar formato específico
john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Ver contraseñas ya rotas en la base de datos local
john --show hashes.txt
```

---

## ⚡ 3. Hashcat (GPU Cracking)

### Sintaxis Base y Modos de Ataque (`-a`)
```bash
hashcat -a <MODO_ATAQUE> -m <TIPO_HASH> <HASH_O_FICHERO> <DICCIONARIO_O_MASCARA>
```

| Parámetro `-a` | Modo de Ataque | Descripción |
| :--- | :--- | :--- |
| `-a 0` | **Straight / Wordlist** | Ataque de diccionario clásico línea por línea. |
| `-a 1` | **Combination** | Combina palabras de dos diccionarios (ej. `palabra1 + palabra2`). |
| `-a 3` | **Brute-force / Mask** | Fuerza bruta personalizada mediante patrones de máscara. |
| `-a 6` | **Hybrid Wordlist + Mask** | Añade sufijos/máscaras al final de cada palabra del diccionario. |
| `-a 7` | **Hybrid Mask + Wordlist** | Añade prefijos/máscaras al inicio de cada palabra del diccionario. |

### Modos de Hashes Habituales (`-m`)
| Algoritmo | Modo `-m` | Ejemplo |
| :--- | :--- | :--- |
| **MD5** | `0` | `hashcat -a 0 -m 0 hash.txt rockyou.txt` |
| **NTLM (Windows)** | `1000` | `hashcat -a 0 -m 1000 hash.txt rockyou.txt` |
| **Kerberos 5 AS-REP (krb5asrep)** | `18200` | `hashcat -a 0 -m 18200 asrep.txt rockyou.txt` |
| **Kerberos 5 TGS (Kerberoast)** | `13100` | `hashcat -a 0 -m 13100 tgs.txt rockyou.txt` |
| **SHA-256** | `1400` | `hashcat -a 0 -m 1400 hash.txt rockyou.txt` |
| **SHA-512 ($6$ Linux Shadow)** | `1800` | `hashcat -a 0 -m 1800 hash.txt rockyou.txt` |
| **Bcrypt ($2a$ / $2y$)** | `3200` | `hashcat -a 0 -m 3200 hash.txt rockyou.txt` |
| **MSSQL (2012 / 2014)** | `17300` | `hashcat -a 0 -m 17300 hash.txt rockyou.txt` |
| **IPMI 2.0 RAKP** | `7300` | `hashcat -a 0 -m 7300 hash.txt rockyou.txt` |
| **BitLocker** | `22100` | `hashcat -a 0 -m 22100 hash.txt rockyou.txt` |

---

## 🎭 4. Ataques de Máscara (Mask Attacks)

Símbolos de conjuntos de caracteres en Hashcat:

| Símbolo | Conjunto de Caracteres | Rango |
| :--- | :--- | :--- |
| `?l` | Letras minúsculas | `abcdefghijklmnopqrstuvwxyz` |
| `?u` | Letras mayúsculas | `ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| `?d` | Dígitos | `0123456789` |
| `?h` | Hexadecimal minúscula | `0123456789abcdef` |
| `?H` | Hexadecimal mayúscula | `0123456789ABCDEF` |
| `?s` | Símbolos y caracteres especiales | `!"#$%&'()*+,-./:;<=>?@[\]^_\`{\|}~` |
| `?a` | Todos los anteriores imprimibles | `?l?u?d?s` |
| `?b` | Todos los bytes posibles | `0x00 - 0xff` |

### Ejemplos Prácticos de Máscara:
```bash
# Patrón: 1 Mayúscula, 4 minúsculas, 1 dígito, 1 símbolo (ej. Admin1!)
hashcat -a 3 -m 0 hash.txt '?u?l?l?l?l?d?s'

# Definir conjunto personalizado (-1) con mayúsculas y dígitos:
hashcat -a 3 -m 7300 hash.txt -1 ?d?u '?1?1?1?1?1?1?1?1'
```

---

## 📜 5. Uso de Reglas (Rules)

Las reglas aplican mutaciones lógicas a las palabras del diccionario (capitalizaciones, sustituciones `e -> 3`, números al final):

```bash
# Listar reglas instaladas en el sistema
ls -l /usr/share/hashcat/rules/

# Ataque con la regla best64 (64 transformaciones estándar más probables)
hashcat -a 0 -m 1000 hash.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# Reglas avanzadas
hashcat -a 0 -m 1000 hash.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/rockyou-30000.rule
```

---

## 🔠 6. Generación de Diccionarios a Medida

### Extracción de Palabras Web con CeWL
```bash
# Rastrear una web con profundidad 4 y extraer palabras con longitud mínima de 6 caracteres
cewl https://www.inlanefreight.com -d 4 -m 6 --lowercase -w inlane.wordlist
```

### Diccionarios Compuestos con Hashcat (`-a 1`)
Permite fusionar dos listas de palabras (ej. datos OSINT de empleados con fechas/años) combinándolas en la salida estándar:
```bash
# Combina cada palabra de lista1 con lista2 aplicando mayúscula inicial (-j c -k c)
hashcat -a 1 lista1.txt lista2.txt -j c -k c --stdout > compuesta.txt

# Lanzar ataque con el diccionario compuesto resultante aplicando una regla personalizada
hashcat -a 0 -m 0 hash.txt compuesta.txt -r custom.rule
```
