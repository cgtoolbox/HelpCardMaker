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

from HelpCardMaker import help_widgets
reload(help_widgets)

from HelpCardMaker.utils import *
from HelpCardMaker.help_widgets import *
from HelpCardMaker.core import *

class MainPanel(QtWidgets.QMainWindow):
    """ Main UI for pypanel creation
    """
    def __init__(self, parent=None):
        super(MainPanel, self).__init__(parent=parent)
        
        cw = QtWidgets.QWidget()

        self.setProperty("houdiniStyle", True)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(5)
        
        # toolbar
        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setFloatable(True)
        self.toolbar.setStyleSheet("""QToolBar{border: 0px;
                                               background-color: None}""")

        self.read_help_btn = QtWidgets.QToolButton()
        self.read_help_btn.setIcon(get_icon("open_card"))
        self.read_help_btn.setFixedHeight(34)
        self.read_help_btn.setFixedWidth(34)
        self.read_help_btn.setIconSize(QtCore.QSize(32,32))
        self.read_help_btn.clicked.connect(self.read_helpcard)
        self.read_help_btn.setToolTip("Read existing help card from selected asset")
        self.toolbar.addWidget(self.read_help_btn)

        self.apply_help_btn = QtWidgets.QToolButton()
        self.apply_help_btn.setIcon(get_icon("apply"))
        self.apply_help_btn.setFixedHeight(34)
        self.apply_help_btn.setFixedWidth(34)
        self.apply_help_btn.setIconSize(QtCore.QSize(32,32))
        self.apply_help_btn.clicked.connect(self.apply_help)
        self.apply_help_btn.setToolTip("Set help card to selected digital asset")
        self.toolbar.addWidget(self.apply_help_btn)

        self.clear_btn = QtWidgets.QToolButton()
        self.clear_btn.setIcon(get_icon("clean"))
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.setFixedWidth(34)
        self.clear_btn.setIconSize(QtCore.QSize(32,32))
        self.clear_btn.clicked.connect(self.clean_widgets)
        self.clear_btn.setToolTip("Clear Elements")
        self.toolbar.addWidget(self.clear_btn)

        self.toolbar.addSeparator()

        self.title_main_btn = ToolIcon("header", "maintitle")
        self.title_main_btn.setToolTip("Add main title + icon from selected node")
        self.toolbar.addWidget(self.title_main_btn)

        self.title2_btn = ToolIcon("title1", "title:2")
        self.title2_btn.setToolTip("Add title")
        self.toolbar.addWidget(self.title2_btn)

        self.title3_btn = ToolIcon("title2", "title:3")
        self.title3_btn.setToolTip("Add navigation menu entry")
        self.toolbar.addWidget(self.title3_btn)

        self.text_block_btn = ToolIcon("text_block", "text:block")
        self.text_block_btn.setToolTip("Add simple block of text")
        self.toolbar.addWidget(self.text_block_btn)

        self.parms_grid_btn = ToolIcon("view_gridline", "params")
        self.parms_grid_btn.setToolTip("Add parameters help grid")
        self.toolbar.addWidget(self.parms_grid_btn)

        self.tips_btn = ToolIcon("tips", "tips")
        self.tips_btn.setToolTip("Add tips line")
        self.toolbar.addWidget(self.tips_btn)

        self.info_btn = ToolIcon("info", "note")
        self.info_btn.setToolTip("Add info line")
        self.toolbar.addWidget(self.info_btn)

        self.warning_btn = ToolIcon("warning", "warning")
        self.warning_btn.setToolTip("Add warning line")
        self.toolbar.addWidget(self.warning_btn)

        self.box_btn = ToolIcon("box", "textbox")
        self.box_btn.setToolTip("Add box text")
        self.toolbar.addWidget(self.box_btn)

        self.dotted_list_btn = ToolIcon("bullet", "bullets")
        self.dotted_list_btn.setToolTip("Add bullet text")
        self.toolbar.addWidget(self.dotted_list_btn)

        self.image_btn = ToolIcon("image", "image")
        self.image_btn.setToolTip("Add image from disk")
        self.toolbar.addWidget(self.image_btn)

        self.separator_btn = ToolIcon("sep", "separator")
        self.separator_btn.setToolTip("Add horizontal separator line")
        self.toolbar.addWidget(self.separator_btn)

        self.vimeo_btn = ToolIcon("vimeo", "vimeo")
        self.vimeo_btn.setToolTip("Add vimeo embedded video.")
        self.toolbar.addWidget(self.vimeo_btn)

        self.toolbar.addSeparator()

        self.help_btn = QtWidgets.QToolButton()
        self.help_btn.setIcon(get_icon("help"))
        self.help_btn.setFixedHeight(34)
        self.help_btn.setFixedWidth(34)
        self.help_btn.setIconSize(QtCore.QSize(32,32))
        self.help_btn.clicked.connect(self.show_help)
        self.help_btn.setToolTip("Show Help")
        self.toolbar.addWidget(self.help_btn)
        
        self.addToolBar(self.toolbar)

        # scroll area
        self.ui_widgets = []
        self.scroll_w = ScrollWidget(parent=self)
        self.scroll_w.setAutoFillBackground(True)
        self.scroll_lay = QtWidgets.QVBoxLayout()
        self.scroll_lay.setContentsMargins(5,5,5,5)
        self.scroll_lay.setSpacing(5)
        self.scroll_lay.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_w.setLayout(self.scroll_lay)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setObjectName("scroll")
        self.scroll_area.setStyleSheet("""QScrollArea{background-color: white;}""")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_w)

        # on this page menu
        self.on_this_page = None
        self.n_titles = 0

        self.main_layout.addWidget(self.scroll_area)

        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        
        cw.setLayout(self.main_layout)
        self.setCentralWidget(cw)

    def hide_on_this_page(self):

        if self.on_this_page:
            self.on_this_page.setVisible(False)

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

        elif w_type == "bullets":
            w = Bullets(parent=self)

        elif w_type == "textbox":
            w = TextBox(parent=self)

        elif w_type == "image":

            img = QtWidgets.QFileDialog.getOpenFileName(filter="Png (*.png)")
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

        elif w_type == "vimeo":

            w = Vimeo(parent=self)

        elif w_type.startswith("title:"):

            size = int(w_type.split(':')[-1])
            title_type = TitleType.ENTRY_MENU
            if size == 2:
                title_type = TitleType.TITLE

            w = Title(title_type=title_type, parent=self)

            # TODO: update on this page menu if any
            """if self.on_this_page:
                self.on_this_page.append_entry(idx, "Title", w)
                if not self.on_this_page.isVisible():
                    self.on_this_page.setVisible(True)
            else:
                self.on_this_page = OnThisPage(parent=self)
                self.on_this_page.append_entry(1, "Title", w)
                self.scroll_lay.insertWidget(1, self.on_this_page)"""

            self.n_titles += 1

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
        
        self.refresh_ids()

    def refresh_ids(self):

        for i, w in enumerate(self.ui_widgets):
            w.idx = i

    def add_image_from_clip(self, img_path):
        
        w = ImageFromDisk(img=img_path, parent=self)

        idx = len(self.ui_widgets) + 1
        self.scroll_lay.insertWidget(idx, w)
        self.ui_widgets.insert(idx, w)
        self.refresh_ids()

    def get_help_str(self):
        """ Fetch all the output help string from widgets
        """
        return "//HELP CARD MAKER " + VERSION + '\n' + \
               '\n'.join([w.output() for w in self.ui_widgets]) + \
               "\n//END"

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

        elif cluster == "BULLETS":
            
            numbered = False
            cleaned_data = []
            for _d in data:
                if _d.startswith("* "):
                    cleaned_data.append(_d[2:])
                elif _d.startswith("# "):
                    cleaned_data.append(_d[2:])
                    numbered = True
                else:
                    cleaned_data.append(_d)

            text = "".join(cleaned_data)
            w = Bullets(texts=cleaned_data, numbered=numbered, parent=self)

        elif cluster == "TEXTBOX":
            title = data[0].split(':box:')[-1]
            if title == ":box:": title = ""
            color_str = data[1].split(' ')[-1]
            text = "".join([n[4:] for n in data[2:]])
            w = TextBox(text=text, color_str=color_str, title=title,
                        parent=self)

        elif cluster == "VIMEO":
            video_title = data[0].replace(":vimeo: ", '')
            video_id = data[1].split(':')[-1]
            w = Vimeo(title=video_title, video_id=video_id, parent=self)

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
        message += "More infos:\ncontact@cgtoolbox.com\nwww.cgtoolbox.com"

        w = QtWidgets.QMessageBox()
        w.setStyleSheet(hou.ui.qtStyleSheet())
        w.setWindowIcon(get_icon("help"))
        w.setWindowTitle("Help")
        w.setText(message)
        w.exec_()