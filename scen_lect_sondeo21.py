# -*- coding: utf-8 -*-
import mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


import xml.dom.minidom
import xml.etree.cElementTree as et

class MyLabel(Label):

    def __init__(self, **kwargs):
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor = (0, 0, 0, 0)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'height' not in kwargs:
            fmn = 1.3
            lines = len(self.text.split('\n'))
            simb = len(self.text) / 60
            if lines < simb: lines = simb
            if lines < 7: lines = 7
            if lines > 20: lines = 20
            if fs > 20: 
                lines = lines * 1.1
                fmn = 1.7
            self.height = fmn * lines * fs
        if 'font_size' not in kwargs:
            self.font_size = fs
        super(MyLabel, self).__init__(**kwargs)
    
    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=self.pos, size=self.size)


class Scenario(App):
    
    def __init__(self, **kwargs):
        
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.data = kwargs['data']
        
        self.blue_part_size = 0.75
        self.status_event = None
        self.clock_event = None
        self.timer_event = None
        self.running = True
        self.need_update = False
        DOMTree = mod_zip.get_xml_scenario(self.data)
        ScmRoom = DOMTree.documentElement
        ScmParams = ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = ScmRoom.getElementsByTagName('ScmSet')
        ScmLists = ScmRoom.getElementsByTagName("ScmList")
        
        self.ScmParam = OrderedDict()
        self.ScmSet = OrderedDict()
        self.labels = {}
        self.ScmList_Etats = []
        self.ScmList_Messages = []
        
        for Param in ScmParams:
            name = pyren_encode(Param.getAttribute('name'))
            value = pyren_encode(Param.getAttribute('value'))
            self.ScmParam[name] = value
        
        for Set in ScmSets:
            if len(Set.attributes) != 1:
                setname = pyren_encode(Set.getAttribute('name'))
                ScmParams = Set.getElementsByTagName('ScmParam')
                scmParamsDict = OrderedDict()
                for Param in ScmParams:
                    name = pyren_encode(Param.getAttribute('name'))
                    value = pyren_encode(Param.getAttribute('value'))
                    scmParamsDict[name] = value
                self.ScmSet[setname]= scmParamsDict
        
        for ScmList in ScmLists:
            listname = ScmList.getAttribute("name")
            ScmUSets = ScmList.getElementsByTagName("ScmUSet")
         
            ScmUSet = {}
            for Set in ScmUSets:
                ScmParams = Set.getElementsByTagName("ScmParam")
                for Param in ScmParams:
                    name = pyren_encode( Param.getAttribute("name")    )
                    value = pyren_encode( Param.getAttribute("value") )            
                    ScmUSet[name] = value
                    
                if listname.lower()=='etats':
                    self.ScmList_Etats.append( deepcopy(ScmUSet) )
                else:
                    self.ScmList_Messages.append( deepcopy(ScmUSet) )
        
        super(Scenario, self).__init__(**kwargs)

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1.0, 1))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(self.info('TexteInformations', ['TexteContenuInformationsE1', 'TexteContenuInformationsE4', 'TexteProcedureFin']))
        root.add_widget(Button(text=self.get_message('TexteScenario'), on_press=self.sondeO, size_hint=(1, None), height=80))
        root.add_widget(Button(text=self.get_message('6218'), on_press=self.stop, size_hint=(1, None), height=80))
        rot = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        rot.add_widget(root)
        return rot

    def update_timer(self, dt):
        if not self.running:
            return
        hours, minutes, seconds = self.timer()
        try:
            self.label_time.text = self.get_message('57936')+'   -   %02d:%02d:%02d' % (hours, minutes, seconds)
        except:
            pass
        self.timer_event = Clock.schedule_once(self.update_timer, 1)

    def timer(self):
        current_time = time.time()
        elapsed = int(current_time-self.begin_time)
        minutes, seconds = divmod(elapsed, 60)
        hours, minutes = divmod(minutes, 60)
        return hours, minutes, seconds

    def phase_stop(self, phase):
        for m in self.ScmList_Messages:
            if self.value1 == pyren_encode(mod_globals.language_dict[m['Valeur']]):
                self.result    = pyren_encode( mod_globals.language_dict[m['Texte']])
        self.popup_O.dismiss()
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        layout.add_widget(MyLabel(text=phase, bgcolor=(1, 1, 0, 0.3)))
        layout.add_widget(MyLabel(text=self.get_message('TexteSousTitre') + ': ' + self.result, bgcolor=(1, 0, 0, 0.3)))
        layout.add_widget(Button(text=self.get_message('6218'), on_press=self.stop, size_hint=(1, None), height=80))
        self.popup_open(self.get_message('TexteCommandeTerminee'), layout, 0.8, 0.8)

    def update_status(self, dt):
        if not self.running:
            return
        self.ecu.elm.clear_cache()
        self.result = ''
        codemr0, label0, self.value0 = self.ecu.get_st(self.ScmParam['EtatComTer'], True)
        self.key0 = '%s - %s' % (codemr0, label0)
        codemr1, label1, self.value1 = self.ecu.get_st(self.ScmParam['EtatResultatTest'], True)
        self.key1 = '%s - %s' % (codemr1, label1)
        self.Phase = self.get_message('804')+' - '+pyren_encode(self.value0)
        self.phase.text = self.Phase
        rescode = pyren_encode(self.value1)
        self.result = rescode
        self.labels[self.key0].text = self.value0 
        self.labels[self.key1].text = self.value1 
        if self.value0 == self.get_message_by_id('19532'):
            
            self.finish()
            self.popup_O.dismiss()
            self.phase_stop(self.Phase)
            return
        self.status_event = Clock.schedule_once(self.update_status, 0.1)

    def sonde_O(self):
        codemr0, label0, self.value0 = self.ecu.get_st(self.ScmParam['EtatComTer'], True)
        self.key0 = '%s - %s' % (codemr0, label0)
        codemr1, label1, self.value1 = self.ecu.get_st(self.ScmParam['EtatResultatTest'], True)
        self.key1 = '%s - %s' % (codemr1, label1)
        responce = self.ecu.run_cmd(self.ScmParam['CommandeTestSonde'])
        self.begin_time = time.time()
        self.pfe = 0
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        hours, minutes, seconds = self.timer()
        self.label_time = MyLabel(text='', bgcolor=(1, 1, 0, 0.3))
        layout.add_widget(self.label_time)
        self.phase = MyLabel(text='', bgcolor=(1, 1, 0, 0.3))
        layout.add_widget(self.phase)
        layout.add_widget(self.make_box_params(self.key0, self.value0))
        layout.add_widget(self.make_box_params(self.key1, self.value1))
        layout.add_widget(Button(text=self.get_message_by_id('16870'), on_press=self.stopf, size_hint=(1, 1), height=fs*4))
        self.popup_open(self.get_message('TexteCommandeEnCours'), layout, 0.9, 0.8)
        if self.need_update:
            self.timer_event = Clock.schedule_once(self.update_timer, 1)
            self.status_event = Clock.schedule_once(self.update_status, 0.1)

    def sonde_o(self, instance):
        self.popup_O.dismiss()
        self.need_update = True
        self.sonde_O()

    def sondeO(self, instance):
        self.layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.layout.add_widget(MyLabel(text='', height=fs*0.001, size_hint=(1, 1), bgcolor=(1, 1, 1, 0.3)))
        for etat in self.ScmList_Etats:
            state_ref = self.ecu.get_ref_st(etat['Index'])
            codemr1, label1, value1 = self.ecu.get_st(etat['Index'], True)
            key1 = '%s - %s' % (codemr1, label1)
            if value1 != pyren_encode( mod_globals.language_dict[etat['RefOK']] ):
                codemr2, label2, value2 = self.ecu.get_st(etat['Donne1'], True)
                key2 = '%s - %s' % (codemr2, label2)
                self.layout.add_widget(self.make_box_params(key1, value1))
                self.layout.add_widget(MyLabel(text=pyren_encode(mod_globals.language_dict[etat['TexteSortie']]), size_hint=(1, 1), bgcolor=(1, 0, 1, 0.3)))
                self.layout.add_widget(self.make_box_params(key2, value2))
                self.layout.add_widget(MyLabel(text='', height=fs*0.001, size_hint=(1, 1), bgcolor=(1, 1, 1, 0.3)))
        self.layout.add_widget(MyLabel(text=self.get_message('TexteLancerTest')))
        self.layout.add_widget(self.button_yes_no(True, '4531', self.sonde_o))
        self.popup_open(self.get_message('TexteInformations'), self.layout, 0.9, 0.9)

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

    def button_yes_no(self, no=True, yes=None, Yes=None):
        layout = BoxLayout(orientation='horizontal', spacing=15, size_hint=(1, 1))
        if yes: layout.add_widget(Button(text=self.get_message(yes), on_press=Yes, size_hint=(1, 1), height=fs*2))
        if no: layout.add_widget(Button(text=self.get_message_by_id('16870'), on_press=self.stop, size_hint=(1, 1), height=fs*4))
        return layout
    
    def popup_open(self, title, message, S1=None, S2=None):
        if S1==None: S1 = Window.size[0]*0.5
        else: S1 = Window.size[0]*S1
        if S2==None: S2 = Window.size[1]*0.5
        else: S2 = Window.size[1]*S2
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        root.add_widget(message)
        self.popup_O = Popup(title=title, content=root, auto_dismiss=True, size=(S1, S2), size_hint=(None, None))
        self.popup_O.open()

    def make_box_params(self, parameter_name, value):
        glay = BoxLayout(orientation='horizontal', size_hint=(1, 1), height=fs * 2.0)
        self.label1 = MyLabelGreen(text=parameter_name, halign='left', valign='top', size_hint=(self.blue_part_size, 1), font_size=fs, param_name=None)
        self.label2 = MyLabelBlue(text=value, halign='right', valign='top', size_hint=(1 - self.blue_part_size, 1), font_size=fs)
        glay.add_widget(self.label1)
        glay.add_widget(self.label2)
        self.labels[parameter_name] = self.label2
        return glay

    def info(self, info, message):
        layout = BoxLayout(orientation='vertical', size_hint=(1, 1))
        layout.add_widget(MyLabel(text=self.get_message(info), size_hint=(1, 1), bgcolor=(0.3, 0.3, 0, 0.3)))
        for mess in message:
            layout.add_widget(MyLabel(text=self.get_message(mess), size_hint=(1, 1), bgcolor=(1, 0, 0, 0.3)))
        return layout

    def finish(self):
        self.need_update = False
        self.running = False

    def stopf(self, instance):
        self.need_update = False
        self.running = False
        self.phase_stop(self.Phase)
        

def run(elm, ecu, command, data):
    app = Scenario(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()