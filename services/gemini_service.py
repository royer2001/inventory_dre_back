import requests
from config import GEMINI_API_KEY

class GeminiService:
    BASE_URL = "https://api.gemini.google.com/v1"

    @staticmethod
    def analyze_text(prompt):
        url = f"{GeminiService.BASE_URL}/generate"
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"prompt": prompt}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Error al comunicarse con Gemini", "status": response.status_code}
