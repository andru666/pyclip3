#Embedded file name: /build/PyCLIP/android/app/scen_ecri_codevin.py
import os
import sys
import re
import time
import mod_globals
import mod_utils
import mod_ecu
import mod_zip
from mod_utils import *
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle

class Scenarii(App):
    global fs
    fs = mod_globals.fontSize
    def __init__(self, **kwargs):
        
        DOMTree = mod_zip.get_xml_scenario(kwargs['data'])
        self.ScmRoom = DOMTree.documentElement
        ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.ScmParam = {}
        self.ScmSet = {}
        for Param in ScmParams:
            name = pyren_encode(Param.getAttribute('name'))
            value = pyren_encode(Param.getAttribute('value'))
            self.ScmParam[name] = value

        for Set in ScmSets:
            setname = pyren_encode(mod_globals.language_dict[Set.getAttribute('name')])
            ScmParams = Set.getElementsByTagName('ScmParam')
            for Param in ScmParams:
                name = pyren_encode(Param.getAttribute('name'))
                value = pyren_encode(Param.getAttribute('value'))
                self.ScmSet[setname] = value
                self.ScmParam[name] = value
        super(Scenarii, self).__init__()

    def build(self):
        
        notv = str('F'*int(self.ScmParam['nbCaractereCode']))
        if notv == '0': notv = 'F'
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=5, size_hint=(1.0, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=self.get_message('TexteTitre'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=self.get_message('LabelSaisieCode'), bgcolor=(1, 0, 0, 0.8)))
        codemr1, label1, value1 = self.ecu.get_id(self.ScmParam['Injecteur1'], True)
        values1 = '%s : %s' % (pyren_encode(codemr1), pyren_encode(value1))
        root.add_widget(MyLabel(text=pyren_encode(label1), size_hint=(1, None), font_size=fs * 1.5, bgcolor=(0, 1, 1, 0.3)))
        layout_current1 = BoxLayout(orientation='horizontal', size_hint=(1, None))
        layout_current1.add_widget(MyLabel(text=self.get_message('dat_TitreActuel'), size_hint=(0.6, None), bgcolor=(0, 0, 1, 0.3)))
        layout_current1.add_widget(MyLabel(text=values1, size_hint=(0.4, None), bgcolor=(0, 1, 0, 0.3)))
        layout_c1 = BoxLayout(orientation='horizontal', size_hint=(1, None))
        layout_c1.add_widget(MyLabel(text=self.get_message('dat_TitreSouhaite'), size_hint=(0.6, None), bgcolor=(1, 0, 0, 0.3)))
        self.injec1 = TextInput(text=notv, multiline=False, size_hint=(0.4, None), halign = 'center', font_size=fs)
        layout_c1.add_widget(self.injec1)
        root.add_widget(layout_current1)
        root.add_widget(layout_c1)
        codemr2, label2, value2 = self.ecu.get_id(self.ScmParam['Injecteur2'], True)
        values2 = '%s : %s' % (pyren_encode(codemr2), pyren_encode(value2))
        root.add_widget(MyLabel(text=pyren_encode(label2), size_hint=(1, None), font_size=fs * 1.5, bgcolor=(0, 1, 1, 0.3)))
        layout_current2 = BoxLayout(orientation='horizontal', size_hint=(1, None))
        layout_current2.add_widget(MyLabel(text=self.get_message('dat_TitreActuel'), size_hint=(0.6, None), bgcolor=(0, 0, 1, 0.3)))
        layout_current2.add_widget(MyLabel(text=values2, size_hint=(0.4, None), bgcolor=(0, 1, 0, 0.3)))
        layout_c2 = BoxLayout(orientation='horizontal', size_hint=(1, None))
        layout_c2.add_widget(MyLabel(text=self.get_message('dat_TitreSouhaite'), size_hint=(0.6, None), bgcolor=(1, 0, 0, 0.3)))
        self.injec2 = TextInput(text=notv, multiline=False, size_hint=(0.4, None), halign = 'center', font_size=fs)
        layout_c2.add_widget(self.injec2)
        root.add_widget(layout_current2)
        root.add_widget(layout_c2)
        codemr3, label3, value3 = self.ecu.get_id(self.ScmParam['Injecteur3'], True)
        values3 = '%s : %s' % (pyren_encode(codemr3), pyren_encode(value3))
        root.add_widget(MyLabel(text=pyren_encode(label3), size_hint=(1, None), font_size=fs * 1.5, bgcolor=(0, 1, 1, 0.3)))
        layout_current3 = BoxLayout(orientation='horizontal', size_hint=(1, None))
        layout_current3.add_widget(MyLabel(text=self.get_message('dat_TitreActuel'), size_hint=(0.6, None), bgcolor=(0, 0, 1, 0.3)))
        layout_current3.add_widget(MyLabel(text=values3, size_hint=(0.4, None), bgcolor=(0, 1, 0, 0.3)))
        layout_c3 = BoxLayout(orientation='horizontal', size_hint=(1, None))
        layout_c3.add_widget(MyLabel(text=self.get_message('dat_TitreSouhaite'), size_hint=(0.6, None), bgcolor=(1, 0, 0, 0.3)))
        self.injec3 = TextInput(text=notv, multiline=False, size_hint=(0.4, None), halign = 'center', font_size=fs)
        layout_c3.add_widget(self.injec3)
        root.add_widget(layout_current3)
        root.add_widget(layout_c3)
        codemr4, label4, value4 = self.ecu.get_id(self.ScmParam['Injecteur4'], True)
        values4 = '%s : %s' % (pyren_encode(codemr4), pyren_encode(value4))
        root.add_widget(MyLabel(text=pyren_encode(label4), size_hint=(1, None), font_size=fs * 1.5, bgcolor=(0, 1, 1, 0.3)))
        layout_current4 = BoxLayout(orientation='horizontal', size_hint=(1, None))
        layout_current4.add_widget(MyLabel(text=self.get_message('dat_TitreActuel'), size_hint=(0.6, None), bgcolor=(0, 0, 1, 0.3)))
        layout_current4.add_widget(MyLabel(text=values4, size_hint=(0.4, None), bgcolor=(0, 1, 0, 0.3)))
        layout_c4 = BoxLayout(orientation='horizontal', size_hint=(1, None))
        layout_c4.add_widget(MyLabel(text=self.get_message('dat_TitreSouhaite'), size_hint=(0.6, None), bgcolor=(1, 0, 0, 0.3)))
        self.injec4 = TextInput(text=notv, multiline=False, size_hint=(0.4, None), halign = 'center', font_size=fs)
        layout_c4.add_widget(self.injec4)
        root.add_widget(layout_current4)
        root.add_widget(layout_c4)
        root.add_widget(MyLabel(text=self.get_message('ContenuMb'), bgcolor=(1, 0, 0, 0.8)))
        root.add_widget(MyButton(text=self.get_message('TexteTitre'), on_press=self.write_inj, size_hint=(1, None)))
        root.add_widget(MyButton(text=self.get_message('6218'), on_press=self.stop, size_hint=(1, None)))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot

    def write_inj(self, instance):
        ch1 = self.injec1.text.upper()
        ch2 = self.injec2.text.upper()
        ch3 = self.injec3.text.upper()
        ch4 = self.injec4.text.upper()
        chk = ch1 + ch2 + ch3 + ch4
        
        status = self.get_message('TitreMbPartie2')
        nbCC = int(self.ScmParam['nbCaractereCode'])
        if nbCC !=6 and nbCC !=7 and nbCC !=16:
            ch = 'Error nbCaractereCode in scenario xml'
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None

        isHEX = int(self.ScmParam['FormatHexadecimal'])
        if isHEX != 0 and isHEX != 1:
            ch = self.get_message('Error FormatHexadecimal in scenario xml')
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None

        prmCHAR = self.ScmParam['PermittedCharacters']
        if len(prmCHAR) << 16 and len(prmCHAR) >> 33:
            ch = 'Error PermittedCharacters in scenario xml'
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        
        while not (all (c in prmCHAR for c in ch1.upper())):
            ch = str(self.get_message('dat_Cylindre1')) + ' :\n' + str(self.get_message('SymbolsErrorCode'))
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        while not (all (c in prmCHAR for c in ch2.upper())):
            ch = str(self.get_message('dat_Cylindre2')) + ' :\n' + str(self.get_message('SymbolsErrorCode'))
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        while not (all (c in prmCHAR for c in ch3.upper())):
            ch = str(self.get_message('dat_Cylindre3')) + ' :\n' + str(self.get_message('SymbolsErrorCode'))
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        while not (all (c in prmCHAR for c in ch4.upper())):
            ch = str(self.get_message('dat_Cylindre4')) + ' :\n' + str(self.get_message('SymbolsErrorCode'))
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        
        if not len(ch1)==nbCC:
            ch = str(self.get_message('dat_Cylindre1')) + ' :\n' + str(self.get_message('TexteErreurCode').replace('\n', ' '))
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        if not len(ch2)==nbCC:
            ch = self.get_message('dat_Cylindre2') + ' :\n' +  self.get_message('TexteErreurCode').replace('\n', ' ')
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        if not len(ch3)==nbCC:
            ch = self.get_message('dat_Cylindre3') + ' :\n' +  self.get_message('TexteErreurCode').replace('\n', ' ')
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        if not len(ch4)==nbCC:
            ch = self.get_message('dat_Cylindre4') + ' :\n' +  self.get_message('TexteErreurCode').replace('\n', ' ')
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        
        if isHEX == 1:
            inj_code = chk.upper()
        elif isHEX == 0:
            inj_code = ASCIITOHEX(chk.upper())
        else:
            ch = self.get_message('TexteErreurInit')
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        
        if isHEX == 1 and not (all (c in prmCHAR for c in chk.upper()) and (len(chk) == nbCC * 4)):
            ch = 'Hexdata check failed.'
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        elif isHEX == 0 and not (all (c in prmCHAR for c in chk.upper()) and (len(chk) == nbCC * 4)) :
            ch = 'ASCII check failed.'
            popup = MyPopup(title=status, close=True, content=Label(text=ch, font_size=fs*2, halign  = 'center'), auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        else:
            ch = self.get_message('CommandeTerminee')
            self.ecu.run_cmd(self.ScmParam['EcritureCodeInjecteur'], inj_code)
            popup = MyPopup(title=self.get_message('TexteSousTitreCommandeTerminee'), content=Label(text=ch, font_size=fs*2, halign = 'center'), close=True, auto_dismiss=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None

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
