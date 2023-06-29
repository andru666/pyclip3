# -*- coding: utf-8 -*-
import re, mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

class Scenarii(App):
    global fs
    fs = mod_globals.fontSize
    
    def __init__(self, elm, ecu, command, data):
        self.elm = elm
        self.command = command
        self.ecu = ecu
        self.DOMTree = mod_zip.get_xml_scenario(data)
        self.ScmRoom = self.DOMTree.documentElement
        ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
        self.ScmParam = {}
        self.ScmSet = {}
        super(Scenarii, self).__init__()

    def build(self):
        self.header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1.0, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=self.header))
        root.add_widget(MyLabel(text=self.command.scenario))
        root.add_widget(MyButton(text='SHOW SCEN', on_press=self.show_scen))
        root.add_widget(MyButton(text='CANCEL', on_press=self.stop))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot
    
    def show_scen(self, msg):
        layout_popup = GridLayout(cols=1, spacing=5, padding=fs*0.5, size_hint=(1, None))
        layout_popup.bind(minimum_width=layout_popup.setter('width'), minimum_height=layout_popup.setter('height'))
        layout_popup.add_widget(MyLabel(size_hint=(0.8, None), text=self.command.scenario.split('#')[1], bgcolor=(1, 0, 0, 0.3)))
        for line in self.DOMTree.toprettyxml().splitlines():
            if 'value' in line:
                layout_popup.add_widget(MyLabel(size_hint=(0.8, None), text='', height=fs/8, bgcolor=(1, 1, 0, 0.3)))
                pa = re.compile(r'name=\"(.+)\"value=\"(\w+)\"')
                ma = pa.search(line.strip().replace(' ', ''))
                if ma:
                    p_name = ma.group(1)
                    p_value = ma.group(2)
                    if p_value.isdigit() and p_value in list(mod_globals.language_dict.keys()):
                        p_value = mod_globals.language_dict[p_value]
                    lab = MyLabel(size_hint=(0.8, None), text="%-20s : %s" % ((p_name), (p_value)), halign= 'left')
                    layout_popup.add_widget(lab)
                else:
                    lab = MyLabel(size_hint=(0.8, None), text=str(line.strip()), halign= 'left')
                    layout_popup.add_widget(lab)
        if self.command.scenario.startswith('scen'):
            name_scen_text = (self.command.scenario.split('#')[1].replace('&', '=').split('=')[1] +'_text.xml').lower()
            layout_popup.add_widget(MyLabel(size_hint=(0.8, None), text=name_scen_text, bgcolor=(1, 0, 0, 0.3)))
            for line in mod_zip.get_xml_scenario('scendata/'+ name_scen_text).toprettyxml().splitlines():
                if 'value' in line:
                    layout_popup.add_widget(MyLabel(size_hint=(0.8, None), text='', height=fs/8, bgcolor=(1, 1, 0, 0.3)))
                    pa = re.compile(r'value=\"(\w+)\"name=\"(.+)\"')
                    ma = pa.search(line.strip().replace(' ', ''))
                    pa2 = re.compile(r'name=\"(.+)\"value=\"(\w+)\"')
                    ma2 = pa2.search(line.strip().replace(' ', ''))
                    if ma:
                        p_name = ma.group(2)
                        p_value = ma.group(1)
                        if p_value.isdigit() and p_value in list(mod_globals.language_dict.keys()):
                            p_value = mod_globals.language_dict[p_value]
                        lab = MyLabel(size_hint=(0.8, None), text="%-20s : %s" % ((p_name), (p_value)), halign= 'left')
                        layout_popup.add_widget(lab)
                    elif ma2:
                        p_name = ma2.group(1)
                        p_value = ma2.group(2)
                        if p_value.isdigit() and p_value in list(mod_globals.language_dict.keys()):
                            p_value = mod_globals.language_dict[p_value]
                        lab = MyLabel(size_hint=(0.8, None), text="%-20s : %s" % ((p_name), (p_value)), halign= 'left')
                        layout_popup.add_widget(lab)
                    else:
                        lab = MyLabel(size_hint=(0.8, None), text=str(line.strip()), halign= 'left')
                        layout_popup.add_widget(lab)
        layout_popup.add_widget(MyButton(text='CANCEL', on_press=self.stop))
        root = ScrollView(size_hint=(1, 1), size=(Window.width*0.9, Window.height*0.9))
        root.add_widget(layout_popup)
        popup = MyPopup(title=self.header, content=root, size_hint=(1, 1))
        popup.open()

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, ecu=ecu, command=command, data=data)
    app.run()
