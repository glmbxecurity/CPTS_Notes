---
title: SNMP (Simple Network Management Protocol - Puertos 161, 162 UDP)
pubDate: '2026-08-26'
---

## ¿Qué es SNMP?
**Simple Network Management Protocol (SNMP)** se utiliza para monitorizar y gestionar dispositivos de red (routers, switches, servidores). La información se organiza en una estructura jerárquica mediante **OIDs** (Object Identifiers). Para acceder a esta información, necesitas conocer la **Community String**, que actúa como una contraseña de acceso.

### Riesgos principales
1. **Fuga masiva de información:** Revela nombres de usuario, procesos en ejecución, software instalado, rutas de red y uptime del sistema.
2. **Credenciales en procesos:** Al listar los procesos, a veces se pueden ver comandos que incluyen contraseñas en texto claro (ej: backups o conexiones a bases de datos).

---

## ⚙️ Ficheros de Configuración y Directivas Críticas

### Ruta Clave: `/etc/snmp/snmpd.conf`
| Ajuste en `snmpd.conf` | Descripción e Impacto de Seguridad |
| :--- | :--- |
| `rwuser noauth` | **Crítico:** Proporciona acceso total de lectura y escritura al árbol OID completo sin ninguna autenticación. |
| `rwcommunity <community> <IPv4>` | Permite acceso de lectura/escritura a cualquier cliente que conozca la cadena de comunidad. |
| `rocommunity <community> default` | Permite acceso de solo lectura desde cualquier origen de red con esa comunidad. |

---

## 🔎 1. Descubrimiento de la Community String

```bash
# Onesixtyone (Muy rápido para adivinar comunidades con diccionario)
onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp.txt <TARGET_IP>
onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt <TARGET_IP>

# Scripts Nmap para SNMP
sudo nmap -sU -sV -p 161,162 --script=snmp-info,snmp-interfaces,snmp-processes,snmp-win32-services,snmp-brute,snmp-sysdescr <TARGET_IP>
```

---

## 🚀 2. Enumeración Completa

### snmp-check (Recomendado)
Traduce automáticamente los OIDs a un formato estructurado y legible:
```bash
snmp-check -v2c -c <community_string> <TARGET_IP>
```

### snmpwalk (Volcado Completo)
```bash
# Volcar todo el árbol OID a un archivo de texto para análisis posterior
snmpwalk -v2c -c <community_string> <TARGET_IP> .1 > snmp_completo.txt
```

### Braa (Consultas Ultrarrápidas de Ramas OID)
```bash
braa <community_string>@<TARGET_IP>:.1.3.6.*
braa public@<TARGET_IP>:.1.3.6.1.2.1.25.4.2.1.2
```

---

## 🎯 3. OIDs Útiles y Greps de Extracción de Datos

### OIDs de Referencia
| Información deseada | OID |
| :--- | :--- |
| **Nombres de Usuarios** | `1.3.6.1.4.1.77.1.2.25` |
| **Procesos en ejecución** | `1.3.6.1.2.1.25.4.2.1.2` |
| **Software instalado** | `1.3.6.1.2.1.25.6.3.1.2` |
| **Hostname del sistema** | `1.3.6.1.2.1.1.5` |
| **Interfaces de Red** | `1.3.6.1.2.1.2.2.1.2` |

### Regex y Greps Esenciales sobre `snmp_completo.txt`:
```bash
# 1. Buscar credenciales y contraseñas filtradas en argumentos de comandos
grep -iE "pass|pwd|secret|cred|login|user" snmp_completo.txt

# 2. Buscar cadenas de conexión a bases de datos (ej. mysql -u root -p...)
grep -iE "mysql|psql|sqlcmd" snmp_completo.txt

# 3. Rastrear scripts y ejecutables personalizados
grep -iE "/bin/|/opt/|/usr/|/tmp/|/var/www/|\.sh|\.py|\.php" snmp_completo.txt

# 4. Descubrimiento de direcciones IPv4 internas
grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}" snmp_completo.txt | sort -u
```

### Rastrear Salida de un Script por su OID:
Si en el volcado encuentras una línea como `iso.3.6.1.4.1.2021.8.1.2.100.101.118 = STRING: "/opt/backup.sh"`, extrae el identificador final (`100.101.118`) y búscalo en el archivo para ver qué salida generó dicho script:
```bash
grep "100.101.118" snmp_completo.txt
```
