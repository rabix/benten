"""This manages the tabs that we open as part of inspecting workflow steps. Any state that is not
isolated to one CWL object/sub-object is managed here"""
from typing import Tuple, List, Dict, Union, Callable
import pathlib

from PySide2.QtWidgets import QTabWidget, QTabBar, QMessageBox
from PySide2.QtCore import Slot
from PySide2.QtGui import QCloseEvent

from ..sbg.jsonimport import if_json_convert_to_yaml_and_save

from ..editing.rootyamlview import RootYamlView, YamlView, TextView
from ..sbg.profiles import Profiles, Configuration
from ..models.workflow import Step, InvalidSub, InlineSub, ExternalSub

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
        self.view_directory: Dict[str, ViewWidget] = {}
        # Because we often need to find a ViewWidget by path

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
        self.currentWidget().save()

    @Slot(int)
    def tab_about_to_close(self, index):
        # todo: logic to remove child views to save computation
        # todo: currently we never actually delete a tab ...
        self.removeTab(index)

    def ok_to_close_everything(self, event: QCloseEvent):
        logger.debug("Closing Benten")
        unsaved_root_docs = [tab.view for tab in self.view_directory.values() if not tab.view.saved()]
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

    @Slot(object)
    def open_steps(self, data: Tuple[YamlView, List[Step]]):
        yaml_view, steps = data
        for step in steps:
            sub = step.sub_workflow
            if isinstance(sub, InvalidSub):
                continue
            elif isinstance(sub, InlineSub):
                self.open_inline_section(yaml_view, sub.inline_path)
            elif isinstance(sub, ExternalSub):
                self.open_linked_file(sub.path)
            else:
                raise RuntimeError("Code error: Unknown sub workflow type!")

    def open_linked_file(self, file_path: pathlib.Path):
        fp_str = file_path.resolve().as_uri()
        if fp_str not in self.view_directory:
            file_path = if_json_convert_to_yaml_and_save(file_path, strip_sbg_tags=True)
            fp_str = file_path.resolve().as_uri()

            vw = self._prepare_view_widget()

            if file_path.exists():
                raw_text = file_path.open("r").read()
            else:
                raw_text = ""

            vw.set_view(RootYamlView(
                raw_text=raw_text,
                file_path=file_path))

            self.view_directory[fp_str] = vw
            self.addTab(vw, file_path.name)

            if self.count() == 1:
                self._make_base_tab_unclosable()

        vw = self.view_directory[fp_str]

        self.setCurrentWidget(vw)

    def open_inline_section(self, yaml_view: YamlView, inline_path: Tuple[str, ...]):
        if yaml_view.yaml_error is not None:
            logger.warning("Editor is locked, can not navigate away")
            return

        fp_str = ":".join(yaml_view.root().file_path.resolve().as_uri() + yaml_view.inline_path + inline_path)
        if fp_str not in self.view_directory:
            vw = self._prepare_view_widget()
            vw.set_view(yaml_view.create_child_view(
                child_path=inline_path,
                can_have_children=True))  # todo: figure out logic around this

            self.view_directory[fp_str] = vw

        vw = self.view_directory[fp_str]

        if vw not in self:
            self.addTab(vw, vw.view.readable_path())

        self.setCurrentWidget(vw)

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

    def _unsaved_changes_dialog(self, doc_l: List[TextView]):
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

    def _prepare_view_widget(self):
        vw = ViewWidget(config=self.config)
        vw.open_steps.connect(self.open_steps)
        return vw

    def __contains__(self, item):
        for idx in range(self.count()):
            if item == self.widget(idx):
                return True
        else:
            return False
