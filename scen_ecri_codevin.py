# -*- coding: utf-8 -*-
import mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from collections import OrderedDict

class VinWrite(App):
    global fs
    fs = mod_globals.fontSize
    def __init__(self, **kwargs):
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        DOMTree = mod_zip.get_xml_scenario(kwargs['data'])
        self.ScmRoom = DOMTree.documentElement
        ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
        self.ScmParam = {}
        self.ScmSet = {}
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
            
        super(VinWrite, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        codemr, label, value = self.ecu.get_id(self.ScmParam['identVIN'], True)
        codemr = '%s : %s' % ((codemr), (label))
        self.vin_input = MyTextInput(text='VF', multiline=False, font_size=fs*1.5)
        root = GridLayout(cols=1, spacing=6, size_hint=(1, 1))
        layout_current = BoxLayout(orientation='horizontal', size_hint=(1, None))
        c = MyLabel(text=codemr, size_hint=(0.35, 1), bgcolor=(0, 0, 1, 0.3))
        v = MyLabel(text=value, size_hint=(0.65, 1), bgcolor=(0, 1, 0, 0.3))
        layout_current.add_widget(c)
        layout_current.add_widget(v)
        if c.height > v.height:
            layout_current.height = c.height
        else:
            layout_current.height = v.height
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TextTitre')))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'MessageBox3'), bgcolor=(1, 0, 0, 0.3)))
        root.add_widget(layout_current)
        root.add_widget(self.vin_input)
        root.add_widget(MyButton(text=self.command.label, on_press=self.pupp))
        root.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), on_press=self.stop))
        return root

    def write_vin(self, instance):
        vin = self.vin_input.text.upper()
        if not (len(vin) == 17 and 'I' not in vin and 'O' not in vin):
            MyPopup_close(get_message(self.ScmParam, 'MessageBoxERREUR'), MyLabel(text=get_message(self.ScmParam, 'MessageBox2'), size_hint=(1, 1), font_size=fs*2))
            return None
        vin_crc = hex_VIN_plus_CRC(vin)
        self.ecu.run_cmd(self.ScmParam['ConfigurationName'], vin_crc)
        MyPopup_close(get_message(self.ScmParam, 'MessageBoxAVERTISSEMENT'), MyLabel(text=get_message(self.ScmParam, 'confFin_text'), size_hint=(1, 1), font_size=fs*2))

    def pupp(self, instance):
        layout = GridLayout(cols=1, spacing=5, padding=fs*0.5, size_hint=(1, None))
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'MessageBox3'), bgcolor=(1, 0, 0, 0.3)))
        layout_box = BoxLayout(orientation='horizontal', spacing=25, size_hint=(1, None))
        self.buttons_ok = MyButton(text=get_message(self.ScmParam, 'Bouton1'), on_press=self.write_vin, on_release=lambda *args: self.popup.dismiss())
        layout_box.add_widget(self.buttons_ok)
        layout_box.add_widget(MyButton(text=get_message(self.ScmParam, 'Bouton2'), font_size=fs, on_press=self.stop))
        layout.add_widget(layout_box)
        rootP = ScrollView(size_hint=(1, 1), size=(Window.size[0]*0.9, Window.size[1]*0.9))
        rootP.add_widget(layout)
        status = get_message(self.ScmParam, 'MessageBoxAVERTISSEMENT')
        self.popup = MyPopup(title=status, content=rootP)
        self.popup.open()
        return

def run(elm, ecu, command, data):
    app = VinWrite(elm=elm, ecu=ecu, command=command, data=data)
    app.run()
