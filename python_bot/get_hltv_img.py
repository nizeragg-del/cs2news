import requests
from bs4 import BeautifulSoup

def get_hltv_image(url):
    print(f"Buscando: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"property": "og:image"})
            if og_img:
                print(f"OG_IMAGE: {og_img['content']}")
            
            img_tag = soup.select_one(".main-image img") or soup.select_one(".story img")
            if img_tag:
                print(f"IMG_TAG: {img_tag['src']}")
        else:
            print(f"Status Erro: {res.status_code}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    get_hltv_image("https://www.hltv.org/news/43946/media-3dmax-to-swap-bodyy-for-misutaaa-nbk-to-join-as-assistant-coach")
