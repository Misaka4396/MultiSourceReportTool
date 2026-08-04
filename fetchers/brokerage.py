"""Fetcher for brokerage research reports from East Money (东方财富)."""

import random
from .base import BaseFetcher


MOCK_BROKERAGE_DATA = [
    {"title": "半导体产业链深度报告：AI芯片驱动新一轮景气周期", "authors": "中信证券研究部",
     "date": "2026-07-20", "rating": "买入",
     "abstract": "全球半导体市场在AI大模型训练和推理需求驱动下进入新一轮增长周期。本报告深度梳理芯片设计、制造、封测全产业链，重点推荐GPU/FPGA、HBM存储及先进封装赛道。预计2026年全球半导体市场规模将突破7000亿美元。",
     "link": "https://data.eastmoney.com/report/zw/industry/20260720/semiconductor.html",
     "analyst": "张三, 李四", "industry": "电子", "supply_chain": "上游：硅片/光刻胶/EDA工具 → 中游：芯片设计/晶圆制造/封测 → 下游：AI服务器/消费电子/汽车电子"},
    {"title": "新能源汽车2026中期策略：全球化竞争格局重塑", "authors": "华泰证券研究所",
     "date": "2026-07-15", "rating": "增持",
     "abstract": "全球新能源汽车渗透率持续提升，中国品牌加速出海。本报告分析比亚迪、特斯拉、蔚小理等主要厂商竞争态势，关注固态电池、800V高压平台等关键技术突破。",
     "link": "https://data.eastmoney.com/report/zw/industry/20260715/nev.html",
     "analyst": "王五", "industry": "新能源", "supply_chain": "上游：锂/钴/镍矿 → 中游：动力电池/电机电控 → 下游：整车制造/充电桩/换电"},
    {"title": "医药行业2026年度策略：创新药出海与CXO拐点", "authors": "中金公司研究部",
     "date": "2026-06-28", "rating": "买入",
     "abstract": "中国创新药企License-out交易额持续创新高，CXO行业经历调整后迎来拐点。重点关注ADC、双抗、细胞治疗等前沿技术领域的投资机会，以及全球供应链重构下的CDMO产业转移趋势。",
     "link": "https://data.eastmoney.com/report/zw/industry/20260628/pharma.html",
     "analyst": "赵六, 钱七", "industry": "医药", "supply_chain": "上游：原料药/培养基/色谱填料 → 中游：CDMO/CRO/创新药研发 → 下游：医院/药店/医保支付"},
    {"title": "消费升级趋势分析：新零售与国货品牌崛起", "authors": "招商证券",
     "date": "2026-06-10", "rating": "增持",
     "abstract": "Z世代消费行为变化驱动新零售业态变革。本报告分析直播电商、即时零售、会员店等新渠道增长，以及美妆护肤、运动服饰等国货品牌的市场份额提升逻辑。",
     "link": "https://data.eastmoney.com/report/zw/industry/20260610/consumer.html",
     "analyst": "孙八", "industry": "消费", "supply_chain": "上游：原材料/代工厂 → 中游：品牌运营/渠道分销 → 下游：电商平台/线下零售/消费者"},
    {"title": "AI应用落地元年：从算力到场景的产业链机遇", "authors": "天风证券",
     "date": "2026-07-05", "rating": "买入",
     "abstract": "2026年是AI应用规模化落地的关键一年。报告梳理了AI+办公、AI+教育、AI+医疗、AI+工业等主要应用场景，评估各细分赛道的商业化进展和投资价值。",
     "link": "https://data.eastmoney.com/report/zw/industry/20260705/ai-applications.html",
     "analyst": "周九", "industry": "电子", "supply_chain": "上游：AI芯片/算力基础设施 → 中游：大模型平台 → 下游：行业应用/端侧AI部署"},
    {"title": "氢能产业链全景图：从制氢到用氢的万亿市场", "authors": "国泰君安研究所",
     "date": "2026-05-22", "rating": "增持",
     "abstract": "绿氢成本持续下降，氢能在工业脱碳和长距离运输领域的经济性逐步显现。报告梳理电解槽、燃料电池、储氢运氢等核心技术环节，评估各细分市场空间。",
     "link": "https://data.eastmoney.com/report/zw/industry/20260522/hydrogen.html",
     "analyst": "吴十", "industry": "新能源", "supply_chain": "上游：可再生能源制氢/电解槽 → 中游：储氢/运氢/加氢站 → 下游：燃料电池汽车/工业用氢"},
]


class BrokerageFetcher(BaseFetcher):
    """Fetcher for brokerage reports from East Money research center."""

    BASE_URL = "https://data.eastmoney.com/report/zw/industry.html"

    def fetch(self, industry: str, rating: str, start_date: str,
              end_date: str, keywords: str) -> tuple[list[dict], bool]:
        """Fetch brokerage reports. Returns (data, is_mock)."""
        self.use_mock = False

        html = self.safe_fetch(self.BASE_URL)
        results = []
        if html and not self.use_mock:
            try:
                results = self._parse_page(html)
            except Exception:
                self.use_mock = True

        if self.use_mock or not results:
            results = self._get_filtered_mock(industry, rating, start_date, end_date, keywords)

        return results, self.use_mock

    def _parse_page(self, html: str) -> list[dict]:
        """Parse East Money research center page."""
        soup = self.parse_html(html)
        results = []
        rows = soup.select("table tbody tr") or soup.select(".report-item")
        for row in rows[:10]:
            cells = row.find_all("td")
            if len(cells) >= 4:
                title_el = cells[0].find("a") if cells else None
                title = title_el.get_text(strip=True) if title_el else ""
                link = title_el.get("href", "") if title_el else ""
                org = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                rating_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                date_text = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                if title:
                    results.append({
                        "title": title, "authors": org, "date": date_text,
                        "rating": rating_text, "abstract": "", "link": link,
                        "analyst": "", "industry": "", "supply_chain": "",
                    })
        return results

    def _get_filtered_mock(self, industry, rating, start_date, end_date, keywords):
        """Filter mock data based on constraints."""
        results = list(MOCK_BROKERAGE_DATA)

        if industry and industry != "全部":
            results = [r for r in results if r.get("industry") == industry]
        if rating and rating != "全部":
            results = [r for r in results if r.get("rating") == rating]
        if start_date:
            results = [r for r in results if r.get("date", "") >= start_date]
        if end_date:
            results = [r for r in results if r.get("date", "") <= end_date]
        if keywords:
            kw_list = [k.strip().lower() for k in keywords.split(",")]
            results = [r for r in results if any(
                kw in (r.get("title", "") + r.get("abstract", "")).lower() for kw in kw_list
            )]

        return results
