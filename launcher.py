import os
import sys
import platform
import subprocess
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

# Renk kodları
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RED = '\033[91m'
GREY = '\033[90m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

# Config'den proje klasörünü al
try:
    import config
    PROJECTS_ROOT = Path.cwd() / config.PROJECTS_DIR
except ImportError:
    # Config yoksa varsayılan
    PROJECTS_ROOT = Path.cwd() / "my_projects"

try:
    from core.memory import MemoryManager
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from core.memory import MemoryManager

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def ensure_workspace():
    """Çalışma alanı klasörünü oluşturur."""
    if not PROJECTS_ROOT.exists():
        os.makedirs(PROJECTS_ROOT)

def slugify(text):
    text = text.lower()
    text = text.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    text = re.sub(r'[^a-z0-9]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def get_projects():
    projects = []
    ensure_workspace()
    for entry in PROJECTS_ROOT.iterdir():
        if entry.is_dir() and (entry / ".coder_memory").exists():
            projects.append(entry)
    return projects

def get_project_stats(project_path: Path):
    stats_file = project_path / ".project_stats.json"
    total_cost = 0.0
    last_updated = "-"
    if stats_file.exists():
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_cost = data.get("total_cost", 0.0)
                last_updated = data.get("last_updated", "-")
        except: pass
    return total_cost, last_updated

def export_project(project_path: Path):
    """Projeyi taşınabilir ZIP formatına getirir."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    zip_name = f"{project_path.name}_BACKUP_{timestamp}"
    zip_path = PROJECTS_ROOT / zip_name
    
    print(f"\n{CYAN}📦 Proje paketleniyor: {project_path.name}...{RESET}")
    try:
        shutil.make_archive(str(zip_path), 'zip', project_path)
        print(f"{GREEN}✅ Yedek Oluşturuldu: {zip_path}.zip{RESET}")
        print(f"{GREY}   (Bu dosyayı USB'ye atıp başka bilgisayara taşıyabilirsiniz){RESET}")
        input(f"\nDevam etmek için Enter...")
    except Exception as e:
        print(f"{RED}Paketleme hatası: {e}{RESET}")
        input()

def create_new_project_wizard():
    print(f"\n{CYAN}✨ YENİ PROJE OLUŞTUR{RESET}")
    while True:
        p_name = input(f"{YELLOW}1. Proje Adı: {RESET}").strip()
        if p_name: break
    
    print(f"{CYAN}2. Açıklama{RESET}")
    p_desc = input(f"{YELLOW}   Detay: {RESET}").strip()
    if not p_desc: p_desc = f"{p_name} projesi."

    suggested_folder = slugify(p_name)
    p_folder = input(f"{YELLOW}3. Klasör Adı [{suggested_folder}]: {RESET}").strip()
    if not p_folder: p_folder = suggested_folder
        
    # ARTIK ANA DİZİNE DEĞİL, MY_PROJECTS ALTINA KURUYORUZ
    target_path = PROJECTS_ROOT / p_folder
    
    if target_path.exists():
        print(f"\n{RED}❌ Hata: Bu isimde bir proje zaten var!{RESET}")
        return None

    try:
        os.makedirs(target_path)
        print(f"{CYAN}🧠 Hafıza kuruluyor...{RESET}")
        memory = MemoryManager(project_root=str(target_path))
        
        readme_content = f"# {p_name}\n\n## Proje Hakkında\n{p_desc}\n\nBu proje Coder-Asistan ile oluşturuldu."
        with open(target_path / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
            
        memory.collection.upsert(
            documents=[f"PROJE TANIMI: {p_desc}"],
            embeddings=memory.embedder.encode([p_desc]).tolist(),
            metadatas=[{"source": "project_init"}],
            ids=["project_description"]
        )
        print(f"{GREEN}✅ Proje Hazır!{RESET}")
        return target_path
    except Exception as e:
        print(f"{RED}Hata: {e}{RESET}")
        return None

def print_chat_history(project_path: Path):
    log_file = project_path / ".chat_history.log"
    if log_file.exists():
        print(f"\n{GREY}📜 GEÇMİŞ KAYITLAR{RESET}")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                content = content.replace("👤 USER:", f"{YELLOW}👤 USER:{RESET}")
                content = content.replace("🤖 AI:", f"{GREEN}🤖 AI:{RESET}")
                content = content.replace("💰 MALİYET:", f"{MAGENTA}💰 MALİYET:{RESET}")
                print(content)
        except: pass
    else:
        print(f"\n{GREY}(Henüz geçmiş yok){RESET}")

def launch_assistant(project_path):
    clear_screen()
    total_cost, last_upd = get_project_stats(project_path)
    
    print(f"{GREEN}📂 PROJE: {project_path.name}{RESET}")
    print(f"{MAGENTA}💰 TOPLAM: ${total_cost:.5f}{RESET} {GREY}(Son: {last_upd}){RESET}")
    
    readme = project_path / "README.md"
    if readme.exists():
         with open(readme, 'r', encoding='utf-8') as f:
             print(f"{CYAN}ℹ️  {f.readline().strip().replace('# ', '')}{RESET}")

    print_chat_history(project_path)
    print(f"{CYAN}----------------------------------------{RESET}")
    print(f"{GREY}(Sohbet geçmişi yukarıda kalacaktır. Çıkış için 'b' yazın){RESET}\n")

    while True:
        task = input(f"{YELLOW}User (Siz) > {RESET}").strip()
        if task.lower() == 'b': return
        if not task: continue
            
        # Assistant scripti bir üst dizinde (ana kök dizinde)
        assistant_script = Path(__file__).parent / "assistant.py"
        cmd = [sys.executable, str(assistant_script), task]
        
        print(f"{CYAN}----------------------------------------{RESET}")
        try:
            subprocess.run(cmd, cwd=str(project_path))
            print(f"{CYAN}----------------------------------------{RESET}")
        except Exception as e:
            print(f"{RED}Hata: {e}{RESET}")

def main():
    ensure_workspace()
    
    while True:
        clear_screen()
        projects = get_projects()
        
        if not projects:
            create_new_project_wizard()
            continue

        print(f"{GREEN}╔══════════════════════════════════════════╗")
        print(f"║   🚀 CODER-ASISTAN (Projeler: {len(projects)})      ║")
        print(f"╚══════════════════════════════════════════╝{RESET}")
        
        for idx, proj in enumerate(projects, 1):
            cost, _ = get_project_stats(proj)
            print(f"[{idx}] {proj.name:<20} {MAGENTA}${cost:.4f}{RESET}")
            
        print(f"\n[{GREEN}N{RESET}] ✨ Yeni Proje")
        print(f"[{CYAN}E{RESET}] 📦 Projeyi Paketle (Zip/Yedek)")
        print(f"[{RED}Q{RESET}] 🚪 Çıkış")
        
        choice = input(f"\n{YELLOW}Seçim: {RESET}").strip().upper()
        
        if choice == 'Q': sys.exit()
        elif choice == 'N':
            new_proj = create_new_project_wizard()
            if new_proj: launch_assistant(new_proj)
        elif choice == 'E':
            try:
                p_idx = int(input("Paketlenecek proje numarası: "))
                if 1 <= p_idx <= len(projects):
                    export_project(projects[p_idx-1])
            except ValueError: pass
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(projects):
                launch_assistant(projects[idx-1])

if __name__ == "__main__":
    main()