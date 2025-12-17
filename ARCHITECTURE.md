# 🏗️ Coder-Asistan v2.5: Teknik Mimari Referansı

Bu belge, **Coder-Asistan** projesinin iç yapısını, veri akışını ve **v2.5** ile gelen katmanlı mimariyi açıklayan teknik referanstır.

Proje, basit bir script değil; **Command Interception (Komut Kesme)**, **Chain-of-Thought Orchestration** ve **Hibrit RAG** prensipleri üzerine kurulmuş modüler bir sistemdir.

---

## 1. 🗺️ Katmanlı Mimari (Layered Architecture)

Sistem, veriyi işlemeden önce çeşitli filtrelerden geçirir. Bu yapı **"Least Privilege"** (En Az Yetki) ve **"Cost Efficiency"** (Maliyet Verimliliği) prensiplerine dayanır.

```text
[KULLANICI GİRDİSİ]
       ⬇
┌──────────────────────────────────────────────┐
│  KATMAN 1: GATEKEEPER (Interception Layer)   │ 
│  (assistant.py)                              │
│                                              │
│  1. Regex Kontrolü: Sistem komutu mu?        │ ──➡ [YEREL İŞLEM] (tara, indeksle)
│  2. Semantik Kontrol: Soru mu?               │ ──➡ [RAG ONLY] (Sadece Cevap)
│  3. İşlem Kontrolü: Kod değişikliği mi?      │ ──➡ [ORCHESTRATOR'A İLET]
└──────┬───────────────────────────────────────┘
       │ (Sadece İşlem Gerekiyorsa)
       ⬇
┌──────────────────────────────────────────────┐
│  KATMAN 2: ORCHESTRATOR (Agentic Layer)      │
│  (core/orchestrator.py)                      │
│                                              │
│  1. MİMAR (Groq): Planlama ve Strateji       │ ──➡ JSON Planı
│        ⬇ (Kullanıcı Onayı)                   │
│  2. MÜHENDİS (Gemini): Kod Üretimi           │ ──➡ JSON Kod Çıktısı
└──────┬───────────────────────────────────────┘
       ⬇
┌──────────────────────────────────────────────┐
│  KATMAN 3: SAFE I/O (Execution Layer)        │
│  (assistant.py)                              │
│                                              │
│  1. JSON Sanitization (Temizleme)            │
│  2. Diff View Rendering (Görselleştirme)     │
│  3. Backup & Write (Yedekle ve Yaz)          │
└──────────────────────────────────────────────┘
```

---

## 2. 🛡️ Katman 1: The Gatekeeper (Komut Kesme)

`assistant.py` içindeki `process_single_turn` fonksiyonu, körü körüne her isteği AI modeline göndermez. Bu katman sistemin **"Akıllı Filtresi"**dir.

*   **Logic:** Girdi string'i üzerinde analiz yapar.
*   **Short-Circuit (Kısa Devre):** Eğer kullanıcı `tara`, `yenile` veya `hafızayı güncelle` dediyse, akış AI modellerine gitmeden kesilir ve doğrudan `memory.index_files()` çağrılır.
*   **Fayda:** Token maliyeti $0.00 olur ve işlem milisaniyeler sürer.

---

## 3. 🧠 Katman 2: Hibrit Hafıza (Memory v2)

v2.5 ile birlikte hafıza sistemi "Memory Layer v2"ye yükseltilmiştir. Bu katman `core/memory.py` içinde bulunur ve **iki farklı arama algoritmasını** birleştirir.

### Neden Hibrit?
Vektör veritabanları (ChromaDB) "kavramsal" benzerlikleri bulmakta iyidir, ancak spesifik değişken isimlerini (örn: `process_payment_v2`) kaçırabilirler.

### Algoritma: Weighted Fusion
1.  **Semantic Search (Vektör):** `SentenceTransformer` ile embedding oluşturulur ve kosinüs benzerliği aranır.
2.  **Keyword Search (BM25):** `rank_bm25` kütüphanesi ile metin tabanlı kesin eşleşme aranır.
3.  **Merge (Birleştirme):** İki listeden gelen sonuçlar tekilleştirilir.

```python
# Pseudo-code örneği
results = merge_unique(
    bm25_results(query, limit=3),   # Öncelik 1: Kesin Eşleşme
    vector_results(query, limit=3)  # Öncelik 2: Anlamsal Eşleşme
)
```

---

## 4. 🤖 Katman 3: Orchestrator (Ajan Zinciri)

Bu katman (`core/orchestrator.py`), tek bir LLM'in hem planlama hem kodlama yaparken yaşadığı dikkat dağınıklığını çözmek için tasarlanmıştır.

### Rol Dağılımı
1.  **Mimar (Architect - Groq Llama 3):**
    *   **Prompt:** "Kod yazma, sadece plan yap." (`ARCHITECT_INSTRUCTION`)
    *   **Çıktı:** Yapılacak adımlar ve etkilenecek dosyalar listesi.
    *   **Avantaj:** Groq LPU sayesinde çok hızlıdır, kullanıcının bekleme süresini azaltır.

2.  **Mühendis (Developer - Gemini 2.5):**
    *   **Prompt:** "Mimarın planına sadık kal, kodu yaz." (`DEVELOPER_INSTRUCTION`)
    *   **Girdi:** Mimarın planı + Kullanıcı isteği + RAG Bağlamı.
    *   **Avantaj:** Gemini'nin 1M token bağlamı, büyük dosyaları işleyebilir.

---

## 5. 📂 Dizin Yapısı ve Sorumluluklar

```text
coder-asistan/
│
├── launcher.py                 # [ENTRY POINT] Proje seçimi ve ortam hazırlığı
├── assistant.py                # [CONTROLLER] Gatekeeper ve Safe I/O katmanı
├── config.py                   # [CONFIG] Promptlar, Fiyatlar, Sabitler
│
├── core/                       # [BACKEND]
│   ├── orchestrator.py         # -> Ajan Yönetimi (Mimar -> Mühendis)
│   ├── memory.py               # -> Hibrit Hafıza (Chroma + BM25)
│   ├── gemini.py / groq.py     # -> Model Adaptörleri
│   └── base.py                 # -> Interface
│
├── my_projects/                # [DATA]
│   └── proje-x/
│       ├── .coder_memory/      # -> Vektör DB ve Keyword Index
│       ├── .gassist_backups/   # -> Güvenlik Yedekleri
│       └── src/                # -> Kullanıcı Kodları
```

---

## 6. 🔒 Güvenlik ve Safe Write Protokolü

Sistem, AI'nın halüsinasyon görüp dosyaları bozmasını engellemek için **"Human-in-the-Loop"** (Döngüde İnsan) prensibiyle çalışır.

1.  **JSON Sanitization:** AI'dan gelen çıktı, Markdown (` ```json `) ve hatalı karakterlerden temizlenir.
2.  **Path Traversal Check:** `../../etc/passwd` gibi zararlı dosya yolları engellenir.
3.  **Diff View:** Değişiklikler kullanıcıya `difflib` ile renkli olarak gösterilir.
4.  **Onay:** Kullanıcı açıkça onaylamadan `os.write` fonksiyonu asla çalıştırılmaz.

---

## 7. Gelecek Planları (Roadmap)

*   **v3.0:** Multi-modal destek (Ekran görüntüsünden kod üretimi).
*   **Self-Healing:** Çalıştırılan kod hata verirse, ajanın logu okuyip kendini düzeltmesi (Loopback).
*   **Git Entegrasyonu:** Diff view yerine doğrudan Git commit önerisi.

---

**Geliştirici:** Ahmet Çetin
**Mimari Versiyon:** 2.5.0
**Son Güncelleme:** 18 Aralık 2024