---
title: Organización del Workspace y Documentación
pubDate: '2026-08-26'
---

La organización, la productividad y una documentación precisa son fundamentales para el éxito en la ciberseguridad. Un profesional técnico desorganizado tendrá dificultades para ser eficiente, especialmente durante la fase de elaboración de informes.

## 📁 1. Estructura de Carpetas

Es imperativo mantener una jerarquía de directorios estandarizada en la máquina de ataque para separar entornos, evaluaciones y tipos de datos.

### Estructura de Directorios Estándar (script init-workspace.sh)

Se debe separar por cliente y, dentro de este, por tipo de evaluación (ej. `EPT` - Externa, `IPT` - Interna).

```bash
Projects/
└── Nombre_del_Cliente/
    ├── EPT/  (External Penetration Test)
    │   ├── evidence/      (Evidencias)
    │   │   ├── credentials/   (Credenciales obtenidas)
    │   │   ├── data/          (Datos sensibles exfiltrados)
    │   │   └── screenshots/   (Capturas de pantalla)
    │   ├── logs/          (Registros de actividad/sesiones)
    │   ├── scans/         (Salidas de Nmap, Nessus, etc.)
    │   ├── scope/         (Listas de IPs, redes, dominios)
    │   └── tools/         (Herramientas o scripts específicos usados)
    └── IPT/  (Internal Penetration Test)
        ├── evidence/
        ├── logs/
        ├── scans/
        ├── scope/
        └── tools/
```

### Script Automatizado (`init-workspace.sh`):
```bash
#!/bin/bash
create_standard_structure() {
    local target_dir="$1"
    mkdir -p "$target_dir/evidence/credentials"
    mkdir -p "$target_dir/evidence/data"
    mkdir -p "$target_dir/evidence/screenshots"
    mkdir -p "$target_dir/logs"
    mkdir -p "$target_dir/scans"
    mkdir -p "$target_dir/scope"
    mkdir -p "$target_dir/tools"
    echo -e "  [+] Estructura desplegada en: $target_dir"
}

clear
echo "================================================="
echo "   🛡️  Pentest Workspace Generator"
echo "================================================="
echo ""
echo "¿Qué tipo de entorno vas a atacar?"
echo "  1) CTF Aislado (Máquina o Reto)"
echo "  2) Enterprise Network (Auditoría Corporativa)"
read -p "Selecciona una opción [1 o 2]: " env_type

if [ "$env_type" == "1" ]; then
    read -p "Introduce el nombre del CTF o de la máquina: " ctf_name
    ctf_name=$(echo "$ctf_name" | tr ' ' '_')
    create_standard_structure "./CTFs/$ctf_name"
    echo -e "\n[✔] Workspace de CTF listo."
elif [ "$env_type" == "2" ]; then
    read -p "Introduce el nombre de la Empresa o Cliente: " company_name
    company_name=$(echo "$company_name" | tr ' ' '_')
    while true; do
        read -p "Introduce el nombre de un activo (o ENTER vacío para terminar): " asset_name
        [ -z "$asset_name" ] && break
        asset_name=$(echo "$asset_name" | tr ' ' '_')
        echo "  ¿Tipo de auditoría en $asset_name? 1) EPT, 2) IPT, 3) Ambos"
        read -p "  Selecciona [1, 2 o 3]: " test_type
        case $test_type in
            1) create_standard_structure "./Projects/$company_name/$asset_name/EPT" ;;
            2) create_standard_structure "./Projects/$company_name/$asset_name/IPT" ;;
            3) create_standard_structure "./Projects/$company_name/$asset_name/EPT"
               create_standard_structure "./Projects/$company_name/$asset_name/IPT" ;;
            *) create_standard_structure "./Projects/$company_name/$asset_name" ;;
        esac
    done
    echo -e "\n[✔] Workspace corporativo completado para $company_name."
fi
```

*Nota operativa:* La organización de evidencias puede adaptarse (ej. crear una subcarpeta por cada host objetivo), pero debe mantenerse consistente en toda la auditoría.

---

## 📝 2. Herramientas para Tomar Notas

La elección de la herramienta es personal, pero debe permitir estructurar páginas tipo Wiki, chuletas (*cheat sheets*) y búsqueda rápida. Se recomienda dominar **Markdown** para agilizar el formato visual.

**Herramientas recomendadas:**

- Cherrytree
- Visual Studio Code
- Evernote
- Notion
- GitBook
- Sublime Text
- Notepad++

> ⚠️ **ADVERTENCIA DE SEGURIDAD CRÍTICA:** Al trabajar en entornos de clientes reales, es obligatorio garantizar que la herramienta elegida **NO sincronice los datos con la nube** (ej. cuidado con Notion o Evernote en auditorías confidenciales). Los datos del cliente deben almacenarse de forma estrictamente **local**.

---

## 🧠 3. Base de Conocimiento y Bases de Datos de Hallazgos

Todo pentester debe construir y mantener un repositorio personal de conocimiento técnico para evitar el re-trabajo continuo.

### Componentes de la Base de Conocimiento

- **Guías de referencia rápida:** Pasos para configuraciones recurrentes.
- **Chuletas (Cheat sheets):** Comandos comunes clasificados por cada fase de la evaluación (Reconocimiento, Explotación, Escalada de privilegios).
- **Repositorio de Payloads:** Recopilación de payloads y scripts funcionales obtenidos de formaciones, laboratorios (HTB) y auditorías pasadas.

### Base de Datos de Vulnerabilidades (Plantillas de Informes)

Para ahorrar tiempo durante la redacción del informe final, se debe mantener una base de datos (hoja de cálculo o wiki) con vulnerabilidades pre-redactadas que incluya siempre estos 5 campos:

1. **Título del hallazgo**
2. **Descripción técnica**
3. **Impacto** (Consecuencias reales para el negocio)
4. **Consejos de remediación** (Soluciones o parches)
5. **Referencias** (Enlaces a CVEs, OWASP, documentación oficial)

Disponer de esto permite que, al encontrar un fallo, solo se requiera personalizar la evidencia para el entorno objetivo, en lugar de redactar todo desde cero.
