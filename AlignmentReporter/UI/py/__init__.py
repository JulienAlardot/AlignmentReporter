import json
import math
import os
import pickle
import sys
import time
import traceback as tr

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PySide2.QtCore import QFile, Qt, Signal, SIGNAL, SLOT, QThread, QObject
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QSizePolicy, QMainWindow, QApplication, QLabel
from multiprocessing import Pool

import AlignmentReporter.Vizualisation as vis
import AlignmentReporter.UI.Qt.AlignmentReporterRessources as ar_r

path = __file__.split("UI")[0]



icon_path = os.path.join(path, "UI", "Qt")



class settingWindow(QMainWindow):
    def __init__(self, parent=None):
        """
        Subclass used for the child window with the graph customization parameters
        :param parent: (optional) Set the parent window instance for this subclass instance
        :type parent: PySide2.QtWidgets.QWidget
        """
        # Window setup
        super(settingWindow, self).__init__()
        loader = QUiLoader()
        file = QFile(os.path.join(path, "UI", "Qt", "imageSettings.ui"))
        file.open(QFile.ReadOnly)
        self.centralWidget = loader.load(file, self)
        file.close()
        # self.setParent(parent)
        self.setWindowTitle("Image Settings")
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        # self.setMinimumSize(self.centralWidget.minimumSize())
        self.assignWidgets()
        self.setWindowFlags(Qt.Window)
        with open(os.path.join(path, "UI", "Qt", "style.css"), "r") as f:
            self.setStyleSheet(f.read())
        self.setWindowIcon(
            QIcon(
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
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


class mainWindow(QMainWindow):
    advanced = Signal()
    
    def __init__(self, savefile):
        """
        Subclass used for the child window with the graph customization parameters
        :param savefile: name string for the saving file e.g: "Celtaidd"
        :type savefile: str
        """
        # Window setup
        super(mainWindow, self).__init__()
        with open(os.path.join(path, "UI", "Qt", "style.css"), "r") as f:
            style = f.read()
        self.setStyleSheet(style)
        loader = QUiLoader()
        f = QFile(os.path.join(path, "UI", "Qt", "mainWindow.ui"))
        f.open(QFile.ReadOnly)
        self.centralWidget = loader.load(f, self)
        f.close()
        self.setWindowIcon(
            QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'AlignmentTool.ico')))
        self.setUI = settingWindow(self)
        self.settingsUI = self.setUI
        
        self.setWindowTitle("Party Setup")
        self.settingsUI.setWindowTitle("Image Settings")
        self.__save = savefile
        self.assignWidgets()
        self.setWindowFlags(Qt.Window)
        
        # Plugin setup
        
        # Custom variables
        self.datapath = os.path.join(path, "data")
        self.savefile = os.path.join(self.datapath, self.__save + ".pkl")
        self.savefile_json = os.path.join(self.datapath, self.__save + ".json")
        self.data = dict()
        self.__TMP = os.path.join(self.datapath, "TMP.pkl")
        self.__Final = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "out")
        self.__player_data = dict()
        self.__fontsize = 8
        self.finished = True
        
        # Init Widgets
        self.mutate_widget(self.centralWidget.l_image)
        self.centralWidget.f_progress_bar.hide()
        self.centralWidget.prb_preview.setValue(0)
        self.centralWidget.l_image.resized.connect(self.resizeImage)
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
            widget.setProperty("holder", True)
        # Custom functions calls
        self.show()
    
    ####################################################################################################################
    #                                               Default functions                                                  #
    ####################################################################################################################
    def assignWidgets(self):
        """
        Method used to connect QSignals to other Methods
        """
        self.centralWidget.tb_settings.released.connect(self.setUI.show)
        self.centralWidget.pb_save_quit.released.connect(self.close)
        self.centralWidget.pb_set_color.released.connect(self.setPlayerColor)
        self.centralWidget.pb_set_party_color.released.connect(self.setPartyColor)
        self.centralWidget.pb_set_name.released.connect(self.setPlayerName)
        self.centralWidget.pb_set_party_name.released.connect(self.setPartyName)
        self.centralWidget.pb_set_title.released.connect(self.setTitle)
        self.centralWidget.pb_add_player_entry.released.connect(self.addEntry)
        self.centralWidget.pb_delete_player_entry.released.connect(self.delEntry)
        self.centralWidget.pb_delete_player_all_entries.released.connect(self.clearEntries)
        self.centralWidget.pb_save_player.released.connect(self.savePlayer)
        self.centralWidget.pb_del_player.released.connect(self.delPlayer)
        self.centralWidget.cob_players_select.currentIndexChanged.connect(self.updatePlayer)
        self.centralWidget.pb_generate.released.connect(self.runGenerateImage)
        self.centralWidget.pb_save.released.connect(self.save)
        # self.centralWidget.gb_add_auto_party.toggled.connect(self.clicked_party_player)
        self.advanced.connect(self.progressUpdate)
    
    def updateSignalBlock(self, state):
        """
        Method used to un/block QSignals on critical connections when an infinite loop is possible
        :param state: (optional) Set the parent window instance for this subclass instance
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
        :param old: Qlabel object of the image preview
        :type old: PySide2.QtWidgets.QLabel
        """
        layout = old.parent().layout()
        old = self.centralWidget.l_image
        old_name = old.objectName()
        old_style = old.style()
        new = myQLabel()
        new.setPixmap(old.pixmap())
        new.setSizePolicy(old.sizePolicy())
        new.setMinimumSize(old.minimumSize())
        new.setMaximumSize(old.maximumSize())
        new.setParent(old.parent())
        layout.replaceWidget(old, new)
        old.deleteLater()
        new.setObjectName(old_name)
        new.setStyle(old_style)
        new.setStyleSheet(old.styleSheet())
        self.centralWidget.l_image = new
    
    def close(self):
        """
        Method used to save data and close the window
        """
        self.save()
        self.setUI.close()
        super(mainWindow, self).close()
    
    def show(self):
        """
        Method used to show the window and load the image
        """
        try:
            self.load()
            self.image = None
        except FileNotFoundError:
            pass
        super(mainWindow, self).show()
    
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
                with open(self.savefile_json, 'w', encoding="utf-8") as f:
                    json.dump(self.data, f, indent=4, sort_keys=True)
        except Exception:
            tr.print_exc()
    
    def savePlayer(self):
        """
        Method used to save current player parameters data into the players data dictionnary
        """
        self.update_data()
        w = self.centralWidget
        player = self.data["player"]
        self.updateSignalBlock(True)
        if w.cob_players_select.findText(player['Name']) == -1:
            l = list()
            l.append(player['Name'])
            r = w.cob_players_select.currentText()
            for row in range(w.cob_players_select.count()):
                text = w.cob_players_select.itemText(row)
                if text != "New Player":
                    l.append(text)
                    try:
                        del self.data['players'][w.cob_players_select.currentText()]
                    except KeyError:
                        pass
            if r != 'New Player':
                l.remove(r)
            l = ["New Player"] + sorted(l)
            
            w.cob_players_select.clear()
            for p in l:
                w.cob_players_select.addItem(p)
            w.cob_players_select.setCurrentIndex(w.cob_players_select.findText(player['Name']))
        
        elif w.cob_players_select.findText(player['Name']) is not w.cob_players_select.currentIndex():
            w.cob_players_select.setCurrentIndex(w.cob_players_select.findText(player['Name']))
        try:
            self.data["players"][player["Name"]] = player
        except KeyError:
            self.data["players"] = dict()
            self.data["players"][player["Name"]] = player
        
        self.updateSignalBlock(False)
    
    def delPlayer(self):
        """
        Method used to remove all current player data
        """
        try:
            w = self.centralWidget
            del self.data["players"][w.cob_players_select.currentText()]
            w.cob_players_select.removeItem(w.cob_players_select.currentIndex())
        except KeyError:
            pass
    
    def updatePlayer(self):
        """
        Method used to switch to new selected player data
        """
        try:
            w = self.centralWidget
            player_name = w.cob_players_select.currentText()
            if player_name != "New Player":
                try:
                    self.data["player"] = self.data["players"][player_name]
                except KeyError:
                    tr.print_exc()
            else:
                self.data["player"] = {"Name": "Player Name", "Color": "Black", "Entries": list()}
            self.update_ui()
            self.update_data()
        except Exception:
            tr.print_exc()
    
    def progressUpdate(self, set=False, start=None, stop=None, i=1, current=None, fullstop=False):
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
                self.__start = start
            else:
                self.__start = 0
            
            if stop:
                self.__stop = stop
            else:
                self.__stop = 100
            
            self.__i = i
            if current:
                self.__current = current
            else:
                self.__current = self.__start
        
        else:
            self.__i = i
            if current:
                self.__current = current
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
        Property that tries to return the current player data dictionnary extracted from UI placeholderText values
        :return: Current player data dictionnay
        :rtype: int or float
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
        Property.setter that sets current player data dictionnary values into UI placeholderText values
        :param data: (optional) override current player data and force given values
        :type data: dict
        """
        if data:
            self.__player_data = data
        w = self.centralWidget
        w.le_player_name.setText("")
        w.le_player_name.setPlaceholderText(
            self.__player_data["Name"] if 'Name' in self.__player_data.keys() else
            "Player Name")
        w.lw_player_entries.clear()
        if "Entries" in self.__player_data.keys():
            for entry in self.__player_data["Entries"]:
                self.addEntry(entry)
        
        w.le_player_color.setText('')
        w.le_player_color.setPlaceholderText(
            self.__player_data["Color"] if 'Color' in self.__player_data.keys() else
            "Black")
    
    def load(self, js=True):
        """
        Method that loads save dato into UI
        :param js: (optional) Force json save file
        :type js: book
        """
        with open(self.savefile, 'rb') as f:
            try:
                self.data = pickle.load(f)
            except EOFError:
                tr.print_exc()
        if js:
            try:
                with open(self.savefile_json, 'r', encoding="utf-8") as f:
                    self.data = json.load(f)
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
        :return: Current players data values
        :rtype: dict
        """
        return self.__data
    
    @data.setter
    def data(self, data):
        """
        Property.setter that override players data
        :param data: New players data values
        :type data: dict
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
        :type img: numpy.array
        """
        # self.update_data()
        try:
            f = self.__TMP
            if not img:
                line_qual = int(360 * (10 ** np.linspace(-0.5, 3.8, 100)[self.data["hs_line_quality"]]))
                t = self.data["le_image_title"] if self.data["chb_image_title"] else False
                alignment = 'left' if self.data["title_alignment"] == 0 else 'right' if \
                    self.data["title_alignment"] == 2 else "center"
                
                vis.plot_background(n=line_qual, kwargs=BACKGROUND_KWARGS)
                vis.plot_foreground(
                    tight=False, kwargs={
                        'title': t, 'alignment': alignment, 'fontsize':
                            self.__fontsize * 1.1})
                
                self.savefig(f, min(self.data['sb_image_dpi'], 500), "png", q=6, t=True)
            self.centralWidget.l_image.setPixmap(
                QPixmap(f).scaled(np.array(self.centralWidget.l_image.size()) * 1, mode=Qt.SmoothTransformation,
                    aspectMode=Qt.KeepAspectRatio))
        except KeyError:
            pass
    
    def resizeImage(self):
        """
        Method called by QSignal that generates a resized preview image
        """
        self.centralWidget.l_image.setPixmap(
            QPixmap(self.__TMP).scaled(
                self.centralWidget.l_image.size() * 1,
                mode=Qt.SmoothTransformation,
                aspectMode=Qt.KeepAspectRatio))
    
    def savefig(self, out, size=None, f=None, t=None, q=None):
        """
        Method that outputs the final version of the image into the output folder
        :param out: fullpath of the output file
        :param size: (optional) size value converted into dpi for the matplotlib.pyplot.savefig method
        :param f: (optional) ['png' or 'jpeg'] override output file format, default is based on user choice data
        :param t: (optional) override output transparency if file format is 'png', default is based on user choice data
        :param q: (optional) [1 <-> 12] override jpeg file quality if file format is 'jpeg', default is based on user
            choice data
        :type out: str
        :type size: int
        :type f: str
        :type t: bool
        :type q: int
        """
        self.update_data()
        try:
            metadata = METADATA
        except NameError:
            metadata = METADATA
        metadata["Creation Time"] = time.ctime()
        dpi = size / (72 / 100 * 5.) if size else self.data["sb_image_dpi"] / (72 / 100 * 5.)
        f = f if f else "png" if self.data["image_format"] < 2 else "jpeg"
        t = t if t else True if self.data["image_format"] == 1 else False
        q = round(np.linspace(0, 95, 12)[q - 1]) if q else round(
            np.linspace(0, 95, 12)[self.data["hs_jpeg_qual"] - 1])
        plt.savefig(
            fname=out, dpi=dpi, format=f, transparent=t, pil_kwargs={
                'quality': int(round(q)), "metadata":
                    metadata})
    
    def update_data(self):
        """
        Update data dictionary based on UI values
        """
        try:
            data = dict()
            w = self.centralWidget
            ww = self.settingsUI.centralWidget
            data['chb_image_title'] = w.chb_image_title.isChecked()
            data['le_image_title'] = w.le_image_title.placeholderText()
            data["sb_first_entry_weight"] = w.sb_first_entry_weight.value()
            data["sb_rolling_window_size"] = w.sb_rolling_window_size.value()
            data["cob_players_select"] = w.cob_players_select.currentIndex()
            data["gb_add_auto_party"] = w.gb_add_auto_party.isChecked()
            data["le_party_color"] = w.le_party_color.placeholderText()
            data["le_party_name"] = w.le_party_name.placeholderText()
            data["cob_party_starting_aligmnent"] = w.cob_party_starting_aligmnent.currentText()
            data["rb_average"] = w.rb_party_average.isChecked()
            data['out_path'] = os.path.realpath((ww.le_output_path.text())) if ww.le_output_path.text() else \
                os.path.realpath((ww.le_output_path.placeholderText()))
            data["image_format"] = 0 if ww.rb_png.isChecked() else 1 if ww.rb_png_transparency.isChecked() else 2
            data["hs_line_quality"] = ww.hs_line_quality.value()
            data["hs_jpeg_qual"] = ww.hs_jpeg_qual.value()
            data["sb_image_dpi"] = ww.sb_image_dpi.value()
            data["hs_current_scale"] = ww.hs_current_scale.value()
            data["hs_legend_h_offset"] = ww.hs_legend_h_offset.value()
            data["hs_legend_v_offset"] = ww.hs_legend_v_offset.value()
            data["hs_legend_v_offset"] = ww.hs_legend_v_offset.value()
            data["hs_legend_stretch"] = ww.hs_legend_stretch.value()
            data["hs_scale"] = ww.hs_scale.value()

            data["le_party_color"] = w.le_party_color.placeholderText()
            data["le_party_name"] = w.le_party_name.placeholderText()
            
            data["legend_text_alignment"] = 0 if ww.rb_legend_text_left.isChecked() else 1 if \
                ww.rb_legend_text_center.isChecked() else 2
            data["le_current_custom"] = ww.le_current_custom.text()
            data["current_marker"] = 0 if ww.rb_current_o.isChecked() else 1 if ww.rb_current_x.isChecked() else 2 if \
                ww.rb_current_star.isChecked() else 3 if ww.rb_current_plus.isChecked() else 4 if \
                ww.rb_current_left.isChecked() else 5 if ww.rb_current_up.isChecked() else 6 if \
                ww.rb_current_right.isChecked() else 7 if ww.rb_current_down.isChecked() else 8 if \
                ww.rb_current_none.isChecked() else 9
            data["le_previous_custom"] = ww.le_previous_custom.text()
            data["previous_marker"] = 0 if ww.rb_previous_o.isChecked() else 1 if ww.rb_previous_x.isChecked() else 2 \
                if \
                ww.rb_previous_star.isChecked() else 3 if ww.rb_previous_plus.isChecked() else 4 if \
                ww.rb_previous_left.isChecked() else 5 if ww.rb_previous_up.isChecked() else 6 if \
                ww.rb_previous_right.isChecked() else 7 if ww.rb_previous_down.isChecked() else 8 if \
                ww.rb_previous_none.isChecked() else 9
            data["title_alignment"] = 0 if ww.rb_title_left.isChecked() else 1 if ww.rb_title_center.isChecked() else 2
            data["player"] = self.current_player_data
            if "players" in self.data.keys():
                data["players"] = self.data["players"]
            else:
                data["players"] = dict()
            self.data = data
            self.__Final = data["out_path"]
        except Exception:
            tr.print_exc()
    
    def update_ui(self, firstCall=False):
        """
        Override UI values safely
        :param firstCall: (optional) Also call the method to update player values ui, default False
        :type firstCall: bool
        """
        self.updateSignalBlock(True)
        try:
            w = self.centralWidget
            ww = self.settingsUI.centralWidget
            w.chb_image_title.setChecked(self.data["chb_image_title"])
            current_player = w.cob_players_select.currentText()
            w.cob_players_select.clear()
            w.cob_players_select.addItem("New Player")
            for entry in sorted(self.data["players"]):
                w.cob_players_select.addItem(entry)
            w.cob_players_select.setCurrentIndex(w.cob_players_select.findText(current_player))
            w.le_image_title.setPlaceholderText(
                self.data["le_image_title"] if self.data["le_image_title"] else
                "Party Players Alignment Chart")
            w.sb_first_entry_weight.setValue(self.data["sb_first_entry_weight"])
            w.sb_rolling_window_size.setValue(self.data["sb_rolling_window_size"])
            
            w.gb_add_auto_party.setChecked(self.data["gb_add_auto_party"])
            w.cob_party_starting_aligmnent.setCurrentIndex(
                w.cob_party_starting_aligmnent.findText(self.data["cob_party_starting_aligmnent"]))
            w.rb_party_average.setChecked(self.data["rb_average"])
            
            ww.hs_current_scale.setValue(self.data["hs_current_scale"])
            

            w.le_party_color.setPlaceholderText(self.data["le_party_color"])
            w.le_party_name.setPlaceholderText(self.data["le_party_name"])
            
            if current_player in self.data['players'].keys():
                p = self.data['players'][current_player]
                w.le_player_color.setPlaceholderText(p['Color'])
                w.le_player_name.setPlaceholderText(p['Name'])
                w.lw_player_entries.clear()
                for entry in p["Entries"]:
                    w.lw_player_entries.addItem(entry)
            
            elif current_player == "New Player":
                w.le_player_color.setPlaceholderText("Black")
                w.le_player_name.setPlaceholderText("Player Name")
                w.lw_player_entries.clear()
            ww.rb_png.setChecked(True) if self.data["image_format"] == 0 else \
                ww.rb_png_transparency.setChecked(True) if self.data["image_format"] == 1 else ww.rb_jpeg.setChecked(
                    True)
            ww.hs_line_quality.setValue(self.data["hs_line_quality"])
            ww.hs_jpeg_qual.setValue(self.data["hs_jpeg_qual"])
            ww.sb_image_dpi.setValue(self.data["sb_image_dpi"])
            ww.hs_legend_h_offset.setValue(self.data["hs_legend_h_offset"])
            ww.hs_legend_v_offset.setValue(self.data["hs_legend_v_offset"])
            ww.hs_legend_stretch.setValue(self.data["hs_legend_stretch"])
            ww.hs_scale.setValue(self.data["hs_scale"])
            ww.le_current_custom.setText(self.data["le_current_custom"])
            ww.le_output_path.setText(self.data["out_path"])
            
            ww.rb_current_o.setChecked(True) if self.data["current_marker"] == 0 else ww.rb_current_x.setChecked(True) \
                if self.data["current_marker"] == 1 else ww.rb_current_star.setChecked(True) if \
                self.data["current_marker"] == 2 else ww.rb_current_plus.setChecked(True) if \
                self.data["current_marker"] == 3 else ww.rb_current_left.setChecked(True) if \
                self.data["current_marker"] == 4 else ww.rb_current_up.setChecked(True) if \
                self.data["current_marker"] == 5 else ww.rb_current_right.setChecked(True) if \
                self.data["current_marker"] == 6 else ww.rb_current_down.setChecked(True) if \
                self.data["current_marker"] == 7 else ww.rb_current_none.setChecked(True) if \
                self.data["current_marker"] == 8 else ww.rb_current_custom.setChecked(True)
            
            ww.rb_previous_o.setChecked(True) if self.data["previous_marker"] == 0 else ww.rb_previous_x.setChecked(
                True) if self.data["previous_marker"] == 1 else ww.rb_previous_star.setChecked(True) if \
                self.data["previous_marker"] == 2 else ww.rb_previous_plus.setChecked(True) if \
                self.data["previous_marker"] == 3 else ww.rb_previous_left.setChecked(True) if \
                self.data["previous_marker"] == 4 else ww.rb_previous_up.setChecked(True) if \
                self.data["previous_marker"] == 5 else ww.rb_previous_right.setChecked(True) if \
                self.data["previous_marker"] == 6 else ww.rb_previous_down.setChecked(True) if \
                self.data["previous_marker"] == 7 else ww.rb_previous_none.setChecked(True) if \
                self.data["previous_marker"] == 8 else ww.rb_previous_custom.setChecked(True)
            ww.le_previous_custom.setText(self.data["le_previous_custom"])
            ww.rb_title_left.setChecked(True) if self.data["title_alignment"] == 0 else ww.rb_title_center.setChecked(
                True) if self.data["title_alignment"] == 1 else ww.rb_title_right.setChecked(True)
            ww.rb_legend_text_left.setChecked(True) if self.data["legend_text_alignment"] == 0 else \
                ww.rb_legend_text_center.setChecked(True) if self.data["legend_text_alignment"] == 1 else \
                    ww.rb_legend_text_right.setChecked(True)
            ww.le_output_path.setText(self.__Final)
            self.current_player_data = self.data["player"] if "player" in self.data.keys() else None
            if firstCall:
                self.updatePlayer()
        
        except KeyError:
            pass
        except Exception:
            tr.print_exc()
        self.updateSignalBlock(False)
        
    def setColor(self, in_le):
        """
        Method that verifies if the given color value is valid, if so update QLabel placeholder value and change
        focus
        """
        colors = ['black', 'blue', 'brown', 'cyan', 'darkblue', 'darkcyan', 'darkgray', 'darkgreen', 'darkmagenta',
                  'darkred', 'gray', 'green', 'lightblue', 'lightcyan', 'lightgray', 'lightgreen', 'lightmagenta',
                  'lightred', 'magenta', 'orange', 'red', 'white', 'yellow', "pink", ""]
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
    
    def setPlayerColor(self):
        self.setColor(self.centralWidget.le_player_color)
        
    def setPartyColor(self):
        self.setColor(self.centralWidget.le_party_color)
    
    def setName(self, le_name):
        """
        Method that update player name if a new value was given, then changes focus
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
        
    def setPlayerName(self):
        self.setName(self.centralWidget.le_player_name)
        
    
    def setTitle(self):
        if self.centralWidget.le_image_title.text():
            self.centralWidget.le_image_title.setPlaceholderText(self.centralWidget.le_image_title.text())
            self.centralWidget.le_image_title.setText("")
        self.centralWidget.le_player_name.setFocus()
        self.update_data()
    
    def addEntry(self, entry=None):
        """
        Method that verifies if new alignment entry is valid, if so adds it to the QListWidget
        :param entry: (optional) Overrides new entry value, default is None
        :type entry: str
        """
        alignement = ["LG", "LB", "NG", "NB", "CG", "CB", "LN", "TN", "CN", "LE", "LM", "NE", "NM", "CE", "CM", "L",
                      "N", "T", "C", "G", "B", "E", "M"]
        if not entry:
            entry = self.centralWidget.le_player_entry.text().upper()
        if entry in alignement:
            self.centralWidget.lw_player_entries.addItem(entry)
            self.centralWidget.le_player_entry.clear()
        
        self.update_data()
    
    def delEntry(self):
        """
        Method that deletes the selected entry (or the last if none is selected) of the QListWidget
        """
        if self.centralWidget.lw_player_entries.currentItem():
            self.centralWidget.lw_player_entries.takeItem(self.centralWidget.lw_player_entries.currentRow())
        else:
            self.centralWidget.lw_player_entries.takeItem(self.centralWidget.lw_player_entries.count() - 1)
    
    def clearEntries(self):
        """
        Method that clear all current QListWidget entries
        """
        self.centralWidget.lw_player_entries.clear()
    
    def runGenerateImage(self):
        """
        Method that tries to render the output image of the graph and update the progress bar
        """
        if self.finished:
            self.finished = False
            self.update_data()
            data = self.data
            
            players = data['players']
            line_qual = int(360 * (10 ** np.linspace(-0.5, 3.8, 100)[data["hs_line_quality"]]))
            tasks = 0
            for player in players:
                player = players[player]
                tasks += (max(0, data['sb_first_entry_weight'] - data['sb_rolling_window_size'])) * 2
                tasks += (len(player["Entries"]) - 1) * 2
            self.progressUpdate(True, 0, 10 + tasks + line_qual, 1, 0)
        try:
            self.centralWidget.pb_generate.setEnabled(False)
            self.loop = QThread()
            self.workers = list()
            
            worker = Worker((self.data.copy(), self.__Final, self.__TMP, self.__fontsize))
            
            
            
            worker.moveToThread(self.loop)
            
            worker.finished.connect(self.getGeneratedImage, Qt.QueuedConnection)
            worker.signal.connect(self.progressUpdate, Qt.QueuedConnection)
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
    
    def getGeneratedImage(self):
        self.update()
        self.finished = True
        self.loop.quit()
        time.sleep(0.2)
        self.image = self.__TMP
        self.progressUpdate(fullstop=True)
        self.centralWidget.pb_generate.setEnabled(True)
        self.update()


def compute_time(t):
    """
    Function that convert a given time value into a nice string
    :param t: Time in second
    :type t: float
    :return: Time string
    :rtype: str
    """
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
        p += "{} seconds".format(round(t, 2))
    else:
        p += "{} second".format(round(t, 2))
    return p


class myQLabel(QLabel):
    resized = Signal()
    
    def __init__(self):
        """
        Subclass of QLabel that emit a Signal when resized
        """
        super(myQLabel, self).__init__()
    
    def resizeEvent(self, event):
        """
        Override of the QWidget resizeEvent to add a custom QSignal.emit()
        """
        self.resized.emit()
        super(myQLabel, self).resizeEvent(event)
        

class Worker(QObject):
    signal = Signal()
    finished = Signal()
    def __init__(self, data, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.data = data
        
    @property
    def data(self):
        return self.__data, self.__final_file, self.__temp_file, self.__fontsize
    
    @data.setter
    def data(self, data_list):
        self.__data, self.__final_file, self.__temp_file, self.__fontsize = data_list
    

    def generate_image(self):
        try:
            data, final_file, temp_file, fontsize = self.data
            al = tuple((('LG', 'NG', 'CG'), ('LN', 'TN', 'CN'), ('LE', 'NE', 'CE')))
            plt.close()
            t_start = time.time()
            players = data['players']
            line_qual = int(360 * (10 ** np.linspace(-0.5, 3.8, 100)[data["hs_line_quality"]]))
            
            vis.plot_background(n=line_qual, kwargs=BACKGROUND_KWARGS)
            for i in range(line_qual): #Fixme: Maybe not do that
                self.signal.emit()
            t = data["le_image_title"] if data["chb_image_title"] else False
            alignment = 'left' if data["title_alignment"] == 0 else 'right' if data[
                                                                                   "title_alignment"] == 2 else "center"
            
            pos_y = float(data["hs_legend_v_offset"] / 100.0) * 1.5
            pos_x = data["hs_legend_h_offset"] * 0.015
            stretch = float(data["hs_legend_stretch"] / 40.0)
            
            players_pos = np.array(
                list(
                    zip(
                        np.linspace(pos_x, pos_x, len(players)),
                        np.linspace(pos_y, (pos_y - (stretch * len(players))), len(players)))))
            for player, pos in zip(players.values(), players_pos):
                if len(player["Entries"]) > 0:
                    color = player['Color']
                    
                    a = np.array(player["Entries"])
                    values = list()
                    for i, value in enumerate(a):
                        x = []
                        y = []
                        if len(value) == 2:
                            value = [c for c in value]
                            value = ['T' if v == "N" and i == 0 else v for i, v in enumerate(value)]
                        if len(value) == 1:
                            value = [value]
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
                            y += [np.nan] * (len(x) - len(y))
                        elif len(y) > len(x):
                            x += [np.nan] * (len(y) - len(x))
                        if i == 0:
                            for i in range(max(0, data['sb_first_entry_weight'] - 1)):
                                values += list(zip(x, y))
                        values += list(zip(x, y))
                    df_player = pd.DataFrame(np.array(values), columns=['x', 'y']).fillna(np.array(values).mean())
                    mean_df_normal = df_player.fillna(value=df_player.mean()).rolling(
                        data["sb_rolling_window_size"], min_periods=1).mean().iloc[max(
                        0, data[
                               "sb_rolling_window_size"] - data["sb_first_entry_weight"]):, :]
                    mean_df = vis.map_to_circle(mean_df_normal)
                    
                    mean_df["alpha"] = np.logspace(-0.5, 0, mean_df.shape[0])
                    ha = 'left' if data['legend_text_alignment'] == 0 else "center" if data[
                                                                                           'legend_text_alignment'] \
                                                                                       == 1 \
                        else 'right'
                    s = np.logspace(-1.2, 1.5, mean_df.shape[0]) * math.sqrt((data["hs_scale"]) / 100.0)
                    plt.plot(mean_df['x'], mean_df['y'], color=color, **PLOT_KWARGS)
                    self.signal.emit()
                    
                    prev_markers = ["o", "x", '*', "+", "<", "^", ">", "v", '', '$' + data['le_previous_custom'] + '$']
                    last_markers = ["o", "x", '*', "+", "<", "^", ">", "v", '', '$' + data['le_current_custom'] + '$']
                    
                    kwargs = {"marker": prev_markers[data["previous_marker"]]}
                    for i in range(mean_df.shape[0]):
                        if i == mean_df.shape[0] - 1:
                            kwargs['marker'] = last_markers[data["current_marker"]]
                        row = pd.DataFrame(mean_df.iloc[i, :]).transpose()
                        for a, scale in zip(
                                np.linspace(row['alpha'].values[-1], 0.0, 10) ** 8,
                                np.linspace(s[i], s[i] * 1.1, 4)):
                            kwargs['alpha'] = a
                            kwargs['s'] = scale
                            if i == mean_df.shape[0] - 1:
                                kwargs['marker'] = last_markers[data["current_marker"]]
                                kwargs['s'] = scale * data["hs_current_scale"] / 10.0
                            plt.scatter(data=row, x='x', y='y', color=color, **kwargs)
                        self.signal.emit()
                    first_row = pd.DataFrame(mean_df_normal.iloc[0, :]).transpose()
                    last_row = pd.DataFrame(mean_df_normal.iloc[mean_df_normal.shape[0] - 1, :]).transpose()
                    y = int(round(1 - first_row["y"]))
                    x = int(round(first_row["x"] + 1))
                    y_o = int(round(1 - last_row["y"]))
                    x_o = int(round(last_row["x"] + 1))
                    p_o_al = al[y][x]
                    p_al = al[y_o][x_o]
                    
                    plt.annotate(
                        player["Name"] + ":\n{} -> {}".format(p_o_al, p_al), xy=pos, color=color, ha=ha,
                        va='center', fontsize=fontsize, fontweight='semibold')
            
            vis.plot_foreground(tight=False, kwargs={'title': t, 'alignment': alignment, 'fontsize': fontsize * 1.1})
            self.signal.emit()
            print(compute_time(time.time() - t_start))
            t = temp_file
            title = data['le_image_title'].replace(' ', '_').lower() if data['chb_image_title'] else \
                'party_players_alignment'
            new_title = ''
            for c in title:
                if 'azertyuiopqsdfghjklmwxcvbn123456789_-'.find(c) != -1:
                    new_title += c
                else:
                    new_title += '_'
            title = new_title
            
            ext = ".png" if data['image_format'] < 2 else '.jpg'
            
            f = os.path.join(final_file, title + ext)
            print('Starting saving data')
            im_size = min(data['sb_image_dpi'], 720)
            self.savefig(t, im_size, 'png', q=6, t=True)
            self.signal.emit()
            self.savefig(f)
        except Exception:
            tr.print_exc()
    
    def savefig(self, out, size=None, f=None, t=None, q=None):
        """
        Method that outputs the final version of the image into the output folder
        :param out: fullpath of the output file
        :param size: (optional) size value converted into dpi for the matplotlib.pyplot.savefig method
        :param f: (optional) ['png' or 'jpeg'] override output file format, default is based on user choice data
        :param t: (optional) override output transparency if file format is 'png', default is based on user choice data
        :param q: (optional) [1 <-> 12] override jpeg file quality if file format is 'jpeg', default is based on user
            choice data
        :type out: str
        :type size: int
        :type f: str
        :type t: bool
        :type q: int
        """
        metadata = METADATA
        metadata["Creation Time"] = time.ctime()
        dpi = size / (72 / 100 * 5.) if size else self.__data["sb_image_dpi"] / (72 / 100 * 5.)
        f = f if f else "png" if self.__data["image_format"] < 2 else "jpeg"
        t = t if t else True if self.__data["image_format"] == 1 else False
        q = round(np.linspace(0, 95, 12)[q - 1]) if q else \
            round(np.linspace(0, 95, 12)[self.__data["hs_jpeg_qual"] -1])
        plt.savefig(
            fname=out, dpi=dpi, format=f, transparent=t,
            pil_kwargs={'quality': int(round(q)), "metadata": metadata})
        self.finished.emit()


PATH = __file__.split("__init__")[0]
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
    'Copyright': 'All Right Reserved by Julien Alardot'
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
        win = mainWindow(input("Savefile Name: "))
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
