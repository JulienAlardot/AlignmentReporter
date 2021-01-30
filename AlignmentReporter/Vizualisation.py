try:
    from AlignmentReporter import *
except ModuleNotFoundError:
    pass
from matplotlib import pyplot as plt
from matplotlib import transforms as trans
import random as rand
import math
import pandas as pd
import numpy as np
import traceback as tr
try:
    from scipy.interpolate import make_interp_spline
except Exception:
    pass
import time


def gen_rand_array(n_row=100, n_column=2, min=-1.0, max=1.0, s=0.1):
    array = list()
    for row in range(n_row):
        array.append(rand.choices(np.arange(min, max + s, s), k=n_column))
    return pd.DataFrame(np.array(array), columns=["x", "y"])


def square_root(df):
    for i, row in enumerate(df.values):
        x, y = row
        ratio1 = max(1e-15, math.sqrt(x ** 2 + y ** 2))
        n_x, n_y = (abs(x / ratio1), abs(y / ratio1))
        if math.tan(math.acos(n_x)) / max(1e-15, (1 / (max(1e-15, math.tan(math.acos(n_x)))))) <= 1.0:
            ratio2 = math.sqrt(math.tan(math.acos(n_x)) ** 2 + 1)
        else:
            ratio2 = math.sqrt((1 / max(1e-15, math.tan(math.acos(n_x)))) ** 2 + 1)
        df.loc[i] = (x / ratio2, y / ratio2)
    return df


def rotatematrix(array, kwargs, angle=180):
    angle = np.radians(angle)
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    new_array = list()
    for i, row in enumerate(array.reset_index().values):
        row = np.array(row)
        rotated_matrix = rotation_matrix * row
        for j, r in enumerate(rotated_matrix):
            row[j] = rotated_matrix[j].sum()
        new_array.append(row)
    array = pd.DataFrame(np.array(new_array), columns=["x", "y"]).sort_values(["x", "y"])
    try:
        xnew = np.linspace(array["x"].min(), array["x"].max(), 200)
        spl = make_interp_spline(tuple(array["x"]), array["y"], k=2)
        power_smooth = spl(xnew)
        plt.plot(xnew, power_smooth, **kwargs)
    except Exception:
        plt.plot(array["x"], array["y"], **kwargs)


def plot_background(n=100, kwargs=dict()):
    n = int(n)
    try:
        plt.figure(figsize=(5,5), constrained_layout=True)
        x = np.linspace(-1.0, 1.0, n)
        x_small = np.linspace(-1.0, 1.0, round(math.sqrt(n) * 2))
        
        ax1 = np.linspace(1 / 3, 1.0, round(math.sqrt(n)))
        ax2 = np.zeros(round(math.sqrt(n))) + 1 / 3
        bars = ((ax1, ax2), (ax2, ax1))
        
        for bar in bars:
            df_no_mid = square_root(pd.DataFrame(np.array(bar).transpose(), columns=["x", "y"])).set_index("x")
            for angle in np.linspace(0, 270, 4):
                rotatematrix(df_no_mid, kwargs, angle)
        
        y = np.array([math.sqrt(1 - v ** 2) for v in x])
        bkwards = kwargs.copy()
        bkwards["linewidth"] *= 2
        plt.plot(x, y, zorder=1, **bkwards)
        plt.plot(x, -y, zorder=1, **bkwards)
        
        inner_circle = pd.DataFrame(
                np.array([x_small / 3, np.array([math.sqrt((1 / 9) - v ** 2) for v in x_small / 3])]).transpose(),
                columns=['x', 'y'])
        plt.plot(inner_circle['x'], inner_circle['y'], zorder=1, **kwargs)
        plt.plot(inner_circle['x'], -inner_circle['y'], zorder=1, **kwargs)
        
        # corners = np.array([[-1.0, -0.67, -0.33, 0.0, 0.33, 0.67, 1.0] * 7,
        #                     [1.0] * 7 + [0.67] * 7 + [0.33] * 7 + [0.0] * 7 + [-0.33] * 7
        #                     + [-0.67] * 7 + [-1.0] * 7]).transpose()
        #
        # data = square_root(pd.DataFrame(corners, columns=["x", "y"]))
        # plt.scatter(data["x"], data["y"], color='red')
    
    except Exception:
        tr.print_exc()


def plot_foreground(tight=False, kwargs=dict()):
    try:
        df = pd.DataFrame(np.array([[-2 / 3, 2 / 3], [0.0, 2 / 3], [2 / 3, 2 / 3], [-2 / 3, 0], [0.0, 0],
                                    [2 / 3, 0], [-2 / 3, -2 / 3], [0.0, -2 / 3], [2 / 3, -2 / 3]]))
        df = square_root(df)
        # plt.annotate("Lawful\nGood", df.loc[0], ha="center", va='center', fontsize=kwargs['fontsize'],
        #              fontweight='bold')
        # plt.annotate("Neutral\nGood", df.loc[1], ha="center", va='center', fontsize=kwargs['fontsize'],
        #              fontweight='bold')
        # plt.annotate("Chaotic\nGood", df.loc[2], ha="center", va='center', fontsize=kwargs['fontsize'],
        #              fontweight='bold')
        #
        # plt.annotate("Lawful\nNeutral", df.loc[3], ha="left", va='center', fontsize=kwargs['fontsize'],
        #              fontweight='bold')
        # plt.annotate("True\nNeutral", df.loc[4], ha="center", va='center', fontsize=kwargs['fontsize'],
        #              fontweight='bold')
        # plt.annotate("Chaotic\nNeutral", df.loc[5], ha="center", va='center', fontsize=kwargs['fontsize'],
        #              fontweight='bold')
        #
        # plt.annotate("Lawful\nEvil", df.loc[6], ha="center", va='center', fontsize=kwargs['fontsize'],
        #              fontweight='bold')
        # plt.annotate("Neutral\nEvil", df.loc[7], ha="center", va='center', fontsize=kwargs['fontsize'],
        #              fontweight='bold')
        # plt.annotate("Chaotic\nEvil", df.loc[8], ha="center", va='center', fontsize=kwargs['fontsize'],
        #              fontweight='bold')
        
        plt.annotate("LG", df.loc[0], ha="center", va='center', fontsize=kwargs['fontsize'],
                     fontweight='bold')
        plt.annotate("NG", df.loc[1], ha="center", va='center', fontsize=kwargs['fontsize'],
                     fontweight='bold')
        plt.annotate("CG", df.loc[2], ha="center", va='center', fontsize=kwargs['fontsize'],
                     fontweight='bold')

        plt.annotate("LN", df.loc[3], ha="left", va='center', fontsize=kwargs['fontsize'],
                     fontweight='bold')
        plt.annotate("TN", df.loc[4], ha="center", va='center', fontsize=kwargs['fontsize'],
                     fontweight='bold')
        plt.annotate("CN", df.loc[5], ha="center", va='center', fontsize=kwargs['fontsize'],
                     fontweight='bold')

        plt.annotate("LE", df.loc[6], ha="center", va='center', fontsize=kwargs['fontsize'],
                     fontweight='bold')
        plt.annotate("NE", df.loc[7], ha="center", va='center', fontsize=kwargs['fontsize'],
                     fontweight='bold')
        plt.annotate("CE", df.loc[8], ha="center", va='center', fontsize=kwargs['fontsize'],
                     fontweight='bold')
        plt.axis('square')
        plt.axis("off")
        plt.xlim(-1.5, 1.5)
        plt.ylim(-1.5, 1.5)
        title = kwargs["title"] if kwargs['title'] else False
        
        if title:
            text = kwargs['title']
            alignment = kwargs['alignment'] if kwargs['alignment'] else 'center'
            plt.title(text, y=0.9, loc=alignment, fontsize=kwargs['fontsize']*1.1, fontweight='bold')
        
        if tight:
            plt.tight_layout()
    except Exception:
        tr.print_exc()


def finalize():
    metadata = {
        'Title'        : 'Characters Current Alignement Chart Evolution',
        'Author'       : 'Julien Alardot',
        'Description'  : 'Characters Current Alignement Chart Evolution',
        'Copyright'    : 'All Right Reserved by Julien Alardot',
        'Creation Time': time.ctime()
    }
    plt.savefig(fname=r'out\AlignementChartTransparent_high.png', dpi=600, format='png', transparent=True,
                metadata=metadata)
    plt.savefig(fname=r'out\AlignementChart_high.png', dpi=600, format='png', transparent=False, metadata=metadata)
    
    plt.savefig(fname=r'out\AlignementChartTransparent_med.png', dpi=300, format='png', transparent=True,
                metadata=metadata)
    plt.savefig(fname=r'out\AlignementChart_med.png', dpi=300, format='png', transparent=False, metadata=metadata)
    
    plt.savefig(fname=r'out\AlignementChartTransparent_low.png', dpi=72, format='png', transparent=True,
                metadata=metadata)
    plt.savefig(fname=r'out\AlignementChart_low.png', dpi=72, format='png', transparent=False, metadata=metadata)


kwargs = {
    'n_row'   : 10000,
    'n_column': 2,
    'min'     : -1.0,
    'max'     : 1.0,
    's'       : 0.05
}
# plt.subplot(1, 2, 1)
# data = gen_rand_array(**kwargs)
# plt.scatter(data=data, x="x", y="y")
# plt.xlim(-1.1, 1.1)
# plt.ylim(-1.1, 1.1)
# plt.plot()
#
# plt.subplot(1, 2, 2)
# data = square_root(data)
#
# plt.scatter(data=data, x="x", y="y")
# plt.xlim(-1.1, 1.1)
# plt.ylim(-1.1, 1.1)
# plt.plot()
#
# plt.tight_layout()
# plt.show()

# Endfile
