import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

load_dotenv()
key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

genai.configure(api_key=key)

print(f"Iniciando teste com chave: {key[:10]}...")

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Modelo instanciado.")
    response = model.generate_content("Diga OK.")
    print(f"Sucesso: {response.text}")
except Exception as e:
    print("Ocorreu um erro:")
    print(str(e))
    traceback.print_exc()
