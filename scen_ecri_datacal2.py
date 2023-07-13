# -*- coding: utf-8 -*-
import mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from collections import OrderedDict
import xml.dom.minidom as et

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
                ScmParams = Set.getElementsByTagName('ScmParam')
                scmParamsDict = OrderedDict()
                for Param in ScmParams:
                    name = Param.getAttribute('name')
                    value = Param.getAttribute('value')
                    scmParamsDict[name] = value
                self.ScmSet[setname] = scmParamsDict
            else:
                print(11)
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
    
    def saveds(self, idents):
        print('test')
        if  not os.path.isfile(self.file_saved):
            self.popup.title = get_message(self.ScmParam, 'MessageBoxTitle2')
            self.label.text = get_message(self.ScmParam, 'Message21')
            self.root.remove_widget(self.yes)
            return
        self.popup.dismiss()
        ty = (et.parse(self.file_saved).documentElement)
        tyScmParams = ty.getElementsByTagName('ScmParam')
        params = {}
        for p in tyScmParams:
            name = p.getAttribute('name')
            value = p.getAttribute('value')
            params[name] = value
        for k, v in self.ScmSet.items():
            if k.startswith('vdiag'):
                print(v['ini1'])
        return
        '''fileRoot = et.Element("ScmRoot")
        fileRoot.text = "\n"
        doom = et.fromstring(mod_zip.get_xml_scenario_et(self.data))
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        lab = MyLabel(text=get_message(self.ScmParam, 'CmdeInProgress'))
        root.add_widget(lab)
        but = MyButton(text=get_message_by_id('16831'), font_size=fs*1.5)
        root.add_widget(but)
        pop = MyPopup(title=get_message(self.ScmParam, 'MessageBoxTitle1'), content=root)
        pop.open()
        but.bind(on_press=pop.dismiss)
        Vdiag = get_message(self.ScmParam, 'Vdiag')
        val_diag = str(self.ecu.get_id(Vdiag, 5))
        if val_diag:
            el = et.Element("ScmParam", name=Vdiag, value=val_diag)
            el.tail = "\n"
            fileRoot.insert(1,el)
        lab.text += str('\n' + Vdiag + ' : ' + val_diag)
        lab.height += fs * 1.2
        
        for child in doom:
            if child.attrib['name'].startswith('Data_Read'):
                val = child.attrib['value']
                ident = self.ecu.get_id(val, 5)
                lab.text += str('\n' + val + ' : ' + ident)
                lab.height += fs * 1.2
                if ident:
                    el = et.Element("ScmParam", name=val, value=str(ident))
                    el.tail = "\n"
                    fileRoot.insert(1,el)
        if len(fileRoot) != int(self.ScmParam['Nb_Data_Read']) + 1:
            pop.title = get_message(self.ScmParam, 'CmdeFinish')
            lab.text = get_message(self.ScmParam, 'Message2')
            return
        tree = et.ElementTree(fileRoot)
        tree.write(self.file_saved)
        MyPopup_close(get_message(self.ScmParam, 'SubTitleScr2'), MyLabel(text=get_message(self.ScmParam, 'Message3'), font_size=fs*1.5))'''




def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
