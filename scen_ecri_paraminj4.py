# -*- coding: utf-8 -*-
import re, time, mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from mod_ecu import *
from collections import OrderedDict
import xml.dom.minidom
import xml.etree.ElementTree as et

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
        
        super(Scenarii, self).__init__()

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'Title'), font_size=fs, bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'Subtitle'), font_size=fs*1.5, bgcolor=(1, 0.3, 0, 0.3)))
        root.add_widget(MyLabel(text=get_message(self.ScmParam, 'InformationsContent'), font_size=fs*2, bgcolor=(1, 0, 0, 0.3)))
        root.add_widget(MyButton(text=get_message(self.ScmParam, 'Yes'), font_size=fs*2, on_press=self.resetValues))
        root.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), font_size=fs*2, on_press=self.stop))
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
                paramByteLength = len(parameters[0])//2
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
                        if (len(hexVal)//2) % paramByteLength:
                            hexVal = '00' * (paramByteLength - len(hexVal)//2) + hexVal
                        response = self.ecu.run_cmd(self.ScmSet['Commands'][name],hexVal)
            else:
                idValue = self.ecu.get_id(self.ScmSet['Identifications'][value], 5)
                if isHex(idValue):
                    response = self.ecu.run_cmd(self.ScmSet['Commands'][name],idValue)
        return response

    def reset_Values(self, d):
        self.popup.dismiss()
        lat = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        self.lbltxt = MyLabel(text=get_message(self.ScmParam, 'CommandInProgress'), size_hint=(1, 0.3), bgcolor=(0.5, 0, 0, 0.3))
        self.lbltxt1 = MyLabel(text=get_message(self.ScmParam, ''), bgcolor=(1, 0, 0, 0.3))
        root = ScrollView(size_hint=(1, 1))
        lat.add_widget(self.lbltxt)
        root.add_widget(self.lbltxt1)
        lat.add_widget(root)
        response = ''
        MyPopup_close(get_message(self.ScmParam, 'Informations'), lat)
        for name, value in self.ScmSet['CommandParameters'].items():
            base.EventLoop.idle
            rsp = self.valueReset(name, value)
            self.lbltxt1.text += rsp
            self.lbltxt1.height += fs
            response += rsp
            base.EventLoop.idle()
        self.lbltxt.text = get_message(self.ScmParam, 'CommandFinished')
        self.lbltxt.text += ':\n'
        
        if "NR" in response:
            self.lbltxt.text += get_message(self.ScmParam, 'EndScreenMessage4')
        else:
            self.lbltxt.text += get_message(self.ScmParam, 'EndScreenMessage3')

    def getIdsDump(self):
        idsDump = OrderedDict()
        for name, value in self.ScmSet['CommandIdentifications'].items():
            idValue = self.ecu.get_id(self.ScmSet['Identifications'][value], True)
            if isHex(idValue):
                idsDump[self.ScmSet['Commands'][name]] = idValue
        return idsDump

    def makeDump(self):
        fileRoot = et.Element("ScmRoot")
        fileRoot.text = "\n    "

        idsDump = self.getIdsDump()
        
        if not idsDump: return

        for cmd, value in idsDump.items():
            el = et.Element("ScmParam", name=cmd, value=value)
            el.tail = "\n    "
            fileRoot.insert(1,el)

        tree = et.ElementTree(fileRoot)
        tree.write(mod_globals.dumps_dir + ScmParam['FileName'])
      

    def resetValues(self, instance):
        if not mod_globals.opt_demo:
            self.makeDump()
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        self.lbltxt = MyLabel(text=get_message(self.ScmParam, 'ComboBoxName'), font_size=fs*1.5)
        layout.add_widget(self.lbltxt)
        layout.add_widget(MyButton(text=get_message(self.ScmParam, '1926'), font_size=fs*2, on_release=self.reset_Values))
        self.popup = MyPopup_close(get_message(self.ScmParam, 'Informations'), layout, op=False)
        self.popup.open()

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
