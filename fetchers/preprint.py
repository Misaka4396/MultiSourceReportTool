"""Fetcher for preprint platforms (arXiv, SSRN)."""

import urllib.parse
import xml.etree.ElementTree as ET
from .base import BaseFetcher


MOCK_PREPRINT_DATA = [
    {"title": "Scaling Laws for Multimodal Foundation Models: An Empirical Analysis",
     "authors": "Alex J. Thompson, Sarah Chen, David Park", "date": "2026-07-28",
     "abstract": "We conduct a large-scale empirical study of scaling laws for multimodal transformer models across vision, language, and audio modalities. Using training runs spanning 3 orders of magnitude in compute, we find that optimal model size scales as a power law with dataset size and modality count.",
     "link": "https://arxiv.org/abs/2607.12345", "source": "arXiv", "category": "cs.LG"},
    {"title": "Diffusion Models for Protein Structure Prediction: A Comprehensive Survey",
     "authors": "Yuki Tanaka, James Wilson, Priya Patel", "date": "2026-07-25",
     "abstract": "This survey reviews the rapid progress in applying diffusion models to protein structure prediction, covering score-based generative models, flow matching, and equivariant architectures. We benchmark 15 methods on standard datasets.",
     "link": "https://arxiv.org/abs/2607.12000", "source": "arXiv", "category": "q-bio.BM"},
    {"title": "The Impact of Generative AI on Knowledge Worker Productivity: Evidence from a Large-Scale Field Experiment",
     "authors": "Erik Brynjolfsson, Danielle Li, Lindsey Raymond", "date": "2026-07-20",
     "abstract": "We report results from a randomized field experiment with 5,000+ knowledge workers across 12 Fortune 500 companies, measuring the productivity impact of generative AI tools on writing, coding, analysis, and creative tasks.",
     "link": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4567890", "source": "SSRN", "category": "Economics"},
    {"title": "Quantum Error Correction at Scale: Recent Advances and Remaining Challenges",
     "authors": "John Preskill, Peter Shor, et al.", "date": "2026-07-18",
     "abstract": "We review recent experimental demonstrations of quantum error correction codes achieving logical error rates below the physical error rate, and discuss the engineering challenges to achieving fault-tolerant quantum computation at scale.",
     "link": "https://arxiv.org/abs/2607.11500", "source": "arXiv", "category": "quant-ph"},
    {"title": "Central Bank Digital Currencies and Financial Stability: A Network Analysis",
     "authors": "Markus Brunnermeier, Hyun Song Shin", "date": "2026-07-15",
     "abstract": "Using a network model of the financial system, we analyze how the introduction of CBDCs affects financial intermediation, bank funding structures, and systemic risk under various design choices (tiered vs. unconstrained).",
     "link": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4567891", "source": "SSRN", "category": "Economics"},
    {"title": "Efficient Fine-Tuning of Large Language Models via Low-Rank Gradient Compression",
     "authors": "Li Wei, Kim Min-Jun, Anna Schmidt", "date": "2026-07-10",
     "abstract": "We propose LoRA-GC, a novel fine-tuning method combining low-rank adaptation with gradient compression, achieving 3.5x memory reduction and 2.1x speedup compared to full fine-tuning while maintaining 99.2% of the accuracy on standard benchmarks.",
     "link": "https://arxiv.org/abs/2607.10000", "source": "arXiv", "category": "cs.CL"},
]


CATEGORY_MAP = {
    "计算机科学": "cs", "经济学": "econ", "物理学": "physics",
    "数学": "math", "生物学": "q-bio", "统计学": "stat",
}


class PreprintFetcher(BaseFetcher):
    """Fetcher for preprint platforms with arXiv API support."""

    ARXIV_API = "http://export.arxiv.org/api/query"

    def fetch(self, sources: list[str], category: str, keywords: str,
              max_results: int = 20) -> tuple[list[dict], bool]:
        """Fetch preprints. Returns (data, is_mock)."""
        self.use_mock = False
        results = []

        if "arXiv" in sources:
            arxiv_results = self._fetch_arxiv(category, keywords, max_results)
            results.extend(arxiv_results)

        if "SSRN" in sources:
            ssrn_results = self._fetch_ssrn(keywords)
            results.extend(ssrn_results)

        if self.use_mock or not results:
            results = self._get_filtered_mock(sources, category, keywords)

        return results, self.use_mock

    def _fetch_arxiv(self, category: str, keywords: str, max_results: int) -> list[dict]:
        """Query the arXiv API."""
        query_parts = []
        if keywords:
            query_parts.append(f"all:{urllib.parse.quote(keywords)}")
        if category and category in CATEGORY_MAP:
            query_parts.append(f"cat:{CATEGORY_MAP[category]}*")

        if not query_parts:
            query_parts.append("all:artificial+intelligence")

        query_str = "+AND+".join(query_parts)
        url = f"{self.ARXIV_API}?search_query={query_str}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

        html = self.safe_fetch(url)
        if not html:
            return []

        try:
            root = ET.fromstring(html)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)
            results = []
            for entry in entries:
                title = entry.find("atom:title", ns)
                title = title.text.strip().replace("\n", " ") if title is not None and title.text else ""
                summary = entry.find("atom:summary", ns)
                summary = summary.text.strip()[:300] if summary is not None and summary.text else ""
                authors = []
                for author in entry.findall("atom:author", ns):
                    name = author.find("atom:name", ns)
                    if name is not None and name.text:
                        authors.append(name.text)
                link_el = entry.find("atom:id", ns)
                link = link_el.text.strip() if link_el is not None and link_el.text else ""
                published = entry.find("atom:published", ns)
                date = published.text[:10] if published is not None and published.text else ""
                cat_el = entry.find("atom:category", ns)
                cat = cat_el.get("term", "") if cat_el is not None else ""
                results.append({
                    "title": title, "authors": ", ".join(authors[:5]), "date": date,
                    "abstract": summary, "link": link, "source": "arXiv", "category": cat,
                })
            return results
        except Exception:
            self.use_mock = True
            return []

    def _fetch_ssrn(self, keywords: str) -> list[dict]:
        """Attempt to fetch from SSRN (likely falls back to mock)."""
        query = urllib.parse.quote(keywords or "economics")
        url = f"https://papers.ssrn.com/sol3/results.cfm?n=10&sort=date&q={query}"
        html = self.safe_fetch(url)
        if not html:
            return []
        try:
            soup = self.parse_html(html)
            results = []
            for item in soup.select(".result")[:5]:
                title_el = item.select_one("h3 a") or item.find("a")
                title = title_el.get_text(strip=True) if title_el else ""
                link = title_el.get("href", "") if title_el else ""
                if link and not link.startswith("http"):
                    link = f"https://papers.ssrn.com{link}"
                authors_el = item.select_one(".authors") or item.find("span", class_="author")
                authors = authors_el.get_text(strip=True) if authors_el else ""
                date = ""
                if title:
                    results.append({
                        "title": title, "authors": authors, "date": date,
                        "abstract": "", "link": link, "source": "SSRN", "category": "",
                    })
            return results
        except Exception:
            self.use_mock = True
            return []

    def _get_filtered_mock(self, sources, category, keywords):
        """Filter mock data."""
        results = [r for r in MOCK_PREPRINT_DATA if r["source"] in sources]
        if keywords:
            kw_list = [k.strip().lower() for k in keywords.split(",")]
            results = [r for r in results if any(
                kw in (r.get("title", "") + r.get("abstract", "")).lower() for kw in kw_list
            )]
        return results
