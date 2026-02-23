import urllib.request
import urllib.error
from bs4 import BeautifulSoup

def test_urllib(url):
    print(f"Testando urllib com: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            print(f"Status: {response.status}")
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            og_img = soup.find("meta", property="og:image")
            print(f"OG Image: {og_img['content'] if og_img else 'None'}")
            
    except Exception as e:
        print(f"Erro urllib: {e}")

if __name__ == "__main__":
    test_urllib("https://www.hltv.org/news/43946/media-3dmax-to-swap-bodyy-for-misutaaa-nbk-to-join-as-assistant-coach")
