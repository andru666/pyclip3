# -*- coding: utf-8 -*-
import mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from collections import OrderedDict
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown

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
        self.data = kwargs['data']
        
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
        if 'ecudata' in self.data:
            sdata = self.data.rsplit('_', 2)[0].replace('ecudata', 'scendata') + '_text.xml'
            dt = self.data.replace('_ecu_', '_const_')
            datas = [sdata, dt, self.data]
        else:
            datas = self.data
        for dat in datas:
            try:
                DOMTree = mod_zip.get_xml_scenario(dat)
            except:
                continue
            self.ScmRoom = DOMTree.documentElement
            ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
            ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
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

    def button_screen(self, dat, start=None):
        self.sm.current = dat

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'text_48202'), bgcolor=(1, 0.5, 0, 0.3)))

        self.layout2 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        
        self.sm = ScreenManager(size_hint=(1, 1))
        
        self.scr1 = ScrMsg(name='Scr1')
        self.sm.add_widget(self.scr1)
        self.sceen1 = self.sceen('C_s2', 'Scr2')
        self.scr1.add_widget(self.sceen1)
        self.scr2 = ScrMsg(name='Scr2')
        self.sm.add_widget(self.scr2)
        self.sceen2 = self.sceen(self.screen1(), 'Scr3', btn1='Scr1')
        self.scr2.add_widget(self.sceen2)
        self.scr3 = ScrMsg(name='Scr3')
        self.sm.add_widget(self.scr3)
        self.sceen3 = self.sceen('text_33974', 'Scr3', btn1='Scr2')
        self.scr3.add_widget(self.sceen3)
        
        self.layout2.add_widget(self.sm)
        root.add_widget(self.layout2)
        root.add_widget(MyButton(text=get_message(self.ScmParam, '1053'), on_press=self.finish, size_hint=(1, None), height=80))
        return root

    def screen1(self):
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'C_s4'), font_size=fs*1.2, size_hint=(1, 1), bgcolor=(1, 0.8, 0, 0.3)))
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'C_s3'), font_size=fs*1.2, size_hint=(1, 1), bgcolor=(1, 0, 0, 0.3)))
        self.drop_distn = DropDown()
        for index in ['text_32076', 'text_32077']:
            btn2 = MyButton(text=get_message(self.ScmParam, index), size_hint_y = None, font_size=fs*1.5)
            btn2.bind(on_release = lambda btn2: self.drop_distn.select(btn2.text))
            self.drop_distn.add_widget(btn2)
        self.but_distn = MyButton(text =get_message(self.ScmParam, 'text_184'), font_size=fs*1.5, size_hint =(1, 1))
        self.but_distn.bind(on_release = self.drop_distn.open)
        self.drop_distn.bind(on_select = lambda instance, x: setattr(self.but_distn, 'text', x))
        layout.add_widget(self.but_distn)
        layout.add_widget(self.box('C_s5'))
        return layout

    def sceen(self, screen, btn2, informations=None, btn1=None, start=None):
        lat = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        if informations:
            lat.add_widget(MyLabel(text=get_message(self.ScmParam, informations), size_hint=(1, None), bgcolor=(1, 0, 0, 0.3)))
        root = ScrollView(size_hint=(1, 1))
        if type(screen) is str:
            root.add_widget(MyLabel(text=get_message(self.ScmParam, screen), bgcolor=(0, 1, 1, 0.3)))
        else:
            root.add_widget(screen)
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

    def MyButton_screen(self, dat, start=None):
        if start == 1:
            self.begin_time = time.time()
            responce = self.ecu.run_cmd(self. ScmParam['Cmde1'])
        if dat == 'Scr7Msg8':
            self.need_update = True
        self.sm.current = dat

    def box(self, text):
        glay = BoxLayout(orientation='horizontal', size_hint=(1, None))
        label1 = MyLabelBlue(text=self.paramsLabels[self.ScmParam[text]], halign='left', size_hint=(.65, 1), param_name=parameter_name)
        text = MyTextInput(text='')
        glay.height = label1.height
        glay.add_widget(label1)
        glay.add_widget(text)
        self.labels[self.ScmParam[parameter_name]] = text
        return glay

    def make_box_params(self, parameter_name):
        params = self.get_ecu_values()
        glay = BoxLayout(orientation='horizontal', size_hint=(1, None))
        label1 = MyLabelBlue(text=self.paramsLabels[self.ScmParam[parameter_name]], halign='left', size_hint=(.65, 1), param_name=parameter_name)
        label2 = MyLabelGreen(text=params[self.ScmParam[parameter_name]], halign='right', size_hint=(.35, 1), font_size=fs)
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
