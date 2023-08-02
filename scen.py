# -*- coding: utf-8 -*-
import mod_zip
from collections import OrderedDict

def DOOM(data):
    ScmParam = {}
    ScmSet = {}
    if 'ecudata' in data:
        sdata = data.rsplit('_', 2)[0].replace('ecudata', 'scendata') + '_text.xml'
        dt = data.replace('_ecu_', '_const_')
        datas = [sdata, dt, data]
    else:
        datas = [data]
    for dat in datas:
        try:
            DOMTree = mod_zip.get_xml_scenario(dat)
        except:
            continue
        ScmParams = DOMTree.getElementsByTagName('ScmParam')
        ScmSets = DOMTree.getElementsByTagName('ScmSet')
        if len(ScmParams):
            for Param in ScmParams:
                name = Param.getAttribute('name')
                value = Param.getAttribute('value')
                ScmParam[name] = value
        if len(ScmSets):
            for Set in ScmSets:
                if len(Set.attributes) >= 1:
                    setname = Set.getAttribute('name')
                    Scm_Set = Set.getElementsByTagName('ScmSet')
                    ScmParams = Set.getElementsByTagName('ScmParam')
                    scmParamsDict = OrderedDict()
                    if Scm_Set:
                        for sets in Scm_Set:
                            setn = sets.getAttribute('name')
                            ScmParamS = sets.getElementsByTagName('ScmParam')
                            scmParamsDict[setn] = OrderedDict()
                            for ParamS in ScmParamS:
                                name = ParamS.getAttribute('name')
                                value = ParamS.getAttribute('value')
                                scmParamsDict[setn][name] = value
                    for Param in ScmParams:
                        name = Param.getAttribute('name')
                        value = Param.getAttribute('value')
                        scmParamsDict[name] = value
                    ScmSet[setname] = scmParamsDict
    return ScmParam, ScmSet
#DOOM('ecudata/lecture contexte de choc 16p_ecu_10306.xml')