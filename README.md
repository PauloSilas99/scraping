# 🛍️ Scraping de Produtos do Boticário

Este projeto automatiza a extração de produtos do site do Boticário usando Selenium. O script navega pelo site, carrega todos os produtos disponíveis e extrai informações detalhadas de cada item.

## 📋 Pré-requisitos

1. **Python 3.7+** instalado
2. **Google Chrome** instalado no sistema
3. Conexão com a internet

## 🚀 Instalação

1. Clone ou baixe este repositório

2. Instale as dependências usando o arquivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

As dependências incluem:
- `selenium` - Automação do navegador
- `webdriver-manager` - Gerenciamento automático do ChromeDriver
- `beautifulsoup4` - Parsing de HTML
- `requests` - Requisições HTTP
- `lxml` - Parser XML/HTML

## 🎯 Como usar

Execute o script principal:
```bash
python app_selenium.py
```

O script irá:
1. Abrir automaticamente o navegador Chrome
2. Navegar pelo site do Boticário
3. Carregar todos os produtos disponíveis
4. Extrair os dados e salvar em arquivos JSON

**Tempo estimado**: 5-15 minutos (dependendo da quantidade de produtos e velocidade da conexão)

## 📊 O que o script faz

O processo de extração ocorre em **3 passos principais**:

### PASSO 1: Acesso à página de produtos
- Abre o site do Boticário
- Clica no botão **"Veja Mais"** para acessar a página completa de produtos

### PASSO 2: Carregamento de todos os produtos
- Localiza o botão **"Carregar mais produtos"**
- Clica repetidamente até carregar todos os produtos disponíveis
- Monitora o progresso e para quando não há mais produtos para carregar

### PASSO 3: Extração de dados
- Para cada produto encontrado (elementos com classe `showcase-card-link-overlay`):
  - Faz scroll até o elemento para garantir que está visível
  - Extrai os seguintes dados:
    - **Nome do produto**
    - **Preço atual** (com opções de parcelamento)
    - **Preço original** (se houver desconto)
    - **Percentual de desconto**
    - **Link do produto**
    - **URL da imagem**
    - **Descrição/Badge promocional**
    - **Badges/Tags especiais** (ex: "SUPER DESCONTO!", "MENOR PREÇO DO ANO!")

## 📁 Arquivos gerados

Os produtos são salvos na pasta `produtos/` em arquivos JSON separados:

- **Formato**: `produtos_001_100.json`, `produtos_101_200.json`, etc.
- **Quantidade**: 100 produtos por arquivo
- **Estrutura**: Array JSON com objetos de produtos

Exemplo de estrutura de um produto:
```json
{
  "link": "https://www.boticario.com.br/produto/...",
  "nome": "EGEO\nSpicy Vibe Desodorante Colônia 90ml",
  "preco": "R$ 154,90\nR$ 61,90\n3x R$ 20,63",
  "preco_original": null,
  "desconto": "-60%",
  "imagem": "https://res.cloudinary.com/...",
  "descricao": "SUPER DESCONTO!🔥",
  "badges": ["-60%", "SUPER DESCONTO!🔥"]
}
```

## 📝 Logs e Progresso

Durante a execução, o script exibe:
- ✅ Status de cada etapa
- 📊 Contagem de produtos encontrados
- 💾 Arquivos criados
- 📋 Resumo dos primeiros produtos extraídos
- ⚠️ Avisos e erros (se houver)

## ⚠️ Possíveis problemas

### Erro 403 - Acesso negado
- **Causa**: Site bloqueando requisições automatizadas
- **Solução**: Aguarde alguns minutos e tente novamente

### Elementos não encontrados
- **Causa**: Estrutura HTML do site pode ter mudado
- **Solução**: O script tenta seletores alternativos automaticamente

### Timeout
- **Causa**: Conexão lenta ou site demorado para carregar
- **Solução**: Verifique sua conexão com a internet

### ChromeDriver não encontrado
- **Causa**: Problema na instalação do webdriver-manager
- **Solução**: O script tenta instalar automaticamente, mas certifique-se de ter Chrome atualizado

## 🛠️ Soluções e Dicas

1. **Aguarde alguns minutos** entre execuções para evitar bloqueios
2. **Verifique sua conexão** com a internet antes de executar
3. **Atualize o Chrome** para a versão mais recente
4. **Execute em horários** de menor tráfego (madrugada/manhã)
5. **Não feche o navegador** durante a execução - o script fecha automaticamente ao finalizar
6. **Mantenha o terminal aberto** para acompanhar o progresso

## 📂 Estrutura do Projeto

```
scraping/
├── app_selenium.py          # Script principal de scraping
├── app.py                   # Script de teste com requests
├── requirements.txt         # Dependências do projeto
├── produtos/                # Pasta com produtos extraídos (criada automaticamente)
│   ├── produtos_001_100.json
│   ├── produtos_101_200.json
│   └── ...
├── produtos_boticario.json  # Arquivo de backup/exemplo
└── README.md               # Este arquivo
```

## 🔍 Notas Técnicas

- O script usa **Selenium WebDriver** para simular um navegador real
- Implementa técnicas anti-detecção (User-Agent customizado, ocultação de automação)
- Remove produtos duplicados automaticamente usando o link como identificador único
- Faz scroll automático para garantir que elementos estejam visíveis antes de extrair
- Aguarda carregamento dinâmico de conteúdo JavaScript
