import math
import os
import time
import traceback as tr
from typing import Tuple, Dict, Callable, Union, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PySide2.QtCore import Signal, QObject
from PySide2.QtWidgets import QLabel

import AlignmentReporter.Vizualisation as vis
from AlignmentReporter.UI.py.default_parameters import (
    BACKGROUND_KWARGS,
    PLOT_KWARGS,
    METADATA,
)
from AlignmentReporter.UI.py.funcutils import alignment_to_position, compute_time
from AlignmentReporter.UI.py.typed_dict import DataDict, PlayerDict


class MyQLabel(QLabel):
    resized: Signal = Signal()

    def __init__(self):
        """
        Simple subclass of QLabel that emits a Signal when resized
        """
        super(MyQLabel, self).__init__()

    def resizeEvent(self, event):
        """
        Override of the QWidget resizeEvent to add a custom QSignal.emit()
        """
        self.resized.emit()
        super(MyQLabel, self).resizeEvent(event)


class Worker(QObject):
    signal = Signal()
    finished = Signal()

    def __init__(self, data, *args, **kwargs):
        """
        Subclass of QObject that generate an output image with given parameter data

        :param data: array containing the plotting data, output path, temp output path and the fontsize
        :param args: any positional argument given to QObject
        :param kwargs: any keyword argument given to QObject
        :type data: tuple[DataDict, str, str, int]
        """
        super(Worker, self).__init__(*args, **kwargs)
        self.data = data

    @property
    def data(self):
        """
        Method packing the attributes into a data tuple. (Unused)

        :return: tuple containing the plotting data, output path, temp output path and the fontsize
        :rtype: tuple[DataDict, str, str, int]
        """
        return self.__data, self.__final_file, self.__temp_file, self.__fontsize

    @data.setter
    def data(self, data_list):
        """
        Method unpacking the given data into the correct attributes

        :param data_list: array containing the plotting data, output path, temp output path and the fontsize
        :type data_list: tuple[DataDict, str, str, int]
        """
        self.__data, self.__final_file, self.__temp_file, self.__fontsize = data_list

    def generate_image(self):
        try:
            data: DataDict = self.__data
            final_file: str = self.__final_file
            temp_file: str = self.__temp_file
            fontsize: int = self.__fontsize

            al: Tuple[
                Tuple[str, str, str], Tuple[str, str, str], Tuple[str, str, str]
            ] = (("LG", "NG", "CG"), ("LN", "TN", "CN"), ("LE", "NE", "CE"))

            plt.close()

            t_start = time.time()
            players = data["players"]
            line_qual = int(
                360 * (10 ** np.linspace(-0.5, 3.8, 100)[data["hs_line_quality"]])
            )
            vis.plot_background(n=line_qual, kwargs=BACKGROUND_KWARGS)

            for i in range(line_qual):  # Fixme: Maybe not do that
                self.signal.emit()

            t = data["le_image_title"] if data["chb_image_title"] else False

            alignment = (
                "left"
                if data["title_alignment"] == 0
                else "right"
                if data["title_alignment"] == 2
                else "center"
            )

            pos_y = float(data["hs_legend_v_offset"] / 100.0) * 1.5
            pos_x = data["hs_legend_h_offset"] * 0.015
            stretch = float(data["hs_legend_stretch"] / 40.0)

            players_values: List[PlayerDict] = list(players.values())

            if data["gb_add_auto_party"]:
                party_pos_list: Union[Tuple[float, float], List[float, float]] = list()

                if data["cob_party_starting_alignment"] != "Average":
                    first_pos: np.array = np.array(
                        *alignment_to_position(
                            [data["cob_party_starting_alignment"]],
                            1,
                        )
                    )

                else:
                    first_pos_list: List[np.ndarray] = list()

                    for v in players.values():
                        first_pos_list += alignment_to_position([v["Entries"][0]])

                    first_pos: np.ndarray = np.array(first_pos_list).mean(axis=0)
                first_pos_list = list()
                for i in range(data["sb_first_entry_weight"]):
                    first_pos_list.append(first_pos)

                party_func: Callable = np.mean if data["rb_average"] else np.sum
                party_name: str = data["le_party_name"]
                party_color: str = data["le_party_color"]

                party_all_entries: Union[
                    np.ndarray, List[Tuple[Tuple[float, float]]]
                ] = list()
                len_entries: Union[List[int], Tuple[int]] = list()

                for player in players.values():
                    party_all_entries.append(
                        alignment_to_position(player["Entries"][1:])
                    )
                    len_entries.append(len(party_all_entries[-1]))

                party_array_values: np.ndarray = np.zeros(
                    (max(len_entries), len(players.values()), 2)
                )
                party_array_values[:, :, :] = 0.0

                for i, array in enumerate(party_all_entries):
                    party_array_values[: len_entries[i], i, :] = np.array(array)
                party_align_values = np.concatenate(
                    (first_pos_list, party_func(party_array_values, axis=1)), axis=0
                )

                party_player: Dict[str, Union[np.ndarray, str]] = {
                    "Color": party_color,
                    "Entries": party_align_values,
                    "Name": party_name,
                }
                players_values.append(party_player)

            players_pos: np.ndarray = np.array(
                list(
                    zip(
                        np.linspace(pos_x, pos_x, len(players_values)),
                        np.linspace(
                            pos_y,
                            (pos_y - (stretch * len(players_values))),
                            len(players_values),
                        ),
                    )
                )
            )

            for player, pos in zip(players_values, players_pos):
                if len(player["Entries"]) > 0:
                    color: str = player["Color"]
                    if player is not players_values[-1]:
                        a: np.ndarray = np.array(player["Entries"])
                        values: Tuple[Tuple[float, float]] = alignment_to_position(
                            entries=a, first_entry_weight=data["sb_first_entry_weight"]
                        )
                    else:
                        values: Tuple[Tuple[float, float]] = player["Entries"]

                    df_player = pd.DataFrame(
                        np.array(values), columns=["x", "y"]
                    ).fillna(np.array(values).mean())

                    mean_df_normal = (
                        df_player.fillna(value=df_player.mean())
                        .rolling(data["sb_rolling_window_size"], min_periods=1)
                        .mean()
                        .iloc[
                            max(
                                0,
                                data["sb_rolling_window_size"]
                                - data["sb_first_entry_weight"],
                            ) :,
                            :,
                        ]
                    )

                    mean_df = vis.map_to_circle(mean_df_normal)
                    mean_df["alpha"] = np.logspace(-0.5, 0, mean_df.shape[0])

                    ha = (
                        "left"
                        if data["legend_text_alignment"] == 0
                        else "center"
                        if data["legend_text_alignment"] == 1
                        else "right"
                    )

                    s = np.logspace(-1.2, 1.5, mean_df.shape[0]) * math.sqrt(
                        (data["hs_scale"]) / 100.0
                    )
                    plt.plot(mean_df["x"], mean_df["y"], color=color, **PLOT_KWARGS)
                    self.signal.emit()

                    prev_markers: Tuple = (
                        "o",
                        "x",
                        "*",
                        "+",
                        "<",
                        "^",
                        ">",
                        "v",
                        "",
                        "$" + data["le_previous_custom"] + "$",
                    )

                    last_markers: Tuple = (
                        "o",
                        "x",
                        "*",
                        "+",
                        "<",
                        "^",
                        ">",
                        "v",
                        "",
                        "$" + data["le_current_custom"] + "$",
                    )

                    kwargs: Dict[str, str] = {
                        "marker": prev_markers[data["previous_marker"]]
                    }

                    for i in range(mean_df.shape[0]):
                        if i == mean_df.shape[0] - 1:
                            kwargs["marker"]: str = last_markers[data["current_marker"]]

                        row: pd.DataFrame = pd.DataFrame(mean_df.iloc[i, :]).transpose()

                        for alpha, scale in zip(
                            np.linspace(row["alpha"].values[-1], 0.0, 10) ** 8,
                            np.linspace(s[i], s[i] * 1.1, 4),
                        ):

                            kwargs["alpha"]: float = alpha
                            kwargs["s"]: float = scale

                            if i == mean_df.shape[0] - 1:
                                kwargs["marker"]: str = last_markers[
                                    data["current_marker"]
                                ]
                                kwargs["s"]: float = (
                                    scale * data["hs_current_scale"] / 10.0
                                )

                            plt.scatter(data=row, x="x", y="y", color=color, **kwargs)

                        self.signal.emit()

                    first_row: pd.DataFrame = pd.DataFrame(
                        mean_df_normal.iloc[0, :]
                    ).transpose()
                    last_row: pd.DataFrame = pd.DataFrame(
                        mean_df_normal.iloc[mean_df_normal.shape[0] - 1, :]
                    ).transpose()

                    y: int = int(round(1 - first_row["y"]))
                    x: int = int(round(first_row["x"] + 1))
                    y_o: int = int(round(1 - last_row["y"]))
                    x_o: int = int(round(last_row["x"] + 1))
                    p_o_al: Tuple[float, float] = al[y][x]
                    p_al: Tuple[float, float] = al[y_o][x_o]

                    plt.annotate(
                        player["Name"] + ":\n{} -> {}".format(p_o_al, p_al),
                        xy=pos,
                        color=color,
                        ha=ha,
                        va="center",
                        fontsize=fontsize,
                        fontweight="semibold",
                    )

            vis.plot_foreground(
                tight=False,
                kwargs={"title": t, "alignment": alignment, "fontsize": fontsize * 1.1},
            )
            self.signal.emit()
            print(compute_time(time.time() - t_start))
            title: str = (
                data["le_image_title"].replace(" ", "_").lower()
                if data["chb_image_title"]
                else "party_players_alignment"
            )
            new_title: str = ""
            for c in title:
                if "-123456789_abcdefghijklmnopqrstuvwxyz".find(c) != -1:
                    new_title += c
                else:
                    new_title += "_"
            title: str = new_title
            ext: str = ".png" if data["image_format"] < 2 else ".jpg"
            f_path = os.path.join(final_file, title + ext)
            print("Starting saving data")
            im_size: int = min(data["sb_image_dpi"], 720)
            self.savefig(
                temp_file, im_size, f_format="png", quality=6, transparency=True
            )
            self.signal.emit()
            self.savefig(f_path)

        except Exception:
            tr.print_exc()

    def savefig(self, out, size=None, f_format=None, transparency=None, quality=None):
        """
        Method that outputs the final version of the image into the output folder

        :param out: fullpath of the output file
        :param size: (optional) size value converted into dpi for the matplotlib.pyplot.savefig method
        :param f_format: (optional) ['png' or 'jpeg'] override output file format, default is based on user choice data
        :param transparency: (optional) override output transparency if file format is 'png', default is based on
            user choice data
        :param quality: (optional) [1 <-> 12] override jpeg file quality if file format is 'jpeg', default is based on user
            choice data
        :type out: str
        :type size: int
        :type f_format: str
        :type transparency: bool
        :type quality: int
        """
        metadata: Dict[str, str] = METADATA
        metadata["Creation Time"]: str = time.ctime()
        dpi: float = (
            size / (72 / 100 * 5.0)
            if size
            else self.__data["sb_image_dpi"] / (72 / 100 * 5.0)
        )
        f_format = (
            f_format
            if f_format
            else "png"
            if self.__data["image_format"] < 2
            else "jpeg"
        )
        transparency = (
            transparency
            if transparency
            else True
            if self.__data["image_format"] == 1
            else False
        )
        quality = (
            round(np.linspace(0, 95, 12)[quality - 1])
            if quality
            else round(np.linspace(0, 95, 12)[self.__data["hs_jpeg_qual"] - 1])
        )
        plt.savefig(
            fname=out,
            dpi=dpi,
            format=f_format,
            transparent=transparency,
            pil_kwargs={"quality": int(round(quality)), "metadata": metadata},
        )
        try:
            self.finished.emit()
        except RuntimeError:
            pass  # Worker already deleted
