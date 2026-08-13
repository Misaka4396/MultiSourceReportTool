"""P8 单元测试 — 纯函数：文件名净化 / 文本分段 / 换行算法 / PDF 内容。

覆盖规范：AAA 结构、Given-When-Then 语义命名、边界值、确定性。
"""

from article_grab.grabber import _safe_name
from article_grab.pdf_daily import DailyPDF, _segments


class TestSafeName:
    """文件名净化（P1.6 安全基线：防路径穿越）。"""

    def test_illegal_chars_replaced(self):
        """Given 含非法字符文件名 → When 净化 → Then 全部替换为下划线。"""
        assert _safe_name('a/b:c*d?<"e>|f') == "a_b_c_d___e__f"

    def test_windows_reserved_illegal(self):
        """Windows 保留字符（<>:"|?*）必须被替换。"""
        for ch in '<>:"|?*':
            assert ch not in _safe_name(f"x{ch}y")

    def test_long_input_truncated_to_limit(self):
        """Given 超长输入 → When 净化 → Then 截断至 60 字符。"""
        assert len(_safe_name("x" * 200)) == 60

    def test_empty_input_fallback(self):
        """Given 空/空白输入 → When 净化 → Then 回退为 'article'。"""
        assert _safe_name("") == "article"
        assert _safe_name("   ") == "article"

    def test_path_traversal_attempt_neutralized(self):
        """Given 路径穿越尝试 ../.. → When 净化 → Then 斜杠被替换。"""
        out = _safe_name("../../etc/passwd")
        assert "/" not in out and "\\" not in out


class TestSegments:
    """文本分段（中英混排换行的基础）。"""

    def test_cjk_chars_are_single_units(self):
        """Given 中文字符串 → Then 每个中文字符独立成段。"""
        assert _segments("中文") == ["中", "文"]

    def test_ascii_runs_are_kept_together(self):
        """Given 连续 ASCII → Then 合并为一个段。"""
        assert _segments("hello") == ["hello"]

    def test_mixed_cjk_ascii(self):
        """Given 中英混排 → Then 按语言边界切分。"""
        assert _segments("中abc文") == ["中", "abc", "文"]

    def test_punctuation_and_space(self):
        """Given 空格+ASCII → Then 归入同一 ASCII 段（由换行算法处理空格）。"""
        assert _segments("a b") == ["a b"]


class TestWrapText:
    """PDF 换行算法（防文字挤压的核心，P1 质量要点）。"""

    def setup_method(self):
        self.pdf = DailyPDF("测试日报")
        self.pdf.set_font(self.pdf.font_name, "", 11)  # get_string_width 前必须 set_font

    def test_short_text_single_line(self):
        """Given 短文本 → When 换行 → Then 保持单行。"""
        lines = self.pdf._wrap_text("短文", 100)
        assert len(lines) == 1

    def test_wrap_breaks_on_width(self):
        """Given 超宽文本 → When 换行 → Then 每行宽度不超限。"""
        text = "这是一段用于测试换行的中文文本" * 20
        lines = self.pdf._wrap_text(text, 80)
        assert len(lines) > 1
        for ln in lines:
            assert self.pdf.get_string_width(ln) <= 80

    def test_long_url_hard_breaks_char_by_char(self):
        """Given 超长无空格 URL → When 换行 → Then 逐字符硬断且不超宽。"""
        url = "https://example.com/" + "x" * 500
        lines = self.pdf._wrap_text(url, 60)
        assert len(lines) > 1
        for ln in lines:
            assert self.pdf.get_string_width(ln) <= 60

    def test_empty_text_returns_blank_line(self):
        """Given 空文本 → When 换行 → Then 返回单空行。"""
        assert self.pdf._wrap_text("", 100) == [""]

    def test_mixed_content_no_line_overflow(self):
        """Given 中英混排+URL → When 换行 → Then 无任何行溢出。"""
        text = "中文段落 mixed English words " + "https://x.com/" + "y" * 300 + " 结尾"
        for ln in self.pdf._wrap_text(text, 80):
            assert self.pdf.get_string_width(ln) <= 80
