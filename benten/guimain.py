import argparse
import sys
import pathlib

from PySide2.QtGui import QCloseEvent, QIcon
from PySide2.QtWidgets import QAction, QActionGroup, QApplication, QMainWindow, QMessageBox

from .sbg.jsonimport import if_json_convert_to_yaml_and_save
from .gui.mainwindow import MainWindow

import logging
logger = logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('cwl', help="Path to CWL document")
    parser.add_argument('-v', action='count', help="Verbosity level")

    args = parser.parse_args()

    if args.v is not None:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    QApplication.setDesktopSettingsAware(True)
    app = QApplication(sys.argv)

    app.setApplicationDisplayName("Benten")
    app.setWindowIcon(QIcon(str(pathlib.Path(pathlib.Path(__file__).parent, "benten-icon.png"))))

    f_path = pathlib.Path(args.cwl)
    if f_path.exists():
        f_path = if_json_convert_to_yaml_and_save(f_path, strip_sbg_tags=True)

    window = MainWindow(file_path=f_path)
    window.show()

    # Window dimensions
    # on macOS this causes the jumping window bug: https://bugreports.qt.io/browse/PYSIDE-941
    # geometry = app.desktop().availableGeometry()
    # window.setBaseSize(geometry.width() * 0.8, geometry.height() * 0.7)

    # # Load the file AFTER the geometry is set ...
    # path_str = args.cwl
    # path = pathlib.Path(path_str)
    # if not path.exists():
    #     with open(path, "w") as f:
    #         pass
    # window.tab_widget.open_document(path, None)
    # window.setWindowTitle(str(path.absolute()))

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
