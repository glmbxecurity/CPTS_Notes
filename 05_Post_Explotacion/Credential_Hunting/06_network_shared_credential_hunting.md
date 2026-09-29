Seccion dedicada a la busqueda de credenciales en recursos compartidos en la red.


- Busca palabras clave dentro de los archivos como `passw`, `user`, `token`, `key` y `secret`.
- Busca archivos con extensiones comúnmente asociadas con credenciales almacenadas, como `.ini`, `.cfg`, `.env`, `.xlsx`, `.ps1` y `.bat`.
- Presta atención a los archivos con nombres "interesantes" que incluyan términos como `config`, `user`, `passw`, `cred` o `initial`.
- Si estás intentando localizar credenciales dentro del dominio `INLANEFREIGHT.LOCAL`, puede ser útil buscar archivos que contengan la cadena `INLANEFREIGHT\`.
- Las palabras clave deben localizarse según el objetivo; si estás atacando a una empresa alemana, es más probable que hagan referencia a un `"Benutzer"` que a un `"User"`.
- Presta atención a los recursos compartidos que estás mirando y sé estratégico. Si escaneas diez recursos compartidos con miles de archivos cada uno, va a tomar una cantidad significativa de tiempo. Los recursos compartidos utilizados por `empleados de TI` podrían ser un objetivo más valioso que los utilizados para las fotos de la empresa.

## Snaffler
Herramienta para utilizar si estamos en un equipo windows víctima unido al dominio.
https://github.com/SnaffCon/Snaffler

- `-u` recupera una lista de usuarios de Active Directory y busca referencias a ellos en los archivos
- `-i` y `-n` te permiten especificar qué recursos compartidos deben incluirse en la búsqueda

```cmd
Snaffler.exe -s
```

## PowerHuntShares
Script de powershell, no requiere estar en una maquina unida a dominio (aunque tambien serviría)
https://github.com/NetSPI/PowerHuntShares

Ejemplos:
```powershell
.EXAMPLE 1: Run from a domain computer. Performs Active Directory computer discovery by default.
PS C:\temp\test> Invoke-HuntSMBShares -Threads 100 -OutputDirectory c:\temp\test 

.EXAMPLE 2: Run from a domain computer with alternative domain credentials. Performs Active Directory computer discovery by default.
PS C:\temp\test> Invoke-HuntSMBShares -Threads 100 -OutputDirectory c:\temp\test -Credential domain\user

.EXAMPLE 3: Run from a domain computer as current user. Target hosts in a file. One per line.
PS C:\temp\test> Invoke-HuntSMBShares -Threads 100 -OutputDirectory c:\temp\test  -HostFile c:\temp\hosts.txt      

.EXAMPLE 4: Run from a non-domain computer with credential. Performs Active Directory computer discovery by default.
C:\temp\test> runas /netonly /user:domain\user PowerShell.exe
PS C:\temp\test> Import-Module PowerHuntShares.psm1
PS C:\temp\test> Invoke-HuntSMBShares -Threads 100 -RunSpaceTimeout 10 -OutputDirectory c:\folder\ -DomainController 10.1.1.1 -Credential domain\user 
```

## MANSPIDER
Para realizar la búsqueda en recursos SMB desde Linux directamente.
https://github.com/blacklanternsecurity/MANSPIDER

Desplegar herramienta
```bash
docker build .
mkdir -p ./manspider

```

##### Buscar ficheros que contengan credenciales
Se pueden modificar las palabras clave a buscar, al final es como un grep, y adaptar al idioma
```bash
manspider 192.168.0.0/24 -f passw user admin account network login logon cred -d evilcorp -u bob -p Passw0rd
```

##### Buscar hojas de calculo con credenciales
Se pueden modificar las palabras clave y el formato, lo mismo interesa buscar en otro tipo de ficheros como doc, docx, odt
```bash
manspider share.evilcorp.local -f passw -e xlsx csv -d evilcorp -u bob -p Passw0rd
```

##### Buscar en documentos
```bash
manspider share.evilcorp.local -c passw -e xlsx csv docx pdf -d evilcorp -u bob -p Passw0rd
```

##### Buscar ficheros con extensiones interesantes
se pueden agregar mas, como: kdbx, sh, txt, (todos los formatos de documentos), .db, .sqlite3 y todo lo que se te ocurra (mirar en otras notas de credential hunting para coger ideas)
```bash
manspider share.evilcorp.local -e bat com vbs ps1 psd1 psm1 pem key rsa pub reg pfx cfg conf config vmdk vhd vdi dit -d evilcorp -u bob -p Passw0rd
```

##### Buscar carpetas financieras
Adaptar al idioma si fuera necesario
```bash
manspider share.evilcorp.local --dirnames bank financ payable payment reconcil remit voucher vendor eft swift -f '[0-9]{5,}' -d evilcorp -u bob -p Passw0rd
```

##### Buscar claves SSH
```bash
manspider share.evilcorp.local -e ppk rsa pem ssh rsa -o -f id_rsa id_dsa id_ed25519 -d evilcorp -u bob -p Passw0rd


manspider share.evilcorp.local -e '' -c 'BEGIN .{1,10} PRIVATE KEY' -d evilcorp -u bob -p Passw0rd
```

##### Buscar ficheros de password manager
```bash
# .kdbx - KeePass Password Database (KeePass, KeePassXC)
# .kdb - KeePass Classic Database (KeePass 1.x)
# .1pif - 1Password Interchange Format (1Password)
# .agilekeychain - Agile Keychain Format (1Password, deprecated)
# .opvault - OPVault Format (1Password)
# .lpd - LastPass Data File (LastPass)
# .dashlane - Dashlane Data File (Dashlane)
# .psafe3 - Password Safe Database (Password Safe)
# .enpass - Enpass Password Manager Data File (Enpass)
# .bwdb - Bitwarden Database (Bitwarden)
# .msecure - mSecure Password Manager Data File (mSecure)
# .stickypass - Sticky Password Data File (Sticky Password)
# .pwm - Password Memory Data File (Password Memory)
# .rdb - RoboForm Data File (RoboForm)
# .safe - SafeInCloud Password Manager Data File (SafeInCloud)
# .zps - Zoho Vault Encrypted Data File (Zoho Vault)
# .pmvault - SplashID Safe Data File (SplashID Safe)
# .mywallet - MyWallet Password Manager Data File (MyWallet)
# .jpass - JPass Password Manager Data File (JPass)
# .pwmdb - Universal Password Manager Database (Universal Password Manager)
$ manspider share.evilcorp.local -e kdbx kdb 1pif agilekeychain opvault lpd dashlane psafe3 enpass bwdb msecure stickypass pwm rdb safe zps pmvault mywallet jpass pwmdb -d evilcorp -u bob -p Passw0rd
```

##### Buscar certificados
```bash
manspider share.evilcorp.local -e pfx p12 pkcs12 pem key crt cer csr jks keystore key keys der -d evilcorp -u bob -p Passw0rd
```

##### Buscar ficheros modificados recientemente
Modificar la extension a buscar y la fecha
```bash
$ manspider share.evilcorp.local -e docx xlsx pdf --modified-after 2026-01-01 -d evilcorp -u bob -p Passw0rd
```

## Buscar con NXC
```bash
# Busca coiincidenciasficheros que contengan la cadena "passwd"
nxc smb 10.129.234.121 -u mendres -p 'Inlanefreight2025!' --spider IT --content --pattern "passw"

# Enumera los Shares, descarga los ficheros legibles de hsata 50Kb (por defecto) para lueg poder hacer grep sobre todo el arbol y buscar coincidencias
nxc smb 10.129.154.247 -u mendres -p Inlanefreight2025! -M spider_plus -o DOWNLOAD_FLAG=True --smb-timeout 60
```