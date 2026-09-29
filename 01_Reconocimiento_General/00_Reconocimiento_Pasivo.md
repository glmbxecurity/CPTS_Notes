---
title: "Reconocimiento Pasivo y OSINT"
pubDate: '2026-08-26'
---

El reconocimiento pasivo recopila información sobre el objetivo sin interactuar directamente con sus sistemas ni generar registros de red defensivos.

## 🔍 1. Google Dorks y Recursos en la Nube

### Búsqueda de Activos Expuestos
* `site:target.com ext:pdf OR ext:docx OR ext:xlsx` (Documentación sensible)
* `site:target.com inurl:admin OR intitle:"index of"` (Paneles y listados de directorios)
* `site:target.com intext:"password" filetype:log` (Logs y credenciales en texto claro)
* `site:target.com inurl:conf OR inurl:env OR inurl:config` (Archivos de configuración)
* `site:target.com intext:"sql syntax near" OR intext:"syntax error"` (Fugas de errores SQL)

### Almacenamiento en la Nube Expuesto
```text
# AWS S3 Buckets
intext:"target_company" inurl:amazonaws.com

# Azure Blob Storage
intext:"target_company" inurl:blob.core.windows.net
```
* **GrayHatWarfare:** [https://buckets.grayhatwarfare.com/](https://buckets.grayhatwarfare.com/) (Buscador público de buckets abiertos para localizar backups, bases de datos o claves SSH `id_rsa`).

### Tabla de Operadores de Búsqueda Avanzada
| Operador | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `site:` | Limita la búsqueda al dominio especificado. | `site:example.com` |
| `inurl:` | Coincidencia en la URL. | `inurl:login` |
| `filetype:` / `ext:` | Filtra por extensión de archivo. | `filetype:pdf` |
| `intitle:` | Coincidencia en la etiqueta `<title>` de la web. | `intitle:"confidential report"` |
| `intext:` | Coincidencia en el cuerpo del texto HTML. | `intext:"password reset"` |
| `allintext:` | Exige que todas las palabras estén en el cuerpo. | `allintext:admin password reset` |
| `allinurl:` | Exige que todas las palabras estén en la URL. | `allinurl:admin panel` |
| `allintitle:` | Exige que todas las palabras estén en el título. | `allintitle:internal portal` |
| `cache:` | Muestra la versión en caché de Google. | `cache:example.com` |
| `AND` / `OR` / `NOT` | Operadores lógicos booleanos. | `site:example.com AND (inurl:admin OR inurl:login)` |
| `*` (comodín) | Reemplaza cualquier palabra. | `site:example.com filetype:pdf user* manual` |
| `" "` | Búsqueda de frase exacta. | `"information security policy"` |
| `-` | Excluye términos de la búsqueda. | `site:example.com -inurl:careers` |

---

## 📧 2. OSINT: Emails, Usuarios y Credenciales

* **theHarvester:** Emails, subdominios y direcciones IP.
  ```bash
  theHarvester -d target.com -b google,bing,linkedin,dnsdumpster -l 500
  ```
* **Phonebook.cz:** Búsqueda masiva de correos electrónicos, subdominios y URLs públicas.
* **Hunter.io:** Detección del patrón y formato de correos corporativos (ej. `nombre.apellido@empresa.com`).
* **Intelx.io:** Inteligencia de amenazas y búsqueda en dumps de datos filtrados.
* **HaveIBeenPwned:** Comprobación de correos corporativos en filtraciones públicas.
* **WaybackMachine (Archive.org):** Inspección de versiones históricas de la web en busca de endpoints deprecados o archivos JavaScript antiguos.

---

## 🌐 3. Dominio, DNS y Certificados SSL

### Información de Registro (WHOIS)
Identifica entidad propietaria, fechas de caducidad y datos de contacto:
```bash
whois inlanefreight.com
```
* **Campos clave:** `Domain Name`, `Registrar`, `Registrant Contact`, `Administrative Contact`, `Technical Contact`, `Creation and Expiration Dates`, `Name Servers`.

### Consultas DNS Pasivas con `dig` y `nslookup`
```bash
# Consultar servidores de correo (MX)
dig target.com MX
nslookup -type=MX target.com

# Consultar registros TXT (SPF, DKIM, DMARC, validaciones de dominio)
dig target.com TXT
```

| Comando DIG | Propósito |
| :--- | :--- |
| `dig domain.com A` | Recupera la dirección IPv4. |
| `dig domain.com AAAA` | Recupera la dirección IPv6. |
| `dig domain.com MX` | Identifica servidores de correo. |
| `dig domain.com NS` | Identifica servidores DNS autoritativos. |
| `dig domain.com TXT` | Registros de texto (SPF, verificaciones). |
| `dig domain.com CNAME` | Registro de alias canónico. |
| `dig domain.com SOA` | Registro de Inicio de Autoridad de la zona. |
| `dig @1.1.1.1 domain.com` | Consulta forzando un servidor DNS concreto. |
| `dig +trace domain.com` | Traza completa de la resolución recursiva DNS. |
| `dig -x 192.168.1.1` | Búsqueda inversa (Reverse PTR). |
| `dig +short domain.com` | Salida limpia en una sola línea (ideal para scripts). |
| `dig +noall +answer domain.com` | Muestra exclusivamente la sección de respuestas. |
| `dig domain.com ANY` | Solicita todos los registros disponibles de una sola vez. |

### Certificados de Transparencia (CT Logs) y `crt.sh`
Los logs públicos de SSL/TLS permiten descubrir subdominios activos e históricos:
```bash
# Extracción directa y parseo en JSON con jq
curl -s "https://crt.sh/?q=inlanefreight.com&output=json" | jq -r '.[].name_value' | sort -u

# Filtrar solo subdominios específicos (ej. dev, staging, test)
curl -s "https://crt.sh/?q=inlanefreight.com&output=json" | jq -r '.[] | select(.name_value | contains("dev")) | .name_value' | sort -u
```

### Enumeración de Subdominios por OSINT
```bash
# Subfinder (Rápido y moderno)
subfinder -d target.com

# Sublist3r
sublist3r -d target.com
```

---

## 🛠️ 4. Herramientas y Frameworks OSINT

### Shodan.io
Buscador de dispositivos conectados a internet (filtros: `hostname:"target.com"`, `org:"Empresa"`, `net:"1.2.3.0/24"`, `port:80,443`).

### FinalRecon
Framework modular de reconocimiento OSINT y perfilado de infraestructura:
```bash
git clone https://github.com/thewhiteh4t/FinalRecon.git
cd FinalRecon
pip3 install -r requirements.txt
chmod +x ./finalrecon.py
./finalrecon.py --help
```
