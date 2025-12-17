import os
import sys
import chromadb
from pathlib import Path

# Renkler
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def list_projects():
    workspace = Path.cwd()
    projects = []
    for entry in workspace.iterdir():
        if entry.is_dir() and (entry / ".coder_memory").exists():
            projects.append(entry)
    return projects

def inspect_memory(project_path):
    memory_path = project_path / ".coder_memory"
    
    print(f"\n{CYAN}🧠 Veritabanı Bağlanıyor: {memory_path}{RESET}")
    
    try:
        client = chromadb.PersistentClient(path=str(memory_path))
        # Koleksiyon adımız config.py'de 'project_codebase' idi
        collection = client.get_collection("project_codebase")
        
        count = collection.count()
        print(f"{GREEN}📊 Toplam Kayıtlı Parça (Chunk): {count}{RESET}")
        
        if count == 0:
            print(f"{RED}⚠️ Hafıza boş! Henüz hiçbir dosya indekslenmemiş.{RESET}")
            return

        print(f"\n{YELLOW}--- SON KAYDEDİLEN 5 VERİ ---{RESET}")
        # İlk 5 veriyi çek (metadata ve id'leri getir)
        data = collection.peek(limit=5)
        
        ids = data['ids']
        metadatas = data['metadatas']
        documents = data['documents']
        
        for i in range(len(ids)):
            doc_id = ids[i]
            meta = metadatas[i]
            content = documents[i]
            
            # İçerik çok uzunsa kısalt
            preview = content[:100].replace('\n', ' ') + "..."
            
            print(f"[{i+1}] ID: {doc_id}")
            print(f"    Kaynak: {meta}")
            print(f"    İçerik: {preview}\n")
            
    except Exception as e:
        print(f"{RED}Hata: {e}{RESET}")
        print("Veritabanı henüz oluşturulmamış veya bozuk olabilir.")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🕵️  RAG HAFIZA MÜFETTİŞİ")
    print("-----------------------")
    
    projects = list_projects()
    
    if not projects:
        print("Hiç proje bulunamadı.")
        sys.exit()
        
    for idx, p in enumerate(projects, 1):
        print(f"[{idx}] {p.name}")
        
    choice = input("\nHangi projeyi inceleyelim? (No): ")
    if choice.isdigit() and 1 <= int(choice) <= len(projects):
        inspect_memory(projects[int(choice)-1])
    else:
        print("Geçersiz seçim.")