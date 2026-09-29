---
title: Herramientas Esenciales de Terminal (Tmux y Vim)
pubDate: '2026-08-26'
---

## 🪟 Tmux (Multiplexor de Terminal)

Permite tener múltiples ventanas y paneles divididos dentro de una única sesión de terminal. Es crucial para organizar el entorno de ataque y mantener el registro de actividad (*logging*).

- **Instalación:** `sudo apt install tmux -y`
- **Iniciar tmux:** `tmux`
- **Prefijo base:** `CTRL + B` (Se debe presionar siempre antes de ejecutar cualquier atajo).

### Atajos Básicos de Tmux

| Acción | Comando (Después de `CTRL + B`) |
| --- | --- |
| **Nueva ventana** | `C` |
| **Cambiar de ventana** | `Número (Ej: 0, 1, 2)` |
| **Dividir panel verticalmente** | `SHIFT + %` |
| **Dividir panel horizontalmente** | `SHIFT + "` |
| **Navegar entre paneles** | `Flechas de dirección (Arriba, Abajo, Izq, Der)` |

---

## 📝 Vim (Editor de Texto)

Editor en consola basado completamente en el uso del teclado. Está instalado por defecto en la inmensa mayoría de los sistemas Linux (incluidos los servidores comprometidos), por lo que es indispensable dominarlo para editar código y configuraciones de forma remota.

- **Abrir/Crear archivo:** `vim nombre_del_archivo`

### Modos de Vim

1. **Modo Normal:** Modo por defecto al abrir un archivo (solo lectura). Se utiliza para navegar y aplicar atajos de teclado.
2. **Modo de Inserción:** Permite escribir y editar el texto. Se accede pulsando la tecla `i` y se sale pulsando `ESC`.
3. **Modo de Comandos:** Para ejecutar acciones del sistema. Se accede pulsando `:` desde el modo normal.

### Atajos de Edición (Modo Normal)

> 💡 *Consejo de productividad:* Puedes multiplicar cualquier comando introduciendo un número antes. Por ejemplo, `4yw` copiará 4 palabras y `3dd` cortará 3 líneas completas.

| Acción | Tecla / Comando |
| --- | --- |
| **Cortar carácter** | `x` |
| **Cortar palabra** | `dw` |
| **Cortar línea completa** | `dd` |
| **Copiar palabra** | `yw` |
| **Copiar línea completa** | `yy` |
| **Pegar** | `p` |

### Guardado y Salida (Modo Comandos `:`)

| Acción | Comando |
| --- | --- |
| **Ir a la línea específica** | `:1` (En este ejemplo, va a la línea 1) |
| **Guardar el archivo** | `:w` |
| **Salir de Vim** | `:q` |
| **Salir sin guardar (forzar)** | `:q!` |
| **Guardar y Salir** | `:wq` |
