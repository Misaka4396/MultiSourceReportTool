"""Local daily report generation service.

Schedules a daily digest: at the configured time the selected source modules
are fetched in a background thread and a TXT + PDF report is written to the
configured output directory.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from PyQt5.QtCore import QObject, QThread, QTime, QTimer, pyqtSignal

from fetchers.brokerage import BrokerageFetcher
from fetchers.consulting import ConsultingFetcher
from fetchers.grey_lit import GreyLiteratureFetcher
from fetchers.hs_code import HSCodeFetcher
from fetchers.libgen import LibGenFetcher
from fetchers.preprint import PreprintFetcher
from fetchers.scihub import SciHubFetcher
from report.pdf_writer import generate_daily_pdf_report
from report.txt_writer import generate_txt_report

COMMON_FIELDS = {
    "module": "来源模块",
    "title": "标题",
    "authors": "作者/机构",
    "date": "日期",
    "abstract": "摘要",
    "link": "链接",
    "notes": "额外备注",
}


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _default_dates() -> dict[str, str]:
    today = datetime.now()
    return {
        "start_6m": (today - timedelta(days=180)).strftime("%Y-%m-%d"),
        "start_1y": (today - timedelta(days=365)).strftime("%Y-%m-%d"),
        "end": today.strftime("%Y-%m-%d"),
        "start_2024": "2024-01-01",
    }


# --------------------------------------------------------------------------- #
# module fetch adapters (reuse existing fetchers with sensible defaults)
# --------------------------------------------------------------------------- #
def _fetch_consulting():
    d = _default_dates()
    f = ConsultingFetcher()
    return f.fetch(
        firms=["mckinsey", "bcg", "roland_berger", "accenture"],
        language="中文",
        start_date=d["start_6m"],
        end_date=d["end"],
        keywords="",
        keyword_logic="OR",
    )


def _fetch_brokerage():
    d = _default_dates()
    f = BrokerageFetcher()
    return f.fetch(
        industry="全部", rating="全部", start_date=d["start_6m"], end_date=d["end"], keywords=""
    )


def _fetch_hscode():
    d = _default_dates()
    f = HSCodeFetcher()
    return f.fetch(
        country="中国 (China)",
        hs_query="",
        trade_type="双边贸易 (Bilateral)",
        start_date=d["start_1y"],
        end_date=d["end"],
    )


def _fetch_greylit():
    d = _default_dates()
    f = GreyLiteratureFetcher()
    return f.fetch(
        keywords="",
        domains=["worldbank.org", "rand.org"],
        file_types=["pdf"],
        start_date=d["start_2024"],
        end_date=d["end"],
    )


def _fetch_preprint():
    f = PreprintFetcher()
    return f.fetch(sources=["arXiv", "SSRN"], category="全部", keywords="", max_results=20)


def _fetch_scihub():
    f = SciHubFetcher()
    data = f.fetch(
        [
            "10.1038/nature12373",
            "10.1126/science.aad0919",
            "10.1016/j.cell.2020.02.007",
        ]
    )
    return data, any(r.get("is_mock", False) for r in data)


def _fetch_libgen():
    f = LibGenFetcher()
    return f.fetch(
        title="artificial intelligence",
        author="",
        isbn="",
        language="全部",
        formats=["pdf", "epub", "mobi"],
    )


MODULE_SPECS: dict[str, dict] = {
    "consulting": {
        "name": "顶级咨询公司报告",
        "fetch": _fetch_consulting,
        "fields": {"source": "来源机构"},
    },
    "brokerage": {
        "name": "券商研报",
        "fetch": _fetch_brokerage,
        "fields": {
            "analyst": "分析师",
            "rating": "评级",
            "supply_chain": "产业链图谱",
            "industry": "所属行业",
        },
    },
    "hscode": {
        "name": "海关编码查询",
        "fetch": _fetch_hscode,
        "fields": {
            "hs_code": "HS编码",
            "country": "国家/地区",
            "trade_type": "贸易类型",
            "trade_value": "贸易额(美元)",
            "quantity": "数量",
            "yoy_change": "同比变化",
            "top_partners": "前十贸易伙伴",
            "flow_desc": "供应链流向描述",
        },
    },
    "greylit": {
        "name": "灰色文献抓取",
        "fetch": _fetch_greylit,
        "fields": {"organization": "出版机构", "file_type": "文件类型"},
    },
    "preprint": {
        "name": "预印本检索",
        "fetch": _fetch_preprint,
        "fields": {"source": "来源平台", "category": "学科分类"},
    },
    "scihub": {
        "name": "Sci-Hub 下载器",
        "fetch": _fetch_scihub,
        "fields": {
            "doi": "DOI",
            "journal": "期刊",
            "year": "出版年",
            "publisher": "出版社",
            "download_status": "下载状态",
            "mirror_hint": "镜像提示",
        },
    },
    "libgen": {
        "name": "LibGen 电子书",
        "fetch": _fetch_libgen,
        "fields": {
            "publisher": "出版社",
            "year": "出版年份",
            "isbn": "ISBN",
            "size": "文件大小",
            "mirrors": "下载镜像",
            "description": "内容简介",
        },
    },
}


class DailyReportWorker(QThread):
    """Background worker that fetches modules and writes TXT + PDF reports."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, list)  # success, message, [file paths]

    def __init__(self, module_keys: list[str], output_dir: str, parent=None):
        super().__init__(parent)
        self.module_keys = module_keys
        self.output_dir = output_dir

    def run(self):
        module_sections: list[dict] = []
        flat_items: list[dict] = []
        field_labels = dict(COMMON_FIELDS)
        selected_fields = ["module", "title", "authors", "date", "abstract", "link", "notes"]
        seen_fields = set(selected_fields)
        errors: list[str] = []

        for key in self.module_keys:
            spec = MODULE_SPECS.get(key)
            if not spec:
                continue
            self.progress.emit(f"正在抓取：{spec['name']} ...")
            try:
                data, _is_mock = spec["fetch"]()
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{spec['name']}：{exc}")
                continue

            for item in data:
                tagged = dict(item)
                tagged["module"] = spec["name"]
                flat_items.append(tagged)

            module_sections.append({"name": spec["name"], "items": data, "fields": spec["fields"]})
            for field, label in spec["fields"].items():
                field_labels.setdefault(field, label)
                if field not in seen_fields:
                    seen_fields.add(field)
                    selected_fields.append(field)

        if not flat_items:
            self.finished.emit(False, "没有抓取到任何数据。", [])
            return

        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except OSError as exc:
            self.finished.emit(False, f"无法创建输出目录：{exc}", [])
            return

        stem = f"daily_report_{datetime.now():%Y%m%d}"
        title = f"每日情报日报 {_today()}"

        try:
            txt_path = generate_txt_report(
                title=title,
                data=flat_items,
                output_dir=self.output_dir,
                selected_fields=selected_fields,
                field_labels=field_labels,
                extra_notes="由本地日报生成服务自动生成。",
                filename_stem=stem,
            )
            self.progress.emit("正在生成 PDF 日报 ...")
            pdf_path = generate_daily_pdf_report(
                title=title,
                subtitle="Daily Intelligence Digest",
                module_sections=module_sections,
                output_dir=self.output_dir,
                filename_stem=stem,
            )
        except Exception as exc:  # noqa: BLE001
            self.finished.emit(False, f"生成报告失败：{exc}", [])
            return

        msg = f"成功生成 {len(flat_items)} 条结果（{len(module_sections)} 个模块）"
        if errors:
            msg += f"；部分模块失败：{'; '.join(errors)}"
        self.finished.emit(True, msg, [txt_path, pdf_path])


class DailyReportService(QObject):
    """Owns the schedule timer and the background worker."""

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedule_time = QTime(9, 0)
        self.module_keys = list(MODULE_SPECS.keys())
        self.output_dir = os.path.expanduser("~/Desktop")

        self.state = "未启动"
        self.last_run_time = ""
        self.last_status = "尚未生成日报"
        self.last_paths: list[str] = []

        self._worker: DailyReportWorker | None = None
        self._running = False
        self._last_generated_on = ""

        self._timer = QTimer(self)
        self._timer.setInterval(15_000)
        self._timer.timeout.connect(self._tick)

    def is_running(self) -> bool:
        return self._running

    def start(self):
        if self._running:
            return
        if not self.module_keys:
            self.state = "未选择模块"
            self.changed.emit()
            return
        self._running = True
        self._timer.start()
        self.state = "运行中"
        self.changed.emit()

    def stop(self):
        self._running = False
        self._timer.stop()
        self.state = "已停止"
        self.changed.emit()

    def _tick(self):
        now = datetime.now()
        if self._last_generated_on == now.strftime("%Y-%m-%d"):
            return
        t = now.time()
        due = t.hour > self.schedule_time.hour() or (
            t.hour == self.schedule_time.hour() and t.minute >= self.schedule_time.minute()
        )
        if due:
            self.run_now()

    def run_now(self):
        if self._worker is not None and self._worker.isRunning():
            return
        if not self.module_keys:
            self.state = "未选择模块"
            self.changed.emit()
            return

        self.state = "生成中..."
        self.changed.emit()

        self._worker = DailyReportWorker(list(self.module_keys), self.output_dir)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, msg: str):
        self.state = msg
        self.changed.emit()

    def _on_finished(self, success: bool, msg: str, paths: list[str]):
        now = datetime.now()
        self.last_run_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.last_status = ("成功" if success else "失败") + " — " + msg
        self.last_paths = paths
        if success:
            self._last_generated_on = now.strftime("%Y-%m-%d")
            self.state = "运行中" if self._running else "上次已完成"
        else:
            self.state = "生成失败"
        self.changed.emit()
