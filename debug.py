import os
import sys
from pathlib import Path
from core.memory import MemoryManager
import config
from config import Colors

def inspect_project():
    workspace = Path.cwd() / config.PROJECTS_DIR
    projects = [d for d in workspace.iterdir() if d.is_dir() and (d / ".coder_memory").exists()]
    
    if not projects:
        print(f"{Colors.RED}İncelenecek aktif hafızalı proje bulunamadı.{Colors.RESET}")
        return

    print(f"\n{Colors.CYAN}🕵️ HAFIZA MÜFETTİŞİ: Proje Seçin{Colors.RESET}")
    for idx, p in enumerate(projects, 1):
        print(f"[{idx}] {p.name}")
    
    choice = input("\nSeçim: ")
    if not choice.isdigit() or int(choice) > len(projects): return
    
    target_proj = projects[int(choice)-1]
    memory = MemoryManager(str(target_proj))
    
    while True:
        print(f"\n{Colors.YELLOW}--- {target_proj.name} Hafıza Menüsü ---{Colors.RESET}")
        print("[1] Anlamsal Sorgu Testi (RAG Test)")
        print("[2] Tüm Kayıtlı Dosyaları Listele")
        print("[3] Belirli Bir Dosyanın Hafızasını Sil")
        print("[Q] Çıkış")
        
        sub_choice = input("\nSeçim: ").lower()
        
        if sub_choice == '1':
            q = input("🔍 AI gibi bir soru sorun: ")
            res = memory.query(q)
            print(f"\n{Colors.GREEN}🔎 BULUNAN BAĞLAM:{Colors.RESET}\n{res}")
            
        elif sub_choice == '2':
            res = memory.collection.get()
            print(f"\n{Colors.CYAN}📑 İNDEKSLENMİŞ DOSYALAR:{Colors.RESET}")
            for mid in res['ids']: print(f"  - {mid}")
            
        elif sub_choice == '3':
            fname = input("Silinecek dosya yolu (örn: main.py): ")
            try:
                memory.collection.delete(ids=[fname])
                print(f"{Colors.RED}🗑️ {fname} hafızadan silindi.{Colors.RESET}")
            except: print("Hata: Dosya bulunamadı.")
            
        elif sub_choice == 'q': break

if __name__ == "__main__":
    inspect_project()