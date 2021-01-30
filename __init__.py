import time
import os
from UI import py as UIPY
from PySide2.QtCore import *
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *
import traceback as tr

PATH=__file__.split("__init__")[0]
BACKLOG = 100
BACKLOG_SCALE = 50
COLORS = ('gray', 'cyan', 'magenta', 'green', 'red', 'blue')

BACKGROUND_QUALITY = int(360 * (10 ** 0.1))
BACKGROUND_KWARGS = {
    "color"    : 'black',
    'linewidth': 3
}

METADATA = {
    'Title'        : 'Characters Current Alignement Chart Evolution',
    'Author'       : 'Julien Alardot',
    'Description'  : 'Characters Current Alignement Chart Evolution',
    'Copyright'    : 'All Right Reserved by Julien Alardot',
    'Creation Time': time.ctime()
}

PLOT_KWARGS = {
    'linewidth'      : 2,
    "alpha"          : 0.3,
    'ms'             : 20,
    'aa'             : True,
    'drawstyle'      : 'steps-pre',
    'solid_capstyle' : 'projecting',
    'solid_joinstyle': 'round',
    'linestyle'      : '--'

}
SCATTER_KWARGS = {
    "marker": 'o'

}
EXCEL_FILE = os.path.join(PATH, "AlignementData.xlsx")

if __name__ == '__main__':
    try:
        import sys
        import os
        
        app = QApplication(sys.argv)
        app.setApplicationName("partyAlignmentChartTool")
        app.setApplicationDisplayName("Party Alignment Chart Tool")
        app.setApplicationVersion("0.1.0")
        app.setOrganizationName("Julien Alardot")
        win = UIPY.mainWindow(input("Savefile Name: "))
        win.resize(0, 0)
        win.setFocus()
        app.setWindowIcon(QIcon(os.path.join(PATH, "UI", "AlignmentTool.icon")))
        app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))
        app.exec_()
    except Exception:
        tr.print_exc()