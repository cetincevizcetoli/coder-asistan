# 🏗️ Coder-Asistan v2.5: Teknik Mimari ve Geliştirici Kılavuzu

Bu belge, **Coder-Asistan** projesinin iç yapısını, veri akışını, tasarım kararlarını ve sistemin "neden" böyle çalıştığını anlatan **derinlemesine teknik referanstır**.

Proje, basit bir script değil; **Agentic Workflow**, **Hibrit RAG (Retrieval-Augmented Generation)** ve durum (state) korumalı bir **CLI Kodlama Stüdyosu**dur.

---

## 📋 İçindekiler

1. [Kuş Bakışı Sistem Mimarisi](#1-🗺️-kuş-bakışı-sistem-mimarisi)
2. [Dizin Yapısı ve Sorumluluklar](#2-📂-dizin-yapısı-ve-sorumluluklar)
3. [Veri Akışı (Bir Komutun Yolculuğu)](#3-⚙️-veri-akışı-bir-komutun-yolculuğu)
4. [Kritik Konfigürasyonlar](#4-🔧-kritik-konfigürasyonlar-configpy)
5. [Geliştirici Araç Seti](#5-🛠️-geliştirici-araç-seti-devtools)
6. [Agentic Workflow (Orchestrator)](#6-🤖-agentic-workflow-orchestrator)
7. [Hibrit Hafıza Sistemi](#7-🧠-hibrit-hafıza-sistemi-rag--bm25)
8. [Güvenlik Mimarisi](#8-🛡️-güvenlik-mimarisi)
9. [Performans Optimizasyonu](#9-⚡-performans-optimizasyonu)
10. [Gelecek Planları](#10-🚀-gelecek-planları-ve-genişletilebilirlik)

---

## 1. 🗺️ Kuş Bakışı Sistem Mimarisi

Sistem **5 ana katmandan** oluşur:

### 1.1 Katmanlar ve Sorumlulukları

```text
┌─────────────────────────────────────────────────────────┐
│                    KULLANICI KATMANI                    │
│                  (Terminal Interface)                   │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              1. YÖNETİM KATMANI (Launcher)              │
│  • Proje seçimi ve izolasyon                            │
│  • Ortam kontrolü (API keys, model uyumluluk)           │
│  • Ayarlar yönetimi (Model + Hafıza profilleri)        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│          2. KARAR KATMANI (Assistant + Filters)         │
│  • Akıllı filtreleme (Soru/Komut/İşlem ayrımı)         │
│  • Maliyet hesaplama ve istatistik toplama             │
│  • JSON temizleme ve güvenlik kontrolü                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                ┌───────┴────────┐
                │                │
                ▼                ▼
    ┌───────────────┐   ┌────────────────┐
    │ 3a. HAFIZA    │   │ 3b. AJANLAR    │
    │    (Memory)   │   │ (Orchestrator) │
    │               │   │                │
    │ • ChromaDB    │   │ • Mimar (Groq) │
    │   (Vektör)    │   │ • Müh. (Gem)   │
    │ • BM25        │   │                │
    │   (Keyword)   │   │                │
    └───────────────┘   └────────────────┘
                │                │
                └───────┬────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│            4. ADAPTÖR KATMANI (Model Core)              │
│  • Gemini, Groq, DeepSeek, HuggingFace                  │
│  • Standart arayüz (BaseModel)                          │
│  • Token sayımı ve hata yönetimi                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              5. DEPOLAMA KATMANI (Storage)              │
│  • .coder_memory/ (ChromaDB + BM25 index)               │
│  • .chat_history.log (Oturum kayıtları)                 │
│  • .project_stats.json (Maliyet takibi)                 │
│  • .gassist_backups/ (Dosya yedekleri)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 📂 Dizin Yapısı ve Sorumluluklar

```text
coder-asistan/
│
├── launcher.py                 # [ENTRY POINT] Sistem başlatıcı
│   ├─ load_projects()          → my_projects/ tarar
│   ├─ create_new_project()     → Yeni proje oluşturur
│   ├─ start_project()          → assistant.main() çağırır
│   └─ settings_menu()          → Model/Hafıza ayarları
│
├── assistant.py                # [CORE ENGINE] İşlem motoru
│   ├─ process_single_turn()    → Ana iş akışı (Akıllı filtreleme)
│   ├─ show_diff()              → Diff view oluşturur
│   ├─ clean_json_string()      → AI çıktısını temizler
│   ├─ backup_file()            → Dosya yedekleme
│   ├─ log_conversation()       → Oturum loglama
│   └─ update_project_stats()   → Maliyet hesaplama
│
├── config.py                   # [SETTINGS] Sistem sabitleri
│   ├─ Colors                   → Terminal renkleri
│   ├─ MODEL_CONFIGS            → AI model ayarları
│   ├─ MEMORY_PROFILES          → Embedding modelleri
│   ├─ PRICING_RATES            → Maliyet tablosu
│   ├─ ARCHITECT_INSTRUCTION    → Mimar promptu
│   └─ DEVELOPER_INSTRUCTION    → Mühendis promptu
│
├── my_projects/                # [USER DATA] İzole proje alanları
│   └── proje-x/
│       ├── .coder_memory/      → ChromaDB veritabanı
│       │   ├── chroma.sqlite3  → Vektör indeksi
│       │   └── keyword_index.json → BM25 indeksi
│       ├── .chat_history.log   → Oturum geçmişi
│       ├── .project_stats.json → Maliyet istatistikleri
│       ├── .gassist_backups/   → Otomatik yedekler
│       ├── metadata.json       → Proje metaverisi
│       └── src/                → Kullanıcı kodları
│
├── core/                       # [BACKEND] Sistem çekirdeği
│   ├── base.py                 # Soyut model sınıfı
│   │   ├─ BaseModel            → Interface tanımı
│   │   └─ ModelAPIError        → Hata sınıfı
│   │
│   ├── orchestrator.py         # 🆕 İkili ajan sistemi
│   │   └─ AgentOrchestrator
│   │       ├─ architect (Groq) → Plan üretir
│   │       ├─ developer (Gem)  → Kod üretir
│   │       └─ execute_workflow()
│   │
│   ├── memory.py               # 🆕 Hibrit hafıza motoru
│   │   └─ MemoryManager
│   │       ├─ embedder         → SentenceTransformer
│   │       ├─ collection       → ChromaDB collection
│   │       ├─ bm25             → BM25Okapi instance
│   │       ├─ index_files()    → Dosyaları indeksler
│   │       └─ query()          → Hibrit arama
│   │
│   ├── gemini.py               # Google Gemini adapter
│   │   └─ GeminiModel
│   │       └─ generate_content() → JSON + usage döner
│   │
│   ├── groq.py                 # Groq (Llama 3) adapter
│   │   └─ GroqModel
│   │       └─ generate_content() → JSON string döner
│   │
│   ├── deepseek.py             # DeepSeek adapter
│   └── huggingface.py          # HuggingFace adapter
│
├── debug.py                    # [DEVTOOL] Hafıza müfettişi
│   ├─ inspect_project()        → Proje seçimi
│   ├─ anlamsal_sorgu_testi()   → RAG test
│   └─ dosya_silme()            → Hafıza temizleme
│
├── system_audit.py             # [DEVTOOL] Sistem doktoru
│   ├─ audit_log_file()         → Log kontrolü
│   ├─ audit_vector_db()        → ChromaDB kontrolü
│   └─ check_bm25_index()       → BM25 kontrolü
│
├── migrate_projects.py         # [UTILITY] Proje taşıyıcı
├── generate_docs.py            # [UTILITY] Kod dökümanleyici
├── check_models.py             # [UTILITY] Model listeyici
│
└── requirements.txt            # Python bağımlılıkları
    ├─ google-genai             → Gemini API
    ├─ chromadb                 → Vektör DB
    ├─ sentence-transformers    → Embedding
    ├─ rank_bm25                → 🆕 Keyword arama
    ├─ torch                    → ML framework
    └─ requests                 → HTTP client
```

---

## 3. ⚙️ Veri Akışı (Bir Komutun Yolculuğu)

Kullanıcı `python launcher.py` çalıştırıp bir projeye girdiğinde ve "Hatayı düzelt" dediğinde arka planda şu olaylar zinciri gerçekleşir:

### 3.1 Aşama 1: Akıllı Ön Filtreleme

```python
# assistant.py: process_single_turn() fonksiyonu

# 1. GİRİŞ KONTROLÜ
sorgu_temiz = prompt_text.lower().strip()

# 2. SİSTEM KOMUTU KONTROLÜ
sistem_komutlari = ["tara", "indeksle", "hafızayı güncelle", "yenile"]
if any(k in sorgu_temiz for k in sistem_komutlari):
    # KISA DEVRE: Orchestrator'a gitmeye gerek yok
    memory.index_files([...])  # Dosyaları tara ve indeksle
    return

# 3. SORU/BİLGİ SORGUSU KONTROLÜ
soru_kelimeleri = ["nedir", "kaç", "nasıl", "?"]
is_question = any(q in sorgu_temiz for q in soru_kelimeleri)

if is_question:
    # KISA DEVRE: Sadece bilgi ver, kod yazma
    rag_context = memory.query(prompt_text)
    response = developer.generate_content("Sen bilgi verici bir asistansın...", rag_context)
    print(response)
    return

# 4. NORMAL İŞLEM: Orchestrator'a yönlendir
execute_workflow(prompt_text, rag_context, working_dir)
```

**Filtreleme Mantığı:**

| Girdi Tipi | Anahtar Kelimeler | Akış | Orchestrator? |
|------------|-------------------|------|---------------|
| Sistem Komutu | tara, indeksle, güncelle | Dosya tarama | ❌ Hayır |
| Bilgi Sorusu | nedir, nasıl, kaç, ? | RAG sorgusu | ❌ Hayır |
| Kod İşlemi | düzelt, ekle, yap, değiştir | Agentic workflow | ✅ Evet |

---

### 3.2 Aşama 2: Hibrit Hafıza Sorgusu

```python
# core/memory.py: query() metodu

def query(self, prompt, n_results=3):
    # 1. VEKTÖR ARAMA (Semantic)
    query_embedding = embedder.encode([prompt])
    vector_results = collection.query(
        query_embeddings=query_embedding, 
        n_results=n_results
    )
    
    # 2. BM25 ARAMA (Keyword)
    tokenized = prompt.split()
    bm25_results = bm25.get_top_n(tokenized, corpus, n=n_results)
    
    # 3. SONUÇLARI BİRLEŞTİR
    # Öncelik: BM25 (keyword accuracy) > Vektör (semantic)
    final = merge_unique(bm25_results, vector_results)
    
    return format_context(final)
```

**Örnek Hibrit Arama:**

```
KULLANICI: "Login fonksiyonundaki email validation hatasını düzelt"

BM25 SONUÇLARI (Keyword Match):
  1. auth/login.py (email, validation kelimeleri geçiyor)
  2. utils/validators.py (validation geçiyor)

VEKTÖR SONUÇLARI (Semantic):
  1. auth/login.py (anlamsal olarak login ile ilgili)
  2. auth/register.py (benzer bağlam)
  3. models/user.py (kullanıcı işlemleri)

BİRLEŞTİRİLMİŞ (Tekil):
  ✅ auth/login.py (Her iki yöntemde de üst sırada)
  ✅ utils/validators.py (BM25'ten)
  ✅ models/user.py (Vektörden, ek bağlam)
```

---

### 3.3 Aşama 3: Agentic Workflow (Orchestrator)

```python
# core/orchestrator.py: execute_workflow()

def execute_workflow(prompt, context, working_dir):
    # 1. MİMAR AŞAMASI (Groq Llama 3 - Hızlı Düşünme)
    arch_prompt = f"BAĞLAM:\n{context}\n\nİSTEK: {prompt}"
    plan_json = architect.generate_content(
        ARCHITECT_INSTRUCTION,  # "Sen bir mimar olarak plan çıkar"
        arch_prompt
    )
    
    # Plan örneği:
    # {
    #   "plan": "1. auth/login.py'daki validate_email fonksiyonunu düzelt\n2. Regex'i RFC 5322'ye uygun yap",
    #   "etkilenecek_dosyalar": ["auth/login.py", "utils/validators.py"]
    # }
    
    print("MİMARIN PLANI:", plan_json["plan"])
    
    # 2. ONAY MEKANİZMASI
    confirm = input("Bu planı onaylıyor musunuz? (e/h): ")
    if confirm != 'e':
        return None
    
    # 3. MÜHENDİS AŞAMASI (Gemini 2.5 - Detaylı Kodlama)
    dev_prompt = f"MİMAR PLANI: {plan_json['plan']}\n\nBAĞLAM: {context}\n\nİSTEK: {prompt}"
    code_json = developer.generate_content(
        DEVELOPER_INSTRUCTION,  # "Sen bir mühendis olarak kod yaz"
        dev_prompt
    )
    
    # Kod örneği:
    # {
    #   "aciklama": "Email validation regex'i RFC 5322 standartına uyarlandı",
    #   "dosya_olustur": {
    #     "auth/login.py": "import re\n\ndef validate_email(email):\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'\n    return re.match(pattern, email)"
    #   },
    #   "dosya_sil": []
    # }
    
    return code_json
```

**Mimar vs Mühendis Karşılaştırması:**

| Özellik | Mimar (Groq Llama 3.3) | Mühendis (Gemini 2.5) |
|---------|-------------------------|------------------------|
| **Görev** | Plan + Strateji | Kod yazma |
| **Hız** | 🚀 Çok Hızlı (LPU) | ⚡ Hızlı |
| **Token Limiti** | 8K | 1M |
| **Maliyet** | Düşük | Ücretsiz (Free tier) |
| **Güçlü Yön** | Mantıksal çıkarım | Kod sentezi, geniş bağlam |
| **Zayıf Yön** | Uzun kod üretimi | Planlama kararsızlığı |

---

### 3.4 Aşama 4: JSON Temizliği ve Güvenlik

```python
# assistant.py: clean_json_string()

def clean_json_string(json_string):
    # 1. MARKDOWN FENCE TEMİZLEME
    # AI bazen şöyle döner: ```json\n{...}\n```
    if "```" in json_string:
        lines = json_string.split('\n')
        clean_lines = [l for l in lines if "```" not in l]
        json_string = "\n".join(clean_lines)
    
    # 2. TRAILING GARBAGE TEMİZLEME
    # AI bazen sonuna açıklama ekler: {...} Bu işlem tamamlandı.
    last_brace = json_string.rfind('}')
    json_string = json_string[:last_brace+1]
    
    # 3. PARSE VE DOĞRULAMA
    try:
        return json.loads(json_string)
    except:
        return None  # Geçersiz JSON

# GÜVENLİK KONTROLÜ
def is_safe_path(file_path, current_directory):
    # Path Traversal önleme
    if os.path.isabs(file_path):
        return False  # /etc/passwd gibi mutlak yollar yasak
    
    if '..' in file_path:
        return False  # ../../../ gibi çıkışlar yasak
    
    # Hedef yol proje içinde mi?
    target = os.path.abspath(os.path.join(current_directory, file_path))
    safe_root = os.path.abspath(current_directory)
    
    return target.startswith(safe_root)
```

---

### 3.5 Aşama 5: Diff View ve Dosya İşlemleri

```python
# assistant.py: show_diff()

def show_diff(file_path, old_content, new_content):
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(old_lines, new_lines, n=0)
    
    for line in diff:
        if line.startswith('+'):
            print(Colors.GREEN + line + Colors.RESET)  # Eklenen
        elif line.startswith('-'):
            print(Colors.RED + line + Colors.RESET)    # Silinen
        elif line.startswith('@@'):
            print(Colors.MAGENTA + line + Colors.RESET) # Satır numarası

# DOSYA İŞLEMLERİ
for path, content in files_create.items():
    full_path = os.path.join(working_dir, path)
    
    # 1. GÜVENLİK KONTROLÜ
    if not is_safe_path(path, working_dir):
        continue
    
    # 2. ESKİ İÇERİĞİ OKU (Diff için)
    old_content = ""
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            old_content = f.read()
    
    # 3. DIFF GÖSTER
    show_diff(path, old_content, content)
    
    # 4. YEDEKLE
    if os.path.exists(full_path):
        backup_file(full_path)  # .gassist_backups/dosya.py.20241218_143022.backup
    
    # 5. YAZ
    with open(full_path, 'w') as f:
        f.write(content)
    
    # 6. HAFIZAYA AL (Otomatik indeksleme)
    memory.index_files([path])
```

**Diff View Çıktı Örneği:**

```diff
📝 DEĞİŞİKLİK ÖZETİ (auth/login.py):
@@ -12,3 +12,5 @@
-    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
+    # RFC 5322 uyumlu regex
+    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

---

## 4. 🔧 Kritik Konfigürasyonlar (`config.py`)

### 4.1 Sistem Sabitleri

```python
# DOSYA İŞLEMLERİ
MAX_FILE_SIZE = 5 * 1024 * 1024      # 5MB (Token limiti için)
MAX_TOTAL_SIZE = 20 * 1024 * 1024    # 20MB (Toplam bağlam)
BACKUP_DIR = ".gassist_backups"      # Yedek klasörü
MAX_BACKUPS_PER_FILE = 10            # Dosya başına max yedek

# HAFIZA (RAG)
MEMORY_DIR_NAME = ".coder_memory"
COLLECTION_NAME = "project_codebase"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # Türkçe desteği
MAX_CONTEXT_RESULTS = 3              # Hibrit aramadan kaç sonuç
MAX_CONTEXT_CHARS = 12000            # Bağlam max karakter (token kontrolü)

# PROJE YÖNETİMİ
PROJECTS_DIR = "my_projects"         # İzole proje klasörü
```

---

### 4.2 AI Model Konfigürasyonları

```python
MODEL_CONFIGS = {
    "gemini": {
        "env_var": "GOOGLE_API_KEY",
        "model_name": "gemini-2.5-flash-lite",  # Ücretsiz tier
        "display_name": "Google Gemini 2.5 Flash Lite",
    },
    "groq": {
        "env_var": "GROQ_API_KEY",
        "model_id": "llama-3.3-70b-versatile",  # Ultra hızlı
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

ACTIVE_PROFILE = 'gemini'  # Varsayılan
```

---

### 4.3 Maliyet Tablosu (USD per 1M tokens)

```python
PRICING_RATES = {
    "gemini-2.5-flash-lite": {"input": 0.075, "output": 0.30},
    "gemini-2.5-flash": {"input": 0.10, "output": 0.40},
    "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
    "deepseek-chat": {"input": 0.14, "output": 0.28},
    "Qwen/Qwen2.5-Coder-7B-Instruct": {"input": 0.0, "output": 0.0}  # Ücretsiz
}
```

**Maliyet Hesaplama Örneği:**

```python
# Kullanım:
input_tokens = 15420
output_tokens = 3821

# Model: gemini-2.5-flash-lite
rates = PRICING_RATES["gemini-2.5-flash-lite"]

cost = (input_tokens / 1_000_000 * rates["input"]) + \
       (output_tokens / 1_000_000 * rates["output"])
# cost = (15420/1M * 0.075) + (3821/1M * 0.30)
# cost ≈ $0.00116 + $0.00115 = $0.00231
```

---

### 4.4 Prompt Mühendisliği (Sistem Talimatları)

```python
# MİMAR İÇİN (Groq)
ARCHITECT_INSTRUCTION = (
    "Sen uzman bir yazılım mimarısın. Görevin, kullanıcı isteğini analiz etmek "
    "ve bir uygulama planı çıkarmaktır.\n"
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
    "Sen uzman bir yazılım geliştiricsin. Mimarın sunduğu plana göre kodları yazmalısın.\n"
    "KURALLAR:\n"
    "1. Sadece geçerli bir JSON objesi döndür.\n"
    "2. Format:\n"
    "{\n"
    "  'aciklama': 'Yapılan işlemin özeti',\n"
    "  'dosya_olustur': {'yol': 'icerik'},\n"
    "  'dosya_sil': []\n"
    "}"
)
```

**Prompt Tasarım İlkeleri:**

1. **Katı Format:** AI'ya serbest sohbet izni vermemek (JSON zorla)
2. **Tek Sorumluluk:** Her ajana tek bir görev (Mimar planlar, Mühendis kodlar)
3. **Örnek Vermeden Açıklama:** AI kendi örneklerini üretsin (daha esnek)
4. **Negatif Talimatlar:** "Yapma" kuralları eklemek (Mimar kod yazmasın)

---

### 4.5 Hafıza Profilleri

```python
MEMORY_PROFILES = {
    "1": {
        "model_name": "all-MiniLM-L6-v2",
        "display": "Hafif (Light)",
        "desc": "🚀 En Hızlısı | Düşük RAM | 384 Boyut",
        "dim": 384
    },
    "2": {
        "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
        "display": "Dengeli (Medium)",
        "desc": "⚖️ Daha İyi Türkçe | Orta Hız | 384 Boyut",
        "dim": 384
    },
    "3": {
        "model_name": "all-mpnet-base-v2",
        "display": "Güçlü (Heavy)",
        "desc": "🧠 En Yüksek Doğruluk | Yavaş | 768 Boyut",
        "dim": 768
    }
}
```


## 4.4 Hafıza Profilleri - 

**Model Seçim Kriterleri:**

| Donanım | Önerilen Profil | Sebep |
|---------|-----------------|-------|
| Laptop (Intel i5, 8GB RAM) | `all-MiniLM-L6-v2` | CPU inference hızı |
| Desktop (Ryzen 5, 16GB RAM) | `paraphrase-multilingual-MiniLM-L12-v2` | Türkçe kalitesi |
| Workstation (GPU, 32GB RAM) | `all-mpnet-base-v2` | Maksimum doğruluk |

**Profil Değiştirme Etkisi:**
```python
# launcher.py içinde profil değiştiğinde:
def start_project(name, project_embed_model):
    if project_embed_model != config.EMBEDDING_MODEL:
        print(f"{Colors.RED}⛔ UYUMSUZLUK: Bu proje '{project_embed_model}' kullanıyor.{Colors.RESET}")
        # Sistem projeye girmeden önce kontrol yapar
```

**Neden Uyumsuzluk Önemli?**
- Her embedding modeli farklı boyutta vektör üretir (384 vs 768)
- Eski vektörlerle yeni model uyumlu çalışmaz
- Proje hafızası yeniden indekslenmeli

---

## 5. 🛠️ Geliştirici Araç Seti (DevTools)

### 5.1 debug.py - Hafıza Müfettişi

**Kullanım Senaryoları:**

1. **RAG Test:**
```python
# debug.py çalıştırıldığında:
q = input("🔍 AI gibi bir soru sorun: ")
res = memory.query(q)
print(f"\n{Colors.GREEN}🔎 BULUNAN BAĞLAM:{Colors.RESET}\n{res}")
```

2. **Vektör İçeriğini İnceleme:**
```python
res = memory.collection.get()
for mid in res['ids']: 
    print(f"  - {mid}")
# Çıktı:
# - src/main.py
# - config/settings.json
# - utils/helpers.py
```

3. **Belirli Dosya Silme:**
```python
memory.collection.delete(ids=["old_file.py"])
# Dosya fiziksel olarak değil, sadece hafızadan silinir
```

**Ne Zaman Kullanılır?**
- ❌ AI, kodunuzu hatırlamıyorsa
- ❌ Yanlış bağlam dönüyorsa
- ✅ Hibrit aramanın nasıl çalıştığını test etmek için

---

### 5.2 system_audit.py - Sistem Doktoru

**Kontrol Edilen Unsurlar:**

1. **Log Dosyası Sağlığı:**
```python
log_path = project_path / ".chat_history.log"
with open(log_path, 'r') as f:
    lines = f.readlines()
    print(f"   📄 Toplam Satır: {len(lines)}")
```

2. **ChromaDB Bütünlüğü:**
```python
conn = sqlite3.connect(sqlite_file)
cursor.execute("SELECT count(*) FROM embeddings;")
count = cursor.fetchone()[0]
print(f"   🧬 İndekslenmiş Vektör Sayısı: {count}")
```

**Çıktı Örneği:**
```
🔍 SİSTEM DENETÇİSİ BAŞLATILDI
📂 Hedef Dizin: /home/user/my_projects

========================================
📂 PROJE DENETLENİYOR: proje-x
========================================

--- 📜 LOG DOSYASI KONTROLÜ (.chat_history.log) ---
✅ Log Dosyası Mevcut (45234 bytes)
   📄 Toplam Satır: 382
   🔖 Son Kayıt: 🤖 AI:   İşlem tamamlandı.

--- 🧠 VEKTÖR VERİTABANI KONTROLÜ ---
✅ ChromaDB SQLite Dosyası Mevcut (2048000 bytes)
   📊 Tablo Sayısı: 7
   🧬 İndekslenmiş Vektör Sayısı: 23
   ✅ Veritabanı bütünlüğü (Integrity) sağlam.
```

---

### 5.3 migrate_projects.py - Proje Taşıyıcı

**Problem:**
```
# Eski proje yapısı (v2.0)
coder-asistan/
├── proje-a/         # ❌ Ana dizinde
├── proje-b/         # ❌ Ana dizinde
└── launcher.py

# Yeni yapı (v2.5+)
coder-asistan/
├── my_projects/
│   ├── proje-a/     # ✅ İzole alan
│   └── proje-b/     # ✅ İzole alan
└── launcher.py
```

**Çözüm:**
```python
for entry in Path.cwd().iterdir():
    if entry.is_dir() and (entry / ".coder_memory").exists():
        shutil.move(str(entry), str(TARGET_DIR / entry.name))
        print(f"   ✅ Taşındı: {entry.name}")
```

---

### 5.4 generate_docs.py - Proje Katibi

**Filtreleme Mantığı:**

```python
# Taranmayan klasörler
DIKKATE_ALINMAYACAK_DIZINLER = [
    '.git', '__pycache__', 'venv', 'node_modules',
    '.gassist_backups', '.coder_memory'
]

# İçeriği gösterilmeyen ama varlığı belirtilen
OZEL_USER_KLASORLERI = ['my_projects']
```

**Çıktı Formatı:**
```markdown
# 📄 Proje Dökümü: coder-asistan

### 📂 Proje Dizin Yapısı ve Dosyalar
- **coder-asistan/** (Proje Kökü)
  - launcher.py
  - assistant.py
  - **my_projects/** (Kullanıcı Projeleri - İçerik Gizli)

---
### 💻 Kod İçeriği Dökümü

#### 📄 Dosya: `launcher.py`
```python
import os
...
```
```

**Ne İşe Yarar?**
- 🤖 Tüm kodu tek bir dosyada ChatGPT/Claude'a gönderebilirsiniz
- 📚 Dokümantasyon oluşturabilirsiniz
- 🔍 Global arama yapabilirsiniz

---

### 5.5 check_models.py - Model Kontrolcüsü

**Gemini API Testi:**
```python
client = genai.Client(api_key=api_key)
for m in client.models.list():
    if "generateContent" in m.supported_actions:
        clean_name = m.name.replace('models/', '')
        print(f"✅ {clean_name}")
```

**Örnek Çıktı:**
```
🔑 Anahtar ile bağlanılıyor... (Son 4 hane: X7k9)

📡 --- HESABINIZDA AKTİF OLAN MODELLER ---
✅ gemini-2.0-flash-exp
✅ gemini-2.5-flash-lite
✅ gemini-pro

💉 İPUCU: Yukarıdaki ✅ ile başlayan isimlerden birini config.py dosyasına kopyalayın.
```

---

## 6. 🤖 Agentic Workflow (Orchestrator)

### 6.1 İkili Ajan Sistemi

**Mimari Karar:**
- **Neden Tek Değil İki Model?**
  - Planlama ≠ Kodlama
  - Groq: Saniyede 750 token (planlama için ideal)
  - Gemini: 1M token bağlam (büyük dosyalar için)

**Akış Diyagramı:**
```
KULLANICI İSTEĞİ
      ↓
┌─────────────────┐
│  1. MİMAR       │ → Groq Llama 3.3 70B
│  (Strateji)     │    • Plan oluştur
│                 │    • Dosyaları belirle
└────────┬────────┘    • JSON formatında yanıt
         │
         ↓ (ONAY BEKLENİYOR)
         │
┌────────┴────────┐
│  2. MÜHENDİS    │ → Gemini 2.5 Flash Lite
│  (Uygulama)     │    • Kodu yaz
│                 │    • Diff oluştur
└────────┬────────┘    • Dosyaya kaydet
         │
         ↓
   TAMAMLANDI
```

### 6.2 Orchestrator Kodu Detayı

**Mimar Aşaması:**
```python
arch_prompt = f"BAĞLAM:\n{context}\n\nİSTEK: {prompt}"
arch_res = self.architect.generate_content(ARCHITECT_INSTRUCTION, arch_prompt)

# Beklenen JSON:
# {
#   "plan": "1. login.py'daki validate_email() düzelt\n2. Regex RFC 5322'ye uyarla",
#   "etkilenecek_dosyalar": ["auth/login.py", "utils/validators.py"]
# }
```

**Onay Mekanizması:**
```python
confirm = input(f"\n{Colors.YELLOW}Bu planı onaylıyor musunuz? (e/h): {Colors.RESET}").lower()
if confirm != 'e':
    return None  # İşlem iptal
```

**Mühendis Aşaması:**
```python
dev_prompt = f"MİMAR PLANI: {plan_data.get('plan')}\n\nBAĞLAM: {context}\n\nİSTEK: {prompt}"
dev_res = self.developer.generate_content(DEVELOPER_INSTRUCTION, dev_prompt)

# Beklenen JSON:
# {
#   "aciklama": "Email validation regex'i RFC 5322'ye uyarlandı",
#   "dosya_olustur": {
#     "auth/login.py": "import re\n\ndef validate_email(email):\n..."
#   },
#   "dosya_sil": []
# }
```

---

## 7. 🧠 Hibrit Hafıza Sistemi (RAG + BM25)

### 7.1 Neden Hibrit?

**Vektör Arama (Semantic) Sorunu:**
```python
query: "Login fonksiyonundaki email validation hatası"
vector_results: 
  1. auth/register.py (çünkü "login" kelimesi yok ama anlamsal benzerlik var)
  2. auth/login.py
  3. models/user.py
```

**BM25 (Keyword) Avantajı:**
```python
query: "Login fonksiyonundaki email validation hatası"
bm25_results:
  1. auth/login.py (doğrudan "login", "email", "validation" kelimelerini içeriyor)
  2. utils/validators.py
```

**Hibrit Çözüm:**
```python
# Öncelik: BM25 (keyword accuracy) > Vektör (semantic)
final = merge_unique(bm25_results, vector_results)
```

### 7.2 BM25 İndeksleme

**Kaydetme:**
```python
# core/memory.py: index_files()
corpus_for_bm25.append(content)  # Ham metin
current_data = {"files": self.indexed_files, "corpus": documents}
with open(self.bm25_path, 'w', encoding='utf-8') as f:
    json.dump(current_data, f)
```

**Yükleme:**
```python
def _load_bm25(self):
    with open(self.bm25_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        corpus = [doc.split() for doc in data['corpus']]
        self.bm25 = BM25Okapi(corpus)
```

### 7.3 Hibrit Sorgu Algoritması

```python
def query(self, prompt: str, n_results=3):
    # 1. VektÖr Arama
    query_embedding = self.embedder.encode([prompt]).tolist()
    vector_results = self.collection.query(query_embeddings=query_embedding, n_results=n_results)
    
    # 2. BM25 Arama
    tokenized_query = prompt.split()
    bm25_results = self.bm25.get_top_n(tokenized_query, self.indexed_files, n=n_results)
    
    # 3. Birleştirme (Tekilleştir)
    seen_sources = set()
    final_context = []
    
    # Öncelik: BM25 sonra Vektör
    for source, doc, mtype in (bm25_docs + vector_docs):
        if source not in seen_sources:
            final_context.append(f"--- BAĞLAM ({mtype}): {source} ---\n{doc}\n")
            seen_sources.add(source)
            if len(final_context) >= n_results: break
    
    return "\n".join(final_context)
```

---

## 8. 🛡️ Güvenlik Mimarisi

### 8.1 Path Traversal Önleme

**Saldırı Örneği:**
```python
# AI'dan gelen JSON:
{
  "dosya_olustur": {
    "../../../etc/passwd": "zararlı_kod"
  }
}
```

**Savunma:**
```python
def is_safe_path(file_path, current_directory):
    # 1. Mutlak yol kontrolü
    if os.path.isabs(file_path): 
        return False  # /etc/passwd yasak
    
    # 2. Üst dizin çıkışı kontrolü
    if '..' in file_path: 
        return False  # ../../../ yasak
    
    # 3. Hedef yol proje içinde mi?
    target = os.path.abspath(os.path.join(current_directory, file_path))
    safe_root = os.path.abspath(current_directory)
    
    return target.startswith(safe_root)
```

### 8.2 JSON Injection Önleme

**AI Yanıtı (Temizleme Öncesi):**
```json
```json
{
  "aciklama": "İşlem tamamlandı",
  "dosya_olustur": {...}
}
```

Bu işlem başarıyla tamamlanmıştır. Başka bir şey yapmamı ister misiniz?
```

**Temizleme:**
```python
def clean_json_string(json_string):
    # 1. Markdown fence temizle
    if "```" in json_string:
        lines = json_string.split('\n')
        clean_lines = [l for l in lines if "```" not in l]
        json_string = "\n".join(clean_lines)
    
    # 2. Trailing garbage temizle
    last_brace = json_string.rfind('}')
    json_string = json_string[:last_brace+1]
    
    return json.loads(json_string)
```

### 8.3 Otomatik Yedekleme

**Yedekleme Stratejisi:**
```python
def backup_file(full_path):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{os.path.basename(full_path)}.{timestamp}.backup"
    shutil.copy(full_path, os.path.join(config.BACKUP_DIR, backup_name))
    
    # Eski yedekleri temizle (max 10)
    backups = sorted([f for f in os.listdir(config.BACKUP_DIR) if f.startswith(os.path.basename(full_path))])
    if len(backups) > config.MAX_BACKUPS_PER_FILE:
        for old in backups[:-config.MAX_BACKUPS_PER_FILE]:
            os.remove(os.path.join(config.BACKUP_DIR, old))
```

**Klasör Yapısı:**
```
.gassist_backups/
├── main.py.20241218_143022.backup
├── main.py.20241218_144530.backup
├── config.json.20241218_145612.backup
└── ... (en fazla 10 yedek/dosya)
```

---

## 9. ⚡ Performans Optimizasyonu

### 9.1 Donanım Adaptasyonu

**CPU/GPU Algılama:**
```python
def _detect_device(self):
    if torch.cuda.is_available(): 
        return "cuda"      # NVIDIA GPU
    if torch.backends.mps.is_available(): 
        return "mps"       # Apple Silicon
    return "cpu"           # CPU fallback
```

**Embedding Optimizasyonu:**
```python
# GPU varsa batch processing
if self.device == "cuda":
    embeddings = self.embedder.encode(documents, batch_size=32, normalize_embeddings=True)
else:
    embeddings = self.embedder.encode(documents, batch_size=8, normalize_embeddings=True)
```

### 9.2 Bellek Yönetimi

**Dosya Boyutu Kontrolleri:**
```python
MAX_FILE_SIZE = 5 * 1024 * 1024      # 5MB (Token limiti için)
MAX_TOTAL_SIZE = 20 * 1024 * 1024    # 20MB (Toplam bağlam)

# assistant.py içinde:
if os.path.getsize(file_path) > config.MAX_FILE_SIZE:
    print(f"{Colors.YELLOW}⚠️ {file_path} çok büyük, atlanıyor.{Colors.RESET}")
    continue
```

### 9.3 Maliyet Optimizasyonu

**Token Sayımı:**
```python
# core/gemini.py içinde:
usage = {
    "input_tokens": response.usage_metadata.prompt_token_count,
    "output_tokens": response.usage_metadata.candidates_token_count
}

# Maliyet hesaplama:
rates = PRICING_RATES[model_key]
cost = (input_tokens / 1_000_000 * rates["input"]) + \
       (output_tokens / 1_000_000 * rates["output"])
```

**Proje Bazlı İstatistik:**
```json
// .project_stats.json
{
    "total_cost": 0.45,
    "total_input_tokens": 152340,
    "total_output_tokens": 38210,
    "last_updated": "2024-12-18 14:30:22"
}
```

---

## 10. 🚀 Gelecek Planları ve Genişletilebilirlik

### 10.1 Planlanan Özellikler

**1. Multi-Modal Destek (Görsel Analiz):**
```python
# core/gemini.py genişletilecek
def generate_content_with_image(self, system_instruction, prompt_text, image_path):
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    response = self.client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                    types.Part.from_text(prompt_text)
                ]
            )
        ]
    )
```

**2. Kod İnceleme (Code Review) Modu:**
```python
# assistant.py'ye yeni komut
elif user_input.startswith("review:"):
    file_path = user_input.split(":", 1)[1].strip()
    review_code(file_path, orchestrator, memory)
```

**3. Test Otomasyonu:**
```python
def generate_tests(self, source_file):
    """AI kaynak koddan unit test üretir."""
    content = read_file(source_file)
    prompt = f"Bu kod için pytest testleri yaz:\n{content}"
    return orchestrator.developer.generate_content(TEST_INSTRUCTION, prompt)
```

### 10.2 Yeni Model Ekleme Rehberi

**Adım 1: core/new_model.py oluştur**
```python
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class NewModel(BaseModel):
    def __init__(self):
        conf = MODEL_CONFIGS["new_model"]
        self.MODEL_NAME = conf["display_name"]
        # API client başlat
    
    def generate_content(self, system_instruction, prompt_text):
        # API çağrısı
        return response
```

**Adım 2: config.py'ye ekle**
```python
MODEL_CONFIGS = {
    # ... mevcut modeller
    "new_model": {
        "env_var": "NEW_MODEL_API_KEY",
        "model_id": "new-model-v1",
        "display_name": "Yeni Model",
    }
}

PRICING_RATES = {
    # ... mevcut fiyatlar
    "new-model-v1": {"input": 0.20, "output": 0.50}
}
```

**Adım 3: launcher.py menüsünü güncelle**
```python
MODEL_OPTIONS = {
    # ... mevcut seçenekler
    "5": {"id": "new_model", "name": "Yeni Model", "desc": "🆕 Yeni özellik"}
}
```

### 10.3 Web Arayüzü Migrasyonu

**Mevcut CLI → Web Geçişi:**

```python
# app.py (Flask örneği)
from flask import Flask, request, jsonify
from assistant import process_single_turn
from core.orchestrator import AgentOrchestrator

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data['prompt']
    project = data['project_name']
    
    orchestrator = AgentOrchestrator()
    memory = MemoryManager(project)
    
    result = process_single_turn(prompt, orchestrator, project, memory, is_dry_run=False)
    return jsonify(result)
```

**Avantajlar:**
- 🌐 Uzaktan erişim
- 👥 Çoklu kullanıcı
- 📱 Mobil uyumluluk
- 📊 Görsel dashboard

---

## 📝 Sonuç

Coder-Asistan, basit bir "chatbot" değil; **endüstriyel seviye bir geliştirme ortamıdır**:

✅ **Modüler Mimari** - Yeni modeller kolayca eklenebilir
✅ **Güvenli Tasarım** - Path traversal, JSON injection korumalı
✅ **Hibrit Hafıza** - Keyword + Semantic arama
✅ **Maliyet Şeffaflığı** - Her işlem kuruşuna kadar takip edilir
✅ **Proje İzolasyonu** - Her projenin kendi hafızası

**Geliştirici Felsefesi:**
> "Karmaşık sistemler basit araçlarla yönetilmeli. AI, kullanıcının kontrolündedir - asla tam otonomiye geçmez."

---

**Versiyonlar:**
- v2.0: İlk stabil sürüm
- v2.4: Hibrit RAG eklendi
- v2.5: Orchestrator (İkili ajan) eklendi
- v3.0 (Planlanan): Multi-modal + Test otomasyonu

**Geliştirici:** Ahmet Çetin  
**Lisans:** MIT  
**Son Güncelleme:** 18 Aralık 2024