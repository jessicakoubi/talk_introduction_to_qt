# No shebang line. This file is meant to be imported
"""
Interface with a text field, a text and a button.
"""

# standard imports
import logging
import sys

# third-party imports
from PySide6 import QtWidgets, QtGui

# logger
_log = logging.getLogger(__name__)
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
_log.addHandler(_log_handler)
_log.setLevel("INFO")

# constants


class PopupWin(QtWidgets.QMainWindow):
    def __init__(self, *args):
        """Initialize the QMainWindow"""
        super(PopupWin, self).__init__(*args)

        self.setWindowTitle("Pop-up Example UI")
        self.resize(150, 50)

        # Create a layout to put the widgets in
        main_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)

        # Create a QWidget, assign its layout to be the one we jsut created then
        # set it as the main widget of the window.
        main_wid = QtWidgets.QWidget()
        main_wid.setLayout(main_lay)
        self.setCentralWidget(main_wid)

        run_btn = QtWidgets.QPushButton("Run")
        main_lay.addWidget(run_btn)

        run_btn.pressed.connect(self.run)

    def run(self):
        """Get the input field and display it on the label"""

        # Create a QMessageBox witha  title and text
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText("Data not saved.")
        msg_box.setInformativeText(
            "The current data hasn't been saved. Do you want to save it before proceeding ?"
        )
        # Add buttons to it so we cna choose between multiple actions based on the
        # user choice.
        msg_box.setStandardButtons(
            QtWidgets.QMessageBox.Save
            | QtWidgets.QMessageBox.Ignore
            | QtWidgets.QMessageBox.Cancel
        )
        msg_box.setDefaultButton(QtWidgets.QMessageBox.Save)

        # Execute the QMessageBox and get its user input result.
        answer = msg_box.exec_()

        if answer == QtWidgets.QMessageBox.Cancel:
            return
        elif answer == QtWidgets.QMessageBox.Save:
            print("Data saved")

        print("Do stuff")


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    window = PopupWin()
    window.show()

    exit_code = app.exec_()
    sys.exit(exit_code)
