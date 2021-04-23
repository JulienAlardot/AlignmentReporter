import json
import os
import pickle
import sys
import time
import traceback as tr
from typing import List, Dict

import matplotlib.pyplot as plt
import numpy as np
from PySide2.QtCore import QFile, Qt, Signal, SIGNAL, SLOT, QThread
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QSizePolicy, QMainWindow, QApplication, QLabel, QWidget, QLayout, QStyle, QLineEdit

import AlignmentReporter.UI.Qt.AlignmentReporterRessources as ar_r
import AlignmentReporter.Vizualisation as vis
from AlignmentReporter.UI.py.default_parameters import BACKGROUND_KWARGS, METADATA
from AlignmentReporter.UI.py.classutils import MyQLabel, Worker
from AlignmentReporter.UI.py.funcutils import timeit, compute_time, alignment_to_position
from AlignmentReporter.UI.py.typed_dict import DataDict, PlayerDict

ar_r.qInitResources  # avoid import optimization removing the previous  line

_path = __file__.split("UI")[0]

_icon_path = os.path.join(_path, "UI", "Qt")

with open(os.path.join(_path, "UI", "Qt", "style.css"), "r") as f:
    _style_sheet: str = f.read()


class SettingWindow(QMainWindow):
    def __init__(self, parent=None):
        """
        Subclass used for the child window with the graph customization parameters

        :param parent: (deprecated) Set the parent window instance for this subclass instance
        :type parent: QWidget or QMainWindow
        """
        # Window setup
        super(SettingWindow, self).__init__()
        loader: QUiLoader = QUiLoader()
        file: QFile = QFile(os.path.join(_path, "UI", "Qt", "imageSettings.ui"))
        file.open(QFile.ReadOnly)
        self.centralWidget: QMainWindow = loader.load(file, self)
        file.close()
        # self.setParent(parent)
        self.setWindowTitle("Image Settings")
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        # self.setMinimumSize(self.centralWidget.minimumSize())
        self.setStyleSheet(_style_sheet)
        self.assignWidgets()
        self.setWindowFlags(Qt.Window)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                              'AlignmentTool.ico')))
        # Plugin setup

        # Custom variables

        # Init Widgets

        # Custom functions calls
        self.close()

    ####################################################################################################################
    #                                               Default functions                                                  #
    ####################################################################################################################
    def assignWidgets(self):
        """
        Link Widgets to functions
        """
        pass

    ####################################################################################################################
    #                                               Custom UI functions                                                #
    ####################################################################################################################

    ####################################################################################################################
    #                                               Custom Effective functions                                         #
    ####################################################################################################################
    @staticmethod
    def print_click():
        """"
        PLACEHOLDER FUNCTION
        """
        print("Button clicked")


class MainWindow(QMainWindow):
    advanced: Signal = Signal()

    def __init__(self, savefile):
        """
        Subclass used for the child window with the graph customization parameters

        :param savefile: name string for the saving file e.g: "Celtaidd"
        :type savefile: str
        """
        # Window setup
        super(MainWindow, self).__init__()
        self.setStyleSheet(_style_sheet)
        loader: QUiLoader = QUiLoader()
        ui_file: QFile = QFile(os.path.join(_path, "UI", "Qt", "mainWindow.ui"))
        ui_file.open(QFile.ReadOnly)
        self.centralWidget = loader.load(ui_file, self)
        ui_file.close()

        self.setWindowIcon(
            QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'AlignmentTool.ico')))
        self.settingsUI: SettingWindow = SettingWindow(self)

        self.setWindowTitle("Party Setup")
        self.settingsUI.setWindowTitle("Image Settings")
        self.__save = savefile
        self.assignWidgets()
        self.setWindowFlags(Qt.Window)

        # Plugin setup

        # Custom variables
        self.datapath: str = os.path.join(_path, "data")
        self.savefile: str = os.path.join(self.datapath, self.__save + ".pkl")
        self.savefile_json: str = os.path.join(self.datapath, self.__save + ".json")
        self.data = dict()
        self.__TMP: str = os.path.join(self.datapath, "TMP.pkl")
        self.__Final: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "out")
        self.__player_data: dict = dict()
        self.__fontsize: int = 8
        self.finished: bool = True
        self.loop: QThread = QThread()
        self.workers: List[QThread] = list()

        # Init Widgets
        self.mutate_widget(self.centralWidget.l_image)
        self.centralWidget.f_progress_bar.hide()
        self.centralWidget.prb_preview.setValue(0)
        self.centralWidget.l_image.resized.connect(self.resize_image)
        self.centralWidget.cob_players_select.setFocus()

        group = (
            self.centralWidget.line,
            self.centralWidget.line_2,
            self.centralWidget.line_3,
            self.centralWidget.line_4,
            self.centralWidget.line_5,
            self.centralWidget.line_6,
            self.centralWidget.line_7,
        )
        for widget in group:
            widget.setProperty("holder", True)  # Stylesheet property for holding widgets
        # Custom functions calls
        self.show()

    ####################################################################################################################
    #                                               Default functions                                                  #
    ####################################################################################################################
    def assignWidgets(self):
        """
        Method used to connect QSignals to other Methods
        """
        self.centralWidget.tb_settings.released.connect(self.settingsUI.show)
        self.centralWidget.pb_save_quit.released.connect(self.close)
        self.centralWidget.pb_set_color.released.connect(self.set_player_color)
        self.centralWidget.pb_set_party_color.released.connect(self.set_party_color)
        self.centralWidget.pb_set_name.released.connect(self.set_player_name)
        self.centralWidget.pb_set_party_name.released.connect(self.set_party_name)
        self.centralWidget.pb_set_title.released.connect(self.set_title)
        self.centralWidget.pb_add_player_entry.released.connect(self.add_entry)
        self.centralWidget.pb_delete_player_entry.released.connect(self.del_entry)
        self.centralWidget.pb_delete_player_all_entries.released.connect(self.clear_entries)
        self.centralWidget.pb_save_player.released.connect(self.save_player)
        self.centralWidget.pb_del_player.released.connect(self.del_player)
        self.centralWidget.cob_players_select.currentIndexChanged.connect(self.update_player)
        self.centralWidget.pb_generate.released.connect(self.run_generate_image)
        self.centralWidget.pb_save.released.connect(self.save)
        # self.centralWidget.gb_add_auto_party.toggled.connect(self.clicked_party_player)
        self.advanced.connect(self.progress_update)

    def change_signals_block_state(self, state):
        """
        Method used to un/block QSignals on critical connections when an infinite loop is possible

        :param state: Set the parent window instance for this subclass instance
        :type state: bool
        """
        self.centralWidget.cob_players_select.blockSignals(state)

    ####################################################################################################################
    #                                               Custom functions                                                   #
    ####################################################################################################################
    @staticmethod
    def print_click():
        """"
        PLACEHOLDER FUNCTION
        """
        print("Button clicked")

    def mutate_widget(self, old):
        """
        Method used to "change" the class for the image label. The new instance emits a custom QSignal when it is
        resized.

        :param old: Widget used to hold the image preview
        :type old: QLabel
        """
        layout: QLayout = old.parent().layout()
        old: QLabel = self.centralWidget.l_image
        old_name: str = old.objectName()
        old_style: QStyle = old.style()
        new_label: MyQLabel = MyQLabel()
        new_label.setPixmap(old.pixmap())
        new_label.setSizePolicy(old.sizePolicy())
        new_label.setMinimumSize(old.minimumSize())
        new_label.setMaximumSize(old.maximumSize())
        new_label.setParent(old.parent())
        layout.replaceWidget(old, new_label)
        old.deleteLater()
        new_label.setObjectName(old_name)
        new_label.setStyle(old_style)
        new_label.setStyleSheet(old.styleSheet())
        self.centralWidget.l_image = new_label

    def close(self):
        """
        Method used to save data and close the window
        """
        self.save()
        self.settingsUI.close()
        super(MainWindow, self).close()

    def show(self):
        """
        Method used to show the window and load the image
        """
        try:
            self.load()
            self.image = None
        except FileNotFoundError:
            pass
        super(MainWindow, self).show()

    def save(self, js=True):
        """
        Method used to save data to a pickle file.

        :param js: (optional) If True a json will also be saved (mainly for debug and to read data without launching
                    the tool), default is True
        :type js: bool
        """
        self.update_data()
        try:
            with open(self.savefile, 'wb') as f:
                try:
                    pickle.dump(self.data, f)
                except TypeError:
                    print(self.data)

            if js:
                with open(self.savefile_json, 'w', encoding="utf-8") as save_file:
                    json.dump(self.data, save_file, indent=4, sort_keys=True)

        except Exception:
            tr.print_exc()

    def save_player(self):
        """
        Method used to save current player parameters data into the players' data dictionary
        """
        self.update_data()
        c_widget: QWidget = self.centralWidget
        player: dict = self.data["player"]
        self.change_signals_block_state(True)

        if c_widget.cob_players_select.findText(player['Name']) == -1:
            new_player_list: List[str] = list()
            new_player_list.append(player['Name'])
            selected_player_name: str = c_widget.cob_players_select.currentText()

            for row in range(c_widget.cob_players_select.count()):
                text: str = c_widget.cob_players_select.itemText(row)

                if text != "New Player":
                    new_player_list.append(text)
                    try:
                        del (self.data['players'][c_widget.cob_players_select.currentText()])
                    except KeyError:
                        pass

            if selected_player_name != 'New Player':
                new_player_list.remove(selected_player_name)

            new_player_list: List[str] = ["New Player"] + sorted(new_player_list)

            c_widget.cob_players_select.clear()

            for p in new_player_list:
                c_widget.cob_players_select.addItem(p)

            c_widget.cob_players_select.setCurrentIndex(c_widget.cob_players_select.findText(player['Name']))

        elif c_widget.cob_players_select.findText(player['Name']) is not c_widget.cob_players_select.currentIndex():
            c_widget.cob_players_select.setCurrentIndex(c_widget.cob_players_select.findText(player['Name']))

        try:
            self.data["players"][player["Name"]] = player
        except KeyError:
            self.data["players"] = dict()
            self.data["players"][player["Name"]] = player

        self.change_signals_block_state(False)

    def del_player(self):
        """
        Method used to remove all current player data
        """
        try:
            c_widget: QWidget = self.centralWidget
            del (self.data["players"][c_widget.cob_players_select.currentText()])
            c_widget.cob_players_select.removeItem(c_widget.cob_players_select.currentIndex())

        except KeyError:
            pass

    def update_player(self):
        """
        Method used to switch to new selected player data
        """
        try:
            c_widget: QWidget = self.centralWidget
            player_name: str = c_widget.cob_players_select.currentText()

            if player_name != "New Player":
                try:
                    self.data["player"]: PlayerDict = self.data["players"][player_name]
                except KeyError:
                    tr.print_exc()
            else:
                self.data["player"]: PlayerDict = {"Name": "Player Name", "Color": "Black", "Entries": list()}

            self.update_ui()
            self.update_data()

        except Exception:
            tr.print_exc()

    def progress_update(self, set=False, start=None, stop=None, i=1, current=None, fullstop=False):
        """
        Method used to control the main QProgressbar and call the method 'show' and 'hide' of its QFrame container

        :param set: (optional) Reset the progress to 0 or given value
        :param start: (optional) If given and 'set=True', will set the minimum value for the progress bar, default is 0
        :param stop: (optional) If given and 'set=True', will set the maximum value for the progress bar, default is 100
        :param i: (optional) If given, will increase the current value by the given value, default is 1
        :param current: (optional) If given, will hardwrite the current value
        :param fullstop: (optional) If given, will stop and hide the progress bar
        :type set: bool
        :type start: int or float
        :type stop: int or float
        :type i: int
        :type current: int or float
        :type fullstop: bool
        """
        bar = self.centralWidget.prb_preview
        if set:
            if start:
                self.__start: int = start
            else:
                self.__start: int = 0

            if stop:
                self.__stop: int = stop
            else:
                self.__stop: int = 100

            self.__i = i

            if current:
                self.__current: int = current
            else:
                self.__current: int = self.__start

        else:
            self.__i: int = i

            if current:
                self.__current: int = current
            else:
                self.__current += self.__i

        bar.setMinimum(self.__start)
        bar.setMaximum(self.__stop)
        bar.setValue(self.__current)

        if bar.value() >= bar.maximum() or fullstop:
            self.centralWidget.f_progress_bar.hide()

        self.update()

    @property
    def current_player_data(self):
        """
        Property that tries to return the current player data dictionary extracted from UI placeholderText values

        :return: Current player data dictionary
        :rtype: PlayerDict
        """
        try:
            self.__player_data = {
                "Name": self.centralWidget.le_player_name.placeholderText(),
                "Color": self.centralWidget.le_player_color.placeholderText(),
                "Entries": [self.centralWidget.lw_player_entries.item(entry).text() for entry in
                            range(self.centralWidget.lw_player_entries.count())]
            }

            return self.__player_data

        except Exception:
            tr.print_exc()

    @current_player_data.setter
    def current_player_data(self, data=None):
        """
        Property.setter that sets current player data dictionary values into UI placeholderText values

        :param data: (optional) override current player data and force given values
        :type data: PlayerDict
        """
        if data:
            self.__player_data: Dict[str, List[str]] = data

        c_widget: QWidget = self.centralWidget
        c_widget.le_player_name.setText("")

        c_widget.le_player_name.setPlaceholderText(
            self.__player_data["Name"] if 'Name' in self.__player_data.keys() else "Player Name")

        c_widget.lw_player_entries.clear()

        if "Entries" in self.__player_data.keys():
            for entry in self.__player_data["Entries"]:
                self.add_entry(entry)

        c_widget.le_player_color.setText('')

        c_widget.le_player_color.setPlaceholderText(
            self.__player_data["Color"] if 'Color' in self.__player_data.keys() else "Black")

    def load(self, js=True):
        """
        Method that loads save data into UI

        :param js: (optional) Force json save file
        :type js: bool
        """
        with open(self.savefile, 'rb') as data_file:
            try:
                self.data = pickle.load(data_file)
            except EOFError:
                tr.print_exc()

        if js:
            try:
                with open(self.savefile_json, 'r', encoding="utf-8") as data_file:
                    self.data = json.load(data_file)
            except EOFError:
                tr.print_exc()

        try:
            self.update_ui(True)
        except KeyError:
            tr.print_exc()

    @property
    def data(self):
        """
        Property that returns players data

        :return: Current players' data values
        :rtype: DataDict
        """
        return self.__data

    @data.setter
    def data(self, data):
        """
        Property.setter that override players data

        :param data: New players' data values
        :type data: DataDict
        """
        self.__data = data.copy()

    @property
    def image(self):
        """
        Property that returns the QLabel used to show the image preview

        :return: the QLabel holding the image preview
        :rtype: PySide2.QWidgets.QLabel
        """
        return self.centralWidget.l_image

    @image.setter
    def image(self, img=None):
        """
        Property that generate the preview image

        :param img: (optional) if given, will override the image preview with the one given
        :type img: np.ndarray
        """
        # self.update_data()
        try:
            f_path = self.__TMP

            if not img:
                line_qual = int(360 * (10 ** np.linspace(-0.5, 3.8, 100)[self.data["hs_line_quality"]]))
                t = self.data["le_image_title"] if self.data["chb_image_title"] else False

                alignment = 'left' if self.data["title_alignment"] == 0 else 'right' if \
                    self.data["title_alignment"] == 2 else "center"

                vis.plot_background(n=line_qual, kwargs=BACKGROUND_KWARGS)

                vis.plot_foreground(tight=False, kwargs={'title': t, 'alignment': alignment, 'fontsize':
                    self.__fontsize * 1.1})

                self.savefig(f_path, min(self.data['sb_image_dpi'], 500), "png", quality=6, transparency=True)

            self.centralWidget.l_image.setPixmap(QPixmap(f_path).scaled(np.array(self.centralWidget.l_image.size()) * 1,
                                                                        mode=Qt.SmoothTransformation,
                                                                        aspectMode=Qt.KeepAspectRatio))

        except KeyError:
            pass

    def resize_image(self):
        """
        Method called by QSignal that generates a resized preview image
        """
        self.centralWidget.l_image.setPixmap(QPixmap(self.__TMP).scaled(self.centralWidget.l_image.size() * 1,
                                                                        mode=Qt.SmoothTransformation,
                                                                        aspectMode=Qt.KeepAspectRatio))

    def savefig(self, out, size=None, f_format=None, transparency=None, quality=None):
        """
        Method that outputs the final version of the image into the output folder

        :param out: absolute path of the output file
        :param size: (optional) size value converted into dpi for the matplotlib.pyplot.savefig method
        :param f_format: (optional) ['png' or 'jpeg'] override output file format, default is based on user choice data
        :param transparency: (optional) override output transparency if file format is 'png', default is
                            based on user choice data
        :param q: (optional) [1 <-> 12] override jpeg file quality if file format is 'jpeg', default is based on user
                    choice data
        :type out: str
        :type size: int
        :type f_format: str
        :type transparency: bool
        :type quality: int
        """
        self.update_data()
        metadata = METADATA

        metadata["Creation Time"] = time.ctime()

        dpi = size / (72 / 100 * 5.) if size else self.data["sb_image_dpi"] / (72 / 100 * 5.)

        f_format = f_format if f_format else "png" if self.data["image_format"] < 2 else "jpeg"

        transparency = transparency if transparency else True if self.data["image_format"] == 1 else False

        quality = round(np.linspace(0, 95, 12)[quality - 1]) if quality else round(
            np.linspace(0, 95, 12)[self.data["hs_jpeg_qual"] - 1])

        plt.savefig(fname=out, dpi=dpi, format=f_format, transparent=transparency, pil_kwargs={
            'quality': int(round(quality)), "metadata": metadata})

    def update_data(self):
        """
        Update data dictionary based on UI values
        """
        try:
            data: DataDict = dict()
            c_widget: QWidget = self.centralWidget
            s_c_widget: QWidget = self.settingsUI.centralWidget
            data['chb_image_title'] = c_widget.chb_image_title.isChecked()
            data['le_image_title'] = c_widget.le_image_title.placeholderText()
            data["sb_first_entry_weight"] = c_widget.sb_first_entry_weight.value()
            data["sb_rolling_window_size"] = c_widget.sb_rolling_window_size.value()
            data["cob_players_select"] = c_widget.cob_players_select.currentIndex()
            data["gb_add_auto_party"] = c_widget.gb_add_auto_party.isChecked()
            data["le_party_color"] = c_widget.le_party_color.placeholderText()
            data["le_party_name"] = c_widget.le_party_name.placeholderText()
            data["cob_party_starting_alignment"] = c_widget.cob_party_starting_alignment.currentText()
            data["rb_average"] = c_widget.rb_party_average.isChecked()

            data['out_path'] = os.path.realpath((s_c_widget.le_output_path.text())) \
                if s_c_widget.le_output_path.text() else os.path.realpath((s_c_widget.le_output_path.placeholderText()))

            data["image_format"] = 0 if s_c_widget.rb_png.isChecked() else 1 \
                if s_c_widget.rb_png_transparency.isChecked() else 2

            data["hs_line_quality"] = s_c_widget.hs_line_quality.value()
            data["hs_jpeg_qual"] = s_c_widget.hs_jpeg_qual.value()
            data["sb_image_dpi"] = s_c_widget.sb_image_dpi.value()
            data["hs_current_scale"] = s_c_widget.hs_current_scale.value()
            data["hs_legend_h_offset"] = s_c_widget.hs_legend_h_offset.value()
            data["hs_legend_v_offset"] = s_c_widget.hs_legend_v_offset.value()
            data["hs_legend_v_offset"] = s_c_widget.hs_legend_v_offset.value()
            data["hs_legend_stretch"] = s_c_widget.hs_legend_stretch.value()
            data["hs_scale"] = s_c_widget.hs_scale.value()

            data["le_party_color"] = c_widget.le_party_color.placeholderText()
            data["le_party_name"] = c_widget.le_party_name.placeholderText()

            data["legend_text_alignment"] = 0 if s_c_widget.rb_legend_text_left.isChecked() else 1 if \
                s_c_widget.rb_legend_text_center.isChecked() else 2

            data["le_current_custom"] = s_c_widget.le_current_custom.text()

            data["current_marker"] = 0 if s_c_widget.rb_current_o.isChecked() else 1 \
                if s_c_widget.rb_current_x.isChecked() else 2 if s_c_widget.rb_current_star.isChecked() else 3 \
                if s_c_widget.rb_current_plus.isChecked() else 4 if s_c_widget.rb_current_left.isChecked() else 5 \
                if s_c_widget.rb_current_up.isChecked() else 6 if s_c_widget.rb_current_right.isChecked() else 7 \
                if s_c_widget.rb_current_down.isChecked() else 8 if s_c_widget.rb_current_none.isChecked() else 9

            data["le_previous_custom"] = s_c_widget.le_previous_custom.text()

            data["previous_marker"] = 0 if s_c_widget.rb_previous_o.isChecked() else 1 \
                if s_c_widget.rb_previous_x.isChecked() else 2 if s_c_widget.rb_previous_star.isChecked() else 3 \
                if s_c_widget.rb_previous_plus.isChecked() else 4 if s_c_widget.rb_previous_left.isChecked() else 5 \
                if s_c_widget.rb_previous_up.isChecked() else 6 if s_c_widget.rb_previous_right.isChecked() else 7 \
                if s_c_widget.rb_previous_down.isChecked() else 8 if s_c_widget.rb_previous_none.isChecked() else 9

            data["title_alignment"] = 0 if s_c_widget.rb_title_left.isChecked() else 1 \
                if s_c_widget.rb_title_center.isChecked() else 2

            data["player"] = self.current_player_data

            if "players" in self.data.keys():
                data["players"] = self.data["players"]
            else:
                data["players"] = dict()

            self.data = data
            self.__Final = data["out_path"]

        except Exception:
            tr.print_exc()

    def update_ui(self, first_call=False):
        """
        Override UI values safely

        :param bool first_call: (optional) Also call the method to update player values ui, default False
        :type first_call: bool
        """
        self.change_signals_block_state(True)

        try:
            c_widget: QWidget = self.centralWidget
            s_c_widget: QWidget = self.settingsUI.centralWidget
            current_player: str = c_widget.cob_players_select.currentText()

            c_widget.chb_image_title.setChecked(self.data["chb_image_title"])
            c_widget.cob_players_select.clear()
            c_widget.cob_players_select.addItem("New Player")

            for entry in sorted(self.data["players"]):
                c_widget.cob_players_select.addItem(entry)

            c_widget.cob_players_select.setCurrentIndex(c_widget.cob_players_select.findText(current_player))

            c_widget.le_image_title.setPlaceholderText(self.data["le_image_title"] if self.data["le_image_title"] else
                                                       "Party Players Alignment Chart")

            c_widget.sb_first_entry_weight.setValue(self.data["sb_first_entry_weight"])
            c_widget.sb_rolling_window_size.setValue(self.data["sb_rolling_window_size"])
            c_widget.gb_add_auto_party.setChecked(self.data["gb_add_auto_party"])

            c_widget.cob_party_starting_alignment.setCurrentIndex(c_widget.cob_party_starting_alignment.findText(
                self.data["cob_party_starting_alignment"]))

            c_widget.rb_party_average.setChecked(self.data["rb_average"])
            c_widget.le_party_color.setPlaceholderText(self.data["le_party_color"])
            c_widget.le_party_name.setPlaceholderText(self.data["le_party_name"])

            if current_player in self.data['players'].keys():
                p = self.data['players'][current_player]
                c_widget.le_player_color.setPlaceholderText(p['Color'])
                c_widget.le_player_name.setPlaceholderText(p['Name'])
                c_widget.lw_player_entries.clear()
                for entry in p["Entries"]:
                    c_widget.lw_player_entries.addItem(entry)

            elif current_player == "New Player":
                c_widget.le_player_color.setPlaceholderText("Black")
                c_widget.le_player_name.setPlaceholderText("Player Name")
                c_widget.lw_player_entries.clear()

            s_c_widget.rb_png.setChecked(True) if self.data["image_format"] == 0 \
                else s_c_widget.rb_png_transparency.setChecked(True) if self.data["image_format"] == 1 \
                else s_c_widget.rb_jpeg.setChecked(True)

            s_c_widget.hs_current_scale.setValue(self.data["hs_current_scale"])
            s_c_widget.hs_line_quality.setValue(self.data["hs_line_quality"])
            s_c_widget.hs_jpeg_qual.setValue(self.data["hs_jpeg_qual"])
            s_c_widget.sb_image_dpi.setValue(self.data["sb_image_dpi"])
            s_c_widget.hs_legend_h_offset.setValue(self.data["hs_legend_h_offset"])
            s_c_widget.hs_legend_v_offset.setValue(self.data["hs_legend_v_offset"])
            s_c_widget.hs_legend_stretch.setValue(self.data["hs_legend_stretch"])
            s_c_widget.hs_scale.setValue(self.data["hs_scale"])
            s_c_widget.le_current_custom.setText(self.data["le_current_custom"])
            s_c_widget.le_output_path.setText(self.data["out_path"])

            s_c_widget.rb_current_o.setChecked(True) if self.data["current_marker"] == 0 \
                else s_c_widget.rb_current_x.setChecked(True) if self.data["current_marker"] == 1 \
                else s_c_widget.rb_current_star.setChecked(True) if self.data["current_marker"] == 2 \
                else s_c_widget.rb_current_plus.setChecked(True) if self.data["current_marker"] == 3 \
                else s_c_widget.rb_current_left.setChecked(True) if self.data["current_marker"] == 4 \
                else s_c_widget.rb_current_up.setChecked(True) if self.data["current_marker"] == 5 \
                else s_c_widget.rb_current_right.setChecked(True) if self.data["current_marker"] == 6 \
                else s_c_widget.rb_current_down.setChecked(True) if self.data["current_marker"] == 7 \
                else s_c_widget.rb_current_none.setChecked(True) if self.data["current_marker"] == 8 \
                else s_c_widget.rb_current_custom.setChecked(True)

            s_c_widget.rb_previous_o.setChecked(True) if self.data["previous_marker"] == 0 \
                else s_c_widget.rb_previous_x.setChecked(True) if self.data["previous_marker"] == 1 \
                else s_c_widget.rb_previous_star.setChecked(True) if self.data["previous_marker"] == 2 \
                else s_c_widget.rb_previous_plus.setChecked(True) if self.data["previous_marker"] == 3 \
                else s_c_widget.rb_previous_left.setChecked(True) if self.data["previous_marker"] == 4 \
                else s_c_widget.rb_previous_up.setChecked(True) if self.data["previous_marker"] == 5 \
                else s_c_widget.rb_previous_right.setChecked(True) if self.data["previous_marker"] == 6 \
                else s_c_widget.rb_previous_down.setChecked(True) if self.data["previous_marker"] == 7 \
                else s_c_widget.rb_previous_none.setChecked(True) if self.data["previous_marker"] == 8 \
                else s_c_widget.rb_previous_custom.setChecked(True)

            s_c_widget.le_previous_custom.setText(self.data["le_previous_custom"])

            s_c_widget.rb_title_left.setChecked(True) if self.data["title_alignment"] == 0 \
                else s_c_widget.rb_title_center.setChecked(True) if self.data["title_alignment"] == 1 \
                else s_c_widget.rb_title_right.setChecked(True)

            s_c_widget.rb_legend_text_left.setChecked(True) if self.data["legend_text_alignment"] == 0 else \
                s_c_widget.rb_legend_text_center.setChecked(True) if self.data["legend_text_alignment"] == 1 else \
                    s_c_widget.rb_legend_text_right.setChecked(True)

            s_c_widget.le_output_path.setText(self.__Final)
            self.current_player_data = self.data["player"] if "player" in self.data.keys() else None

            if first_call:
                self.update_player()
        except KeyError:
            pass
        except Exception:
            tr.print_exc()

        self.change_signals_block_state(False)

    def set_color(self, in_le):
        """
        Method that verifies if the color value entered in the given QLineEdit is valid, if so update QLabel
        placeholder value and change focus

        :param in_le: A QLineEdit widget to test
        :type in_le: QLineEdit
        """
        colors = ('black', 'blue', 'brown', 'cyan', 'darkblue', 'darkcyan', 'darkgray', 'darkgreen', 'darkmagenta',
                  'darkred', 'gray', 'green', 'lightblue', 'lightcyan', 'lightgray', 'lightgreen', 'lightmagenta',
                  'lightred', 'magenta', 'orange', 'red', 'white', 'yellow', "pink", "")
        # FIXME: Some colors return an error, they need to be checked and possibly extended

        if in_le is self.centralWidget.le_player_color:
            if self.centralWidget.le_player_color.text().lower() in colors:
                if self.centralWidget.le_player_color.text():
                    self.centralWidget.le_player_color.setPlaceholderText(
                        self.centralWidget.le_player_color.text().capitalize())

                    self.centralWidget.le_player_color.setText("")
                self.centralWidget.le_player_entry.setFocus()

        elif in_le is self.centralWidget.le_party_color:
            if self.centralWidget.le_party_color.text().lower() in colors:
                if self.centralWidget.le_party_color.text():
                    self.centralWidget.le_party_color.setPlaceholderText(
                        self.centralWidget.le_party_color.text().capitalize())

                    self.centralWidget.le_party_color.setText("")
                self.centralWidget.le_player_name.setFocus()

        self.update_data()

    def set_player_color(self):
        """
        Check and change the current player name in the GUI
        """
        self.set_color(self.centralWidget.le_player_color)

    def set_party_color(self):
        """
        Check and change the party name in the GUI
        """
        self.set_color(self.centralWidget.le_party_color)

    def set_name(self, le_name):
        """
        Method that checks a given QLineEdit for a new inputted value, then changes focus
        :param le_name: A QLineEdit that may have a new text value
        :type le_name: QLineEdit
        """

        if le_name is self.centralWidget.le_player_name:
            if self.centralWidget.le_player_name.text():
                self.centralWidget.le_player_name.setPlaceholderText(self.centralWidget.le_player_name.text())
                self.centralWidget.le_player_name.setText("")
            self.centralWidget.le_player_color.setFocus()

        elif le_name is self.centralWidget.le_party_name:
            if self.centralWidget.le_party_name.text():
                self.centralWidget.le_party_name.setPlaceholderText(self.centralWidget.le_party_name.text())
                self.centralWidget.le_party_name.setText("")

            self.centralWidget.le_party_color.setFocus()

        self.update_data()

    def set_party_name(self):
        """
        Method that updates the party name if a new entry was given
        """
        self.set_name(self.centralWidget.le_party_name)

    def set_player_name(self):
        """
        Method that updates the current player name if a new entry was given
        """
        self.set_name(self.centralWidget.le_player_name)

    def set_title(self):
        """
        Method that updates the current party name if a new entry was given
        """
        if self.centralWidget.le_image_title.text():
            self.centralWidget.le_image_title.setPlaceholderText(self.centralWidget.le_image_title.text())
            self.centralWidget.le_image_title.setText("")

        self.centralWidget.le_player_name.setFocus()
        self.update_data()

    def add_entry(self, entry=None):
        """
        Method that verifies if new alignment entry is valid, if so adds it to the QListWidget

        :param entry: (optional) Overrides new entry value, default is None
        :type entry: str
        """
        alignement = ("LG", "LB", "NG", "NB", "CG", "CB", "LN", "TN", "CN", "LE", "LM", "NE", "NM", "CE", "CM", "L",
                      "N", "T", "C", "G", "B", "E", "M")

        if not entry:
            entry = self.centralWidget.le_player_entry.text().upper()

        if entry in alignement:
            self.centralWidget.lw_player_entries.addItem(entry)
            self.centralWidget.le_player_entry.clear()

        self.update_data()

    def del_entry(self):
        """
        Method that deletes the selected entry (or the last if none is selected) of the QListWidget
        """
        if self.centralWidget.lw_player_entries.currentItem():
            self.centralWidget.lw_player_entries.takeItem(self.centralWidget.lw_player_entries.currentRow())
        else:
            self.centralWidget.lw_player_entries.takeItem(self.centralWidget.lw_player_entries.count() - 1)

    def clear_entries(self):
        """
        Method that clear all current QListWidget entries
        """
        self.centralWidget.lw_player_entries.clear()

    def run_generate_image(self):
        """
        Method that tries to render the output image of the graph and update the progress bar
        """
        if self.finished:
            self.finished = False
            self.update_data()
            data: DataDict = self.data
            players: Dict[str, PlayerDict] = data['players']
            line_qual = int(360 * (10 ** np.linspace(-0.5, 3.8, 100)[data["hs_line_quality"]]))
            tasks = 0

            for player in players:
                player: PlayerDict = players[player]
                tasks += (max(0, data['sb_first_entry_weight'] - data['sb_rolling_window_size'])) * 2
                tasks += (len(player["Entries"]) - 1) * 2

            tasks += (max(0, data['sb_first_entry_weight'] - data['sb_rolling_window_size'])) * 2 + 2
            self.progress_update(True, 0, 10 + tasks + line_qual, 1, 0)

        try:
            self.centralWidget.pb_generate.setEnabled(False)
            worker: Worker = Worker((self.data.copy(), self.__Final, self.__TMP, self.__fontsize))
            worker.moveToThread(self.loop)
            worker.finished.connect(self.get_generated_image, Qt.QueuedConnection)
            worker.signal.connect(self.progress_update, Qt.QueuedConnection)
            worker.finished.connect(worker.deleteLater, Qt.QueuedConnection)
            self.loop.started.connect(worker.generate_image, Qt.QueuedConnection)
            self.loop.finished.connect(self.loop.quit, Qt.QueuedConnection)
            self.loop.start()
            self.loop.setPriority(QThread.LowPriority)
            self.update()
            self.workers.append(worker)

        except Exception:
            tr.print_exc()
            self.centralWidget.pb_generate.setEnabled(True)

    def get_generated_image(self):
        """
        Method called when a QThread worker is done. Assign the image and return to the "default" GUI look
        """
        self.update()
        self.finished = True
        self.loop.quit()
        time.sleep(0.2)
        self.image = self.__TMP
        self.progress_update(fullstop=True)
        self.centralWidget.pb_generate.setEnabled(True)
        self.update()


PATH = __file__.split("__init__")[0]


def launch():
    """
    Instantiate a new QAplication and mainWindow classes and takes stdin input for savefile name

    :param app: (optional) If given, will not generate a new instance but use the one given, default is None
    :param win: (optional) if given, will not generate a new instance but use the one given, default is None
    :type app: PySide2.QtWidgets.QApplication
    :type app: PySide2.QtWidgets.QMainWindow
    """
    global app
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("partyAlignmentChartTool")
        app.setApplicationDisplayName("Party Alignment Chart Tool")
        app.setApplicationVersion("1.0.2")
        app.setOrganizationName("Julien Alardot")
        win = MainWindow(input("Savefile Name: "))
        win.resize(0, 0)
        app.setWindowIcon(QIcon(os.path.join(PATH, "UI", "AlignmentTool.icon")))
        app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))
        app.setActiveWindow(win)
        app.focusWindow()
        app.exec_()
        app.deleteLater()
        del (app)

    except Exception:
        tr.print_exc()
