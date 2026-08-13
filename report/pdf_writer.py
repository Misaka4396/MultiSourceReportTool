"""PDF report generator with academic formatting using fpdf2.

Layout notes (fixes for text overlap):
- Every paragraph is wrapped with a CJK-aware, char-level line breaker
  (`_wrap_text`) so long titles / URLs / cell contents never overflow the
  right margin.
- Text is emitted one line at a time via `cell()` with explicit
  `new_x=XPos.LMARGIN, new_y=YPos.NEXT`, instead of mixing `multi_cell()`
  with manual `set_x()/set_y()`, which was the source of overlapping glyphs.
- `header()` / `footer()` save and restore the active font/color so a page
  break in the middle of a paragraph never corrupts the following text.
"""

import os
import re
import sys
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

_ILLEGAL_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _safe_stem(stem: str, max_len: int = 80) -> str:
    """Sanitize + truncate a file name stem (no extension) for Windows."""
    stem = _ILLEGAL_FILENAME.sub("_", stem or "")
    stem = " ".join(stem.split())
    if len(stem) > max_len:
        stem = stem[:max_len].rstrip()
    return stem or "report"


def _find_chinese_font() -> str:
    """Find a usable Chinese font file on the system or in resources."""
    candidates = [
        # Windows fonts
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        # Bundled in resources
        os.path.join(os.path.dirname(__file__), "..", "resources", "msyh.ttc"),
        os.path.join(os.path.dirname(__file__), "..", "resources", "font.ttf"),
        # PyInstaller bundled path
        os.path.join(sys._MEIPASS, "resources", "msyh.ttc") if hasattr(sys, "_MEIPASS") else "",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return ""


def _is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x2E80 <= cp <= 0x9FFF
        or 0xF900 <= cp <= 0xFAFF
        or 0xFF00 <= cp <= 0xFFEF
    )


class AcademicPDF(FPDF):
    """Custom PDF with academic report formatting."""

    XP_BLUE = (49, 106, 197)
    HEADING_COLOR = (0, 51, 153)
    BODY_COLOR = (51, 65, 85)
    MUTED_COLOR = (110, 110, 110)
    GRID_COLOR = (200, 200, 200)

    def __init__(self, title: str, subtitle: str = "", dual_column: bool = False):
        super().__init__("P", "mm", "A4")
        self.report_title = title
        self.report_subtitle = subtitle
        self.dual_column = dual_column
        self.font_name = "Helvetica"
        self.body_pt = 11  # body font size in points (fpdf2 owns `font_size` in mm)
        self.line_height_factor = 1.6
        self.toc_entries: list[tuple[str, int, int]] = []  # (title, page, level)
        self.in_toc = False
        self.in_cover = False
        self.section_number = 0
        self._style = ("", self.body_pt, self.BODY_COLOR)

        # Try to load Chinese font
        font_path = _find_chinese_font()
        if font_path:
            try:
                self.add_font("CJK", "", font_path)
                self.add_font("CJK", "B", font_path)
                self.add_font("CJK", "I", font_path)
                self.add_font("CJK", "BI", font_path)
                self.font_name = "CJK"
            except Exception:
                pass

        self.set_auto_page_break(True, 20)

    # ------------------------------------------------------------------ #
    # style helpers
    # ------------------------------------------------------------------ #
    def _set_style(self, style: str = "", size: int | None = None, color=None):
        """Set font + text color and remember them for post-page-break restore."""
        if size is None:
            size = self.font_size_pt
        self.set_font(self.font_name, style, size)
        if color is not None:
            self.set_text_color(*color)
        self._style = (style, size, color)

    def _reapply_style(self):
        style, size, color = self._style
        self.set_font(self.font_name, style, size)
        if color is not None:
            self.set_text_color(*color)

    def content_width(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def line_height(self) -> float:
        return self.font_size_pt * self.line_height_factor * 0.3528  # pt -> mm

    # ------------------------------------------------------------------ #
    # wrapping
    # ------------------------------------------------------------------ #
    def _segments(self, text: str) -> list[str]:
        """Split text into units: CJK chars are individual, latin words stay whole."""
        units: list[str] = []
        buf = ""
        for ch in text:
            if ch in (" ", "\t"):
                if buf:
                    units.append(buf)
                    buf = ""
                units.append(" ")
            elif _is_cjk(ch):
                if buf:
                    units.append(buf)
                    buf = ""
                units.append(ch)
            else:
                buf += ch
        if buf:
            units.append(buf)
        return units

    def _wrap_text(self, text: str, width: float) -> list[str]:
        """Wrap text to `width` mm, breaking long latin tokens char-by-char."""
        if not text:
            return [""]
        width = max(width, 1.0)
        lines: list[str] = []
        line = ""
        for unit in self._segments(text):
            if unit == " ":
                if line and not line.endswith(" "):
                    line += " "
                continue
            candidate = line + unit if line else unit
            if self.get_string_width(unit) > width:
                # Long unbreakable token (URL, etc.) -> hard break by char.
                if line.strip():
                    lines.append(line.rstrip())
                    line = ""
                for ch in unit:
                    if line and self.get_string_width(line + ch) > width:
                        lines.append(line.rstrip())
                        line = ""
                    line += ch
                continue
            if self.get_string_width(candidate) > width:
                lines.append(line.rstrip())
                line = unit
            else:
                line = candidate
        if line.strip():
            lines.append(line.rstrip())
        return lines if lines else [""]

    def _truncate(self, text: str, width: float) -> str:
        if self.get_string_width(text) <= width:
            return text
        ell = "..."
        while text and self.get_string_width(text + ell) > width:
            text = text[:-1]
        return (text.rstrip() + ell) if text else ""

    def _write_wrapped(self, text: str, h: float, align: str = "L", width: float = 0) -> int:
        """Write text as individually wrapped lines with explicit positioning."""
        if width <= 0:
            width = self.content_width()
        lines = self._wrap_text(text, width)
        for ln in lines:
            if self.get_y() > self.h - 25:
                self.add_page()
                self._reapply_style()
            self.cell(width, h, ln, align=align, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        return len(lines)

    # ------------------------------------------------------------------ #
    # header / footer
    # ------------------------------------------------------------------ #
    def header(self):
        if self.in_cover or self.in_toc:
            return
        self._reapply_style()
        self.set_font(self.font_name, "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, self._truncate(self.report_title, self.content_width()),
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        if self.in_cover:
            return
        self._reapply_style()
        self.set_y(-15)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        self.set_font(self.font_name, "", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, f"{self.page_no()}  |  多源报告汇总工具生成", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ------------------------------------------------------------------ #
    # cover / toc
    # ------------------------------------------------------------------ #
    def render_cover(self, date_str: str = ""):
        self.in_cover = True
        self.add_page()

        # Top XP-blue bars
        self.set_fill_color(*self.XP_BLUE)
        self.rect(0, 0, self.w, 6, "F")
        self.set_fill_color(27, 106, 201)
        self.rect(0, 6, self.w, 1.5, "F")

        # Title block
        self.set_y(32)
        self._set_style("B", 24, self.HEADING_COLOR)
        self._write_wrapped(self.report_title, 13, "C")
        self.ln(3)
        self._set_style("", 11, self.MUTED_COLOR)
        self._write_wrapped("Multi-Source Report Aggregation Tool", 7, "C")
        self.ln(6)

        # Centered separator
        self.set_draw_color(*self.XP_BLUE)
        self.set_line_width(0.6)
        mid = self.w / 2
        self.line(mid - 35, self.get_y(), mid + 35, self.get_y())
        self.ln(12)

        if self.report_subtitle:
            self._set_style("", 13, (60, 60, 60))
            self._write_wrapped(self.report_subtitle, 8, "C")
            self.ln(8)

        self._set_style("", 12, self.MUTED_COLOR)
        self.cell(0, 8, f"生成日期：{date_str or datetime.now().strftime('%Y-%m-%d')}",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Bottom XP-blue bar
        self.set_fill_color(*self.XP_BLUE)
        self.rect(0, self.h - 6, self.w, 6, "F")

        self.in_cover = False

    def render_toc(self):
        if not self.toc_entries:
            return
        self.in_toc = True
        self.add_page()

        self._set_style("B", 18, self.HEADING_COLOR)
        self.cell(0, 12, "目  录", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(8)

        line_w = self.content_width()
        for title, page, level in self.toc_entries:
            indent = level * 8
            title_w = line_w - indent - 14
            page_str = str(page)
            page_w = self.get_string_width(page_str) + 4
            left_w = title_w - page_w

            # Truncate title to fit (with ellipsis) so it never collides with dots/page.
            display = title
            if self.get_string_width(display) > left_w - 4:
                ell = "..."
                while self.get_string_width(display) > left_w - 4 - self.get_string_width(ell) and len(display) > 1:
                    display = display[:-1]
                display = display.rstrip() + ell

            dot_w = self.get_string_width(".")
            remaining = left_w - self.get_string_width(display) - 2
            dots = "." * int(remaining / dot_w) if remaining > dot_w else ""

            self.set_x(self.l_margin + indent)
            self._set_style("B" if level == 0 else "", 11, self.BODY_COLOR)
            self.cell(left_w, 8, f"{display} {dots}", new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.cell(page_w, 8, page_str, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.in_toc = False

    # ------------------------------------------------------------------ #
    # sections / table / references
    # ------------------------------------------------------------------ #
    def add_section(self, title: str, content_lines: list[str], level: int = 0):
        self.section_number += 1
        sec_label = f"§{self.section_number}"

        if self.get_y() > self.h - 45:
            self.add_page()

        # Record TOC entry at the page where the heading actually starts.
        self.toc_entries.append((f"{sec_label} {title}", self.page_no(), level))

        self._set_style("B", 14 if level == 0 else 12, self.HEADING_COLOR)
        heading_h = (14 if level == 0 else 12) * self.line_height_factor * 0.3528 + 1
        self._write_wrapped(f"{sec_label}  {title}", heading_h, "L")
        self.ln(2)

        self._set_style("", self.body_pt, self.BODY_COLOR)
        lh = self.line_height()
        for line in content_lines:
            if not line:
                self.ln(lh)
                continue
            self._write_wrapped(line, lh, "L")
            self.ln(1)
        self.ln(4)

    def add_table(self, headers: list[str], rows: list[list[str]],
                  col_widths: list[float] | None = None, font_size: int = 9,
                  padding: float = 1.6):
        """Render a grid table with wrapped cells and auto row heights.

        Rows are never split across pages: if a row does not fit, the whole
        row (with a repeated header) is moved to the next page.
        """
        n = len(headers)
        cw = self.content_width()
        if col_widths is None:
            col_widths = [cw / n] * n
        else:
            total = sum(col_widths)
            col_widths = [w / total * cw for w in col_widths]

        line_h = font_size * 1.35 * 0.3528
        cell_pad = padding * 2

        header_lines = [self._wrap_text(str(h), w - cell_pad) for h, w in zip(headers, col_widths)]
        header_h = max(len(ls) for ls in header_lines) * line_h + cell_pad

        def draw_header():
            self._draw_table_row(headers, col_widths, header_lines, header_h, line_h,
                                 cell_pad, font_size, fill=self.XP_BLUE,
                                 text_color=(255, 255, 255), font_style="B")

        # Temporarily disable auto page-break so fpdf2 never splits a row on us.
        self.set_auto_page_break(False)
        try:
            if self.get_y() + header_h > self.h - 25:
                self.add_page()
            draw_header()

            for ridx, row in enumerate(rows):
                cells = [str(row[i]) if i < len(row) else "" for i in range(n)]
                cell_lines = [self._wrap_text(c, w - cell_pad) for c, w in zip(cells, col_widths)]
                row_h = max(len(ls) for ls in cell_lines) * line_h + cell_pad

                if self.get_y() + row_h > self.h - 25:
                    self.add_page()
                    draw_header()

                fill = (245, 247, 250) if ridx % 2 == 1 else (255, 255, 255)
                self._draw_table_row(cells, col_widths, cell_lines, row_h, line_h,
                                     cell_pad, font_size, fill=fill,
                                     text_color=(0, 0, 0), font_style="")
            self.ln(2)
        finally:
            self.set_auto_page_break(True, 20)

    def _draw_table_row(self, cells, col_widths, cell_lines, row_h, line_h,
                        cell_pad, font_size, fill, text_color, font_style):
        y0 = self.get_y()
        x = self.l_margin
        self.set_draw_color(*self.GRID_COLOR)
        self.set_line_width(0.2)
        for w, lines in zip(col_widths, cell_lines):
            self.set_fill_color(*fill)
            self.rect(x, y0, w, row_h, "DF")
            self._set_style(font_style, font_size, text_color)
            ty = y0 + cell_pad / 2
            for ln in lines:
                self.set_xy(x + cell_pad / 2, ty)
                self.cell(w - cell_pad, line_h, ln, align="L")
                ty += line_h
            x += w
        self.set_y(y0 + row_h)

    def add_references(self, refs: list[str]):
        self.add_page()
        self._set_style("B", 16, self.HEADING_COLOR)
        self.cell(0, 10, "参考文献", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)

        self._set_style("", 10, self.BODY_COLOR)
        for i, ref in enumerate(refs, 1):
            self._write_wrapped(f"[{i}] {ref}", 6, "L")
            self.ln(1)


def _build_content(item: dict, selected_fields: list[str], field_labels: dict[str, str]) -> list[str]:
    content = []
    for field in selected_fields:
        if field in item and item[field]:
            label = field_labels.get(field, field)
            value = item[field]
            if isinstance(value, list):
                value = "; ".join(str(v) for v in value)
            content.append(f"{label}：{value}")
    return content


def generate_pdf_report(
    title: str,
    subtitle: str,
    data: list[dict],
    output_dir: str,
    selected_fields: list[str],
    field_labels: dict[str, str],
    dual_column: bool = False,
    filename_stem: str = "",
) -> str:
    """Generate an academic-style PDF report (cover + TOC + sections + references)."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    if not filename_stem:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_stem = _safe_stem(f"{title.replace(' ', '_')}_{timestamp}")
    else:
        filename_stem = _safe_stem(filename_stem)
    filepath = os.path.join(output_dir, f"{filename_stem}.pdf")

    def sections_for(items):
        out = []
        for item in items:
            out.append((
                item.get("title", item.get("名称", "Untitled")),
                _build_content(item, selected_fields, field_labels),
            ))
        return out

    def references_for(items):
        refs = []
        for item in items:
            if "link" in item and item["link"]:
                refs.append(f"{item.get('title', '')} — {item['link']}")
            elif "原文链接" in item and item["原文链接"]:
                refs.append(f"{item.get('title', item.get('名称', ''))} — {item['原文链接']}")
        return refs

    sections = sections_for(data)
    references = references_for(data)

    # Pass 1: measure real page numbers for the TOC (body starts at page 2).
    probe = AcademicPDF(title=title, subtitle=subtitle, dual_column=dual_column)
    probe.set_left_margin(20)
    probe.set_right_margin(20)
    probe.set_top_margin(20)
    probe.render_cover(date_str)
    for sec_title, content in sections:
        probe.add_section(sec_title, content)
    entries = list(probe.toc_entries)

    # Dry-run the TOC to learn how many pages it occupies.
    offset = 0
    if entries:
        dry = AcademicPDF(title=title, subtitle=subtitle, dual_column=dual_column)
        dry.set_left_margin(20)
        dry.set_right_margin(20)
        dry.set_top_margin(20)
        dry.toc_entries = [(t, 0, lv) for t, _, lv in entries]
        dry.render_cover(date_str)
        dry.render_toc()
        offset = dry.page - 1

    # Final pass.
    final_pdf = AcademicPDF(title=title, subtitle=subtitle, dual_column=dual_column)
    final_pdf.set_left_margin(20)
    final_pdf.set_right_margin(20)
    final_pdf.set_top_margin(20)
    final_pdf.render_cover(date_str)
    final_pdf.toc_entries = [(t, p + offset, lv) for t, p, lv in entries]
    final_pdf.render_toc()
    for sec_title, content in sections:
        final_pdf.add_section(sec_title, content)
    if references:
        final_pdf.add_references(references)

    final_pdf.output(filepath)
    return filepath


def generate_daily_pdf_report(
    title: str,
    subtitle: str,
    module_sections: list[dict],
    output_dir: str,
    filename_stem: str,
) -> str:
    """Generate a daily digest PDF: cover + summary table + per-module tables.

    Args:
        module_sections: list of dicts with keys
            "name" (str), "items" (list[dict]), "fields" (dict key->label).
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename_stem = _safe_stem(filename_stem)
    filepath = os.path.join(output_dir, f"{filename_stem}.pdf")

    pdf = AcademicPDF(title=title, subtitle=subtitle)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_top_margin(20)
    pdf.render_cover(date_str)

    # Summary table
    summary_rows = []
    for sec in module_sections:
        summary_rows.append([sec["name"], str(len(sec["items"]))])
    pdf.add_section("内容概览", [f"本次日报共覆盖 {len(module_sections)} 个信息源模块。"])
    pdf.add_table(["来源模块", "结果数量"], summary_rows, col_widths=[0.7, 0.3], font_size=9)

    # Per-module detail tables
    for sec in module_sections:
        name = sec["name"]
        items = sec["items"]
        pdf.add_section(name, [f"本模块共汇总 {len(items)} 条结果。"])
        rows = []
        for idx, it in enumerate(items, 1):
            title = str(it.get("title") or it.get("名称", ""))
            link = str(it.get("link") or it.get("原文链接", ""))
            date = str(it.get("date", ""))
            rows.append([str(idx), title, date, link])
        pdf.add_table(["#", "标题", "日期", "链接"], rows,
                      col_widths=[0.05, 0.40, 0.15, 0.40], font_size=8)

    pdf.output(filepath)
    return filepath
