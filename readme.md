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

## 👤 Geliştirici

**Ahmet Çetin**
* **GitHub:** [github.com/cetincevizcetoli](https://github.com/cetincevizcetoli)
* **Web:** [yapanzeka.acetin.com.tr](https://yapanzeka.acetin.com.tr)

> *"Karmaşık kodları, kontrollü araçlarla yönetin."*