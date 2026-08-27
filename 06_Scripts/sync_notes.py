#!/usr/bin/env python3
"""
sync_notes.py
Sincronizador inteligente de notas de estudio desde CPTS_Notes hacia glmbx-web.
Normaliza y valida el Frontmatter YAML de Astro y gestiona la sincronización local y remota en Git.
"""

import os
import sys
import re
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Colores ANSI para salida en terminal
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
    print(f"{BOLD}DESCRIPCIÓN:{RESET}")
    print(f"  Sincroniza y transforma notas de estudio desde CPTS_Notes hacia glmbx-web.\n")
    print(f"{BOLD}USO:{RESET}")
    print(f"  ./sync_notes.py [MODO] [OPCIONES]\n")
    print(f"{BOLD}MODOS DE EJECUCIÓN (Seleccioná uno):{RESET}")
    print(f"  {GREEN}-l, --local{RESET}         {BOLD}Sincronización local:{RESET} Copia y normaliza notas hacia glmbx-web local (sin Git).")
    print(f"  {GREEN}--push-cpts{RESET}        {BOLD}Push CPTS_Notes:{RESET} Hace commit y push de cambios en el repositorio CPTS_Notes.")
    print(f"  {GREEN}-f, --full{RESET}          {BOLD}Flujo Completo:{RESET} Sincronización local + Push a CPTS_Notes + Push a glmbx-web.\n")
    print(f"{BOLD}OPCIONES ADICIONALES:{RESET}")
    print(f"  {YELLOW}-d, --dry-run{RESET}       {BOLD}Simulación:{RESET} Muestra qué notas se copiarían y qué cambios habría en Git sin modificar nada.")
    print(f"  {YELLOW}-h, --help{RESET}          Muestra este menú de ayuda detallado.\n")
    print(f"{BOLD}EJEMPLOS DE USO:{RESET}")
    print(f"  {CYAN}./sync_notes.py --local{RESET}            Copia notas modificadas a glmbx-web para probarlas localmente.")
    print(f"  {CYAN}./sync_notes.py --push-cpts{RESET}        Guarda y sube los cambios únicamente a tu repositorio CPTS_Notes.")
    print(f"  {CYAN}./sync_notes.py --full{RESET}             Sincroniza localmente y sube cambios a ambos repositorios remotos.")
    print(f"  {CYAN}./sync_notes.py --local --dry-run{RESET}  Simula la sincronización local sin tocar archivos en disco.\n")


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
    """
    modified = False
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw_text, re.DOTALL)
    
    if frontmatter_match:
        fm_content = frontmatter_match.group(1)
        body = frontmatter_match.group(2)
        
        has_title = bool(re.search(r"^title:\s*", fm_content, re.MULTILINE))
        has_pubdate = bool(re.search(r"^pubDate:\s*", fm_content, re.MULTILINE))
        
        new_fm_lines = fm_content.splitlines()
        
        if not has_title:
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
        first_h1 = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
        clean_title = first_h1.group(1).strip() if first_h1 else filename.replace(".md", "").replace("_", " ")
        today_str = datetime.now().strftime("%Y-%m-%d")
        final_text = f"---\ntitle: \"{clean_title}\"\npubDate: '{today_str}'\n---\n\n{raw_text.lstrip()}"
        modified = True

    return final_text, modified


def sync_notes(cpts_root: Path, web_notes_dir: Path, dry_run: bool = False) -> Tuple[int, int, int]:
    added, updated, deleted = 0, 0, 0
    
    if not web_notes_dir.exists():
        if not dry_run:
            web_notes_dir.mkdir(parents=True, exist_ok=True)
            
    source_files = {}
    for section in SECTIONS:
        sec_dir = cpts_root / section
        if sec_dir.exists():
            for p in sec_dir.rglob("*.md"):
                rel = p.relative_to(cpts_root)
                source_files[str(rel)] = p
                
    dest_files = {}
    if web_notes_dir.exists():
        for p in web_notes_dir.rglob("*.md"):
            rel = p.relative_to(web_notes_dir)
            dest_files[str(rel)] = p

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

    for rel_str, dest_path in sorted(dest_files.items()):
        top_folder = rel_str.split(os.sep)[0]
        if top_folder in SECTIONS:
            if rel_str not in source_files:
                deleted += 1
                print(f"  {RED}[-] ELIMINADO{RESET} {rel_str}")
                if not dry_run:
                    dest_path.unlink()

    return added, updated, deleted


def git_commit_and_push_cpts(cpts_root: Path, dry_run: bool = False) -> bool:
    print(f"\n{BOLD}🚀 Verificando Git en CPTS_Notes...{RESET}")
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cpts_root, capture_output=True, text=True, check=True
        )
        changes = status.stdout.strip()
        if not changes:
            print(f"{YELLOW}ℹ️ No hay cambios pendientes en CPTS_Notes para commitear.{RESET}")
            return False

        if dry_run:
            print(f"{YELLOW}[DRY-RUN] Cambios detectados en CPTS_Notes que se commitearían:{RESET}")
            for line in changes.splitlines():
                print(f"  {line}")
            print(f"{YELLOW}[DRY-RUN] Se ejecutaría: git add . && git commit -m 'docs: update notes' && git push{RESET}")
            return True

        subprocess.run(["git", "add", "."], cwd=cpts_root, check=True)
        commit_msg = f"docs: update study notes ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=cpts_root, check=True)
        print(f"{GREEN}✔ Commit creado en CPTS_Notes: {commit_msg}{RESET}")

        print(f"📤 Haciendo push a origin en CPTS_Notes...")
        subprocess.run(["git", "push"], cwd=cpts_root, check=True)
        print(f"{GREEN}✔ Push completado en CPTS_Notes exitosamente.{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Error en git (CPTS_Notes): {e}{RESET}")
        return False


def git_commit_and_push_web(web_root: Path, summary_msg: str, dry_run: bool = False) -> bool:
    print(f"\n{BOLD}🚀 Verificando Git en glmbx-web...{RESET}")
    target_path = "src/content/1_cibersecurity"
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain", target_path],
            cwd=web_root, capture_output=True, text=True, check=True
        )
        changes = status.stdout.strip()
        if not changes:
            print(f"{YELLOW}ℹ️ No hay cambios pendientes en glmbx-web ({target_path}) para commitear.{RESET}")
            return False

        if dry_run:
            print(f"{YELLOW}[DRY-RUN] Cambios detectados en glmbx-web ({target_path}) que se commitearían:{RESET}")
            for line in changes.splitlines():
                print(f"  {line}")
            print(f"{YELLOW}[DRY-RUN] Se ejecutaría: git add {target_path} && git commit -m 'docs(cibersecurity): sync notes from CPTS vault - {summary_msg}' && git push{RESET}")
            return True

        subprocess.run(["git", "add", target_path], cwd=web_root, check=True)
        commit_msg = f"docs(cibersecurity): sync notes from CPTS vault - {summary_msg}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=web_root, check=True)
        print(f"{GREEN}✔ Commit creado en glmbx-web: {commit_msg}{RESET}")

        print(f"📤 Haciendo push a origin en glmbx-web...")
        subprocess.run(["git", "push"], cwd=web_root, check=True)
        print(f"{GREEN}✔ Push completado en glmbx-web exitosamente.{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Error en git (glmbx-web): {e}{RESET}")
        return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sincronizador de notas de CPTS_Notes hacia glmbx-web.",
        add_help=False
    )
    parser.add_argument("-l", "--local", action="store_true", help="Sincronización local hacia glmbx-web (sin Git).")
    parser.add_argument("--push-cpts", action="store_true", help="Commit y push únicamente en el repositorio CPTS_Notes.")
    parser.add_argument("-f", "--full", action="store_true", help="Flujo completo: Sincronización local + Push en CPTS_Notes + Push en glmbx-web.")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Simula el proceso sin escribir en disco ni ejecutar Git.")
    parser.add_argument("-h", "--help", action="store_true", help="Muestra el menú de ayuda detallado.")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Si no se pasan argumentos o se solicita ayuda, mostrar menú explicativo
    if len(sys.argv) == 1 or args.help:
        print_help()
        return

    # Validar que al menos un modo o dry-run sea seleccionado
    if not (args.local or args.push_cpts or args.full or args.dry_run):
        print_help()
        return

    print_banner()
    cpts_root, web_root, web_notes_dir = get_paths()

    if not cpts_root.exists():
        print(f"{RED}❌ Error: No se encontró la carpeta CPTS_Notes en {cpts_root}{RESET}")
        sys.exit(1)

    if not web_root.exists():
        print(f"{RED}❌ Error: No se encontró el repositorio glmbx-web en {web_root}{RESET}")
        sys.exit(1)

    print(f"{BOLD}Rutas configuradas:{RESET}")
    print(f"  • Origen (Obsidian):  {CYAN}{cpts_root}{RESET}")
    print(f"  • Destino (Web):      {CYAN}{web_notes_dir}{RESET}")
    if args.dry_run:
        print(f"  • Modo:               {YELLOW}DRY-RUN (Simulación activa){RESET}")
    print()

    # Modo: Push solo en CPTS_Notes
    if args.push_cpts and not (args.local or args.full):
        git_commit_and_push_cpts(cpts_root, dry_run=args.dry_run)
        print(f"\n{GREEN}{BOLD}✨ Tarea de CPTS_Notes finalizada.{RESET}\n")
        return

    # Sincronización local (aplica para --local, --full o --dry-run standalone)
    added, updated, deleted = sync_notes(cpts_root, web_notes_dir, dry_run=args.dry_run)

    print(f"\n{BOLD}═════════════════ Resumen de Sincronización ═════════════════{RESET}")
    print(f"  • Agregados:   {GREEN}{added}{RESET}")
    print(f"  • Actualizados:{YELLOW}{updated}{RESET}")
    print(f"  • Eliminados:  {RED}{deleted}{RESET}")
    print(f"{BOLD}═════════════════════════════════════════════════════════════{RESET}")

    total_changes = added + updated + deleted
    summary_str = f"{added} added, {updated} updated, {deleted} deleted"

    # Manejo de Git según el modo elegido
    if args.full:
        git_commit_and_push_cpts(cpts_root, dry_run=args.dry_run)
        git_commit_and_push_web(web_root, summary_str, dry_run=args.dry_run)
    elif args.push_cpts:
        git_commit_and_push_cpts(cpts_root, dry_run=args.dry_run)
    elif args.local and not args.dry_run:
        print(f"\n{CYAN}💡 Tip:{RESET} Para sincronizar y publicar en ambos repositorios ejecutá: {BOLD}./sync_notes.py --full{RESET}\n")

    print(f"\n{GREEN}{BOLD}🚀 Proceso completado exitosamente.{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Operación cancelada por el usuario.{RESET}\n")
        sys.exit(0)
