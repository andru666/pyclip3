# -*- coding: utf-8 -*-
import mod_globals, mod_zip, time
from datetime import datetime
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
            name = Param.getAttribute('name')
            value = Param.getAttribute('value')
            self.ScmParam[name] = value
        for Set in ScmSets:
            if len(Set.attributes) >= 1:
                setname = Set.getAttribute('name')
                Scm_Set = Set.getElementsByTagName('ScmSet')
                ScmParams = Set.getElementsByTagName('ScmParam')
                scmParamsDict = OrderedDict()
                if Scm_Set:
                    for sets in Scm_Set:
                        setn = sets.getAttribute('name')
                        ScmParamS = sets.getElementsByTagName('ScmParam')
                        scmParamsDict[setn] = OrderedDict()
                        for ParamS in ScmParamS:
                            name = ParamS.getAttribute('name')
                            value = ParamS.getAttribute('value')
                            scmParamsDict[setn][name] = value
                for Param in ScmParams:
                    name = Param.getAttribute('name')
                    value = Param.getAttribute('value')
                    scmParamsDict[name] = value
                self.ScmSet[setname] = scmParamsDict
        self.file_saved = mod_globals.dumps_dir + self.ScmParam['RecordingFile']

        super(Scenarii, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TextTitle'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'Message12'), font_size=fs*1.5, bgcolor=(1, 0, 0, 0.3)))
        root.add_widget(MyButton(text=self.command.label, font_size=fs*1.5, on_press=self.pupp))
        root.add_widget(MyButton(text=get_message_by_id('6218'), font_size=fs*1.5, on_press=self.stop))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot

    def pupp(self, dt):
        self.root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        self.label = MyLabel(text=get_message(self.ScmParam, 'Message11'), size_hint=(1, .8), font_size=fs*1.2, bgcolor=(1, 0, 0, 0.3))
        self.root.add_widget(self.label)
        self.yes = MyButton(text=get_message(self.ScmParam, 'TextTitle'), font_size=fs*1.2, id='Yes', size_hint=(1, 0.2), on_press=self.saveds)
        self.root.add_widget(self.yes)
        self.popup = MyPopup_close(get_message(self.ScmParam, 'MessageBoxTitle1'), self.root, op=None)
        self.popup.open()
    
    def respon(self, dt):
        pass
        
    
    def saveds(self, idents):
        if  not os.path.isfile(self.file_saved):
            self.popup.title = get_message(self.ScmParam, 'MessageBoxTitle2')
            self.label.text = get_message(self.ScmParam, 'Message21')
            self.root.remove_widget(self.yes)
            return
        self.popup.dismiss()
        self.root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        self.label = MyLabel(text=get_message(self.ScmParam, 'CmdeInProgress'), size_hint=(1, .8), font_size=fs*1.2, bgcolor=(1, 0, 0, 0.3))
        self.root.add_widget(self.label)
        tree = et.parse(self.file_saved)
        root = tree.getroot()
        params = {}
        for child in root:
            name = child.attrib['name']
            if name != self.ScmParam['Vdiag']:
                params[name] = child.attrib['value']
            else:
                Vdiag = child.attrib['value']
        self.popup = MyPopup_close(get_message(self.ScmParam, 'MessageBoxTitle1'), self.root, op=None)
        self.popup.open()
        for k, v in self.ScmSet.items():
            if k == 'vdiagGroup' + self.ScmParam['NumDataGroups']:
                for i in range(1, int(v['Num_Commands'])+1):
                    self.cmd = v['Command'+str(i)]
                    self.sends = ''
                    for l in range(int(v['startCommand'+str(i)]), int(v['endCommand'+str(i)])+1):
                        p = params[v['Data_Read'+str(l)]['AgcdRef']]
                        self.sends += p
                    base.EventLoop.idle()
                    time.sleep(int(self.ScmParam['Timer'])/1000)
                    rsp = self.ecu.run_cmd(self.cmd, self.sends)
                    base.EventLoop.idle()
                    self.label.text += '\n' 
                    self.label.text += self.cmd + ' : ' + rsp
                    self.label.text += '\n' 
                    if 'NR' in rsp:
                        self.popup.title = get_message(self.ScmParam, 'CmdeFinish')
                        self.label.text += get_message(self.ScmParam, 'CmdeImpossible')
                    else:
                        self.label.text += get_message(self.ScmParam, 'Message23')
        return
    

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
