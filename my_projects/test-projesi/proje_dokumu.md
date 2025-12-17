# 📝 Proje Dökümü: coder-asistan

Bu döküm, **/home/ahmetc/proje/coder-asistan** dizini için oluşturulmuştur.
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
  - settings_menu.py
  - system_audit.py
  - user_settings.json
  - **temp_install_dir/**
  - **core/**
    - base.py
    - deepseek.py
    - gemini.py
    - groq.py
    - huggingface.py
    - memory.py
    - orchestrator.py
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
import difflib
import time
from datetime import datetime
from typing import List, Optional, Any, Tuple, Dict

# --- PROJE MODÜLLERİ ---
try:
    import config
    from config import Colors, PRICING_RATES
    from core.memory import MemoryManager
    from core.gemini import GeminiModel 
    from core.orchestrator import AgentOrchestrator
except ImportError:
    print("⚠️  Kritik modüller yüklenemedi. Lütfen kütüphanelerin yüklü olduğundan emin olun.")

# --- SABİTLER ---
FILE_PATTERN = re.compile(r"[\w-]+\.(py|js|html|css|md|json|txt|java|cpp|h|ts|jsx|tsx|sh|env|sql|xml|yaml)", re.IGNORECASE)

# ==========================================
# 🛠️ YARDIMCI FONKSİYONLAR
# ==========================================

def is_safe_path(file_path: str, current_directory: str) -> bool:
    try:
        if os.path.isabs(file_path): return False
        if '..' in file_path: return False
        target_path = os.path.abspath(os.path.join(current_directory, file_path))
        safe_root = os.path.abspath(current_directory)
        return target_path.startswith(safe_root)
    except: return False

def show_diff(file_path: str, old_content: str, new_content: str):
    """Dosyadaki değişiklikleri terminalde görsel olarak gösterir."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}🔍 DEĞİŞİKLİK ÖZETİ ({file_path}):{Colors.RESET}")
    
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(old_lines, new_lines, fromfile='Eski', tofile='Yeni', n=0)
    
    has_changes = False
    for line in diff:
        has_changes = True
        if line.startswith('+') and not line.startswith('+++'):
            print(f"{Colors.GREEN}{line.strip()}{Colors.RESET}")
        elif line.startswith('-') and not line.startswith('---'):
            print(f"{Colors.RED}{line.strip()}{Colors.RESET}")
        elif line.startswith('@@'):
            print(f"{Colors.MAGENTA}{line.strip()}{Colors.RESET}")
            
    if not has_changes:
        print(f"{Colors.GREY}Değişiklik tespit edilmedi (içerik aynı).{Colors.RESET}")    

def clean_json_string(json_string: str) -> Optional[Dict]:
    if isinstance(json_string, dict): return json_string
    try:
        if "```" in json_string:
            lines = json_string.split('\n')
            clean_lines = []
            capture = False
            for line in lines:
                if "```" in line:
                    capture = not capture
                    continue
                if capture:
                    clean_lines.append(line)
            json_string = "\n".join(clean_lines) if clean_lines else json_string.replace("```json", "").replace("```", "")

        json_string = json_string.strip()
        if json_string.rfind('}') != -1:
            json_string = json_string[:json_string.rfind('}')+1]
        
        return json.loads(json_string)
    except Exception:
        return None

def backup_file(full_path: str) -> Optional[str]:
    if not os.path.exists(full_path): return None
    os.makedirs(config.BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{os.path.basename(full_path)}.{timestamp}.backup"
    shutil.copy(full_path, os.path.join(config.BACKUP_DIR, backup_name))
    return backup_name

def log_conversation(working_dir: str, user_prompt: str, ai_explanation: str, model_name: str, cost: float = 0.0):
    log_file = os.path.join(working_dir, ".chat_history.log")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    log_entry = (
        f"{'═'*60}\n📅 ZAMAN: {timestamp} | 🤖 MODEL: {model_name}\n"
        f"💰 MALİYET: ${cost:.5f}\n👤 USER: {user_prompt}\n🤖 AI:   {ai_explanation}\n"
    )
    try:
        with open(log_file, "a", encoding="utf-8") as f: f.write(log_entry)
    except: pass

def update_project_stats(working_dir: str, usage_data: dict, model_key: str) -> Tuple[float, float]:
    stats_file = os.path.join(working_dir, ".project_stats.json")
    stats = {"total_cost": 0.0, "total_input_tokens": 0, "total_output_tokens": 0, "last_updated": ""}
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f: stats = json.load(f)
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
        with open(stats_file, 'w', encoding='utf-8') as f: json.dump(stats, f, indent=4)
    except: pass
    return current_cost, stats["total_cost"]

# ==========================================
# 🚀 ANA İŞLEM MOTORU (AGENTIC)
# ==========================================

def process_single_turn(prompt_text: str, orchestrator: AgentOrchestrator, working_dir: str, memory: Any, is_dry_run: bool = False):
    """Hibrit RAG bağlamı ile isteği akıllıca yönlendirir."""
    
    # 1. HİBRİT HAFIZA SORGUSU (Bağlamı her durumda alıyoruz)
    rag_context = ""
    if memory:
        print(f"{Colors.CYAN}🔍 Hibrit Hafıza taranıyor...{Colors.RESET}")
        rag_context = memory.query(prompt_text, n_results=config.MAX_CONTEXT_RESULTS)
        if len(rag_context) > config.MAX_CONTEXT_CHARS:
            rag_context = rag_context[:config.MAX_CONTEXT_CHARS] + "\n...(Kırpıldı)..."

    # --- 🛡️ 1. GÜNCELLENMİŞ SİSTEMSEL KOMUT FİLTRESİ (KISA DEVRE) ---
    sorgu_temiz = prompt_text.lower().strip()
    sistem_komutlari = ["tara", "indeksle", "hafızayı güncelle", "yenile", "reindex"]
    aksiyon_kelimeleri = ["yerine", "yap", "değiştir", "ekle", "düzelt", "sil"]
    
    # Sadece sistemle ilgiliyse ve değişiklik/aksiyon içermiyorsa kısa devre yap
    if any(k in sorgu_temiz for k in sistem_komutlari) and not any(x in sorgu_temiz for x in aksiyon_kelimeleri):
        print(f"{Colors.GREEN}⚙️  Sistem işlemi algılandı, dosyalar taranıyor...{Colors.RESET}")
        if memory:
            files = [f for f in os.listdir(working_dir) if FILE_PATTERN.match(f)]
            memory.index_files(files)
            print(f"{Colors.GREEN}✅ Hafıza güncellendi. Artık sorularınızı sorabilirsiniz.{Colors.RESET}")
            return 

    # --- 🛡️ 2. FİLTRE: BİLGİ SORGUSU / SORU MODU ---
    soru_kelimeleri = ["nedir", "kaç", "nasıl", "kim", "nerede", "neden", "bilgi ver", "anlat", "?"]
    is_question = any(q in sorgu_temiz for q in soru_kelimeleri)

    if is_question and not any(x in sorgu_temiz for x in aksiyon_kelimeleri):
        print(f"{Colors.MAGENTA}ℹ️  Soru algılandı, doğrudan yanıtlanıyor...{Colors.RESET}")
        try:
            raw_res = orchestrator.developer.generate_content(
                "Sen bilgili bir yazılım asistanısın. SADECE kullanıcıya bilgi ver. Kod yazma, dosya değiştirme planı yapma.",
                f"HAFIZADAN GELEN BİLGİLER:\n{rag_context}\n\nKULLANICI SORUSU: {prompt_text}"
            )
            content = raw_res["content"] if isinstance(raw_res, dict) else str(raw_res)
            print(f"\n{Colors.MAGENTA}🤖 CEVAP:{Colors.RESET} {Colors.CYAN}{content}{Colors.RESET}")
            
            if isinstance(raw_res, dict):
                current_cost, total_cost = update_project_stats(working_dir, raw_res.get("usage", {}), raw_res.get("model_key", ""))
                print(f"{Colors.GREY}📊 Maliyet: ${current_cost:.5f}{Colors.RESET}")
            return
        except Exception as e:
            print(f"{Colors.RED}Soru yanıtlanırken hata oluştu: {e}{Colors.RESET}")
            return

    # --- 3. NORMAL AKIŞ: ORCHESTRATOR (MİMAR + MÜHENDİS) ---
    raw_response = orchestrator.execute_workflow(prompt_text, rag_context, working_dir)
    
    if not raw_response:
        print(f"{Colors.YELLOW}⚠️ İşlem durduruldu veya iptal edildi.{Colors.RESET}")
        return

    # 4. YANIT ANALİZİ
    if isinstance(raw_response, dict):
        content = raw_response.get("content", "")
        usage = raw_response.get("usage", {})
        model_key = raw_response.get("model_key", "unknown")
    else:
        content = raw_response
        usage = {}
        model_key = "unknown"

    ai_response_plan = clean_json_string(content)
    
    if ai_response_plan is None:
        print(f"{Colors.RED}❌ Mühendis yanıtı JSON formatında değil. İşlem iptal edildi.{Colors.RESET}")
        return

    # İstatistik ve Maliyet
    current_cost, total_cost = update_project_stats(working_dir, usage, model_key)
    print(f"\n{Colors.GREY}📊 İşlem Maliyeti: {Colors.GREEN}${current_cost:.5f}{Colors.RESET} (Proje Toplamı: ${total_cost:.5f})")

    # 5. UYGULAMA (Dosya İşlemleri)
    explanation = ai_response_plan.get("aciklama", "İşlem tamamlandı.")
    files_create = ai_response_plan.get("dosya_olustur", {})
    files_delete = ai_response_plan.get("dosya_sil", [])

    print(f"\n{Colors.MAGENTA}🤖 SONUÇ:{Colors.RESET} {Colors.CYAN}{explanation}{Colors.RESET}")
    
    if is_dry_run: return

    # Silme
    for p in files_delete:
        if is_safe_path(p, working_dir):
            full = os.path.join(working_dir, p)
            if os.path.exists(full):
                backup_file(full); os.remove(full)
                print(f"{Colors.RED}🗑️ Silindi: {p}{Colors.RESET}")

    # Yazma
    new_files = []
    # ... (Dosya Yazma Döngüsü İçinde) ...
    for p, content in files_create.items():
        if is_safe_path(p, working_dir):
            full = os.path.join(working_dir, p)
            try:
                os.makedirs(os.path.dirname(full), exist_ok=True)
                
                # Özet Gösterimi:
                old_text = ""
                if os.path.exists(full):
                    with open(full, 'r', encoding='utf-8') as f:
                        old_text = f.read()
                
                # Değişiklikleri ekrana bas
                show_diff(p, old_text, content)
                
                # Kayıt İşlemi
                if os.path.exists(full): backup_file(full)
                with open(full, 'w', encoding='utf-8') as f: f.write(content)
                print(f"{Colors.GREEN}💾 Yazıldı ve Hafızaya Alındı: {p}{Colors.RESET}")
                new_files.append(p)
            except Exception as e:
                 print(f"{Colors.RED}Dosya hatası ({p}): {e}{Colors.RESET}")

    # Hafızayı Güncelle (Yeni yazılan dosyaları otomatik indeksle)
    if memory and new_files:
        memory.index_files(new_files)

    log_conversation(working_dir, prompt_text, explanation, "Agent-Workflow", current_cost)

# ==========================================
# 🌟 PROJE ANA DÖNGÜSÜ
# ==========================================

def main(project_name):
    project_path = os.path.abspath(os.path.join(config.PROJECTS_DIR, project_name))
    
    if not os.path.exists(project_path):
        print(f"{Colors.RED}Hata: {project_path} yolu mevcut değil.{Colors.RESET}")
        return

    print(f"\n{Colors.GREEN}🚀 OTURUM BAŞLATILDI: {project_name.upper()}{Colors.RESET}")

    try:
        orchestrator = AgentOrchestrator()
        memory = MemoryManager(project_root=project_path)
    except Exception as e:
        print(f"{Colors.RED}Başlatma hatası: {e}{Colors.RESET}")
        return

    print(f"{Colors.CYAN}{'━'*50}{Colors.RESET}")
    print(f"Sohbet Aktif. 'q': çıkış | 'b': ana menü")
    
    while True:
        try:
            user_input = input(f"{Colors.BOLD}{Colors.YELLOW}({project_name}) > {Colors.RESET}").strip()
            
            if user_input.lower() in ['exit', 'q', 'quit', 'b']:
                break
            
            if not user_input: continue
            
            process_single_turn(user_input, orchestrator, project_path, memory)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"{Colors.RED}Beklenmedik Hata: {e}{Colors.RESET}")

if __name__ == "__main__":
    print("Lütfen 'launcher.py' kullanın.")
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
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
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
ACTIVE_PROFILE = 'gemini'
# ==========================================
# 🚀 AKTİF PROFİL SEÇİMİ (Eksik Olan Kısım)
# ==========================================
# Buraya MODEL_CONFIGS içindeki anahtarlardan birini yazmalısın:
# Seçenekler: 'gemini', 'groq', 'deepseek', 'huggingface'


# ==========================================
# 🧠 YENİ AI SİSTEM TALİMATI (Akıllı JSON Modu)
# ==========================================
# config.py içindeki SYSTEM_INSTRUCTION kısmını şununla değiştirin veya ekleyin:

# MİMAR İÇİN (Groq)
ARCHITECT_INSTRUCTION = (
    "Sen uzman bir yazılım mimarısın. Görevin, kullanıcı isteğini analiz etmek ve bir uygulama planı çıkarmaktır.\n"
    "KURALLAR:\n"
    "1. Kod yazma, sadece hangi dosyaların neden değişmesi gerektiğini açıkla.\n"
    "2. Yanıtın şu JSON formatında olmalı:\n"
    "{\n"
    "  'plan': 'Adım adım yapılacak işlemler listesi',\n"
    "  'etkilenecek_dosyalar': ['dosya1.py', 'dosya2.py']\n"
    "}"
)

# MÜHENDİS İÇİN (Gemini)
DEVELOPER_INSTRUCTION = (
    "Sen uzman bir yazılım geliştiricisin. Mimarın sunduğu plana göre kodları yazmalısın.\n"
    "KURALLAR:\n"
    "1. Sadece geçerli bir JSON objesi döndür.\n"
    "2. Format:\n"
    "{\n"
    "  'aciklama': 'Yapılan işlemin özeti',\n"
    "  'dosya_olustur': {'yol': 'icerik'},\n"
    "  'dosya_sil': []\n"
    "}"
)

# ==========================================
# 🧠 HAFIZA PROFİLLERİ (Menüde Görünecekler)
# ==========================================
MEMORY_PROFILES = {
    "1": {
        "model_name": "all-MiniLM-L6-v2",
        "display": "Hafif (Light)",
        "desc": "🚀 En Hızlısı | Düşük RAM | 384 Boyut | Genel projeler için ideal.",
        "dim": 384
    },
    "2": {
        "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
        "display": "Dengeli (Medium)",
        "desc": "⚖️  Daha İyi Türkçe | Orta Hız | 384 Boyut | Karmaşık metinler için.",
        "dim": 384
    },
    "3": {
        "model_name": "all-mpnet-base-v2",
        "display": "Güçlü (Heavy)",
        "desc": "🧠 En Yüksek Doğruluk | Yavaş | 768 Boyut | Akademik/Derin analiz için.",
        "dim": 768
    }
}
# ==========================================
# 🚀 AKTİF MODEL VE HAFIZA SEÇİMİ
# ==========================================
# Seçenekler: 'gemini', 'groq', 'deepseek', 'huggingface'
ACTIVE_MODEL = "gemini" 

# Hafıza Ayarı
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

```

#### 📄 Dosya: `debug.py`

```py
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
import json
import time
import datetime
import importlib

try:
    import config
except ImportError:
    print("HATA: config.py bulunamadı!")
    sys.exit(1)

# ==========================================
# AYAR SEÇENEKLERİ
# ==========================================
MEMORY_OPTIONS = {
    "1": {"id": "all-MiniLM-L6-v2", "name": "Hafif (Light)", "desc": "🚀 Hızlı"},
    "2": {"id": "paraphrase-multilingual-MiniLM-L12-v2", "name": "Dengeli (Medium)", "desc": "⚖️ Türkçe"},
    "3": {"id": "all-mpnet-base-v2", "name": "Güçlü (Heavy)", "desc": "🧠 Detaylı"}
}

MODEL_OPTIONS = {
    "1": {"id": "gemini", "name": "Google Gemini", "desc": "⚡ Dengeli ve Ücretsiz"},
    "2": {"id": "groq", "name": "Groq (Llama 3)", "desc": "🚀 Işık Hızında"},
    "3": {"id": "deepseek", "name": "DeepSeek Chat", "desc": "👨‍💻 Kodlama Uzmanı"},
    "4": {"id": "huggingface", "name": "Hugging Face", "desc": "🤗 Açık Kaynak Modeller"}
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def update_config_file(variable_name, new_value):
    try:
        with open("config.py", "r", encoding="utf-8") as f: lines = f.readlines()
        with open("config.py", "w", encoding="utf-8") as f:
            found = False
            for line in lines:
                if line.strip().startswith(variable_name):
                    f.write(f'{variable_name} = "{new_value}"\n'); found = True
                else: f.write(line)
            if not found: f.write(f'\n{variable_name} = "{new_value}"\n')
        return True
    except: return False

def load_projects():
    projects = []
    if not os.path.exists(config.PROJECTS_DIR):
        try: os.makedirs(config.PROJECTS_DIR)
        except: pass
    try: items = os.listdir(config.PROJECTS_DIR)
    except: items = []
    for item in items:
        path = os.path.join(config.PROJECTS_DIR, item)
        if os.path.isdir(path):
            meta_path = os.path.join(path, "metadata.json")
            embedding_model = "BİLİNMİYOR"
            cost = 0.0
            last_date = "0"
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r') as f:
                        data = json.load(f)
                        embedding_model = data.get("embedding_model", "Eski")
                        cost = data.get("total_cost", 0.0)
                        last_date = data.get("last_interaction", "0")
                except: pass
            projects.append({"name": item, "embedding_model": embedding_model, "cost": cost, "last_date": last_date})
    return sorted(projects, key=lambda x: x['last_date'], reverse=True)

def create_new_project():
    print(f"\n{config.Colors.CYAN}✨ Yeni Proje{config.Colors.RESET}")
    name = input("Proje İsmi: ").strip()
    if not name: return
    path = os.path.join(config.PROJECTS_DIR, name)
    if os.path.exists(path): print("Zaten var!"); time.sleep(1); return
    try:
        os.makedirs(path)
        metadata = {
            "created_at": str(datetime.datetime.now()),
            "embedding_model": config.EMBEDDING_MODEL,
            "total_cost": 0.0,
            "last_interaction": str(datetime.datetime.now())
        }
        with open(os.path.join(path, "metadata.json"), 'w') as f: json.dump(metadata, f, indent=4)
        start_project(name, config.EMBEDDING_MODEL)
    except Exception as e: print(f"Hata: {e}"); input("Enter...")

def start_project(name, project_embed_model):
    if project_embed_model != config.EMBEDDING_MODEL:
        print(f"\n{config.Colors.RED}⛔ UYUMSUZLUK: Bu proje '{project_embed_model}' kullanıyor.{config.Colors.RESET}")
        print("Ayarlardan hafıza modelini değiştirmeniz gerek."); input("Enter..."); return

    print(f"\n{config.Colors.GREEN}🚀 Sistem Başlatılıyor...{config.Colors.RESET}")
    try:
        # Kodun en başına import assistant eklemek yerine burada dene
        import assistant
        importlib.reload(assistant)
        assistant.main(name) 
    except Exception as e:
        # Hata olduğunda ekranın temizlenmesini engellemek için:
        print(f"\n{config.Colors.RED}❌ KRİTİK HATA OLUŞTU:{config.Colors.RESET}")
        import traceback
        traceback.print_exc() # Hatanın tam yerini ve nedenini yazar
        input(f"\n{config.Colors.YELLOW}Devam etmek için Enter'a basın (Hata kaybolmadan okuyun)...{config.Colors.RESET}")

def settings_menu():
    while True:
        clear_screen()
        print(f"{config.Colors.YELLOW}=== AYARLAR ==={config.Colors.RESET}")
        print(f"1. Yapay Zeka Modeli : {config.Colors.GREEN}{config.ACTIVE_MODEL.upper()}{config.Colors.RESET}")
        print(f"2. Hafıza (RAG) Tipi : {config.Colors.CYAN}{config.EMBEDDING_MODEL}{config.Colors.RESET}")
        print("-" * 50)
        print("[M] Model Değiştir")
        print("[H] Hafıza Değiştir")
        print("[X] Geri Dön")
        
        sel = input("\nSeçim: ").strip().upper()
        
        if sel == 'X': break
        
        elif sel == 'M':
            print(f"\n{config.Colors.BLUE}--- MODEL SEÇİMİ ---{config.Colors.RESET}")
            for k, v in MODEL_OPTIONS.items():
                mark = " (AKTİF)" if v['id'] == config.ACTIVE_MODEL else ""
                print(f"[{k}] {v['name']}{mark} - {v['desc']}")
            m_sel = input("Seçim: ").strip()
            if m_sel in MODEL_OPTIONS:
                new_val = MODEL_OPTIONS[m_sel]['id']
                update_config_file("ACTIVE_MODEL", new_val)
                print("♻️  Kaydedildi, yeniden başlatılıyor..."); time.sleep(1)
                os.execv(sys.executable, ['python'] + sys.argv)

        elif sel == 'H':
            print(f"\n{config.Colors.BLUE}--- HAFIZA SEÇİMİ ---{config.Colors.RESET}")
            for k, v in MEMORY_OPTIONS.items():
                mark = " (AKTİF)" if v['id'] == config.EMBEDDING_MODEL else ""
                print(f"[{k}] {v['name']}{mark} - {v['desc']}")
            h_sel = input("Seçim: ").strip()
            if h_sel in MEMORY_OPTIONS:
                new_val = MEMORY_OPTIONS[h_sel]['id']
                update_config_file("EMBEDDING_MODEL", new_val)
                print("♻️  Kaydedildi, yeniden başlatılıyor..."); time.sleep(1)
                os.execv(sys.executable, ['python'] + sys.argv)

def main():
    while True:
        clear_screen()
        importlib.reload(config)
        projects = load_projects()
        
        print(f"{config.Colors.BOLD}{config.Colors.BLUE}=== AI ASİSTAN (v2.4) ==={config.Colors.RESET}")
        print(f"🤖 Model : {config.Colors.GREEN}{config.ACTIVE_MODEL.upper()}{config.Colors.RESET}")
        print(f"🧠 Hafıza: {config.Colors.YELLOW}{config.EMBEDDING_MODEL}{config.Colors.RESET}")
        print("-" * 60)
        
        for idx, p in enumerate(projects, 1):
            status = "✅" if p['embedding_model'] == config.EMBEDDING_MODEL else "⛔"
            print(f"[{idx}] {p['name']:<15} {status} ({p['embedding_model']})")
            
        print("-" * 60)
        print("[N] Yeni Proje  |  [S] Ayarlar  |  [Q] Çıkış")
        ch = input("> ").strip().upper()
        
        if ch == 'Q': sys.exit()
        elif ch == 'N': create_new_project()
        elif ch == 'S': settings_menu()
        elif ch.isdigit():
            idx = int(ch) - 1
            if 0 <= idx < len(projects): start_project(projects[idx]['name'], projects[idx]['embedding_model'])

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
openai
chromadb>=0.4.0
sentence-transformers>=2.2.0
torch>=2.0.0
rank_bm25  # <--- Hibrit (Keyword) arama motoru için yeni eklendi
termcolor
tqdm

```

#### 📄 Dosya: `settings_menu.py`

```py
import os
import json
import time

# Renkler
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

SETTINGS_FILE = "user_settings.json"

# Hafıza Profilleri
PROFILES = {
    'light':  {'name': 'Hafif (Light)',  'size': '80 MB',  'desc': '🚀 Çok Hızlı, Düşük RAM (Z570 İçin Önerilen)'},
    'medium': {'name': 'Orta (Medium)',  'size': '470 MB', 'desc': '⚖️ Daha İyi Türkçe, Dengeli Hız'},
    'heavy':  {'name': 'Ağır (Heavy)',   'size': '2.2 GB', 'desc': '🏋️ Çok Yavaş, GPU İster (Dikkat!)'}
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {"active_profile": "light"}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"{RED}Ayarlar kaydedilemedi: {e}{RESET}")

def settings_main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        current_settings = load_settings()
        curr_profile = current_settings.get("active_profile", "light")
        
        if curr_profile not in PROFILES:
            curr_profile = 'light'

        print(f"{CYAN}╔══════════════════════════════════════════════╗{RESET}")
        print(f"{CYAN}║           ⚙️  SİSTEM AYARLARI                 ║{RESET}")
        print(f"{CYAN}╚══════════════════════════════════════════════╝{RESET}")
        
        p_info = PROFILES[curr_profile]
        
        print(f"\n🧠 Aktif Hafıza Modeli: {GREEN}{p_info['name']} [{p_info['size']}]{RESET}")
        print(f"{YELLOW}   └─ {p_info['desc']}{RESET}\n")
        
        print("Mevcut Seçenekler:")
        print(f"   [1] Hafif  (80 MB)  - Hız Odaklı")
        print(f"   [2] Orta   (470 MB) - Anlama Odaklı")
        print(f"   [3] Ağır   (2 GB)   - Detay Odaklı")
        print(f"\n   [Q] Menüye Dön")
        
        choice = input(f"\n{YELLOW}Seçiminiz: {RESET}").strip().lower()
        
        if choice == 'q':
            break
            
        new_profile = None
        if choice == '1': new_profile = 'light'
        elif choice == '2': new_profile = 'medium'
        elif choice == '3': new_profile = 'heavy'
        
        if new_profile and new_profile != curr_profile:
            print(f"\n{RED}⚠️  DİKKAT: Hafıza Modeli Değiştiriliyor!{RESET}")
            print(f"Eski model ile oluşturulan proje hafızaları, bu model ile çalışmaz.")
            print(f"Sistem, projeye girdiğinde eski hafızayı otomatik olarak {RED}ARŞİVLEYİP SIFIRLAYACAKTIR.{RESET}")
            
            # --- DÜZELTME BURADA ---
            # Artık hem 'evet' hem 'e' kabul ediyor
            confirm = input(f"\n{RED}Onaylıyor musunuz? (e/h): {RESET}").lower()
            
            if confirm in ['evet', 'e']:
                current_settings["active_profile"] = new_profile
                save_settings(current_settings)
                print(f"\n{GREEN}✅ Ayar değiştirildi: {new_profile.upper()}{RESET}")
                time.sleep(1.5)
            else:
                print(f"\n{YELLOW}İptal edildi.{RESET}")
                time.sleep(1)
        elif new_profile == curr_profile:
            print(f"\n{YELLOW}Zaten bu mod aktif.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    settings_main()
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

#### 📄 Dosya: `user_settings.json`

```json
{
    "active_profile": "medium"
}
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

#### 📄 Dosya: `core/deepseek.py`

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

#### 📄 Dosya: `core/gemini.py`

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

#### 📄 Dosya: `core/groq.py`

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

#### 📄 Dosya: `core/memory.py`

```py
import os
import shutil
import chromadb
import torch
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import config
from config import Colors

class MemoryManager:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.memory_path = os.path.join(project_root, config.MEMORY_DIR_NAME)
        self.bm25_path = os.path.join(self.memory_path, "keyword_index.json")
        
        # 1. Donanım Algılama
        self.device = self._detect_device()
        print(f"{Colors.MAGENTA}🧠 Hibrit Hafıza Motoru Başlatılıyor... ({self.device}){Colors.RESET}")
        
        # 2. Vektör Motoru (ChromaDB)
        self.embedder = SentenceTransformer(config.EMBEDDING_MODEL, device=self.device)
        os.makedirs(self.memory_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.memory_path)
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        # 3. Anahtar Kelime Motoru (BM25)
        self.bm25 = None
        self.indexed_files = []
        self._load_bm25()

    def _detect_device(self):
        if torch.cuda.is_available(): return "cuda"
        if torch.backends.mps.is_available(): return "mps"
        return "cpu"

    def _load_bm25(self):
        """BM25 indeksini diskten yükler."""
        if os.path.exists(self.bm25_path):
            try:
                with open(self.bm25_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.indexed_files = data['files']
                    corpus = [doc.split() for doc in data['corpus']]
                    self.bm25 = BM25Okapi(corpus)
            except: pass

    def index_files(self, file_paths: list):
        """Dosyaları hem Vektör hem de BM25 için indeksler."""
        documents = []
        metadatas = []
        ids = []
        corpus_for_bm25 = []

        print(f"{Colors.CYAN}📥 {len(file_paths)} dosya hibrit indeksleniyor...{Colors.RESET}")

        for fpath in file_paths:
            full_path = os.path.join(self.project_root, fpath)
            if not os.path.exists(full_path): continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if not content.strip(): continue

                documents.append(content)
                metadatas.append({"source": fpath})
                ids.append(fpath)
                corpus_for_bm25.append(content)
                if fpath not in self.indexed_files: self.indexed_files.append(fpath)

            except Exception as e:
                print(f"{Colors.YELLOW}Uyarı: {fpath} okunamadı ({e}){Colors.RESET}")

        if documents:
            # Vektör Kayıt
            embeddings = self.embedder.encode(documents, normalize_embeddings=True).tolist()
            self.collection.upsert(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)
            
            # BM25 Kayıt
            current_data = {"files": self.indexed_files, "corpus": documents} 
            with open(self.bm25_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f)
            self._load_bm25()
            print(f"{Colors.GREEN}✅ Hibrit hafıza güncellendi.{Colors.RESET}")

    def query(self, prompt: str, n_results=config.MAX_CONTEXT_RESULTS):
        """Hibrit Arama: Vektör + BM25 sonuçlarını birleştirir."""
        # 1. Vektör Araması (Anlamsal)
        query_embedding = self.embedder.encode([prompt], normalize_embeddings=True).tolist()
        vector_results = self.collection.query(query_embeddings=query_embedding, n_results=n_results)
        
        vector_docs = []
        if vector_results['documents']:
            for i, doc in enumerate(vector_results['documents'][0]):
                source = vector_results['metadatas'][0][i]['source']
                vector_docs.append((source, doc, "Vektör"))

        # 2. BM25 Araması (Anahtar Kelime)
        bm25_docs = []
        if self.bm25:
            tokenized_query = prompt.split()
            top_n = self.bm25.get_top_n(tokenized_query, self.indexed_files, n=n_results)
            for source in top_n:
                # BM25'ten gelen dosyanın içeriğini Chroma'dan çekelim
                res = self.collection.get(ids=[source])
                if res['documents']:
                    bm25_docs.append((source, res['documents'][0], "Keyword"))

        # 3. Sonuçları Birleştir (Tekilleştir)
        seen_sources = set()
        final_context = []
        
        # Öncelik: BM25 (Nokta atışı kelime eşleşmesi) sonra Vektör
        for source, doc, mtype in (bm25_docs + vector_docs):
            if source not in seen_sources:
                final_context.append(f"--- BAĞLAM ({mtype}): {source} ---\n{doc}\n")
                seen_sources.add(source)
                if len(final_context) >= n_results: break
        
        return "\n".join(final_context)
```

#### 📄 Dosya: `core/orchestrator.py`

```py
# core/orchestrator.py
import json
from config import Colors, ARCHITECT_INSTRUCTION, DEVELOPER_INSTRUCTION
from core.groq import GroqModel
from core.gemini import GeminiModel

class AgentOrchestrator:
    def __init__(self):
        self.architect = GroqModel()  # Hızlı ve mantıklı
        self.developer = GeminiModel() # Geniş bağlam ve hassas yazım

    def execute_workflow(self, prompt, context, working_dir):
        print(f"{Colors.MAGENTA}🏗️  MİMAR (Groq) planı hazırlıyor...{Colors.RESET}")
        
        # 1. Mimar Planı Çıkarır
        arch_prompt = f"BAĞLAM:\n{context}\n\nİSTEK: {prompt}"
        arch_res = self.architect.generate_content(ARCHITECT_INSTRUCTION, arch_prompt)
        
        # JSON temizleme ve yükleme
        try:
            # Groq bazen string bazen dict dönebilir, adaptörüne göre ayarla
            plan_data = json.loads(arch_res) if isinstance(arch_res, str) else arch_res
        except:
            print(f"{Colors.RED}Mimar planı oluşturamadı.{Colors.RESET}")
            return None

        print(f"\n{Colors.CYAN}📋 MİMARIN PLANI:{Colors.RESET}\n{plan_data.get('plan')}")
        print(f"📂 Etkilenecek Dosyalar: {plan_data.get('etkilenecek_dosyalar')}")

        confirm = input(f"\n{Colors.YELLOW}Bu planı onaylıyor musunuz? (e/h): {Colors.RESET}").lower()
        if confirm != 'e':
            return None

        # 2. Mühendis Kodu Yazar
        print(f"\n{Colors.GREEN}👨‍💻 MÜHENDİS (Gemini) kodlamaya başlıyor...{Colors.RESET}")
        dev_prompt = f"MİMAR PLANI: {plan_data.get('plan')}\n\nBAĞLAM: {context}\n\nİSTEK: {prompt}"
        dev_res = self.developer.generate_content(DEVELOPER_INSTRUCTION, dev_prompt)
        
        return dev_res # Assistant.py'deki clean_json_string'e gidecek
```
