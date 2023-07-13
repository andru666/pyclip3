# -*- coding: utf-8 -*-
import mod_globals, mod_zip
from mod_utils import *
from kivy.app import App
from collections import OrderedDict
import xml.dom.minidom
import xml.etree.ElementTree as et
from kivy.clock import Clock

class ScrMsg(Screen):
    pass

class ecus:
    
    vdiag = ""
    buttons = {}
    ncalib = ""

    def __init__(self, vd, nc, bt):
        self.vdiag = vd
        self.ncalib = nc
        self.buttons = bt

class Scenario(App):
    global fs
    fs = mod_globals.fontSize
    def __init__(self, **kwargs):
        self.data = kwargs['data']
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        DOMTree = mod_zip.get_xml_scenario(self.data)
        ScmRoom = DOMTree.documentElement
        ScmParams = ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = ScmRoom.getElementsByTagName('ScmSet')
        self.ScmLists = ScmRoom.getElementsByTagName("ScmList")
        self.ScmParam = OrderedDict()
        self.vdiagExists = False
        self.ncalibExists = False
        self.ScmSet = {}
        self.ScmUSet = []
        self.Buttons = {}
        self.commands = {}
        self.ScmList_Etats = []
        self.ScmList_Messages = []
        self.ecusList = []
        self.blue_part_size = 0.75
        self.correctEcu = ''
        self.droot = et.fromstring(mod_zip.get_xml_scenario_et(self.data))
        
        for Param in ScmParams:
            name = (Param.getAttribute('name'))
            value = (Param.getAttribute('value'))
            self.ScmParam[name] = value
        
        for Set in ScmSets:
            if len(Set.attributes) >= 1:
                if len(Set.attributes) >= 1:
                    setname = Set.getAttribute('name')
                    ScmParams = Set.getElementsByTagName('ScmParam')
                    scmParamsDict = OrderedDict()
                    for Param in ScmParams:
                        name = Param.getAttribute('name')
                        value = Param.getAttribute('value')
                        scmParamsDict[name] = value
                    self.ScmSet[setname] = scmParamsDict
                else:
                    print(11)
        if "IdentVdiag" in list(self.ScmParam.keys()):
            self.vdiagExists = True

        for vDiag in self.droot:
            if vDiag.attrib["name"] == "ListVdiag":
                if len(list(vDiag.keys())) == 1:
                    for vDiagName in vDiag:
                        buttons = OrderedDict()
                        if vDiagName:
                            for vDiagButton in vDiagName:
                                buttons[vDiagButton.attrib["name"]] = vDiagButton.attrib["value"]
                                self.ecusList.append(ecus(vDiagName.attrib["name"], '', buttons))
            if vDiag.attrib["name"] == "Commands":
                if len(list(vDiag.keys())) == 1:
                    for param in vDiag:
                        serviceIDs = self.ecu.get_ref_cmd(param.attrib["value"]).serviceID
                        startReq = ""
                        for sid in serviceIDs:
                            if self.ecu.Services[sid].params:
                                startReq = self.ecu.Services[sid].startReq
                                break
                        self.commands[param.attrib["name"]] = {"command": param.attrib["value"], "startReq": startReq}
        
        if self.vdiagExists:
            value1 = self.ecu.get_id(self.ScmParam['IdentVdiag'], 5)
            for ecuSet in self.ecusList:
                if ecuSet.vdiag == value1.upper():
                    self.correctEcu = ecuSet
                    break 
        else:
            self.correctEcu = self.ecusList[0]

        if not self.correctEcu and mod_globals.opt_demo:
            self.correctEcu = self.ecusList[0]
        
        if self.vdiagExists:
            if not self.correctEcu:
                return
        
        self.identsList = OrderedDict()
        self.identsRangeKeys = OrderedDict()

        for param in list(self.ScmParam.keys()):
            if param.startswith('Idents') and param.endswith('Begin'):
                key = param[6:-5]
                begin = int(self.ScmParam['Idents'+key+'Begin'])
                end = int(self.ScmParam['Idents'+key+'End'])
                try:
                    self.ecu.get_ref_id(self.ScmParam['Ident' + str(begin)]).mnemolist[0]
                except:
                    continue
                else:
                    for idnum in range(begin ,end + 1):
                        self.identsList['D'+str(idnum)] = self.ScmParam['Ident'+str(idnum)]
                        if len(self.ecu.get_ref_id(self.ScmParam['Ident' + str(idnum)]).mnemolist) > 1:
                            mnemonicsLen = [int(self.ecu.Mnemonics[bitsLen].bitsLength) for bitsLen in self.ecu.get_ref_id(self.ScmParam['Ident' + str(idnum)]).mnemolist]
                            self.ecu.get_ref_id(self.ScmParam['Ident' + str(idnum)]).mnemolist = [self.ecu.get_ref_id(self.ScmParam['Ident' + str(idnum)]).mnemolist[mnemonicsLen.index(max(mnemonicsLen))]]
                    frame = self.ecu.Mnemonics[self.ecu.get_ref_id(self.identsList['D'+str(begin)]).mnemolist[0]].request
                    self.identsRangeKeys[key] = {"begin": begin, "end": end, "frame": frame}
        
        self.functions = OrderedDict()
        for cmdKey in list(self.commands.keys()):
            if cmdKey == 'Cmd1' and "Cmd5" in list(self.commands.keys()):
                self.injectorsDict = OrderedDict()
                self.injectorsDict[get_message(self.ScmParam, 'Cylinder1')] = self.commands['Cmd1']['command']
                self.injectorsDict[get_message(self.ScmParam, 'Cylinder2')] = self.commands['Cmd2']['command']
                self.injectorsDict[get_message(self.ScmParam, 'Cylinder3')] = self.commands['Cmd3']['command']
                self.injectorsDict[get_message(self.ScmParam, 'Cylinder4')] = self.commands['Cmd4']['command']
                self.functions[1] = [1, self.injectorsDict]
            if cmdKey == 'Cmd5':
                self.functions[2] = ["EGR_VALVE", 2, self.commands['Cmd5']['command']]
            if cmdKey == 'Cmd6':
                self.functions[3] = ["INLET_FLAP", 3, self.commands['Cmd6']['command']]
            if cmdKey == 'Cmd7':
                self.functions[4] = ["PARTICLE_FILTER", 4, self.commands['Cmd7']['command']]
                self.functions[5] = ["Button5ChangeData", 5, self.commands['Cmd7']['command']]
                self.functions[6] = ["Button6ChangeData", 6, self.commands['Cmd7']['command']]
            if len(self.commands) == 1 and cmdKey == 'Cmd1':
                self.functions[7] = ["Button7ChangeData", 7]
        if self.ScmLists:
            for Set in self.ScmLists:
                ScmParams = Set.getElementsByTagName("ScmItem")
                for Param in ScmParams:
                    value = ( Param.getAttribute("value") ) 
                    self.ScmUSet.append(value)
        super(Scenario, self).__init__()

    def build(self):
        self.CLIP = get_message(self.ScmParam, 'Informations')
        self.mainText =get_message(self.ScmParam, 'Title')
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=self.mainText, bgcolor=(1, 1, 0, 0.3)))
        self.sm = ScreenManager(size_hint=(1, 1))
        scr1 = ScrMsg(name='SCR1')
        self.sm.add_widget(scr1)
        layout11 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        layout1 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=fs*1.5)
        layout11.add_widget(self.info('Informations', 'Message1'))
        id_bt = 1
        self.Buttons = OrderedDict()
        for bt in list(self.correctEcu.buttons.keys()):
            if bt == 'InjectorsButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    self.Buttons[1] = get_message(self.ScmParam, 'Injectors')
                    but = MyButton(text=self.Buttons[1], on_press=lambda *args: self.button_screen('SCR_INJ'), size_hint=(1, None))
                    layout1.height += but.height
                    layout1.add_widget(but)
            if bt == 'EGRValveButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    self.Buttons[2] = get_message(self.ScmParam, 'EGR_VALVE')
                    but = MyButton(text=self.Buttons[2], id=str(id_bt), on_press=self.resetValues, size_hint=(1, None))
                    layout1.height += but.height
                    layout1.add_widget(but)
            if bt == 'InletFlapButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    self.Buttons[3] = get_message(self.ScmParam, 'INLET_FLAP')
                    but = MyButton(text=self.Buttons[3], id=str(id_bt), on_press=self.resetValues, size_hint=(1, None))
                    layout1.height += but.height
                    layout1.add_widget(but)
            if bt == 'ParticleFilterButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    self.Buttons[4] = get_message(self.ScmParam, 'PARTICLES_FILTER')
                    but = MyButton(text=self.Buttons[4], id=str(id_bt), on_press=self.resetValues, size_hint=(1, None))
                    layout1.height += but.height
                    layout1.add_widget(but)
            if bt.startswith("Button"):
                if str(self.correctEcu.buttons[bt]) == 'true':
                    self.Buttons[int(bt.strip('MyButton'))] = get_message(self.ScmParam, bt[:-6] + "Text")
                    but = MyButton(text=self.Buttons[int(bt.strip('MyButton'))],id=str(id_bt), on_press=self.resetValues, size_hint=(1, None))
                    layout1.height += but.height
                    layout1.add_widget(but)
            id_bt += 1
        if len(self.commands) > 5:
            scr2 = ScrMsg(name='SCR_INJ')
            layout2 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
            layout2.add_widget(self.info('Informations', 'Message21'))
            for inj in list(self.functions[1][1].keys()): 
                layout2.add_widget(MyButton(text=inj, id=inj, on_press=self.resetInjetorsData, size_hint=(1, 1)))
            layout2.add_widget(MyButton(text=get_message(self.ScmParam, '6218'), on_press=lambda *args: self.button_screen('SCR1'), size_hint=(1, 1)))
            scr2.add_widget(layout2)
            self.sm.add_widget(scr2)
        self.scr3 = ScrMsg(name='SCR_I')
        self.sm.add_widget(self.scr3)
        rot = ScrollView(size_hint=(1, 1))
        rot.add_widget(layout1)
        layout11.add_widget(rot)
        scr1.add_widget(layout11)
        root.add_widget(self.sm)
        root.add_widget(MyButton(text=get_message(self.ScmParam, '1053'), on_press=self.stop, size_hint=(1, None)))
        return root

    def takesParams(self, request):
        for cmd in list(self.commands.values()):
            if cmd['startReq'] == request:
                commandToRun = cmd['command']
                return commandToRun

    def makeDump(self, cmd, idents):
        fileRoot = et.Element("ScmRoot")
        fileRoot.text = "\n        "

        cmdElement = et.Element("ScmParam", name="Command", value=cmd)
        cmdElement.tail = "\n        "
        fileRoot.insert(1,cmdElement)
        
        for k in idents:
            el = et.Element("ScmParam", name='D'+ '{:0>2}'.format(k[1:]), value=str(idents[k]))
            el.tail = "\n        "
            fileRoot.insert(1,el)

        tree = et.ElementTree(fileRoot)
        tree.write(mod_globals.dumps_dir + self.ScmParam['FileName'])

    def getValuesFromEcu(self, params):
        paramToSend = ""
        commandToRun = ""
        requestToFindInCommandsRequests = ""
        backupDict = {}
        try:
            idKeyToFindInRange = int((list(params.keys())[0]).replace("D",""))
        except:
            return commandToRun, paramToSend
        else:
            layout = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
            lbltxt = MyLabel(text='')
            for rangeK in list(self.identsRangeKeys.keys()):
                if self.identsRangeKeys[rangeK]['begin'] <= idKeyToFindInRange <= self.identsRangeKeys[rangeK]['end']:
                    requestToFindInCommandsRequests = "3B" + self.identsRangeKeys[rangeK]['frame'][-2:]
                    isTakingParams = self.takesParams(requestToFindInCommandsRequests)
                    if isTakingParams:
                        for k,v in params.items():
                            backupDict[k] = self.ecu.get_id(self.identsList[k], 5)
                            if v in list(self.identsList.keys()):
                                self.identsList[k] = self.ecu.get_id(self.identsList[v], 5)
                            else:
                                self.identsList[k] = v
                        layout.add_widget(MyLabel(text=str(self.identsList)))
                        for idKey in range(self.identsRangeKeys[rangeK]['begin'], self.identsRangeKeys[rangeK]['end'] + 1):
                            if str(self.identsList["D" + str(idKey)]).startswith("ID"):
                                self.identsList["D" + str(idKey)] = self.ecu.get_id(self.identsList["D" + str(idKey)], 5)
                                backupDict["D" + str(idKey)] = self.identsList["D" + str(idKey)]
                            paramToSend += str(self.identsList["D" + str(idKey)])
                        layout.add_widget(MyLabel(text=str(self.identsList)))
                        commandToRun = isTakingParams
                        break
            self.makeDump(commandToRun, backupDict)
            return commandToRun, paramToSend

    def info(self, info, message):
        layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None))
        l1 = MyLabel(text=get_message(self.ScmParam, info), size_hint=(1, None), bgcolor=(0.3, 0.3, 0, 0.3))
        l2 = MyLabel(text=get_message(self.ScmParam, message), size_hint=(1, None), bgcolor=(1, 0, 0, 0.3))
        layout.height = l1.height + l2.height
        layout.add_widget(l1)
        layout.add_widget(l2)
        return layout

    def getValuesToChange(self, resetItem):
        params = {}
        for child in self.droot:
            if child.attrib["name"] == resetItem:
                if len(list(child.keys())) == 1:
                    for param in child:
                        params[param.attrib["name"].replace("D0", "D")] = param.attrib["value"]
        return params

    def button_screen(self, dat, start=None):
        self.sm.current = dat
 
    def afterEcu_Change(self, instance):
        self.popup_afterEcuChange.dismiss()
        title = self.functions[6][0]
        params = self.getValuesToChange(title)
        mileage = int(self.mileage.text)
        lbltxt = MyLabel(text=get_message(self.ScmParam, 'CommandInProgressMessage'), font_size=fs*1.5, size_hint=(1, 1))
        for paramkey in list(params.keys()):
            if params[paramkey] == "Mileage":
                mnemonics = self.ecu.get_ref_id(self.identsList[paramkey]).mnemolist[0]
                identValue = self.ecu.get_id(self.identsList[paramkey], 5)
                if identValue == 'ERROR':
                    identValue = '00000000'
                hexval = "{0:0{1}X}".format(mileage,len(identValue))
                if self.ecu.Mnemonics[mnemonics].littleEndian == '1':
                    a = hexval
                    b = ''
                    if not len(a) % 2:
                        for i in range(0,len(a),2):
                            b = a[i:i+2]+b
                        hexval = b
                params[paramkey] = hexval
        command, paramToSend = self.getValuesFromEcu(params)
        response = self.ecu.run_cmd(command,paramToSend)
        lbltxt.text = get_message(self.ScmParam, 'CommandFinishedMessage')
        lbltxt.text += ':\n'
        
        if "ERROR" in paramToSend:
            lbltxt.text = "Data downloading went wrong. Aborting."
            MyPopup_close(self.CLIP, lbltxt)
            return
        if "NR" in response:
            lbltxt.text += get_message(self.ScmParam, 'Message41')
        else:
            lbltxt.text += get_message(self.ScmParam, 'Message31')
        MyPopup_close(self.CLIP, lbltxt)

    def afterEcuChange(self, instance):
        self.popup_resetValues.dismiss()
        button = self.functions[6][1]
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        if instance.id == '0':
            milea = self.mileage.text
        else:
            milea = ''
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'Message262')))
        layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'MessageBox2')))
        self.mileage = MyTextInput(text=milea, multiline=False)
        if instance.id == '0':
            if not self.mileage.text.isdigit() and self.mileage.text:
                layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'MessageBox2')))
                self.mileage = MyTextInput(text=milea, multiline=False)
                layout.add_widget(self.mileage)
                self.AECbutton = MyButton(text=get_message(self.ScmParam, '1926'), id='0', on_press=self.afterEcuChange, size_hint=(1, None))
                self.popup_afterEcuChange.dismiss()
            elif not (2 <= len(self.mileage.text) <= 6 and int(self.mileage.text) >= 10):
                layout.add_widget(MyLabel(text=get_message(self.ScmParam, 'MessageBox1')))
                self.mileage = MyTextInput(text=milea, multiline=False)
                layout.add_widget(self.mileage)
                self.AECbutton = MyButton(text=get_message(self.ScmParam, '1926'), id='0', on_press=self.afterEcuChange, size_hint=(1, None))
                self.popup_afterEcuChange.dismiss()
            else:
                layout.add_widget(MyLabel(text=self.mileage.text + ' ' + get_message(self.ScmParam, 'Unit1')))
                self.AECbutton = MyButton(text=get_message(self.ScmParam, '1926'), id='0', on_press=self.afterEcu_Change, size_hint=(1, None))
                self.popup_afterEcuChange.dismiss()
        else:
            layout.add_widget(self.mileage)
            self.AECbutton = MyButton(text=get_message(self.ScmParam, '1926'), id='0', on_press=self.afterEcuChange, size_hint=(1, None))
        layout.add_widget(self.AECbutton)
        self.popup_afterEcuChange = MyPopup(title=(self.Buttons[button]), content=layout)
        self.popup_afterEcuChange.open()
        
    def set_GlowPlugsType(self, instance):
        self.popup_setGlowPlugsType.dismiss()
        params = self.getValuesToChange(self.functions[7][0])
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        lbltxt = MyLabel(text=get_message(self.ScmParam, 'CommandInProgressMessage'), font_size=fs*1.5, size_hint=(1, 1))
        glowPlugType =    "{0:0{1}X}".format((int(self.ScmParam['Mask1']) + int(self.ScmParam[instance.id])),2)
        params[list(params.keys())[0]] = glowPlugType
        command, paramToSend = self.getValuesFromEcu(params)
        if "ERROR" in paramToSend:
            lbltxt.text = "Data downloading went wrong. Aborting."
            MyPopup_close(self.CLIP, lbltxt)
            return
        response = self.ecu.run_cmd(command,paramToSend)
        lbltxt.text = get_message(self.ScmParam, 'CommandFinishedMessage')
        lbltxt.text += ':\n'
        if "NR" in response:
            lbltxt.text += get_message(self.ScmParam, 'Message41')
        else:
            lbltxt.text += get_message(self.ScmParam, 'Message31')
        layout.add_widget(lbltxt)
        MyPopup_close(self.CLIP, layout)

    def setGlowPlugsType(self, instance):
        self.popup_resetValues.dismiss()
        params = self.getValuesToChange(self.functions[7][0])
        codemr, label, self.VALUE = self.ecu.get_st(self.ScmParam['State1'], True)
        self.CODEMR = '%s - %s' % (codemr, label)
        layout = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        layout.add_widget(self.make_box_params(self.CODEMR, self.VALUE))
        for USet in self.ScmUSet:
            layout.add_widget(MyButton(text=get_message_by_id(USet), size_hint=(1, 1), id=USet, on_press=self.set_GlowPlugsType))
        layout.add_widget(MyButton(text=get_message(self.ScmParam, '1053'), size_hint=(1, 1), on_press=self.stop))
        self.popup_setGlowPlugsType = MyPopup(title=(self.Buttons[self.functions[7][1]]), content=layout)
        self.popup_setGlowPlugsType.open()    

    def reset_Values(self, instance):
        self.popup_resetValues.dismiss()
        key = int(instance.id)
        defaultCommand = self.functions[key][2]
        title = self.functions[key][0]
        params = self.getValuesToChange(title)
        lbltxt = MyLabel(text=get_message(self.ScmParam, 'CommandInProgressMessage'), font_size=fs*1.5, size_hint=(1, 1))
        command, paramToSend = self.getValuesFromEcu(params)
        if "ERROR" in paramToSend:
            lbltxt.text = "Data downloading went wrong. Aborting."
            MyPopup_close(self.CLIP, lbltxt)
            return
        lbltxt.text = get_message(self.ScmParam, 'CommandFinishedMessage')
        lbltxt.text += ':\n'
        if command:
            response = self.ecu.run_cmd(command,paramToSend)
        else:
            response = self.ecu.run_cmd(defaultCommand)
        if "NR" in response:
            lbltxt.text += get_message(self.ScmParam, 'Message41')
        else:
            lbltxt.text += get_message(self.ScmParam, 'Message31')
        MyPopup_close(self.CLIP, lbltxt)

    def resetValues(self, instance):
        key = int(instance.id)
        paramToSend = ""
        commandTakesParams = True
        button = self.functions[key][1]
        lay = GridLayout(cols=1, spacing=5, size_hint=(1, 1))
        layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=0)
        lbltxt = MyLabel(text='', size_hint=(1, None), bgcolor=(0.3, 0, 0, 0.3))
        if key == 2 or key == 3:
            lbltxt = MyLabel(text=get_message(self.ScmParam, 'Message23'), size_hint=(1, None), bgcolor=(0.3, 0, 0, 0.3))
        if key == 4:
            lbltxt = MyLabel(text=get_message(self.ScmParam, 'Message24'), size_hint=(1, None), bgcolor=(0.3, 0, 0, 0.3))
        if key == 5:
            lbltxt = MyLabel(text=get_message(self.ScmParam, 'Message25'), size_hint=(1, None), bgcolor=(0.3, 0, 0, 0.3))
        if key == 7:
            if 'Message29' in list(self.ScmParam.keys()):
                li = self.info('Informations', 'Message29')
            else:
                li = self.info('Informations', 'Message261')
            layout.add_widget(li)
            layout.height += li.height
        if key == 6:
            lbltxt = MyLabel(text=get_message(self.ScmParam, 'Message261'), size_hint=(1, None), bgcolor=(0.3, 0, 0, 0.3))
        layout.height += lbltxt.height
        if lbltxt.text != '': layout.add_widget(lbltxt)
        layout_box = BoxLayout(orientation='horizontal', spacing=5, size_hint=(1, 0.2))
        res_button = MyButton(text=get_message(self.ScmParam, 'Yes'), id=str(key), size_hint=(1, 1))
        layout_box.add_widget(res_button)
        if key == 6:
            res_button.bind(on_press=self.afterEcuChange)
        elif key == 7:
            res_button.bind(on_press=self.setGlowPlugsType)
        else:
            res_button.bind(on_press=self.reset_Values)
        NoBut = MyButton(text=get_message(self.ScmParam, 'No'), size_hint=(1, 1))
        layout_box.add_widget(NoBut)
        root = ScrollView(size_hint=(1, 1))
        root.add_widget(layout)
        lay.add_widget(root)
        lay.add_widget(layout_box)
        self.popup_resetValues = MyPopup(title=(self.Buttons[button]), content=lay)
        self.popup_resetValues.open()
        NoBut.bind(on_press=self.popup_resetValues.dismiss)

    def resetInjetorsData(self, instance):
        response = ''
        lbltxt = MyLabel(text=get_message(self.ScmParam, 'CommandInProgressMessage'), font_size=fs*1.5, size_hint=(1, 1))
        MyPopup_close(get_message(self.ScmParam, 'Informations'), lbltxt)
        base.EventLoop.idle()
        response = self.ecu.run_cmd(self.functions[1][1][instance.id])
        base.EventLoop.idle()
        lbltxt.text = get_message(self.ScmParam, 'CommandFinishedMessage')
        lbltxt.text += ':\n'
        if "NR" in response:
            lbltxt.text += get_message(self.ScmParam, 'Message41')
        else:
            lbltxt.text += get_message(self.ScmParam, 'Message31')
    
    def make_box_params(self, param, value):
        glay = BoxLayout(orientation='horizontal', size_hint=(1, 1))
        label1 = MyLabelBlue(text=param, size_hint_x=0.7, param_name=param)
        label2 = MyLabelGreen(text=value, halign='right', size_hint_x=0.3)
        if label1.height > label2.height:
            glay.height = label1.height
        else:
            glay.height = label2.height
        glay.add_widget(label1)
        glay.add_widget(label2)
        return glay

def run(elm, ecu, command, data):
    app = Scenario(elm=elm, ecu=ecu, command=command, data=data)
    app.run()