"""Fetcher for Library Genesis book search (mock with realistic data)."""

import random
from .base import BaseFetcher


MOCK_BOOK_DATA = [
    {"title": "Deep Learning", "authors": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
     "publisher": "MIT Press", "year": "2016", "isbn": "978-0262035613",
     "language": "English", "format": "PDF", "size": "18.5 MB",
     "mirrors": ["https://libgen.is/book/1234001", "https://libgen.st/book/1234001",
                 "https://libgen.rs/book/1234001"],
     "description": "An comprehensive introduction to deep learning covering mathematical foundations, modern practices, and research perspectives."},
    {"title": "Pattern Recognition and Machine Learning", "authors": "Christopher M. Bishop",
     "publisher": "Springer", "year": "2006", "isbn": "978-0387310732",
     "language": "English", "format": "PDF", "size": "8.2 MB",
     "mirrors": ["https://libgen.is/book/2345002", "https://libgen.st/book/2345002"],
     "description": "The classic graduate-level textbook on probabilistic approaches to machine learning and pattern recognition."},
    {"title": "统计学习方法 (第二版)", "authors": "李航",
     "publisher": "清华大学出版社", "year": "2019", "isbn": "978-7302495697",
     "language": "中文", "format": "PDF", "size": "12.1 MB",
     "mirrors": ["https://libgen.is/book/3456003", "https://libgen.rs/book/3456003"],
     "description": "系统介绍统计学习的主要方法，包括感知机、k近邻、朴素贝叶斯、决策树、逻辑回归、支持向量机、提升方法、EM算法、隐马尔可夫模型等。"},
    {"title": "Reinforcement Learning: An Introduction (2nd Edition)",
     "authors": "Richard S. Sutton, Andrew G. Barto", "publisher": "MIT Press",
     "year": "2018", "isbn": "978-0262039246", "language": "English",
     "format": "PDF", "size": "14.3 MB",
     "mirrors": ["https://libgen.is/book/4567004", "https://libgen.st/book/4567004",
                 "https://libgen.rs/book/4567004"],
     "description": "The definitive textbook on reinforcement learning, covering bandits, MDPs, dynamic programming, Monte Carlo methods, TD learning, and deep RL."},
    {"title": "The Elements of Statistical Learning (2nd Edition)",
     "authors": "Trevor Hastie, Robert Tibshirani, Jerome Friedman",
     "publisher": "Springer", "year": "2009", "isbn": "978-0387848570",
     "language": "English", "format": "PDF", "size": "12.8 MB",
     "mirrors": ["https://libgen.is/book/5678005", "https://libgen.st/book/5678005"],
     "description": "A comprehensive treatment of statistical learning methods including linear models, kernel methods, model assessment, boosting, random forests, and neural networks."},
    {"title": "自然语言处理综论 (Speech and Language Processing)", "authors": "Daniel Jurafsky, James H. Martin",
     "publisher": "Prentice Hall", "year": "2023", "isbn": "978-0131873216",
     "language": "English", "format": "PDF", "size": "22.0 MB",
     "mirrors": ["https://libgen.is/book/6789006"],
     "description": "The most comprehensive textbook on NLP, covering from traditional methods to modern transformer-based architectures and large language models."},
    {"title": "算法导论 (Introduction to Algorithms, 4th Edition)",
     "authors": "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
     "publisher": "MIT Press", "year": "2022", "isbn": "978-0262046305",
     "language": "English", "format": "PDF", "size": "15.6 MB",
     "mirrors": ["https://libgen.is/book/7890007", "https://libgen.rs/book/7890007"],
     "description": "The definitive reference on algorithms, updated with new chapters on machine learning algorithms, online algorithms, and parallel algorithms."},
]


class LibGenFetcher(BaseFetcher):
    """Fetcher for Library Genesis book search (mock-based due to access restrictions)."""

    BASE_URLS = [
        "https://libgen.is",
        "https://libgen.st",
    ]

    def fetch(self, title: str, author: str, isbn: str, language: str,
              formats: list[str]) -> tuple[list[dict], bool]:
        """Search for books. Returns (data, is_mock)."""
        self.use_mock = False
        results = []

        # Attempt real search on libgen
        search_url = None
        query_params = {}
        if isbn:
            query_params["req"] = isbn
            query_params["column"] = "identifier"
        elif title:
            query_params["req"] = title
            query_params["column"] = "title"
        elif author:
            query_params["req"] = author
            query_params["column"] = "author"
        else:
            self.use_mock = True

        if not self.use_mock:
            for base in self.BASE_URLS:
                search_url = f"{base}/search.php?req={query_params.get('req', '')}&column={query_params.get('column', 'title')}"
                html = self.safe_fetch(search_url)
                if html:
                    try:
                        parsed = self._parse_results(html)
                        if parsed:
                            results = parsed
                            break
                    except Exception:
                        continue

        if self.use_mock or not results:
            results = self._get_filtered_mock(title, author, isbn, language, formats)

        return results, self.use_mock or not self._has_real_data(results)

    def _has_real_data(self, results):
        return len(results) > 0 and not any("示例" in r.get("notes", "") for r in results)

    def _parse_results(self, html: str) -> list[dict]:
        """Parse libgen search results page."""
        soup = self.parse_html(html)
        results = []
        rows = soup.select("table.c tr") or soup.select("table tr")
        for row in rows[1:11]:  # Skip header, limit to 10
            cells = row.find_all("td")
            if len(cells) < 8:
                continue
            try:
                title_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                author_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                publisher_text = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                year_text = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                size_text = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                results.append({
                    "title": title_text, "authors": author_text,
                    "publisher": publisher_text, "year": year_text,
                    "isbn": "", "language": "", "format": "PDF",
                    "size": size_text,
                    "mirrors": [f"https://libgen.is/book/{i}" for i in range(1, 4)],
                    "description": "",
                })
            except Exception:
                continue
        return results

    def _get_filtered_mock(self, title, author, isbn, language, formats):
        """Filter mock data."""
        results = list(MOCK_BOOK_DATA)

        if isbn:
            results = [r for r in results if isbn.strip() in r.get("isbn", "")]
        elif title:
            kw = title.lower()
            results = [r for r in results if kw in r.get("title", "").lower()]
        elif author:
            kw = author.lower()
            results = [r for r in results if kw in r.get("authors", "").lower()]

        if language and language != "全部":
            results = [r for r in results if r.get("language") == language]

        if formats:
            fmt_set = {f.lower() for f in formats}
            results = [r for r in results if r.get("format", "").lower() in fmt_set]

        if not results:
            results = list(MOCK_BOOK_DATA)[:3]

        for r in results:
            r["notes"] = "示例数据 — 实际下载请访问 Library Genesis 镜像站点"

        return results
