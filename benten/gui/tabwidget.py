"""This manages the tabs that we open as part of inspecting workflow steps. Any state that is not
isolated to one CWL object/sub-object is managed here"""
from typing import Tuple, List, Dict, Union
import pathlib

from PySide2.QtWidgets import QTabWidget, QTabBar, QMessageBox
from PySide2.QtCore import Slot
from PySide2.QtGui import QCloseEvent

from ..sbg.profiles import Profiles, Configuration
from .cwldoc import CwlDoc

from .view.viewwidget import ViewWidget

import logging
logger = logging.getLogger(__name__)


class TabWidget(QTabWidget):
    def __init__(self, file_path: pathlib.Path, config: Configuration, parent=None):
        super().__init__(parent)

        self.config = config
        self.setDocumentMode(True)  # This is perfect!
        self.setMovable(True)
        self.setUsesScrollButtons(True)

        self.sbg_profiles = Profiles(config=config)

        self.api = None
        self.doc_directory: Dict[str, CwlDoc] = {}

        # self.tab_directory: Dict[str, Dict[Union[Tuple[str], None], BentenWindow]] = {}
        self.active_window: ViewWidget = None

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.tab_about_to_close)

        self.currentChanged.connect(self.tab_selected)

        self.open_linked_file(file_path=file_path)

    @Slot(str)
    def profile_selected(self, profile):
        self.api = self.sbg_profiles[profile]
        logger.debug("Profile set to: {}".format(profile))

    @Slot()
    def save(self):
        pass

    @Slot(int)
    def tab_about_to_close(self, index):
        pass

    def ok_to_close_everything(self, event: QCloseEvent):
        logger.debug("Closing Benten")
        unsaved_root_docs = [doc for doc in self.doc_directory.values() if not doc.saved()]
        if len(unsaved_root_docs):
            return self._unsaved_changes_dialog(unsaved_root_docs)
        else:
            return True

    @Slot()
    def tab_selected(self):
        if self.active_window is not None:
            self.active_window.set_inactive_window()
        self.active_window = self.currentWidget()
        self.active_window.set_active_window()

    def open_linked_file(self, file_path: pathlib.Path):
        fp_str = file_path.resolve().as_uri()
        if fp_str not in self.doc_directory:
            vw = ViewWidget(config=self.config)
            self._create_file_if_needed(file_path)
            self.doc_directory[fp_str] = CwlDoc(file_path=file_path, editor=vw)
            self.addTab(vw, "...")

            if self.count() == 1:
                self._make_base_tab_unclosable()

        self.setCurrentWidget(self.doc_directory[fp_str].root_view.attached_editor)
        # self._refresh_tab_titles()


    #
    # Ugly helper functions
    #

    def _make_base_tab_unclosable(self):
        tbl = self.tabBar().tabButton(0, QTabBar.LeftSide)
        tbr = self.tabBar().tabButton(0, QTabBar.RightSide)
        if tbl is not None:
            tbl.hide()
        if tbr is not None:
            tbr.hide()

    def _unsaved_changes_dialog(self, doc_l: List[CwlDoc]):
        plural = "documents" if len(doc_l) > 1 else "document"
        button = QMessageBox.warning(
            self, "Unsaved changes!",
            "There are unsaved changes in your {}. Do you wish to save?".format(plural),
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Cancel)
        if button == QMessageBox.Cancel:
            return False
        elif button == QMessageBox.Discard:
            return True
        else:
            for doc in doc_l:
                doc.save()
            return True

    @staticmethod
    def _create_file_if_needed(file_path: pathlib.Path):
        if file_path.exists():
            return
        else:
            with open(file_path, "w") as f:
                pass
