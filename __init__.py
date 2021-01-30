import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import sys
import os
try:
    from AlignmentReporter.UI.py import run
    from AlignmentReporter import converter as converter
    from AlignmentReporter import Vizualisation as vizualisation
    PATH=__file__.split("__init__")[0]
except ModuleNotFoundError:
    from UI.py import run
    import converter
    import Vizualisation as vizualisation
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

if __name__ == "__main__":
    app=object()
    win=object()
    run(app, win)