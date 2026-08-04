"""Page 5: Preprint platform search (arXiv, SSRN)."""

from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QCheckBox, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal

from .base_page import BasePage
from fetchers.preprint import PreprintFetcher, MOCK_PREPRINT_DATA


class _FetchThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list, bool)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        self.progress.emit("正在检索预印本...")
        fetcher = PreprintFetcher()
        data, is_mock = fetcher.fetch(**self.params)
        self.finished.emit(data, is_mock)


class PreprintPage(BasePage):
    """Page for preprint platform search."""

    EXTRA_FIELDS = {
        "source": "来源平台",
        "category": "学科分类",
    }

    def __init__(self, parent=None):
        super().__init__("预印本平台检索", "preprint", parent)
        self.report_title = "预印本检索报告"
        self.report_subtitle = "arXiv · SSRN · Preprint Search"
        self.mock_note = "注意：部分结果为示例数据。"

    def get_all_fields(self):
        fields = dict(self.COMMON_FIELDS)
        fields.update(self.EXTRA_FIELDS)
        return fields

    def get_sample_data(self):
        return list(MOCK_PREPRINT_DATA)

    def build_ui(self):
        super().build_ui()
        self._build_constraints()
        self.action_btn.setText("检索预印本并生成报告")

    def _build_constraints(self):
        # Source selection
        src_row = QHBoxLayout()
        src_row.addWidget(QLabel("预印本来源："))
        self.cb_arxiv = QCheckBox("arXiv")
        self.cb_arxiv.setChecked(True)
        self.cb_ssrn = QCheckBox("SSRN")
        self.cb_ssrn.setChecked(True)
        src_row.addWidget(self.cb_arxiv)
        src_row.addWidget(self.cb_ssrn)
        src_row.addStretch()
        self.constraints_layout.addLayout(src_row)

        # Category
        self.cat_combo = QComboBox()
        self.cat_combo.addItems([
            "全部", "计算机科学", "经济学", "物理学", "数学", "生物学", "统计学",
            "金融学", "电子工程", "化学", "材料科学",
        ])
        self.add_constraint_row("学科分类：", self.cat_combo)

        # Keywords
        self.kw_input = QLineEdit()
        self.kw_input.setPlaceholderText("输入搜索关键词，如：large language model, diffusion")
        self.add_constraint_row("关键词：", self.kw_input)

        # Time preset
        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("时间限定："))
        self.time_combo = QComboBox()
        self.time_combo.addItems([
            "since 2026", "2025-2026", "2024-2026", "2020-2026", "不限时间"
        ])
        time_row.addWidget(self.time_combo)
        time_row.addStretch()
        self.constraints_layout.addLayout(time_row)

    def on_action_clicked(self):
        if not self._validate_output_dir():
            return

        sources = []
        if self.cb_arxiv.isChecked():
            sources.append("arXiv")
        if self.cb_ssrn.isChecked():
            sources.append("SSRN")

        if not sources:
            self.show_result_dialog(False, "请至少选择一个预印本来源。")
            return

        params = {
            "sources": sources,
            "category": self.cat_combo.currentText(),
            "keywords": self.kw_input.text().strip(),
            "max_results": 20,
        }

        self.action_btn.setEnabled(False)
        self.set_progress("正在检索预印本...")

        self.thread = _FetchThread(params)
        self.thread.progress.connect(self.set_progress)
        self.thread.finished.connect(lambda data, mock: self.generate_report(data, mock))
        self.thread.start()

