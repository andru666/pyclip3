# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: /build/PyCLIP/android/app/cmdr_example.py
# Compiled at: 2018-11-25 22:57:49
import os, sys, time, pyren, mod_globals
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
try:
    import androidhelper as android
    mod_globals.os = 'android'
except:
    try:
        import android
        mod_globals.os = 'android'
    except:
        pass

if mod_globals.os != 'android':
    try:
        import serial
        from serial.tools import list_ports
    except ImportError:
        sys.exit()

from mod_elm import ELM
from mod_scan_ecus import ScanEcus
from mod_ecu import ECU
from mod_optfile import *
from mod_utils import *

def prepareECU():
    global ecu
    global elm
    pyren.optParser()
    if len(mod_globals.opt_log) == 0:
        mod_globals.opt_log = 'commander_log.txt'
    print('Opening ELM')
    elm = ELM(mod_globals.opt_port, mod_globals.opt_speed, mod_globals.opt_log)
    print('Loading ECUs list')
    se = ScanEcus(elm)
    if not os.path.isfile('savedEcus.p') or mod_globals.opt_scan:
        se.chooseModel(mod_globals.opt_car)
    se.scanAllEcus()
    print('Loading language ')
    sys.stdout.flush()
    lang = optfile('../Location/DiagOnCan_' + mod_globals.opt_lang + '.bqm', True)
    mod_globals.language_dict = lang.dict
    print('Done')
    choosen_ecu = se.chooseECU(mod_globals.opt_ecuid)
    if choosen_ecu == -1:
        print('#\n#\n#\n', '#   Unknown ECU defined!!!\n', '#\n#\n#\n')
        exit(1)
    ecucashfile = './cache/' + choosen_ecu['ModelId'] + '_' + mod_globals.opt_lang + '.p'
    if os.path.isfile(ecucashfile):
        ecu = pickle.load(open(ecucashfile, 'rb'))
    else:
        ecu = ECU(choosen_ecu, lang.dict)
        pickle.dump(ecu, open(ecucashfile, 'wb'))
    ecu.initELM(elm)


def main():
    prepareECU()
    print(elm.request(req='2180', positive='61', cache=False))
    print(elm.request(req='2181', positive='61', cache=False))
    for i in range(1, 10):
        value1, datastr1 = ecu.get_st('E019')
        value2, datastr2 = ecu.get_pr('PR141')
        value3, datastr3 = ecu.get_val('PR091')
        value4, datastr4 = ecu.get_id('ID008')
        clearScreen()
        print()
        print('E019 ', value1)
        print('RP141', value2)
        print('PR091', value3)
        print('ID008', value4)
        time.sleep(0.3)

    ecu.run_cmd('RZ001')


if __name__ == '__main__':
    main()