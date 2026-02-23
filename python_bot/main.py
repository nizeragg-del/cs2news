import os
import requests
import time
from bs4 import BeautifulSoup
from supabase import create_client, Client
import google.generativeai as genai
from dotenv import load_dotenv
import base64
import random

# Deixamos o google.generativeai por enquanto...

load_dotenv()

# Configurações
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configura Gemini (usando gemini-2.5-flash validado)
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    # gemini-1.5-flash tem 15 RPM e 1M de tokens no plano grátis (mais estável que o 2.5 experimental)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

HLTV_RSS_URL = "https://www.hltv.org/rss/news"

def get_headers(site="hltv"):
    """Retorna headers específicos para cada site para evitar bloqueios"""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    if site == "liquipedia":
        # Liquipedia exige um contato no User-Agent para não dar 403
        return {
            "User-Agent": f"GamerNewsBot/1.0 (contact@gamernewsbrasil.com.br) {ua}",
            "Accept-Encoding": "gzip, deflate",
        }
    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US,en;q=0.8",
        "Referer": "https://www.google.com/"
    }

def upload_image_to_supabase(url, file_name):
    """Baixa a imagem e faz upload para o Supabase Storage"""
    if not url:
        return None
    try:
        print(f"Baixando imagem para Storage: {url}")
        # Tenta com headers de Liquipedia se for de lá, senão padrão
        site = "liquipedia" if "liquipedia" in url else "hltv"
        response = requests.get(url, headers=get_headers(site), timeout=25)
        
        if response.status_code == 200:
            storage_path = f"news/{file_name}.jpg"
            # Usa upsert para não dar erro se já existir
            supabase.storage.from_("images").upload(
                path=storage_path,
                file=response.content,
                file_options={"content-type": "image/jpeg", "x-upsert": "true"}
            )
            return f"{SUPABASE_URL}/storage/v1/object/public/images/{storage_path}"
        else:
            print(f"Falha ao baixar imagem (Status {response.status_code})")
    except Exception as e:
        print(f"Erro ao subir para storage: {e}")
    return None

def get_player_image_wikimedia(player_name):
    """Busca imagem no Wikimedia Commons (extremamente amigável a bots)"""
    if not player_name:
        return None
    try:
        print(f"Buscando {player_name} no Wikimedia...")
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={player_name} counter-strike&format=json"
        res = requests.get(search_url, timeout=10).json()
        if res.get("query", {}).get("search"):
            title = res["query"]["search"][0]["title"]
            img_info_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={title}&prop=imageinfo&iiprop=url&format=json"
            img_res = requests.get(img_info_url, timeout=10).json()
            pages = img_res.get("query", {}).get("pages", {})
            for p in pages.values():
                if "imageinfo" in p:
                    return p["imageinfo"][0]["url"]
    except:
        pass
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
        # Tenta com retentativa se der 429
        for attempt in range(3):
            try:
                response = model.generate_content(prompt)
                text = response.text
                break
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    print(f"Quota Gemini excedida. Aguardando 10s (tentativa {attempt+1})...")
                    time.sleep(10)
                else:
                    raise e
        
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

def get_player_image(player_name, team_name=None):
    """Buscador de imagem resiliente (Wikimedia + Liquipedia)"""
    if not player_name and not team_name:
        return None
    
    search_term = player_name if player_name else team_name
    print(f"Buscando imagem para: {search_term}")

    # 1. Tenta Wikimedia (API oficial, super estável)
    wiki_img = get_player_image_wikimedia(f"{search_term} Counter-Strike")
    if wiki_img: 
        print(f"Imagem encontrada no Wikimedia: {wiki_img}")
        return wiki_img

    # 2. Tenta Liquipedia com headers de bot identificado
    if player_name:
        formatted_name = player_name.replace(" ", "_")
        url = f"https://liquipedia.net/counterstrike/{formatted_name}"
        try:
            print(f"Tentando Liquipedia: {url}")
            res = requests.get(url, headers=get_headers("liquipedia"), timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                img_tag = soup.select_one(".infobox-image img") or soup.select_one(".thumbimage")
                if img_tag:
                    full_url = "https://liquipedia.net" + img_tag['src'] if img_tag['src'].startswith("/") else img_tag['src']
                    print(f"Imagem encontrada na Liquipedia: {full_url}")
                    return full_url
        except Exception as e:
            print(f"Erro Liquipedia: {e}")
    
    return None

def extract_entities(title, text):
    """Usa a IA para identificar o jogador ou time principal"""
    if not model:
        return None, None
    
    prompt = f"""
    Analise o título e o texto da notícia de Counter-Strike 2.
    Identifique:
    1. O Jogador principal (Nickname).
    2. O Time principal citado.
    
    Responda EXATAMENTE neste formato:
    PLAYER: [Nome/Nickname ou None]
    TEAM: [Nome do Time ou None]
    
    Título: {title}
    Texto: {text[:500]}
    """
    try:
        for attempt in range(2):
            try:
                response = model.generate_content(prompt)
                lines = response.text.strip().split('\n')
                player, team = None, None
                for line in lines:
                    if "PLAYER:" in line: player = line.split("PLAYER:")[1].strip()
                    if "TEAM:" in line: team = line.split("TEAM:")[1].strip()
                return (None if player == "None" else player), (None if team == "None" else team)
            except Exception as e:
                if "429" in str(e) and attempt == 0:
                    time.sleep(5)
                else:
                    raise e
    except:
        # Fallback manual simples se a IA falhar (pega palavras em caixa alta)
        print("Fallback manual de extração de jogadores...")
        words = title.split()
        for w in words:
            if w.isupper() and len(w) > 2: return w, None
        return None, None

# Fallback IDs do Unsplash caso tudo falhe
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
        
        # Reescrita IA
        title, excerpt, content = rewrite_with_ai(full_text)

        # ESTRATÉGIA DE IMAGEM MULTI-CAMADA (RESILIENTE)
        final_image_url = None
        post_id = str(int(time.time()))
        
        # 1. Tentativa HLTV
        print("Tentando Imagem HLTV...")
        final_image_url = upload_image_to_supabase(hltv_image_url, f"hltv_{post_id}")
        
        # 2. Busca por Entidades (Jogador ou Time)
        if not final_image_url:
            print("HLTV falhou. Buscando foto do jogador ou time...")
            player_name, team_name = extract_entities(item['title'], full_text or excerpt)
            
            search_img_url = get_player_image(player_name, team_name)
            if search_img_url:
                final_image_url = upload_image_to_supabase(search_img_url, f"entity_{post_id}")
        
        # 3. Fallback final Unsplash (enviado para o storage para garantir)
        if not final_image_url:
            print("Busca de entidades falhou. Usando Unsplash profissional...")
            unsplash_url = get_fallback_image()
            final_image_url = upload_image_to_supabase(unsplash_url, f"fallback_{post_id}")
            # Se até o upload do fallback falhar (raro), usa a URL direta
            if not final_image_url: final_image_url = unsplash_url
        
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
