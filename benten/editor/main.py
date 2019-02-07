import os
import argparse
import sys
import pathlib

from PySide2.QtCore import Qt, QDateTime, QModelIndex, QSignalBlocker, QRect, Qt, QTimeZone, Slot

from PySide2.QtWidgets import QAction, QApplication, QTabWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, \
    QHeaderView, QTabBar, \
    QMenuBar, QMainWindow, QLineEdit, QSizePolicy, QTableView, QWidget

from benten.editor.bentenwindow import BentenWindow


class MainWindow(QMainWindow):
    def __init__(self, path_str=None):
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
        self.status = self.statusBar()
        self.status.showMessage("Ready")

        # Window dimensions
        # geometry = app.desktop().availableGeometry(self)
        # self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)

        # This needs to come before tabs are added because adding tabs triggers
        # the currentChanged signal which triggers a slot that requires this to
        # be defined
        self.active_window: BentenWindow = None

        self.tab_widget = QTabWidget()
        # https://stackoverflow.com/questions/18022290/qt5-align-osx-qtabwidget-left
        self.tab_widget.setTabsClosable(True)

        # https://stackoverflow.com/questions/18022290/qt5-align-osx-qtabwidget-left
        # Setting stylesheet removes close buttons
        # self.tab_widget.setStyleSheet("QTabWidget::tab-bar {alignment: left; };"
        #                               "QTabWidget::tab-bar::closeButton {position: right;}")

        self.setCentralWidget(self.tab_widget)

        b1 = BentenWindow()
        if path_str is not None:
            path = pathlib.Path(path_str)

            if not path.exists():
                with open(path, "w") as f:
                    pass

            b1.load(path)
            self.setWindowTitle("Benten: {}".format(path_str))

        self.tab_widget.currentChanged.connect(self.breadcrumb_selected)

        self.tab_widget.addTab(b1, "Benten")
        self.tab_widget.tabBar().tabButton(0, QTabBar.LeftSide).hide()

        self.tab_widget.addTab(BentenWindow(), "Remove this benten")

        # self.active_window: BentenWindow = self.tab_widget.currentWidget()
        # self.active_window.code_editor.setFocus()


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

        print(self.tab_widget.currentIndex())


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('cwl', nargs='?', help="Path to CWL document")
    parser.add_argument('-v', action='count', help="Verbosity level")

    args = parser.parse_args()

    app = QApplication(sys.argv)

    window = MainWindow(path_str=args.cwl)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
