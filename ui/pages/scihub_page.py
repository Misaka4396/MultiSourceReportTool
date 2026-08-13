"""Page 6: Sci-Hub / DOI downloader."""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel, QTextEdit

from fetchers.scihub import MOCK_DOI_DATA, SciHubFetcher

from .base_page import BasePage


class _FetchThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, doi_list):
        super().__init__()
        self.doi_list = doi_list

    def run(self):
        self.progress.emit("正在查询DOI元数据...")
        fetcher = SciHubFetcher()
        data = fetcher.fetch(self.doi_list)
        self.finished.emit(data)


class SciHubPage(BasePage):
    """Page for Sci-Hub / DOI metadata retrieval."""

    EXTRA_FIELDS = {
        "doi": "DOI",
        "journal": "期刊",
        "year": "出版年",
        "publisher": "出版社",
        "download_status": "下载状态",
        "mirror_hint": "镜像提示",
    }

    def __init__(self, parent=None):
        super().__init__("Sci-Hub 文献下载器", "scihub", parent)
        self.report_title = "文献信息检索报告"
        self.report_subtitle = "DOI Metadata Lookup via Crossref API"
        self.mock_note = "注意：部分DOI查询返回示例数据。"
        self.extra_result_msg = (
            "\n\n提示：可通过 Sci-Hub 镜像获取全文。常用域名：sci-hub.se, sci-hub.st, sci-hub.ru"
        )

    def get_all_fields(self):
        fields = dict(self.COMMON_FIELDS)
        fields.update(self.EXTRA_FIELDS)
        return fields

    def get_sample_data(self):
        return [dict(data) for data in MOCK_DOI_DATA.values()]

    def build_ui(self):
        super().build_ui()
        self._build_constraints()
        self.action_btn.setText("获取文献信息并准备报告")

    def _build_constraints(self):
        # DOI input
        doi_label = QLabel("DOI 号输入（每行一个）：")
        self.constraints_layout.addWidget(doi_label)

        self.doi_input = QTextEdit()
        self.doi_input.setPlaceholderText(
            "请输入DOI号，每行一个，例如：\n"
            "10.1038/nature12373\n"
            "10.1126/science.aad0919\n"
            "10.1016/j.cell.2020.02.007"
        )
        self.doi_input.setMinimumHeight(120)
        self.constraints_layout.addWidget(self.doi_input)

        # Legal notice
        notice = QLabel(
            "法律声明：本工具使用Crossref公开API获取文献元数据。"
            "实际PDF下载需用户自行通过合法渠道（机构订阅、开放获取等）获取。"
            "本工具不存储或分发受版权保护的文献全文。"
        )
        notice.setStyleSheet(
            "color: #5A5A5A; font-size: 11px; padding-top: 8px; background: transparent;"
        )
        notice.setWordWrap(True)
        self.constraints_layout.addWidget(notice)

    def on_action_clicked(self):
        if not self._validate_output_dir():
            return

        doi_text = self.doi_input.toPlainText().strip()
        if not doi_text:
            self.show_result_dialog(False, "请输入至少一个DOI号。")
            return

        doi_list = [d.strip() for d in doi_text.split("\n") if d.strip()]

        self.action_btn.setEnabled(False)
        self.set_progress(f"正在查询{len(doi_list)}个DOI的元数据...")

        self.thread = _FetchThread(doi_list)
        self.thread.progress.connect(self.set_progress)
        self.thread.finished.connect(
            lambda data: self.generate_report(data, any(r.get("is_mock", False) for r in data))
        )
        self.thread.start()
