---
title: Checklist de Escalada de Privilegios en Windows
pubDate: 2026-05-22
---

## ¿Qué es la Escalada de Privilegios en Windows?
Es el proceso de saltar de una cuenta con acceso limitado (como un usuario local o una cuenta de servicio IIS) a una cuenta con control total del sistema, generalmente `Administrator` o `NT AUTHORITY\SYSTEM`.

### Riesgos principales
1.  **Control de la Máquina:** Acceso total a archivos, procesos y registros.
2.  **Extracción de Hashes:** Obtención de la SAM o volcado de LSASS para comprometer otras cuentas.
3.  **Compromiso del Dominio:** Si la máquina está en un entorno AD, el acceso SYSTEM permite robar tickets o credenciales de otros usuarios conectados.

---

## 🚀 1. Enumeración Rápida & Automatizada
No reinventes la rueda; usa herramientas que analicen el sistema por ti:

*   **WinPEAS:** `winPEASany.exe` o `winPEAS.ps1`. Es la herramienta más completa.
*   **Seatbelt:** Muy potente para auditorías (requiere .NET).
*   **PrivescCheck:** Script de PowerShell que no requiere privilegios administrativos.
*   **SharpUp:** Busca configuraciones erróneas de servicios y binarios.

---

## 🔎 2. Enumeración Manual (Información Crítica)

### Sistema y Parches
```powershell
systeminfo
wmic qfe get Caption,Description,HotFixID,InstalledOn # Listar actualizaciones instaladas
```

### Usuarios y Privilegios
```powershell
whoami /priv        # ¡CRÍTICO! Busca: SeImpersonate, SeDebug, SeBackup
whoami /groups      # ¿Perteneces a algún grupo inusual?
net user            # Listar usuarios del sistema
net localgroup Administradores # Ver quién es administrador
```

### Red y Puertos Internos
```powershell
ipconfig /all
netstat -ano        # Ver puertos escuchando solo localmente (ej: DBs)
```

---

## 🛠️ 3. Abusando de Privilegios (Whoami /priv)

### SeImpersonatePrivilege / SeAssignPrimaryToken
Permite suplantar los privilegios de otro usuario. Muy común en cuentas de servicio.
*   **Exploits:** Juicy Potato (Win antiguos), Rogue Potato, PrintNightmare (CVE-2021-34527).

### SeDebugPrivilege
Permite interactuar con cualquier proceso en memoria.
*   **Ataque:** Volcar el proceso `lsass.exe` con **Mimikatz** o Procdump para extraer contraseñas en texto claro y hashes NTLM.

### SeBackupPrivilege / SeRestorePrivilege
Permite leer y escribir CUALQUIER archivo sin importar sus permisos.
*   **Ataque:** Hacer una copia de seguridad de las colmenas `SAM` y `SYSTEM` del registro para extraer los hashes localmente.

---

## ⚙️ 4. Configuraciones Erróneas de Servicios

### Unquoted Service Paths (Rutas sin comillas)
Si la ruta de un servicio tiene espacios y no está entre comillas (ej: `C:\Program Files\App Folder\bin.exe`).
*   **Ataque:** Si tienes permisos de escritura en `C:\Program Files\`, puedes subir un archivo llamado `App.exe` que el sistema ejecutará en lugar del binario real.

### AlwaysInstallElevated (Registro)
Si estas dos llaves del registro están activas, cualquier usuario puede instalar un `.msi` con privilegios de SYSTEM.
```powershell
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```
*   **Ataque:** Genera un `.msi` malicioso con Msfvenom y ejecútalo.

---

## 🔑 5. Archivos de Configuración y Credenciales
*   **Búsqueda de contraseñas:** `findstr /si password *.xml *.config *.txt`
*   **Registro de Windows:** Busca credenciales de autologin o sesiones de Putty/VNC guardadas.
*   **Unattend.xml:** Archivos de instalación automática que a menudo contienen la clave de administrador en Base64 o texto claro.

---

## 🧪 6. Kernel Exploits
Úsalos como último recurso si el sistema está desactualizado.
*   **Herramienta:** **WES-NG** (Windows Exploit Suggester).
*   **Vulnerabilidades clásicas:** EternalBlue (MS17-010), BlueKeep (RDP).

> **Tip:** Antes de intentar un exploit de Kernel que pueda tirar la máquina, agota todas las vías de configuraciones erróneas (servicios, privilegios, archivos de configuración).
