from AlignmentReporter import *
import time
from numba import jit
def old():
    t_start = time.time()
    players = converter.loader(EXCEL_FILE)
    vizualisation.plot_background(BACKGROUND_QUALITY, BACKGROUND_KWARGS)
    players_pos = np.array(list(zip(np.linspace(-1.10, -1.10, len(players)), np.linspace(1.0, (1.0-0.1*len(players)),
                                                                                               len(players)))))
    for player, color, pos in zip(players, COLORS, players_pos):
        df = vizualisation.square_root(players[player].fillna(players[player].mean()))
        mean_df = df.fillna(value=df.mean()).rolling(BACKLOG_SCALE, min_periods=1).mean().iloc[max(0, 100 - BACKLOG):, :]
        mean_df["alpha"] = np.logspace(-0.5, 0, mean_df.shape[0])
        plt.annotate(player, xy=pos, color=color, ha='left', va='center')
        
        plt.plot(mean_df['x'], mean_df['y'], color=color, **PLOT_KWARGS)
        s = np.logspace(-1, 1.5, mean_df.shape[0])
        kwargs = SCATTER_KWARGS.copy()
        for i in range(mean_df.shape[0]):
            if i == mean_df.shape[0] - 1:
                kwargs['marker'] = '*'
            row = pd.DataFrame(mean_df.iloc[i, :]).transpose()
            for a, scale in zip(np.linspace(row['alpha'].values[-1], 0.0, 10) ** 8,
                                np.linspace(s[i], s[i] * 1.1, 10) ** 1.02):
                kwargs['alpha'] = a
                kwargs['s'] = scale
                if i == mean_df.shape[0] - 1:
                    kwargs['marker'] = '*'
                    kwargs['s'] = scale * 10
                # kwargs['s'] = s[i]
                plt.scatter(data=row, x='x', y='y', color=color, **kwargs)
    
    plt.title("Party Alignment Chart", loc="center")
    vizualisation.plot_foreground(tight=False)
    vizualisation.finalize()
    t_tot = time.time() - t_start
    
    
    
    
    print(compute_time(t_tot))
    plt.show()

@jit
def compute_time(t):
    force = False
    p = "Process took: "
    if t >= 60 ** 2:
        force = True
        h = int(t / 60 ** 2)
        if h > 1:
            p += "{:2} hours, ".format(h)
        else:
            p += "{:2} hour, ".format(h)
        
        t %= 60 ** 2
    
    if t >= 60 or force:
        force = True
        m = int(t / 60)
        if m > 1:
            p += "{:2} minutes, ".format(m)
        else:
            p += "{:2} minute, ".format(m)
        
        t %= 60
    
    
    if t > 1:
        p += "{} seconds".format(round(t,2))
    else:
        p += "{} second".format(round(t,2))
    
    return p
# Endfile
