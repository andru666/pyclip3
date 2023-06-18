# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: /build/PyCLIP/android/app/cmdr_odometr.py
# Compiled at: 2018-11-25 22:57:49
import os, sys, pyren, mod_globals
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

def prepareECUs():
    global elm
    global lang
    global se
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
    return se.detectedEcus


def chooseEcu(ecu_number):
    global ecu
    choosen_ecu = se.chooseECU(ecu_number)
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
    list = prepareECUs()
    tot = ''
    for l in list:
        if l['idf'] == '1':
            print('### Connecting to Engine ###')
            chooseEcu(l['ecuname'])
            tot += 'Engine    PR025 : '
            num, string = ecu.get_pr('PR025')
            print(pyren_encode(string))
            tot += str(num)
            tot += '\n'
            tot += 'Engine    PR992 : '
            num, string = ecu.get_pr('PR992')
            print(pyren_encode(string))
            tot += str(num)
            tot += '\n'
            num, string = ecu.get_pr('PR391')
            print(pyren_encode(string))
            num, string = ecu.get_pr('PR412')
            print(pyren_encode(string))
            print()
        if l['idf'] == '2':
            print('### Connecting to ABS ###')
            chooseEcu(l['ecuname'])
            tot += 'ABS       PR121 : '
            num, string = ecu.get_pr('PR121')
            print(pyren_encode(string))
            tot += str(num)
            tot += '\n'
            print()
        if l['idf'] == '3':
            print('### Connecting to TDB ###')
            chooseEcu(l['ecuname'])
            tot += 'TDB       PR009 : '
            num, string = ecu.get_pr('PR009')
            print(pyren_encode(string))
            tot += str(num)
            tot += '\n'
            tot += 'TDB (km)  PR025 : '
            num, string = ecu.get_pr('PR025')
            print(pyren_encode(string))
            tot += str(num)
            tot += '\n'
            tot += 'TDB (mil) PR026 : '
            num, string = ecu.get_pr('PR026')
            print(pyren_encode(string))
            tot += str(num)
            tot += '\n'
            print()

    if mod_globals.os != 'android':
        print(pyren_encode('Listening to CAN. Please wait a bit...'))
        elm.cmd('at z')
        elm.cmd('at e1')
        elm.cmd('at l1')
        elm.cmd('at h1')
        elm.cmd('at d1')
        elm.cmd('at caf0')
        elm.cmd('at sp 6')
        elm.cmd('at al')
        elm.portTimeout = 1
        elm.cmd('at cra 5C5')
        resp = elm.cmd('atma')
        elm.cmd('at')
        for l in resp.split('\n'):
            if l.upper().startswith('5C5'):
                kmt = l[9:18].replace(' ', '')
                tot += 'Frame 5C5  : '
                tot = tot + str(int(kmt, 16))
                tot += '\n'
                break

        elm.cmd('at cra 715')
        elm.portTimeout = 5
        resp = elm.cmd('atma')
        elm.portTimeout = 1
        elm.cmd('at')
        for l in resp.split('\n'):
            if l.upper().startswith('715'):
                kmt = l[6:15].replace(' ', '')
                tot += 'Frame 715  : '
                tot = tot + str(int(kmt, 16))
                tot += '\n'
                break

        elm.cmd('at cra 5FD')
        elm.portTimeout = 5
        resp = elm.cmd('atma')
        elm.portTimeout = 1
        elm.cmd('at')
        for l in resp.split('\n'):
            if l.upper().startswith('5FD'):
                kmt = l[6:15].replace(' ', '')
                tot += 'Frame 5FD  : '
                tot = tot + str(int(kmt, 16))
                tot += '\n'
                break

    elm.lastMessage = tot


if __name__ == '__main__':
    main()