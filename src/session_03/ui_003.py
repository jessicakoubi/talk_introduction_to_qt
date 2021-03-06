# No shebang line. This file is meant to be imported
"""
Interface around a basic curve filtering function.
"""

# standard imports
import sys
import os
import logging
import random

# third-party imports
from PySide2 import QtWidgets, QtGui, QtCore

# internal imports
import core

# logger
_log = logging.getLogger(__name__)
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
_log.addHandler(_log_handler)
_log.setLevel("INFO")

# constants

class CurveFiltererWin(QtWidgets.QMainWindow):
    def __init__(self, *args):
        super(CurveFiltererWin, self).__init__(*args)

        # Define the variable that will hold the values before they get filtered. We
        # start with a random sampling of 25 values between 25.0 and 155.0 for demo
        # purpose.
        self.raw_values = [random.uniform(25.0, 155.0) for x in range(25)]

        # Set the application title and size.
        self.setWindowTitle("Curve Filterer")
        self.resize(600, 550)

        # Create the main layout and widget that will contain the various sections
        # of our UI.
        main_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_wid = QtWidgets.QWidget()
        main_wid.setLayout(main_lay)
        self.setCentralWidget(main_wid)

        # Create the UI sections in their own separate functions for better lisibility
        self.create_intensity_layout(main_lay)
        self.create_preview_layout(main_lay)

    def create_intensity_layout(self, parent_layout):
        """Create the intensity layout.

        :param QLayout parent_layout:
            Layout to parent to
        """

        intensity_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        intensity_lay.setContentsMargins(10, 10, 10, 10)
        intensity_wid = QtWidgets.QWidget()
        intensity_wid.setLayout(intensity_lay)
        parent_layout.addWidget(intensity_wid)

        # Intensity labels. We want to display those above the actual sliders and we use the spacers
        # so they line-up to the slider  extremities fow low and high while the medium stay at the
        # center even if the mmain window width change.
        intensity_labels_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        intensity_labels_lay.setContentsMargins(0, 0, 0, 0)
        intensity_labels_wid = QtWidgets.QWidget()
        intensity_labels_wid.setLayout(intensity_labels_lay)
        intensity_lay.addWidget(intensity_labels_wid)

        low_intensity_label = QtWidgets.QLabel(self)
        low_intensity_label.setText("Low")
        low_intensity_label.setToolTip("Low Intensity")
        intensity_labels_lay.addWidget(low_intensity_label)

        intensity_label_spacer_a = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        intensity_labels_lay.addItem(intensity_label_spacer_a)

        mid_intensity_label = QtWidgets.QLabel(self)
        mid_intensity_label.setText("Medium")
        mid_intensity_label.setToolTip("Medium Intensity")
        intensity_labels_lay.addWidget(mid_intensity_label)

        intensity_label_spacer_b = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        intensity_labels_lay.addItem(intensity_label_spacer_b)

        high_intensity_label = QtWidgets.QLabel(self)
        high_intensity_label.setText("High")
        high_intensity_label.setToolTip("High Intensity")
        intensity_labels_lay.addWidget(high_intensity_label)

        # Intensity slider
        self.intensity_slider = QCurveIntensitySlider(QtCore.Qt.Horizontal, self)
        intensity_lay.addWidget(self.intensity_slider)

        # Set a default value.
        self.intensity_slider.setValue(25)

    def create_preview_layout(self, parent_layout):
        """Create the curve preview layout.

        :param QLayout parent_layout:
            Layout to parent to
        """

        preview_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        preview_lay.setSpacing(0)
        preview_wid = QtWidgets.QWidget()
        preview_wid.setLayout(preview_lay)
        parent_layout.addWidget(preview_wid)

        # Add a random backgroudn to see the widget in the UI for demo purpose.
        preview_wid.setStyleSheet("background-color: rgb({}, {}, {});".format(45, 14, 123))

        preview_spline_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        preview_spline_lay.setContentsMargins(10, 10, 10, 10)
        preview_spline_wid = QtWidgets.QWidget()
        # Set a fixed height so the QCurvvePreviewer widget gets drawn in a fixed area
        # when it comes to its height.
        preview_spline_wid.setFixedHeight(200)
        preview_spline_wid.setLayout(preview_spline_lay)
        preview_lay.addWidget(preview_spline_wid)

        left_spacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        preview_spline_lay.addItem(left_spacer)

        self.spline_preview_wid = QCurvvePreviewer()
        preview_spline_lay.addWidget(self.spline_preview_wid)

        right_spacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        preview_spline_lay.addItem(right_spacer)

        bottom_spacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding
        )
        preview_lay.addItem(bottom_spacer)


class QCurveIntensitySlider(QtWidgets.QSlider):
    """
    QSlider with a custom background and handle to display intensity.
    """

    def __init__(self, *args):
        super(QCurveIntensitySlider, self).__init__(*args)


class QCurvvePreviewer(QtWidgets.QWidget):
    """
    Widget that paint two curve. One that represent the raw pre-filtered data
    and the second that represent the curve after being filtered.
    """

    def __init__(self, values=None, filtered_values=None, parent=None):
        super(QCurvvePreviewer, self).__init__(parent)

        self._values = values
        self._filtered_values = filtered_values


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    # Initialize and show the QMainWindow.
    window = CurveFiltererWin()
    window.show()

    exit_code = app.exec_()
    sys.exit(exit_code)
