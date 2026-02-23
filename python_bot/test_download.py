import cloudscraper
import os

def test_download():
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # URL provável da imagem
    img_url = "https://img-cdn.hltv.org/static/38210.png" # Uma que vimos no DB antes
    print(f"Tentando baixar: {img_url}")
    
    try:
        response = scraper.get(img_url, timeout=15)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            with open("test_img.png", "wb") as f:
                f.write(response.content)
            print("Download concluído com sucesso! Arquivo: test_img.png")
        else:
            print(f"Falha: {response.status_code}")
    except Exception as e:
        print(f"Erro no download: {e}")

if __name__ == "__main__":
    test_download()
