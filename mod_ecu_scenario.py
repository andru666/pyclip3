# -*- coding: utf-8 -*-
import re, os, mod_globals

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
    if mod_globals.os != 'android': print(scenarioName)
    try:
        if scenarioName.endswith('_ecu'):
            name = scenarioName[:len(scenarioName)-4]
        elif scenarioName.endswith('_const'):
            name = scenarioName[:len(scenarioName)-6]
        else:
            name = scenarioName
        scen = __import__(name)
        scen.run(elm, ecu, command, scenarioData)
        return True
    except ModuleNotFoundError:
        scen = __import__('show_scen')
        scen.run(elm, ecu, command, scenarioData)
        return True