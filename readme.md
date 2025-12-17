# 🚀 Coder-Asistan: AI Destekli Kodlama Stüdyosu

![Python](https://img.shields.io/badge/python-3.10%252B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

**Coder-Asistan**, sadece kod yazan bir bot değil; projelerinizi yöneten, hafızası olan ve bağlamı kaybetmeden çalışan **terminal tabanlı bir geliştirme ortamıdır.**

Eski nesil botların aksine, her projeniz için ayrı bir "beyin" (Vektör Veritabanı) oluşturur. Böylece "A projesi" hakkında konuşurken, "B projesi" ile kafası karışmaz.

---

## ✨ Neden Farklı? (Yeni Mimari)

* **🏭 Proje Fabrikası (`launcher.py`):** Tüm projelerinizi tek bir menüden yönetin. Yeni proje açın, eskisine geçin veya yedekleyip zipleyin.
* **🧠 İzole Hafıza (RAG):** Her projenin kendi `.coder_memory` klasörü vardır. AI, o projeye ait tüm dosyaları okur ve hatırlar.
* **💰 Maliyet Takibi:** Hangi proje ne kadar harcadı? Token başına maliyet hesaplar ve raporlar.
* **🛡️ Güvenlik:** Kodları doğrudan yazmaz; önce JSON formatında plan sunar, onaylarsanız işler.
* **🔌 Çoklu Model Desteği:** Google Gemini (Önerilen), Llama 3 (Groq), DeepSeek veya Hugging Face. Özgürsünüz.

---

## 📦 Kurulum Rehberi (Adım Adım)

Bu bölüm, teknik bilgisi az olan kullanıcılar için **en basit haliyle** hazırlanmıştır. Lütfen işletim sisteminize uygun adımları takip edin.

### 1️⃣ Projeyi İndirin

Bilgisayarınızda projeyi kurmak istediğiniz klasöre gidin (Örn: Masaüstü) ve terminali açıp şu komutları yapıştırın:

```bash
git clone [https://github.com/cetincevizcetoli/coder-asistan.git](https://github.com/cetincevizcetoli/coder-asistan.git)
cd coder-asistan
```

### 2️⃣ Sanal Ortam Oluşturun (ÖNEMLİ!)

Bilgisayarınızdaki diğer Python projeleriyle çakışma olmaması için, bu projeye özel izole bir alan oluşturmalıyız.

**🪟 Windows Kullanıcıları:**
```cmd
python -m venv venv
venv\Scripts\activate
```
*(Komutu girdikten sonra satırın en başında `(venv)` yazısını görmelisiniz. Görmüyorsanız işlem başarısızdır.)*

**🐧 Linux / macOS Kullanıcıları:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```
*(Bu işlem internet hızınıza göre 1-2 dakika sürebilir. Kırmızı bir hata yazısı görmediyseniz işlem tamamdır.)*

---

## 🔑 API Anahtarı (Motoru Çalıştırmak)

Aracın çalışması için bir yapay zeka beynine ihtiyacı var. **Google Gemini (Ücretsiz ve Hızlı)** önerilir.

### Adım A: Anahtarı Almak
1.  [Google AI Studio](https://aistudio.google.com/app/apikey) adresine gidin.
2.  Google hesabınızla giriş yapın.
3.  **"Create API Key"** butonuna basın ve çıkan uzun şifreyi kopyalayın.

### Adım B: Anahtarı Bilgisayara Tanıtmak

**🪟 Windows İçin (Kalıcı Yöntem):**
Terminalinize şu komutu yapıştırın (`Sizin_Keyiniz` kısmını değiştirmeyi unutmayın):
```cmd
setx GOOGLE_API_KEY "AIzaSyD_Sizin_Kopyaladiginiz_Uzun_Sifre"
```
⚠️ **KRİTİK UYARI:** Bu komutu yazdıktan sonra anahtarın geçerli olması için **açık olan tüm terminalleri ve VS Code'u kapatıp yeniden açmanız ŞARTTIR.** Aksi halde "Key bulunamadı" hatası alırsınız.

**🐧 Linux / macOS İçin:**
```bash
echo 'export GOOGLE_API_KEY="AIzaSyD_Sizin_Uzun_Sifreniz"' >> ~/.bashrc
source ~/.bashrc
```

---

## ▶️ Kullanım (Launcher Menüsü)

Eskiden olduğu gibi karışık komutlar yazmanıza gerek yok. Artık her şeyi yöneten bir ana menümüz var.

Sanal ortamınız aktifken (`venv` yazıyorken) şu komutu girin:

```bash
python launcher.py
```

Karşınıza şöyle bir ekran gelecek:

```text
╔══════════════════════════════════════════╗
║   🚀 CODER-ASISTAN (Projeler: 2)         ║
╚══════════════════════════════════════════╝
[1] odev-projesi       $0.0042
[2] web-sitesi         $0.1205

[N] ✨ Yeni Proje
[E] 📦 Projeyi Paketle (Zip/Yedek)
[Q] 🚪 Çıkış
```

* **Yeni Başlayanlar:** `N` tuşuna basıp proje adını girin. Sistem sizin için `my_projects` klasöründe izole bir alan oluşturur.
* **Çalışmaya Başlamak:** Listeden proje numarasını (Örn: `1`) seçin.
* **Sohbet:** Açılan ekranda AI'ya ne yapması gerektiğini söyleyin:
    * *"Bana basit bir hesap makinesi yap."*
    * *"main.py dosyasındaki hatayı bul."*

---

## 🏗️ Yeni Proje Yapısı

Dosyalarınız nerede? Bizim sistemimiz artık düzenli bir fabrika gibi çalışır:

```text
coder-asistan/
├─ launcher.py            # 🎮 ANA KUMANDA (Bunu çalıştırın)
├─ assistant.py           # 🧠 İşlem motoru
├─ config.py              # ⚙️ Ayarlar
├─ my_projects/           # 📂 SİZİN PROJELERİNİZ BURADA
│  ├─ odev-projesi/       # 🔒 Proje 1 (İzole)
│  │  ├─ .coder_memory/   # 🧠 Bu projenin hafızası
│  │  ├─ src/             # Kodlarınız
│  │  └─ README.md
│  └─ web-sitesi/         # 🔒 Proje 2
└─ requirements.txt
```

---

## 🧩 Desteklenen Modeller

`config.py` üzerinden modeli değiştirebilirsiniz, ancak varsayılanlar şöyledir:

| Model | Hız | Maliyet | Not |
| :--- | :--- | :--- | :--- |
| **Gemini 2.5 Flash** | ⚡ Çok Hızlı | **Ücretsiz** | ✅ Başlangıç için en iyisi. |
| **Llama 3.3 (Groq)** | 🚀 Işık Hızı | Ücretsiz | Kodlama mantığı çok güçlü. |
| **DeepSeek Chat** | 🧠 Çok Zeki | Çok Ucuz | Karmaşık algoritmalar için ideal. |

---

## ❓ Sıkça Sorulan Sorular (Hata Çözümleri)

**S: `ModuleNotFoundError: No module named 'google'` hatası alıyorum.**
C: Kütüphaneler yüklenmemiş veya sanal ortam aktif değil.
1. `venv\Scripts\activate` (Windows) veya `source venv/bin/activate` (Mac) yaptığınızdan emin olun.
2. `pip install -r requirements.txt` komutunu tekrar çalıştırın.

**S: `GOOGLE_API_KEY tanımlı değil` hatası alıyorum.**
C: Anahtarı tanımladıktan sonra terminali kapatıp açmadınız. Windows'ta `setx` komutu, **yeni açılan** pencerelerde geçerli olur. VS Code'u tamamen kapatıp açın.

**S: Hafıza (Memory) çalışmıyor veya hata veriyor.**
C: Bilgisayarınızda C++ derleyicileri eksik olabilir (ChromaDB için gereklidir). Ancak endişelenmeyin, sistem otomatik olarak hafızasız moda geçip çalışmaya devam edecektir.

---

## 👤 Geliştirici

**Ahmet Çetin** (cetincevizcetoli)
* GitHub: [github.com/cetincevizcetoli](https://github.com/cetincevizcetoli)
* Web: [yapanzeka.acetin.com.tr](https://yapanzeka.acetin.com.tr/)

> *"Karmaşık kodları basitçe yönetin."*