import os
import argparse
import sys
import pathlib

from PySide2.QtCore import Qt, QDateTime, QModelIndex, QSignalBlocker, QRect, Qt, QTimeZone, Slot

from PySide2.QtWidgets import QAction, QApplication, QTabWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, \
    QHeaderView, QTabBar, QDesktopWidget, \
    QMenuBar, QMainWindow, QLineEdit, QSizePolicy, QTableView, QWidget

from benten.editor.bentenmainwidget import BentenMainWidget
from benten.editor.bentenwindow import BentenWindow

import logging
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowTitle("Benten")

        # Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("&Exit", self)
        #exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)
        file_menu.addAction(exit_action)

        # Status Bar
        # self.status = self.statusBar()
        # self.status.showMessage("Ready")

        # This needs to come before tabs are added because adding tabs triggers
        # the currentChanged signal which triggers a slot that requires this to
        # be defined
        self.active_window: BentenWindow = None

        self.tab_widget = BentenMainWidget()
        self.tab_widget.currentChanged.connect(self.breadcrumb_selected)
        self.setCentralWidget(self.tab_widget)

    @Slot()
    def exit_app(self, checked):
        sys.exit()

    def get_current_view(self):
        pass

    def open_sub_document(self):
        pass

    @Slot()
    def breadcrumb_selected(self):
        # Reload from disk
        # If no differences, nothing to do
        # If different, apply a squashed edit to bring us up to the latest version
        if self.active_window is not None:
            self.active_window.set_inactive_window()
        self.active_window = self.tab_widget.currentWidget()
        self.active_window.set_active_window()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('cwl', nargs='?', help="Path to CWL document")
    parser.add_argument('-v', action='count', help="Verbosity level")

    args = parser.parse_args()

    if args.v is not None:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # Window dimensions
    geometry = app.desktop().availableGeometry()
    window.setBaseSize(geometry.width() * 0.8, geometry.height() * 0.7)

    # Load the file AFTER the geometry is set ...
    path_str = args.cwl
    if path_str is not None:
        path = pathlib.Path(path_str)
        if not path.exists():
            with open(path, "w") as f:
                pass

        window.tab_widget.open_document(path, None)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
