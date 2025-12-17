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