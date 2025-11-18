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
import os

def click_see_more_button(driver, wait):
    """
    Clica no botão "Veja Mais" para acessar a página de produtos
    
    Args:
        driver: Instância do webdriver
        wait: Instância do WebDriverWait
    
    Returns:
        bool: True se o botão foi clicado com sucesso, False caso contrário
    """
    try:
        print("🔍 Procurando botão 'Veja Mais'...")
        
        # Aguardar um pouco para o JavaScript carregar
        time.sleep(2)
        
        # Procurar pelo botão "Veja Mais" usando diferentes seletores
        see_more_button = None
        button_selectors = [
            '.slot-see-more',
            'span.slot-see-more',
            'span[class*="see-more"]',
            '//span[contains(@class, "see-more")]',
            '//span[contains(text(), "Veja Mais")]'
        ]
        
        for selector in button_selectors:
            try:
                if selector.startswith('//'):
                    # XPath
                    see_more_button = driver.find_element(By.XPATH, selector)
                else:
                    # CSS Selector
                    see_more_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                if see_more_button:
                    # Verificar se o botão está visível e habilitado
                    if see_more_button.is_displayed():
                        print(f"✅ Botão 'Veja Mais' encontrado usando: {selector}")
                        break
                    else:
                        see_more_button = None
            except:
                continue
        
        if not see_more_button:
            print("⚠️ Botão 'Veja Mais' não encontrado. Tentando continuar...")
            return False
        
        # Scroll até o botão para garantir que está visível
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", see_more_button)
        time.sleep(1)
        
        # Clicar no botão usando JavaScript para garantir que funcione
        try:
            driver.execute_script("arguments[0].click();", see_more_button)
            print("✅ Botão 'Veja Mais' clicado com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao clicar com JavaScript: {e}. Tentando clique direto...")
            try:
                see_more_button.click()
                print("✅ Botão 'Veja Mais' clicado com sucesso!")
            except Exception as e2:
                print(f"❌ Erro ao clicar no botão: {e2}")
                return False
        
        # Aguardar a página carregar após o clique
        print("⏳ Aguardando página carregar após clique...")
        time.sleep(3)
        
        # Verificar se a URL mudou ou se a página carregou
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.showcase-card-link-overlay')))
            print("✅ Página carregada com sucesso!")
        except:
            print("⚠️ Aguardando mais tempo para produtos aparecerem...")
            time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao clicar no botão 'Veja Mais': {e}")
        return False

def load_all_products(driver, wait, max_clicks=50):
    """
    Clica no botão 'Carregar mais' até que não haja mais produtos para carregar
    
    Args:
        driver: Instância do webdriver
        wait: Instância do WebDriverWait
        max_clicks: Número máximo de cliques para evitar loop infinito (padrão: 50)
    
    Returns:
        int: Número de cliques realizados
    """
    clicks_count = 0
    previous_count = 0
    
    while clicks_count < max_clicks:
        try:
            # Procurar pelo botão "Carregar mais"
            load_more_button = None
            
            # Tentar diferentes seletores para o botão
            button_selectors = [
                '.btn-load-more',
                '.js-load-more',
                'button.btn-load-more',
                'button[class*="load-more"]',
                'button:contains("Carregar mais")'
            ]
            
            for selector in button_selectors:
                try:
                    if ':contains' in selector:
                        # Buscar por texto usando XPath
                        load_more_button = driver.find_element(By.XPATH, '//button[contains(text(), "Carregar mais")]')
                    else:
                        load_more_button = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if load_more_button:
                        # Verificar se o botão está visível e habilitado
                        if load_more_button.is_displayed() and load_more_button.is_enabled():
                            break
                        else:
                            load_more_button = None
                except:
                    continue
            
            if not load_more_button:
                print("✅ Não há mais botão 'Carregar mais' disponível")
                break
            
            # Contar produtos atuais antes do clique
            current_products = driver.find_elements(By.CSS_SELECTOR, '.showcase-card-link-overlay')
            current_count = len(current_products)
            
            if current_count == previous_count and clicks_count > 0:
                print("⚠️ Nenhum produto novo foi carregado. Parando...")
                break
            
            # Scroll até o botão para garantir que está visível
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more_button)
            time.sleep(1)
            
            # Clicar no botão usando JavaScript para garantir que funcione
            try:
                driver.execute_script("arguments[0].click();", load_more_button)
                clicks_count += 1
                print(f"🔄 Clique {clicks_count}: Carregando mais produtos...")
            except Exception as e:
                print(f"⚠️ Erro ao clicar no botão: {e}")
                # Tentar clicar diretamente
                try:
                    load_more_button.click()
                    clicks_count += 1
                    print(f"🔄 Clique {clicks_count}: Carregando mais produtos...")
                except:
                    print("❌ Não foi possível clicar no botão. Parando...")
                    break
            
            # Aguardar novos produtos carregarem
            time.sleep(3)
            
            # Verificar se novos produtos foram carregados
            new_products = driver.find_elements(By.CSS_SELECTOR, '.showcase-card-link-overlay')
            new_count = len(new_products)
            
            if new_count > current_count:
                print(f"✅ {new_count - current_count} novos produtos carregados (Total: {new_count})")
                previous_count = current_count
            else:
                print("⏳ Aguardando produtos carregarem...")
                time.sleep(2)
                # Verificar novamente
                final_products = driver.find_elements(By.CSS_SELECTOR, '.showcase-card-link-overlay')
                final_count = len(final_products)
                if final_count == current_count:
                    print("✅ Todos os produtos já foram carregados")
                    break
                else:
                    print(f"✅ {final_count - current_count} novos produtos carregados (Total: {final_count})")
                    previous_count = current_count
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar mais produtos: {e}")
            break
    
    final_count = len(driver.find_elements(By.CSS_SELECTOR, '.showcase-card-link-overlay'))
    print(f"📊 Total de produtos carregados: {final_count}")
    return clicks_count

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
        driver_path = ChromeDriverManager().install()
        
        # Corrigir caminho se necessário (webdriver-manager pode retornar arquivo errado)
        if 'THIRD_PARTY_NOTICES' in driver_path or 'LICENSE' in driver_path:
            # Encontrar o diretório correto e usar o executável chromedriver
            driver_dir = os.path.dirname(driver_path)
            driver_path = os.path.join(driver_dir, 'chromedriver')
        
        # Garantir que o arquivo é executável
        if os.path.exists(driver_path):
            os.chmod(driver_path, 0o755)
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Executar script para ocultar que é um bot
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🚀 Abrindo navegador e acessando o site...")
        driver.get("https://www.boticario.com.br/")
        
        # Aguardar a página carregar completamente
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print("✅ Página inicial carregada!")
        
        # Aguardar um pouco para o JavaScript carregar
        time.sleep(3)
        
        # PASSO 1: Clicar no botão "Veja Mais" primeiro
        print("\n" + "="*60)
        print("📋 PASSO 1: Clicando no botão 'Veja Mais'...")
        print("="*60)
        see_more_clicked = click_see_more_button(driver, wait)
        
        if not see_more_clicked:
            print("⚠️ Não foi possível clicar no 'Veja Mais'. Tentando continuar...")
        
        # Aguardar um pouco mais para garantir que a página carregou
        time.sleep(2)
        
        # PASSO 2: Procurar produtos e clicar no "Carregar mais produtos"
        print("\n" + "="*60)
        print("📋 PASSO 2: Carregando todos os produtos disponíveis...")
        print("="*60)
        print("🔍 Procurando produtos com classe 'showcase-card-link-overlay'...")
        
        # Verificar quantos produtos já existem antes de clicar no "Carregar mais"
        initial_products = driver.find_elements(By.CSS_SELECTOR, '.showcase-card-link-overlay')
        print(f"📊 Produtos iniciais encontrados: {len(initial_products)}")
        
        # Carregar todos os produtos clicando no botão "Carregar mais produtos"
        load_all_products(driver, wait)
        
        # PASSO 3: Extrair todos os produtos após carregar tudo
        print("\n" + "="*60)
        print("📋 PASSO 3: Extraindo dados de todos os produtos...")
        print("="*60)
        
        # Aguardar um pouco mais para garantir que o JavaScript carregou
        time.sleep(2)
        
        # Procurar pelos elementos específicos
        product_elements = driver.find_elements(By.CSS_SELECTOR, '.showcase-card-link-overlay')
        print(f"🛍️ Total de produtos encontrados: {len(product_elements)}")
        print(f"📊 Total de produtos disponíveis na página: {len(product_elements)}")
        
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
        seen_links = set()  # Para evitar produtos duplicados
        
        print(f"\n📦 Iniciando extração de dados de {len(product_elements)} produtos...")
        
        for i, element in enumerate(product_elements):
            try:
                print(f"\n📦 Processando produto {i+1}/{len(product_elements)}...")
                
                # Scroll para o elemento para garantir que está visível
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(0.5)
                
                # Extrair dados do produto
                product_data = extract_product_data_from_showcase(element, driver)
                if product_data:
                    # Verificar se o produto já foi extraído (usando o link como identificador único)
                    product_link = product_data.get('link', '')
                    if product_link and product_link not in seen_links:
                        products_data.append(product_data)
                        seen_links.add(product_link)
                        print(f"✅ Produto extraído: {product_data.get('nome', 'Nome não encontrado')[:50]}...")
                    elif product_link:
                        print(f"⏭️ Produto duplicado ignorado: {product_data.get('nome', 'Nome não encontrado')[:50]}...")
                    else:
                        # Se não tiver link, adicionar mesmo assim (pode ser um produto válido)
                        products_data.append(product_data)
                        print(f"✅ Produto extraído (sem link): {product_data.get('nome', 'Nome não encontrado')[:50]}...")
                else:
                    print(f"❌ Falha ao extrair dados do produto {i+1}")
                    
            except Exception as e:
                print(f"❌ Erro ao processar produto {i+1}: {e}")
                continue
        
        # Salvar dados em JSON (arquivos de 100 produtos cada)
        total_produtos = len(products_data)
        if products_data:
            # Criar pasta "produtos" se não existir
            produtos_dir = 'produtos'
            if not os.path.exists(produtos_dir):
                os.makedirs(produtos_dir)
                print(f"📁 Pasta '{produtos_dir}' criada")
            
            # Salvar produtos em arquivos de 100
            produtos_por_arquivo = 100
            arquivos_criados = []
            
            for i in range(0, total_produtos, produtos_por_arquivo):
                # Calcular intervalo do arquivo
                inicio = i + 1
                fim = min(i + produtos_por_arquivo, total_produtos)
                
                # Extrair produtos para este arquivo
                produtos_lote = products_data[i:fim]
                
                # Nome do arquivo: produtos_001_100.json, produtos_101_200.json, etc.
                nome_arquivo = f'produtos_{inicio:03d}_{fim:03d}.json'
                caminho_arquivo = os.path.join(produtos_dir, nome_arquivo)
                
                # Salvar arquivo
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(produtos_lote, f, ensure_ascii=False, indent=2)
                
                arquivos_criados.append(caminho_arquivo)
                print(f"💾 Arquivo criado: {caminho_arquivo} - {len(produtos_lote)} produtos (produtos {inicio} a {fim})")
            
            print(f"\n✅ Total de {total_produtos} produtos extraídos e salvos em {len(arquivos_criados)} arquivo(s)")
            print(f"📁 Pasta: {produtos_dir}/")
            
            # Mostrar resumo dos arquivos criados
            print("\n📊 ARQUIVOS CRIADOS:")
            print("=" * 50)
            for arquivo in arquivos_criados:
                print(f"  - {arquivo}")
            
            # Mostrar resumo dos produtos (primeiros 10 apenas)
            print("\n📊 RESUMO DOS PRIMEIROS PRODUTOS:")
            print("=" * 50)
            for i, product in enumerate(products_data[:10], 1):
                print(f"{i}. {product.get('nome', 'N/A')[:60]}...")
                print(f"   Preço: {product.get('preco', 'N/A')}")
                print(f"   Desconto: {product.get('desconto', 'N/A')}")
                print("-" * 30)
            
            if total_produtos > 10:
                print(f"\n... e mais {total_produtos - 10} produtos")
            
            print(f"\n{'='*60}")
            print(f"🎉 EXTRAÇÃO CONCLUÍDA!")
            print(f"📊 Total de produtos extraídos: {total_produtos}")
            print(f"📁 Arquivos salvos na pasta: {produtos_dir}/")
            print(f"{'='*60}")
        
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
