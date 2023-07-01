# -*- coding: utf-8 -*-
import mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock

class ScrMsg(Screen):
    pass

class Scenarii(App):
    
    count = 0

    def __init__(self, **kwargs):
        
        self.status_event = None
        self.clock_event = None
        self.timer_event = None
        self.running = True
        self.need_update = False
        self.start_regen = False
        self.begin_time = 0
        self.blue_part_size = 0.75
        DOMTree = mod_zip.get_xml_scenario(kwargs['data'])
        self.ScmRoom = DOMTree.documentElement
        ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.ScmParam = {}
        self.ScmSet = {}
        self.labels = {}
        self.paramsLabels = OrderedDict()
        
        for Param in ScmParams:
            name = pyren_encode(Param.getAttribute('name'))
            value = pyren_encode(Param.getAttribute('value'))
            self.ScmParam[name] = value
        
        for Set in ScmSets:
            try:
                setname = pyren_encode(mod_globals.language_dict[Set.getAttribute('name')])
            except:
                pass
            ScmParams = Set.getElementsByTagName('ScmParam')
            for Param in ScmParams:
                name = pyren_encode(Param.getAttribute('name'))
                value = pyren_encode(Param.getAttribute('value'))
                try:
                    self.ScmSet[setname] = value
                except:
                    pass
                self.ScmParam[name] = value

        super(Scenarii, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.key_handler)

    def key_handler(self, window, keycode1, keycode2, text, modifiers):
        global resizeFont
        if resizeFont:
            return True
        if keycode1 == 45 and mod_globals.fontSize > 10:
            mod_globals.fontSize = mod_globals.fontSize - 1
            resizeFont = True
            if self.clock_event is not None:
                self.clock_event.cancel()
            self.need_update = False
            self.running = False
            self.stop()
            return True
        if keycode1 == 61 and mod_globals.fontSize < 40:
            mod_globals.fontSize = mod_globals.fontSize + 1
            resizeFont = True
            if self.clock_event is not None:
                self.clock_event.cancel()
            self.need_update = False
            self.running = False
            self.stop()
            return True
        return 

    def button_screen(self, dat, start=None):
        if start == 1:
            self.begin_time = time.time()
            responce = self.ecu.run_cmd(self. ScmParam['Cmde1'])
        if dat == 'Scr7Msg8':
            self.need_update = True
        self.sm.current = dat

    def build(self):
        
        fs = mod_globals.fontSize
        header = '[' + self.command.codeMR + '] ' + self.command.label

        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=self.get_message('SCMTitle'), bgcolor=(1, 0, 1, 0.3)))
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
        if pyren_encode(self.status) != (self.get_message('TOURNANT')):
            self.sceen6 = self.sceen('Scr6Msg7', 'Scr7Msg8', 'Informations', 'Scr5Msg6', 2)
        else:
            self.sceen6 = self.sceen('Scr6Msg7', 'Scr7Msg8', 'Informations', 'Scr5Msg6', 1)
        self.scr6.add_widget(self.sceen6)

        self.scr7 = ScrMsg(name='Scr7Msg8')
        self.sm.add_widget(self.scr7)
        
        if pyren_encode(self.status) != (self.get_message('TOURNANT')):
            layout_current7 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
            layout_current7.add_widget(MyLabel(text=self.get_message('MsgBox_Message'), size_hint=(1, 0.2), bgcolor=(1, 0, 0, 0.3)))
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
        root.add_widget(Button(text=self.get_message_by_id('1053'), on_press=self.finish, size_hint=(1, None), height=80))
        root_s = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5,
         'center_y': 0.5})
        root_s.add_widget(root)
        return root_s
    
    def update(self, dt):
        if self.need_update:
            self.timer_event = Clock.schedule_once(self.update_timer, 1)
            self.clock_event = Clock.schedule_once(self.update_values, 0.1)
            self.status_event = Clock.schedule_once(self.update_status, 0.1)
    
    def regen(self):
        layout_current7 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        
        hours, minutes, seconds = self.timer()
        layout_current7.add_widget(MyLabel(text=self.get_message('TextCommandInProgress'), bgcolor=(0, 1, 1, 0.3)))
        self.label_time = MyLabel(text='', bgcolor=(1, 1, 0, 0.3))
        layout_current7.add_widget(self.label_time)
        layout_current7.add_widget(self.phase_status())
        layout_current7.add_widget(self.make_box_params('Param1'))
        layout_current7.add_widget(self.make_box_params('Param2'))
        layout_current7.add_widget(self.make_box_params('Param3'))
        layout_current7.add_widget(self.make_box_params('Param4'))
        layout_current7.add_widget(self.make_box_params('Param5'))
        layout_current7.add_widget(self.make_box_params('Param6'))
        layout_current7.add_widget(self.make_box_params('Param7'))
        layout_current7.add_widget(self.make_box_params('State1'))
        layout_current7.add_widget(self.make_box_params('State2'))
        layout_current7.add_widget(self.make_box_params('State3'))
        layout_current7.add_widget(self.make_box_params('State4'))
        self.button_stop = Button(text=self.get_message('69')+str(' ')+self.get_message('SCMTitle'), on_press=self.stop_regen, size_hint=(1, None), height=80)
        layout_current7.add_widget(self.button_stop)
        return layout_current7
    
    
    def update_timer(self, dt):
        if not self.running:
            return
        hours, minutes, seconds = self.timer()
        try:
            self.label_time.text = self.get_message_by_id('57936')+'   -   %02d:%02d:%02d' % (hours, minutes, seconds)
        except:
            pass
        self.timer_event = Clock.schedule_once(self.update_timer, 1)
    
    def timer(self):
        current_time = time.time()
        elapsed = int(current_time-self.begin_time)
        minutes, seconds = divmod(elapsed, 60)
        hours, minutes = divmod(minutes, 60)
        return hours, minutes, seconds

    def phase_status(self):
        glay = BoxLayout(orientation='horizontal', size_hint=(1, None), height=fs * 2.5)
        self.label_status = MyLabel(text='', bgcolor=(1, 1, 0, 0.3))
        glay.add_widget(self.label_status)
        return glay

    def stop_regen(self, instance=None):
        self.need_update = False
        self.running = False
        responce = self.ecu.run_cmd(self.ScmParam['Cmde2'])
        params = self.get_ecu_values()
        self.rescode = pyren_encode(params[self.ScmParam['State3']])
        self.result = pyren_encode(mod_globals.language_dict[self.ScmSet[self.rescode]])
        layout_popup = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        layout_popup.add_widget(MyLabel(text=(self.get_message_by_id('804'))+' - '+(self.phase), size_hint=(1, 0.2), bgcolor=(1, 1, 0, 0.3)))
        layout_popup.add_widget(MyLabel(text=(self.get_message_by_id('23819'))+' :\n '+(self.result), size_hint=(1, 0.2), bgcolor=(1, 0, 0, 0.3)))
        layout_popup.add_widget(Button(text=self.get_message_by_id('1053'), on_press=self.finish, size_hint=(1, None), height=80))
        popup = Popup(title=self.get_message('TextCommandFinished'), content=layout_popup, size=(500, 500), size_hint=(None, None))

        popup.open()

    def update_status(self, dt):
        if not self.running:
            return
        self.ecu.elm.clear_cache()
        params = self.get_ecu_values()
        self.etat = pyren_encode(params[self.ScmParam['State2']])
        self.pfe = 0
        if self.etat == self.get_message('ETAT1'):
            self.phase = self.get_message('Phase1')
            self.pfe = 0
        elif self.etat == self.get_message('ETAT2'): 
            self.phase = self.get_message('Phase2')
            self.pfe = 0
        elif self.etat == self.get_message('ETAT3'): 
            self.phase = self.get_message('Phase3')
            self.pfe = 0
        elif self.etat == self.get_message('ETAT4'): 
            self.phase = self.get_message('Phase4')
            self.pfe = 0
        elif self.etat == self.get_message('ETAT5'): 
            self.phase = self.get_message('Phase5')
            self.pfe = 1
        elif self.etat == self.get_message('ETAT6'): 
            self.phase = self.get_message('Phase6')
            self.pfe = 2
        else:  
            self.phase = self.etat
        if self.pfe > 0:
            self.stop_regen()
        self.label_status.text = self.get_message_by_id('804')+' - ' + (self.phase)
        self.status_event = Clock.schedule_once(self.update_status, 0.1)

    def sceen(self, screen, btn2, informations, btn1, start=None):
        
        layout_current = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        if informations:
            layout_current.add_widget(MyLabel(text=self.get_message(informations), size_hint=(1, 0.2), bgcolor=(1, 0, 0, 0.3)))
        layout_current.add_widget(MyLabel(text=self.get_message(screen), size_hint=(1, 0.7), bgcolor=(0, 1, 1, 0.3)))
        if btn1 or btn2:
            layout = BoxLayout(orientation='horizontal', spacing=5, size_hint=(1, 0.2))
        if btn1:
            nbtn1 = Button(text=self.get_message_by_id('6218'))
            nbtn1.bind(on_press=lambda *args: self.button_screen(btn1))
            layout.add_widget(nbtn1)
        if btn2:
            if start == 1:
                nbtn2 = Button(text=self.get_message_by_id('29116'))
                nbtn2.bind(on_press=lambda *args: self.button_screen(btn2, 1))
            elif start == 2:
                nbtn2 = Button(text=self.get_message_by_id('29116'))
                nbtn2.bind(on_press=lambda *args: self.button_screen(btn2, 2))
            else:
                nbtn2 = Button(text=self.get_message_by_id('6219'))
                nbtn2.bind(on_press=lambda *args: self.button_screen(btn2))
            layout.add_widget(nbtn2)
        if btn1 or btn2:
            layout_current.add_widget(layout)
        return layout_current
    
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
        glay = BoxLayout(orientation='horizontal', size_hint=(1, None), height=fs * 2.0)
        self.label1 = MyLabelGreen(text=self.paramsLabels[self.ScmParam[parameter_name]], halign='left', valign='top', size_hint=(self.blue_part_size, None), font_size=fs, on_press= lambda *args: self.ecu.addElem(self.paramsLabels[parameter_name].split(' ')[0]), param_name=parameter_name)
        self.label2 = MyLabelBlue(text=params[self.ScmParam[parameter_name]], halign='right', valign='top', size_hint=(1 - self.blue_part_size, 1), font_size=fs)
        glay.add_widget(self.label1)
        glay.add_widget(self.label2)
        self.labels[self.ScmParam[parameter_name]] = self.label2
        return glay

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
    
    def finish(self, instance):
        self.need_update = False
        self.running = False
        self.stop()

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, ecu=ecu, command=command, data=data)
    app.run()
