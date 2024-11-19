# -*- coding: utf-8 -*-
try:
    from kivy_deps import sdl2, glew
except:
    pass
from kivy.utils import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.switch import Switch
from kivy.graphics import Color, Rectangle
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy import base
from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
import sys, os, re, string, time, mod_globals, mod_elm, mod_utils, main
from mod_utils import *
import urllib.request

__all__ = 'install_android'

macro = {}
var = {}
cmd_delay = 0
stack = []

auto_macro = ""
auto_dia = False
debug_mode = False

key_pressed = ''

mod_globals.os = platform

mod_globals.opt_demo = False

if mod_globals.os != 'android':
    import serial
    from serial.tools import list_ports
else:
    from jnius import autoclass
    mod_globals.os = 'android'
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
    UUID = autoclass('java.util.UUID')

if mod_globals.os == 'android':
    try:
        from jnius import autoclass
        import glob
        AndroidPythonActivity = autoclass('org.renpy.android.PythonActivity')
        PythonActivity = autoclass('org.renpy.android.PythonActivity')
        AndroidActivityInfo = autoclass('android.content.pm.ActivityInfo')
        Environment = autoclass('android.os.Environment')
        Params = autoclass('android.view.WindowManager$LayoutParams')
        user_datadir = Environment.getExternalStorageDirectory().getAbsolutePath() + '/pyren/'
        mod_globals.user_data_dir = user_datadir
        mod_globals.cache_dir = user_datadir + '/cache/'
        mod_globals.log_dir = user_datadir + '/logs/'
        mod_globals.dumps_dir = user_datadir + '/dumps/'
        mod_globals.csv_dir = user_datadir + '/csv/'
    except:
        mod_globals.ecu_root = '../'
        try:
            import serial
            from serial.tools import list_ports
        except:
            pass

class Term():
    def __init__(self, opt_port, opt_speed, opt_log):
        self.opt_port = opt_port
        self.opt_speed = opt_speed
        self.opt_log = opt_log
    
    def test(self):
        MyApp(self.opt_port, self.opt_speed, self.opt_log).run()

class MyApp(App):

    def __init__(self, opt_port, opt_speed, opt_log):
        self.macros = True
        self.LINK = False
        mod_globals.opt_port = opt_port
        mod_globals.opt_speed = opt_speed
        mod_globals.opt_log = opt_log
        self.orig_log = mod_globals.opt_log
        self.dir_macro = os.path.join(mod_globals.user_data_dir, 'macro')
        super(MyApp, self).__init__()
    
    def build(self):

        Clock.schedule_once(self.select_macro, 0.1)
        
        self.label = MyLabel(text='', bgcolor=(1, 1, 0, 0.3), font_size=fs, size_hint=(1, None), height=fs*1.5)
        self.roots = GridLayout(cols=1, padding=fs*1.5, spacing=fs*1.5, size_hint=(1, None), size_hint_y=None)
        self.roots.bind(minimum_height=self.roots.setter('height'))
        self.roots.add_widget(MyLabel(text='Running macro', font_size=fs, bgcolor=(1, 1, 0, 0.3)))
        self.roots.add_widget(self.label)
        layout = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5,'center_y': 0.5})
        layout.add_widget(self.roots)
        
        return layout
    
    def MaLabel(self, text):
        label = MyLabel(text=str(text), bgcolor=(0.5,0.5,0,1))
        self.roots.add_widget(label)
    
    def select_macro(self, instance):
        root = GridLayout(cols=1, size_hint=(1, 1))
        self.fichoo = FileChooserListView(path=self.dir_macro)
        root.add_widget(self.fichoo)
        root.add_widget(MyButton(text='Open Links', on_release=self.popp_links, size_hint=(1, None)))
        root.add_widget(MyButton(text='Open', on_release=self.popp, size_hint=(1, None)))
        self.popup_macro = MyPopup_close(title='SELECT macro', cont=root, cl=1, op=None)
        self.popup_macro.open()

    def open_link(self, instance):
        self.popup_links.dismiss()
        data = urllib.request.urlopen(self.links.text)
        print(data)
        self.data_link = []
        for line in data:
            self.data_link.append(line.decode('utf-8'))
        self.LINK = True
        Clock.schedule_once(self.macro_start, 1)
        
    def popp_links(self, instance):
        self.popup_macro.dismiss()
        box = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.links = MyTextInput(size_hint=(1, 1))
        box.add_widget(self.links)
        box.add_widget(MyButton(text='Open', on_release=self.open_link, size_hint=(1, None)))
        self.popup_links = MyPopup_close(title='Links', cont=box, cl=1, op=None)
        self.popup_links.open()
        

    def popp(self, instance):
        self.popup_macro.dismiss()
        Clock.schedule_once(self.macro_start, 1)
    
    def exits(self, instance):
        mod_globals.opt_cfc0 = False
        mod_globals.opt_log = self.orig_log
        self.stop()
        main.kivyScreenConfig()
    
    def macro_start(self, instance):
        try:
            try:
                file_macro = str(self.fichoo.selection[0].rsplit('\\', 1)[1])
            except:
                file_macro = str(self.fichoo.selection[0].rsplit('/', 1)[1])
        except:
            self.MaLabel('Not select macro')
            self.roots.add_widget(MyButton(text='CLOSE', size_hint=(1, None), height=fs*3, on_release=self.exits))
            return 
        self.label.text = str('File macro select: ' + file_macro)
        mod_globals.opt_log = file_macro.replace('.cmd', '.txt')
        try:
            self.elm = mod_elm.ELM(mod_globals.opt_port, mod_globals.opt_speed, mod_globals.opt_log)
        except:
            self.stop()
            root = GridLayout(cols=1, size_hint=(1, 1))
            labelText = '''
                Could not connect to the ELM.

                Possible causes:
                - Bluetooth is not enabled
                - other applications are connected to your ELM e.g Torque
                - other device is using this ELM
                - ELM got unpaired
                - ELM is read under new name or it changed its name

                Check your ELM connection and try again.
            '''
            lbltxt = Label(text=labelText, font_size=mod_globals.fontSize)
            root.add_widget(lbltxt)
            root.add_widget(MyButton(text='CLOSE', size_hint=(1, None), height=fs*5, on_release=self.exits))
            popup_load = Popup(title='ELM connection error', content=root, size=(800, 800))
            popup_load.open()
            base.runTouchApp()
            return
        
        global auto_macro
        global auto_dia
        global debug_mode
        global macro
        global var
        self.init_macro()
        self.init_var()
        self.load_macro()
        
        mod_globals.opt_cfc0 = True
        
        auto_dia = True
        
        """if not mod_globals.opt_demo and self.elm.port:
            #self.elm.port.check_elm()
            if mod_globals.opt_speed < mod_globals.opt_rate:
                self.elm.port.soft_boudrate(mod_globals.opt_rate)"""
        
        self.elm.currentaddress = '7A'
        self.elm.currentprotocol = 'can'

        cmd_lines = []
        cmd_ref = 0
        if auto_dia:
            if self.LINK:
                cmd_lines = self.data_link
            else:
                fname = self.fichoo.selection[0]
                if len(fname)>0:
                    with open(fname, 'rt') as f:
                        cmd_lines = f.readlines()
        
        if debug_mode:
            mod_globals.opt_demo = True
            self.elm.loadDump('./dumps/term_test.txt')
            fname = './macro/test/test.cmd'
            if len(fname)>0:
                with open(fname, 'rt') as f:
                    cmd_lines = f.readlines()

        if auto_macro != '':
            if auto_macro in list(macro.keys()):
                self.play_macro(auto_macro, self.elm)
            else:
                self.popup = Popup(title='ERROR', content=MyLabel(text=str('Error: unknown macro name: ' + auto_macro)), size=(400, 400), size_hint=(None, None))
                self.popup.open()

        while self.macros:
            label = MyLabel(text=str(var['$addr']+':'+var['$txa']+':'+var['$prompt'] + '#'), bgcolor=(0.5,0.5,0,1), size_hint=(1, None))
            self.roots.add_widget(label)
            
            if len(cmd_lines)==0:
                l = input().lower()
            else:
                if cmd_ref<len(cmd_lines):
                    l = cmd_lines[cmd_ref].strip()
                    cmd_ref += 1
                else:
                    cmd_lines = []
                    l = "# end of command file"
                    self.macros = False
                if l != '': label.text += str(l)
            goto = self.proc_line(l, self.elm)

            if goto and len(cmd_lines):
                c_str = 0
                for c in cmd_lines:
                    if c.startswith(':'):
                        if goto == c[1:].strip():
                            cmd_ref = c_str
                            break
                    c_str += 1
        label = MyLabel(text='', bgcolor=(0.5,0.5,0,1), size_hint=(1, None))
        self.roots.add_widget(label)
        self.roots.add_widget(MyButton(text='CLOSE', size_hint=(1, None), height=fs*3, on_release=self.exits))
        
    def open_pop(self, instance):
        lbltxt = MyLabel(text=instance)
        popup_load = Popup(title='ELM connection error', content=lbltxt, size=(800, 800))
        popup_load.open()
    
    def init_macro(self):
        global macro
        macro = {}
        
    def init_var(self):
        global var
        var = {}    
        var['$addr'] = '7A'
        var['$txa'] = '7E0'
        var['$rxa'] = '7E8'
        var['$prompt'] = 'ELM'

    def pars_macro(self, file):
        global macro
        global var
        self.MaLabel('openning file: ' + file)
        with open(file, 'rt') as f:
            lines = f.readlines()
        macro = {}
        macroname = ''
        macrostrings = []
        line_num = 0
        for l in lines:
            line_num += 1
            l = l.split('#')[0] # remove comments
            l = l.strip()
            if l == '': continue
            if '{' in l:
                if macroname=='':
                    literals =    l.split('{')
                    macroname = literals[0].strip()
                    macroname = macroname.replace(' ', '_').replace('\t', '_')
                    macrostrings = []
                    if len(literals)>1 and literals[1]!='' :
                        macrostrings.append(literals[1])
                    continue
                else:
                    self.MaLabel('Error: empty macro name in line: ' + line_num)
                    
                    macro = {}
                    var = {}
                    return macro, var
            if '}' in l:
                if macroname!='':
                    literals =    l.split('}')
                    cmd = literals[0].strip()
                    if cmd!='':
                        macrostrings.append(cmd)
                    macro[macroname] = macrostrings
                    macroname = ''
                    macrostrings = []
                    continue
                else:
                    self.MaLabel('Error: unexpected end of macro in line: ' + line_num)
                    
                    macro = {}
                    var = {}
                    return macro, var
            m = re.search('\$\S+\s*=\s*\S+', l)
            if m and macroname=='':
                r = m.group(0).replace(' ', '').replace('\t', '')
                rl = r.split('=')
                var[rl[0]]=rl[1]
            else:
                macrostrings.append(l)
        return macro, var

    def load_macro(self, mf=''):
        if mf=='' :
            for root, dirs, files in os.walk(self.dir_macro):
                for mfile in files:
                    if mfile.endswith('.txt'):
                        full_path = os.path.join(mod_globals.user_data_dir, os.path.join("macro", mfile))
                        return self.pars_macro(full_path)
        else:
            return self.pars_macro(mf) 

    def play_macro(self, mname, elm):
        global macro
        global var
        global stack
        if mname in stack:
            self.MaLabel('Error: recursion prohibited: ' + mname)
            
            return
        else:
            stack.append(mname)

        for l in macro[mname]:

            if l in list(macro.keys()):
                self.play_macro(l, elm)
                continue

            self.proc_line(l, elm)

        stack.remove(mname)

    def term_cmd(self, c, elm):
        global var
        rsp = elm.request(c, cache=False)
        #rsp = elm.cmd(rcmd)
        var['$lastResponse'] = rsp
        return rsp

    def bit_cmd(self, l, elm, fnc='set_bits'):

        error_msg1 = '''ERROR: command should have 5 parameters: 
        <command> <lid> <rsp_len> <offset> <hex mask> <hex value>
            <lid> - ECUs local identifier. Length should be 2 simbols for KWP or 4 for CAN
            <rsp_len> - lengt of command response including positive response bytes, equals MinBytes from ddt db
            <offset> - offeset in bytes to first changed byte (starts from 1 not 0) 
            <hex mask> - bit mask for changed bits, 1 - changable, 0 - untachable
            <hex value> - bit value
        <hex mask> and <hex value> should have equal length
        
        '''
        error_msg2 = '''ERROR: command should have 6 parameters: 
        <command> <lid> <rsp_len> <offset> <hex mask> <hex value> <label>
            <lid> - ECUs local identifier. Length should be 2 simbols for KWP or 4 for CAN
            <rsp_len> - lengt of command response including positive response bytes, equals MinBytes from ddt db
            <offset> - offeset in bytes to first changed byte (starts from 1 not 0) 
            <hex mask> - bit mask for changed bits, 1 - changable, 0 - untachable
            <hex value> - bit value
            <label> - label to go
        <hex mask> and <hex value> should have equal length

        '''

        error_msg3 = '''ERROR: command should have 6 parameters: 
        <command> <lid> <rsp_len> <offset> <hex mask> <hex value> <label>
            <lid> - ECUs local identifier. Length should be 2 simbols for KWP or 4 for CAN
            <rsp_len> - lengt of command response including positive response bytes, equals MinBytes from ddt db
            <offset> - offeset in bytes to first changed byte (starts from 1 not 0) 
            <hex mask> - bit mask for changed bits, 1 - changable, 0 - untachable
            <val step> - value step
            <val offset> - value offset
            <val divider> - value divider

        '''
        if fnc not in ['set_bits','xor_bits','exit_if','exit_if_not'] and \
                fnc not in ['goto_if','goto_if_not', 'value']:
            self.MaLabel("\nERROR: Unknown function\n")
            
            return

        par = l.strip().split(' ')

        if fnc in ['set_bits','xor_bits','exit_if','exit_if_not']:
            error_msg = error_msg1
            if len(par)!=5:
                self.MaLabel(error_msg)
                
                return

        if fnc in ['goto_if','goto_if_not']:
            error_msg = error_msg2
            if len(par)!=6:
                self.MaLabel(error_msg)
                
                return

        if fnc in ['value']:
            error_msg = error_msg3
            if len(par)==4:
                par = par + ['1','0','1']
            if len(par)!=7:
                self.MaLabel(error_msg)
                
                return

        try:
            lid = par[0].strip()
            lng = int(par[1].strip())
            off = int(par[2].strip())-1
            mask = par[3].strip()
            val = par[4].strip()
            if fnc in ['goto_if', 'goto_if_not']:
                go = par[5].strip()
            if fnc in ['value']:
                val = '0'*len(mask)
                stp = par[4].strip()
                ofs = par[5].strip()
                div = par[6].strip()
        except:
            self.MaLabel(error_msg)
            
            return

        if len(lid) in [2,4] and off>=0 and off<=lng:
            if fnc not in ['value'] and (len(mask)!=len(val)):
                self.MaLabel(error_msg)
                
                return
        else:
            self.MaLabel(error_msg)
            
            return

        if len(lid)==2: #KWP
            rcmd = '21'+lid
        else: #CAN
            rcmd = '22' + lid

        rsp = self.term_cmd(rcmd, elm)
        rsp = rsp.replace(' ','')[:lng*2].upper()

        if fnc not in ['value']:
            self.MaLabel("read    value: "+rsp)
            

        if len(rsp) != lng * 2:
            self.MaLabel('\nERROR: Length is unexpected\n')
            
            if fnc.startswith('exit'):
                self.macros = False
            return

        if not all(c in string.hexdigits for c in rsp):
            if fnc.startswith('exit'):
                self.macros = False
            self.MaLabel('\nERROR: Wrong simbol in response\n')
            
            return

        pos_rsp = ('6'+rcmd[1:]).upper()
        if not rsp.startswith(pos_rsp):
            if fnc.startswith('exit'):
                self.macros = False
            self.MaLabel('\nERROR: Not positive response\n')
            
            return

        diff = 0
        i = 0
        int_val = 0
        while i<len(mask)/2:
            c_by = int(rsp[(off+i)*2:(off+i)*2+2],16)
            c_ma = int(mask[i*2:i*2+2],16)
            c_va = int(val[i*2:i*2+2],16)

            if fnc == 'xor_bits':
                n_by = c_by ^ (c_va & c_ma)
            elif fnc == 'set_bits':
                n_by = (c_by & ~c_ma) | c_va
            else:
                n_by = c_by & c_ma
                int_val = int_val * 256 + n_by
                if (c_by & c_ma) != (c_va & c_ma):
                    diff += 1
                i += 1
                continue

            str_n_by = hex(n_by & 0xFF).upper()[2:].zfill(2)

            n_rsp = rsp[0:(off+i)*2] + str_n_by + rsp[(off+i+1)*2:]
            rsp = n_rsp
            i += 1

        if fnc == 'exit_if':
            if diff==0:
                self.MaLabel("Match. Exit")
                
                self.macros = False
            else:
                self.MaLabel("Not match. Continue")
                
                return

        if fnc == 'exit_if_not':
            if diff!=0:
                self.MaLabel("Not match. Exit")
                
                self.macros = False
            else:
                self.MaLabel("Match. Continue")
                
                return

        if fnc == 'goto_if':
            if diff==0:
                self.MaLabel("Match. goto:"+ go)
                
                return go
            else:
                self.MaLabel("Not match. Continue")
                
                return

        if fnc == 'goto_if_not':
            if diff!=0:
                self.MaLabel("Not match. goto:"+go)
                
                return go
            else:
                self.MaLabel("Match. Continue")
                
                return

        if fnc == 'value':
            res = (int_val*float(stp)+float(ofs))/float(div)
            self.MaLabel('# LID(',lid,') ='+ res)
            
            return

        if rsp[:2]=='61':
            wcmd = '3B'+rsp[2:]
        elif rsp[:2]=='62':
            wcmd = '2E'+rsp[2:]

        self.MaLabel("write value:"+ wcmd)
        
        self.MaLabel(self.term_cmd(wcmd, elm))
        

    def wait_kb(self, ttw):
        global key_pressed
        st = time.time()

        while(time.time()<(st+ttw)):
            #key_pressed = kb.getch()
            time.sleep(0.1)


    def proc_line(self, l, elm):
        
        global macro
        global var
        global cmd_delay
        global key_pressed
        
        if '#' in l:
            l = l.split('#')[0]

        l = l.strip()

        if l.startswith(':'):
            self.MaLabel(l)
            
            return

        if len(l) == 0:
            return

        if l in ['q', 'quit', 'e', 'exit', 'end']:
            mod_globals.opt_log = self.orig_log
            self.macros = False
            return

        if l in ['cls']:
            mod_utils.clearScreen()
            return
        if l in list(macro.keys()):
            self.play_macro(l, elm)
            return

        m = re.search('\$\S+\s*=\s*\S+', l)
        if m:
            # find variable definition
            r = m.group(0).replace(' ', '').replace('\t', '')
            rl = r.split('=')
            var[rl[0]] = rl[1]
            if rl[0] == '$addr':
                if var['$addr'].upper() in list(mod_elm.dnat.keys()):
                    var['$txa'] = mod_elm.dnat[var['$addr'].upper()]
                    var['$rxa'] = mod_elm.snat[var['$addr'].upper()]
                    elm.currentaddress = var['$addr'].upper()
            return

        # find veriable usage
        m = re.search('\$\S+', l)
        while m:
            vu = m.group(0)
            if vu in list(var.keys()):
                l = re.sub("\\" + vu, var[vu], l)
            else:
                self.MaLabel('Error: unknown variable '+vu)
                
                return
            m = re.search('\$\S+', l)

        l_parts = l.split()
        if len(l_parts) > 0 and l_parts[0] in ['wait', 'sleep']:
            try:
                self.wait_kb(int(l_parts[1]))
                return
            except:
                pass

        if len(l_parts) > 0 and l_parts[0] in ['ses', 'session']:
            try:
                elm.startSession = l_parts[1]
                l = l_parts[1]
            except:
                pass

        if len(l_parts) > 0 and l_parts[0] in ['delay']:
            cmd_delay = int(l_parts[1])
            return

        if l.lower().startswith('set_bits'):
            self.bit_cmd(l.lower()[8:], elm, fnc='set_bits')
            return

        if l.lower().startswith('xor_bits'):
            self.bit_cmd(l.lower()[8:], elm, fnc='xor_bits')
            return

        if l.lower().startswith('exit_if_not'):
            self.bit_cmd(l.lower()[11:], elm, fnc='exit_if_not')
            return

        if l.lower().startswith('exit_if'):
            self.bit_cmd(l.lower()[7:], elm, fnc='exit_if')
            return

        if l.lower().startswith('goto_if_not'):
            go = self.bit_cmd(l.lower()[11:], elm, fnc='goto_if_not')
            return go

        if l.lower().startswith('goto_if'):
            go = self.bit_cmd(l.lower()[7:], elm, fnc='goto_if')
            return go

        if l.lower().startswith('if_key'):
            if len(l_parts) != 3 or l_parts[1] != key_pressed:
                return
            else:
                key_pressed = ''
                return l_parts[2]

        if l.lower().startswith('value'):
            val = self.bit_cmd(l.lower()[5:], elm, fnc='value')
            return

        if len(l_parts) > 0 and l_parts[0] in ['go','goto']:
            self.MaLabel(l)
            return l_parts[1]

        if len(l_parts) > 0 and l_parts[0] in ['var','variable']:
            self.MaLabel(l)
            
            return

        if l.lower().startswith('_'):
            self.MaLabel(elm.send_raw(l[1:]))
            
        else:
            self.MaLabel(self.term_cmd(l, elm))
            

        if cmd_delay>0:
            self.MaLabel('# delay: '+str(cmd_delay))
            self.wait_kb(cmd_delay)