
# 🤖 Proje Geliştirme Asistanı (CLI & AI Entegrasyonu)

Bu araç, yapay zeka modellerinin (Google Gemini, Hugging Face vb.) proje dosyalarınızı okumasını, anlamasını ve tek bir komutla çoklu dosya düzenlemesi yapmasını sağlayan Python tabanlı bir CLI (Komut Satırı Arayüzü) yöneticisidir.

Model bağımsız çalışacak şekilde tasarlanmıştır ve proje bütünlüğünü korumak için katı çıktı formatlarına (JSON) sadık kalır.

## 1. 🚀 Özellikler

* **Çoklu Model Desteği:** Google Gemini ve Hugging Face modelleri arasında seçim yapabilme.
* **Akıllı Bağlam (Context) Yönetimi:** Prompt içinde adı geçen dosyaları (örn: `app.py`) otomatik olarak okur ve modele iletir.
* **Güvenli Dosya Yönetimi:** Yalnızca proje dizini içinde işlem yapar.
* **Otomatik Yedekleme:** Herhangi bir değişiklikten önce dosyaların yedeğini `.gassist_backups` klasörüne alır.
* **Token Tasarrufu:** Tüm projeyi değil, sadece ilgili dosyaları okuyarak API maliyetini ve süresini düşürür.

## 2. 🛠️ Kurulum

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin.

### Gereksinimler
* Python 3.8 veya üzeri
* Google Gemini API Anahtarı (veya Hugging Face Anahtarı)

### Adım Adım Kurulum

1.  **Repoyu Klonlayın:**
    ```bash
    git clone [https://github.com/cetincevizcetoli/coder-asistan.git](https://github.com/cetincevizcetoli/coder-asistan.git)
    cd coder-asistan
    ```

2.  **Sanal Ortam Oluşturun ve Aktif Edin:**
    Bu adım, sisteminizdeki diğer Python paketleriyle çakışmayı önler.
    ```bash
    # Sanal ortamı oluştur
    python3 -m venv gemini_venv

    # Aktif et (Linux/Mac)
    source gemini_venv/bin/activate

    # Aktif et (Windows)
    # gemini_venv\Scripts\activate
    ```

3.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **API Anahtarlarını Ayarlayın:**
    Terminal oturumunuz için anahtarları tanımlayın (Kalıcı olması için `.bashrc` dosyanıza ekleyebilirsiniz).
    ```bash
    export GOOGLE_API_KEY="BURAYA_GEMINI_API_KEY_GELECEK"
    
    # (Opsiyonel) Hugging Face kullanacaksanız:
    export HUGGINGFACE_API_KEY="BURAYA_HF_TOKEN_GELECEK"
    ```

## 3. 💻 Kullanım

Asistanı proje kök dizininde şu şekilde çalıştırabilirsiniz:

```bash
python assistant.py "src/app.py dosyasına yeni bir /login route'u ekle."

İpucu: Alias (Kısayol) Tanımlama

Her seferinde uzun komut yazmamak için terminalinize şu kısayolu ekleyebilirsiniz:
Bash

alias gassist='python3 assistant.py'

Artık sadece şu şekilde kullanabilirsiniz:
Bash

gassist "README.md dosyasını güncelle ve kurulum adımlarını ekle."

4. ⚙️ Proje Yapısı

    assistant.py: Uygulamanın beyni. Dosya okuma/yazma ve AI iletişimini yönetir.

    core/: Farklı AI modellerini (Gemini, HuggingFace) yöneten modül klasörü.

    .gassist_backups/: Değiştirilen dosyaların otomatik yedekleri burada tarih damgasıyla tutulur.

    requirements.txt: Projenin çalışması için gereken minimum Python paketleri.

5. 📝 Etkili Prompt Yazma Rehberi

Asistandan en iyi verimi almak için:

    Dosya Adını Belirtin: Asistan sadece ismini verdiğiniz dosyaları okur.

        Kötü: "Hata var düzelt."

        İyi: "src/utils.py içindeki tarih formatlama hatasını düzelt."

    Net Yollar Kullanın: Yeni dosya oluştururken tam yol verin.

        İyi: "tests/test_user.py dosyasını oluştur."

    Tek Seferde Tek Görev: Karmaşık işleri parçalara bölün.

Bu proje açık kaynaklıdır ve geliştirilmeye açıktır.
