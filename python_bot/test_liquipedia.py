import requests
from bs4 import BeautifulSoup
import os

def test_liquipedia_image(player_name):
    url = f"https://liquipedia.net/counterstrike/{player_name}"
    print(f"Buscando player na Liquipedia: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            img_tag = soup.select_one(".infobox-image img")
            if img_tag:
                img_url = "https://liquipedia.net" + img_tag['src']
                print(f"Imagem encontrada: {img_url}")
                
                # Tenta baixar
                print(f"Baixando imagem...")
                img_res = requests.get(img_url, headers=headers, timeout=15)
                if img_res.status_code == 200:
                    with open(f"player_{player_name}.png", "wb") as f:
                        f.write(img_res.content)
                    print(f"Sucesso! Imagem salva como player_{player_name}.png")
                    return True
            else:
                print("Imagem não encontrada na infobox.")
    except Exception as e:
        print(f"Erro: {e}")
    return False

if __name__ == "__main__":
    test_liquipedia_image("NBK-")
