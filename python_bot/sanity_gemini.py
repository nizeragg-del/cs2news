import os
import google.generativeai as genai
from dotenv import load_dotenv
import warnings

# Silencia avisos para ver o erro real
warnings.filterwarnings("ignore")

load_dotenv()
key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

genai.configure(api_key=key)

print(f"Testando com chave: {key[:10]}...")

try:
    # Tenta um modelo padrão
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Diga OK.")
    print(f"Sucesso (1.5-flash): {response.text}")
except Exception as e1:
    print(f"Erro (1.5-flash): {e1}")
    try:
        # Tenta o modelo novo que apareceu na lista
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Diga OK.")
        print(f"Sucesso (2.0-flash): {response.text}")
    except Exception as e2:
        print(f"Erro (2.0-flash): {e2}")
