# 🛍️ Scraping de Produtos do Boticário

Este projeto extrai produtos específicos do site do Boticário, focando nos elementos com classe `showcase-card-link-overlay`.

## 📋 Pré-requisitos

1. **Python 3.7+** instalado
2. **Google Chrome** instalado no sistema
3. Conexão com a internet

## 🚀 Instalação

1. Instale as dependências:
```bash
pip install selenium webdriver-manager beautifulsoup4
```

## 🎯 Como usar

Execute o script principal:
```bash
python app_selenium.py
```

## 📊 O que o script faz

1. **Abre o navegador Chrome** automaticamente
2. **Acessa o site** do Boticário
3. **Localiza elementos** com classe `showcase-card-link-overlay`
4. **Extrai dados** de cada produto encontrado:
   - Nome do produto
   - Preço atual
   - Preço original (se houver desconto)
   - Percentual de desconto
   - Link do produto
   - Imagem do produto
   - Descrição
   - Badges/Tags especiais

5. **Salva os dados** em `produtos_boticario.json`

## 🔍 Estrutura dos dados extraídos

```json
{
  "nome": "Nome do Produto",
  "preco": "R$ 99,90",
  "preco_original": "R$ 149,90",
  "desconto": "33% OFF",
  "link": "https://www.boticario.com.br/produto/...",
  "imagem": "https://imagem-do-produto.jpg",
  "descricao": "Descrição do produto",
  "badges": ["Novidade", "Mais Vendido"]
}
```

## ⚠️ Possíveis problemas

- **Erro 403**: Site bloqueando requisições automatizadas
- **Elementos não encontrados**: Classe `showcase-card-link-overlay` pode ter mudado
- **Timeout**: Conexão lenta ou site demorado para carregar

## 🛠️ Soluções

1. **Aguarde alguns minutos** e tente novamente
2. **Verifique sua conexão** com a internet
3. **Atualize o Chrome** para a versão mais recente
4. **Execute em horários** de menor tráfego
5. **O script tenta seletores alternativos** automaticamente

## 📁 Arquivos gerados

- `produtos_boticario.json`: Dados dos produtos extraídos
- Logs no terminal com progresso da extração
