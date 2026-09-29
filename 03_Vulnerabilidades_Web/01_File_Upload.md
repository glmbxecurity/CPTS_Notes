---
title: "File Upload Attacks (Subida de Archivos)"
pubDate: '2026-08-26'
---

## Extension Upload Bypass

### Content-Type Bypass con BurpSuite
Cuando la aplicación web valida o sanitiza únicamente la cabecera `Content-Type`:

```http
# Modificar en Burp Suite para subir un webshell.php cuando solo permite imágenes:
Content-Type: image/png
```
