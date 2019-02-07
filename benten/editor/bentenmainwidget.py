"""This manages the tabs that we open as part of inspecting workflow steps. It also
manages the synchronization between the windows since the code is interdependent in one
way or the other"""

from PySide2.QtCore import Qt, QDateTime, QModelIndex, QSignalBlocker, QRect, Qt, QTimeZone, Slot

from PySide2.QtWidgets import QAction, QApplication, QTabWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, \
    QHeaderView, QTabBar, \
    QMenuBar, QMainWindow, QLineEdit, QSizePolicy, QTableView, QWidget

from benten.editing.cwldoc import CwlDoc
from benten.editor.bentenwindow import BentenWindow
from benten.editor.multidocumentmanager import MultiDocumentManager


class BentenMainWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.multi_document_manager = MultiDocumentManager()
        self.active_window: BentenWindow = None

        self.setTabsClosable(True)
        self._make_base_tab_unclosable()

        self.currentChanged.connect(self.breadcrumb_selected)

    def _make_base_tab_unclosable(self):
        tbl = self.tabBar().tabButton(0, QTabBar.LeftSide)
        tbr = self.tabBar().tabButton(0, QTabBar.RightSide)
        if tbl is not None:
            tbl.hide()
        if tbr is not None:
            tbr.hide()

    def open_document(self, parent_path: str, inline_path: [str]):
        bw = self.multi_document_manager.open_window(parent_path, inline_path)
        for idx in range(self.count()):
            if self.widget(idx) == bw:
                self.setCurrentIndex(idx)
        else:
            self.addTab(bw, "Some clever name")

    @Slot()
    def breadcrumb_selected(self):
        # Reload from disk
        # If no differences, nothing to do
        # If different, apply a squashed edit to bring us up to the latest version
        if self.active_window is not None:
            self.active_window.set_inactive_window()
        self.active_window = self.currentWidget()
        self.active_window.set_active_window()

        print(self.currentIndex())
