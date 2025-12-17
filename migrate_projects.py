import os
import shutil
from pathlib import Path

# Hedef
TARGET_DIR = Path("my_projects")
if not TARGET_DIR.exists():
    os.makedirs(TARGET_DIR)

print("🚚 Proje Taşıma İşlemi Başlıyor...")

# Mevcut dizindeki klasörleri tara
for entry in Path.cwd().iterdir():
    # Kendi dizinimizdeki klasörler (my_projects hariç)
    if entry.is_dir() and entry.name != "my_projects" and entry.name != "core" and entry.name != "venv" and not entry.name.startswith("."):
        
        # Eğer içinde .coder_memory varsa bu bir projedir!
        if (entry / ".coder_memory").exists():
            print(f"📦 Bulundu ve Taşınıyor: {entry.name}")
            try:
                shutil.move(str(entry), str(TARGET_DIR / entry.name))
                print(f"   ✅ Taşındı.")
            except Exception as e:
                print(f"   ❌ Hata: {e}")

print("\n🏁 İşlem Tamam. Artık launcher.py'yi çalıştırabilirsiniz.")