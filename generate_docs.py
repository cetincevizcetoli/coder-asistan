import os
import sys

# Döküme dahil edilmeyecek sistem, ortam ve geçici dizinler
DIKKATE_ALINMAYACAK_DIZINLER = [
    '.git', '__pycache__', 'venv', '.venv', 'env', '.env', 'node_modules', 
    '.vscode', '.idea', 'dist', 'build', 'target', 'bin',
    '__macosx', '.ds_store', 'logs', 'site-packages', 'lib', 'include',
    '.gassist_backups' # Yedekleri de dahil etmeyelim
]

# İçeriği döküme eklenecek kod uzantıları
BELGELENECEK_KOD_UZANTILARI = [
    '.py', '.php', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', 
    '.sh', '.bash', '.c', '.cpp', '.h', '.hpp', '.java', '.go', '.rb', '.swift', 
    '.kt', '.ts', '.jsx', '.tsx', '.conf', '.ini', '.sql'
]

# Sadece isminin listeleneceği, içeriği dökülmeyecek uzantılar
SADECE_ISIM_LISTELENECEK_UZANTILAR = ['.txt', '.md', '.log', '.csv', '.tsv']

# Çıktı dosyasının adı
CIKTI_DOSYASI = "proje_dokumu.md"

def dosya_icerigini_getir(yol):
    """Dosya içeriğini okur ve Markdown kod bloğu içinde döndürür."""
    try:
        with open(yol, 'r', encoding='utf-8') as f:
            icerik = f.read()
            
        uzanti = os.path.splitext(yol)[1].lstrip('.').lower()
        return f"\n```{(uzanti if uzanti else 'plaintext')}\n{icerik}\n```\n"

    except UnicodeDecodeError:
        try:
            with open(yol, 'r', encoding='latin-1') as f:
                icerik = f.read()
            return f"\n```plaintext (Latin-1 Kodlaması)\n{icerik}\n```\n"
        except Exception as e:
            return f"\n> [Dosya Okuma Hatası (Kodlama): {e}]\n"
    except Exception as e:
        return f"\n> [Dosya Okuma Hatası (Genel): {e}]\n"

def dizin_yapisi_getir(hedef_dizin):
    """Verilen yoldan başlayarak dizin yapısını döndürür."""
    yapı = "### 📂 Proje Dizin Yapısı ve Dosyalar\n\n"
    
    for kok, dizinler, dosyalar in os.walk(hedef_dizin):
        dizinler[:] = [d for d in dizinler if d.lower() not in DIKKATE_ALINMAYACAK_DIZINLER]
        yol_parcalari = kok.lower().split(os.sep)
        if any(yasak in yol_parcalari for yasak in DIKKATE_ALINMAYACAK_DIZINLER):
            continue

        goreli_yol = os.path.relpath(kok, hedef_dizin)
        
        if goreli_yol == '.':
            seviye = 0
            yapı += f"- **{os.path.basename(hedef_dizin)}/** (Proje Kökü)\n"
        else:
            seviye = goreli_yol.count(os.sep) + 1
            girinti = "  " * seviye
            yapı += f"{girinti}- **{os.path.basename(kok)}/**\n"

        girinti_dosya = "  " * (seviye + 1)
        
        for dosya in sorted(dosyalar):
            if dosya != CIKTI_DOSYASI and dosya != os.path.basename(__file__):
                if not dosya.startswith('.'):
                    yapı += f"{girinti_dosya}- {dosya}\n"
                    
    return yapı

def ana_fonksiyon():
    hedef_dizin = os.getcwd() 
    proje_adi = os.path.basename(hedef_dizin)
    
    dokum_metni = f"# 📝 Proje Dökümü: {proje_adi}\n\n"
    dokum_metni += f"Bu döküm, **{hedef_dizin}** dizini (mevcut klasör) ve altındakileri kapsar.\n\n"
    
    print(f"1/3: '{proje_adi}' klasörü taranıyor...")
    dokum_metni += dizin_yapisi_getir(hedef_dizin)
    
    dokum_metni += "\n---\n"
    dokum_metni += "### 💻 Kod İçeriği Dökümü\n\n"
    
    print("2/3: Kod içerikleri toplanıyor...")
    
    dosya_sayisi = 0
    for kok, dizinler, dosyalar in os.walk(hedef_dizin):
        dizinler[:] = [d for d in dizinler if d.lower() not in DIKKATE_ALINMAYACAK_DIZINLER]
        yol_parcalari = kok.lower().split(os.sep)
        if any(yasak in yol_parcalari for yasak in DIKKATE_ALINMAYACAK_DIZINLER): continue

        for dosya in sorted(dosyalar):
            dosya_yolu = os.path.join(kok, dosya)
            if dosya == CIKTI_DOSYASI or dosya == os.path.basename(__file__): continue
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
