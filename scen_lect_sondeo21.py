# -*- coding: utf-8 -*-
import time, mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from kivy.clock import Clock
from collections import OrderedDict
import xml.dom.minidom
import xml.etree.ElementTree as et
from copy import deepcopy

class Scenario(App):
    global fs
    fs = mod_globals.fontSize
    def __init__(self, **kwargs):
        self.data = kwargs['data']
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
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
            name = (Param.getAttribute('name'))
            value = (Param.getAttribute('value'))
            self.ScmParam[name] = value
        
        for Set in ScmSets:
            if len(Set.attributes) >= 1:
                setname = Set.getAttribute('name')
                ScmParams = Set.getElementsByTagName('ScmParam')
                scmParamsDict = OrderedDict()
                for Param in ScmParams:
                    name = (Param.getAttribute('name'))
                    value = (Param.getAttribute('value'))
                    scmParamsDict[name] = value
                self.ScmSet[setname]= scmParamsDict
        
        for ScmList in ScmLists:
            listname = ScmList.getAttribute("name")
            ScmUSets = ScmList.getElementsByTagName("ScmUSet")
         
            ScmUSet = {}
            for Set in ScmUSets:
                ScmParams = Set.getElementsByTagName("ScmParam")
                for Param in ScmParams:
                    name = ( Param.getAttribute("name")    )
                    value = ( Param.getAttribute("value") )            
                    ScmUSet[name] = value
                    
                if listname.lower()=='etats':
                    self.ScmList_Etats.append( deepcopy(ScmUSet) )
                else:
                    self.ScmList_Messages.append( deepcopy(ScmUSet) )
        super(Scenario, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(self.info('TexteInformations', ['TexteContenuInformationsE1', 'TexteContenuInformationsE4', 'TexteProcedureFin']))
        root.add_widget(MyButton(text=get_message(self.ScmParam, 'TexteScenario'), on_press=self.sondeO))
        root.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), on_press=self.stop))
        return root

    def update_timer(self, dt):
        if not self.running:
            return
        hours, minutes, seconds = self.timer()
        try:
            self.label_time.text = get_message(self.ScmParam, '57936')+'   -   %02d:%02d:%02d' % (hours, minutes, seconds)
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
            if self.value1 == (mod_globals.language_dict[m['Valeur']]):
                self.result = ( mod_globals.language_dict[m['Texte']])
        self.popup_O.dismiss()
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        layout.add_widget(MyLabel(text=phase, bgcolor=(1, 1, 0, 0.3)))
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'TexteSousTitre') + ': ' + self.result, bgcolor=(1, 0, 0, 0.3)))
        layout.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), on_press=self.stop))
        self.popup_open(get_message(self.ScmParam, 'TexteCommandeTerminee'), layout, 0.8, 0.8)

    def update_status(self, dt):
        if not self.running:
            return
        self.ecu.elm.clear_cache()
        self.result = ''
        codemr0, label0, self.value0 = self.ecu.get_st(self.ScmParam['EtatComTer'], True)
        self.key0 = '%s - %s' % (codemr0, label0)
        codemr1, label1, self.value1 = self.ecu.get_st(self.ScmParam['EtatResultatTest'], True)
        self.key1 = '%s - %s' % (codemr1, label1)
        self.Phase = get_message(self.ScmParam, '804')+' - '+(self.value0)
        self.phase.text = self.Phase
        rescode = (self.value1)
        self.result = rescode
        self.labels[self.key0].text = self.value0 
        self.labels[self.key1].text = self.value1 
        if self.value0 == get_message_by_id('19532'):
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
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        hours, minutes, seconds = self.timer()
        self.label_time = MyLabel(text='', bgcolor=(1, 1, 0, 0.3))
        layout.add_widget(self.label_time)
        self.phase = MyLabel(text='', bgcolor=(1, 1, 0, 0.3))
        layout.add_widget(self.phase)
        layout.add_widget(self.make_box_params(self.key0, self.value0))
        layout.add_widget(self.make_box_params(self.key1, self.value1))
        layout.add_widget(MyButton(text=get_message_by_id('69'), on_press=self.stopf))
        self.popup_open(get_message(self.ScmParam, 'TexteCommandeEnCours'), layout, 0.9, 0.8)
        if self.need_update:
            self.timer_event = Clock.schedule_once(self.update_timer, 1)
            self.status_event = Clock.schedule_once(self.update_status, 0.1)

    def sonde_o(self, instance):
        self.popup_O.dismiss()
        self.need_update = True
        self.sonde_O()

    def sondeO(self, instance):
        self.layout = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.layout.add_widget(MyLabel(text='', height=fs*0.001, bgcolor=(1, 1, 1, 0.3)))
        for etat in self.ScmList_Etats:
            state_ref = self.ecu.get_ref_st(etat['Index'])
            codemr1, label1, value1 = self.ecu.get_st(etat['Index'], True)
            key1 = '%s - %s' % (codemr1, label1)
            if value1 != mod_globals.language_dict[etat['RefOK']]:
                codemr2, label2, value2 = self.ecu.get_st(etat['Donne1'], True)
                key2 = '%s - %s' % (codemr2, label2)
                self.layout.add_widget(self.make_box_params(key1, value1))
                self.layout.add_widget(MyLabel(text=(mod_globals.language_dict[etat['TexteSortie']]), bgcolor=(1, 0, 1, 0.3)))
                self.layout.add_widget(self.make_box_params(key2, value2))
                self.layout.add_widget(MyLabel(text='', height=fs*0.001, bgcolor=(1, 1, 1, 0.3)))
        self.layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'TexteLancerTest'), bgcolor=(1, 1, 0, 0.3)))
        self.layout.add_widget(self.button_yes_no(True, '4531', self.sonde_o))
        self.popup_open(get_message(self.ScmParam, 'TexteInformations'), self.layout, 0.9, 0.9)

    def button_yes_no(self, no=True, yes=None, Yes=None):
        layout = BoxLayout(orientation='horizontal', spacing=15, size_hint=(1, None))
        if yes: layout.add_widget(MyButton(text=get_message(self.ScmParam, yes), on_press=Yes))
        if no:
            Byt = MyButton(text=get_message_by_id('16870'), on_press=self.stop)
            layout.add_widget(Byt)
            layout.height = Byt.height
        return layout
    
    def popup_open(self, title, message, S1=None, S2=None):
        if S1==None: S1 = Window.size[0]*0.5
        else: S1 = Window.size[0]*S1
        if S2==None: S2 = Window.size[1]*0.5
        else: S2 = Window.size[1]*S2
        root = ScrollView(size_hint=(1, 1))
        root.add_widget(message)
        self.popup_O = Popup(title=title, content=root, size=(S1, S2), size_hint=(None, None))
        self.popup_O.open()

    def make_box_params(self, parameter_name, value):
        glay = BoxLayout(orientation='horizontal', size_hint=(1, None))
        label1 = MyLabelBlue(text=parameter_name, halign='left', size_hint=(0.7, 1), param_name=None)
        label2 = MyLabelGreen(text=value, halign='right', size_hint=(0.3, 1), font_size=fs)
        if label1.height > label2.height:
            glay.height = label1.height
        else:
            glay.height = label2.height
        glay.add_widget(label1)
        glay.add_widget(label2)
        self.labels[parameter_name] = label2
        return glay

    def info(self, info, message):
        root = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=0)
        root.add_widget(MyLabel(text=get_message(self.ScmParam, info), bgcolor=(0.3, 0.3, 0, 0.3)))
        for mess in message:
            lab = MyLabel(text=get_message(self.ScmParam, mess), bgcolor=(1, 0, 0, 0.3))
            layout.height += lab.height
            layout.add_widget(lab)
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(layout)
        root.add_widget(rot)
        return root

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