# -*- coding: utf-8 -*-
import os, sys, atexit, subprocess, string, signal, glob
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
from kivy import base
from kivy.uix.popup import Popup
import kivy.metrics
from mod_ecu_screen import *

import mod_globals

widgetglobal = None
choice_result = None
resizeFont = False
favouriteScreen = ecu_own_screen('FAV')
fmn = 2
bmn = 2.5

try:
    import webbrowser
except:
    pass

def InfoPopup(bas=None):
    fs = mod_globals.fontSize
    pop = MyPopup(content=MyLabel(text='LOADING', size_hint = (1, 1), font_size=fs*3, halign = 'center'))
    if not bas:
        base.runTouchApp(embedded=True)
    pop.open()
    base.EventLoop.idle()
    pop.dismiss()
    if not bas:
        base.stopTouchApp()

def MyPopup_close(title='', cont=True, l=True, op=True):
    fs = mod_globals.fontSize
    layout = GridLayout(cols=1, padding=5, spacing=10, size_hint=(1, 1))
    if not l:
        t = 'CLOSE'
    else:
        t = get_message_by_id('16831')
    btn = MyButton(text=t, size_hint=(1, None), font_size=fs*2)
    layout.add_widget(cont)
    layout.add_widget(btn)
    pop = MyPopup(title=title, content=layout)
    btn.bind(on_press=lambda *args:pop.dismiss())
    if op:
        pop.open()
    else:
        return pop
    

class MyTextInput(TextInput):
    def __init__(self, **kwargs):
        fs = mod_globals.fontSize
        font = None
        super(MyTextInput, self).__init__(**kwargs)
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'halign' not in kwargs:
            self.halign='center'
        if 'font_size' not in kwargs:
            self.font_size = fs*0.9
            font = True
        if 'height' not in kwargs:
            lines = len(self.text.split('\n'))
            simb = round((len(self.text) * self.font_size) / (Window.size[0] * self.size_hint[0]), 2)
            if lines < simb:
                if (lines * 2) > simb: lines = simb + lines/2
                else: lines = simb
            if 2 < lines < 3: lines = lines
            if lines < 2: lines = lines
            self.height = lines * self.font_size * 1.5
        if mod_globals.os == 'android':
            self.font_size = self.font_size * 0.8
        self.height = kivy.metrics.dp(self.height)
        self.font_size = kivy.metrics.dp(self.font_size)
        self.padding = str(self.font_size / self.height) + 'sp'

class MyPopup(Popup):
    close = ''
    def __init__(self, **kwargs):
        fs = mod_globals.fontSize
        super(MyPopup, self).__init__(**kwargs)
        if 'title' not in kwargs:
            self.title='INFO'
        if 'auto_dismiss' not in kwargs:
            self.auto_dismiss=True
        if 'title_size' not in kwargs:
            self.title_size=str(fs) + 'sp'
        if 'content' not in kwargs:
            self.content=MyLabel(text='LOADING', size_hint = (1, 1))
        if 'title_align' not in kwargs:
            self.title_align='center'
        if 'size_hint' not in kwargs:
            self.size_hint=(None, None)
            self.size=(Window.size[0]*0.95, Window.size[1]*0.95)

class MyButton(Button):
    def __init__(self, **kwargs):
        fs = mod_globals.fontSize
        id = ''
        if 'id' in kwargs:
            self.id = kwargs['id']
            del kwargs ['id']
        super(MyButton, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'font_size' not in kwargs:
            self.font_size = fs
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'height' not in kwargs:
            lines = len(self.text.split('\n'))
            simb = round((len(self.text) * self.font_size) / (Window.size[0] * self.size_hint[0]), 2)
            if lines < simb: lines = simb
            if lines < 2: lines = lines * 1.5
            self.height = lines * self.font_size * 1.5
        if mod_globals.os == 'android':
            self.font_size = self.font_size * 0.8
        self.height = kivy.metrics.dp(self.height)
        self.font_size = kivy.metrics.dp(self.font_size)

class MyGridLayout(GridLayout):
    def __init__(self, **kwargs):
        if 'spadding' in kwargs:
            del kwargs ['spadding']
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
            del kwargs ['bgcolor']
        else:
            self.bgcolor =(1, 0, 0, 1)
        super(MyGridLayout, self).__init__(**kwargs)
        
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
    
    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=(self.pos[0],self.pos[1]), size=(self.size[0], self.size[1]))

class MyLabel(Label):
    def __init__(self, **kwargs):
        fs = mod_globals.fontSize
        self.bgcolor = ''
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
            del kwargs['bgcolor']
        if 'multiline' in kwargs:
            del kwargs['multiline']
        super(MyLabel, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        self.text = self.text.replace('\n\n', '\n')
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'font_size' not in kwargs:
            self.font_size = fs*0.8
        if 'height' not in kwargs:
            lines = len(self.text.split('\n'))
            simb = round((len(self.text) * self.font_size) / (Window.size[0] * self.size_hint[0]), 2)
            if lines < simb: lines = simb + lines / 1.5
            if lines <= 1.9: lines = 1.9
            if 1.9 < lines <= 3: lines = 3
            self.height = lines * self.font_size * 1.2
        self.height = kivy.metrics.dp(self.height)
        self.font_size = kivy.metrics.dp(self.font_size)

    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        if self.bgcolor:
            with self.canvas.before:
                Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
                Rectangle(pos=self.pos, size=self.size)

class MyLabelGreen(ButtonBehavior, Label):
    global fs
    fs = mod_globals.fontSize
    def __init__(self, **kwargs):
        super(MyLabelGreen, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'font_size' not in kwargs:
            self.font_size = fs*0.8
        if 'height' not in kwargs:
            lines = len(self.text.split('\n'))
            simb = ((len(self.text.strip()) * self.font_size) / (Window.size[0] * self.size_hint[0]))
            if lines < simb: lines = simb
            if 1.9 < lines <= 3: lines = 3
            if lines <= 1.9: lines = 1.9
            self.height = lines * self.font_size * 1.3
        self.height = kivy.metrics.dp(self.height)
        self.font_size = kivy.metrics.dp(self.font_size)
        
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 1, 0, 0.25)
            Rectangle(pos=self.pos, size=self.size)

class MyLabelBlue(ButtonBehavior, Label):
    global fs
    fs = mod_globals.fontSize
    def __init__(self, mfs = None, **kwargs):
        if 'param_name' in kwargs:
            self.param_name = kwargs['param_name']
            del kwargs ['param_name']
        super(MyLabelBlue, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        self.bind(text=self.on_text_changed)
        if 'halign' not in kwargs:
            self.halign = 'left'
        if 'font_size' not in kwargs:
            self.font_size = fs*0.8
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'height' not in kwargs:
            lines = len(self.text.split('\n'))
            simb = ((len(self.text) * self.font_size) / (Window.size[0] * self.size_hint[0]))
            if lines < simb: lines = simb
            if lines <= 1.9: lines = 1.9
            if 1.9 < lines <= 3: lines = 3
            self.height = lines * self.font_size * 1.3
        self.height = kivy.metrics.dp(self.height)
        self.font_size = kivy.metrics.dp(self.font_size)
        self.clicked = False

    def on_size(self, widget, size):
        
        self.text_size = (size[0], None)
        self.texture_update()
        if self.size_hint_y is None and self.size_hint_x is not None:
            self.height = fs * fmn
        elif self.size_hint_x is None and self.size_hint_y is not None:
            self.width = self.texture_size[0]
        self.toNormal()
        for dr in favouriteScreen.datarefs:
            if dr.name == self.param_name:
                self.toAdd()
                self.clicked = True
                break

    def on_text_changed(self, widget, text):
        self.on_size(self, self.size)

    def toAdd(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.38, 0.55, 0.95, 0.5)
            Rectangle(pos=self.pos, size=self.size)

    def toNormal(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 1, 0.25)
            Rectangle(pos=self.pos, size=self.size)
    
    def on_press(self):
        if self.clicked:
            self.toNormal()
            self.clicked = False
        else: 
            self.toAdd()
            self.clicked = True

class widgetChoiceLong(App):

    def __init__(self, list, question, header = ''):
        self.menu_entries = list
        self.header = header
        self.question = question
        self.choice_result = None
        super(widgetChoiceLong, self).__init__()
        Window.bind(on_keyboard=self.key_handler)

    def key_handler(self, window, keycode1, keycode2, text, modifiers):
        global choice_result
        global resizeFont
        if resizeFont:
            return True
        if keycode1 == 45 and mod_globals.fontSize > 10:
            mod_globals.fontSize = mod_globals.fontSize - 1
            resizeFont = True
            self.stop()
            return True
        if keycode1 == 61 and mod_globals.fontSize < 40:
            mod_globals.fontSize = mod_globals.fontSize + 1
            resizeFont = True
            self.stop()
            return True
        if keycode1 == 27:
            choice_result = ['<Up>', -1]
            self.stop()
            return True
        return False

    def choice_done(self, instance):
        global choice_result
        choice_result = [instance.txt, instance.ID]
        self.stop()
        InfoPopup()
        base.EventLoop.window.canvas.clear()

    def build(self):
        fs = mod_globals.fontSize
        layout = GridLayout(cols=1, padding=5, spacing=10, size_hint=(1.0, None))
        layout.bind(minimum_height=layout.setter('height'))
        if self.header:
            titlelabel = MyLabel(text=self.header)
            titlelabel.bind(size=titlelabel.setter('text_size'))
            titlelabel.texture_update()
            titlelabel.height = titlelabel.texture_size[1]
            layout.add_widget(titlelabel)
        question = MyLabel(text=self.question)
        layout.add_widget(question)
        i = 1
        for entry in self.menu_entries:
            btn = MyButton(text=' ' + (entry), size_hint=(1.0, None), halign='left', valign='middle', font_name='RobotoMono-Regular')
            btn.bind(size=btn.setter('text_size'))
            btn.txt = entry
            btn.ID = i
            btn.bind(on_press=self.choice_done)
            layout.add_widget(btn)
            i += 1

        root = ScrollView(size_hint=(1, 1), pos_hint={'center_x': 0.5,
         'center_y': 0.5}, do_scroll_x=False)
        root.add_widget(layout)
        return root


def kivyChoiceLong(list, question, header = ''):
    global widgetglobal
    global resizeFont
    while 1:
        widgetglobal = widgetChoiceLong(list, question, header)
        widgetglobal.run()
        if not resizeFont:
            return choice_result
        resizeFont = False


def Choice(list, question):
    return kivyChoiceLong(list, question)


def ChoiceLong(list, question, header = ''):
    return kivyChoiceLong(list, question, header)


def ChoiceFromDict(dict, question, showId = True):
    d = {}
    c = 1
    exitNumber = 0
    for k in sorted(dict.keys()):
        s = dict[k]
        if k.lower() == '<up>' or k.lower() == '<exit>':
            exitNumber = c
            d['Q'] = k
        else:
            d[str(c)] = k
        c = c + 1

    while True:
        try:
            ch = input(question)
        except (KeyboardInterrupt, SystemExit):
            sys.exit()

        if ch == 'q':
            ch = 'Q'
        if ch in list(d.keys()):
            return [d[ch], ch]

def pyren_encodeS(inp):
    if mod_globals.os == 'android':
        return inp.encode('utf-8', errors='replace')
    else:
        return inp.encode(sys.stdout.encoding, errors='replace').decode('utf-8')

def pyren_encode(inp):
    return inp

def pyren_decode(inp):
    return inp

def pyren_decode_i(inp):
    if mod_globals.os == 'android':
        return inp.decode('utf-8', errors='ignore')
    else:
        return inp.decode(sys.stdout.encoding, errors='ignore')

def clearScreen():
    pass
    #sys.stdout.write(chr(27) + '[2J' + chr(27) + '[;H')

def get_message(ScmParam, msg):
    if msg in list(ScmParam.keys()):
        value = ScmParam[msg]
    else:
        value = msg
    if value.isdigit() and value in list(mod_globals.language_dict.keys()):
        value = (mod_globals.language_dict[value])
    return value

def get_message_by_id(id):
    if id.isdigit() and id in list(mod_globals.language_dict.keys()):
        value = (mod_globals.language_dict[id])
        return value

def hex_VIN_plus_CRC(VIN, plusCRC=True):
    VIN = VIN.upper()
    hexVIN = ''
    CRC = 65535
    for c in VIN:
        b = ord(c)
        hexVIN = hexVIN + hex(b)[2:].upper()
        for i in range(8):
            if (CRC ^ b) & 1:
                CRC = CRC >> 1
                CRC = CRC ^ 33800
                b = b >> 1
            else:
                CRC = CRC >> 1
                b = b >> 1

    CRC = CRC ^ 65535
    b1 = CRC >> 8 & 255
    b2 = CRC & 255
    CRC = (b2 << 8 | b1) & 65535
    sCRC = hex(CRC)[2:].upper()
    sCRC = '0'*(4 - len(sCRC)) + sCRC
    if plusCRC:
        return hexVIN + sCRC
    else:
        return hexVIN

def ASCIITOHEX(ATH):
    ATH = ATH.upper()
    hexATH = ''.join(('{:02x}'.format(ord(c)) for c in ATH))
    return hexATH


def StringToIntToHex(DEC):
    DEC = int(DEC)
    hDEC = hex(DEC)
    return hDEC[2:].zfill(2).upper()


def getVIN(de, elm, getFirst = False):
    m_vin = set([])
    for e in de:
        if mod_globals.opt_demo:
            loadDumpToELM(e['ecuname'], elm)
        else:
            if e['pin'].lower() == 'can':
                elm.init_can()
                elm.set_can_addr(e['dst'], e)
            else:
                elm.init_iso()
                elm.set_iso_addr(e['dst'], e)
            elm.start_session(e['startDiagReq'])
        if e['stdType'].lower() == 'uds':
            rsp = elm.request(req='22F190', positive='62', cache=False)[9:59]
        else:
            rsp = elm.request(req='2181', positive='61', cache=False)[6:56]
        try:
            vin = rsp.replace(' ', '').decode('HEX')
        except:
            continue

        if len(vin) == 17:
            m_vin.add(vin)
            if getFirst:
                return vin

    l_vin = m_vin
    if os.path.exists('savedVIN.txt'):
        with open(mod_globals.user_data_dir + 'savedVIN.txt') as vinfile:
            vinlines = vinfile.readlines()
            for l in vinlines:
                l = l.strip()
                if '#' in l:
                    continue
                if len(l) == 17:
                    l_vin.add(l.upper())

    if len(l_vin) == 0 and not getFirst:
        exit()
    if len(l_vin) < 2:
        try:
            ret = next(iter(l_vin))
        except:
            ret = ''

        return ret
    base.runTouchApp(embedded=True)
    pop.open()
    base.EventLoop.idle()
    pop.dismiss()
    base.stopTouchApp()
    choice = Choice(l_vin, 'Choose VIN : ')
    return choice[0]

def DBG(tag, s):
    if mod_globals.opt_debug and mod_globals.debug_file != None:
        mod_globals.debug_file.write('### ' + tag + '\n')
        mod_globals.debug_file.write('"' + s + '"\n')

def isHex(s):
    return all(c in string.hexdigits for c in s)

def kill_server():
    if mod_globals.doc_server_proc is None:
        pass
    else:
        os.kill(mod_globals.doc_server_proc.pid, signal.SIGTERM)


def show_doc(addr, id):
    if mod_globals.vin == '':
        return
    if mod_globals.doc_server_proc == None:
        mod_globals.doc_server_proc = subprocess.Popen(['python',
         '-m',
         'SimpleHTTPServer',
         '59152'])
        atexit.register(kill_server)
    if mod_globals.opt_sd:
        url = 'http://localhost:59152/doc/' + id[1:] + '.htm'
    else:
        url = 'http://localhost:59152/doc/' + mod_globals.vin + '.htm' + id
    webbrowser.open(url, new=0)
