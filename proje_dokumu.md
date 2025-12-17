# 📝 Proje Dökümü: coder-asistan

Bu döküm, **D:\projects\coder-asistan** dizini için oluşturulmuştur.
Not: `my_projects` klasörünün içeriği gizlilik gereği hariç tutulmuştur.

### 📂 Proje Dizin Yapısı ve Dosyalar

- **coder-asistan/** (Proje Kökü)
  - .gitignore
  - ARCHITECTURE.md
  - assistant.py
  - check_models.py
  - config.py
  - debug.py
  - generate_docs.py
  - launcher.py
  - migrate_projects.py
  - model_selector.py
  - proje_dokumu.md
  - readme.md
  - requirements.txt
  - system_audit.py
  - **core/**
    - base.py
    - deepseek.py
    - gemini.py
    - groq.py
    - huggingface.py
    - memory.py
  - **my_projects/** (Kullanıcı Projeleri - İçerik Gizli)

---
### 💻 Kod İçeriği Dökümü


#### 📄 Dosya: `ARCHITECTURE.md`

```md
# 🏗️ Coder-Asistan: Teknik Mimari ve Geliştirici Kılavuzu

Bu belge, **Coder-Asistan** projesinin iç yapısını, veri akışını, tasarım kararlarını ve sistemin "neden" böyle çalıştığını anlatan teknik referanstır.

Proje, basit bir script değil; modüler, RAG (Retrieval-Augmented Generation) tabanlı ve durum (state) korumalı bir **CLI Kodlama Stüdyosu**dur.

---

## 1. 🗺️ Kuş Bakışı Sistem Mimarisi

Sistem 4 ana katmandan oluşur:

1.  **Yönetim Katmanı (Launcher):** Kullanıcıyı karşılar, proje izolasyonunu sağlar ve çalışma dizinini ayarlar.
2.  **Beyin Katmanı (Assistant & Config):** Kullanıcı isteğini işler, maliyeti hesaplar ve AI'ya "JSON formatında" emir verir.
3.  **Hafıza Katmanı (RAG Core):** Projedeki kodları vektörleştirir (Embedding) ve anlamsal arama yapar.
4.  **Adaptör Katmanı (Model Core):** Farklı AI sağlayıcılarını (Gemini, Groq, HF) tek bir standart arayüze dönüştürür.


```text
      [ KULLANICI ]
           │
           ▼
  ┌─────────────────┐
  │   LAUNCHER.PY   │  (1. Giriş Kapısı & Proje Seçimi)
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐       ┌───────────────────┐
  │  ASSISTANT.PY   │ ◄───► │  CONFIG (Kurallar)│
  │ (Karar Motoru)  │       └───────────────────┘
  └────────┬────────┘
           │
           ├───► [ 🧠 HAFIZA (RAG) ] ◄─── (.coder_memory)
           │      (Kodları Hatırlar)
           │
           ▼
  ┌─────────────────┐
  │   MODEL CORE    │  (Adaptör Katmanı)
  └────────┬────────┘
           │
           ├───► Google Gemini
           ├───► Groq Llama 3
           └───► DeepSeek / HF

---

## 2. 📂 Dizin Yapısı ve Sorumluluklar

```text
coder-asistan/
├── launcher.py           # [ENTRY POINT] Proje seçimi ve ortam hazırlığı
├── assistant.py          # [MAIN LOOP] İstek-Cevap döngüsü ve dosya işlemleri
├── config.py             # [SETTINGS] Sabitler, Promptlar ve Fiyatlandırma
├── requirements.txt      # Bağımlılıklar
│
├── my_projects/          # [USER DATA] Kullanıcı projelerinin fiziksel konumu
│   └── proje_x/          # -> İzole Çalışma Alanı
│       ├── .coder_memory/ # -> ChromaDB (Vektör Veritabanı)
│       ├── .chat_history/ # -> Loglar
│       └── src/           # -> Kullanıcı Kodları
│
├── core/                 # [BACKEND] Sistem çekirdeği
│   ├── base.py           # -> Soyut Model Sınıfı (Interface)
│   ├── memory.py         # -> RAG Motoru (SentenceTransformers + ChromaDB)
│   ├── gemini.py         # -> Google Adapter
│   └── groq.py           # -> Groq Adapter
│
└── utils/ (Opsiyonel)    # Yardımcı araçlar (debug.py, system_audit.py vb.)
```

---

## 3. ⚙️ Veri Akışı (Bir Komutun Yolculuğu)

Kullanıcı `python launcher.py` çalıştırıp bir projeye girdiğinde ve "Hatayı düzelt" dediğinde arka planda şu olaylar zinciri gerçekleşir:

### Adım 1: Bağlamın Yüklenmesi (Context Loading)
* `assistant.py`, `core.memory.MemoryManager`'ı başlatır.
* Kullanıcının sorusu ("Hatayı düzelt"), `SentenceTransformer` modeli ile **vektöre** (sayısal diziye) çevrilir.
* ChromaDB içinde bu vektöre matematiksel olarak en yakın olan kod parçaları (Chunks) bulunur.

### Adım 2: Prompt Mühendisliği (Prompt Engineering)
AI'ya giden metin şu şablonda birleştirilir:
1.  **Sistem Emri (`config.SYSTEM_INSTRUCTION`):** "Sen bir JSON makinesisin. Asla sohbet etme."
2.  **RAG Bağlamı:** "Veritabanından bulduğum ilgili kodlar şunlar: ..."
3.  **Kullanıcı İsteği:** "Hatayı düzelt."

### Adım 3: Model Çağrısı ve Adaptasyon
* Seçili model (Örn: Gemini), `core/gemini.py` üzerinden çağrılır.
* Her model farklı yanıt verse de (Object, Dict, Text), adaptörler bunu standart bir formata çevirir.

### Adım 4: JSON Temizliği ve Güvenlik
* AI'dan gelen yanıt `clean_json_string()` fonksiyonuna girer. Markdown etiketleri (` ```json `) temizlenir.
* Saf JSON parse edilir.
* **Güvenlik:** AI "Bilgisayarı kapat" diyemez. Sadece `dosya_olustur` veya `dosya_sil` komutları işlenir.

### Adım 5: İşlem ve Yedekleme
* Dosya yazılmadan önce `backup_file()` fonksiyonu devreye girer.
* Hedef dosyanın bir kopyası `.gassist_backups` klasörüne zaman damgasıyla (timestamp) kaydedilir.
* Yeni içerik yazılır.

---

## 4. 🔧 Kritik Konfigürasyonlar (`config.py`)

Geliştiricilerin bilmesi gereken hassas ayarlar:

* **`SYSTEM_INSTRUCTION`:** Sistemsel prompt. AI'nın "Suskun" olmasını sağlayan yer burasıdır. Buradaki kurallar gevşetilirse sistemin JSON parse yeteneği bozulabilir.
* **`MAX_FILE_SIZE`:** Varsayılan 5MB. AI'nın token limitini patlatmaması için büyük dosyalar (loglar, binaryler) okunmaz.
* **`PRICING_RATES`:** Maliyet hesaplama tablosu. Statiktir, API fiyatları değişirse manuel güncellenmelidir.

---

## 5. 🛠️ Geliştirici Araç Seti (DevTools)

Projeyi debug etmek veya yönetmek için kullanılan "İsviçre Çakısı" araçları:

| Araç | Dosya | Görevi |
| :--- | :--- | :--- |
| **Hafıza Müfettişi** | `debug.py` | ChromaDB veritabanına bağlanır, vektörleri ve kayıtlı kod parçalarını ham haliyle gösterir. |
| **Sistem Doktoru** | `system_audit.py` | Dosya izinlerini, log boyutlarını ve veritabanı bütünlüğünü (integrity) kontrol eder. |
| **Proje Taşıyıcı** | `migrate_projects.py` | `my_projects` dışındaki "sahipsiz" projeleri bulup içeriye taşır. |
| **Belgeleyici** | `generate_docs.py` | Tüm kod yapısını tek bir Markdown dosyasına döker (LLM analizi için). |

---

## 6. 🚀 Gelecek Planları ve Genişletilebilirlik

Bu mimari şunlara izin verecek şekilde tasarlanmıştır:
* **Yeni Model Ekleme:** Sadece `core/` altına yeni bir `.py` dosyası ekleyerek.
* **Resim Desteği:** `assistant.py` güncellenerek Gemini 1.5 Pro'nun Vision özellikleri açılabilir.
* **Web Arayüzü:** Logic (Mantık) ve UI (Arayüz) ayrıldığı için, `launcher.py` yerine bir `app.py` (Flask/Streamlit) yazılarak kolayca web'e taşınabilir.

---
**Geliştirici:** Ahmet Çetin
*Bu doküman Coder-Asistan v2.0 mimarisini yansıtır.*
```

#### 📄 Dosya: `assistant.py`

```py
import sys
import os
import re
import json
import shutil
import time
import requests
from datetime import datetime
from typing import List, Optional, Any, Tuple, Dict

# --- PROJE MODÜLLERİ ---
import config
from config import Colors, PRICING_RATES
from core.memory import MemoryManager

# --- DİNAMİK MODEL İMPORTLARI ---
try: from core.gemini import GeminiModel
except ImportError: pass
try: from core.groq import GroqModel; GROQ_AVAILABLE = True
except ImportError: GROQ_AVAILABLE = False
try: from core.deepseek import DeepSeekModel; DEEPSEEK_AVAILABLE = True
except ImportError: DEEPSEEK_AVAILABLE = False
try: from core.huggingface import HuggingFaceModel; HF_AVAILABLE = True
except ImportError: HF_AVAILABLE = False

# --- SABİTLER ---
FILE_PATTERN = re.compile(r"[\w-]+\.(py|js|html|css|md|json|txt|java|cpp|h|ts|jsx|tsx|sh|env)", re.IGNORECASE)

# ==========================================
# 🛠️ YARDIMCI FONKSİYONLAR
# ==========================================

def is_safe_path(file_path: str, current_directory: str) -> bool:
    if os.path.isabs(file_path): return False
    normalized_path = os.path.normpath(file_path)
    if normalized_path.startswith('..'): return False
    full_path = os.path.join(current_directory, file_path)
    return os.path.realpath(full_path).startswith(current_directory)

def clean_json_string(json_string: str) -> Optional[Dict]:
    """
    AI'dan gelen yanıtı temizler ve parse eder.
    GELİŞTİRİLMİŞ VERSİYON: Hata olursa programı çökertmek yerine None döner.
    """
    try:
        # Markdown kod bloklarını temizle (```json ... ```)
        if "```" in json_string:
            lines = json_string.split('\n')
            clean_lines = []
            capture = False
            for line in lines:
                if "```" in line:
                    capture = not capture # Blok başladı/bitti
                    continue
                if capture:
                    clean_lines.append(line)
            
            # Eğer kod bloğu bulduysak onu kullan, bulamadıysak (sadece ``` varsa) ham metni temizle
            if clean_lines:
                json_string = "\n".join(clean_lines)
            else:
                json_string = json_string.replace("```json", "").replace("```", "")

        # Temizlik sonrası kalan boşlukları al
        json_string = json_string.strip()
        
        # Olası fazlalıkları temizle (Bazen AI en sona açıklama ekler)
        if json_string.rfind('}') != -1:
            json_string = json_string[:json_string.rfind('}')+1]

        # JSON Parse Denemesi
        return json.loads(json_string)

    except json.JSONDecodeError:
        print(f"\n{Colors.RED}❌ AI Yanıtı JSON Formatına Uymuyor!{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.RED}❌ Beklenmeyen JSON Hatası: {e}{Colors.RESET}")
        return None

def backup_file(full_path: str) -> Optional[str]:
    if not os.path.exists(full_path): return None
    os.makedirs(config.BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{os.path.basename(full_path)}.{timestamp}.backup"
    shutil.copy(full_path, os.path.join(config.BACKUP_DIR, backup_name))
    return backup_name

def extract_wait_time(error_message: str) -> int:
    match = re.search(r"retry in (\d+(\.\d+)?)s", str(error_message))
    if match: return int(float(match.group(1))) + 2 
    return 30 

def log_conversation(working_dir: str, user_prompt: str, ai_explanation: str, model_name: str, cost: float = 0.0):
    """Sohbeti ve MALİYETİ detaylı şekilde log dosyasına kaydeder."""
    log_file = os.path.join(working_dir, ".chat_history.log")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    log_entry = (
        f"════════════════════════════════════════════════════════════\n"
        f"📅 ZAMAN: {timestamp} | 🤖 MODEL: {model_name}\n"
        f"💰 MALİYET: ${cost:.5f}\n"
        f"👤 USER: {user_prompt}\n"
        f"🤖 AI:   {ai_explanation}\n"
    )
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"{Colors.RED}Log Yazma Hatası: {e}{Colors.RESET}")

def update_project_stats(working_dir: str, usage_data: dict, model_key: str) -> Tuple[float, float]:
    """Toplam proje maliyetini hesaplar, kaydeder ve döner."""
    stats_file = os.path.join(working_dir, ".project_stats.json")
    
    stats = {
        "total_cost": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "last_updated": ""
    }

    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        except: pass

    in_tokens = usage_data.get("input_tokens", 0)
    out_tokens = usage_data.get("output_tokens", 0)
    rates = PRICING_RATES.get(model_key, {"input": 0, "output": 0})
    
    current_cost = ((in_tokens / 1_000_000) * rates["input"]) + ((out_tokens / 1_000_000) * rates["output"])

    stats["total_cost"] += current_cost
    stats["total_input_tokens"] += in_tokens
    stats["total_output_tokens"] += out_tokens
    stats["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=4)
    except Exception as e:
        print(f"{Colors.RED}İstatistik kayıt hatası: {e}{Colors.RESET}")

    return current_cost, stats["total_cost"]

def print_cost_report(current_cost: float, total_cost: float, usage_data: dict):
    in_tokens = usage_data.get("input_tokens", 0)
    out_tokens = usage_data.get("output_tokens", 0)

    tier_label = "ÜCRETSİZ KATMAN" if config.USER_TIER == 'free' else "ÜCRETLİ API"
    
    if config.USER_TIER == 'free':
        c_cost_str = "$0.00000"
        t_cost_str = "$0.00000"
    else:
        c_cost_str = f"${current_cost:.5f}"
        t_cost_str = f"${total_cost:.5f}"

    print(f"\n{Colors.GREY}📊 FİNANSAL RAPOR ({tier_label}){Colors.RESET}")
    print(f"{Colors.GREY}   ├── Bu İşlem:  Girdi: {in_tokens:<5} | Çıktı: {out_tokens:<5} | Maliyet: {Colors.GREEN}{c_cost_str}{Colors.RESET}")
    print(f"{Colors.GREY}   └── 💰 TOPLAM: {Colors.CYAN}Proje Geneli Harcama: {t_cost_str}{Colors.RESET}")

# ==========================================
# 🚀 ANA İŞLEM DÖNGÜSÜ
# ==========================================

def main_process(prompt_text: str, model_instance: Any, working_dir: str, is_dry_run: bool = False):
    
    try: memory = MemoryManager(project_root=working_dir)
    except: memory = None

    if memory:
        all_files = []
        for root, dirs, files in os.walk(working_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if FILE_PATTERN.match(file):
                    rel_path = os.path.relpath(os.path.join(root, file), working_dir)
                    all_files.append(rel_path)
        if all_files: memory.index_files(all_files)

    rag_context = ""
    if memory:
        print(f"{Colors.CYAN}🔍 Hafıza taranıyor...{Colors.RESET}")
        rag_context = memory.query(prompt_text, n_results=config.MAX_CONTEXT_RESULTS)
        if len(rag_context) > config.MAX_CONTEXT_CHARS:
            rag_context = rag_context[:config.MAX_CONTEXT_CHARS] + "\n...(Kırpıldı)..."

    full_prompt = (
        f"--- PROJE BAĞLAMI ---\n{rag_context}\n\n"
        f"--- KULLANICI İSTEĞİ ---\n{prompt_text}\n"
    )
        
    print(f"{Colors.BLUE}✅ GÖREV:{Colors.RESET} {prompt_text}")
    if is_dry_run: print(f"{Colors.YELLOW}🧪 (DRY-RUN AKTİF){Colors.RESET}")

    ai_response_plan = {} 
    
    # Maliyet değişkenleri
    current_cost = 0.0
    total_cost = 0.0

    # 4. MODEL ÇALIŞTIRMA
    while True:
        masked_key = os.getenv("GOOGLE_API_KEY", "")[:5] + "..."
        print(f"{Colors.CYAN}⏳ {model_instance.MODEL_NAME} düşünüyor... (Key: {masked_key}){Colors.RESET}")
        
        try:
            response_data = model_instance.generate_content(
                system_instruction=config.SYSTEM_INSTRUCTION,
                prompt_text=full_prompt
            )
            
            if isinstance(response_data, str):
                raw_text = response_data; usage_info = {}; model_key_used = "unknown"
            else:
                raw_text = response_data["content"]; usage_info = response_data["usage"]; model_key_used = response_data["model_key"]

            # --- GÜVENLİ PARSE İŞLEMİ (DÜZELTİLDİ) ---
            # Artık clean_json_string direkt olarak dictionary veya None dönüyor
            ai_response_plan = clean_json_string(raw_text)
            
            if ai_response_plan is None:
                print(f"{Colors.RED}⚠️ AI geçersiz format üretti. Tekrar deneniyor...{Colors.RESET}")
                # İsterseniz burada 'continue' diyerek AI'ya tekrar sordurabilirsiniz
                # Ancak sonsuz döngüye girmemesi için şimdilik çıkış yapıyoruz veya kullanıcıya soruyoruz.
                if input("Format bozuk. Tekrar denesin mi? (e/h): ").lower() == 'e':
                    continue
                else:
                    return

            # --- MALİYET HESAPLAMA ---
            current_cost, total_cost = update_project_stats(working_dir, usage_info, model_key_used)
            print_cost_report(current_cost, total_cost, usage_info)
            break 

        except requests.exceptions.ConnectionError:
            print(f"\n{Colors.RED}📡 İNTERNET BAĞLANTISI YOK!{Colors.RESET}")
            if input("Tekrar? (e/h): ").lower() != 'e': return
        
        except Exception as e:
            err_str = str(e)
            print(f"\n{Colors.RED}💣 HATA: {e}{Colors.RESET}")
            if "429" in err_str:
                wait_time = extract_wait_time(err_str)
                print(f"{Colors.YELLOW}🚦 Kota doldu ({wait_time}s). [1] Bekle [2] Model Seç [3] İptal{Colors.RESET}")
                c = input("Seçim: ")
                if c == "1":
                    time.sleep(wait_time); continue
                elif c == "2":
                    from model_selector import select_model_interactive
                    m = select_model_interactive()
                    if m: model_instance = m
                    continue
                else: return
            else:
                if input("Tekrar? (e/h): ").lower() != 'e': return

    # --- PLANLAMA ---
    explanation = ai_response_plan.get("aciklama", "Açıklama yok.")
    files_to_create = ai_response_plan.get("dosya_olustur", {})
    files_to_delete = ai_response_plan.get("dosya_sil", [])

    print(f"\n{Colors.MAGENTA}🤖 AI DİYOR Kİ:{Colors.RESET}")
    print(f"{Colors.CYAN}{explanation}{Colors.RESET}")
    
    print("\n📋 PLANLANAN DEĞİŞİKLİKLER:")
    for path in files_to_create.keys(): print(f"   📂 OLUŞTUR/GÜNCELLE: {path}")
    for path in files_to_delete: print(f"   🗑️  SİLİNECEK: {path}")

    if not files_to_create and not files_to_delete:
        print(f"{Colors.YELLOW}   (İşlem yok){Colors.RESET}")
        log_conversation(working_dir, prompt_text, explanation, model_instance.MODEL_NAME, current_cost)
        return

    if is_dry_run:
        print(f"\n{Colors.YELLOW}🧪 DRY-RUN Bitti.{Colors.RESET}")
        return

    if input(f"\n{Colors.GREEN}Onaylıyor musunuz? (e/h): {Colors.RESET}").lower() != 'e':
        print("❌ İptal edildi.")
        return

    # --- UYGULAMA ---
    for rel_path in files_to_delete:
        if not is_safe_path(rel_path, working_dir): continue
        full_path = os.path.join(working_dir, rel_path)
        if os.path.exists(full_path):
            try:
                backup_file(full_path)
                os.remove(full_path)
                print(f"{Colors.RED}   🗑️  Silindi: {rel_path}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}   ❌ Silinemedi: {rel_path} ({e}){Colors.RESET}")

    for rel_path, content in files_to_create.items():
        if not is_safe_path(rel_path, working_dir):
            print(f"{Colors.RED}🚨 Engellendi: {rel_path}{Colors.RESET}")
            continue
        full_path = os.path.join(working_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if os.path.exists(full_path): backup_file(full_path)
        with open(full_path, 'w', encoding='utf-8') as f: f.write(content)
        print(f"{Colors.GREEN}   ✅ Yazıldı: {rel_path}{Colors.RESET}")
        if memory: memory.index_files([rel_path])

    # Loglama (Maliyet parametresi eklendi)
    log_conversation(working_dir, prompt_text, explanation, model_instance.MODEL_NAME, current_cost)


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    
    raw_args = sys.argv[1:]
    is_dry_run = "--dry-run" in raw_args
    cleaned_args = [a for a in raw_args if a != "--dry-run" and a != "--verbose"]
    prompt = " ".join(cleaned_args)
    cwd = os.getcwd()
    
    from model_selector import select_model_interactive
    model = select_model_interactive()
    if model: main_process(prompt, model, cwd, is_dry_run=is_dry_run)
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
    sys.exit(1)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ HATA: GOOGLE_API_KEY tanımlı değil!")
    sys.exit(1)

print(f"🔑 Anahtar ile bağlanılıyor... (Son 4 hane: {api_key[-4:]})")

try:
    client = genai.Client(api_key=api_key)
    print("\n📡 --- HESABINIZDA AKTİF OLAN MODELLER ---")
    
    count = 0
    # Modelleri çek ve listele
    # Pager üzerinden döner, listeye çevirelim
    for m in client.models.list():
        # Sadece içerik üretebilen modelleri al
        if "generateContent" in m.supported_actions:
            # İsmi temizle (models/ önekini at)
            clean_name = m.name.replace('models/', '')
            print(f"✅ {clean_name}")
            count += 1
            
    if count == 0:
        print("\n⚠️ HATA: Hiçbir model bulunamadı. API Key'inizin yetkilerini kontrol edin.")
    else:
        print("\n👉 İPUCU: Yukarıdaki ✅ ile başlayan isimlerden birini config.py dosyasına kopyalayın.")

except Exception as e:
    print(f"\n❌ BAĞLANTI HATASI: {e}")
```

#### 📄 Dosya: `config.py`

```py
import os

# ==========================================
# 🎨 RENK AYARLARI
# ==========================================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    GREY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# ==========================================
# ⚙️ SİSTEM VE DOSYA AYARLARI
# ==========================================
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_TOTAL_SIZE = 20 * 1024 * 1024
BACKUP_DIR = ".gassist_backups"
MAX_BACKUPS_PER_FILE = 5
MEMORY_DIR_NAME = ".coder_memory"
COLLECTION_NAME = "project_codebase"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_CONTEXT_RESULTS = 3
MAX_CONTEXT_CHARS = 12000
MAX_BACKUPS_PER_FILE = 10


# YENİ: Projelerin toplanacağı ana klasör
PROJECTS_DIR = "my_projects"

# ==========================================
# 💰 MALİYET VE KATMAN
# ==========================================
USER_TIER = 'free' 
PRICING_RATES = {
    "gemini-2.5-flash-lite": { "input": 0.075, "output": 0.30 },
    "gemini-2.5-flash": { "input": 0.10, "output": 0.40 },
    "llama-3.3-70b-versatile": { "input": 0.59, "output": 0.79 },
    "deepseek-chat": { "input": 0.14, "output": 0.28 },
    "Qwen/Qwen2.5-Coder-7B-Instruct": { "input": 0.0, "output": 0.0 }
}

# ==========================================
# 🤖 MODEL AYARLARI
# ==========================================
MODEL_CONFIGS = {
    "gemini": {
        "env_var": "GOOGLE_API_KEY",
        "model_name": "gemini-2.5-flash-lite", 
        "display_name": "Google Gemini 2.5 Flash Lite",
    },
    "groq": {
        "env_var": "GROQ_API_KEY",
        "model_id": "llama-3.3-70b-versatile",
        "display_name": "Groq Llama 3.3 70B",
    },
    "deepseek": {
        "env_var": "DEEPSEEK_API_KEY",
        "model_id": "deepseek-chat",
        "display_name": "DeepSeek Chat",
    },
    "huggingface": {
        "env_var": "HUGGINGFACE_API_KEY",
        "model_id": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "display_name": "Hugging Face Qwen",
    }
}

# ==========================================
# 🧠 YENİ AI SİSTEM TALİMATI (Akıllı JSON Modu)
# ==========================================
SYSTEM_INSTRUCTION = (
    "Sen uzman bir yazılım mimarı ve kodlama asistanısın. "
    "Görevin: Verilen talimatlara ve RAG hafızasından gelen bağlama göre projeyi yönetmektir.\n"
    "KURALLAR:\n"
    "1. Yanıtın SADECE ve SADECE geçerli bir JSON objesi olmalıdır.\n"
    "2. JSON formatı ŞU ŞEKİLDE OLMALIDIR:\n"
    "{\n"
    "  'aciklama': 'Yaptığınız işlemin kısa bir özeti ve nedeni (Örn: Hatalı yolu düzelttim)',\n"
    "  'dosya_olustur': {'dosya_yolu': 'icerik', 'dosya_yolu2': 'icerik'},\n"
    "  'dosya_sil': ['silinecek_dosya_yolu_1', 'silinecek_dosya_yolu_2']\n"
    "}\n"
    "3. Eğer silinecek dosya yoksa 'dosya_sil': [] gönder.\n"
    "4. Asla Markdown (```json ... ```) kullanma, sadece saf JSON döndür.\n"
    "5. Türkçe karakterleri UTF-8 olarak koru."
)
```

#### 📄 Dosya: `debug.py`

```py
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
```

#### 📄 Dosya: `generate_docs.py`

```py
import os
import sys

# ==========================================
# ⚙️ AYARLAR VE FİLTRELER
# ==========================================

# Sadece içeriği taranmayacak sistem klasörleri
DIKKATE_ALINMAYACAK_DIZINLER = [
    '.git', '__pycache__', 'venv', '.venv', 'env', '.env', 'node_modules', 
    '.vscode', '.idea', 'dist', 'build', 'target', 'bin',
    '__macosx', '.ds_store', 'logs', 'site-packages', 'lib', 'include',
    '.gassist_backups', '.coder_memory'
]

# İçeriği dökülmeyecek ama varlığı gösterilecek "Özel" klasörler
OZEL_USER_KLASORLERI = ['my_projects']

# İçeriği döküme eklenecek kod uzantıları
BELGELENECEK_KOD_UZANTILARI = [
    '.py', '.php', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', 
    '.sh', '.bash', '.c', '.cpp', '.h', '.hpp', '.java', '.go', '.rb', '.swift', 
    '.kt', '.ts', '.jsx', '.tsx', '.conf', '.ini', '.sql', '.md', '.txt'
]

# Çıktı dosyasının adı
CIKTI_DOSYASI = "proje_dokumu.md"

# ==========================================
# 🛠️ FONKSİYONLAR
# ==========================================

def dosya_icerigini_getir(yol):
    """Dosya içeriğini okur ve Markdown kod bloğu içinde döndürür."""
    try:
        with open(yol, 'r', encoding='utf-8') as f:
            icerik = f.read()
            
        uzanti = os.path.splitext(yol)[1].lstrip('.').lower()
        return f"\n```{(uzanti if uzanti else 'plaintext')}\n{icerik}\n```\n"
    except Exception as e:
        return f"\n> [Okunamadı: {e}]\n"

def dizin_yapisi_getir(hedef_dizin):
    """Verilen yoldan başlayarak dizin yapısını döndürür."""
    yapı = "### 📂 Proje Dizin Yapısı ve Dosyalar\n\n"
    
    for kok, dizinler, dosyalar in os.walk(hedef_dizin):
        # Filtreleme: Gereksiz klasörleri gezme
        dizinler[:] = [d for d in dizinler if d.lower() not in DIKKATE_ALINMAYACAK_DIZINLER]
        
        yol_parcalari = kok.lower().split(os.sep)
        if any(yasak in yol_parcalari for yasak in DIKKATE_ALINMAYACAK_DIZINLER):
            continue

        base_name = os.path.basename(kok)
        goreli_yol = os.path.relpath(kok, hedef_dizin)
        
        # Ağaç yapısı başlığı
        if goreli_yol == '.':
            seviye = 0
            yapı += f"- **{os.path.basename(hedef_dizin)}/** (Proje Kökü)\n"
        else:
            seviye = goreli_yol.count(os.sep) + 1
            girinti = "  " * seviye
            
            # Özel klasör kontrolü (my_projects gibi)
            if base_name in OZEL_USER_KLASORLERI:
                yapı += f"{girinti}- **{base_name}/** (Kullanıcı Projeleri - İçerik Gizli)\n"
                dizinler[:] = [] # Altına inme
                continue 
            else:
                yapı += f"{girinti}- **{base_name}/**\n"

        girinti_dosya = "  " * (seviye + 1)
        
        # DOSYALARI LİSTELEME (Filtresiz)
        for dosya in sorted(dosyalar):
            # .git klasörü içindeki dosyaları hariç tut, gerisi gelsin
            if '.git' in yol_parcalari: continue
            
            yapı += f"{girinti_dosya}- {dosya}\n"
                    
    return yapı

def ana_fonksiyon():
    hedef_dizin = os.getcwd() 
    proje_adi = os.path.basename(hedef_dizin)
    
    dokum_metni = f"# 📝 Proje Dökümü: {proje_adi}\n\n"
    dokum_metni += f"Bu döküm, **{hedef_dizin}** dizini için oluşturulmuştur.\n"
    dokum_metni += "Not: `my_projects` klasörünün içeriği gizlilik gereği hariç tutulmuştur.\n\n"
    
    print(f"1/3: '{proje_adi}' klasör yapısı taranıyor...")
    dokum_metni += dizin_yapisi_getir(hedef_dizin)
    
    dokum_metni += "\n---\n"
    dokum_metni += "### 💻 Kod İçeriği Dökümü\n\n"
    
    print("2/3: Kod içerikleri toplanıyor...")
    
    dosya_sayisi = 0
    for kok, dizinler, dosyalar in os.walk(hedef_dizin):
        dizinler[:] = [d for d in dizinler if d.lower() not in DIKKATE_ALINMAYACAK_DIZINLER]
        
        if os.path.basename(kok) in OZEL_USER_KLASORLERI:
            dizinler[:] = []
            continue

        yol_parcalari = kok.lower().split(os.sep)
        if any(yasak in yol_parcalari for yasak in DIKKATE_ALINMAYACAK_DIZINLER): continue

        for dosya in sorted(dosyalar):
            dosya_yolu = os.path.join(kok, dosya)
            
            # KENDİSİNİ VE ÇIKTI DOSYASINI OKUMASIN (İçerik Dökümünde)
            if dosya == CIKTI_DOSYASI: continue
            
            uzanti = os.path.splitext(dosya)[1].lower()

            if uzanti in BELGELENECEK_KOD_UZANTILARI:
                goreli_yol = os.path.relpath(dosya_yolu, hedef_dizin)
                dokum_metni += f"\n#### 📄 Dosya: `{goreli_yol}`\n"
                dokum_metni += dosya_icerigini_getir(dosya_yolu)
                dosya_sayisi += 1
            
    print(f"3/3: '{CIKTI_DOSYASI}' dosyasına kayıt yapılıyor...")
    try:
        cikti_yolu = os.path.join(hedef_dizin, CIKTI_DOSYASI)
        with open(cikti_yolu, 'w', encoding='utf-8') as f:
            f.write(dokum_metni)
        print(f"\n✅ İşlem Başarılı! Toplam {dosya_sayisi} dosya belgelendi.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        
if __name__ == "__main__":
    ana_fonksiyon()
```

#### 📄 Dosya: `launcher.py`

```py
import os
import sys
import platform
import subprocess
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

# Renk kodları
GREEN = '\033[92m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RED = '\033[91m'
GREY = '\033[90m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

# Config'den proje klasörünü al
try:
    import config
    PROJECTS_ROOT = Path.cwd() / config.PROJECTS_DIR
except ImportError:
    # Config yoksa varsayılan
    PROJECTS_ROOT = Path.cwd() / "my_projects"

try:
    from core.memory import MemoryManager
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from core.memory import MemoryManager

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def ensure_workspace():
    """Çalışma alanı klasörünü oluşturur."""
    if not PROJECTS_ROOT.exists():
        os.makedirs(PROJECTS_ROOT)

def slugify(text):
    text = text.lower()
    text = text.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    text = re.sub(r'[^a-z0-9]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def get_projects():
    projects = []
    ensure_workspace()
    for entry in PROJECTS_ROOT.iterdir():
        if entry.is_dir() and (entry / ".coder_memory").exists():
            projects.append(entry)
    return projects

def get_project_stats(project_path: Path):
    stats_file = project_path / ".project_stats.json"
    total_cost = 0.0
    last_updated = "-"
    if stats_file.exists():
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_cost = data.get("total_cost", 0.0)
                last_updated = data.get("last_updated", "-")
        except: pass
    return total_cost, last_updated

def export_project(project_path: Path):
    """Projeyi taşınabilir ZIP formatına getirir."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    zip_name = f"{project_path.name}_BACKUP_{timestamp}"
    zip_path = PROJECTS_ROOT / zip_name
    
    print(f"\n{CYAN}📦 Proje paketleniyor: {project_path.name}...{RESET}")
    try:
        shutil.make_archive(str(zip_path), 'zip', project_path)
        print(f"{GREEN}✅ Yedek Oluşturuldu: {zip_path}.zip{RESET}")
        print(f"{GREY}   (Bu dosyayı USB'ye atıp başka bilgisayara taşıyabilirsiniz){RESET}")
        input(f"\nDevam etmek için Enter...")
    except Exception as e:
        print(f"{RED}Paketleme hatası: {e}{RESET}")
        input()

def create_new_project_wizard():
    print(f"\n{CYAN}✨ YENİ PROJE OLUŞTUR{RESET}")
    while True:
        p_name = input(f"{YELLOW}1. Proje Adı: {RESET}").strip()
        if p_name: break
    
    print(f"{CYAN}2. Açıklama{RESET}")
    p_desc = input(f"{YELLOW}   Detay: {RESET}").strip()
    if not p_desc: p_desc = f"{p_name} projesi."

    suggested_folder = slugify(p_name)
    p_folder = input(f"{YELLOW}3. Klasör Adı [{suggested_folder}]: {RESET}").strip()
    if not p_folder: p_folder = suggested_folder
        
    # ARTIK ANA DİZİNE DEĞİL, MY_PROJECTS ALTINA KURUYORUZ
    target_path = PROJECTS_ROOT / p_folder
    
    if target_path.exists():
        print(f"\n{RED}❌ Hata: Bu isimde bir proje zaten var!{RESET}")
        return None

    try:
        os.makedirs(target_path)
        print(f"{CYAN}🧠 Hafıza kuruluyor...{RESET}")
        memory = MemoryManager(project_root=str(target_path))
        
        readme_content = f"# {p_name}\n\n## Proje Hakkında\n{p_desc}\n\nBu proje Coder-Asistan ile oluşturuldu."
        with open(target_path / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
            
        memory.collection.upsert(
            documents=[f"PROJE TANIMI: {p_desc}"],
            embeddings=memory.embedder.encode([p_desc]).tolist(),
            metadatas=[{"source": "project_init"}],
            ids=["project_description"]
        )
        print(f"{GREEN}✅ Proje Hazır!{RESET}")
        return target_path
    except Exception as e:
        print(f"{RED}Hata: {e}{RESET}")
        return None

def print_chat_history(project_path: Path):
    log_file = project_path / ".chat_history.log"
    if log_file.exists():
        print(f"\n{GREY}📜 GEÇMİŞ KAYITLAR{RESET}")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                content = content.replace("👤 USER:", f"{YELLOW}👤 USER:{RESET}")
                content = content.replace("🤖 AI:", f"{GREEN}🤖 AI:{RESET}")
                content = content.replace("💰 MALİYET:", f"{MAGENTA}💰 MALİYET:{RESET}")
                print(content)
        except: pass
    else:
        print(f"\n{GREY}(Henüz geçmiş yok){RESET}")

def launch_assistant(project_path):
    clear_screen()
    total_cost, last_upd = get_project_stats(project_path)
    
    print(f"{GREEN}📂 PROJE: {project_path.name}{RESET}")
    print(f"{MAGENTA}💰 TOPLAM: ${total_cost:.5f}{RESET} {GREY}(Son: {last_upd}){RESET}")
    
    readme = project_path / "README.md"
    if readme.exists():
         with open(readme, 'r', encoding='utf-8') as f:
             print(f"{CYAN}ℹ️  {f.readline().strip().replace('# ', '')}{RESET}")

    print_chat_history(project_path)
    print(f"{CYAN}----------------------------------------{RESET}")
    print(f"{GREY}(Sohbet geçmişi yukarıda kalacaktır. Çıkış için 'b' yazın){RESET}\n")

    while True:
        task = input(f"{YELLOW}User (Siz) > {RESET}").strip()
        if task.lower() == 'b': return
        if not task: continue
            
        # Assistant scripti bir üst dizinde (ana kök dizinde)
        assistant_script = Path(__file__).parent / "assistant.py"
        cmd = [sys.executable, str(assistant_script), task]
        
        print(f"{CYAN}----------------------------------------{RESET}")
        try:
            subprocess.run(cmd, cwd=str(project_path))
            print(f"{CYAN}----------------------------------------{RESET}")
        except Exception as e:
            print(f"{RED}Hata: {e}{RESET}")

def main():
    ensure_workspace()
    
    while True:
        clear_screen()
        projects = get_projects()
        
        if not projects:
            create_new_project_wizard()
            continue

        print(f"{GREEN}╔══════════════════════════════════════════╗")
        print(f"║   🚀 CODER-ASISTAN (Projeler: {len(projects)})      ║")
        print(f"╚══════════════════════════════════════════╝{RESET}")
        
        for idx, proj in enumerate(projects, 1):
            cost, _ = get_project_stats(proj)
            print(f"[{idx}] {proj.name:<20} {MAGENTA}${cost:.4f}{RESET}")
            
        print(f"\n[{GREEN}N{RESET}] ✨ Yeni Proje")
        print(f"[{CYAN}E{RESET}] 📦 Projeyi Paketle (Zip/Yedek)")
        print(f"[{RED}Q{RESET}] 🚪 Çıkış")
        
        choice = input(f"\n{YELLOW}Seçim: {RESET}").strip().upper()
        
        if choice == 'Q': sys.exit()
        elif choice == 'N':
            new_proj = create_new_project_wizard()
            if new_proj: launch_assistant(new_proj)
        elif choice == 'E':
            try:
                p_idx = int(input("Paketlenecek proje numarası: "))
                if 1 <= p_idx <= len(projects):
                    export_project(projects[p_idx-1])
            except ValueError: pass
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(projects):
                launch_assistant(projects[idx-1])

if __name__ == "__main__":
    main()
```

#### 📄 Dosya: `migrate_projects.py`

```py
import os
import shutil
from pathlib import Path

# Hedef
TARGET_DIR = Path("my_projects")
if not TARGET_DIR.exists():
    os.makedirs(TARGET_DIR)

print("🚚 Proje Taşıma İşlemi Başlıyor...")

# Mevcut dizindeki klasörleri tara
for entry in Path.cwd().iterdir():
    # Kendi dizinimizdeki klasörler (my_projects hariç)
    if entry.is_dir() and entry.name != "my_projects" and entry.name != "core" and entry.name != "venv" and not entry.name.startswith("."):
        
        # Eğer içinde .coder_memory varsa bu bir projedir!
        if (entry / ".coder_memory").exists():
            print(f"📦 Bulundu ve Taşınıyor: {entry.name}")
            try:
                shutil.move(str(entry), str(TARGET_DIR / entry.name))
                print(f"   ✅ Taşındı.")
            except Exception as e:
                print(f"   ❌ Hata: {e}")

print("\n🏁 İşlem Tamam. Artık launcher.py'yi çalıştırabilirsiniz.")
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

#### 📄 Dosya: `readme.md`

```md
# 🚀 Coder-Asistan
### Hafızalı, Güvenli ve Proje Odaklı AI Kodlama Stüdyosu

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

**Coder-Asistan**, klasik "soru sor – cevap al" botlarından farklı olarak, projelerinizi yöneten, bağlamı hatırlayan ve kodu **kontrollü şekilde** değiştiren **terminal tabanlı bir AI geliştirme ortamıdır.**

Her proje için ayrı bir hafıza oluşturur (RAG). Bir projede öğrendiğini diğerine taşımaz. Ne yaptığını önce planlar, sonra siz onaylarsanız uygular.

> **Kısaca:** Bu bir bot değil, **AI destekli bir geliştirme çalışma alanı**.

---

## 🎯 Temel Özellikler

* **🏭 Proje Fabrikası (`launcher.py`):** Tüm projeleri tek merkezden yönetin.
* **🧠 İzole Hafıza:** Her projenin kendi `.coder_memory` klasörü vardır. AI, projenizdeki dosyaları okur ve hatırlar.
* **🛡️ Güvenli Mod:** Kodları doğrudan yazmaz; önce plan sunar, onaylarsanız işler.
* **💰 Maliyet Takibi:** Token başına harcamayı kuruşu kuruşuna raporlar.
* **🔌 Model Özgürlüğü:** Google Gemini, Llama 3 (Groq), DeepSeek veya Hugging Face.

---

## 📦 Kurulum (2 Dakikada Hazır)

### 1️⃣ Projeyi İndirin
```bash
git clone [https://github.com/cetincevizcetoli/coder-asistan.git](https://github.com/cetincevizcetoli/coder-asistan.git)
cd coder-asistan
```

### 2️⃣ Sanal Ortam Oluşturun (ÖNEMLİ)

**🪟 Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**🐧 Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```
*(Terminal satırının başında `(venv)` yazısını görmelisiniz.)*

### 3️⃣ Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

---

## 🔑 API Anahtarı Ayarları

Coder-Asistan bir beyne ihtiyaç duyar. **Google Gemini (Ücretsiz)** önerilir.

1. [Google AI Studio](https://aistudio.google.com/app/apikey) adresinden Key alın.
2. Bilgisayarınıza kaydedin:

**🪟 Windows (Kalıcı):**
```cmd
setx GOOGLE_API_KEY "API_KEY_BURAYA_YAPISTIR"
```
*(Komuttan sonra terminali kapatıp yeniden açın!)*

**🐧 Linux / macOS:**
```bash
echo 'export GOOGLE_API_KEY="API_KEY_BURAYA"' >> ~/.bashrc
source ~/.bashrc
```

---

## ▶️ Nasıl Kullanılır? (Ana Kumanda)

Tüm sistemi yönetmek için tek bir komut yeterlidir:

```bash
python launcher.py
```

Karşınıza gelen menüden:
* **[N]** ile yeni proje oluşturabilir,
* **[1-9]** ile mevcut projelerinize girip AI ile çalışmaya başlayabilirsiniz.
* **[E]** ile projelerinizi ZIP olarak yedekleyebilirsiniz.

---

## 🛠️ İsviçre Çakısı: Yardımcı Araçlar

Bu projede sadece kod yazan bir asistan yok, işinizi kolaylaştıracak bir dizi **profesyonel araç** bulunur. İşte alet çantanız:

### 1. 🕵️‍♂️ Hafıza Müfettişi (`debug.py`)
AI'nın projeniz hakkında ne bildiğini merak mı ediyorsunuz? Vektör veritabanının içine girip kaydedilen kod parçalarını okumanızı sağlar.
```bash
python debug.py
```
* **Ne zaman kullanılır?** AI, kodunuzu hatırlamıyorsa veya yanlış cevap veriyorsa hafızayı kontrol etmek için.

### 2. 🚚 Proje Nakliyecisi (`migrate_projects.py`)
Eski sürümden kalma veya yanlışlıkla ana dizine kopyaladığınız projeleri bulur ve otomatik olarak yeni sisteme (`my_projects` klasörüne) taşır.
```bash
python migrate_projects.py
```
* **Ne zaman kullanılır?** Klasörde projeniz var ama Launcher listesinde görünmüyorsa.

### 3. 🩺 Sistem Doktoru (`system_audit.py`)
Projelerinizin sağlık kontrolünü yapar. Log dosyaları dolu mu? Veritabanı bütünlüğü (integrity) sağlam mı? Hepsini raporlar.
```bash
python system_audit.py
```
* **Ne zaman kullanılır?** Sistemsel bir hatadan şüpheleniyorsanız veya veritabanı bozulduysa.

### 4. 📝 Proje Katibi (`generate_docs.py`)
Tüm projenizin kodlarını okur ve tek bir Markdown dosyasında (`proje_dokumu.md`) birleştirir.
```bash
python generate_docs.py
```
* **Ne zaman kullanılır?** Projenin tamamını ChatGPT/Claude gibi başka bir AI'ya atıp "Bunu analiz et" demek istediğinizde.

### 5. 📡 Model Kontrolcüsü (`check_models.py`)
Google hesabınızda tanımlı ve erişilebilir olan Gemini modellerini listeler.
```bash
python check_models.py
```
* **Ne zaman kullanılır?** "Hangi modelleri kullanabilirim?" diye merak ettiğinizde.

---

## 🧪 Gelişmiş Parametreler

Projeye girdikten sonra (veya `assistant.py`'yi manuel kullanırken) şu modları kullanabilirsiniz:

* **`--dry-run` (Prova Modu):**
  AI kodları yazar, planı gösterir ama **dosyaya kaydetmez.**
  ```bash
  python assistant.py "Ana sayfayı değiştir" --dry-run
  ```

* **`--verbose` (Geveze Mod):**
  Arka planda dönen ham JSON verisini ve düşünce sürecini gösterir. Hata ayıklamak için idealdir.
  ```bash
  python assistant.py "Hata bul" --verbose
  ```

---

## 🏗️ Proje Mimarisi

```text
coder-asistan/
├─ launcher.py          # 🎮 ANA KUMANDA (Başlatıcı)
├─ assistant.py         # 🧠 İşlem Motoru
├─ my_projects/         # 📂 PROJE FABRİKASI
│  └─ odev-1/           # 🔒 İzole Proje Alanı
│     ├─ .coder_memory/ # 🧠 Projeye özel hafıza
│     └─ src/           # Kodlarınız
├─ debug.py             # 🕵️‍♂️ Hafıza Müfettişi
├─ system_audit.py      # 🩺 Sistem Doktoru
├─ migrate_projects.py  # 🚚 Taşıyıcı
└─ requirements.txt
```

---

## 💡 İpuçları ve Püf Noktaları

* **🗑️ Proje Silme:** Bir projeyi silmek için Launcher'da bir komut yoktur. `my_projects` klasörüne gidip ilgili proje klasörünü **elle silmeniz** yeterlidir.
* **🧠 Hafıza Sıfırlama:** AI eski kodları hatırlamakta ısrar ediyorsa veya kafası karıştıysa; proje klasörünüzdeki `.coder_memory` klasörünü silin. Coder-Asistan bir sonraki açılışta dosyaları tarayıp hafızayı sıfırdan kuracaktır.
* **⚙️ İnce Ayarlar:** Dosya boyutu sınırlarını veya maliyet hesaplama yöntemini değiştirmek isterseniz `config.py` dosyasını düzenleyebilirsiniz.

---
## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir! Büyük değişiklikler için önce bir Issue açarak tartışalım.

> 🏗️ **Geliştirici Notu:** Bu projenin iç yapısını, veri akışını ve teknik detaylarını derinlemesine incelemek için lütfen **[MİMARİ VE TEKNİK KILAVUZ (ARCHITECTURE.md)](ARCHITECTURE.md)** dosyasını okuyunuz.
---
## 👤 Geliştirici

**Ahmet Çetin**
* **GitHub:** [github.com/cetincevizcetoli](https://github.com/cetincevizcetoli)
* **Web:** [yapanzeka.acetin.com.tr](https://yapanzeka.acetin.com.tr)

> *"Karmaşık kodları, kontrollü araçlarla yönetin."*
```

#### 📄 Dosya: `requirements.txt`

```txt
google-genai
requests
# --- RAG ve Hafıza ---
chromadb>=0.4.0
sentence-transformers>=2.2.0
torch>=2.0.0
# --- Yardımcılar ---
tqdm  # İndeksleme sırasında progress bar için (opsiyonel ama iyi pratik)
```

#### 📄 Dosya: `system_audit.py`

```py
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

#### 📄 Dosya: `core\deepseek.py`

```py
# core/deepseek.py
import os
import requests
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class DeepSeekModel(BaseModel):
    """DeepSeek API - Ücretsiz ve güçlü"""
    
    def __init__(self):
        conf = MODEL_CONFIGS["deepseek"]
        self.MODEL_NAME = conf["display_name"]
        
        self.api_key = os.getenv(conf["env_var"])
        if not self.api_key:
            raise ModelAPIError(f"{conf['env_var']} ortam değişkeni bulunamadı.")
        
        # DeepSeek OpenAI uyumlu API uç noktası
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
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
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Debug için
            if hasattr(self, 'DEBUG') and self.DEBUG:
                print(f"DEBUG DeepSeek Response: {result}")
                
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            # Hata mesajını daha detaylı görmek için
            if hasattr(e, 'response') and e.response is not None:
                error_msg = e.response.text
                print(f"DEBUG DeepSeek Error: {error_msg}")
                try:
                    error_json = json.loads(error_msg)
                    raise ModelAPIError(f"DeepSeek Hatası: {error_json.get('message', str(e))}")
                except:
                    raise ModelAPIError(f"DeepSeek API Hatası: {e}")
            else:
                raise ModelAPIError(f"DeepSeek Bağlantı Hatası: {e}")
        except Exception as e:
            raise ModelAPIError(f"DeepSeek İşlem Hatası: {e}")
```

#### 📄 Dosya: `core\gemini.py`

```py
import os
from google import genai
from google.genai import types
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class GeminiModel(BaseModel):
    def __init__(self):
        conf = MODEL_CONFIGS["gemini"]
        self.MODEL_NAME = conf["display_name"]
        self.raw_model_name = conf["model_name"] # Fiyat hesaplaması için
        
        api_key = os.getenv(conf["env_var"])
        if not api_key:
            raise ModelAPIError(f"{conf['env_var']} bulunamadı.")

        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise ModelAPIError(f"Gemini Client Başlatılamadı: {e}")

    def generate_content(self, system_instruction, prompt_text):
        try:
            response = self.client.models.generate_content(
                model=self.raw_model_name,
                contents=[prompt_text],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            
            # Token kullanımını güvenli şekilde al
            usage = {
                "input_tokens": 0,
                "output_tokens": 0
            }
            
            if hasattr(response, 'usage_metadata'):
                usage["input_tokens"] = response.usage_metadata.prompt_token_count
                usage["output_tokens"] = response.usage_metadata.candidates_token_count

            return {
                "content": response.text.strip(),
                "usage": usage,
                "model_key": self.raw_model_name
            }

        except Exception as e:
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

#### 📄 Dosya: `core\memory.py`

```py
import os
import shutil
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import torch
import config
from config import Colors

class MemoryManager:
    def __init__(self, project_root: str):
        """
        Belirtilen proje dizini için izole hafıza yöneticisi.
        """
        self.project_root = project_root
        self.memory_path = os.path.join(project_root, config.MEMORY_DIR_NAME)
        
        # 1. Donanım Algılama ve Embedding Modelini Yükleme
        self.device = self._detect_device()
        print(f"{Colors.MAGENTA}🧠 Hafıza Motoru Başlatılıyor... ({self.device}){Colors.RESET}")
        
        try:
            self.embedder = SentenceTransformer(config.EMBEDDING_MODEL, device=self.device)
        except Exception as e:
            print(f"{Colors.RED}Model yükleme hatası, CPU'ya geçiliyor: {e}{Colors.RESET}")
            self.embedder = SentenceTransformer(config.EMBEDDING_MODEL, device="cpu")

        # 2. ChromaDB İstemcisini Başlatma (Persistent)
        os.makedirs(self.memory_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.memory_path)
        
        # Koleksiyonu al veya oluştur
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"} # Kod benzerliği için kosinüs idealdir
        )

    def _detect_device(self) -> str:
        """Sistemi tarar: NVIDIA GPU -> Apple Silicon (MPS) -> CPU"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def index_files(self, file_paths: list):
        """Dosyaları okur, vektörleştirir ve veritabanına kaydeder."""
        documents = []
        metadatas = []
        ids = []

        print(f"{Colors.CYAN}📥 {len(file_paths)} dosya indeksleniyor...{Colors.RESET}")

        for fpath in file_paths:
            full_path = os.path.join(self.project_root, fpath)
            if not os.path.exists(full_path):
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basit chunking: Dosyayı olduğu gibi alıyoruz (küçük dosyalar için)
                # Büyük projelerde buraya "TextSplitter" eklenmeli.
                if len(content.strip()) == 0: continue

                documents.append(content)
                metadatas.append({"source": fpath})
                ids.append(fpath) # ID olarak dosya yolu benzersizdir

            except Exception as e:
                print(f"{Colors.YELLOW}Uyarı: {fpath} okunamadı ({e}){Colors.RESET}")

        if documents:
            # Embedding işlemini manuel yapıp Chroma'ya veriyoruz (Daha fazla kontrol için)
            embeddings = self.embedder.encode(documents, normalize_embeddings=True).tolist()
            
            # Upsert: Varsa güncelle, yoksa ekle
            self.collection.upsert(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"{Colors.GREEN}✅ Hafıza güncellendi.{Colors.RESET}")

    def query(self, prompt: str, n_results=config.MAX_CONTEXT_RESULTS):
        """Prompt ile alakalı kod parçalarını getirir."""
        query_embedding = self.embedder.encode([prompt], normalize_embeddings=True).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        context_parts = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                source = results['metadatas'][0][i]['source']
                context_parts.append(f"--- BAĞLAM: {source} ---\n{doc}\n")
        
        return "\n".join(context_parts)

    def clear_memory(self):
        """Hafızayı sıfırlar."""
        self.client.delete_collection(config.COLLECTION_NAME)
        shutil.rmtree(self.memory_path)
        print(f"{Colors.YELLOW}🧹 Hafıza temizlendi.{Colors.RESET}")
```
