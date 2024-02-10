# -*- coding: utf-8 -*-
import re, mod_globals, mod_zip, mod_ecu_mnemonic, time
from mod_utils import *
from kivy.app import App
from collections import OrderedDict
import xml.etree.ElementTree as et

class Scenarii(App):
    global fs
    fs = mod_globals.fontSize
    def __init__(self, **kwargs):
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.data = kwargs['data']
        DOMTree = mod_zip.get_xml_scenario(self.data)
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
                for Param in ScmParams:
                    name = (Param.getAttribute('name'))
                    value = (Param.getAttribute('value'))
                    self.ScmSet[setname] = value
                    self.ScmParam[name] = value
        self.file_saved = mod_globals.dumps_dir + self.ScmParam['FichierSav']
        super(Scenarii, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1.0, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TextTitre'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'SsTitre0'), bgcolor=(1, 0.5, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'Consigne1'), font_size=fs*1.5, bgcolor=(1, 0, 0, 0.3)))
        root.add_widget(MyButton(text=self.command.label, on_press=self.pupp))
        root.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), on_press=self.stop))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot

    def pupp(self, dt):
        self.root = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        self.label = MyLabel(text=get_message(self.ScmParam, 'Message1'), size_hint=(1, .8), font_size=fs*1.2, bgcolor=(1, 0, 0, 0.3))
        self.root.add_widget(self.label)
        self.yes = MyButton(text=get_message(self.ScmParam, '4531'), font_size=fs*1.5, id='', size_hint=(1, 0.2), on_press=self.saveds)
        self.root.add_widget(self.yes)
        self.popup = MyPopup_close(get_message(self.ScmParam, '2500'), self.root, op=None)
        self.popup.open()

    def saveds(self, idents):
        if not os.path.isfile(self.file_saved):
            self.popup.title = get_message(self.ScmParam, 'SsTitre0')
            self.label.text = get_message(self.ScmParam, 'Err_Consigne3')
            self.root.remove_widget(self.yes)
            return
        tree = et.parse(self.file_saved)
        root = tree.getroot()
        ecri = {}
        lab = MyLabel(text='', font_size=fs*1.5, size_hint=(1, 1))
        self.popup = MyPopup_close(get_message_by_id('804'), lab, op=None)
        self.popup.open()
        for child in root:
            ecri[child.attrib['name']] = child.attrib['value']
        if len(ecri) != int(self.ScmParam['Nb_Donnees_lec']):
            self.popup.title = get_message(self.ScmParam, 'CmdeTerminee')
            lab.text = get_message(self.ScmParam, 'Err_Consigne2')
            return
        for k, v in self.ScmParam.items():
            if k.startswith('Cmde_ecr'):
                time.sleep(int(self.ScmParam['Tempo'])/1000)
                resp = self.ecu.run_cmd(v, ecri[self.ScmParam[k.replace('Cmde_ecr', 'Donnee_lec')]])
                lab.text += resp
                if 'NR' in resp:
                    lab.text = get_message(self.ScmParam, 'CmdeImpossible')
                    break
                    return
        if not 'NR' in lab.text:
            lab.text += get_message(self.ScmParam, 'Err_Consigne5')
        

    def pupp1(self, instance):
        
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
                        ch = missing_data_message + "\n\nPress to exit"
                        MyPopup_close(get_message_by_id('804'), MyLabel(text=ch, font_size=fs*1.5, size_hint=(1, 1)))
                        return
        response = self.ecu.run_cmd(self.ScmParam['Cmde1'], paramsToSend)
        if 'NR' in response:
            ch = get_message(self.ScmParam, 'CommandImpossible')
        else:
            ch = get_message(self.ScmParam, 'CommandFinished')
        MyPopup_close(get_message_by_id('804'), MyLabel(text=ch, font_size=fs*1.5, size_hint=(1, 1)))

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
