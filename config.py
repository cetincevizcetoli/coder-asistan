import os

# ==========================================
# 🎨 RENK AYARLARI
# ==========================================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    GREY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# ==========================================
# ⚙️ SİSTEM VE DOSYA AYARLARI
# ==========================================
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_TOTAL_SIZE = 20 * 1024 * 1024
BACKUP_DIR = ".gassist_backups"
MAX_BACKUPS_PER_FILE = 5
MEMORY_DIR_NAME = ".coder_memory"
COLLECTION_NAME = "project_codebase"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
MAX_CONTEXT_RESULTS = 3
MAX_CONTEXT_CHARS = 12000
MAX_BACKUPS_PER_FILE = 10


# YENİ: Projelerin toplanacağı ana klasör
PROJECTS_DIR = "my_projects"

# ==========================================
# 💰 MALİYET VE KATMAN
# ==========================================
USER_TIER = 'free' 
PRICING_RATES = {
    "gemini-2.5-flash-lite": { "input": 0.075, "output": 0.30 },
    "gemini-2.5-flash": { "input": 0.10, "output": 0.40 },
    "llama-3.3-70b-versatile": { "input": 0.59, "output": 0.79 },
    "deepseek-chat": { "input": 0.14, "output": 0.28 },
    "Qwen/Qwen2.5-Coder-7B-Instruct": { "input": 0.0, "output": 0.0 }
}

# ==========================================
# 🤖 MODEL AYARLARI
# ==========================================

MODEL_CONFIGS = {
    "gemini": {
        "env_var": "GOOGLE_API_KEY",
        "model_name": "gemini-2.5-flash-lite", 
        "display_name": "Google Gemini 2.5 Flash Lite",
    },
    "groq": {
        "env_var": "GROQ_API_KEY",
        "model_id": "llama-3.3-70b-versatile",
        "display_name": "Groq Llama 3.3 70B",
    },
    "deepseek": {
        "env_var": "DEEPSEEK_API_KEY",
        "model_id": "deepseek-chat",
        "display_name": "DeepSeek Chat",
    },
    "huggingface": {
        "env_var": "HUGGINGFACE_API_KEY",
        "model_id": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "display_name": "Hugging Face Qwen",
    }
}
ACTIVE_PROFILE = 'gemini'
# ==========================================
# 🚀 AKTİF PROFİL SEÇİMİ (Eksik Olan Kısım)
# ==========================================
# Buraya MODEL_CONFIGS içindeki anahtarlardan birini yazmalısın:
# Seçenekler: 'gemini', 'groq', 'deepseek', 'huggingface'


# ==========================================
# 🧠 YENİ AI SİSTEM TALİMATI (Akıllı JSON Modu)
# ==========================================
SYSTEM_INSTRUCTION = (
    "Sen uzman bir yazılım mimarı ve kodlama asistanısın. "
    "Görevin: Verilen talimatlara ve RAG hafızasından gelen bağlama göre projeyi yönetmektir.\n"
    "KURALLAR:\n"
    "1. Yanıtın SADECE ve SADECE geçerli bir JSON objesi olmalıdır.\n"
    "2. JSON formatı ŞU ŞEKİLDE OLMALIDIR:\n"
    "{\n"
    "  'aciklama': 'Yaptığınız işlemin kısa bir özeti ve nedeni (Örn: Hatalı yolu düzelttim)',\n"
    "  'dosya_olustur': {'dosya_yolu': 'icerik', 'dosya_yolu2': 'icerik'},\n"
    "  'dosya_sil': ['silinecek_dosya_yolu_1', 'silinecek_dosya_yolu_2']\n"
    "}\n"
    "3. Eğer silinecek dosya yoksa 'dosya_sil': [] gönder.\n"
    "4. Asla Markdown (```json ... ```) kullanma, sadece saf JSON döndür.\n"
    "5. Türkçe karakterleri UTF-8 olarak koru."
)


# ==========================================
# 🧠 HAFIZA PROFİLLERİ (Menüde Görünecekler)
# ==========================================
MEMORY_PROFILES = {
    "1": {
        "model_name": "all-MiniLM-L6-v2",
        "display": "Hafif (Light)",
        "desc": "🚀 En Hızlısı | Düşük RAM | 384 Boyut | Genel projeler için ideal.",
        "dim": 384
    },
    "2": {
        "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
        "display": "Dengeli (Medium)",
        "desc": "⚖️  Daha İyi Türkçe | Orta Hız | 384 Boyut | Karmaşık metinler için.",
        "dim": 384
    },
    "3": {
        "model_name": "all-mpnet-base-v2",
        "display": "Güçlü (Heavy)",
        "desc": "🧠 En Yüksek Doğruluk | Yavaş | 768 Boyut | Akademik/Derin analiz için.",
        "dim": 768
    }
}
# ==========================================
# 🚀 AKTİF MODEL VE HAFIZA SEÇİMİ
# ==========================================
# Seçenekler: 'gemini', 'groq', 'deepseek', 'huggingface'
ACTIVE_MODEL = "gemini" 

# Hafıza Ayarı
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
