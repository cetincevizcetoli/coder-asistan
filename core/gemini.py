import os
from google import genai
from google.genai import types
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class GeminiModel(BaseModel):
    def __init__(self):
        conf = MODEL_CONFIGS["gemini"]
        self.MODEL_NAME = conf["display_name"]
        self.raw_model_name = conf["model_name"] # Fiyat hesaplaması için
        
        api_key = os.getenv(conf["env_var"])
        if not api_key:
            raise ModelAPIError(f"{conf['env_var']} bulunamadı.")

        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise ModelAPIError(f"Gemini Client Başlatılamadı: {e}")

    def generate_content(self, system_instruction, prompt_text):
        try:
            response = self.client.models.generate_content(
                model=self.raw_model_name,
                contents=[prompt_text],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            
            # Token kullanımını güvenli şekilde al
            usage = {
                "input_tokens": 0,
                "output_tokens": 0
            }
            
            if hasattr(response, 'usage_metadata'):
                usage["input_tokens"] = response.usage_metadata.prompt_token_count
                usage["output_tokens"] = response.usage_metadata.candidates_token_count

            return {
                "content": response.text.strip(),
                "usage": usage,
                "model_key": self.raw_model_name
            }

        except Exception as e:
            raise ModelAPIError(f"Gemini Hatası: {e}")