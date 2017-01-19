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

VERSION = "0.9.4"

import hou
import os
from collections import OrderedDict

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
    
class TitleType(object):
    
    TITLE = 11
    ENTRY_MENU = 12

CONTEXT_REMAP = {
                 "sop":"Geometry node",
                 "object":"Object node",
                 "obj":"Object node",
                 "cop2":"Compositing node",
                 "vop":"VOP node",
                 "particle": "Particle node",
                 "pop": "POP node",
                 "dop": "DOP node",
                 "chop": "CHOP node",
                }

MULTIPARM_TYPES = [hou.folderType.MultiparmBlock,
                   hou.folderType.ScrollingMultiparmBlock,
                   hou.folderType.TabbedMultiparmBlock]

FOLDER_TYPES = [hou.parmTemplateType.FolderSet,
                hou.parmTemplateType.Folder]

class WidgetInterface(object):
    """ Help widgets interface for drag and drop system implementation
    """
    def dragEnterEvent(self, event):

        return

    def dragMoveEvent(self, event):
        
        return

    def dropEvent(self, event):
        
        if not self.top_w: return
        data = event.mimeData().text()

        # insert a widget
        if data.startswith("%HCM_W%"):
            self.top_w.insert_widget(data.split('_')[-1], self.idx + 1)

        # widget has been moved
        elif data.startswith("%W%"):
            idx_from = int(data.split(';')[-1])
            self.top_w.move_widget(idx_from, self.idx)

        else:
            self.text.setPlainText(self.text.toPlainText() + data)

    def remove_me(self):
        
        self.top_w.remove_widget(self)

class WidgetHandle(QtGui.QFrame):

    def __init__(self, idx=0, parent=None):
        super(WidgetHandle, self).__init__(parent=parent)

        self.widget = parent
        self.setObjectName("handle")
        self.setStyleSheet("""QFrame#handle{background-color: #eaeaea;}
                              QFrame#handle:hover{background-color: #d5dae5;}""")
        self.setFixedWidth(10)

    def mousePressEvent(self, event):

        pix = QtGui.QPixmap(self.widget.size())
        self.widget.render(pix)

        mimeData = QtCore.QMimeData()
        mimeData.setText("%W%;" + str(self.widget.idx))
        drag = QtGui.QDrag(self)
        
        drag.setPixmap(pix)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())
        drag.start(QtCore.Qt.MoveAction)

class ToolIcon(QtGui.QLabel):
    """ Custom flat icon which stats the drag system, used in 
        toolbar widget only.
    """
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

class CLabel(QtGui.QWidget):
    """ Utilitiy label with output() method to be compatible with
        other help widgets.
    """
    def __init__(self, text="", show_btn=True, parent=None):
        super(CLabel, self).__init__(parent=parent)

        self.top_w = parent

        layout = QtGui.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        self.lbl = QtGui.QLabel(text)
        layout.addWidget(self.lbl)

        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def remove_me(self):

        self.top_w.remove_widget(self)

    def output(self):

        return self.lbl.text() + '\n'

class ColorChooser(QtGui.QDialog):
    """ Custom color picker with button. Parse the given color_class
        to fetch which colors are available.
    """
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
    """ smal vertival separator widget for toolbar
    """
    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.setFrameStyle(QtGui.QFrame.VLine)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Expanding)
        self.setFixedHeight(34)

# MAIN INTERFACE
class MainPanel(QtGui.QFrame):
    """ Main UI for pypanel creation
    """
    def __init__(self, parent=None):
        super(MainPanel, self).__init__(parent=parent)

        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setSpacing(5)

        # toolbar
        self.toolbar = QtGui.QHBoxLayout()
        self.toolbar.setAlignment(QtCore.Qt.AlignLeft)

        self.read_help_btn = QtGui.QToolButton()
        self.read_help_btn.setStyleSheet("""QToolButton{border: None;
                                             background-color: None}""")
        self.read_help_btn.setIcon(get_icon("open_card"))
        self.read_help_btn.setFixedHeight(34)
        self.read_help_btn.setFixedWidth(34)
        self.read_help_btn.setIconSize(QtCore.QSize(32,32))
        self.read_help_btn.clicked.connect(self.read_helpcard)
        self.read_help_btn.setToolTip("Read existing help card from selected asset")
        self.toolbar.addWidget(self.read_help_btn)

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
        self.clear_btn.clicked.connect(self.clean_widgets)
        self.clear_btn.setToolTip("Clear Elements")
        self.toolbar.addWidget(self.clear_btn)

        self.toolbar.addWidget(wSep())

        self.title_main_btn = ToolIcon("header", "%HCM_W%_maintitle")
        self.title_main_btn.setToolTip("Add main title + icon from selected node")
        self.toolbar.addWidget(self.title_main_btn)

        self.title2_btn = ToolIcon("title1", "%HCM_W%_title:2")
        self.title2_btn.setToolTip("Add title")
        self.toolbar.addWidget(self.title2_btn)

        self.title3_btn = ToolIcon("title2", "%HCM_W%_title:3")
        self.title3_btn.setToolTip("Add navigation menu entry")
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

        self.image_btn = ToolIcon("image", "%HCM_W%_image")
        self.image_btn.setToolTip("Add image from disk")
        self.toolbar.addWidget(self.image_btn)

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

    def clean_widgets(self, show_popup=True):
        """ Remove all widgets from the scroll area.
        """
        if show_popup:
            r = hou.ui.displayMessage("Clear all items ?", buttons=["Yes", "Cancel"])
            if r == 1: return

        while len(self.ui_widgets) != 0:
            for w in self.ui_widgets:
                w.remove_me()

    def remove_widget(self, w, delete=True):
        """ Remove a given widget from scroll area
        """
        w.setParent(None)
        self.scroll_lay.removeWidget(w)

        if w in self.ui_widgets:
            id = self.ui_widgets.index(w)
            self.ui_widgets.pop(id)

        if delete:
            w.deleteLater()

        for i, w in enumerate(self.ui_widgets):
            w.idx = i

    def move_widget(self, idx_from, idx_to):
        """ Move a widget using ids from / to.
            Used when widgets are reordered using drag and drops.
        """
        

        it = self.scroll_lay.itemAt(idx_from)
        if not it: return
        w = it.widget()
        if not w: return

        self.remove_widget(w, delete=False)
        
        self.scroll_lay.insertWidget(idx_to, w)
        self.ui_widgets.insert(idx_to, w)

        for i, w in enumerate(self.ui_widgets):
            w.idx = i

    def insert_widget(self, w_type, idx):
        """ Insert a widget to the scroll area, w_type is a formated string
            fetched from a drop Mimedata.
        """
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

        elif w_type == "image":

            img = QtGui.QFileDialog.getOpenFileName(filter="Png (*.png)")
            img = img[0]
            if not img: return

            w = ImageFromDisk(img=img, parent=self)

        elif w_type == "maintitle":

            selection = hou.selectedNodes()
            if not selection:
                hou.ui.displayMessage("Nothing selected")
                return
            main_title = [w for w in self.ui_widgets \
                            if isinstance(w, MainTitle)]
            if main_title:
                hou.ui.displayMessage("Help card contains already a main title")
                return
            selection = selection[0]

            if not selection.type().definition():
                hou.ui.displayMessage("Selected node is not a valid asset")
                return
            idx = 0
            w = MainTitle(asset=selection, parent=self)

        elif w_type.startswith("title:"):

            size = int(w_type.split(':')[-1])
            title_type = TitleType.ENTRY_MENU
            if size == 2:
                title_type = TitleType.TITLE

            w = Title(title_type=title_type, parent=self)

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
        """ Fetch all the output help string from widgets
        """
        return "//HELP CARD MAKER " + VERSION + '\n' + \
               '\n'.join([w.output() for w in self.ui_widgets]) + \
               "\n\n\n//END"

    def apply_help(self):
        """ Apply the sideFX help-wiki formatted strings to the section "Help" of
            the selected asset.
            This also save the current definition of the asset and switch it to 
            'allow editing of contents' mode beforehand.
        """
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
        sections = definition.sections()
        if not definition:
            hou.ui.displayMessage("Selected node is not an digital asset")
            return

        node.allowEditingOfContents()
        help = sections.get("Help", None)
        if not help:
            help = definition.addSection("Help", "")

        help.setContents(self.get_help_str())

        # clean unused help_card sections ( for old images )
        current_imgs = [w.section_name for w in self.ui_widgets \
                        if isinstance(w, ImageFromDisk)]

        current_img_sections = [k for k in sections.keys() if \
                                k.startswith("HELP_CARD_IMG_")]

        for s in current_img_sections:
            if s not in current_imgs:
                sections[s].destroy()

        definition.save(definition.libraryFilePath())
        hou.ui.displayMessage("Help card updated !")
        hou.ui.displayNodeHelp(node.type())

    def read_helpcard(self):
        """ Read the current asset help card (if generated with Help Card Maker only)
        """
        sel = hou.selectedNodes()
        if not sel:
            hou.ui.displayMessage("Nothing selected",
                                  severity=hou.severityType.Error)
            return

        sel = sel[0]
        sel_def = sel.type().definition()
        if not sel_def:
            hou.ui.displayMessage("Selected node is not a valid asset",
                                  severity=hou.severityType.Error)
            return

        help = sel_def.sections().get("Help")
        if not help:
            hou.ui.displayMessage("No help card found in this asset",
                                  severity=hou.severityType.Error)
            return

        help = help.contents()
        if not help.startswith("//HELP CARD MAKER"):
            hou.ui.displayMessage("Can't read current asset's help card",
                                  help="Help card was not created by help card maker",
                                  severity=hou.severityType.Error)
            return

        r = hou.ui.displayMessage("Load current asset help card ?",
                                  buttons=["Yes", "Cancel"])
        if r == 1:
            return

        self.clean_widgets(show_popup=False)

        self.widgets_infos = OrderedDict()
        cur_cluster = True
        help = [n for n in help.split('\n') if n not in ['\n', '']]

        for i, data in enumerate(help):

            if i == 0: continue  # skip header

            if data.startswith('//'):
                cur_cluster = data.replace('//', '').replace('\n', '')
                cur_cluster += '_' + str(i - 1)
                self.widgets_infos[cur_cluster] = []
                continue
            
            self.widgets_infos[cur_cluster].append(data)

        for k in self.widgets_infos.keys():
            self.apply_cluster(k, sel)

    def apply_cluster(self, cluster, asset):
        """ Apply a given "help cluster" and create a help widget accordingly
            (help cluster is info about the widget, type and data).
        """
        w = None
        data = self.widgets_infos[cluster]
        idx = 0
        cluster = cluster.split('_')[0]
        if cluster == "MAINTITLE":
 
            text = data[0].replace("= ", '').replace(" =", '').replace('\n', '')
            context = data[2].replace("#context: ", '').replace('\n', '')
            icon = data[2].split('?')[-1].replace('\n', '')
            icon_section = asset.type().definition().sections().get(icon)
            icon_data = None
            if icon_section:
                icon_data = icon_section.contents()
            w = MainTitle(text=text, context=context,
                          icon=icon, icon_data=icon_data,
                          asset=asset, parent=self)

        elif cluster == "TEXTBLOCK":
            text = '\n'.join(data)
            w = TextBlock(text=text, parent=self)

        elif cluster == "TIP":
            text = "".join([ n[4:] for n in data if not n.startswith("    #")])
            w = Tips(text=text, parent=self)

        elif cluster == "WARNING":
            text = "".join([ n[4:] for n in data[2:]])
            w = Warning(text=text, parent=self)

        elif cluster == "NOTE":
            text = "".join([ n[4:] for n in data[2:]])
            w = Note(text=text, parent=self)

        elif cluster == "SEPARATOR":
            w = Separator(parent=self)

        elif cluster == "TITLEENTIRYMENU":
            text = data[0].split(' ', 1)[-1]
            w = Title(title_type=TitleType.ENTRY_MENU, text=text, parent=self)

        elif cluster == "TITLE":
            text = data[0].replace("== ", '').replace(" ==", '')
            w = Title(title_type=TitleType.TITLE, text=text, parent=self)

        elif cluster == "BULLET":

            cleaned_data = []
            for _d in data:
                if _d.startswith("* "):
                    cleaned_data.append(_d[2:])
                else:
                    cleaned_data.append(_d)

            text = "".join(cleaned_data)
            w = Bullet(text=text, parent=self)

        elif cluster == "TEXTBOX":
            color_str = data[1].split(' ')[-1]
            text = "".join([n[4:] for n in data[2:]])
            w = TextBox(text=text, color_str=color_str, parent=self)

        elif cluster == "IMG":

            img = data[0].split('?')[-1].replace(']', '')
            img_data = asset.type().definition().sections().get(img)
            if not img_data:
                print("Reading Error: " + img + " data not found in asset sections.")
                return
            img_data = img_data.contents()
            img = img.replace("HELP_CARD_IMG_", "")
            w = ImageFromDisk(img=img, img_data=img_data, parent=self)

        elif cluster == "PARAMETERS":

            parms_dict = {"_NO_FOLDER_":[]}
            cur_folder = "_NO_FOLDER_"

            for i in range(len(data) - 1):

                d = data[i]
                next_d = data[i + 1]

                if d == "@parameters": continue
                if d.startswith("    "): continue

                if d.endswith(':') and next_d.startswith("    "):
                    parms_dict[cur_folder].append([d[:-1], next_d[4:]])
                else:
                    cur_folder = d
                    if not cur_folder in parms_dict.keys():
                        parms_dict[cur_folder] = []

                w = Parameters(node=asset, parms_dict=parms_dict, parent=self)

        if w:
            w.idx = idx
            self.scroll_lay.addWidget(w)
            self.ui_widgets.append(w)
            idx += 1

    def show_help(self):
        """ Show little help dialog box about how to use HelpCardMaker
        """
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
    """ Custom widget used in scroll area which supports drag an drop
        system for helkp widgets creation
    """
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
    """ Basic automatically resizable text block used for multilines
        string texts.
    """
    def __init__(self, text="Text", idx=0, show_btn=True, parent=None):
        super(TextBlock, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        self.setAcceptDrops(True)

        layout = QtGui.QHBoxLayout()
        
        if show_btn:
            handle = WidgetHandle(parent=self)
            layout.addWidget(handle)
        
        self.text = QtGui.QTextEdit()
        self.text.setAcceptDrops(False)
        self.text.setPlainText(text)

        doc = QtGui.QTextDocument()
        doc.setPlainText(text)
        self.text.setDocument(doc)
        self.text.updateGeometry()
        h = self.text.document().size().height()
        self.text.setMaximumHeight(h)
        
        self.text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text.setWordWrapMode(QtGui.QTextOption.WordWrap)
        self.text.setLineWrapMode(QtGui.QTextEdit.LineWrapMode.WidgetWidth)
        self.text.setSizePolicy(QtGui.QSizePolicy.Minimum,
                                QtGui.QSizePolicy.MinimumExpanding)
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

    def update_height(self):

        h = self.text.document().size().height()
        self.text.setFixedHeight(h)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def keyReleaseEvent(self, event):

        self.update_height()
        super(TextBlock, self).keyReleaseEvent(event)

    def resizeEvent(self, event):

        self.update_height()
        super(TextBlock, self).resizeEvent(event)

    def output(self):

        return '\n\n//TEXTBLOCK\n\n\n' + self.text.toPlainText() + '\n'

class MainTitle(QtGui.QWidget, WidgetInterface):

    def __init__(self, text="", idx=0, context="", asset=None,
                 icon="", icon_data=None, parent=None):
        super(MainTitle, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx

        self.setAcceptDrops(True)

        layout = QtGui.QHBoxLayout()
        text_layout = QtGui.QVBoxLayout()
        
        self.text = QtGui.QLineEdit()
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
        icon_lbl = QtGui.QLabel("")
        icon_lbl.setFixedHeight(32)
        icon_lbl.setFixedWidth(32)
        icon_lbl.setPixmap(icon_pix)
        layout.addWidget(icon_lbl)

        self.text.setText(text)
        self.setStyleSheet("""QLineEdit{background-color: transparent;
                                         border: 0px;
                                         color: black;
                                         font-size: 16pt;
                                         font-family: Arial;;
                                         font-weight: bold}
                              QLineEdit:hover{background-color: rgba(0,0,80,16)}""")
        text_layout.addWidget(self.text)

        k = self.asset.type().category().name().lower()
        context_txt = CONTEXT_REMAP.get(k, "Unknown category node")
        context_lbl = QtGui.QLabel(context_txt)
        context_lbl.setStyleSheet("""QLabel{color: grey;
                                            font-size: 10pt;
                                            font-family: Arial}""")
        text_layout.addWidget(context_lbl)

        layout.addLayout(text_layout)
        
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
        self.extra_infos += "?" + self.main_icon_section + '\n'

    def output(self):

        self.save_icon()
        return "\n\n//MAINTITLE\n\n\n" + '= ' + self.text.text() + \
                ' =\n' + self.extra_infos

class Title(QtGui.QWidget, WidgetInterface):
    """ Simple line text input for title help widget.
    """
    def __init__(self, title_type=None, text="Title", idx=0,
                 parent=None):
        super(Title, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        self.title_type = title_type
        self.setAcceptDrops(True)

        layout = QtGui.QHBoxLayout()

        handle = WidgetHandle(parent=self)
        layout.addWidget(handle)

        self.text = QtGui.QLineEdit()
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
        
        if self.title_type == TitleType.ENTRY_MENU:
            return "\n\n//TITLEENTIRYMENU\n\n\n@" + \
                   self.text.text().replace(' ', '') + ' ' + \
                   self.text.text() + '\n'

        return '\n\n//TITLE\n\n\n== '+ self.text.text() + \
               ' ' + ' ==' +'\n'

class Bullet(QtGui.QWidget, WidgetInterface):
    """ Text block formatted with a small bullet icon
    """
    def __init__(self, text="item", idx=0, parent=None):
        super(Bullet, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx

        self.setAcceptDrops(True)

        layout = QtGui.QHBoxLayout()
        layout.setSpacing(5)

        handle = WidgetHandle(parent=self)
        layout.addWidget(handle)

        ico_lay = QtGui.QVBoxLayout()
        ico_lay.setContentsMargins(5,5,5,5)
        self.ico = QtGui.QLabel("")
        self.ico.setFixedSize(10,10)
        self.ico.setPixmap(get_icon("s_dot").pixmap(6,6))
        self.ico.setAlignment(QtCore.Qt.AlignTop)
        ico_lay.addWidget(self.ico)

        layout.addLayout(ico_lay)

        self.text = TextBlock(text=text, show_btn=False)
        layout.addWidget(self.text)
        
        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent; border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)

        layout.setContentsMargins(0,0,0,0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def dropEvent(self, event):
        return WidgetInterface.dropEvent(self, event)

    def dragEnterEvent(self, event):
        return WidgetInterface.dragEnterEvent(self, event)

    def dragMoveEvent(self, event):
        return WidgetInterface.dragMoveEvent(self, event)

    def output(self):

        return '\n\n//BULLET\n\n\n* ' \
               + self.text.toPlainText().replace('\n', ' ') + '\n'

class _tiw(QtGui.QWidget, WidgetInterface):
    """ Base class for Tips, Warning and Info widgets
    """
    def __init__(self, text="tips", idx=0, parent=None):
        super(_tiw, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        self.default_text = text

        self.init_values()
        self.init_widget()

    def init_values(self):
    
        self.icon = "s_tips"
        self.icon_lbl = "Tip"
        self.color_n = "yellow"
        self.color = Colors.YELLOW
        self.type = "TIP"

    def init_widget(self):

        self.setAcceptDrops(True)

        layout = QtGui.QHBoxLayout()

        handle = WidgetHandle(parent=self)
        layout.addWidget(handle)

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

        self.text = TextBlock(text=self.default_text, show_btn=False)
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

        return "\n\n//"+ self.type + "\n\n\n" + \
               self.type + ":\n    #display: " + \
               self.color_n + "\n    " + \
               self.text.text.toPlainText() + "\n"

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
        self.type = "WARNING"

class Parameters(QtGui.QWidget, WidgetInterface):
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

        self.idx = idx
        self.parm_blocks = []
        self.widgets = []
        
        self.setAcceptDrops(True)
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
        
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        handle = WidgetHandle(parent=self)
        layout.addWidget(handle)

        self.top_w = parent

        self.parms_layout = QtGui.QVBoxLayout()
        self.parms_layout.setContentsMargins(0,0,0,0)
        self.parms_layout.setSpacing(2)
        lbl = QtGui.QLabel("Parameters")
        lbl.setStyleSheet("""QLabel{background-color: Transparent;
                                    font-family: Arial;
                                    color: black;
                                    font-size: 15pt;
                                    font-weight: bold}""")
        self.parms_layout.addWidget(lbl)

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
                                            font-family: Arial; 
                                            font-size: 10pt;
                                            font-weight: bold;
                                            color: black;}""")
            self.parms_layout.addWidget(k_lbl)
            self.widgets.append(k_lbl)

            for _pn, _ph in self.parms_dict[k]:

                p = ParmBlock(_pn, _ph, self)
                self.parm_blocks.append(p)
                self.parms_layout.addWidget(p)
                self.widgets.append(p)

        layout.addItem(self.parms_layout)
        
        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)
        layout.addWidget(delete_btn)
        
        self.setLayout(layout)

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

        out = "\n\n//PARAMETERS\n\n\n"
        out += "@parameters\n"
        out += "\n".join([w.output() for w in self.widgets])
        return out

class ParmBlock(QtGui.QWidget):
    """ Parameter label / help block, used in Parameters object.
    """
    def __init__(self, parm_name, parm_help, parent=None):
        super(ParmBlock, self).__init__(parent=parent)

        self.parm_name = parm_name
        self.parm_help = parm_help
        self.top_w = parent

        layout = QtGui.QHBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(10,1,1,1)

        self.setAutoFillBackground(True)

        # parm's name
        self.name = QtGui.QLabel(self.parm_name)
        self.name.setStyleSheet("""QLabel{background-color: #ececec;
                                          color: black;
                                          margin:2px}""")
        self.name.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                QtGui.QSizePolicy.Minimum)

        # parm's help
        self.help = TextBlock(text=self.parm_help, show_btn=False)
        self.help.text.setStyleSheet("""QTextEdit{background-color: #ececec;
                                                  color: black}""")
        self.help.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                QtGui.QSizePolicy.Maximum)

        delete_btn = QtGui.QToolButton()
        delete_btn.setStyleSheet("""QToolButton{background-color:
                                    transparent;border: 0px}""")
        delete_btn.setIcon(get_icon("close"))
        delete_btn.clicked.connect(self.remove_me)

        layout.addWidget(self.name)
        layout.addWidget(self.help)
        layout.addWidget(delete_btn)
        
        self.setLayout(layout)

    def remove_me(self):

        self.top_w.remove_widget(self)

    def output(self):
        
        return "\n" + self.parm_name + ':' + \
               "\n    " + self.help.text.toPlainText().replace('\n', '\n    ') + "\n"

class Separator(QtGui.QWidget, WidgetInterface):
    """ Simple horizontal separator line help widget
    """
    def __init__(self, idx=0, parent=None):
        super(Separator, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        self.setObjectName("base")
        self.setAcceptDrops(True)

        layout = QtGui.QHBoxLayout()

        handle = WidgetHandle(parent=self)
        layout.addWidget(handle)

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

        return '\n\n//SEPARATOR\n\n\n~~~\n'

class TextBox(QtGui.QWidget, WidgetInterface):
    """ Text block formatted in a rounded edges colored box.
    """
    def __init__(self, text="text", idx=0,
                 color_str="blue", parent=None):
        super(TextBox, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.color = getattr(BoxColors, color_str.upper())
        self.color_str = color_str

        layout = QtGui.QHBoxLayout()

        handle = WidgetHandle(parent=self)
        handle.setObjectName("handle")
        handle.setStyleSheet("""QFrame#handle{background-color: #eaeaea;
                                              border: 0px}""")
        layout.addWidget(handle)

        self.text_input = QtGui.QTextEdit()
        self.text_input.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.text_input.setText(text)
        mh = self.text_input.document().size().height() + 20
        self.text_input.setFixedHeight(mh + 20)
        self.text_input.setAcceptDrops(False)
        self.text_input.setContentsMargins(5,10,10,10)
        self.text_input.setViewportMargins(10,10,10,10)
        layout.addWidget(self.text_input)

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

        self.apply_color()

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

    def keyReleaseEvent(self, event):

        self.text_input.setFixedHeight(self.text_input.document().size().height() + 20)
        super(TextBox, self).keyReleaseEvent(event)

    def output(self):

        return '\n\n//TEXTBOX\n\n\n' + \
               '\n:box:\n    #display: bordered ' + \
               self.color_str + '\n    ' + \
               self.text_input.toPlainText().replace('\n', ' ')

class ImageFromDisk(QtGui.QWidget, WidgetInterface):
    """ Fetch a png image from disk and add it to the help card.
        The file is embedded in the asset external file section with the
        output() method is called. The link in the help card 
        will point to this embedded file.
    """
    def __init__(self, img="", img_data=None, idx=0, parent=None):
        super(ImageFromDisk, self).__init__(parent=parent)

        self.top_w = parent
        self.idx = idx
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.img_file = img
        self.img_name = os.path.split(img)[1]
        self.section_name = "HELP_CARD_IMG_" + self.img_name

        self.img_data = img_data
        if not self.img_data:
            with open(img, 'rb') as f: data = f.read()
            self.img_data = data

        layout = QtGui.QHBoxLayout()

        handle = WidgetHandle(parent=self)
        layout.addWidget(handle)

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(self.img_data)

        self.img = QtGui.QLabel("")
        self.img.setFixedHeight(pixmap.height())
        self.img.setFixedWidth(pixmap.width())
        self.img.setPixmap(pixmap)
        layout.addWidget(self.img)

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

        return "\n\n//IMG\n\n\n" + \
               "\n[Image:opdef:/"+ tag + self.section_name + "]\n"