# Alignment Reporter V1.0
# Julien Alardot
import json
import math
import pickle
import time
import traceback as tr

import matplotlib.pyplot as plt
import pandas as pd
from PySide2.QtCore import *
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
# from numba import *
import os
import numpy as np
import Vizualisation as vis
path = __file__.split("UI")[0]
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
    'linewidth'      : 1,
    "alpha"          : 0.2,
    'ms'             : 20,
    'aa'             : True,
    'drawstyle'      : 'steps-pre',
    'solid_capstyle' : 'projecting',
    'solid_joinstyle': 'round',
    'linestyle'      : '--'
    
}

with open(os.path.join(path, "UI", "Qt", "style.css"), "r") as f:
    style = f.read()

icon_path = os.path.join(path, "UI", "Qt")

# TODO: Add "Add Party" option and automatise the Party Player
# class mainWindow(QMainWindow):
#     def __init__(self, *args):
#         super(mainWindow.__init__, (self,) + args)
#
#         loader = QtUiTools.QUiLoader()
#         file = QtCore.QFile("pyside_ui_qtdesigner_form_test.ui")
#         file.open(QtCore.QFile.ReadOnly)
#         self.myWidget = loader.load(file, self)
#         file.close()
#
#         self.setCentralWidget(self.myWidget)

class settingWindow(QMainWindow):
    def __init__(self, parent=None):
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
        self.setMinimumSize(self.centralWidget.minimumSize())
        self.assignWidgets()
        self.setWindowFlags(Qt.Window)
        with open(os.path.join(path, "UI", "Qt", "style.css"), "r") as f:
            self.setStyleSheet(f.read())
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
        # Window setup
        super(mainWindow, self).__init__()
        self.setStyleSheet(style)
        loader = QUiLoader()
        file = QFile(os.path.join(path, "UI", "Qt", "mainWindow.ui"))
        file.open(QFile.ReadOnly)
        self.centralWidget = loader.load(file, self)
        file.close()
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
        Link Widgets to functions
        """
        self.centralWidget.tb_settings.released.connect(self.setUI.show)
        self.centralWidget.pb_save_quit.released.connect(self.close)
        self.centralWidget.pb_set_color.released.connect(self.setPlayerColor)
        self.centralWidget.pb_set_name.released.connect(self.setPlayerName)
        self.centralWidget.pb_set_title.released.connect(self.setTitle)
        self.centralWidget.pb_add_player_entry.released.connect(self.addEntry)
        self.centralWidget.pb_delete_player_entry.released.connect(self.delEntry)
        self.centralWidget.pb_delete_player_all_entries.released.connect(self.clearEntries)
        self.centralWidget.pb_save_player.released.connect(self.savePlayer)
        self.centralWidget.pb_del_player.released.connect(self.delPlayer)
        self.centralWidget.cob_players_select.currentIndexChanged.connect(self.updatePlayer)
        self.centralWidget.pb_generate.released.connect(self.generateImage)
        self.centralWidget.pb_save.released.connect(self.save)
        self.advanced.connect(self.taskAdvance)
    
    def updateSignalBlock(self, state):
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
        self.save()
        self.setUI.close()
        super(mainWindow, self).close()
    
    def show(self):
        try:
            self.load()
            self.image = None
        except FileNotFoundError:
            pass
        super(mainWindow, self).show()
    
    def save(self, j=True):
        self.update_data()
        try:
            with open(self.savefile, 'wb') as f:
                try:
                    pickle.dump(self.data, f)
                except TypeError:
                    print(self.data)
            
            if j:
                with open(self.savefile_json, 'w', encoding="utf-8") as f:
                    json.dump(self.data, f, indent=4, sort_keys=True)
        except Exception:
            tr.print_exc()
    
    def savePlayer(self):
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
        try:
            w = self.centralWidget
            del self.data["players"][w.cob_players_select.currentText()]
            w.cob_players_select.removeItem(w.cob_players_select.currentIndex())
        except KeyError:
            pass
    
    def updatePlayer(self):
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
    
    def taskAdvance(self):
        self.progressUpdate()
    
    def progressUpdate(self, set=False, start=None, stop=None, i=1, current=None):
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
        if bar.value() >= bar.maximum():
            self.centralWidget.f_progress_bar.hide()
    
    @property
    def current_player_data(self):
        pass
    
    @current_player_data.getter
    def current_player_data(self):
        try:
            self.__player_data = {
                "Name"   : self.centralWidget.le_player_name.placeholderText(),
                "Color"  : self.centralWidget.le_player_color.placeholderText(),
                "Entries": [self.centralWidget.lw_player_entries.item(entry).text() for entry in
                            range(self.centralWidget.lw_player_entries.count())]
            }
            return self.__player_data
        except Exception:
            tr.print_exc()
    
    @current_player_data.setter
    def current_player_data(self, data=None):
        if data:
            self.__player_data = data
        w = self.centralWidget
        w.le_player_name.setText("")
        w.le_player_name.setPlaceholderText(self.__player_data["Name"] if 'Name' in self.__player_data.keys() else
                                            "Player Name")
        w.lw_player_entries.clear()
        if "Entries" in self.__player_data.keys():
            for entry in self.__player_data["Entries"]:
                self.addEntry(entry)
        
        w.le_player_color.setText('')
        w.le_player_color.setPlaceholderText(self.__player_data["Color"] if 'Color' in self.__player_data.keys() else
                                             "Black")
    
    def load(self, j=True):
        with open(self.savefile, 'rb') as f:
            try:
                self.data = pickle.load(f)
            except EOFError:
                tr.print_exc()
        if j:
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
        return self.__data
    
    @data.setter
    def data(self, data):
        self.__data = data.copy()
    
    @property
    def image(self):
        pass
    
    @image.getter
    def image(self):
        return None
    
    @image.setter
    def image(self, img=None):
        # self.update_data()
        try:
            f = self.__TMP
            if not img:
                line_qual = int(360 * (10 ** np.linspace(-0.5, 3.8, 100)[self.data["hs_line_quality"]]))
                try:
                    vis.plot_background(n=line_qual, kwargs=AlignmentReporter.BACKGROUND_KWARGS)
                except NameError:
                    vis.plot_background(n=line_qual, kwargs=BACKGROUND_KWARGS)
                
                t = self.data["le_image_title"] if self.data["chb_image_title"] else False
                alignment = 'left' if self.data["title_alignment"] == 0 else 'right' if self.data[
                                                                                            "title_alignment"] == 2 \
                    else "center"
                vis.plot_foreground(tight=False, kwargs={'title': t, 'alignment': alignment, 'fontsize':
                    self.__fontsize * 1.1})
                self.savefig(f, min(self.data['sb_image_dpi'], 100), "png", q=6, t=True)
            self.centralWidget.l_image.setPixmap(QPixmap(f).scaled(np.array(self.centralWidget.l_image.size()) * 1,
                                                                   mode=Qt.SmoothTransformation,
                                                                   aspectMode=Qt.KeepAspectRatio))
        except KeyError:
            pass
    
    def resizeImage(self):
        self.centralWidget.l_image.setPixmap(QPixmap(self.__TMP).scaled(self.centralWidget.l_image.size() * 1,
                                                                        mode=Qt.SmoothTransformation,
                                                                        aspectMode=Qt.KeepAspectRatio))
    
    def savefig(self, out, dpi=None, f=None, t=None, q=None):
        self.update_data()
        try:
            metadata = AlignmentReporter.METADATA
        except NameError:
            metadata = METADATA
        metadata["Creation Time"] = time.ctime()
        dpi = dpi if dpi else self.data["sb_image_dpi"]
        f = f if f else "png" if self.data["image_format"] < 2 else "jpeg"
        t = t if t else True if self.data["image_format"] == 1 else False
        q = round(np.linspace(0, 95, 12)[q - 1]) if q else round(
                np.linspace(0, 95, 12)[self.data["hs_jpeg_qual"] - 1])
        
        plt.savefig(fname=out, dpi=dpi, format=f, transparent=t,
                    pil_kwargs={'quality': int(round(q)), "metadata": metadata})
    
    def update_data(self):
        try:
            data = dict()
            w = self.centralWidget
            ww = self.settingsUI.centralWidget
            data['chb_image_title'] = w.chb_image_title.isChecked()
            data['le_image_title'] = w.le_image_title.placeholderText()
            data["sb_first_entry_weight"] = w.sb_first_entry_weight.value()
            data["sb_rolling_window_size"] = w.sb_rolling_window_size.value()
            data["cob_players_select"] = w.cob_players_select.currentIndex()
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
            data["legend_text_alignment"] = 0 if ww.rb_legend_text_left.isChecked() else 1 if \
                ww.rb_legend_text_center.isChecked() else 2
            data["le_current_custom"] = ww.le_current_custom.text()
            data["current_marker"] = 0 if ww.rb_current_o.isChecked() else 1 if ww.rb_current_x.isChecked() else 2 if \
                ww.rb_current_star.isChecked() else 3 if ww.rb_current_plus.isChecked() else 4 if \
                ww.rb_current_left.isChecked() else 5 if ww.rb_current_up.isChecked() else 6 if \
                ww.rb_current_right.isChecked() else 7 if ww.rb_current_down.isChecked() else 8 if \
                ww.rb_current_none.isChecked() else 9
            data["le_previous_custom"] = ww.le_previous_custom.text()
            data["previous_marker"] = 0 if ww.rb_previous_o.isChecked() else 1 if ww.rb_previous_x.isChecked() else 2 if \
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
        except Exception:
            tr.print_exc()
    
    def update_ui(self, firstCall=False):
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
            w.le_image_title.setPlaceholderText(self.data["le_image_title"] if self.data["le_image_title"] else
                                                "Party Players Alignment Chart")
            w.sb_first_entry_weight.setValue(self.data["sb_first_entry_weight"])
            w.sb_rolling_window_size.setValue(self.data["sb_rolling_window_size"])
            
            ww.hs_current_scale.setValue(self.data["hs_current_scale"])
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
            self.current_player_data = self.data["player"] if "player" in self.data.keys() else None
            if firstCall:
                self.updatePlayer()
        
        except KeyError:
            pass
        except Exception:
            tr.print_exc()
        self.updateSignalBlock(False)
    
    def setPlayerColor(self):
        colors = ['black', 'blue', 'brown', 'cyan', 'darkblue', 'darkcyan', 'darkgray', 'darkgreen', 'darkmagenta',
                  'darkred', 'gray', 'green', 'lightblue', 'lightcyan', 'lightgray', 'lightgreen', 'lightmagenta',
                  'lightred', 'magenta', 'orange', 'red', 'white', 'yellow', "pink", ""]
        if self.centralWidget.le_player_color.text().lower() in colors:
            if self.centralWidget.le_player_color.text():
                self.centralWidget.le_player_color.setPlaceholderText(
                        self.centralWidget.le_player_color.text().capitalize())
                self.centralWidget.le_player_color.setText("")
            self.centralWidget.le_player_entry.setFocus()
        self.update_data()
    
    def setPlayerName(self):
        if self.centralWidget.le_player_name.text():
            self.centralWidget.le_player_name.setPlaceholderText(self.centralWidget.le_player_name.text())
            self.centralWidget.le_player_name.setText("")
        self.centralWidget.le_player_color.setFocus()
        self.update_data()
    
    def setTitle(self):
        if self.centralWidget.le_image_title.text():
            self.centralWidget.le_image_title.setPlaceholderText(self.centralWidget.le_image_title.text())
            self.centralWidget.le_image_title.setText("")
        self.centralWidget.le_player_name.setFocus()
        self.update_data()
    
    def addEntry(self, entry=None):
        alignement = ["LG", "LB", "NG", "NB", "CG", "CB", "LN", "TN", "CN", "LE", "LM", "NE", "NM", "CE", "CM", "L",
                      "N", "T", "C", "G", "B", "E", "M"]
        if not entry:
            entry = self.centralWidget.le_player_entry.text().upper()
        if entry in alignement:
            self.centralWidget.lw_player_entries.addItem(entry)
            self.centralWidget.le_player_entry.clear()
        
        self.update_data()
    
    def delEntry(self):
        if self.centralWidget.lw_player_entries.currentItem():
            self.centralWidget.lw_player_entries.takeItem(self.centralWidget.lw_player_entries.currentRow())
        else:
            self.centralWidget.lw_player_entries.takeItem(self.centralWidget.lw_player_entries.count() - 1)
    
    def clearEntries(self):
        self.centralWidget.lw_player_entries.clear()
    
    def generateImage(self):
        try:
            plt.close()
            self.update_data()
            t_start = time.time()
            al = tuple((('LG', 'NG', 'CG'), ('LN', 'TN', 'CN'), ('LE', 'NE', 'CE')))
            
            players = self.data['players']
            line_qual = int(360 * (10 ** np.linspace(-0.5, 3.8, 100)[self.data["hs_line_quality"]]))
            tasks = 0
            for player in players:
                player = players[player]
                tasks += (max(0, self.data['sb_first_entry_weight'] - self.data['sb_rolling_window_size'])) * 2
                tasks += (len(player["Entries"]) - 1) * 2
            
            self.progressUpdate(True, 0, 10 + tasks + line_qual, 1, 0)
            try:
                vis.plot_background(n=line_qual, kwargs=AlignmentReporter.BACKGROUND_KWARGS)
            except NameError:
                vis.plot_background(n=line_qual, kwargs=BACKGROUND_KWARGS)
            for i in range(line_qual):
                self.advanced.emit()
            t = self.data["le_image_title"] if self.data["chb_image_title"] else False
            alignment = 'left' if self.data["title_alignment"] == 0 else 'right' if self.data["title_alignment"] == 2 \
                else "center"
            
            pos_y = float(self.data["hs_legend_v_offset"] / 100.0) * 1.5
            pos_x = self.data["hs_legend_h_offset"] * 0.015
            stretch = float(self.data["hs_legend_stretch"] / 40.0)
            
            players_pos = np.array(list(zip(np.linspace(pos_x, pos_x, len(players)),
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
                            for i in range(max(0, self.data['sb_first_entry_weight'] - 1)):
                                values += list(zip(x, y))
                        values += list(zip(x, y))
                    
                    df_player = pd.DataFrame(np.array(values), columns=['x', 'y']).fillna(np.array(values).mean())
                    mean_df_normal = df_player.fillna(value=df_player.mean()).rolling(self.data[
                                                                                          "sb_rolling_window_size"],
                                                                                      min_periods=1).mean().iloc[
                                     max(0, self.data["sb_rolling_window_size"] - self.data["sb_first_entry_weight"]):,
                                     :]
                    mean_df = vis.square_root(mean_df_normal)
                    
                    mean_df["alpha"] = np.logspace(-0.5, 0, mean_df.shape[0])
                    ha = 'left' if self.data['legend_text_alignment'] == 0 else "center" \
                        if self.data['legend_text_alignment'] == 1 else 'right'
                    s = np.logspace(-1.2, 1.5, mean_df.shape[0]) * math.sqrt((self.data["hs_scale"]) / 100.0)
                    try:
                        plt.plot(mean_df['x'], mean_df['y'], color=color, **AlignmentReporter.PLOT_KWARGS)
                    except Exception:
                        plt.plot(mean_df['x'], mean_df['y'], color=color, **PLOT_KWARGS)
                    self.advanced.emit()
                    
                    prev_markers = ["o", "x", '*', "+", "<", "^", ">", "v", '',
                                    '$' + self.data['le_previous_custom'] + '$']
                    last_markers = ["o", "x", '*', "+", "<", "^", ">", "v", '',
                                    '$' + self.data['le_current_custom'] + '$']
                    
                    kwargs = {"marker": prev_markers[self.data["previous_marker"]]}
                    for i in range(mean_df.shape[0]):
                        if i == mean_df.shape[0] - 1:
                            kwargs['marker'] = last_markers[self.data["current_marker"]]
                        row = pd.DataFrame(mean_df.iloc[i, :]).transpose()
                        for a, scale in zip(np.linspace(row['alpha'].values[-1], 0.0, 10) ** 8,
                                            np.linspace(s[i], s[i] * 1.1, 4)):
                            kwargs['alpha'] = a
                            kwargs['s'] = scale
                            if i == mean_df.shape[0] - 1:
                                kwargs['marker'] = last_markers[self.data["current_marker"]]
                                kwargs['s'] = scale * self.data["hs_current_scale"] / 10.0
                            plt.scatter(data=row, x='x', y='y', color=color, **kwargs)
                        self.advanced.emit()
                        self.advanced.emit()
                        self.update()
                    first_row = pd.DataFrame(mean_df_normal.iloc[0, :]).transpose()
                    last_row = pd.DataFrame(mean_df_normal.iloc[mean_df_normal.shape[0] - 1, :]).transpose()
                    y = int(round(1 - first_row["y"]))
                    x = int(round(first_row["x"] + 1))
                    y_o = int(round(1 - last_row["y"]))
                    x_o = int(round(last_row["x"] + 1))
                    p_o_al = al[y][x]
                    p_al = al[y_o][x_o]
                    # p_o_al = al[1 - int(round(first_row["y"][0])),int(round(first_row["x"][0] + 1))]
                    # p_al = al[1 - int(round(last_row["y"][0])),int(round(last_row["x"][0] + 1))]
                    
                    plt.annotate(player["Name"] + ":\n{} -> {}".format(p_o_al, p_al), xy=pos, color=color, ha=ha,
                                 va='center', fontsize=self.__fontsize, fontweight='semibold')
            
            vis.plot_foreground(tight=False, kwargs={'title': t, 'alignment': alignment, 'fontsize':
                self.__fontsize * 1.1})
            self.advanced.emit()
            print(compute_time(time.time() - t_start))
            t = self.__TMP
            title = self.data['le_image_title'].replace(' ', '_').lower() if self.data['chb_image_title'] else \
                'party_players_alignment'
            new_title = ''
            for c in title:
                if 'azertyuiopqsdfghjklmwxcvbn123456789_-'.find(c) != -1:
                    new_title += c
                else:
                    new_title += '_'
            title = new_title
            
            ext = ".png" if self.data['image_format'] < 2 else '.jpg'
            
            f = os.path.join(self.__Final, title + ext)
            print('Starting saving data')
            self.savefig(t, min(self.data['sb_image_dpi'], 100), 'png', q=6, t=True)
            self.advanced.emit()
            self.savefig(f)
            self.advanced.emit()
            self.centralWidget.l_image.resized.emit()
            self.advanced.emit()
            self.advanced.emit()
            self.advanced.emit()
            self.advanced.emit()
            self.advanced.emit()
        except Exception:
            tr.print_exc()


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
        p += "{} seconds".format(round(t, 2))
    else:
        p += "{} second".format(round(t, 2))
    return p


class myQLabel(QLabel):
    resized = Signal()
    
    def __init__(self):
        super(myQLabel, self).__init__()
    
    def resizeEvent(self, event):
        self.resized.emit()
        super(myQLabel, self).resizeEvent(event)


def run(app, win):
    try:
        import sys
        import os
        app = QApplication(sys.argv)
        app.setApplicationName("partyAlignmentChartTool")
        app.setApplicationDisplayName("Party Alignment Chart Tool")
        app.setApplicationVersion("0.1.0")
        app.setOrganizationName("Julien Alardot")
        win = mainWindow()
        win.setFocus()
        app.setWindowIcon(QIcon(os.path.join(path, "UI", "AlignmentTool.icon")))
        app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))
        app.exec_()
    except Exception:
        tr.print_exc()


if __name__ == '__main__':
    try:
        import sys
        import os
        
        app = QApplication(sys.argv)
        app.setApplicationName("partyAlignmentChartTool")
        app.setApplicationDisplayName("Party Alignment Chart Tool")
        app.setApplicationVersion("0.1.0")
        app.setOrganizationName("Julien Alardot")
        win = mainWindow(input("Savefile Name: "))
        win.resize(0, 0)
        win.setFocus()
        app.setWindowIcon(QIcon(os.path.join(AlignmentReporter.PATH, "UI", "AlignmentTool.icon")))
        app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))
        app.exec_()
    except Exception:
        tr.print_exc()

# # Endfile
