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
import sys, array, os
import time
import pprint
pp = pprint.PrettyPrinter(indent = 2)

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
                    default   =   '',
                    dest      =   'year',
                    help      =   'Year (16,17,18)')
    parser.add_option('-x', '--pileup', metavar='F', type='string', action='store',
                    default   =   'on',
                    dest      =   'pileup',
                    help      =   'If not data do pileup reweighting?')
    parser.add_option('-J', '--JES', metavar='F', type='string', action='store',
                    default   =   'nom',
                    dest      =   'JES',
                    help      =   'nom, up, or down')
    parser.add_option('-R', '--JER', metavar='F', type='string', action='store',
                    default   =   'nom',
                    dest      =   'JER',
                    help      =   'nom, up, or down')
    parser.add_option('-a', '--JMS', metavar='F', type='string', action='store',
                    default   =   'nom',
                    dest      =   'JMS',
                    help      =   'nom, up, or down')
    parser.add_option('-b', '--JMR', metavar='F', type='string', action='store',
                    default   =   'nom',
                    dest      =   'JMR',
                    help      =   'nom, up, or down')
    parser.add_option('-u', '--ptreweight', metavar='F', type='string', action='store',
                    default   =   'on',
                    dest      =   'ptreweight',
                    help      =   'on or off')
    parser.add_option('-j', '--job', metavar='FILE', type='string', action='store',
                    default   =   '',
                    dest      =   'job',
                    help      =   'Job number')
    parser.add_option('-n', '--njobs', metavar='FILE', type='string', action='store',
                    default   =   '',
                    dest      =   'njobs',
                    help      =   'Number of jobs')
    parser.add_option('-q', '--qcdweight', action='store_true',
                    default   =   False,
                    dest      =   'qcdweight',
                    help      =   'Use QCD weighting')


    (options, args) = parser.parse_args()

    # Prep for deepcsv b-tag
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

    if options.region == 'ttbar':
        wIsTtagged = True
        print 'W side will be top tagged'
    else:
        wIsTtagged = False

    qcdweight_string = ''
    if options.qcdweight:
        print 'Will use QCD weighting for this run'
        qcdweight_string='QCDweighting'

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

    # if tname == 'HLT_PFHT900ORHLT_PFHT800ORHLT_AK8PFJet450':
    #     tnamestr = 'nominal'
    # else:
    #     tnamestr = tname

    # JECs
    runOthers = True
    mod = ''
    if options.JES!='nom':
        mod = '_JES' + '_' + options.JES
        # JMC_name = '_jesTotal'+options.JES.capitalize()
        # JEC_name = '_jesTotal'+options.JES.capitalize()
        runOthers = False
    if options.JER!='nom':
        mod = '_JER' + '_' + options.JER
        # JMC_name = '_nom'
        # JEC_name = '_jer'+options.JER.capitalize()
        runOthers = False
    if options.JMS!='nom':
        mod = '_JMS' + '_' + options.JMS
        # JMC_name = '_jms'+options.JMS.capitalize()
        # JEC_name = '_nom'
        runOthers = False
    if options.JMR!='nom':
        mod = '_JMR' + '_' + options.JMR
        # JMC_name = '_jmr'+options.JMR.capitalize()
        # JEC_name = '_nom'
        runOthers = False

    # if options.year == '16':
    #     jetcoll = "FatJet"#"CustomAK8Puppi"
    # elif options.year == '17':
    jetcoll = "FatJet"

    print 'Jet collection is '+jetcoll

    if options.tau32 == 'off':
        print 'ERROR: tau32 is set to off. Please turn on. Quitting...'
        quit()
    elif options.tau32 != 'off':
        ttagstring = 'tau32'+options.tau32+qcdweight_string

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
    if not options.qcdweight:
        lumi = Cons['lumi']
    else:
        lumi = Cons['qcd_lumi']

    Cuts = LoadCuts(options.region,options.year)

    tempyear = options.year
    if options.year == '18':
        tempyear = '17'

    #########################################################################
    # Load Trigger, Pileup reweight, Puppi+SD corr, and ttag sf if not data #
    #########################################################################
    if 'data' not in options.set:
        if options.region != 'ttbar': trigfile_str = "Triggerweight"+options.year+"_data_W_pre_"+pretrig_string+".root"
        else: trigfile_str = "Triggerweight"+options.year+"_data_t_pre_"+pretrig_string+".root"
        trighist_str = 'TriggerWeight_'+tname+'_Res'
        print trigfile_str
        print trighist_str
        TrigFile = TFile.Open("trigger/trigger_studies/"+trigfile_str)
        TrigPlot = TrigFile.Get(trighist_str)
        TrigPlot1 = TrigPlot.Clone()
        
        ttagsffile = TFile.Open('SFs/20'+tempyear+'TopTaggingScaleFactors_NoMassCut.root')

    # lepSFfile = TFile.Open('SFs/bstar_lep_veto_sfs.root')


    #############################
    # Make new file for storage #
    #############################
    if njobs!=1:
        f = TFile( "TWpreselection"+options.year+"_"+options.set+"_job"+str(ijob)+"of"+str(njobs)+"_"+ttagstring+mod+'_'+options.region+".root", "recreate" )
    else:
        f = TFile( "TWpreselection"+options.year+"_"+options.set+"_"+ttagstring+mod+'_'+options.region+".root", "recreate" )
    f.cd()

    
    ###################
    # Book histograms #
    ###################
    MtwvMtPass     = TH2F("MtwvMtPass",     "mass of tw vs mass of top - Pass", 60, 50, 350, 35, 500, 4000 )
    MtwvMtFail     = TH2F("MtwvMtFail",     "mass of tw vs mass of top - Fail", 60, 50, 350, 35, 500, 4000 )
    MtwvMtFailSub  = TH2F("MtwvMtFailSub",     "mass of tw vs mass of top - FailSub", 60, 50, 350, 35, 500, 4000 )
    MtwvMtPass.Sumw2()
    MtwvMtFail.Sumw2()
    MtwvMtFailSub.Sumw2()

    nev = TH1F("nev",   "nev",      1, 0, 1 )

    lepVetoCount = TH1F('lepVetoCount','Lepton veto count',2,0,2)
    lepVetoCount.GetXaxis().SetBinLabel(1,'In Semi-lep channels')
    lepVetoCount.GetXaxis().SetBinLabel(2,'Not in Semi-lep channels')

    wmatchCount = TH1F('wmatchCount','W match count',1,0,1)
    wmatchCount.GetXaxis().SetBinLabel(1,'Number of times the W matching passed')

    if runOthers == True:
        if 'data' not in options.set:
            MtwvMtPassPDFup   = TH2F("MtwvMtPassPDFup", "mass of tw vs mass of top PDF up - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassPDFdown = TH2F("MtwvMtPassPDFdown",   "mass of tw vs mass of top PDF down - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassPDFup.Sumw2()
            MtwvMtPassPDFdown.Sumw2()

            MtwvMtPassPUup   = TH2F("MtwvMtPassPUup", "mass of tw vs mass of top PU up - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassPUdown = TH2F("MtwvMtPassPUdown",   "mass of tw vs mass of top PU down - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassPUup.Sumw2()
            MtwvMtPassPUdown.Sumw2()

            MtwvMtPassTopup   = TH2F("MtwvMtPassTopup", "mass of tw vs mass of top sf up - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassTopdown = TH2F("MtwvMtPassTopdown",   "mass of tw vs mass of top sf down - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassTopup.Sumw2()
            MtwvMtPassTopdown.Sumw2()

            MtwvMtPassScaleup   = TH2F("MtwvMtPassScaleup", "mass of tw vs mass of Q^2 scale up - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassScaledown = TH2F("MtwvMtPassScaledown",   "mass of tw vs mass of Q^2 scale down - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassScaleup.Sumw2()
            MtwvMtPassScaledown.Sumw2()

            MtwvMtPassSjbtagup   = TH2F("MtwvMtPassSjbtagup", "mass of tw vs mass of sjbtag sf up - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassSjbtagdown = TH2F("MtwvMtPassSjbtagdown",   "mass of tw vs mass of sjbtag sf down - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassSjbtagup.Sumw2()
            MtwvMtPassSjbtagdown.Sumw2()

            MtwvMtPassTrigup   = TH2F("MtwvMtPassTrigup", "mass of tw vs mass of top trig up - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassTrigdown = TH2F("MtwvMtPassTrigdown",   "mass of tw vs mass of top trig down - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassTrigup.Sumw2()
            MtwvMtPassTrigdown.Sumw2()

            if 'ttbar' in options.set:
                MtwvMtPassTptup    = TH2F("MtwvMtPassTptup",  "mass of tw vs mass of top top pt reweight up - Pass",  60, 50, 350, 35, 500, 4000 )
                MtwvMtPassTptdown  = TH2F("MtwvMtPassTptdown",    "mass of tw vs mass of top top pt reweight down - Pass",60, 50, 350, 35, 500, 4000 )
                MtwvMtPassTptup.Sumw2()
                MtwvMtPassTptdown.Sumw2()

            if ('tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                MtwvMtPassWup      = TH2F("MtwvMtPassWup",    "mass of tw vs mass of top w tag SF up - Pass", 60, 50, 350, 35, 500, 4000 )
                MtwvMtPassWdown    = TH2F("MtwvMtPassWdown",  "mass of tw vs mass of top w tag SF down - Pass",   60, 50, 350, 35, 500, 4000 )
                MtwvMtPassWup.Sumw2()
                MtwvMtPassWdown.Sumw2()

                MtwvMtPassExtrapUp = TH2F("MtwvMtPassExtrapUp", "mass of tw vs mass of top extrapolation uncertainty up - Pass", 60, 50, 350, 35, 500, 4000)
                MtwvMtPassExtrapDown = TH2F("MtwvMtPassExtrapDown", "mass of tw vs mass of top extrapolation uncertainty down - Pass", 60, 50, 350, 35, 500, 4000)
                MtwvMtPassExtrapUp.Sumw2()
                MtwvMtPassExtrapDown.Sumw2()

            # Fail
            MtwvMtFailPDFup   = TH2F("MtwvMtFailPDFup", "mass of tw vs mass of top PDF up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailPDFdown = TH2F("MtwvMtFailPDFdown",   "mass of tw vs mass of top PDF up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailPDFup.Sumw2()
            MtwvMtFailPDFdown.Sumw2()

            MtwvMtFailPUup   = TH2F("MtwvMtFailPUup", "mass of tw vs mass of top PU up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailPUdown = TH2F("MtwvMtFailPUdown",   "mass of tw vs mass of top PU up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailPUup.Sumw2()
            MtwvMtFailPUdown.Sumw2()

            MtwvMtFailTopup   = TH2F("MtwvMtFailTopup", "mass of tw vs mass of top sf up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailTopdown = TH2F("MtwvMtFailTopdown",   "mass of tw vs mass of top sf up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailTopup.Sumw2()
            MtwvMtFailTopdown.Sumw2()

            MtwvMtFailScaleup   = TH2F("MtwvMtFailScaleup", "mass of tw vs mass of Q^2 scale up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailScaledown = TH2F("MtwvMtFailScaledown",   "mass of tw vs mass of Q^2 scale down - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailScaleup.Sumw2()
            MtwvMtFailScaledown.Sumw2()

            MtwvMtFailSjbtagup   = TH2F("MtwvMtFailSjbtagup", "mass of tw vs mass of sjbtag sf up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSjbtagdown = TH2F("MtwvMtFailSjbtagdown",   "mass of tw vs mass of sjbtag sf down - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSjbtagup.Sumw2()
            MtwvMtFailSjbtagdown.Sumw2()

            MtwvMtFailTrigup   = TH2F("MtwvMtFailTrigup", "mass of tw vs mass of top trig up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailTrigdown = TH2F("MtwvMtFailTrigdown",   "mass of tw vs mass of top trig up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailTrigup.Sumw2()
            MtwvMtFailTrigdown.Sumw2()
            
            if 'ttbar' in options.set:
                MtwvMtFailTptup    = TH2F("MtwvMtFailTptup",  "mass of tw vs mass of top top pt reweight up - Fail",  60, 50, 350, 35, 500, 4000 )
                MtwvMtFailTptdown  = TH2F("MtwvMtFailTptdown",    "mass of tw vs mass of top top pt reweight down - Fail",60, 50, 350, 35, 500, 4000 )
                MtwvMtFailTptup.Sumw2()
                MtwvMtFailTptdown.Sumw2()

            if ('tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                MtwvMtFailExtrapUp = TH2F("MtwvMtFailExtrapUp", "mass of tw vs mass of top extrapolation uncertainty up - Fail", 60, 50, 350, 35, 500, 4000)
                MtwvMtFailExtrapDown = TH2F("MtwvMtFailExtrapDown", "mass of tw vs mass of top extrapolation uncertainty down - Fail", 60, 50, 350, 35, 500, 4000)
                MtwvMtFailExtrapUp.Sumw2()
                MtwvMtFailExtrapDown.Sumw2()

                MtwvMtFailWup      = TH2F("MtwvMtFailWup",    "mass of tw vs mass of top w tag SF up - Fail", 60, 50, 350, 35, 500, 4000 )
                MtwvMtFailWdown    = TH2F("MtwvMtFailWdown",  "mass of tw vs mass of top w tag SF down - Fail",   60, 50, 350, 35, 500, 4000 )
                MtwvMtFailWup.Sumw2()
                MtwvMtFailWdown.Sumw2()

            # Subtraction of Fail the Pass events that change because of the top SF application
            MtwvMtFailSubPDFup   = TH2F("MtwvMtFailSubPDFup", "mass of tw vs mass of top PDF up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubPDFdown = TH2F("MtwvMtFailSubPDFdown",   "mass of tw vs mass of top PDF up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubPDFup.Sumw2()
            MtwvMtFailSubPDFdown.Sumw2()

            MtwvMtFailSubPUup   = TH2F("MtwvMtFailSubPUup", "mass of tw vs mass of top PU up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubPUdown = TH2F("MtwvMtFailSubPUdown",   "mass of tw vs mass of top PU up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubPUup.Sumw2()
            MtwvMtFailSubPUdown.Sumw2()

            MtwvMtFailSubTopup   = TH2F("MtwvMtFailSubTopup", "mass of tw vs mass of top sf up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubTopdown = TH2F("MtwvMtFailSubTopdown",   "mass of tw vs mass of top sf up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubTopup.Sumw2()
            MtwvMtFailSubTopdown.Sumw2()

            MtwvMtFailSubScaleup   = TH2F("MtwvMtFailSubScaleup", "mass of tw vs mass of Q^2 scale up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubScaledown = TH2F("MtwvMtFailSubScaledown",   "mass of tw vs mass of Q^2 scale down - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubScaleup.Sumw2()
            MtwvMtFailSubScaledown.Sumw2()

            MtwvMtFailSubSjbtagup   = TH2F("MtwvMtFailSubSjbtagup", "mass of tw vs mass of sjbtag sf up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubSjbtagdown = TH2F("MtwvMtFailSubSjbtagdown",   "mass of tw vs mass of sjbtag sf down - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubSjbtagup.Sumw2()
            MtwvMtFailSubSjbtagdown.Sumw2()

            MtwvMtFailSubTrigup   = TH2F("MtwvMtFailSubTrigup", "mass of tw vs mass of top trig up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubTrigdown = TH2F("MtwvMtFailSubTrigdown",   "mass of tw vs mass of top trig up - FailSub", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailSubTrigup.Sumw2()
            MtwvMtFailSubTrigdown.Sumw2()

            
            if 'ttbar' in options.set:
                MtwvMtFailSubTptup    = TH2F("MtwvMtFailSubTptup",  "mass of tw vs mass of top top pt reweight up - FailSub",  60, 50, 350, 35, 500, 4000 )
                MtwvMtFailSubTptdown  = TH2F("MtwvMtFailSubTptdown",    "mass of tw vs mass of top top pt reweight down - FailSub",60, 50, 350, 35, 500, 4000 )
                MtwvMtFailSubTptup.Sumw2()
                MtwvMtFailSubTptdown.Sumw2()

            if ('tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                MtwvMtFailSubExtrapUp = TH2F("MtwvMtFailSubExtrapUp", "mass of tw vs mass of top extrapolation uncertainty up - FailSub", 60, 50, 350, 35, 500, 4000)
                MtwvMtFailSubExtrapDown = TH2F("MtwvMtFailSubExtrapDown", "mass of tw vs mass of top extrapolation uncertainty down - FailSub", 60, 50, 350, 35, 500, 4000)
                MtwvMtFailSubExtrapUp.Sumw2()
                MtwvMtFailSubExtrapDown.Sumw2()

                MtwvMtFailSubWup      = TH2F("MtwvMtFailSubWup",    "mass of tw vs mass of top w tag SF up - FailSub", 60, 50, 350, 35, 500, 4000 )
                MtwvMtFailSubWdown    = TH2F("MtwvMtFailSubWdown",  "mass of tw vs mass of top w tag SF down - FailSub",   60, 50, 350, 35, 500, 4000 )
                MtwvMtFailSubWup.Sumw2()
                MtwvMtFailSubWdown.Sumw2()

            if not wIsTtagged and 'ttbar' in options.set:
                wFakes = TH1F('wFakes','Status of ttbar MC tops that are tagged as W',4,0,4)
                wFakes.GetXaxis().SetBinLabel(1,'0 merged particles')
                wFakes.GetXaxis().SetBinLabel(2,'1 merged particle')
                wFakes.GetXaxis().SetBinLabel(3,'2 merged particle')
                wFakes.GetXaxis().SetBinLabel(4,'3 merged particle')

            TopMerging = TH1F('TopMerging','Merge status of top tagged jets',7,-3,4)
            TopMerging.GetXaxis().SetBinLabel(1,'Only two prongs found')
            TopMerging.GetXaxis().SetBinLabel(2,'Only one prong found')
            TopMerging.GetXaxis().SetBinLabel(3,'Zero prongs found')
            TopMerging.GetXaxis().SetBinLabel(4,'0 prongs in jet')
            TopMerging.GetXaxis().SetBinLabel(5,'1 merged particle')
            TopMerging.GetXaxis().SetBinLabel(6,'2 merged particle')
            TopMerging.GetXaxis().SetBinLabel(7,'3 merged particle')

        Mtw_cut1    = TH1F("Mtw_cut1",  "mass of tw after pt cuts and dy cuts", 35, 500, 4000)
        Mtw_cut2    = TH1F("Mtw_cut2",  "mass of tw after tau21 cut", 35, 500, 4000)
        Mtw_cut3    = TH1F("Mtw_cut3",  "mass of tw after wmass cut", 35, 500, 4000)
        Mtw_cut4    = TH1F("Mtw_cut4", "mass of tw after tau32 cut", 35, 500, 4000)
        Mtw_cut5    = TH1F("Mtw_cut5", "mass of tw after sjbtag cut", 35, 500, 4000)
        Mtw_cut1.Sumw2()
        Mtw_cut2.Sumw2()
        Mtw_cut3.Sumw2()
        Mtw_cut4.Sumw2()
        Mtw_cut5.Sumw2()


    dumbTagPass = TH2F("dumbTagPass",     "mass of tw vs mass of top - Pass random tag", 60, 50, 350, 35, 500, 4000 )
    dumbTagFail = TH2F("dumbTagFail",     "mass of tw vs mass of top - Fail random tag", 60, 50, 350, 35, 500, 4000 )

    dumbTagPass.Sumw2()
    dumbTagFail.Sumw2()

    weightArrays = {
        'PDF':array.array('d',[1.0]),
        'Pileup':array.array('d',[1.0]),
        'Topsf':array.array('d',[1.0]),
        'Q2':array.array('d',[1.0]),
        # 'sjbsf':array.array('d',[1.0]),
        'Wsf':array.array('d',[1.0]),
        'Trigger':array.array('d',[1.0]),
        'Ptreweight':array.array('d',[1.0]),
        'Extrap':array.array('d',[1.0]),
        'Total':array.array('d',[1.0])
    }
    weightTree = Make_Trees(weightArrays,'weights')

    ###############################
    # Grab root file that we want #
    ###############################
    file_string = Load_jetNano(options.set,options.year)
    file = TFile.Open('../temp/ttbar_bstar17.root')


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
    if 'data' not in options.set:
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
    wmatchcount = 0
    inLepSel = 0
    notInLepSel = 0

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
                    checkingFirstHemi = True
                    tVals = {
                        "tau1":leadingJet.tau1,
                        "tau2":leadingJet.tau2,
                        "tau3":leadingJet.tau3,
                        "phi":leadingJet.phi,
                        "mass":leadingJet.mass_nom,
                        "pt":leadingJet.pt_nom, # This will just have JER and JES corrections
                        "eta":leadingJet.eta,
                        "SDmass":leadingJet.msoftdrop_raw if 'data' not in options.set else leadingJet.msoftdrop, # Does not have PUPPI SD mass correction
                        "subJetIdx1":leadingJet.subJetIdx1,
                        "subJetIdx2":leadingJet.subJetIdx2,
                        "JEScorr":1.0
                    }
                    wVals = {
                        "tau1":subleadingJet.tau1,
                        "tau2":subleadingJet.tau2,
                        "tau3":subleadingJet.tau3,
                        "phi":subleadingJet.phi,
                        "mass":subleadingJet.mass_nom, # This will just JEC
                        "pt":subleadingJet.pt_nom, # This will just JEC
                        "eta":subleadingJet.eta,
                        "SDmass":subleadingJet.msoftdrop_raw if 'data' not in options.set else subleadingJet.msoftdrop, # Has only PUPPI SD mass correction
                        "subJetIdx1":subleadingJet.subJetIdx1,
                        "subJetIdx2":subleadingJet.subJetIdx2,
                        "JEScorr":1.0
                    }

                    if options.JES != 'nom':
                        tVals['JEScorr'] = getattr(leadingJet,'corr_JES_Total'+options.JES.capitalize())
                        wVals['JEScorr'] = getattr(subleadingJet,'corr_JES_Total'+options.JES.capitalize())
                    if 'data' not in options.set:
                        tVals['JERcorr'] = getattr(leadingJet,'corr_JER_'+options.JER)
                        wVals["JERcorr"] = getattr(subleadingJet,'corr_JER_'+options.JER)

                        if options.region != 'ttbar':
                            wVals["JMScorr"] = getattr(subleadingJet,'corr_JMS_'+options.JER)
                            wVals["JMRcorr"] = getattr(subleadingJet,'groomed_corr_JMR_'+options.JER)

                elif hemis == 'hemis1' and doneAlready == False:
                    checkingFirstHemi = False
                    wVals = {
                        "tau1":leadingJet.tau1,
                        "tau2":leadingJet.tau2,
                        "tau3":leadingJet.tau3,
                        "phi":leadingJet.phi,
                        "mass":leadingJet.mass_nom, # This will just JEC
                        "pt":leadingJet.pt_nom, # This will just JEC
                        "eta":leadingJet.eta,
                        "SDmass":leadingJet.msoftdrop_raw if 'data' not in options.set else leadingJet.msoftdrop, # Has only PUPPI SD mass correction
                        "subJetIdx1":leadingJet.subJetIdx1,
                        "subJetIdx2":leadingJet.subJetIdx2,
                        "JEScorr":1.0 
                    }
                    tVals = {
                        "tau1":subleadingJet.tau1,
                        "tau2":subleadingJet.tau2,
                        "tau3":subleadingJet.tau3,
                        "phi":subleadingJet.phi,
                        "mass":subleadingJet.mass_nom, # This will just JEC
                        "pt":subleadingJet.pt_nom, # This will just JEC
                        "eta":subleadingJet.eta,
                        "SDmass":subleadingJet.msoftdrop_raw if 'data' not in options.set else subleadingJet.msoftdrop, # Does not have PUPPI SD mass correction
                        "subJetIdx1":subleadingJet.subJetIdx1,
                        "subJetIdx2":subleadingJet.subJetIdx2,
                        "JEScorr":1.0
                    }

                    if options.JES != 'nom':
                        wVals['JEScorr'] = getattr(leadingJet,'corr_JES_Total'+options.JES.capitalize())
                        tVals['JEScorr'] = getattr(subleadingJet,'corr_JES_Total'+options.JES.capitalize())

                    if 'data' not in options.set:
                         wVals['JERcorr'] = getattr(leadingJet,'corr_JER_'+options.JER)
                         tVals["JERcorr"] = getattr(subleadingJet,'corr_JER_'+options.JER)

                         if options.region != 'ttbar':
                            wVals["JMScorr"] = getattr(leadingJet,'corr_JMS_'+options.JER)
                            wVals["JMRcorr"] = getattr(leadingJet,'groomed_corr_JMR_'+options.JER)

                elif hemis == 'hemis1' and doneAlready == True:
                    continue

                # Apply jet corrections
                if 'data' not in options.set:
                    wVals['pt'] = wVals['pt']*wVals['JEScorr']*wVals['JERcorr']
                    tVals['pt'] = tVals['pt']*tVals['JEScorr']*tVals['JERcorr']
                    wVals['SDmass'] = wVals['SDmass']*wVals['JEScorr']*wVals['JERcorr']
                    tVals['SDmass'] = tVals['SDmass']*tVals['JEScorr']*tVals['JERcorr']
                    if options.region != 'ttbar':
                        wVals['SDmass'] = wVals['SDmass']*wVals['JMScorr']*wVals['JMRcorr']


                # Make the lorentz vectors
                tjet = TLorentzVector()
                tjet.SetPtEtaPhiM(tVals["pt"],tVals["eta"],tVals["phi"],tVals["SDmass"])

                wjet = TLorentzVector()
                wjet.SetPtEtaPhiM(wVals["pt"],wVals["eta"],wVals["phi"],wVals["SDmass"])

                ht = tjet.Perp() + wjet.Perp()
                MtopW = (tjet+wjet).M()
                
                # Make and get all cuts
                MtopW_cut = MtopW > 1000.
                dy_val = abs(tjet.Rapidity()-wjet.Rapidity())
                wpt_cut = Cuts['wpt'][0]<wjet.Perp()<Cuts['wpt'][1]
                tpt_cut = Cuts['tpt'][0]<tjet.Perp()<Cuts['tpt'][1]
                dy_cut = Cuts['dy'][0]<=dy_val<Cuts['dy'][1]
                
                # if runOthers:
                #     deltaRap.Fill(dy_val)
                #     Pt1presel.Fill(leadingJet.pt)
                #     Pt2presel.Fill(subleadingJet.pt)

                # Standard W tag
                if not wIsTtagged:
                    if wVals['tau1'] > 0: tau21val = wVals['tau2']/wVals['tau1']
                    else: continue

                    tau21_cut =  Cuts['tau21'][0]<=tau21val<Cuts['tau21'][1]
                    wmass_cut = Cuts['wmass'][0]<=wVals["SDmass"]<Cuts['wmass'][1]
                    preselection = wpt_cut and tpt_cut and dy_cut and MtopW_cut and wmass_cut and tau21_cut
                
                    if runOthers and checkingFirstHemi:
                        if wpt_cut and tpt_cut and dy_cut:
                            Mtw_cut1.Fill(MtopW,norm_weight)
                            if tau21_cut:
                                Mtw_cut2.Fill(MtopW,norm_weight)
                                if wmass_cut:
                                    Mtw_cut3.Fill(MtopW,norm_weight)

                # If tagging regular W as a top
                else:
                    wmass_cut = Cuts['tmass'][0]<=wVals["SDmass"]<Cuts['tmass'][1]

                    if wVals['tau2'] > 0: w_tau32val = wVals['tau3']/wVals['tau2']
                    else: continue

                    w_tau32_cut = Cuts['tau32tight'][0]<=w_tau32val<Cuts['tau32tight'][1]

                    if (wVals['subJetIdx1'] < 0) or (wVals['subJetIdx1'] >= len(subJetsColl)):
                        if (wVals['subJetIdx2'] < 0) or (wVals['subJetIdx2'] >= len(subJetsColl)): continue # if both negative, throw away event
                        else: w_btagval = getattr(subJetsColl[wVals['subJetIdx2']],btagtype)  # if idx2 not negative or bad index, use that
                            
                    else:
                        if (wVals['subJetIdx2'] < 0) or (wVals['subJetIdx2'] >= len(subJetsColl)): w_btagval = getattr(subJetsColl[wVals['subJetIdx1']],btagtype)# if idx1 not negative, use that
                        # if both not negative, use largest
                        else: w_btagval = max(getattr(subJetsColl[wVals['subJetIdx1']],btagtype), getattr(subJetsColl[wVals['subJetIdx2']],btagtype))
                        
                        w_sjbtag_cut = Cuts['deepbtag'][0]<= w_btagval<Cuts['deepbtag'][1]
                        preselection = wpt_cut and tpt_cut and dy_cut and MtopW_cut and wmass_cut and w_sjbtag_cut and w_tau32_cut

                    if runOthers and checkingFirstHemi:
                        if wpt_cut and tpt_cut and dy_cut:
                            Mtw_cut1.Fill(MtopW,norm_weight)
                            if w_sjbtag_cut and w_tau32_cut:
                                Mtw_cut2.Fill(MtopW,norm_weight)
                                if wmass_cut:
                                    Mtw_cut3.Fill(MtopW,norm_weight)

                if preselection: 
                    doneAlready = True
                    lepveto,lepvetoSF = LeptonVeto(event,options.year,lepSFfile)

                    if not lepveto:
                        inLepSel += 1
                        continue
                    else:
                        notInLepSel += 1

                    # Get GenParticles for use below
                    if 'data' not in options.set:
                        GenParticles = Collection(event,'GenPart')

                    ###############################
                    # Weighting and Uncertainties #
                    ###############################

                    # Initialize event weight
                    weights = { 'PDF':{},
                                'Pileup':{},
                                'Topsf':{},
                                'Q2':{},
                                # 'sjbsf':{},
                                'Wsf':{},
                                'Trigger':{},
                                'Ptreweight':{},
                                'Extrap':{}}
                    for k in weightArrays.keys(): weightArrays[k][0] = 1.0
                    
                    if 'data' not in options.set:
                        # PDF weight
                        weights['PDF']['up'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'up')
                        weights['PDF']['down'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'down')

                        # Q2 Scale
                        weights['Q2']['up'] = inTree.readBranch('LHEScaleWeight')[0]
                        weights['Q2']['down'] = inTree.readBranch('LHEScaleWeight')[8]

                        # Pileup reweighting applied
                        if options.pileup == 'on':
                            weights['Pileup']['nom'] = inTree.readBranch('puWeight')
                            weights['Pileup']['up'] = inTree.readBranch('puWeightUp')
                            weights['Pileup']['down'] = inTree.readBranch('puWeightDown')

                        if not wIsTtagged:
                            # Determine purity for scale factor
                            if options.region == 'default': Wpurity = 'HP'
                            elif options.region == 'sideband':
                                if options.year == '16': Wpurity = 'LP'
                                elif options.year != '16' and (Cuts['tau21LP'][0] < tau21val < Cuts['tau21LP'][1]): Wpurity = 'LP'
                                else: Wpurity = False
                            else: Wpurity = False

                            if 'ttbar' in options.set and runOthers:
                                dummyvar,top_merged_particles = SFT_Lookup(wjet,ttagsffile,GenParticles,'tight')
                                wFakes.Fill(top_merged_particles+1)

                            # W matching
                            if ('QCD' not in options.set and not wIsTtagged):#'tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                                if WJetMatching(wjet,GenParticles) and Wpurity != False:
                                    wmatchcount+=1
                                    wtagsf = Cons['wtagsf_'+Wpurity]
                                    wtagsfsig = Cons['wtagsfsig_'+Wpurity]

                                else:
                                    wtagsf = 1.0
                                    wtagsfsig = 0.0

                                weights['Wsf']['nom'] = wtagsf
                                weights['Wsf']['up'] = (wtagsf + wtagsfsig)
                                weights['Wsf']['down'] = (wtagsf - wtagsfsig)

                                # Get the extrapolation uncertainty
                                extrap = ExtrapUncert_Lookup(wjet.Perp(),Wpurity,options.year)
                                weights['Extrap']['up'] = 1+extrap
                                weights['Extrap']['down'] = 1-extrap

                        # Trigger weight applied
                        if tname != 'none' and 'data' not in options.set:
                            weights['Trigger']['nom'] = Trigger_Lookup( ht , TrigPlot1 )[0]
                            weights['Trigger']['up'] = Trigger_Lookup( ht , TrigPlot1 )[1]
                            weights['Trigger']['down'] = Trigger_Lookup( ht , TrigPlot1 )[2]

                        # Top pt reweighting
                        if options.ptreweight == "on" and 'ttbar' in options.set:
                            weights['Ptreweight']['nom'] = PTW_Lookup(GenParticles)
                            weights['Ptreweight']['up'] = 1.5*PTW_Lookup(GenParticles)
                            weights['Ptreweight']['down'] = 0.5*PTW_Lookup(GenParticles)
                    

                    # Fill weight tree
                    for k in weightArrays.keys():
                        if k != 'Total' and 'nom' in weights[k].keys(): weightArrays[k][0] = weights[k]['nom']
                        elif k != 'Total' and 'nom' not in weights[k].keys(): weightArrays[k][0] = 1.0
                        else:
                            weightArrays[k][0] = 1.0
                            for w in weights.keys(): 
                                if 'nom' in weights[w]: weightArrays[k][0] *= weights[w]['nom']
                    weightTree.Fill()

                    ####################################
                    # Split into top tag pass and fail #
                    ####################################
                    if tVals['tau2'] > 0:
                        tau32val = tVals['tau3']/tVals['tau2']
                    else:
                        continue
                    tau32_cut = Cuts['tau32'+options.tau32][0]<=tau32val<Cuts['tau32'+options.tau32][1]

                    if (tVals['subJetIdx1'] < 0) or (tVals['subJetIdx1'] >= len(subJetsColl)):
                        if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)):  # if both negative, throw away event
                            continue
                        else:   # if idx2 not negative or bad index, use that
                            btagval = getattr(subJetsColl[tVals['subJetIdx2']],btagtype)

                    else:
                        if (tVals['subJetIdx2'] < 0) or (tVals['subJetIdx2'] >= len(subJetsColl)): # if idx1 not negative, use that
                            btagval = getattr(subJetsColl[tVals['subJetIdx1']],btagtype)
                        # if both not negative, use largest
                        else:
                            btagval = max(getattr(subJetsColl[tVals['subJetIdx1']],btagtype), getattr(subJetsColl[tVals['subJetIdx2']],btagtype))
                        
                    sjbtag_cut = Cuts['deepbtag'][0]<= btagval<Cuts['deepbtag'][1]
                        

                    top_tag = sjbtag_cut and tau32_cut

                    if tau32_cut:
                        if runOthers and checkingFirstHemi: Mtw_cut4.Fill(MtopW,norm_weight)
                        if sjbtag_cut:
                            if runOthers and checkingFirstHemi: Mtw_cut5.Fill(MtopW,norm_weight)

                    if top_tag:
                        # Top tagging tau32+sjbtag scale factor 
                        if "QCD" not in options.set and 'data' not in options.set:
                            sft,top_merging_status = SFT_Lookup(tjet,ttagsffile,GenParticles,options.tau32,count)
                            if runOthers: TopMerging.Fill(top_merging_status)
                            weights['Topsf']['nom'] = sft[0]
                            weights['Topsf']['up'] = sft[1]
                            weights['Topsf']['down'] = sft[2]
                            # Subjet b tagging scale factor
                            # weights['sjbsf']['nom'] = reader.eval_auto_bounds('central', 0, abs(tVals['eta']), tVals['pt'])
                            # weights['sjbsf']['up'] = reader.eval_auto_bounds('up', 0, abs(tVals['eta']), tVals['pt'])
                            # weights['sjbsf']['down'] = reader.eval_auto_bounds('down', 0, abs(tVals['eta']), tVals['pt'])

                        else:
                            weights['Topsf']['nom'] = 1.0
                            weights['Topsf']['up'] =  1.0
                            weights['Topsf']['down'] = 1.0
                            # weights['sjbsf']['nom'] = 1.0
                            # weights['sjbsf']['up'] = 1.0
                            # weights['sjbsf']['down'] = 1.0

                        if wIsTtagged:
                            # Top tagging tau32+sjbtag scale factor 
                            if "QCD" not in options.set and 'data' not in options.set:
                                sft,wtop_merging_status = SFT_Lookup(wjet,ttagsffile,GenParticles,'tight')#(wjet, ttagsffile, GenParticles, options.tau32)#, GenParticles)
                                weights['Topsf']['nom'] *= sft[0]
                                weights['Topsf']['up'] *= sft[1]
                                weights['Topsf']['down'] *= sft[2]

                                # Subjet b tagging scale factor
                                # weights['sjbsf']['nom'] *= reader.eval_auto_bounds('central', 0, abs(wVals['eta']), wVals['pt'])
                                # weights['sjbsf']['up'] *= reader.eval_auto_bounds('up', 0, abs(wVals['eta']), wVals['pt'])
                                # weights['sjbsf']['down'] *= reader.eval_auto_bounds('down', 0, abs(wVals['eta']), wVals['pt'])

                            else:
                                weights['Topsf']['nom'] = 1.0
                                weights['Topsf']['up'] =  1.0
                                weights['Topsf']['down'] = 1.0
                                # weights['sjbsf']['nom'] = 1.0
                                # weights['sjbsf']['up'] = 1.0
                                # weights['sjbsf']['down'] = 1.0


                        MtwvMtPass.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 
                        MtwvMtFailSub.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                        if runOthers:
                            if 'data' not in options.set:
                                MtwvMtPassPDFup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_up'))
                                MtwvMtPassPDFdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_down'))

                                MtwvMtPassPUup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_up'))
                                MtwvMtPassPUdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_down'))

                                MtwvMtPassTopup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_up'))
                                MtwvMtPassTopdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_down'))

                                MtwvMtPassScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up'))
                                MtwvMtPassScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down'))

                                # MtwvMtPassSjbtagup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_up'))
                                # MtwvMtPassSjbtagdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_down'))

                                MtwvMtPassTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up'))
                                MtwvMtPassTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down'))

                                MtwvMtFailSubPDFup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                MtwvMtFailSubPDFdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                MtwvMtFailSubPUup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                MtwvMtFailSubPUdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                MtwvMtFailSubTopup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])*(weights['Topsf']['up']-1))
                                MtwvMtFailSubTopdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])*(weights['Topsf']['down']-1))

                                MtwvMtFailSubScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                MtwvMtFailSubScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                # MtwvMtFailSubSjbtagup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                # MtwvMtFailSubSjbtagdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                MtwvMtFailSubTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                MtwvMtFailSubTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                if ('tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                                    MtwvMtPassWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up')) 
                                    MtwvMtPassWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down'))

                                    MtwvMtPassExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up'))
                                    MtwvMtPassExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down'))

                                    MtwvMtFailSubWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                    MtwvMtFailSubWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                    MtwvMtFailSubExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                    MtwvMtFailSubExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                if 'ttbar' in options.set:
                                    MtwvMtPassTptup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_up'))
                                    MtwvMtPassTptdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_down')) 

                                    MtwvMtFailSubTptup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                    MtwvMtFailSubTptdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_down',drop=['Topsf'])*(weights['Topsf']['nom']-1)) 

                    else:
                        MtwvMtFail.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])) 

                        if flatTag() < 0.1:
                            dumbTagPass.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])) 
                        else:
                            dumbTagFail.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])) 

                        if runOthers and 'data' not in options.set:
                            MtwvMtFailPDFup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_up',drop=['Topsf']))
                            MtwvMtFailPDFdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_down',drop=['Topsf']))

                            MtwvMtFailPUup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_up',drop=['Topsf']))
                            MtwvMtFailPUdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_down',drop=['Topsf']))

                            MtwvMtFailTopup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf']))
                            MtwvMtFailTopdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf']))

                            MtwvMtFailScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up',drop=['Topsf']))
                            MtwvMtFailScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down',drop=['Topsf']))

                            # MtwvMtFailSjbtagup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_up'))
                            # MtwvMtFailSjbtagdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_down'))

                            MtwvMtFailTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up',drop=['Topsf']))
                            MtwvMtFailTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down',drop=['Topsf']))
                            
                            if ('tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                                MtwvMtFailWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up',drop=['Topsf'])) 
                                MtwvMtFailWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down',drop=['Topsf']))

                                MtwvMtFailExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up',drop=['Topsf']))
                                MtwvMtFailExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down',drop=['Topsf']))

                            if 'ttbar' in options.set:
                                MtwvMtFailTptup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_up',drop=['Topsf']))
                                MtwvMtFailTptdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_down',drop=['Topsf'])) 

                
    lepVetoCount.SetBinContent(1,inLepSel)
    lepVetoCount.SetBinContent(2,notInLepSel)
    wmatchCount.SetBinContent(1,wmatchcount)
    nev.SetBinContent(1,count)          
    end = time.time()
    print '\n'
    print str((end-start)/60.) + ' min'

    # Correct the failing distribution from the top tag sf application in pass (subtract events that were gained/lost in pass)
    MtwvMtFail.Add(MtwvMtFailSub,-1)
    if runOthers and 'data' not in options.set:
        MtwvMtFailPDFup.Add(MtwvMtFailSubPDFup,-1)
        MtwvMtFailPDFdown.Add(MtwvMtFailSubPDFdown,-1)
        MtwvMtFailPUup.Add(MtwvMtFailSubPUup,-1)
        MtwvMtFailPUdown.Add(MtwvMtFailSubPUdown,-1)
        MtwvMtFailTopup.Add(MtwvMtFailSubTopup,-1)
        MtwvMtFailTopdown.Add(MtwvMtFailSubTopdown,-1)
        MtwvMtFailScaleup.Add(MtwvMtFailSubScaleup,-1)
        MtwvMtFailScaledown.Add(MtwvMtFailSubScaledown,-1)
        MtwvMtFailTrigup.Add(MtwvMtFailSubTrigup,-1)
        MtwvMtFailTrigdown.Add(MtwvMtFailSubTrigdown,-1)
        if ('tW' in options.set or 'signal' in options.set) and not wIsTtagged:
            MtwvMtFailWup.Add(MtwvMtFailSubWup,-1)
            MtwvMtFailWdown.Add(MtwvMtFailSubWdown,-1)
            MtwvMtFailExtrapUp.Add(MtwvMtFailSubExtrapUp,-1)
            MtwvMtFailExtrapDown.Add(MtwvMtFailSubExtrapDown,-1)
        if 'ttbar' in options.set:
            MtwvMtFailTptup.Add(MtwvMtFailSubTptup,-1)
            MtwvMtFailTptdown.Add(MtwvMtFailSubTptdown,-1)


    f.cd()
    f.Write()
    f.Close()



    
