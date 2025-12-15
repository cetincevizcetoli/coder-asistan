# core/gemini.py: Google Gemini API Uygulaması
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
from .base import BaseModel, ModelAPIError

class GeminiModel(BaseModel):
    MODEL_NAME = "Google Gemini (gemini-2.5-flash)"

    def __init__(self):
        try:
            self.client = genai.Client()
        except Exception as e:
            raise ModelAPIError(f"Gemini istemcisi başlatılamadı: {e}")

    def generate_content(self, system_instruction, prompt_text):
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt_text],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            return response.text.strip()
            
        except APIError as e:
            # API hatalarını genel ModelAPIError olarak yükseltme
            error_message = getattr(e, 'message', str(e))
            raise ModelAPIError(f"Gemini API Hatası: {error_message}")