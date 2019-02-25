import hou
from PySide2 import QtGui

def get_icon(name):
    
    try:
        return hou.ui.createQtIcon("HelpcardMaker/" + name + ".png")
    except:
        try:
            return hou.ui.createQtIcon("HelpcardMaker/" + name + ".svg")
        except:
            print("Error: icon {} not found.".format(name))
            return QtGui.QIcon("")

class Colors(object):

    GRAY = QtGui.QColor(240,240,240)
    BLUE = QtGui.QColor(0,135,255)
    PINK = QtGui.QColor(252,232,239)
    RED = QtGui.QColor(255,50,0)
    RED_LIGHT = QtGui.QColor(255,240,245)
    GREEN = QtGui.QColor(105,205,32)
    GREEN_LIGHT = QtGui.QColor(245,255,245)
    YELLOW = QtGui.QColor(255,205,0)
    PURPLE = QtGui.QColor(241,232,252)
    PURPLE_LIGHT = QtGui.QColor(255,242,255)
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
    GRAY = QtGui.QColor(240,240,240)
    PINK = QtGui.QColor(251,232,239)
    YELLOW = QtGui.QColor(254,247,215)
    PURPLE = QtGui.QColor(241,232,251)
    MAGENTA = QtGui.QColor(251,206,238)
    TEAL = QtGui.QColor(211,242,249)
    SEAFOAM = QtGui.QColor(211,250,232)
    WHITE = QtGui.QColor(255,255,255)
    
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