import os
import sys

# ==========================================
# ⚙️ AYARLAR VE FİLTRELER
# ==========================================

# Sadece içeriği taranmayacak sistem klasörleri
DIKKATE_ALINMAYACAK_DIZINLER = [
    '.git', '__pycache__', 'venv', '.venv', 'env', '.env', 'node_modules', 
    '.vscode', '.idea', 'dist', 'build', 'target', 'bin',
    '__macosx', '.ds_store', 'logs', 'site-packages', 'lib', 'include',
    '.gassist_backups', '.coder_memory'
]

# İçeriği dökülmeyecek ama varlığı gösterilecek "Özel" klasörler
OZEL_USER_KLASORLERI = ['my_projects']

# İçeriği döküme eklenecek kod uzantıları
BELGELENECEK_KOD_UZANTILARI = [
    '.py', '.php', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', 
    '.sh', '.bash', '.c', '.cpp', '.h', '.hpp', '.java', '.go', '.rb', '.swift', 
    '.kt', '.ts', '.jsx', '.tsx', '.conf', '.ini', '.sql', '.md', '.txt'
]

# Çıktı dosyasının adı
CIKTI_DOSYASI = "proje_dokumu.md"

# ==========================================
# 🛠️ FONKSİYONLAR
# ==========================================

def dosya_icerigini_getir(yol):
    """Dosya içeriğini okur ve Markdown kod bloğu içinde döndürür."""
    try:
        with open(yol, 'r', encoding='utf-8') as f:
            icerik = f.read()
            
        uzanti = os.path.splitext(yol)[1].lstrip('.').lower()
        return f"\n```{(uzanti if uzanti else 'plaintext')}\n{icerik}\n```\n"
    except Exception as e:
        return f"\n> [Okunamadı: {e}]\n"

def dizin_yapisi_getir(hedef_dizin):
    """Verilen yoldan başlayarak dizin yapısını döndürür."""
    yapı = "### 📂 Proje Dizin Yapısı ve Dosyalar\n\n"
    
    for kok, dizinler, dosyalar in os.walk(hedef_dizin):
        # Filtreleme: Gereksiz klasörleri gezme
        dizinler[:] = [d for d in dizinler if d.lower() not in DIKKATE_ALINMAYACAK_DIZINLER]
        
        yol_parcalari = kok.lower().split(os.sep)
        if any(yasak in yol_parcalari for yasak in DIKKATE_ALINMAYACAK_DIZINLER):
            continue

        base_name = os.path.basename(kok)
        goreli_yol = os.path.relpath(kok, hedef_dizin)
        
        # Ağaç yapısı başlığı
        if goreli_yol == '.':
            seviye = 0
            yapı += f"- **{os.path.basename(hedef_dizin)}/** (Proje Kökü)\n"
        else:
            seviye = goreli_yol.count(os.sep) + 1
            girinti = "  " * seviye
            
            # Özel klasör kontrolü (my_projects gibi)
            if base_name in OZEL_USER_KLASORLERI:
                yapı += f"{girinti}- **{base_name}/** (Kullanıcı Projeleri - İçerik Gizli)\n"
                dizinler[:] = [] # Altına inme
                continue 
            else:
                yapı += f"{girinti}- **{base_name}/**\n"

        girinti_dosya = "  " * (seviye + 1)
        
        # DOSYALARI LİSTELEME (Filtresiz)
        for dosya in sorted(dosyalar):
            # .git klasörü içindeki dosyaları hariç tut, gerisi gelsin
            if '.git' in yol_parcalari: continue
            
            yapı += f"{girinti_dosya}- {dosya}\n"
                    
    return yapı

def ana_fonksiyon():
    hedef_dizin = os.getcwd() 
    proje_adi = os.path.basename(hedef_dizin)
    
    dokum_metni = f"# 📝 Proje Dökümü: {proje_adi}\n\n"
    dokum_metni += f"Bu döküm, **{hedef_dizin}** dizini için oluşturulmuştur.\n"
    dokum_metni += "Not: `my_projects` klasörünün içeriği gizlilik gereği hariç tutulmuştur.\n\n"
    
    print(f"1/3: '{proje_adi}' klasör yapısı taranıyor...")
    dokum_metni += dizin_yapisi_getir(hedef_dizin)
    
    dokum_metni += "\n---\n"
    dokum_metni += "### 💻 Kod İçeriği Dökümü\n\n"
    
    print("2/3: Kod içerikleri toplanıyor...")
    
    dosya_sayisi = 0
    for kok, dizinler, dosyalar in os.walk(hedef_dizin):
        dizinler[:] = [d for d in dizinler if d.lower() not in DIKKATE_ALINMAYACAK_DIZINLER]
        
        if os.path.basename(kok) in OZEL_USER_KLASORLERI:
            dizinler[:] = []
            continue

        yol_parcalari = kok.lower().split(os.sep)
        if any(yasak in yol_parcalari for yasak in DIKKATE_ALINMAYACAK_DIZINLER): continue

        for dosya in sorted(dosyalar):
            dosya_yolu = os.path.join(kok, dosya)
            
            # KENDİSİNİ VE ÇIKTI DOSYASINI OKUMASIN (İçerik Dökümünde)
            if dosya == CIKTI_DOSYASI: continue
            
            uzanti = os.path.splitext(dosya)[1].lower()

            if uzanti in BELGELENECEK_KOD_UZANTILARI:
                goreli_yol = os.path.relpath(dosya_yolu, hedef_dizin)
                dokum_metni += f"\n#### 📄 Dosya: `{goreli_yol}`\n"
                dokum_metni += dosya_icerigini_getir(dosya_yolu)
                dosya_sayisi += 1
            
    print(f"3/3: '{CIKTI_DOSYASI}' dosyasına kayıt yapılıyor...")
    try:
        cikti_yolu = os.path.join(hedef_dizin, CIKTI_DOSYASI)
        with open(cikti_yolu, 'w', encoding='utf-8') as f:
            f.write(dokum_metni)
        print(f"\n✅ İşlem Başarılı! Toplam {dosya_sayisi} dosya belgelendi.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        
if __name__ == "__main__":
    ana_fonksiyon()