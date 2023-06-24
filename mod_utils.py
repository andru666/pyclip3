#Embedded file name: /build/PyCLIP/android/app/mod_utils.py
import os
import sys, atexit, subprocess, string, signal
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
from kivy import base
from kivy.uix.popup import Popup

import mod_globals
fs = mod_globals.fontSize

widgetglobal = None
choice_result = None
resizeFont = False
try:
    import webbrowser
except:
    pass

def InfoPopup(bas=None):
    pop = MyPopup(content=Label(text='LOADING', font_size=fs*3, halign = 'center'))
    if not bas:
        base.runTouchApp(embedded=True)
    pop.open()
    base.EventLoop.idle()
    pop.dismiss()
    if not bas:
        base.stopTouchApp()

class MyPopup(Popup):
    def __init__(self, **kwargs):
        super(MyPopup, self).__init__(**kwargs)
        if 'title' not in kwargs:
            self.title='INFO'
        if 'title_size' not in kwargs:
            self.title_size=fs*1.5
        if 'content' not in kwargs:
            self.content=Label(text='Loading')
        if 'title_align' not in kwargs:
            self.title_align='center'
        if 'size' in kwargs:
            self.size_hint=(None, None)

class MyButton(Button):
    def __init__(self, **kwargs):
        global fs
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
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'height' not in kwargs:
            fmn = 1.7
            lines = len(self.text.split('\n'))
            simb = len(self.text)*2.0 / self.width
            if 1 > simb: simb = 1
            if lines < simb: lines = simb
            if lines < 2: lines = 2
            if lines > 20: lines = 20
            if fs > 20: 
                lines = lines*1.05
            self.height = fmn*lines*fs*simb
        if 'font_size' not in kwargs and len(self.text)*1.8 < self.height:
            self.font_size = self.height*0.4

class MyGridLayout(GridLayout):
    def __init__(self, **kwargs):
        if 'spadding' in kwargs:
            del kwargs ['spadding']
        super(MyGridLayout, self).__init__(**kwargs)
        self.pos_hint={"top": 1, "left": 1}
        
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor =(1, 0, 0, 1)
    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=(self.pos[0],self.pos[1]), size=(self.size[0], self.size[1]))

class MyLabel(Label):
    global fs
    def __init__(self, **kwargs):
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
            del kwargs['bgcolor']
        else:
            self.bgcolor = (0.5, 0.5, 0, 1)
        if 'multiline' in kwargs:
            del kwargs['multiline']
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'font_size' not in kwargs:
            self.font_size = fs*1.6
        if 'height' not in kwargs:
            fmn = 1.7
            lines = len(self.text.split('\n'))
            simb = len(self.text) / 60
            if lines < simb: lines = simb
            if lines < 7: lines = 5
            if lines > 20: lines = 15
            if 1 > simb: lines = 1.5
            if fs > 20: 
                lines = lines*1.05
                fmn = 1.5
            self.height = fmn*lines*fs
        super(MyLabel, self).__init__(**kwargs)
        
    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=self.pos, size=self.size)

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
            titlelabel = Label(text=self.header, height=fs*3, size_hint=(1.0, None))
            titlelabel.bind(size=titlelabel.setter('text_size'))
            titlelabel.texture_update()
            titlelabel.height = titlelabel.texture_size[1]
            layout.add_widget(titlelabel)
        question = Label(text=self.question, height=fs, size_hint=(1.0, None))
        layout.add_widget(question)
        i = 1
        for entry in self.menu_entries:
            btn = MyButton(text=' ' + (entry), height=fs*4, size_hint=(1.0, None), halign='left', valign='middle', font_name='RobotoMono-Regular')
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
    sys.stdout.write(chr(27) + '[2J' + chr(27) + '[;H')


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
