"""This manages the tabs that we open as part of inspecting workflow steps. It also
manages the synchronization between the windows since the code is interdependent in one
way or the other"""
from typing import Tuple, List, Dict, Union
import pathlib

from PySide2.QtCore import Slot, Signal
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QTabWidget, QTabBar, QMessageBox

from ..editing.cwlprocess import CwlProcess
from ..models.workflow import InvalidSub, InlineSub, ExternalSub
from .bentenwindow import BentenWindow
from ..sbg.profiles import Profiles
from ..sbg.jsonimport import if_json_convert_to_yaml_and_save

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

        self.sbg_profiles = Profiles(config=config)

        self.api = None
        self.tab_directory: Dict[str, Dict[Union[Tuple[str], None], BentenWindow]] = {}
        # self.multi_document_manager = MultiDocumentManager(benten_main_window=self)
        self.active_window: BentenWindow = None

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.tab_about_to_close)

        self.currentChanged.connect(self.breadcrumb_selected)

    def _make_base_tab_unclosable(self):
        tbl = self.tabBar().tabButton(0, QTabBar.LeftSide)
        tbr = self.tabBar().tabButton(0, QTabBar.RightSide)
        if tbl is not None:
            tbl.hide()
        if tbr is not None:
            tbr.hide()

    def open_document(self, parent_path: pathlib.Path, inline_path: Tuple[str, ...], step_id=None):
        parent_path_str = parent_path.resolve().as_uri()
        if parent_path_str in self.tab_directory:
            if inline_path in self.tab_directory[parent_path_str]:
                bw = self.tab_directory[parent_path_str][inline_path]
            else:
                root_bw = self.tab_directory[parent_path_str][None]
                child_cwl_process = root_bw.cwl_doc.create_child_view_from_path(inline_path)
                bw = self.tab_directory[parent_path_str][inline_path] = \
                    BentenWindow(cwl_doc=child_cwl_process, benten_main_window=self)
                bw.step_id = step_id
        else:
            new_path = if_json_convert_to_yaml_and_save(parent_path)
            if new_path is not None:
                parent_path = new_path
                parent_path_str = parent_path.resolve().as_uri()

            bw = BentenWindow(cwl_doc=CwlProcess.create_from_file(parent_path), benten_main_window=self)
            self.tab_directory[parent_path_str] = {None: bw}
            bw.step_id = step_id

        for idx in range(self.count()):
            if self.widget(idx) == bw:
                self.setCurrentIndex(idx)
        else:
            bw.scene_double_clicked.connect(self.scene_double_clicked)
            bw.edit_registered.connect(self.edit_registered)
            idx = self.addTab(bw, "...")
            self.setCurrentIndex(idx)

        if self.count() == 1:
            self._make_base_tab_unclosable()

        self._refresh_tab_titles()

    def _refresh_tab_titles(self):
        for index in range(self.count()):
            bw: BentenWindow = self.widget(index)
            cwl_doc = bw.cwl_doc
            tab_name = ".".join([x for x in ((bw.step_id,) + (cwl_doc.inline_path or ()))
                                 if x is not None] or ["root"])
            self.setTabText(index, tab_name)
            self.setTabToolTip(index, str(cwl_doc.path) +
                               (":{}".format(cwl_doc.inline_path) if cwl_doc.inline_path else ""))

    def windows_for_this_doc(self, cwl_doc):
        win_list = []
        for index in range(self.count()):
            bw = self.widget(index)
            if bw.cwl_doc.path == cwl_doc.path:
                win_list += [bw]
        return win_list

    @Slot(int)
    def tab_about_to_close(self, index):
        bw: BentenWindow = self.widget(index)
        if len(self.windows_for_this_doc(bw.cwl_doc)) == 1:
            mdmu = self.multi_document_manager.lookup_parent_doc(bw.cwl_doc)
            if not mdmu.doc_man.status()["saved"]:
                if not self.unsaved_changes_dialog([mdmu]):
                    return

        self.removeTab(index)

    def ok_to_close_everything(self, event:QCloseEvent):
        logger.debug("Closing Benten")
        unsaved_root_docs = [win[None].cwl_doc for win in self.tab_directory.values()
                             if win[None].cwl_doc.needs_saving()]
        if len(unsaved_root_docs):
            return self.unsaved_changes_dialog(unsaved_root_docs)
        else:
            return True

    def unsaved_changes_dialog(self, doc_l: List[CwlProcess]):
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

    @Slot()
    def breadcrumb_selected(self):
        if self.active_window is not None:
            self.active_window.set_inactive_window()
        self.active_window = self.currentWidget()
        self.active_window.set_active_window()

    @Slot(object)
    def scene_double_clicked(self, steps):
        for step in steps:
            sub = step.sub_workflow
            if isinstance(sub, InvalidSub):
                continue
            elif isinstance(sub, InlineSub):
                self.open_document(sub.path, sub.inline_path)
            elif isinstance(sub, ExternalSub):
                self.open_document(sub.path, None, step_id=step.id)
            else:
                raise RuntimeError("Code error: Unknown sub workflow type!")

    @Slot(object)
    def edit_registered(self, cwl_doc: CwlProcess, force_save=False):
        if cwl_doc.needs_saving():
            logger.debug("{} needs saving".format(cwl_doc.path))
            if self.config.getboolean("files", "autosave", fallback=False) or force_save:
                logger.debug("Saving {}".format(cwl_doc.path))
                cwl_doc.save()
        else:
            logger.debug("Document already saved")

        self._refresh_tab_titles()

    @Slot()
    def cwl_save(self):
        self.edit_registered(cwl_doc=self.active_window.cwl_doc, force_save=True)

    @Slot()
    def right_click_over_step(self):
        pass

    @Slot(str)
    def profile_selected(self, profile):
        self.api = self.sbg_profiles[profile]
        logger.debug("Profile set to: {}".format(profile))

    @Slot()
    def cwl_push_to_sbg(self):
        pass
