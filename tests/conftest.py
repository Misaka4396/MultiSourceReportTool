"""共享 fixtures：测试环境路径与最小 HTML fixture。"""

import os
import sys

import pytest

# 确保被测模块可导入（项目根在 sys.path）
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from article_grab.grabber import _load_article_meta, _safe_name  # noqa: E402,F401
from article_grab.pdf_daily import DailyPDF, _segments  # noqa: E402,F401

# 一份极简"文章页"HTML，模拟真实站点的标题/作者/日期/正文结构
MINIMAL_ARTICLE_HTML = """<!DOCTYPE html>
<html><head><title>测试文章标题</title></head>
<body>
  <article>
    <h1>测试文章标题</h1>
    <p class="author">测试作者</p>
    <p class="date">2026-08-13</p>
    <p>这是正文第一段，用于验证 trafilatura 的正文提取。</p>
    <p>这是正文第二段，包含中文与 English mixed text。</p>
  </article>
  <nav>导航链接（应被剥离）</nav>
  <footer>页脚广告（应被剥离）</footer>
</body></html>
"""


@pytest.fixture
def article_html() -> str:
    return MINIMAL_ARTICLE_HTML


@pytest.fixture
def tmp_out_dir(tmp_path) -> str:
    """隔离的临时输出目录（每个测试独立，符合 P9 数据隔离）。"""
    return str(tmp_path / "out")
