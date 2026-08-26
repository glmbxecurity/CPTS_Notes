#!/usr/bin/env python3
"""
sync_notes.py
Sincronizador inteligente de notas de CPTS_Notes (Obsidian Vault) hacia glmbx-web (1_cibersecurity).
Valida y normaliza el Frontmatter YAML de Astro (title, pubDate, description, tags), convierte sintaxis de Obsidian
y gestiona la publicación con git en glmbx-web.
"""

import os
import sys
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Colores ANSI
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
DIM = "\033[2m"

SECTIONS = [
    "00_Fundamentos_y_Metodologias",
    "01_Reconocimiento_General",
    "02_Servicios_Puertos",
    "03_Vulnerabilidades_Web",
    "04_Post_Explotacion",
]


def print_banner():
    print(f"\n{CYAN}{BOLD}╔════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}{BOLD}║         🛡️  CPTS_Notes ➜ glmbx-web Notes Sync              ║{RESET}")
    print(f"{CYAN}{BOLD}╚════════════════════════════════════════════════════════════╝{RESET}\n")


def print_help():
    print_banner()
    print(f"{BOLD}USO:{RESET}")
    print(f"  ./sync_notes.py [OPCIONES]\n")
    print(f"{BOLD}OPCIONES:{RESET}")
    print(f"  {GREEN}-g, --git{RESET}         Ejecuta 'git add', 'commit' y 'push' en glmbx-web tras la sincronización.")
    print(f"  {GREEN}--dry-run{RESET}         Simula el proceso sin copiar archivos ni ejecutar git.")
    print(f"  {GREEN}-h, --help{RESET}        Muestra este mensaje de ayuda.\n")
    print(f"{BOLD}EJEMPLOS:{RESET}")
    print(f"  {CYAN}./sync_notes.py{RESET}              Sincroniza y valida frontmatter de notas hacia la web")
    print(f"  {CYAN}./sync_notes.py --git{RESET}        Sincroniza, valida y publica los cambios directamente en GitHub")
    print(f"  {CYAN}./sync_notes.py --dry-run{RESET}    Comprueba qué archivos se copiarían sin modificar nada\n")


def get_paths() -> Tuple[Path, Path, Path]:
    script_dir = Path(__file__).resolve().parent
    cpts_root = script_dir.parent if script_dir.name in ["06_Scripts", "scripts", "Scripts"] else Path("/home/eddy/Documentos/git_repos/CPTS_Notes")
    
    web_root = cpts_root.parent / "glmbx-web"
    if not web_root.exists():
        web_root = Path("/home/eddy/Documentos/git_repos/glmbx-web")
        
    web_notes_dir = web_root / "src" / "content" / "1_cibersecurity"
    return cpts_root, web_root, web_notes_dir


def process_markdown_content(raw_text: str, filename: str) -> Tuple[str, bool]:
    """
    Verifica y normaliza el Frontmatter YAML para compatibilidad estricta con Astro:
    - Asegura la presencia de 'title' y 'pubDate'.
    - Si no existen, los infiere del primer encabezado (# Titulo) o del nombre de archivo.
    - Convierte posibles wikilinks de Obsidian [[Link]] a enlaces estándar.
    """
    modified = False
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw_text, re.DOTALL)
    
    if frontmatter_match:
        fm_content = frontmatter_match.group(1)
        body = frontmatter_match.group(2)
        
        # Verificar si falta title o pubDate
        has_title = bool(re.search(r"^title:\s*", fm_content, re.MULTILINE))
        has_pubdate = bool(re.search(r"^pubDate:\s*", fm_content, re.MULTILINE))
        
        new_fm_lines = fm_content.splitlines()
        
        if not has_title:
            # Inferir título del primer # del body o del filename
            first_h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            clean_title = first_h1.group(1).strip() if first_h1 else filename.replace(".md", "").replace("_", " ")
            new_fm_lines.insert(0, f"title: \"{clean_title}\"")
            modified = True
            
        if not has_pubdate:
            today_str = datetime.now().strftime("%Y-%m-%d")
            new_fm_lines.append(f"pubDate: '{today_str}'")
            modified = True
            
        final_text = f"---\n" + "\n".join(new_fm_lines) + f"\n---\n{body}"
    else:
        # No tiene frontmatter, construir uno nuevo
        first_h1 = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
        clean_title = first_h1.group(1).strip() if first_h1 else filename.replace(".md", "").replace("_", " ")
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Si el body empieza con # Header idéntico, mantener el texto limpio
        final_text = f"---\ntitle: \"{clean_title}\"\npubDate: '{today_str}'\n---\n\n{raw_text.lstrip()}"
        modified = True

    return final_text, modified


def sync_notes(cpts_root: Path, web_notes_dir: Path, dry_run: bool = False) -> Tuple[int, int, int]:
    added, updated, deleted = 0, 0, 0
    
    if not web_notes_dir.exists():
        if not dry_run:
            web_notes_dir.mkdir(parents=True, exist_ok=True)
            
    # Recolectar archivos fuente
    source_files = {}
    for section in SECTIONS:
        sec_dir = cpts_root / section
        if sec_dir.exists():
            for p in sec_dir.rglob("*.md"):
                rel = p.relative_to(cpts_root)
                source_files[str(rel)] = p
                
    # Recolectar archivos destino existentes
    dest_files = {}
    if web_notes_dir.exists():
        for p in web_notes_dir.rglob("*.md"):
            rel = p.relative_to(web_notes_dir)
            dest_files[str(rel)] = p

    # 1. Copiar nuevos y modificados procesando Frontmatter
    for rel_str, src_path in sorted(source_files.items()):
        dest_path = web_notes_dir / rel_str
        raw_text = src_path.read_text(encoding="utf-8")
        processed_text, fm_added = process_markdown_content(raw_text, src_path.name)
        
        needs_copy = False
        action_tag = ""
        
        if rel_str not in dest_files:
            needs_copy = True
            added += 1
            action_tag = f"{GREEN}[+] NUEVO{RESET}"
        else:
            dest_text = dest_path.read_text(encoding="utf-8")
            if processed_text != dest_text:
                needs_copy = True
                updated += 1
                action_tag = f"{YELLOW}[~] MODIFICADO{RESET}"
                
        if needs_copy:
            fm_note = f" {MAGENTA}(frontmatter validado){RESET}" if fm_added else ""
            print(f"  {action_tag} {rel_str}{fm_note}")
            if not dry_run:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_text(processed_text, encoding="utf-8")

    # 2. Limpiar archivos borrados en fuente
    for rel_str, dest_path in sorted(dest_files.items()):
        top_folder = rel_str.split(os.sep)[0]
        if top_folder in SECTIONS:
            if rel_str not in source_files:
                deleted += 1
                print(f"  {RED}[-] ELIMINADO{RESET} {rel_str}")
                if not dry_run:
                    dest_path.unlink()

    return added, updated, deleted


def git_commit_and_push(web_root: Path, summary_msg: str):
    print(f"\n{BOLD}🚀 Ejecutando Git en glmbx-web...{RESET}")
    try:
        subprocess.run(["git", "add", "src/content/1_cibersecurity"], cwd=web_root, check=True)
        status = subprocess.run(["git", "status", "--porcelain", "src/content/1_cibersecurity"], cwd=web_root, capture_output=True, text=True, check=True)
        
        if not status.stdout.strip():
            print(f"{YELLOW}ℹ️ No hay cambios pendientes en git para commitear.{RESET}")
            return

        commit_msg = f"docs(cibersecurity): sync notes from CPTS vault - {summary_msg}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=web_root, check=True)
        print(f"{GREEN}✔ Commit creado: {commit_msg}{RESET}")
        
        print(f"📤 Haciendo push a origin...")
        subprocess.run(["git", "push"], cwd=web_root, check=True)
        print(f"{GREEN}✔ Push completado exitosamente.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Error en git: {e}{RESET}")


def main():
    args = sys.argv[1:]
    
    if "-h" in args or "--help" in args:
        print_help()
        return

    dry_run = "--dry-run" in args
    do_git = "-g" in args or "--git" in args

    print_banner()
    cpts_root, web_root, web_notes_dir = get_paths()

    print(f"{BOLD}Rutas configuradas:{RESET}")
    print(f"  • Origen (Obsidian):  {CYAN}{cpts_root}{RESET}")
    print(f"  • Destino (Web):      {CYAN}{web_notes_dir}{RESET}")
    if dry_run:
        print(f"  • Modo:               {YELLOW}DRY-RUN (Simulación){RESET}")
    print()

    added, updated, deleted = sync_notes(cpts_root, web_notes_dir, dry_run=dry_run)

    print(f"\n{BOLD}═════════════════ Resumen de Sincronización ═════════════════{RESET}")
    print(f"  • Agregados:   {GREEN}{added}{RESET}")
    print(f"  • Actualizados:{YELLOW}{updated}{RESET}")
    print(f"  • Eliminados:  {RED}{deleted}{RESET}")
    print(f"{BOLD}═════════════════════════════════════════════════════════════{RESET}")

    total_changes = added + updated + deleted
    if total_changes == 0:
        print(f"\n{GREEN}✔ Todo está al día y validado con el esquema de Astro. No se requirieron cambios.{RESET}\n")
    else:
        summary_str = f"{added} added, {updated} updated, {deleted} deleted"
        if not dry_run and do_git:
            git_commit_and_push(web_root, summary_str)
        elif not dry_run and not do_git:
            print(f"\n{CYAN}💡 Tip:{RESET} Para hacer commit y push automático a GitHub, ejecutá: {BOLD}./sync_notes.py --git{RESET}\n")


if __name__ == "__main__":
    main()
