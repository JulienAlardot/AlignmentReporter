BACKLOG = 100
BACKLOG_SCALE = 50
COLORS = ('gray', 'cyan', 'magenta', 'green', 'red', 'blue')

BACKGROUND_QUALITY = int(360 * (10 ** 0.1))
BACKGROUND_KWARGS = {
    "color": 'black',
    'linewidth': 3
}

METADATA = {
    'Title': 'Characters Current Alignement Chart Evolution',
    'Author': 'Julien Alardot',
    'Description': 'Characters Current Alignement Chart Evolution',
    'Copyright': 'See LICENSE file'
}

PLOT_KWARGS = {
    'linewidth': 2,
    "alpha": 0.3,
    'ms': 20,
    'aa': True,
    'drawstyle': 'steps-pre',
    # 'solid_capstyle': 'projecting',
    'solid_capstyle': 'round',
    'solid_joinstyle': 'round',
    'linestyle': '--'
}

SCATTER_KWARGS = {
    "marker": 'o'
}
