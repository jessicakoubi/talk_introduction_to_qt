# No shebang line. This file is meant to be imported
"""
Interface with a button that randomly change colour when pressed.
"""

# standard imports
import random
import sys
import logging

# third-party imports
from PySide2 import QtWidgets, QtGui

# logger
_log = logging.getLogger(__name__)
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
_log.addHandler(_log_handler)
_log.setLevel("INFO")

# constants


class RandButtonWin(QtWidgets.QMainWindow):
    def __init__(self, *args):
        """Initialize the QMainWindow with a QPushButton"""
        super(RandButtonWin, self).__init__(*args)

        # Set the name of our window (what the titlebar will display)
        self.setWindowTitle("Random Button Colour UI")

        # Set the size of our window.
        self.resize(150, 50)

        # Create a button.
        run_btn = QtWidgets.QPushButton("Run", self)


if __name__ == "__main__":

    # Create a QApplication to handle our QMainWindow. This is requiered if you
    # create any QWidget-based application.
    app = QtWidgets.QApplication(sys.argv)

    window = RandButtonWin()

    # Display the new QMainWindow instance we created.
    window.show()

    # Execute the QApplication
    exit_code = app.exec_()
    sys.exit(exit_code)
