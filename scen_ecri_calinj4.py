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
        notv = str('F'*int(self.ScmParam['nbCaractereCode']))
        if notv == '0': notv = 'F'
        header = '[' + self.command.codeMR + '] ' + self.command.label

        root = GridLayout(cols=1, spacing=5, size_hint=(1.0, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'TexteTitre'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'LabelSaisieCode'), bgcolor=(1, 0, 0, 0.8)))
        
        codemr1, label1, value1 = self.ecu.get_id(self.ScmParam['Ident1'], True)
        values1 = '%s : %s' % ((codemr1), (value1))
        root.add_widget(MyLabel(text=(label1), size_hint=(1, None), font_size=fs * 1.5, bgcolor=(0, 1, 1, 0.3)))
        layout_current1 = BoxLayout(orientation='horizontal', size_hint=(1, None))
        lc1_1 = MyLabel(text=get_message(self.ScmParam, 'dat_TitreActuel'), size_hint=(0.4, None), bgcolor=(0, 0, 1, 0.3))
        lc2_1 = MyLabel(text=values1, size_hint=(0.6, None), bgcolor=(0, 1, 0, 0.3))
        if lc2_1.height > lc1_1.height:
            layout_current1.height = lc2_1.height
        else:
            layout_current1.height = lc1_1.height
        layout_current1.add_widget(lc1_1)
        layout_current1.add_widget(lc2_1)
        layout_c1 = BoxLayout(orientation='horizontal',size_hint=(1, None))
        l_c1_1 = MyLabel(text=get_message(self.ScmParam, 'dat_TitreSouhaite'), size_hint=(0.4, None), bgcolor=(1, 0, 0, 0.3))
        layout_c1.add_widget(l_c1_1)
        self.injec1 = TextInput(text=notv, multiline=False, size_hint=(0.6, None), halign = 'center')
        layout_c1.height = self.injec1.height = l_c1_1.height
        layout_c1.add_widget(self.injec1)
        root.add_widget(layout_current1)
        root.add_widget(layout_c1)
        
        codemr2, label2, value2 = self.ecu.get_id(self.ScmParam['Ident2'], True)
        values2 = '%s : %s' % ((codemr2), (value2))
        root.add_widget(MyLabel(text=(label2), size_hint=(1, None), font_size=fs * 1.5, bgcolor=(0, 1, 1, 0.3)))
        layout_current2 = BoxLayout(orientation='horizontal',size_hint=(1, None))
        lc1_2 = MyLabel(text=get_message(self.ScmParam, 'dat_TitreActuel'), size_hint=(0.4, None), bgcolor=(0, 0, 1, 0.3))
        lc2_2 = MyLabel(text=values2, size_hint=(0.6, None), bgcolor=(0, 1, 0, 0.3))
        if lc2_2.height > lc1_2.height:
            layout_current2.height = lc2_2.height
        else:
            layout_current2.height = lc1_2.height
        layout_current2.add_widget(lc1_2)
        layout_current2.add_widget(lc2_2)
        layout_c2 = BoxLayout(orientation='horizontal',size_hint=(1, None))
        l_c1_2 = MyLabel(text=get_message(self.ScmParam, 'dat_TitreSouhaite'), size_hint=(0.4, None), bgcolor=(1, 0, 0, 0.3))
        layout_c2.add_widget(l_c1_2)
        self.injec2 = TextInput(text=notv, multiline=False, size_hint=(0.6, None), halign = 'center', font_size=fs)
        layout_c2.height = self.injec2.height = l_c1_2.height
        layout_c2.add_widget(self.injec2)
        root.add_widget(layout_current2)
        root.add_widget(layout_c2)
        
        codemr3, label3, value3 = self.ecu.get_id(self.ScmParam['Ident3'], True)
        values3 = '%s : %s' % ((codemr3), (value3))
        root.add_widget(MyLabel(text=(label3), size_hint=(1, None), font_size=fs * 1.5, bgcolor=(0, 1, 1, 0.3)))
        layout_current3 = BoxLayout(orientation='horizontal',size_hint=(1, None))
        lc1_3 = MyLabel(text=get_message(self.ScmParam, 'dat_TitreActuel'), size_hint=(0.4, None), bgcolor=(0, 0, 1, 0.3))
        lc2_3 = MyLabel(text=values3, size_hint=(0.6, None), bgcolor=(0, 1, 0, 0.3))
        if lc2_3.height > lc1_3.height:
            layout_current3.height = lc2_3.height
        else:
            layout_current3.height = lc1_3.height
        layout_current3.add_widget(lc1_3)
        layout_current3.add_widget(lc2_3)
        layout_c3 = BoxLayout(orientation='horizontal',size_hint=(1, None))
        l_c1_3 = MyLabel(text=get_message(self.ScmParam, 'dat_TitreSouhaite'), size_hint=(0.4, None), bgcolor=(1, 0, 0, 0.3))
        layout_c3.add_widget(l_c1_3)
        self.injec3 = TextInput(text=notv, multiline=False, size_hint=(0.6, None), halign = 'center', font_size=fs)
        layout_c3.height = self.injec3.height = l_c1_3.height
        layout_c3.add_widget(self.injec3)
        root.add_widget(layout_current3)
        root.add_widget(layout_c3)
        
        codemr4, label4, value4 = self.ecu.get_id(self.ScmParam['Ident4'], True)
        values4 = '%s : %s' % ((codemr4), (value4))
        root.add_widget(MyLabel(text=(label4), size_hint=(1, None), font_size=fs * 1.5, bgcolor=(0, 1, 1, 0.3)))
        layout_current4 = BoxLayout(orientation='horizontal',size_hint=(1, None))
        lc1_4 = MyLabel(text=get_message(self.ScmParam, 'dat_TitreActuel'), size_hint=(0.4, None), bgcolor=(0, 0, 1, 0.3))
        lc2_4 = MyLabel(text=values4, size_hint=(0.6, None), bgcolor=(0, 1, 0, 0.3))
        if lc2_4.height > lc1_4.height:
            layout_current4.height = lc2_4.height
        else:
            layout_current4.height = lc1_4.height
        layout_current4.add_widget(lc1_4)
        layout_current4.add_widget(lc2_4)
        layout_c4 = BoxLayout(orientation='horizontal',size_hint=(1, None))
        l_c1_4 = MyLabel(text=get_message(self.ScmParam, 'dat_TitreSouhaite'), size_hint=(0.4, None), bgcolor=(1, 0, 0, 0.3))
        layout_c4.add_widget(l_c1_4)
        self.injec4 = TextInput(text=notv, multiline=False, size_hint=(0.6, None), halign = 'center', font_size=fs)
        layout_c4.height = self.injec4.height = l_c1_4.height
        layout_c4.add_widget(self.injec4)
        root.add_widget(layout_current4)
        root.add_widget(layout_c4)
        root.add_widget(MyButton(text=get_message(self.ScmParam, 'TexteTitre'), on_press=self.write_inj, size_hint=(1, None)))
        root.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), on_press=self.stop, size_hint=(1, None)))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot

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
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None

        isHEX = int(self.ScmParam['FormatHexadecimal'])
        if isHEX != 0 and isHEX != 1:
            ch = get_message(self.ScmParam, 'Error FormatHexadecimal in scenario xml')
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None

        prmCHAR = self.ScmParam['PermittedCharacters']
        if len(prmCHAR) << 16 and len(prmCHAR) >> 33:
            ch = 'Error PermittedCharacters in scenario xml'
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        
        while not (all (c in prmCHAR for c in ch1.upper())):
            ch = str(get_message(self.ScmParam, 'dat_Cylindre1')) + ' :\n' + str(get_message(self.ScmParam, 'SymbolsErrorCode'))
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        while not (all (c in prmCHAR for c in ch2.upper())):
            ch = str(get_message(self.ScmParam, 'dat_Cylindre2')) + ' :\n' + str(get_message(self.ScmParam, 'SymbolsErrorCode'))
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        while not (all (c in prmCHAR for c in ch3.upper())):
            ch = str(get_message(self.ScmParam, 'dat_Cylindre3')) + ' :\n' + str(get_message(self.ScmParam, 'SymbolsErrorCode'))
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        while not (all (c in prmCHAR for c in ch4.upper())):
            ch = str(get_message(self.ScmParam, 'dat_Cylindre4')) + ' :\n' + str(get_message(self.ScmParam, 'SymbolsErrorCode'))
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        
        if not len(ch1)==nbCC:
            ch = str(get_message(self.ScmParam, 'dat_Cylindre1')) + ' :\n' + str(get_message(self.ScmParam, 'TexteErreurCode').replace('\n', ' '))
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        if not len(ch2)==nbCC:
            ch = get_message(self.ScmParam, 'dat_Cylindre2') + ' :\n' +  get_message(self.ScmParam, 'TexteErreurCode').replace('\n', ' ')
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        if not len(ch3)==nbCC:
            ch = get_message(self.ScmParam, 'dat_Cylindre3') + ' :\n' +  get_message(self.ScmParam, 'TexteErreurCode').replace('\n', ' ')
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        if not len(ch4)==nbCC:
            ch = get_message(self.ScmParam, 'dat_Cylindre4') + ' :\n' +  get_message(self.ScmParam, 'TexteErreurCode').replace('\n', ' ')
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
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
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        
        if isHEX == 1 and not (all (c in prmCHAR for c in chk.upper()) and (len(chk) == nbCC * 4)):
            ch = 'Hexdata check failed.'
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        elif isHEX == 0 and not (all (c in prmCHAR for c in chk.upper()) and (len(chk) == nbCC * 4)) :
            ch = 'ASCII check failed.'
            popup = MyPopup(title=status, content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None
        else:
            ch = get_message(self.ScmParam, 'CommandeTerminee')
            self.ecu.run_cmd(self.ScmParam['Cmde1'], inj_code1)
            self.ecu.run_cmd(self.ScmParam['Cmde2'], inj_code2)
            self.ecu.run_cmd(self.ScmParam['Cmde3'], inj_code3)
            self.ecu.run_cmd(self.ScmParam['Cmde4'], inj_code4)
            popup = MyPopup(title=get_message(self.ScmParam, 'TexteSousTitreCommandeTerminee'), content=MyLabel(text=ch, font_size=fs*2, halign = 'center'), auto_dismiss=True, close=True, size=(Window.size[0]*0.8, Window.size[1]*0.8), size_hint=(None, None))
            popup.open()
            return None

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, ecu=ecu, command=command, data=data)
    app.run()
