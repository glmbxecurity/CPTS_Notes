#!/usr/bin/env python3
"""
sync_writeups.py
Sincronizador automático e interactivo de writeups desde CPTS_Notes hacia glmbx-web.
Infiere metadatos (título, plataforma, dificultad, certificación), transforma imágenes Obsidian
y gestiona la sincronización local y remota en Git.
"""

import os
import sys
import re
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Colores ANSI para salida en terminal
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
DIM = "\033[2m"

PLATFORMS = ["HackTheBox", "TryHackMe", "VulnHub", "Proving Grounds", "Other"]
DIFFICULTIES = ["Easy", "Medium", "Hard", "Insane"]


def print_banner():
    print(f"\n{CYAN}{BOLD}╔════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}{BOLD}║         🛡️  CPTS_Notes ➜ glmbx-web Writeups Sync           ║{RESET}")
    print(f"{CYAN}{BOLD}╚════════════════════════════════════════════════════════════╝{RESET}\n")


def print_help():
    print_banner()
    print(f"{BOLD}DESCRIPCIÓN:{RESET}")
    print(f"  Detecta, transforma y sincroniza writeups de CTFs desde CPTS_Notes hacia glmbx-web.\n")
    print(f"{BOLD}USO:{RESET}")
    print(f"  ./sync_writeups.py [MODO] [OPCIONES]\n")
    print(f"{BOLD}MODOS DE EJECUCIÓN (Seleccioná uno):{RESET}")
    print(f"  {GREEN}-l, --local{RESET}         {BOLD}Sincronización local:{RESET} Procesa y copia writeups hacia glmbx-web local (sin Git).")
    print(f"  {GREEN}--push-cpts{RESET}        {BOLD}Push CPTS_Notes:{RESET} Hace commit y push de cambios en el repositorio CPTS_Notes.")
    print(f"  {GREEN}-f, --full{RESET}          {BOLD}Flujo Completo:{RESET} Sincronización local + Push a CPTS_Notes + Push a glmbx-web.\n")
    print(f"{BOLD}MODO DE IMPORTACIÓN:{RESET}")
    print(f"  {CYAN}-i, --interactive{RESET}   Modo interactivo: Valida o edita título, plataforma y dificultad uno a uno (por defecto).")
    print(f"  {CYAN}-a, --auto{RESET}          Modo automático: Acepta todas las inferencias y sincroniza de forma 100% desatendida.\n")
    print(f"{BOLD}OPCIONES ADICIONALES:{RESET}")
    print(f"  {YELLOW}-d, --dry-run{RESET}       {BOLD}Simulación:{RESET} Muestra qué writeups e imágenes se procesarían sin modificar nada.")
    print(f"  {YELLOW}--all{RESET}               Fuerza la re-sincronización de todos los writeups (incluso los existentes).")
    print(f"  {YELLOW}-h, --help{RESET}          Muestra este menú de ayuda detallado.\n")
    print(f"{BOLD}EJEMPLOS DE USO:{RESET}")
    print(f"  {CYAN}./sync_writeups.py --local -a{RESET}            Sincroniza writeups nuevos a glmbx-web de forma automática.")
    print(f"  {CYAN}./sync_writeups.py --local -i{RESET}            Sincroniza revisando los metadatos interactivamente.")
    print(f"  {CYAN}./sync_writeups.py --push-cpts{RESET}          Guarda y sube los writeups a tu repositorio CPTS_Notes.")
    print(f"  {CYAN}./sync_writeups.py --full -a{RESET}            Sincroniza y publica todo automáticamente en ambos repositorios.")
    print(f"  {CYAN}./sync_writeups.py --local --dry-run{RESET}    Simula el proceso de detección sin escribir en disco.\n")


def get_paths() -> Tuple[Path, Path, Path, Path]:
    """Obtiene las rutas base de CPTS_Notes y glmbx-web."""
    script_dir = Path(__file__).resolve().parent
    cpts_root = script_dir.parent if script_dir.name in ["06_Scripts", "scripts", "Scripts"] else Path("/home/eddy/Documentos/git_repos/CPTS_Notes")
    
    web_root = cpts_root.parent / "glmbx-web"
    if not web_root.exists():
        web_root = Path("/home/eddy/Documentos/git_repos/glmbx-web")
        
    web_writeups_dir = web_root / "src" / "content" / "ctf_writeups"
    web_images_dir = web_root / "public" / "images" / "ctf_writeups"
    
    return cpts_root, web_root, web_writeups_dir, web_images_dir


def find_writeup_files(cpts_root: Path) -> List[Path]:
    """Busca archivos markdown de writeups en CPTS_Notes."""
    writeup_files = []
    
    for path in cpts_root.rglob("*.md"):
        if any(part.startswith(".") for part in path.parts):
            continue
        
        parent_name = path.parent.name.lower()
        if "writeup" in parent_name:
            writeup_files.append(path)
            
    writeup_files.sort(key=lambda p: p.name.lower())
    return writeup_files


def get_existing_web_writeups(web_writeups_dir: Path) -> Dict[str, Path]:
    """Obtiene un mapa de los writeups ya existentes en glmbx-web por nombre de archivo y por título."""
    existing = {}
    if not web_writeups_dir.exists():
        return existing
        
    for p in web_writeups_dir.rglob("*.md"):
        if p.is_file():
            existing[p.name.lower()] = p
            clean_stem = re.sub(r"[-_\s]", "", p.stem.lower())
            existing[clean_stem] = p
            
            try:
                content = p.read_text(encoding="utf-8")
                match = re.search(r"^title:\s*['\"]?(.*?)['\"]?\s*$", content, re.MULTILINE)
                if match:
                    title_clean = re.sub(r"[-_\s]", "", match.group(1).lower())
                    existing[title_clean] = p
            except Exception:
                pass
                
    return existing


def infer_metadata(file_path: Path, content: str) -> Dict[str, any]:
    """Infiere metadatos por defecto a partir del contenido y nombre de archivo."""
    meta = {}
    
    # 1. Título
    h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1_match:
        raw_title = h1_match.group(1).strip()
        clean_title = re.sub(r"[\s\-_]+(Hack\s*The\s*Box|HTB|TryHackMe|THM|VulnHub|Writeup).*$", "", raw_title, flags=re.IGNORECASE).strip()
        meta["title"] = clean_title if clean_title else file_path.stem
    else:
        meta["title"] = file_path.stem
        
    # 2. Fecha (hoy)
    meta["pubDate"] = datetime.now().strftime("%Y-%m-%d")
    
    # 3. Plataforma
    parent_lower = file_path.parent.name.lower()
    content_lower = content[:1500].lower()
    
    if "htb" in parent_lower or "hackthebox" in parent_lower or "hack the box" in content_lower:
        meta["platform"] = "HackTheBox"
    elif "thm" in parent_lower or "tryhackme" in parent_lower or "try hack me" in content_lower:
        meta["platform"] = "TryHackMe"
    elif "vulnhub" in parent_lower or "vulnhub" in content_lower:
        meta["platform"] = "VulnHub"
    elif "proving" in parent_lower or "pg" in parent_lower or "proving grounds" in content_lower:
        meta["platform"] = "Proving Grounds"
    else:
        meta["platform"] = "HackTheBox"
        
    # 4. Dificultad
    if re.search(r"\b(easy|fácil|facil)\b", content_lower):
        meta["difficulty"] = "Easy"
    elif re.search(r"\b(medium|media|medio)\b", content_lower):
        meta["difficulty"] = "Medium"
    elif re.search(r"\b(insane|locura)\b", content_lower):
        meta["difficulty"] = "Insane"
    elif re.search(r"\b(hard|difícil|dificil)\b", content_lower):
        meta["difficulty"] = "Hard"
    else:
        meta["difficulty"] = "Easy"
        
    # 5. Certificación por defecto
    meta["certification"] = ["CPTS"]
    
    # 6. Descripción corta
    intro_match = re.search(r"##\s*Introduction\s*\n+([^\n#]+)", content, re.IGNORECASE)
    if intro_match:
        first_sentence = intro_match.group(1).strip()
        first_sentence = re.sub(r"\*\*([^*]+)\*\*", r"\1", first_sentence)
        if len(first_sentence) > 140:
            first_sentence = first_sentence[:137] + "..."
        meta["description"] = first_sentence
    else:
        meta["description"] = ""
        
    meta["path"] = []
    meta["tags"] = []
    
    return meta


def prompt_user_metadata(inferred: Dict[str, any], filename: str, auto_mode: bool = False) -> Optional[Dict[str, any]]:
    """Pregunta de forma interactiva con valores por defecto inteligentes."""
    if auto_mode:
        return inferred
        
    print(f"\n{MAGENTA}─────────────────────────────────────────────────────────────{RESET}")
    print(f"📄 {BOLD}Writeup detectado:{RESET} {CYAN}{filename}{RESET}")
    print(f"{MAGENTA}─────────────────────────────────────────────────────────────{RESET}")
    
    skip = input(f"{YELLOW}¿Deseas importar este writeup? [S/n]: {RESET}").strip().lower()
    if skip in ["n", "no"]:
        print(f"{DIM}Saltando {filename}...{RESET}")
        return None
        
    meta = {}
    
    # 1. Título
    title_default = inferred.get("title", "")
    title_in = input(f"🔹 {BOLD}Título{RESET} [{GREEN}{title_default}{RESET}]: ").strip()
    meta["title"] = title_in if title_in else title_default
    
    # 2. Fecha
    date_default = inferred.get("pubDate", datetime.now().strftime("%Y-%m-%d"))
    date_in = input(f"🔹 {BOLD}Fecha (YYYY-MM-DD){RESET} [{GREEN}{date_default}{RESET}]: ").strip()
    meta["pubDate"] = date_in if date_in else date_default
    
    # 3. Plataforma
    plat_default = inferred.get("platform", "HackTheBox")
    print(f"🔹 {BOLD}Plataforma{RESET}:")
    for idx, p in enumerate(PLATFORMS, 1):
        indicator = f" {GREEN}(default){RESET}" if p == plat_default else ""
        print(f"   [{idx}] {p}{indicator}")
    plat_in = input(f"   Selecciona número o pulsa Enter para [{GREEN}{plat_default}{RESET}]: ").strip()
    if plat_in.isdigit() and 1 <= int(plat_in) <= len(PLATFORMS):
        meta["platform"] = PLATFORMS[int(plat_in) - 1]
    else:
        meta["platform"] = plat_default
        
    # 4. Dificultad
    diff_default = inferred.get("difficulty", "Easy")
    print(f"🔹 {BOLD}Dificultad{RESET}:")
    for idx, d in enumerate(DIFFICULTIES, 1):
        indicator = f" {GREEN}(default){RESET}" if d == diff_default else ""
        print(f"   [{idx}] {d}{indicator}")
    diff_in = input(f"   Selecciona número o pulsa Enter para [{GREEN}{diff_default}{RESET}]: ").strip()
    if diff_in.isdigit() and 1 <= int(diff_in) <= len(DIFFICULTIES):
        meta["difficulty"] = DIFFICULTIES[int(diff_in) - 1]
    else:
        meta["difficulty"] = diff_default
        
    # 5. Certificaciones
    cert_default = ", ".join(inferred.get("certification", ["CPTS"]))
    cert_in = input(f"🔹 {BOLD}Certificaciones (separadas por coma){RESET} [{GREEN}{cert_default}{RESET}]: ").strip()
    if cert_in:
        meta["certification"] = [c.strip() for c in cert_in.split(",") if c.strip()]
    else:
        meta["certification"] = inferred.get("certification", ["CPTS"])
        
    # 6. Path / Ruta opcional
    path_default = ", ".join(inferred.get("path", []))
    path_in = input(f"🔹 {BOLD}Path / Track (opcional, ej: THM Offensive Pentesting){RESET} [{GREEN}{path_default if path_default else 'ninguno'}{RESET}]: ").strip()
    if path_in:
        meta["path"] = [p.strip() for p in path_in.split(",") if p.strip()]
    else:
        meta["path"] = inferred.get("path", [])
        
    # 7. Tags opcionales
    tags_default = ", ".join(inferred.get("tags", []))
    tags_in = input(f"🔹 {BOLD}Tags (opcionales, separados por coma){RESET} [{GREEN}{tags_default if tags_default else 'ninguno'}{RESET}]: ").strip()
    if tags_in:
        meta["tags"] = [t.strip() for t in tags_in.split(",") if t.strip()]
    else:
        meta["tags"] = inferred.get("tags", [])
        
    # 8. Descripción corta
    desc_default = inferred.get("description", "")
    desc_in = input(f"🔹 {BOLD}Descripción corta{RESET} [{GREEN}{desc_default[:50] + '...' if len(desc_default) > 50 else desc_default}{RESET}]: ").strip()
    meta["description"] = desc_in if desc_in else desc_default
    
    return meta


def process_markdown_and_assets(
    source_file: Path,
    content: str,
    meta: Dict[str, any],
    web_images_dir: Path,
    dry_run: bool = False
) -> str:
    """Transforma el markdown: añade frontmatter, convierte imágenes de Obsidian y limpia duplicados de H1."""
    source_dir = source_file.parent
    assets_dir = source_dir / "assets"
    
    def replace_obsidian_image(match):
        raw_target = match.group(1).split("|")[0].strip()
        img_name = Path(raw_target).name
        
        found_source = None
        if assets_dir.exists() and (assets_dir / img_name).exists():
            found_source = assets_dir / img_name
        elif (source_dir / img_name).exists():
            found_source = source_dir / img_name
            
        if found_source:
            if not dry_run:
                web_images_dir.mkdir(parents=True, exist_ok=True)
                dest_img = web_images_dir / img_name
                shutil.copy2(found_source, dest_img)
            print(f"  {GREEN}✔{RESET} Imagen procesada: {img_name} ➔ public/images/ctf_writeups/")
            return f"![{meta['title']}](/images/ctf_writeups/{img_name})"
        else:
            return f"![{img_name}](/images/ctf_writeups/{img_name})"
            
    processed_content = re.sub(r"!\[\[(.*?)\]\]", replace_obsidian_image, content)
    processed_content = re.sub(r"^---\n.*?\n---\n+", "", processed_content, flags=re.DOTALL)
    
    h1_match = re.search(r"^#\s+(.+)$", processed_content, re.MULTILINE)
    if h1_match:
        processed_content = re.sub(r"^#\s+.+\n+", "", processed_content, count=1)
        
    frontmatter_lines = ["---"]
    frontmatter_lines.append(f"title: {meta['title']}")
    frontmatter_lines.append(f"pubDate: {meta['pubDate']}")
    if meta.get("difficulty"):
        frontmatter_lines.append(f"difficulty: {meta['difficulty']}")
    if meta.get("platform"):
        frontmatter_lines.append(f"platform: {meta['platform']}")
        
    if meta.get("certification"):
        frontmatter_lines.append("certification:")
        for c in meta["certification"]:
            frontmatter_lines.append(f"  - {c}")
            
    if meta.get("path"):
        frontmatter_lines.append("path:")
        for p in meta["path"]:
            frontmatter_lines.append(f"  - {p}")
            
    if meta.get("tags"):
        frontmatter_lines.append("tags:")
        for t in meta["tags"]:
            frontmatter_lines.append(f"  - {t}")
            
    if meta.get("description"):
        escaped_desc = meta["description"].replace('"', '\\"')
        frontmatter_lines.append(f'description: "{escaped_desc}"')
        
    frontmatter_lines.append("---\n")
    
    final_text = "\n".join(frontmatter_lines) + "\n" + processed_content.lstrip()
    return final_text


def git_commit_and_push_cpts(cpts_root: Path, dry_run: bool = False) -> bool:
    """Realiza commit y push en el repositorio CPTS_Notes."""
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
            print(f"{YELLOW}[DRY-RUN] Se ejecutaría: git add . && git commit -m 'docs: update writeups' && git push{RESET}")
            return True

        subprocess.run(["git", "add", "."], cwd=cpts_root, check=True)
        commit_msg = f"docs(ctf): update writeups ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=cpts_root, check=True)
        print(f"{GREEN}✔ Commit creado en CPTS_Notes: {commit_msg}{RESET}")

        print(f"📤 Haciendo push a origin en CPTS_Notes...")
        subprocess.run(["git", "push"], cwd=cpts_root, check=True)
        print(f"{GREEN}✔ Push completado en CPTS_Notes exitosamente.{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Error en git (CPTS_Notes): {e}{RESET}")
        return False


def git_commit_and_push_web(web_root: Path, writeup_titles: List[str], dry_run: bool = False) -> bool:
    """Realiza commit y push en el repositorio glmbx-web."""
    print(f"\n{BOLD}🚀 Verificando Git en glmbx-web...{RESET}")
    targets = ["src/content/ctf_writeups", "public/images/ctf_writeups"]
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"] + targets,
            cwd=web_root, capture_output=True, text=True, check=True
        )
        changes = status.stdout.strip()
        if not changes:
            print(f"{YELLOW}ℹ️ No hay cambios pendientes en glmbx-web para commitear.{RESET}")
            return False

        titles_str = ", ".join(writeup_titles) if writeup_titles else "update ctf writeups"
        if len(writeup_titles) == 1:
            commit_msg = f"feat(ctf): add writeup for {writeup_titles[0]}"
        elif len(writeup_titles) > 1:
            commit_msg = f"feat(ctf): add {len(writeup_titles)} writeups ({titles_str})"
        else:
            commit_msg = "feat(ctf): update writeups and assets"

        if dry_run:
            print(f"{YELLOW}[DRY-RUN] Cambios detectados en glmbx-web que se commitearían:{RESET}")
            for line in changes.splitlines():
                print(f"  {line}")
            print(f"{YELLOW}[DRY-RUN] Se ejecutaría: git add {' '.join(targets)} && git commit -m '{commit_msg}' && git push{RESET}")
            return True

        subprocess.run(["git", "add"] + targets, cwd=web_root, check=True)
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
        description="Sincronizador de writeups de CPTS_Notes hacia glmbx-web.",
        add_help=False
    )
    parser.add_argument("-l", "--local", action="store_true", help="Sincronización local hacia glmbx-web (sin Git).")
    parser.add_argument("--push-cpts", action="store_true", help="Commit y push únicamente en el repositorio CPTS_Notes.")
    parser.add_argument("-f", "--full", action="store_true", help="Flujo completo: Sincronización local + Push en CPTS_Notes + Push en glmbx-web.")
    parser.add_argument("-a", "--auto", action="store_true", help="Modo automático / desatendido (usa metadatos inferidos).")
    parser.add_argument("-i", "--interactive", action="store_true", help="Modo interactivo para validar/ajustar metadatos.")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Simula el proceso sin escribir en disco ni ejecutar Git.")
    parser.add_argument("--all", action="store_true", help="Fuerza la re-sincronización de todos los writeups.")
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
    auto_mode = args.auto and not args.interactive

    cpts_root, web_root, web_writeups_dir, web_images_dir = get_paths()

    if not cpts_root.exists():
        print(f"{RED}❌ Error: No se encontró la carpeta CPTS_Notes en {cpts_root}{RESET}")
        sys.exit(1)

    if not web_root.exists():
        print(f"{RED}❌ Error: No se encontró el repositorio glmbx-web en {web_root}{RESET}")
        sys.exit(1)

    print(f"{BOLD}Rutas configuradas:{RESET}")
    print(f"  • Origen (CPTS_Notes):  {CYAN}{cpts_root}{RESET}")
    print(f"  • Destino (glmbx-web):  {CYAN}{web_writeups_dir}{RESET}")
    if args.dry_run:
        print(f"  • Modo:                 {YELLOW}DRY-RUN (Simulación activa){RESET}")
    print()

    # Modo: Push solo en CPTS_Notes
    if args.push_cpts and not (args.local or args.full):
        git_commit_and_push_cpts(cpts_root, dry_run=args.dry_run)
        print(f"\n{GREEN}{BOLD}✨ Tarea de CPTS_Notes finalizada.{RESET}\n")
        return

    # Búsqueda y preparación de writeups
    cpts_writeups = find_writeup_files(cpts_root)
    if not cpts_writeups:
        print(f"{YELLOW}No se encontraron archivos de writeups en {cpts_root}.{RESET}")
        return

    existing_web = get_existing_web_writeups(web_writeups_dir)
    pending_files = []
    for file_path in cpts_writeups:
        clean_name = re.sub(r"[-_\s]", "", file_path.stem.lower())
        if args.all or (file_path.name.lower() not in existing_web and clean_name not in existing_web):
            pending_files.append(file_path)
        else:
            print(f"  {DIM}✔ Ya en la web: {file_path.name}{RESET}")

    if not pending_files:
        print(f"\n{GREEN}{BOLD}✨ ¡Todos los writeups de CPTS_Notes ya están sincronizados en glmbx-web!{RESET}")
        if not args.all:
            print(f"{DIM}Usa --all para forzar la re-sincronización de todos.{RESET}\n")
    else:
        print(f"\n{CYAN}{BOLD}Se encontraron {len(pending_files)} writeup(s) pendientes de sincronizar:{RESET}")
        for p in pending_files:
            print(f"  📌 {p.name} ({p.parent.name})")

    imported_titles = []
    if pending_files:
        if not args.dry_run:
            web_writeups_dir.mkdir(parents=True, exist_ok=True)

        for file_path in pending_files:
            content = file_path.read_text(encoding="utf-8")
            inferred = infer_metadata(file_path, content)
            
            meta = prompt_user_metadata(inferred, file_path.name, auto_mode=auto_mode)
            if not meta:
                continue
                
            final_markdown = process_markdown_and_assets(file_path, content, meta, web_images_dir, dry_run=args.dry_run)
            
            dest_filename = f"{meta['title'].replace('/', '-').replace(' ', '-')}.md"
            dest_file = web_writeups_dir / dest_filename
            
            if not args.dry_run:
                dest_file.write_text(final_markdown, encoding="utf-8")
                print(f"  {GREEN}{BOLD}✔ Guardado:{RESET} {dest_file.relative_to(web_root)}")
            else:
                print(f"  {YELLOW}{BOLD}[DRY-RUN] Se guardaría:{RESET} {dest_file.relative_to(web_root)}")
                
            imported_titles.append(meta["title"])

    # Manejo de Git según el modo
    if args.full:
        git_commit_and_push_cpts(cpts_root, dry_run=args.dry_run)
        git_commit_and_push_web(web_root, imported_titles, dry_run=args.dry_run)
    elif args.push_cpts:
        git_commit_and_push_cpts(cpts_root, dry_run=args.dry_run)
    elif args.local and not args.dry_run:
        print(f"\n{CYAN}💡 Tip:{RESET} Para sincronizar y publicar en ambos repositorios ejecutá: {BOLD}./sync_writeups.py --full -a{RESET}\n")

    print(f"\n{GREEN}{BOLD}🚀 Proceso completado exitosamente.{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Operación cancelada por el usuario.{RESET}\n")
        sys.exit(0)
