"""PDF report generator with academic formatting using fpdf2."""

import os
import sys
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos


def _find_chinese_font() -> str:
    """Find a usable Chinese font file on the system or in resources."""
    candidates = [
        # Windows fonts
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
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


class AcademicPDF(FPDF):
    """Custom PDF with academic report formatting."""

    def __init__(self, title: str, subtitle: str = "", dual_column: bool = False):
        super().__init__("P", "mm", "A4")
        self.report_title = title
        self.report_subtitle = subtitle
        self.dual_column = dual_column
        self.font_name = "Helvetica"
        self.font_size = 11
        self.line_height_factor = 1.5
        self.toc_entries: list[tuple[str, int, int]] = []  # (title, page, level)
        self.in_toc = False
        self.in_cover = False
        self.section_number = 0
        self._col_width = 0
        self._col_x_left = 0
        self._col_x_right = 0

        # Try to load Chinese font
        font_path = _find_chinese_font()
        if font_path:
            try:
                self.add_font("CJK", "", font_path, uni=True)
                self.add_font("CJK", "B", font_path, uni=True)
                self.add_font("CJK", "I", font_path, uni=True)
                self.add_font("CJK", "BI", font_path, uni=True)
                self.font_name = "CJK"
            except Exception:
                pass

        self.set_auto_page_break(True, 20)

    def header(self):
        if self.in_cover or self.in_toc:
            return
        if self.page_no() == 1:
            return
        self.set_font(self.font_name, "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, self.report_title, align="C")
        self.ln(8)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        if self.in_cover:
            return
        self.set_y(-15)
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
        self.set_font(self.font_name, "", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"{self.page_no()}  |  多源报告汇总工具生成", align="C")

    def line_height(self) -> float:
        return self.font_size * self.line_height_factor * 0.3528  # pt to mm

    def render_cover(self, date_str: str = ""):
        """Render the cover page."""
        self.in_cover = True
        self.add_page()
        page_h = self.h
        center_y = page_h / 2

        # Top decorative line
        self.set_fill_color(59, 130, 246)
        self.rect(0, 0, self.w, 4, "F")

        # Logo placeholder
        self.set_y(25)
        self.set_font(self.font_name, "B", 28)
        self.set_text_color(30, 41, 59)
        self.cell(0, 14, "多源报告汇总推送工具", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font(self.font_name, "", 11)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, "Multi-Source Report Aggregation Tool", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)

        # Separator
        self.set_draw_color(59, 130, 246)
        self.set_line_width(0.5)
        mid_x = self.w / 2
        self.line(mid_x - 30, self.get_y(), mid_x + 30, self.get_y())
        self.ln(10)

        # Report title
        self.set_font(self.font_name, "B", 22)
        self.set_text_color(30, 41, 59)
        # Word wrap the title
        self.multi_cell(0, 12, self.report_title, align="C")
        self.ln(4)

        if self.report_subtitle:
            self.set_font(self.font_name, "", 13)
            self.set_text_color(71, 85, 105)
            self.cell(0, 8, self.report_subtitle, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(6)

        self.ln(8)

        # Date
        self.set_font(self.font_name, "", 12)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, f"生成日期：{date_str or datetime.now().strftime('%Y-%m-%d')}", align="C",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)

        # Logo placeholder box
        self.set_draw_color(59, 130, 246)
        self.set_line_width(0.3)
        box_w = 60
        box_h = 40
        box_x = (self.w - box_w) / 2
        self.rect(box_x, self.get_y(), box_w, box_h, "D")
        self.set_font(self.font_name, "", 9)
        self.set_text_color(148, 163, 184)
        self.set_y(self.get_y() + box_h / 2 - 4)
        self.cell(0, 8, "[ LOGO ]", align="C")

        # Bottom decorative line
        self.rect(0, page_h - 4, self.w, 4, "F")

        self.in_cover = False

    def render_toc(self):
        """Render table of contents page."""
        if not self.toc_entries:
            return

        self.in_toc = True
        self.add_page()

        self.set_font(self.font_name, "B", 18)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, "目  录", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(8)

        for title, page, level in self.toc_entries:
            indent = level * 8
            self.set_x(self.l_margin + indent)
            self.set_font(self.font_name, "B" if level == 0 else "", 11)
            self.set_text_color(51, 65, 85)

            # Title with dot leaders
            title_width = self.w - self.l_margin - self.r_margin - indent - 15
            # Truncate title if too long
            while self.get_string_width(title) > title_width and len(title) > 3:
                title = title[:-4] + "..."

            dots = ""
            dot_width = self.get_string_width(".")
            remaining = title_width - self.get_string_width(title)
            if remaining > dot_width:
                dots = "." * int(remaining / dot_width)

            self.cell(title_width, 8, f"{title} {dots} {page}", align="L",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.in_toc = False

    def add_section(self, title: str, content_lines: list[str], level: int = 0):
        """Add a numbered section to the report."""
        self.section_number += 1
        sec_label = f"§{self.section_number}"

        # Record TOC entry
        self.toc_entries.append((f"{sec_label} {title}", self.page_no() + 1, level))

        # Check if we need a new page
        if self.get_y() > self.h - 40:
            self.add_page()

        # Section heading
        self.set_font(self.font_name, "B", 14 if level == 0 else 12)
        self.set_text_color(30, 41, 59)
        heading = f"{sec_label}  {title}"
        self.cell(0, self.line_height() + 2, heading, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

        # Content
        self.set_font(self.font_name, "", self.font_size)
        self.set_text_color(51, 65, 85)
        lh = self.line_height()

        for line in content_lines:
            if not line:
                self.ln(lh)
                continue
            if self.get_y() > self.h - 25:
                self.add_page()
            self.multi_cell(0, lh, line, align="L")
            self.ln(1)

        self.ln(4)

    def add_references(self, refs: list[str]):
        """Add a references section."""
        self.add_page()
        self.set_font(self.font_name, "B", 16)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, "参考文献", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)

        self.set_font(self.font_name, "", 10)
        self.set_text_color(51, 65, 85)
        for i, ref in enumerate(refs, 1):
            self.multi_cell(0, 6, f"[{i}] {ref}")
            self.ln(1)


def generate_pdf_report(
    title: str,
    subtitle: str,
    data: list[dict],
    output_dir: str,
    selected_fields: list[str],
    field_labels: dict[str, str],
    dual_column: bool = False,
) -> str:
    """Generate an academic-style PDF report.

    Args:
        title: Report title
        subtitle: Report subtitle
        data: List of result dicts, each becomes a section
        output_dir: Directory to save the file
        selected_fields: List of field keys to include
        field_labels: Mapping of field keys to display labels
        dual_column: Whether to use two-column layout

    Returns:
        Path to the generated file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title.replace(' ', '_')}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    pdf = AcademicPDF(title=title, subtitle=subtitle, dual_column=dual_column)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_top_margin(20)

    date_str = datetime.now().strftime("%Y-%m-%d")
    pdf.render_cover(date_str)

    # Collect references
    references = []

    # Build section content from data
    for item in data:
        sec_title = item.get("title", item.get("名称", "Untitled"))
        content = []
        for field in selected_fields:
            if field in item and item[field]:
                label = field_labels.get(field, field)
                value = item[field]
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value)
                content.append(f"{label}：{value}")

        pdf.add_section(sec_title, content)

        # Collect reference info
        if "link" in item and item["link"]:
            references.append(f"{item.get('title', '')} — {item['link']}")
        elif "原文链接" in item and item["原文链接"]:
            references.append(f"{item.get('title', item.get('名称', ''))} — {item['原文链接']}")

    # Render TOC (after body so page numbers are known, or use placeholder pages)
    # We rebuild the PDF since fpdf2 doesn't support two-pass
    # Workaround: create a new PDF with cover + TOC + body
    final_pdf = AcademicPDF(title=title, subtitle=subtitle, dual_column=dual_column)
    final_pdf.set_left_margin(20)
    final_pdf.set_right_margin(20)
    final_pdf.set_top_margin(20)
    final_pdf.toc_entries = []

    final_pdf.render_cover(date_str)

    for item in data:
        sec_title = item.get("title", item.get("名称", "Untitled"))
        final_pdf.toc_entries.append((sec_title, 0, 0))

    final_pdf.render_toc()

    # Now render all sections
    for item in data:
        sec_title = item.get("title", item.get("名称", "Untitled"))
        content = []
        for field in selected_fields:
            if field in item and item[field]:
                label = field_labels.get(field, field)
                value = item[field]
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value)
                content.append(f"{label}：{value}")
        final_pdf.section_number += 1 if final_pdf.section_number < len(data) else 0
        final_pdf.add_section(sec_title, content)

    if references:
        final_pdf.add_references(references)

    # Write the final PDF
    final_pdf.output(filepath)

    return filepath
