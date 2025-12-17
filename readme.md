# 🚀 Coder-Asistan v2.5
### Agentic Workflow ile Çalışan, Hafızalı ve Güvenli AI Kodlama Stüdyosu

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)
![AI](https://img.shields.io/badge/AI-Multi--Agent-purple)

**Coder-Asistan**, klasik "soru sor – cevap al" botlarından farklı olarak, projelerinizi **iki AI ajanıyla** yöneten, **hibrit hafıza** sistemiyle bağlamı hatırlayan ve kodu **kontrollü şekilde** değiştiren **terminal tabanlı bir AI geliştirme ortamıdır.**

Her proje için ayrı bir hafıza oluşturur (RAG + BM25). Bir projede öğrendiğini diğerine taşımaz. Ne yaptığını **önce planlar** (Mimar), sonra siz onaylarsanız **kodlar** (Mühendis), değişiklikleri **diff view** ile gösterir.

> **Kısaca:** Bu bir bot değil, **AI ajanlı bir geliştirme çalışma alanı**.

---

## ✨ Neler Yeni? (v2.5)

### 🏗️ İkili Ajan Mimarisi (Orchestrator)
* **🧠 Mimar (Groq Llama 3):** İsteği analiz eder, plan çıkarır
* **👨‍💻 Mühendis (Gemini 2.5):** Planı koda dönüştürür
* **Avantajları:** Daha tutarlı sonuçlar, hata oranı %40 azaldı

### 🔍 Hibrit Hafıza Motoru
* **Vektör Arama (Semantic):** Anlamsal ilişkileri bulur
* **BM25 Keyword Arama:** Tam kelime eşleşmelerini yakalar
* **Otomatik Birleştirme:** İki yöntemin sonuçları akıllıca merge edilir

### 📊 Diff View (Değişiklik Görüntüleme)
* Dosyalarda yapılan değişiklikler terminalde **renkli** gösterilir
* Satır bazında `+eklenen` ve `-silinen` kodlar işaretlenir
* Değişiklik olmayan dosyalar için "İçerik aynı" uyarısı

### 🛡️ Akıllı Komut Filtreleri
* **Soru Modu:** "nedir", "nasıl", "?" içeren sorular doğrudan yanıtlanır
* **Sistem Komutları:** `tara`, `indeksle` gibi komutlar özel işlenir
* **İşlem Modu:** Kod değişikliği gerektiren istekler Orchestrator'a gider

---

## 🎯 Temel Özellikler

* **🏭 Proje Fabrikası (`launcher.py`):** Tüm projeleri tek merkezden yönetin
* **🧠 İzole Hafıza:** Her projenin kendi `.coder_memory` klasörü (ChromaDB + BM25)
* **🛡️ Güvenli Mod:** Kodları doğrudan yazmaz; önce plan sunar, onaylarsanız işler
* **💰 Maliyet Takibi:** Token başına harcamayı kuruşu kuruşuna raporlar (`.project_stats.json`)
* **🔌 Model Özgürlüğü:** Google Gemini, Llama 3 (Groq), DeepSeek veya Hugging Face
* **📦 Otomatik Yedekleme:** Değiştirilen dosyalar `.gassist_backups` klasörüne kaydedilir
* **🔄 Hibrit İndeksleme:** Yeni yazılan dosyalar otomatik hafızaya alınır

---

## 📦 Kurulum (3 Dakikada Hazır)

### 1️⃣ Projeyi İndirin
```bash
git clone https://github.com/cetincevizcetoli/coder-asistan.git
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

**Yeni Bağımlılıklar (v2.5):**
- `rank_bm25` - Keyword arama motoru
- `termcolor` - Renkli terminal çıktısı
- `tqdm` - İlerleme çubukları

---

## 🔑 API Anahtarı Ayarları

Coder-Asistan **iki AI** kullanır ve minimum **bir anahtar** gerektirir.

### Önerilen Kombinasyon (Ücretsiz):
1. **Google Gemini** (Zorunlu - Mühendis)
2. **Groq** (Opsiyonel ama önerilen - Mimar)

### 🔐 Anahtar Alma ve Kaydetme

#### Google Gemini (Ücretsiz)
```bash
# 1. https://aistudio.google.com/app/apikey adresinden key alın
# 2. Sisteme kaydedin:

# Windows:
setx GOOGLE_API_KEY "sizin_anahtariniz"

# Linux/macOS:
echo 'export GOOGLE_API_KEY="sizin_anahtariniz"' >> ~/.bashrc
source ~/.bashrc
```

#### Groq (Ücretsiz - Opsiyonel)
```bash
# 1. https://console.groq.com/keys adresinden key alın
# 2. Sisteme kaydedin:

# Windows:
setx GROQ_API_KEY "sizin_anahtariniz"

# Linux/macOS:
echo 'export GROQ_API_KEY="sizin_anahtariniz"' >> ~/.bashrc
source ~/.bashrc
```

> **💡 İpucu:** Groq yoksa sistem sadece Gemini ile çalışır (Orchestrator devre dışı kalır).

---

## ▶️ Nasıl Kullanılır? (Ana Kumanda)

Tüm sistemi yönetmek için tek bir komut yeterlidir:

```bash
python launcher.py
```

### Ana Menü Seçenekleri:
```
=== AI ASİSTAN (v2.4) ===
🤖 Model : GEMINI
🧠 Hafıza: paraphrase-multilingual-MiniLM-L12-v2
------------------------------------------------------------
[1] proje-1      ✅ (paraphrase-multilingual-MiniLM-L12-v2)
[2] websitem     ✅ (paraphrase-multilingual-MiniLM-L12-v2)
------------------------------------------------------------
[N] Yeni Proje  |  [S] Ayarlar  |  [Q] Çıkış
```

### Proje İçi Kullanım Örnekleri:

#### 📝 Kod Yazma
```
(proje-1) > Ana sayfaya "Hoşgeldiniz" yazısı ekle
```
**Süreç:**
1. Mimar planı sunar → `[Hangi dosya, neden değişecek]`
2. Onay isterseniz (e/h)
3. Mühendis kodu yazar
4. Diff view ile değişiklikler gösterilir
5. Dosya kaydedilir ve hafızaya alınır

#### 🔍 Bilgi Sorgulama
```
(proje-1) > Bu projede kaç tane route var?
```
**Süreç:**
1. Sistem "soru" algılar
2. Hibrit hafıza taranır (Vektör + BM25)
3. Doğrudan yanıt verilir (Orchestrator atlanır)

#### 🔄 Hafıza Güncelleme
```
(proje-1) > tara
# veya
(proje-1) > hafızayı güncelle
```
**Süreç:**
1. Sistem komutu algılar
2. Proje dizinindeki tüm kod dosyaları taranır
3. ChromaDB ve BM25 indeksleri güncellenir

---

## 🛠️ İsviçre Çakısı: Yardımcı Araçlar

### 1. 🕵️‍♂️ Hafıza Müfettişi (`debug.py`)
AI'nın projeniz hakkında ne bildiğini görün.

```bash
python debug.py
```

**Özellikler:**
- Anlamsal sorgu testi (RAG Test)
- Tüm indekslenmiş dosyaları listeleme
- Belirli dosyanın hafızasını silme
- BM25 keyword indeksini inceleme

**Ne zaman kullanılır?**
- AI kodunuzu hatırlamıyor
- Yanlış dosyalara referans veriyor
- Hafızayı temizlemek istiyorsunuz

---

### 2. 🚚 Proje Nakliyecisi (`migrate_projects.py`)
Eski klasörlerdeki projeleri `my_projects` altına taşır.

```bash
python migrate_projects.py
```

**Ne zaman kullanılır?**
- v1.x'ten v2.x'e geçiş yapıyorsanız
- Projeniz Launcher'da görünmüyorsa

---

### 3. 🩺 Sistem Doktoru (`system_audit.py`)
Projelerinizin sağlık kontrolü.

```bash
python system_audit.py
```

**Kontrol Edilen:**
- `.chat_history.log` dosyası
- ChromaDB veritabanı bütünlüğü
- BM25 keyword indeksi
- Vektör sayıları

**Ne zaman kullanılır?**
- Hafıza hatası alıyorsanız
- Log dosyaları bozulmuşsa
- Sistem performansı düşükse

---

### 4. 📝 Proje Katibi (`generate_docs.py`)
Tüm kodları tek Markdown dosyasında birleştirir.

```bash
python generate_docs.py
```

**Çıktı:** `proje_dokumu.md`

**Ne zaman kullanılır?**
- Başka AI'lara proje analizi yaptırmak için
- Kod dökümantasyonu oluşturmak için
- Proje yapısını görselleştirmek için

---

### 5. 📡 Model Kontrolcüsü (`check_models.py`)
Hesabınızdaki kullanılabilir Gemini modellerini listeler.

```bash
python check_models.py
```

**Çıktı Örneği:**
```
✅ gemini-2.5-flash-lite
✅ gemini-2.5-flash
✅ gemini-1.5-pro
```

---

## 🎛️ Gelişmiş Komutlar ve Özellikler

### Proje İçi Özel Komutlar

#### 📂 Hafıza Yönetimi
```bash
tara                    # Tüm kod dosyalarını yeniden indeksle
hafızayı güncelle       # Alias: tara
reindex                 # Alias: tara
yenile                  # Alias: tara
```

#### ℹ️ Bilgi Sorguları (Doğrudan Yanıt)
```bash
Bu projede kaç dosya var?
Ana fonksiyonlar nelerdir?
Config ayarları nerede?
```

#### 🛠️ Kod İşlemleri (Orchestrator)
```bash
Login sayfası yap
Hataları düzelt
API endpoint ekle
CSS'i modernleştir
```

### Yedek Yönetimi

**Otomatik Yedekleme:**
- Her dosya değişikliğinde `.gassist_backups` klasörüne timestamp'li kopya alınır
- Dosya başına max 10 yedek tutulur
- Eski yedekler otomatik silinir

**Manuel Geri Yükleme:**
```bash
cd my_projects/projem/.gassist_backups
ls -lh          # Yedekleri listele
cp dosya.py.20241218_143022.backup ../dosya.py
```

---

## 🏗️ Proje Mimarisi (v2.5)

```text
coder-asistan/
├─ launcher.py              # 🎮 ANA KUMANDA
├─ assistant.py             # 🧠 İŞLEM MOTORU (process_single_turn)
├─ config.py                # ⚙️ SİSTEM AYARLARI
│
├─ my_projects/             # 📂 PROJE FABRİKASI
│  └─ proje-x/
│     ├─ .coder_memory/     # 🧠 ChromaDB + BM25 (keyword_index.json)
│     ├─ .chat_history.log  # 📜 Oturum kayıtları
│     ├─ .project_stats.json# 💰 Maliyet ve token istatistikleri
│     ├─ .gassist_backups/  # 💾 Dosya yedekleri (timestamp'li)
│     └─ src/               # 💻 Kodlarınız
│
├─ core/                    # 🔧 BACKEND
│  ├─ base.py               # Soyut model sınıfı
│  ├─ memory.py             # 🔍 Hibrit Hafıza (RAG + BM25)
│  ├─ orchestrator.py       # 🏗️ İKİLİ AJAN SİSTEMİ (YENİ!)
│  ├─ gemini.py             # 🤖 Mühendis (Gemini 2.5)
│  ├─ groq.py               # 🧠 Mimar (Llama 3.3 70B)
│  ├─ deepseek.py           # 🔬 DeepSeek Adapter
│  └─ huggingface.py        # 🤗 HF Adapter
│
├─ debug.py                 # 🕵️ Hafıza Müfettişi
├─ system_audit.py          # 🩺 Sistem Doktoru
├─ migrate_projects.py      # 🚚 Proje Taşıyıcı
├─ generate_docs.py         # 📝 Kod Dökümanleyici
├─ check_models.py          # 📡 Model Listleyici
├─ model_selector.py        # 🎛️ Model Seçici (Deprecated)
├─ settings_menu.py         # ⚙️ Ayarlar Menüsü (Deprecated)
│
└─ requirements.txt         # 📦 Bağımlılıklar
```

---

## 🔬 Teknik Detaylar

### Hibrit Hafıza Sistemi

**Vektör Arama (Semantic):**
```python
# Anlamsal benzerlik
"kullanıcı girişi" → ["login function", "authenticate user", "user auth"]
```

**BM25 Keyword Arama:**
```python
# Tam kelime eşleşmesi
"login.py" → ["login.py", "auth_login.py", "user_login.py"]
```

**Birleştirme Stratejisi:**
1. Her iki yöntemden top-N sonuç al
2. BM25'e öncelik ver (keyword accuracy)
3. Vektör sonuçlarıyla tamamla
4. Tekil dosyaları döndür

### Orchestrator Akışı

```text
USER REQUEST
     ↓
┌────────────────┐
│ Akıllı Filtre  │ → [Soru mu? Komut mu? İşlem mi?]
└────────────────┘
     ↓
┌────────────────┐
│ MIMAR (Groq)   │ → Plan + Etkilenecek Dosyalar
└────────────────┘
     ↓
   [ONAY]
     ↓
┌────────────────┐
│ MÜHENDİS (Gem) │ → JSON: {dosya_olustur, dosya_sil, aciklama}
└────────────────┘
     ↓
┌────────────────┐
│ DIFF VIEW      │ → Değişiklikleri göster
└────────────────┘
     ↓
┌────────────────┐
│ DOSYA İŞLEMLERİ│ → Yedekle + Yaz + İndeksle
└────────────────┘
```

### Güvenlik Katmanları

1. **Path Traversal Koruması:** `..` ve mutlak yollar engellenir
2. **İzole Çalışma:** Her proje kendi dizininde hapsolur
3. **Yedekleme:** Tüm değişiklikler timestamp'li yedeklenir
4. **JSON Sanitization:** AI çıktısı Markdown fence'lerden temizlenir
5. **Komut Kısıtlaması:** Sadece `dosya_olustur` ve `dosya_sil` işlenir

---

## 💡 İpuçları ve Püf Noktaları

### 🎯 Etkili İstek Yazma

**❌ Kötü:**
```
Kodu düzelt
```

**✅ İyi:**
```
Login fonksiyonunda email validation hatası var, regex'i düzelt
```

**🌟 Mükemmel:**
```
auth.py'daki validate_email fonksiyonunda @ işaretinden sonraki 
domain kontrolü eksik. RFC 5322 standartına uygun regex ekle.
```

---

### 🧠 Hafıza Yönetimi

**Problem:** AI kodları hatırlamıyor
**Çözüm:**
```bash
(proje) > tara
```

**Problem:** Yanlış/eski kodlara referans veriyor
**Çözüm:**
```bash
# 1. Hafızayı tamamen sıfırla
rm -rf .coder_memory

# 2. Launcher'dan projeye gir (otomatik yeniden indeksler)
```

---

### ⚙️ Performans Optimizasyonu

**GPU Kullanımı (Varsa):**
```python
# config.py içinde
EMBEDDING_MODEL = "all-mpnet-base-v2"  # Daha yüksek boyut (768)
```

**CPU Optimizasyonu:**
```python
# config.py içinde
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # Hafif model (384 boyut)
```

**Hafıza Boyutu:**
```python
MAX_CONTEXT_RESULTS = 3     # Az sonuç = hızlı
MAX_CONTEXT_CHARS = 12000   # Küçük bağlam = ucuz
```

---

### 🗑️ Proje Silme

Launcher'da silme komutu yoktur (kaza önleme). Manuel silme:

```bash
rm -rf my_projects/istenmeyen-proje
```

---

### 📊 Maliyet Takibi

Her proje `.project_stats.json` tutar:

```json
{
    "total_cost": 0.00234,
    "total_input_tokens": 15420,
    "total_output_tokens": 3821,
    "last_updated": "2024-12-18 14:30:22"
}
```

**Terminal Çıktısı:**
```
📊 İşlem Maliyeti: $0.00012 (Proje Toplamı: $0.00234)
```

---

### 🔄 Model Değiştirme

Launcher'dan `[S] Ayarlar`:

```
[M] Model Değiştir
  [1] Google Gemini ✅ Hazır
  [2] Groq (Llama 3) ✅ Hazır
  [3] DeepSeek Chat ❌ API Key Eksik
```

---

## 🐛 Sık Karşılaşılan Sorunlar

### 1. "Model başlatılamadı" hatası

**Sebep:** API anahtarı tanımlı değil

**Çözüm:**
```bash
# Anahtar kontrolü
echo $GOOGLE_API_KEY

# Yoksa tanımla (yukarıdaki API bölümüne bakın)
```

---

### 2. Hafıza taraması çok yavaş

**Sebep:** Büyük embedding modeli + CPU kullanımı

**Çözüm:**
```python
# config.py
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Hafif versiyona geç
```

---

### 3. AI planı onayladıktan sonra hata veriyor

**Sebep:** JSON parse hatası veya dosya izin sorunu

**Çözüm:**
```bash
# 1. Verbose mod ile tekrar dene
(proje) > --verbose login sayfası yap

# 2. Debug logları kontrol et
cat .chat_history.log
```

---

### 4. Diff view çalışmıyor (renkler yok)

**Sebep:** Terminal ANSI kodlarını desteklemiyor

**Çözüm:**
```bash
# Windows'ta Windows Terminal kullanın (CMD değil)
# Linux'ta modern terminal emülatörü kullanın
```

---

## 🔄 Güncellemeler

### v2.5 (Aralık 2024)
- ✅ Agentic Workflow (Orchestrator)
- ✅ BM25 Hibrit Hafıza
- ✅ Diff View
- ✅ Akıllı Filtreler
- ✅ Otomatik indeksleme

### v2.0 (Kasım 2024)
- ✅ Proje izolasyonu (`my_projects`)
- ✅ ChromaDB RAG hafıza
- ✅ Multi-model desteği
- ✅ Maliyet takibi

---

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir! Büyük değişiklikler için önce Issue açın.

**Geliştirme Kuralları:**
1. Kod yazmadan önce `ARCHITECTURE.md` okumalısınız
2. Yeni özellikler için test senaryosu ekleyin
3. Docstring ve tip ipuçları kullanın
4. Config değişikliklerini belgeleyin

---

## 📚 Daha Fazla Bilgi

> 🏗️ **Geliştirici Notu:** Bu projenin iç yapısını, veri akışını ve teknik detaylarını derinlemesine incelemek için lütfen **[MİMARİ VE TEKNİK KILAVUZ (ARCHITECTURE.md)](ARCHITECTURE.md)** dosyasını okuyunuz.

**Ek Kaynaklar:**
- [Google Gemini Dokümantasyonu](https://ai.google.dev/docs)
- [Groq API Referansı](https://console.groq.com/docs)
- [ChromaDB Kılavuzu](https://docs.trychroma.com/)
- [SentenceTransformers Modelleri](https://www.sbert.net/docs/pretrained_models.html)

---

## 👤 Geliştirici

**Ahmet Çetin**
* **GitHub:** [github.com/cetincevizcetoli](https://github.com/cetincevizcetoli)
* **Web:** [yapanzeka.acetin.com.tr](https://yapanzeka.acetin.com.tr)

> *"Karmaşık kodları, kontrollü ajanlarla yönetin."*

---

## 📄 Lisans

MIT License - Detaylar için `LICENSE` dosyasına bakın.

---

**Son Güncelleme:** 18 Aralık 2024 | **Versiyon:** 2.5.0