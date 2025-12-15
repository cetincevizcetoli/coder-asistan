# 📝 Proje Dökümü: coder-asistan

Bu döküm, **/home/ahmetc/proje/coder-asistan** dizini (mevcut klasör) ve altındakileri kapsar.

### 📂 Proje Dizin Yapısı ve Dosyalar

- **coder-asistan/** (Proje Kökü)
  - assistant.py
  - check_models.py
  - config.py
  - index.html
  - model_selector.py
  - proje_dokumu_orjınal.md
  - readme.md
  - requirements.txt
  - **core/**
    - base.py
    - gemini.py
    - huggingface.py
  - **src/**
    - app.py
    - requirements.txt
    - **handlers/**
      - user.py
  - **gemini_venv/**
    - pyvenv.cfg
  - **.gassist_backups/**
    - app.py.20251214_225803.backup

---
### 💻 Kod İçeriği Dökümü


#### 📄 Dosya: `assistant.py`

```py
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
# config.py
import os

# --- RENKLER ---
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# --- DOSYA AYARLARI ---
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_TOTAL_SIZE = 20 * 1024 * 1024
BACKUP_DIR = ".gassist_backups"
HISTORY_LOG = ".gassist_history.log"
MAX_BACKUPS_PER_FILE = 10

# --- MODEL AYARLARI ---
MODEL_CONFIGS = {
    "gemini": {
        "env_var": "GOOGLE_API_KEY",
        "model_name": "gemini-2.5-flash", # En standart isim
        "display_name": "gemini-2.5-flash"
    },
    "huggingface": {
        "env_var": "HUGGINGFACE_API_KEY",
        "model_id": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "display_name": "Hugging Face (Qwen 2.5 Coder)"
    }
}

# --- SYSTEM PROMPT ---
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

#### 📄 Dosya: `core/base.py`

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

#### 📄 Dosya: `core/gemini.py`

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

#### 📄 Dosya: `core/huggingface.py`

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

#### 📄 Dosya: `src/app.py`

```py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/users')
def get_users():
    users = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'},
        {'id': 3, 'name': 'Charlie'}
    ]
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True)
```

#### 📄 Dosya: `src/handlers/user.py`

```py
Content preserved from original handlers/user.py
```
