# 📝 Proje Dökümü: coder-asistan

Bu döküm, **D:\projects\coder-asistan** dizini (mevcut klasör) ve altındakileri kapsar.

### 📂 Proje Dizin Yapısı ve Dosyalar

- **coder-asistan/** (Proje Kökü)
  - assistant.py
  - check_models.py
  - claude_oneri.txt
  - config.py
  - index.html
  - model_selector.py
  - proje_dokumu_orjınal.md
  - readme.md
  - requirements.txt
  - **core/**
    - base.py
    - gemini.py
    - groq.py
    - huggingface.py

---
### 💻 Kod İçeriği Dökümü


#### 📄 Dosya: `assistant.py`

```py
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
```

#### 📄 Dosya: `check_models.py`

```py
import os
import sys

# google-genai yüklü mü kontrol et
try:
    from google import genai
except ImportError:
    print("❌ HATA: 'google-genai' kütüphanesi bulunamadı.")
    print("👉 Çözüm: Önce 'pip install google-genai' komutunu çalıştırın.")
    sys.exit(1)

# API Anahtarını al
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ HATA: GOOGLE_API_KEY tanımlı değil!")
    print("👉 Terminale şunu yazın: export GOOGLE_API_KEY='anahtariniz'")
    sys.exit(1)

print(f"🔑 Anahtar ile bağlanılıyor: {api_key[:5]}...")

try:
    client = genai.Client(api_key=api_key)
    print("\n📡 --- GOOGLE TARAFINDAN ONAYLANAN MODELLER ---")
    
    count = 0
    # Modelleri çek ve listele
    for m in client.models.list():
        if "generateContent" in m.supported_actions:
            # model isminin başındaki 'models/' kısmını atarak temiz göster
            clean_name = m.name.replace('models/', '')
            print(f"✅ {clean_name}")
            count += 1
            
    if count == 0:
        print("\n⚠️ HATA: Erişim izniniz olan hiçbir model bulunamadı.")
        print("Hesabınızın faturalandırma (Billing) ayarlarını kontrol etmeniz gerekebilir.")

except Exception as e:
    print(f"\n❌ KRİTİK HATA: {e}")

```

#### 📄 Dosya: `config.py`

```py
import os

# ==========================================
# 🎨 RENK AYARLARI (Terminal Çıktısı İçin)
# ==========================================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# ==========================================
# ⚙️ SİSTEM VE DOSYA AYARLARI
# ==========================================
# Dosya okuma/yazma limitleri (Sihirli sayılar burada toplandı)
MAX_FILE_SIZE = 5 * 1024 * 1024        # 5 MB (Tek dosya limiti)
MAX_TOTAL_SIZE = 20 * 1024 * 1024      # 20 MB (Toplam proje okuma limiti)
BACKUP_DIR = ".gassist_backups"        # Yedekleme klasörü
HISTORY_LOG = ".gassist_history.log"   # Log dosyası
MAX_BACKUPS_PER_FILE = 10              # Bir dosya için tutulacak max yedek



# ==========================================
# 🤖 MODEL AYARLARI (Deklarasyon)
# ==========================================
# Not: API Anahtarları (Secret) burada değil, os.getenv ile çekilecek.
MODEL_CONFIGS = {
    "gemini": {
        "env_var": "GOOGLE_API_KEY",
        "model_name": "gemini-2.5-flash",
        "display_name": "Google Gemini 2.5 Flash",
    },
    "groq": {
    "env_var": "GROQ_API_KEY",
    "model_id": "llama-3.3-70b-versatile",  # ÜCRETSİZ KATMANDA BULUNUR
    "display_name": "Groq Llama 3.3 70B (ÜCRETSİZ)",
},
    "huggingface": {
        "env_var": "HUGGINGFACE_API_KEY",
        "model_id": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "display_name": "Hugging Face Qwen",
    }
}

# (Dosyanın geri kalanı aynı kalacak)

# ==========================================
# 🧠 AI SİSTEM TALİMATI (System Prompt)
# ==========================================
SYSTEM_INSTRUCTION = (
    "Sen uzman bir yazılım mimarı ve kodlama asistanısın. "
    "Görevin: Verilen talimatlara göre dosya yapısını oluşturmak veya güncellemektir.\n"
    "KURALLAR:\n"
    "1. Yanıtın SADECE ve SADECE geçerli bir JSON objesi olmalıdır.\n"
    "2. JSON formatı: {'dosya_yolu': 'dosya_icerigi'}\n"
    "3. Asla Markdown (```json ... ```) kullanma, sadece saf JSON döndür.\n"
    "4. Sohbet etme, açıklama yapma, sadece JSON ver.\n"
    "5. Türkçe karakterleri UTF-8 olarak koru."
)

```

#### 📄 Dosya: `index.html`

```html
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bootstrap Form Örneği</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" crossorigin="anonymous">
</head>
<body>
    <div class="container mt-5">
        <h2>Basit Form Örneği</h2>
        <form>
            <div class="mb-3">
                <label for="adSoyad" class="form-label">Ad Soyad</label>
                <input type="text" class="form-control" id="adSoyad" placeholder="Adınızı ve Soyadınızı Girin">
            </div>
            <div class="mb-3">
                <label for="email" class="form-label">E-posta Adresi</label>
                <input type="email" class="form-control" id="email" placeholder="name@example.com">
            </div>
            <div class="mb-3">
                <label for="mesaj" class="form-label">Mesajınız</label>
                <textarea class="form-control" id="mesaj" rows="3"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Gönder</button>
        </form>
    </div>

    <!-- Bootstrap JS (isteğe bağlı, form için zorunlu değil ama iyi pratik) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz" crossorigin="anonymous"></script>
</body>
</html>
```

#### 📄 Dosya: `model_selector.py`

```py
# model_selector.py
import os
from config import Colors, MODEL_CONFIGS

def check_api_key(env_var):
    """Ortam değişkeninde API anahtarı var mı kontrol eder."""
    key = os.getenv(env_var)
    return key is not None and len(key) > 0

def get_available_models():
    """Sistemdeki kullanılabilir modelleri dinamik olarak tarar."""
    available = {}
    
    # 1. Gemini Kontrolü
    gemini_conf = MODEL_CONFIGS["gemini"]
    if check_api_key(gemini_conf["env_var"]):
        try:
            from core.gemini import GeminiModel
            available["1"] = {
                "class": GeminiModel,
                "name": gemini_conf["display_name"],
                "status": f"{Colors.GREEN}✅ Hazır{Colors.RESET}"
            }
        except ImportError:
            available["1"] = {"status": f"{Colors.RED}❌ Kütüphane eksik (google-genai){Colors.RESET}"}
    else:
        available["1"] = {
            "name": gemini_conf["display_name"],
            "status": f"{Colors.RED}❌ API Key Eksik ({gemini_conf['env_var']}){Colors.RESET}"
        }

    # 2. Hugging Face Kontrolü
    hf_conf = MODEL_CONFIGS["huggingface"]
    if check_api_key(hf_conf["env_var"]):
        try:
            from core.huggingface import HuggingFaceModel
            available["2"] = {
                "class": HuggingFaceModel,
                "name": hf_conf["display_name"],
                "status": f"{Colors.GREEN}✅ Hazır{Colors.RESET}"
            }
        except ImportError:
             available["2"] = {"status": f"{Colors.RED}❌ Kütüphane eksik (requests){Colors.RESET}"}
    else:
        available["2"] = {
            "name": hf_conf["display_name"],
            "status": f"{Colors.RED}❌ API Key Eksik ({hf_conf['env_var']}){Colors.RESET}"
        }

    return available

def select_model_interactive():
    """Kullanıcıya interaktif seçim menüsü sunar."""
    available = get_available_models()
    
    print(f"\n{Colors.BLUE}╔════════════════════════════════════════╗")
    print(f"║       🤖  AI MODEL SEÇİM EKRANI        ║")
    print(f"╚════════════════════════════════════════╝{Colors.RESET}\n")

    ready_models = {}
    
    for key, info in available.items():
        # Eğer 'class' anahtarı varsa model çalıştırılabilir demektir
        if "class" in info:
            ready_models[key] = info["class"]
            print(f"  [{key}] {info['name']}  {info['status']}")
        else:
            print(f"  [{key}] {info.get('name', 'Bilinmeyen')}  {info['status']}")

    if not ready_models:
        print(f"\n{Colors.RED}⚠️  HİÇBİR MODEL KULLANILABİLİR DURUMDA DEĞİL!{Colors.RESET}")
        print(f"{Colors.YELLOW}Lütfen .bashrc dosyasına API anahtarlarınızı ekleyin.{Colors.RESET}")
        return None

    # Varsayılan olarak ilk hazır modeli seç
    default_key = list(ready_models.keys())[0]
    
    print(f"\n{Colors.CYAN}Varsayılan Model: {available[default_key]['name']} (Enter'a bas){Colors.RESET}")
    choice = input(f"{Colors.YELLOW}Seçiminiz [1/2]: {Colors.RESET}").strip()
    
    if not choice:
        choice = default_key
        
    if choice in ready_models:
        try:
            return ready_models[choice]()
        except Exception as e:
            print(f"{Colors.RED}Model başlatılırken hata oluştu: {e}{Colors.RESET}")
            return None
    else:
        print(f"{Colors.RED}Geçersiz seçim.{Colors.RESET}")
        return None
```

#### 📄 Dosya: `core\base.py`

```py
# core/base.py: Ortak Arayüz ve Hata Tanımları

class ModelAPIError(Exception):
    """API bağlantı/kota hataları için genel hata sınıfı."""
    pass

class BaseModel:
    """Tüm model sınıflarının miras alacağı soyut sınıf."""
    MODEL_NAME = "Temel Model"

    def __init__(self):
        # API anahtarını kontrol etme vb.
        pass

    def generate_content(self, system_instruction, prompt_text):
        """AI'dan içerik üretme çağrısı."""
        raise NotImplementedError("Bu metot alt sınıflar tarafından uygulanmalıdır.")
```

#### 📄 Dosya: `core\gemini.py`

```py
# core/gemini.py
import os
from google import genai
from google.genai import types
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class GeminiModel(BaseModel):
    def __init__(self):
        conf = MODEL_CONFIGS["gemini"]
        self.MODEL_NAME = conf["display_name"]
        
        # API Key'i ortamdan alıyoruz
        api_key = os.getenv(conf["env_var"])
        if not api_key:
            raise ModelAPIError(f"{conf['env_var']} bulunamadı.")

        try:
            # Client başlat (Orijinal koddaki gibi sade)
            self.client = genai.Client(api_key=api_key)
            self.model_id = conf["model_name"]
        except Exception as e:
            raise ModelAPIError(f"Gemini Client Başlatılamadı: {e}")

    def generate_content(self, system_instruction, prompt_text):
        try:
            # --- ORİJİNAL YAPIYA DÖNÜLDÜ ---
            # response_mime_type parametresi kaldırıldı, hata kaynağı buydu.
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt_text],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            return response.text.strip()
        except Exception as e:
            # Hata mesajını daha net görelim
            raise ModelAPIError(f"Gemini Hatası: {e}")
```

#### 📄 Dosya: `core\groq.py`

```py
# core/groq.py (DOĞRU VERSİYON)
import os
import requests
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class GroqModel(BaseModel):
    """Groq LPU - Ultra hızlı inference"""
    
    def __init__(self):
        conf = MODEL_CONFIGS["groq"]
        self.MODEL_NAME = conf["display_name"]
        
        # ⚠️ Buradaki atamaların doğru yapıldığından emin olun:
        self.api_key = os.getenv(conf["env_var"])
        if not self.api_key:
            raise ModelAPIError(f"{conf['env_var']} ortam değişkeni bulunamadı.")
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model_id = conf["model_id"]
    
    def generate_content(self, system_instruction, prompt_text):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt_text}
            ],
            "temperature": 0.1,
            "max_tokens": 8000,
            "response_format": {"type": "json_object"}  # JSON zorla
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            # Hata mesajını daha detaylı görmek için
            if hasattr(e, 'response') and e.response is not None:
                 print(f"DEBUG RESPONSE: {e.response.text}")
            raise ModelAPIError(f"Groq API Hatası: {e}")
```

#### 📄 Dosya: `core\huggingface.py`

```py
# core/huggingface.py
import os
import requests
import json
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class HuggingFaceModel(BaseModel):
    def __init__(self):
        conf = MODEL_CONFIGS["huggingface"]
        self.MODEL_NAME = conf["display_name"]
        self.model_id = conf["model_id"]
        
        self.api_key = os.getenv(conf["env_var"])
        if not self.api_key:
            raise ModelAPIError(f"{conf['env_var']} bulunamadı.")
        
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.api_url = f"https://router.huggingface.co/models/{self.model_id}"

    def generate_content(self, system_instruction, prompt_text):
        # --- PROMPT FORMATLAMA ---
        # Qwen ve modern modeller için ChatML formatı en iyisidir
        if "qwen" in self.model_id.lower():
            full_prompt = (
                f"<|im_start|>system\n{system_instruction}<|im_end|>\n"
                f"<|im_start|>user\n{prompt_text}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )
        elif "llama-3" in self.model_id.lower():
            full_prompt = (
                f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_instruction}<|eot_id|>\n"
                f"<|start_header_id|>user<|end_header_id|>\n{prompt_text}<|eot_id|>\n"
                f"<|start_header_id|>assistant<|end_header_id|>"
            )
        else:
            # Varsayılan (Mistral/Eski Llama)
            full_prompt = f"[INST] <<SYS>>\n{system_instruction}\n<</SYS>>\n{prompt_text} [/INST]"

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 4096, # Kod üretimi için yüksek token
                "temperature": 0.1,     # Tutarlılık için düşük sıcaklık
                "return_full_text": False
            }
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Hugging Face API bazen liste, bazen dict döner
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()
            elif isinstance(result, dict):
                return result.get('generated_text', '').strip()
            else:
                raise ModelAPIError(f"Beklenmeyen API yanıt formatı: {type(result)}")

        except Exception as e:
            raise ModelAPIError(f"HF API Hatası: {e}")
```
