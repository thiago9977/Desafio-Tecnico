# Multi-Scraper Project (IMDb & Quotes)

Este projeto é um ecossistema de web scraping robusto desenvolvido em **Python**. Ele foi projetado para coletar dados de forma automatizada, utilizando diferentes abordagens para lidar com sites estáticos e dinâmicos.

## Tecnologias e Ferramentas

* **Python 3.12**
* **Selenium 3.141.0**: Utilizado no scraper do IMDb para lidar com renderização de JavaScript e *Lazy Loading*.
* **BeautifulSoup4 & Requests**: Utilizados no scraper de Citações para extração rápida de dados em HTML estático.
* **Docker & Docker Compose**: Garantem que o ambiente (incluindo o Google Chrome e o ChromeDriver) seja idêntico em qualquer máquina.
* **Logging**: Sistema de logs detalhado para monitoramento de execução.

---

## Estrutura do Projeto

```text
.
├── data/               # Arquivos JSON gerados (movies.json, quotes.json)
├── logs/               # Logs de execução e capturas de tela de erro
├── scrapp_imbd.py      # Lógica do scraper IMDb (Selenium)
├── scrapp_quote.py     # Lógica do scraper de Citações (BeautifulSoup)
├── run.py              # Orquestrador central (Ponto de entrada CLI)
├── settings.py         # Gerenciamento de variáveis de ambiente
├── logger_config.py    # Configuração padronizada de logs
├── Dockerfile          # Configuração da imagem Linux + Chrome + Python
└── docker-compose.yml  # Orquestração dos serviços (all, imdb, quotes)
```

# Como Executar
A forma recomendada de execução é através do Docker, pois ele já configura o Google Chrome e o ChromeDriver compatível dentro do Linux.

### Pré-requisitos
Docker Desktop instalado e rodando.

Docker Compose instalado.

### Construindo a Imagem
No terminal, dentro da pasta do projeto, execute:
```
docker compose build 
```

### Executando os Scrapers
Você pode escolher rodar um scraper específico ou todos de uma vez:
* Executar Tudo (IMDb + Quotes):
```
docker compose up all_scrapers
```
* Executar apenas IMDb:
```
docker compose up imdb
```
* Executar apenas Quotes:
```
docker compose up quotes
```

### Comandos via CLI (Execução Local)
Caso prefira rodar fora do Docker (necessário ter o Chrome e ChromeDriver instalados manualmente no Path), use o arquivo main.py:

```
# Rodar tudo
python main.py --all

# Rodar apenas um específico
python main.py --imdb
python main.py --quotes
```

Antes de rodar o arquivo imdb é necessário fazer uma alteração no arquivo scrap_imdb.py
```
no metodo create_chromedriver

return webdriver.Chrome(
    executable_path='/usr/local/bin/chromedriver', # Adicione essa linha com o caminho que leva ao chromedrive
    options=options
)
```
## Saída de Dados
Após a execução, os dados serão salvos automaticamente na pasta /data do seu computador, graças ao mapeamento de volumes do Docker:

IMDb: data/movies.json (Contém o ranking, título e nota de 250 filmes).

Quotes: data/quotes.json (Contém todas as citações e autores coletados).














