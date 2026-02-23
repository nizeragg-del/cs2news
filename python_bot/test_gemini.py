import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
print(f"Chave encontrada: {key[:10]}...")

genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    response = model.generate_content("Diga 'Gemini Online' se você estiver funcionando.")
    print(f"Resposta: {response.text}")
except Exception as e:
    print(f"Erro: {e}")
