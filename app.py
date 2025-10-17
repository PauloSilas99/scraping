import requests
from bs4 import BeautifulSoup
import time
import random

try:
    # Headers mais completos para simular um navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    # Criar uma sessão para manter cookies
    session = requests.Session()
    session.headers.update(headers)
    
    print("Fazendo requisição para o site...")
    
    # Adicionar delay aleatório para parecer mais humano
    time.sleep(random.uniform(1, 3))
    
    # Tentar diferentes URLs
    urls_teste = [
        "https://www.boticario.com.br/",
        "https://www.boticario.com.br/br/",
        "https://www.boticario.com.br/br/pt/",
    ]
    
    pagina = None
    for url in urls_teste:
        print(f"Tentando: {url}")
        try:
            pagina = session.get(url, timeout=15)
            print(f"Status: {pagina.status_code}")
            if pagina.status_code == 200:
                break
        except Exception as e:
            print(f"Erro com {url}: {e}")
            continue
    
    print(f"Status da requisição: {pagina.status_code}")
    
    if pagina.status_code == 200:
        dados_pagina = BeautifulSoup(pagina.text, "html.parser")
        print("Conteúdo da página obtido com sucesso!")
        print(f"Título da página: {dados_pagina.title.string if dados_pagina.title else 'Não encontrado'}")
        print(f"Tamanho do conteúdo: {len(pagina.text)} caracteres")
        
        # Mostrar apenas uma parte do conteúdo para não sobrecarregar o terminal
        print("\nPrimeiros 500 caracteres do HTML:")
        print("-" * 50)
        print(pagina.text[:500])
        print("-" * 50)
    else:
        print(f"Erro na requisição. Status: {pagina.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")