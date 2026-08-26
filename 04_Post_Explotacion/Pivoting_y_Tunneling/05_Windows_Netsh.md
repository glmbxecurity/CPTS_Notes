---
title: Portproxy de Windows (Netsh)
pubDate: 2026-05-22
---

## ¿Qué es Netsh Portproxy?
Es una funcionalidad nativa de Windows que permite redirigir el tráfico de red de un puerto a otro. Su mayor ventaja es que **no requiere subir binarios externos** (como Chisel), lo que lo hace muy sigiloso y difícil de detectar por antivirus.

### Requisitos
*   Tener privilegios de **Administrador**.
*   El servicio **IP Helper** debe estar activo.
*   El soporte para **IPv6** debe estar habilitado en la interfaz (aunque redirijas tráfico IPv4).

---

## 🚀 1. Configurar Redirección de Puertos
**Escenario:** Quieres que el puerto `8080` de tu máquina víctima Windows redirija todo el tráfico al puerto `80` de un servidor interno (`192.168.1.10`).

```powershell
# Añadir la redirección
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=192.168.1.10
```

---

## 🛡️ 2. Abrir el Firewall de Windows
Para que la redirección funcione, el firewall de Windows debe permitir la conexión entrante en el puerto donde estás escuchando (`8080`).

```powershell
# Crear regla para permitir el tráfico en el puerto 8080
netsh advfirewall firewall add rule name="Port Forwarding 8080" protocol=TCP dir=in localport=8080 action=allow
```

---

## 🔎 3. Gestión y Limpieza

### Listar mapeos activos
```powershell
netsh interface portproxy show all
```

### Eliminar una redirección específica
```powershell
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0
```

### Resetear toda la configuración
```powershell
netsh interface portproxy reset
```

> **Tip:** Este método es excelente para ataques de **Relay** o para exponer servicios de bases de datos internas que solo escuchan en el localhost de un servidor Windows.
