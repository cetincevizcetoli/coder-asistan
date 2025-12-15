# 🤖 Coder-Asistan: Terminal Tabanlı AI Kodlama Arkadaşınız

![Python](https://img.shields.io/badge/python-3.8%252B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-stable-success)

**Coder-Asistan**, tarayıcı sekmeleri arasında kaybolmadan, doğrudan terminalinizden çıkmadan kod yazmanıza, dosya yönetmenize ve proje mimarisi kurmanıza yardımcı olan hafif, modüler ve güvenli bir CLI (Komut Satırı Arayüzü) aracıdır.

## 🚀 Neden Coder-Asistan?

Piyasada birçok AI aracı varken neden bunu kullanmalısınız?

*   **🔒 Tam Gizlilik & Güvenlik:** Sadece sizin belirlediğiniz dosyaları okur. Path Traversal koruması ile sisteminizin geri kalanına dokunmaz.
*   **🔌 Model Agnostik:** Tek bir firmaya bağımlı kalmayın. İster Google Gemini (2.5 Flash) kullanın, ister açık kaynak Hugging Face (Qwen/Llama) modellerini.
*   **🛠️ Otomatik Dosya Yönetimi:** Kodu sadece ekrana yazmaz; sizin onayınızla dosyaları oluşturur, klasörleri açar ve mevcut dosyaları günceller.
*   **🛡️ Otomatik Yedekleme:** Bir dosyayı değiştirmeden önce `.gassist_backups` klasörüne yedeğini alır. Hata yapma korkusu yok!

## 🏗️ Proje Mimarisi

Bu proje, genişletilebilir ve modüler bir yapı üzerine kurulmuştur:

*   `assistant.py`: Orkestra şefi. Kullanıcı girdisini alır, AI'ya iletir, gelen JSON yanıtını işler ve dosyaları yazar.
*   `core/`: Farklı AI sağlayıcıları için adaptörler (Gemini, HF) burada bulunur. Yeni bir model eklemek için buraya bir dosya eklemeniz yeterlidir.
*   `config.py`: Tüm ayarların (token limitleri, model isimleri) merkezi.

---

## 📦 Kurulum

Projeyi bilgisayarınıza kurmak 2 dakikadan az sürer.

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/cetincevizcetoli/coder-asistan.git
cd coder-asistan
```

### 2. Sanal Ortamı Hazırlayın (Önerilen)

Sistem kütüphanelerinizi kirletmemek için sanal ortam kullanın.

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. API Anahtarlarını Tanımlayın

Projenin çalışması için bir API anahtarına ihtiyacınız var. `.env.example` dosyasındaki şablonu kullanabilirsiniz.

**Linux/Mac için (Kalıcı Yöntem):**
Terminale şu komutları yazarak `.bashrc` dosyanıza ekleyin:

```bash
# Google Gemini için (Önerilen - Ücretsiz & Hızlı)
echo 'export GOOGLE_API_KEY="Sizin_Keyiniz_Buraya"' >> ~/.bashrc

# VEYA Hugging Face için
echo 'export HUGGINGFACE_API_KEY="Sizin_Tokeniniz_Buraya"' >> ~/.bashrc

source ~/.bashrc
```

---

## 💻 Kullanım

Coder-Asistan bir CLI (Komut Satırı) aracıdır. Tüm komutlar terminal üzerinden verilir.

### Temel Komut

```bash
# Ana kullanım şekli
python assistant.py "Yapılacak işlemin tanımı"
```

### Örnek Senaryolar

**1. Sıfırdan Proje Başlatma:**
```bash
python assistant.py "Basit bir Flask projesi yap. app.py, requirements.txt ve templates/index.html dosyalarını oluştur."
```

**2. Mevcut Dosyayı Düzenleme:**
```bash
python assistant.py "index.html dosyasını Bootstrap 5 kullanacak şekilde güncelle ve bir Navbar ekle."
```

**3. Hata Ayıklama (Debug):**
```bash
python assistant.py "app.py dosyasındaki hatayı bul ve düzelt."
```

---

## ⚙️ Yapılandırma (config.py)

Projenin davranışlarını `config.py` dosyasından özelleştirebilirsiniz:

*   **MAX_FILE_SIZE:** İşlenebilecek maksimum dosya boyutu.
*   **BACKUP_DIR:** Yedeklerin tutulacağı klasör.
*   **MODEL_CONFIGS:** Kullanılan model sürümlerini buradan değiştirebilirsiniz (Örn: gemini-2.5-flash yerine pro sürümü).

### 🎛️ Gelişmiş Parametreler

**1. `--dry-run` (Prova Modu / Güvenli Mod)**
Kodu oluşturur, planı gösterir ama **dosyalara yazmaz**. Değişiklikleri kaydetmeden önce görmek için idealdir.
```bash
python assistant.py "Snake oyunu yaz" --dry-run
```
--

verbose (Detaylı Log Modu) "Geveze" modudur. AI'dan gelen ham yanıtı, JSON temizleme sürecini ve olası gizli hataları detaylı gösterir. Hata ayıklamak (debug) için kullanılır.

```bash
python assistant.py "Hata veren bir dosya üzerinde çalış" --verbose
```
## 🛠️ Ekstra Araçlar

Proje içinde, geliştirmeyi kolaylaştıran yardımcı bir script daha bulunur.

### 📄 generate_docs.py (Proje Belgeleyici)

Bu araç, projenizdeki tüm kod dosyalarını okur ve tek bir Markdown dosyasında (`proje_dokumu.md`) birleştirir.

**Neden Kullanmalıyım?**
*   Tüm projeyi tek bir dosyada toplayıp ChatGPT, Claude veya Gemini'ye "Bu projeyi analiz et" diyerek yapıştırmak için mükemmeldir.
*   Proje yedeği almak veya dokümantasyon oluşturmak için idealdir.

**Kullanım:**
```bash
python generate_docs.py
```

---

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir! Büyük değişiklikler için önce bir Issue açarak tartışalım.

1.  Forklayın
2.  Feature branch oluşturun (`git checkout -b feature/yenilik`)
3.  Commit leyin (`git commit -m 'Yeni özellik eklendi'`)
4.  Push layın (`git push origin feature/yenilik`)
5.  PR açın

---
## 🧠 Katkıda Bulunanlar & Teknoloji Yığını

Bu proje geliştirilirken aşağıdaki yapay zeka modellerinden ve açık kaynak kütüphanelerden güç alınmıştır:

### 🤖 Yapay Zeka (AI)
*   **Google Gemini (2.5 Flash):** Projenin ana mantıksal motoru ve kod üreticisi.
*   **Hugging Face (Qwen/Llama):** Açık kaynak model entegrasyonu ve alternatif zeka.

### 🛠️ Altyapı & Kütüphaneler
*   **Python 3.8+:** Ana geliştirme dili.
*   **Google GenAI SDK:** Gemini API bağlantısı.

---
**Geliştirici:** Ahmet Çetin (cetincevizcetoli)
