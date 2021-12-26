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
import theme

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

# Height of the CurveFiltererWin QMainWindow with both the options layout collapsed or expanded.
_WIN_HEIGHT_HIDE_OPTIONS = 250
_WIN_HEIGHT_SHOW_OPTIONS = _WIN_HEIGHT_HIDE_OPTIONS + 300

# Path to the icons relative to the current module location.
_ICONS_PATH = os.path.join(os.path.dirname(__file__), "icons")

# QSettings instance used to save and restore the interface parameters next time you open it.
_SETTINGS = QtCore.QSettings("jkoubi", "curve_filterer")


class CurveFiltererWin(QtWidgets.QMainWindow):
    def __init__(self, *args):
        super(CurveFiltererWin, self).__init__(*args)

        # Define the variable that will hold the values before they get filtered. We
        # start with a random sampling of 25 values between 25.0 and 155.0 for demo
        # purpose.
        self.raw_values = [random.uniform(25.0, 155.0) for x in range(25)]

        # Set the application title and size.
        self.setWindowTitle("Curve Filterer")
        self.resize(600, _WIN_HEIGHT_HIDE_OPTIONS)

        # Create menus in the QMainWindow menu-bar.
        self.create_menus()

        # Create teh main layout and widget that will contain the various sections
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

        # Connect the main widgets to the preview updating functions.
        self.intensity_slider.valueChanged.connect(self.update_preview)
        self.filter_type_cb.currentIndexChanged[int].connect(self.update_preview)
        self.filter_type_cb.currentIndexChanged[int].connect(
            self.update_filter_description
        )
        self.preserve_edges_chkb.stateChanged.connect(self.update_preview)

    def closeEvent(self, event):
        """Save the UI state when closing it."""

        # Save the current window state.
        _SETTINGS.setValue("windowState", self.saveState())

        # Save the current filter widgets data.
        _SETTINGS.setValue("filter_type", self.filter_type_cb.currentIndex())
        _SETTINGS.setValue("preserve_edges", self.preserve_edges_chkb.isChecked())
        _SETTINGS.setValue("intensity", self.intensity_slider.value())

        # Save the settings we just set on disk.
        _SETTINGS.sync()

        # Accept the event and execute it's default behaviour next.
        event.accept()

        QtWidgets.QMainWindow.closeEvent(self, event)

    def showEvent(self, event):
        """Restore the UI state when it's being shown."""

        # Restore the window state.
        self.restoreState(_SETTINGS.value("windowState"))

        # Get the saved filter widgets data and apply it.
        self.filter_type_cb.setCurrentIndex(int(_SETTINGS.value("filter_type", 0)))
        self.preserve_edges_chkb.setChecked(
            bool(_SETTINGS.value("preserve_edges", False))
        )
        self.intensity_slider.setValue(float(_SETTINGS.value("intensity", 25)))

        # Update the filter description adn teh filter preview widgets.
        self.update_filter_description()
        self.update_preview()

        # Accept the event and execute it's default behaviour next.
        event.accept()

        QtWidgets.QMainWindow.showEvent(self, event)

    def create_menus(self):
        """Create the menus in the QMainWindow menu bar."""

        # Create a "File" QMenu in the current QMainWindow menu bar and add a few actions.
        file_menu = self.menuBar().addMenu("File")

        # Create an open action in teh file menu that can also be triggered by the Ctrl+O shortcut.
        open_icon_path = os.path.join(_ICONS_PATH, "open.png")
        open_action = QtWidgets.QAction(QtGui.QIcon(open_icon_path), "Open", file_menu)
        open_action.setStatusTip("Open a curve file.")
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.open_curve_file)

        save_icon_path = os.path.join(_ICONS_PATH, "save.png")
        save_action = QtWidgets.QAction(QtGui.QIcon(save_icon_path), "Save", file_menu)
        save_action.setStatusTip("Save the smoothed curve.")
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.save_curve)

        close_icon_path = os.path.join(_ICONS_PATH, "close.png")
        close_action = QtWidgets.QAction(
            QtGui.QIcon(close_icon_path), "Close", file_menu
        )
        close_action.setStatusTip("Close the application.")
        close_action.setShortcut("Ctrl+Q")
        file_menu.addAction(close_action)
        close_action.triggered.connect(self.close)

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

        # Set a default value.
        self.intensity_slider.setValue(25)

        # Set a fixed height so we can have a "chunkier"-looking slider.
        self.intensity_slider.setFixedHeight(25)
        intensity_lay.addWidget(self.intensity_slider)

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

    def toggle_options(self):
        """
        Show or Hide the options layout.
        """

        if self.scroll_area.isVisible():
            self.scroll_area.setVisible(False)
            self.options_bar_button.setText("+")

            # This is a bit of an hack where in order for the window to resize properly
            # and the Option button to stay at the same spot we need to process an arbitrary
            # number of events before we call the resize() function to make sure that all QT
            # processes ran.
            for i in range(0, 10):
                QtWidgets.QApplication.processEvents()
            self.resize(self.width(), _WIN_HEIGHT_HIDE_OPTIONS)
        else:
            self.scroll_area.setVisible(True)
            self.options_bar_button.setText("-")
            for i in range(0, 10):
                QtWidgets.QApplication.processEvents()
            self.resize(self.width(), _WIN_HEIGHT_SHOW_OPTIONS)

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

        self.options_bar_button.clicked.connect(self.toggle_options)

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

        # Hide the scroll area since the options are hidden by default
        self.scroll_area.hide()

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

        # Add a spacer at teh bottom so the options are all spaced nicely even if we had or remove some later on.
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

    def update_preview(self):
        """Update the curve preview by setting the raw data (the pre-filtered curve Y values), then
        running the filtering algorithm by calling smooth_curve() which return a list of
        filtered Y values.

        :note: This can become slow if the input data is large, it's meant only as a preview,
               if you work with a large data set it's better to have a pre-made set of Y values
               to show the end-user a visual representation of the intensity and how each algorithm
               treat the curve data as an alternative.
        """

        self.spline_preview_wid.set_raw_values(self.raw_values)
        self.spline_preview_wid.set_filtered_values(self.smooth_curve())

    def smooth_curve(self):
        """Run the actual smoothing of the raw curve data based on the interface parameters.

        :return: List of smoothed Y values.
        :rtype: list
        """

        strength = self.intensity_slider.value() / 100.0
        smooth_type = self.filter_type_cb.currentText()
        preserve_edges = self.preserve_edges_chkb.isChecked()

        if self.raw_values:
            filtered_values = core.smooth_values(
                self.raw_values,
                strength=strength,
                smooth_type=smooth_type,
                preserve_edges=preserve_edges,
            )

            return filtered_values

        return []

    def open_curve_file(self):
        """Open a curve file and set it as the raw values to smooth."""

        # We use QFileDialog to select the file to open. We filter out for the .crv
        # extension.
        default_path = os.path.join(os.path.dirname(__file__), "test_data")
        filepath = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open", default_path, "Curve files (*.crv)"
        )

        self.raw_values = core.read_curve_file(filepath[0])
        self.update_preview()

    def save_curve(self):
        """Save the result of the smoothing operations to a curve file."""

        filtered_values = self.smooth_curve()

        default_path = os.path.join(os.path.dirname(__file__), "test_data")
        filepath = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save", default_path, "Curve files (*.crv)"
        )

        core.save_curve_file(filepath[0], filtered_values)


class QCurveIntensitySlider(QtWidgets.QSlider):
    """
    QSlider with a custom background and handle to display intensity.
    """

    def __init__(self, *args):
        super(QCurveIntensitySlider, self).__init__(*args)

    def paintEvent(self, event):
        """Paint our own slider by overriding the paint event."""

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        # Create a border around our widget
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setColor(QtGui.QColor(46, 46, 46))
        painter.setPen(pen)

        # Draw two rectangles based on the widget enclosing one. We use the first
        # rectangle to draw a gradient and then a second on top that work as a mask.
        # We use the slider handle position to know where to start drawing the second
        # rectangle used as a mask.
        bg_rect = self.rect()
        bg_rect.setHeight(bg_rect.height() - 6)
        bg_center = bg_rect.center()
        bg_center.setY(bg_center.y() + 3)
        bg_rect.moveCenter(bg_center)

        grad = QtGui.QLinearGradient(self.rect().topLeft(), self.rect().topRight())
        grad.setColorAt(0.0, QtGui.QColor(94, 185, 115))
        grad.setColorAt(1.0, QtGui.QColor(185, 94, 94))
        painter.setBrush(grad)

        painter.drawRect(bg_rect)

        slider_pos = self.sliderPosition()
        width = bg_rect.width()
        right_x = slider_pos * width / 100
        bg_rect.setX(right_x)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(57, 57, 57)))
        painter.drawRect(bg_rect)

        # Now draw the handle to be a circle based of the height of the widget.
        handle_rect = self.rect()
        handle_rect.setWidth(handle_rect.height())

        handle_center = handle_rect.center()
        handle_center.setX(right_x)
        handle_rect.moveCenter(handle_center)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(101, 101, 101)))
        painter.drawEllipse(handle_rect)


class QCurvvePreviewer(QtWidgets.QWidget):
    """
    Widget that paint two curve. One that represent the raw pre-filtered data
    and the second that represent the curve after being filtered.
    """

    def __init__(self, values=None, filtered_values=None, parent=None):
        super(QCurvvePreviewer, self).__init__(parent)

        self._values = values
        self._filtered_values = filtered_values

    def set_raw_values(self, values):
        """Set the raw curve values (pre-filtered) and then update the widget to re-draw it."""

        self._values = values
        self.update()

    def set_filtered_values(self, filtered_values):
        """Set the filtered curve values and then update the widget to re-draw it."""

        self._filtered_values = filtered_values
        self.update()

    def paintEvent(self, event):
        """
        call the draw_curve() function twice. The first time with the raw Y coordinates, and second
        time as a filtered one with the filtered values.
        """

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing, True)
        self.draw_curve(painter, self._values)
        self.draw_curve(painter, self._filtered_values, "filtered")
        painter.end()

    def draw_curve(self, painter, y_values, crv_type="raw"):
        """Draw a curve based on the given values.

        :param painter: QPainter instance to use.
        :type painter: QPainter
        :param y_values: List of the curve Y coordinates.
        :type y_values: list of floats
        :param crv_type: Type of curve to draw (raw or filtered), defaults to "raw"
        :type crv_type: str, optional
        """

        if len(y_values) > 2:

            # Change the curve and point colours and style based on its type.
            if crv_type == "raw":
                point_pen = QtGui.QPen(
                    QtGui.QColor(0, 205, 207, 100), 1, QtCore.Qt.DashLine
                )
                point_brush = QtGui.QBrush(QtGui.QColor(0, 205, 207, 50))
                line_pen = QtGui.QPen(
                    QtGui.QColor(43, 120, 224, 160), 1, QtCore.Qt.DashLine
                )
            else:
                point_pen = QtGui.QPen(
                    QtGui.QColor(229, 1, 1, 255), 1, QtCore.Qt.DashLine
                )
                point_brush = QtGui.QBrush(QtGui.QColor(210, 35, 0, 255))
                line_pen = QtGui.QPen(
                    QtGui.QColor(183, 183, 183, 255), 1, QtCore.Qt.SolidLine
                )

            # Calculate the spacing based on the width of the QCurvvePreviewer parent widget.
            # This ensure that even if parent widget change size we still draw the whole curve
            # albeit with a lower or higher spacing between points.
            # In our case the values we pass on to this draw_curve() functions are only on the Y
            # axis since. You can however extend it to work with both axis if needed. The spacing
            # below replace the X coordinate.
            x_spacing = self.parent().width() / float(len(y_values) + 1)

            # Draw the first point
            prev_y = y_values[0]
            prev_x = 2

            painter.setPen(point_pen)
            painter.setBrush(point_brush)
            painter.drawEllipse(prev_x - 2, prev_y - 2, 4, 4)

            # Draw the remaining points
            for y in y_values[1:]:
                x = prev_x + x_spacing
                painter.setPen(line_pen)
                painter.drawLine(prev_x, prev_y, x, y)

                painter.setPen(point_pen)
                painter.drawEllipse(x - 2, y - 2, 4, 4)

                prev_y = y
                prev_x = x


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    # Create a pixmap with our splash-screen iamge.
    pixmap = QtGui.QPixmap()
    pixmap.load(os.path.join(_ICONS_PATH, "splash.png"))

    # Create a slpash screen and brign it on top of other windows.
    splash = QtWidgets.QSplashScreen(pixmap)
    splash.setWindowFlags(splash.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

    # Use the pixmap alpha as a mask for teh splash screen since our image
    # have rounded corners on top.
    splash.setMask(pixmap.mask())

    # Display a loading message at the bottom-right corner.
    splash.showMessage(
        "Loading ...",
        alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight,
        color=QtGui.QColor("#fff"),
    )

    # Show the splash screen and process the events to make sure it gets displayed
    splash.show()
    app.processEvents()

    # Apply our theme to the whole application.
    theme.apply_theme(app)

    # Initialize and show the QMainWindow.
    window = CurveFiltererWin()
    window.show()

    # Close the splash-screen once the QMainWindow show event is done.
    splash.finish(window)

    exit_code = app.exec_()
    sys.exit(exit_code)
