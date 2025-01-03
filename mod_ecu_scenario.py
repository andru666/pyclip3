# -*- coding: utf-8 -*-
import re, os, mod_globals, sys
from mod_utils import *

if mod_globals.os == 'android':
    from jnius import autoclass
    Environment = autoclass('android.os.Environment')
    import sys
    scen_dir = Environment.getExternalStorageDirectory().getAbsolutePath() + '/pyren/scen3/'
    if not os.path.exists(scen_dir):
        os.makedirs(scen_dir)
    sys.path.append(scen_dir)
else:
    scen_dir = mod_globals.user_data_dir + '/scen3/'
    if not os.path.exists(scen_dir):
        os.makedirs(scen_dir)
    sys.path.append(scen_dir)
def playScenario(command, ecu, elm):
    services = ecu.Services
    scenarioName, scenarioData = command.scenario.split('#')
    if scenarioName.startswith('scm'):
        scenarioName = scenarioName.split(':')[1]
        ecuNumberPattern = re.compile(r'_\d{5}')
        ecuNumberIndex = ecuNumberPattern.search(scenarioData)
        if ecuNumberIndex:
            scenarioName = scenarioData[:scenarioData.find(ecuNumberIndex.group(0))]
        else:
            scenarioName = scenarioData
        scenarioData = scenarioData
    else:
        scenarioData = scenarioData[5:].replace('=', '_').replace('.xml', '').replace('&', '_')+'.xml'
        scenarioName = scenarioName.split(':')[1]
        ecuNumberPattern = re.compile(r'_\d{5}')
        ecuNumberIndex = ecuNumberPattern.search(scenarioData)
        scenarioName = scenarioData[:scenarioData.find(ecuNumberIndex.group(0))]
        scenarioData = 'ecudata/'+scenarioData
    if mod_globals.os != 'android':
        print(scenarioName)
    try:
        if scenarioName.endswith('_ecu'):
            name = scenarioName[:len(scenarioName)-4]
        elif scenarioName.endswith('_const'):
            name = scenarioName[:len(scenarioName)-6]
        else:
            name = scenarioName
        scen = __import__(name.lower())
        scen.run(elm, ecu, command, scenarioData)
        return True
    except:
        scen = __import__('show_scen')
        try:
            scen.run(elm, ecu, command, scenarioData)
        except:
            return False
        return True