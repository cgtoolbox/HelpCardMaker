
# Houdini Help card maker
# Compatibility => Houdini 14, 15, 15.5

# Author:  Guillaume Jobst
# Contact: contact@guillaume-j.com
# Website: www.guillaume-j.com
# Github:  GJpy

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. http://www.gnu.org/licenses/

VERSION = "0.1.1"

import hou
import os

from PySide import QtGui
from PySide import QtCore

ICONS = os.path.dirname(__file__) + "\\icons\\"
def get_icon(name):
    return QtGui.QIcon(ICONS + name + ".png")

# UTILITIES
class Colors(object):

    GRAY = QtGui.QColor(240,240,240)
    BLUE = QtGui.QColor(0,135,255)
    PINK = QtGui.QColor(252,232,239)
    RED = QtGui.QColor(255,50,0)
    GREEN = QtGui.QColor(105,205,0)
    YELLOW = QtGui.QColor(255,205,0)
    PURPLE = QtGui.QColor(241,232,252)
    MAGENTA = QtGui.QColor(252,207,239)
    TEAL = QtGui.QColor(209,242,250)
    ORANGE = QtGui.QColor(250,234,209)
    MAGENTA = QtGui.QColor(250,234,209)
    SEAFOAM = QtGui.QColor(209,250,232)
    WHITE = QtGui.QColor(255,255,255)

class BoxColors(object):

    RED = QtGui.QColor(255,215,205)
    GREEN = QtGui.QColor(220,250,185)
    BLUE = QtGui.QColor(210,230,255)
    ORANGE = QtGui.QColor(250,235,210)
    
class WidgetInterface(object):

    def dragEnterEvent(self, event):

        return

    def dragMoveEvent(self, event):
        
        return

    def dropEvent(self, event):
        
        data = event.mimeData().text()
        if data.startswith("%HCM_W%"):
            self.top_w.insert_widget(data.split('_')[-1], self.idx + 1)

        else:
            self.text.setPlainText(self.text.toPlainText() + data)

    def remove_me(self):
        
        self.top_w.remove_widget(self)

class ToolIcon(QtGui.QLabel):

    def __init__(self, icon="", widget_type="", parent=None):
        super(ToolIcon, self).__init__(parent=parent)

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

class CLabel(QtGui.QLabel):
    """ Utilitiy label with output() method to be compatible with
        other help widgets
    """
    def __init__(self, text="", decorator="===", parent=None):
        super(CLabel, self).__init__(text, parent=parent)

    def output(self):

        return self.text()

class ColorChooser(QtGui.QDialog):

    def __init__(self, color_class=BoxColors, parent=None):
        super(ColorChooser, self).__init__(parent=parent)

        self.setWindowIcon(get_icon("color"))
        self.setWindowTitle("Pick a Color")

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(5)
        self.color = None

        colors = [f for f in color_class.__dict__.keys() \
                  if not f.startswith("__")]

        for c in colors:

            _c = getattr(color_class, c)
            color_str = ','.join([str(v) for v in [_c.red(), _c.green(), _c.blue()]])
            btn = QtGui.QPushButton(c.capitalize())
            btn.setStyleSheet("""QPushButton{background-color: rgb(""" + color_str + """);
                                             color: black}""")
            btn.clicked.connect(lambda c=c: self.set_color(c))
            layout.addWidget(btn)

        layout.addWidget(QtGui.QLabel(""))
        cancel_btn = QtGui.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        layout.addWidget(cancel_btn)

        self.setLayout(layout)

    def set_color(self, color):

        self.color = color
        self.close()

class wSep(QtGui.QFrame):

    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.setFrameStyle(QtGui.QFrame.VLine)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Expanding)
        self.setFixedHeight(34)

# MAIN INTERFACE
class MainPanel(QtGui.QFrame):

    def __init__(self, parent=None):
        super(MainPanel, self).__init__(parent=parent)

        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setSpacing(5)
        self.main_layout.addWidget(QtGui.QLabel("Help Card Maker " + VERSION))

        # toolbar
        self.toolbar = QtGui.QHBoxLayout()
        self.toolbar.setAlignment(QtCore.Qt.AlignLeft)

        self.apply_help_btn = QtGui.QToolButton()
        self.apply_help_btn.setStyleSheet("""QToolButton{border: None;
                                           background-color: None}""")
        self.apply_help_btn.setIcon(get_icon("apply"))
        self.apply_help_btn.setFixedHeight(34)
        self.apply_help_btn.setFixedWidth(34)
        self.apply_help_btn.setIconSize(QtCore.QSize(32,32))
        self.apply_help_btn.clicked.connect(self.apply_help)
        self.apply_help_btn.setToolTip("Set help card to selected digital asset")
        self.toolbar.addWidget(self.apply_help_btn)

        self.clear_btn = QtGui.QToolButton()
        self.clear_btn.setStyleSheet("""QToolButton{border: None;
                                           background-color: None}""")
        self.clear_btn.setIcon(get_icon("clean"))
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.setFixedWidth(34)
        self.clear_btn.setIconSize(QtCore.QSize(32,32))
        self.clear_btn.clicked.connect(self.clearn_widgets)
        self.clear_btn.setToolTip("Clear Elements")
        self.toolbar.addWidget(self.clear_btn)

        self.toolbar.addWidget(wSep())

        self.title_main_btn = ToolIcon("header", "%HCM_W%_title:1")
        self.title_main_btn.setToolTip("Add main title")
        self.toolbar.addWidget(self.title_main_btn)

        self.title2_btn = ToolIcon("title1", "%HCM_W%_title:2")
        self.title2_btn.setToolTip("Add title 2")
        self.toolbar.addWidget(self.title2_btn)

        self.title3_btn = ToolIcon("title2", "%HCM_W%_title:3")
        self.title3_btn.setToolTip("Add title 3")
        self.toolbar.addWidget(self.title3_btn)

        self.text_block_btn = ToolIcon("text_block", "%HCM_W%_text:block")
        self.text_block_btn.setToolTip("Add simple block of text")
        self.toolbar.addWidget(self.text_block_btn)

        self.parms_grid_btn = ToolIcon("view_gridline", "%HCM_W%_params")
        self.parms_grid_btn.setToolTip("Add parameters help grid")
        self.toolbar.addWidget(self.parms_grid_btn)

        self.tips_btn = ToolIcon("tips", "%HCM_W%_tips")
        self.tips_btn.setToolTip("Add tips line")
        self.toolbar.addWidget(self.tips_btn)

        self.info_btn = ToolIcon("info", "%HCM_W%_note")
        self.info_btn.setToolTip("Add info line")
        self.toolbar.addWidget(self.info_btn)

        self.warning_btn = ToolIcon("warning", "%HCM_W%_warning")
        self.warning_btn.setToolTip("Add warning line")
        self.toolbar.addWidget(self.warning_btn)

        self.box_btn = ToolIcon("box", "%HCM_W%_textbox")
        self.box_btn.setToolTip("Add box text")
        self.toolbar.addWidget(self.box_btn)

        self.dotted_list_btn = ToolIcon("bullet", "%HCM_W%_bullet")
        self.dotted_list_btn.setToolTip("Add bullet text")
        self.toolbar.addWidget(self.dotted_list_btn)

        self.separator_btn = ToolIcon("sep", "%HCM_W%_separator")
        self.separator_btn.setToolTip("Add horizontal separator line")
        self.toolbar.addWidget(self.separator_btn)

        self.toolbar.addWidget(wSep())

        self.help_btn = QtGui.QToolButton()
        self.help_btn.setStyleSheet("""QToolButton{border: None;
                                           background-color: None}""")
        self.help_btn.setIcon(get_icon("help"))
        self.help_btn.setFixedHeight(34)
        self.help_btn.setFixedWidth(34)
        self.help_btn.setIconSize(QtCore.QSize(32,32))
        self.help_btn.clicked.connect(self.show_help)
        self.help_btn.setToolTip("Show Help")
        self.toolbar.addWidget(self.help_btn)

        self.main_layout.addItem(self.toolbar)

        # scroll area
        self.ui_widgets = []
        self.scroll_w = ScrollWidget(parent=self)
        self.scroll_w.setAutoFillBackground(True)
        self.scroll_lay = QtGui.QVBoxLayout()
        self.scroll_lay.setContentsMargins(5,5,5,5)
        self.scroll_lay.setSpacing(5)
        self.scroll_lay.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_w.setLayout(self.scroll_lay)
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setObjectName("scroll")
        self.scroll_area.setStyleSheet("""QScrollArea{background-color: white;}""")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_w)

        self.main_layout.addWidget(self.scroll_area)

        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

    def clearn_widgets(self):

        r = hou.ui.displayMessage("Clear all items ?", buttons=["Yes", "Cancel"])
        if r == 1: return

        while len(self.ui_widgets) != 0:
            for w in self.ui_widgets:
                w.remove_me()

    def remove_widget(self, w):

        w.setParent(None)
        self.scroll_lay.removeWidget(w)

        if w in self.ui_widgets:
            id = self.ui_widgets.index(w)
            self.ui_widgets.pop(id)

        w.deleteLater()

        for i, w in enumerate(self.ui_widgets):
            w.idx = i

    def insert_widget(self, w_type, idx):
        
        w = None
        if w_type == "text:block":
            w = TextBlock(parent=self)

        elif w_type == "separator":
            w = Separator(parent=self)

        elif w_type == "tips":
            w = Tips(parent=self)

        elif w_type == "warning":
            w = Warning(parent=self)

        elif w_type == "note":
            w = Note(parent=self)

        elif w_type == "bullet":
            w = Bullet(parent=self)

        elif w_type == "textbox":
            w = TextBox(parent=self)

        elif w_type.startswith("title:"):
            size = int(w_type.split(':')[-1])
            w = Title(size=size, parent=self)

        elif w_type == "params":
            sel = hou.selectedNodes()
            if not sel:
                hou.ui.displayMessage("Nothing selected")
                return
            sel = sel[0]
            w = Parameters(node=sel, parent=self)

        if w:
            if idx == -1:
                w.idx = len(self.ui_widgets) + 1
                self.scroll_lay.addWidget(w)
                self.ui_widgets.append(w)
            else:
                w.idx = idx
                self.scroll_lay.insertWidget(idx, w)
                self.ui_widgets.insert(idx, w)

        for i, w in enumerate(self.ui_widgets):
            w.idx = i

    def get_help_str(self):

        return '\n'.join([w.output() for w in self.ui_widgets])

    def apply_help(self):

        sel = hou.selectedNodes()
        if not sel:
            hou.ui.displayMessage("Nothing selected")
            return
        node = sel[0]

        if len(self.ui_widgets) == 0:
            hou.ui.displayMessage("Help card is empty",
                                  severity=hou.severityType.Warning)
            return

        r = hou.ui.displayMessage("This will erase the current help card on selected asset: " \
                                  + node.name(),
                                  help="Warning: This can't be undo !",
                                  buttons=["Ok", "Cancel"],
                                  severity=hou.severityType.ImportantMessage)
        if r == 1: return

        definition = node.type().definition()
        if not definition:
            hou.ui.displayMessage("Selected node is not an digital asset")
            return

        node.allowEditingOfContents()
        help = definition.sections().get("Help", None)
        if not help:
            help = definition.addSection("Help", "")

        help.setContents(self.get_help_str())

        definition.save(definition.libraryFilePath())
        hou.ui.displayMessage("Help card updated !")

        hou.ui.displayNodeHelp(node.type())

    def show_help(self):

        message = "Houdini Help card maker, version:" + VERSION + "\n\n"
        message += "Created by Guillaume Jobst\n\n"
        message += "More infos:\ncontact@guillaume-j.com\nwww.guillaume-j.com"

        w = QtGui.QMessageBox()
        w.setStyleSheet(hou.ui.qtStyleSheet())
        w.setWindowIcon(get_icon("help"))
        w.setWindowTitle("Help")
        w.setText(message)
        w.exec_()

class ScrollWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ScrollWidget, self).__init__(parent=parent)

        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.top_w = parent
        self.setStyleSheet("""QWidget{background-color: white;}""")

    def dragEnterEvent(self, event):

        return

    def dragMoveEvent(self, event):
        
        return

    def dropEvent(self, event):
        
        data = event.mimeData().text()
        if data.startswith("%HCM_W%"):
            self.top_w.insert_widget(data.split('_')[-1], -1)

# HELP WIDGETS
class TextBlock(QtGui.QWidget, WidgetInterface):

    def __init__(self, text="Text", idx=0, show_btn=True, parent=None):
        super(TextBlock, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx

        layout = QtGui.QHBoxLayout()

        self.setAcceptDrops(True)

        self.text = QtGui.QTextEdit()
        self.text.setAcceptDrops(False)
        self.text.setPlainText(text)
        self.text.setMaximumHeight(20)
        self.text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text.setWordWrapMode(QtGui.QTextOption.WordWrap)
        self.setStyleSheet("""QTextEdit{background-color: transparent;
                                         border: 0px;
                                         color: black}
                               QTextEdit:hover{background-color: rgba(0,0,80,16)}""")
        layout.addWidget(self.text)
        
        if show_btn:
            delete_btn = QtGui.QToolButton()
            delete_btn.setStyleSheet("""QToolButton{background-color:
                                        transparent;border: 0px}""")
            delete_btn.setIcon(get_icon("close"))
            delete_btn.clicked.connect(self.remove_me)
            layout.addWidget(delete_btn)

        layout.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Maximum)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def keyReleaseEvent(self, event):

        self.text.setFixedHeight(self.text.document().size().height())
        super(TextBlock, self).keyReleaseEvent(event)

    def output(self):

        return '\n' + self.text.toPlainText() + '\n'

class Title(QtGui.QWidget, WidgetInterface):

    def __init__(self, size=1, text="Title", idx=0, parent=None):
        super(Title, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        self.size = size

        layout = QtGui.QHBoxLayout()

        self.setAcceptDrops(True)

        self.text = QtGui.QLineEdit()
        self.text.setAcceptDrops(False)
        
        font_size = 10
        if size == 1:
            font_size = 16
            sel = hou.selectedNodes()
            if sel:
                text = sel[0].type().name().replace('_', ' ')

        elif size == 2:
            font_size = 14

        elif size == 3:
            font_size = 12

        self.text.setText(text)
        self.setStyleSheet("""QLineEdit{background-color: transparent;
                                         border: 0px;
                                         color: black;
                                         font-size: """ + str(font_size) + """pt;
                                         font-family: Time;}
                              QLineEdit:hover{background-color: rgba(0,0,80,16)}""")
        layout.addWidget(self.text)
        
        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent; border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)

        layout.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Maximum)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        return '\n' + '=' * self.size + ' ' + self.text.text() + \
               ' ' + '=' * self.size +'\n'

class Bullet(QtGui.QWidget, WidgetInterface):

    def __init__(self, size=1, text="item", idx=0, parent=None):
        super(Bullet, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        self.size = size

        layout = QtGui.QHBoxLayout()
        layout.setSpacing(5)

        self.setAcceptDrops(True)

        self.ico = QtGui.QLabel("")
        self.ico.setFixedSize(10,10)
        self.ico.setPixmap(get_icon("s_dot").pixmap(6,6))
        layout.addWidget(self.ico)

        self.text = QtGui.QLineEdit()
        self.text.setAcceptDrops(False)

        self.text.setText(text)
        self.text.setStyleSheet("""QLineEdit{background-color: transparent;
                                         border: 0px;
                                         color: black;
                                         font-size: 10pt;
                                         font-family: Time;}
                              QLineEdit:hover{background-color: rgba(0,0,80,16)}""")
        layout.addWidget(self.text)
        
        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent; border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)

        layout.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Maximum)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        return '* ' + self.text.text() + '\n'

class _tiw(QtGui.QWidget, WidgetInterface):
    """ Base class for Tips, Warning and Info line
    """
    def __init__(self, idx=0, parent=None):
        super(_tiw, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx

        self.init_values()
        self.init_widget()

    def init_values(self):

        self._text = "tips"
        self.icon = "s_tips"
        self.icon_lbl = "Tip"
        self.color_n = "yellow"
        self.color = Colors.YELLOW
        self.type = "TIP"

    def init_widget(self):

        self.setAcceptDrops(True)

        layout = QtGui.QHBoxLayout()
        tips_layout = QtGui.QVBoxLayout()

        tip_lbl_lay = QtGui.QHBoxLayout()
        tip_lbl_lay.setAlignment(QtCore.Qt.AlignLeft)
        tip_lbl_lay.setSpacing(5)

        tip_ico = QtGui.QLabel("")
        tip_ico.setFixedHeight(16)
        tip_ico.setFixedWidth(16)
        tip_ico.setPixmap(get_icon(self.icon).pixmap(16,16))
        tip_lbl_lay.addWidget(tip_ico)
        tip_lbl = QtGui.QLabel(self.icon_lbl)
        tip_lbl_lay.addWidget(tip_lbl)
        color_str = ','.join([str(self.color.red()),
                              str(self.color.green()),
                              str(self.color.blue())])

        tip_lbl.setStyleSheet("""QLabel{color: rgba(""" + color_str + """,255);
                                        font-size: 10pt} """)
        tips_layout.addItem(tip_lbl_lay)

        self.text = QtGui.QLineEdit()
        self.text.setContentsMargins(10,2,2,2)
        self.text.setAcceptDrops(False)
        self.text.setText(self._text)

        self.setStyleSheet("""QLineEdit{background-color: transparent;
                                         border: 0px;
                                         color: black;
                                         font-size: 10pt;
                                         font-family: Time;}
                              QLineEdit:hover{background-color: rgba(0,0,80,16)}""")
        tips_layout.addWidget(self.text)

        layout.addItem(tips_layout)
        
        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)

        layout.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Maximum)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        return "\n" + self.type + ":\n    #display: " + \
               self.color_n + "\n    " + \
               self.text.text() + "\n"

class Tips(_tiw):

    def __init__(self, idx = 0, parent = None):
        super(Tips, self).__init__(idx, parent)

class Note(_tiw):   

    def __init__(self, idx = 0, parent = None):
        super(Note, self).__init__(idx, parent)

    def init_values(self):

        self._text = "info"
        self.icon = "s_info"
        self.icon_lbl = "Info"
        self.color_n = "blue"
        self.color = Colors.BLUE
        self.type = "NOTE"

class Warning(_tiw):

    def __init__(self, idx = 0, parent = None):
        super(Warning, self).__init__(idx, parent)

    def init_values(self):

        self._text = "warning"
        self.icon = "s_warning"
        self.icon_lbl = "Warning"
        self.color_n = "red"
        self.color = Colors.RED
        self.type = "WARNING"

class Parameters(QtGui.QWidget, WidgetInterface):

    def __init__(self, node=None, idx=0, parent=None):
        super(Parameters, self).__init__(parent=parent)

        self.idx = idx
        self.parms = node.parms()
        self.parm_blocks = []
        self.widgets = []
        
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)

        # init parm dict
        self.parms_dict = {}
        tmp_names = []
        self.parms_dict["_NO_FODER_"] = []

        for p in self.parms:

            t = p.parmTemplate()
            
            # skip folders and parm with no help set or invisible
            if t.type() in [hou.parmTemplateType.FolderSet,
                            hou.parmTemplateType.Folder]:
                continue

            help = t.help()
            if not help:
                continue

            if t.isHidden():
                continue
            
            # fetch name and label, remove last digit when parm is vector
            # if name already in tmp_name: skip it ( used for vector )
            t_name = t.name()
            if t.numComponents() > 1:
                t_name = t_name[:-1]
            if t_name in tmp_names:
                continue
            tmp_names.append(t_name)
            t_label = t.label()

            # populate parms / folder dictionary
            container = p.containingFolders()
            if len(container) == 0:
                self.parms_dict["_NO_FODER_"].append([t_label, help])
            else:
                container = container[-1]
                if container not in self.parms_dict.keys():
                    self.parms_dict[container] = [[t_label, help]]
                else:
                    self.parms_dict[container].append([t_label, help])
        
        layout = QtGui.QHBoxLayout()
        self.top_w = parent

        params_layout = QtGui.QVBoxLayout()
        params_layout.setContentsMargins(0,0,0,0)
        params_layout.setSpacing(2)
        lbl = QtGui.QLabel("Parameters")
        lbl.setContentsMargins(2,15,2,2)
        lbl.setStyleSheet("""QLabel{background-color: Transparent;
                                    font-family: Arial;
                                    color: black;
                                    font-size: 15pt;
                                    font-weight: bold}""")
        params_layout.addWidget(lbl)

        # orphan params
        for k in self.parms_dict["_NO_FODER_"]:

            p = _parmblock(k[0], k[1], self)
            self.parm_blocks.append(p)
            params_layout.addWidget(p)
            self.widgets.append(p)

        for k in reversed(self.parms_dict.keys()):

            if k == "_NO_FODER_": continue

            k_lbl = CLabel(k)
            k_lbl.setStyleSheet("""QLabel{background-color: Transparent;
                                            font-family: Arial; 
                                            font-size: 10pt;
                                            font-weight: bold;
                                            color: black;}""")
            k_lbl.setContentsMargins(2,10,2,2)
            params_layout.addWidget(k_lbl)
            self.widgets.append(k_lbl)

            for _pn, _ph in self.parms_dict[k]:

                p = _parmblock(_pn, _ph, self)
                self.parm_blocks.append(p)
                params_layout.addWidget(p)
                self.widgets.append(p)

        layout.addItem(params_layout)
        
        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)

        self.setContentsMargins(5,5,5,5)
        self.setLayout(layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        out = "@parameters\n"
        out += "\n".join([w.output() for w in self.widgets])
        return out

class _parmblock(QtGui.QWidget):
    """ Parameter label / help block, used in Parameters object
    """
    def __init__(self, parm_name, parm_help, parent=None):
        super(_parmblock, self).__init__(parent=parent)

        self.parm_name = parm_name
        self.parm_help = parm_help

        layout = QtGui.QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(10,1,1,1)

        self.setAutoFillBackground(True)

        # parm's name
        name_w = QtGui.QWidget(self)
        name_w.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        name_w.setMinimumWidth(100)
        name_w.setMaximumWidth(200)
        name_w.setAutoFillBackground(True)
        name_w.setObjectName("name_w")
        name_w.setStyleSheet("""QWidget{background-color: #f3f3f3;
                                               color: black}""")
        name_layout = QtGui.QVBoxLayout()
        name_layout.setContentsMargins(15,0,0,0)
        name_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.name = QtGui.QLabel(self.parm_name)
        self.name.setStyleSheet("""QLabel{font-weight: bold;} """)
        self.name.setAlignment(QtCore.Qt.AlignRight)
        self.name.setContentsMargins(5,5,5,5)
        self.name.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.name.setWordWrap(True)
        name_layout.addWidget(self.name)
        name_w.setLayout(name_layout)

        # parm's help
        help_w = QtGui.QWidget(self)
        help_w.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Maximum)
        help_w.setAutoFillBackground(True)
        help_w.setObjectName("name_w")
        help_w.setStyleSheet("""QWidget{background-color: #ececec;
                                        color: black}""")
        help_layout = QtGui.QVBoxLayout()
        help_layout.setContentsMargins(0,0,0,0)
        help_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.help = TextBlock(text=self.parm_help, show_btn=False)#QtGui.QLabel(self.parm_help)
        self.help.text.setStyleSheet("""QTextEdit{background-color: #ececec;
                                                  border: 0px;
                                                  color: black}""")
        self.help.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Maximum)
        help_layout.addWidget(self.help)
        help_w.setLayout(help_layout)

        layout.addWidget(name_w)
        layout.addWidget(help_w)
        
        self.setLayout(layout)

    def output(self):

        return "\n" + self.parm_name + ':' + \
               "\n    " + self.help.text.toPlainText().replace('\n', '\n    ') + "\n"

class Separator(QtGui.QWidget, WidgetInterface):

    def __init__(self, idx=0, parent=None):
        super(Separator, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        
        layout = QtGui.QHBoxLayout()

        self.setObjectName("base")
        self.setAcceptDrops(True)

        sep = QtGui.QFrame()
        sep.setObjectName("sep")
        sep.setAcceptDrops(False)
        sep.setFrameStyle(QtGui.QFrame.HLine)
        sep.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Expanding)
        layout.addWidget(sep)

        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)

        layout.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Maximum)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        self.setStyleSheet("""QWidget{background-color: transparent;color:black}
                              QWidget:hover{background-color: rgba(0,0,80,16)}""")

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        return '\n~~~\n'

class TextBox(QtGui.QWidget, WidgetInterface):

    def __init__(self, text="", idx=0,
                 color_str="blue", parent=None):
        super(TextBox, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.color = getattr(BoxColors, color_str.upper())
        self.color_str = color_str

        self.apply_color()

        layout = QtGui.QHBoxLayout()
        self.text = QtGui.QLineEdit(text)
        self.text.setAcceptDrops(False)
        self.text.setContentsMargins(5,10,10,10)
        self.text.setTextMargins(10,10,10,10)
        layout.addWidget(self.text)

        change_color_btn = QtGui.QToolButton()
        change_color_btn.setStyleSheet("""QToolButton{background-color:
                                          transparent;border: 0px}""")
        change_color_btn.setIcon(get_icon("color"))
        change_color_btn.clicked.connect(self.change_color)
        layout.addWidget(change_color_btn)

        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)

        layout.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Maximum)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def apply_color(self):

        color_str = ','.join([str(v) for v in [self.color.red(),
                                               self.color.green(),
                                               self.color.blue()]])

        self.setStyleSheet("""QWidget{background-color: rgb(""" + color_str + """);
                                       border: 1px solid black;
                                       border-radius: 8px;
                                       color: black}""")

    def change_color(self):

        w = ColorChooser()
        w.setStyleSheet(hou.ui.qtStyleSheet())
        w.exec_()
        color = w.color
        if color:
            self.color = getattr(BoxColors, color)
            self.color_str = color.lower()
            self.apply_color() 

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        return '\n:box:\n    #display: bordered ' + \
               self.color_str + '\n    ' + \
               self.text.text()