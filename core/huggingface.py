# core/huggingface.py: Hugging Face Inference API Uygulaması
import os
import requests
import json
from .base import BaseModel, ModelAPIError

# Örnek kodlama görevleri için güçlü bir model
# Bu modelin API erişimi daha stabil olma eğilimindedir.
# Code Llama'nın 7B Instruct versiyonunu deneyelim
# Yeni, daha stabil olduğu varsayılan model:
# Yeni, kodlama odaklı ve stabil olduğu varsayılan model
DEFAULT_HF_MODEL = "meta-llama/Meta-Llama-3–8B-Instruct"
HF_API_URL_TEMPLATE = "https://router.huggingface.co/models/{model_id}"

class HuggingFaceModel(BaseModel):
    MODEL_NAME = f"Hugging Face ({DEFAULT_HF_MODEL})"

    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ModelAPIError("HUGGINGFACE_API_KEY ortam değişkeni ayarlanmadı.")
        
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.api_url = HF_API_URL_TEMPLATE.format(model_id=DEFAULT_HF_MODEL)
        
    def generate_content(self, system_instruction, prompt_text):
        
        # Mistral formatını kullanarak system instruction ve prompt'u birleştirme
        full_prompt = (
            f"<s>[INST] <<SYS>>{system_instruction}<</SYS>>"
            f"Görevi tamamla ve SADECE JSON çıktısı ver: {prompt_text} [/INST]"
        )
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 2000,
                "temperature": 0.1,
                "return_full_text": False
            },
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status() # HTTP 4xx veya 5xx hatası varsa fırlatır

            response_json = response.json()
            
            # Hugging Face'in yanıt formatı genellikle bir liste döndürür.
            if not isinstance(response_json, list) or 'generated_text' not in response_json[0]:
                raise ModelAPIError(f"Hugging Face'ten beklenmedik yanıt formatı alındı: {response_json}")
                
            return response_json[0]['generated_text'].strip()

        except requests.exceptions.RequestException as e:
            # Tüm requests hatalarını (bağlantı, timeout, HTTP hataları) yakala
            raise ModelAPIError(f"Hugging Face API çağrısı başarısız oldu: {e}")