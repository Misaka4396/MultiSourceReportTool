"""Base fetcher with common HTTP handling and rate limiting."""

from __future__ import annotations

import time
import random
import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]


class BaseFetcher:
    """Base class for all data fetchers with rate limiting and error handling."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
        })
        self.last_request_time = 0
        self.min_delay = 1.5  # seconds between requests
        self.use_mock = False

    def _rate_limit(self):
        """Enforce minimum delay between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed + random.uniform(0, 0.5))
        self.last_request_time = time.time()

    def fetch_page(self, url: str, timeout: int = 15) -> str | None:
        """Fetch a web page and return its HTML text. Returns None on failure."""
        self._rate_limit()
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or 'utf-8'
            return resp.text
        except Exception:
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML string into BeautifulSoup object."""
        return BeautifulSoup(html, 'lxml')

    def safe_fetch(self, url: str, timeout: int = 15) -> str | None:
        """Fetch with fallback — sets use_mock flag on failure."""
        result = self.fetch_page(url, timeout)
        if result is None:
            self.use_mock = True
        return result

    def get_mock_data(self, params: dict) -> list[dict]:
        """Override in subclass to provide mock data."""
        return []
