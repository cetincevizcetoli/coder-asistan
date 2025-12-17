import sys
import os
import re
import json
import shutil
import difflib
import time
from datetime import datetime
from typing import List, Optional, Any, Tuple, Dict

# --- PROJE MODÜLLERİ ---
try:
    import config
    from config import Colors, PRICING_RATES
    from core.memory import MemoryManager
    from core.gemini import GeminiModel 
    from core.orchestrator import AgentOrchestrator
except ImportError:
    print("⚠️  Kritik modüller yüklenemedi. Lütfen kütüphanelerin yüklü olduğundan emin olun.")

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

def show_diff(file_path: str, old_content: str, new_content: str):
    """Dosyadaki değişiklikleri terminalde görsel olarak gösterir."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}🔍 DEĞİŞİKLİK ÖZETİ ({file_path}):{Colors.RESET}")
    
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(old_lines, new_lines, fromfile='Eski', tofile='Yeni', n=0)
    
    has_changes = False
    for line in diff:
        has_changes = True
        if line.startswith('+') and not line.startswith('+++'):
            print(f"{Colors.GREEN}{line.strip()}{Colors.RESET}")
        elif line.startswith('-') and not line.startswith('---'):
            print(f"{Colors.RED}{line.strip()}{Colors.RESET}")
        elif line.startswith('@@'):
            print(f"{Colors.MAGENTA}{line.strip()}{Colors.RESET}")
            
    if not has_changes:
        print(f"{Colors.GREY}Değişiklik tespit edilmedi (içerik aynı).{Colors.RESET}")    

def clean_json_string(json_string: str) -> Optional[Dict]:
    if isinstance(json_string, dict): return json_string
    try:
        if "```" in json_string:
            lines = json_string.split('\n')
            clean_lines = []
            capture = False
            for line in lines:
                if "```" in line:
                    capture = not capture
                    continue
                if capture:
                    clean_lines.append(line)
            json_string = "\n".join(clean_lines) if clean_lines else json_string.replace("```json", "").replace("```", "")

        json_string = json_string.strip()
        if json_string.rfind('}') != -1:
            json_string = json_string[:json_string.rfind('}')+1]
        
        return json.loads(json_string)
    except Exception:
        return None

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
    log_entry = (
        f"{'═'*60}\n📅 ZAMAN: {timestamp} | 🤖 MODEL: {model_name}\n"
        f"💰 MALİYET: ${cost:.5f}\n👤 USER: {user_prompt}\n🤖 AI:   {ai_explanation}\n"
    )
    try:
        with open(log_file, "a", encoding="utf-8") as f: f.write(log_entry)
    except: pass

def update_project_stats(working_dir: str, usage_data: dict, model_key: str) -> Tuple[float, float]:
    stats_file = os.path.join(working_dir, ".project_stats.json")
    stats = {"total_cost": 0.0, "total_input_tokens": 0, "total_output_tokens": 0, "last_updated": ""}
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f: stats = json.load(f)
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
        with open(stats_file, 'w', encoding='utf-8') as f: json.dump(stats, f, indent=4)
    except: pass
    return current_cost, stats["total_cost"]

# ==========================================
# 🚀 ANA İŞLEM MOTORU (AGENTIC)
# ==========================================

def process_single_turn(prompt_text: str, orchestrator: AgentOrchestrator, working_dir: str, memory: Any, is_dry_run: bool = False):
    """Hibrit RAG bağlamı ile isteği akıllıca yönlendirir."""
    
    # 1. HİBRİT HAFIZA SORGUSU (Bağlamı her durumda alıyoruz)
    rag_context = ""
    if memory:
        print(f"{Colors.CYAN}🔍 Hibrit Hafıza taranıyor...{Colors.RESET}")
        rag_context = memory.query(prompt_text, n_results=config.MAX_CONTEXT_RESULTS)
        if len(rag_context) > config.MAX_CONTEXT_CHARS:
            rag_context = rag_context[:config.MAX_CONTEXT_CHARS] + "\n...(Kırpıldı)..."

    # --- 🛡️ 1. GÜNCELLENMİŞ SİSTEMSEL KOMUT FİLTRESİ (KISA DEVRE) ---
    sorgu_temiz = prompt_text.lower().strip()
    sistem_komutlari = ["tara", "indeksle", "hafızayı güncelle", "yenile", "reindex"]
    aksiyon_kelimeleri = ["yerine", "yap", "değiştir", "ekle", "düzelt", "sil"]
    
    # Sadece sistemle ilgiliyse ve değişiklik/aksiyon içermiyorsa kısa devre yap
    if any(k in sorgu_temiz for k in sistem_komutlari) and not any(x in sorgu_temiz for x in aksiyon_kelimeleri):
        print(f"{Colors.GREEN}⚙️  Sistem işlemi algılandı, dosyalar taranıyor...{Colors.RESET}")
        if memory:
            files = [f for f in os.listdir(working_dir) if FILE_PATTERN.match(f)]
            memory.index_files(files)
            print(f"{Colors.GREEN}✅ Hafıza güncellendi. Artık sorularınızı sorabilirsiniz.{Colors.RESET}")
            return 

    # --- 🛡️ 2. FİLTRE: BİLGİ SORGUSU / SORU MODU ---
    soru_kelimeleri = ["nedir", "kaç", "nasıl", "kim", "nerede", "neden", "bilgi ver", "anlat", "?"]
    is_question = any(q in sorgu_temiz for q in soru_kelimeleri)

    if is_question and not any(x in sorgu_temiz for x in aksiyon_kelimeleri):
        print(f"{Colors.MAGENTA}ℹ️  Soru algılandı, doğrudan yanıtlanıyor...{Colors.RESET}")
        try:
            raw_res = orchestrator.developer.generate_content(
                "Sen bilgili bir yazılım asistanısın. SADECE kullanıcıya bilgi ver. Kod yazma, dosya değiştirme planı yapma.",
                f"HAFIZADAN GELEN BİLGİLER:\n{rag_context}\n\nKULLANICI SORUSU: {prompt_text}"
            )
            content = raw_res["content"] if isinstance(raw_res, dict) else str(raw_res)
            print(f"\n{Colors.MAGENTA}🤖 CEVAP:{Colors.RESET} {Colors.CYAN}{content}{Colors.RESET}")
            
            if isinstance(raw_res, dict):
                current_cost, total_cost = update_project_stats(working_dir, raw_res.get("usage", {}), raw_res.get("model_key", ""))
                print(f"{Colors.GREY}📊 Maliyet: ${current_cost:.5f}{Colors.RESET}")
            return
        except Exception as e:
            print(f"{Colors.RED}Soru yanıtlanırken hata oluştu: {e}{Colors.RESET}")
            return

    # --- 3. NORMAL AKIŞ: ORCHESTRATOR (MİMAR + MÜHENDİS) ---
    raw_response = orchestrator.execute_workflow(prompt_text, rag_context, working_dir)
    
    if not raw_response:
        print(f"{Colors.YELLOW}⚠️ İşlem durduruldu veya iptal edildi.{Colors.RESET}")
        return

    # 4. YANIT ANALİZİ
    if isinstance(raw_response, dict):
        content = raw_response.get("content", "")
        usage = raw_response.get("usage", {})
        model_key = raw_response.get("model_key", "unknown")
    else:
        content = raw_response
        usage = {}
        model_key = "unknown"

    ai_response_plan = clean_json_string(content)
    
    if ai_response_plan is None:
        print(f"{Colors.RED}❌ Mühendis yanıtı JSON formatında değil. İşlem iptal edildi.{Colors.RESET}")
        return

    # İstatistik ve Maliyet
    current_cost, total_cost = update_project_stats(working_dir, usage, model_key)
    print(f"\n{Colors.GREY}📊 İşlem Maliyeti: {Colors.GREEN}${current_cost:.5f}{Colors.RESET} (Proje Toplamı: ${total_cost:.5f})")

    # 5. UYGULAMA (Dosya İşlemleri)
    explanation = ai_response_plan.get("aciklama", "İşlem tamamlandı.")
    files_create = ai_response_plan.get("dosya_olustur", {})
    files_delete = ai_response_plan.get("dosya_sil", [])

    print(f"\n{Colors.MAGENTA}🤖 SONUÇ:{Colors.RESET} {Colors.CYAN}{explanation}{Colors.RESET}")
    
    if is_dry_run: return

    # Silme
    for p in files_delete:
        if is_safe_path(p, working_dir):
            full = os.path.join(working_dir, p)
            if os.path.exists(full):
                backup_file(full); os.remove(full)
                print(f"{Colors.RED}🗑️ Silindi: {p}{Colors.RESET}")

    # Yazma
    new_files = []
    # ... (Dosya Yazma Döngüsü İçinde) ...
    for p, content in files_create.items():
        if is_safe_path(p, working_dir):
            full = os.path.join(working_dir, p)
            try:
                os.makedirs(os.path.dirname(full), exist_ok=True)
                
                # Özet Gösterimi:
                old_text = ""
                if os.path.exists(full):
                    with open(full, 'r', encoding='utf-8') as f:
                        old_text = f.read()
                
                # Değişiklikleri ekrana bas
                show_diff(p, old_text, content)
                
                # Kayıt İşlemi
                if os.path.exists(full): backup_file(full)
                with open(full, 'w', encoding='utf-8') as f: f.write(content)
                print(f"{Colors.GREEN}💾 Yazıldı ve Hafızaya Alındı: {p}{Colors.RESET}")
                new_files.append(p)
            except Exception as e:
                 print(f"{Colors.RED}Dosya hatası ({p}): {e}{Colors.RESET}")

    # Hafızayı Güncelle (Yeni yazılan dosyaları otomatik indeksle)
    if memory and new_files:
        memory.index_files(new_files)

    log_conversation(working_dir, prompt_text, explanation, "Agent-Workflow", current_cost)

# ==========================================
# 🌟 PROJE ANA DÖNGÜSÜ
# ==========================================

def main(project_name):
    project_path = os.path.abspath(os.path.join(config.PROJECTS_DIR, project_name))
    
    if not os.path.exists(project_path):
        print(f"{Colors.RED}Hata: {project_path} yolu mevcut değil.{Colors.RESET}")
        return

    print(f"\n{Colors.GREEN}🚀 OTURUM BAŞLATILDI: {project_name.upper()}{Colors.RESET}")

    try:
        orchestrator = AgentOrchestrator()
        memory = MemoryManager(project_root=project_path)
    except Exception as e:
        print(f"{Colors.RED}Başlatma hatası: {e}{Colors.RESET}")
        return

    print(f"{Colors.CYAN}{'━'*50}{Colors.RESET}")
    print(f"Sohbet Aktif. 'q': çıkış | 'b': ana menü")
    
    while True:
        try:
            user_input = input(f"{Colors.BOLD}{Colors.YELLOW}({project_name}) > {Colors.RESET}").strip()
            
            if user_input.lower() in ['exit', 'q', 'quit', 'b']:
                break
            
            if not user_input: continue
            
            process_single_turn(user_input, orchestrator, project_path, memory)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"{Colors.RED}Beklenmedik Hata: {e}{Colors.RESET}")

if __name__ == "__main__":
    print("Lütfen 'launcher.py' kullanın.")