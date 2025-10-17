from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json

def scrape_boticario_products():
    """Extrai produtos do carrossel de perfumarias com descontos exclusivos"""
    driver = None
    try:
        # Configurar opções do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Instalar e configurar o driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Executar script para ocultar que é um bot
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🚀 Abrindo navegador e acessando o site...")
        driver.get("https://www.boticario.com.br/")
        
        # Aguardar a página carregar completamente
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print("✅ Página carregada! Procurando carrossel de perfumarias...")
        
        # Aguardar um pouco para o JavaScript carregar
        time.sleep(3)
        
        # Procurar diretamente pelos elementos com classe showcase-card-link-overlay
        print("🔍 Procurando elementos com classe 'showcase-card-link-overlay'...")
        
        # Aguardar um pouco mais para garantir que o JavaScript carregou
        time.sleep(5)
        
        # Procurar pelos elementos específicos
        product_elements = driver.find_elements(By.CSS_SELECTOR, '.showcase-card-link-overlay')
        print(f"🛍️ Encontrados {len(product_elements)} elementos com classe 'showcase-card-link-overlay'")
        
        if not product_elements:
            print("❌ Nenhum elemento encontrado. Procurando alternativas...")
            
            # Procurar por elementos similares
            alternative_selectors = [
                '[class*="showcase-card"]',
                '[class*="card-link"]',
                '[class*="product-card"]',
                'article',
                '.product-item'
            ]
            
            for selector in alternative_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"📋 Encontrados {len(elements)} elementos com seletor: {selector}")
                    product_elements = elements
                    break
            
            if not product_elements:
                print("❌ Nenhum produto encontrado com os seletores disponíveis")
                return False
        
        products_data = []
        
        for i, element in enumerate(product_elements):
            try:
                print(f"\n📦 Processando produto {i+1}/{len(product_elements)}...")
                
                # Scroll para o elemento para garantir que está visível
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(1)
                
                # Extrair dados do produto
                product_data = extract_product_data_from_showcase(element, driver)
                if product_data:
                    products_data.append(product_data)
                    print(f"✅ Produto extraído: {product_data.get('nome', 'Nome não encontrado')}")
                else:
                    print(f"❌ Falha ao extrair dados do produto {i+1}")
                    
            except Exception as e:
                print(f"❌ Erro ao processar produto {i+1}: {e}")
                continue
        
        # Salvar dados em JSON
        if products_data:
            with open('produtos_boticario.json', 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Dados salvos em 'produtos_boticario.json' - {len(products_data)} produtos")
            
            # Mostrar resumo
            print("\n📊 RESUMO DOS PRODUTOS:")
            print("=" * 50)
            for i, product in enumerate(products_data, 1):
                print(f"{i}. {product.get('nome', 'N/A')}")
                print(f"   Preço: {product.get('preco', 'N/A')}")
                print(f"   Desconto: {product.get('desconto', 'N/A')}")
                print(f"   Link: {product.get('link', 'N/A')}")
                print("-" * 30)
        
        return len(products_data) > 0
        
    except Exception as e:
        print(f"💥 Erro geral: {e}")
        return False
    finally:
        if driver:
            driver.quit()
            print("🔒 Navegador fechado")

def extract_product_data_from_showcase(showcase_element, driver):
    """Extrai dados específicos de um elemento showcase-card-link-overlay"""
    try:
        product_data = {}
        
        # Link do produto (o próprio elemento showcase-card-link-overlay é um link)
        try:
            product_data['link'] = showcase_element.get_attribute('href')
        except:
            product_data['link'] = None
        
        # Procurar pelo elemento pai que contém as informações do produto
        parent_element = showcase_element.find_element(By.XPATH, './..')
        
        # Nome do produto - procurar em diferentes locais
        nome_selectors = [
            'h3', 'h4', 'h2',
            '[class*="name"]', '[class*="title"]', '[class*="product-name"]',
            '.product-title', '.card-title', '.showcase-title'
        ]
        
        for selector in nome_selectors:
            try:
                nome_element = parent_element.find_element(By.CSS_SELECTOR, selector)
                if nome_element.text.strip():
                    product_data['nome'] = nome_element.text.strip()
                    break
            except:
                continue
        
        if 'nome' not in product_data:
            product_data['nome'] = "Nome não encontrado"
        
        # Preço atual
        preco_selectors = [
            '[class*="price"]', '[class*="preco"]', '[class*="current-price"]',
            '.price', '.valor', '.showcase-price', '.card-price'
        ]
        
        for selector in preco_selectors:
            try:
                preco_element = parent_element.find_element(By.CSS_SELECTOR, selector)
                if preco_element.text.strip():
                    product_data['preco'] = preco_element.text.strip()
                    break
            except:
                continue
        
        if 'preco' not in product_data:
            product_data['preco'] = "Preço não encontrado"
        
        # Preço original (se houver desconto)
        preco_original_selectors = [
            '[class*="original"]', '[class*="old"]', '[class*="before"]',
            '.old-price', '.preco-original', '.price-before', '.showcase-old-price'
        ]
        
        for selector in preco_original_selectors:
            try:
                preco_original = parent_element.find_element(By.CSS_SELECTOR, selector)
                if preco_original.text.strip():
                    product_data['preco_original'] = preco_original.text.strip()
                    break
            except:
                continue
        
        if 'preco_original' not in product_data:
            product_data['preco_original'] = None
        
        # Desconto
        desconto_selectors = [
            '[class*="discount"]', '[class*="desconto"]', '[class*="off"]',
            '.discount', '.off', '.showcase-discount', '.card-discount'
        ]
        
        for selector in desconto_selectors:
            try:
                desconto_element = parent_element.find_element(By.CSS_SELECTOR, selector)
                if desconto_element.text.strip():
                    product_data['desconto'] = desconto_element.text.strip()
                    break
            except:
                continue
        
        if 'desconto' not in product_data:
            product_data['desconto'] = None
        
        # Imagem
        try:
            img_element = parent_element.find_element(By.CSS_SELECTOR, 'img')
            product_data['imagem'] = img_element.get_attribute('src')
        except:
            product_data['imagem'] = None
        
        # Descrição/Resumo
        desc_selectors = [
            'p', '[class*="description"]', '[class*="desc"]', '[class*="summary"]',
            '.product-description', '.card-description', '.showcase-description'
        ]
        
        for selector in desc_selectors:
            try:
                desc_element = parent_element.find_element(By.CSS_SELECTOR, selector)
                if desc_element.text.strip():
                    product_data['descricao'] = desc_element.text.strip()
                    break
            except:
                continue
        
        if 'descricao' not in product_data:
            product_data['descricao'] = None
        
        # Informações adicionais específicas do showcase
        try:
            # Procurar por badges ou tags especiais
            badges = parent_element.find_elements(By.CSS_SELECTOR, '[class*="badge"], [class*="tag"], [class*="label"]')
            if badges:
                product_data['badges'] = [badge.text.strip() for badge in badges if badge.text.strip()]
        except:
            product_data['badges'] = []
        
        return product_data
        
    except Exception as e:
        print(f"❌ Erro ao extrair dados do showcase: {e}")
        return None

def extract_product_data(article_element, driver):
    """Função original mantida para compatibilidade"""
    return extract_product_data_from_showcase(article_element, driver)

if __name__ == "__main__":
    print("🛍️ Iniciando extração de produtos do Boticário...")
    print("=" * 60)
    
    success = scrape_boticario_products()
    
    if success:
        print("\n🎉 Extração concluída com sucesso!")
    else:
        print("\n❌ Falha na extração dos produtos")
        print("\n💡 Possíveis soluções:")
        print("1. Verifique se o site carregou completamente")
        print("2. O carrossel pode ter um seletor diferente")
        print("3. Tente executar novamente em alguns minutos")
