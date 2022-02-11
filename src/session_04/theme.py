# No shebang line. This file is meant to be imported
"""
Module to apply a theme to Show Launcher ui.
"""

# standard imports
import os
import logging

# third-party imports
from PySide2 import QtGui


# logger
_log = logging.getLogger(__name__)
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
_log.addHandler(_log_handler)
_log.setLevel("INFO")

# constants
HIGHLIGHT_COLOUR = QtGui.QColor(103, 141, 178)
BRIGHTNESS_SPREAD = 2.5

BRIGHT_COLOUR = QtGui.QColor(200, 200, 200)
LIGHT_COLOUR = QtGui.QColor(100, 100, 100)
DARK_COLOUR = QtGui.QColor(42, 42, 42)
MID_COLOUR = QtGui.QColor(68, 68, 68)
MID_LIGHT_COLOUR = QtGui.QColor(84, 84, 84)
SHADOW_COLOUR = QtGui.QColor(21, 21, 21)

BASE_COLOUR = MID_COLOUR
TEXT_COLOUR = BRIGHT_COLOUR
DISABLED_BUTTON_COLOUR = QtGui.QColor(78, 78, 78)
DISABLED_TEXT_COLOUR = QtGui.QColor(128, 128, 128)
ALTERNATE_BASE_COLOUR = QtGui.QColor(46, 46, 46)


def apply_theme(widget):
    """Apply the theme to the given QWidget.

    :param widget: QWidget to apply the theme to.
    :type widget: QtWidgets.QWidget
    """

    # Create a new palette for our theme.
    palette = QtGui.QPalette()

    if BASE_COLOUR.toHsv().valueF() > 0.5:
        spread = 100 / BRIGHTNESS_SPREAD
    else:
        spread = 100 * BRIGHTNESS_SPREAD

    if HIGHLIGHT_COLOUR.toHsv().valueF() > 0.6:
        highlighted_text_colour = BASE_COLOUR.darker(spread * 2)
    else:
        highlighted_text_colour = BASE_COLOUR.lighter(spread * 2)

    palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(MID_COLOUR))
    palette.setBrush(QtGui.QPalette.WindowText, QtGui.QBrush(TEXT_COLOUR))
    palette.setBrush(QtGui.QPalette.Foreground, QtGui.QBrush(BRIGHT_COLOUR))
    palette.setBrush(QtGui.QPalette.Base, QtGui.QBrush(DARK_COLOUR))
    palette.setBrush(QtGui.QPalette.AlternateBase, QtGui.QBrush(ALTERNATE_BASE_COLOUR))
    palette.setBrush(QtGui.QPalette.ToolTipBase, QtGui.QBrush(BASE_COLOUR))
    palette.setBrush(QtGui.QPalette.ToolTipText, QtGui.QBrush(TEXT_COLOUR))

    palette.setBrush(QtGui.QPalette.Text, QtGui.QBrush(TEXT_COLOUR))
    palette.setBrush(
        QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QBrush(DISABLED_TEXT_COLOUR)
    )

    palette.setBrush(QtGui.QPalette.Button, QtGui.QBrush(LIGHT_COLOUR))
    palette.setBrush(
        QtGui.QPalette.Disabled,
        QtGui.QPalette.Button,
        QtGui.QBrush(DISABLED_BUTTON_COLOUR),
    )
    palette.setBrush(QtGui.QPalette.ButtonText, QtGui.QBrush(TEXT_COLOUR))
    palette.setBrush(
        QtGui.QPalette.Disabled,
        QtGui.QPalette.ButtonText,
        QtGui.QBrush(DISABLED_TEXT_COLOUR),
    )
    palette.setBrush(QtGui.QPalette.BrightText, QtGui.QBrush(TEXT_COLOUR))
    palette.setBrush(
        QtGui.QPalette.Disabled,
        QtGui.QPalette.BrightText,
        QtGui.QBrush(DISABLED_TEXT_COLOUR),
    )

    palette.setBrush(QtGui.QPalette.Light, QtGui.QBrush(LIGHT_COLOUR))
    palette.setBrush(QtGui.QPalette.Midlight, QtGui.QBrush(MID_LIGHT_COLOUR))
    palette.setBrush(QtGui.QPalette.Mid, QtGui.QBrush(MID_COLOUR))
    palette.setBrush(QtGui.QPalette.Dark, QtGui.QBrush(DARK_COLOUR))
    palette.setBrush(QtGui.QPalette.Shadow, QtGui.QBrush(SHADOW_COLOUR))

    palette.setBrush(QtGui.QPalette.Highlight, QtGui.QBrush(HIGHLIGHT_COLOUR))
    palette.setBrush(
        QtGui.QPalette.HighlightedText, QtGui.QBrush(highlighted_text_colour)
    )

    # Apply the palette to the given widget.
    widget.setPalette(palette)
