# No shebang line. This file is meant to be imported
"""
Interface with a text field, a text and a button.
"""

# standard imports
import logging
import sys
import os

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

# Path to the icons relative to the current module location.
_ICONS_PATH = os.path.join(os.path.dirname(__file__), "icons")


class PrintFieldWin(QtWidgets.QMainWindow):
    def __init__(self, *args):
        """Initialize the QMainWindow"""
        super(PrintFieldWin, self).__init__(*args)

        self.setWindowTitle("Text Field Example UI")
        self.resize(150, 50)

        self.create_menu()

        # Create a layout to put the widgets in
        main_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)

        # Create a QWidget, assign its layout to be the one we jsut created then
        # set it as the main widget of the window.
        main_wid = QtWidgets.QWidget()
        main_wid.setLayout(main_lay)
        self.setCentralWidget(main_wid)

        # Create a text field.
        self.text_le = QtWidgets.QLineEdit()
        main_lay.addWidget(self.text_le)

        # Create a label to display the resulting text.
        self.result_label = QtWidgets.QLabel()
        main_lay.addWidget(self.result_label)

        run_btn = QtWidgets.QPushButton("Run")
        main_lay.addWidget(run_btn)

        run_btn.pressed.connect(self.run)

    def create_menu(self):

        # Add a menu to the QMainWindow menu-bar.
        file_menu = self.menuBar().addMenu("File")

        # Add an action to the File menu that close the QMainWindow
        # We also add an icon, a tool-tip and shortcut.
        close_icon_path = os.path.join(_ICONS_PATH, "close.png")
        close_action = QtWidgets.QAction(
            QtGui.QIcon(close_icon_path), "Close", file_menu
        )
        close_action.setStatusTip("Close Interface.")
        close_action.setShortcut("Ctrl+Q")
        file_menu.addAction(close_action)
        close_action.triggered.connect(self.close)

    def run(self):
        """Get the input field and display it on the label"""

        # Get the text currently set in the self.text_le QLineEdit.
        input_text = self.text_le.text()

        # Create the text to display.
        text = f"The input was {input_text}"

        # Set the text in the self.result_label QLabel.
        self.result_label.setText(text)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    window = PrintFieldWin()
    window.show()

    exit_code = app.exec_()
    sys.exit(exit_code)
