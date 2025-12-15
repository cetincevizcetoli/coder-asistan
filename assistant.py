# assistant.py
import sys
import os
import re
import json
import shutil
import glob
from datetime import datetime

# YENİ MODÜLLER
from config import *
from model_selector import select_model_interactive
from core.base import ModelAPIError

FILE_PATH_PATTERN = re.compile(r'\b[\w./-]+\.(py|js|html|css|md|json|txt|java|cpp|h|ts|jsx|tsx|sh|sql)\b', re.IGNORECASE)
VERBOSE = False
DRY_RUN = False

# --- YARDIMCI FONKSİYONLAR ---
def clean_json_string(json_str):
    """
    AI'dan gelen kirli JSON string'ini temizler ve parse edilebilir hale getirir.
    """
    if not json_str: return ""

    # 1. Markdown kod bloklarını temizle (```json ... ```)
    json_str = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'^```\s*', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'```\s*$', '', json_str, flags=re.MULTILINE)

    # 2. Görünmez ve bozuk karakterleri temizle
    json_str = json_str.replace('\u00ad', '') # Soft hyphen
    json_str = json_str.replace('\u200b', '') # Zero width space
    
    # 3. JSON'un başındaki ve sonundaki fazlalıkları at (Örn: "İşte JSON:" gibi yazılar)
    # İlk '{' karakterini bul
    start_idx = json_str.find('{')
    # Son '}' karakterini bul
    end_idx = json_str.rfind('}')

    if start_idx != -1 and end_idx != -1:
        json_str = json_str[start_idx : end_idx + 1]

    return json_str.strip()

def is_safe_path(file_path, current_directory):
    if os.path.isabs(file_path): return False
    if file_path.startswith('..'): return False
    full_path = os.path.realpath(os.path.join(current_directory, file_path))
    return full_path.startswith(current_directory)

def backup_if_exists(full_path):
    if os.path.exists(full_path):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{os.path.basename(full_path)}.{timestamp}.bak"
        shutil.copy(full_path, os.path.join(BACKUP_DIR, backup_name))
        return backup_name
    return None

def main_process(prompt_text, model_instance):
    current_directory = os.getcwd()
    
    # 1. Dosya Okuma (Context)
    files_context = ""
    found_files = FILE_PATH_PATTERN.findall(prompt_text)
    for fname in found_files:
        path = os.path.join(current_directory, fname)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                files_context += f"\n--- DOSYA: {fname} ---\n{f.read()}\n"

    full_prompt = f"MEVCUT PROJE DOSYALARI:\n{files_context}\n\nKULLANICI İSTEĞİ:\n{prompt_text}"
    
    print(f"{Colors.BLUE}⏳ {model_instance.MODEL_NAME} düşünüyor...{Colors.RESET}")
    
    try:
        # AI'dan yanıt al
        raw_response = model_instance.generate_content(SYSTEM_INSTRUCTION, full_prompt)
        
        # JSON Temizle
        clean_response = clean_json_string(raw_response)
        
        if VERBOSE:
            print(f"{Colors.YELLOW}[DEBUG] Ham Yanıt:\n{raw_response}{Colors.RESET}")
            print(f"{Colors.CYAN}[DEBUG] Temiz Yanıt:\n{clean_response}{Colors.RESET}")

        # JSON Parse Et
        try:
            file_changes = json.loads(clean_response)
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}❌ JSON Ayrıştırma Hatası! AI bozuk format döndürdü.{Colors.RESET}")
            print(f"Hata detayı: {e}")
            return

        # Dosyaları Yaz
        print(f"\n{Colors.BOLD}Planlanan Değişiklikler:{Colors.RESET}")
        for path, content in file_changes.items():
            print(f" 📄 {path}")

        if not DRY_RUN:
            confirm = input(f"\n{Colors.YELLOW}Onaylıyor musunuz? (e/h): {Colors.RESET}").lower()
            if confirm == 'e':
                for path, content in file_changes.items():
                    full_path = os.path.join(current_directory, path)
                    
                    if not is_safe_path(path, current_directory):
                        print(f"{Colors.RED}⛔ Güvenlik Uyarısı: {path} atlandı.{Colors.RESET}")
                        continue
                        
                    # Klasör oluştur
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Yedekle
                    backup_if_exists(full_path)
                    
                    # Yaz
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"{Colors.GREEN}✅ Kaydedildi: {path}{Colors.RESET}")
            else:
                print("İptal edildi.")

    except ModelAPIError as e:
        print(f"{Colors.RED}⚡ API Hatası: {e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}🔥 Beklenmeyen Hata: {e}{Colors.RESET}")

if __name__ == "__main__":
    if "--verbose" in sys.argv:
        VERBOSE = True
        sys.argv.remove("--verbose")
    
    if len(sys.argv) < 2:
        print(f"Kullanım: python assistant.py \"görev tanımı\"")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    
    # Yeni Seçici
    model = select_model_interactive()
    
    if model:
        main_process(prompt, model)