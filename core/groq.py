# core/groq.py
import os
import requests
from .base import BaseModel, ModelAPIError
from config import MODEL_CONFIGS

class GroqModel(BaseModel):
    """Groq LPU - Ultra hızlı inference"""
    
    def __init__(self):
        conf = MODEL_CONFIGS["groq"]
        self.MODEL_NAME = conf["display_name"] [cite: 14]
        
        self.api_key = os.getenv(conf["env_var"])
        if not self.api_key:
            raise ModelAPIError(f"{conf['env_var']} ortam değişkeni bulunamadı.") [cite: 14]
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions" [cite: 14]
        self.model_id = conf["model_id"] [cite: 14]
        
    def generate_content(self, system_instruction, prompt_text):
        headers = { [cite: 15]
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_instruction}, [cite: 16]
                {"role": "user", "content": prompt_text} [cite: 16]
            ],
            "temperature": 0.1,
            "max_tokens": 8000,
            "response_format": {"type": "json_object"}  # JSON zorla
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30) [cite: 17]
            response.raise_for_status()
            result = response.json() [cite: 17]
            return result["choices"][0]["message"]["content"].strip() [cite: 17]
        except Exception as e:
            raise ModelAPIError(f"Groq API Hatası: {e}") [cite: 17]