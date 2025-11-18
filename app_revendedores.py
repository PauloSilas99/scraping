from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import os
import re
from datetime import datetime

def setup_driver():
    """Configura e retorna uma instância do Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver_path = ChromeDriverManager().install()
    
    if 'THIRD_PARTY_NOTICES' in driver_path or 'LICENSE' in driver_path:
        driver_dir = os.path.dirname(driver_path)
        driver_path = os.path.join(driver_dir, 'chromedriver')
    
    if os.path.exists(driver_path):
        os.chmod(driver_path, 0o755)
    
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def login(driver, wait, username, password):
    """
    Realiza login no portal de revendedores
    
    Args:
        driver: Instância do webdriver
        wait: Instância do WebDriverWait
        username: Usuário para login
        password: Senha para login
    
    Returns:
        bool: True se o login foi bem-sucedido, False caso contrário
    """
    try:
        print("🔐 Iniciando processo de login...")
        print(f"📍 Acessando: https://revendedores.grupoboticario.com.br/login")
        
        driver.get("https://revendedores.grupoboticario.com.br/login")
        
        # Aguardar página carregar
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        
        # Encontrar campo de usuário
        print("🔍 Procurando campo de usuário...")
        username_selectors = [
            'input#username',
            'input[name="username"]',
            'input[placeholder*="CPF"]',
            'input[autocomplete="username"]'
        ]
        
        username_field = None
        for selector in username_selectors:
            try:
                username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if username_field:
                    print(f"✅ Campo de usuário encontrado: {selector}")
                    break
            except:
                continue
        
        if not username_field:
            print("❌ Campo de usuário não encontrado")
            return False
        
        # Preencher usuário
        username_field.clear()
        username_field.send_keys(username)
        print(f"✅ Usuário preenchido: {username[:5]}***")
        time.sleep(1)
        
        # Encontrar campo de senha
        print("🔍 Procurando campo de senha...")
        password_selectors = [
            'input#password',
            'input[name="password"]',
            'input[type="password"]',
            'input[autocomplete="password"]'
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                if password_field:
                    print(f"✅ Campo de senha encontrado: {selector}")
                    break
            except:
                continue
        
        if not password_field:
            print("❌ Campo de senha não encontrado")
            return False
        
        # Preencher senha
        password_field.clear()
        password_field.send_keys(password)
        print("✅ Senha preenchida")
        time.sleep(1)
        
        # Encontrar botão de entrar
        print("🔍 Procurando botão 'Entrar'...")
        button_selectors = [
            'button[type="submit"]',
            'button:contains("Entrar")',
            'input[type="submit"]',
            'button[data-flora="button"]',
            '//button[contains(text(), "Entrar")]',
            '//input[@value="Entrar"]'
        ]
        
        login_button = None
        for selector in button_selectors:
            try:
                if ':contains' in selector or selector.startswith('//'):
                    login_button = driver.find_element(By.XPATH, '//button[contains(text(), "Entrar")] | //input[@value="Entrar"]')
                else:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                if login_button and login_button.is_displayed():
                    print(f"✅ Botão 'Entrar' encontrado")
                    break
            except:
                continue
        
        if not login_button:
            print("❌ Botão 'Entrar' não encontrado")
            return False
        
        # Clicar no botão de entrar
        try:
            driver.execute_script("arguments[0].click();", login_button)
            print("✅ Botão 'Entrar' clicado")
        except:
            try:
                login_button.click()
                print("✅ Botão 'Entrar' clicado")
            except Exception as e:
                print(f"❌ Erro ao clicar no botão: {e}")
                return False
        
        # Aguardar redirecionamento após login
        print("⏳ Aguardando redirecionamento após login...")
        time.sleep(5)
        
        # Verificar se o login foi bem-sucedido (URL mudou ou elementos da página principal aparecem)
        current_url = driver.current_url
        if 'login' not in current_url.lower():
            print("✅ Login realizado com sucesso!")
            return True
        else:
            print("⚠️ Pode não ter feito login. Verificando...")
            time.sleep(3)
            current_url = driver.current_url
            if 'login' not in current_url.lower():
                print("✅ Login realizado com sucesso!")
                return True
            else:
                print("❌ Falha no login - ainda está na página de login")
                return False
        
    except Exception as e:
        print(f"❌ Erro durante o login: {e}")
        return False

def extract_cycle_period(driver):
    """
    Extrai informações do período do ciclo exibido na página
    
    Returns:
        dict: Dicionário com informações do ciclo ou None
    """
    try:
        print("\n📅 Extraindo informações do período do ciclo...")
        
        # Procurar pelo elemento que contém a informação do ciclo
        cycle_selectors = [
            'small.css-2mmsys',
            'small[class*="css-"]',
            '//small[contains(@class, "css-")]',
            '//div[contains(text(), "Ciclo")]',
            '//*[contains(text(), "Ciclo")]'
        ]
        
        cycle_element = None
        for selector in cycle_selectors:
            try:
                if selector.startswith('//'):
                    cycle_element = driver.find_element(By.XPATH, selector)
                else:
                    cycle_element = driver.find_element(By.CSS_SELECTOR, selector)
                
                if cycle_element and cycle_element.is_displayed():
                    print(f"✅ Elemento do ciclo encontrado")
                    break
            except:
                continue
        
        if not cycle_element:
            print("⚠️ Informações do ciclo não encontradas na página")
            return None
        
        # Obter o texto completo
        cycle_text = cycle_element.text.strip()
        print(f"📋 Texto do ciclo: {cycle_text}")
        
        # Tentar extrair informações estruturadas
        # Formato esperado: "Ciclo 16: 03/11 a 30/11"
        cycle_info = {
            'texto_completo': cycle_text,
            'extraido_em': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Extrair número do ciclo
        ciclo_match = re.search(r'Ciclo\s+(\d+)', cycle_text)
        if ciclo_match:
            cycle_info['numero_ciclo'] = ciclo_match.group(1)
        
        # Extrair período (datas)
        periodo_match = re.search(r'(\d{2}/\d{2})\s+a\s+(\d{2}/\d{2})', cycle_text)
        if periodo_match:
            cycle_info['data_inicio'] = periodo_match.group(1)
            cycle_info['data_fim'] = periodo_match.group(2)
        
        print(f"✅ Informações do ciclo extraídas: {cycle_info}")
        return cycle_info
        
    except Exception as e:
        print(f"⚠️ Erro ao extrair informações do ciclo: {e}")
        return None

def click_ver_tudo_button(driver, wait):
    """
    Clica no botão "Ver tudo" para acessar a página de produtos
    
    Returns:
        bool: True se o botão foi clicado com sucesso, False caso contrário
    """
    try:
        print("\n🔍 Procurando botão 'Ver tudo'...")
        time.sleep(2)
        
        # Procurar pelo botão "Ver tudo"
        button_selectors = [
            'p[data-flora="typography"]:contains("Ver tudo")',
            '//p[contains(text(), "Ver tudo")]',
            '//p[@data-flora="typography"][contains(text(), "Ver tudo")]',
            'a:contains("Ver tudo")',
            '//a[contains(text(), "Ver tudo")]'
        ]
        
        ver_tudo_button = None
        for selector in button_selectors:
            try:
                if ':contains' in selector or selector.startswith('//'):
                    ver_tudo_button = driver.find_element(By.XPATH, '//p[contains(text(), "Ver tudo")] | //a[contains(text(), "Ver tudo")]')
                else:
                    ver_tudo_button = driver.find_element(By.CSS_SELECTOR, selector)
                
                if ver_tudo_button and ver_tudo_button.is_displayed():
                    print(f"✅ Botão 'Ver tudo' encontrado")
                    break
            except:
                continue
        
        if not ver_tudo_button:
            print("⚠️ Botão 'Ver tudo' não encontrado. Tentando continuar...")
            return False
        
        # Scroll até o botão
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ver_tudo_button)
        time.sleep(1)
        
        # Clicar no botão
        try:
            driver.execute_script("arguments[0].click();", ver_tudo_button)
            print("✅ Botão 'Ver tudo' clicado com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao clicar com JavaScript: {e}. Tentando clique direto...")
            try:
                ver_tudo_button.click()
                print("✅ Botão 'Ver tudo' clicado com sucesso!")
            except Exception as e2:
                print(f"❌ Erro ao clicar no botão: {e2}")
                return False
        
        # Aguardar página carregar
        print("⏳ Aguardando página de produtos carregar...")
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao clicar no botão 'Ver tudo': {e}")
        return False

def load_all_products(driver, wait, max_clicks=100):
    """
    Clica no botão 'Ver mais produtos' até que não haja mais produtos para carregar
    
    Args:
        driver: Instância do webdriver
        wait: Instância do WebDriverWait
        max_clicks: Número máximo de cliques (padrão: 100)
    
    Returns:
        int: Número de cliques realizados
    """
    clicks_count = 0
    previous_count = 0
    
    while clicks_count < max_clicks:
        try:
            print(f"\n🔄 Tentativa {clicks_count + 1}: Procurando botão 'Ver mais produtos'...")
            
            # Procurar pelo botão "Ver mais produtos"
            button_selectors = [
                'button[data-flora-text="ver-mais-produtos"]',
                'button[data-flora="button"]:contains("Ver mais produtos")',
                '//button[contains(text(), "Ver mais produtos")]',
                '//button[@data-flora-text="ver-mais-produtos"]'
            ]
            
            load_more_button = None
            for selector in button_selectors:
                try:
                    if ':contains' in selector or selector.startswith('//'):
                        load_more_button = driver.find_element(By.XPATH, '//button[contains(text(), "Ver mais produtos")]')
                    else:
                        load_more_button = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if load_more_button and load_more_button.is_displayed() and load_more_button.is_enabled():
                        break
                    else:
                        load_more_button = None
                except:
                    continue
            
            if not load_more_button:
                print("✅ Não há mais botão 'Ver mais produtos' disponível")
                break
            
            # Contar produtos atuais (precisa identificar seletor correto)
            # Vamos tentar encontrar produtos primeiro
            product_selectors = [
                '[class*="product"]',
                '[class*="card"]',
                '[class*="item"]',
                'article',
                '[data-testid*="product"]'
            ]
            
            current_products = []
            for selector in product_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        current_products = elements
                        break
                except:
                    continue
            
            current_count = len(current_products)
            
            if current_count == previous_count and clicks_count > 0:
                print("⚠️ Nenhum produto novo foi carregado. Parando...")
                break
            
            # Scroll até o botão
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more_button)
            time.sleep(1)
            
            # Clicar no botão
            try:
                driver.execute_script("arguments[0].click();", load_more_button)
                clicks_count += 1
                print(f"✅ Clique {clicks_count}: Carregando mais produtos...")
            except Exception as e:
                print(f"⚠️ Erro ao clicar no botão: {e}")
                try:
                    load_more_button.click()
                    clicks_count += 1
                    print(f"✅ Clique {clicks_count}: Carregando mais produtos...")
                except:
                    print("❌ Não foi possível clicar no botão. Parando...")
                    break
            
            # Aguardar novos produtos carregarem
            time.sleep(3)
            
            # Verificar se novos produtos foram carregados
            new_products = []
            for selector in product_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) > 0:
                        new_products = elements
                        break
                except:
                    continue
            
            new_count = len(new_products)
            
            if new_count > current_count:
                print(f"✅ {new_count - current_count} novos produtos carregados (Total: {new_count})")
                previous_count = current_count
            else:
                print("⏳ Aguardando produtos carregarem...")
                time.sleep(2)
                # Verificar novamente
                final_products = []
                for selector in product_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if len(elements) > 0:
                            final_products = elements
                            break
                    except:
                        continue
                
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
    
    final_count = len(driver.find_elements(By.CSS_SELECTOR, '[class*="product"], [class*="card"], article'))
    print(f"\n📊 Total de cliques realizados: {clicks_count}")
    return clicks_count

def extract_products(driver, wait):
    """
    Extrai dados de todos os produtos disponíveis na página
    
    Returns:
        list: Lista de dicionários com dados dos produtos
    """
    try:
        print("\n📦 Iniciando extração de dados dos produtos...")
        time.sleep(3)
        
        # Obter HTML da página para análise mais detalhada
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Procurar produtos na página usando múltiplos seletores
        product_selectors = [
            '[class*="product"]',
            '[class*="card"]',
            '[class*="item"]',
            'article',
            '[data-testid*="product"]',
            '[class*="grid"] > *',
            '[class*="product-card"]',
            '[class*="product-item"]',
            '[class*="showcase"]',
            'div[class*="col"]',
            'div[class*="product"]'
        ]
        
        product_elements = []
        max_elements = 0
        best_selector = None
        
        # Testar todos os seletores e escolher o que retorna mais elementos únicos
        for selector in product_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                # Filtrar elementos que parecem ser produtos (têm links, imagens, ou texto)
                filtered = []
                for elem in elements:
                    try:
                        # Verificar se tem características de produto
                        has_link = len(elem.find_elements(By.TAG_NAME, 'a')) > 0
                        has_img = len(elem.find_elements(By.TAG_NAME, 'img')) > 0
                        has_text = len(elem.text.strip()) > 10
                        
                        if has_link or (has_img and has_text):
                            filtered.append(elem)
                    except:
                        continue
                
                if len(filtered) > max_elements:
                    max_elements = len(filtered)
                    product_elements = filtered
                    best_selector = selector
            except:
                continue
        
        if product_elements:
            print(f"✅ Encontrados {len(product_elements)} elementos com seletor: {best_selector}")
        else:
            print("⚠️ Nenhum produto encontrado com seletores padrão. Tentando busca alternativa...")
            # Buscar por links que podem ser de produtos
            try:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                product_elements = []
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        if href and ('/produto' in href.lower() or '/product' in href.lower() or 'produto' in href.lower()):
                            parent = link.find_element(By.XPATH, './..')
                            if parent not in product_elements:
                                product_elements.append(parent)
                    except:
                        continue
                
                if product_elements:
                    print(f"✅ Encontrados {len(product_elements)} produtos via links")
                else:
                    raise Exception("Nenhum produto encontrado")
            except:
                print("❌ Não foi possível identificar produtos na página")
                # Salvar HTML para análise manual
                debug_file = 'produtos_revendedores/pagina_debug.html'
                os.makedirs('produtos_revendedores', exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print(f"💾 HTML da página salvo em {debug_file} para análise")
                return []
        
        print(f"🛍️ Total de produtos encontrados: {len(product_elements)}")
        
        products_data = []
        seen_links = set()
        seen_names = set()
        
        for i, element in enumerate(product_elements):
            try:
                if (i + 1) % 10 == 0 or i == 0:
                    print(f"📦 Processando produto {i+1}/{len(product_elements)}...")
                
                # Scroll para o elemento
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(0.3)
                
                # Extrair dados do produto
                product_data = extract_product_data(element, driver)
                
                if product_data:
                    product_link = product_data.get('link', '')
                    product_name = product_data.get('nome', '').strip()
                    
                    # Evitar duplicados por link ou nome
                    is_duplicate = False
                    if product_link and product_link in seen_links:
                        is_duplicate = True
                    elif product_name and product_name in seen_names and product_name != "Nome não encontrado":
                        is_duplicate = True
                    
                    if not is_duplicate:
                        products_data.append(product_data)
                        if product_link:
                            seen_links.add(product_link)
                        if product_name:
                            seen_names.add(product_name)
                        
            except Exception as e:
                print(f"❌ Erro ao processar produto {i+1}: {e}")
                continue
        
        print(f"✅ Total de produtos extraídos: {len(products_data)}")
        return products_data
        
    except Exception as e:
        print(f"❌ Erro ao extrair produtos: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_product_data(product_element, driver):
    """
    Extrai dados de um produto individual
    
    Returns:
        dict: Dicionário com dados do produto ou None
    """
    try:
        product_data = {}
        
        # Tentar extrair link (procurar em 'a' tags dentro do elemento)
        try:
            link_elements = product_element.find_elements(By.TAG_NAME, 'a')
            for link_elem in link_elements:
                href = link_elem.get_attribute('href')
                if href and ('produto' in href.lower() or 'product' in href.lower() or href.startswith('http')):
                    product_data['link'] = href
                    break
        except:
            pass
        
        if 'link' not in product_data:
            product_data['link'] = None
        
        # Tentar extrair nome (títulos, spans com nome, etc)
        nome_selectors = [
            'h1', 'h2', 'h3', 'h4', 'h5',
            '[class*="name"]', '[class*="title"]', '[class*="product-name"]',
            '[class*="nome"]', '[class*="titulo"]',
            'p[class*="name"]', 'span[class*="name"]',
            '[data-testid*="name"]', '[data-testid*="title"]'
        ]
        
        for selector in nome_selectors:
            try:
                nome_elements = product_element.find_elements(By.CSS_SELECTOR, selector)
                for nome_elem in nome_elements:
                    nome_text = nome_elem.text.strip()
                    if nome_text and len(nome_text) > 3:  # Ignorar textos muito curtos
                        product_data['nome'] = nome_text
                        break
                if 'nome' in product_data:
                    break
            except:
                continue
        
        if 'nome' not in product_data:
            # Tentar extrair nome do texto do link
            try:
                link_elem = product_element.find_element(By.TAG_NAME, 'a')
                alt_text = link_elem.get_attribute('aria-label') or link_elem.text.strip()
                if alt_text and len(alt_text) > 3:
                    product_data['nome'] = alt_text
            except:
                pass
        
        if 'nome' not in product_data:
            product_data['nome'] = "Nome não encontrado"
        
        # Tentar extrair preço atual
        preco_selectors = [
            '[class*="price"]', '[class*="preco"]', '[class*="valor"]',
            '[class*="current-price"]', '[class*="preco-atual"]',
            '[class*="price-current"]', '[data-testid*="price"]'
        ]
        
        for selector in preco_selectors:
            try:
                preco_elements = product_element.find_elements(By.CSS_SELECTOR, selector)
                for preco_elem in preco_elements:
                    preco_text = preco_elem.text.strip()
                    if preco_text and ('R$' in preco_text or 'reais' in preco_text.lower()):
                        product_data['preco'] = preco_text
                        break
                if 'preco' in product_data:
                    break
            except:
                continue
        
        if 'preco' not in product_data:
            product_data['preco'] = None
        
        # Tentar extrair preço original (se houver desconto)
        preco_original_selectors = [
            '[class*="original"]', '[class*="old"]', '[class*="before"]',
            '[class*="preco-original"]', '[class*="old-price"]',
            '[class*="price-before"]', '[data-testid*="old-price"]'
        ]
        
        for selector in preco_original_selectors:
            try:
                preco_original = product_element.find_element(By.CSS_SELECTOR, selector)
                if preco_original.text.strip():
                    product_data['preco_original'] = preco_original.text.strip()
                    break
            except:
                continue
        
        if 'preco_original' not in product_data:
            product_data['preco_original'] = None
        
        # Tentar extrair desconto
        desconto_selectors = [
            '[class*="discount"]', '[class*="desconto"]', '[class*="off"]',
            '[class*="badge"]', '[class*="tag"]', '[class*="promo"]'
        ]
        
        for selector in desconto_selectors:
            try:
                desconto_elements = product_element.find_elements(By.CSS_SELECTOR, selector)
                for desconto_elem in desconto_elements:
                    desconto_text = desconto_elem.text.strip()
                    if desconto_text and ('%' in desconto_text or 'off' in desconto_text.lower() or 'desconto' in desconto_text.lower()):
                        product_data['desconto'] = desconto_text
                        break
                if 'desconto' in product_data:
                    break
            except:
                continue
        
        if 'desconto' not in product_data:
            product_data['desconto'] = None
        
        # Tentar extrair imagem
        try:
            img_elements = product_element.find_elements(By.TAG_NAME, 'img')
            for img_elem in img_elements:
                src = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                if src and ('http' in src or 'data:image' in src):
                    product_data['imagem'] = src
                    break
        except:
            pass
        
        if 'imagem' not in product_data:
            product_data['imagem'] = None
        
        # Tentar extrair descrição
        desc_selectors = [
            '[class*="description"]', '[class*="desc"]', '[class*="summary"]',
            'p', '[class*="text"]'
        ]
        
        for selector in desc_selectors:
            try:
                desc_elements = product_element.find_elements(By.CSS_SELECTOR, selector)
                for desc_elem in desc_elements:
                    desc_text = desc_elem.text.strip()
                    if desc_text and len(desc_text) > 10 and desc_text != product_data.get('nome', ''):
                        product_data['descricao'] = desc_text[:200]  # Limitar tamanho
                        break
                if 'descricao' in product_data:
                    break
            except:
                continue
        
        if 'descricao' not in product_data:
            product_data['descricao'] = None
        
        # Extrair texto completo para análise posterior (limitado)
        try:
            full_text = product_element.text.strip()
            product_data['texto_completo'] = full_text[:300] if len(full_text) > 300 else full_text
        except:
            product_data['texto_completo'] = None
        
        return product_data
        
    except Exception as e:
        print(f"⚠️ Erro ao extrair dados do produto: {e}")
        return None

def save_data(cycle_info, products_data, base_dir='produtos_revendedores'):
    """
    Salva as informações do ciclo e produtos em arquivos JSON
    
    O arquivo do ciclo é salvo PRIMEIRO no início da pasta (como solicitado).
    
    Args:
        cycle_info: Dicionário com informações do ciclo
        products_data: Lista de dicionários com dados dos produtos
        base_dir: Diretório base para salvar os arquivos
    """
    try:
        # Criar diretório se não existir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            print(f"📁 Pasta '{base_dir}' criada")
        
        # Salvar informações do ciclo PRIMEIRO (fundamental para controle de dados)
        if cycle_info:
            cycle_file = os.path.join(base_dir, 'ciclo_periodo.json')
            with open(cycle_file, 'w', encoding='utf-8') as f:
                json.dump(cycle_info, f, ensure_ascii=False, indent=2)
            print(f"💾 Informações do ciclo salvas em: {cycle_file}")
            print(f"   📅 Ciclo: {cycle_info.get('numero_ciclo', 'N/A')} | Período: {cycle_info.get('data_inicio', 'N/A')} a {cycle_info.get('data_fim', 'N/A')}")
        else:
            print("⚠️ Informações do ciclo não foram extraídas")
        
        # Salvar produtos
        if products_data:
            produtos_por_arquivo = 100
            total_produtos = len(products_data)
            arquivos_criados = []
            
            for i in range(0, total_produtos, produtos_por_arquivo):
                inicio = i + 1
                fim = min(i + produtos_por_arquivo, total_produtos)
                
                produtos_lote = products_data[i:fim]
                
                nome_arquivo = f'produtos_{inicio:03d}_{fim:03d}.json'
                caminho_arquivo = os.path.join(base_dir, nome_arquivo)
                
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(produtos_lote, f, ensure_ascii=False, indent=2)
                
                arquivos_criados.append(caminho_arquivo)
                print(f"💾 Arquivo criado: {caminho_arquivo} - {len(produtos_lote)} produtos")
            
            print(f"\n✅ Total de {total_produtos} produtos salvos em {len(arquivos_criados)} arquivo(s)")
            print(f"📁 Pasta: {base_dir}/")
            
            # Mostrar resumo
            print("\n📊 ARQUIVOS CRIADOS:")
            print("=" * 50)
            for arquivo in arquivos_criados:
                print(f"  - {arquivo}")
            
            # Mostrar primeiros produtos
            if products_data:
                print("\n📊 RESUMO DOS PRIMEIROS PRODUTOS:")
                print("=" * 50)
                for i, product in enumerate(products_data[:5], 1):
                    print(f"{i}. {product.get('nome', 'N/A')[:60]}...")
                    print(f"   Preço: {product.get('preco', 'N/A')}")
                    print("-" * 30)
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")

def scrape_revendedores():
    """Função principal para realizar scraping do portal de revendedores"""
    driver = None
    try:
        print("🚀 Iniciando extração do portal de revendedores do Grupo Boticário...")
        print("=" * 70)
        
        # Credenciais
        username = "92700934334"
        password = "F81Q80k09m14@"
        
        # Configurar driver
        driver = setup_driver()
        wait = WebDriverWait(driver, 20)
        
        # PASSO 1: Login
        print("\n" + "="*70)
        print("📋 PASSO 1: Realizando login...")
        print("="*70)
        if not login(driver, wait, username, password):
            print("❌ Falha no login. Encerrando...")
            return False
        
        time.sleep(3)
        
        # PASSO 2: Extrair informações do ciclo
        print("\n" + "="*70)
        print("📋 PASSO 2: Extraindo informações do ciclo...")
        print("="*70)
        cycle_info = extract_cycle_period(driver)
        
        # PASSO 3: Clicar em "Ver tudo"
        print("\n" + "="*70)
        print("📋 PASSO 3: Navegando para página de produtos...")
        print("="*70)
        click_ver_tudo_button(driver, wait)
        
        time.sleep(3)
        
        # PASSO 4: Carregar todos os produtos
        print("\n" + "="*70)
        print("📋 PASSO 4: Carregando todos os produtos disponíveis...")
        print("="*70)
        load_all_products(driver, wait)
        
        time.sleep(2)
        
        # PASSO 5: Extrair dados dos produtos
        print("\n" + "="*70)
        print("📋 PASSO 5: Extraindo dados dos produtos...")
        print("="*70)
        products_data = extract_products(driver, wait)
        
        # PASSO 6: Salvar dados
        print("\n" + "="*70)
        print("📋 PASSO 6: Salvando dados extraídos...")
        print("="*70)
        save_data(cycle_info, products_data)
        
        print("\n" + "="*70)
        print("🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n💥 Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if driver:
            print("\n🔒 Fechando navegador...")
            driver.quit()

if __name__ == "__main__":
    scrape_revendedores()

