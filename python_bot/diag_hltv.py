import cloudscraper
from bs4 import BeautifulSoup
import time

def test_hltv_access(url):
    print(f"Testando acesso a: {url}")
    
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        response = scraper.get(url, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Tenta encontrar og:image
            og_image = soup.find("meta", property="og:image")
            print(f"OG Image found: {og_image['content'] if og_image else 'None'}")
            
            # Tenta encontrar a imagem principal no corpo
            main_img = soup.select_one(".main-image-con img") or soup.select_one(".news-image")
            print(f"Main Image Element found: {main_img['src'] if main_img else 'None'}")
            
            # Salva o HTML para inspeção se necessário
            with open("hltv_debug.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("HTML salvo em hltv_debug.html")
            
        else:
            print(f"Falha no acesso. Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_url = "https://www.hltv.org/news/43946/media-3dmax-to-swap-bodyy-for-misutaaa-nbk-to-join-as-assistant-coach"
    test_hltv_access(test_url)
