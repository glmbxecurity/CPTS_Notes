# Ataques a Passwd y Shadow

### Archivo Passwd
El fichero passwd contiene los usuarios del sistema y por cada usuario tiene una entrada. Conocer bien su contenido puede ayudar a entender y encontrar vulnerabilidades.

```bash
htb-student:x:1000:1000:,,,:/home/htb-student:/bin/bash
```

| Campo                                              | Valor               |
| -------------------------------------------------- | ------------------- |
| Nombre de usuario                                  | `htb-student`       |
| Contraseña                                         | `x`                 |
| ID de usuario                                      | `1000`              |
| ID de grupo                                        | `1000`              |
| [GECOS](https://en.wikipedia.org/wiki/Gecos_field) | `,,,`               |
| Directorio de inicio                               | `/home/htb-student` |
| Shell por defecto                                  | `/bin/bash`         |
> Muy importante el campo contraseña, la "x" significa que la password está hasheada y está almacenada en /etc/passwd, pero si tuvieramos permisos de escritura sobre /etc/passwd por una mala configuracion, podriamos eliminar esa "x" y al usuario podriamos pivotar / movimiento lateral sin necesidad de meter la contraseña. Directamente escribiendo `su <user>`

### Archivo Shadow
```
htb-student:$y$j9T$3QSBB6CbHEu...SNIP...f8Ms:18955:0:99999:7:::
```

Importante el campo de la contraseña hasheada, tiene el siguiente formato:
`$<id>$<salt>$<hashed>`

En la siguiente tabla vemos las equivalencias de salt o hash.

| ID     | Algoritmo de hash criptográfico                                       |
| ------ | --------------------------------------------------------------------- |
| `1`    | [MD5](https://en.wikipedia.org/wiki/MD5)                              |
| `2a`   | [Blowfish](https://en.wikipedia.org/wiki/Blowfish_\(cipher\))         |
| `5`    | [SHA-256](https://en.wikipedia.org/wiki/SHA-2)                        |
| `6`    | [SHA-512](https://en.wikipedia.org/wiki/SHA-2)                        |
| `sha1` | [SHA1crypt](https://en.wikipedia.org/wiki/SHA-1)                      |
| `y`    | [Yescrypt](https://github.com/openwall/yescrypt)                      |
| `gy`   | [Gost-yescrypt](https://www.openwall.com/lists/yescrypt/2019/06/30/1) |
| `7`    | [Scrypt](https://en.wikipedia.org/wiki/Scrypt)                        |
| `2y`   | bcrypt                                                                |

### Fichero Opasswd
Fichero donde se almacena el historial de contraseña de los usuarios, solo se puede acceder con privilegios de administrador. Es interesante mirarlo porque se pueden descubrir credenciales o patrones que pueden abrir otras puertas, aunque ya seamos administrador en ese sistema. 

```
/etc/security/opasswd
```

### Crack credenciales Linux
```
sudo cp /etc/passwd /tmp/passwd.bak 
sudo cp /etc/shadow /tmp/shadow.bak 
unshadow /tmp/passwd.bak /tmp/shadow.bak > /tmp/unshadowed.hashes
```

```
hashcat -m 1800 -a 0 /tmp/unshadowed.hashes rockyou.txt -o /tmp/unshadowed.cracked
```
