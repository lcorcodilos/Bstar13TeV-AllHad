import ROOT
from ROOT import *

import FatJetNNHelper
import Bstar_Functions_local
from Bstar_Functions_local import FindDeepAK8csv, Load_jetNano
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event



import time
import sys

file_string = Load_jetNano('signalLH1200')
file = TFile.Open(file_string)

inTree = file.Get("Events")
elist,jsonFiter = preSkim(inTree,None,'')
inTree = InputTree(inTree,elist)

# CSV method
# start_csv = time.time()

# DeepAK8_csv_locations = FindDeepAK8csv('signalLH1200')
# DAK8_Helper = FatJetNNHelper.FatJetNNHelper('DeepAK8Results/signalLH1200.csv',True)

# for entry in range(1000):
# 	sys.stdout.write("\r%i / 1000 ..." % (entry))
# 	sys.stdout.flush()
# 	event = Event(inTree, entry)

# 	DAK8_Helper.set_event(inTree.readBranch('event'))
# 	score = DAK8_Helper.get_binarized_score_top(0)

# stop_csv = time.time()

# print 'CSV method took ' + str(stop_csv-start_csv)+' seconds'

# TTree method
start_tree = time.time()

DAK8_file = TFile.Open('DeepAK8Results/signalLH1200.root')
DAK8_tree = DAK8_file.Get('DeepAK8')

for entry in range(1000):
	sys.stdout.write("\r%i / 1000 ..." % (entry))
	sys.stdout.flush()
	event = Event(inTree, entry)

	DAK8_tree.Draw('>>elist','(nn_version=="Decorrelated")&&(jet_no==0)&&(event=='+str(event.event)+')',"entrylist")
	elist = ROOT.gDirectory.Get('elist')
	DAK8_tree.GetEntry(elist.GetEntry(0))
	score = DAK8_tree.binarized_score_top


stop_tree = time.time()

print 'TTree method took ' + str(stop_tree-start_tree)+' seconds'