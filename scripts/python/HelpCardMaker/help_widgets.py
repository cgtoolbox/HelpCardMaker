import HelpCardMaker
VERSION = HelpCardMaker.__version__

import hou
import os
import tempfile
import uuid
import traceback
from collections import OrderedDict

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from HelpCardMaker import core
reload(core)
from HelpCardMaker import utils
reload(utils)

from HelpCardMaker.ui import *
from HelpCardMaker.core import *
from HelpCardMaker.utils import *

class TextBlock(QtWidgets.QWidget, WidgetInterface):
    """ Basic automatically resizable text block used for multilines
        string texts.
    """
    
    text_changed_sgn = QtCore.Signal(str)

    def __init__(self, text="Text", idx=0, show_btn=True, parent=None):
        super(TextBlock, self).__init__(parent=parent)
        WidgetInterface.__init__(self, idx, show_handle=show_btn, parent=parent)

        self.text = QtWidgets.QTextEdit()
        self.text.textChanged.connect(self._emit_sgn)
        self.text.setAcceptDrops(False)

        doc = QtGui.QTextDocument()
        doc.setPlainText(text)

        self.text.setDocument(doc)
        self.text.updateGeometry()
        h = self.text.document().size().height()
        self.text.setMaximumHeight(h)
        
        self.text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text.setWordWrapMode(QtGui.QTextOption.WordWrap)
        self.text.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)
        self.text.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                QtWidgets.QSizePolicy.MinimumExpanding)
        self.setStyleSheet("""QTextEdit{background-color: transparent;
                                         border: 0px;
                                         color: black}
                               QTextEdit:hover{background-color: rgba(0,0,80,16)}""")
        self.main_layout.addWidget(self.text)
        
        if show_btn:
            self.create_delete_btn()
        
        self.setLayout(self.main_layout)

    def _emit_sgn(self):

        self.text_changed_sgn.emit(self.text.toPlainText())

    def update_height(self):

        h = self.text.document().size().height()
        self.text.setFixedHeight(h)

    def dropEvent(self, event):
        return #WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return #WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return #WidgetInterface.dragMoveEvent(self, event)

    def keyReleaseEvent(self, event):

        self.update_height()
        super(TextBlock, self).keyReleaseEvent(event)

    def resizeEvent(self, event):

        self.update_height()
        super(TextBlock, self).resizeEvent(event)

    def toPlainText(self):

        return self.text.toPlainText()

    def output(self):
        allFormats = self.text.document().allFormats()
        return '//TEXTBLOCK\n' + self.text.toPlainText()

class MainTitle(QtWidgets.QWidget, WidgetInterface):

    def __init__(self, text="", idx=0, context="", asset=None,
                 icon="", icon_data=None, parent=None):
        super(MainTitle, self).__init__(parent=parent)
        WidgetInterface.__init__(self, idx, parent=parent)
        
        text_layout = QtWidgets.QVBoxLayout()
        
        self.text = QtWidgets.QLineEdit()
        self.text.setAcceptDrops(False)

        self.extra_infos = ""
        self.asset = asset 
        self.main_icon_section = icon
        self.main_icon_data = icon_data

        if not text:
            t = self.asset.type()
            text = t.name().replace('_', ' ')
            context = t.category().name().lower()

        if not context:
            if context == "object":
                context = "obj"

        self.extra_infos += "#type: node\n#context: " + context + '\n'

        if not self.main_icon_data:
            self.fetch_icon()

        icon_pix = QtGui.QPixmap()
        icon_pix.loadFromData(self.main_icon_data)
        icon_lbl = QtWidgets.QLabel("")
        icon_lbl.setFixedHeight(32)
        icon_lbl.setFixedWidth(32)
        icon_lbl.setPixmap(icon_pix)
        self.main_layout.addWidget(icon_lbl)

        self.text.setText(text)
        self.setStyleSheet("""QLineEdit{background-color: transparent;
                                         border: 0px;
                                         color: black;
                                         font-size: 12pt;
                                         font-family: Arial;;
                                         font-weight: bold}
                              QLineEdit:hover{background-color: rgba(0,0,80,16)}""")
        text_layout.addWidget(self.text)

        k = self.asset.type().category().name().lower()
        context_txt = CONTEXT_REMAP.get(k, "Unknown category node")
        context_lbl = QtWidgets.QLabel(context_txt)
        context_lbl.setStyleSheet("""QLabel{color: grey;
                                            font-size: 10pt;
                                            font-family: Arial}""")
        text_layout.addWidget(context_lbl)

        self.main_layout.addLayout(text_layout)
        
        self.create_delete_btn()
        self.setLayout(self.main_layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def fetch_icon(self):
        """ Fetch the selected node's icon binary data
        """
        node_type = self.asset.type()
        node_def = node_type.definition()
        qicon = hou.ui.createQtIcon(node_def.icon())
        pix = qicon.pixmap(32,32).toImage()
        data = QtCore.QByteArray()
        buffer = QtCore.QBuffer(data)
        buffer.open(QtCore.QIODevice.WriteOnly)
        pix.save(buffer, "PNG")
        
        self.main_icon_section = "HELP_CARD_ICO_" + node_def.nodeTypeName() + ".png"
        self.main_icon_data = str(buffer.data())

    def save_icon(self):
        """ Save icon binary data to asset extra files, also update the extra_info
            with the icon link.
        """
        node_type = self.asset.type()
        node_def = node_type.definition()
        sections = node_def.sections()
        section = sections.get(self.main_icon_section)
        if not section:
            node_def.addSection(self.main_icon_section, self.main_icon_data)
        else:
            section.setContents(self.main_icon_data)

        self.extra_infos += "#icon: opdef:" + node_type.nameWithCategory()
        self.extra_infos += "?" + self.main_icon_section

    def output(self):

        self.save_icon()
        return "//MAINTITLE\n" + '= ' + self.text.text() + \
                ' =\n' + self.extra_infos

class Title(QtWidgets.QWidget, WidgetInterface):
    """ Simple line text input for title help widget.
    """
    def __init__(self, title_type=None, text="Title", idx=0,
                 parent=None):
        super(Title, self).__init__(parent=parent)
        WidgetInterface.__init__(self, idx, parent=parent)
        
        self.title_type = title_type
        
        self.text = QtWidgets.QLineEdit()
        self.text.setAcceptDrops(False)
        self.extra_infos = ""

        text_color = "black"
        if title_type == TitleType.ENTRY_MENU:
            text_color = "rgba(0,0,105)"

        self.text.setText(text)
        self.setStyleSheet("""QLineEdit{background-color: transparent;
                                         border: 0px;
                                         color: """ + text_color + """;
                                         font-size: """ + str(title_type) + """pt;
                                         font-family: Arial;;
                                         font-weight: bold}
                              QLineEdit:hover{background-color: rgba(0,0,80,16)}""")
        self.main_layout.addWidget(self.text)
        
        self.create_delete_btn()
        
        self.setLayout(self.main_layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):
        
        if self.title_type == TitleType.ENTRY_MENU:
            return "//TITLEENTIRYMENU\n@" + \
                   self.text.text().replace(' ', '') + ' ' + \
                   self.text.text()

        return '//TITLE\n== '+ self.text.text() + \
               ' ' + ' =='

class Bullets(QtWidgets.QWidget, WidgetInterface):

    def __init__(self, texts=["item1", "item2", "item3"], idx=0, parent=None):
        super(Bullets, self).__init__(parent=parent)        
        WidgetInterface.__init__(self, idx, parent=parent)
        
        self.bullets = []

        self.bullets_layout = QtWidgets.QVBoxLayout()
        self.bullets_layout.setSpacing(0)
        self.bullets_layout.setAlignment(QtCore.Qt.AlignTop)
        for text in texts:
            w = Bullet(text=text, parent=self)
            self.bullets_layout.addWidget(w)
            self.bullets.append(w)

        self.main_layout.addLayout(self.bullets_layout)

        self.create_delete_btn()
        self.setLayout(self.main_layout)

    def add_bullet(self, w, text=""):
        
        if text == "":
            text = "item" + str(len(self.bullets) + 1)

        nw = Bullet(text=text, parent=self)
        idx = self.bullets.index(w) + 1

        if idx == len(self.bullets):
            self.bullets_layout.addWidget(nw)
            self.bullets.append(nw)
        else:
            self.bullets.insert(idx, nw)
            self.bullets_layout.insertWidget(idx, nw)

    def remove_bullet(self, w):

        if w in self.bullets and len(self.bullets) > 1:
            
            idx = self.bullets.index(w)
            w.setParent(None)
            self.bullets.pop(idx)
            w.deleteLater()

    def output(self):
        
        return "//BULLETS\n" + '\n'.join([w.output() for w in self.bullets])

class Bullet(QtWidgets.QWidget, WidgetInterface):
    """ Text block formatted with a small bullet icon
    """
    def __init__(self, text="", idx=0, parent=None):
        super(Bullet, self).__init__(parent=parent)        
        WidgetInterface.__init__(self, idx, show_handle=False, parent=parent)
        
        ico_lay = QtWidgets.QVBoxLayout()
        ico_lay.setContentsMargins(5,5,5,5)
        self.ico = QtWidgets.QLabel("")
        self.ico.setFixedSize(10,10)
        self.ico.setPixmap(get_icon("s_dot").pixmap(6,6))
        self.ico.setAlignment(QtCore.Qt.AlignTop)
        ico_lay.addWidget(self.ico)

        self.main_layout.addLayout(ico_lay)

        self.text = TextBlock(text=text, show_btn=False, parent=self)
        self.text.text.keyPressEvent = self._keyPressEvent
        self.main_layout.addWidget(self.text)
            
        self.setLayout(self.main_layout)

    def _keyPressEvent(self, e):
        
        if e.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:

            doc = self.text.text.document()
            cursor = self.text.text.textCursor()
            cursor.movePosition(QtGui.QTextCursor.EndOfBlock,
                                QtGui.QTextCursor.KeepAnchor,
                                QtGui.QTextCursor.End)
            cursor.select(QtGui.QTextCursor.WordUnderCursor)
            txt = cursor.selectedText()
            if txt != self.text.text.toPlainText():
                cursor.removeSelectedText()
                self.text.text.setTextCursor(cursor)
                self.top_w.add_bullet(self, txt)
            else:
                self.top_w.add_bullet(self)

        elif e.key() == QtCore.Qt.Key_Backspace:
            if self.text.text.toPlainText() == "":
                self.top_w.remove_bullet(self)
            else:
                QtWidgets.QTextEdit.keyPressEvent(self.text.text, e)
        else:
            QtWidgets.QTextEdit.keyPressEvent(self.text.text, e)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        return '* ' + self.text.toPlainText().replace('\n', ' ')

class _tiw(QtWidgets.QFrame, WidgetInterface):
    """ Base class for Tips, Warning and Info widgets
    """
    def __init__(self, text="tips", idx=0, parent=None):
        super(_tiw, self).__init__(parent=parent)
        WidgetInterface.__init__(self, idx, parent=parent)
        
        self.default_text = text

        self.init_values()
        self.init_widget()

    def init_values(self):
    
        self.icon = "s_tips"
        self.icon_lbl = "Tip"
        self.color_n = "yellow"
        self.color = Colors.YELLOW
        self.color_bg = Colors.GREEN_LIGHT
        self.type = "TIP"

    def init_widget(self):

        self.setAcceptDrops(True)

        tips_layout = QtWidgets.QVBoxLayout()

        tip_lbl_lay = QtWidgets.QHBoxLayout()
        tip_lbl_lay.setAlignment(QtCore.Qt.AlignLeft)
        tip_lbl_lay.setSpacing(10)

        v_sep = wSep(orientation=QtCore.Qt.Vertical)
        v_sep.setFixedWidth(2)
        self.main_layout.addWidget(v_sep)

        tip_ico = QtWidgets.QLabel("")
        tip_ico.setFixedHeight(16)
        tip_ico.setFixedWidth(16)
        tip_ico.setPixmap(get_icon(self.icon).pixmap(16,16))
        tip_lbl_lay.addWidget(tip_ico)
        tip_lbl = QtWidgets.QLabel(self.icon_lbl)
        tip_lbl_lay.addWidget(tip_lbl)
        color_str = ','.join([str(self.color.red()),
                              str(self.color.green()),
                              str(self.color.blue())])
        color_bg_str = ','.join([str(self.color_bg.red()),
                                 str(self.color_bg.green()),
                                 str(self.color_bg.blue())])

        tip_lbl.setStyleSheet("""QLabel{color: rgba(""" + color_str + """,255);
                                        font-size: 11pt;
                                        font-weight: bold;}""")
        self.setStyleSheet("""QFrame{background-color: rgba(""" + color_bg_str + """,255);}""")
        v_sep.setStyleSheet("background-color: rgba(" + color_str + ",255)")
        
        tips_layout.addItem(tip_lbl_lay)

        self.text = TextBlock(text=self.default_text, show_btn=False, parent=self)
        tips_layout.addWidget(self.text)

        self.main_layout.addItem(tips_layout)
        
        self.create_delete_btn()
        self.setLayout(self.main_layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        return "//"+ self.type + "\n" + \
               self.type + ":\n    #display: " + \
               self.color_n + "\n    " + \
               self.text.text.toPlainText()

class Tips(_tiw):
    """ Tips formatted help text ( with bulb icon )
    """
    def __init__(self, text="Tips", idx=0, parent=None):
        super(Tips, self).__init__(text=text, idx=idx, parent=parent)

class Note(_tiw):   
    """ Note formatted help text ( with (!) icon )
    """
    def __init__(self, text="info", idx=0, parent=None):
        super(Note, self).__init__(text=text, idx=idx, parent=parent)

    def init_values(self):
        
        self.icon = "s_info"
        self.icon_lbl = "Info"
        self.color_n = "blue"
        self.color = Colors.BLUE
        self.color_bg = Colors.PURPLE_LIGHT
        self.type = "NOTE"

class Warning(_tiw):
    """ Warning formatted help text ( with warning icon )
    """
    def __init__(self, text="warning", idx=0, parent=None):
        super(Warning, self).__init__(text=text, idx=idx, parent=parent)

    def init_values(self):
        
        self.icon = "s_warning"
        self.icon_lbl = "Warning"
        self.color_n = "red"
        self.color = Colors.RED
        self.color_bg = Colors.RED_LIGHT
        self.type = "WARNING"

class Parameters(QtWidgets.QWidget, WidgetInterface):
    """ A grid layer widget with section name. Created from given
        selected node parameters label and help.
        Folder are formatted as section title

        -Folder Name-
           parm label A : parm help A
           parm label B : parm help B
           ...

        Only the parameters with help tool and visible are fetched.
        The help value can by edited.
    """
    def __init__(self, node=None, idx=0, parms_dict=None, parent=None):
        super(Parameters, self).__init__(parent=parent)
        WidgetInterface.__init__(self, idx, parent=parent)
        
        self.parm_blocks = []
        self.widgets = []
        
        self.setAutoFillBackground(True)

        # init parm dict from the selected node or from a given parm dict
        # when help card is read.
        self.parms_dict = parms_dict
        if not self.parms_dict:

            self.parms = node.parms()
            self.parm_tuples = node.parmTuples()
            tmp_names = []
            self.parms_dict = OrderedDict()
            self.parms_dict["_NO_FOLDER_"] = []
            
            # create folders
            for p in [_p for _p in self.parm_tuples if \
                      _p.parmTemplate().type() in FOLDER_TYPES]:

                t = p.parmTemplate()
                if t.folderType() in MULTIPARM_TYPES:
                    continue

                lbl = t.label()
                if lbl:
                    self.parms_dict[lbl] = []

            # parse parameters and multiparms
            for p in self.parms:

                t = p.parmTemplate()

                # skip multiparm instances, the first parameter will be fetched from
                # multiparm parameter itself
                if p.isMultiParmInstance():
                    continue
            
                # fetch multiparms
                if t.type() == hou.parmTemplateType.Folder and \
                   t.folderType() in MULTIPARM_TYPES:
                    
                    instances = p.multiParmInstances()
                    if not instances: continue
                    
                    nInstances = p.eval()  # number of block instances
                    nParms = len(instances) / nInstances

                    mParms = []
                    for i in range(nParms):
                        _p = instances[i]
                        _t = _p.parmTemplate()
                        mParms.append([_t.label(), _t.help()])

                    self.parms_dict[t.label() + " (multiparm)"] = mParms

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
                    self.parms_dict["_NO_FOLDER_"].append([t_label, help])
                else:
                    container = container[-1]
                    if container not in self.parms_dict.keys():
                        self.parms_dict[container] = [[t_label, help]]
                    else:
                        self.parms_dict[container].append([t_label, help])

        self.top_w = parent
        self.setContentsMargins(0,0,0,0)
        self.parms_layout = QtWidgets.QVBoxLayout()
        self.parms_layout.setContentsMargins(0,0,0,0)
        self.parms_layout.setSpacing(0)
        lbl = QtWidgets.QLabel("PARAMETERS")
        lbl.setStyleSheet("""QLabel{background-color: Transparent;
                                    font-family: Source Sans Pro;
                                    color: black;
                                    font-size: 10pt}""")
        self.parms_layout.addWidget(lbl)
        self.parms_layout.addWidget(wSep())
        
        # orphan params
        for k in self.parms_dict["_NO_FOLDER_"]:

            p = ParmBlock(k[0], k[1], self)
            self.parms_layout.addWidget(p)
            self.widgets.append(p)

        for i, k in enumerate(self.parms_dict.keys()):

            if k == "_NO_FOLDER_": continue

            k_lbl = CLabel(k, parent=self)
            self.parm_blocks.append(k_lbl)
            k_lbl.setStyleSheet("""QLabel{background-color: Transparent;
                                            font-family: Source Sans Pro; 
                                            font-size: 10pt;
                                            color: black;}""")
            self.parms_layout.addWidget(k_lbl)
            self.widgets.append(k_lbl)

            for _pn, _ph in self.parms_dict[k]:

                p = ParmBlock(_pn, _ph, self)
                self.parm_blocks.append(p)
                self.parms_layout.addWidget(p)
                self.widgets.append(p)

        self.main_layout.addItem(self.parms_layout)
        
        self.create_delete_btn()
        
        self.setLayout(self.main_layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def remove_widget(self, pb):

        if pb in self.widgets:

            pb.setParent(None)
            self.parms_layout.removeWidget(pb)
            self.widgets.pop(self.widgets.index(pb))
            pb.deleteLater()

    def output(self):

        out = "//PARAMETERS\n"
        out += "@parameters\n"
        out += "\n".join([w.output() for w in self.widgets])
        return out

class ParmBlock(QtWidgets.QWidget):
    """ Parameter label / help block, used in Parameters object.
    """
    def __init__(self, parm_name, parm_help, parent=None):
        super(ParmBlock, self).__init__(parent=parent)

        self.parm_name = parm_name
        self.parm_help = parm_help
        self.top_w = parent

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10,1,1,1)
        self.setContentsMargins(0,0,0,0)

        self.setAutoFillBackground(True)
        
        # parm's name
        self.name = TextBlock(text=self.parm_name, show_btn=False, parent=self)
        self.name.setContentsMargins(0,0,0,0)
        self.name.text.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.name.setStyleSheet("""QTextEdit{background-color: #f2f2f2;
                                          color: black;
                                          font-weight: bold;
                                          border: 0px;
                                          font-family: Source Sans Pro;}""")
        self.name.setMaximumWidth(200)
        self.name.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Minimum)

        # parm's help
        self.help = TextBlock(text=self.parm_help, show_btn=False, parent=self)
        self.help.setContentsMargins(0,0,0,0)
        self.help.text.setStyleSheet("""QTextEdit{background-color: #ececec;
                                                  color: black;
                                                  font-family: Source Sans Pro;}""")
        self.help.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Maximum)
        
        layout.addWidget(self.name)
        layout.addWidget(self.help)
        
        self.delete_btn = QtWidgets.QToolButton()
        self.delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        self.delete_btn.setIcon(get_icon("close"))
        self.delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(self.delete_btn)
        
        self.setLayout(layout)

    def remove_me(self):

        self.top_w.remove_widget(self)

    def output(self):
        
        return self.parm_name + ':' + \
               "\n    " + self.help.text.toPlainText().replace('\n', '\n    ')

class Separator(QtWidgets.QWidget, WidgetInterface):
    """ Simple horizontal separator line help widget
    """
    def __init__(self, idx=0, parent=None):
        super(Separator, self).__init__(parent=parent)
        WidgetInterface.__init__(self, idx, parent=parent)
        
        sep = QtWidgets.QFrame()
        sep.setObjectName("sep")
        sep.setAcceptDrops(False)
        sep.setFrameStyle(QtWidgets.QFrame.HLine)
        sep.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                           QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addWidget(sep)

        self.create_delete_btn()

        self.setLayout(self.main_layout)

        self.setStyleSheet("""QWidget{background-color: transparent;color:black}
                              QWidget:hover{background-color: rgba(0,0,80,16)}""")

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def data(self):

        return {"type":"Separator"}

    def output(self):

        return '//SEPARATOR\n~~~'

class TextBox(QtWidgets.QFrame, WidgetInterface):
    """ Text block formatted in a rounded edges colored box.
    """
    def __init__(self, text="text", idx=0,
                 color_str="blue", title="Box title", parent=None):
        super(TextBox, self).__init__(parent=parent)
        WidgetInterface.__init__(self, idx, parent=parent)

        self.setAutoFillBackground(True)
        self.color = getattr(BoxColors, color_str.upper())
        self.color_str = color_str
        
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(2)

        self.title = title
        self.title_input = TextBlock(text=title, show_btn=False, parent=self)
        self.title_input.setStyleSheet("""QTextEdit{background-color: transparent;
                                         border: 0px;
                                         color: rgb(74, 160, 163, 255)}
                               QTextEdit:hover{background-color: rgba(0,0,80,16)}""")
        layout.addWidget(self.title_input)
        layout.setContentsMargins(0,0,0,0)

        self.text_input = QtWidgets.QTextEdit()
        self.text_input.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text_input.setText(text)
        mh = self.text_input.document().size().height() + 20
        self.text_input.setFixedHeight(mh + 20)
        self.text_input.setAcceptDrops(False)
        self.text_input.setContentsMargins(5,10,10,10)
        self.text_input.setViewportMargins(10,10,10,10)
        layout.addWidget(self.text_input)

        self.main_layout.addLayout(layout)

        change_color_btn = QtWidgets.QToolButton()
        change_color_btn.setStyleSheet("""QToolButton{background-color:
                                          transparent;border: 0px}""")
        change_color_btn.setIcon(get_icon("color"))
        change_color_btn.clicked.connect(self.change_color)
        self.main_layout.addWidget(change_color_btn)

        self.create_delete_btn()
        self.setLayout(self.main_layout)

        self.apply_color()

    def apply_color(self):

        color_str = ','.join([str(v) for v in [self.color.red(),
                                               self.color.green(),
                                               self.color.blue()]])

        self.setStyleSheet("""QTextEdit{background-color: rgb(""" + color_str + """);
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

    def keyReleaseEvent(self, event):

        self.text_input.setFixedHeight(self.text_input.document().size().height() + 20)
        super(TextBox, self).keyReleaseEvent(event)

    def data(self):

        return {"type" : "TextBox",
                text : self.text_input.toPlainText(),
                color_str : self.color_str}

    def output(self):

        return '//TEXTBOX\n' + \
               '\n:box:{}\n    #display: raised '.format(self.text_input.toPlainText()) + \
               self.color_str + '\n    ' + \
               self.text_input.toPlainText().replace('\n', ' ')

class ImageFromDisk(QtWidgets.QWidget, WidgetInterface):
    """ Fetch a png image from disk and add it to the help card.
        The file is embedded in the asset external file section with the
        output() method is called. The link in the help card 
        will point to this embedded file.
    """
    def __init__(self, img="", img_data=None, idx=0, parent=None):
        super(ImageFromDisk, self).__init__(parent=parent)
        WidgetInterface.__init__(self, idx, parent=parent)
        
        self.setAutoFillBackground(True)
        self.img_file = img
        self.img_name = os.path.split(img)[1]
        self.section_name = "HELP_CARD_IMG_" + self.img_name

        self.img_data = img_data
        if not self.img_data:
            with open(img, 'rb') as f: data = f.read()
            self.img_data = data

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(self.img_data)

        self.img = QtWidgets.QLabel("")
        self.img.setFixedHeight(pixmap.height())
        self.img.setFixedWidth(pixmap.width())
        self.img.setPixmap(pixmap)
        self.main_layout.addWidget(self.img)

        self.create_delete_btn()
        self.setLayout(self.main_layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def _save_img_to_asset(self, definition):
        """ Called when only output() is called, save the image data
            to an HDA section to fetch the image from.
        """ 
        section = definition.sections().get(self.section_name)
        if not section:
            section= definition.addSection(self.section_name,
                                           self.img_data)
        else:
            section.setContents(self.img_data)

    def output(self):

        node = hou.selectedNodes()[0]
        definition = node.type().definition()

        self._save_img_to_asset(definition)

        tag = node.type().nameWithCategory() + "?"

        return "//IMG\n" + \
               "[Image:opdef:/"+ tag + self.section_name + "]"

class Vimeo(QtWidgets.QWidget, WidgetInterface):

    def __init__(self, title="Video tite", video_id="00000000",
                 idx=0, parent=None):
        super(Vimeo, self).__init__(parent=parent)
        WidgetInterface.__init__(self, idx=idx, parent=parent)

        self.title = title
        self.video_id = video_id

        ico = QtWidgets.QLabel("")
        ico.setFixedSize(QtCore.QSize(32, 32))
        pixmap = get_icon("vimeo").pixmap(32,32)
        ico.setPixmap(pixmap)
        self.main_layout.addWidget(ico)

        infos_layout = QtWidgets.QVBoxLayout()
        infos_layout.setAlignment(QtCore.Qt.AlignTop)

        self.title_input = TextBlock(text=title, show_btn=False, parent=self)
        self.title_input.text_changed_sgn.connect(self.video_title_changed)
        self.title_input.setAcceptDrops(False)
        infos_layout.addWidget(self.title_input)

        id_layout = QtWidgets.QHBoxLayout()
        id_layout.setAlignment(QtCore.Qt.AlignLeft)
        id_layout.addWidget(QtWidgets.QLabel("#id:"))

        self.video_id_input = TextBlock(text=video_id, show_btn=False, parent=self)
        self.video_id_input.text_changed_sgn.connect(self.video_id_changed)
        self.video_id_input.setAcceptDrops(False)
        id_layout.addWidget(self.video_id_input)

        infos_layout.addLayout(id_layout)

        self.main_layout.addLayout(infos_layout)

        self.create_delete_btn()

        self.setLayout(self.main_layout)

    def video_id_changed(self, s):

        self.video_id = s

    def video_title_changed(self, s):

        self.title = s

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        return "//VIMEO\n" + \
                ":vimeo: {}\n    #id:{}".format(self.title,
                                                self.video_id)