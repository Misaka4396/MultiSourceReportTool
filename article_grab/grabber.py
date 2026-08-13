"""文章抓取 Demo — trafilatura + httpx 正文提取。

用法:
    python article_grabber.py <url1> [<url2> ...]
    python article_grabber.py --file urls.txt
    python article_grabber.py --demo          # 运行内置示例 URL

输出:
    out/<域名>_<日期>.md  — 每篇文章一个 Markdown 文件
"""

import argparse
import os
import re
import sys
from datetime import datetime
from typing import Any

import httpx
import trafilatura

# Windows 控制台 UTF-8 输出
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 输出目录：项目根/out（包内模块用 __file__ 上级两级定位）
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def _safe_name(text: str, max_len: int = 60) -> str:
    """文件名净化：非法字符替换 + 超长截断。"""
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", text or "").strip()
    text = re.sub(r"\s+", "_", text)
    return text[:max_len].rstrip("_") or "article"


def fetch_page(url: str, timeout: float = 20.0) -> str | None:
    """httpx 抓取 HTML，带真实浏览器头 + 重试一次。"""
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
        for attempt in (1, 2):
            try:
                resp = client.get(url)
                resp.raise_for_status()
                return resp.text
            except (httpx.HTTPError, OSError) as exc:
                print(f"  ⚠️ 第 {attempt} 次请求失败: {exc}")
                if attempt == 2:
                    return None
    return None  # 所有尝试均失败


# 维基百科域名 → 语言代码（页面 HTML 反爬 403，官方 REST API 可用）
WIKI_DOMAINS = {
    "zh.wikipedia.org": "zh",
    "en.wikipedia.org": "en",
    "ja.wikipedia.org": "ja",
    "fr.wikipedia.org": "fr",
    "de.wikipedia.org": "de",
    "ru.wikipedia.org": "ru",
    "es.wikipedia.org": "es",
}


def _is_wikipedia(url: str) -> str | None:
    """若 URL 是维基百科词条页，返回语言代码；否则 None。"""
    from urllib.parse import urlparse

    host = urlparse(url).netloc.lower()
    lang = WIKI_DOMAINS.get(host)
    if not lang:
        return None
    path = urlparse(url).path
    if not path.startswith("/wiki/") or len(path) <= len("/wiki/"):
        return None
    return lang


def fetch_wikipedia(url: str, timeout: float = 20.0) -> str | None:
    """通过维基百科官方 REST API 获取词条完整 HTML（绕过页面反爬）。"""
    lang = _is_wikipedia(url)
    if not lang:
        return None
    from urllib.parse import unquote

    title = unquote(url.rsplit("/wiki/", 1)[1].split("#")[0].split("?")[0]).replace("_", " ")
    api_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/html/{title}"
    headers = {
        "User-Agent": "ArticleGrabDemo/1.2.1 (research; contact: 82802571@qq.com)",
        "Accept": "text/html",
    }
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=timeout) as client:
            resp = client.get(api_url)
            resp.raise_for_status()
            return resp.text
    except (httpx.HTTPError, OSError) as exc:
        print(f"  ⚠️ 维基百科 API 请求失败: {exc}")
        return None


def extract_article(url: str, html: str) -> dict[str, Any]:
    """trafilatura 提取正文，返回结构化字典。"""
    text = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
        favor_recall=False,
    )
    meta = trafilatura.extract_metadata(html, default_url=url)
    return {
        "url": url,
        "title": (meta.title if meta and meta.title else url),
        "author": (meta.author if meta else None),
        "date": (meta.date if meta else None),
        "site": (meta.sitename if meta else None),
        "text": text or "",
    }


def save_markdown(article: dict[str, Any]) -> str:
    """将文章存为 Markdown 文件，返回文件路径。"""
    os.makedirs(OUT_DIR, exist_ok=True)
    site = article.get("site")
    url = article.get("url", "")
    title = article.get("title", "untitled")
    text = article.get("text", "")
    domain = re.sub(r"^www\.", "", site or re.sub(r"^https?://", "", url).split("/")[0])
    domain = _safe_name(domain, 30)
    date = article.get("date") or datetime.now().strftime("%Y%m%d")
    date = re.sub(r"[^0-9]", "", date)[:8] or datetime.now().strftime("%Y%m%d")
    fname = f"{domain}_{date}_{_safe_name(title, 40)}.md"
    path = os.path.join(OUT_DIR, fname)

    lines = [f"# {title}", ""]
    if article.get("author"):
        lines.append(f"- 作者：{article['author']}")
    if article.get("date"):
        lines.append(f"- 日期：{article['date']}")
    if site:
        lines.append(f"- 来源：{site}")
    lines += ["- 原文链接：" + url, "", "---", "", text, ""]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def grab(url: str) -> bool:
    """抓取单篇文章：请求 → 提取 → 保存。

    维基百科词条页自动走官方 REST API（页面 HTML 有反爬 403）。
    """
    print(f"\n▶ 抓取: {url}")
    if _is_wikipedia(url):
        html = fetch_wikipedia(url)
        source = "维基百科 API"
    else:
        html = fetch_page(url)
        source = "HTTP"
    if not html:
        print(f"  ❌ 抓取失败（{source}：网络/反爬/超时）")
        return False
    article = extract_article(url, html)
    if not article["text"]:
        print("  ❌ 页面已获取但未能提取正文（可能是 JS 渲染页）")
        return False
    path = save_markdown(article)
    n_chars = len(article["text"])
    print(f"  ✅ 标题: {article['title'][:60]}")
    print(f"  ✅ 正文: {n_chars} 字  →  {path}")
    return True


DEMO_URLS = [
    "https://arxiv.org/abs/2306.05284",  # arXiv 论文页（学术）
    "https://zh.wikipedia.org/wiki/Python",  # 维基百科（多语言）
]


def main() -> None:
    parser = argparse.ArgumentParser(description="文章抓取 Demo (trafilatura + httpx)")
    parser.add_argument("urls", nargs="*", help="要抓取的 URL")
    parser.add_argument("--file", help="从文本文件读取 URL 列表（每行一个）")
    parser.add_argument("--demo", action="store_true", help="运行内置示例 URL")
    parser.add_argument(
        "--pdf", action="store_true", help="同时生成 PDF 日报（合并所有成功抓取的文章）"
    )
    args = parser.parse_args()

    urls = list(args.urls)
    if args.file and os.path.exists(args.file):
        with open(args.file, encoding="utf-8") as f:
            urls += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    if args.demo or not urls:
        urls = DEMO_URLS
        print("使用内置示例 URL")

    ok = 0
    grabbed = []
    for url in urls:
        if grab(url):
            ok += 1
            grabbed.append(_load_article_meta(url))
    print(f"\n完成: {ok}/{len(urls)} 成功，输出目录: {OUT_DIR}")

    if args.pdf and grabbed:
        try:
            from .pdf_daily import generate_daily_pdf

            pdf_path = generate_daily_pdf(grabbed, OUT_DIR)
            print(f"📄 PDF 日报生成: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
        except Exception as exc:  # noqa: BLE001 — CLI 边界，需兜底所有生成错误
            print(f"❌ PDF 日报生成失败: {exc}")


def _load_article_meta(url: str) -> dict[str, Any]:
    """从 out/ 目录读取刚抓取文章的最新 Markdown，回填结构化字段。

    按「原文链接：<url>」内容匹配文件（文件名可能用 site 名或域名，
    内容匹配最可靠）。
    """
    latest = None
    for fn in os.listdir(OUT_DIR):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(OUT_DIR, fn)
        try:
            with open(p, encoding="utf-8") as f:
                head = f.read(2000)
        except OSError:
            continue
        if f"原文链接：{url}" in head and (
            latest is None or os.path.getmtime(p) > os.path.getmtime(latest)
        ):
            latest = p
    if latest is None:
        return {"title": url, "url": url, "text": ""}
    with open(latest, encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else url
    meta = {"title": title, "url": url, "text": content}
    for key, label in (("author", "作者"), ("date", "日期"), ("site", "来源")):
        for ln in lines[:8]:
            if ln.startswith(f"- {label}："):
                meta[key] = ln[len(f"- {label}：") :].strip()
                break
    return meta


if __name__ == "__main__":
    main()
