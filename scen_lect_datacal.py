# -*- coding: utf-8 -*-
import mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
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
                scmParamsDict = OrderedDict()
                for Param in ScmParams:
                    name = Param.getAttribute('name')
                    value = Param.getAttribute('value')
                    scmParamsDict[name] = value
                self.ScmSet[setname] = scmParamsDict
        self.file_saved = mod_globals.dumps_dir + self.ScmParam['FichierDeSauvegarde']
        super(Scenarii, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TexteTitre'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TexteInformations'), font_size=fs*1.5, bgcolor=(1, 0.5, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TexteInstructions'), font_size=fs*1.5, bgcolor=(1, 0, 0, 0.3)))
        root.add_widget(MyButton(text=self.command.label, font_size=fs*1.5, on_press=self.pupp))
        root.add_widget(MyButton(text=get_message_by_id('6218'), font_size=fs*1.5, on_press=self.stop))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot

    def pupp(self, dt):
        root = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        self.label = MyLabel(text=get_message(self.ScmParam, 'TexteLabel'), size_hint=(1, .8), font_size=fs*1.2, bgcolor=(1, 0, 0, 0.3))
        root.add_widget(self.label)
        self.yes = MyButton(text=get_message(self.ScmParam, 'TexteOui'), font_size=fs*1.5, id='', size_hint=(1, 0.2), on_press=self.saveds)
        root.add_widget(self.yes)
        self.popup = MyPopup_close(get_message(self.ScmParam, 'TexteClip'), root, op=None)
        self.popup.open()
    
    def saveds(self, idents):
        if  os.path.isfile(self.file_saved) and not idents.id:
            self.popup.title = get_message(self.ScmParam, 'TexteAvertissement')
            self.label.text = get_message(self.ScmParam, 'TexteMessageBox')
            idents.id = 'Yes'
            return
        self.popup.dismiss()
        fileRoot = et.Element("ScmRoot")
        fileRoot.text = "\n"
        root = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        lab = MyLabel(text=get_message(self.ScmParam, 'TexteCommandeEnCours'), font_size=fs*1.5, size_hint=(1, 1))
        root.add_widget(lab)
        but = MyButton(text=get_message_by_id('16831'), font_size=fs*1.5)
        root.add_widget(but)
        pop = MyPopup(title=get_message(self.ScmParam, 'MessageBoxTitle1'), content=root)
        pop.open()
        but.bind(on_press=pop.dismiss)
        l = 0
        if 'Vdiag' in self.ScmParam.keys():
            l = 1
            Vdiag = get_message(self.ScmParam, 'Vdiag')
            val_diag = str(self.ecu.get_id(Vdiag, 5))
            if val_diag:
                el = et.Element("ScmParam", name=Vdiag, value=val_diag)
                el.tail = "\n"
                fileRoot.insert(1,el)
            lab.text += str('\n' + Vdiag + ' : ' + val_diag)
            lab.height += fs * 1.2
        
        for k, val in self.ScmParam.items():
            if k.startswith('Donnee_Lec'):
                ident = self.ecu.get_id(val, 5)
                lab.text += str('\n' + val + ' : ' + ident)
                lab.height += fs * 1.2
                if ident:
                    el = et.Element("ScmParam", name=val, value=str(ident))
                    el.tail = "\n"
                    fileRoot.insert(1,el)
        if len(fileRoot) != int(self.ScmParam['NombreDeDonnees']) + l:
            pop.title = get_message(self.ScmParam, 'TexteSousTitre')
            lab.text = get_message(self.ScmParam, 'TexteDefautMemoire')
            return
        pop.dismiss()
        tree = et.ElementTree(fileRoot)
        tree.write(self.file_saved)
        MyPopup_close(get_message(self.ScmParam, 'TexteSousTitre'), MyLabel(text=get_message(self.ScmParam, 'TexteCommandeTerminee'), font_size=fs*1.5, size_hint=(1, 1)))


def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
