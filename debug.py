import os
import sys
import chromadb
from pathlib import Path

# Config'den proje klasör ismini çekelim
try:
    import config
    PROJECTS_DIR_NAME = config.PROJECTS_DIR
except ImportError:
    PROJECTS_DIR_NAME = "my_projects"

# Renkler
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def list_projects():
    # DÜZELTME: Artık ana dizine değil, my_projects klasörüne bakıyoruz
    workspace = Path.cwd() / PROJECTS_DIR_NAME
    
    if not workspace.exists():
        print(f"{RED}Hata: {PROJECTS_DIR_NAME} klasörü bulunamadı.{RESET}")
        return []

    projects = []
    for entry in workspace.iterdir():
        # .coder_memory klasörü olanları proje say
        if entry.is_dir() and (entry / ".coder_memory").exists():
            projects.append(entry)
    return projects

def inspect_memory(project_path):
    memory_path = project_path / ".coder_memory"
    
    print(f"\n{CYAN}🧠 Veritabanı Bağlanıyor: {memory_path}{RESET}")
    
    try:
        # ChromaDB istemcisi
        client = chromadb.PersistentClient(path=str(memory_path))
        
        # Koleksiyonu bulmaya çalış
        try:
            # Config'deki ismi kullanıyoruz
            collection = client.get_collection("project_codebase")
        except:
            print(f"{RED}⚠️ Koleksiyon bulunamadı. Veritabanı bozuk olabilir.{RESET}")
            return
        
        count = collection.count()
        print(f"{GREEN}📊 Toplam Kayıtlı Parça (Chunk): {count}{RESET}")
        
        if count == 0:
            print(f"{RED}⚠️ Hafıza boş! Henüz hiçbir dosya indekslenmemiş.{RESET}")
            return

        print(f"\n{YELLOW}--- SON KAYDEDİLEN 5 VERİ (Örnek) ---{RESET}")
        
        # İlk 5 veriyi çek
        data = collection.peek(limit=5)
        
        if not data['ids']:
            print("Veri çekilemedi.")
            return

        ids = data['ids']
        metadatas = data['metadatas']
        documents = data['documents']
        
        for i in range(len(ids)):
            doc_id = ids[i]
            meta = metadatas[i] if metadatas else "{}"
            content = documents[i] if documents else ""
            
            # İçerik çok uzunsa kısaltarak göster
            preview = content[:150].replace('\n', ' ') + "..."
            
            print(f"[{i+1}] ID: {doc_id}")
            print(f"    Kaynak: {meta}")
            print(f"    İçerik: {preview}\n")
            
    except Exception as e:
        print(f"{RED}Hata: {e}{RESET}")
        print("Veritabanı okunamadı. C++ Build Tools eksik olabilir veya DB kilitli.")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"🕵️  RAG HAFIZA MÜFETTİŞİ (Hedef: {PROJECTS_DIR_NAME}/)")
    print("------------------------------------------------")
    
    projects = list_projects()
    
    if not projects:
        print(f"{YELLOW}Hiç proje bulunamadı.{RESET}")
        print(f"Not: Projelerinizin '{PROJECTS_DIR_NAME}' klasöründe olduğundan emin olun.")
        sys.exit()
        
    for idx, p in enumerate(projects, 1):
        print(f"[{idx}] {p.name}")
        
    print("\n[Q] Çıkış")
    choice = input("\nHangi projeyi inceleyelim? (No): ").strip()
    
    if choice.lower() == 'q':
        sys.exit()
        
    if choice.isdigit() and 1 <= int(choice) <= len(projects):
        inspect_memory(projects[int(choice)-1])
    else:
        print("Geçersiz seçim.")