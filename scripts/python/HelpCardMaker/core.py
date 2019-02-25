import hou
import os
import tempfile
import uuid
import traceback
from collections import OrderedDict

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from HelpCardMaker.utils import *

class WidgetInterface(object):
    """ Help widgets interface for drag and drop system implementation
    """
    
    def __init__(self, idx, show_handle=True, parent=None):
        
        assert parent is not None, "parent widget is needed"

        self.top_w = parent
        self.idx = idx
        self.setAcceptDrops(True)
        self.show_handle = show_handle

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setAlignment(QtCore.Qt.AlignLeft)
        
        if show_handle:
            handle = WidgetHandle(parent=self)
            self.main_layout.addWidget(handle)

        self.main_layout.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                           QtWidgets.QSizePolicy.Maximum)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)

    def dragEnterEvent(self, event):

        return

    def dragMoveEvent(self, event):
        
        return

    def dropEvent(self, event):
        
        if not self.top_w: return
        data = event.mimeData().text()
        source = event.source()

        # insert a widget
        if isinstance(source, ToolIcon):
            self.top_w.insert_widget(source.objectName(), self.idx + 1)

        # widget has been moved
        elif hasattr(source, "widget"):
            idx_from = source.widget.idx
            self.top_w.move_widget(idx_from, self.idx)

        else:
            self.text.setHtml(self.text.toPlainText() + data)

    def remove_me(self):
        
        self.top_w.remove_widget(self)

    def create_delete_btn(self):

        self.delete_btn = QtWidgets.QToolButton()
        self.delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        self.delete_btn.setIcon(get_icon("close"))
        self.delete_btn.clicked.connect(self.remove_me)
        self.main_layout.addWidget(self.delete_btn)

class ScrollWidget(QtWidgets.QWidget):
    """ Custom widget used in scroll area which supports drag an drop
        system for help widgets creation
    """
    def __init__(self, parent=None):
        super(ScrollWidget, self).__init__(parent=parent)

        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.top_w = parent
        self.setStyleSheet("""QWidget{background-color: white;}""")
        self.setFocus()
        
    def mousePressEvent(self, event):

        self.setFocus()

    def keyPressEvent(self, event):
            
        if event.matches(QtGui.QKeySequence.Paste):

            try:
                clip = QtGui.QClipboard()
                img = clip.image()
                if img.isNull():
                    return super(ScrollWidget, self).keyPressEvent(event)

                temp = tempfile.gettempdir() + os.sep + uuid.uuid4().hex + ".png"

                img.save(temp)
                self.top_w.add_image_from_clip(temp)
            except Exception as e:
                print("Invalid clipboard: " + str(e))

        super(ScrollWidget, self).keyPressEvent(event)

    def mouseEnterEvent(self, event):

        self.setFocus()

    def dropEvent(self, event):
        
        source = event.source()
        if isinstance(source, ToolIcon):
            self.top_w.insert_widget(source.objectName(), -1)

class OnThisPageEntry(QtWidgets.QLabel):

    def __init__(self, target_widget=None, text="None", parent=None):
        super(OnThisPageEntry, self).__init__(parent=parent)

        self.top_w = parent
        self.target_widget = target_widget

        self.setText(text)

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                               QtWidgets.QSizePolicy.Minimum)
        self.setStyleSheet("""QLabel{color: #1782ba;}
                              QLabel:hover{color: #349ed5;}""")
        
    def mousePressEvent(self, event):

        self.top_w.top_w.scroll_area.ensureWidgetVisible(self.target_widget)

    def update_text(self, text):

        self.lbl.setText(text)

class OnThisPage(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(OnThisPage, self).__init__(parent=parent)

        self.top_w = parent

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_lbl = QtWidgets.QLabel("On This Page")
        self.main_lbl.setStyleSheet("""QLabel{color: rgb(250, 150, 0);
                                              font-weight: bold}""")
        self.main_layout.addWidget(self.main_lbl)

        self.bg_frame = QtWidgets.QFrame()
        self.bg_frame.setAutoFillBackground(True)
        self.bg_frame.setStyleSheet("""QFrame{background-color: #f3f3f3;
                                              border-radius: 10px}""")
        #self.bg_frame.setContentsMargins(5,5,5,5)
        self.bg_layout = QtWidgets.QVBoxLayout()
        self.bg_layout.setSpacing(5)
        self.bg_frame.setLayout(self.bg_layout)

        self.main_layout.addWidget(self.bg_frame)
        self.main_layout.setSpacing(3)
        self.setLayout(self.main_layout)

        self.entries = []

    def append_entry(self, idx, text, widget):

        entry = OnThisPageEntry(target_widget=widget, text=text, parent=self)
        self.bg_layout.insertWidget(idx, entry)
        self.entries.append(entry)

class WidgetHandle(QtWidgets.QFrame):

    def __init__(self, idx=0, parent=None):
        super(WidgetHandle, self).__init__(parent=parent)

        self.widget = parent
        self.setObjectName("handle")
        self.setStyleSheet("""QFrame#handle{background-color: #eaeaea;}
                              QFrame#handle:hover{background-color: #d5dae5;}""")
        self.setFixedWidth(10)

    def mousePressEvent(self, event):
        """ Init the drag and drop system for reordering widgets.
            Limite the size of the thumbnail's pixmap to 200pix height
            Add a small gradient as alpha mask.
        """
        widget_size = self.widget.size()

        w_h = widget_size.height()
        pix_h = 100
        if w_h < 200: pix_h = w_h

        pix_w = widget_size.width()

        mask_pix = QtGui.QPixmap(QtCore.QSize(pix_w, pix_h))
 
        w_pix = QtGui.QPixmap(widget_size)
        self.widget.render(w_pix)

        painter	= QtGui.QPainter(mask_pix)
        
        gradient = QtGui.QLinearGradient(QtCore.QPointF(mask_pix.rect().topLeft()),
				                   QtCore.QPointF(mask_pix.rect().bottomLeft()))
        gradient.setColorAt(0, QtGui.QColor(200, 200, 200))
        gradient.setColorAt(0.5, QtGui.QColor(200, 200, 200))
        gradient.setColorAt(1, QtCore.Qt.black)
        brush = QtGui.QBrush(gradient)
        
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
        painter.fillRect(QtCore.QRectF(0, 0, pix_w, pix_h), w_pix)
        
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_DestinationIn)
        painter.fillRect(QtCore.QRectF(0, 0, pix_w, pix_h), brush) 
        painter.end()
        
        pix = w_pix.copy(0, 0, pix_w, pix_h)

        mimeData = QtCore.QMimeData()
        mimeData.setText("%W%;" + str(self.widget.idx))
        drag = QtGui.QDrag(self)
        
        drag.setPixmap(pix)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())
        drag.start(QtCore.Qt.MoveAction)

class ToolIcon(QtWidgets.QLabel):
    """ Custom flat icon which stats the drag system, used in 
        toolbar widget only.
    """
    def __init__(self, icon="", widget_type="", parent=None):
        super(ToolIcon, self).__init__(parent=parent)

        self.setObjectName(widget_type)

        self.setFixedHeight(34)
        self.setFixedWidth(34)
        self.icon_pix = get_icon(icon).pixmap(32,32)
        self.setPixmap(self.icon_pix)
        self.widget_type = widget_type

    def mousePressEvent(self, event):

        mimeData = QtCore.QMimeData()
        mimeData.setText(self.widget_type)
        drag = QtGui.QDrag(self)
        drag.setPixmap(self.icon_pix)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())
        drag.start(QtCore.Qt.MoveAction)

class CLabel(QtWidgets.QWidget):
    """ Utilitiy label with output() method to be compatible with
        other help widgets.
    """
    def __init__(self, text="", show_btn=True, parent=None):
        super(CLabel, self).__init__(parent=parent)

        self.top_w = parent

        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        self.lbl = QtWidgets.QLabel(text)
        layout.addWidget(self.lbl)

        delete_btn = QtWidgets.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def remove_me(self):

        self.top_w.remove_widget(self)

    def output(self):

        return self.lbl.text()

class ColorChooser(QtWidgets.QDialog):
    """ Custom color picker with button. Parse the given color_class
        to fetch which colors are available.
    """
    def __init__(self, color_class=BoxColors, parent=None):
        super(ColorChooser, self).__init__(parent=parent)

        self.setWindowIcon(get_icon("color"))
        self.setWindowTitle("Pick a Color")

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(5)
        self.color = None

        colors = [f for f in color_class.__dict__.keys() \
                  if not f.startswith("__")]

        for c in colors:

            _c = getattr(color_class, c)
            color_str = ','.join([str(v) for v in [_c.red(), _c.green(), _c.blue()]])
            btn = QtWidgets.QPushButton(c.capitalize())
            btn.setStyleSheet("""QPushButton{background-color: rgb(""" + color_str + """);
                                             color: black}""")
            btn.clicked.connect(lambda c=c: self.set_color(c))
            layout.addWidget(btn)

        layout.addWidget(QtWidgets.QLabel(""))
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        layout.addWidget(cancel_btn)

        self.setLayout(layout)

    def set_color(self, color):

        self.color = color
        self.close()

class wSep(QtWidgets.QFrame):
    """ smal vertival separator widget for toolbar
    """
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        self.setFrameStyle(QtWidgets.QFrame.VLine)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                           QtWidgets.QSizePolicy.Expanding)
        self.setFixedHeight(34)