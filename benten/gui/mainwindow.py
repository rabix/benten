import pathlib
import sys

from PySide2.QtWidgets import QAction, QActionGroup, QApplication, QMainWindow, QMessageBox
from PySide2.QtCore import QSettings, Slot
from PySide2.QtGui import QCloseEvent, QIcon

import qdarkstyle

from ..version import __version__
from ..configuration import Configuration
from ..sbg.profiles import Profiles
from .tabwidget import TabWidget
from .view.viewwidget import ViewWidget


class MainWindow(QMainWindow):

    def __init__(self, file_path: pathlib.Path):
        QMainWindow.__init__(self)

        self.config = Configuration()

        if self.config.getboolean("qt", "dark_theme"):
            QApplication.instance().setStyleSheet(qdarkstyle.load_stylesheet())

        # todo: figure out how to write to specific file
        self.settings = QSettings("sbg", "benten-dev")
        #self.settings = QSettings(str(self.config.getpath("qt", "settings_file").absolute()))
        # self.settings = QSettings("file")
        # self.settings = QSettings(fileName="eraseme.ini")
        # print(self.settings.fileName())
        geometry = self.settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        else:
            self.resize(800, 600)  # default size

        # This needs to come before tabs are added because adding tabs triggers
        # the currentChanged signal which triggers a slot that requires this to
        # be defined
        self.active_window: ViewWidget = None

        self.tab_widget = TabWidget(file_path=file_path, config=self.config)
        # This comes after creating BentenMainWidget because we connect some menu actions
        # directly to it
        self._setup_main_menu()

        self.setCentralWidget(self.tab_widget)

    def _setup_main_menu(self):

        # An epic can be written about the confusing behavior of menus on macOS, but the main
        # reading material is https://doc.qt.io/qt-5/qmenubar.html#qmenubar-as-a-global-menu-bar

        # Main menu
        menu = self.menuBar()

        file_menu = menu.addMenu("Program")

        # Exit QAction
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        def _about_dialog():
            QMessageBox.about(self, "Benten {}".format(__version__),
                              "This is a workflow helper for "
                              "Common Workflow Language documents.\n"
                              "See https://github.com/rabix/benten for details.")

        about_action = QAction("&About", self)
        about_action.triggered.connect(_about_dialog)
        file_menu.addAction(about_action)

        self._add_profile_menu(menu)
        self._add_file_menu(menu)

        # menu.setNativeMenuBar(False) # We actually don't want this, native mac is ... nicer

    def _add_profile_menu(self, menu):
        profile_list = Profiles(config=self.config).profiles

        if len(profile_list) == 0:
            return

        prof_menu = menu.addMenu("SBG &profile")
        prof_action_group = QActionGroup(prof_menu)
        for prof_name in profile_list:
            action = QAction(prof_name, prof_menu)
            action.setCheckable(True)
            prof_action_group.addAction(action)
            prof_menu.addAction(action)  # Apparently we still need to add these

        def _profile_selected(_action: QAction):
            prof_menu.setTitle(_action.text())
            self.tab_widget.profile_selected(_action.text())

        prof_action_group.triggered.connect(_profile_selected)
        prof_action_group.actions()[0].setChecked(True)
        _profile_selected(prof_action_group.actions()[0])

    def _add_file_menu(self, menu):
        file_menu = menu.addMenu("File")

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.tab_widget.save)
        file_menu.addAction(save_action)

    def closeEvent(self, event: QCloseEvent):
        if self.tab_widget.ok_to_close_everything(event):
            self.settings.setValue("geometry", self.saveGeometry())
            event.accept()
        else:
            event.ignore()
        # super().closeEvent(event)

    # @Slot()
    # def exit_app(self, checked):
    #     sys.exit()
