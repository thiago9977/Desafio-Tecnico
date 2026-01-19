import json
import logging
from dataclasses import dataclass
from typing import Iterable, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Quote:
    """
    Classe que representa uma citação.

    Attributes:
        message (str): A citação.
        author (str): O autor da citação.
    """

    message: str
    author: str


class HttpClient:
    def get(self, url: str) -> str:
        """
        Realiza uma requisição HTTP GET para a URL fornecida.

        Args:
            url (str): URL para a qual a requisição será feita.

        Returns:
            str: Conteúdo da resposta HTTP.
        """
        logger.debug(f'HTTP GET: {url}')
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text


class JsonWriter:
    def write(self, path: str, data: Iterable[dict]) -> None:
        """
        Salva os dados coletados em um arquivo JSON.

        Args:
            path (str): Caminho do arquivo onde os dados serão salvos.
            data (Iterable[dict]): Dados a serem salvos.
        """
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(list(data), file, ensure_ascii=False, indent=4)


class QuotesParser:
    def parse(self, html: str) -> List[Quote]:
        """
        Parseia o HTML para extrair as citações e seus autores.

        Args:
            html (str): HTML a ser parseado.

        Returns:
            List[Quote]: Lista de citações extraídas.
        """
        soup = BeautifulSoup(html, 'html.parser')
        quotes_elements = soup.find_all('div', class_='quote')

        return [
            Quote(
                message=quote.find('span', class_='text').text,
                author=quote.find('small', class_='author').text,
            )
            for quote in quotes_elements
        ]

    def next_page(self, html: str, current_url: str) -> Optional[str]:
        """
        Encontra a próxima página de citações no HTML.

        Args:
            html (str): HTML a ser parseado.
            current_url (str): URL atual.

        Returns:
            Optional[str]: URL da próxima página ou None se não houver.
        """
        soup = BeautifulSoup(html, 'html.parser')
        next_link = soup.find('li', class_='next')

        if not next_link:
            return None

        return urljoin(current_url, next_link.find('a')['href'])


class QuotesScraper:
    def __init__(
        self,
        start_url: str,
        client: HttpClient,
        parser: QuotesParser,
    ) -> None:
        """
        Inicializa o scraper com as dependências necessárias.

        Args:
            start_url (str): URL inicial para o scraper.
            client (HttpClient): Cliente HTTP para realizar requisições.
            parser (QuotesParser): Parser para extrair dados das citações.
        """
        self.start_url = start_url
        self.client = client
        self.parser = parser

    def scrape(self) -> List[Quote]:
        """
        Realiza o scraping das citações.

        Returns:
            List[Quote]: Lista de citações coletadas.
        """
        logger.info(f'Iniciando scraper para {self.start_url}')

        quotes: List[Quote] = []
        url: Optional[str] = self.start_url

        while url:
            logger.info(f'Acessando página: {url}')
            html = self.client.get(url)

            page_quotes = self.parser.parse(html)
            quotes.extend(page_quotes)

            logger.info(f'{len(page_quotes)} citações coletadas')
            url = self.parser.next_page(html, url)

        return quotes


def main() -> None:
    """
    Função principal que executa o scraper.
    """
    scraper = QuotesScraper(
        start_url='https://quotes.toscrape.com/',
        client=HttpClient(),
        parser=QuotesParser(),
    )

    quotes = scraper.scrape()

    JsonWriter().write(
        'data/quotes.json',
        (quote.__dict__ for quote in quotes),
    )

    logger.info(f'Total de citações coletadas: {len(quotes)}')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logger.critical(f'Erro inesperado: {exc}', exc_info=True)
