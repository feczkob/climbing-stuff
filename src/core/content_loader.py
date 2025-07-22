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


class PlaywrightContentLoader(ContentLoader):
    def get_content(self, url: str) -> BeautifulSoup:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
            return BeautifulSoup(content, "html.parser")