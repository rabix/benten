import os
import argparse
import sys
import pathlib

from PySide2.QtCore import Qt, QDateTime, QModelIndex, QSignalBlocker, QRect, Qt, QTimeZone, Slot

from PySide2.QtWidgets import QAction, QApplication, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QHeaderView, \
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

        self.benten_window = BentenWindow()
        self.setCentralWidget(self.benten_window)
        self.benten_window.code_editor.setFocus()

        if path_str is not None:
            path = pathlib.Path(path_str)

            if not path.exists():
                with open(path, "w") as f:
                    pass

            self.benten_window.load(path)
            self.setWindowTitle("Benten: {}".format(path_str))

    @Slot()
    def exit_app(self, checked):
        sys.exit()


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
