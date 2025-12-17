# 🚀 Coder-Asistan
### Hafızalı, Güvenli ve Proje Odaklı AI Kodlama Stüdyosu (Terminal Tabanlı)

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

**Coder-Asistan**, klasik "soru sor – cevap al" botlarından farklı olarak, projelerinizi yöneten, bağlamı hatırlayan ve kodu **kontrollü şekilde** değiştiren **terminal tabanlı bir AI geliştirme ortamıdır.**

Her proje için ayrı bir hafıza oluşturur. Bir projede öğrendiğini diğerine taşımaz. Ne yaptığını önce planlar, sonra siz onaylarsanız uygular.

> **Kısaca:** Bu bir bot değil, **AI destekli bir geliştirme çalışma alanı**.

---

## 🎯 Kimler İçin?

- Terminal ile çalışmayı seven geliştiriciler
- Birden fazla projeyi aynı anda AI ile yönetenler
- Kodunu AI’ya körü körüne emanet etmek istemeyenler
- Harcadığı token ve maliyeti görmek isteyenler
- "Proje bazlı hafıza" isteyenler

---

## ❗ Bu Proje Ne Değildir?

- ❌ ChatGPT veya web tabanlı bir sohbet aracı değildir.
- ❌ Bir IDE eklentisi değildir.
- ❌ Kodları siz fark etmeden sessizce değiştirmez.
- ❌ Tek seferlik script yazan basit bir bot değildir.

---

## ✨ Neden Farklı?

### 🧠 Proje Bazlı İzole Hafıza (RAG)
Her proje için ayrı bir `.coder_memory` oluşturur. AI yalnızca o projeye ait dosyaları okur ve hatırlar.

### 🛡️ Güvenli Çalışma Modeli
AI şu adımları izler:
1. Önce **JSON formatında plan** üretir.
2. Hangi dosyaların oluşturulacağını/silineceğini gösterir.
3. Siz onaylarsanız işlemi uygular.

### 💰 Maliyet Takibi
- Proje bazlı toplam harcama takibi.
- Token giriş/çıkış sayıları.
- `.project_stats.json` ile şeffaf kayıt.

### 🏭 Proje Fabrikası (Launcher)
- Tek menüden tüm projeleri yönetme.
- Yeni proje sihirbazı.
- Proje zip/yedekleme.
- Sohbet geçmişi ve maliyet özeti.

### 🔌 Çoklu Model Desteği
- Google Gemini (Önerilen)
- Groq Llama 3
- DeepSeek
- Hugging Face

---

## 📦 Kurulum (Adım Adım)

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
*(Terminal başında `(venv)` yazısını görmelisiniz.)*

### 3️⃣ Gerekli Paketleri Kurun
```bash
pip install -r requirements.txt
```

---

## 🔑 API Anahtarı (Motoru Çalıştırmak)

Coder-Asistan bir AI modele ihtiyaç duyar. **Google Gemini (Ücretsiz ve Hızlı)** önerilir.

### Anahtar Alma
1. [Google AI Studio](https://aistudio.google.com/app/apikey) adresine gidin.
2. Google hesabı ile giriş yapın.
3. **"Create API Key"** diyerek anahtarı kopyalayın.

### Ortam Değişkeni Olarak Tanımlama

**🪟 Windows (Kalıcı):**
```cmd
setx GOOGLE_API_KEY "SIZIN_API_KEYINIZ"
```
> ⚠️ **Uyarı:** Bu komuttan sonra geçerli olması için açık olan tüm terminalleri ve VS Code’u kapatıp açmanız gerekir.

**🐧 Linux / macOS:**
```bash
echo 'export GOOGLE_API_KEY="SIZIN_API_KEYINIZ"' >> ~/.bashrc
source ~/.bashrc
```

---

## ▶️ Kullanım

Sanal ortam aktifken (`venv`) şu komutu çalıştırın:

```bash
python launcher.py
```

**Örnek Ekran:**
```text
╔══════════════════════════════════════════╗
║   🚀 CODER-ASISTAN (Projeler: 2)         ║
╚══════════════════════════════════════════╝
[1] odev-projesi       $0.0042
[2] web-sitesi         $0.1205

[N] ✨ Yeni Proje
[E] 📦 Projeyi Paketle
[Q] 🚪 Çıkış
```

* **N:** Yeni proje oluştur.
* **Numara:** Projeye gir.
* **İçeride AI’ya doğal dilde görev ver:**
    * *"Bu projeyi analiz et"*
    * *"main.py içindeki hatayı bul"*
    * *"Basit bir REST API oluştur"*

---

## 🏗️ Proje Yapısı

```text
coder-asistan/
├─ launcher.py          # 🎮 Ana kontrol merkezi (Başlatıcı)
├─ assistant.py         # 🧠 AI işlem motoru
├─ config.py            # ⚙️ Ayarlar
├─ core/                # 🤖 Model entegrasyonları
├─ my_projects/         # 📂 SİZİN PROJELERİNİZ BURADA
│  └─ proje-adi/
│     ├─ .coder_memory/
│     ├─ src/
│     └─ README.md
└─ requirements.txt
```

---

## 🧩 Desteklenen Modeller

| Model | Hız | Maliyet | Not |
| :--- | :--- | :--- | :--- |
| **Gemini 2.5 Flash** | ⚡⚡⚡ | **Ücretsiz** | Başlangıç için ideal |
| **Llama 3.3 (Groq)** | 🚀 | Ücretsiz | Çok hızlı |
| **DeepSeek Chat** | 🧠 | Düşük | Karmaşık işler |
| **HF Qwen** | 🛠️ | Ücretsiz | Alternatif |

---

## ❓ Sık Karşılaşılan Hatalar

* **`ModuleNotFoundError: google`**
    * Sanal ortam aktif değil veya paketler kurulmamış (`pip install -r requirements.txt`).
* **`GOOGLE_API_KEY tanımlı değil`**
    * Anahtarı tanımladıktan sonra terminali kapatıp açmadınız.
* **Hafıza (ChromaDB) hata veriyor**
    * Sistem otomatik olarak hafızasız (no-memory) moda geçer ve çalışmaya devam eder. Endişelenmeyin.

---

## 👤 Geliştirici

**Ahmet Çetin**
* **GitHub:** [github.com/cetincevizcetoli](https://github.com/cetincevizcetoli)
* **Web:** [yapanzeka.acetin.com.tr](https://yapanzeka.acetin.com.tr)

> *"Karmaşık kodları, kontrollü şekilde yönetin."*