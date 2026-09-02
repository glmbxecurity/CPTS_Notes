---
title: "Generación de Diccionarios y Wordlists a Medida"
pubDate: '2026-08-31'
---

Guía técnica para la creación, extracción y personalización de diccionarios dirigidos (targeted wordlists) durante evaluaciones de seguridad y auditorías de contraseñas.

---

## Extracción de Palabras Web (CeWL)

**CeWL** (Custom Word List generator) es una herramienta en Ruby que rastrea un sitio web hasta una profundidad específica y extrae palabras únicas para armar un diccionario temático contextualizado en la empresa objetivo.

### Comandos y Opciones Esenciales
```bash
# Extracción básica (profundidad 2, longitud mínima 6 caracteres)
cewl https://example.com -d 2 -m 6 -w custom_wordlist.txt

# Extracción en minúsculas y guardando recuento de ocurrencias
cewl https://example.com -d 3 -m 6 --lowercase -c -w wordlist_count.txt

# Extraer también correos electrónicos encontrados en la web
cewl https://example.com -d 2 -m 6 -e --email_file emails.txt -w words.txt

# Seguir enlaces externos/subdominios y autenticarse en el sitio
cewl http://intranet.local/portal -d 2 -m 7 -a "admin:password123" --auth_type basic -w intranet.txt
```

---

## Generación por Patrones y Conjuntos (Crunch)

**Crunch** permite generar listas de palabras basadas en longitud mínima, máxima y patrones específicos utilizando máscaras y conjuntos de caracteres.

### Sintaxis de Marcadores de Patrón en Crunch:
* `@` : Letras minúsculas (`[a-z]`)
* `,` : Letras mayúsculas (`[A-Z]`)
* `%` : Números (`[0-9]`)
* `^` : Caracteres especiales

### Ejemplos Prácticos
```bash
# Generar todas las combinaciones numéricas de 8 dígitos (ej. teléfonos / PINs)
crunch 8 8 0123456789 -o pins.txt

# Generar contraseñas con patrón específico: "Corp" + 4 dígitos + 1 símbolo
# (ej. Corp2024!, Corp1234#)
crunch 9 9 -t Corp%%%%^ -o passwords_pattern.txt

# Generar combinaciones basadas en un charset específico con longitud de 4 a 6
crunch 4 6 abcdef123456 -o custom_hex.txt

# Dividir el diccionario resultante en bloques de tamaño específico (ej. archivos de 50MB)
crunch 8 8 -t pass%%%% -b 50mb -o START
```

---

## Diccionarios Dirigidos por OSINT (CUPP)

**CUPP** (Common User Passwords Profiler) genera diccionarios personalizados basados en datos biográficos y contextuales obtenidos durante la fase de reconocimiento/OSINT sobre un objetivo (nombres, fechas de nacimiento, nombres de mascotas, empresa, etc.).

```bash
# Ejecutar asistente interactivo de preguntas
cupp -i

# Descargar y parsear filtraciones/listas estándar con CUPP
cupp -l
```

---

## Fusión y Combinatoria de Listas (Hashcat Combinator)

Permite fusionar dos diccionarios independientes (ej. lista de palabras clave corporativas + lista de años/fechas o terminaciones comunes) para generar candidatos compuestos.

```bash
# Combinar dos listas enviando el resultado a stdout
hashcat -a 1 lista1.txt lista2.txt --stdout > combinadas.txt

# Combinar aplicando transformaciones (mayúscula al inicio en ambas partes: -j c -k c)
hashcat -a 1 palabras.txt anios.txt -j c -k c --stdout > passwords_compuestas.txt
```

---

## Filtrado, Manipulación y Limpieza de Wordlists

Comandos estándar en Linux para procesar, limpiar y optimizar diccionarios antes de usarlos en herramientas de cracking o fuerza bruta.

```bash
# Filtrar contraseñas con longitud mínima de 8 y máxima de 20 caracteres
awk 'length($0) >= 8 && length($0) <= 20' wordlist.txt > wordlist_filtrada.txt

# Convertir todo a minúsculas
tr '[:upper:]' '[:lower:]' < wordlist.txt > wordlist_minusculas.txt

# Eliminar caracteres no imprimibles o corruptos
tr -cd '[:print:]\n' < wordlist.txt > wordlist_limpia.txt

# Unir dos o más listas eliminando duplicados
sort -u list1.txt list2.txt list3.txt -o wordlist_unica.txt

# Desduplicar manteniendo el orden original (muy rápido con AWK)
awk '!seen[$0]++' wordlist.txt > wordlist_sin_duplicados.txt
```

## Username Anarchy
Con esta herramienta podemos convertir una lista de nombres en una potencial lista de usuarios basandose en patrones conocidos. Ejemplo, nombre: John Doe, usuarios posibles: jdoe, john.doe, doe.j, etc.

Mirar el repositorio y la ayuda porque tiene varios patrones y maneras de utilizarlo, como pasarle nombre y apellido, el country, etc.
```bash
git clone https://github.com/urbanadventurer/username-anarchy
```

Ejemplo 1:
```bash
./username-anarchy --input-file ./test-names.txt
```