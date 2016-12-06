import hou
import os

from PySide import QtGui
from PySide import QtCore

ICONS = os.path.dirname(__file__) + "\\icons\\"
def get_icon(name):
    return QtGui.QIcon(ICONS + name + ".png")

class Colors(object):

    GRAY = QtGui.QColor(240,240,240)
    BLUE = QtGui.QColor(207,230,252)
    PINK = QtGui.QColor(252,232,239)
    RED = QtGui.QColor(254,215,205)
    GREEN = QtGui.QColor(218,247,186)
    YELLOW = QtGui.QColor(255,247,214)
    PURPLE = QtGui.QColor(241,232,252)
    MAGENTA = QtGui.QColor(252,207,239)
    TEAL = QtGui.QColor(209,242,250)
    ORANGE = QtGui.QColor(250,234,209)
    MAGENTA = QtGui.QColor(250,234,209)
    SEAFOAM = QtGui.QColor(209,250,232)
    WHITE = QtGui.QColor(255,255,255)


class MainPanel(QtGui.QFrame):

    def __init__(self, parent=hou.ui.mainQtWindow()):
        super(MainPanel, self).__init__(parent=parent)

        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setSpacing(5)
        self.main_layout.addWidget(QtGui.QLabel("Help Card Maker 0.0.0"))

        # toolbar



        # scroll area
        self.ui_widget = []
        self.scroll_w = QtGui.QWidget()
        self.scroll_w.setAutoFillBackground(True)
        self.scroll_lay = QtGui.QVBoxLayout()
        self.scroll_lay.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_w.setLayout(self.scroll_lay)

        # TEST
        text = TextBlock()
        self.scroll_lay.addWidget(text)

        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setObjectName("scroll")
        self.scroll_area.setStyleSheet("""QWidget#scroll{background-color: white;}""")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_w)

        self.main_layout.addWidget(self.scroll_area)

        # footer


        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

class TextProperties(QtGui.QWidget):

    def __init__(self, parent=None):
        super(TextProperties, self).__init__(parent=parent)

        main_layout = QtGui.QGridLayout()
        main_layout.addWidget(QtGui.QLabel("Text Properties:"), 0, 0)

class TextBlock(QtGui.QWidget):

    def __init__(self, text="Text", parent=None):
        super(TextBlock, self).__init__(parent=parent)

        layout = QtGui.QHBoxLayout()

        self.text = QtGui.QTextEdit()
        self.text.setPlainText(text)
        self.text.setMaximumHeight(20)
        self.text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text.setWordWrapMode(QtGui.QTextOption.WordWrap)
        self.setStyleSheet("""QTextEdit{background-color: transparent;
                                         border: 0px;
                                         color: black}
                               QTextEdit:hover{background-color: rgba(0,0,80,16)}""")
        layout.addWidget(self.text)
        
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def keyReleaseEvent(self, event):

        self.text.setFixedHeight(self.text.document().size().height())
        super(TextBlock, self).keyReleaseEvent(event)



        