# -*- coding: utf-8 -*-
import re, mod_globals, mod_zip, mod_ecu_mnemonic
from mod_utils import *
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

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
            name = pyren_encode(Param.getAttribute('name'))
            value = pyren_encode(Param.getAttribute('value'))
            self.ScmParam[name] = value
        for Set in ScmSets:
            if len(Set.attributes) != 1:
                setname = pyren_encode(mod_globals.language_dict[Set.getAttribute('name')])
                ScmParams = Set.getElementsByTagName('ScmParam')
                for Param in ScmParams:
                    name = pyren_encode(Param.getAttribute('name'))
                    value = pyren_encode(Param.getAttribute('value'))
                    self.ScmSet[setname] = value
                    self.ScmParam[name] = value
        super(Scenarii, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1.0, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'Title'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'Message1'), font_size=fs*1.5, bgcolor=(1, 0, 0, 0.3)))
        root.add_widget(MyButton(text=self.command.label, on_press=self.pupp))
        root.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), on_press=self.stop))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot

    def pupp(self, instance):
        
        mnemonics = self.ecu.get_ref_id(self.ScmParam['default']).mnemolist

        if mnemonics[0][-2:] > mnemonics[1][-2:]:
            mnemo1 = mnemonics[1]
            mnemo2 = mnemonics[0]
        else:
            mnemo1 = mnemonics[0]
            mnemo2 = mnemonics[1]
        byteFrom = int(mnemo1[-2:])
        byteTo = int(re.findall('\d+',mnemo2)[1])
        byteCount = byteTo - byteFrom - 1
        resetBytes = byteCount * '00'
        params_to_send_length = int(mnemo2[-2:])
        
        mnemo1Data = mod_ecu_mnemonic.get_mnemonic(self.ecu.Mnemonics[mnemo1], self.ecu.Services, self.elm)
        mnemo2Data = mod_ecu_mnemonic.get_mnemonic(self.ecu.Mnemonics[mnemo2], self.ecu.Services, self.elm)
    
        paramsToSend = mnemo1Data + resetBytes + mnemo2Data
        fap_command_sids = self.ecu.get_ref_cmd(self.ScmParam['Cmde1']).serviceID
        if len(fap_command_sids) and not mod_globals.opt_demo:
            for sid in fap_command_sids:
                if len(self.ecu.Services[sid].params):
                    if (len(self.ecu.Services[sid].startReq + paramsToSend)/2 != params_to_send_length):
                        ch = missing_data_message + "\n\nPress ENTER to exit"
                        popup = MyPopup(title='STATUS', content=MyLabel(text=ch, font_size=fs*1.5, size_hint=(1, 1)), close=True)
                        popup.open()
                        return
        response = self.ecu.run_cmd(self.ScmParam['Cmde1'], paramsToSend)
        if 'NR' in response:
            ch = get_message(self.ScmParam, 'CommandImpossible')
        else:
            ch = get_message(self.ScmParam, 'CommandFinished')
        
        popup = MyPopup(title='STATUS', content=MyLabel(text=ch, font_size=fs*1.5, size_hint=(1, 1)), close=True)
        popup.open()

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
