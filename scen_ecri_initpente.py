# -*- coding: utf-8 -*-
import mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from collections import OrderedDict

class Scenarii(App):
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
            else:
                print(11)
        super(Scenarii, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TexteTitre'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TexteConsigne'), font_size=fs*1.5, bgcolor=(1, 0, 0, 0.3)))
        root.add_widget(MyButton(text=self.command.label, font_size=fs*1.5, on_press=self.pupp))
        root.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), font_size=fs*1.5, on_press=self.stop))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot

    def pupp(self, instance):
        cmd = self.ecu.get_ref_cmd(self.ScmParam['Commande1'])
        resVal = self.ScmParam['ParametreCommande1']
        responce = self.ecu.run_cmd(self.ScmParam['Commande1'], resVal)
        codemr, label, value, unit = self.ecu.get_pr(self.ScmParam['ParametreInclinaison'], True)
        key = '%s - %s' % (codemr, label)
        value = '%s %s' % (value, unit)
        layout = GridLayout(cols=1, spacing=5, padding=fs*0.5, size_hint=(1, 1))
        layout_current = BoxLayout(orientation='horizontal', size_hint=(1, 1))
        lb1 = MyLabel(text=key, font_size=fs, size_hint=(0.6, 1), bgcolor=(0, 0, 1, 0.3))
        lb2 = MyLabel(text=value, font_size=fs, size_hint=(0.4, 1), bgcolor=(0, 1, 0, 0.3))
        if lb1.height > lb2.height:
            layout_current.height = lb2.height = lb1.height
        else:
            layout_current.height = lb1.height = lb2.height
        layout_current.add_widget(lb1)
        layout_current.add_widget(lb2)
        layout.add_widget(layout_current)
        layout.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), font_size=fs*1.5, on_press=self.stop, size_hint=(1, None)))
        rootP = ScrollView(size_hint=(1, 1))
        rootP.add_widget(layout)
        if 'NR' not in responce:
            ch = get_message(self.ScmParam, 'TexteProcedureInterompue')
        else:
            ch = get_message(self.ScmParam, 'TexteInitialisationEffectuee')
        
        popup = MyPopup(title='STATUS', content=rootP)
        popup.open()

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
