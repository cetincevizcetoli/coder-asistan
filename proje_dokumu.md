# 📝 Proje Dökümü: coder-asistan

Bu döküm, **/home/ahmetc/proje/coder-asistan** dizini (mevcut klasör) ve altındakileri kapsar.

### 📂 Proje Dizin Yapısı ve Dosyalar

- **coder-asistan/** (Proje Kökü)
  - assistant.py
  - readme.md
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
# assistant.py (MODÜLER ÇEKİRDEK)
import sys
import os
import re
import json
import shutil
import glob
from datetime import datetime

# Modül importları (Gemini ve diğer modelleri buraya ekleyeceğiz)
from core.base import ModelAPIError
from core.gemini import GeminiModel 

# --- KONSTANTLAR ve YAPILANDIRMA ---
FILE_PATH_PATTERN = re.compile(r'\b[\w./-]+\.(py|js|html|css|md|json|txt|java|cpp|h|ts|jsx|tsx|sh)\b', re.IGNORECASE)
MAX_FILE_SIZE = 5_242_880  # 5MB
MAX_TOTAL_SIZE = 20_971_520 # 20MB
BACKUP_DIR = ".gassist_backups"
HISTORY_LOG = ".gassist_history.log"
MAX_BACKUPS_PER_FILE = 10 

# Renkli Terminal Çıktısı
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
DRY_RUN = False
VERBOSE = False

# Kullanılabilir Model Sınıfları Sözlüğü
AVAILABLE_MODELS = {
    "1": GeminiModel,
}

# Hugging Face modelini güvenli bir şekilde yükleme denemesi
try:
    from core.huggingface import HuggingFaceModel
    AVAILABLE_MODELS["2"] = HuggingFaceModel
except ImportError as e:
    print(f"{Colors.YELLOW}⚠️ Uyarı: Hugging Face modeli yüklenemedi. Detay: {e}{Colors.RESET}")
    print(f"{Colors.YELLOW}   Lütfen 'pip install requests' komutunu çalıştırdığınızdan emin olun.{Colors.RESET}")
except Exception as e:
    print(f"{Colors.YELLOW}⚠️ Uyarı: Hugging Face modülünde beklenmeyen hata: {e}{Colors.RESET}")

# --- GÜVENLİK ve UTILITY FONKSİYONLARI ---
# (is_safe_path, backup_if_exists, log_command fonksiyonları aynı kalır)

def is_safe_path(file_path, current_directory):
    if os.path.isabs(file_path): return False
    normalized_path = os.path.normpath(file_path)
    if normalized_path.startswith('..'): return False
    full_path = os.path.join(current_directory, file_path)
    real_path = os.path.realpath(full_path) 
    if not real_path.startswith(current_directory): return False
    return True

def backup_if_exists(full_path):
    if os.path.exists(full_path) and os.path.isfile(full_path):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{os.path.basename(full_path)}.{timestamp}.backup"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        try:
            shutil.copy(full_path, backup_path)
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Yedekleme Hatası: {os.path.basename(full_path)} yedeklenemedi. Detay: {e}{Colors.RESET}")
            return None
        pattern = os.path.join(BACKUP_DIR, f"{os.path.basename(full_path)}.*.backup")
        backups = sorted(glob.glob(pattern))
        if len(backups) > MAX_BACKUPS_PER_FILE:
            for old_backup in backups[:len(backups) - MAX_BACKUPS_PER_FILE]:
                os.remove(old_backup)
                if VERBOSE:
                     print(f"{Colors.YELLOW}   🗑️ Eski yedek silindi: {os.path.basename(old_backup)}{Colors.RESET}")
        return backup_path
    return None

def log_command(prompt, files_saved_names):
    with open(HISTORY_LOG, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Komut: {prompt[:100]}...\n")
        f.write(f"Sonuç: {len(files_saved_names)} dosya oluşturuldu/güncellendi: {', '.join(files_saved_names)}\n")

# --- YENİ: MODEL SEÇİMİ ---
def get_model_choice():
    """Kullanıcıya hangi modelin kullanılacağını sorar."""
    print(f"\n{Colors.BLUE}--- MEVCUT AI MODELLERİ ---{Colors.RESET}")
    for key, model_class in AVAILABLE_MODELS.items():
        print(f"  [{key}] {model_class.MODEL_NAME}")
    
    while True:
        choice = input(f"{Colors.YELLOW}Kullanılacak modeli seçin (Örn: 1):{Colors.RESET} ").strip()
        if choice in AVAILABLE_MODELS:
            try:
                # Seçilen modelin istemcisini başlat
                model_instance = AVAILABLE_MODELS[choice]()
                print(f"{Colors.GREEN}✨ Model seçildi: {model_instance.MODEL_NAME}{Colors.RESET}")
                return model_instance
            except ModelAPIError as e:
                print(f"{Colors.RED}Model Hatası: {e}{Colors.RESET}")
                print(f"{Colors.YELLOW}Lütfen API anahtarınızı veya ayarlarınızı kontrol edin.{Colors.RESET}")
                continue
        else:
            print(f"{Colors.YELLOW}Geçersiz seçim. Lütfen listeden bir sayı girin.{Colors.RESET}")

# --- ANA FONKSİYON ---
def get_assistant_response_and_save(prompt_text, model_instance):
    current_directory = os.getcwd()
    files_to_read = []
    
    # ... (1. ve 2. Adımlar: Dosya Okuma ve Prompt Hazırlama aynı kalır)
    potential_files = FILE_PATH_PATTERN.findall(prompt_text)
    
    for file_match in potential_files:
        file_path = file_match[0]
        full_path = os.path.join(current_directory, file_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                files_to_read.append(f"----- {file_path} -----\n{content}\n")
            except Exception as e:
                print(f"{Colors.YELLOW}Uyarı: '{file_path}' dosyası okunamadı. ({e}){Colors.RESET}")

    context = "\n".join(files_to_read)
    if context:
        prompt_text = f"Aşağıdaki mevcut dosya içeriğini ve yapısını dikkate alarak görevi tamamla:\n\n{context}\n\n--- YENİ GÖREV ---\n{prompt_text}"
        
    system_instruction = (
        "Sen gelişmiş bir Proje Yöneticisi Yapay Zekasın. "
        "Görevin, istenen dosya yapısını (oluşturma/güncelleme) sağlamaktır. "
        "Yanıtın SADECE, dosya yollarını (klasör dahil) anahtar, dosya içeriğini ise değer olarak içeren tek bir JSON sözlüğü olmalıdır. "
        "Dosya yolları göreceli olmalıdır (örn: 'src/config.py')."
        
        "\nÇOK ÖNEMLİ: JSON içeriğinde (değerlerde), JSON ayrıştırıcısını bozan özel karakterler veya kaçış dizileri kullanma. Tüm metin UTF-8 uyumlu olmalıdır. Tüm çıktıyı tek bir ```json ... ``` bloğunda ver."
        
        "\nÖRNEK JSON FORMATI: {'dosya/yolu.py': 'kod içeriği', 'README.md': 'metin içeriği'}"
    )
    
    print(f"{Colors.BLUE}✅ GÖREV ALINDI:{Colors.RESET} {prompt_text.splitlines()[-1][:70]}...")

    try:
        # API çağrısı, seçilen model örneği üzerinden yapılır
        full_response_text = model_instance.generate_content(
            system_instruction=system_instruction,
            prompt_text=prompt_text
        )
        
        # 3. JSON Çıktısını Güvenli Şekilde Ayıkla ve Ayrıştır
        json_match = re.search(r"```json\n(.*?)```", full_response_text, re.DOTALL)
        
        if json_match:
            json_string = json_match.group(1).strip()
            if VERBOSE: print(f"{Colors.YELLOW}DEBUG: JSON Markdown bloğu başarıyla ayrıştırıldı.{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️ Uyarı: Yanıtta beklenen JSON Markdown bloğu bulunamadı. Tam metinden ayrıştırma deneniyor...{Colors.RESET}")
            json_string = full_response_text.strip()
            
        # JSON yüklenirken hata yakalama
        try:
            json_string = json_string.replace('\u00ad', '').replace('\u200b', '').strip()
            file_map = json.loads(json_string)
            
        except json.JSONDecodeError as e:
            # ... (JSON Hata işleme aynı kalır)
            print(f"{Colors.RED}--- JSON ÇÖZÜMLEME HATASI ---{Colors.RESET}")
            print(f"{Colors.RED}AI, geçerli bir JSON formatı döndüremedi. Detay: {e}{Colors.RESET}")
            print(f"{Colors.YELLOW}İPUCU: Hata, genellikle README.md gibi çok satırlı metinlerdeki hatalı kaçış karakterlerinden kaynaklanır.{Colors.RESET}")
            raise e
            
        # ... (4, 5, 6, 7. Adımlar: Ön Kontrol, Onay, Kayıt ve Loglama aynı kalır)
        files_to_save = {}
        total_size = 0
        
        if not isinstance(file_map, dict):
             raise ValueError(f"{Colors.RED}AI, sözlük formatında (JSON Object) yanıt vermedi.{Colors.RESET}")
             
        for file_path, content in file_map.items():
            content_str = str(content).strip()
            content_size = len(content_str.encode('utf-8'))
            
            if not is_safe_path(file_path, current_directory):
                print(f"{Colors.RED}🚨 GÜVENLİK UYARISI: Şüpheli yol engellendi: {file_path}{Colors.RESET}")
                continue
            
            if content_size > MAX_FILE_SIZE:
                print(f"{Colors.YELLOW}⚠️ {file_path} çok büyük ({content_size/1024/1024:.2f}MB), atlanıyor (Limit: {MAX_FILE_SIZE/1024/1024:.2f}MB).{Colors.RESET}")
                continue
                
            total_size += content_size
            if total_size > MAX_TOTAL_SIZE:
                print(f"{Colors.YELLOW}⚠️ Toplam dosya boyutu limitini aştı ({total_size/1024/1024:.2f}MB). Kalan dosyalar atlanıyor.{Colors.RESET}")
                break

            files_to_save[file_path] = content_str
        
        if not files_to_save:
             print("\nİşlem yapılacak dosya bulunamadı. İptal edildi.")
             return
             
        print("\n📋 OLUŞTURULACAK/GÜNCELLENECEK DOSYALAR:")
        for file_path, content in files_to_save.items():
             print(f"{Colors.BLUE}   - {file_path} ({len(content)} karakter, Boyut: {len(content.encode('utf-8'))/1024:.2f} KB){Colors.RESET}")
             
        if DRY_RUN:
             print(f"\n{Colors.YELLOW}🧪 [DRY-RUN MODU AKTİF] Dosyalar kaydedilmeyecek, sadece gösterildi.{Colors.RESET}")
             return
             
        confirm = input(f"\nDevam edilsin mi? (e/h): {Colors.YELLOW}").lower()
        print(Colors.RESET, end="") 
        if confirm != 'e':
             print(f"{Colors.YELLOW}İşlem kullanıcı tarafından iptal edildi.{Colors.RESET}")
             return
             
        files_saved_names = []
        for file_path, content in files_to_save.items():
            full_path = os.path.join(current_directory, file_path)
            
            target_dir = os.path.dirname(full_path)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            backup_path = backup_if_exists(full_path)
            if backup_path:
                print(f"{Colors.GREEN}   📦 Yedeklendi: {os.path.basename(backup_path)}{Colors.RESET}")

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"{Colors.GREEN}   -> KAYDEDİLDİ/GÜNCELLENDİ: {file_path}{Colors.RESET}")
            files_saved_names.append(file_path)
            
        print(f"\n{Colors.GREEN}✨ BAŞARILI: Toplam {len(files_saved_names)} dosya oluşturuldu/güncellendi.{Colors.RESET}")
        
        log_command(prompt_text, files_saved_names)


    # YENİ HATA YAKALAMA BLOKLARI (Modül üzerinden gelen hataları yakalar)
    except ModelAPIError as e:
        print(f"\n{Colors.RED}--- KRİTİK API HATASI ---{Colors.RESET}")
        print(f"{Colors.RED}API İletişim Hatası: {e}{Colors.RESET}")
        
    except Exception as e:
        if 'full_response_text' in locals() and full_response_text:
             print(f"\n{Colors.YELLOW}--- AI YANITI (HATA AYIKLAMA İÇİN) ---{Colors.RESET}")
             print(full_response_text)
             print("------------------------------------------")
        else:
             print(f"\n{Colors.RED}--- KRİTİK HATA ---{Colors.RESET}")

        print(f"{Colors.RED}❌ BEKLENMEYEN HATA: Proje kaydı başarısız oldu. Detay: {e}{Colors.RESET}")

# --- ANA ÇALIŞMA BLOĞU ---
if __name__ == "__main__":
    
    if "--dry-run" in sys.argv:
        DRY_RUN = True
        sys.argv.remove("--dry-run")
    if "--verbose" in sys.argv:
        VERBOSE = True
        sys.argv.remove("--verbose")

    if len(sys.argv) < 2:
        print(f"{Colors.YELLOW}Kullanım:{Colors.RESET} gassist \"[Göreviniz Buraya]\" [--dry-run] [--verbose]")
        print(f"{Colors.YELLOW}Örnek:{Colors.RESET} gassist \"src/app.js ve index.html oluştur.\" --dry-run")
        sys.exit(1)
    
    gorev_prompt = " ".join(sys.argv[1:]) 
    
    # Yeni: Modeli Seç
    selected_model = get_model_choice()
    
    get_assistant_response_and_save(gorev_prompt, selected_model)
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
# core/gemini.py: Google Gemini API Uygulaması
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
from .base import BaseModel, ModelAPIError

class GeminiModel(BaseModel):
    MODEL_NAME = "Google Gemini (gemini-2.5-flash)"

    def __init__(self):
        try:
            self.client = genai.Client()
        except Exception as e:
            raise ModelAPIError(f"Gemini istemcisi başlatılamadı: {e}")

    def generate_content(self, system_instruction, prompt_text):
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt_text],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            return response.text.strip()
            
        except APIError as e:
            # API hatalarını genel ModelAPIError olarak yükseltme
            error_message = getattr(e, 'message', str(e))
            raise ModelAPIError(f"Gemini API Hatası: {error_message}")
```

#### 📄 Dosya: `core/huggingface.py`

```py
# core/huggingface.py: Hugging Face Inference API Uygulaması
import os
import requests
import json
from .base import BaseModel, ModelAPIError

# Örnek kodlama görevleri için güçlü bir model
# Bu modelin API erişimi daha stabil olma eğilimindedir.
# Code Llama'nın 7B Instruct versiyonunu deneyelim
# Yeni, daha stabil olduğu varsayılan model:
# Yeni, kodlama odaklı ve stabil olduğu varsayılan model
DEFAULT_HF_MODEL = "meta-llama/Meta-Llama-3–8B-Instruct"
HF_API_URL_TEMPLATE = "https://router.huggingface.co/models/{model_id}"

class HuggingFaceModel(BaseModel):
    MODEL_NAME = f"Hugging Face ({DEFAULT_HF_MODEL})"

    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ModelAPIError("HUGGINGFACE_API_KEY ortam değişkeni ayarlanmadı.")
        
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.api_url = HF_API_URL_TEMPLATE.format(model_id=DEFAULT_HF_MODEL)
        
    def generate_content(self, system_instruction, prompt_text):
        
        # Mistral formatını kullanarak system instruction ve prompt'u birleştirme
        full_prompt = (
            f"<s>[INST] <<SYS>>{system_instruction}<</SYS>>"
            f"Görevi tamamla ve SADECE JSON çıktısı ver: {prompt_text} [/INST]"
        )
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 2000,
                "temperature": 0.1,
                "return_full_text": False
            },
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status() # HTTP 4xx veya 5xx hatası varsa fırlatır

            response_json = response.json()
            
            # Hugging Face'in yanıt formatı genellikle bir liste döndürür.
            if not isinstance(response_json, list) or 'generated_text' not in response_json[0]:
                raise ModelAPIError(f"Hugging Face'ten beklenmedik yanıt formatı alındı: {response_json}")
                
            return response_json[0]['generated_text'].strip()

        except requests.exceptions.RequestException as e:
            # Tüm requests hatalarını (bağlantı, timeout, HTTP hataları) yakala
            raise ModelAPIError(f"Hugging Face API çağrısı başarısız oldu: {e}")
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
