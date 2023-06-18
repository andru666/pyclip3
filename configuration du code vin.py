#Embedded file name: /build/PyCLIP/android/app/scen_ecri_codevin.py
import os
import sys
import re
import time
import mod_globals
import mod_utils
import mod_ecu
import mod_zip
from mod_utils import hex_VIN_plus_CRC
from mod_utils import pyren_encode
from mod_utils import clearScreen
from mod_utils import ASCIITOHEX
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
class MyLabel(Label):

    def __init__(self, **kwargs):
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor = (0, 0, 0, 0)
        super(MyLabel, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'height' not in kwargs:
                 
            fmn = 1.3
            lines = len(self.text.split('\n'))
            simb = len(self.text) / 60
            if lines < simb: lines = simb
            if lines < 7: lines = 7
            if lines > 20: lines = 20
            if 1 > simb: lines = 2
            if fs > 20: 
                lines = lines * 1.05
                fmn = 1.5
            self.height = fmn * lines * fs

    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=self.pos, size=self.size)

class Scenarii(App):
    
    def __init__(self, **kwargs):
        self.data = kwargs['data']
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.ScmParam = {}
        self.ScmSet = {}
        if 'ecudata' in self.data:
            self.sdata = self.data.split('_')[0].replace('ecudata', 'scendata') + '_text.xml'
            datas = [self.sdata, self.data]
        else:
            datas = self.data
        for dat in datas:
            DOMTree = mod_zip.get_xml_scenario(dat)
            self.ScmRoom = DOMTree.documentElement
            ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
            ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
            for Param in ScmParams:
                name = pyren_encode(Param.getAttribute('name'))
                value = pyren_encode(Param.getAttribute('value'))
                self.ScmParam[name] = value
            for Set in ScmSets:
                try:
                    setname = pyren_encode(mod_globals.language_dict[Set.getAttribute('name')])
                except:
                    pass
                ScmParams = Set.getElementsByTagName('ScmParam')
                for Param in ScmParams:
                    name = pyren_encode(Param.getAttribute('name'))
                    value = pyren_encode(Param.getAttribute('value'))
                    try:
                        self.ScmSet[setname] = value
                    except:
                        pass
                    self.ScmParam[name] = value
        super(Scenarii, self).__init__(**kwargs)

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5)
        root.add_widget(MyLabel(text=header))
        codemr, label, value = self.ecu.get_id(self.ScmParam['pdd_ID-4-8'], True)
        codemr = '%s : %s' % (pyren_encode(codemr), pyren_encode(label))
        self.vin_input = TextInput(text='VF', multiline=False, size_hint=(1, None), height=40)
        layout_current = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        layout_current.add_widget(MyLabel(text=codemr, size_hint=(0.3, 1), bgcolor=(0, 0, 1, 0.3)))
        layout_current.add_widget(MyLabel(text=value, size_hint=(0.7, 1), bgcolor=(0, 1, 0, 0.3)))
        root.add_widget(layout_current)
        root.add_widget(MyLabel(text=self.get_message('text_33975'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(self.vin_input)
        root.add_widget(Button(text=self.command.label, on_press=self.pupp, size_hint=(1, None), height=80))
        root.add_widget(Button(text=self.get_message('text_CANCEL'), on_press=self.stop, size_hint=(1, None), height=80))
        return root

    def write_vin(self, instance):
        vin = self.vin_input.text.upper()
        if not (len(vin) == 17 and 'I' not in vin and 'O' not in vin):
            popup_w = Popup(title=self.get_message('text_33973'), content=Label(text=self.get_message('text_29121')), auto_dismiss=True, size=(Window.width*0.7, Window.width*0.8), size_hint=(None, None))
            popup_w.open()
            return None
        vin_crc = hex_VIN_plus_CRC(vin)
        self.ecu.run_cmd(self.ScmParam['pdd_VP-4-41'], vin_crc)
        popup_w = Popup(title=self.get_message('text_9234'), content=Label(text=self.get_message('text_41453')), auto_dismiss=True, size=(Window.width*0.7, Window.width*0.8), size_hint=(None, None))
        popup_w.open()

    def pupp(self, instance):
        layout = GridLayout(cols=1, spacing=5, padding=fs*0.5, size_hint=(1, None))
        layout.add_widget(MyLabel(text=self.get_message('text_29120'), height=Window.width*0.4, bgcolor=(1, 0, 0, 0.3)))
        layout.add_widget(MyLabel(text=self.get_message('text_30338'), bgcolor=(1, 1, 1, 0.3)))
        layout_box = BoxLayout(orientation='horizontal', spacing=25, size_hint=(1, None))
        self.buttons_ok = Button(text=self.get_message('text_OK'), fonte_size=fs, size_hint=(1, None), height=fs*4, on_press=self.write_vin, on_release=lambda *args: self.popup.dismiss())
        layout_box.add_widget(self.buttons_ok)
        layout_box.add_widget(Button(text=self.get_message('text_NO'), fonte_size=fs, on_press=self.stop, size_hint=(1, None), height=fs*4))
        layout.add_widget(layout_box)
        rootP = ScrollView(size_hint=(1, 1), size=(Window.width*0.9, Window.height*0.9))
        rootP.add_widget(layout)
        status = self.get_message('text_33973')
        self.popup = Popup(title=status, content=rootP, auto_dismiss=True, size=(Window.width*0.7, Window.width*0.8), size_hint=(1, None))
        self.popup.open()
        return

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