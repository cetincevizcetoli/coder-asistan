import os

# ==========================================
# 🎨 RENK AYARLARI (Terminal Çıktısı İçin)
# ==========================================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# ==========================================
# ⚙️ SİSTEM VE DOSYA AYARLARI
# ==========================================
# Dosya okuma/yazma limitleri (Sihirli sayılar burada toplandı)
MAX_FILE_SIZE = 5 * 1024 * 1024        # 5 MB (Tek dosya limiti)
MAX_TOTAL_SIZE = 20 * 1024 * 1024      # 20 MB (Toplam proje okuma limiti)
BACKUP_DIR = ".gassist_backups"        # Yedekleme klasörü
HISTORY_LOG = ".gassist_history.log"   # Log dosyası
MAX_BACKUPS_PER_FILE = 10              # Bir dosya için tutulacak max yedek



# ==========================================
# 🤖 MODEL AYARLARI (Deklarasyon)
# ==========================================
# Not: API Anahtarları (Secret) burada değil, os.getenv ile çekilecek.
MODEL_CONFIGS = {
    "gemini": {
        "env_var": "GOOGLE_API_KEY",
        "model_name": "gemini-2.5-flash",
        "display_name": "Google Gemini 2.5 Flash",
    },
    "groq": {  # YENİ EKLEME
        "env_var": "GROQ_API_KEY",
        "model_id": "llama-3.1-70b-versatile",
        "display_name": "Groq Llama 3.1 70B (ÖNERİLEN ✨)",
    },
    "huggingface": {
        "env_var": "HUGGINGFACE_API_KEY",
        "model_id": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "display_name": "Hugging Face Qwen",
    }
}

# (Dosyanın geri kalanı aynı kalacak)

# ==========================================
# 🧠 AI SİSTEM TALİMATI (System Prompt)
# ==========================================
SYSTEM_INSTRUCTION = (
    "Sen uzman bir yazılım mimarı ve kodlama asistanısın. "
    "Görevin: Verilen talimatlara göre dosya yapısını oluşturmak veya güncellemektir.\n"
    "KURALLAR:\n"
    "1. Yanıtın SADECE ve SADECE geçerli bir JSON objesi olmalıdır.\n"
    "2. JSON formatı: {'dosya_yolu': 'dosya_icerigi'}\n"
    "3. Asla Markdown (```json ... ```) kullanma, sadece saf JSON döndür.\n"
    "4. Sohbet etme, açıklama yapma, sadece JSON ver.\n"
    "5. Türkçe karakterleri UTF-8 olarak koru."
)
