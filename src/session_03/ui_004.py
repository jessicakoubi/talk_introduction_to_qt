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

# We use this to populate both the QComboBox that determine which filter to use but also the QPlainTextEdit with a
# description of the currently selected filter.
_FILTERS = {
    "Savitzky-Golay": "The Savitzky-Golay is a type of low-pass filter, particularly suited for smoothing noisy data.",
    "Mean Average": "Sum of the key values divided by the number of keys.",
    "Gaussian": "One-dimensional Gaussian filter. This is a very agressive filter that can remove a lot of noise.",
    "Moving Average": "Average each key value based on it's surrounding values.",
}

# Path to the icons relative to the current module location.
_ICONS_PATH = os.path.join(os.path.dirname(__file__), "icons")


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
        self.create_options_layout(main_lay)

        self.filter_type_cb.currentIndexChanged[int].connect(
            self.update_filter_description
        )

        # We call the filter description in the session 3 only to display
        # the description for the first entry when we launch the UI.
        self.update_filter_description()

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

    def create_options_layout(self, parent_layout):
        """Create the options layout.

        :param QLayout parent_layout:
            Layout to parent to
        """

        options_bar_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        options_bar_lay.setContentsMargins(10, 0, 0, 0)
        options_bar_lay.setSpacing(0)
        options_bar_wid = QtWidgets.QWidget()
        options_bar_wid.setFixedHeight(20)
        options_bar_wid.setLayout(options_bar_lay)
        parent_layout.addWidget(options_bar_wid)

        # Change the color of the option bar to be a lighter then other widgets.
        options_bar_wid.setAutoFillBackground(True)
        palette = options_bar_wid.palette()
        palette.setColor(QtGui.QPalette.Window, palette.window().color().lighter())
        options_bar_wid.setPalette(palette)

        # Create a button that we will use to show/hide the options.
        self.options_bar_button = QtWidgets.QPushButton()
        self.options_bar_button.setText("+")
        self.options_bar_button.setToolTip("Show/Hide the smoothing options.")
        self.options_bar_button.setFixedWidth(25)
        self.options_bar_button.setFlat(True)
        options_bar_lay.addWidget(self.options_bar_button)

        options_bar_label = QtWidgets.QLabel(self)
        options_bar_label.setText("Options")
        options_bar_label.setToolTip("Show/Hide the smoothing options.")
        options_bar_lay.addWidget(options_bar_label)

        options_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        options_lay.setContentsMargins(10, 10, 10, 10)
        options_wid = QtWidgets.QWidget()
        options_wid.setLayout(options_lay)

        # Create a QScrollArea in case our options takes more room then its aprent widget.
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setWidget(options_wid)
        parent_layout.addWidget(self.scroll_area)

        smooth_type_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        smooth_type_lay.setContentsMargins(0, 0, 0, 0)
        smooth_type_wid = QtWidgets.QWidget()
        smooth_type_wid.setLayout(smooth_type_lay)
        options_lay.addWidget(smooth_type_wid)

        smooth_type_label = QtWidgets.QLabel(self)
        smooth_type_label.setText("Method :")
        smooth_type_label.setToolTip("Select the smooth method to apply.")
        smooth_type_lay.addWidget(smooth_type_label)

        self.filter_type_cb = QtWidgets.QComboBox()
        smooth_type_lay.addWidget(self.filter_type_cb)

        self.filter_type_cb.addItems(_FILTERS.keys())

        smooth_type_right_spacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        smooth_type_lay.addItem(smooth_type_right_spacer)

        smooth_type_description_lay = QtWidgets.QBoxLayout(
            QtWidgets.QBoxLayout.LeftToRight
        )
        smooth_type_description_lay.setContentsMargins(10, 10, 10, 10)
        smooth_type_description_wid = QtWidgets.QWidget()
        smooth_type_description_wid.setLayout(smooth_type_description_lay)
        options_lay.addWidget(smooth_type_description_wid)

        self.filter_description_pte = QtWidgets.QPlainTextEdit(self)
        self.filter_description_pte.setPlainText("")
        self.filter_description_pte.setReadOnly(True)
        smooth_type_description_lay.addWidget(self.filter_description_pte)

        # Separator
        separator_a = QtWidgets.QFrame()
        separator_a.setFrameShape(QtWidgets.QFrame.HLine)
        separator_a.setFrameShadow(QtWidgets.QFrame.Sunken)
        options_lay.addWidget(separator_a)

        # Preserve Edges
        preserve_edges_lay = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        preserve_edges_lay.setContentsMargins(0, 0, 0, 0)
        preserve_edges_wid = QtWidgets.QWidget()
        preserve_edges_wid.setLayout(preserve_edges_lay)
        options_lay.addWidget(preserve_edges_wid)

        preserve_edges_label = QtWidgets.QLabel(self)
        preserve_edges_label.setText("Preserve Edges :")
        preserve_edges_label.setToolTip("Keeps the first and last keyframe intact.")
        preserve_edges_lay.addWidget(preserve_edges_label)

        self.preserve_edges_chkb = QtWidgets.QCheckBox()
        self.preserve_edges_chkb.setChecked(False)
        self.preserve_edges_chkb.setToolTip("Keeps the first and last keyframe intact.")
        preserve_edges_lay.addWidget(self.preserve_edges_chkb)

        preserve_edges_right_spacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        preserve_edges_lay.addItem(preserve_edges_right_spacer)

        # Add a spacer at the bottom so the options are all spaced nicely even if we had or remove some later on.
        options_spacer = QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding
        )
        options_lay.addItem(options_spacer)

    def update_filter_description(self):
        """Update the filter description based on the currently selected filter name."""

        self.filter_description_pte.setPlainText("")

        smooth_type = str(self.filter_type_cb.currentText())
        if smooth_type in _FILTERS:
            description_text = _FILTERS[smooth_type]
            self.filter_description_pte.setPlainText(description_text)


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
