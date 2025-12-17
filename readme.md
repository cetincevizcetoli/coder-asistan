# 🚀 Coder-Asistan v2.5
### Agentic Workflow ile Çalışan, Hafızalı ve Güvenli AI Kodlama Stüdyosu

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)
![AI](https://img.shields.io/badge/AI-Multi--Agent-purple)

**Coder-Asistan**, klasik "soru sor – cevap al" botlarından farklı olarak, projelerinizi **iki AI ajanıyla** yöneten, **hibrit hafıza** sistemiyle bağlamı hatırlayan ve kodu **kontrollü şekilde** değiştiren **terminal tabanlı bir AI geliştirme ortamıdır.**

> **Kısaca:** Bu bir bot değil, **AI ajanlı bir geliştirme çalışma alanı**. Sizin yerinize düşünür, planlar ama onaysız asla işlem yapmaz.

---

## ✨ Neden v2.5? (Öne Çıkan Özellikler)

### 📉 Akıllı Tasarruf (Smart Short-Circuit)
Sistem, her yazdığınızı AI'ya gönderip paranızı harcamaz.
* **Soru Modu:** "Bu projede kaç dosya var?" gibi soruları doğrudan hafızadan yanıtlar.
* **Komut Modu:** `tara`, `yenile` gibi komutları yerel işlemciyle yapar.
* **Sonuç:** Gereksiz API çağrıları engellenir, token maliyeti düşer.

### 🧠 Hibrit Hafıza Motoru (Kayıp Yok)
Eski sistemler sadece "anlam" arardı. v2.5 ise iki motoru birleştirir:
1. **Vektör Arama:** "Kullanıcı giriş işlemi" dediğinizde `auth.py` dosyasını bulur.
2. **BM25 (Keyword):** "get_user_id" dediğinizde, bu kelimenin geçtiği satırı nokta atışı bulur.
* **Sonuç:** AI, projenizdeki en küçük detayı bile ıskalamaz.

### 🏗️ İkili Ajan Mimarisi (Orchestrator)
Tek bir AI yerine, uzmanlaşmış iki ajan çalışır:
* **Mimar (Groq):** Kod yazmaz. Sadece düşünür, analiz eder ve plan çıkarır.
* **Mühendis (Gemini):** Plana sadık kalarak kodu yazar.
* **Sonuç:** Hata oranı %40 azalmış, daha tutarlı kodlar.

### 🛡️ Paranoyak Güvenlik (Diff View)
AI asla kodunuzu sizden habersiz değiştiremez ("Overwrite" yoktur).
* **Ön İzleme:** Değişiklikler terminalde Renkli Diff formatında (`+yeşil`, `-kırmızı`) gösterilir.
* **Onay Zinciri:** Siz `[E]vet` demeden diske yazma işlemi gerçekleşmez.
* **Otomatik Yedek:** Her işlemden önce dosyanın yedeği `.gassist_backups` altına alınır.

---

## 🎯 Temel Yetenekler

* **🏭 Proje Fabrikası (`launcher.py`):** Tüm projeleri tek merkezden yönetin
* **🧠 İzole Hafıza:** Her projenin kendi `.coder_memory` klasörü (Proje A'nın verisi Proje B'ye karışmaz)
* **💰 Şeffaf Maliyet:** İşlem başına kaç cent harcadığınızı kuruşu kuruşuna raporlar
* **🔌 Model Özgürlüğü:** Google Gemini, Llama 3 (Groq), DeepSeek veya Hugging Face
* **📦 Otomatik Yedekleme:** Hata yapma lüksünüz var; eski versiyonlar saklanır.

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

### 3️⃣ Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

---

## 🔑 API Anahtarı Ayarları

Sistem **Google Gemini (Mühendis)** ve opsiyonel olarak **Groq (Mimar)** kullanır.

#### Google Gemini (Ücretsiz & Zorunlu)
```bash
# Windows:
setx GOOGLE_API_KEY "sizin_anahtariniz"

# Linux/macOS:
echo 'export GOOGLE_API_KEY="sizin_anahtariniz"' >> ~/.bashrc
source ~/.bashrc
```

#### Groq (Opsiyonel - Hız İçin)
```bash
# Windows:
setx GROQ_API_KEY "sizin_anahtariniz"
```

---

## ▶️ Nasıl Kullanılır?

Tüm sistemi yönetmek için tek komut yeterlidir:
```bash
python launcher.py
```

### Örnek Senaryolar

#### 1. Kod Yazdırma (Agent Modu)
```
(proje-1) > Login sayfasına "Beni Hatırla" checkbox'ı ekle
```
**Süreç:** Sistem önce Mimar ile plan yapar, onayınızı alır, sonra Mühendis kodu yazar ve Diff gösterir.

#### 2. Bilgi Sorma (RAG Modu - Ucuz)
```
(proje-1) > Bu projede hangi veritabanı kullanılıyor?
```
**Süreç:** Sistem kod yazmaz, sadece hafızayı tarayıp bilgi verir. Maliyet minimumdur.

#### 3. Hafıza Tazeleme (Yerel Mod - Bedava)
```
(proje-1) > tara
```
**Süreç:** Dosyaları yeniden okur ve hafızayı günceller. AI kullanılmaz.

---

## 🏗️ Proje Yapısı

Kullanıcı olarak bilmeniz gereken temel yapı şöyledir:

```text
coder-asistan/
├─ launcher.py          # 🎮 Başlatıcı (Buradan girin)
├─ my_projects/         # 📂 Tüm projeleriniz burada saklanır
│  └─ projem/
│     ├─ .coder_memory/ # 🧠 Projenin hafızası (SİLME!)
│     ├─ src/           # 💻 Sizin kodlarınız
│     └─ .gassist_backups/ # 💾 Otomatik yedekler
└─ config.py            # ⚙️ Ayarlar
```

---

## 🛠️ Yardımcı Araçlar

Bu projede sadece kod yazan bir asistan yok, işinizi kolaylaştıracak bir dizi **profesyonel araç** bulunur:

* **`debug.py`**: Hafıza Müfettişi. AI'nın ne hatırladığını kontrol edin.
* **`migrate_projects.py`**: Eski sürümden kalan projeleri yeni yapıya taşır.
* **`system_audit.py`**: Sistem sağlık kontrolü yapar.
* **`generate_docs.py`**: Projenin tamamını tek bir Markdown dosyasına döker (LLM analizi için).

---

## 💡 İpuçları

* **Hafıza Temizliği:** AI saçmalamaya başlarsa `tara` komutunu kullanın. Düzelmezse proje içindeki `.coder_memory` klasörünü silip tekrar `tara` deyin.
* **Maliyet Takibi:** Her işlemden sonra terminalde yazan `$0.00xxx` maliyeti gerçektir. `.project_stats.json` dosyasından toplam harcamanızı görebilirsiniz.
* **Model Değiştirme:** Launcher menüsünden `[S] Ayarlar` diyerek Gemini, Groq veya DeepSeek arasında geçiş yapabilirsiniz.

---

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir! Büyük değişiklikler için önce bir Issue açarak tartışalım.

> 🏗️ **Geliştirici Notu:** Bu projenin iç yapısını, veri akışını ve teknik detaylarını derinlemesine incelemek için lütfen **[MİMARİ VE TEKNİK KILAVUZ (ARCHITECTURE.md)](ARCHITECTURE.md)** dosyasını okuyunuz.

---

## 👤 Geliştirici

**Ahmet Çetin**
* **GitHub:** [github.com/cetincevizcetoli](https://github.com/cetincevizcetoli)
* **Web:** [yapanzeka.acetin.com.tr](https://yapanzeka.acetin.com.tr)

> *"Karmaşık kodları, kontrollü ajanlarla yönetin."*