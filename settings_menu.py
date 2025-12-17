import os
import json
import time

# Renkler
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

SETTINGS_FILE = "user_settings.json"

# Hafıza Profilleri
PROFILES = {
    'light':  {'name': 'Hafif (Light)',  'size': '80 MB',  'desc': '🚀 Çok Hızlı, Düşük RAM (Z570 İçin Önerilen)'},
    'medium': {'name': 'Orta (Medium)',  'size': '470 MB', 'desc': '⚖️ Daha İyi Türkçe, Dengeli Hız'},
    'heavy':  {'name': 'Ağır (Heavy)',   'size': '2.2 GB', 'desc': '🏋️ Çok Yavaş, GPU İster (Dikkat!)'}
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {"active_profile": "light"}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"{RED}Ayarlar kaydedilemedi: {e}{RESET}")

def settings_main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        current_settings = load_settings()
        curr_profile = current_settings.get("active_profile", "light")
        
        if curr_profile not in PROFILES:
            curr_profile = 'light'

        print(f"{CYAN}╔══════════════════════════════════════════════╗{RESET}")
        print(f"{CYAN}║           ⚙️  SİSTEM AYARLARI                 ║{RESET}")
        print(f"{CYAN}╚══════════════════════════════════════════════╝{RESET}")
        
        p_info = PROFILES[curr_profile]
        
        print(f"\n🧠 Aktif Hafıza Modeli: {GREEN}{p_info['name']} [{p_info['size']}]{RESET}")
        print(f"{YELLOW}   └─ {p_info['desc']}{RESET}\n")
        
        print("Mevcut Seçenekler:")
        print(f"   [1] Hafif  (80 MB)  - Hız Odaklı")
        print(f"   [2] Orta   (470 MB) - Anlama Odaklı")
        print(f"   [3] Ağır   (2 GB)   - Detay Odaklı")
        print(f"\n   [Q] Menüye Dön")
        
        choice = input(f"\n{YELLOW}Seçiminiz: {RESET}").strip().lower()
        
        if choice == 'q':
            break
            
        new_profile = None
        if choice == '1': new_profile = 'light'
        elif choice == '2': new_profile = 'medium'
        elif choice == '3': new_profile = 'heavy'
        
        if new_profile and new_profile != curr_profile:
            print(f"\n{RED}⚠️  DİKKAT: Hafıza Modeli Değiştiriliyor!{RESET}")
            print(f"Eski model ile oluşturulan proje hafızaları, bu model ile çalışmaz.")
            print(f"Sistem, projeye girdiğinde eski hafızayı otomatik olarak {RED}ARŞİVLEYİP SIFIRLAYACAKTIR.{RESET}")
            
            # --- DÜZELTME BURADA ---
            # Artık hem 'evet' hem 'e' kabul ediyor
            confirm = input(f"\n{RED}Onaylıyor musunuz? (e/h): {RESET}").lower()
            
            if confirm in ['evet', 'e']:
                current_settings["active_profile"] = new_profile
                save_settings(current_settings)
                print(f"\n{GREEN}✅ Ayar değiştirildi: {new_profile.upper()}{RESET}")
                time.sleep(1.5)
            else:
                print(f"\n{YELLOW}İptal edildi.{RESET}")
                time.sleep(1)
        elif new_profile == curr_profile:
            print(f"\n{YELLOW}Zaten bu mod aktif.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    settings_main()