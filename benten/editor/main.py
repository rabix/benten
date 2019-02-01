import sys
import pathlib

from PySide2.QtCore import Qt, QDateTime, QModelIndex, QSignalBlocker, QRect, Qt, QTimeZone, Slot

from PySide2.QtWidgets import QAction, QApplication, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QHeaderView, \
    QMenuBar, QMainWindow, QLineEdit, QSizePolicy, QTableView, QWidget

from benten.editor.bentenwindow import BentenWindow


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
        self.status = self.statusBar()
        self.status.showMessage("Ready")

        # Window dimensions
        # geometry = app.desktop().availableGeometry(self)
        # self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)

        self.benten_window = BentenWindow()
        self.setCentralWidget(self.benten_window)
        self.benten_window.code_editor.setFocus()

        self.centralWidget().load(pathlib.Path("/Users/kghose/Work/code/benten/tests/cwl/sbg/salmon.cwl"))

    @Slot()
    def exit_app(self, checked):
        sys.exit()


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
