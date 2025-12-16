import sys
import os
import re
import json
import shutil
import glob
from datetime import datetime
from typing import List, Dict, Optional, Any

# Proje Modülleri
import config
from config import Colors, MODEL_CONFIGS
from core.base import ModelAPIError
from core.gemini import GeminiModel 

# --- IMPORT: GROQ (Yeni) ---
try:
    from core.groq import GroqModel
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# --- IMPORT: HUGGING FACE (Opsiyonel) ---
try:
    from core.huggingface import HuggingFaceModel
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

# --- SABİTLER (Config'den alınır) ---
FILE_PATH_PATTERN = re.compile(r'\b[\w./-]+\.(py|js|html|css|md|json|txt|java|cpp|h|ts|jsx|tsx|sh|env)\b', re.IGNORECASE)
DRY_RUN = False
VERBOSE = False

# --- MODEL SEÇİCİ ---
def get_model_choice():
    """Kullanıcıya model seçtirir."""
    print(f"\n{Colors.BLUE}╔═══════════════════════════════╗")
    print(f"║   🤖 AI MODEL SEÇİMİ          ║")
    print(f"╚═══════════════════════════════╝{Colors.RESET}\n")
    
    print(f"  [1] {MODEL_CONFIGS['gemini']['display_name']}")
    
    if GROQ_AVAILABLE:
        print(f"  [2] {MODEL_CONFIGS['groq']['display_name']}")
    else:
        print(f"  [2] Groq (API Key Eksik - ÜCRETSİZ!)")
    
    if HF_AVAILABLE:
        print(f"  [3] {MODEL_CONFIGS['huggingface']['display_name']}")
    
    while True:
        choice = input(f"\n{Colors.YELLOW}Seçiminiz (1/2/3): {Colors.RESET}").strip()
        
        if choice == "1":
            try:
                return GeminiModel()
            except Exception as e:
                print(f"{Colors.RED}Gemini Başlatılamadı: {e}{Colors.RESET}")
        
        elif choice == "2" and GROQ_AVAILABLE:
            try:
                return GroqModel()
            except Exception as e:
                print(f"{Colors.RED}Groq Başlatılamadı: {e}{Colors.RESET}")
        
        elif choice == "3" and HF_AVAILABLE:
            try:
                return HuggingFaceModel()
            except Exception as e:
                print(f"{Colors.RED}Hugging Face Başlatılamadı: {e}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Geçersiz seçim veya model hazır değil.{Colors.RESET}")

# --- YARDIMCI FONKSİYONLAR ---

def is_safe_path(file_path: str, current_directory: str) -> bool:
    """Path Traversal saldırılarını önler."""
    if os.path.isabs(file_path): return False
    normalized_path = os.path.normpath(file_path)
    if normalized_path.startswith('..'): return False
    full_path = os.path.join(current_directory, file_path)
    real_path = os.path.realpath(full_path) 
    if not real_path.startswith(current_directory): return False
    return True

def backup_file(full_path: str) -> Optional[str]:
    """Dosya değişmeden önce yedeğini alır."""
    if not os.path.exists(full_path):
        return None
        
    os.makedirs(config.BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{os.path.basename(full_path)}.{timestamp}.backup"
    backup_path = os.path.join(config.BACKUP_DIR, backup_name)
    
    try:
        shutil.copy(full_path, backup_path)
        
        # Eski yedekleri temizle
        pattern = os.path.join(config.BACKUP_DIR, f"{os.path.basename(full_path)}.*.backup")
        backups = sorted(glob.glob(pattern))
        if len(backups) > config.MAX_BACKUPS_PER_FILE:
            for old in backups[:-config.MAX_BACKUPS_PER_FILE]:
                os.remove(old)
    except Exception as e:
        print(f"{Colors.RED}Yedekleme Hatası: {e}{Colors.RESET}")
        return None
        
    return backup_path

def clean_json_string(json_str: str) -> str:
    """AI yanıtını temiz JSON formatına sokar."""
    # Markdown bloklarını temizle
    if "```" in json_str:
        # Kod bloklarını kaldırırken (```json ... ```) veya sadece (```)
        json_str = re.sub(r"```json\n?|```", "", json_str)
    
    # Görünmez karakterleri temizle
    json_str = json_str.replace('\u00ad', '').replace('\u200b', '')
    return json_str.strip()

def read_context_files(file_paths: List[str], current_dir: str) -> str:
    """
    Belirtilen dosyaları okur ve AI için bağlam oluşturur.
    """
    context_parts = []
    total_size = 0
    
    for fname in file_paths:
        full_path = os.path.join(current_dir, fname)
        
        if not os.path.exists(full_path):
            continue
            
        try:
            # Dosya boyutunu kontrol et
            fsize = os.path.getsize(full_path)
            if fsize > config.MAX_FILE_SIZE:
                print(f"{Colors.YELLOW}⚠️ Dosya çok büyük, atlandı: {fname}{Colors.RESET}")
                continue
                
            total_size += fsize
            if total_size > config.MAX_TOTAL_SIZE:
                print(f"{Colors.YELLOW}⚠️ Toplam okuma limiti aşıldı, kalan dosyalar atlandı.{Colors.RESET}")
                break

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                context_parts.append(f"----- {fname} -----\n{content}\n")
                
        except Exception as e:
            if VERBOSE: print(f"Dosya okuma hatası ({fname}): {e}")

    return "".join(context_parts)

# --- ANA İŞLEM FONKSİYONU ---

def main_process(prompt_text: str, model_instance: Any):
    current_directory = os.getcwd()
    
    # 1. Prompt içindeki dosya isimlerini bul
    potential_files = FILE_PATH_PATTERN.findall(prompt_text)
    
    # 2. Dosyaları verimli şekilde oku
    files_context = read_context_files(potential_files, current_directory)

    # 3. Son Promptu Hazırla
    if files_context:
        full_prompt = f"MEVCUT DOSYALAR:\n{files_context}\n\nKULLANICI İSTEĞİ:\n{prompt_text}"
    else:
        full_prompt = prompt_text
        
    print(f"{Colors.BLUE}✅ GÖREV:{Colors.RESET} {prompt_text[:80]}...")
    print(f"{Colors.CYAN}⏳ {model_instance.MODEL_NAME} çalışıyor...{Colors.RESET}")

    try:
        # 4. AI'dan Yanıt Al
        raw_response = model_instance.generate_content(
            system_instruction=config.SYSTEM_INSTRUCTION,
            prompt_text=full_prompt
        )
        
        # 5. JSON Parse Et
        clean_response = clean_json_string(raw_response)
        
        try:
            file_changes = json.loads(clean_response)
        except json.JSONDecodeError:
            # Bazen AI tek tırnak kullanıyor, düzeltmeyi dene
            try:
                # Tek tırnakları çift tırnağa çevirme denemesi
                file_changes = json.loads(clean_response.replace("'", '"'))
            except:
                print(f"{Colors.RED}❌ JSON Ayrıştırma Hatası. AI Yanıtı:\n{raw_response}{Colors.RESET}")
                return

        if not isinstance(file_changes, dict):
            print(f"{Colors.RED}❌ Beklenmeyen yanıt formatı.{Colors.RESET}")
            return

        # 6. Değişiklikleri Uygula
        print("\n📋 PLANLANAN DEĞİŞİKLİKLER:")
        for path, content in file_changes.items():
            print(f"   📂 {path} ({len(content)} karakter)")
            
        if DRY_RUN:
            print(f"\n{Colors.YELLOW}🧪 Dry-Run Modu: Kayıt yapılmadı.{Colors.RESET}")
            return

        confirm = input(f"\n{Colors.GREEN}Onaylıyor musunuz? (e/h): {Colors.RESET}").lower()
        if confirm != 'e':
            print("❌ İşlem iptal edildi.")
            return

        for rel_path, content in file_changes.items():
            if not is_safe_path(rel_path, current_directory):
                print(f"{Colors.RED}🚨 Güvenlik Uyarısı: {rel_path} engellendi.{Colors.RESET}")
                continue

            full_path = os.path.join(current_directory, rel_path)
            
            # Klasör oluştur
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Yedekle
            if os.path.exists(full_path):
                backup = backup_file(full_path)
                if backup: print(f"   📦 Yedek: {os.path.basename(backup)}")

            # Yaz
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"{Colors.GREEN}   ✅ Yazıldı: {rel_path}{Colors.RESET}")

    except ModelAPIError as e:
        print(f"\n{Colors.RED}💣 API Hatası: {e}{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}💣 Beklenmeyen Hata: {e}{Colors.RESET}")
        if VERBOSE: raise e

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Kullanım: python assistant.py \"Göreviniz...\" [--dry-run] [--verbose]")
        sys.exit(1)
        
    # Argümanları ayıkla
    args = sys.argv[1:]
    if "--dry-run" in args:
        DRY_RUN = True
        args.remove("--dry-run")
    if "--verbose" in args:
        VERBOSE = True
        args.remove("--verbose")
        
    user_prompt = " ".join(args)
    
    # Modeli seç ve başlat
    model = get_model_choice()
    
    if model:
        main_process(user_prompt, model)