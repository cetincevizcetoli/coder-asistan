import sys
import os
import re
import json
import shutil
import time
import requests
from datetime import datetime
from typing import List, Optional, Any, Tuple

# --- PROJE MODÜLLERİ ---
import config
from config import Colors, PRICING_RATES
from core.memory import MemoryManager

# --- DİNAMİK MODEL İMPORTLARI ---
try: from core.gemini import GeminiModel
except ImportError: pass
try: from core.groq import GroqModel; GROQ_AVAILABLE = True
except ImportError: GROQ_AVAILABLE = False
try: from core.deepseek import DeepSeekModel; DEEPSEEK_AVAILABLE = True
except ImportError: DEEPSEEK_AVAILABLE = False
try: from core.huggingface import HuggingFaceModel; HF_AVAILABLE = True
except ImportError: HF_AVAILABLE = False

# --- SABİTLER ---
FILE_PATTERN = re.compile(r"[\w-]+\.(py|js|html|css|md|json|txt|java|cpp|h|ts|jsx|tsx|sh|env)", re.IGNORECASE)

# ==========================================
# 🛠️ YARDIMCI FONKSİYONLAR
# ==========================================

def is_safe_path(file_path: str, current_directory: str) -> bool:
    if os.path.isabs(file_path): return False
    normalized_path = os.path.normpath(file_path)
    if normalized_path.startswith('..'): return False
    full_path = os.path.join(current_directory, file_path)
    return os.path.realpath(full_path).startswith(current_directory)

def clean_json_string(json_str: str) -> str:
    if "```" in json_str:
        json_str = re.sub(r"```json\n?|```", "", json_str)
    return json_str.strip()

def backup_file(full_path: str) -> Optional[str]:
    if not os.path.exists(full_path): return None
    os.makedirs(config.BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{os.path.basename(full_path)}.{timestamp}.backup"
    shutil.copy(full_path, os.path.join(config.BACKUP_DIR, backup_name))
    return backup_name

def extract_wait_time(error_message: str) -> int:
    match = re.search(r"retry in (\d+(\.\d+)?)s", str(error_message))
    if match: return int(float(match.group(1))) + 2 
    return 30 

def log_conversation(working_dir: str, user_prompt: str, ai_explanation: str, model_name: str, cost: float = 0.0):
    """Sohbeti ve MALİYETİ detaylı şekilde log dosyasına kaydeder."""
    log_file = os.path.join(working_dir, ".chat_history.log")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # YENİ: Maliyet satırı eklendi
    log_entry = (
        f"════════════════════════════════════════════════════════════\n"
        f"📅 ZAMAN: {timestamp} | 🤖 MODEL: {model_name}\n"
        f"💰 MALİYET: ${cost:.5f}\n"
        f"👤 USER: {user_prompt}\n"
        f"🤖 AI:   {ai_explanation}\n"
    )
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"{Colors.RED}Log Yazma Hatası: {e}{Colors.RESET}")

def update_project_stats(working_dir: str, usage_data: dict, model_key: str) -> Tuple[float, float]:
    """Toplam proje maliyetini hesaplar, kaydeder ve döner."""
    stats_file = os.path.join(working_dir, ".project_stats.json")
    
    stats = {
        "total_cost": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "last_updated": ""
    }

    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        except: pass

    in_tokens = usage_data.get("input_tokens", 0)
    out_tokens = usage_data.get("output_tokens", 0)
    rates = PRICING_RATES.get(model_key, {"input": 0, "output": 0})
    
    current_cost = ((in_tokens / 1_000_000) * rates["input"]) + ((out_tokens / 1_000_000) * rates["output"])

    stats["total_cost"] += current_cost
    stats["total_input_tokens"] += in_tokens
    stats["total_output_tokens"] += out_tokens
    stats["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=4)
    except Exception as e:
        print(f"{Colors.RED}İstatistik kayıt hatası: {e}{Colors.RESET}")

    return current_cost, stats["total_cost"]

def print_cost_report(current_cost: float, total_cost: float, usage_data: dict):
    in_tokens = usage_data.get("input_tokens", 0)
    out_tokens = usage_data.get("output_tokens", 0)

    tier_label = "ÜCRETSİZ KATMAN" if config.USER_TIER == 'free' else "ÜCRETLİ API"
    
    if config.USER_TIER == 'free':
        c_cost_str = "$0.00000"
        t_cost_str = "$0.00000"
    else:
        c_cost_str = f"${current_cost:.5f}"
        t_cost_str = f"${total_cost:.5f}"

    print(f"\n{Colors.GREY}📊 FİNANSAL RAPOR ({tier_label}){Colors.RESET}")
    print(f"{Colors.GREY}   ├── Bu İşlem:  Girdi: {in_tokens:<5} | Çıktı: {out_tokens:<5} | Maliyet: {Colors.GREEN}{c_cost_str}{Colors.RESET}")
    print(f"{Colors.GREY}   └── 💰 TOPLAM: {Colors.CYAN}Proje Geneli Harcama: {t_cost_str}{Colors.RESET}")

# ==========================================
# 🚀 ANA İŞLEM DÖNGÜSÜ
# ==========================================

def main_process(prompt_text: str, model_instance: Any, working_dir: str, is_dry_run: bool = False):
    
    try: memory = MemoryManager(project_root=working_dir)
    except: memory = None

    if memory:
        all_files = []
        for root, dirs, files in os.walk(working_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if FILE_PATTERN.match(file):
                    rel_path = os.path.relpath(os.path.join(root, file), working_dir)
                    all_files.append(rel_path)
        if all_files: memory.index_files(all_files)

    rag_context = ""
    if memory:
        print(f"{Colors.CYAN}🔍 Hafıza taranıyor...{Colors.RESET}")
        rag_context = memory.query(prompt_text, n_results=config.MAX_CONTEXT_RESULTS)
        if len(rag_context) > config.MAX_CONTEXT_CHARS:
            rag_context = rag_context[:config.MAX_CONTEXT_CHARS] + "\n...(Kırpıldı)..."

    full_prompt = (
        f"--- PROJE BAĞLAMI ---\n{rag_context}\n\n"
        f"--- KULLANICI İSTEĞİ ---\n{prompt_text}\n"
    )
        
    print(f"{Colors.BLUE}✅ GÖREV:{Colors.RESET} {prompt_text}")
    if is_dry_run: print(f"{Colors.YELLOW}🧪 (DRY-RUN AKTİF){Colors.RESET}")

    ai_response_plan = {} 
    
    # Maliyet değişkenleri
    current_cost = 0.0
    total_cost = 0.0

    # 4. MODEL ÇALIŞTIRMA
    while True:
        masked_key = os.getenv("GOOGLE_API_KEY", "")[:5] + "..."
        print(f"{Colors.CYAN}⏳ {model_instance.MODEL_NAME} düşünüyor... (Key: {masked_key}){Colors.RESET}")
        
        try:
            response_data = model_instance.generate_content(
                system_instruction=config.SYSTEM_INSTRUCTION,
                prompt_text=full_prompt
            )
            
            if isinstance(response_data, str):
                raw_text = response_data; usage_info = {}; model_key_used = "unknown"
            else:
                raw_text = response_data["content"]; usage_info = response_data["usage"]; model_key_used = response_data["model_key"]

            clean_response = clean_json_string(raw_text)
            
            try:
                ai_response_plan = json.loads(clean_response)
            except json.JSONDecodeError:
                print(f"{Colors.YELLOW}⚠️ Uyarı: AI eski formatta yanıt verdi, dönüştürülüyor...{Colors.RESET}")
                temp_dict = json.loads(clean_response)
                ai_response_plan = {
                    "aciklama": "AI açıklama sağlamadı.",
                    "dosya_olustur": temp_dict,
                    "dosya_sil": []
                }

            # --- MALİYET HESAPLAMA ---
            current_cost, total_cost = update_project_stats(working_dir, usage_info, model_key_used)
            print_cost_report(current_cost, total_cost, usage_info)
            break 

        except requests.exceptions.ConnectionError:
            print(f"\n{Colors.RED}📡 İNTERNET BAĞLANTISI YOK!{Colors.RESET}")
            if input("Tekrar? (e/h): ").lower() != 'e': return
        
        except Exception as e:
            err_str = str(e)
            print(f"\n{Colors.RED}💣 HATA: {e}{Colors.RESET}")
            if "429" in err_str:
                wait_time = extract_wait_time(err_str)
                print(f"{Colors.YELLOW}🚦 Kota doldu ({wait_time}s). [1] Bekle [2] Model Seç [3] İptal{Colors.RESET}")
                c = input("Seçim: ")
                if c == "1":
                    time.sleep(wait_time); continue
                elif c == "2":
                    from model_selector import select_model_interactive
                    m = select_model_interactive()
                    if m: model_instance = m
                    continue
                else: return
            else:
                if input("Tekrar? (e/h): ").lower() != 'e': return

    # --- PLANLAMA ---
    explanation = ai_response_plan.get("aciklama", "Açıklama yok.")
    files_to_create = ai_response_plan.get("dosya_olustur", {})
    files_to_delete = ai_response_plan.get("dosya_sil", [])

    print(f"\n{Colors.MAGENTA}🤖 AI DİYOR Kİ:{Colors.RESET}")
    print(f"{Colors.CYAN}{explanation}{Colors.RESET}")
    
    print("\n📋 PLANLANAN DEĞİŞİKLİKLER:")
    for path in files_to_create.keys(): print(f"   📂 OLUŞTUR/GÜNCELLE: {path}")
    for path in files_to_delete: print(f"   🗑️  SİLİNECEK: {path}")

    if not files_to_create and not files_to_delete:
        print(f"{Colors.YELLOW}   (İşlem yok){Colors.RESET}")
        log_conversation(working_dir, prompt_text, explanation, model_instance.MODEL_NAME, current_cost)
        return

    if is_dry_run:
        print(f"\n{Colors.YELLOW}🧪 DRY-RUN Bitti.{Colors.RESET}")
        return

    if input(f"\n{Colors.GREEN}Onaylıyor musunuz? (e/h): {Colors.RESET}").lower() != 'e':
        print("❌ İptal edildi.")
        return

    # --- UYGULAMA ---
    for rel_path in files_to_delete:
        if not is_safe_path(rel_path, working_dir): continue
        full_path = os.path.join(working_dir, rel_path)
        if os.path.exists(full_path):
            try:
                backup_file(full_path)
                os.remove(full_path)
                print(f"{Colors.RED}   🗑️  Silindi: {rel_path}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}   ❌ Silinemedi: {rel_path} ({e}){Colors.RESET}")

    for rel_path, content in files_to_create.items():
        if not is_safe_path(rel_path, working_dir):
            print(f"{Colors.RED}🚨 Engellendi: {rel_path}{Colors.RESET}")
            continue
        full_path = os.path.join(working_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if os.path.exists(full_path): backup_file(full_path)
        with open(full_path, 'w', encoding='utf-8') as f: f.write(content)
        print(f"{Colors.GREEN}   ✅ Yazıldı: {rel_path}{Colors.RESET}")
        if memory: memory.index_files([rel_path])

    # Loglama (Maliyet parametresi eklendi)
    log_conversation(working_dir, prompt_text, explanation, model_instance.MODEL_NAME, current_cost)


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    
    raw_args = sys.argv[1:]
    is_dry_run = "--dry-run" in raw_args
    cleaned_args = [a for a in raw_args if a != "--dry-run" and a != "--verbose"]
    prompt = " ".join(cleaned_args)
    cwd = os.getcwd()
    
    from model_selector import select_model_interactive
    model = select_model_interactive()
    if model: main_process(prompt, model, cwd, is_dry_run=is_dry_run)