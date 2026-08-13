"""Main application window with XP-style navigation sidebar and stacked pages."""

import os
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QPalette, QPixmap
from PyQt5.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from .daily_service import MODULE_SPECS, DailyReportService
from .pages.brokerage_page import BrokeragePage
from .pages.consulting_page import ConsultingPage
from .pages.grey_lit_page import GreyLitPage
from .pages.hs_code_page import HSCodePage
from .pages.libgen_page import LibGenPage
from .pages.preprint_page import PreprintPage
from .pages.scihub_page import SciHubPage
from .styles import GLOBAL_STYLE

NAV_ITEMS = [
    ("consulting", "顶级咨询公司报告", "🏢", "#3b82f6"),
    ("brokerage", "券商研报", "📈", "#10b981"),
    ("hscode", "海关编码查询", "🔍", "#f59e0b"),
    ("greylit", "灰色文献抓取", "📄", "#8b5cf6"),
    ("preprint", "预印本检索", "📝", "#ec4899"),
    ("scihub", "Sci-Hub 下载器", "🔬", "#ef4444"),
    ("libgen", "LibGen 电子书", "📚", "#14b8a6"),
]


class NavButton(QPushButton):
    """Custom navigation button with icon badge."""

    def __init__(self, key: str, text: str, emoji: str, color: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.setText(f"  {emoji}  {text}")
        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        self._color = color

    def set_active(self, active: bool):
        self.setProperty("active", str(active).lower())
        self.style().unpolish(self)
        self.style().polish(self)
        self.setChecked(active)


class DailyReportDialog(QDialog):
    """Configuration and status panel for the local daily report service."""

    def __init__(self, service: DailyReportService, parent=None):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("日报本地生成服务")
        self.setMinimumWidth(600)
        self._build_ui()
        self._refresh()
        service.changed.connect(self._refresh)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Schedule time
        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("生成时间："))
        self.time_edit = QTimeEdit(self.service.schedule_time)
        self.time_edit.setDisplayFormat("HH:mm")
        time_row.addWidget(self.time_edit)
        time_row.addWidget(QLabel("（每天到点自动抓取并生成 TXT + PDF 日报）"))
        time_row.addStretch()
        layout.addLayout(time_row)

        # Module selection
        layout.addWidget(QLabel("选取信息源模块："))
        self.module_checks: dict[str, QCheckBox] = {}
        grid = QGridLayout()
        for i, (key, spec) in enumerate(MODULE_SPECS.items()):
            cb = QCheckBox(spec["name"])
            cb.setChecked(key in self.service.module_keys)
            self.module_checks[key] = cb
            grid.addWidget(cb, i // 2, i % 2)
        layout.addLayout(grid)

        # Output directory
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("输出目录："))
        self.dir_edit = QLineEdit(self.service.output_dir)
        dir_row.addWidget(self.dir_edit)
        browse_btn = QPushButton("浏览...")
        browse_btn.setObjectName("secondaryButton")
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(browse_btn)
        layout.addLayout(dir_row)

        # Action buttons
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("启动服务")
        self.start_btn.setObjectName("successButton")
        self.stop_btn = QPushButton("停止服务")
        self.stop_btn.setObjectName("dangerButton")
        self.run_btn = QPushButton("立即生成一次")
        self.run_btn.setObjectName("secondaryButton")
        self.start_btn.clicked.connect(self._on_start)
        self.stop_btn.clicked.connect(self._on_stop)
        self.run_btn.clicked.connect(self._on_run_now)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.run_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Status panel
        panel = QGroupBox("服务状态")
        p = QVBoxLayout(panel)
        p.setSpacing(4)
        self.state_label = QLabel()
        self.time_label = QLabel()
        self.status_label = QLabel()
        self.paths_label = QLabel()
        self.paths_label.setWordWrap(True)
        self.paths_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        for w in (self.state_label, self.time_label, self.status_label, self.paths_label):
            w.setStyleSheet("background: transparent;")
            p.addWidget(w)
        layout.addWidget(panel)

    def _apply_config(self):
        self.service.schedule_time = self.time_edit.time()
        self.service.module_keys = [k for k, cb in self.module_checks.items() if cb.isChecked()]
        out = self.dir_edit.text().strip()
        if out:
            self.service.output_dir = out

    def _on_start(self):
        self._apply_config()
        if not self.service.module_keys:
            QMessageBox.warning(self, "提示", "请至少选择一个信息源模块。")
            return
        try:
            os.makedirs(self.service.output_dir, exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(self, "路径错误", f"无法创建输出目录：{exc}")
            return
        self.service.start()

    def _on_stop(self):
        self.service.stop()

    def _on_run_now(self):
        self._apply_config()
        if not self.service.module_keys:
            QMessageBox.warning(self, "提示", "请至少选择一个信息源模块。")
            return
        try:
            os.makedirs(self.service.output_dir, exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(self, "路径错误", f"无法创建输出目录：{exc}")
            return
        self.service.run_now()

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录", self.dir_edit.text())
        if d:
            self.dir_edit.setText(d)

    def _refresh(self):
        self.state_label.setText(f"运行状态：{self.service.state}")
        self.time_label.setText(f"上次生成时间：{self.service.last_run_time or '—'}")
        self.status_label.setText(f"上次状态：{self.service.last_status}")
        if self.service.last_paths:
            self.paths_label.setText("生成文件：\n" + "\n".join(self.service.last_paths))
        else:
            self.paths_label.setText("生成文件：—")
        running = self.service.is_running()
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("多源报告汇总推送工具")
        self.setMinimumSize(1200, 780)
        self.setStyleSheet(GLOBAL_STYLE)
        self._bg_image_path = ""
        self.daily_service = DailyReportService(self)
        self._build_ui()
        self._start_clock()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- Top bar (XP title bar) ---
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 4, 8, 4)
        top_layout.setSpacing(8)

        title = QLabel("  多源报告汇总推送工具")
        title.setObjectName("appTitle")
        top_layout.addWidget(title)

        top_layout.addStretch()

        # Background settings button
        self.bg_btn = QPushButton("  背景")
        self.bg_btn.setObjectName("bgSettingsButton")
        self.bg_btn.setCursor(Qt.PointingHandCursor)
        self.bg_btn.clicked.connect(self._show_bg_menu)
        top_layout.addWidget(self.bg_btn)

        self.time_label = QLabel("")
        self.time_label.setObjectName("timeLabel")
        top_layout.addWidget(self.time_label)

        # XP-style caption buttons (functional)
        self.min_btn = self._caption_button("–", "captionButton", self.showMinimized)
        self.max_btn = self._caption_button("□", "captionButton", self._toggle_max)
        self.close_btn = self._caption_button("✕", "captionCloseButton", self.close)
        top_layout.addWidget(self.min_btn)
        top_layout.addWidget(self.max_btn)
        top_layout.addWidget(self.close_btn)

        root.addWidget(top_bar)

        # --- Main content area: sidebar + pages ---
        content_row = QHBoxLayout()
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(0)

        # Sidebar (XP task pane)
        sidebar = QFrame()
        sidebar.setObjectName("navSidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 6, 0, 6)
        sidebar_layout.setSpacing(2)

        nav_header = QLabel("功  能  模  块")
        nav_header.setObjectName("navHeader")
        sidebar_layout.addWidget(nav_header)

        self.nav_buttons: dict[str, NavButton] = {}
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        for i, (key, name, emoji, color) in enumerate(NAV_ITEMS):
            btn = NavButton(key, name, emoji, color)
            btn.clicked.connect(lambda checked, k=key: self._switch_page(k))
            self.nav_buttons[key] = btn
            self.nav_group.addButton(btn)
            sidebar_layout.addWidget(btn)
            if i == 2:  # Separator after HS Code
                sep = QFrame()
                sep.setObjectName("navSeparator")
                sidebar_layout.addWidget(sep)

        sidebar_layout.addStretch()

        # Daily report service button at bottom of sidebar
        daily_btn = QPushButton("  ⏰  日报服务")
        daily_btn.setObjectName("navButton")
        daily_btn.setCursor(Qt.PointingHandCursor)
        daily_btn.clicked.connect(self._open_daily_service)
        sidebar_layout.addWidget(daily_btn)

        content_row.addWidget(sidebar)

        # Stacked widget for pages
        self.stack = QStackedWidget()

        # Create all pages
        self.pages = {}
        page_classes = {
            "consulting": ConsultingPage,
            "brokerage": BrokeragePage,
            "hscode": HSCodePage,
            "greylit": GreyLitPage,
            "preprint": PreprintPage,
            "scihub": SciHubPage,
            "libgen": LibGenPage,
        }

        for key, cls in page_classes.items():
            page = cls()
            page.progress_signal.connect(self._on_progress)
            self.pages[key] = page
            self.stack.addWidget(page)

        content_row.addWidget(self.stack, 1)
        root.addLayout(content_row, 1)

        # --- Status bar ---
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("就绪")
        self.setStatusBar(self.status_bar)

        # Default to first page
        self._switch_page("consulting")

    def _caption_button(self, text: str, name: str, slot) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName(name)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.clicked.connect(slot)
        return btn

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _switch_page(self, key: str):
        """Switch the stacked widget to the given page key."""
        if key in self.pages:
            self.stack.setCurrentWidget(self.pages[key])
            for k, btn in self.nav_buttons.items():
                btn.set_active(k == key)

    def _on_progress(self, msg: str):
        """Update status bar with progress message."""
        self.status_bar.showMessage(msg)

    def _start_clock(self):
        """Update the time label every second."""
        self.clock = QTimer(self)
        self.clock.timeout.connect(self._update_time)
        self.clock.start(1000)
        self._update_time()

    def _update_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(now)

    def _open_daily_service(self):
        """Open the daily report service dialog."""
        dlg = DailyReportDialog(self.daily_service, self)
        dlg.exec_()

    def _show_bg_menu(self):
        """Show background settings dropdown menu."""
        menu = QMenu(self.bg_btn)

        choose_action = menu.addAction("  选择背景图片...")
        choose_action.triggered.connect(self._choose_background)

        if self._bg_image_path:
            clear_action = menu.addAction("  清除背景")
            clear_action.triggered.connect(self._clear_background)

        menu.exec_(self.bg_btn.mapToGlobal(self.bg_btn.rect().bottomLeft()))

    def _choose_background(self):
        """Open file dialog to select a background image."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择背景图片",
            os.path.expanduser("~/Pictures"),
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;所有文件 (*.*)",
        )
        if not path:
            return
        self._bg_image_path = path
        self._apply_background()

    def _clear_background(self):
        """Remove the custom background."""
        self._bg_image_path = ""
        self._apply_background()

    def _apply_background(self):
        """Apply or clear the background image on the content area."""
        if self._bg_image_path:
            pixmap = QPixmap(self._bg_image_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "错误", "无法加载图片，请检查文件格式。")
                self._bg_image_path = ""
                return
            scaled = pixmap.scaled(
                self.stack.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            palette = self.stack.palette()
            palette.setBrush(QPalette.Window, QBrush(scaled))
            self.stack.setPalette(palette)
            self.stack.setAutoFillBackground(True)
        else:
            self.stack.setAutoFillBackground(False)
            self.stack.setPalette(self.style().standardPalette())

    def resizeEvent(self, event):
        """Re-apply background on window resize for proper scaling."""
        super().resizeEvent(event)
        if self._bg_image_path:
            self._apply_background()
