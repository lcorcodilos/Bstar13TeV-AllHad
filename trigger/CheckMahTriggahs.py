import ROOT
from ROOT import *
import sys

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim

if sys.argv[1] == '16':
    f = TFile.Open('data16C_sample.root')
    trigs = 'HLT_PFHT800,HLT_PFHT900,HLT_PFJet450'
elif sys.argv[1] == '17':
    f = TFile.Open('data17C_sample.root')

inTree = f.Get("Events")
elist,jsonFiter = preSkim(inTree,None,'')
inTree = InputTree(inTree,elist)
treeEntries = 1000000#inTree.entries
print 'Total events: '+str(treeEntries)

count = 0
count_2jets = 0
count_2pt = 0
count_trigs = {'HLT_PFHT800,HLT_PFHT900,HLT_PFJet450':0,
               'HLT_PFHT780':0,
               'HLT_PFHT890':0,
               'HLT_PFHT1050,HLT_PFJet500':0,
               'HLT_AK8PFHT800_TrimMass50':0,
               'HLT_AK8PFJet400_TrimMass30':0,
               'HLT_AK8PFJet400':0,
               "HLT_PFHT510":0
               }

trig_list17 = ['HLT_PFHT780','HLT_PFHT890','HLT_PFHT1050,HLT_PFJet500','HLT_AK8PFHT800_TrimMass50','HLT_AK8PFJet400_TrimMass30','HLT_AK8PFJet400','HLT_PFHT510']

for entry in range(0,treeEntries):
    count = count + 1
    sys.stdout.write("%i / %i ... %.2f \r" % (count,treeEntries,100*float(count)/float(treeEntries)))
    sys.stdout.flush()

    event = Event(inTree, entry)

    fatJetsColl = Collection(event, "FatJet")

    if len(fatJetsColl) < 2:
        continue 

    count_2jets += 1
    
    if fatJetsColl[0].pt > 400 and fatJetsColl[0].pt > 400:
        
        count_2pt += 1

        if sys.argv[1] == '16':
            passt = False
            for t in trigs.split(','):
                try:
                    if inTree.readBranch(t):
                        passt = True
                except:
                    continue

            if not passt:
                continue

            count_trigs[trigs] += 1

        elif sys.argv[1] == '17':
            for t in trig_list17:
                passt = False
                for t1 in t.split(','):
                    try:
                        if inTree.readBranch(t1):
                            passt = True
                    except:
                        continue

                if not passt:
                    continue

                count_trigs[t]+=1

print '\n'

print 'Events with 2 jets: ' + str(count_2jets)
print 'Events with 2 high pt jets: ' + str(count_2pt)
if sys.argv[1] == '16':
    print 'Events that also pass '+trigs+': ' + str(count_trigs[trigs])
elif sys.argv[1] == '17':
    for t in trig_list17:
        print 'Events that also pass '+t+': '+str(count_trigs[t])



