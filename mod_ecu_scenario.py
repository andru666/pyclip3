#Embedded file name: /build/PyCLIP/android/app/mod_ecu_scenario.py
import re, os, mod_globals

if mod_globals.os == 'android':
    from jnius import autoclass
    Environment = autoclass('android.os.Environment')
    import sys
    scen_dir = Environment.getExternalStorageDirectory().getAbsolutePath() + '/pyren/scen/'
    if not os.path.exists(scen_dir):
        os.makedirs(scen_dir)
    sys.path.append(scen_dir)

def playScenario(command, ecu, elm):
    services = ecu.Services
    scenarioName, scenarioData = command.scenario.split('#')
    if scenarioName.lower().startswith('scm'):
        scenarioName = scenarioName.split(':')[1]
        ecuNumberPattern = re.compile(r'_\d{5}')
        ecuNumberIndex = ecuNumberPattern.search(scenarioData)
        scenarioName = scenarioData[:scenarioData.find(ecuNumberIndex.group(0))].lower()
        scenarioData = scenarioData.lower()
    else:
        scenarioData = scenarioData[5:].replace('=', '_').replace('.xml', '').replace('&', '_')+'.xml'
        scenarioName = scenarioName.split(':')[1]
        ecuNumberPattern = re.compile(r'_\d{5}')
        ecuNumberIndex = ecuNumberPattern.search(scenarioData)
        scenarioName = scenarioData[:scenarioData.find(ecuNumberIndex.group(0))].lower()
        scenarioData = 'ecudata/'+scenarioData.lower()
    if scenarioName == 'scen5':
        if scenarioName.endswith('_ecu'):
            scen = __import__(scenarioName[:len(scenarioName)-4])
        elif scenarioName.endswith('_const'):
            scen = __import__(scenarioName[:len(scenarioName)-6])
        else:
            scen = __import__(scenarioName)
        scen.run(elm, ecu, command, scenarioData)
        return True
    else:    
        if True:
            if scenarioName.endswith('_ecu'):
                scen = __import__(scenarioName[:len(scenarioName)-4])
            elif scenarioName.endswith('_const'):
                scen = __import__(scenarioName[:len(scenarioName)-6])
            else:
                scen = __import__(scenarioName)
            scen.run(elm, ecu, command, scenarioData)
            return True
        else:
            scen = __import__('show_scen')
            scen.run(elm, ecu, command, scenarioData)
            return True