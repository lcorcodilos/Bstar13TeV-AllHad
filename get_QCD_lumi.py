import ROOT
from ROOT import *
import sys

import Bstar_Functions_local
from Bstar_Functions_local import Load_jetNano, LoadConstants

year = sys.argv[1]

if year == '16':
    files = {
        'QCDHT700':None,
        'QCDHT1000':None,
        'QCDHT1500':None,
        'QCDHT2000':None,
        'QCDHT700ext':None,
        'QCDHT1000ext':None,
        'QCDHT1500ext':None,
        'QCDHT2000ext':None
    }
else:
    files = {
        'QCDHT700':None,
        'QCDHT1000':None,
        'QCDHT1500':None,
        'QCDHT2000':None
    }

nevents = {}
xsecs = {}
lumis = {}
for f in files.keys():
    files[f] = TFile.Open(Load_jetNano(f,year))
    nevents[f] = -1
    xsecs[f] = -1

for q in sorted(nevents.keys()):
    runs_tree = files[q].Get("Runs")
    nevents_gen = 0
    for i in runs_tree:
        nevents_gen+=i.genEventCount

    nevents[q] = float(nevents_gen)

    xsecs[q] = float(LoadConstants(year)[q.replace('ext','')+'_xsec'])

    lumis[q] = nevents[q]/xsecs[q]

    print 'Weight for '+q+' = ' + str(xsecs[q]/nevents[q]*float(LoadConstants(year)['lumi']))

if year == '16':
    for q in [q for q in lumis.keys() if 'ext' in q]:
        lumis[q.replace('ext','')] =  lumis[q.replace('ext','')] + lumis[q]
        del lumis[q]
        nevents[q.replace('ext','')] =  nevents[q.replace('ext','')] + nevents[q]
        del nevents[q]


final_lumi = min([lumis[l] for l in lumis.keys()])
print 'Scale to ' + str(final_lumi)

for q in sorted(lumis.keys()):
    print 'Final weight '+q+' '+str(float(xsecs[q])/float(nevents[q])*float(final_lumi))