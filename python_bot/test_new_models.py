import os
import google.generativeai as genai
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")
load_dotenv()
key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
genai.configure(api_key=key)

models_to_test = ['gemini-2.5-flash', 'gemini-3-flash-preview', 'gemini-2.0-flash-lite-preview-02-05']

for m_name in models_to_test:
    print(f"Testando {m_name}...")
    try:
        model = genai.GenerativeModel(m_name)
        response = model.generate_content("Diga OK.")
        print(f"Sucesso {m_name}: {response.text}")
        break
    except Exception as e:
        print(f"Erro {m_name}: {e}")
