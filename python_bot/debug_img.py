import cloudscraper
from bs4 import BeautifulSoup
import os

def test_image_process(url):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    try:
        print(f"Buscando: {url}")
        res = scraper.get(url, timeout=20)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            og_img = soup.find("meta", property="og:image")
            print(f"OG Image: {og_img['content'] if og_img else 'None'}")
            
            # Tenta baixar se achou
            if og_img:
                img_url = og_img['content']
                if img_url.startswith("//"): img_url = "https:" + img_url
                
                print(f"Tentando baixar: {img_url}")
                img_res = scraper.get(img_url, timeout=10)
                print(f"Download Status: {img_res.status_code}")
                
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_image_process("https://www.hltv.org/news/43946/media-3dmax-to-swap-bodyy-for-misutaaa-nbk-to-join-as-assistant-coach")
