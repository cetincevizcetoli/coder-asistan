# core/gemini.py
import os
from google import genai
from google.genai import types
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class GeminiModel(BaseModel):
    def __init__(self):
        conf = MODEL_CONFIGS["gemini"]
        self.MODEL_NAME = conf["display_name"]
        
        # API Key'i ortamdan alıyoruz
        api_key = os.getenv(conf["env_var"])
        if not api_key:
            raise ModelAPIError(f"{conf['env_var']} bulunamadı.")

        try:
            # Client başlat (Orijinal koddaki gibi sade)
            self.client = genai.Client(api_key=api_key)
            self.model_id = conf["model_name"]
        except Exception as e:
            raise ModelAPIError(f"Gemini Client Başlatılamadı: {e}")

    def generate_content(self, system_instruction, prompt_text):
        try:
            # --- ORİJİNAL YAPIYA DÖNÜLDÜ ---
            # response_mime_type parametresi kaldırıldı, hata kaynağı buydu.
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt_text],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            return response.text.strip()
        except Exception as e:
            # Hata mesajını daha net görelim
            raise ModelAPIError(f"Gemini Hatası: {e}")