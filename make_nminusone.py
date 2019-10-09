# make_nminusone.py

#################################################################
# make_preselection.py - Written by Lucas Corcodilos, 7/13/18   #
# -----------------------------------------------------------   #
# Reads the jetNano trees on EOS, builds the 2D distributions   #
# for 2D Alphabet, and creates and stores an even smaller TTree #
# that can be used later to analyze variable distributions with #
# the 2D Alphabet Rp/f applied.                                 #
#################################################################

import ROOT
from ROOT import *

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.JetSysColl import JetSysColl, JetSysObj
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim


# import FatJetNNHelper
# from FatJetNNHelper import *

import pickle
from optparse import OptionParser
import copy
import math
from math import sqrt
import sys
import time

import Bstar_Functions_local
from Bstar_Functions_local import *


if __name__ == "__main__":
    
    parser = OptionParser()

    parser.add_option('-s', '--set', metavar='F', type='string', action='store',
                    default   =   'data',
                    dest      =   'set',
                    help      =   'dataset (ie data,ttbar etc)')
    parser.add_option('-r', '--region', metavar='F', type='string', action='store',
                    default   =   'default',
                    dest      =   'region',
                    help      =   'default, sideband, ttbar')
    parser.add_option('-t', '--tau32', metavar='F', type='string', action='store',
                    default   =   'medium',
                    dest      =   'tau32',
                    help      =   'Cut strength (off, loose, medium, tight')
    parser.add_option('-y', '--year', metavar='FILE', type='string', action='store',
                default   =   '16',
                dest      =   'year',
                help      =   'Year (16,17,18)')
    parser.add_option('-j', '--job', metavar='FILE', type='string', action='store',
                    default   =   '',
                    dest      =   'job',
                    help      =   'Job number')
    parser.add_option('-n', '--njobs', metavar='FILE', type='string', action='store',
                    default   =   '',
                    dest      =   'njobs',
                    help      =   'Number of jobs')

    (options, args) = parser.parse_args()

    # Prep for deepcsv b-tag if deepak8 is off
    # From https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration
    # gSystem.Load('libCondFormatsBTauObjects') 
    # gSystem.Load('libCondToolsBTau') 
    # if options.year == '16':
    #     calib = BTagCalibration('DeepCSV', 'SFs/DeepCSV_2016LegacySF_V1.csv')
    # elif options.year == '17':
    #     calib = BTagCalibration('DeepCSV', 'SFs/subjet_DeepCSV_94XSF_V4_B_F.csv')
    # elif options.year == '18':
    #     calib = BTagCalibration('DeepCSV', 'SFs/DeepCSV_102XSF_V1.csv')
        
    # v_sys = getattr(ROOT, 'vector<string>')()
    # v_sys.push_back('up')
    # v_sys.push_back('down')

    # reader = BTagCalibrationReader(
    #     0,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
    #     "central",      # central systematic type
    #     v_sys,          # vector of other sys. types
    # )   

    # reader.load(
    #     calib, 
    #     0,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
    #     "incl"      # measurement type
    # ) 

    # if options.region == 'ttbar':
    #     wIsTtagged = True
    #     print 'W side will be top tagged'
    # else:
    #     wIsTtagged = False

    ######################################
    # Make strings for final file naming #
    ######################################

    # Trigger
    if options.year == '16':
        tname = 'HLT_PFHT800ORHLT_PFHT900ORHLT_PFJet450'
        pretrig_string = 'HLT_Mu50'
        # btagtype = 'btagCSVV2'
    elif options.year == '17' or options.year == '18':
        tname = 'HLT_PFHT1050ORHLT_PFJet500'
        pretrig_string = 'HLT_Mu50'
    btagtype = 'btagDeepB'


    jetcoll = "FatJet"
    print 'Jet collection is '+jetcoll

    ttagstring = 'tau32'+options.tau32

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

    #################################
    # Load cut values and constants #
    #################################
    Cons = LoadConstants(options.year)
    lumi = Cons['lumi']

    Cuts = LoadCuts(options.region,options.year)

    tempyear = options.year
    if options.year == '18':
        tempyear = '17'

    ##########################################################
    # Load Trigger, Pileup reweight, and ttag sf if not data #
    ##########################################################
    if options.set != 'data':
        print "Triggerweight_data"+options.year+"_pre_"+pretrig_string+".root"
        print 'TriggerWeight_'+tname+'_Res'
        TrigFile = TFile.Open("trigger/Triggerweight_data"+options.year+"_pre_"+pretrig_string+".root")
        TrigPlot = TrigFile.Get('TriggerWeight_'+tname+'_Res')
        TrigPlot1 = TrigPlot.Clone()
        
        # PileFile = TFile.Open("pileup/PileUp_Ratio_ttbar"+options.year+".root")
        # PilePlots = {
        #     "nom": PileFile.Get("Pileup_Ratio"),
        #     "up": PileFile.Get("Pileup_Ratio_up"),
        #     "down": PileFile.Get("Pileup_Ratio_down")}
        
        ttagsffile = TFile.Open('SFs/20'+tempyear+'TopTaggingScaleFactors_NoMassCut.root')


    #############################
    # Make new file for storage #
    #############################
    if njobs!=1:
        f = TFile( "TWvariables"+options.year+"_"+options.set+"_job"+str(ijob)+"of"+str(njobs)+"_"+ttagstring+'_'+options.region+".root", "recreate" )
    else:
        f = TFile( "TWvariables"+options.year+"_"+options.set+"_"+ttagstring+'_'+options.region+".root", "recreate" )
    f.cd()

    
    ###################
    # Book histograms #
    ###################
    # Pt
    PtTop = TH1F("PtTop",         "Top jet pt (GeV) after full selection",             46, 350, 1500 )
    PtW = TH1F("PtW",         "W jet pt (GeV) after full selection",             46, 350, 1500 )
    MtwvsdeltaY = TH2F("MtwvsdeltaY",         "M_{tW} (GeV) vs Delta Y between leading jets",   60, 0, 6.0, 30, 1000,4000)
    PtTopW      = TH1F("PtTopW",        "Pt of system after full selection",                35,   0, 700 )
    PtTopWScalar      = TH1F("PtTopWScalar",        "Scalar sum of pt of system after full selection",                80,   0, 2000 )
    PtTop.Sumw2()
    PtW.Sumw2()
    MtwvsdeltaY.Sumw2()
    PtTopW.Sumw2()
    PtTopWScalar.Sumw2()

    # Eta
    EtaTop      = TH1F("EtaTop",        "Top jet eta after full selection",                  12, -2.5, 2.5 )
    EtaW   = TH1F("EtaW",     "W jet eta after full selection",              12, -2.5, 2.5 )
    dEta   = TH1F("dEta",     "|\Delta \eta| between two leading jets after full selection",              12, 0, 2.5 )
    EtaTop.Sumw2()
    EtaW.Sumw2()
    dEta.Sumw2()

    # Phi
    PhiTop    = TH1F("PhiTop",      "Top jet Phi (rad) after full selection",                       12, -math.pi, math.pi )
    PhiW      = TH1F("PhiW",    "W jet Phi (rad) after full selection",                       12, -math.pi, math.pi )
    dPhi      = TH1F("dPhi",        "|\Delta \phi| between two leading jets after full selection",          12, 1.57, math.pi )
    PhiTop.Sumw2()
    PhiW.Sumw2()
    dPhi.Sumw2()

    # Mass
    MSDtop = TH1F("MSDtop",      "Top Candidate Soft Drop Mass (GeV)",                       30, 50, 350 )
    MSDw = TH1F("MSDw",      "W Candidate Soft Drop Mass (GeV)",                       27, 30, 300 )
    MSDtop.Sumw2()
    MSDw.Sumw2()

    # Tagging vars
    Tau21       = TH1F('Tau21',     'N-subjetiness W',    20,0,1.0)
    Tau32       = TH1F('Tau32',     'N-subjetiness Top',    20,0,1.0)
    SJbtag      = TH1F('SJbtag',    'Subjet b-tag (DeepCSV)', 20,0,1.0)
    Tau21.Sumw2()
    Tau32.Sumw2()
    SJbtag.Sumw2()

    nminusones = ['dy','sjbtag','tau32','tau21','wmass','none']

    ###############################
    # Grab root file that we want #
    ###############################
    file_string = Load_jetNano(options.set,options.year)
    file = TFile.Open(file_string)


    ################################
    # Grab event tree from nanoAOD #
    ################################
    inTree = file.Get("Events")
    elist,jsonFiter = preSkim(inTree,None,'')
    inTree = InputTree(inTree,elist)
    treeEntries = inTree.entries

    #############################
    # Get process normalization #
    #############################
    norm_weight = 1
    if options.set != 'data':
        runs_tree = file.Get("Runs")
        nevents_gen = 0
        
        for i in runs_tree:
            nevents_gen+=i.genEventCount

        xsec = Cons[options.set.replace('ext','')+'_xsec']
        norm_weight = lumi*xsec/float(nevents_gen)

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

    count = 0

    ##############
    # Begin Loop #
    ##############
    start = time.time()
    last_event_time = start
    event_time_sum = 0
    for entry in range(lowBinEdge,highBinEdge):
        count   =   count + 1

        if count % 10000 == 0 :
            print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(highBinEdge-lowBinEdge)) + '% -- '

        # Grab the event
        event = Event(inTree, entry)

        #####################################
        # Basic stuff applied to everything #
        #####################################

        # Apply triggers first
        if 'data' in options.set:
            passt = False
            for t in tname.split('OR'):
                try: 
                    if inTree.readBranch(t):
                        passt = True
                except:
                    continue

            if not passt:
                continue

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
        filters = [inTree.readBranch('Flag_goodVertices'),
                   inTree.readBranch('Flag_HBHENoiseFilter'),
                   inTree.readBranch('Flag_HBHENoiseIsoFilter'),
                   inTree.readBranch('Flag_globalTightHalo2016Filter'),
                   inTree.readBranch('Flag_EcalDeadCellTriggerPrimitiveFilter'),
                   inTree.readBranch('Flag_eeBadScFilter')]

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

        # First do N-1 of non-tagging variables (pt, eta, phi, rapidity)
        # Require they pass a W and top tag and then proceed

        doneAlready = False

        for hemis in ['hemis0','hemis1']:
            if hemis == 'hemis0':
                # Load up the ttree values
                checkingFirstHemi = True
                tVals = {
                    "tau2":leadingJet.tau2,
                    "tau3":leadingJet.tau3,
                    "phi":leadingJet.phi,
                    "pt":leadingJet.pt_nom,
                    "eta":leadingJet.eta,
                    "SDmass":leadingJet.msoftdrop_raw,
                    "subJetIdx1":leadingJet.subJetIdx1,
                    "subJetIdx2":leadingJet.subJetIdx2
                }
                wVals = {
                    "tau1":subleadingJet.tau1,
                    "tau2":subleadingJet.tau2,
                    "phi":subleadingJet.phi,
                    "pt":subleadingJet.pt_nom,
                    "eta":subleadingJet.eta,
                    "SDmass":subleadingJet.msoftdrop_nom,
                    "subJetIdx1":subleadingJet.subJetIdx1,
                    "subJetIdx2":subleadingJet.subJetIdx2
                }


            elif hemis == 'hemis1' and doneAlready == False:
                checkingFirstHemi = False
                wVals = {
                    "tau1":leadingJet.tau1,
                    "tau2":leadingJet.tau2,
                    "phi":leadingJet.phi,
                    "pt":leadingJet.pt_nom,
                    "eta":leadingJet.eta,
                    "SDmass":leadingJet.msoftdrop_nom,
                    "subJetIdx1":leadingJet.subJetIdx1,
                    "subJetIdx2":leadingJet.subJetIdx2
                }
                tVals = {
                    "tau2":subleadingJet.tau2,
                    "tau3":subleadingJet.tau3,
                    "phi":subleadingJet.phi,
                    "pt":subleadingJet.pt_nom,
                    "eta":subleadingJet.eta,
                    "SDmass":subleadingJet.msoftdrop_raw,
                    "subJetIdx1":subleadingJet.subJetIdx1,
                    "subJetIdx2":subleadingJet.subJetIdx2
                }

            elif hemis == 'hemis1' and doneAlready == True:
                continue

            # Standard W tag
            if wVals['tau1'] > 0: tau21val = wVals['tau2']/wVals['tau1']
            else: continue
            if tVals['tau2'] > 0: tau32val = tVals['tau3']/tVals['tau2']
            else: continue

       
            # Make the lorentz vectors
            tjet = TLorentzVector()
            tjet.SetPtEtaPhiM(tVals["pt"],tVals["eta"],tVals["phi"],tVals["SDmass"])

            wjet = TLorentzVector()
            wjet.SetPtEtaPhiM(wVals["pt"],wVals["eta"],wVals["phi"],wVals["SDmass"])

            ht = tjet.Perp() + wjet.Perp()
            MtopW = (tjet+wjet).M()

            # Get GenParticles for use below
            if 'data' not in options.set:
                GenParticles = Collection(event,'GenPart')

            ###############################
            # Weighting and Uncertainties #
            ###############################

            # Initialize event weight
            weights = { 'Pileup':{},
                        'Topsf':{},
                        'Wsf':{},
                        'Trigger':{},
                        'Ptreweight':{}
                        }

            
            if 'data' not in options.set:
                # Pileup reweighting applied
                weights['Pileup']['nom'] = inTree.readBranch('puWeight')

                # Top tagging tau32+sjbtag scale factor 
                if "QCD" not in options.set:
                    sft,top_merging_status = SFT_Lookup(tjet,ttagsffile,GenParticles,options.tau32,count)#(tjet, ttagsffile, GenParticles, options.tau32)#_MERGEDONLY(tjet, ttagsffile)#, GenParticles)
                    weights['Topsf']['nom'] = sft[0]

                # Determine purity for scale factor
                if options.region == 'default':    Wpurity = 'HP'
                elif options.region == 'sideband':
                    if options.year == '16':       Wpurity = 'LP'
                    elif options.year != '16' and (Cuts['tau21LP'][0] < tau21val < Cuts['tau21LP'][1]): Wpurity = 'LP'
                    else:                          Wpurity = False
                else:                              Wpurity = False

                # W matching
                WJetMatchingRequirement = 0
                if ('tW' in options.set or 'signal' in options.set):
                    if WJetMatching(wjet,GenParticles) and Wpurity != False:
                        wtagsf = Cons['wtagsf_'+Wpurity]
                        weights['Wsf']['nom'] = wtagsf
                    else: weights['Wsf']['nom'] = 1.0
                else: weights['Wsf']['nom'] = 1.0

                # # Get the extrapolation uncertainty
                # extrap = ExtrapUncert_Lookup(wjet.Perp(),Wpurity,options.year)
                # weights['Extrap']['up'] = 1+extrap
                # weights['Extrap']['down'] = 1-extrap

                # Trigger weight applied
                if tname != 'none' and 'data' not in options.set:
                    weights['Trigger']['nom'] = Trigger_Lookup( ht , TrigPlot1 )[0]

                # Top pt reweighting
                if 'ttbar' in options.set:
                    weights['Ptreweight']['nom'] = PTW_Lookup(GenParticles)


            ####################################
            # Split into top tag pass and fail #
            ####################################
            if (tVals['subJetIdx1'] < 0) or (tVals['subJetIdx1'] >= len(subJetsColl)):
                # if both negative, throw away event
                if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)): continue
                # if idx2 not negative or bad index, use that
                else: btagval = getattr(subJetsColl[tVals['subJetIdx2']],btagtype)

            else:
                # if idx1 not negative, use that
                if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)): btagval = getattr(subJetsColl[tVals['subJetIdx1']],btagtype)
                # if both not negative, use largest
                else: btagval = max(getattr(subJetsColl[tVals['subJetIdx1']],btagtype), getattr(subJetsColl[tVals['subJetIdx2']],btagtype))
                
            

            # Make and get all cuts
            dy_val = abs(tjet.Rapidity()-wjet.Rapidity())
            eta_cut = (Cuts['eta'][0]<abs(leadingJet.eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(subleadingJet.eta)<Cuts['eta'][1])
            wpt_cut = Cuts['wpt'][0]<wjet.Perp()<Cuts['wpt'][1]
            tpt_cut = Cuts['tpt'][0]<tjet.Perp()<Cuts['tpt'][1]
            dy_cut = Cuts['dy'][0]<=dy_val<Cuts['dy'][1]
            tau21_cut =  Cuts['tau21'][0]<=tau21val<Cuts['tau21'][1]
            wmass_cut = Cuts['wmass'][0]<=wVals["SDmass"]<Cuts['wmass'][1]
            sjbtag_cut = Cuts['deepbtag'][0]<= btagval<Cuts['deepbtag'][1]
            tau32_cut = Cuts['tau32'+options.tau32][0]<=tau32val<Cuts['tau32'+options.tau32][1]

            if eta_cut and wpt_cut and tpt_cut: doneAlready = True

            for nminus in nminusones:

                if nminus == 'dy':      preselection = eta_cut and wpt_cut and tpt_cut and tau21_cut and wmass_cut
                elif nminus == 'tau21': preselection = eta_cut and wpt_cut and tpt_cut and dy_cut and wmass_cut
                elif nminus == 'wmass': preselection = eta_cut and wpt_cut and tpt_cut and dy_cut and tau21_cut
                else:                   preselection = eta_cut and wpt_cut and tpt_cut and dy_cut and tau21_cut and wmass_cut

                if preselection: 
                    if nminus == 'tau32':       top_tag = sjbtag_cut
                    elif nminus == 'sjbtag':    top_tag = tau32_cut
                    else:                       top_tag = sjbtag_cut and tau32_cut

                    # Fill histograms
                    if top_tag:
                        if nminus == 'tau32':
                            Tau32.Fill(tau32val,norm_weight*Weightify(weights,'nominal')) 
                        elif nminus == 'tau21':
                            Tau21.Fill(tau21val,norm_weight*Weightify(weights,'nominal')) 
                        elif nminus == 'wmass':
                            MSDw.Fill(wjet.M(),norm_weight*Weightify(weights,'nominal')) 
                        elif nminus == 'dy':
                            MtwvsdeltaY.Fill(dy_val,MtopW,norm_weight*Weightify(weights,'nominal')) 
                            dEta.Fill(abs(tjet.Eta()-wjet.Eta()),norm_weight*Weightify(weights,'nominal'))
                        elif nminus == 'sjbtag':
                            SJbtag.Fill(btagval,norm_weight*Weightify(weights,'nominal')) 
                        elif nminus == 'none':
                            PtTop.Fill(tjet.Perp(),norm_weight*Weightify(weights,'nominal'))
                            PtW.Fill(wjet.Perp(),norm_weight*Weightify(weights,'nominal'))
                            PtTopW.Fill((wjet+tjet).Perp(),norm_weight*Weightify(weights,'nominal'))
                            PtTopWScalar.Fill(wjet.Perp()+tjet.Perp(),norm_weight*Weightify(weights,'nominal'))
                            EtaTop.Fill(tjet.Eta(),norm_weight*Weightify(weights,'nominal'))
                            EtaW.Fill(wjet.Eta(),norm_weight*Weightify(weights,'nominal'))
                            PhiTop.Fill(tjet.Phi(),norm_weight*Weightify(weights,'nominal'))
                            PhiW.Fill(wjet.Phi(),norm_weight*Weightify(weights,'nominal'))
                            dPhi.Fill(abs(tjet.DeltaPhi(wjet)),norm_weight*Weightify(weights,'nominal'))
                            MSDtop.Fill(tjet.M(),norm_weight*Weightify(weights,'nominal'))

                    
                  
    end = time.time()
    print '\n'
    print str((end-start)/60.) + ' min'
    f.cd()
    f.Write()
    f.Close()



    
