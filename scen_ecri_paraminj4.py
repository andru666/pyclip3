# -*- coding: utf-8 -*-
import re, time, mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from collections import OrderedDict
import xml.dom.minidom
import xml.etree.cElementTree as et

class Scenarii(App):
    global fs
    fs = mod_globals.fontSize
    def __init__(self, **kwargs):
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        DOMTree = mod_zip.get_xml_scenario(kwargs['data'])
        ScmRoom = DOMTree.documentElement
        ScmParams = ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = ScmRoom.getElementsByTagName('ScmSet')
        self.ScmParam = OrderedDict()
        self.ScmSet = OrderedDict()
        for Param in ScmParams:
            name = pyren_encode(Param.getAttribute('name'))
            value = pyren_encode(Param.getAttribute('value'))
            self.ScmParam[name] = value
        
        for Set in ScmSets:
            setname = pyren_encode(Set.getAttribute('name'))
            ScmParams = Set.getElementsByTagName('ScmParam')
            scmParamsDict = OrderedDict()
            for Param in ScmParams:
                name = pyren_encode(Param.getAttribute('name'))
                value = pyren_encode(Param.getAttribute('value'))
                scmParamsDict[name] = value
            self.ScmSet[setname]= scmParamsDict
        
        super(Scenarii, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'Title'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'Subtitle'), bgcolor=(1, 0.3, 0, 0.3)))
        root.add_widget(self.info('Informations', 'InformationsContent'))
        root.add_widget(self.button_yes_no(False, self.resetValues))
        root.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), on_press=self.stop))
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(root)
        return rot
    
    def valueReset(self, name, value):
        if isHex(value):
            response = self.ecu.run_cmd(self.ScmSet['Commands'][name],value)
        else:
            result = re.search(r"[^a-zA-Z\d\s:]", value)
            if result:
                parameters = re.findall(r"Ident\d+", value)
                paramByteLength = len(parameters[0])/2
                comp = value
                for param in parameters:
                    paramValue = self.ecu.get_id(self.ScmSet['Identifications'][param], 5)
                    if isHex(paramValue):
                        comp = comp.replace(param, '0x' + self.ecu.get_id(self.ScmSet['Identifications'][param], 5))
                    if comp:
                        calc = Calc()
                        idValue = calc.calculate(comp)
                        hexVal = hex(idValue)[2:]
                        if len(hexVal)%2:
                            hexVal = '0' + hexVal
                        if (len(hexVal)/2) % paramByteLength:
                            hexVal = '00' * (paramByteLength - len(hexVal)/2) + hexVal
                        response = self.ecu.run_cmd(self.ScmSet['Commands'][name],hexVal)
            else:
                idValue = self.ecu.get_id(self.ScmSet['Identifications'][value], 5)
                if isHex(idValue):
                    response = self.ecu.run_cmd(self.ScmSet['Commands'][name],idValue)
        return response

    def reset_Values(self,instance):
        self.popup.dismiss()
        self.lbltxt = Label(text=get_message(self.ScmParam, 'CommandInProgress'))
        response = ''
        popup = MyPopup(title='STATUS', content=self.lbltxt)
        popup.open()
        time.sleep(5)
        base.EventLoop.idle
        for name, value in self.ScmSet['CommandParameters'].items():
            response += self.valueReset(name, value)
        base.EventLoop.idle()
        self.lbltxt.text = get_message(self.ScmParam, 'CommandFinished')
        self.lbltxt.text += ':\n'
        
        if "NR" in response:
            self.lbltxt.text += get_message(self.ScmParam, 'EndScreenMessage4')
        else:
            self.lbltxt.text += get_message(self.ScmParam, 'EndScreenMessage3')   

    def resetValues(self, instance):
        if not mod_globals.opt_demo:
            makeDump()
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        self.lbltxt = MyLabel(text=get_message(self.ScmParam, 'CommandInProgress'))
        layout.add_widget(self.lbltxt)
        layout.add_widget(MyButton(text=get_message(self.ScmParam, '1926'), on_press=self.reset_Values))
        self.popup = MyPopup(title='STATUS', content=layout)
        self.popup.open()
         
        
    def button_yes_no(self, no=True, yes=None):
        layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(1, 1))
        if yes: layout.add_widget(MyButton(text=get_message(self.ScmParam, 'Yes'), on_press=yes))
        if no: layout.add_widget(MyButton(text=get_message(self.ScmParam, 'No'), on_press=self.stop))
        return layout

    def info(self, info, message):
        layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, info), bgcolor=(0.3, 0.3, 0, 0.3)))
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, message), bgcolor=(1, 0, 0, 0.3)))
        return layout

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
