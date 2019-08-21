#! /usr/bin/env python

###################################################################
##                               ##
## Name: TWrate.py                       ##
## Author: Kevin Nash                        ##
## Date: 5/28/2015                       ##
## Purpose: This program creates the numerator and denominator   ##
##          used by TWTrigger_Maker.py to create trigger     ##
##          Efficiency curves.                   ##
##                               ##
###################################################################

import os
import glob
import math
from math import sqrt,exp
import ROOT
from ROOT import *

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.JetSysColl import JetSysColl, JetSysObj
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim

import Bstar_Functions_local  
from Bstar_Functions_local import *

import sys
from optparse import OptionParser
from array import *

parser = OptionParser()

parser.add_option('-s', '--set', metavar='F', type='string', action='store',
                  default   =   'data',
                  dest      =   'set',
                  help      =   'dataset (ie data,ttbar etc)')
parser.add_option('-y', '--y', metavar='F', type='string', action='store',
                  default   =   '16',
                  dest      =   'year',
                  help      =   '16, 17')
parser.add_option('-n', '--num', metavar='F', type='string', action='store',
                  default   =   '1',
                  dest      =   'num',
                  help      =   'job number')
parser.add_option('-j', '--jobs', metavar='F', type='string', action='store',
                  default   =   '1',
                  dest      =   'jobs',
                  help      =   'number of jobs')
parser.add_option('-t', '--tname', metavar='F', type='string', action='store',
                  default   =   'HLT_PFHT800,HLT_PFHT900,HLT_PFJet450', # For 2017 use 'HLT_PFHT1050,HLT_PFJet500'
                  dest      =   'tname',
                  help      =   'trigger name')
parser.add_option('-p', '--pretname', metavar='F', type='string', action='store',
                  default   =   'HLT_Mu50',# For 2016, can use 'HLT_PFHT475', For 2017 use 'HLT_PFHT510' or 'HLT_IsoMu27'
                  dest      =   'pretname',
                  help      =   'pre-trigger name')

print "Test"
(options, args) = parser.parse_args()
print "Options summary"
print "=================="
for  opt,value in options.__dict__.items():
    #print str(option)+ ": " + str(options[option]) 
    print str(opt) +': '+ str(value)
print "=================="
print "" 

# Prep for deepcsv b-tag if deepak8 is off
# From https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration
gSystem.Load('libCondFormatsBTauObjects') 
gSystem.Load('libCondToolsBTau') 
if options.year == '16':
    calib = BTagCalibration('DeepCSV', 'SFs/DeepCSV_2016LegacySF_V1.csv')
elif options.year == '17':
    calib = BTagCalibration('DeepCSV', 'SFs/subjet_DeepCSV_94XSF_V4_B_F.csv')
elif options.year == '18':
    calib = BTagCalibration('DeepCSV', 'SFs/DeepCSV_102XSF_V1.csv')
v_sys = getattr(ROOT, 'vector<string>')()
v_sys.push_back('up')
v_sys.push_back('down')

reader = BTagCalibrationReader(
    0,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
    "central",      # central systematic type
    v_sys,          # vector of other sys. types
)   

reader.load(
    calib, 
    0,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
    "incl"      # measurement type
) 

######################################
# Setup grid production if necessary #
######################################

#If running on the grid we access the script within a tarred directory
di = ""
# if options.grid == 'on':
#     di = "tardir/"
#     sys.path.insert(0, 'tardir/')

# gROOT.Macro(di+"rootlogon.C")


#################################
# Load cut values and constants #
#################################
Cons = LoadConstants(options.year)
lumi = Cons['lumi']

Wpurity = 'HP'
wtagsf = Cons['wtagsf_HP']
wtagsfsig = Cons['wtagsfsig_HP']

Cuts = LoadCuts("default",options.year)

jetcoll = "FatJet"

mass_name = ''

#####################
# Get trigger names #
#####################
tnameOR = ''
tname = options.tname.split(',')
Tstr_list = [options.pretname]
pretrigName = options.pretname # defaults to NONE and nothing happens
for iname in range(0,len(tname)):
    tnameOR+=tname[iname]
    if iname!=len(tname)-1:
        tnameOR+='OR'
    Tstr_list.append(tname[iname])

print Tstr_list


#######################
# Setup job splitting #
#######################
jobs=int(options.jobs)
if jobs != 1:
    num=int(options.num)
    jobs=int(options.jobs)
    print "Running over " +str(jobs)+ " jobs"
    print "This will process job " +str(num)
else:
    print "Running over all events"


#############################
# Make new file for storage #
#############################
if jobs != 1:
    f = TFile( "TWTrigger"+options.set+options.year+tnameOR+"_pre_"+options.pretname+"_job"+options.num+"of"+options.jobs+".root", "recreate" )
else:
    f = TFile( "TWTrigger"+options.set+options.year+tnameOR+"_pre_"+options.pretname+".root", "recreate" )

###################
# Book histograms #
###################
Htpreuntrig          = TH1D("Htpreuntrig",           "",             400,  0,  4000 )
Htuntrig          = TH1D("Htuntrig",           "",             400,  0,  4000 )

Htpreuntrig.Sumw2()
Htuntrig.Sumw2()

Htpre          = TH1D("Htpre",           "",             400,  0,  4000 )
Ht          = TH1D("Ht",           "",             400,  0,  4000 )

Htpre.Sumw2()
Ht.Sumw2()

Htprettags          = TH1D("Htprettags",           "",             400,  0,  4000 )
Htttags         = TH1D("Htttags",           "",             400,  0,  4000 )

Htprettags.Sumw2()
Htttags.Sumw2()

Ptpre          = TH1D("Ptpre",           "",             200,  0,  2000 )
Pt          = TH1D("Pt",           "",             200,  0,  2000 )

Ptpre.Sumw2()
Pt.Sumw2()

Mpre          = TH1D("Mpre",           "",             100,  0,  200 )
M          = TH1D("M",           "",             100,  0,  200 )

Mpre.Sumw2()
M.Sumw2()

Respre          = TH1D("Respre",           "",             36,  400,  4000 )
Res          = TH1D("Res",           "",             36,  400,  4000 )

Respre.Sumw2()
Res.Sumw2()

###############################
# Grab root file that we want #
###############################
file_string = Load_jetNano(options.set,options.year)
print 'Loading '+file_string
file = TFile.Open(file_string)

################################
# Grab event tree from nanoAOD #
################################
inTree = file.Get("Events")
elist,jsonFiter = preSkim(inTree,None,'')
inTree = InputTree(inTree,elist)
treeEntries = inTree.entries


# Setup some pre-loop variables
trigdict = {} # Filled with the trigger names as keys and trigger bits as values

#####################################
# Design the splitting if necessary #
#####################################
if jobs != 1:
    evInJob = int(treeEntries/jobs)
    
    lowBinEdge = evInJob*(num-1)
    highBinEdge = evInJob*num

    if num == jobs:
        highBinEdge = treeEntries
else:
    lowBinEdge = 0
    highBinEdge = treeEntries

print "Range of events: (" + str(lowBinEdge) + ", " + str(highBinEdge) + ")"

count = 0

trigFails = {}

##############
# Begin Loop #
##############
start = time.time()
last_event_time = start
event_time_sum = 0
for entry in range(lowBinEdge,highBinEdge):

    count   =   count + 1
    #sys.stdout.write("%i / %i ... \r" % (count,(highBinEdge-lowBinEdge)))
    #sys.stdout.flush()
    if count % 10000 == 0 :
        print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(highBinEdge-lowBinEdge)) + '% -- '

    event = Event(inTree, entry)

    # Grab bits for event
    trigdict[pretrigName] = inTree.readBranch(pretrigName)

    for t in options.tname.split(','):
        try:
            trigdict[t] = inTree.readBranch(t)
        except:
            print 'Trigger '+t+' does not exist in '+options.set
            if t in trigFails.keys():
                trigFails[t] += 1
            else:
                trigFails[t] = 1

            trigdict[t] = 0
    
    # Have to grab Collections for each collection of interest
    # -- collections are for types of objects where there could be multiple values
    #    for a single event
    ak8JetsColl = Collection(event, jetcoll)
    subJetsColl = Collection(event, 'SubJet')

    # Now jetID which (in binary #s) is stored with bit1 as loose, bit2 as tight, and filters (after grabbing jet collections)
    try:
        for i in range(2):
            looseJetID = ak8JetsColl[i].jetId 
            if (ak8JetsColl[i].jetId & 1 == 0):    # if not loose
                if (ak8JetsColl[i].jetId & 2 == 0): # and if not tight - Need to check here because loose is always false in 2017
                    continue                      # move on
    except:
        continue

    # Now filters/flags
    # flagColl = Collection(event,'Flag')
    filters = [inTree.readBranch('Flag_goodVertices'),
                   inTree.readBranch('Flag_HBHENoiseFilter'),
                   inTree.readBranch('Flag_HBHENoiseIsoFilter'),
                   inTree.readBranch('Flag_globalTightHalo2016Filter'),
                   inTree.readBranch('Flag_EcalDeadCellTriggerPrimitiveFilter'),
                   inTree.readBranch('Flag_eeBadScFilter'),
                   inTree.readBranch('Flag_ecalBadCalibFilter')]

    filterFails = 0
    for thisFilter in filters:
        if thisFilter == 0:
            filterFails += 1
    if filterFails > 0:
        continue

    # Separate into hemispheres the leading and subleading jets
    Jetsh0,Jetsh1 = Hemispherize(ak8JetsColl)
    
    if (len(Jetsh1) < 1):
        continue

    leadingJet = ak8JetsColl[Jetsh0[0]]
    subleadingJet = ak8JetsColl[Jetsh1[0]]

    eta_cut = (Cuts['eta'][0]<abs(leadingJet.eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(subleadingJet.eta)<Cuts['eta'][1])

    if eta_cut:
        doneAlready = False

        for hemis in ['hemis0','hemis1']:
            if hemis == 'hemis0':
                # Load up the ttree values
                tVals = {
                    "tau1":leadingJet.tau1,
                    "tau2":leadingJet.tau2,
                    "tau3":leadingJet.tau3,
                    "phi":leadingJet.phi,
                    "mass":getattr(leadingJet,'mass'+mass_name),
                    "pt":leadingJet.pt,
                    "eta":leadingJet.eta,
                    "SDmass":leadingJet.msoftdrop,
                    "subJetIdx1":leadingJet.subJetIdx1,
                    "subJetIdx2":leadingJet.subJetIdx2
                }
                wVals = {
                    "tau1":subleadingJet.tau1,
                    "tau2":subleadingJet.tau2,
                    "tau3":subleadingJet.tau3,
                    "phi":subleadingJet.phi,
                    "mass":getattr(subleadingJet,'mass'+mass_name),
                    "pt":subleadingJet.pt,
                    "eta":subleadingJet.eta,
                    "SDmass":subleadingJet.msoftdrop,
                    "subJetIdx1":subleadingJet.subJetIdx1,
                    "subJetIdx2":subleadingJet.subJetIdx2
                }


            elif hemis == 'hemis1' and doneAlready == False:
                wVals = {
                    "tau1":leadingJet.tau1,
                    "tau2":leadingJet.tau2,
                    "tau3":leadingJet.tau3,
                    "phi":leadingJet.phi,
                    "mass":getattr(leadingJet,'mass'+mass_name),
                    "pt":leadingJet.pt,
                    "eta":leadingJet.eta,
                    "SDmass":leadingJet.msoftdrop,
                    "subJetIdx1":leadingJet.subJetIdx1,
                    "subJetIdx2":leadingJet.subJetIdx2
                }
                tVals = {
                    "tau1":subleadingJet.tau1,
                    "tau2":subleadingJet.tau2,
                    "tau3":subleadingJet.tau3,
                    "phi":subleadingJet.phi,
                    "mass":getattr(subleadingJet,'mass'+mass_name),
                    "pt":subleadingJet.pt,
                    "eta":subleadingJet.eta,
                    "SDmass":subleadingJet.msoftdrop,
                    "subJetIdx1":subleadingJet.subJetIdx1,
                    "subJetIdx2":subleadingJet.subJetIdx2
                }

            elif hemis == 'hemis1' and doneAlready == True:
                continue

            tjet = TLorentzVector()
            tjet.SetPtEtaPhiM(tVals["pt"],tVals["eta"],tVals["phi"],tVals["mass"])

            wjet = TLorentzVector()
            wjet.SetPtEtaPhiM(wVals["pt"],wVals["eta"],wVals["phi"],wVals["mass"])

            HT = tjet.Perp() + wjet.Perp()
            PT = tjet.Perp()

            MA = tVals['SDmass']

            resmass = (tjet+wjet).M()

            tmass_cut = Cuts['tmass'][0]<tVals['SDmass']<Cuts['tmass'][1]
            wmass_cut = Cuts['wmass'][0]<wVals['SDmass']<Cuts['wmass'][1]

            TRIGBOOL = []
            preTRIGBOOL = False

            for t in trigdict.keys():
                # If the trigger is the pre trigger, save a trigger bit other than FALSE
                if t==pretrigName:
                    preTRIGBOOL = trigdict[t]
                    
                # Add it to the list of trigger booleans
                elif t in Tstr_list:
                    TRIGBOOL.append(trigdict[t])
        

            # If there's no pre trigger, make the bool true
            if options.pretname == 'NONE':
                preTRIGBOOL = True

            # Initialize...
            TPASS = False

            # If the event passes any of the triggers, pass the event and stop checking if it passes others (break for loop)
            for TB in TRIGBOOL:
                if TB:
                    TPASS = True
                    break 


            # Fill HT histo for all events
            Htpreuntrig.Fill(HT)
            if TPASS:
                # and another for events that pass one trigger
                Htuntrig.Fill(HT)

            # If we don't pass the pre trigger, go on to the next event
            if not preTRIGBOOL:
                continue 

            # Make preselection of pt, dy, and W tag
            dy_val = abs(tjet.Rapidity()-wjet.Rapidity())
            wpt_cut = Cuts['wpt'][0]<wjet.Perp()<Cuts['wpt'][1]
            tpt_cut = Cuts['tpt'][0]<tjet.Perp()<Cuts['tpt'][1]
            dy_cut = Cuts['dy'][0]<=dy_val<Cuts['dy'][1]
            if wVals['tau1'] > 0:
                tau21val = wVals['tau2']/wVals['tau1']
            else:
                continue

            tau21_cut =  Cuts['tau21'][0]<=tau21val<Cuts['tau21'][1]

            wmass_cut = Cuts['wmass'][0]<=wVals["SDmass"]<Cuts['wmass'][1]

            preselection = wpt_cut and tpt_cut and dy_cut and wmass_cut and tau21_cut

            if preselection:
                doneAlready = True
                # Fill HT, Pt, and Mass distributions that pass pre trigger
                Htpre.Fill(HT)
                Ptpre.Fill(PT)
                Mpre.Fill(MA)
                Respre.Fill(resmass)


                # Fill HT, Pt, and Mass distributions, that pass main trigger
                if TPASS:
                    Ht.Fill(HT)
                    Pt.Fill(PT)
                    M.Fill(MA)
                    Res.Fill(resmass)

            
                # If we pass top tagging
                if tVals['tau2'] > 0:
                        tau32val = tVals['tau3']/tVals['tau2']
                else:
                    continue
                tau32_cut = Cuts['tau32medium'][0]<=tau32val<Cuts['tau32medium'][1]

                if (tVals['subJetIdx1'] < 0) or (tVals['subJetIdx1'] >= len(subJetsColl)):
                    if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)):  # if both negative, throw away event
                        continue
                    else:   # if idx2 not negative or bad index, use that
                        btagval = subJetsColl[tVals['subJetIdx2']].btagDeepB#btagCSVV2

                else:
                    if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)): # if idx1 not negative, use that
                        btagval = subJetsColl[tVals['subJetIdx1']].btagDeepB#btagCSVV2
                    # if both not negative, use largest
                    else:
                        btagval = max(subJetsColl[tVals['subJetIdx1']].btagDeepB, subJetsColl[tVals['subJetIdx2']].btagDeepB)
                    

                sjbtag_cut = Cuts['deepbtag'][0]<= btagval<Cuts['deepbtag'][1]
                    

                top_tag = sjbtag_cut and tau32_cut

                # Fill if we pass top tagging
                if top_tag and tmass_cut: 
                    Htprettags.Fill(HT)
                    if TPASS:
                        Htttags.Fill(HT)

print trigFails

f.cd()
f.Write()
f.Close()

