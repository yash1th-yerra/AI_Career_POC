# app/services/llm_service.py
import os
from dotenv import load_dotenv
import gemini_ai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_gemini_llm(model_name: str = "gemini-2.5-flash"):
    """
    Returns a callable object for LangChain or direct usage
    """
    client = gemini_ai.Client(api_key=GEMINI_API_KEY)

    def run_prompt(prompt: str):
        response = client.generate_text(model=model_name, prompt=prompt, temperature=0.2)
        return response.text

    return run_prompt
