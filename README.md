# 🛡️ CPTS Notes & HTB Writeups

> Repositorio personal de apuntes técnicos, metodologías y guías de explotación orientadas a la obtención de la certificación **Certified Penetration Testing Specialist (CPTS)** de [Hack The Box](https://www.hackthebox.com/), junto con la resolución detallada de máquinas y entornos de laboratorio (*HTB Writeups*).

---

## 🎯 Propósito del Repositorio

Este repositorio actúa como una **bóveda de conocimiento (Obsidian Vault)** estructurada siguiendo las fases del estándar **PTES** (*Penetration Testing Execution Standard*) y la ruta oficial **Penetration Tester Job Role Path** de HTB Academy. 

Su diseño prioriza:
* **Comandos y sintaxis exacta:** Flags, opciones avanzadas y oneliners listos para su uso en auditorías.
* **Metodología y fundamentos:** Explicación técnica del *por qué* de cada vector de ataque antes del *cómo*.
* **Sincronización automatizada:** Integración directa con el portal web [glmbxecurity](https://github.com/glmbxecurity/glmbx-web).

---

## 📂 Estructura del Repositorio

```text
CPTS_Notes/
├── 00_Fundamentos_y_Metodologias/   # Marco legal, Pre-engagement, PTES, WSTG, MITRE y organización
├── 01_Reconocimiento_General/       # OSINT, DNS pasivo, Nmap avanzado, 14 categorías NSE y Fuzzing
├── 02_Servicios_Puertos/            # Enumeración y explotación profunda puerto por puerto (40+ servicios)
│   ├── 01_Servicios_Comunes/        # FTP, SMB, SSH, MySQL, SMTP, SNMP, Redis, NFS, Rsync, Telnet, POP3/IMAP
│   ├── 02_Windows_Especificos/      # RDP, WinRM, MSSQL, Rejetto HFS, Windows Critical Exploits
│   ├── 03_Infraestructura_Web/      # Apache Tomcat, WebDAV, Git Expuesto
│   ├── 04_Active_Directory/         # AD Enumeration, AD Exploitation, Servicios AD
│   └── 05_Otros_Servicios_e_Infraestructura.md # Oracle TNS (ODAT), IPMI (RAKP) y R-Services
├── 03_Vulnerabilidades_Web/         # Metodologías de explotación web (File Upload, SQLi, XSS, SSRF...)
├── 04_Post_Explotacion/             # Técnicas tras obtener acceso inicial
│   ├── Cracking_y_Cifrado/          # Hashes (Hashcat/John), Cracking de Ficheros/BitLocker y Red (NetExec)
│   ├── Pivoting_y_Tunneling/        # SSH Tunneling, Ligolo-ng, Chisel, Netsh y Port Forwarding
│   ├── Privilege_Escalation/        # Escalada de privilegios en Linux y Windows
│   └── Shells_y_Transferencias/     # Reverse shells, TTY, Msfvenom, Transferencias cifradas y Metasploit
├── 06_Scripts/                      # Scripts de automatización y sincronización con glmbx-web
└── 10_HTB_writeups/                 # Resoluciones técnicas y writeups de máquinas de Hack The Box
```

---

## ⚙️ Automatización y Sincronización con la Web

En la carpeta [`06_Scripts/`](./06_Scripts/) se incluyen herramientas en Python para publicar automáticamente contenido hacia el repositorio de la web:

1. **Sincronización de Notas Técnicas (`sync_notes.py`)**:
   Valida el Frontmatter YAML de Astro (`title`, `pubDate`) y sincroniza los cambios locales:
   ```bash
   ./06_Scripts/sync_notes.py --git
   ```

2. **Sincronización de Writeups (`sync_writeups.py`)**:
   Detecta nuevas resoluciones de máquinas en `10_HTB_writeups/`, normaliza metadatos (plataforma, dificultad, fecha) y migra capturas:
   ```bash
   ./06_Scripts/sync_writeups.py --git
   ```

---

## 🔒 Aviso Legal y Ético

Todo el contenido, comandos y técnicas documentadas en este repositorio están destinados **única y exclusivamente para fines educativos, investigación en ciberseguridad, certificaciones y pruebas de penetración autorizadas**. El autor no se hace responsable del uso indebido de la información aquí expuesta.
