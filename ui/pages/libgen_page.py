"""Page 7: Library Genesis book search."""

from PyQt5.QtWidgets import (
    QLabel, QComboBox, QLineEdit, QCheckBox, QHBoxLayout,
)
from PyQt5.QtCore import QThread, pyqtSignal

from .base_page import BasePage
from fetchers.libgen import LibGenFetcher, MOCK_BOOK_DATA


class _FetchThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list, bool)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        self.progress.emit("正在搜索电子书...")
        fetcher = LibGenFetcher()
        data, is_mock = fetcher.fetch(**self.params)
        self.finished.emit(data, is_mock)


class LibGenPage(BasePage):
    """Page for Library Genesis book search."""

    EXTRA_FIELDS = {
        "publisher": "出版社",
        "year": "出版年份",
        "isbn": "ISBN",
        "size": "文件大小",
        "mirrors": "下载镜像",
        "description": "内容简介",
    }

    def __init__(self, parent=None):
        super().__init__("Library Genesis 电子书搜索", "libgen", parent)
        self.report_title = "电子书搜索报告"
        self.report_subtitle = "Library Genesis · Book Search Results"
        self.mock_note = "注意：搜索结果为模拟示例，实际下载请访问 Library Genesis 镜像站。"
        self.extra_result_msg = "\n\n提示：可通过 libgen.is, libgen.st, libgen.rs 等镜像站点下载。"

    def get_all_fields(self):
        fields = dict(self.COMMON_FIELDS)
        fields.update(self.EXTRA_FIELDS)
        return fields

    def get_sample_data(self):
        return list(MOCK_BOOK_DATA)

    def build_ui(self):
        super().build_ui()
        self._build_constraints()
        self.action_btn.setText("搜索书籍并生成报告")

    def _build_constraints(self):
        # Search type
        self.search_type = QComboBox()
        self.search_type.addItems(["书名 (Title)", "作者 (Author)", "ISBN"])
        self.add_constraint_row("搜索方式：", self.search_type)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入书名、作者名或ISBN号...")
        self.add_constraint_row("搜索内容：", self.search_input)

        # Language
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["全部", "English", "中文", "Deutsch", "Français", "日本語"])
        self.add_constraint_row("书籍语言：", self.lang_combo)

        # File formats
        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("文件格式："))
        self.cb_pdf = QCheckBox("PDF")
        self.cb_pdf.setChecked(True)
        self.cb_epub = QCheckBox("EPUB")
        self.cb_epub.setChecked(True)
        self.cb_mobi = QCheckBox("MOBI")
        self.cb_mobi.setChecked(True)
        fmt_row.addWidget(self.cb_pdf)
        fmt_row.addWidget(self.cb_epub)
        fmt_row.addWidget(self.cb_mobi)
        fmt_row.addStretch()
        self.constraints_layout.addLayout(fmt_row)

        # Notice
        notice = QLabel(
            "说明：电子书搜索结果为模拟示例。实际下载请访问 Library Genesis 镜像站点"
            "（如 libgen.is, libgen.st, libgen.rs）。\n"
            "请遵守当地版权法规，仅下载您有权获取的内容。"
        )
        notice.setStyleSheet("color: #5A5A5A; font-size: 11px; padding-top: 8px; background: transparent;")
        notice.setWordWrap(True)
        self.constraints_layout.addWidget(notice)

    def on_action_clicked(self):
        if not self._validate_output_dir():
            return

        search_type = self.search_type.currentText()
        title = self.search_input.text().strip() if "书名" in search_type else ""
        author = self.search_input.text().strip() if "作者" in search_type else ""
        isbn = self.search_input.text().strip() if "ISBN" in search_type else ""

        if not title and not author and not isbn:
            self.show_result_dialog(False, "请输入搜索内容（书名、作者或ISBN）。")
            return

        formats = []
        if self.cb_pdf.isChecked():
            formats.append("pdf")
        if self.cb_epub.isChecked():
            formats.append("epub")
        if self.cb_mobi.isChecked():
            formats.append("mobi")

        language = self.lang_combo.currentText()

        params = {
            "title": title,
            "author": author,
            "isbn": isbn,
            "language": language,
            "formats": formats,
        }

        self.action_btn.setEnabled(False)
        self.set_progress("正在搜索电子书...")

        self.thread = _FetchThread(params)
        self.thread.progress.connect(self.set_progress)
        self.thread.finished.connect(lambda data, mock: self.generate_report(data, mock))
        self.thread.start()

