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
            
            # Contar produtos atuais usando o seletor correto dos cards
            current_products = driver.find_elements(By.CSS_SELECTOR, 'div[data-flora="card"]')
            current_count = len(current_products)
            print(f"📊 Produtos atuais na página: {current_count}")
            
            # Procurar pelo botão "Ver mais produtos" - pode ser um <p> dentro de um botão
            load_more_button = None
            try:
                # Primeiro tentar encontrar o <p> com o texto
                p_element = driver.find_element(By.XPATH, '//p[contains(text(), "Ver mais produtos")]')
                # Tentar encontrar o botão pai
                try:
                    load_more_button = p_element.find_element(By.XPATH, './ancestor::button')
                except:
                    # Se não encontrar botão pai, tentar clicar no próprio <p>
                    load_more_button = p_element
                print("✅ Botão 'Ver mais produtos' encontrado via <p>")
            except:
                # Tentar encontrar diretamente um botão
                try:
                    load_more_button = driver.find_element(By.XPATH, '//button[.//p[contains(text(), "Ver mais produtos")]]')
                    print("✅ Botão 'Ver mais produtos' encontrado via botão")
                except:
                    try:
                        load_more_button = driver.find_element(By.XPATH, '//button[contains(text(), "Ver mais produtos")]')
                        print("✅ Botão 'Ver mais produtos' encontrado via texto do botão")
                    except:
                        pass
            
            if not load_more_button:
                print("✅ Não há mais botão 'Ver mais produtos' disponível")
                break
            
            if not (load_more_button.is_displayed() and (not hasattr(load_more_button, 'is_enabled') or load_more_button.is_enabled())):
                print("⚠️ Botão encontrado mas não está disponível")
                break
            
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
            time.sleep(4)
            
            # Verificar se novos produtos foram carregados
            new_products = driver.find_elements(By.CSS_SELECTOR, 'div[data-flora="card"]')
            new_count = len(new_products)
            
            if new_count > current_count:
                print(f"✅ {new_count - current_count} novos produtos carregados (Total: {new_count})")
                previous_count = current_count
            else:
                print("⏳ Aguardando produtos carregarem...")
                time.sleep(2)
                # Verificar novamente
                final_products = driver.find_elements(By.CSS_SELECTOR, 'div[data-flora="card"]')
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
    
    final_count = len(driver.find_elements(By.CSS_SELECTOR, 'div[data-flora="card"]'))
    print(f"\n📊 Total de cliques realizados: {clicks_count}")
    print(f"📊 Total de produtos carregados: {final_count}")
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
        
        # Procurar produtos usando o seletor correto dos cards
        product_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-flora="card"]')
        
        if not product_elements:
            print("⚠️ Nenhum produto encontrado. Tentando busca alternativa...")
            # Tentar buscar por classe alternativa
            try:
                product_elements = driver.find_elements(By.CSS_SELECTOR, 'div.flora--c-jAOGHF')
                if product_elements:
                    print(f"✅ Encontrados {len(product_elements)} produtos via classe alternativa")
            except:
                pass
            
            if not product_elements:
                print("❌ Não foi possível identificar produtos na página")
                # Salvar HTML para análise manual
                page_source = driver.page_source
                debug_file = 'produtos_revendedores/pagina_debug.html'
                os.makedirs('produtos_revendedores', exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print(f"💾 HTML da página salvo em {debug_file} para análise")
                return []
        
        print(f"✅ Encontrados {len(product_elements)} cards de produtos")
        
        print(f"🛍️ Total de produtos encontrados: {len(product_elements)}")
        
        products_data = []
        seen_links = set()
        seen_skus = set()
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
                    product_sku = product_data.get('sku', '')
                    product_name = product_data.get('nome', '').strip()
                    
                    # Evitar duplicados por SKU (mais confiável), link ou nome
                    is_duplicate = False
                    if product_sku and product_sku in seen_skus:
                        is_duplicate = True
                    elif product_link and product_link in seen_links:
                        is_duplicate = True
                    elif product_name and product_name in seen_names and product_name != "Nome não encontrado":
                        is_duplicate = True
                    
                    if not is_duplicate:
                        products_data.append(product_data)
                        if product_sku:
                            seen_skus.add(product_sku)
                        if product_link:
                            seen_links.add(product_link)
                        if product_name:
                            seen_names.add(product_name)
                    else:
                        if (i + 1) % 50 == 0:
                            print(f"⏭️ Produto duplicado ignorado (SKU: {product_sku or 'N/A'})")
                        
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
    Extrai dados de um produto individual do card
    
    Estrutura esperada do card:
    - div[data-flora="card"] contendo:
      - Link do produto (a tag com href)
      - SKU (código do produto em uma tag)
      - Imagem do produto
      - Nome do produto
      - Preço "Pague": R$ 118,52
      - Preço "Revenda": R$ 139,44
      - Preço "Lucre": R$ 20,92
      - Desconto: -15%
      - Preço original: R$ 164,90
      - Tag de promoção
    
    Returns:
        dict: Dicionário com dados do produto ou None
    """
    try:
        product_data = {}
        
        # 1. Extrair link do produto
        try:
            link_element = product_element.find_element(By.CSS_SELECTOR, 'a[href*="/produto"]')
            href = link_element.get_attribute('href')
            if href:
                # Completar URL se for relativa
                if href.startswith('/'):
                    product_data['link'] = f"https://revendedores.grupoboticario.com.br{href}"
                else:
                    product_data['link'] = href
            else:
                product_data['link'] = None
        except:
            product_data['link'] = None
        
        # 2. Extrair SKU (código do produto) - está em uma tag com data-custom="true"
        try:
            sku_element = product_element.find_element(By.CSS_SELECTOR, 'span[data-custom="true"] p')
            sku_text = sku_element.text.strip()
            if sku_text and sku_text.isdigit():
                product_data['sku'] = sku_text
            else:
                product_data['sku'] = None
        except:
            product_data['sku'] = None
        
        # 3. Extrair nome do produto - está em um <p> dentro de div.flora--c-ieqJkR
        try:
            nome_element = product_element.find_element(By.CSS_SELECTOR, 'div.flora--c-ieqJkR p')
            product_data['nome'] = nome_element.text.strip()
        except:
            try:
                # Tentar alternativa
                nome_element = product_element.find_element(By.CSS_SELECTOR, 'a[href*="/produto"] img')
                product_data['nome'] = nome_element.get_attribute('alt') or "Nome não encontrado"
            except:
                product_data['nome'] = "Nome não encontrado"
        
        # 4. Extrair imagem
        try:
            img_element = product_element.find_element(By.CSS_SELECTOR, 'img')
            # Tentar src primeiro, depois srcset
            src = img_element.get_attribute('src')
            if not src or 'data:image' in src:
                # Extrair do srcset
                srcset = img_element.get_attribute('srcset')
                if srcset:
                    # Pegar a primeira URL do srcset
                    src = srcset.split(',')[0].strip().split(' ')[0]
            product_data['imagem'] = src if src else None
        except:
            product_data['imagem'] = None
        
        # 5. Extrair preço "Pague" - está em um <p> dentro de div com data-pague="true"
        try:
            pague_element = product_element.find_element(By.CSS_SELECTOR, 'div[data-pague="true"] p.flora--c-PJLV-gvAhgR')
            preco_pague = pague_element.text.strip()
            product_data['preco_pague'] = preco_pague if preco_pague else None
        except:
            product_data['preco_pague'] = None
        
        # 6. Extrair preço "Revenda"
        try:
            # Procurar pelo texto "Revenda" e pegar o próximo <p> com preço
            revenda_section = product_element.find_element(By.XPATH, './/p[contains(text(), "Revenda")]/following-sibling::p[1]')
            preco_revenda = revenda_section.text.strip()
            product_data['preco_revenda'] = preco_revenda if preco_revenda else None
        except:
            product_data['preco_revenda'] = None
        
        # 7. Extrair preço "Lucre"
        try:
            lucre_section = product_element.find_element(By.XPATH, './/p[contains(text(), "Lucre")]/following-sibling::p[1]')
            preco_lucre = lucre_section.text.strip()
            product_data['preco_lucre'] = preco_lucre if preco_lucre else None
        except:
            product_data['preco_lucre'] = None
        
        # 8. Extrair desconto - está em um <p> com data-testid="discount"
        try:
            desconto_element = product_element.find_element(By.CSS_SELECTOR, 'p[data-testid="discount"]')
            product_data['desconto'] = desconto_element.text.strip()
        except:
            product_data['desconto'] = None
        
        # 9. Extrair preço original (antes do desconto) - está em um <p> antes do preço com desconto
        try:
            # Procurar pelo preço que está antes do desconto
            preco_original_element = product_element.find_element(By.CSS_SELECTOR, 'div[data-pague="true"] p.flora--c-PJLV-gxwRVS')
            preco_original = preco_original_element.text.strip()
            product_data['preco_original'] = preco_original if preco_original else None
        except:
            product_data['preco_original'] = None
        
        # 10. Extrair tag de promoção - está em um span com data-custom="promotion"
        try:
            promo_element = product_element.find_element(By.CSS_SELECTOR, 'span[data-custom="promotion"] p span')
            product_data['tag_promocao'] = promo_element.get_attribute('aria-label') or promo_element.text.strip()
        except:
            try:
                # Tentar alternativa
                promo_element = product_element.find_element(By.CSS_SELECTOR, 'span[data-custom="promotion"]')
                product_data['tag_promocao'] = promo_element.text.strip() if promo_element.text.strip() else None
            except:
                product_data['tag_promocao'] = None
        
        # 11. Verificar disponibilidade
        try:
            available = product_element.find_element(By.CSS_SELECTOR, 'div[data-available="true"]')
            product_data['disponivel'] = True
        except:
            product_data['disponivel'] = False
        
        return product_data
        
    except Exception as e:
        print(f"⚠️ Erro ao extrair dados do produto: {e}")
        import traceback
        traceback.print_exc()
        return None

def format_cycle_info(cycle_info):
    """
    Formata as informações do ciclo para o padrão do JSON
    
    Args:
        cycle_info: Dicionário com informações do ciclo extraídas
    
    Returns:
        dict: Dicionário formatado com estrutura ciclo_info
    """
    if not cycle_info:
        return None
    
    # Converter datas de DD/MM para YYYY-MM-DD
    def convert_date(date_str):
        if not date_str:
            return None
        try:
            # Formato: "03/11" -> "2025-11-03" (assumindo ano atual)
            parts = date_str.split('/')
            if len(parts) == 2:
                day, month = parts
                year = datetime.now().year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        return None
    
    numero_ciclo = cycle_info.get('numero_ciclo', '')
    data_inicio_str = cycle_info.get('data_inicio', '')
    data_fim_str = cycle_info.get('data_fim', '')
    
    # Criar formato do ciclo: "16/2025" ou similar
    ano_atual = datetime.now().year
    ciclo_numero_formatado = f"{numero_ciclo.zfill(2)}/{ano_atual}" if numero_ciclo else f"01/{ano_atual}"
    
    # Criar nome do ciclo baseado no período
    nome_ciclo = f"Ciclo {numero_ciclo} {ano_atual}" if numero_ciclo else f"Ciclo {ano_atual}"
    
    formatted = {
        "numero": ciclo_numero_formatado,
        "nome": nome_ciclo,
        "data_inicio": convert_date(data_inicio_str) or f"{ano_atual}-01-01",
        "data_fim": convert_date(data_fim_str) or f"{ano_atual}-12-31"
    }
    
    return formatted

def format_product(product_data):
    """
    Formata um produto para o padrão do JSON
    
    Args:
        product_data: Dicionário com dados do produto extraídos
    
    Returns:
        dict: Dicionário formatado com estrutura do produto
    """
    # Extrair valores numéricos dos preços
    def extract_price(price_str):
        if not price_str:
            return None
        try:
            # Limpar string: remover entidades HTML, espaços, etc
            price_clean = price_str.replace('R$', '').replace('&nbsp;', '').replace(' ', '').strip()
            # Se tiver quebra de linha, pegar apenas a primeira linha
            if '\n' in price_clean:
                price_clean = price_clean.split('\n')[0]
            # Remover pontos de milhar e substituir vírgula por ponto
            # Formato brasileiro: "164,90" ou "1.164,90"
            import re
            # Buscar padrão: números com vírgula (decimal)
            match = re.search(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', price_clean)
            if match:
                price_str_clean = match.group(1).replace('.', '').replace(',', '.')
                return float(price_str_clean)
            # Tentar número simples
            numbers = re.findall(r'\d+\.?\d*', price_clean.replace(',', '.'))
            if numbers:
                return float(numbers[0])
        except Exception as e:
            pass
        return None
    
    def extract_discount_percent(discount_str):
        if not discount_str:
            return None
        try:
            # Remover "%" e outros caracteres
            import re
            numbers = re.findall(r'\d+\.?\d*', discount_str.replace('-', ''))
            if numbers:
                return float(numbers[0])
        except:
            pass
        return None
    
    # Extrair código do produto (SKU ou do link)
    codigo = product_data.get('sku')
    if not codigo:
        try:
            link = product_data.get('link', '')
            if link and '/produto/' in link:
                codigo = link.split('/produto/')[-1].split('?')[0].split('/')[0]
        except:
            pass
    
    # Mapear campos conforme formato da imagem
    formatted = {
        "codigo": codigo,
        "nome": product_data.get('nome', 'Nome não encontrado'),
        "descricao": product_data.get('descricao') or product_data.get('tag_promocao'),
        "preco_custo": extract_price(product_data.get('preco_revenda')),
        "preco_sugerido": extract_price(product_data.get('preco_pague')),
        "preco_tabela": extract_price(product_data.get('preco_original')),
        "desconto_percentual": extract_discount_percent(product_data.get('desconto')),
        "categoria": None,  # Não temos essa informação na extração atual
        "subcategoria": None,  # Não temos essa informação na extração atual
        "ean": None,  # Não temos essa informação na extração atual
        "sku": product_data.get('sku') or codigo,
        "disponivel": product_data.get('disponivel', True),
        "pontos_venda": None,  # Não temos essa informação na extração atual
        "url_imagem": product_data.get('imagem')
    }
    
    return formatted

def save_data(cycle_info, products_data, base_dir='produtos_revendedores'):
    """
    Salva as informações do ciclo e produtos em arquivos JSON
    
    Formato conforme a imagem: cada arquivo contém marca_id, ciclo_info e produtos.
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
        
        # Formatar informações do ciclo
        formatted_cycle_info = format_cycle_info(cycle_info)
        
        # Salvar informações do ciclo PRIMEIRO (fundamental para controle de dados)
        if cycle_info:
            cycle_file = os.path.join(base_dir, 'ciclo_periodo.json')
            with open(cycle_file, 'w', encoding='utf-8') as f:
                json.dump(cycle_info, f, ensure_ascii=False, indent=2)
            print(f"💾 Informações do ciclo salvas em: {cycle_file}")
            print(f"   📅 Ciclo: {cycle_info.get('numero_ciclo', 'N/A')} | Período: {cycle_info.get('data_inicio', 'N/A')} a {cycle_info.get('data_fim', 'N/A')}")
        else:
            print("⚠️ Informações do ciclo não foram extraídas")
            formatted_cycle_info = {
                "numero": "01/2025",
                "nome": "Ciclo 2025",
                "data_inicio": f"{datetime.now().year}-01-01",
                "data_fim": f"{datetime.now().year}-12-31"
            }
        
        # Salvar produtos no formato da imagem
        if products_data:
            produtos_por_arquivo = 100
            total_produtos = len(products_data)
            arquivos_criados = []
            
            # Marca ID (1 para Boticário)
            marca_id = 1
            
            for i in range(0, total_produtos, produtos_por_arquivo):
                inicio = i + 1
                fim = min(i + produtos_por_arquivo, total_produtos)
                
                # Obter lote de produtos
                produtos_lote = products_data[i:fim]
                
                # Formatar produtos para o novo formato
                produtos_formatados = [format_product(p) for p in produtos_lote]
                
                # Criar estrutura conforme a imagem
                arquivo_json = {
                    "marca_id": marca_id,
                    "ciclo_info": formatted_cycle_info,
                    "produtos": produtos_formatados
                }
                
                nome_arquivo = f'produtos_{inicio:03d}_{fim:03d}.json'
                caminho_arquivo = os.path.join(base_dir, nome_arquivo)
                
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(arquivo_json, f, ensure_ascii=False, indent=2)
                
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
                    print(f"   SKU: {product.get('sku', 'N/A')} | Preço Pague: {product.get('preco_pague', 'N/A')}")
                    print("-" * 30)
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")
        import traceback
        traceback.print_exc()

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

