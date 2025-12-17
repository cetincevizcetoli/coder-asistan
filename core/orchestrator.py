# core/orchestrator.py
import json
from config import Colors, ARCHITECT_INSTRUCTION, DEVELOPER_INSTRUCTION
from core.groq import GroqModel
from core.gemini import GeminiModel

class AgentOrchestrator:
    def __init__(self):
        self.architect = GroqModel()  # Hızlı ve mantıklı
        self.developer = GeminiModel() # Geniş bağlam ve hassas yazım

    def execute_workflow(self, prompt, context, working_dir):
        print(f"{Colors.MAGENTA}🏗️  MİMAR (Groq) planı hazırlıyor...{Colors.RESET}")
        
        # 1. Mimar Planı Çıkarır
        arch_prompt = f"BAĞLAM:\n{context}\n\nİSTEK: {prompt}"
        arch_res = self.architect.generate_content(ARCHITECT_INSTRUCTION, arch_prompt)
        
        # JSON temizleme ve yükleme
        try:
            # Groq bazen string bazen dict dönebilir, adaptörüne göre ayarla
            plan_data = json.loads(arch_res) if isinstance(arch_res, str) else arch_res
        except:
            print(f"{Colors.RED}Mimar planı oluşturamadı.{Colors.RESET}")
            return None

        print(f"\n{Colors.CYAN}📋 MİMARIN PLANI:{Colors.RESET}\n{plan_data.get('plan')}")
        print(f"📂 Etkilenecek Dosyalar: {plan_data.get('etkilenecek_dosyalar')}")

        confirm = input(f"\n{Colors.YELLOW}Bu planı onaylıyor musunuz? (e/h): {Colors.RESET}").lower()
        if confirm != 'e':
            return None

        # 2. Mühendis Kodu Yazar
        print(f"\n{Colors.GREEN}👨‍💻 MÜHENDİS (Gemini) kodlamaya başlıyor...{Colors.RESET}")
        dev_prompt = f"MİMAR PLANI: {plan_data.get('plan')}\n\nBAĞLAM: {context}\n\nİSTEK: {prompt}"
        dev_res = self.developer.generate_content(DEVELOPER_INSTRUCTION, dev_prompt)
        
        return dev_res # Assistant.py'deki clean_json_string'e gidecek