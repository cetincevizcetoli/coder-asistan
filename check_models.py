import os
import sys

# google-genai yüklü mü kontrol et
try:
    from google import genai
except ImportError:
    print("❌ HATA: 'google-genai' kütüphanesi bulunamadı.")
    print("👉 Çözüm: Önce 'pip install google-genai' komutunu çalıştırın.")
    sys.exit(1)

# API Anahtarını al
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ HATA: GOOGLE_API_KEY tanımlı değil!")
    print("👉 Terminale şunu yazın: export GOOGLE_API_KEY='anahtariniz'")
    sys.exit(1)

print(f"🔑 Anahtar ile bağlanılıyor: {api_key[:5]}...")

try:
    client = genai.Client(api_key=api_key)
    print("\n📡 --- GOOGLE TARAFINDAN ONAYLANAN MODELLER ---")
    
    count = 0
    # Modelleri çek ve listele
    for m in client.models.list():
        if "generateContent" in m.supported_actions:
            # model isminin başındaki 'models/' kısmını atarak temiz göster
            clean_name = m.name.replace('models/', '')
            print(f"✅ {clean_name}")
            count += 1
            
    if count == 0:
        print("\n⚠️ HATA: Erişim izniniz olan hiçbir model bulunamadı.")
        print("Hesabınızın faturalandırma (Billing) ayarlarını kontrol etmeniz gerekebilir.")

except Exception as e:
    print(f"\n❌ KRİTİK HATA: {e}")
