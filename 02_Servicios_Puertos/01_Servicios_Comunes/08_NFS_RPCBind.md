---
title: NFS & Rpcbind (Network File System - Puertos 111, 2049)
pubDate: '2026-08-26'
---

## ¿Qué es NFS y RPC?
**NFS (Network File System)** es un protocolo que permite compartir carpetas a través de la red como si estuvieran en el propio disco local. Es muy común en entornos Linux para compartir archivos de configuración, directorios `/home` o backups.

Para funcionar, NFS se apoya en **RPCBind (Portmapper)** en el puerto **111**, que actúa como directorio para indicar en qué puerto específico (generalmente el 2049) está escuchando el daemon de NFS.

### Riesgos principales
1. **Exposición de datos:** Comparticiones sin control de acceso donde cualquiera puede montar la carpeta y leer archivos sensibles.
2. **Escalada de privilegios:** Si está mal configurado (`no_root_squash` en `/etc/exports`), permite obtener acceso como **root** de forma inmediata mediante binarios con bit SUID.

---

## ⚙️ Ficheros de Configuración y Directivas Críticas

### Ruta Clave: `/etc/exports`
| Directiva | Impacto de Seguridad |
| :--- | :--- |
| `no_root_squash` | **Crítico:** Si un cliente se conecta como UID 0 (root local), el servidor confía y mantiene los privilegios de root sobre los archivos montados. |
| `root_squash` | Comportamiento seguro por defecto (convierte al root remoto en el usuario `nobody`). |
| `rw` / `ro` | Control de lectura y escritura o solo lectura sobre el recurso compartido. |
| `all_squash` | Mapea todos los usuarios entrantes al usuario anónimo `nobody`. |

---

## 🔎 1. Enumeración Inicial

### Consultar el Portmapper y Scripts Nmap
```bash
# Consultar servicios RPC activos
rpcinfo -p <TARGET_IP>
nmap -p 111,2049 -sV -sC <TARGET_IP>

# Scripts NSE para listar montajes
nmap -p 2049 --script=nfs-ls,nfs-statfs,nfs-showmount <TARGET_IP>
```

### Listar Carpetas Compartidas (`showmount`)
```bash
showmount -e <TARGET_IP>
```

---

## 🚀 2. Montaje y Gestión de Recursos NFS

```bash
# 1. Crear punto de montaje local
mkdir -p /tmp/nfs_target

# 2. Montaje estándar con nolock (evita bloqueos de red)
sudo mount -t nfs <TARGET_IP>:/<RECURSO> /tmp/nfs_target -o nolock

# 3. Montaje forzando versiones específicas (NFSv3 o NFSv4)
sudo mount -t nfs -o vers=3 <TARGET_IP>:/<RECURSO> /tmp/nfs_target
sudo mount -t nfs4 -o proto=tcp,port=2049 <TARGET_IP>:/<RECURSO> /tmp/nfs_target
```

### Inspección de Permisos, UIDs y GIDs:
```bash
ls -la /tmp/nfs_target           # Ver nombres de propietarios
ls -n /tmp/nfs_target            # Ver UID y GID numéricos de los archivos
```

> **Tip Táctico:** Si puedes montar el recurso pero no acceder por permisos, y observas que el propietario es `nobody` (UID 65534), puedes ejecutar comandos o navegar como ese usuario:
> ```bash
> sudo -u nobody ls -la /tmp/nfs_target
> ```

---

## 🛠️ Requisitos Locales
Si los comandos `mount` o `showmount` no están presentes en tu sistema:
```bash
sudo apt install nfs-common -y
```
