"""Main application window with navigation sidebar and stacked pages."""

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QStatusBar, QFrame, QDialog,
    QCheckBox, QSpinBox, QLineEdit, QFileDialog, QMessageBox,
    QButtonGroup, QGridLayout, QMenu, QGraphicsOpacityEffect,
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSettings
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QPalette

from .styles import GLOBAL_STYLE
from .pages.consulting_page import ConsultingPage
from .pages.brokerage_page import BrokeragePage
from .pages.hs_code_page import HSCodePage
from .pages.grey_lit_page import GreyLitPage
from .pages.preprint_page import PreprintPage
from .pages.scihub_page import SciHubPage
from .pages.libgen_page import LibGenPage


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
        self.setMinimumHeight(42)
        self._color = color

    def set_active(self, active: bool):
        self.setProperty("active", str(active).lower())
        self.style().unpolish(self)
        self.style().polish(self)
        self.setChecked(active)


class SchedulerDialog(QDialog):
    """Dialog for configuring scheduled auto-fetch tasks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("定时任务设置")
        self.setMinimumWidth(480)
        self.setup_ui()
        self._timer = None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Module selection
        layout.addWidget(QLabel("选择自动执行的模块："))
        self.module_checks = {}
        grid = QGridLayout()
        for i, (key, name, emoji, _) in enumerate(NAV_ITEMS):
            cb = QCheckBox(f"{emoji} {name}")
            cb.setChecked(True)
            self.module_checks[key] = cb
            grid.addWidget(cb, i // 2, i % 2)
        layout.addLayout(grid)

        # Interval
        int_row = QHBoxLayout()
        int_row.addWidget(QLabel("执行间隔："))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 72)
        self.interval_spin.setValue(6)
        self.interval_spin.setSuffix(" 小时")
        int_row.addWidget(self.interval_spin)
        int_row.addStretch()
        layout.addLayout(int_row)

        # Output directory
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("输出目录："))
        self.dir_edit = QLineEdit()
        self.dir_edit.setText(self._default_dir())
        dir_row.addWidget(self.dir_edit)
        browse_btn = QPushButton("浏览...")
        browse_btn.setObjectName("secondaryButton")
        browse_btn.clicked.connect(lambda: self._browse_dir())
        dir_row.addWidget(browse_btn)
        layout.addLayout(dir_row)

        # Buttons
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("启动定时任务")
        self.start_btn.setObjectName("successButton")
        self.start_btn.clicked.connect(self._on_start)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setObjectName("dangerButton")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        btn_row.addStretch()
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        layout.addLayout(btn_row)

        # Status
        self.status_label = QLabel("状态：未启动")
        self.status_label.setStyleSheet("color: #64748b;")
        layout.addWidget(self.status_label)

    def _default_dir(self):
        import os
        return os.path.expanduser("~/Desktop")

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录", self.dir_edit.text())
        if d:
            self.dir_edit.setText(d)

    def _on_start(self):
        checked = [k for k, cb in self.module_checks.items() if cb.isChecked()]
        if not checked:
            QMessageBox.warning(self, "提示", "请至少选择一个模块。")
            return
        interval_ms = self.interval_spin.value() * 3600 * 1000
        self._timer = QTimer(self)
        self._timer.timeout.connect(lambda: self._execute_tasks(checked))
        self._timer.start(interval_ms)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText(
            f"状态：运行中 — 每{self.interval_spin.value()}小时执行一次"
        )
        self.status_label.setStyleSheet("color: #10b981; font-weight: bold;")

    def _on_stop(self):
        if self._timer:
            self._timer.stop()
            self._timer = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("状态：已停止")
        self.status_label.setStyleSheet("color: #64748b;")

    def _execute_tasks(self, modules: list[str]):
        """Placeholder for scheduled task execution."""
        output_dir = self.dir_edit.text()
        self.status_label.setText(
            f"状态：上次执行 {datetime.now().strftime('%H:%M:%S')} — "
            f"已保存至 {output_dir}"
        )


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("多源报告汇总推送工具")
        self.setMinimumSize(1200, 780)
        self.setStyleSheet(GLOBAL_STYLE)
        self._bg_image_path = ""
        self._build_ui()
        self._start_clock()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- Top bar ---
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 8, 20, 8)

        title = QLabel("多源报告汇总推送工具")
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

        root.addWidget(top_bar)

        # --- Main content area: sidebar + pages ---
        content_row = QHBoxLayout()
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("navSidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 8, 0, 8)
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

        # Scheduler button at bottom of sidebar
        sched_btn = QPushButton("  ⏰  定时任务")
        sched_btn.setObjectName("navButton")
        sched_btn.setCursor(Qt.PointingHandCursor)
        sched_btn.clicked.connect(self._open_scheduler)
        sidebar_layout.addWidget(sched_btn)

        content_row.addWidget(sidebar)

        # Stacked widget for pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #f8fafc;")

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

    def _open_scheduler(self):
        """Open the scheduler dialog."""
        dlg = SchedulerDialog(self)
        dlg.exec_()

    def _show_bg_menu(self):
        """Show background settings dropdown menu."""
        menu = QMenu(self.bg_btn)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                color: #f1f5f9;
                padding: 10px 28px;
                border-radius: 6px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
        """)

        choose_action = menu.addAction("  选择背景图片...")
        choose_action.triggered.connect(self._choose_background)

        if self._bg_image_path:
            clear_action = menu.addAction("  清除背景")
            clear_action.triggered.connect(self._clear_background)

        menu.exec_(self.bg_btn.mapToGlobal(self.bg_btn.rect().bottomLeft()))

    def _choose_background(self):
        """Open file dialog to select a background image."""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片",
            os.path.expanduser("~/Pictures"),
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;所有文件 (*.*)"
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
            self.stack.setStyleSheet("QStackedWidget { background-color: #f8fafc; }")

    def resizeEvent(self, event):
        """Re-apply background on window resize for proper scaling."""
        super().resizeEvent(event)
        if self._bg_image_path:
            self._apply_background()
