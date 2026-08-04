"""Page 2: Brokerage research reports from East Money."""

from PyQt5.QtWidgets import QLabel, QComboBox, QDateEdit, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QDate, QThread, pyqtSignal

from .base_page import BasePage
from fetchers.brokerage import BrokerageFetcher, MOCK_BROKERAGE_DATA


class _FetchThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list, bool)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        self.progress.emit("正在抓取券商研报...")
        fetcher = BrokerageFetcher()
        data, is_mock = fetcher.fetch(**self.params)
        self.finished.emit(data, is_mock)


class BrokeragePage(BasePage):
    """Page for brokerage research reports."""

    EXTRA_FIELDS = {
        "analyst": "分析师",
        "rating": "评级",
        "supply_chain": "产业链图谱",
        "industry": "所属行业",
    }

    def __init__(self, parent=None):
        super().__init__("券商研报（东方财富）", "brokerage", parent)
        self.report_title = "券商研报汇总"
        self.report_subtitle = "东方财富网 · 行业深度研究报告"
        self.mock_note = "注意：以下为示例数据，非实时抓取结果。"

    def get_all_fields(self):
        fields = dict(self.COMMON_FIELDS)
        fields.update(self.EXTRA_FIELDS)
        return fields

    def get_sample_data(self):
        return list(MOCK_BROKERAGE_DATA)

    def build_ui(self):
        super().build_ui()
        self._build_constraints()
        self.action_btn.setText("抓取并生成报告")

    def _build_constraints(self):
        # Industry
        self.industry_combo = QComboBox()
        self.industry_combo.addItems(["全部", "电子", "医药", "新能源", "消费", "汽车", "化工", "计算机"])
        self.add_constraint_row("行业选择：", self.industry_combo)

        # Rating
        self.rating_combo = QComboBox()
        self.rating_combo.addItems(["全部", "买入", "增持", "中性", "减持", "卖出"])
        self.add_constraint_row("评级筛选：", self.rating_combo)

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
        self.kw_input = QLineEdit()
        self.kw_input.setPlaceholderText("多个关键词用逗号分隔，如：半导体, AI, 新能源")
        self.add_constraint_row("关键词过滤：", self.kw_input)

    def on_action_clicked(self):
        if not self._validate_output_dir():
            return

        params = {
            "industry": self.industry_combo.currentText(),
            "rating": self.rating_combo.currentText(),
            "start_date": self.date_start.date().toString("yyyy-MM-dd"),
            "end_date": self.date_end.date().toString("yyyy-MM-dd"),
            "keywords": self.kw_input.text().strip(),
        }

        self.action_btn.setEnabled(False)
        self.set_progress("正在抓取券商研报...")

        self.thread = _FetchThread(params)
        self.thread.progress.connect(self.set_progress)
        self.thread.finished.connect(lambda data, mock: self.generate_report(data, mock))
        self.thread.start()

