"""Fetcher for HS Code trade data (mock with realistic data)."""

from .base import BaseFetcher

# Realistic mock trade data
MOCK_TRADE_DATA = [
    {
        "title": "集成电路/微电子组件",
        "hs_code": "8542",
        "trade_value": 483_500_000_000,
        "quantity": "2,850亿个",
        "yoy_change": "+12.3%",
        "top_partners": [
            "中国台湾 (28.5%)",
            "韩国 (18.2%)",
            "日本 (12.1%)",
            "马来西亚 (8.7%)",
            "越南 (7.3%)",
            "美国 (6.1%)",
            "新加坡 (5.5%)",
            "德国 (3.2%)",
            "菲律宾 (2.8%)",
            "泰国 (2.1%)",
        ],
        "flow_desc": "中国作为全球最大的半导体消费国，从中国台湾和韩国进口大量高端芯片（7nm以下制程），同时向东南亚出口成熟制程芯片（28nm以上）。供应链呈现「研发在美韩台，制造在东亚，封装在东南亚」的三级分工格局。",
        "date": "2026-Q1",
    },
    {
        "title": "半导体器件（二极管、晶体管等）",
        "hs_code": "8541",
        "trade_value": 127_800_000_000,
        "quantity": "4,100亿个",
        "yoy_change": "+8.7%",
        "top_partners": [
            "中国台湾 (22.3%)",
            "日本 (15.8%)",
            "韩国 (13.5%)",
            "德国 (10.2%)",
            "美国 (9.1%)",
            "马来西亚 (7.6%)",
            "越南 (6.4%)",
            "新加坡 (4.9%)",
            "荷兰 (3.3%)",
            "泰国 (2.8%)",
        ],
        "flow_desc": "功率半导体器件（IGBT、SiC MOSFET等）需求受新能源车和光伏逆变器拉动快速增长。中国在功率半导体领域自给率持续提升（约35%），但高端产品仍依赖进口。",
        "date": "2026-Q1",
    },
    {
        "title": "电话机及其他通信设备",
        "hs_code": "8517",
        "trade_value": 312_600_000_000,
        "quantity": "18.5亿台",
        "yoy_change": "+5.2%",
        "top_partners": [
            "美国 (22.1%)",
            "中国香港 (14.3%)",
            "日本 (9.8%)",
            "韩国 (8.5%)",
            "荷兰 (7.2%)",
            "印度 (6.9%)",
            "德国 (5.1%)",
            "越南 (4.8%)",
            "英国 (3.6%)",
            "巴西 (3.2%)",
        ],
        "flow_desc": "智能手机及通信基站设备是中国最大的单项出口品类之一。苹果iPhone供应链深度依赖中国组装产能，同时华为5G基站设备出口至欧洲、中东及拉美市场持续增长。",
        "date": "2026-Q1",
    },
    {
        "title": "自动数据处理设备及部件",
        "hs_code": "8471",
        "trade_value": 215_300_000_000,
        "quantity": "8.2亿台",
        "yoy_change": "+15.8%",
        "top_partners": [
            "美国 (25.6%)",
            "荷兰 (11.3%)",
            "日本 (9.7%)",
            "德国 (8.2%)",
            "印度 (6.5%)",
            "韩国 (5.8%)",
            "英国 (5.1%)",
            "新加坡 (4.7%)",
            "澳大利亚 (3.9%)",
            "加拿大 (3.4%)",
        ],
        "flow_desc": "AI服务器需求爆发式增长是2026年该品类贸易增长的主要驱动力。英伟达GPU服务器大量从中国台湾和韩国进口组件，在中国组装后出口至全球云服务商数据中心。",
        "date": "2026-Q1",
    },
    {
        "title": "锂离子电池",
        "hs_code": "8507.60",
        "trade_value": 98_400_000_000,
        "quantity": "350 GWh",
        "yoy_change": "+22.1%",
        "top_partners": [
            "德国 (18.2%)",
            "美国 (16.5%)",
            "韩国 (12.3%)",
            "日本 (10.8%)",
            "越南 (8.9%)",
            "印度 (7.4%)",
            "荷兰 (6.1%)",
            "英国 (5.5%)",
            "法国 (4.8%)",
            "巴西 (3.9%)",
        ],
        "flow_desc": "中国动力电池企业（宁德时代、比亚迪、中创新航等）占全球市场份额超60%，通过直接出口和在海外建厂（匈牙利、印尼、墨西哥）满足全球电动车产能扩张需求。",
        "date": "2026-Q1",
    },
]


class HSCodeFetcher(BaseFetcher):
    """Fetcher for HS code trade data (primarily mock due to API restrictions)."""

    BASE_URL = "https://comtrade.un.org/data/"

    def fetch(
        self, country: str, hs_query: str, trade_type: str, start_date: str, end_date: str
    ) -> tuple[list[dict], bool]:
        """Fetch trade data. Returns (data, is_mock)."""
        self.use_mock = False

        # UN Comtrade requires API key for programmatic access; attempt page fetch
        html = self.safe_fetch(self.BASE_URL)
        if html and not self.use_mock:
            # Real Comtrade scraping would be complex; for now we mark as mock
            self.use_mock = True

        results = self._get_filtered_mock(country, hs_query, trade_type)
        return results, True  # Always mock since Comtrade needs API key

    def _get_filtered_mock(self, country: str, hs_query: str, trade_type: str) -> list[dict]:
        """Filter mock trade data."""
        results = []
        for item in MOCK_TRADE_DATA:
            hs = item.get("hs_code", "")
            if hs_query and hs_query.lower() not in hs.lower():
                continue
            results.append(dict(item))

        if not results:
            results = list(MOCK_TRADE_DATA)

        # Add country context
        country_map = {
            "中国 (China)": "中国",
            "美国 (USA)": "美国",
            "德国 (Germany)": "德国",
            "越南 (Vietnam)": "越南",
            "印度 (India)": "印度",
        }
        country_name = country_map.get(country, country)

        for r in results:
            r["country"] = country_name
            r["trade_type"] = trade_type
            r["notes"] = (
                f"以上数据为模拟示例，基于{country_name}贸易统计口径。实际数据请查询UN Comtrade数据库。"
            )

        return results
