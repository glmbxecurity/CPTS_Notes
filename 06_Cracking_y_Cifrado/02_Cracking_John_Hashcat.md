---
title: "Cracking de Hashes, Modos y Reglas (John & Hashcat)"
pubDate: '2026-08-26'
---

Guía técnica de cracking de hashes offline, modos de ataque en GPU/CPU (diccionario, combinatorio, máscara), modo Single de John y mutaciones con reglas.

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

# Ataque en modo Single con formato explícito
john --single --format=sha512crypt passwd_single
```

### Modo Wordlist y Especificación de Formato
```bash
# Ataque por diccionario estándar
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Forzar formato específico si no lo autodetecta
john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Ver contraseñas ya rotas en la base de datos local
john --show hashes.txt
```

---

## ⚡ 3. Hashcat (GPU Cracking)

Sintaxis general:
```bash
hashcat -a <MODO_ATAQUE> -m <TIPO_HASH> <HASH_O_FICHERO> <DICCIONARIO_O_MASCARA>
```

### Modos de Ataque (`-a`)
| Modo | Nombre | Descripción |
| :--- | :--- | :--- |
| `-a 0` | **Straight / Wordlist** | Ataque de diccionario clásico línea por línea. |
| `-a 1` | **Combination** | Combina palabras de dos diccionarios (ej. `palabra1 + palabra2`). |
| `-a 3` | **Brute-Force / Mask** | Genera combinaciones basadas en patrones/posiciones de caracteres. |
| `-a 6` | **Hybrid Wordlist + Mask** | Añade sufijos/máscaras al final de cada palabra del diccionario. |
| `-a 7` | **Hybrid Mask + Wordlist** | Añade prefijos/máscaras al inicio de cada palabra del diccionario. |

### Tipos de Hash Comunes (`-m`)
| Modo (`-m`) | Tipo de Hash / Algoritmo |
| :--- | :--- |
| `0` | MD5 |
| `100` | SHA1 |
| `1000` | NTLM (Windows local / SAM / NTDS) |
| `1800` | SHA512-Crypt (Linux `/etc/shadow` `$6$`) |
| `3200` | bcrypt (Linux `/etc/shadow` `$2b$`) |
| `13100` | Kerberos 5 TGS-REP (Kerberoasting) |
| `18200` | Kerberos 5 AS-REP (AS-REPRoasting) |

---

## 🎭 4. Ataques por Máscara (Mask Attacks)

### Charsets Incorporados
* `?l` = Minúsculas `[a-z]`
* `?u` = Mayúsculas `[A-Z]`
* `?d` = Dígitos `[0-9]`
* `?h` = Hexadecimal minúscula `[0-9a-f]`
* `?H` = Hexadecimal mayúscula `[0-9A-F]`
* `?s` = Caracteres especiales y puntuación
* `?a` = Todos los caracteres imprimibles (`?l?u?d?s`)
* `?b` = Todos los bytes (`0x00 - 0xff`)

### Ejemplos Prácticos
```bash
# Fuerza bruta: 8 caracteres minúsculas fijos (?l?l?l?l?l?l?l?l):
hashcat -a 3 -m 0 hash.txt ?l?l?l?l?l?l?l?l

# Máscara compleja: Mayúscula + 4 minúsculas + 2 dígitos + 1 símbolo (ej. Spring23!):
hashcat -a 3 -m 1000 hash.txt '?u?l?l?l?l?d?d?s'

# Longitud incremental (de 6 a 8 dígitos numéricos):
hashcat -a 3 -m 1000 hash.txt --increment --increment-min 6 --increment-max 8 '?d?d?d?d?d?d?d?d'

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

### Crackstation
Suele tener millones de hashes de contraseñas, no esta de mas mirar ahi por si acaso. parece ser que da buenos resultados con hashes NTLM
https://crackstation.net/