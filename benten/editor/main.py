import sys

from PySide2.QtCore import (QDateTime, QModelIndex,
                            QRect, Qt, QTimeZone, Slot)

from PySide2.QtWidgets import (QAction, QApplication, QPushButton, QLabel, QHBoxLayout, QVBoxLayout,
                               QHeaderView, QMenuBar,
                               QMainWindow, QLineEdit, QSizePolicy, QTableView, QWidget)

from benten.editor.codeeditor import CodeEditor
from benten.editor.processdiagram import ProcessDiagramView


class BentenWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.code_editor = CodeEditor()
        self.workflow_map = ProcessDiagramView(self)
        self.command_bar = QLineEdit(self)
        self.inbound_conn_table = QTableView(self)
        self.outbound_conn_table = QTableView(self)

        conn_panes = QHBoxLayout()
        conn_panes.addWidget(self.inbound_conn_table)
        conn_panes.addWidget(self.outbound_conn_table)

        horiz_panes = QVBoxLayout()
        horiz_panes.addWidget(self.workflow_map)
        horiz_panes.addWidget(self.command_bar)
        horiz_panes.addLayout(conn_panes)

        vertical_panes = QHBoxLayout()
        vertical_panes.addLayout(horiz_panes)
        vertical_panes.addWidget(self.code_editor)

        self.setLayout(vertical_panes)


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

        self.setCentralWidget(BentenWindow())

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
