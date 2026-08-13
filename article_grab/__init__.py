"""文章抓取模块 — 正文提取 + PDF 日报生成（MultiSourceReportTool v1.2.1 新增）。"""

from .grabber import fetch_page, fetch_wikipedia, grab  # noqa: F401
from .pdf_daily import generate_daily_pdf  # noqa: F401

__all__ = ["grab", "fetch_page", "fetch_wikipedia", "generate_daily_pdf"]
