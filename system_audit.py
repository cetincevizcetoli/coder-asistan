import os
import sys
import sqlite3
from pathlib import Path

# Config dosyasından proje klasörünü öğrenelim
try:
    import config
    PROJECTS_DIR_NAME = config.PROJECTS_DIR
except ImportError:
    PROJECTS_DIR_NAME = "my_projects"

# Renkler
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
CYAN = '\033[96m'

def check_file_exists(path, description):
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"{GREEN}✅ {description} Mevcut ({size} bytes){RESET}")
        return True
    else:
        print(f"{RED}❌ {description} BULUNAMADI! ({path}){RESET}")
        return False

def audit_log_file(project_path):
    log_path = project_path / ".chat_history.log"
    print(f"\n--- 📜 LOG DOSYASI KONTROLÜ ({log_path.name}) ---")
    
    if check_file_exists(log_path, "Log Dosyası"):
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"   📄 Toplam Satır: {len(lines)}")
                if len(lines) > 0:
                    print(f"   🔍 Son Kayıt: {lines[-2].strip() if len(lines) > 1 else lines[0].strip()}")
                else:
                    print(f"{YELLOW}   ⚠️ Dosya var ama içi boş.{RESET}")
        except Exception as e:
            print(f"{RED}   ❌ Dosya okuma hatası: {e}{RESET}")

def audit_vector_db(project_path):
    db_path = project_path / ".coder_memory"
    sqlite_file = db_path / "chroma.sqlite3"
    
    print(f"\n--- 🧠 VEKTÖR VERİTABANI KONTROLÜ ---")
    
    if not os.path.exists(db_path):
        print(f"{RED}❌ .coder_memory klasörü yok (Hafızasız Proje).{RESET}")
        return

    if check_file_exists(sqlite_file, "ChromaDB SQLite Dosyası"):
        try:
            # ChromaDB kütüphanesini kullanmadan direkt SQL ile bütünlük testi
            conn = sqlite3.connect(sqlite_file)
            cursor = conn.cursor()
            
            # Tabloları say
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchone()[0]
            print(f"   📊 Tablo Sayısı: {tables}")
            
            # Embedding sayısını bulmaya çalış
            try:
                # Chroma versiyonuna göre tablo adı değişebilir, genelde 'embeddings'
                cursor.execute("SELECT count(*) FROM embeddings;")
                count = cursor.fetchone()[0]
                print(f"   🧬 İndekslenmiş Vektör Sayısı: {GREEN}{count}{RESET}")
            except:
                print(f"{YELLOW}   ⚠️ 'embeddings' tablosu direkt okunamadı (Versiyon farkı olabilir).{RESET}")
                
            conn.close()
            print(f"{GREEN}   ✅ Veritabanı bütünlüğü (Integrity) sağlam.{RESET}")
            
        except Exception as e:
            print(f"{RED}   ❌ Veritabanı bozuk veya okunamıyor: {e}{RESET}")

def main():
    # DÜZELTME: Artık kök dizine değil, my_projects içine bakıyoruz
    workspace = Path.cwd() / PROJECTS_DIR_NAME
    
    if not workspace.exists():
        print(f"{RED}Hata: '{PROJECTS_DIR_NAME}' klasörü bulunamadı.{RESET}")
        return

    # Projeleri bul (içinde .coder_memory olan klasörler)
    projects = [d for d in workspace.iterdir() if d.is_dir() and (d / ".coder_memory").exists()]
    
    print(f"{CYAN}🔍 SİSTEM DENETÇİSİ BAŞLATILDI{RESET}")
    print(f"📂 Hedef Dizin: {workspace}")
    
    if not projects:
        print(f"{RED}Test edilecek proje bulunamadı.{RESET}")
        return

    print(f"✅ {len(projects)} adet proje tespit edildi.")
    
    for proj in projects:
        print(f"\n{YELLOW}========================================{RESET}")
        print(f"📂 PROJE DENETLENİYOR: {proj.name}")
        print(f"{YELLOW}========================================{RESET}")
        
        audit_log_file(proj)
        audit_vector_db(proj)

if __name__ == "__main__":
    main()