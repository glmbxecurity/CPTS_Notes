# init-workspace.sh

```jsx
#!/bin/bash

# ==============================================================================
# Script para inicializar la estructura de carpetas de Pentesting / CTF
# ==============================================================================

# Función para crear la estructura base estándar
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

# Limpiar pantalla y mostrar banner
clear
echo "================================================="
echo "   🛡️  Pentest Workspace Generator"
echo "================================================="
echo ""
echo "¿Qué tipo de entorno vas a atacar?"
echo "  1) CTF Aislado (Máquina o Reto)"
echo "  2) Enterprise Network (Auditoría Corporativa)"
echo ""
read -p "Selecciona una opción [1 o 2]: " env_type

if [ "$env_type" == "1" ]; then
    # Flujo para CTF
    echo ""
    read -p "Introduce el nombre del CTF o de la máquina: " ctf_name
    
    # Normalizar nombre (reemplazar espacios por guiones bajos)
    ctf_name=$(echo "$ctf_name" | tr ' ' '_')
    base_dir="./CTFs/$ctf_name"
    
    echo -e "\n[*] Creando entorno para CTF: $ctf_name..."
    create_standard_structure "$base_dir"
    echo -e "\n[✔] Workspace de CTF listo."

elif [ "$env_type" == "2" ]; then
    # Flujo para Enterprise Network
    echo ""
    read -p "Introduce el nombre de la Empresa o Cliente: " company_name
    company_name=$(echo "$company_name" | tr ' ' '_')
    
    echo -e "\n[*] Iniciando proyecto corporativo para: $company_name"
    
    # Bucle para añadir múltiples activos
    while true; do
        echo ""
        read -p "Introduce el nombre de un activo/proyecto (o pulsa [ENTER] vacío para terminar): " asset_name
        
        # Si el input está vacío, salimos del bucle
        if [ -z "$asset_name" ]; then
            break
        fi
        
        asset_name=$(echo "$asset_name" | tr ' ' '_')
        
        # Preguntar por el tipo de test para este activo en concreto
        echo "  ¿Qué tipo de auditoría se realizará en $asset_name?"
        echo "    1) EPT (External Penetration Test)"
        echo "    2) IPT (Internal Penetration Test)"
        echo "    3) Ambos (EPT e IPT)"
        read -p "  Selecciona [1, 2 o 3]: " test_type
        
        case $test_type in
            1)
                create_standard_structure "./Projects/$company_name/$asset_name/EPT"
                ;;
            2)
                create_standard_structure "./Projects/$company_name/$asset_name/IPT"
                ;;
            3)
                create_standard_structure "./Projects/$company_name/$asset_name/EPT"
                create_standard_structure "./Projects/$company_name/$asset_name/IPT"
                ;;
            *)
                # Por defecto, si mete un valor raro, lo crea en la raíz del activo
                create_standard_structure "./Projects/$company_name/$asset_name"
                ;;
        esac
    done
    
    echo -e "\n[✔] Workspace corporativo completado para $company_name."

else
    echo -e "\n[!] Opción no válida. Abortando."
    exit 1
fi
```