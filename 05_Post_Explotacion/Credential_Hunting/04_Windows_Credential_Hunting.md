# Windows Credential Hunting

Una vez tienes acceso por CLI o GUI se pueden buscar credenciales en ficheros, y lugares del sistema.

### Buscar cadenas en ficheros
Buscar palabra `password` en todos los ficheros con esas extensiones
```cmd
findstr /SIM /C:"password" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml
```


Buscar las palabras mas comunes en los ficheros mas comunes:
>va a tardar MUCHISIMO, lo ideal es ejecutarlo desde C:\Users  u otra ruta, o simplificar el comando si fuera necesario

```cmd
findstr /SIM /C:"pass" /C:"cred" /C:"user" /C:"key" /C:"config" /C:"pwd" /C:"login" *.txt *.ini *.cfg *.config *.xml *.git *.ps1 *.yml 2>nul
```

### Busqueda manual
- SYSVOL: Buscar políticas de grupo (GPO) con contraseñas o scripts de inicio de sesión.
- IT Shares: Archivos web.config, scripts de mantenimiento, unattend.xml (archivos de instalación desatendida).
- Shares de usuarios: Archivos ofimáticos con nombres delatores (passwords.xlsx, passwords.docx, pass.txt).
- Revisar los campos de "Descripción" de los usuarios o equipos en AD (a veces los administradores dejan contraseñas por defecto ahí anotadas).
- Bases de datos de KeePass (.kdbx). Si encuentras una, el objetivo pasa a ser buscar o adivinar la contraseña maestra.

##### Consejo pensamiento lateral extra

Antes de lanzar comandos a lo loco, hazte esta pregunta: ¿Para qué usa este equipo el usuario?
Si es de IT: Busca en scripts .ps1, sesiones guardadas de WinSCP o PuTTY.
Si es de RRHH/Finanzas: Busca en excels, documentos de Word o navegadores.
Si es un Servidor (IIS, SQL): Busca en archivos de configuración web (web.config) o strings de conexión a BBDD.

### LaZagne
Herramienta con modulos para buscar credenciales en navegadores, mails, chats, memoria, winscp, wifi, etc.
https://github.com/AlessandroZ/LaZagne

```cmd
# Con "all" ejecuta todos los modulos
start LaZagne.exe all -vv
```

##### Desencriptar credenciales firefox, chrome, etc
https://github.com/ohyicong/decrypt-chrome-passwords
https://github.com/unode/firefox_decrypt