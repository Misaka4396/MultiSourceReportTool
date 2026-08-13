"""PDF 日报生成 — 将多篇文章合并为一份学术风格 PDF 日报。

复用 MultiSourceReportTool 的排版经验：
- 中文字体自动查找（微软雅黑/宋体）
- multi_cell 自动换行 + 显式坐标控制，避免文字挤压
- 超长 URL 逐字符硬断行
- 封面 + 目录 + 正文分节
"""

import logging
import os
from datetime import datetime
from typing import Any

from fpdf import FPDF
from fpdf.enums import XPos, YPos


def _find_chinese_font() -> str:
    """查找系统可用的中文字体（Windows / Linux / macOS）。"""
    candidates = [
        # Windows
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        # Linux (Noto CJK / 文泉驿 / 文鼎)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        # macOS
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


def _segments(text: str) -> list[str]:
    """将文本切分为中文字符 / 连续 ASCII 段（用于智能换行）。"""
    units = []
    buf = ""
    for ch in text:
        if ord(ch) > 0x2E7F:  # CJK 及全角
            if buf:
                units.append(buf)
                buf = ""
            units.append(ch)
        else:
            buf += ch
    if buf:
        units.append(buf)
    return units


def _safe_stem(title: str, max_len: int = 80) -> str:
    import re

    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title or "")
    stem = " ".join(stem.split())
    return stem[:max_len].rstrip() or "daily_report"


class DailyPDF(FPDF):
    """带封面 + 目录 + 分节的 PDF 日报。"""

    def __init__(self, title: str, subtitle: str = ""):
        super().__init__("P", "mm", "A4")
        self.report_title = title
        self.report_subtitle = subtitle
        self.font_name = "Helvetica"
        self.toc_entries: list[tuple[str, int]] = []
        self.in_cover = False
        self.in_toc = False

        font_path = _find_chinese_font()
        if font_path:
            try:
                for style in ("", "B", "I", "BI"):
                    self.add_font("CJK", style, font_path)  # fpdf2≥2.5 默认 unicode
                self.font_name = "CJK"
            except Exception as exc:  # noqa: BLE001 — fpdf 字体注册异常类型不定
                logging.warning("中文字体加载失败（%s），回退 Helvetica", exc)
        self.set_auto_page_break(True, 20)

    def content_width(self) -> float:
        return self.w - self.l_margin - self.r_margin

    # ---------- 换行核心 ----------
    def _wrap_text(self, text: str, width: float) -> list[str]:
        if not text:
            return [""]
        width = max(width, 1.0)
        lines, line = [], ""
        for unit in _segments(text):
            if unit == " ":
                if line and not line.endswith(" "):
                    line += " "
                continue
            if self.get_string_width(unit) > width:
                # 超长无空格 token（URL）→ 逐字符硬断
                if line.strip():
                    lines.append(line.rstrip())
                    line = ""
                for ch in unit:
                    if line and self.get_string_width(line + ch) > width:
                        lines.append(line.rstrip())
                        line = ""
                    line += ch
                continue
            candidate = line + unit if line else unit
            if self.get_string_width(candidate) > width:
                lines.append(line.rstrip())
                line = unit
            else:
                line = candidate
        if line.strip():
            lines.append(line.rstrip())
        return lines or [""]

    def _write_wrapped(self, text: str, h: float, width: float = 0, align: str = "L") -> None:
        if width <= 0:
            width = self.content_width()
        for ln in self._wrap_text(text, width):
            if self.get_y() > self.h - 25:
                self.add_page()
            self.cell(width, h, ln, align=align, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ---------- 页面 ----------
    def header(self) -> None:
        if self.in_cover or self.in_toc or self.page_no() == 1:
            return
        self.set_font(self.font_name, "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, self.report_title, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        if self.in_cover:
            return
        self.set_y(-15)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        self.set_font(self.font_name, "", 7)
        self.set_text_color(150, 150, 150)
        self.cell(
            0,
            6,
            f"{self.page_no()}  |  文章抓取日报生成",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    def render_cover(self) -> None:
        self.in_cover = True
        self.add_page()
        self.set_fill_color(27, 106, 201)
        self.rect(0, 0, self.w, 6, "F")
        self.set_y(40)
        self.set_font(self.font_name, "B", 26)
        self.set_text_color(30, 41, 59)
        self._write_wrapped(self.report_title, 14, align="C")
        self.ln(6)
        if self.report_subtitle:
            self.set_font(self.font_name, "", 12)
            self.set_text_color(100, 116, 139)
            self.cell(0, 8, self.report_subtitle, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(8)
        self.set_draw_color(27, 106, 201)
        self.set_line_width(0.6)
        mid = self.w / 2
        self.line(mid - 30, self.get_y(), mid + 30, self.get_y())
        self.ln(10)
        self.set_font(self.font_name, "", 11)
        self.set_text_color(100, 116, 139)
        self.cell(
            0,
            8,
            f"生成日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.set_fill_color(27, 106, 201)
        self.rect(0, self.h - 6, self.w, 6, "F")
        self.in_cover = False

    def render_toc(self) -> None:
        if not self.toc_entries:
            return
        self.in_toc = True
        self.add_page()
        self.set_font(self.font_name, "B", 16)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, "目  录", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)
        for title, page in self.toc_entries:
            self.set_font(self.font_name, "", 11)
            self.set_text_color(51, 65, 85)
            tw = self.content_width() - 15
            t = title
            while self.get_string_width(t) > tw and len(t) > 3:
                t = t[:-4] + "..."
            dots = ""
            remaining = tw - self.get_string_width(t)
            if remaining > self.get_string_width("."):
                dots = "." * int(remaining / self.get_string_width("."))
            self.cell(tw, 8, f"{t} {dots} {page}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.in_toc = False

    def add_article(self, title: str, meta_lines: list[str], body: str) -> None:
        if self.get_y() > self.h - 40:
            self.add_page()
        self.toc_entries.append((title, self.page_no() + 1))
        self.set_font(self.font_name, "B", 14)
        self.set_text_color(27, 106, 201)
        self._write_wrapped(title, 9)
        self.ln(1)
        self.set_font(self.font_name, "", 9)
        self.set_text_color(120, 120, 120)
        for m in meta_lines:
            self._write_wrapped(m, 5)
        self.ln(2)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
        self.set_font(self.font_name, "", 11)
        self.set_text_color(51, 65, 85)
        # 按段落渲染（\n 拆段，避免缺字形警告，保留段落结构）
        for para in (body or "").split("\n"):
            para = para.strip()
            if not para:
                continue
            self._write_wrapped(para, 6.5)
            self.ln(1.5)
        self.ln(5)


def generate_daily_pdf(
    articles: list[dict[str, Any]], output_dir: str, title: str = "", subtitle: str = ""
) -> str:
    """将多篇文章生成一份 PDF 日报。

    Args:
        articles: [{"title", "author", "date", "site", "url", "text"}, ...]
        output_dir: 输出目录
        title/subtitle: 封面标题（默认自动）

    Returns:
        PDF 文件路径
    """
    os.makedirs(output_dir, exist_ok=True)
    if not title:
        title = f"文章抓取日报 {datetime.now().strftime('%Y-%m-%d')}"
    if not subtitle:
        subtitle = f"共 {len(articles)} 篇文章 · 自动抓取汇总"

    pdf = DailyPDF(title=title, subtitle=subtitle)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_top_margin(20)

    pdf.render_cover()

    # 正文（先写正文记录页码，再重建一次输出目录页——简化：直接渲染 TOC 于正文后不精确）
    # 为准确页码，采用两遍法：第一遍只收集分页，第二遍渲染
    # （简化方案：TOC 页码基于估算，正文后附页码）
    for art in articles:
        meta = []
        if art.get("author"):
            meta.append(f"作者：{art['author']}")
        if art.get("date"):
            meta.append(f"日期：{art['date']}")
        if art.get("site"):
            meta.append(f"来源：{art['site']}")
        meta.append(f"原文：{art['url']}")
        pdf.add_article(art.get("title", "未命名"), meta, art.get("text", ""))

    # 两遍法重建：真实页码的目录
    final = DailyPDF(title=title, subtitle=subtitle)
    final.set_left_margin(20)
    final.set_right_margin(20)
    final.set_top_margin(20)
    final.render_cover()
    # 估算 TOC 页数（每行 8mm）
    toc_lines = len(pdf.toc_entries)
    toc_pages = max(1, int(toc_lines * 8 / (final.h - 40)) + 1)
    final.toc_entries = [(t, p + toc_pages) for t, p in pdf.toc_entries]
    final.render_toc()
    for art in articles:
        meta = []
        if art.get("author"):
            meta.append(f"作者：{art['author']}")
        if art.get("date"):
            meta.append(f"日期：{art['date']}")
        if art.get("site"):
            meta.append(f"来源：{art['site']}")
        meta.append(f"原文：{art['url']}")
        final.add_article(art.get("title", "未命名"), meta, art.get("text", ""))

    stem = _safe_stem(title)
    fname = f"{stem}.pdf"
    path = os.path.join(output_dir, fname)
    final.output(path)
    return path
