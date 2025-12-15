# core/base.py: Ortak Arayüz ve Hata Tanımları

class ModelAPIError(Exception):
    """API bağlantı/kota hataları için genel hata sınıfı."""
    pass

class BaseModel:
    """Tüm model sınıflarının miras alacağı soyut sınıf."""
    MODEL_NAME = "Temel Model"

    def __init__(self):
        # API anahtarını kontrol etme vb.
        pass

    def generate_content(self, system_instruction, prompt_text):
        """AI'dan içerik üretme çağrısı."""
        raise NotImplementedError("Bu metot alt sınıflar tarafından uygulanmalıdır.")