from curl_cffi import requests
from bs4 import BeautifulSoup

def test_curl_cffi(url):
    print(f"Testando curl-cffi com: {url}")
    try:
        # 'impersonate' faz a mágica de mimetizar o TLS do navegador
        response = requests.get(url, impersonate="chrome120", timeout=20)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            og_img = soup.find("meta", property="og:image")
            print(f"OG Image: {og_img['content'] if og_img else 'None'}")
            
            # Tenta baixar a imagem com impersonate também
            if og_img:
                img_url = og_img['content']
                if img_url.startswith("//"): img_url = "https:" + img_url
                print(f"Baixando imagem com curl-cffi: {img_url}")
                img_res = requests.get(img_url, impersonate="chrome120", timeout=15)
                print(f"Download Status: {img_res.status_code}")
                if img_res.status_code == 200:
                    print("Download realizado com sucesso!")
        else:
            print(f"Falha: {response.text[:200]}")
            
    except Exception as e:
        print(f"Erro curl-cffi: {e}")

if __name__ == "__main__":
    test_curl_cffi("https://www.hltv.org/news/43946/media-3dmax-to-swap-bodyy-for-misutaaa-nbk-to-join-as-assistant-coach")
