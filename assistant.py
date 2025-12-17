import sys
import os
import re
import json
import shutil
import time
from datetime import datetime
from typing import List, Optional, Any, Tuple, Dict

try:
    import config
    from config import Colors, PRICING_RATES
    from core.memory import MemoryManager
except ImportError:
    import config

# --- SABİTLER ---
FILE_PATTERN = re.compile(r"[\w-]+\.(py|js|html|css|md|json|txt|java|cpp|h|ts|jsx|tsx|sh|env|sql|xml|yaml)", re.IGNORECASE)

# ==========================================
# 🛠️ YARDIMCI FONKSİYONLAR
# ==========================================

def is_safe_path(file_path: str, current_directory: str) -> bool:
    try:
        if os.path.isabs(file_path): return False
        if '..' in file_path: return False
        target_path = os.path.abspath(os.path.join(current_directory, file_path))
        safe_root = os.path.abspath(current_directory)
        return target_path.startswith(safe_root)
    except: return False

def clean_json_string(json_string: str) -> Optional[Dict]:
    try:
        if "```" in json_string:
            lines = json_string.split('\n')
            clean_lines = []
            capture = False
            for line in lines:
                if "```" in line: capture = not capture; continue
                if capture: clean_lines.append(line)
            json_string = "\n".join(clean_lines) if clean_lines else json_string.replace("```json", "").replace("```", "")
        json_string = json_string.strip()
        if json_string.rfind('}') != -1: json_string = json_string[:json_string.rfind('}')+1]
        return json.loads(json_string)
    except: return None

def backup_file(full_path: str) -> Optional[str]:
    if not os.path.exists(full_path): return None
    os.makedirs(config.BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{os.path.basename(full_path)}.{timestamp}.backup"
    shutil.copy(full_path, os.path.join(config.BACKUP_DIR, backup_name))
    return backup_name

def log_conversation(working_dir: str, user_prompt: str, ai_explanation: str, model_name: str, cost: float = 0.0):
    log_file = os.path.join(working_dir, ".chat_history.log")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"📅 {timestamp} | 🤖 {model_name} | 💰 ${cost:.5f}\n👤 {user_prompt}\n🤖 {ai_explanation}\n{'='*40}\n")
    except: pass

def update_project_stats(working_dir: str, usage_data: dict, model_key: str):
    stats_file = os.path.join(working_dir, ".project_stats.json")
    stats = {"total_cost": 0.0, "total_input_tokens": 0, "total_output_tokens": 0}
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r') as f: stats = json.load(f)
        except: pass

    in_tokens = usage_data.get("input_tokens", 0)
    out_tokens = usage_data.get("output_tokens", 0)
    rates = PRICING_RATES.get(model_key, {"input": 0, "output": 0})
    current_cost = ((in_tokens / 1_000_000) * rates["input"]) + ((out_tokens / 1_000_000) * rates["output"])

    stats["total_cost"] += current_cost
    stats["total_input_tokens"] += in_tokens
    stats["total_output_tokens"] += out_tokens
    
    try:
        with open(stats_file, 'w') as f: json.dump(stats, f, indent=4)
    except: pass
    return current_cost, stats["total_cost"]

def print_cost_report(current_cost: float, total_cost: float, usage_data: dict):
    in_t, out_t = usage_data.get("input_tokens", 0), usage_data.get("output_tokens", 0)
    c_str = f"${current_cost:.5f}" if config.USER_TIER != 'free' else "$0.00"
    t_str = f"${total_cost:.5f}" if config.USER_TIER != 'free' else "$0.00"
    print(f"\n{Colors.GREY}📊 Girdi: {in_t} | Çıktı: {out_t} | Maliyet: {Colors.GREEN}{c_str}{Colors.RESET}")
    print(f"{Colors.GREY}   💰 TOPLAM: {t_str}{Colors.RESET}")

def process_single_turn(prompt_text: str, model_instance: Any, working_dir: str, memory: Any, is_dry_run: bool = False):
    rag_context = ""
    if memory:
        print(f"{Colors.CYAN}🔍 Hafıza taranıyor...{Colors.RESET}")
        rag_context = memory.query(prompt_text, n_results=config.MAX_CONTEXT_RESULTS)
        if len(rag_context) > config.MAX_CONTEXT_CHARS: rag_context = rag_context[:config.MAX_CONTEXT_CHARS]

    full_prompt = f"--- BAĞLAM ---\n{rag_context}\n\n--- İSTEK ---\n{prompt_text}\n"
    print(f"{Colors.BLUE}✅ İŞLENİYOR:{Colors.RESET} {prompt_text}")
    
    ai_response_plan = {}
    current_cost = 0.0
    
    while True:
        try:
            print(f"{Colors.CYAN}⏳ {model_instance.MODEL_NAME} çalışıyor...{Colors.RESET}")
            resp = model_instance.generate_content(config.SYSTEM_INSTRUCTION, full_prompt)
            
            if isinstance(resp, str): raw = resp; usage = {}; key = "unknown"
            else: raw = resp["content"]; usage = resp["usage"]; key = resp["model_key"]

            ai_response_plan = clean_json_string(raw)
            if ai_response_plan is None: print("⚠️ Format hatası, tekrar deneniyor..."); continue

            current_cost, total_cost = update_project_stats(working_dir, usage, key)
            print_cost_report(current_cost, total_cost, usage)
            break 
        except Exception as e: print(f"\n{Colors.RED}Model Hatası: {e}{Colors.RESET}"); return

    explanation = ai_response_plan.get("aciklama", "Açıklama yok.")
    files_create = ai_response_plan.get("dosya_olustur", {})
    files_delete = ai_response_plan.get("dosya_sil", [])

    print(f"\n{Colors.MAGENTA}🤖 AI:{Colors.RESET} {Colors.CYAN}{explanation}{Colors.RESET}")
    if not files_create and not files_delete: 
        log_conversation(working_dir, prompt_text, explanation, model_instance.MODEL_NAME, current_cost); return

    print("\n📋 PLAN:")
    for p in files_create: print(f"   📂 + {p}")
    for p in files_delete: print(f"   🗑️  - {p}")
    if is_dry_run: return

    confirm = input(f"\n{Colors.GREEN}Onay? (e/h): {Colors.RESET}").strip().lower()
    if confirm == 'e':
        for p in files_delete:
            if is_safe_path(p, working_dir):
                full = os.path.join(working_dir, p)
                if os.path.exists(full): backup_file(full); os.remove(full); print(f"{Colors.RED}Silindi: {p}{Colors.RESET}")
            else: print(f"🚨 Güvenlik Engeli: {p}")

        for p, content in files_create.items():
            if is_safe_path(p, working_dir):
                full = os.path.join(working_dir, p)
                try:
                    os.makedirs(os.path.dirname(full), exist_ok=True)
                    if os.path.exists(full): backup_file(full)
                    with open(full, 'w', encoding='utf-8') as f: f.write(content)
                    print(f"{Colors.GREEN}Yazıldı: {p}{Colors.RESET}")
                    if memory: memory.index_files([p])
                except Exception as e: print(f"Hata: {e}")
            else: print(f"🚨 Güvenlik Engeli: {p}")
        log_conversation(working_dir, prompt_text, explanation, model_instance.MODEL_NAME, current_cost)
    else: print("❌ İptal.")

# ==========================================
# 🌟 MAIN (DİNAMİK MODEL YÜKLEME)
# ==========================================
def main(project_name):
    project_path = os.path.abspath(os.path.join(config.PROJECTS_DIR, project_name))
    if not os.path.exists(project_path): print("Proje yok."); return

    # --- DİNAMİK MODEL SEÇİMİ ---
    active_model_key = getattr(config, 'ACTIVE_MODEL', 'gemini')
    print(f"\n{Colors.GREEN}🚀 PROJE: {project_name.upper()} | MOTOR: {active_model_key.upper()}{Colors.RESET}")

    model_instance = None
    try:
        if active_model_key == 'groq':
            from core.groq import GroqModel
            model_instance = GroqModel()
        elif active_model_key == 'deepseek':
            from core.deepseek import DeepSeekModel
            model_instance = DeepSeekModel()
        elif active_model_key == 'huggingface':
            from core.huggingface import HuggingFaceModel
            model_instance = HuggingFaceModel()
        else:
            # Varsayılan Gemini
            from core.gemini import GeminiModel
            model_instance = GeminiModel()
            
    except Exception as e:
        print(f"{Colors.RED}Model Yüklenemedi ({active_model_key}): {e}{Colors.RESET}")
        print("Config dosyasını veya API anahtarlarını kontrol edin.")
        return

    # Hafıza
    memory = None
    try: memory = MemoryManager(project_root=project_path)
    except: pass

    print(f"{Colors.CYAN}--------------------------------------------------{Colors.RESET}")
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}{Colors.YELLOW}({project_name}) > {Colors.RESET}").strip()
            if user_input.lower() in ['exit', 'q', 'b']: break
            if not user_input: continue
            process_single_turn(user_input, model_instance, project_path, memory)
        except KeyboardInterrupt: break
        except Exception as e: print(f"Hata: {e}")

if __name__ == "__main__":
    print("Launcher kullanın.")

