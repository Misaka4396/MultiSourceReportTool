"""Global QSS stylesheet for the application."""

GLOBAL_STYLE = """
/* ===== Global ===== */
QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #334155;
    background-color: #f1f5f9;
}

/* ===== Main Window ===== */
QMainWindow {
    background-color: #f1f5f9;
}

/* ===== Top Bar ===== */
#topBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 20px;
}

#appTitle {
    font-size: 20px;
    font-weight: bold;
    color: #1e293b;
}

#timeLabel {
    font-size: 12px;
    color: #64748b;
}

/* ===== Navigation Sidebar ===== */
#navSidebar {
    background-color: #1e293b;
    min-width: 200px;
    max-width: 200px;
    border-right: none;
}

#navHeader {
    color: #94a3b8;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 16px 16px 8px 16px;
    text-transform: uppercase;
}

#navButton {
    background-color: transparent;
    color: #cbd5e1;
    border: none;
    border-radius: 8px;
    padding: 10px 12px;
    margin: 2px 8px;
    text-align: left;
    font-size: 13px;
}

#navButton:hover {
    background-color: #334155;
    color: #f1f5f9;
}

#navButton:checked, #navButton[active="true"] {
    background-color: #3b82f6;
    color: #ffffff;
    font-weight: bold;
}

#navSeparator {
    background-color: #334155;
    min-height: 1px;
    max-height: 1px;
    margin: 8px 16px;
}

#navIcon {
    color: #ffffff;
    font-weight: bold;
    font-size: 12px;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
    font-size: 12px;
    padding: 4px 12px;
}

/* ===== Cards ===== */
#card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    margin: 4px 0px;
}

#cardTitle {
    font-size: 15px;
    font-weight: bold;
    color: #1e293b;
    padding-bottom: 8px;
    border-bottom: 2px solid #3b82f6;
    margin-bottom: 12px;
}

/* ===== Section Headers ===== */
#sectionHeader {
    font-size: 14px;
    font-weight: bold;
    color: #475569;
    padding: 8px 0px 4px 0px;
}

/* ===== Form Controls ===== */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 20px;
    color: #334155;
}

QComboBox:hover {
    border-color: #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    selection-background-color: #e0f2fe;
    selection-color: #334155;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #334155;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #3b82f6;
}

QDateEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 20px;
}

QDateEdit:focus {
    border-color: #3b82f6;
}

QDateEdit::drop-down {
    border: none;
    width: 24px;
}

QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 20px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #3b82f6;
}

/* ===== Checkboxes ===== */
QCheckBox {
    spacing: 8px;
    color: #475569;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #cbd5e1;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border-color: #3b82f6;
}

QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

/* ===== Radio Buttons ===== */
QRadioButton {
    spacing: 8px;
    color: #475569;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #cbd5e1;
    border-radius: 9px;
    background-color: #ffffff;
}

QRadioButton::indicator:hover {
    border-color: #3b82f6;
}

QRadioButton::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #2563eb;
}

QPushButton:pressed {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #94a3b8;
    color: #e2e8f0;
}

#secondaryButton {
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
    font-weight: normal;
}

#secondaryButton:hover {
    background-color: #e2e8f0;
    border-color: #94a3b8;
}

#dangerButton {
    background-color: #ef4444;
}

#dangerButton:hover {
    background-color: #dc2626;
}

#successButton {
    background-color: #10b981;
}

#successButton:hover {
    background-color: #059669;
}

#primaryActionButton {
    background-color: #3b82f6;
    color: #ffffff;
    font-size: 15px;
    padding: 14px 32px;
    border-radius: 10px;
}

#primaryActionButton:hover {
    background-color: #2563eb;
}

#bgSettingsButton {
    background-color: transparent;
    color: #64748b;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: normal;
}

#bgSettingsButton:hover {
    background-color: #f1f5f9;
    border-color: #3b82f6;
    color: #3b82f6;
}

/* ===== Scroll Area ===== */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #f1f5f9;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f1f5f9;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ===== Group Box ===== */
QGroupBox {
    font-weight: bold;
    color: #475569;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0px 6px;
}

/* ===== Table ===== */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
}

QTableWidget::item {
    padding: 6px;
}

QHeaderView::section {
    background-color: #f8fafc;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    padding: 8px 6px;
    font-weight: bold;
    color: #475569;
}

/* ===== Progress Bar ===== */
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #e2e8f0;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 6px;
}

/* ===== Tooltips ===== */
QToolTip {
    background-color: #1e293b;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

/* ===== Splitter ===== */
QSplitter::handle {
    background-color: #e2e8f0;
    width: 1px;
}

/* ===== Direct Report Menu ===== */
    #directReportMenu {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 6px;
    }

    #directReportMenu::item {
        color: #f1f5f9;
        padding: 10px 28px;
        border-radius: 6px;
        font-size: 13px;
    }

    #directReportMenu::item:selected {
        background-color: #3b82f6;
        color: #ffffff;
    }

    #directReportMenu::separator {
        background-color: #334155;
        height: 1px;
        margin: 4px 8px;
    }

    /* ===== Dialog ===== */
QDialog {
    background-color: #f8fafc;
}

/* ===== Message Box ===== */
QMessageBox {
    background-color: #ffffff;
}

/* ===== Tab Widget (if used) ===== */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border-bottom: 2px solid #3b82f6;
    color: #3b82f6;
    font-weight: bold;
}
"""
