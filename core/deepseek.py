# core/deepseek.py
import os
import requests
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class DeepSeekModel(BaseModel):
    """DeepSeek API - Ücretsiz ve güçlü"""
    
    def __init__(self):
        conf = MODEL_CONFIGS["deepseek"]
        self.MODEL_NAME = conf["display_name"]
        
        self.api_key = os.getenv(conf["env_var"])
        if not self.api_key:
            raise ModelAPIError(f"{conf['env_var']} ortam değişkeni bulunamadı.")
        
        # DeepSeek OpenAI uyumlu API uç noktası
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model_id = conf["model_id"]
    
    def generate_content(self, system_instruction, prompt_text):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt_text}
            ],
            "temperature": 0.1,
            "max_tokens": 8000,
            "response_format": {"type": "json_object"}  # JSON zorla
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # Debug için
            if hasattr(self, 'DEBUG') and self.DEBUG:
                print(f"DEBUG DeepSeek Response: {result}")
                
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            # Hata mesajını daha detaylı görmek için
            if hasattr(e, 'response') and e.response is not None:
                error_msg = e.response.text
                print(f"DEBUG DeepSeek Error: {error_msg}")
                try:
                    error_json = json.loads(error_msg)
                    raise ModelAPIError(f"DeepSeek Hatası: {error_json.get('message', str(e))}")
                except:
                    raise ModelAPIError(f"DeepSeek API Hatası: {e}")
            else:
                raise ModelAPIError(f"DeepSeek Bağlantı Hatası: {e}")
        except Exception as e:
            raise ModelAPIError(f"DeepSeek İşlem Hatası: {e}")