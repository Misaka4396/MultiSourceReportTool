"""Global QSS stylesheet — Windows XP (Luna) retro theme."""

# XP Luna palette
XP_BLUE_DARK = "#003399"
XP_BLUE = "#1B6AC9"
XP_BLUE_BRIGHT = "#0054E3"
XP_ACCENT = "#316AC5"
XP_BEIGE = "#ECE9D8"
XP_BEIGE_LIGHT = "#F8F7F1"
XP_BORDER = "#ACA899"
XP_INPUT_BORDER = "#7F9DB9"

# Reusable gradients
_TITLEBAR = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, " "stop:0 #0054E3, stop:0.5 #0046C0, stop:1 #003399)"
)
_TASKPANE = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, " "stop:0 #7BA2E7, stop:0.6 #5B8BD8, stop:1 #3B6FC4)"
)
_BTN_BLUE = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, "
    "stop:0 #9FDFFF, stop:0.45 #3D8EF3, stop:0.5 #2E6BD8, stop:1 #1B4FA5)"
)
_BTN_BLUE_PRESSED = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, " "stop:0 #1B4FA5, stop:0.5 #2E6BD8, stop:1 #3D8EF3)"
)
_BTN_BEIGE = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, " "stop:0 #FFFFFF, stop:0.5 #F1F0EB, stop:1 #E5E1D8)"
)
_BTN_BEIGE_PRESSED = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, " "stop:0 #E0DCCB, stop:0.5 #ECE8DC, stop:1 #F4F1E6)"
)
_HEADER_BAR = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, " "stop:0 #FFFFFF, stop:0.5 #F5F4EE, stop:1 #D8D6CB)"
)
_SCROLL_HANDLE = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, "
    "stop:0 #F0F5FF, stop:0.45 #C6D8F2, stop:0.5 #A9BFE4, stop:1 #7F9DB9)"
)
_CHECKED_BLUE = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, " "stop:0 #8FC3FF, stop:0.5 #4A8FE8, stop:1 #1B6AC9)"
)
_PROGRESS_CHUNK = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, " "stop:0 #8BE07C, stop:0.5 #4BB84B, stop:1 #2E9E2E)"
)

GLOBAL_STYLE = f"""
/* ===== Global ===== */
QWidget {{
    font-family: "Tahoma", "SimSun", "Microsoft YaHei";
    font-size: 13px;
    color: #000000;
    background-color: {XP_BEIGE};
}}

/* ===== Main Window ===== */
QMainWindow {{
    background-color: {XP_BEIGE};
}}

/* ===== Top Bar (XP title bar) ===== */
#topBar {{
    background-color: {XP_BLUE_DARK};
    background: {_TITLEBAR};
    border-bottom: 1px solid #002366;
    min-height: 44px;
    max-height: 44px;
}}

#appTitle {{
    font-size: 17px;
    font-weight: bold;
    color: #FFFFFF;
    background: transparent;
    padding-left: 4px;
}}

#timeLabel {{
    font-size: 11px;
    color: #DCE9FF;
    background: transparent;
    padding: 0px 10px;
}}

#captionButton {{
    background: {_BTN_BLUE};
    border: 1px solid #0A2E6B;
    border-radius: 3px;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 12px;
    min-width: 24px;
    max-width: 24px;
    min-height: 22px;
    max-height: 22px;
    padding: 0px;
}}

#captionButton:hover {{
    background: {_BTN_BLUE_PRESSED};
    border-color: #FFFFFF;
}}

#captionButton:pressed {{
    background: {_BTN_BLUE_PRESSED};
    padding-top: 1px;
}}

#captionCloseButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F3A693, stop:0.45 #E4683F, stop:0.5 #D24A25, stop:1 #B02E12);
    border: 1px solid #7A1E0C;
    border-radius: 3px;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 12px;
    min-width: 24px;
    max-width: 24px;
    min-height: 22px;
    max-height: 22px;
    padding: 0px;
}}

#captionCloseButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFB7A5, stop:0.45 #F07A55, stop:0.5 #E45C33, stop:1 #C23B1C);
    border-color: #FFFFFF;
}}

#captionCloseButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #B02E12, stop:0.5 #D24A25, stop:1 #E4683F);
    padding-top: 1px;
}}

/* ===== Navigation Sidebar (XP task pane) ===== */
#navSidebar {{
    background-color: #4A78C4;
    background: {_TASKPANE};
    min-width: 208px;
    max-width: 208px;
    border-right: 1px solid #2E56A0;
}}

#navHeader {{
    color: #FFFFFF;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 14px 14px 6px 14px;
    background: transparent;
}}

#navButton {{
    background: transparent;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 9px 12px;
    margin: 1px 8px;
    text-align: left;
    font-size: 13px;
}}

#navButton:hover {{
    background-color: rgba(255, 255, 255, 40);
}}

#navButton:checked, #navButton[active="true"] {{
    background-color: #FFFFFF;
    color: {XP_BLUE_DARK};
    font-weight: bold;
}}

#navSeparator {{
    background-color: rgba(255, 255, 255, 70);
    min-height: 1px;
    max-height: 1px;
    margin: 6px 14px;
}}

#navIcon {{
    color: #FFFFFF;
    font-weight: bold;
    font-size: 12px;
    background: transparent;
}}

/* ===== Status Bar ===== */
QStatusBar {{
    background-color: {XP_BEIGE};
    border-top: 1px solid #FFFFFF;
    color: #000000;
    font-size: 12px;
    padding: 2px 10px;
}}

QStatusBar::item {{
    border: none;
}}

/* ===== Cards ===== */
#card {{
    background-color: #FFFFFF;
    border: 1px solid {XP_BORDER};
    border-radius: 6px;
    padding: 14px;
    margin: 2px 0px;
}}

#cardTitle {{
    font-size: 16px;
    font-weight: bold;
    color: {XP_BLUE_DARK};
    padding-bottom: 6px;
    border-bottom: 1px solid {XP_BORDER};
    margin-bottom: 10px;
}}

/* ===== Section Headers ===== */
#sectionHeader {{
    font-size: 13px;
    font-weight: bold;
    color: {XP_BLUE_DARK};
    padding: 4px 0px 2px 0px;
}}

/* ===== Form Controls ===== */
QComboBox {{
    background-color: #FFFFFF;
    border: 1px solid {XP_INPUT_BORDER};
    border-radius: 3px;
    padding: 4px 10px;
    min-height: 20px;
    color: #000000;
}}

QComboBox:hover {{
    border-color: {XP_ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 22px;
}}

QComboBox QAbstractItemView {{
    background-color: #FFFFFF;
    border: 1px solid {XP_BORDER};
    selection-background-color: {XP_ACCENT};
    selection-color: #FFFFFF;
}}

QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: #FFFFFF;
    border: 1px solid {XP_INPUT_BORDER};
    border-radius: 3px;
    padding: 5px 8px;
    color: #000000;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {XP_BLUE};
}}

QDateEdit {{
    background-color: #FFFFFF;
    border: 1px solid {XP_INPUT_BORDER};
    border-radius: 3px;
    padding: 4px 8px;
    min-height: 20px;
}}

QDateEdit:focus {{
    border-color: {XP_BLUE};
}}

QDateEdit::drop-down {{
    border: none;
    width: 22px;
}}

QSpinBox, QDoubleSpinBox {{
    background-color: #FFFFFF;
    border: 1px solid {XP_INPUT_BORDER};
    border-radius: 3px;
    padding: 4px 8px;
    min-height: 20px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {XP_BLUE};
}}

/* ===== Checkboxes ===== */
QCheckBox {{
    spacing: 7px;
    color: #000000;
    background: transparent;
}}

QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {XP_INPUT_BORDER};
    background-color: #FFFFFF;
}}

QCheckBox::indicator:hover {{
    border-color: {XP_ACCENT};
}}

QCheckBox::indicator:checked {{
    background: {_CHECKED_BLUE};
    border: 2px solid #FFFFFF;
    outline: 1px solid {XP_INPUT_BORDER};
}}

/* ===== Radio Buttons ===== */
QRadioButton {{
    spacing: 7px;
    color: #000000;
    background: transparent;
}}

QRadioButton::indicator {{
    width: 15px;
    height: 15px;
    border-radius: 8px;
    border: 1px solid {XP_INPUT_BORDER};
    background-color: #FFFFFF;
}}

QRadioButton::indicator:hover {{
    border-color: {XP_ACCENT};
}}

QRadioButton::indicator:checked {{
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 {XP_BLUE_DARK}, stop:0.38 {XP_BLUE_DARK}, stop:0.4 #FFFFFF, stop:1 #FFFFFF);
    border: 1px solid {XP_INPUT_BORDER};
}}

/* ===== Buttons ===== */
QPushButton, QToolButton {{
    background-color: {XP_BEIGE_LIGHT};
    background: {_BTN_BEIGE};
    color: #000000;
    border: 1px solid {XP_BORDER};
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 13px;
}}

QPushButton:hover, QToolButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF, stop:1 #F1EEE0);
    border-color: {XP_INPUT_BORDER};
}}

QPushButton:pressed, QToolButton:pressed {{
    background: {_BTN_BEIGE_PRESSED};
    padding-top: 7px;
    padding-bottom: 5px;
    border-color: {XP_BORDER};
}}

QPushButton:disabled, QToolButton:disabled {{
    background: #F0EEE5;
    color: #8A8778;
    border-color: {XP_BORDER};
}}

#secondaryButton {{
    background: {_BTN_BEIGE};
    color: #000000;
    border: 1px solid {XP_BORDER};
    font-weight: normal;
}}

#secondaryButton:hover {{
    border-color: {XP_ACCENT};
}}

#dangerButton, #successButton, #primaryActionButton {{
    background: {_BTN_BLUE};
    color: #FFFFFF;
    border: 1px solid #0A2E6B;
    font-weight: bold;
}}

#dangerButton:hover, #successButton:hover, #primaryActionButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #B5E9FF, stop:0.45 #58A5FF, stop:0.5 #3D80E8, stop:1 #2B62C0);
    border-color: #FFFFFF;
}}

#dangerButton:pressed, #successButton:pressed, #primaryActionButton:pressed {{
    background: {_BTN_BLUE_PRESSED};
    padding-top: 7px;
    padding-bottom: 5px;
}}

#dangerButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F3A693, stop:0.45 #E4683F, stop:0.5 #D24A25, stop:1 #B02E12);
    border-color: #7A1E0C;
}}

#dangerButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFB7A5, stop:0.45 #F07A55, stop:0.5 #E45C33, stop:1 #C23B1C);
}}

#primaryActionButton {{
    font-size: 14px;
    padding: 12px 26px;
    border-radius: 5px;
}}

#bgSettingsButton {{
    background: {_BTN_BEIGE};
    color: #000000;
    border: 1px solid {XP_BORDER};
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: normal;
}}

#bgSettingsButton:hover {{
    border-color: {XP_ACCENT};
}}

/* ===== Scroll Area ===== */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {XP_BEIGE};
    width: 16px;
    border: 1px solid {XP_BORDER};
}}

QScrollBar::handle:vertical {{
    background: {_SCROLL_HANDLE};
    border: 1px solid {XP_INPUT_BORDER};
    min-height: 22px;
}}

QScrollBar::handle:vertical:hover {{
    border-color: {XP_ACCENT};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 16px;
    background: {_BTN_BEIGE};
    border: 1px solid {XP_BORDER};
    subcontrol-origin: margin;
}}

QScrollBar:horizontal {{
    background-color: {XP_BEIGE};
    height: 16px;
    border: 1px solid {XP_BORDER};
}}

QScrollBar::handle:horizontal {{
    background: {_SCROLL_HANDLE};
    border: 1px solid {XP_INPUT_BORDER};
    min-width: 22px;
}}

QScrollBar::handle:horizontal:hover {{
    border-color: {XP_ACCENT};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 16px;
    background: {_BTN_BEIGE};
    border: 1px solid {XP_BORDER};
    subcontrol-origin: margin;
}}

/* ===== Group Box ===== */
QGroupBox {{
    font-weight: bold;
    color: {XP_BLUE_DARK};
    border: 1px solid {XP_BORDER};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 14px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0px 4px;
}}

/* ===== Table ===== */
QTableWidget {{
    background-color: #FFFFFF;
    border: 1px solid {XP_BORDER};
    border-radius: 4px;
    gridline-color: #E3E1D8;
}}

QTableWidget::item {{
    padding: 4px;
}}

QHeaderView::section {{
    background: {_HEADER_BAR};
    border: none;
    border-right: 1px solid {XP_BORDER};
    border-bottom: 1px solid {XP_BORDER};
    padding: 6px 6px;
    font-weight: bold;
    color: #000000;
}}

/* ===== Progress Bar ===== */
QProgressBar {{
    border: 1px solid {XP_INPUT_BORDER};
    border-radius: 3px;
    background-color: #FFFFFF;
    height: 16px;
    text-align: center;
    color: #000000;
    font-size: 11px;
}}

QProgressBar::chunk {{
    background: {_PROGRESS_CHUNK};
    border: 1px solid #1E7A1E;
}}

/* ===== Tooltips ===== */
QToolTip {{
    background-color: #FFFFE1;
    color: #000000;
    border: 1px solid #000000;
    padding: 4px 6px;
    font-size: 12px;
}}

/* ===== Splitter ===== */
QSplitter::handle {{
    background-color: {XP_BORDER};
    width: 2px;
}}

/* ===== Menu ===== */
QMenu {{
    background-color: #FFFFFF;
    border: 1px solid {XP_BORDER};
    padding: 2px;
}}

QMenu::item {{
    color: #000000;
    padding: 6px 26px;
    font-size: 13px;
}}

QMenu::item:selected {{
    background-color: {XP_ACCENT};
    color: #FFFFFF;
}}

QMenu::separator {{
    background-color: {XP_BORDER};
    height: 1px;
    margin: 3px 8px;
}}

/* ===== Dialog ===== */
QDialog {{
    background-color: {XP_BEIGE};
}}

/* ===== About Dialog ===== */
#aboutVersion {{
    font-size: 15px;
    font-weight: bold;
    color: {XP_ACCENT};
    padding: 2px;
}}

#aboutDesc {{
    font-size: 12px;
    color: #404040;
    padding: 4px 12px;
}}

#aboutLicense {{
    font-size: 10px;
    color: #808080;
    padding: 2px;
}}

/* ===== Message Box ===== */
QMessageBox {{
    background-color: {XP_BEIGE};
}}

/* ===== Tab Widget ===== */
QTabWidget::pane {{
    border: 1px solid {XP_BORDER};
    border-radius: 4px;
    background-color: #FFFFFF;
}}

QTabBar::tab {{
    background: {_BTN_BEIGE};
    border: 1px solid {XP_BORDER};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 14px;
    margin-right: 2px;
    color: #000000;
}}

QTabBar::tab:selected {{
    background-color: #FFFFFF;
    border-top: 2px solid {XP_ACCENT};
    color: {XP_BLUE_DARK};
    font-weight: bold;
}}
"""
