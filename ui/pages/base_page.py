"""Base page class with common UI elements for all modules."""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QLineEdit, QGroupBox, QFileDialog, QScrollArea,
    QFrame, QMessageBox, QRadioButton, QButtonGroup, QToolButton, QMenu,
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont

from report.txt_writer import generate_txt_report
from report.pdf_writer import generate_pdf_report


class BasePage(QWidget):
    """Base class for all module pages providing common output/format controls."""

    # Signal: progress message (str)
    progress_signal = pyqtSignal(str)
    # Signal: task finished
    finished_signal = pyqtSignal()

    # Common fields available across all modules
    COMMON_FIELDS = {
        "title": "标题",
        "authors": "作者/机构",
        "date": "日期",
        "abstract": "摘要",
        "link": "链接",
        "notes": "额外备注",
    }

    def __init__(self, module_name: str, module_key: str, parent=None):
        super().__init__(parent)
        self.module_name = module_name
        self.module_key = module_key
        self.output_dir = os.path.expanduser("~/Desktop")
        # Override these in subclass
        self.report_title = module_name
        self.report_subtitle = ""
        self.mock_note = "注意：以下为示例数据，非实时抓取结果。"
        self.extra_result_msg = ""
        self._empty_msg = "未找到匹配的数据。"
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(10)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        # --- Page title ---
        title_label = QLabel(self.module_name)
        title_label.setObjectName("cardTitle")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        scroll_layout.addWidget(title_label)

        # --- Constraints area ---
        constraints_card = QFrame()
        constraints_card.setObjectName("card")
        constraints_layout = QVBoxLayout(constraints_card)
        constraints_layout.setSpacing(8)

        constraints_header = QLabel("约束条件")
        constraints_header.setObjectName("sectionHeader")
        constraints_layout.addWidget(constraints_header)

        # Subclass adds specific constraints here
        self.constraints_widget = QWidget()
        self.constraints_layout = QVBoxLayout(self.constraints_widget)
        self.constraints_layout.setContentsMargins(0, 0, 0, 0)
        constraints_layout.addWidget(self.constraints_widget)

        scroll_layout.addWidget(constraints_card)

        # --- Output content selection ---
        output_card = QFrame()
        output_card.setObjectName("card")
        output_layout = QVBoxLayout(output_card)
        output_layout.setSpacing(8)

        output_header = QLabel("输出内容选择")
        output_header.setObjectName("sectionHeader")
        output_layout.addWidget(output_header)

        self.field_checkboxes: dict[str, QCheckBox] = {}
        fields_row1 = QHBoxLayout()
        fields_row2 = QHBoxLayout()

        all_fields = self.get_all_fields()
        half = (len(all_fields) + 1) // 2
        for i, (key, label) in enumerate(all_fields.items()):
            cb = QCheckBox(label)
            cb.setChecked(True)
            self.field_checkboxes[key] = cb
            if i < half:
                fields_row1.addWidget(cb)
            else:
                fields_row2.addWidget(cb)
        fields_row1.addStretch()
        fields_row2.addStretch()

        output_layout.addLayout(fields_row1)
        if len(all_fields) > half:
            output_layout.addLayout(fields_row2)

        scroll_layout.addWidget(output_card)

        # --- Report settings ---
        settings_card = QFrame()
        settings_card.setObjectName("card")
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setSpacing(8)

        settings_header = QLabel("报告设置")
        settings_header.setObjectName("sectionHeader")
        settings_layout.addWidget(settings_header)

        # Format selection
        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("输出格式："))
        self.cb_txt = QCheckBox("TXT")
        self.cb_txt.setChecked(True)
        self.cb_pdf = QCheckBox("PDF")
        self.cb_pdf.setChecked(True)
        format_row.addWidget(self.cb_txt)
        format_row.addWidget(self.cb_pdf)

        self.rb_single_col = QRadioButton("单栏")
        self.rb_single_col.setChecked(True)
        self.rb_dual_col = QRadioButton("双栏")
        col_group = QButtonGroup(self)
        col_group.addButton(self.rb_single_col)
        col_group.addButton(self.rb_dual_col)
        format_row.addSpacing(16)
        format_row.addWidget(QLabel("PDF排版："))
        format_row.addWidget(self.rb_single_col)
        format_row.addWidget(self.rb_dual_col)
        format_row.addStretch()
        settings_layout.addLayout(format_row)

        # Output directory
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("输出路径："))
        self.dir_edit = QLineEdit(self.output_dir)
        self.dir_edit.setReadOnly(True)
        dir_row.addWidget(self.dir_edit)
        browse_btn = QPushButton("浏览...")
        browse_btn.setObjectName("secondaryButton")
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(browse_btn)
        settings_layout.addLayout(dir_row)

        scroll_layout.addWidget(settings_card)

        # --- Action button with dropdown menu ---
        self.action_btn = QToolButton()
        self.action_btn.setText("抓取并生成报告")
        self.action_btn.setObjectName("primaryActionButton")
        self.action_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.action_btn.setPopupMode(QToolButton.MenuButtonPopup)
        self.action_btn.setMinimumHeight(48)
        self.action_btn.setMinimumWidth(200)
        self.action_btn.clicked.connect(self.on_action_clicked)

        menu = QMenu(self.action_btn)
        direct_action = menu.addAction("直接生成报告（示例数据）")
        direct_action.triggered.connect(self.on_direct_report)
        self.action_btn.setMenu(menu)

        scroll_layout.addWidget(self.action_btn)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def get_all_fields(self) -> dict[str, str]:
        """Return all available fields for this module. Override to add extras."""
        return dict(self.COMMON_FIELDS)

    def get_selected_fields(self) -> list[str]:
        """Get list of field keys that the user has checked."""
        return [k for k, cb in self.field_checkboxes.items() if cb.isChecked()]

    def get_field_labels(self) -> dict[str, str]:
        """Get mapping of field keys to display labels."""
        return self.get_all_fields()

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_dir)
        if d:
            self.output_dir = d
            self.dir_edit.setText(d)

    def on_action_clicked(self):
        """Called when the main action button is clicked. Override in subclass."""
        pass

    def show_result_dialog(self, success: bool, message: str):
        """Show a result message box."""
        if success:
            QMessageBox.information(self, "操作完成", message)
        else:
            QMessageBox.warning(self, "操作失败", message)

    def _validate_output_dir(self) -> bool:
        if not os.path.isdir(self.output_dir):
            QMessageBox.warning(self, "路径错误", f"输出目录不存在：{self.output_dir}")
            return False
        if not self.cb_txt.isChecked() and not self.cb_pdf.isChecked():
            QMessageBox.warning(self, "格式选择", "请至少选择一种输出格式（TXT 或 PDF）。")
            return False
        return True

    def get_sample_data(self) -> list[dict]:
        """Return mock/sample data for direct report generation. Override in subclass."""
        return []

    def on_direct_report(self):
        """Generate a report directly using sample data without fetching."""
        if not self._validate_output_dir():
            return
        data = self.get_sample_data()
        if not data:
            self.show_result_dialog(False, "当前模块暂无示例数据，请使用「抓取并生成报告」功能。")
            return
        self.generate_report(data, is_mock=True)

    def generate_report(self, data: list[dict], is_mock: bool = True):
        """Generate TXT/PDF reports from the given data."""
        self.action_btn.setEnabled(True)

        if not data:
            self.set_progress(self._empty_msg)
            self.show_result_dialog(False, self._empty_msg)
            return

        selected = self.get_selected_fields()
        labels = self.get_field_labels()
        generated = []
        note = self.mock_note if is_mock else ""

        if self.cb_txt.isChecked():
            self.set_progress("正在生成TXT报告...")
            txt_path = generate_txt_report(
                title=self.report_title,
                data=data,
                output_dir=self.output_dir,
                selected_fields=selected,
                field_labels=labels,
                extra_notes=note,
            )
            generated.append(f"TXT: {txt_path}")

        if self.cb_pdf.isChecked():
            self.set_progress("正在生成PDF报告...")
            pdf_path = generate_pdf_report(
                title=self.report_title,
                subtitle=self.report_subtitle,
                data=data,
                output_dir=self.output_dir,
                selected_fields=selected,
                field_labels=labels,
                dual_column=self.rb_dual_col.isChecked(),
            )
            generated.append(f"PDF: {pdf_path}")

        msg = "报告已生成：\n" + "\n".join(generated)
        if is_mock:
            msg += f"\n\n[注意] {self.mock_note}"
        if self.extra_result_msg:
            msg += self.extra_result_msg
        self.set_progress("报告生成完成。")
        self.show_result_dialog(True, msg)

    def add_constraint_row(self, label_text: str, widget, parent_layout=None):
        """Helper to add a labeled constraint row."""
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setMinimumWidth(100)
        row.addWidget(label)
        row.addWidget(widget)
        row.addStretch()
        target = parent_layout or self.constraints_layout
        target.addLayout(row)
        return row

    def set_progress(self, msg: str):
        """Emit progress signal."""
        self.progress_signal.emit(msg)
