"""Fetcher for top consulting firm reports (McKinsey, BCG, Roland Berger, Accenture)."""

import random
from datetime import datetime, timedelta
from .base import BaseFetcher


MOCK_CONSULTING_DATA = {
    "mckinsey": [
        {"title": "The Future of AI in Global Manufacturing", "authors": "McKinsey Global Institute",
         "date": "2026-06-15", "abstract": "This report examines how artificial intelligence is reshaping manufacturing across industries, with case studies from automotive, electronics, and pharmaceutical sectors. Key findings suggest a 25-40% productivity improvement potential.",
         "link": "https://www.mckinsey.com/mgi/ai-manufacturing-2026", "source": "McKinsey & Company"},
        {"title": "Global Energy Transition Outlook 2026", "authors": "McKinsey Sustainability Practice",
         "date": "2026-05-20", "abstract": "A comprehensive analysis of the global energy transition, covering renewable energy adoption rates, policy developments, and investment trends across 50+ countries.",
         "link": "https://www.mckinsey.com/energy-transition-2026", "source": "McKinsey & Company"},
        {"title": "Digital Payments in Southeast Asia", "authors": "McKinsey Financial Services",
         "date": "2026-04-10", "abstract": "Analyzing the rapid growth of digital payments in ASEAN markets, with projections through 2030 and analysis of key players and regulatory frameworks.",
         "link": "https://www.mckinsey.com/digital-payments-sea-2026", "source": "McKinsey & Company"},
        {"title": "Resilience in Supply Chains: Post-Pandemic Lessons", "authors": "McKinsey Operations Practice",
         "date": "2026-03-01", "abstract": "Drawing on lessons from recent global disruptions, this report presents a framework for building resilient, agile supply chains using digital twin technology and AI-driven forecasting.",
         "link": "https://www.mckinsey.com/supply-chain-resilience-2026", "source": "McKinsey & Company"},
    ],
    "bcg": [
        {"title": "Digital Transformation in Healthcare: A 2030 Vision", "authors": "Boston Consulting Group",
         "date": "2026-07-01", "abstract": "BCG's analysis of digital health trends including telemedicine, AI diagnostics, and personalized medicine, with market size projections and adoption forecasts for major healthcare markets.",
         "link": "https://www.bcg.com/digital-health-2030", "source": "Boston Consulting Group"},
        {"title": "Sustainable Supply Chains: The Net-Zero Imperative", "authors": "BCG Climate & Sustainability",
         "date": "2026-06-01", "abstract": "A roadmap for achieving net-zero supply chains, covering scope 3 emissions measurement, supplier engagement strategies, and technology solutions for carbon tracking.",
         "link": "https://www.bcg.com/net-zero-supply-chains", "source": "Boston Consulting Group"},
        {"title": "The AI-Powered Enterprise of 2030", "authors": "BCG Henderson Institute",
         "date": "2026-04-22", "abstract": "Exploring how AI is fundamentally changing organizational structures, decision-making processes, and competitive dynamics across industries.",
         "link": "https://www.bcg.com/ai-enterprise-2030", "source": "Boston Consulting Group"},
    ],
    "roland_berger": [
        {"title": "European Automotive Industry Outlook 2026", "authors": "Roland Berger Automotive",
         "date": "2026-06-10", "abstract": "Analysis of the European automotive market including EV adoption rates, supply chain restructuring, and competitive dynamics between legacy OEMs and new entrants.",
         "link": "https://www.rolandberger.com/auto-outlook-2026", "source": "Roland Berger"},
        {"title": "China's Green Finance Revolution", "authors": "Roland Berger Financial Services",
         "date": "2026-05-05", "abstract": "An in-depth look at China's green bond market, ESG investment trends, and the regulatory framework driving sustainable finance in the world's second-largest economy.",
         "link": "https://www.rolandberger.com/china-green-finance", "source": "Roland Berger"},
        {"title": "Industrial Decarbonization Pathways", "authors": "Roland Berger Engineered Products",
         "date": "2026-03-18", "abstract": "Technical and economic analysis of decarbonization options for heavy industry including steel, cement, and chemicals, with cost curves and technology readiness assessments.",
         "link": "https://www.rolandberger.com/industrial-decarbonization", "source": "Roland Berger"},
    ],
    "accenture": [
        {"title": "Technology Vision 2026: The Cognitive Enterprise", "authors": "Accenture Technology",
         "date": "2026-07-15", "abstract": "Accenture's annual technology trends report highlighting agentic AI, spatial computing, quantum-ready cryptography, and other emerging technologies shaping the next decade.",
         "link": "https://www.accenture.com/tech-vision-2026", "source": "Accenture"},
        {"title": "Cloud Migration Best Practices: 500 Enterprise Case Studies", "authors": "Accenture Cloud First",
         "date": "2026-06-20", "abstract": "Synthesizing lessons from 500 large-scale cloud migrations, this report provides a decision framework covering architecture choices, cost optimization, and change management.",
         "link": "https://www.accenture.com/cloud-migration-2026", "source": "Accenture"},
        {"title": "The Future of Work: Hybrid Models and Talent Strategies", "authors": "Accenture Strategy",
         "date": "2026-04-30", "abstract": "Research on evolving workplace models, employee preferences, and talent management strategies based on surveys of 10,000+ workers and 1,500 executives globally.",
         "link": "https://www.accenture.com/future-work-2026", "source": "Accenture"},
    ],
}


class ConsultingFetcher(BaseFetcher):
    """Fetcher for consulting firm reports."""

    FIRM_URLS = {
        "mckinsey": "https://www.mckinsey.com/featured-insights",
        "bcg": "https://www.bcg.com/publications",
        "roland_berger": "https://www.rolandberger.com/en/Insights/",
        "accenture": "https://www.accenture.com/us-en/insights",
    }

    def fetch(self, firms: list[str], language: str, start_date: str,
              end_date: str, keywords: str, keyword_logic: str) -> tuple[list[dict], bool]:
        """Fetch consulting reports. Returns (data, is_mock)."""
        self.use_mock = False
        results = []

        for firm in firms:
            if firm in self.FIRM_URLS:
                html = self.safe_fetch(self.FIRM_URLS[firm])
                if html and not self.use_mock:
                    try:
                        parsed = self._parse_firm_page(html, firm)
                        results.extend(parsed)
                    except Exception:
                        self.use_mock = True

        if self.use_mock or not results:
            results = self._get_filtered_mock(firms, language, start_date, end_date, keywords, keyword_logic)

        return results, self.use_mock

    def _parse_firm_page(self, html: str, firm: str) -> list[dict]:
        """Attempt to parse a firm's publications page."""
        soup = self.parse_html(html)
        results = []
        articles = soup.find_all("article") or soup.find_all("div", class_=lambda c: c and "card" in c.lower())
        for art in articles[:5]:
            title_el = art.find("h2") or art.find("h3") or art.find("a")
            title = title_el.get_text(strip=True) if title_el else ""
            link_el = art.find("a", href=True)
            link = link_el["href"] if link_el else ""
            if link and not link.startswith("http"):
                link = f"https://www.{firm.replace('_', '')}.com{link}"
            date_el = art.find("time") or art.find("span", class_=lambda c: c and "date" in c.lower())
            date_str = date_el.get_text(strip=True) if date_el else ""
            if title:
                results.append({
                    "title": title, "authors": firm.replace("_", " ").title(),
                    "date": date_str or "Unknown", "abstract": "",
                    "link": link, "source": firm.replace("_", " ").title(),
                })
        return results

    def _get_filtered_mock(self, firms, language, start_date, end_date, keywords, keyword_logic):
        """Filter and return mock data."""
        all_results = []
        for firm in firms:
            firm_data = MOCK_CONSULTING_DATA.get(firm, [])
            all_results.extend(firm_data)

        # Language filter (mock data is mostly bilingual; we don't filter mock data by language)
        if language == "中文":
            for r in all_results:
                r["title"] = self._mock_chinese_title(r["title"])
                r["abstract"] = f"[中文摘要] {r['abstract']}"

        # Date filter
        if start_date:
            all_results = [r for r in all_results if r.get("date", "") >= start_date]
        if end_date:
            all_results = [r for r in all_results if r.get("date", "") <= end_date]

        # Keyword filter
        if keywords:
            kw_list = [k.strip().lower() for k in keywords.split(",")]
            filtered = []
            for r in all_results:
                text = (r.get("title", "") + r.get("abstract", "")).lower()
                if keyword_logic == "AND":
                    if all(kw in text for kw in kw_list):
                        filtered.append(r)
                else:  # OR
                    if any(kw in text for kw in kw_list):
                        filtered.append(r)
            all_results = filtered

        return all_results

    def _mock_chinese_title(self, eng_title: str) -> str:
        """Generate a mock Chinese title."""
        translations = {
            "AI": "人工智能", "Manufacturing": "制造业", "Energy": "能源",
            "Digital": "数字化", "Healthcare": "医疗健康", "Supply Chain": "供应链",
            "Cloud": "云", "Enterprise": "企业", "Automotive": "汽车",
            "Green": "绿色", "Finance": "金融", "Decarbonization": "脱碳",
            "Work": "工作", "Talent": "人才", "Technology": "技术",
        }
        result = eng_title
        for en, zh in translations.items():
            if en.lower() in eng_title.lower():
                result = eng_title.replace(en, zh)
        return result
