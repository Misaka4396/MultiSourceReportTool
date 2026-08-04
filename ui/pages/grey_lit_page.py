"""Page 4: Grey literature search."""

from PyQt5.QtWidgets import (
    QLabel, QComboBox, QDateEdit, QLineEdit, QCheckBox, QHBoxLayout,
)
from PyQt5.QtCore import QDate, QThread, pyqtSignal

from .base_page import BasePage
from fetchers.grey_lit import GreyLiteratureFetcher, MOCK_GREY_DATA


class _FetchThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list, bool)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        self.progress.emit("正在搜索灰色文献...")
        fetcher = GreyLiteratureFetcher()
        data, is_mock = fetcher.fetch(**self.params)
        self.finished.emit(data, is_mock)


class GreyLitPage(BasePage):
    """Page for grey literature search."""

    EXTRA_FIELDS = {
        "organization": "出版机构",
        "file_type": "文件类型",
    }

    def __init__(self, parent=None):
        super().__init__("灰色文献抓取", "greylit", parent)
        self.report_title = "灰色文献搜索报告"
        self.report_subtitle = "World Bank · RAND Corporation · Working Papers"
        self.mock_note = "注意：以下为示例数据，非实时抓取结果。"

    def get_all_fields(self):
        fields = dict(self.COMMON_FIELDS)
        fields.update(self.EXTRA_FIELDS)
        return fields

    def get_sample_data(self):
        return list(MOCK_GREY_DATA)

    def build_ui(self):
        super().build_ui()
        self._build_constraints()
        self.action_btn.setText("搜索并生成报告")

    def _build_constraints(self):
        # Keywords
        self.kw_input = QLineEdit()
        self.kw_input.setPlaceholderText("输入搜索关键词，如：climate adaptation, trade policy")
        self.add_constraint_row("关键词：", self.kw_input)

        # Domain checkboxes
        domain_row = QHBoxLayout()
        domain_row.addWidget(QLabel("来源域名："))
        self.cb_worldbank = QCheckBox("worldbank.org")
        self.cb_worldbank.setChecked(True)
        self.cb_rand = QCheckBox("rand.org")
        self.cb_rand.setChecked(True)
        domain_row.addWidget(self.cb_worldbank)
        domain_row.addWidget(self.cb_rand)

        self.custom_domain = QLineEdit()
        self.custom_domain.setPlaceholderText("自定义域名（可选，如：oecd.org）")
        domain_row.addWidget(self.custom_domain)
        domain_row.addStretch()
        self.constraints_layout.addLayout(domain_row)

        # File type
        ft_row = QHBoxLayout()
        ft_row.addWidget(QLabel("文件类型："))
        self.cb_pdf = QCheckBox("PDF")
        self.cb_pdf.setChecked(True)
        self.cb_docx = QCheckBox("DOCX")
        ft_row.addWidget(self.cb_pdf)
        ft_row.addWidget(self.cb_docx)
        ft_row.addStretch()
        self.constraints_layout.addLayout(ft_row)

        # Date range
        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("时间范围："))
        self.date_start = QDateEdit()
        self.date_start.setDate(QDate(2024, 1, 1))
        self.date_start.setCalendarPopup(True)
        date_row.addWidget(self.date_start)
        date_row.addWidget(QLabel(" 至 "))
        self.date_end = QDateEdit()
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setCalendarPopup(True)
        date_row.addWidget(self.date_end)
        date_row.addStretch()
        self.constraints_layout.addLayout(date_row)

    def on_action_clicked(self):
        if not self._validate_output_dir():
            return

        selected_domains = []
        if self.cb_worldbank.isChecked():
            selected_domains.append("worldbank.org")
        if self.cb_rand.isChecked():
            selected_domains.append("rand.org")
        custom = self.custom_domain.text().strip()
        if custom:
            selected_domains.append(custom)

        if not selected_domains:
            self.show_result_dialog(False, "请至少选择一个来源域名。")
            return

        file_types = []
        if self.cb_pdf.isChecked():
            file_types.append("pdf")
        if self.cb_docx.isChecked():
            file_types.append("docx")

        params = {
            "keywords": self.kw_input.text().strip(),
            "domains": selected_domains,
            "file_types": file_types,
            "start_date": self.date_start.date().toString("yyyy-MM-dd"),
            "end_date": self.date_end.date().toString("yyyy-MM-dd"),
        }

        self.action_btn.setEnabled(False)
        self.set_progress("正在搜索灰色文献...")

        self.thread = _FetchThread(params)
        self.thread.progress.connect(self.set_progress)
        self.thread.finished.connect(lambda data, mock: self.generate_report(data, mock))
        self.thread.start()

