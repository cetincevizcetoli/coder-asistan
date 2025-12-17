import os
import sys

# google-genai yüklü mü kontrol et
try:
    from google import genai
except ImportError:
    print("❌ HATA: 'google-genai' kütüphanesi bulunamadı.")
    sys.exit(1)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ HATA: GOOGLE_API_KEY tanımlı değil!")
    sys.exit(1)

print(f"🔑 Anahtar ile bağlanılıyor... (Son 4 hane: {api_key[-4:]})")

try:
    client = genai.Client(api_key=api_key)
    print("\n📡 --- HESABINIZDA AKTİF OLAN MODELLER ---")
    
    count = 0
    # Modelleri çek ve listele
    # Pager üzerinden döner, listeye çevirelim
    for m in client.models.list():
        # Sadece içerik üretebilen modelleri al
        if "generateContent" in m.supported_actions:
            # İsmi temizle (models/ önekini at)
            clean_name = m.name.replace('models/', '')
            print(f"✅ {clean_name}")
            count += 1
            
    if count == 0:
        print("\n⚠️ HATA: Hiçbir model bulunamadı. API Key'inizin yetkilerini kontrol edin.")
    else:
        print("\n👉 İPUCU: Yukarıdaki ✅ ile başlayan isimlerden birini config.py dosyasına kopyalayın.")

except Exception as e:
    print(f"\n❌ BAĞLANTI HATASI: {e}")