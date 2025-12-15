# 🤖 Coder-Asistan

**AI destekli otomatik kod üretme ve proje yönetim aracı**

Gemini veya Hugging Face modelleriyle çalışan, dosya oluşturma/güncelleme işlemlerini otomatikleştiren terminal tabanlı asistan.

---

## ✨ Özellikler

- 🎯 **Çoklu AI Model Desteği** (Google Gemini, Hugging Face)
- 📁 **Otomatik Dosya Yönetimi** (Oluşturma, güncelleme, yedekleme)
- 🔒 **Güvenlik Önlemleri** (Path traversal koruması)
- 🎨 **Renkli Terminal UI**
- 🧪 **Dry-Run Modu** (Test için)
- 📝 **Verbose Mod** (Debug için)
- 🔄 **Otomatik Yedekleme** (Değişiklik öncesi)

---

## 📦 Kurulum

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/cetincevizcetoli/coder-asistan.git
cd coder-asistan
```

### 2. Sanal Ortam Oluşturun
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. API Anahtarlarını Ayarlayın

**.bashrc veya .zshrc dosyanıza ekleyin:**
```bash
# Google Gemini için
export GOOGLE_API_KEY='your-gemini-api-key-here'

# Hugging Face için (opsiyonel)
export HUGGINGFACE_API_KEY='your-hf-token-here'
```

Sonra terminali yenileyin:
```bash
source ~/.bashrc  # veya source ~/.zshrc
```

### 5. Kurulumu Test Edin
```bash
python check_models.py
```

---

## 🚀 Kullanım

### Temel Kullanım
```bash
python assistant.py "src/app.py dosyası oluştur ve Flask ile bir API yaz"
```

### Verbose Mod (Debug)
```bash
python assistant.py "config.json oluştur" --verbose
```

### Dry-Run (Kaydetsiz Test)
```bash
python assistant.py "tüm dosyaları güncelle" --dry-run
```

---

## 📖 Kullanım Örnekleri

### Örnek 1: Yeni Dosya Oluşturma
```bash
python assistant.py "Python'da bir hesap makinesi programı oluştur (calculator.py)"
```

### Örnek 2: Mevcut Dosyayı Güncelleme
```bash
python assistant.py "app.py dosyasına yeni bir /health endpoint ekle"
```

### Örnek 3: Çoklu Dosya
```bash
python assistant.py "React ile bir Todo uygulaması yap: src/App.js, src/TodoList.js ve README.md oluştur"
```

### Örnek 4: Bağlam ile Çalışma
```bash
python assistant.py "config.py dosyasını oku ve database ayarlarını ekle"
```

---

## 🛠️ Yapılandırma

**config.py** dosyasından şunları özelleştirebilirsiniz:

- Maksimum dosya boyutu
- Yedekleme limitleri
- Model parametreleri
- System instruction

---

## 🧪 Geliştirme

### Yeni Model Eklemek

1. `core/` klasöründe yeni model sınıfı oluşturun
2. `BaseModel`'den miras alın
3. `config.py` içine model ayarlarını ekleyin
4. `model_selector.py` içinde model kontrolünü ekleyin

**Örnek:**
```python
# core/openai.py
from .base import BaseModel

class OpenAIModel(BaseModel):
    MODEL_NAME = "GPT-4"
    
    def generate_content(self, system_instruction, prompt_text):
        # OpenAI API implementasyonu
        pass
```

---

## 🐛 Sorun Giderme

### "Model yüklenemedi" Hatası
```bash
# API anahtarını kontrol edin
echo $GOOGLE_API_KEY

# Boşsa yeniden ayarlayın
export GOOGLE_API_KEY='your-key'
```

### "JSON Parse Hatası"
- AI bazen geçersiz format döndürebilir
- `--verbose` ile ham çıktıyı kontrol edin
- System instruction'ı daha katı hale getirin

### Karakter Kodlama Sorunları
```bash
# Dosyaları UTF-8'e çevirin
iconv -f ISO-8859-9 -t UTF-8 assistant.py > assistant_fixed.py
```

---

## 📁 Proje Yapısı

```
coder-asistan/
├── assistant.py          # Ana program
├── config.py            # Yapılandırma
├── model_selector.py    # Model seçici
├── check_models.py      # Diagnostic tool
├── requirements.txt     # Bağımlılıklar
├── core/
│   ├── base.py         # Soyut sınıf
│   ├── gemini.py       # Google Gemini
│   └── huggingface.py  # Hugging Face
└── .gassist_backups/   # Otomatik yedekler
```

---

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

---

## 📄 Lisans

MIT License - Detaylar için `LICENSE` dosyasına bakın

---

## 🙏 Teşekkürler

- Google Gemini API
- Hugging Face Inference API
- Tüm açık kaynak katkıda bulunanlar

---

## 📞 İletişim

**GitHub:** [@cetincevizcetoli](https://github.com/cetincevizcetoli)

**Sorularınız için:** Issue açın veya Pull Request gönderin!
