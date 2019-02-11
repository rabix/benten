"""This manages the tabs that we open as part of inspecting workflow steps. It also
manages the synchronization between the windows since the code is interdependent in one
way or the other"""
from typing import Tuple
import pathlib

from PySide2.QtCore import Qt, QDateTime, QModelIndex, QSignalBlocker, QRect, Qt, QTimeZone, Slot

from PySide2.QtWidgets import QAction, QApplication, QTabWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, \
    QHeaderView, QTabBar, \
    QMenuBar, QMainWindow, QLineEdit, QSizePolicy, QTableView, QWidget

from benten.editing.cwldoc import CwlDoc
from benten.models.workflow import InvalidSub, InlineSub, ExternalSub
from benten.editor.bentenwindow import BentenWindow
from benten.editor.multidocumentmanager import MultiDocumentManager


class BentenMainWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.multi_document_manager = MultiDocumentManager()
        self.active_window: BentenWindow = None

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.removeTab)

        self.currentChanged.connect(self.breadcrumb_selected)

    def _make_base_tab_unclosable(self):
        tbl = self.tabBar().tabButton(0, QTabBar.LeftSide)
        tbr = self.tabBar().tabButton(0, QTabBar.RightSide)
        if tbl is not None:
            tbl.hide()
        if tbr is not None:
            tbr.hide()

    def open_document(self, parent_path: pathlib.Path, inline_path: Tuple[str, ...]):
        bw = self.multi_document_manager.open_window(parent_path, inline_path)
        for idx in range(self.count()):
            if self.widget(idx) == bw:
                self.setCurrentIndex(idx)
        else:
            tab_name = ".".join(inline_path) if inline_path else "root"
            bw.scene_double_clicked.connect(self.scene_double_clicked)
            bw.edit_registered.connect(self.edit_registered)
            self.setCurrentIndex(self.addTab(bw, tab_name))

        if self.count() == 1:
            self._make_base_tab_unclosable()

    @Slot()
    def breadcrumb_selected(self):
        if self.active_window is not None:
            self.active_window.set_inactive_window()
        self.active_window = self.currentWidget()
        self.active_window.set_active_window()

    @Slot(object)
    def scene_double_clicked(self, sub_workflows):
        for sub in sub_workflows:
            if isinstance(sub, InvalidSub):
                continue
            elif isinstance(sub, InlineSub):
                self.open_document(sub.path, sub.inline_path)
            elif isinstance(sub, ExternalSub):
                self.open_document(sub.path, None)
            else:
                raise RuntimeError("Code error: Unknown sub workflow type!")

    @Slot(object)
    def edit_registered(self, cwl_doc):
        self.multi_document_manager.nested_document_edited(cwl_doc=cwl_doc)
