from PySide2.QtCore import QTimer

import logging
logger = logging.getLogger(__name__)


class ManualEditThrottler:
    """Each manual edit we do (letter we type) triggers a manual edit. We need to manage
    these calls so they don't overwhelm the system and yet not miss out on the final edit in
    a burst of edits. This manager handles that job effectively."""

    def __init__(self, burst_window):
        self.burst_window = burst_window
        # We allow upto a <burst_window> pause in typing before parsing the edit
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(int(self.burst_window * 1000))
        logger.debug("Burst window set to {}s".format(self.burst_window))

    def restart_edit_clock(self):
        logger.debug("User still typing ...")
        self.timer.start()

    def flush(self):
        if self.timer.isActive():
            self.timer.stop()
            self.timer.timeout.emit()
