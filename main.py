"""
多源报告汇总推送工具 (Multi-Source Report Aggregation Tool)

A Windows desktop application for aggregating reports from multiple sources
including consulting firms, brokerage research, customs data, grey literature,
preprints, Sci-Hub, and Library Genesis.

Entry point: python main.py

Packaging with PyInstaller:
    pyinstaller --onefile --windowed --add-data "resources;resources" main.py

Requirements:
    pip install -r requirements.txt
"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    # High DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("多源报告汇总推送工具")

    # Set default font (XP-style Tahoma, SimSun fallback)
    font = QFont("Tahoma", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
