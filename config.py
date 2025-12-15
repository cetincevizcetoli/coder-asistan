# config.py
import os

# --- RENKLER ---
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# --- DOSYA AYARLARI ---
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_TOTAL_SIZE = 20 * 1024 * 1024
BACKUP_DIR = ".gassist_backups"
HISTORY_LOG = ".gassist_history.log"
MAX_BACKUPS_PER_FILE = 10

# --- MODEL AYARLARI ---
MODEL_CONFIGS = {
    "gemini": {
        "env_var": "GOOGLE_API_KEY",
        "model_name": "gemini-2.5-flash", # En standart isim
        "display_name": "gemini-2.5-flash"
    },
    "huggingface": {
        "env_var": "HUGGINGFACE_API_KEY",
        "model_id": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "display_name": "Hugging Face (Qwen 2.5 Coder)"
    }
}

# --- SYSTEM PROMPT ---
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