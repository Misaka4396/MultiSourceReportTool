"""Fetcher for Sci-Hub / Crossref DOI metadata retrieval."""

from .base import BaseFetcher

MOCK_DOI_DATA = {
    "10.1038/nature12373": {
        "title": "A statin-dependent QTL for cardiovascular disease",
        "authors": "Kathiresan S, et al.",
        "journal": "Nature",
        "year": "2013",
        "publisher": "Nature Publishing Group",
    },
    "10.1126/science.aad0919": {
        "title": "Observation of Gravitational Waves from a Binary Black Hole Merger",
        "authors": "Abbott BP, et al. (LIGO Scientific Collaboration and Virgo Collaboration)",
        "journal": "Science",
        "year": "2016",
        "publisher": "AAAS",
    },
    "10.1016/j.cell.2020.02.007": {
        "title": "Structure of the SARS-CoV-2 Spike Glycoprotein in the Prefusion Conformation",
        "authors": "Wrapp D, Wang N, Corbett KS, et al.",
        "journal": "Cell",
        "year": "2020",
        "publisher": "Elsevier",
    },
}


class SciHubFetcher(BaseFetcher):
    """Fetcher for academic paper metadata via Crossref API with Sci-Hub download hints."""

    CROSSREF_API = "https://api.crossref.org/works/"

    # Known Sci-Hub mirrors (for user reference only)
    SCIHUB_MIRRORS = [
        "sci-hub.se",
        "sci-hub.st",
        "sci-hub.ru",
    ]

    def fetch(self, doi_list: list[str]) -> list[dict]:
        """Fetch metadata for a list of DOIs. Returns list of result dicts."""
        results = []
        for doi in doi_list:
            doi = doi.strip()
            if not doi:
                continue
            result = self._lookup_doi(doi)
            results.append(result)
        return results

    def _lookup_doi(self, doi: str) -> dict:
        """Look up a single DOI via Crossref API."""
        # Try real API
        try:
            url = f"{self.CROSSREF_API}{doi}"
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                msg = data.get("message", {})
                authors_list = msg.get("author", [])
                authors = ", ".join(
                    f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_list[:5]
                )
                title_list = msg.get("title", [doi])
                title = title_list[0] if title_list else doi
                journal = ""
                if "container-title" in msg and msg["container-title"]:
                    journal = (
                        msg["container-title"][0]
                        if isinstance(msg["container-title"], list)
                        else msg["container-title"]
                    )

                year = str(msg.get("created", {}).get("date-parts", [[None]])[0][0] or "")
                publisher = msg.get("publisher", "")

                return {
                    "doi": doi,
                    "title": title,
                    "authors": authors,
                    "journal": journal,
                    "year": year,
                    "publisher": publisher,
                    "download_status": "请自行通过Sci-Hub镜像下载",
                    "mirror_hint": f"可用镜像：{', '.join(self.SCIHUB_MIRRORS)}",
                    "is_mock": False,
                }
        except Exception:
            pass

        # Fall back to mock data
        if doi in MOCK_DOI_DATA:
            mock = dict(MOCK_DOI_DATA[doi])
            mock["doi"] = doi
            mock["download_status"] = "示例数据 — 请自行通过Sci-Hub镜像下载"
            mock["mirror_hint"] = f"建议尝试镜像：{', '.join(self.SCIHUB_MIRRORS)}"
            mock["is_mock"] = True
            return mock

        # Generic mock
        return {
            "doi": doi,
            "title": f"文献 {doi}",
            "authors": "示例作者",
            "journal": "示例期刊",
            "year": "2026",
            "publisher": "示例出版社",
            "download_status": "示例数据 — 请自行通过Sci-Hub镜像下载",
            "mirror_hint": f"建议尝试镜像：{', '.join(self.SCIHUB_MIRRORS)}",
            "is_mock": True,
        }
