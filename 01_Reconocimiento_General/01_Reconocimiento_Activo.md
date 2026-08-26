---
title: "Descubrimiento de Red, Escaneo de Puertos y Nmap Avanzado"
pubDate: '2026-08-26'
---

Guía integral de descubrimiento de hosts, escaneo de puertos, parámetros y timings avanzados de Nmap, categorías de scripts NSE, catálogo de puertos de infraestructura, evasión de IDS/Firewalls y automatización.

---

## 🚀 1. Host Discovery (Descubrimiento de Equipos)

### Capa 2 (ARP) - Red Local / Pivot
```bash
# Escaneo ARP (Rápido y fiable en LAN)
sudo arp-scan -l
arp-scan -I <interfaz> --localnet --ignoredups
netdiscover -P -i eth0
nmap -PR -sn <red/cidr>
```

### Capa 3 (ICMP / TCP) - Redes Enrutadas
```bash
# Ping Sweep (ICMP)
nmap -sn 10.10.0.0/24
fping -a -g 10.10.0.0/24 2>/dev/null
fping -a -g <SUBNET>/24 2>/dev/null

# TCP SYN Ping (Bypass de bloqueo ICMP simulando puerto 80/443)
nmap -sn -PS80,443,8080 10.10.0.0/24
masscan -p80,443 10.10.0.0/24 --rate=1000

# TCP ACK Ping
nmap -sn -PA 10.10.0.0/24
```

### Identificación de Hipervisores (OUI MAC Address)
* **VMware:** `00:05:69`, `00:0C:29`, `00:1C:14`, `00:50:56`
* **VirtualBox:** `08:00:27`
* **Hyper-V:** `00:15:5D`

---

## 🎯 2. Metodología de Escaneo de Puertos

### Plantillas Base de Auditoría (Metodología CPTS / OSCP)
```bash
# 1. TCP Quick (Escaneo inicial rápido de puertos comunes con scripts seguros)
sudo nmap -Pn -v -sS -sV -sC -oA nmap/tcp_quick <TARGET_IP>

# 2. TCP Full (Todos los puertos 1-65535 con optimización de evasión de rate-limit)
sudo nmap -Pn -sS --stats-every 3m --max-retries 1 --max-scan-delay 20 --defeat-rst-ratelimit -T4 -p- -sV -oA nmap/tcp_full <TARGET_IP>

# 3. TCP Targeted (Profundizar solo en los puertos abiertos descubiertos)
sudo nmap -Pn -v -sS -A -p <PORTS> -oA nmap/tcp_extra <TARGET_IP>

# 4. UDP Quick (Top 30 puertos UDP comunes)
sudo nmap -Pn -v -sU -sV --top-ports=30 -oA nmap/udp_quick <TARGET_IP>

# 5. UDP 1000 (Top 1000 puertos UDP optimizado)
sudo nmap -Pn --top-ports 1000 -sU --stats-every 3m --max-retries 1 -T4 -oA nmap/udp_1000 <TARGET_IP>

# 6. UDP Targeted (Profundizar en puertos UDP específicos)
sudo nmap -Pn -sU -A -p <PORTS> -oA nmap/udp_extra <TARGET_IP>
```

### Flujo de Trabajo Alternativo con Extracción Grepable (`extractPorts`)
```bash
# 1. Escaneo rápido de todos los puertos exportando en formato Grepable
nmap -p- --open --min-rate 5000 -vvv -n -Pn <TARGET_IP> -oG allPorts

# 2. Función extractPorts para copiar los puertos al portapapeles
cat allPorts | grep -oP '\d{1,5}/open' | awk '{print $1}' FS='/' | xargs | tr ' ' ','

# 3. Escaneo exhaustivo con scripts y versiones sobre los puertos extraídos
nmap -p<PUERTOS_EXTRAIDOS> -sCV -n -Pn <TARGET_IP> -oN targeted
```

---

## ⚙️ 3. Cheatsheet de Parámetros y Técnicas de Nmap

### Definición de Objetivos y Puertos
```bash
nmap 192.168.1.1-254                                 # Rango de IPs
nmap -iL targets.txt                                 # Lista desde archivo
nmap --exclude 192.168.1.1                           # Excluir IPs
-p-                                                  # Todos los puertos (1-65535)
-p T:21,U:53                                         # Protocolo mixto (TCP 21 y UDP 53)
--top-ports=1000                                     # Top 1000 puertos más comunes
```

### Tipos de Escaneo de Red
```bash
-sS     nmap <TARGET_IP> -sS     # TCP SYN (Stealth / Por defecto). Rápido, no completa el handshake (evita logs).
-sT     nmap <TARGET_IP> -sT     # TCP Connect. Completa 3-way handshake (usado cuando no se es root).
-sU     nmap <TARGET_IP> -sU     # UDP Scan. Para DNS, SNMP, DHCP, TFTP.
-sA     nmap <TARGET_IP> -sA     # TCP ACK. Mapea reglas de firewall (Unfiltered vs Filtered).
-sW     nmap <TARGET_IP> -sW     # TCP Window. Analiza tamaño de ventana TCP en paquetes RST.
-sM     nmap <TARGET_IP> -sM     # TCP Maimon. Envía banderas FIN/ACK (evasión RFC 793).
```

### Detección de Versiones y Sistema Operativo
```bash
-sV                                # Detección de versiones interactuando con el servicio
--version-intensity <0-9>          # Nivel de intensidad (0 más rápido, 9 exhaustivo). Por defecto 7
--version-light                    # Alias exacto para --version-intensity 2
--version-all                      # Alias exacto para --version-intensity 9 (máxima exhaustividad)
-A                                 # Todo en uno: OS (-O) + Versiones (-sV) + Scripts (-sC) + Traceroute
-O                                 # Detección de Sistema Operativo mediante TCP/IP fingerprinting
--osscan-limit                     # Omite detección de SO si no halla al menos un puerto abierto y uno cerrado
--osscan-guess                     # Adivinación agresiva del SO con porcentajes de probabilidad
--max-os-tries <x>                 # Límite de intentos de detección de SO (por defecto 5)
```

### Control Granular de Tiempos y Rendimiento (Timing & Performance)
```bash
# Plantillas predefinidas:
-T0 (Paranoid)  | -T1 (Sneaky)  | -T2 (Polite)  | -T3 (Normal)  | -T4 (Aggressive)  | -T5 (Insane)

# Parámetros granulares:
--host-timeout <time>                # Tiempo máximo de vida para un host (ej. 30m, 1h). Salta hosts lentos.
--min-rtt-timeout / --max-rtt-timeout <time> # Ajuste de tiempo de espera Round-Trip Time (ej. 100ms en LAN).
--min-hostgroup / --max-hostgroup <size>     # Tamaño de grupos de hosts escaneados en paralelo.
--min-parallelism / --max-parallelism <num>  # Control estricto de sondas concurrentes en vuelo.
--scan-delay <time>                  # Pausa fija entre paquetes (ej. 500ms, 1s) para evadir rate-limiting.
--max-scan-delay <time>              # Límite máximo al incremento automático de delay.
--max-retries <tries>                # Límite de retransmisiones ante paquetes perdidos (DROP).
--min-rate / --max-rate <number>     # Forzar número mínimo o máximo estricto de paquetes por segundo.
```

### Formatos de Salida (Output) y Generación de Reportes HTML
```bash
-oN <file>                           # Salida Normal legible.
-oX <file>                           # Salida estructurada XML (para Metasploit, Nessus o scripts).
-oG <file>                           # Salida Grepable en una línea por host.
-oA <prefix>                         # Genera los tres formatos (.nmap, .xml, .gnmap) simultáneamente.
--append-output                      # Concatena al final del archivo sin sobrescribir.

# Generar reporte HTML visual para clientes a partir del XML:
xsltproc target.xml -o target.html
```

### Diagnóstico Avanzado de Paquetes
```bash
--packet-trace                      # Muestra paquetes enviados y recibidos en tiempo real (Drop vs Reject).
--reason                            # Muestra el motivo exacto del estado asignado al puerto (syn-ack, no-response).
-v / -vv / -vvv                     # Incrementa la verbosidad en consola.
```

---

## 📜 4. Scripts NSE (Nmap Scripting Engine)

### Categorías Oficiales de Scripts NSE
| Categoría | Descripción |
| :--- | :--- |
| **`auth`** | Comprobación y verificación de credenciales de autenticación. |
| **`broadcast`** | Descubrimiento de hosts mediante difusión en red local (*broadcasting*). |
| **`brute`** | Ataques de fuerza bruta de credenciales contra el servicio objetivo. |
| **`default`** | Scripts estándar y seguros ejecutados con la opción `-sC`. |
| **`discovery`** | Evaluación de servicios accesibles, topología de red y nombres de dominio. |
| **`dos`** | Comprobación de vulnerabilidades de denegación de servicio (usar con precaución). |
| **`exploit`** | Explotación activa de vulnerabilidades conocidas en el servicio. |
| **`external`** | Envío de datos a servicios y APIs externas de terceros (WHOIS, Shodan). |
| **`fuzzer`** | Envío de cargas inesperadas para identificar fallos de manejo de paquetes. |
| **`intrusive`** | Scripts agresivos con riesgo de afectar la estabilidad del host. |
| **`malware`** | Comprobación de infecciones por malware o *backdoors* conocidos. |
| **`safe`** | Scripts no intrusivos que no dañan ni saturan los recursos del host. |
| **`version`** | Extensión avanzada de detección de versiones de software (`-sV`). |
| **`vuln`** | Identificación de vulnerabilidades conocidas (CVEs) sin explotación destructiva. |

### Ejemplos de Ejecución NSE:
```bash
nmap -sC <TARGET_IP>                                         # Scripts por defecto
nmap --script=vuln <TARGET_IP>                               # Categoría de vulnerabilidades conocidas
nmap --script=banner <TARGET_IP>                             # Extracción de banners
nmap --script="http-*" <TARGET_IP>                           # Todos los scripts HTTP
nmap --script "not intrusive and not dos" <TARGET_IP>        # Excluir scripts de riesgo
nmap -p 21,22,23,25,80,110,143,443,3306,5432,6379,8080 --script brute <TARGET_IP> # Fuerza bruta multipuerto
```
---

## 🛡️ 6. Evasión de Firewall / IDS

```bash
# Fragmentar paquetes y MTU personalizada (múltiplo de 8)
nmap -f <TARGET_IP>
nmap --mtu 24 <TARGET_IP>

# Spoofing y Decoys (Señuelos aleatorios para enmascarar IP real)
nmap -D 192.168.1.5,RND:5 <TARGET_IP>
nmap -e <interfaz> -Pn -S <IP_SPOOFED> <TARGET_IP>

# Source Port Spoofing (Simular origen desde puerto DNS 53 o HTTP 80)
nmap -g 53 <TARGET_IP>
nmap --source-port 53 <TARGET_IP>

# ACK Scan (Comprobar si un puerto está filtrado por firewall de estado)
nmap -sA <TARGET_IP>

# Banner Grabbing Evasivo (Forzando puerto origen 53 DNS con Netcat)
nc -vn -p53 <TARGET_IP> <PORT>
sudo fuser -k 53/tcp               # Liberar el puerto 53 local si está ocupado
```

---

## 🤖 7. Automatización de Reconocimiento

```bash
# AutoRecon (Enumeración multihilo por puertos)
autorecon <TARGET_IP>

# NmapAutomator
./NmapAutomator.sh <TARGET_IP> All
```

---

## 🕵️ 8. Identificación de Servicios, OS y Búsqueda de Exploits

### Banner Grabbing Manual
```bash
# Conexión directa
nc -nv <TARGET_IP> <PORT>
curl -I http://<TARGET_IP>
whatweb http://<TARGET_IP>
```

### Fingerprinting de Sistema Operativo por TTL
* **Linux / Unix:** TTL `~64`
* **Windows:** TTL `~128`
* **Cisco / Equipos de Red:** TTL `~255`
```bash
ping -c 1 <TARGET_IP>
```

### Búsqueda de Exploits con Searchsploit
```bash
searchsploit -u                                      # Actualizar base de datos
searchsploit "Apache 2.4.49"                         # Búsqueda por servicio y versión
searchsploit -m <ID_EXPLOIT>                         # Copiar exploit a la carpeta local
searchsploit -x <ID_EXPLOIT>                         # Inspeccionar código fuente
```
## 🌐 5. Catálogo de Scripts NSE para Puertos de Infraestructura y Contenedores

| Puerto | Protocolo / Servicio | Comando / Script Nmap | Acción Táctica |
| :--- | :--- | :--- | :--- |
| **53 TCP/UDP** | **DNS** | `nmap -p 53 --script=dns-zone-transfer,dns-cache-snoop,dns-nsid,dns-brute <IP>` | Comprobar transferencia de zona AXFR y versión (`dig CH TXT version.bind <IP>`). |
| **69 UDP** | **TFTP** | `nmap -sU -p 69 --script tftp-enum <IP>` | Descarga de archivos sin autenticación vía `atftp <IP>`. |
| **88 TCP/UDP** | **Kerberos** | `nmap -p 88 --script krb5-enum-users --script-args krb5-enum-users.realm='DOMAIN.LOCAL' <IP>` | Enumeración de usuarios (`kerbrute userenum`) y AS-REP Roasting (`GetNPUsers.py`). |
| **123 UDP** | **NTP** | `nmap -sU -p 123 --script ntp-info,ntp-monlist <IP>` | Consulta de servidores sincronizados e IPs internas con `ntpmon`. |
| **389 / 636** | **LDAP / LDAPS** | `nmap -p 389 --script "ldap* and not brute" <IP>` | Consultas DSE anónimas y volcado de usuarios de Active Directory con `ldapsearch`. |
| **1099 TCP** | **Java RMI** | `nmap -p 1099 --script rmi-dumpregistry,rmi-vuln-classloader <IP>` | Deserialización Java y ejecución remota con `ysoserial`. |
| **1883 TCP** | **MQTT** | `nmap -p 1883 --script mqtt-subscribe <IP>` | Suscripción a topics de mensajería IoT (`mosquitto_sub -h <IP> -t "#"`). |
| **2181 TCP** | **Zookeeper** | `nmap -p 2181 --script zookeeper-info <IP>` | Extracción de metadatos de cluster enviando `echo "envi" \| nc -nv <IP> 2181`. |
| **2375 TCP** | **Docker API** | `nmap -p 2375 --script docker-version <IP>` | Acceso sin autenticar al daemon: `docker -H tcp://<IP>:2375 run -v /:/mnt alpine chroot /mnt`. |
| **5060 UDP** | **SIP (VoIP)** | `nmap -sU -p 5060 --script sip-methods,sip-enum-users <IP>` | Enumeración de extensiones telefónicas con `svwar` y `sipsak`. |
| **5432 TCP** | **PostgreSQL** | `nmap -p 5432 --script pgsql-databases,pgsql-users,pgsql-empty-password <IP>` | Conexión con `psql -h <IP> -U postgres` y RCE vía `COPY FROM PROGRAM`. |
| **5672 TCP** | **RabbitMQ** | `nmap -p 5672 --script rabbitmq-info <IP>` | Gestión de colas AMQP e inspección de credenciales. |
| **5900 TCP** | **VNC** | `nmap -p 5900 --script vnc-info,vnc-title,vnc-brute <IP>` | Conexión gráfica vía `vncviewer <IP>`. |
| **5938 TCP** | **TeamViewer** | `nmap -p 5938 --script teamviewer-info <IP>` | Detección de software de acceso remoto comercial. |
| **5984 TCP** | **CouchDB** | `nmap -p 5984 --script http-couchdb-info <IP>` | Consulta de bases NoSQL con `curl http://<IP>:5984/_all_dbs` (CVE-2017-12635). |
| **6000 TCP** | **X11** | `nmap -p 6000 --script x11-access <IP>` | Captura de pantalla remota con `xwd -root -screen 0 -silent -display <IP>:0 > screenshot.xwd`. |
| **6081 TCP** | **Varnish Cache** | `nmap -p 6081 --script http-headers,http-title <IP>` | Detección de aceleradores y proxies reversos HTTP. |
| **6443 TCP** | **Kubernetes API** | `nmap -p 6443 --script http-kubernetes-info <IP>` | Consulta no autenticada con `curl -k https://<IP>:6443/api/v1/pods`. |
| **8009 TCP** | **Apache AJP** | `nmap -p 8009 --script ajp-methods,ajp-headers <IP>` | Explotación de lectura arbitraria de archivos Ghostcat (CVE-2020-1938). |
| **8080 TCP** | **Tomcat / Jenkins** | `nmap -p 8080 --script http-tomcat-manager,http-jenkins-info <IP>` | Despliegue de ficheros WAR maliciosos en Apache Tomcat o Jenkins Script Console. |
| **9092 TCP** | **Apache Kafka** | `nmap -p 9092 --script kafka-info <IP>` | Listado de topics y consumo de mensajes corporativos. |
| **9101 TCP** | **Bacula Backup** | `nmap -p 9101 --script bacula-info <IP>` | Extracción de copias de seguridad del demonio Bacula Director. |
| **9200 TCP** | **Elasticsearch** | `nmap -p 9200 --script "http-elasticsearch-*" <IP>` | Volcado de índices sin autenticar: `curl -s http://<IP>:9200/_cat/indices?v`. |
| **11211 TCP** | **Memcached** | `nmap -p 11211 --script memcached-info <IP>` | Volcado de claves enviando `echo "stats items" \| nc -nv <IP> 11211`. |
| **50070 TCP** | **Hadoop HDFS** | `nmap -p 50070 --script http-hadoop-info <IP>` | Explorador del sistema de archivos distribuido de Hadoop. |
| **902 / 903** | **VMware ESXi** | `nmap -p 902,903,443 --script vmware-version <IP>` | Identificación de hipervisores VMware y vCenter Server. |

