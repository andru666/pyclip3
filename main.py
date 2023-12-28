# -*- coding: utf-8 -*-
try:
    from kivy_deps import sdl2, glew
except:
    pass
from kivy.utils import platform
from kivy.config import Config
if platform != 'android':
    import ctypes
    user32 = ctypes.windll.user32
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'top',  20)
    Config.set('graphics', 'left', int(user32.GetSystemMetrics(0))-400)
from kivy.core.window import Window
import traceback, time, mod_globals
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView
import kivy.metrics
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.switch import Switch
from kivy import base

__all__ = 'install_android'
__version__ = '0.02.05'

mod_globals.os = platform
if mod_globals.os == 'android':
    from jnius import cast, autoclass
    from android import mActivity, api_version
    import glob
    
    from android.permissions import request_permissions, check_permission, Permission

    permissions = []
    if api_version > 30:
        try:
            if (check_permission('android.permission.BLUETOOTH_CONNECT') == False):
                permissions.append('android.permission.BLUETOOTH_CONNECT')
        except:
            pass
        try:
            if (check_permission('android.permission.BLUETOOTH_SCAN') == False):
                permissions.append('android.permission.BLUETOOTH_SCAN')
        except:
            pass

    if api_version <= 29:
        try:
            if (check_permission('android.permission.WRITE_EXTERNAL_STORAGE') == False):
                permissions.append('android.permission.WRITE_EXTERNAL_STORAGE')
        except:
            pass
        try:
            if (check_permission('android.permission.READ_EXTERNAL_STORAGE') == False):
                permissions.append('android.permission.READ_EXTERNAL_STORAGE')
        except:
            pass

    try:
        request_permissions (permissions)
    except:
        pass
        #print('Permission request error!')

    Environment = autoclass('android.os.Environment')       
    AndroidPythonActivity = autoclass('org.kivy.android.PythonActivity')

    try:
        if api_version > 29:
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            if Environment.isExternalStorageManager():
                pass
            else:
                try:
                    activity = mActivity.getApplicationContext()
                    uri = Uri.parse("package:" + activity.getPackageName())
                    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                    currentActivity = cast(
                    "android.app.Activity", AndroidPythonActivity.mActivity
                    )
                    currentActivity.startActivityForResult(intent, 101)
                except:
                    intent = Intent()
                    intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                    currentActivity = cast(
                    "android.app.Activity", AndroidPythonActivity.mActivity
                    )
                    currentActivity.startActivityForResult(intent, 101)
    except:
        pass
        #print('ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION unavailable')

    waitPermissionTimer = 0
    permissionIsGranted = False
    while (permissionIsGranted == False) & (waitPermissionTimer < 5):
        time.sleep(0.5)
        waitPermissionTimer = waitPermissionTimer + 0.5
        permissionIsGranted = True
        for perm in permissions:
            if (check_permission(perm) == False):
                permissionIsGranted = False

        if api_version > 29:
            if (Environment.isExternalStorageManager() == False):
                permissionIsGranted = False
    
    AndroidActivityInfo = autoclass('android.content.pm.ActivityInfo')
    Environment = autoclass('android.os.Environment')
    Params = autoclass('android.view.WindowManager$LayoutParams')
    user_datadir = Environment.getExternalStorageDirectory().getAbsolutePath() + '/pyren/'
    mod_globals.user_data_dir = user_datadir
    mod_globals.cache_dir = user_datadir + '/cache/'
    mod_globals.crash_dir = user_datadir + '/crashs/'
    mod_globals.log_dir = user_datadir + '/logs/'
    mod_globals.dumps_dir = user_datadir + '/dumps/'
    mod_globals.macro_dir = user_datadir + '/macro/'
    mod_globals.csv_dir = user_datadir + '/csv/'
    import sys
    mod_globals.scen_dir = user_datadir + '/pyren/scen/'
    sys.path.append(mod_globals.scen_dir)

elif mod_globals.os == 'nt':
    import pip
    try:
        import serial
    except ImportError:
        pip.main(['install', 'pyserial'])

    try:
        import colorama
    except ImportError:
        pip.main(['install', 'colorama'])
        try:
            import colorama
        except ImportError:
            sys.exit()

    colorama.init()
else:
    try:
        import serial
        from serial.tools import list_ports
    except:
        pass
from mod_elm import ELM, get_devices
from mod_zip import *
from mod_scan_ecus import ScanEcus
from mod_ecu import ECU
from mod_ecu_mnemonic import *
from mod_utils import *
from mod_ecu_default import *

os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
argv_glob = sys.argv
sys.argv = sys.argv[0:1]

def my_excepthook(excType, excValue, tb):
    message = traceback.format_exception(excType, excValue, tb)
    string = ''
    for m in message:
        string += m
    error = MyTextInput(text=string, size_hint=(1, 1))
    if mod_globals.os == 'android':
        with open(os.path.join(mod_globals.crash_dir, 'crash_'+str(time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime()))+'.txt'), 'w') as fout:
            fout.write(str(string))
    popup = MyPopup(title='Crash', content=error, size=(Window.size[0]*0.9, Window.size[1]*0.9), size_hint=(None, None), on_dismiss=exit)
    popup.open()
    base.runTouchApp()
    exit(2)


sys.excepthook = my_excepthook
resizeFont = False

def set_orientation_landscape():
    if mod_globals.os == 'android':
        activity = AndroidPythonActivity.mActivity
        activity.setRequestedOrientation(AndroidActivityInfo.SCREEN_ORIENTATION_LANDSCAPE)

def set_orientation_portrait():
    if mod_globals.os == 'android':
        activity = AndroidPythonActivity.mActivity
        activity.setRequestedOrientation(AndroidActivityInfo.SCREEN_ORIENTATION_PORTRAIT)

class screenConfig(App):
    global fs
    fs = mod_globals.fontSize
    def __init__(self):
        self.button = {}
        self.textInput = {}
        super(screenConfig, self).__init__()
        self.settings = mod_globals.Settings()
        Window.bind(on_keyboard=self.key_handler)

    def key_handler(self, window, keycode1, keycode2, text, modifiers):
        global resizeFont
        if resizeFont:
            return True
        if (keycode1 == 45 or keycode1 == 269) and mod_globals.fontSize > 10:
            mod_globals.fontSize = mod_globals.fontSize - 1
            resizeFont = True
            self.stop()
            return True
        if (keycode1 == 61 or keycode1 == 270) and mod_globals.fontSize < 40:
            mod_globals.fontSize = mod_globals.fontSize + 1
            resizeFont = True
            self.stop()
            return True
        if keycode1 == 27:
            exit()
        return False

    def set_orientation_all(self):
        if mod_globals.os == 'android':
            activity = AndroidPythonActivity.mActivity
            activity.setRequestedOrientation(AndroidActivityInfo.SCREEN_ORIENTATION_SENSOR)

    def make_box_switch(self, str1, active, callback = None):
        label = MyLabel(text=str1, halign='left',  size_hint=(0.65, None), bgcolor = (0.5, 0.5, 0, 1))
        sw = Switch(active=active, size_hint=(0.35, None))
        if callback:
            sw.bind(active=callback)
        self.button[str1] = sw
        glay = MyGridLayout(cols=2)
        sw.height = label.height
        glay.height = 1.2 * label.height
        glay.padding = glay.spacing = glay.height / 12
        glay.add_widget(label)
        glay.add_widget(sw)
        return glay

    def make_opt_ecuid(self,active, callback = None):
        global fs
        str1 = 'OPT ecuid'
        label = MyLabel(text=str1, halign='left', size_hint=(0.35, None), bgcolor = (0.5, 0.5, 0, 1))
        if mod_globals.opt_ecu:
            iText = mod_globals.opt_ecu
        else:
            iText = ''
        ti = MyTextInput(text=iText, font_size=fs, size_hint=(0.45, None), multiline=False)
        self.textInput[str1] = ti
        sw = Switch(active=active, size_hint=(0.2, None))
        if callback:
            sw.bind(active=callback)
        self.button[str1] = sw
        glay = MyGridLayout(cols=3)
        ti.height = sw.height = label.height
        glay.height = 1.2 * label.height
        glay.padding = glay.spacing = glay.height / 12
        glay.add_widget(label)
        glay.add_widget(sw)
        glay.add_widget(ti)
        return glay

    def make_input(self, str1, iText):
        global fs
        label = MyLabel(text=str1, halign='left', bgcolor = (0.5, 0.5, 0, 1))
        ti = MyTextInput(text=iText, font_size=fs, multiline=False)
        self.textInput[str1] = ti
        ti.height = label.height
        glay = MyGridLayout(cols=2)
        glay.height = 1.2 * label.height
        glay.padding = glay.spacing = glay.height / 12
        glay.add_widget(label)
        glay.add_widget(ti)
        return glay

    def make_bt_device_entry(self):
        ports = get_devices()
        label = MyLabel(text='ELM port', halign='left', size_hint=(0.35, None), bgcolor = (0.5, 0.5, 0, 1))
        self.bt_dropdown = DropDown()
        glay = MyGridLayout(cols=2)
        btn = MyButton(text='WiFi (192.168.0.10:35000)')
        btn.height = label.height*1.5
        btn.font_size = label.font_size
        btn.bind(on_release=lambda btn: self.bt_dropdown.select(btn.text))
        self.bt_dropdown.add_widget(btn)
        try:
            porte = iter(ports.items())
        except:
            porte = list(ports.items())
        for name, address in porte:
            if mod_globals.opt_port == name:
                mod_globals.opt_dev_address = address
            btn = MyButton(text=name + '>' + address, size_hint=(0.65, None))
            btn.height = label.height*1.5
            btn.font_size = label.font_size
            btn.bind(on_release=lambda btn: self.bt_dropdown.select(btn.text))
            self.bt_dropdown.add_widget(btn)
        self.mainbutton = MyButton(text='Select', size_hint=(0.65, None))
        self.mainbutton.height = label.height
        self.mainbutton.font_size = label.font_size
        self.mainbutton.bind(on_release=self.bt_dropdown.open)
        self.bt_dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
        self.bt_dropdown.select(mod_globals.opt_port)
        glay.height = 1.2 * label.height
        glay.padding = glay.spacing = glay.height / 12
        glay.add_widget(label)
        glay.add_widget(self.mainbutton)
        return glay
    
    def changeLangButton(self, buttonText):
        setattr(self.langbutton, 'text', buttonText)
        setattr(self.langbutton, 'background_normal', '')
        setattr(self.langbutton, 'background_color', (0.345,0.345,0.345,1))

    def make_savedEcus(self):
        ecus = sorted(glob.glob(os.path.join(mod_globals.user_data_dir, 'savedEcus*.p')))
        label = MyLabel(text='savedEcus', halign='left', size_hint=(0.35, None), bgcolor = (0.5, 0.5, 0, 1))
        self.ecus_dropdown = DropDown()
        glay = MyGridLayout(cols=2)
        for s_ecus in ecus:
            s_ecus = os.path.split(s_ecus)[1]
            btn= MyButton(text=s_ecus)
            btn.height = label.height
            btn.font_size = label.font_size
            btn.bind(on_release=lambda btn: self.ecus_dropdown.select(btn.text))
            self.ecus_dropdown.add_widget(btn)
        self.ecusbutton = MyButton(text='', size_hint=(0.65, None))
        self.ecusbutton.bind(on_release=self.ecus_dropdown.open)
        self.ecus_dropdown.bind(on_select=lambda instance, x: setattr(self.ecusbutton, 'text', x))
        self.ecusbutton.height = label.height
        self.ecusbutton.font_size = label.font_size
        glay.height = 1.2 * label.height
        glay.padding = glay.spacing = glay.height / 12
        glay.add_widget(label)
        glay.add_widget(self.ecusbutton)
        return glay

    def make_language_entry(self):
        langs = get_languages()
        label = MyLabel(text='Language', halign='left', size_hint=(0.35, None), bgcolor = (0.5, 0.5, 0, 1))
        self.lang_dropdown = DropDown()
        glay = MyGridLayout(cols=2)
        btn = MyButton(text='SELECT')
        btn.height = label.height
        btn.font_size = label.font_size
        btn.bind(on_release=lambda btn: self.lang_dropdown.select(btn.text))
        self.lang_dropdown.add_widget(btn)
        for lang in sorted(langs):
            btn = MyButton(text=lang)
            btn.height = label.height
            btn.font_size = label.font_size
            btn.bind(on_release=lambda btn: self.lang_dropdown.select(btn.text))
            self.lang_dropdown.add_widget(btn)
        self.langbutton = MyButton(text='SELECT', size_hint=(0.65, None))
        self.langbutton.height = label.height
        self.langbutton.font_size = label.font_size
        self.langbutton.bind(on_release=self.lang_dropdown.open)
        self.lang_dropdown.bind(on_select=lambda instance, x: self.changeLangButton(x))
        if mod_globals.opt_lang:
            self.lang_dropdown.select(mod_globals.opt_lang)
        glay.height = 1.2 * label.height
        glay.padding = glay.spacing = glay.height / 12
        glay.add_widget(label)
        glay.add_widget(self.langbutton)
        return glay

    def finish(self, instance):
        InfoPopup(1)
        mod_globals.opt_port = ''
        mod_globals.opt_ecu = str(self.textInput['OPT ecuid'].text)
        mod_globals.opt_ecuid = str(self.textInput['OPT ecuid'].text)
        mod_globals.opt_ecuid_on = self.button['OPT ecuid'].active
        mod_globals.opt_speed = 38400
        mod_globals.opt_rate = 38400
        mod_globals.savedEcus = self.ecusbutton.text
        mod_globals.opt_lang = self.langbutton.text
        mod_globals.opt_car = 0
        if self.button['Generate logs'].active:
            mod_globals.opt_log = 'log.txt' if self.textInput['Log name'].text == '' else self.textInput['Log name'].text
        else:
            mod_globals.opt_log = ''
        try:
            mod_globals.fontSize = int(self.textInput['Font size'].text)
        except:
            mod_globals.fontSize = 20
        mod_globals.opt_demo = self.button['Demo mode'].active
        mod_globals.opt_scan = self.button['Scan vehicle'].active
        mod_globals.opt_csv = self.button['CSV Log'].active
        mod_globals.opt_csv_only = False
        mod_globals.opt_csv_human = False
        if mod_globals.opt_csv : mod_globals.opt_csv_human = True
        mod_globals.opt_usrkey = ''
        mod_globals.opt_verbose = False
        mod_globals.opt_si = self.button['KWP Force SlowInit'].active
        mod_globals.opt_cfc0 = self.button['Use CFC0'].active
        mod_globals.opt_n1c = False
        mod_globals.opt_exp = False
        mod_globals.opt_dump = self.button['DUMP'].active
        mod_globals.opt_can2 = self.button['CAN2 (Multimedia CAN)'].active
        if self.mainbutton.text:
            if 'com0' in self.mainbutton.text.lower() or 'com6' in self.mainbutton.text.lower():
                mod_globals.opt_port = '127.0.0.1:35000'
            elif 'wifi' in self.mainbutton.text.lower():
                mod_globals.opt_port = '192.168.0.10:35000'
            else:
                bt_device = self.mainbutton.text.split('>')
                if mod_globals.os != 'android':
                    try:
                        mod_globals.opt_port = bt_device[1]
                    except:
                        mod_globals.opt_port = bt_device[0]
                else:
                    mod_globals.opt_port = bt_device[0]
                if len(bt_device) > 1:
                    mod_globals.opt_dev_address = bt_device[-1]
                mod_globals.bt_dev = self.mainbutton.text
        self.settings.save()
        lang = get_lang_dict(mod_globals.opt_lang)
        if lang:
            mod_globals.language_dict = lang
        fs = mod_globals.fontSize
        if not mod_globals.opt_port and not mod_globals.opt_demo:
            MyPopup_close(cont=MyLabel(text='Not select ELM!', font_size=(fs*3), size_hint = (1, 0.7)))
        elif mod_globals.opt_lang == 'SELECT':
            MyPopup_close(cont=MyLabel(text='Not select language!', font_size=(fs*3), size_hint = (1, 0.7)), lang=False)
        elif not mod_globals.savedEcus and not mod_globals.opt_scan and not mod_globals.opt_ecuid_on and not os.path.exists(mod_globals.user_data_dir + '/' + mod_globals.savedEcus):
            MyPopup_close(cont=MyLabel(text='Not select savedEcus!', font_size=(fs*3), size_hint = (1, 0.7)))
        elif mod_globals.opt_ecuid_on and not mod_globals.opt_ecuid:
            MyPopup_close(cont=MyLabel(text='Not enter ECU!', font_size=(fs*3), size_hint = (1, 0.7)))
        else:
            self.stop()

    def change_orientation(self, inst, val):
        if val:
            set_orientation_landscape()
            mod_globals.screen_orient = True
        else:
            set_orientation_portrait()
            mod_globals.screen_orient = False

    def build(self):
        if mod_globals.os == 'android':
            permissionIsGranted = True
            permissionErrorLayout = GridLayout(cols=1, padding=15, spacing=15, size_hint=(1, 1))
            permissionErrorLayout.add_widget(MyLabel(text='Permission not granted', font_size=(fs*0.9), height=(fs*1.4), multiline=True, size_hint=(1, 1)))
            for perm in permissions:
                if (check_permission(perm) == False):
                    permissionIsGranted = False
                    permissionErrorLayout.add_widget(MyLabel(text=perm + ':' +str(check_permission(perm)), font_size=(fs*0.9), height=(fs*1.4), multiline=True, size_hint=(1, 1)))
            if api_version > 29:
                if (Environment.isExternalStorageManager() == False):
                    permissionErrorLayout.add_widget(MyLabel(text='FILES_ACCESS_PERMISSION : False', font_size=(fs*0.9), height=(fs*1.4), multiline=True, size_hint=(1, 1)))
                    permissionIsGranted = False
            if api_version == 29:
                if (Environment.isExternalStorageLegacy() == False):
                    permissionErrorLayout.add_widget(MyLabel(text='LegacyExternalStorage : False', font_size=(fs*0.9), height=(fs*1.4), multiline=True, size_hint=(1, 1)))
                    permissionIsGranted = False
            permissionErrorLayout.add_widget(MyLabel(text='Android api: ' + str(api_version), font_size=(fs*0.9), height=(fs*1.4), multiline=True, size_hint=(1, 1)))
            permissionErrorLayout.add_widget(MyLabel(text='Version: ' + str(__version__), font_size=(fs*0.9), height=(fs*1.4), multiline=True, size_hint=(1, 1)))
            permissionErrorLayout.add_widget(MyButton(text='Click to exit and check permissions!!!', valign = 'middle', halign = 'center', size_hint=(1, 1), font_size=fs*1.5, height=fs*3, on_press=exit))
            if (permissionIsGranted == False):
                return permissionErrorLayout
        layout = GridLayout(cols=1, padding=fs/4, spacing=fs/4, size_hint=(1.0, None))
        layout.bind(minimum_height=layout.setter('height'))
        pycl = MyLabel(text='PyClip3', height=(fs*3), font_size=fs*2, bgcolor = (0.5, 0.5, 0, 1))
        layout.add_widget(pycl)
        layout.add_widget(MyLabel(text='Data directory : ' + mod_globals.user_data_dir, font_size=(fs*0.5), height=(fs), multiline=True, bgcolor = (0.5, 0.5, 0, 1)))
        get_zip()
        try:
            self.archive = str(mod_globals.db_archive_file).rpartition('/')[2]
        except:
            self.archive = str(mod_globals.db_archive_file).rpartition('\\')[2]
        if self.archive == 'None':
            self.archive = 'NOT BASE.\n Download pyrendata_XXX.zip and copy folder pyren'
            root = GridLayout(cols=1, padding=15, spacing=15, size_hint=(1, 1))
            popup = MyPopup(title='INFO', title_size=fs*1.5, title_align='center', content=MyLabel(text=self.archive, font_size=(fs*5), size_hint=(1, 1)), size_hint=(1, 1))
            return popup
        layout.add_widget(MyLabel(text='DB archive : ' + self.archive, font_size=(fs*0.5), height=(fs), multiline=True, bgcolor = (0.5, 0.5, 0, 1)))
        termbtn = MyButton(text='MACRO', height=fs*2, on_press=self.term)
        check = MyButton(text='Check ELM327', height=(fs*4), on_press=self.check_elm)
        gobtn = MyButton(text='START', height=(fs*2.5), on_press=self.finish)
        layout.add_widget(gobtn)
        layout.add_widget(self.make_opt_ecuid(mod_globals.opt_ecuid_on))
        layout.add_widget(self.make_savedEcus())
        layout.add_widget(self.make_bt_device_entry())
        layout.add_widget(self.make_language_entry())
        layout.add_widget(self.make_box_switch('Scan vehicle', mod_globals.opt_scan))
        layout.add_widget(self.make_box_switch('Demo mode', mod_globals.opt_demo))
        layout.add_widget(self.make_box_switch('DUMP', mod_globals.opt_dump))
        layout.add_widget(self.make_box_switch('Orientation landscape', mod_globals.screen_orient, self.change_orientation))
        layout.add_widget(self.make_box_switch('Generate logs', True if len(mod_globals.opt_log) > 0 else False))
        layout.add_widget(self.make_input('Log name', mod_globals.opt_log))
        layout.add_widget(self.make_box_switch('CSV Log',mod_globals.opt_csv))
        layout.add_widget(self.make_box_switch('CAN2 (Multimedia CAN)', mod_globals.opt_can2))
        layout.add_widget(self.make_input('Font size', str(mod_globals.fontSize)))
        layout.add_widget(self.make_box_switch('KWP Force SlowInit', mod_globals.opt_si))
        layout.add_widget(self.make_box_switch('Use CFC0', mod_globals.opt_cfc0))
        layout.add_widget(termbtn)
        layout.add_widget(MyLabel(text='PyClip3 by andru666    26-06-2023', font_size=(fs*0.5), height=(fs*0.7)))
        self.lay = layout
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5,
         'center_y': 0.5})
        root.add_widget(layout)
        return root

    def term(self, instance):
        self.finish(instance)
        self.stop()
        from mod_term import Term
        Term(mod_globals.opt_port, mod_globals.opt_speed, mod_globals.opt_log).test()

    def check_elm(self, instance):
        self.finish(instance)
        from cmdr_chkelm import CHECK
        CHECK()
        
def destroy():
    exit()

def kivyScreenConfig():
    global resizeFont
    Window.bind(on_close=destroy)
    if mod_globals.os == 'android':
        if not mod_globals.screen_orient:
            set_orientation_portrait()
        else:
            set_orientation_landscape()
    while 1:
        config = screenConfig()
        config.run()
        if not resizeFont:
            return
        resizeFont = False


def main():
    if not os.path.exists(mod_globals.crash_dir):
        os.makedirs(mod_globals.crash_dir)
    if not os.path.exists(mod_globals.cache_dir):
        os.makedirs(mod_globals.cache_dir)
    if not os.path.exists(mod_globals.log_dir):
        os.makedirs(mod_globals.log_dir)
    if not os.path.exists(mod_globals.dumps_dir):
        os.makedirs(mod_globals.dumps_dir)
    if not os.path.exists(mod_globals.csv_dir):
        os.makedirs(mod_globals.csv_dir)
    if not os.path.exists(mod_globals.macro_dir):
        os.makedirs(mod_globals.macro_dir)
    if not os.path.exists(mod_globals.scen_dir):
        os.makedirs(mod_globals.scen_dir)
    
    import glob
    zip_macro = sorted(glob.glob(os.path.join('./', 'macro.zip')), reverse=True)
    if len(zip_macro):
        import zipfile
        with zipfile.ZipFile(zip_macro[0], 'r') as zip_file:
            zip_file.extractall(os.path.join(mod_globals.user_data_dir, 'macro'))
    mod_globals.Settings()
    kivyScreenConfig()
    #elm = ELM(mod_globals.opt_port, mod_globals.opt_speed, mod_globals.opt_log)
    try:
        elm = ELM(mod_globals.opt_port, mod_globals.opt_speed, mod_globals.opt_log)
    except:
        if mod_globals.opt_lang == 'RU':
            labelText = '''
                Не удалось подключиться к ELM.

                Возможные причины:
                - Bluetooth не включен 
                - к вашему ELM подключены другие приложения, например Torque
                - другое устройство использует этот ELM
                - ELM не подключен
                - ELM считывается под новым именем или оно изменило свое название

                Проверьте подключение к ELM и повторите попытку.
            '''
            tit = "Ошибка подключения ELM"
        else:
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
            tit = 'ELM connection error'
        lbltxt = MyLabel(text=labelText, font_size=mod_globals.fontSize)
        popup_load = MyPopup(title=tit, content=lbltxt, size=(Window.size[0]*0.9, Window.size[1]*0.9), on_dismiss=exit)
        popup_load.open()
        base.runTouchApp()
        exit(2)
    if mod_globals.opt_speed < mod_globals.opt_rate and not mod_globals.opt_demo:
        elm.port.soft_boudrate(mod_globals.opt_rate)
    se = ScanEcus(elm)
    if mod_globals.opt_scan or mod_globals.savedEcus == 'Select' or mod_globals.savedEcus == '':
        mod_globals.savedEcus = 'savedEcus.p'
    SEFname = mod_globals.user_data_dir + '/' + mod_globals.savedEcus
    if mod_globals.opt_can2:
        if mod_globals.opt_can2 or mod_globals.savedEcus == 'Select' or mod_globals.savedEcus == '':
            mod_globals.savedEcus = 'savedEcus_can2.p'
        SEFname = mod_globals.user_data_dir + '/' + mod_globals.savedEcus_can2
    if not os.path.exists(SEFname):
        SEFname = mod_globals.user_data_dir + '/' + mod_globals.savedEcus

    if mod_globals.opt_demo and len(mod_globals.opt_ecuid) > 0 and mod_globals.opt_ecuid_on:
        se.read_Uces_file(all=True)
        se.detectedEcus = []
        for i in mod_globals.opt_ecuid.split(','):
            if i in list(se.allecus.keys()):
                se.allecus[i]['ecuname'] = i
                se.allecus[i]['idf'] = se.allecus[i]['ModelId'][2:4]
                if se.allecus[i]['idf']!='':
                    if se.allecus[i]['idf'][0] == '0':
                        se.allecus[i]['idf'] = se.allecus[i]['idf'][1]
                se.allecus[i]['pin'] = 'can'
                se.detectedEcus.append(se.allecus[i])

    else:
        if mod_globals.opt_scan:
            se.chooseModel(mod_globals.opt_car)
        se.scanAllEcus()
    fs = mod_globals.fontSize
    lbltxt = MyLabel(text='Loading language', font_size=fs*2, size_hint=(1, 1))
    popup_load = MyPopup(title='Status', content=lbltxt, size=(Window.size[0]*0.9, Window.size[1]*0.9), size_hint=(None, None))
    base.runTouchApp(embedded=True)
    popup_load.open()
    base.EventLoop.idle()
    sys.stdout.flush()
    base.EventLoop.window.remove_widget(popup_load)
    popup_load.dismiss()
    base.stopTouchApp()
    base.EventLoop.window.canvas.clear()

    while 1:
        clearScreen()
        choosen_ecu = se.chooseECU(mod_globals.opt_ecuid)
        mod_globals.opt_ecuid = ''
        if choosen_ecu == -1:
            continue
        ecucashfile = mod_globals.cache_dir + choosen_ecu['ModelId'] + '_' + mod_globals.opt_lang + '.p'
        if os.path.isfile(ecucashfile):
            ecu = pickle.load(open(ecucashfile, 'rb'))
        else:
            ecu = ECU(choosen_ecu, mod_globals.language_dict)
            pickle.dump(ecu, open(ecucashfile, 'wb'))
        ecu.initELM(elm)
        if mod_globals.opt_demo:
            lbltxt = MyLabel(text='Loading dump', font_size=fs*2, size_hint=(1, 1))
            popup_init = MyPopup(title='Initializing', content=lbltxt, size=(Window.size[0]*0.9, Window.size[1]*0.9), size_hint=(None, None))
            base.runTouchApp(embedded=True)
            popup_init.open()
            base.EventLoop.idle()
            sys.stdout.flush()
            ecu.loadDump()
            base.EventLoop.window.remove_widget(popup_init)
            popup_init.dismiss()
            base.stopTouchApp()
            base.EventLoop.window.canvas.clear()
        elif mod_globals.opt_dump:
            lbltxt = MyLabel(text='Save dump', font_size=fs*2, size_hint=(1, 1))
            popup_init = MyPopup(title='Initializing', content=lbltxt, size=(Window.size[0]*0.9, Window.size[1]*0.9), size_hint=(None, None))
            base.runTouchApp(embedded=True)
            popup_init.open()
            base.EventLoop.idle()
            sys.stdout.flush()
            ecu.saveDump(lbltxt)
            base.EventLoop.window.remove_widget(popup_init)
            popup_init.dismiss()
            base.stopTouchApp()
            base.EventLoop.window.canvas.clear()
        ecu.show_screens()

if __name__ == '__main__':
    main()
