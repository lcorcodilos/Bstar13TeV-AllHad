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

import time, os, sys
from Lumi_swig.LumiFilter import LumiFilter
import ROOT
from ROOT import *

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim

import Bstar_Functions_local  
from Bstar_Functions_local import LoadConstants,LoadCuts,Load_jetNano,Hemispherize

from optparse import OptionParser

parser = OptionParser()

parser.add_option('-s', '--set', metavar='F', type='string', action='store',
                default   =   'data',
                dest      =   'set',
                help      =   'dataset (ie data,ttbar etc)')
parser.add_option('-y', '--y', metavar='F', type='string', action='store',
                default   =   '16',
                dest      =   'year',
                help      =   '16, 17')
parser.add_option('-j', '--job', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'job',
                help      =   'Job number')
parser.add_option('-n', '--njobs', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'njobs',
                help      =   'Number of jobs')
# parser.add_option('-t', '--tname', metavar='F', type='string', action='store',
#                 default   =   '',#'HLT_PFHT800,HLT_PFHT900,HLT_PFJet450', # For 2017 use 'HLT_PFHT1050,HLT_PFJet500'
#                 dest      =   'tname',
#                 help      =   'trigger name')
# parser.add_option('-p', '--pretname', metavar='F', type='string', action='store',
#                 default   =   'HLT_Mu50',# For 2016, can use 'HLT_PFHT475', For 2017 use 'HLT_PFHT510' or 'HLT_IsoMu27'
#                 dest      =   'pretname',
#                 help      =   'pre-trigger name')


(options, args) = parser.parse_args()
print "Options summary"
print "=================="
for  opt,value in options.__dict__.items():
    #print str(option)+ ": " + str(options[option]) 
    print str(opt) +': '+ str(value)
print "=================="
print "" 

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

lumiFilter = None
if 'data' in options.set and options.year in ['17','18']:
    lumiFilter = LumiFilter(int(options.year))

#####################
# Get trigger names #
#####################
# Trigger
if options.year == '16':
    tname = 'HLT_PFHT800ORHLT_PFHT900ORHLT_PFJet450'
    pretrig_string = 'HLT_Mu50'
    # btagtype = 'btagCSVV2'
elif options.year == '17' or options.year == '18':
    tname = 'HLT_PFHT1050ORHLT_PFJet500ORHLT_AK8PFJet380_TrimMass30ORHLT_AK8PFJet400_TrimMass30'
    pretrig_string = 'HLT_Mu50'

# tnameOR = ''
# tname = options.tname.split(',')
# Tstr_list = [options.pretname]
# pretrigName = options.pretname # defaults to NONE and nothing happens
# for iname in range(0,len(tname)):
#     tnameOR+=tname[iname]
#     if iname!=len(tname)-1:
#         tnameOR+='OR'
#     Tstr_list.append(tname[iname])

# print Tstr_list

#######################
# Setup job splitting #
#######################
njobs=int(options.njobs)
if njobs != 1:
    ijob=int(options.job)
    print "Running over " +str(njobs)+ " jobs"
    print "This will process job " +str(ijob)
else:
    print "Running over all events"


#############################
# Make new file for storage #
#############################
if njobs != 1:
    f = TFile.Open( "TWTrigger"+options.year+'_'+options.set+'_'+tname+"_pre_"+pretrig_string+"_job"+str(ijob)+"of"+str(njobs)+".root", "recreate" )
else:
    f = TFile.Open( "trigger/trigger_studies/TWTrigger"+options.year+'_'+options.set+'_'+tname+"_pre_"+pretrig_string+".root", "recreate" )

###################
# Book histograms #
###################
Ht_untrig     = TH1D("Ht_untrig",         "", 36, 400, 4000)
Ht_untrig_pre = TH1D("Ht_untrig_pre",         "", 36, 400, 4000)

Ht_W_pre      = TH1D("Ht_W_pre",      "", 36, 400, 4000)
Ht_W         = TH1D("Ht_W",         "", 36, 400, 4000)
Ht_W_pre.Sumw2()
Ht_W.Sumw2()

Ht_t_pre     = TH1D("Ht_t_pre",      "", 36, 400, 4000)
Ht_t         = TH1D("Ht_t",         "", 36, 400, 4000)
Ht_t_pre.Sumw2()
Ht_t.Sumw2()

Ht_tW_pre     = TH1D("Ht_tW_pre",      "", 36, 400, 4000)
Ht_tW         = TH1D("Ht_tW",         "", 36, 400, 4000)
Ht_tW_pre.Sumw2()
Ht_tW.Sumw2()

Ht_tt_pre     = TH1D("Ht_tt_pre",      "", 36, 400, 4000)
Ht_tt         = TH1D("Ht_tt",         "", 36, 400, 4000)
Ht_tt_pre.Sumw2()
Ht_tt.Sumw2()

# Ht_ttag_pre  = TH1D("Ht_ttag_pre",  "", 36, 400, 4000)
# Ht_ttag     = TH1D("Ht_ttag",     "", 36, 400, 4000)
# Ht_ttag_pre.Sumw2()
# Ht_ttag.Sumw2()

Pt_pre       = TH1D("Pt_pre",       "", 160, 400, 2000)
Pt          = TH1D("Pt",          "", 160, 400, 2000)
Pt_pre.Sumw2()
Pt.Sumw2()

M_pre        = TH1D("M_pre",        "", 200, 0, 400)
M           = TH1D("M",           "", 200, 0, 400)
M_pre.Sumw2()
M.Sumw2()

Res_W_pre      = TH1D("Res_W_pre",      "", 36, 400, 4000)
Res_W         = TH1D("Res_W",         "", 36, 400, 4000)
Res_W_pre.Sumw2()
Res_W.Sumw2()

Res_t_pre     = TH1D("Res_t_pre",      "", 36, 400, 4000)
Res_t         = TH1D("Res_t",         "", 36, 400, 4000)
Res_t_pre.Sumw2()
Res_t.Sumw2()

Res_tW_pre     = TH1D("Res_tW_pre",      "", 36, 400, 4000)
Res_tW         = TH1D("Res_tW",         "", 36, 400, 4000)
Res_tW_pre.Sumw2()
Res_tW.Sumw2()

Res_tt_pre     = TH1D("Res_tt_pre",      "", 36, 400, 4000)
Res_tt         = TH1D("Res_tt",         "", 36, 400, 4000)
Res_tt_pre.Sumw2()
Res_tt.Sumw2()

###############################
# Grab root file that we want #
###############################
file_string = Load_jetNano(options.set,options.year)
print 'Loading '+file_string
file = TFile.Open(file_string)

norm_weight_base = 1
lumi = Cons['qcd_lumi']
Cons = LoadConstants(options.year)
if 'data' not in options.set:
    runs_tree = file.Get("Runs")
    nevents_gen = 0
    
    for i in runs_tree:
        try:
            nevents_gen+=i.genEventCount
        except:
            nevents_gen+=i.genEventCount_
            
    xsec = Cons[options.set.replace('ext','')+'_xsec']
    norm_weight_base = lumi*xsec/float(nevents_gen)
    print ('%s*%s/%s = %s'%(lumi,xsec,nevents_gen,norm_weight_base))

################################
# Grab event tree from nanoAOD #
################################
inTree = file.Get("Events")
elist,jsonFiter = preSkim(inTree,None,'')
inTree = InputTree(inTree,elist)
treeEntries = inTree.entries

#####################################
# Design the splitting if necessary #
#####################################
if njobs != 1:
    evInJob = int(treeEntries/njobs)
    
    lowBinEdge = evInJob*(ijob-1)
    highBinEdge = evInJob*ijob

    if ijob == njobs:
        highBinEdge = treeEntries
else:
    lowBinEdge = 0
    highBinEdge = treeEntries

print "Range of events: (" + str(lowBinEdge) + ", " + str(highBinEdge) + ")"

# Setup some pre-loop variables
count = 0
trigdict = {} # Filled with the trigger names as keys and trigger bits as values
trigFails = {}

##############
# Begin Loop #
##############
start = time.time()
last_event_time = start
event_time_sum = 0
for entry in range(lowBinEdge,highBinEdge):
    count   =   count + 1
    if 'condor' not in os.getcwd():
        if count > 1:
            # current_event_time = time.time()
            # event_time_sum += (current_event_time - last_event_time)
            sys.stdout.write("%i / %i ... \r" % (count,(highBinEdge-lowBinEdge)))
            # sys.stdout.write("Avg time = %f " % (event_time_sum/count) )
            sys.stdout.flush()
            # last_event_time = current_event_time
    else:
        if count % 10000 == 0 :
            print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(highBinEdge-lowBinEdge)) + '% -- '

    # Grab the event
    event = Event(inTree, entry)

    # Grab bits for event
    trigdict[pretrig_string] = inTree.readBranch(pretrig_string)

    for t in tname.split('OR'):
        try:
            trigdict[t] = inTree.readBranch(t)
        except:
            # print 'Trigger '+t+' does not exist in '+options.set
            if t in trigFails.keys(): trigFails[t] += 1
            else: trigFails[t] = 1

            trigdict[t] = False
    
    # Have to grab Collections for each collection of interest
    # -- collections are for types of objects where there could be multiple values
    #    for a single event
    ak8JetsColl = Collection(event, jetcoll)
    subJetsColl = Collection(event, 'SubJet')

    if len(ak8JetsColl) < 2: continue

    # Now jetID which (in binary #s) is stored with bit1 as loose, bit2 as tight, and filters (after grabbing jet collections)
    for i in range(2):
        looseJetID = ak8JetsColl[i].jetId 
        if (ak8JetsColl[i].jetId & 1 == 0):    # if not loose
            if (ak8JetsColl[i].jetId & 2 == 0): # and if not tight - Need to check here because loose is always false in 2017
                continue                      # move on

    # Now filters/flags
    # Apply lumi filter
    if lumiFilter != None:
        if not lumiFilter.eval(event.run,event.luminosityBlock):
            # print ('Lumi filter on event (%s,%s)')%(event.run,event.luminosityBlock)
            continue

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
    if (len(Jetsh1) < 1) or (len(Jetsh0) < 1): continue

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
                    "mass":leadingJet.mass_nom,
                    "pt":leadingJet.pt_nom, # This will just have JER and JES corrections
                    "eta":leadingJet.eta,
                    "SDmass":leadingJet.msoftdrop_raw,
                    "subJetIdx1":leadingJet.subJetIdx1,
                    "subJetIdx2":leadingJet.subJetIdx2
                }
                wVals = {
                    "tau1":subleadingJet.tau1,
                    "tau2":subleadingJet.tau2,
                    "tau3":subleadingJet.tau3,
                    "phi":subleadingJet.phi,
                    "mass":subleadingJet.mass_nom,
                    "pt":subleadingJet.pt_nom,
                    "eta":subleadingJet.eta,
                    "SDmass":subleadingJet.msoftdrop_nom,
                    "SDmass_top":leadingJet.msoftdrop_raw,
                    "subJetIdx1":subleadingJet.subJetIdx1,
                    "subJetIdx2":subleadingJet.subJetIdx2
                }

            elif hemis == 'hemis1' and doneAlready == False:
                wVals = {
                    "tau1":leadingJet.tau1,
                    "tau2":leadingJet.tau2,
                    "tau3":leadingJet.tau3,
                    "phi":leadingJet.phi,
                    "mass":leadingJet.mass_nom,
                    "pt":leadingJet.pt_nom,
                    "eta":leadingJet.eta,
                    "SDmass":leadingJet.msoftdrop_nom,
                    "SDmass_top":leadingJet.msoftdrop_raw,
                    "subJetIdx1":leadingJet.subJetIdx1,
                    "subJetIdx2":leadingJet.subJetIdx2
                }
                tVals = {
                    "tau1":subleadingJet.tau1,
                    "tau2":subleadingJet.tau2,
                    "tau3":subleadingJet.tau3,
                    "phi":subleadingJet.phi,
                    "mass":subleadingJet.mass_nom,
                    "pt":subleadingJet.pt_nom,
                    "eta":subleadingJet.eta,
                    "SDmass":subleadingJet.msoftdrop_raw,
                    "subJetIdx1":subleadingJet.subJetIdx1,
                    "subJetIdx2":subleadingJet.subJetIdx2
                }

            elif hemis == 'hemis1' and doneAlready == True:
                continue

            tjet = TLorentzVector()
            tjet.SetPtEtaPhiM(tVals["pt"],tVals["eta"],tVals["phi"],tVals["SDmass"])

            wjet = TLorentzVector()
            wjet.SetPtEtaPhiM(wVals["pt"],wVals["eta"],wVals["phi"],wVals["SDmass"])

            ht = tjet.Perp() + wjet.Perp()
            MtopW = (tjet+wjet).M()
            top_pt = tjet.Perp()
            top_mass = tjet.M()

            trig_bools = []
            pretrig_bool = False

            for t in trigdict.keys():
                # If the trigger is the pre trigger, save a trigger bit other than FALSE
                if t == pretrig_string: pretrig_bool = trigdict[t]
                # Add it to the list of trigger booleans
                elif t in tname.split('OR'): trig_bools.append(trigdict[t])

            # If there's no pre trigger, make the bool true
            # if options.pretname == 'NONE':
            #     preTRIGBOOL = True

            # Initialize...
            trig_pass = False

            # If the event passes any of the triggers, pass the event and stop checking if it passes others (break for loop)
            if True in trig_bools: trig_pass = True

            # Fill HT histo for all events
            Ht_untrig_pre.Fill(ht)
            if trig_pass: Ht_untrig.Fill(ht)                

            # If we don't pass the pre trigger, go on to the next event
            if not pretrig_bool: continue 

            # Make kinematic preselection
            MtopW_cut = MtopW > 1000.
            # ht_cut = ht > 1000.
            Mtop_cut = top_mass > 50.0
            dy_val = abs(tjet.Rapidity()-wjet.Rapidity())
            wpt_cut = Cuts['wpt'][0]<wjet.Perp()<Cuts['wpt'][1]
            tpt_cut = Cuts['tpt'][0]<tjet.Perp()<Cuts['tpt'][1]
            dy_cut = Cuts['dy'][0]<=dy_val<Cuts['dy'][1]

            # Preselection W
            presel_wmass_cut = Cuts['wmass'][0]<wVals['SDmass']<Cuts['wmass'][1]
            if wVals['tau1'] > 0: tau21val = wVals['tau2']/wVals['tau1']
            else: continue
            presel_tau21_cut =  Cuts['tau21'][0]<=tau21val<Cuts['tau21'][1]

            # Preselection Top
            presel_tmass_cut = Cuts['tmass'][0]<wVals['SDmass']<Cuts['tmass'][1]
            if wVals['tau2'] > 0: tau32val = wVals['tau3']/wVals['tau2']
            else: continue
            presel_tau32_cut =  Cuts['tau32tight'][0]<=tau32val<Cuts['tau32tight'][1]

            if (wVals['subJetIdx1'] < 0) or (wVals['subJetIdx1'] >= len(subJetsColl)):
                if (wVals['subJetIdx2'] < 0) or (wVals['subJetIdx2'] >= len(subJetsColl)): continue # if both negative, throw away event
                else: presel_btagval = subJetsColl[wVals['subJetIdx2']].btagDeepB  # if idx2 not negative or bad index, use that
            else:
                if (wVals['subJetIdx2'] < 0) or (wVals['subJetIdx2'] >= len(subJetsColl)): presel_btagval = subJetsColl[wVals['subJetIdx1']].btagDeepB# if idx1 not negative, use that
                # if both not negative, use largest
                else: presel_btagval = max(subJetsColl[wVals['subJetIdx1']].btagDeepB, subJetsColl[wVals['subJetIdx2']].btagDeepB)
            presel_sjbtag_cut = Cuts['deepbtag'][0]<= presel_btagval<Cuts['deepbtag'][1]

            # Alphabet Top
            if tVals['tau2'] > 0: tau32val = tVals['tau3']/tVals['tau2']
            else: continue
            alpha_tau32_cut = Cuts['tau32medium'][0]<=tau32val<Cuts['tau32medium'][1]

            if (tVals['subJetIdx1'] < 0) or (tVals['subJetIdx1'] >= len(subJetsColl)):
                if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)): continue # if both negative, throw away event
                else: alpha_btagval = subJetsColl[tVals['subJetIdx2']].btagDeepB  # if idx2 not negative or bad index, use that
            else:
                if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)): alpha_btagval = subJetsColl[tVals['subJetIdx1']].btagDeepB# if idx1 not negative, use that
                # if both not negative, use largest
                else: alpha_btagval = max(subJetsColl[tVals['subJetIdx1']].btagDeepB, subJetsColl[tVals['subJetIdx2']].btagDeepB)
            alpha_sjbtag_cut = Cuts['deepbtag'][0]<= alpha_btagval<Cuts['deepbtag'][1]
            

            preselection = MtopW_cut and Mtop_cut and wpt_cut and tpt_cut and dy_cut
            if preselection:
                if presel_wmass_cut and presel_tau21_cut:
                    doneAlready = True
                    # Fill HT, Pt, and Mass distributions that pass pre trigger
                    Ht_W_pre.Fill(ht)
                    Pt_pre.Fill(top_pt)
                    M_pre.Fill(top_mass)
                    Res_W_pre.Fill(MtopW)

                    # Fill HT, Pt, and Mass distributions, that pass main trigger
                    if trig_pass:
                        Ht_W.Fill(ht)
                        Pt.Fill(top_pt)
                        M.Fill(top_mass)
                        Res_W.Fill(MtopW)

                    # Fill if we pass top tagging
                    if alpha_sjbtag_cut and alpha_tau32_cut: 
                        Res_tW_pre.Fill(MtopW)
                        Ht_tW_pre.Fill(ht)
                        if trig_pass:
                            Res_tW.Fill(MtopW)
                            Ht_tW.Fill(ht)

                elif presel_tmass_cut and presel_tau32_cut and presel_sjbtag_cut:
                    doneAlready = True
                    # Fill HT, Pt, and Mass distributions that pass pre trigger
                    Res_t_pre.Fill(MtopW)
                    Ht_t_pre.Fill(ht)

                    # Fill HT, Pt, and Mass distributions, that pass main trigger
                    if trig_pass:
                        Res_t.Fill(MtopW)
                        Ht_t.Fill(ht)

                    # Fill if we pass top tagging
                    if alpha_sjbtag_cut and alpha_tau32_cut: 
                        Res_tt_pre.Fill(MtopW)
                        Ht_tt_pre.Fill(ht)
                        if trig_pass:
                            Res_tt.Fill(MtopW)
                            Ht_tt.Fill(ht)

for h in [Ht_W_pre, Ht_W, Ht_t_pre, Ht_t,
          Ht_tW_pre, Ht_tW, Ht_tt_pre, Ht_tt,
          Pt_pre, Pt, M_pre, M, Res_W_pre, 
          Res_W, Res_t_pre, Res_t, Res_tW_pre, 
          Res_tW, Res_tt_pre, Res_tt]:
    h.Scale()

print trigFails

f.cd()
f.Write()
f.Close()

