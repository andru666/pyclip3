#Embedded file name: /build/PyCLIP/android/app/scen_ecri_codevin.py
import os
import sys
import re
import time
import mod_globals
from mod_utils import *
import mod_ecu
import mod_zip
from kivy.uix.widget import Widget
from mod_utils import pyren_encode
from mod_utils import clearScreen
from mod_utils import ASCIITOHEX
from kivy import base
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

fs =  mod_globals.fontSize

class Show_scen():

    def build(self, instance):
        layout_popup = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout_popup.bind(minimum_height=layout_popup.setter('height'))
        for i in range(0, 15):
            btn1 = Button(text=str(i), id=str(i))
            layout_popup.add_widget(btn1)
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        layout_popup.add_widget(Button(text='CANCEL', on_press=self.stop(), size_hint=(1, None), height=80))
        root.add_widget(layout_popup)
        popup = Popup(title='Numbers', content=root, size_hint=(1, 1))
        return popup
    

class Scenarii(App):
    
    def __init__(self, elm, ecu, command, data):
        self.data = data
        self.DOMTree = mod_zip.get_xml_scenario(data)
        self.ScmRoom = self.DOMTree.documentElement
        ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
        self.elm = elm
        self.command = command
        self.ecu = ecu
        self.ScmParam = {}
        self.ScmSet = {}
        super(Scenarii, self).__init__()


    def build(self):
        fs = mod_globals.fontSize
        self.header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1.0, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=self.header))
        root.add_widget(MyLabel(text=self.command.scenario))
        root.add_widget(Button(text='SHOW SCEN', on_press=self.show_scen, size_hint=(1, None), height=80))
        root.add_widget(Button(text='CANCEL', on_press=self.stop, size_hint=(1, None), height=80))
        rot = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5,
         'center_y': 0.5})
        rot.add_widget(root)
        return rot
    
    def show_scen(self, msg):
        layout_popup = GridLayout(cols=1, spacing=5, padding=fs*0.5, size_hint=(1, None))
        layout_popup.bind(minimum_width=layout_popup.setter('width'), minimum_height=layout_popup.setter('height'))
        layout_popup.add_widget(MyLabel(text=self.command.scenario.split('#')[1], bgcolor=(1, 0, 0, 0.3)))
        for line in self.DOMTree.toprettyxml().splitlines():
            if 'value' in line:
                layout_popup.add_widget(MyLabel(text='', height=5, bgcolor=(1, 1, 0, 0.3)))
                pa = re.compile(r'name=\"(.+)\"value=\"(\w+)\"')
                ma = pa.search(line.strip().replace(' ', ''))
                if ma:
                    p_name = ma.group(1)
                    p_value = ma.group(2)
                    if p_value.isdigit() and p_value in list(mod_globals.language_dict.keys()):
                        p_value = mod_globals.language_dict[p_value]
                    lab = MyLabel(text="%-20s : %s" % (pyren_encode(p_name), pyren_encode(p_value)), height=fs*1.5,font_size=fs, halign= 'left')
                    layout_popup.add_widget(lab)
                else:
                    lab = MyLabel(text=str(pyren_encode( line.strip().encode('utf-8', 'ignore').decode('utf-8'))), font_size=fs,  halign= 'left')
                    layout_popup.add_widget(lab)
        if self.command.scenario.startswith('scen'):
            name_scen_text = (self.command.scenario.split('#')[1].replace('&', '=').split('=')[1] +'_text.xml').lower()
            layout_popup.add_widget(MyLabel(text=name_scen_text, bgcolor=(1, 0, 0, 0.3)))
            for line in mod_zip.get_xml_scenario('scendata/'+ name_scen_text).toprettyxml().splitlines():
                if 'value' in line:
                    layout_popup.add_widget(MyLabel(text='', height=5, bgcolor=(1, 1, 0, 0.3)))
                    pa = re.compile(r'value=\"(\w+)\"name=\"(.+)\"')
                    ma = pa.search(line.strip().replace(' ', ''))
                    pa2 = re.compile(r'name=\"(.+)\"value=\"(\w+)\"')
                    ma2 = pa2.search(line.strip().replace(' ', ''))
                    if ma:
                        p_name = ma.group(2)
                        p_value = ma.group(1)
                        if p_value.isdigit() and p_value in list(mod_globals.language_dict.keys()):
                            p_value = mod_globals.language_dict[p_value]
                        lab = MyLabel(text="%-20s : %s" % (pyren_encode(p_name), pyren_encode(p_value)), font_size=fs, halign= 'left')
                        layout_popup.add_widget(lab)
                    elif ma2:
                        p_name = ma2.group(1)
                        p_value = ma2.group(2)
                        if p_value.isdigit() and p_value in list(mod_globals.language_dict.keys()):
                            p_value = mod_globals.language_dict[p_value]
                        lab = MyLabel(text="%-20s : %s" % (pyren_encode(p_name), pyren_encode(p_value)), font_size=fs, halign= 'left')
                        layout_popup.add_widget(lab)
                    else:
                        lab = MyLabel(text=str(pyren_encode( line.strip().encode('utf-8', 'ignore').decode('utf-8'))), font_size=fs,  halign= 'left')
                        layout_popup.add_widget(lab)
        layout_popup.add_widget(Button(text='CANCEL', on_press=self.stop, size_hint=(1, None), height=60))
        root = ScrollView(size_hint=(1, 1), size=(Window.width*0.9, Window.height*0.9))
        root.add_widget(layout_popup)
        popup = Popup(title=self.header, content=root, size_hint=(1, 1))
        popup.open()

    
    def get_message(self, msg):
        if msg in list(self.ScmParam.keys()):
            value = self.ScmParam[msg]
        else:
            value = msg
        if value.isdigit() and value in list(mod_globals.language_dict.keys()):
            value = pyren_encode(mod_globals.language_dict[value])
        return value

    def get_message_by_id(self, id):
        if id.isdigit() and id in list(mod_globals.language_dict.keys()):
            value = pyren_encode(mod_globals.language_dict[id])
        return value

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, ecu=ecu, command=command, data=data)
    app.run()
