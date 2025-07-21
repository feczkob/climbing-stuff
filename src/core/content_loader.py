from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import httpx

from src.core.config import config


class ContentLoader(ABC):
    @abstractmethod
    def get_content(self, url: str) -> BeautifulSoup:
        pass


class HttpContentLoader(ContentLoader):
    def get_content(self, url: str) -> BeautifulSoup:
        response = httpx.get(url, follow_redirects=True)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")


class MockContentLoader(ContentLoader):
    def get_content(self, url: str) -> BeautifulSoup:
        site_name, category = url.split("://")
        with open(config.get_mock_file_path(site_name, category), "r") as f:
            return BeautifulSoup(f.read(), "html.parser")


class SeleniumContentLoader(ContentLoader):
    def get_content(self, url: str) -> BeautifulSoup:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import time

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        return soup