# -*- coding: utf-8 -*-
import os
import sys
import re
import time
import mod_globals
import mod_ecu
import mod_zip
from mod_utils import *
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from collections import OrderedDict

fs = mod_globals.fontSize
class Scenarii(App):
    
    def __init__(self, **kwargs):
        super(Scenarii, self).__init__()
        self.data = kwargs['data']
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.ScmParam = {}
        self.ScmSet = {}
        if 'ecudata' in self.data:
            sdata = self.data.rsplit('_', 2)[0].replace('ecudata', 'scendata') + '_text.xml'
            dt = self.data.replace('_ecu_', '_const_')
            datas = [sdata, dt, self.data]
        else:
            datas = self.data
        for dat in datas:
            try:
                DOMTree = mod_zip.get_xml_scenario(dat)
            except:
                continue
            self.ScmRoom = DOMTree.documentElement
            ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
            ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
            for Param in ScmParams:
                name = (Param.getAttribute('name'))
                value = (Param.getAttribute('value'))
                self.ScmParam[name] = value
            for Set in ScmSets:
                if len(Set.attributes) >= 1:
                    setname = Set.getAttribute('name')
                    ScmParams = Set.getElementsByTagName('ScmParam')
                    scmParamsDict = OrderedDict()
                    for Param in ScmParams:
                        name = Param.getAttribute('name')
                        value = Param.getAttribute('value')
                        scmParamsDict[name] = value
                    self.ScmSet[setname] = scmParamsDict


    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        root.add_widget(MyLabel(text=header))
        codemr, label, value = self.ecu.get_id(self.ScmParam['pdd_ID-4-8'], True)
        codemr = '%s : %s' % ((codemr), (label))
        self.vin_input = MyTextInput(text='VF', font_size=fs*1.5, multiline=False)
        layout_current = BoxLayout(orientation='horizontal', size_hint=(1, None))
        c = MyLabel(text=codemr, size_hint=(0.35, 1), bgcolor=(0, 0, 1, 0.3))
        v = MyLabel(text=value, size_hint=(0.65, 1), bgcolor=(0, 1, 0, 0.3))
        layout_current.add_widget(c)
        layout_current.add_widget(v)
        if c.height > v.height:
            layout_current.height = c.height
        else:
            layout_current.height = v.height
        root.add_widget(layout_current)
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'text_33975'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(self.vin_input)
        root.add_widget(MyButton(text=self.command.label, on_press=self.pupp))
        root.add_widget(MyButton(text=get_message(self.ScmParam, 'text_CANCEL'), on_press=self.stop))
        return root

    def write_vin(self, instance):
        vin = self.vin_input.text.upper()
        if not (len(vin) == 17 and 'I' not in vin and 'O' not in vin):
            MyPopup_close(get_message(self.ScmParam, 'text_33973'), MyLabel(text=get_message(self.ScmParam, 'text_29121'), size_hint=(1, 1), font_size=fs*1.5))
            return None
        vin_crc = hex_VIN_plus_CRC(vin)
        resp = self.ecu.run_cmd(self.ScmParam['pdd_VP-4-41'], vin_crc)
        label = MyLabel(text=get_message(self.ScmParam, 'text_41453'), size_hint=(1, 1), font_size=fs*1.5)
        label.text += '\n'
        label.text += self.ScmParam['pdd_VP-4-41'] + ':\n'
        label.text += resp
        MyPopup_close(get_message(self.ScmParam, 'text_9234'), label)

    def pupp(self, instance):
        layout = GridLayout(cols=1, spacing=5, padding=fs*0.5, size_hint=(1, None))
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'text_29120'), bgcolor=(1, 0, 0, 0.3)))
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'text_30338'), bgcolor=(1, 1, 1, 0.3)))
        layout_box = BoxLayout(orientation='horizontal', spacing=25, size_hint=(1, None))
        self.buttons_ok = MyButton(text=get_message(self.ScmParam, 'text_OK'), on_press=self.write_vin, on_release=lambda *args: self.popup.dismiss())
        layout_box.add_widget(self.buttons_ok)
        layout_box.add_widget(MyButton(text=get_message(self.ScmParam, 'text_NO'), font_size=fs, on_press=self.stop))
        layout.add_widget(layout_box)
        rootP = ScrollView(size_hint=(1, 1))
        rootP.add_widget(layout)
        status = get_message(self.ScmParam, 'text_33973')
        self.popup = MyPopup(title=status, content=rootP)
        self.popup.open()
        return

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, ecu=ecu, command=command, data=data)
    app.run()