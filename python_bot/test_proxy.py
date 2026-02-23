import requests

def test_proxy_image():
    # Tenta carregar a imagem via proxy externo que costuma ignorar blocks de referer
    proxy_url = "https://images.weserv.nl/?url=img.hltv.org/images/article/main/43946"
    print(f"Testando proxy: {proxy_url}")
    
    try:
        res = requests.get(proxy_url, timeout=15)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("Sucesso! Proxy conseguiu acessar a imagem.")
        else:
            print(f"Falha no proxy: {res.status_code}")
    except Exception as e:
        print(f"Erro no proxy: {e}")

if __name__ == "__main__":
    test_proxy_image()
