"""This manages the tabs that we open as part of inspecting workflow steps. It also
manages the synchronization between the windows since the code is interdependent in one
way or the other"""
from typing import Tuple
import pathlib

from PySide2.QtCore import Slot, Signal

from PySide2.QtWidgets import QTabWidget, QTabBar

from ..models.workflow import InvalidSub, InlineSub, ExternalSub
from .bentenwindow import BentenWindow
from .multidocumentmanager import MultiDocumentManager

import logging

logger = logging.getLogger(__name__)


class BentenMainWidget(QTabWidget):

    need_title_change = Signal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config
        self.setDocumentMode(True)  # This is perfect!
        self.setMovable(True)
        self.setUsesScrollButtons(True)

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
            idx = self.addTab(bw, tab_name)
            self.setTabToolTip(idx, str(parent_path) + "#" + tab_name)
            self.setCurrentIndex(idx)

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
    def edit_registered(self, cwl_doc, force_save=False):
        doc_man = self.multi_document_manager.apply_document_edits(cwl_doc=cwl_doc)
        status = doc_man.status()
        # todo: warn if external edits have taken place
        if not status["saved"]:
            logger.debug("{} needs saving".format(doc_man.path))
            if self.config.getboolean("files", "autosave", fallback=False) or force_save:
                logger.debug("Saving {}".format(doc_man.path))
                doc_man.save()
        else:
            logger.debug("Document already saved")

        self._refresh_tab_titles()

    @Slot()
    def cwl_save(self):
        self.edit_registered(cwl_doc=self.active_window.cwl_doc, force_save=True)

    def _refresh_tab_titles(self):
        pass

    @Slot()
    def right_click_over_step(self):
        pass

    @Slot()
    def cwl_push_to_sbg(self):
        pass
