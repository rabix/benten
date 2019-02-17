import argparse
import sys
import pathlib

from PySide2.QtCore import QSettings, Slot
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QAction, QActionGroup, QApplication, QMainWindow

from .configuration import Configuration
from .gui.bentenmainwidget import BentenMainWidget
from .gui.bentenwindow import BentenWindow
from .sbg.profiles import Profiles

import logging
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.resize(800, 600)  # default size
        settings = QSettings("sbg", "benten")
        geometry = settings.value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        # This needs to come before tabs are added because adding tabs triggers
        # the currentChanged signal which triggers a slot that requires this to
        # be defined
        self.active_window: BentenWindow = None

        config = Configuration()
        sbg_profiles = Profiles(config=config)

        self.tab_widget = BentenMainWidget(config=Configuration())
        # This comes after creating BentenMainWidget because we connect some menu actions
        # directly to it
        self._setup_main_menu(config, sbg_profiles)

        self.tab_widget.currentChanged.connect(self.breadcrumb_selected)
        self.setCentralWidget(self.tab_widget)

    def _setup_main_menu(self, config, sbg_profiles):

        # An epic can be written about the confusing behavior of menus on macOS, but the main
        # reading material is https://doc.qt.io/qt-5/qmenubar.html#qmenubar-as-a-global-menu-bar

        # Main menu
        menu = self.menuBar()

        file_menu = menu.addMenu("Program")

        # Exit QAction
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)
        file_menu.addAction(exit_action)

        self._add_profile_menu(menu, sbg_profiles.profiles)
        self._add_cwl_menu(menu, sbg_profiles.profiles)

        # menu.setNativeMenuBar(False) # We actually don't want this, native mac is ... nicer

    def _add_profile_menu(self, menu, profile_list):
        if len(profile_list) == 0: return

        prof_menu = menu.addMenu("SBG &profile")
        prof_action_group = QActionGroup(prof_menu)
        for prof_name in profile_list:
            profile_action = QAction(prof_name, prof_menu)
            profile_action.setCheckable(True)
            # profile_action.changed.connect(self.tab_widget.profile_selected)
            prof_action_group.addAction(profile_action)
            prof_menu.addAction(profile_action)  # Apparently we still need to add these
        prof_action_group.actions()[0].setChecked(True)

    def _add_cwl_menu(self, menu, profile_list):
        cwl_menu = menu.addMenu("File")

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.tab_widget.cwl_save)
        cwl_menu.addAction(save_action)

        if profile_list:
            push_action = QAction("&Push", self)
            push_action.setShortcut("Ctrl+P")
            #save_action.triggered.connect(...)
            cwl_menu.addAction(push_action)

    def closeEvent(self, event: QCloseEvent):
        settings = QSettings("sbg", "benten")
        settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    @Slot()
    def exit_app(self, checked):
        sys.exit()

    @Slot(str)
    def set_title(self, title):
        self.setWindowTitle(title)

    @Slot()
    def breadcrumb_selected(self):
        if self.active_window is not None:
            self.active_window.set_inactive_window()
        self.active_window = self.tab_widget.currentWidget()
        self.active_window.set_active_window()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('cwl', nargs='?', help="Path to CWL document")
    parser.add_argument('-v', action='count', help="Verbosity level")

    args = parser.parse_args()

    if args.v is not None:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    QApplication.setDesktopSettingsAware(True)
    app = QApplication(sys.argv)
    app.setApplicationDisplayName("Benten")

    window = MainWindow()
    window.show()

    # Window dimensions
    # on macOS this causes the jumping window bug: https://bugreports.qt.io/browse/PYSIDE-941
    # geometry = app.desktop().availableGeometry()
    # window.setBaseSize(geometry.width() * 0.8, geometry.height() * 0.7)

    # Load the file AFTER the geometry is set ...
    path_str = args.cwl
    if path_str is not None:
        path = pathlib.Path(path_str)
        if not path.exists():
            with open(path, "w") as f:
                pass
        window.tab_widget.open_document(path, None)
        window.setWindowTitle(str(path.absolute()))

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
