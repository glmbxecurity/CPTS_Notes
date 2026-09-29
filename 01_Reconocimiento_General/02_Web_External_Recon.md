---
title: "Reconocimiento Web y Externo"
pubDate: '2026-08-26'
---

Guía para reconocimiento externo de infraestructura web, enumeración DNS activa, fingerprinting de tecnologías, detección de WAF y descubrimiento de endpoints.

## 🌐 1. Enumeración DNS y Subdominios (Activo)

### Transferencia de Zona (AXFR)
Si el servidor DNS permite transferencias de zona no autenticadas, revelará toda la estructura interna de hosts y subdominios:
```bash
dig axfr @<IP_DNS> dominio.com
dig axfr @nsztm1.digi.ninja zonetransfer.me
host -l dominio.com <IP_DNS>
```

### Fuerza Bruta de Subdominios y Virtual Hosts (VHosts)
```bash
# DNSENUM con recursividad activada (-r)
dnsenum --enum inlanefreight.com -f /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -r

# Gobuster DNS (Subdominios reales en servidores de nombres)
gobuster dns -d dominio.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 20

# Gobuster VHOST (Virtual Hosting con anexado automático de dominio)
gobuster vhost -u http://inlanefreight.htb:81 -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt --append-domain -k

# Wfuzz (Fuzzing mediante cabecera Host)
wfuzz -c -f sub-fighter -w subdomains.txt -u http://target.com -H "Host: FUZZ.target.com" --hc 403,404
```

### Verificación de Subdominios Vivos (HTTPX)
```bash
cat subdominios.txt | httpx -title -status-code -content-length
```

---

## 🔍 2. Fingerprinting Web y Detección de WAF

### Herramientas de Perfilado Tecnológico
| Herramienta | Tipo | Propósito |
| :--- | :--- | :--- |
| `WhatWeb` | CLI | `whatweb -a 3 http://target.com` (Identifica CMS, servidor, frameworks). |
| `Wappalyzer` | Extensión / CLI | Perfilado rápido de librerías JS, analíticas y tecnologías del frontend/backend. |
| `Nikto` | CLI | `nikto -h inlanefreight.com -Tuning b` (`-Tuning b` ejecuta solo módulos de identificación de software). |
| `Nuclei` | CLI | `nuclei -u http://target.com -t exposures/ -t technologies/` |

### Banner Grabbing y Redirecciones
```bash
curl -I https://inlanefreight.com
```
> **Nota técnica:** Si la respuesta devuelve una cabecera `Location:` con redirección (ej. a `https://www.inlanefreight.com/`), se debe volver a lanzar el banner grabbing contra la nueva URL para extraer cabeceras específicas del servidor final.

### Detección de WAF (Web Application Firewall)
```bash
wafw00f inlanefreight.com -a
```

---

## 📂 3. Endpoints Estándar `/.well-known/`

Los estándares modernos exponen metadatos críticos de configuración, seguridad y autenticación en la ruta `/.well-known/`:

| Endpoint | Descripción |
| :--- | :--- |
| `/.well-known/security.txt` | Información de contacto del equipo de seguridad y programa de divulgación de vulnerabilidades. |
| `/.well-known/openid-configuration` | Configuración completa de OAuth 2.0 / OpenID Connect (endpoints de token, autorización y jwks). |
| `/.well-known/change-password` | Redirección oficial hacia el panel de cambio de credenciales de usuario. |
| `/.well-known/assetlinks.json` | Verificación de aplicaciones móviles asociadas al dominio. |
| `/.well-known/mta-sts.txt` | Política de seguridad estricta para servidores de transporte de correo (MTA-STS). |

---

## 🕷️ 4. Crawling y Recolección de Datos (Scrapy / ReconSpider)

Herramienta automatizada para rastrear sitios web y extraer correos, enlaces internos y archivos sensibles a un archivo `results.json`:
```bash
# Instalación
pip3 install scrapy
wget -O ReconSpider.zip https://academy.hackthebox.com/storage/modules/144/ReconSpider.v1.2.zip
unzip ReconSpider.zip

# Ejecución
python3 ReconSpider.py http://inlanefreight.com
```

---

## 📁 5. Ficheros Críticos y Descubrimiento de Parámetros

### Ficheros de Interés
* **Entornos de desarrollo:** `.git` (usar `git-dumper`), `.env`, `.vscode/`, `.svn/`.
* **Backups y configuración:** `config.php.bak`, `web.old.zip`, `backup.sql`, `phpinfo.php`, `web.config`.
* **Rutas públicas:** `/robots.txt`, `/sitemap.xml`.

### Descubrimiento de Parámetros Ocultos
```bash
# Arjun (Búsqueda ultrarrápida de parámetros GET/POST)
arjun -u http://target.com/page.php -m GET
```

### Clonado de Sitio para Análisis Local
```bash
httrack http://target.com -O /tmp/web_clone
```
