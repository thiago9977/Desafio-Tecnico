import argparse
import logging

from logger_config import setup_logging
from scrapp_imbd import IMDbScraper, JSONExporter, WebDriverFactory
from scrapp_quotes import HttpClient, JsonWriter, QuotesParser, QuotesScraper

setup_logging()
logger = logging.getLogger(__name__)


def run_imdb():
    """Executa o fluxo do Scraper IMDb."""
    logger.info('Iniciando tarefa: IMDb')
    driver = WebDriverFactory.create_chrome_driver()
    scraper = IMDbScraper(driver)
    results = scraper.get_top_movies('https://www.imdb.com/pt/chart/top/')
    if results:
        JSONExporter.save(results, 'data/movies.json')


def run_quotes():
    """Executa o fluxo do Scraper de Citações."""
    logger.info('Iniciando tarefa: Quotes')
    scraper = QuotesScraper(
        start_url='https://quotes.toscrape.com/',
        client=HttpClient(),
        parser=QuotesParser(),
    )
    results = scraper.scrape()
    if results:
        JsonWriter().write('data/quotes.json', (q.__dict__ for q in results))
    logger.info(f'Total de citações coletadas: {len(results)}')


def main():
    parser = argparse.ArgumentParser(description='Orquestrador de Scrapers')

    parser.add_argument(
        '--imdb', action='store_true', help='Executa o scraper do IMDb'
    )
    parser.add_argument(
        '--quotes', action='store_true', help='Executa o scraper de Quotes'
    )
    parser.add_argument(
        '--all', action='store_true', help='Executa todos os scrapers'
    )

    args = parser.parse_args()

    if args.all or args.imdb:
        run_imdb()

    if args.all or args.quotes:
        run_quotes()

    if not (args.imdb or args.quotes or args.all):
        parser.print_help()


if __name__ == '__main__':
    main()
