import numpy as np
import pandas as pd


def loader(in_file):
    alignement = ["LG", "LB", "NG", "NB", "CG", "CB", "LN", "TN", "CN", "LE", "LM", "NE", "NM", "CE", "CM", "L", "N",
                  "T", "C", "G", "B", "E", "M"]
    df = pd.read_excel(in_file, sheet_name="Feuil1", index_col=None, header=0, na_values=np.nan)
    players = dict()
    for column in df[:]:
        player_df = pd.DataFrame(df[column])
        values = list()
        for value in player_df[column]:
            x = np.nan
            y = np.nan
            try:
                value = value.upper()
            except AttributeError:
                pass
            if value not in alignement or len(value) > 2 or not value or value == np.nan:
                x = np.nan
                y = np.nan
            
            elif value in alignement:
                if len(value) == 2:
                    value = [c for c in value]
                    value = ['T' if v == "N" and i == 0 else v for i,v in enumerate(value)]
    
                if len(value) == 1:
                    value = [value]
                x = []
                y = []
                for v in value:
                    if v == "L":
                        x.append(-1)
                    elif v == "T":
                        x.append(0)
                    elif v == "C":
                        x.append(1)
                    elif v in ('G', 'B'):
                        y.append(1)
                    elif v == "N":
                        y.append(0)
                    elif v in ("E", 'M'):
                        y.append(-1)
                if len(x) > len(y):
                    y += [np.nan]*(len(x)-len(y))
                elif len(y) > len(x):
                    x += [np.nan]*(len(y)-len(x))
                values += list(zip(x,y))
            df_players = pd.DataFrame(np.array(values), columns=['x', 'y'])
            players[column] = pd.DataFrame(df_players.dropna(axis=0, how='all').reindex())
    return players
# Endfile
