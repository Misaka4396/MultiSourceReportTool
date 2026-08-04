"""Fetcher for grey literature (World Bank, RAND, etc.)."""

import random
from .base import BaseFetcher


MOCK_GREY_DATA = [
    {"title": "Policy Research Working Paper 10124: Trade Liberalization and Income Inequality in Developing Economies",
     "authors": "David Atkin, Amit Khandelwal", "organization": "World Bank",
     "date": "2026-06-01", "file_type": "PDF",
     "abstract": "This paper uses novel firm-level data from 15 developing countries to estimate the distributional effects of trade liberalization, finding that the top 20% of income earners capture 45% of the gains from trade.",
     "link": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/10124"},
    {"title": "AI Safety and National Security: A Technical Assessment Framework",
     "authors": "John S. Davis, Maria Chen, Robert Kim", "organization": "RAND Corporation",
     "date": "2026-07-10", "file_type": "PDF",
     "abstract": "This RAND technical report proposes a multi-dimensional framework for assessing AI safety risks in national security contexts, covering adversarial robustness, interpretability, and alignment verification methodologies.",
     "link": "https://www.rand.org/pubs/technical_reports/TR2026-01.html"},
    {"title": "Working Paper: Digital Infrastructure and Firm Productivity in Sub-Saharan Africa",
     "authors": "Leonard Wantchekon, Sarah Brierley", "organization": "World Bank",
     "date": "2026-05-15", "file_type": "PDF",
     "abstract": "Analyzing the impact of mobile internet and digital payment infrastructure on manufacturing firm productivity across 12 Sub-Saharan African countries from 2020-2025.",
     "link": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/10235"},
    {"title": "The Economic Impact of Climate Adaptation Investments: A Global Meta-Analysis",
     "authors": "Michael Greenstone, Esther Duflo", "organization": "World Bank",
     "date": "2026-04-20", "file_type": "PDF",
     "abstract": "A meta-analysis of 200+ climate adaptation projects worldwide, estimating benefit-cost ratios ranging from 2:1 to 10:1 depending on project type and region.",
     "link": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/10236"},
    {"title": "Supply Chain Vulnerabilities in Critical Mineral Markets",
     "authors": "Emily S. Goldman, Thomas Wright", "organization": "RAND Corporation",
     "date": "2026-03-05", "file_type": "PDF",
     "abstract": "This report maps global supply chains for lithium, cobalt, rare earth elements, and other critical minerals essential for clean energy and defense technologies, identifying geopolitical chokepoints.",
     "link": "https://www.rand.org/pubs/technical_reports/TR2026-02.html"},
    {"title": "Policy Research Working Paper: Universal Basic Income Experiments in the Global South",
     "authors": "Tavneet Suri, Abhijit Banerjee", "organization": "World Bank",
     "date": "2026-02-18", "file_type": "PDF",
     "abstract": "Synthesizing results from 12 UBI pilot programs across India, Kenya, Brazil, and Indonesia, this paper examines labor supply responses, consumption patterns, and psychological well-being outcomes.",
     "link": "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/10237"},
]


class GreyLiteratureFetcher(BaseFetcher):
    """Fetcher for grey literature from World Bank, RAND, and custom domains."""

    DOMAIN_URLS = {
        "worldbank.org": "https://documents.worldbank.org/en/publication/documents-reports",
        "rand.org": "https://www.rand.org/pubs.html",
    }

    def fetch(self, keywords: str, domains: list[str], file_types: list[str],
              start_date: str, end_date: str) -> tuple[list[dict], bool]:
        """Fetch grey literature. Returns (data, is_mock)."""
        self.use_mock = False
        results = []

        for domain in domains:
            if domain in self.DOMAIN_URLS:
                html = self.safe_fetch(self.DOMAIN_URLS[domain])
                if html and not self.use_mock:
                    try:
                        parsed = self._parse_page(html, domain)
                        results.extend(parsed)
                    except Exception:
                        self.use_mock = True

        if self.use_mock or not results:
            results = self._get_filtered_mock(keywords, domains, file_types, start_date, end_date)

        return results, self.use_mock

    def _parse_page(self, html: str, domain: str) -> list[dict]:
        """Parse a domain's publications page."""
        soup = self.parse_html(html)
        results = []
        items = soup.find_all("div", class_=lambda c: c and any(
            w in (c or "").lower() for w in ["result", "publication", "item", "document"]
        ))
        for item in items[:5]:
            title_el = item.find("h3") or item.find("h2") or item.find("a")
            title = title_el.get_text(strip=True) if title_el else ""
            link_el = item.find("a", href=True)
            link = link_el["href"] if link_el else ""
            if link and not link.startswith("http"):
                link = f"https://{domain}{link}"
            date_el = item.find("time") or item.find("span", class_=lambda c: c and "date" in (c or "").lower())
            date_str = date_el.get_text(strip=True) if date_el else ""
            if title:
                results.append({
                    "title": title, "authors": "", "organization": domain,
                    "date": date_str, "file_type": "PDF", "abstract": "", "link": link,
                })
        return results

    def _get_filtered_mock(self, keywords, domains, file_types, start_date, end_date):
        """Filter mock data."""
        results = []
        for item in MOCK_GREY_DATA:
            org = item.get("organization", "").lower()
            domain_match = False
            for d in domains:
                if d.lower() in org:
                    domain_match = True
                    break
            if not domain_match:
                continue
            if file_types and item.get("file_type", "").lower() not in [f.lower() for f in file_types]:
                continue
            if start_date and item.get("date", "") < start_date:
                continue
            if end_date and item.get("date", "") > end_date:
                continue
            if keywords:
                kw_list = [k.strip().lower() for k in keywords.split(",")]
                text = (item.get("title", "") + item.get("abstract", "")).lower()
                if not any(kw in text for kw in kw_list):
                    continue
            results.append(item)
        return results
