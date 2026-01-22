import json
import logging
import os
import time
from typing import Dict, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import settings
from logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class WebDriverFactory:
    @staticmethod
    def create_chrome_driver() -> webdriver.Chrome:
        """
        Configura e inicializa uma instância do Google Chrome WebDriver.

        Este método utiliza o ChromeDriverManager para baixar a versão correta
        do executável e aplica configurações de proxy caso estejam ativadas no
        settings.

        Returns:
            webdriver.Chrome: Uma instância configurada do navegador Chrome.
        """
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/119.0.0.0 Safari/537.36'
        )
        options.add_argument(f'user-agent={user_agent}')
        if os.name == 'nt':
            driver_path = settings.CHROME_PATH
            logger.info(f'Executando no Windows. Path: {driver_path}')
        else:
            driver_path = '/usr/local/bin/chromedriver'
            logger.info('Executando dentro do Docker (Linux).')

        if settings.PROXY_ENABLE and settings.PROXY:
            options.add_argument(f'--proxy-server={settings.PROXY}')

        return webdriver.Chrome(options=options, executable_path=driver_path)


class IMDbParser:
    @staticmethod
    def extract_movie_data(container) -> Dict:
        """
        Extrai dados de um filme a partir de um elemento Web.

        Args:
            container (WebElement): O elemento Web contendo os dados do filme.

        Returns:
            Dict: Um dicionário contendo a classificação o título e a nota
            do filme.
        """
        try:
            title_element = container.find_element(
                By.CLASS_NAME, 'ipc-title__text'
            )
            full_title = title_element.text

            rating = container.find_element(
                By.CLASS_NAME, 'ipc-rating-star--rating'
            ).text

            classification = container.find_element(
                By.CLASS_NAME, 'ipc-signpost__text'
            ).text

            return {'title': (classification, full_title), 'rating': rating}
        except Exception as e:
            logger.warning(f'Erro ao extrair dados de um filme: {e}')
            return {}


class IMDbScraper:
    def __init__(self, driver: webdriver.Chrome):
        """
        Inicializa o scraper com as dependências necessárias.

        Args:
            driver (webdriver.Chrome): Instância do navegador para realizar
            a navegação.
        """
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def get_top_movies(self, url: str) -> List[Dict]:
        """
        Realiza a raspagem dos filmes mais bem avaliados.

        Args:
            url (str): URL da página com a lista de filmes.

        Returns:
            List[Dict]: Lista de dicionários contendo os dados dos filmes.
        """
        logger.info(f'Iniciando raspagem em: {url}')
        results = []

        try:
            self.driver.get(url)
            time.sleep(3.5)
            movie_containers = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'ipc-metadata-list-summary-item')
                )
            )

            for container in movie_containers:
                data = IMDbParser.extract_movie_data(container)
                if data:
                    results.append(data)

            logger.info(f'Sucesso! {len(results)} filmes coletados.')
        except Exception as e:
            logger.error(f'Erro durante a execução: {e}')
        finally:
            self.driver.quit()

        return results


class JSONExporter:
    """Responsável por persistir os dados."""

    @staticmethod
    def save(data: List[Dict], filename: str):
        """
        Salva os dados coletados em um arquivo JSON.

        Args:
            data (List[Dict]): Lista de dicionários contendo os dados
            coletados.
            filename (str): Nome do arquivo onde os dados serão salvos.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f'Dados salvos em {filename}')
        except IOError as e:
            logger.error(f'Erro ao salvar arquivo: {e}')


if __name__ == '__main__':
    url = 'https://www.imdb.com/pt/chart/top/'
    driver_instance = WebDriverFactory.create_chrome_driver()

    scraper = IMDbScraper(driver_instance)
    movies = scraper.get_top_movies(url)

    if movies:
        JSONExporter.save(movies, 'data/movies.json')
