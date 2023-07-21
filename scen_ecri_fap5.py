# -*- coding: utf-8 -*-
import mod_globals, mod_zip, time
from mod_utils import *
from kivy.app import App
from kivy.clock import Clock
from collections import OrderedDict

class ScrMsg(Screen):
    pass

class Scenarii(App):
    count = 0
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
        
        self.status_event = None
        self.clock_event = None
        self.timer_event = None
        self.running = True
        self.need_update = False
        self.start_regen = False
        
        self.begin_time = 0
        self.ScmParam = {}
        self.ScmSet = {}
        self.labels = {}
        self.paramsLabels = OrderedDict()
        
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

        super(Scenarii, self).__init__()

    def MyButton_screen(self, dat, start=None):
        if start == 1:
            self.begin_time = time.time()
            responce = self.ecu.run_cmd(self. ScmParam['Cmde1'])
        if dat == 'Scr7Msg8':
            self.need_update = True
        self.sm.current = dat

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'SCMTitle'), bgcolor=(1, 0, 1, 0.3)))
        self.layout2 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        
        self.sm = ScreenManager(size_hint=(1, 1))
        
        self.scr2 = ScrMsg(name='Scr2Msg2')
        self.sm.add_widget(self.scr2)
        self.sceen2 = self.sceen('Scr2Msg2', 'Scr3Msg3', 'Informations', None)
        self.scr2.add_widget(self.sceen2)
        
        self.scr3 = ScrMsg(name='Scr3Msg3')
        self.sm.add_widget(self.scr3)
        self.sceen3 = self.sceen('Scr3Msg3', 'Scr4Msg4', 'Informations', 'Scr2Msg2')
        self.scr3.add_widget(self.sceen3)
        
        self.scr4 = ScrMsg(name='Scr4Msg4')
        self.sm.add_widget(self.scr4)
        self.sceen4 = self.sceen('Scr4Msg4', 'Scr5Msg6', 'Informations', 'Scr3Msg3')
        self.scr4.add_widget(self.sceen4)
        
        self.scr5 = ScrMsg(name='Scr5Msg6')
        self.sm.add_widget(self.scr5)
        self.sceen5 = self.sceen('Scr5Msg6', 'Scr6Msg7', 'Informations', 'Scr4Msg4')
        self.scr5.add_widget(self.sceen5)
        
        self.scr6 = ScrMsg(name='Scr6Msg7')
        self.sm.add_widget(self.scr6)
        params = self.get_ecu_values()
        self.status = params[self.ScmParam['State1']]
        if (self.status) != (get_message(self.ScmParam, 'TOURNANT')):
            self.sceen6 = self.sceen('Scr6Msg7', 'Scr7Msg8', 'Informations', 'Scr5Msg6', 2)
        else:
            self.sceen6 = self.sceen('Scr6Msg7', 'Scr7Msg8', 'Informations', 'Scr5Msg6', 1)
        self.scr6.add_widget(self.sceen6)

        self.scr7 = ScrMsg(name='Scr7Msg8')
        self.sm.add_widget(self.scr7)
        
        if (self.status) != (get_message(self.ScmParam, 'TOURNANT')):
            layout_current7 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
            layout_current7.add_widget(MyLabel(text=get_message(self.ScmParam, 'MsgBox_Message'), bgcolor=(1, 0, 0, 0.3)))
            layout_current7.add_widget(self.make_box_params('State1'))
            layout_current7.add_widget(self.make_box_params('Param6'))
            layout_current7.add_widget(self.make_box_params('Param7'))
            self.sceen7 = self.sceen('Scr7Msg8', None, None, None, None)
            layout_current7.add_widget(self.sceen7)
            self.scr7.add_widget(layout_current7)
        else:
            self.scr7.bind(on_enter=self.update)
            self.scr7.add_widget(self.regen())
            
        self.layout2.add_widget(self.sm)
        root.add_widget(self.layout2)
        self.But1 = MyButton(text=get_message_by_id('1053'), on_press=self.finish, font_size=fs*1.5)
        root.add_widget(self.But1)
        return root
    
    def update(self, dt):
        if self.need_update:
            self.timer_event = Clock.schedule_once(self.update_timer, 1)
            self.clock_event = Clock.schedule_once(self.update_values, 0.1)
            self.status_event = Clock.schedule_once(self.update_status, 0.1)
    
    def regen(self):
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        root = GridLayout(cols=1, spacing=5, size_hint=(1, None))
        hours, minutes, seconds = self.timer()
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'TextCommandInProgress'), bgcolor=(0, 1, 1, 0.3)))
        self.label_time = MyLabel(text='', bgcolor=(1, 1, 0, 0.3))
        layout.add_widget(self.label_time)
        self.label_status = MyLabel(text='', bgcolor=(1, 1, 0, 0.3))
        layout.add_widget(self.label_status)
        par1 = self.make_box_params('Param1')
        root.add_widget(par1)
        par2 = self.make_box_params('Param2')
        root.add_widget(par2)
        par3 = self.make_box_params('Param3')
        root.add_widget(par3)
        par4 = self.make_box_params('Param4')
        root.add_widget(par4)
        par5 = self.make_box_params('Param5')
        root.add_widget(par5)
        par6 = self.make_box_params('Param6')
        root.add_widget(par6)
        par7 = self.make_box_params('Param7')
        root.add_widget(par7)
        par8 = self.make_box_params('State1')
        root.add_widget(par8)
        par9 = self.make_box_params('State2')
        root.add_widget(par9)
        par10 = self.make_box_params('State3')
        root.add_widget(par10)
        par11 = self.make_box_params('State4')
        root.add_widget(par11)
        root.height += par1.height + par2.height + par3.height + par4.height + par5.height + par6.height + par7.height + par8.height + par9.height + par10.height + par11.height
        self.MyButton_stop = MyButton(text=get_message(self.ScmParam, '69')+str(' ')+get_message(self.ScmParam, 'SCMTitle'), on_press=self.stop_regen)
        roo = ScrollView(size_hint=(1, 1))
        roo.add_widget(root)
        layout.add_widget(roo)
        layout.add_widget(self.MyButton_stop)
        return layout
    
    def update_timer(self, dt):
        if not self.running:
            return
        hours, minutes, seconds = self.timer()
        try:
            self.label_time.text = get_message_by_id('57936')+'   -   %02d:%02d:%02d' % (hours, minutes, seconds)
        except:
            pass
        self.timer_event = Clock.schedule_once(self.update_timer, 1)
    
    def timer(self):
        current_time = time.time()
        elapsed = int(current_time-self.begin_time)
        minutes, seconds = divmod(elapsed, 60)
        hours, minutes = divmod(minutes, 60)
        return hours, minutes, seconds

    def stop_regen(self, instance=None):
        self.need_update = False
        self.running = False
        responce = self.ecu.run_cmd(self.ScmParam['Cmde2'])
        params = self.get_ecu_values()
        self.rescode = (params[self.ScmParam['State3']])
        layout_popup = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        layout_popup.add_widget(MyLabel(text=(get_message_by_id('804'))+' - '+(self.phase), size_hint=(1, 0.4), bgcolor=(1, 1, 0, 0.3)))
        layout_popup.add_widget(MyLabel(text=(get_message_by_id('23819'))+' :\n '+(self.rescode), size_hint=(1, 0.4), bgcolor=(1, 0, 0, 0.3)))
        layout_popup.add_widget(MyButton(text=get_message(self.ScmParam, 'MsgBox_Button'), size_hint=(1, 0.2), on_press=self.finish))
        popup = MyPopup(title=get_message(self.ScmParam, 'TextCommandFinished'), content=layout_popup)
        popup.open()

    def update_status(self, dt):
        if not self.running:
            return
        self.ecu.elm.clear_cache()
        params = self.get_ecu_values()
        self.etat = (params[self.ScmParam['State2']])
        self.pfe = 0
        if self.etat == get_message(self.ScmParam, 'ETAT1'):
            self.phase = get_message(self.ScmParam, 'Phase1')
            self.pfe = 0
        elif self.etat == get_message(self.ScmParam, 'ETAT2'): 
            self.phase = get_message(self.ScmParam, 'Phase2')
            self.pfe = 0
        elif self.etat == get_message(self.ScmParam, 'ETAT3'): 
            self.phase = get_message(self.ScmParam, 'Phase3')
            self.pfe = 0
        elif self.etat == get_message(self.ScmParam, 'ETAT4'): 
            self.phase = get_message(self.ScmParam, 'Phase4')
            self.pfe = 0
        elif self.etat == get_message(self.ScmParam, 'ETAT5'): 
            self.phase = get_message(self.ScmParam, 'Phase5')
            self.pfe = 1
        elif self.etat == get_message(self.ScmParam, 'ETAT6'): 
            self.phase = get_message(self.ScmParam, 'Phase6')
            self.pfe = 2
        else:  
            self.phase = self.etat
        if self.pfe > 0:
            self.stop_regen()
        self.label_status.text = get_message_by_id('804')+' - ' + (self.phase)
        self.status_event = Clock.schedule_once(self.update_status, 0.1)

    def sceen(self, screen, btn2, informations, btn1, start=None):
        lat = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        if informations:
            lat.add_widget(MyLabel(text=get_message(self.ScmParam, informations), size_hint=(1, None), bgcolor=(1, 0, 0, 0.3)))
        root = ScrollView(size_hint=(1, 1))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, screen), bgcolor=(0, 1, 1, 0.3)))
        lat.add_widget(root)
        if btn1 or btn2:
            layout = BoxLayout(orientation='horizontal', spacing=5, size_hint=(1, None))
        if btn1:
            nbtn1 = MyButton(text=get_message_by_id('6218'), font_size=fs*1.5)
            layout.height = nbtn1.height
            nbtn1.bind(on_press=lambda *args: self.MyButton_screen(btn1))
            layout.add_widget(nbtn1)
        if btn2:
            if start == 1:
                nbtn2 = MyButton(text=get_message_by_id('29116'), font_size=fs*1.5)
                nbtn2.bind(on_press=lambda *args: self.MyButton_screen(btn2, 1))
            elif start == 2:
                nbtn2 = MyButton(text=get_message_by_id('29116'), font_size=fs*1.5)
                nbtn2.bind(on_press=lambda *args: self.MyButton_screen(btn2, 2))
            else:
                nbtn2 = MyButton(text=get_message_by_id('6219'), font_size=fs*1.5)
                nbtn2.bind(on_press=lambda *args: self.MyButton_screen(btn2))
            layout.height = nbtn2.height
            layout.add_widget(nbtn2)
        if btn1 or btn2:
            lat.add_widget(layout)
        return lat
    
    def get_ecu_values(self):
        dct = OrderedDict()
        for name, key in self.ScmParam.items():
            if not key[:1].isdigit():
                if key[:2] == 'PR':
                    codemr, label, value, unit = self.ecu.get_pr(self.ScmParam[name], True)
                    key = '%s - %s' % (codemr, label)
                    value = '%s %s' % (value, unit)
                    dct[codemr] = value
                    self.paramsLabels[codemr] = key
                    self.need_update = True
                if key[:2] == 'ET':
                    codemr, label, value = self.ecu.get_st(self.ScmParam[name], True)
                    key = '%s - %s' % (codemr, label)
                    dct[codemr] = value
                    self.paramsLabels[codemr] = key
                    self.need_update = True
                if key[:2] == 'ID':
                    codemr, label, value = self.ecu.get_id(self.ScmParam[name], True)
                    key = '%s - %s' % (codemr, label)
                    dct[codemr] = str(value).strip()
                    self.paramsLabels[codemr] = key
        return dct
        
    def update_values(self, dt):
        if not self.running:
            return
        self.ecu.elm.clear_cache()
        params = self.get_ecu_values()
        for param, val in params.items():
            try:
                self.labels[param].text = val.strip()
            except:
                continue
        self.clock_event = Clock.schedule_once(self.update_values, 0.1)
    
    def make_box_params(self, parameter_name):
        params = self.get_ecu_values()
        glay = BoxLayout(orientation='horizontal', size_hint=(1, None))
        label1 = MyLabelBlue(text=self.paramsLabels[self.ScmParam[parameter_name]], halign='left', size_hint=(0.65, 1), param_name=parameter_name)
        label2 = MyLabelGreen(text=params[self.ScmParam[parameter_name]], halign='right', size_hint=(0.35, 1))
        if label1.height > label2.height:
            glay.height = label1.height
        else:
            glay.height = label2.height
        glay.add_widget(label1)
        glay.add_widget(label2)
        self.labels[self.ScmParam[parameter_name]] = label2
        return glay
    
    def finish(self, instance):
        self.need_update = False
        self.running = False
        self.stop()

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, ecu=ecu, command=command, data=data)
    app.run()
