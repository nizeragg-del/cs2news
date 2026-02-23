import os
import requests
import time
from bs4 import BeautifulSoup
from supabase import create_client, Client
import google.generativeai as genai
from dotenv import load_dotenv
import base64

load_dotenv()

# Configurações
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configura Gemini (usando gemini-2.5-flash validado)
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None

HLTV_RSS_URL = "https://www.hltv.org/rss/news"

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US,en;q=0.8",
    }

def download_image_as_base64(url):
    """Baixa a imagem e retorna em formato Base64 para salvar no banco"""
    if not url:
        return None
    try:
        print(f"Baixando imagem para Base64: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://www.hltv.org/"
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "image/jpeg")
            encoded_string = base64.b64encode(response.content).decode("utf-8")
            return f"data:{content_type};base64,{encoded_string}"
        else:
            print(f"Falha ao baixar imagem (Status {response.status_code})")
    except Exception as e:
        print(f"Erro ao converter imagem: {e}")
    return None

def fetch_full_content(url, description=""):
    """
    Tenta capturar o conteúdo completo. 
    Dada a proteção da HLTV, se houver falha de rede (10054), 
    usamos a descrição do RSS e construímos a URL da imagem de forma algorítmica.
    """
    news_id = "unknown"
    try:
        news_id = url.split("/news/")[1].split("/")[0]
    except:
        pass

    # Padrão de imagem provável da CDN HLTV (Funciona com no-referrer)
    probable_image = f"https://img-cdn.hltv.org/images/article/main/{news_id}.jpg" if news_id != "unknown" else ""

    try:
        print(f"Tentando capturar detalhes via rede: {url}")
        response = requests.get(url, headers=get_headers(), timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Pega imagem OG (Meta) - Mais estável
            og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"property": "og:image"})
            if og_img:
                probable_image = og_img["content"]
            
            # Pega Texto
            content_div = soup.select_one(".story") or soup.select_one(".newstext-con") or soup.select_one(".abstract")
            full_text = content_div.get_text(separator="\n", strip=True) if content_div else description
            
            return full_text, probable_image
        else:
            print(f"Acesso à página falhou (Status {response.status_code}). Usando fallback...")
            return description, probable_image
    except Exception as e:
        print(f"Bloqueio de rede HLTV ({e}). Usando fallback inteligente.")
        return description, probable_image

def rewrite_with_ai(original_content):
    if not model:
        return "Notícia", "Resumo", original_content

    prompt = f"""
    Você é o redator principal do portal "Gamer News Brasil".
    Sua missão é transformar o conteúdo abaixo em uma notícia IMPACTANTE e PROFISSIONAL.
    
    REGRAS:
    1. Nunca cite HLTV ou fontes externas. Atue como redação original.
    2. Linguagem: Português do Brasil.
    3. Use Markdown (negritos, subtítulos).
    
    TEXTO BASE:
    {original_content}
    
    SAÍDA EXATA:
    TITULO: [Título Chamativo]
    RESUMO: [Resumo curto]
    CONTEUDO: [Texto completo]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        new_title = ""
        new_excerpt = ""
        new_content = ""
        
        for line in text.split('\n'):
            if line.startswith("TITULO:"): new_title = line.replace("TITULO:", "").strip()
            elif line.startswith("RESUMO:"): new_excerpt = line.replace("RESUMO:", "").strip()
            elif line.startswith("CONTEUDO:"): 
                new_content = text.split("CONTEUDO:")[1].strip()
                break
        
        return new_title, new_excerpt, new_content
    except Exception as e:
        print(f"Erro Gemini: {e}")
        return "Erro na Reescrita", "Falha de IA", original_content

# Fallback IDs do Unsplash caso a imagem da HLTV falhe totalmente
UNSPLASH_IDS = [
    "1542751371-adc38448a05e", # Guy playing
    "1511512578047-dfb367046420", # Gaming setup
    "1542751110-97427bbecf20"  # ESports arena
]

def get_fallback_image():
    import random
    img_id = random.choice(UNSPLASH_IDS)
    return f"https://images.unsplash.com/photo-{img_id}?q=80&w=1000&auto=format&fit=crop"

def job():
    print("--- INICIANDO ROBÔ DE NOTÍCIAS (GERAÇÃO DE CONTEÚDO E IMAGENS LOCAIS) ---")
    
    # Notícia específica solicitada pelo usuário
    news_list = [
        {
            "title": "3DMAX to swap bodyy for misutaaa; NBK- to join as assistant coach",
            "link": "https://www.hltv.org/news/43946/media-3dmax-to-swap-bodyy-for-misutaaa-nbk-to-join-as-assistant-coach",
            "description": "The French veteran returns to a starting lineup for the first time since December 2023."
        }
    ]

    for item in news_list:
        print(f"Processando: {item['title']}")
        
        # Obtém conteúdo e a URL da imagem (HLTV CDN ou Meta Tag)
        full_text, hltv_image_url = fetch_full_content(item['link'], item['description'])
        
        # Tenta baixar a imagem e converter para Base64 para salvar no banco
        base64_image = download_image_as_base64(hltv_image_url)
        
        # Se a imagem da HLTV falhar, usa Unsplash
        final_image_url = base64_image if base64_image else get_fallback_image()
        
        # Reescrita IA
        title, excerpt, content = rewrite_with_ai(full_text)
        
        if not title or not content or len(content) < 50:
            print(f"⚠️ Conteúdo insuficiente para: {item['title']}. Pulando...")
            continue

        data = {
            "title": title,
            "excerpt": excerpt,
            "content": content,
            "image_url": final_image_url,
            "source_url": None,
            "category": "Mercado"
        }
        
        try:
            supabase.table("posts").insert(data).execute()
            print(f"✅ Postado com sucesso! Imagem: {final_image_url}")
        except Exception as e:
            print(f"❌ Erro Supabase: {e}")

if __name__ == "__main__":
    job()
