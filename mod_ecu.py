# -*- coding: utf-8 -*-
import sys, threading, random, asyncio
import time
import xml.dom.minidom
from collections import OrderedDict
from datetime import datetime, timedelta
from xml.dom.minidom import parse
from kivy import base
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock, mainthread
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty
from kivy.utils import platform
from kivy.properties import ObjectProperty, StringProperty, ListProperty
import mod_globals
import mod_zip
from mod_ecu_command import *
from mod_ecu_dataids import *
from mod_ecu_default import *
from mod_ecu_identification import *
from mod_ecu_mnemonic import *
from mod_ecu_parameter import *
from mod_ecu_service import *
from mod_ecu_state import *
from mod_elm import AllowedList
from mod_elm import dnat
from mod_elm import snat
from mod_ply import *
from mod_utils import *
from kivy_garden.graph import Graph, LinePlot
from math import sin, ceil, floor
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

F2A = {'01': '7A',
 '02': '01',
 '03': '51',
 '04': '26',
 '05': '2C',
 '06': '00',
 '07': '24',
 '08': '29',
 '09': '6E',
 '10': '57',
 '11': '52',
 '12': '79',
 '13': '0D',
 '14': '00',
 '15': '32',
 '16': '37',
 '17': '6B',
 '18': '04',
 '19': '3F',
 '20': '27',
 '21': '08',
 '22': '00',
 '23': '3A',
 '24': '50',
 '25': '1C',
 '26': '00',
 '27': '99',
 '28': '00',
 '29': '07',
 '30': '66',
 '31': 'A7',
 '32': '60',
 '33': '4B',
 '34': '2B',
 '35': '1B',
 '36': '61',
 '37': '25',
 '38': '1E',
 '39': 'D2',
 '40': '23',
 '41': '0E',
 '42': '40',
 '43': '7C',
 '44': '97',
 '45': '3C',
 '46': '82',
 '47': '4D',
 '48': '11',
 '49': '47',
 '50': '02',
 '51': '0F',
 '52': '70',
 '53': '71',
 '54': '72',
 '55': '0E',
 '56': '1A',
 '57': '5D',
 '59': 'E2',
 '60': 'A5',
 '61': 'A6',
 '62': '00',
 '63': '65',
 '64': 'DF',
 '65': '2A',
 '66': 'FE',
 '67': '7B',
 '68': '73',
 '69': '16',
 '70': '62',
 '72': '00',
 '73': '63',
 '74': '81',
 '76': '13',
 '77': '77',
 '78': '64',
 '79': 'D1',
 '80': 'F7',
 '81': 'F8',
 '86': '2E',
 '87': '06',
 '90': '59',
 '91': '86',
 '92': '87',
 '93': '00',
 '94': '67',
 '95': '93',
 '96': '95',
 '97': '68',
 '98': 'A8',
 '99': 'C0'}
ecudump = {}
resizeFont = False

class Plot(BoxLayout):
    def __init__(self, dt, **kwargs):
        self.dt = dt
        self.labels = {}
        super(Plot, self).__init__(**kwargs)
        self.graph = Graph(x_ticks_minor=1,  x_ticks_major=1, y_ticks_major=1, y_grid_label=True, padding=2, x_grid=True, y_grid=True, xmin=-0, xmax=10, ymin=-10, ymax=10)# x_grid_label=True,
        for k, v in self.dt.items():
            self.plot = LinePlot(line_width=2, color=v['color'])
            self.plot.points = v['plot']
            self.labels[k] = self.plot
            self.graph.add_plot(self.plot)
        self.add_widget(self.graph)
        
class showDatarefGui(App):
    def __init__(self, ecu, datarefs, path):
        self.ecu = ecu
        self.blue_part_size = 0.7
        self.datarefs = datarefs
        self.p_graf = {}
        self.labels = {}
        self.params = {}
        self.params_graf = {}
        self.UPDATE_DATA = []
        self.needupdate = True
        self.running = True
        self.clock_event = None
        self.path = path
        self.paramsLabels = OrderedDict()
        self.csvf = 0
        self.csvline = ''
        super(showDatarefGui, self).__init__()
        Window.bind(on_keyboard=self.key_handler)

    def key_handler(self, window, keycode1, keycode2, text, modifiers):
        global resizeFont
        if resizeFont:
            return True
        if keycode1 == 45 and mod_globals.fontSize > 10:
            MyPopup()
            mod_globals.fontSize = mod_globals.fontSize - 1
            resizeFont = True
            self.needupdate = False
            self.running = False
            self.stop()
            return True
        if keycode1 == 61 and mod_globals.fontSize < 40:
            MyPopup()
            mod_globals.fontSize = mod_globals.fontSize + 1
            resizeFont = True
            self.needupdate = False
            self.running = False
            self.stop()
            return True
        if keycode1 == 27:
            MyPopup()
            choice_result = ['<' + mod_globals.language_dict['6218'] + '>', -1]
            self.stop()
            return True
        return False

    def on_pause(self):
        self.running = False
        return True

    def on_resume(self):
        self.running = True
        pass
    
    def on_stop(self):
        self.running = False

    def make_box_params(self, parameter_name, val):
        fs = mod_globals.fontSize
        glay = BoxLayout(orientation='horizontal', size_hint=(1, None))
        label1 = MyLabelBlue(text=self.paramsLabels[parameter_name], size_hint=(self.blue_part_size, None), on_press= lambda *args: self.ecu.addElem(self.paramsLabels[parameter_name].split(' ')[0]), param_name=parameter_name)
        label2 = MyLabelGreen(text=val, size_hint=(1 - self.blue_part_size, None))
        if label1.height > label2.height:
            glay.height = label2.height = label1.height
        else:
            glay.height = label1.height = label2.height
        glay.add_widget(label1)
        glay.add_widget(label2)
        self.labels[parameter_name] = label2
        return glay

    def finish(self, instance):
        print('finish')
        if self.path[:3] == 'FAV':
            self.ecu.saveFavList()
        if self.ecu.GRAF:
            self.ecu.GRAF = False
        self.needupdate = False
        self.running = False
        if self.clock_event is not None:
            self.clock_event.cancel()
            self.clock_event = None
        if mod_globals.opt_csv and self.csvf!=0:
            self.csvf.close()
        self.stop()
    
    def get_ecu_values(self):
        self.ecu.elm.clear_cache()
        if mod_globals.opt_csv and self.csvf!=0:
            self.csvline = self.csvline + "\n"
            self.csvline = self.csvline.replace(';','\t')
            self.csvf.write(self.csvline if mod_globals.opt_csv_human else self.csvline)
            self.csvf.flush()
            self.csvline = datetime.now().strftime("%H:%M:%S.%f,")
            
        dct = OrderedDict()
        for dr in self.datarefs:
            if dr.name in self.UPDATE_DATA:
                continue
            
            if dr.type == 'State':
                if self.ecu.DataIds and "DTC" in self.path and dr in self.ecu.Defaults[mod_globals.ext_cur_DTC[:4]].memDatarefs:
                    name, codeMR, label, value, csvd = get_state(self.ecu.States[dr.name], self.ecu.Mnemonics, self.ecu.Services, self.ecu.elm, self.ecu.calc, True, self.ecu.DataIds)
                else:
                    name, codeMR, label, value, csvd = get_state(self.ecu.States[dr.name], self.ecu.Mnemonics, self.ecu.Services, self.ecu.elm, self.ecu.calc, True)
                key = '%s - %s' % (codeMR, label)
                dct[name] = str(value)
                self.paramsLabels[name] = key
            if dr.type == 'Parameter':
                if self.ecu.DataIds and "DTC" in self.path and dr in self.ecu.Defaults[mod_globals.ext_cur_DTC[:4]].memDatarefs:
                    name, codeMR, label, value, unit, csvd = get_parameter(self.ecu.Parameters[dr.name], self.ecu.Mnemonics, self.ecu.Services, self.ecu.elm, self.ecu.calc, True, self.ecu.DataIds)
                else:
                    name, codeMR, label, value, unit, csvd = get_parameter(self.ecu.Parameters[dr.name], self.ecu.Mnemonics, self.ecu.Services, self.ecu.elm, self.ecu.calc, True)
                if self.ecu.GRAF:
                    key = '%s - %s' % (codeMR, label)
                    if value == 'None':
                        val = 'None'
                    else:
                        val = str(value).strip()
                else:
                    key = '%s - %s' % (codeMR, label)
                    if value == 'None':
                        val = 'None'
                    else:
                        val = '%s %s' % (value, unit)
                dct[name] = str(val)
                self.paramsLabels[name] = key
            if dr.type == 'Identification':
                name, codeMR, label, value = get_identification(self.ecu.Identifications[dr.name], self.ecu.Mnemonics, self.ecu.Services, self.ecu.elm, self.ecu.calc, True)
                key = '%s - %s' % (codeMR, label)
                dct[name] = str(value).strip()
                self.paramsLabels[name] = key
            if dr.type=='Text' or dr.type=='DTCText':
                dct[dr.name] = str(dr.type)
            if mod_globals.opt_csv and self.csvf!=0 and (dr.type=='State' or dr.type=='Parameter'):
                self.csvline += ";" + (pyren_encode(csvd) if mod_globals.opt_csv_human else str(csvd))
                self.csvline += ","
        self.ecu.elm.currentScreenDataIds = self.ecu.getDataIds(list(self.ecu.elm.rsp_cache.keys()), self.ecu.DataIds)
        return dct

    def update_values(self, dt):
        if not self.running:
            return
        self.ecu.elm.clear_cache()
        params = self.get_ecu_values()
        for param, val in params.items():
            if val != 'Text' and val != 'DTCText':
                self.labels[param].text = val.strip()
        self.ecu.elm.currentScreenDataIds = self.ecu.getDataIds(self.ecu.elm.rsp_cache.keys(), self.ecu.DataIds)
        
        if mod_globals.opt_csv:
            self.clock_event = Clock.schedule_once(self.update_values, 0.02)
        else:
            self.clock_event = Clock.schedule_once(self.update_values, 0.05)

    async def fetch_and_update(self):
        while self.running:
            try:
                param = self.get_ecu_values()
                Clock.schedule_once(lambda dt: self.update_label(param))
                if mod_globals.opt_csv:
                    await asyncio.sleep(0.02)
                else:
                    await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                break

    def update_label(self, dt=None):
        if mod_globals.opt_demo:
            self.running = False
        if self.ecu.GRAF:
            self.plots()
            pass
        else:
            for param, val in dt.items():
                if val != 'Text' and val != 'DTCText':
                    self.labels[param].text = val.strip()

    def on_start(self):
        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            self.finish(self)
            return True

    def plots(self, dt=None):
        cle = False
        l = {}
        if self.Xmin < self.graph.graph.xmax: self.Xmin += 1
        for k, v in self.params.items():
            if not k in self.params_graf: self.params_graf[k] = []
            self.params_graf[k].append(v)
            if len(self.params_graf[k]) > 30:
                self.params_graf[k].pop(0)
            v = float(v)
            if len(self.p_graf[k]['plot']) >= self.graph.graph.xmax-1:
                prd = []
                i = 0
                for kk, vv in self.p_graf[k]['plot']:
                    if kk == 1:
                        continue
                    prd.append((i, vv))
                    i += 1
                self.p_graf[k]['plot'] = prd
                self.Xmin = self.graph.graph.xmax-1
            p = 1
            while v > 10:
                v = v / 10.0
                p += 1
            self.labels[k].text = '*' + str(p)
            self.p_graf[k]['plot'].append((self.Xmin, float(v)))
            self.graph.labels[k].points = self.p_graf[k]['plot']

    def graf_lab(self, k, col, p = 1):
        box1 = BoxLayout(orientation='horizontal',size_hint = (1, None), height=fs)
        name = self.paramsLabels[k].split('-', 1)
        box1.add_widget(MyLabel(text=name[0], font_size=fs*0.5, bgcolor=col, size_hint = (0.15, None)))
        self.labels[k] = MyLabel(text='*' + str(p), font_size=fs*0.5, bgcolor=[1, 0.2, 0.5, 1], size_hint = (0.1, None))
        box1.add_widget(self.labels[k])
        l = MyLabel(text=name[1], font_size=fs*0.5, size_hint = (0.75, None))
        box1.height = l.height*0.7
        box1.add_widget(l)
        return box1

    def zoom_y(self, d):
        if d == 1:
            self.graph.graph.ymax = self.graph.graph.ymax+1
            self.graph.graph.ymin = self.graph.graph.ymin-1
        if d == 0:
            self.graph.graph.ymax = self.graph.graph.ymax-1
            self.graph.graph.ymin = self.graph.graph.ymin+1
        
    def zoom_x(self, d):
        if d == 1:
            self.graph.graph.xmax = self.graph.graph.xmax+1
            self.Xmin = self.graph.graph.xmax
        if d == 0:
            self.graph.graph.xmax = self.graph.graph.xmax-1
            self.Xmin = self.graph.graph.xmax
            for k, v in self.p_graf.items():
                self.p_graf[k]['plot'].pop(0)

    def build(self):
        if mod_globals.opt_perform:
            self.ecu.elm.currentScreenDataIds = []
        if mod_globals.opt_csv and mod_globals.ext_cur_DTC == '000000':
            self.csvf, self.csvline = self.ecu.prepareCSV(self.datarefs, self.path)
        self.layout = GridLayout(cols=1, spacing=(4, 4), size_hint=(1.0, None))
        self.layout.bind(minimum_height=self.layout.setter('height'))
        fs = mod_globals.fontSize
        defaultFS = float(fs)/30.0
        header = 'ECU : ' + self.ecu.ecudata['ecuname'] + '  ' + self.ecu.ecudata['doc']
        self.layout.add_widget(MyLabel(text=header))
        params = self.get_ecu_values()
        max_str = ''
        for param in list(self.paramsLabels.values()):
            len_str = len(param)
            if len_str > len(max_str):
                max_str = param
        tmp_label = MyLabel(text=max_str)
        tmp_label._label.render()
        self.UPDATE_DATA = []
        UPDATE = False
        if self.ecu.GRAF:
            self.Xmin = 0
            self.layout.size_hint = (1, 1)
            b = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
            b.add_widget(MyLabel(text='Axe X', bgcolor=(1,0,0,1)))
            b.add_widget(MyLabel(text='Axe Y', bgcolor=(1,0,0,1)))
            b_xy = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=5)
            b_xy.add_widget(MyButton(text='+', size_hint=(1, None), on_press=lambda *args: self.zoom_x(1)))
            b_xy.add_widget(MyButton(text='-', size_hint=(1, None), on_press=lambda *args: self.zoom_x(0)))
            b_xy.add_widget(MyButton(text='+', size_hint=(1, None), on_press=lambda *args: self.zoom_y(1)))
            b_xy.add_widget(MyButton(text='-', size_hint=(1, None), on_press=lambda *args: self.zoom_y(0)))
            self.layout.add_widget(b)
            self.layout.add_widget(b_xy)
            i = 0
            rrt = GridLayout(cols=1, spacing=(4, 4), size_hint=(1.0, None))
            rrt.bind(minimum_height=rrt.setter('height'))
            for k, v in params.items():
                v = float(v)
                p = 1
                while v > 10:
                    v = v / 10.0
                    p += 1
                
                col = [1, i/10, 0, 1]
                self.p_graf[k] = {'color':col, 'plot':[]}
                self.p_graf[k]['plot'].append((self.Xmin, float(v)))
                i += 3
                rrt.add_widget(self.graf_lab(k, col, p))
            self.graph = Plot(size_hint=(1, 1), dt=self.p_graf)
            self.layout.add_widget(self.graph)
            rt = ScrollView(size_hint=(1, 0.2))
            rt.add_widget(rrt)
            self.layout.add_widget(rt)
            self.layout.add_widget(MyButton(text='PLOTS', size_hint=(1, None), on_press=self.plots))
        else:
            for paramName, val in params.items():
                if val == 'Text':
                    if mod_globals.language_dict['299'] in paramName:
                        UPDATE = True
                    else:
                        UPDATE = False
                    self.layout.add_widget(MyLabel(text=paramName))
                elif val == 'DTCText':
                    lines = len(paramName.split('\n'))
                    simb = len(paramName)
                    operation = simb / int(60/defaultFS)
                    if lines <= operation:
                        lines = operation
                        lines += 1
                    elif lines - 1 == operation or lines - 2 == operation:
                        lines += 1
                    if fs >= 40:
                        lines += 1
                    prelabel = MyTextInput(text=pyren_encode(paramName), size_hint=(1, None), multiline=True, readonly=True, foreground_color=[1,1,1,1], background_color=[0,0,1,1], padding=[0, 0])
                    self.layout.add_widget(prelabel)
                else:
                    if UPDATE:
                        self.UPDATE_DATA.append(paramName)
                    self.layout.add_widget(self.make_box_params(paramName, val))
        quitbutton = MyButton(text='<' + mod_globals.language_dict['6218'] + '>', size_hint=(1, None), on_press=self.finish)
        self.layout.add_widget(quitbutton)
        root = ScrollView(size_hint=(None, None), size=Window.size, do_scroll_x=True, pos_hint={'center_x': 0.5,
         'center_y': 0.5})
        root.add_widget(self.layout)
        if self.needupdate:
            self.clock_event = Clock.schedule_once(self.update_values, 0.5)
            #threading.Thread(target=self.start_async_loop, daemon=True).start()
        return root
    
    def start_async_loop(self):
        self.clock_event = asyncio.run(self.fetch_and_update())
    

class ECU():
    global fs
    GRAF = False
    fs = mod_globals.fontSize
    getDTCmnemo = ''
    resetDTCcommand = ''
    screens = []
    Defaults = {}
    Parameters = {}
    States = {}
    Identifications = {}
    Commands = {}
    Services = {}
    Mnemonics = {}
    DataIds = {}
    ext_de = []
    ecudata = {}
    minimumrefreshrate = 0.1

    def __init__(self, cecu, tran):
        self.GRAF = False
        self.elm = 0
        self.ecudata = cecu
        self.getDTCmnemo = ''
        self.resetDTCcommand = ''
        self.screens = []
        self.Defaults = {}
        self.Parameters = {}
        self.States = {}
        self.Identifications = {}
        self.Commands = {}
        self.Services = {}
        self.Mnemonics = {}
        self.DataIds = {}
        modelid = self.ecudata['ModelId'].replace('XML', 'xml')
        mdom = mod_zip.get_xml_file(modelid)
        mdoc = mdom.documentElement
        lbltxt = MyLabel(text='Loading languages', font_size=fs * 1.5, size_hint=(1, 1))
        popup_init = MyPopup(title='Initializing', content=lbltxt)
        base.runTouchApp(embedded=True)
        popup_init.open()
        lbltxt.text = 'Loading screens'
        EventLoop.idle()
        self.screens = []
        sc_class = ecu_screens(self.screens, mdoc, tran)
        lbltxt.text = 'Loading optimyzer'
        EventLoop.idle()
        self.defaults = []
        optimizerfile = self.ecudata['OptimizerId'][:-4] + '.p'
        dict = mod_zip.get_ecu_p(optimizerfile)
        lbltxt.text = 'Loading defaults'
        EventLoop.idle()
        df_class = ecu_defaults(self.Defaults, mdoc, dict, tran)
        lbltxt.text = 'Loading parameters'
        EventLoop.idle()
        pr_class = ecu_parameters(self.Parameters, mdoc, dict, tran)
        lbltxt.text = 'Loading states'
        EventLoop.idle()
        st_class = ecu_states(self.States, mdoc, dict, tran)
        lbltxt.text = 'Loading identifications'
        EventLoop.idle()
        id_class = ecu_identifications(self.Identifications, mdoc, dict, tran)
        lbltxt.text = 'Loading commands'
        EventLoop.idle()
        cm_class = ecu_commands(self.Commands, mdoc, dict, tran)
        lbltxt.text = 'Loading services'
        EventLoop.idle()
        sv_class = ecu_services(self.Services, mdoc, dict, tran)
        lbltxt.text = 'Loading mnemonics'
        EventLoop.idle()
        mm_class = ecu_mnemonics(self.Mnemonics, mdoc, dict, tran)
        lbltxt.text = 'Loading DTC commands'
        EventLoop.idle()
        self.getDTCmnemo, self.resetDTCcommand = df_class.getDTCCommands(mdoc, dict, cecu['stdType'])
        if 'DataIds' in list(dict.keys()):
            lbltxt.text = 'Loading Data ids'
            EventLoop.idle()
            xmlstr = dict['DataIds']
            ddom = xml.dom.minidom.parseString(xmlstr)
            ddoc = ddom.documentElement
            di_class = ecu_dataids(self.DataIds, ddoc, dict, tran)
        EventLoop.window.remove_widget(popup_init)
        popup_init.dismiss()
        base.stopTouchApp()
        EventLoop.window.canvas.clear()

    def initELM(self, elm):
        global ecudump
        self.calc = Calc()
        self.elm = elm
        if self.ecudata['pin'].lower() == 'can':
            self.elm.init_can()
            self.elm.set_can_addr(self.ecudata['dst'], self.ecudata)
        else:
            self.elm.init_iso()
            self.elm.set_iso_addr(self.ecudata['dst'], self.ecudata)
        self.elm.start_session(self.ecudata['startDiagReq'])
        if self.ecudata['pin'].lower()=='can' and self.DataIds and mod_globals.opt_csv:
            mod_globals.opt_perform = True
            self.elm.checkModulePerformaceLevel(self.DataIds)
        ecudump = {}

    def saveDump(self):
        reqs = len(self.Services.values())
        layout = GridLayout(cols=1, padding=fs/4, spacing=fs/4, size_hint=(1, 1))
        lbltxt = MyLabel(text='Save dump', font_size=fs, size_hint=(1, 1))
        pb = ProgressBar(max=reqs)
        layout.add_widget(lbltxt)
        layout.add_widget(pb)
        popup_init = MyPopup(title='Save dump', content=layout, size=(Window.size[0]*0.9, Window.size[1]*0.9), size_hint=(None, None))
        base.runTouchApp(embedded=True)
        popup_init.open()
        base.EventLoop.idle()
        sys.stdout.flush()
        dumpname = mod_globals.dumps_dir + str(int(time.time())) + '_' + self.ecudata['ecuname'] + '.txt'
        df = open(dumpname, 'wt')
        self.elm.clear_cache()
        i = 0
        for service in list(self.Services.values()):
            lbltxt.text='Save ' + str(i) + ' in ' + str(reqs)
            base.EventLoop.idle()
            pb.value = i
            i += 1
            if service.startReq[:2] in AllowedList:
                if service.startReq[:2] == '19' and service.startReq[:4] != '1902':
                    continue
                if service.startReq[:2] == '22' and len(service.startReq) < 6:
                    continue
                pos = chr(ord(service.startReq[0]) + 4) + service.startReq[1]
                rsp = self.elm.request(service.startReq, pos, False)
                if ':' in rsp:
                    continue
                df.write('%s:%s\n' % (service.startReq, rsp))
        df.close()
        base.EventLoop.window.remove_widget(popup_init)
        popup_init.dismiss()
        base.stopTouchApp()
        base.EventLoop.window.canvas.clear()

    def loadDump(self, dumpname = ''):

        global ecudump
        ecudump = {}
        if len(dumpname) == 0:
            flist = []
            for root, dirs, files in os.walk(mod_globals.dumps_dir):
                for f in files:
                    if self.ecudata['ecuname'] + '.txt' in f:
                        flist.append(f)

            if len(flist) == 0:
                return
            flist.sort()
            dumpname = os.path.join(mod_globals.dumps_dir, flist[-1])
        df = open(dumpname, 'rt')
        lines = df.readlines()
        df.close()
        for l in lines:
            l = l.strip().replace('\n', '')
            if ':' in l:
                req, rsp = l.split(':')
                ecudump[req] = rsp
        self.elm.setDump(ecudump)

    def get_st(self, name, no_formatting = False):
        if name not in list(self.States.keys()):
            for i in list(self.States.keys()):
                if name == self.States[i].codeMR:
                    name = i
                    break

        if name not in list(self.States.keys()):
            return ('none', 'unknown state')
        self.elm.clear_cache()
        if no_formatting:
            idName, datastr, help, csvd, icsvd = get_state(self.States[name], self.Mnemonics, self.Services, self.elm, self.calc, no_formatting)
            return (datastr, help, csvd)
        else:
            datastr, help, csvd = get_state(self.States[name], self.Mnemonics, self.Services, self.elm, self.calc)
            return (csvd, datastr)

    def get_ref_st(self, name):
        if name not in list(self.States.keys()):
            for i in list(self.States.keys()):
                if name == self.States[i].codeMR:
                    name = i
                    break

        if name not in list(self.States.keys()):
            return None
        return self.States[name]

    def get_pr(self, name, no_formatting = False):
        if name not in list(self.Parameters.keys()):
            for i in list(self.Parameters.keys()):
                if name == self.Parameters[i].codeMR and not self.Parameters[i].agcdRef.endswith('FF'):
                    name = i
                    break

        if name not in list(self.Parameters.keys()):
            return ('none', 'unknown parameter')
        self.elm.clear_cache()
        if no_formatting:
            idName, datastr, help, csvd, unit, icsvd  = get_parameter(self.Parameters[name], self.Mnemonics, self.Services, self.elm, self.calc, no_formatting)
            return (datastr, help, csvd, unit)
        else:
            datastr, help, csvd = get_parameter(self.Parameters[name], self.Mnemonics, self.Services, self.elm, self.calc)
            return (csvd, datastr)

    def get_ref_pr(self, name):
        if name not in list(self.Parameters.keys()):
            for i in list(self.Parameters.keys()):
                if name == self.Parameters[i].codeMR:
                    name = i
                    break

        if name not in list(self.Parameters.keys()):
            return None
        return self.Parameters[name]

    def get_id(self, name, no_formatting = False):
        if name not in list(self.Identifications.keys()):
            for i in list(self.Identifications.keys()):
                if name == self.Identifications[i].codeMR:
                    name = i
                    break
        if name not in list(self.Identifications.keys()):
            return ('none', 'unknown identification')
        self.elm.clear_cache()
        if no_formatting == 5:
            return get_identification( self.Identifications[name], self.Mnemonics, self.Services, self.elm, self.calc, no_formatting)
        elif no_formatting:
            idName, datastr, help, csvd = get_identification(self.Identifications[name], self.Mnemonics, self.Services, self.elm, self.calc, no_formatting)
            return (datastr, help, csvd)
        else:
            datastr, help, csvd = get_identification(self.Identifications[name], self.Mnemonics, self.Services, self.elm, self.calc)
            return (csvd, datastr)

    def get_ref_id(self, name):
        if name not in list(self.Identifications.keys()):
            for i in list(self.Identifications.keys()):
                if name == self.Identifications[i].codeMR:
                    name = i
                    break

        if name not in list(self.Identifications.keys()):
            return None
        return self.Identifications[name]

    def get_val(self, name):
        r1, r2 = self.get_st(name)
        if r1 != 'none':
            return (r1, r2)
        r1, r2 = self.get_pr(name)
        if r1 != 'none':
            return (r1, r2)
        r1, r2 = self.get_id(name)
        if r1 != 'none':
            return (r1, r2)
        return ('none', 'unknown name')

    def run_cmd(self, name, param = '', partype = 'HEX'):
        if name not in list(self.Commands.keys()):
            for i in list(self.Commands.keys()):
                if name == self.Commands[i].codeMR:
                    name = i
                    break

        if name not in list(self.Commands.keys()):
            return 'none'
        self.elm.clear_cache()
        resp = runCommand(self.Commands[name], self, self.elm, param, partype)
        return resp

    def get_ref_cmd(self, name):
        if name not in list(self.Commands.keys()):
            for i in list(self.Commands.keys()):
                if name == self.Commands[i].codeMR:
                    name = i
                    break

        if name not in list(self.Commands.keys()):
            return None
        return self.Commands[name]

    def show_commands(self, datarefs, path):
        while True:
            clearScreen()
            header = 'ECU : ' + self.ecudata['ecuname'] + '  ' + self.ecudata['doc'] + '\n'
            header = header + 'Screen : ' + path
            menu = []
            cmds = []
            for dr in datarefs:
                datastr = dr.name
                if dr.type == 'State':
                    datastr = self.States[dr.name].name + 'States not supported on one screen with commands'
                if dr.type == 'Parameter':
                    datastr = self.Parameters[dr.name].name + 'Parameters not supported on one screen with commands'
                if dr.type == 'Identification':
                    datastr = self.Identifications[dr.name].name + 'Identifications not supported on one screen with commands'
                if dr.type == 'Command':
                    datastr = self.Commands[dr.name].codeMR + ' ' + self.Commands[dr.name].label
                    cmds.append(dr.name)
                menu.append(datastr)
            menu.append('<' + mod_globals.language_dict['6218'] + '>')
            choice = ChoiceLong(menu, 'Choose :', header)
            if choice[0] == '<' + mod_globals.language_dict['6218'] + '>':
                return
            header = header + ' -> ' + cmds[int(choice[1]) - 1] + ' [Command] '
            executeCommand(self.Commands[cmds[int(choice[1]) - 1]], self, self.elm, header)
    
    def prepareCSV(self, datarefs, path):
        csvf = 0
        csvline = "sep=,\n"
        csvline += "Time,"
        nparams = 0
        for dr in datarefs:
            if dr.type=='State':
                csvline += ";" + self.States[dr.name].codeMR + (":" + self.States[dr.name].label  if mod_globals.opt_csv_human else "")
                csvline += ","
                nparams += 1
            if dr.type=='Parameter':
                csvline += (";" + self.Parameters[dr.name].codeMR + (":" +self.Parameters[dr.name].label if mod_globals.opt_csv_human else "") + 
            " [" + self.Parameters[dr.name].unit + "]")
                csvline += ","
                nparams += 1
        if nparams:
            csv_filename = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
            csv_filename = csv_filename+'_'+self.ecudata['ecuname']+'_'+path
            csv_filename += ".csv"
            csv_filename = csv_filename.replace('/','_')
            csv_filename = csv_filename.replace(' : ','_')
            csv_filename = csv_filename.replace(' -> ','_')
            csv_filename = csv_filename.replace(' ','_')
            csvf = open(mod_globals.csv_dir + csv_filename, "w")
        return csvf, csvline

    def grafic(self, path):
        graphicsScreen.datarefs = []
        menu = []
        for k, v in self.Parameters.items():
            if not v.agcdRef.endswith('FF'):
                menu.append(v.codeMR + ':' + v.label)
        menu.sort()
        choice = ChoiceSelect(menu, 'Choose :')
        if choice[0] == '<' + mod_globals.language_dict['6218'] + '>':
            return
        #choice[2] = ['PR364', 'PR365', 'PR405', 'PR406']
        if choice[2]:
            for i in choice[2]:
                self.addGraf(i)
            self.GRAF = True
            self.show_screen(graphicsScreen)

    def show_datarefs(self, datarefs, path):
        print('show_datarefs')
        global resizeFont
        csvf = 0
        mask = False
        masks = []
        datarefsToRemove = []

        for st in self.States:
            if st.startswith('MAS'):
                mask = True
                get_state( self.States[st], self.Mnemonics, self.Services, self.elm, self.calc )
                if self.States[st].value.strip().isdigit():
                    masks.append(self.States[st].name)
        
        if mask:
            for dr in datarefs:
                if dr.type=='State':
                    if self.States[dr.name].mask and self.States[dr.name].mask not in masks:
                        datarefsToRemove.append(dr)
                if dr.type=='Parameter':
                    if self.Parameters[dr.name].mask and self.Parameters[dr.name].mask not in masks:
                        datarefsToRemove.append(dr)
                if dr.type=='Identification':
                    if self.Identifications[dr.name].mask and self.Identifications[dr.name].mask not in masks:
                        datarefsToRemove.append(dr)
                if dr.type=='Command':
                    if self.Commands[dr.name].mask and self.Commands[dr.name].mask not in masks:
                        datarefsToRemove.append(dr)
            for dr in datarefsToRemove:
                datarefs.remove(dr)
        
        for dr in datarefs:
            if dr.type == 'Command':
                self.show_commands(datarefs, path)
                return

        while 1:
            print('showDatarefGui')
            loop = asyncio.get_event_loop()
            gui = showDatarefGui(self, datarefs, path)
            gui.run()
            if not resizeFont:
                return
            resizeFont = False

        kb = KBHit()
        tb = time.time()
        if len(datarefs) == 0 and 'DE' not in path:
            return
        page = 0
        while True:
            strlst = []
            if mod_globals.opt_csv and csvf != 0:
                csvline = csvline + '\n'
                # csvline = csvline.replace('.', ',')
                csvline = csvline.replace(';', '\t')
                csvf.write(pyren_decode(csvline).encode('utf8') if mod_globals.opt_csv_human else csvline)
                csvf.flush()
                csvline = datetime.now().strftime('%H:%M:%S,%f,')
            self.elm.clear_cache()
            if mod_globals.opt_csv and mod_globals.opt_csv_only:
                clearScreen()
            for dr in datarefs:
                datastr = dr.name
                help = dr.type
                if dr.type == 'State':
                    datastr, help, csvd = get_state(self.States[dr.name], self.Mnemonics, self.Services, self.elm, self.calc)
                if dr.type == 'Parameter':
                    datastr, help, csvd = get_parameter(self.Parameters[dr.name], self.Mnemonics, self.Services, self.elm, self.calc)
                if dr.type == 'Identification':
                    datastr, help, csvd = get_identification(self.Identifications[dr.name], self.Mnemonics, self.Services, self.elm, self.calc)
                if dr.type == 'Command':
                    datastr = dr.name + ' [Command] ' + self.Commands[dr.name].label
                if mod_globals.opt_csv and csvf != 0 and (dr.type == 'State' or dr.type == 'Parameter'):
                    csvline += ';' + (pyren_encode(csvd) if mod_globals.opt_csv_human else str(csvd))
                if not (mod_globals.opt_csv and mod_globals.opt_csv_only):
                    strlst.append(datastr)
                    if mod_globals.opt_verbose and len(help) > 0:
                        tmp_str = ''
                        for s in help:
                            s = s.replace('\r', '\n')
                            s = s.replace('&gt;', '>')
                            s = s.replace('&le;', '<')
                            tmp_str = tmp_str + s + '\n\n'

                        W = 50
                        for line in tmp_str.split('\n'):
                            i = 0
                            while i * W < len(line):
                                strlst.append('\t' + line[i * W:(i + 1) * W])
                                i = i + 1

                        strlst.append('')

            if not (mod_globals.opt_csv and mod_globals.opt_csv_only):
                clearScreen()
                header = 'ECU : ' + self.ecudata['ecuname'] + '  ' + self.ecudata['doc'] + '\n'
                header = header + 'Screen : ' + path
                H = 25
                pages = len(strlst) / H
                if mod_globals.opt_demo:
                    self.minimumrefreshrate = 1
                tc = time.time()
                if tc - tb < self.minimumrefreshrate:
                    time.sleep(tb + self.minimumrefreshrate - tc)
                tb = tc
            if kb.kbhit():
                c = kb.getch()
                if len(c) != 1:
                    continue
                n = ord(c) - ord('0')
                if not mod_globals.opt_csv_only and n > 0 and n <= pages + 1:
                    page = n - 1
                    continue
                if mod_globals.opt_csv and c in mod_globals.opt_usrkey:
                    csvline += ';' + c
                    continue
                kb.set_normal_term()
                if mod_globals.opt_csv and csvf != 0:
                    csvf.close()
                return

    def show_subfunction(self, subfunction, path):
        print('show_subfunction')
        while 1:
            clearScreen()
            if len(subfunction.datarefs) != 0 and len(subfunction.datarefs) > 0:
                self.show_datarefs(subfunction.datarefs, path + ' -> ' + subfunction.text)
                return
            return

    def show_function(self, function, path):
        print('show_function')
        while 1:
            clearScreen()
            menu = []
            if len(function.subfunctions) != 0:
                for sfu in function.subfunctions:
                    menu.append(sfu.text)
                menu.append('<' + mod_globals.language_dict['6218'] + '>')
                choice = Choice(menu, 'Choose :')
                if choice[0] == '<' + mod_globals.language_dict['6218'] + '>':
                    return
                self.show_subfunction(function.subfunctions[int(choice[1]) - 1], path + ' -> ' + function.text)
            if len(function.datarefs) != 0:
                self.show_datarefs(function.datarefs, path + ' -> ' + function.text)
                return

    def show_screen(self, screen):
        print('show_screen')
        while 1:
            clearScreen()
            menu = []
            if len(screen.functions) != 0:
                for fu in screen.functions:
                    menu.append(fu.text)
                menu.append('<' + mod_globals.language_dict['6218'] + '>')
                choice = Choice(menu, 'Choose :')
                if choice[0] == '<' + mod_globals.language_dict['6218'] + '>':
                    return
                self.show_function(screen.functions[int(choice[1]) - 1], screen.name)
            if len(screen.datarefs) != 0:
                self.show_datarefs(screen.datarefs, screen.name)
                return

    def show_defaults_std_a(self, dt=None):
        print('show_defaults_std_a')
        while 1:
            clearScreen()
            path = 'DE (STD_A)'
            header = 'ECU : ' + self.ecudata['ecuname'] + '  ' + self.ecudata['doc'] + '\n'
            header = header + 'Screen : ' + path
            menu = []
            defstr = {}
            hlpstr = {}
            self.elm.clear_cache()
            dtcs, defstr, hlpstr = get_default_std_a(self.Defaults, self.Mnemonics, self.Services, self.elm, self.calc, self.getDTCmnemo)
            listkeys = list(defstr.keys())
            for d in listkeys:
                menu.append(defstr[d])

            menu.append('<' + mod_globals.language_dict['6218'] + '>')
            menu.append('<' + mod_globals.language_dict['256'] + '>')
            choice = Choice(menu, 'Choose one for detailed view or <' + mod_globals.language_dict['256'] + '>:')
            if choice[0] == '<' + mod_globals.language_dict['6218'] + '>':
                mod_globals.ext_cur_DTC = '000000'
                return
            if choice[0] == '<' + mod_globals.language_dict['256'] + '>':
                executeCommand(self.Commands[self.resetDTCcommand], self, self.elm, header)
                return
            index = int(choice[1]) - 1
            dtchex = listkeys[index] if len(listkeys) > index else listkeys[0]
            mod_globals.ext_cur_DTC = dtchex

            path = path + ' -> ' + defstr[dtchex] + '\n\n' + hlpstr[dtchex] + '\n'

            tmp_helpString = defstr[dtchex] + '\n\n' + hlpstr[dtchex]

            cur_dtrf = []
            mem_dtrf = []

            helpString = [ecu_screen_dataref(0, tmp_helpString, 'DTCText')]
            
            if self.Defaults[dtchex[:4]].datarefs:
                cur_dtrf = [ecu_screen_dataref(0, mod_globals.language_dict['300'], 'Text')] + self.Defaults[dtchex[:4]].datarefs
            if self.Defaults[dtchex[:4]].memDatarefs:
                mem_dtrf_txt = mod_globals.language_dict['299'] + " DTC" + mod_globals.ext_cur_DTC
                mem_dtrf = [ecu_screen_dataref(0, mem_dtrf_txt, 'Text')] + self.Defaults[dtchex[:4]].memDatarefs
            
            tmp_dtrf = helpString + mem_dtrf + cur_dtrf
            self.show_datarefs(tmp_dtrf, path)

    def show_defaults_std_b(self):
        print('show_defaults_std_b')
        while 1:
            clearScreen()
            path = 'DE (STD_B)'
            header = 'ECU : ' + self.ecudata['ecuname'] + '  ' + self.ecudata['doc'] + '\n'
            header = header + 'Screen : ' + path
            menu = []
            defstr = {}
            hlpstr = {}
            self.elm.clear_cache()
            dtcs, defstr, hlpstr = get_default_std_b(self.Defaults, self.Mnemonics, self.Services, self.elm, self.calc, self.getDTCmnemo)
            listkeys = list(defstr.keys())
            for d in listkeys:
                menu.append(defstr[d])

            menu.append('<' + mod_globals.language_dict['6218'] + '>')
            menu.append('<' + mod_globals.language_dict['256'] + '>')
            choice = Choice(menu, 'Choose one for detailed view or <' + mod_globals.language_dict['256'] + '>:')
            if choice[0] == '<' + mod_globals.language_dict['6218'] + '>':
                mod_globals.ext_cur_DTC = '000000'
                return
            if choice[0] == '<' + mod_globals.language_dict['256'] + '>':
                executeCommand(self.Commands[self.resetDTCcommand], self, self.elm, header)
                return
            index = int(choice[1]) - 1
            dtchex = listkeys[index] if len(listkeys) > index else listkeys[0]
            mod_globals.ext_cur_DTC = dtchex
            path = path + ' -> ' + defstr[dtchex] + '\n\n' + hlpstr[dtchex] + '\n'

            tmp_helpString = defstr[dtchex] + '\n\n' + hlpstr[dtchex]

            cur_dtrf = []
            mem_dtrf = []
            ext_info_dtrf = []

            helpString = [ecu_screen_dataref(0, tmp_helpString, 'DTCText')]
            if self.ext_de:
                ext_info_dtrf = [ecu_screen_dataref(0, mod_globals.language_dict['1691'], 'Text')] + self.ext_de
            if self.Defaults[dtchex[:4]].datarefs:
                cur_dtrf = [ecu_screen_dataref(0, mod_globals.language_dict['300'], 'Text')] + self.Defaults[dtchex[:4]].datarefs
            if self.Defaults[dtchex[:4]].memDatarefs:
                mem_dtrf_txt = mod_globals.language_dict['299'] + " DTC" + mod_globals.ext_cur_DTC
                mem_dtrf = [ecu_screen_dataref(0, mem_dtrf_txt, 'Text')] + self.Defaults[dtchex[:4]].memDatarefs
            tmp_dtrf = helpString + ext_info_dtrf + mem_dtrf + cur_dtrf   
            self.show_datarefs(tmp_dtrf, path)

    def show_defaults_failflag(self):
        print('show_defaults_failflag')
        while 1:
            path = 'DE (FAILFLAG)'
            clearScreen()
            header = 'ECU : ' + self.ecudata['ecuname'] + '  ' + self.ecudata['doc'] + '\n'
            header = header + 'Screen : ' + path
            menu = []
            defstr = {}
            hlpstr = {}
            self.elm.clear_cache()
            dtcs, defstr, hlpstr = get_default_failflag(self.Defaults, self.Mnemonics, self.Services, self.elm, self.calc)
            for d in sorted(defstr.keys()):
                menu.append(defstr[d])
            menu.append('<' + mod_globals.language_dict['6218'] + '>')
            menu.append('<' + mod_globals.language_dict['256'] + '>')
            choice = Choice(menu, 'Choose one for detailed view or <' + mod_globals.language_dict['256'] + '>:')
            if choice[0] == '<' + mod_globals.language_dict['6218'] + '>':
                return
            if choice[0] == '<' + mod_globals.language_dict['256'] + '>':
                executeCommand(self.Commands[self.resetDTCcommand], self, self.elm, header)
                return
            dtchex = dtcs[int(choice[1]) - 1]
            path = path + ' -> ' + defstr[dtchex] + '\n\n' + hlpstr[dtchex] + '\n'
            tmp_helpString = defstr[dtchex] + '\n\n' + hlpstr[dtchex]
            helpString = [ecu_screen_dataref(0, tmp_helpString, 'DTCText')]
            self.show_datarefs(helpString + self.Defaults[dtchex].datarefs, path)

    def show_screens(self):
        print('show_screens')
        if mod_globals.test: self.screens.append(graphicsScreen)
        self.screens.append(favouriteScreen)
        while 1:
            clearScreen()
            header = 'ECU : ' + self.ecudata['ecuname'] + '  ' + self.ecudata['doc'] + '\n'
            menu = []
            for l in self.screens:
                if l.name == 'DE':
                    l.name = 'DE : ' + mod_globals.language_dict['260']
                if l.name == 'ID':
                    l.name = 'ID : ' + mod_globals.language_dict['2140']
                if l.name == 'SY':
                    l.name = 'SY : ' + mod_globals.language_dict['251']
                if l.name == 'LC':
                    l.name = 'LC : ' + mod_globals.language_dict['517']
                if l.name == 'SP':
                    l.name = 'SP : ' + mod_globals.language_dict['297']
                if l.name == 'AC':
                    l.name = 'AC : ' + mod_globals.language_dict['262']
                if l.name == 'CF':
                    l.name = 'CF : '  + mod_globals.language_dict['8362']
                if l.name == 'VP':
                    l.name = 'VP : ' + mod_globals.language_dict['268']
                if l.name == 'RZ':
                    l.name = 'RZ : ' + mod_globals.language_dict['4416']
                if l.name == 'SC':
                    l.name = 'SC : ' + mod_globals.language_dict['267']
                if l.name == 'SCS':
                    if mod_globals.opt_lang == 'RU':
                        l.name = 'SCS : Сценарии настройки безопасности'
                    else:
                        l.name = 'SCS : Security configuration scenarios'
                if l.name == 'EZ':
                    l.name = 'EZ : EZSTEP'
                if mod_globals.test:
                    if l.name == 'GR':
                        l.name = 'GR: ' + mod_globals.language_dict['4283']
                if l.name == 'FAV':
                    l.name = 'FAV : ' + mod_globals.language_dict['26330']
                if l.name == 'ED':
                    self.ext_de = l.datarefs
                    l.name = 'ED : ' + mod_globals.language_dict['638']
                    continue
                menu.append(l.name)
            
            
            if mod_globals.opt_cmd:
                if mod_globals.opt_lang == 'RU':
                    menu.append('ECM : Расширенный набор команд')
                else:
                    menu.append('ECM : Extended command set')
            if mod_globals.opt_demo:
                if self.Parameters : menu.append('PRA : ' + mod_globals.language_dict['2496'])
                if self.States : menu.append('ETA : ' + mod_globals.language_dict['2497'])
                if self.Identifications :
                    if mod_globals.opt_lang == 'RU':
                        menu.append('IDA : ВСЕ ИДЕНТИФИКАЦИИ')
                    else:
                        menu.append('IDA : ALL IDENTIFICATIONS')
            menu.append('<' + mod_globals.language_dict['6218'] + '>')
            if mod_globals.opt_lang == 'RU':
                choice = Choice(menu, 'Выбор :')
            else:
                choice = Choice(menu, 'Choose :')
            if choice[0] == '<' + mod_globals.language_dict['6218'] + '>':
                favouriteScreen.datarefs = []
                graphicsScreen.datarefs = []
                return
            if choice[0][:2] == 'GR':
                self.grafic(choice)
                continue
            if choice[0][:2] == 'DE':
                if self.ecudata['stdType'] == 'STD_A':
                    self.show_defaults_std_a()
                if self.ecudata['stdType'] == 'STD_B' or self.ecudata['stdType'] == 'UDS':
                    self.show_defaults_std_b()
                if self.ecudata['stdType'] == 'FAILFLAG':
                    self.show_defaults_failflag()
                continue
            if choice[0][:3] == 'ECM':
                scrn = ecu_screen('ECM')
                scrn.datarefs = []
                for cm in sorted(self.Commands):
                    scrn.datarefs.append(ecu_screen_dataref('', cm, 'Command'))
                self.show_screen(scrn)
                continue
            if choice[0][:3]=="PRA":  
                scrn = ecu_screen( "PRA" ) 
                scrn.datarefs = []
                tempDict = {}
                for pr in self.Parameters:
                    if not self.Parameters[pr].agcdRef.endswith('FF'):
                        tempDict[pr] = self.Parameters[pr].codeMR
                sortedParams = sorted(list(tempDict.items()), key=lambda x:int(x[1][2:]))
                for pr in sortedParams:
                    if self.Parameters[pr[0]].mnemolist:
                        if self.Mnemonics[self.Parameters[pr[0]].mnemolist[0]].serviceID:
                            scrn.datarefs.append( ecu_screen_dataref("",pr[0],"Parameter")) 
                self.show_screen(scrn)
                continue
              
            if choice[0][:3]=="ETA":  
                scrn = ecu_screen( "ETA" ) 
                scrn.datarefs = []
                tempDict = {}
                for st in self.States:
                    if not self.States[st].agcdRef.endswith('FF') and self.States[st].agcdRef.startswith('ET'):
                        tempDict[st] = self.States[st].codeMR
                sortedStates = sorted(list(tempDict.items()), key=lambda x:[int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', x[1])])
                for st in sortedStates:
                    if self.States[st[0]].mnemolist:
                        if self.Mnemonics[self.States[st[0]].mnemolist[0]].serviceID:
                            scrn.datarefs.append( ecu_screen_dataref("",st[0],"State")) 
                self.show_screen(scrn)
                continue

            if choice[0][:3]=="IDA":  
                scrn = ecu_screen( "IDA" ) 
                scrn.datarefs = []
                for idk in sorted(self.Identifications):
                    scrn.datarefs.append( ecu_screen_dataref("",idk,"Identification")) 
                self.show_screen(scrn)
                continue
              
            if choice[0][:3] == 'FAV':
                if not favouriteScreen.datarefs:
                    if self.loadFavList():
                        self.show_screen(favouriteScreen)
                    else:
                        clearScreen()
                else:
                    self.show_screen(favouriteScreen)
                continue
            self.show_screen(self.screens[int(choice[1]) - 1])

    def addGraf(self, elem):
        if elem[:2] == 'PR':
            for pr in list(self.Parameters.keys()):
                if self.Parameters[pr].agcdRef == elem:
                    if not any(pr == dr.name for dr in graphicsScreen.datarefs):
                        graphicsScreen.datarefs.append(ecu_screen_dataref('',pr,'Parameter'))
                        return False
                    else:
                        for dr in graphicsScreen.datarefs:
                            if pr == dr.name:
                                graphicsScreen.datarefs.remove(dr)
                                clearScreen()
        elif elem[:2] == 'ET':
            for st in list(self.States.keys()):
                if self.States[st].agcdRef == elem:
                    if not any(st == dr.name for dr in graphicsScreen.datarefs):
                        graphicsScreen.datarefs.append(ecu_screen_dataref('',st,'State'))
                        return False
                    else:
                        for dr in graphicsScreen.datarefs:
                            if st == dr.name:
                                graphicsScreen.datarefs.remove(dr)
                                clearScreen()
        elif elem[:2] == 'ID':
            for idk in list(self.Identifications.keys()):
                if self.Identifications[idk].agcdRef == elem:
                    if not any(idk == dr.name for dr in graphicsScreen.datarefs):
                        graphicsScreen.datarefs.append(ecu_screen_dataref("",idk,"Identification"))
                        return False
                    else:
                        for dr in graphicsScreen.datarefs:
                            if idk == dr.name:
                                graphicsScreen.datarefs.remove(dr)
                                clearScreen()
        else:
            return False

    def addElem(self, elem):
        if elem[:2] == 'PR':
            for pr in list(self.Parameters.keys()):
                if self.Parameters[pr].agcdRef == elem:
                    if not any(pr == dr.name for dr in favouriteScreen.datarefs):
                        favouriteScreen.datarefs.append(ecu_screen_dataref('',pr,'Parameter'))
                        return False
                    else:
                        for dr in favouriteScreen.datarefs:
                            if pr == dr.name:
                                favouriteScreen.datarefs.remove(dr)
                                clearScreen()
        elif elem[:2] == 'ET':
            for st in list(self.States.keys()):
                if self.States[st].agcdRef == elem:
                    if not any(st == dr.name for dr in favouriteScreen.datarefs):
                        favouriteScreen.datarefs.append(ecu_screen_dataref('',st,'State'))
                        return False
                    else:
                        for dr in favouriteScreen.datarefs:
                            if st == dr.name:
                                favouriteScreen.datarefs.remove(dr)
                                clearScreen()
        elif elem[:2] == 'ID':
            for idk in list(self.Identifications.keys()):
                if self.Identifications[idk].agcdRef == elem:
                    if not any(idk == dr.name for dr in favouriteScreen.datarefs):
                        favouriteScreen.datarefs.append(ecu_screen_dataref("",idk,"Identification"))
                        return False
                    else:
                        for dr in favouriteScreen.datarefs:
                            if idk == dr.name:
                                favouriteScreen.datarefs.remove(dr)
                                clearScreen()
        else:
            return False

    def loadFavList(self):
        fn = mod_globals.cache_dir + 'favlist_' + self.ecudata['ecuname'] + '.txt'

        if not os.path.isfile(fn):
            favlistfile = open(fn, 'wb')
            favlistfile.close()
        
        fl = open(fn, 'r').readlines()
        if len(fl):
            for drname in fl:
                drname = drname.strip().replace('\n','')
                if not (drname.startswith('PR') or drname.startswith('ET') or drname.startswith("ID")):
                    return False
                else:
                    self.addElem(drname)
            return True
        else:
            return False

    def saveFavList(self):
        fl = open(mod_globals.cache_dir + 'favlist_' +self.ecudata['ecuname']+".txt", "w")
        for dr in favouriteScreen.datarefs:
            if dr.name.startswith('P'):
                for pr in list(self.Parameters.keys()):
                    if dr.name == pr:
                        fl.write(self.Parameters[pr].agcdRef + "\n")
            if dr.name.startswith('E'):
                for st in list(self.States.keys()):
                    if dr.name == st:
                        fl.write(self.States[st].agcdRef + "\n")
            if dr.name.startswith('I'):
                for idk in list(self.Identifications.keys()):
                    if dr.name == idk:
                        fl.write(self.Identifications[idk].agcdRef + "\n")
        fl.close()

    def getLanguageMap(self):
        map = {}
        for i in sorted(self.Parameters.keys()):
            m = self.Mnemonics[self.Parameters[i].mnemolist[0]]
            label = self.Parameters[i].label
            if 'ETAT' in label:
                continue
            if len(self.Parameters[i].mnemolist) != 1:
                continue
            if m.bitsLength == '':
                continue
            if m.startBit == '':
                continue
            if m.startByte == '':
                continue
            key = '%s:%s:%s:%s' % (m.request,
             m.startByte,
             m.startBit,
             m.bitsLength)
            map[key] = label

        for i in sorted(self.States.keys()):
            m = self.Mnemonics[self.States[i].mnemolist[0]]
            label = self.States[i].label
            if 'ETAT' in label:
                continue
            if len(self.States[i].mnemolist) != 1:
                continue
            if m.bitsLength == '':
                continue
            if m.startBit == '':
                continue
            if m.startByte == '':
                continue
            bitsLength = m.bitsLength
            startBit = m.startBit
            comp = self.States[i].computation
            if m.name + '#' in comp:
                comp = comp.split(m.name + '#')[1]
                startBit = 7 - int(comp[0])
                bitsLength = 1
            key = '%s:%s:%s:%s' % (m.request,
             m.startByte,
             startBit,
             bitsLength)
            map[key] = label

        return map

    def getDataIds(self, cache, dataids):
        dataIdsList = []
        if self.elm.performanceModeLevel == 1:
            return dataIdsList
        
        for key in cache:
            if key.startswith('22'):
                if key[2:] in list(dataids.keys()):
                    dataIdsList.append(dataids[key[2:]])

        chunk_size = self.elm.performanceModeLevel
        if dataIdsList:
            return [dataIdsList[offset:offset+chunk_size] for offset in range(0, len(dataIdsList), chunk_size)]
        
        return dataIdsList

def bukva(bt, l, sign = False):
    S1 = chr((bt - l) % 26 + ord('A'))
    ex = int(bt - l) / 26
    if ex:
        S2 = chr((ex - 1) % 26 + ord('A'))
        S1 = S2 + S1
    if sign:
        S1 = 'signed(' + S1 + ')'
    return S1


def gen_equ(m):
    l = len(m.request) / 2 + 1
    sb = int(m.startByte)
    bits = int(m.bitsLength)
    sbit = int(m.startBit)
    bytes = (bits + sbit - 1) / 8 + 1
    rshift = ((bytes + 1) * 8 - (bits + sbit)) % 8
    mask = str(2 ** bits - 1)
    if m.type.startswith('SNUM'):
        sign = True
    else:
        sign = False
    equ = bukva(sb, l)
    if bytes == 2:
        equ = bukva(sb, l, sign) + '*256+' + bukva(sb + 1, l)
    if bytes == 3:
        equ = bukva(sb, l, sign) + '*65536+' + bukva(sb + 1, l) + '*256+' + bukva(sb + 2, l)
    if bytes == 4:
        equ = bukva(sb, l, sign) + '*16777216+' + bukva(sb + 1, l) + '*65536+' + bukva(sb + 2, l) + '*256+' + bukva(sb + 3, l)
    if m.littleEndian == '1':
        if bytes == 2:
            equ = bukva(sb + 1, l, sign) + '*256+' + bukva(sb, l)
        if bytes == 3:
            equ = bukva(sb + 2, l, sign) + '*65536+' + bukva(sb + 1, l) + '*256+' + bukva(sb, l)
        if bytes == 4:
            equ = bukva(sb + 3, l, sign) + '*16777216+' + bukva(sb + 2, l) + '*65536+' + bukva(sb + 1, l) + '*256+' + bukva(sb, l)
    if len(equ) > 2:
        if equ[0] == '(' and equ[-1] == ')':
            pass
        else:
            equ = '(' + equ + ')'
    if bits % 8:
        smask = '&' + mask
    else:
        smask = ''
    if bits == 1:
        equ = '{' + equ + ':' + str(rshift) + '}'
    elif rshift == 0:
        equ += smask
    else:
        equ = '(' + equ + '>' + str(rshift) + ')' + smask
    if len(equ) > 2:
        if equ[0] == '(' and equ[-1] == ')' or equ[0] == '{' and equ[-1] == '}':
            pass
    else:
        equ = '(' + equ + ')'
    return equ


def find_real_ecuid(eid):
    fastinit = ''
    slowinit = ''
    protocol = ''
    candst = ''
    startDiagReq = '10C0'
    DOMTree = xml.dom.minidom.parse(mod_zip.get_uces())
    Ecus = DOMTree.documentElement
    EcuDatas = Ecus.getElementsByTagName('EcuData')
    if EcuDatas:
        for EcuData in EcuDatas:
            name = EcuData.getAttribute('name')
            if name == eid:
                if EcuData.getElementsByTagName('ModelId').item(0).firstChild:
                    eid = EcuData.getElementsByTagName('ModelId').item(0).firstChild.nodeValue
                else:
                    eid = name
                ecui = EcuData.getElementsByTagName('ECUInformations')
                if ecui:
                    fastinit_tag = ecui.item(0).getElementsByTagName('FastInitAddress')
                    if fastinit_tag:
                        fastinit = fastinit_tag.item(0).getAttribute('value')
                    slowinit_tag = ecui.item(0).getElementsByTagName('SlowInitAddress')
                    if slowinit_tag:
                        slowinit = slowinit_tag.item(0).getAttribute('value')
                    protocol_tag = ecui.item(0).getElementsByTagName('Protocol')
                    if protocol_tag:
                        protocol = protocol_tag.item(0).getAttribute('value')
                    addr = ecui.item(0).getElementsByTagName('Address')
                    if addr:
                        candst = addr.item(0).getAttribute('targetAddress')
                    frms = ecui.item(0).getElementsByTagName('Frames')
                    if frms:
                        StartDiagSession = frms.item(0).getElementsByTagName('StartDiagSession')
                        if StartDiagSession:
                            startDiagReq = StartDiagSession.item(0).getAttribute('request')
                break

    if len(eid) > 5:
        eid = eid.upper().replace('FG', '')
        eid = eid.upper().replace('.XML', '')
    return (eid,
     fastinit,
     slowinit,
     protocol,
     candst,
     startDiagReq)


def main():
    try:
        import androidhelper as android
        mod_globals.os = 'android'
    except:
        try:
            import android
            mod_globals.os = 'android'
        except:
            pass

    if mod_globals.os == 'android':
        ecuid = input('Enetr  ECU ID:')
        lanid = input('Language [RU]:')
        if len(lanid) < 2:
            lanid = 'RU'
        sys.argv.append(ecuid)
        sys.argv.append(lanid)
        sys.argv.append('TORQ')
    if len(sys.argv) < 3:
        sys.exit(0)
    ecuid = sys.argv[1]
    lanid = sys.argv[2]
    if len(ecuid) == 5:
        ecuid, fastinit, slowinit, protocol, candst, startDiagReq = find_real_ecuid(ecuid)
        sys.argv[1] = ecuid
    Defaults = {}
    Parameters = {}
    States = {}
    Identifications = {}
    Commands = {}
    Services = {}
    Mnemonics = {}
    sys.stdout.flush()
    lang = optfile('../Location/DiagOnCAN_' + lanid + '.bqm', True)
    sys.stdout.flush()
    mdom = mod_zip.get_xml_file('FG' + ecuid + '.xml')
    sgfile = 'SG' + ecuid + '.xml'
    mdoc = mdom.documentElement
    sys.stdout.flush()
    opt_file = optfile(sgfile, False, True, True)
    df_class = ecu_defaults(Defaults, mdoc, opt_file.dict, lang.dict)
    pr_class = ecu_parameters(Parameters, mdoc, opt_file.dict, lang.dict)
    st_class = ecu_states(States, mdoc, opt_file.dict, lang.dict)
    id_class = ecu_identifications(Identifications, mdoc, opt_file.dict, lang.dict)
    cm_class = ecu_commands(Commands, mdoc, opt_file.dict, lang.dict)
    mm_class = ecu_mnemonics(Mnemonics, mdoc, opt_file.dict, lang.dict)
    if len(sys.argv) == 3:
        sys.exit(0)
    if len(sys.argv) > 3 and sys.argv[3].upper() != 'TORQ':
        sys.exit(0)
    family = sys.argv[1][:2]
    eindex = sys.argv[1][2:]
    sss = snat[F2A[family]]
    ddd = dnat[F2A[family]]
    filename = 'PR_' + ddd + '_' + sss + '_' + eindex + '_' + sys.argv[2] + '.csv'
    if mod_globals.os == 'android' and os.path.exists('/sdcard/.torque/extendedpids'):
        filename = '/sdcard/.torque/extendedpids/' + filename
    cf = open(filename, 'w')
    line = '%s,%s,%s,%s,%s,%s,%s,%s\n' % ('name', 'ShortName', 'ModeAndPID', 'Equation', 'Min Value', 'Max Value', 'Units', 'Header')
    cf.write(line)
    memIt = []
    for i in sorted(Parameters.keys()):
        if Parameters[i].codeMR in memIt:
            continue
        else:
            memIt.append(Parameters[i].codeMR)
        m = Parameters[i].mnemolist[0]
        if len(Parameters[i].mnemolist) != 1:
            continue
        if '?' in Parameters[i].computation:
            if len(sys.argv) == 5 and sys.argv[4].upper() == 'NOCHK':
                pass
            else:
                continue
        if Mnemonics[m].bitsLength == '':
            continue
        if Mnemonics[m].startBit == '':
            continue
        if Mnemonics[m].startByte == '':
            continue
        equ = gen_equ(Mnemonics[m])
        c_name = Parameters[i].label.replace(',', '.')
        c_short = Parameters[i].codeMR
        c_pid = Mnemonics[m].request
        c_equ = Parameters[i].computation.replace(m, equ)
        c_min = Parameters[i].min
        c_max = Parameters[i].max
        c_unit = Parameters[i].unit
        line = '"[PR]%s","%s","%s","%s","%s","%s","%s","%s"\n' % (c_name,
         c_short,
         c_pid,
         c_equ,
         c_min,
         c_max,
         c_unit,
         ddd)
        cf.write(line)

    memIt = []
    for i in sorted(States.keys()):
        if States[i].codeMR in memIt:
            continue
        else:
            memIt.append(States[i].codeMR)
        m = States[i].mnemolist[0]
        if len(States[i].mnemolist) != 1:
            continue
        if Mnemonics[m].bitsLength == '':
            continue
        if Mnemonics[m].startBit == '':
            continue
        if Mnemonics[m].startByte == '':
            continue
        equ = gen_equ(Mnemonics[m])
        c_name = States[i].label.replace(',', '.')
        c_short = States[i].codeMR
        c_pid = Mnemonics[m].request
        if len(sys.argv) == 5 and sys.argv[4].upper() == 'NOCHK':
            c_equ = States[i].computation.replace(m, equ)
        else:
            c_equ = equ
        c_min = '0'
        c_max = '0'
        c_unit = ''
        line = '"[ST]%s","%s","%s","%s","%s","%s","%s","%s"\n' % (c_name,
         c_short,
         c_pid,
         c_equ,
         c_min,
         c_max,
         c_unit,
         ddd)
        cf.write(line)

    cf.close()
    can250init = 'ATAL\\nATSH' + ddd + '\\nATCRA' + sss + '\\nATFCSH' + ddd + '\\nATFCSD300000\\nATFCSM1\\nATSP8\\n' + startDiagReq
    can500init = 'ATAL\\nATSH' + ddd + '\\nATCRA' + sss + '\\nATFCSH' + ddd + '\\nATFCSD300000\\nATFCSM1\\nATSP6\\n' + startDiagReq
    slow05init = 'ATSH81' + F2A[family] + 'F1\\nATSW96\\nATIB10\\nATSP4\\nATSI\\n' + startDiagReq
    fast10init = 'ATSH81' + F2A[family] + 'F1\\nATSW96\\nATIB10\\nATSP5\\nATFI\\n' + startDiagReq
    profilename = str(int(time.time())) + '.tdv'
    if mod_globals.os == 'android' and os.path.exists('/sdcard/.torque/vehicles'):
        profilename = '/sdcard/.torque/vehicles/' + str(int(time.time())) + '.tdv'
    prn = open(profilename, 'w')
    prn.write('#This is an ECU profile generated by pyren\n')
    prn.write('fuelType=0\n')
    prn.write('obdAdjustNew=1.0\n')
    prn.write('lastMPG=0.0\n')
    prn.write('tankCapacity=295.5\n')
    prn.write('volumetricEfficiency=85.0\n')
    prn.write('weight=1400.0\n')
    prn.write('odoMeter=0.0\n')
    prn.write('adapterName=OBDII [00\\:00\\:00\\:00\\:00\\:0]\n')
    prn.write('adapter=00\\:00\\:00\\:00\\:00\\:00\n')
    prn.write('boostAdjust=0.0\n')
    prn.write('mpgAdjust=1.0\n')
    prn.write('fuelCost=0.18000000715255737\n')
    prn.write('ownProfile=false\n')
    prn.write('displacement=1.6\n')
    prn.write('tankUsed=147.75\n')
    prn.write('lastMPGCount=0\n')
    prn.write('maxRpm=7000\n')
    prn.write('fuelDistance=0.0\n')
    prn.write('fuelUsed=0.0\n')
    prn.write('alternateHeader=true\n')
    prn.write(('name=PR_' + ecuid + '\n'))
    if len(candst) > 1:
        prn.write(('customInit=' + can500init.replace('\\', '\\\\') + '\n'))
        prn.write('preferredProtocol=7\n')
    elif len(fastinit) > 1:
        prn.write(('customInit=' + fast10init.replace('\\', '\\\\') + '\n'))
        prn.write('preferredProtocol=6\n')
    else:
        prn.write(('customInit=' + slow05init.replace('\\', '\\\\') + '\n'))
        prn.write('preferredProtocol=5\n')
    prn.close()

if __name__ == '__main__':
    main()