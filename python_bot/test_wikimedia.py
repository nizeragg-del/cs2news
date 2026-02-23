import requests
import os

def test_wikimedia_download():
    # URL direta de um thumbnail/arquivo do Wikimedia para NBK
    img_url = "https://upload.wikimedia.org/wikipedia/commons/e/ed/Nathan_Schmitt_-_BLAST_Pro_Series_Miami_2019_%281%29.jpg"
    print(f"Tentando baixar do Wikimedia: {img_url}")
    
    headers = {
        "User-Agent": "GamerNewsBot/1.0 (contact: admin@gamernewsbrasil.com.br) Python-Requests"
    }
    
    try:
        res = requests.get(img_url, headers=headers, timeout=20)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            with open("nbk_wikimedia.jpg", "wb") as f:
                f.write(res.content)
            print("Sucesso! Imagem salva como nbk_wikimedia.jpg")
            return True
        else:
            print(f"Falha Wikimedia: {res.status_code}")
    except Exception as e:
        print(f"Erro Wikimedia: {e}")
    return False

if __name__ == "__main__":
    test_wikimedia_download()
