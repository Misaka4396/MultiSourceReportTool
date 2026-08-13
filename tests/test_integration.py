"""P9 集成测试 — 跨模块链路（HTTP mock + 提取 + 保存 + PDF 生成）。

替身策略：monkeypatch 替换 httpx.Client 的 HTTP 层（不 mock 解析逻辑，
符合"测行为不测实现"）；数据隔离：tmp_path 每测试独立。
"""

import os
import sys

import httpx
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import article_grab.grabber as grabber_mod
from article_grab.grabber import (
    _is_wikipedia,
    extract_article,
    fetch_page,
    fetch_wikipedia,
    grab,
    save_markdown,
)
from article_grab.pdf_daily import generate_daily_pdf


class FakeResponse:
    """极简 httpx.Response 替身（抛 httpx 兼容异常）。"""

    def __init__(self, text: str, status: int = 200):
        self.text = text
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(f"HTTP {self.status_code}", request=None, response=None)


class FakeClient:
    """替身 httpx.Client：按 URL 返回预注册的响应，未注册抛网络异常。"""

    def __init__(self, responses_by_url: dict[str, FakeResponse]):
        self._responses = responses_by_url
        self.headers = {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get(self, url: str, **kwargs):
        if url not in self._responses:
            raise httpx.ConnectError(f"connection failed: {url}")
        return self._responses[url]


@pytest.fixture
def mock_http(monkeypatch):
    """替换 article_grab.grabber 模块内的 httpx.Client。"""

    def _install(responses_by_url: dict[str, FakeResponse]):
        monkeypatch.setattr(
            grabber_mod.httpx, "Client", lambda *a, **kw: FakeClient(responses_by_url)
        )

    return _install


class TestFetchPage:
    """HTTP 层（替身网络）。"""

    def test_success_returns_html(self, mock_http):
        """Given 200 响应 → When fetch_page → Then 返回 HTML。"""
        mock_http({"https://ex.com/a": FakeResponse("<html>ok</html>")})
        assert fetch_page("https://ex.com/a") == "<html>ok</html>"

    def test_http_error_retries_then_none(self, mock_http):
        """Given 4xx/5xx → When fetch_page → Then 重试后返回 None。"""
        mock_http({"https://ex.com/b": FakeResponse("", status=404)})
        assert fetch_page("https://ex.com/b") is None

    def test_network_error_returns_none(self, mock_http):
        """Given 未注册 URL（模拟网络异常）→ Then 返回 None 不抛异常。"""
        mock_http({})  # 所有 URL 都会抛 RuntimeError
        assert fetch_page("https://ex.com/c") is None


class TestExtractArticle:
    """正文提取（真实 trafilatura 引擎，本地 HTML fixture）。"""

    def test_metadata_and_body_extracted(self, article_html):
        """Given 标准文章 HTML → When 提取 → Then 标题/正文齐全。"""
        art = extract_article("https://ex.com/a", article_html)
        assert art["title"] != ""
        assert "正文第一段" in art["text"]
        assert "正文第二段" in art["text"]

    def test_navigation_stripped(self):
        """Given 高链接密度导航 + 充分正文 → When 提取 → Then 导航文本被剥离。"""
        body_paras = "".join(
            f"<p>这是正文第{i}段，包含足够的有效文字描述，用于让 trafilatura 判定"
            f"其为页面主体内容而不是导航链接或页脚信息。内容长度足够触发正文提取。</p>"
            for i in range(12)
        )
        html = (
            "<html><head><title>测试标题</title></head><body>"
            "<nav>"
            + "".join(f'<a href="/link{i}">导航链接{i}导航链接{i}</a>' for i in range(20))
            + "</nav>"
            f"<article><h1>测试标题</h1>{body_paras}</article>"
            "<footer>页脚广告页脚广告页脚广告</footer>"
            "</body></html>"
        )
        art = extract_article("https://ex.com/a", html)
        assert "正文第1段" in art["text"]
        assert "导航链接0" not in art["text"]


class TestSaveMarkdown:
    """Markdown 落盘。"""

    def test_file_created_with_heading(self, tmp_out_dir):
        """Given 文章 dict → When 保存 → Then 生成 md 且首行为标题。"""
        path = save_markdown(
            {
                "url": "https://ex.com/a",
                "title": "标题A",
                "date": "2026-08-13",
                "site": "ex.com",
                "text": "正文",
            }
        )
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as f:
            assert f.readline().startswith("# ")


class TestGenerateDailyPdf:
    """PDF 日报生成（防挤压验证）。"""

    def _make_articles(self):
        long_url = "https://example.com/research/" + "verylongpath" * 40
        return [
            {
                "title": "文章一" * 30,
                "author": "作者A",
                "date": "2026-08-13",
                "site": "site-a",
                "url": long_url,
                "text": "第一段正文。" * 100,
            },
            {
                "title": "文章二",
                "author": "作者B",
                "date": "2026-08-12",
                "site": "site-b",
                "url": "https://ex.com/2",
                "text": "第二段正文。" * 80,
            },
        ]

    def test_pdf_generated_and_contains_bodies(self, tmp_out_dir):
        """Given 2 篇文章（含超长标题/URL）→ When 生成 → Then PDF 含全部正文。"""
        import pymupdf

        path = generate_daily_pdf(self._make_articles(), tmp_out_dir)
        assert os.path.exists(path) and os.path.getsize(path) > 1000
        doc = pymupdf.open(path)
        text = "".join(p.get_text() for p in doc)
        assert "第一段正文" in text
        assert "第二段正文" in text
        doc.close()

    def test_pdf_no_overlap_no_overflow(self, tmp_out_dir):
        """Given 极端长文本 → When 生成 → Then 逐词检测 0 重叠 0 溢出。"""
        import pymupdf

        path = generate_daily_pdf(self._make_articles(), tmp_out_dir)
        doc = pymupdf.open(path)
        overlaps = overflows = 0
        for page in doc:
            words = page.get_text("words")
            pw, ph = page.rect.width, page.rect.height
            for w in words:
                if w[0] < 45 or w[2] > pw - 45 or w[3] > ph - 8:
                    overflows += 1
            for i in range(len(words)):
                for j in range(i + 1, len(words)):
                    a, b = words[i], words[j]
                    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
                    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
                    if ix1 > ix0 and iy1 > iy0 and (ix1 - ix0) * (iy1 - iy0) > 1.5:
                        overlaps += 1
        doc.close()
        assert overlaps == 0, f"检测到 {overlaps} 处文字重叠"
        assert overflows == 0, f"检测到 {overflows} 处溢出"


class TestWikipediaAdapter:
    """维基百科 API 适配器（反爬 403 的替代通道）。"""

    def test_is_wikipedia_detects_wiki_entries(self):
        """Given 维基词条 URL → Then 返回语言代码；非维基/非词条返回 None。"""
        assert _is_wikipedia("https://zh.wikipedia.org/wiki/Python") == "zh"
        assert _is_wikipedia("https://en.wikipedia.org/wiki/Web_scraping") == "en"
        assert _is_wikipedia("https://example.com/article") is None
        assert _is_wikipedia("https://zh.wikipedia.org/wiki/") is None
        assert _is_wikipedia("https://zh.wikipedia.org/w/index.php?title=X") is None

    def test_fetch_wikipedia_uses_api(self, mock_http, monkeypatch):
        """Given 维基 URL → When 抓取 → Then 请求官方 REST API 并返回 HTML。"""
        mock_http({})
        # 断言请求的是 /api/rest_v1/page/html/<title> 而非 /wiki/<title>
        seen = {}

        class CapturingClient(FakeClient):
            def get(self, url, **kwargs):
                seen["url"] = url
                return FakeResponse("<html><article><h1>Python</h1><p>正文</p></article></html>")

        monkeypatch.setattr(grabber_mod.httpx, "Client", lambda *a, **kw: CapturingClient({}))
        html = fetch_wikipedia("https://zh.wikipedia.org/wiki/Python")
        assert html is not None
        assert "api/rest_v1/page/html/Python" in seen["url"]

    def test_fetch_wikipedia_non_wiki_returns_none(self):
        """Given 非维基 URL → Then 返回 None（不误伤普通站点）。"""
        assert fetch_wikipedia("https://example.com/article") is None


class TestGrabEndToEnd:
    """全链路（替身 HTTP，不联网）。"""

    def test_grab_writes_markdown(self, tmp_out_dir, monkeypatch, mock_http):
        """Given mock 文章页 → When grab → Then 生成 md 且返回 True。"""
        mock_http(
            {
                "https://ex.com/article": FakeResponse(
                    "<html><head><title>标题</title></head><body>"
                    "<article><h1>标题</h1><p>正文内容测试。</p></article></body></html>"
                )
            }
        )
        monkeypatch.setattr(grabber_mod, "OUT_DIR", tmp_out_dir)
        ok = grab("https://ex.com/article")
        assert ok is True
        md_files = [f for f in os.listdir(tmp_out_dir) if f.endswith(".md")]
        assert len(md_files) == 1
