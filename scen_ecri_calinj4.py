# -*- coding: utf-8 -*-
import mod_globals, mod_zip
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
            name = (Param.getAttribute('name'))
            value = (Param.getAttribute('value'))
            self.ScmParam[name] = value

        for Set in ScmSets:
            setname = (mod_globals.language_dict[Set.getAttribute('name')])
            ScmParams = Set.getElementsByTagName('ScmParam')
            for Param in ScmParams:
                name = (Param.getAttribute('name'))
                value = (Param.getAttribute('value'))
                self.ScmSet[setname] = value
                self.ScmParam[name] = value
        super(Scenarii, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=5, size_hint=(1.0, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TexteTitre'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'LabelSaisieCode'), bgcolor=(1, 0, 0, 0.8)))
        
        self.injec1, inj1 = self.inject_param('Ident1', 'dat_TitreActuel', 'dat_TitreSouhaite')
        self.injec2, inj2 = self.inject_param('Ident2', 'dat_TitreActuel', 'dat_TitreSouhaite')
        self.injec3, inj3 = self.inject_param('Ident3', 'dat_TitreActuel', 'dat_TitreSouhaite')
        self.injec4, inj4 = self.inject_param('Ident4', 'dat_TitreActuel', 'dat_TitreSouhaite')
        
        root.add_widget(inj1)
        root.add_widget(inj2)
        root.add_widget(inj3)
        root.add_widget(inj4)
        
        root.add_widget(MyButton(text=get_message(self.ScmParam, 'TexteTitre'), on_press=self.write_inj, size_hint=(1, None)))
        root.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), on_press=self.stop, size_hint=(1, None)))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot

    def inject_param(self, inj, tit1, tit2):
        notv = str('F'*int(self.ScmParam['nbCaractereCode']))
        if notv == '0': notv = 'F'
        glay = MyGridLayout(cols=1, bgcolor =(0, 0, 0, 1))
        codemr, label, value = self.ecu.get_id(self.ScmParam[inj], True)
        values = '%s : %s' % ((codemr), (value))
        lab = MyLabel(text=label, size_hint=(1, None), bgcolor=(0, 1, 1, 0.3))
        glay.add_widget(lab)
        glay.height = lab.height
        layout_current = BoxLayout(orientation='horizontal', size_hint=(1, None))
        lc1 = MyLabel(text=get_message(self.ScmParam, tit1), size_hint=(0.4, None), bgcolor=(0, 0, 1, 0.3))
        lc2 = MyLabel(text=values, size_hint=(0.6, None), bgcolor=(0, 1, 0, 0.3))
        if lc2.height > lc1.height:
            layout_current.height = lc2.height
        else:
            layout_current.height = lc1.height
        glay.height += layout_current.height
        layout_current.add_widget(lc1)
        layout_current.add_widget(lc2)
        layout_c = BoxLayout(orientation='horizontal', size_hint=(1, None))
        l_c1 = MyLabel(text=get_message(self.ScmParam, tit2), size_hint=(0.4, None), bgcolor=(1, 0, 0, 0.3))
        layout_c.add_widget(l_c1)
        injec = MyTextInput(text=notv, multiline=False, size_hint=(0.6, None))
        layout_c.height = injec.height = l_c1.height
        glay.height += layout_c.height
        layout_c.add_widget(injec)
        glay.add_widget(layout_current)
        glay.add_widget(layout_c)
        return injec, glay

    def write_inj(self, instance):
        ch1 = self.injec1.text.upper()
        ch2 = self.injec2.text.upper()
        ch3 = self.injec3.text.upper()
        ch4 = self.injec4.text.upper()
        chk = ch1 + ch2 + ch3 + ch4

        status = get_message(self.ScmParam, 'TitreMbPartie2')
        nbCC = int(self.ScmParam['nbCaractereCode'])
        if nbCC !=6 and nbCC !=7 and nbCC !=16:
            ch = 'Error nbCaractereCode in scenario xml'
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None

        isHEX = int(self.ScmParam['FormatHexadecimal'])
        if isHEX != 0 and isHEX != 1:
            ch = get_message(self.ScmParam, 'Error FormatHexadecimal in scenario xml')
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None

        prmCHAR = self.ScmParam['PermittedCharacters']
        if len(prmCHAR) << 16 and len(prmCHAR) >> 33:
            ch = 'Error PermittedCharacters in scenario xml'
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        
        while not (all (c in prmCHAR for c in ch1.upper())):
            ch = str(get_message(self.ScmParam, 'dat_Cylindre1')) + ' :\n' + str(get_message(self.ScmParam, 'SymbolsErrorCode'))
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        while not (all (c in prmCHAR for c in ch2.upper())):
            ch = str(get_message(self.ScmParam, 'dat_Cylindre2')) + ' :\n' + str(get_message(self.ScmParam, 'SymbolsErrorCode'))
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        while not (all (c in prmCHAR for c in ch3.upper())):
            ch = str(get_message(self.ScmParam, 'dat_Cylindre3')) + ' :\n' + str(get_message(self.ScmParam, 'SymbolsErrorCode'))
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        while not (all (c in prmCHAR for c in ch4.upper())):
            ch = str(get_message(self.ScmParam, 'dat_Cylindre4')) + ' :\n' + str(get_message(self.ScmParam, 'SymbolsErrorCode'))
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        
        if not len(ch1)==nbCC:
            ch = str(get_message(self.ScmParam, 'dat_Cylindre1')) + ' :\n' + str(get_message(self.ScmParam, 'TexteErreurCode').replace('\n', ' '))
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        if not len(ch2)==nbCC:
            ch = get_message(self.ScmParam, 'dat_Cylindre2') + ' :\n' +  get_message(self.ScmParam, 'TexteErreurCode').replace('\n', ' ')
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        if not len(ch3)==nbCC:
            ch = get_message(self.ScmParam, 'dat_Cylindre3') + ' :\n' +  get_message(self.ScmParam, 'TexteErreurCode').replace('\n', ' ')
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        if not len(ch4)==nbCC:
            ch = get_message(self.ScmParam, 'dat_Cylindre4') + ' :\n' +  get_message(self.ScmParam, 'TexteErreurCode').replace('\n', ' ')
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        
        if isHEX == 0:
            inj_code1 = ch1.upper()
            inj_code2 = ch2.upper()
            inj_code3 = ch3.upper()
            inj_code4 = ch4.upper()
            inj_code = chk.upper()
        elif isHEX == 1:
            inj_code1 = ASCIITOHEX(ch1.upper())
            inj_code2 = ASCIITOHEX(ch2.upper())
            inj_code3 = ASCIITOHEX(ch3.upper())
            inj_code4 = ASCIITOHEX(ch4.upper())
            inj_code = ASCIITOHEX(chk.upper())
        else:
            ch = get_message_by_id('23545')
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        
        if isHEX == 1 and not (all (c in prmCHAR for c in chk.upper()) and (len(chk) == nbCC * 4)):
            ch = 'Hexdata check failed.'
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        elif isHEX == 0 and not (all (c in prmCHAR for c in chk.upper()) and (len(chk) == nbCC * 4)) :
            ch = 'ASCII check failed.'
            popup = MyPopup(title=status, close=True, content=MyLabel(text=ch, font_size=fs*1.5, halign='center'))
            popup.open()
            return None
        else:
            ch = get_message(self.ScmParam, 'CommandeTerminee')
            self.ecu.run_cmd(self.ScmParam['Cmde1'], inj_code1)
            self.ecu.run_cmd(self.ScmParam['Cmde2'], inj_code2)
            self.ecu.run_cmd(self.ScmParam['Cmde3'], inj_code3)
            self.ecu.run_cmd(self.ScmParam['Cmde4'], inj_code4)
            popup = MyPopup(title=get_message(self.ScmParam, 'TexteSousTitreCommandeTerminee'), content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), close=True)
            popup.open()
            return None

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, ecu=ecu, command=command, data=data)
    app.run()
