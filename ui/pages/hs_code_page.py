"""Page 3: HS Code trade data tracker."""

from PyQt5.QtWidgets import QLabel, QComboBox, QDateEdit, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QDate, QThread, pyqtSignal

from .base_page import BasePage
from fetchers.hs_code import HSCodeFetcher, MOCK_TRADE_DATA


class _FetchThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list, bool)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        self.progress.emit("正在查询贸易数据...")
        fetcher = HSCodeFetcher()
        data, is_mock = fetcher.fetch(**self.params)
        self.finished.emit(data, is_mock)


class HSCodePage(BasePage):
    """Page for HS code trade data tracking."""

    EXTRA_FIELDS = {
        "hs_code": "HS编码",
        "country": "国家/地区",
        "trade_type": "贸易类型",
        "trade_value": "贸易额(美元)",
        "quantity": "数量",
        "yoy_change": "同比变化",
        "top_partners": "前十贸易伙伴",
        "flow_desc": "供应链流向描述",
    }

    def __init__(self, parent=None):
        super().__init__("海关编码查询工具", "hscode", parent)
        self.report_title = "海关编码贸易数据查询报告"
        self.report_subtitle = "HS Code Trade Data Report"
        self.mock_note = "注意：贸易数据为模拟示例，实际数据请查询UN Comtrade数据库。"

    def get_all_fields(self):
        fields = dict(self.COMMON_FIELDS)
        fields.update(self.EXTRA_FIELDS)
        return fields

    def get_sample_data(self):
        return list(MOCK_TRADE_DATA)

    def build_ui(self):
        super().build_ui()
        self._build_constraints()
        self.action_btn.setText("查询贸易数据并生成报告")

    def _build_constraints(self):
        # Country
        self.country_combo = QComboBox()
        self.country_combo.addItems([
            "中国 (China)", "美国 (USA)", "德国 (Germany)",
            "越南 (Vietnam)", "印度 (India)", "日本 (Japan)",
            "韩国 (Korea)", "马来西亚 (Malaysia)",
        ])
        self.add_constraint_row("选择国家：", self.country_combo)

        # HS code query
        self.hs_input = QLineEdit()
        self.hs_input.setPlaceholderText("输入HS编码或关键词，如：8542, 半导体, 集成电路")
        self.add_constraint_row("HS编码/关键词：", self.hs_input)

        # Trade type
        self.trade_combo = QComboBox()
        self.trade_combo.addItems(["进口 (Import)", "出口 (Export)", "双边贸易 (Bilateral)"])
        self.add_constraint_row("贸易类型：", self.trade_combo)

        # Date range
        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("时间范围："))
        self.date_start = QDateEdit()
        self.date_start.setDate(QDate.currentDate().addYears(-1))
        self.date_start.setCalendarPopup(True)
        date_row.addWidget(self.date_start)
        date_row.addWidget(QLabel(" 至 "))
        self.date_end = QDateEdit()
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setCalendarPopup(True)
        date_row.addWidget(self.date_end)
        date_row.addStretch()
        self.constraints_layout.addLayout(date_row)

        # Note about data source
        note = QLabel("注意：贸易数据为示例数据，基于UN Comtrade公开统计口径模拟。实际精确数据需通过官方API获取。")
        note.setStyleSheet("color: #94a3b8; font-size: 11px; padding-top: 4px;")
        note.setWordWrap(True)
        self.constraints_layout.addWidget(note)

    def on_action_clicked(self):
        if not self._validate_output_dir():
            return

        params = {
            "country": self.country_combo.currentText(),
            "hs_query": self.hs_input.text().strip(),
            "trade_type": self.trade_combo.currentText(),
            "start_date": self.date_start.date().toString("yyyy-MM-dd"),
            "end_date": self.date_end.date().toString("yyyy-MM-dd"),
        }

        self.action_btn.setEnabled(False)
        self.set_progress("正在查询贸易数据...")

        self.thread = _FetchThread(params)
        self.thread.progress.connect(self.set_progress)
        self.thread.finished.connect(lambda data, mock: self.generate_report(data, mock))
        self.thread.start()

