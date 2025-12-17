import os
import sys
import json
import time
import datetime
import importlib

try:
    import config
except ImportError:
    print("HATA: config.py bulunamadı!")
    sys.exit(1)

# ==========================================
# AYAR SEÇENEKLERİ
# ==========================================
MEMORY_OPTIONS = {
    "1": {"id": "all-MiniLM-L6-v2", "name": "Hafif (Light)", "desc": "🚀 Hızlı"},
    "2": {"id": "paraphrase-multilingual-MiniLM-L12-v2", "name": "Dengeli (Medium)", "desc": "⚖️ Türkçe"},
    "3": {"id": "all-mpnet-base-v2", "name": "Güçlü (Heavy)", "desc": "🧠 Detaylı"}
}

MODEL_OPTIONS = {
    "1": {"id": "gemini", "name": "Google Gemini", "desc": "⚡ Dengeli ve Ücretsiz"},
    "2": {"id": "groq", "name": "Groq (Llama 3)", "desc": "🚀 Işık Hızında"},
    "3": {"id": "deepseek", "name": "DeepSeek Chat", "desc": "👨‍💻 Kodlama Uzmanı"},
    "4": {"id": "huggingface", "name": "Hugging Face", "desc": "🤗 Açık Kaynak Modeller"}
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def update_config_file(variable_name, new_value):
    try:
        with open("config.py", "r", encoding="utf-8") as f: lines = f.readlines()
        with open("config.py", "w", encoding="utf-8") as f:
            found = False
            for line in lines:
                if line.strip().startswith(variable_name):
                    f.write(f'{variable_name} = "{new_value}"\n'); found = True
                else: f.write(line)
            if not found: f.write(f'\n{variable_name} = "{new_value}"\n')
        return True
    except: return False

def load_projects():
    projects = []
    if not os.path.exists(config.PROJECTS_DIR):
        try: os.makedirs(config.PROJECTS_DIR)
        except: pass
    try: items = os.listdir(config.PROJECTS_DIR)
    except: items = []
    for item in items:
        path = os.path.join(config.PROJECTS_DIR, item)
        if os.path.isdir(path):
            meta_path = os.path.join(path, "metadata.json")
            embedding_model = "BİLİNMİYOR"
            cost = 0.0
            last_date = "0"
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r') as f:
                        data = json.load(f)
                        embedding_model = data.get("embedding_model", "Eski")
                        cost = data.get("total_cost", 0.0)
                        last_date = data.get("last_interaction", "0")
                except: pass
            projects.append({"name": item, "embedding_model": embedding_model, "cost": cost, "last_date": last_date})
    return sorted(projects, key=lambda x: x['last_date'], reverse=True)

def create_new_project():
    print(f"\n{config.Colors.CYAN}✨ Yeni Proje{config.Colors.RESET}")
    name = input("Proje İsmi: ").strip()
    if not name: return
    path = os.path.join(config.PROJECTS_DIR, name)
    if os.path.exists(path): print("Zaten var!"); time.sleep(1); return
    try:
        os.makedirs(path)
        metadata = {
            "created_at": str(datetime.datetime.now()),
            "embedding_model": config.EMBEDDING_MODEL,
            "total_cost": 0.0,
            "last_interaction": str(datetime.datetime.now())
        }
        with open(os.path.join(path, "metadata.json"), 'w') as f: json.dump(metadata, f, indent=4)
        start_project(name, config.EMBEDDING_MODEL)
    except Exception as e: print(f"Hata: {e}"); input("Enter...")

def start_project(name, project_embed_model):
    if project_embed_model != config.EMBEDDING_MODEL:
        print(f"\n{config.Colors.RED}⛔ UYUMSUZLUK: Proje '{project_embed_model}' hafızasıyla oluşturulmuş.{config.Colors.RESET}")
        print(f"Sizin ayarınız: '{config.EMBEDDING_MODEL}'. Lütfen ayarlardan değiştirin."); input("Enter..."); return

    print(f"\n{config.Colors.GREEN}🚀 Başlatılıyor ({config.ACTIVE_MODEL.upper()})...{config.Colors.RESET}")
    try:
        import assistant
        importlib.reload(assistant)
        assistant.main(name) 
    except Exception as e:
        print(f"\nERROR: {e}"); input("Enter...")

def settings_menu():
    while True:
        clear_screen()
        print(f"{config.Colors.YELLOW}=== AYARLAR ==={config.Colors.RESET}")
        print(f"1. Yapay Zeka Modeli : {config.Colors.GREEN}{config.ACTIVE_MODEL.upper()}{config.Colors.RESET}")
        print(f"2. Hafıza (RAG) Tipi : {config.Colors.CYAN}{config.EMBEDDING_MODEL}{config.Colors.RESET}")
        print("-" * 50)
        print("[M] Model Değiştir")
        print("[H] Hafıza Değiştir")
        print("[X] Geri Dön")
        
        sel = input("\nSeçim: ").strip().upper()
        
        if sel == 'X': break
        
        elif sel == 'M':
            print(f"\n{config.Colors.BLUE}--- MODEL SEÇİMİ ---{config.Colors.RESET}")
            for k, v in MODEL_OPTIONS.items():
                mark = " (AKTİF)" if v['id'] == config.ACTIVE_MODEL else ""
                print(f"[{k}] {v['name']}{mark} - {v['desc']}")
            m_sel = input("Seçim: ").strip()
            if m_sel in MODEL_OPTIONS:
                new_val = MODEL_OPTIONS[m_sel]['id']
                update_config_file("ACTIVE_MODEL", new_val)
                print("♻️  Kaydedildi, yeniden başlatılıyor..."); time.sleep(1)
                os.execv(sys.executable, ['python'] + sys.argv)

        elif sel == 'H':
            print(f"\n{config.Colors.BLUE}--- HAFIZA SEÇİMİ ---{config.Colors.RESET}")
            for k, v in MEMORY_OPTIONS.items():
                mark = " (AKTİF)" if v['id'] == config.EMBEDDING_MODEL else ""
                print(f"[{k}] {v['name']}{mark} - {v['desc']}")
            h_sel = input("Seçim: ").strip()
            if h_sel in MEMORY_OPTIONS:
                new_val = MEMORY_OPTIONS[h_sel]['id']
                update_config_file("EMBEDDING_MODEL", new_val)
                print("♻️  Kaydedildi, yeniden başlatılıyor..."); time.sleep(1)
                os.execv(sys.executable, ['python'] + sys.argv)

def main():
    while True:
        clear_screen()
        importlib.reload(config)
        projects = load_projects()
        
        print(f"{config.Colors.BOLD}{config.Colors.BLUE}=== AI ASİSTAN (v2.4) ==={config.Colors.RESET}")
        print(f"🤖 Model : {config.Colors.GREEN}{config.ACTIVE_MODEL.upper()}{config.Colors.RESET}")
        print(f"🧠 Hafıza: {config.Colors.YELLOW}{config.EMBEDDING_MODEL}{config.Colors.RESET}")
        print("-" * 60)
        
        for idx, p in enumerate(projects, 1):
            status = "✅" if p['embedding_model'] == config.EMBEDDING_MODEL else "⛔"
            print(f"[{idx}] {p['name']:<15} {status} ({p['embedding_model']})")
            
        print("-" * 60)
        print("[N] Yeni Proje  |  [S] Ayarlar  |  [Q] Çıkış")
        ch = input("> ").strip().upper()
        
        if ch == 'Q': sys.exit()
        elif ch == 'N': create_new_project()
        elif ch == 'S': settings_menu()
        elif ch.isdigit():
            idx = int(ch) - 1
            if 0 <= idx < len(projects): start_project(projects[idx]['name'], projects[idx]['embedding_model'])

if __name__ == "__main__":
    main()