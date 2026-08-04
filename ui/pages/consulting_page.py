"""Page 1: Top consulting firm reports."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QComboBox, QDateEdit, QLineEdit, QRadioButton, QButtonGroup,
)
from PyQt5.QtCore import QDate, QThread, pyqtSignal

from .base_page import BasePage
from fetchers.consulting import ConsultingFetcher, MOCK_CONSULTING_DATA


class _FetchThread(QThread):
    """Worker thread for fetching data."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list, bool)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        self.progress.emit("正在抓取咨询公司报告...")
        fetcher = ConsultingFetcher()
        data, is_mock = fetcher.fetch(**self.params)
        self.finished.emit(data, is_mock)


class ConsultingPage(BasePage):
    """Page for consulting firm report aggregation."""

    EXTRA_FIELDS = {
        "source": "来源机构",
    }

    def __init__(self, parent=None):
        super().__init__("顶级咨询公司报告", "consulting", parent)
        self.report_title = "顶级咨询公司报告汇总"
        self.report_subtitle = "McKinsey · BCG · Roland Berger · Accenture"
        self.mock_note = "注意：以下为示例数据，非实时抓取结果。"
        self.extra_result_msg = ""

    def get_all_fields(self):
        fields = dict(self.COMMON_FIELDS)
        fields.update(self.EXTRA_FIELDS)
        return fields

    def get_sample_data(self):
        results = []
        for firm_data in MOCK_CONSULTING_DATA.values():
            results.extend(firm_data)
        return results

    def build_ui(self):
        super().build_ui()
        self._build_constraints()
        self.action_btn.setText("抓取并生成报告")

    def _build_constraints(self):
        # Company selection
        companies = [("mckinsey", "McKinsey 麦肯锡"), ("bcg", "BCG 波士顿咨询"),
                     ("roland_berger", "Roland Berger 罗兰贝格"), ("accenture", "Accenture 埃森哲")]
        self.firm_checkboxes = {}
        firm_row = QHBoxLayout()
        firm_row.addWidget(QLabel("选择公司："))
        for key, label in companies:
            cb = QCheckBox(label)
            cb.setChecked(True)
            self.firm_checkboxes[key] = cb
            firm_row.addWidget(cb)
        firm_row.addStretch()
        self.constraints_layout.addLayout(firm_row)

        # Language
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["中文", "English"])
        self.add_constraint_row("语言选择：", self.lang_combo)

        # Date range
        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("发布时间范围："))
        self.date_start = QDateEdit()
        self.date_start.setDate(QDate.currentDate().addMonths(-6))
        self.date_start.setCalendarPopup(True)
        date_row.addWidget(self.date_start)
        date_row.addWidget(QLabel(" 至 "))
        self.date_end = QDateEdit()
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setCalendarPopup(True)
        date_row.addWidget(self.date_end)
        date_row.addStretch()
        self.constraints_layout.addLayout(date_row)

        # Keywords
        kw_row = QHBoxLayout()
        kw_row.addWidget(QLabel("关键词过滤："))
        self.kw_input = QLineEdit()
        self.kw_input.setPlaceholderText("多个关键词用逗号分隔，如：AI, digital, energy")
        kw_row.addWidget(self.kw_input)
        self.rb_and = QRadioButton("AND")
        self.rb_or = QRadioButton("OR")
        self.rb_or.setChecked(True)
        kw_row.addWidget(self.rb_and)
        kw_row.addWidget(self.rb_or)
        kw_row.addStretch()
        self.constraints_layout.addLayout(kw_row)

    def on_action_clicked(self):
        if not self._validate_output_dir():
            return

        firms = [k for k, cb in self.firm_checkboxes.items() if cb.isChecked()]
        if not firms:
            self.show_result_dialog(False, "请至少选择一家咨询公司。")
            return

        params = {
            "firms": firms,
            "language": self.lang_combo.currentText(),
            "start_date": self.date_start.date().toString("yyyy-MM-dd"),
            "end_date": self.date_end.date().toString("yyyy-MM-dd"),
            "keywords": self.kw_input.text().strip(),
            "keyword_logic": "AND" if self.rb_and.isChecked() else "OR",
        }

        self.action_btn.setEnabled(False)
        self.set_progress("正在抓取咨询公司报告...")

        self.thread = _FetchThread(params)
        self.thread.progress.connect(self.set_progress)
        self.thread.finished.connect(lambda data, mock: self.generate_report(data, mock))
        self.thread.start()

