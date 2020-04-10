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
# import PrefireCorr


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
        tname = 'HLT_PFHT1050ORHLT_PFJet500ORHLT_AK8PFJet380_TrimMass30ORHLT_AK8PFJet400_TrimMass30'
        pretrig_string = 'HLT_Mu50'
    btagtype = 'btagDeepB'

    # if tname == 'HLT_PFHT900ORHLT_PFHT800ORHLT_AK8PFJet450':
    #     tnamestr = 'nominal'
    # else:
    #     tnamestr = tname

    if options.year in ['16','17'] and 'QCD' not in options.set and 'cale' not in options.set: prefcorr = True
    else: prefcorr = False

    # JECs
    runOthers = True
    mod = ''
    JES = ''
    JER = ''
    JMS = ''
    JMR = ''
    if options.JES!='nom':
        mod = '_JES' + '_' + options.JES
        JES = '_'+options.JES
        # JMC_name = '_jesTotal'+options.JES.capitalize()
        # JEC_name = '_jesTotal'+options.JES.capitalize()
        runOthers = False
    if options.JER!='nom':
        mod = '_JER' + '_' + options.JER
        JER = '_'+options.JER
        # JMC_name = '_nom'
        # JEC_name = '_jer'+options.JER.capitalize()
        runOthers = False
    if options.JMS!='nom':
        mod = '_JMS' + '_' + options.JMS
        JMS = '_'+options.JMS
        # JMC_name = '_jms'+options.JMS.capitalize()
        # JEC_name = '_nom'
        runOthers = False
    if options.JMR!='nom':
        mod = '_JMR' + '_' + options.JMR
        JMR = '_'+options.JMR
        # JMC_name = '_jmr'+options.JMR.capitalize()
        # JEC_name = '_nom'
        runOthers = False
    if 'scale' in options.set:
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

    # tempyear = options.year
    # if options.year == '18':
    #     tempyear = '17'

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
        
        ttagsffile = TFile.Open('SFs/20'+options.year+'TopTaggingScaleFactors_NoMassCut.root')
        ttagsffile_wmass = TFile.Open('SFs/20'+options.year+'TopTaggingScaleFactors.root')
        if 'signal' in options.set:
            pdf_norm_file = TFile.Open('SFs/pdf_norm_uncertainties_bstar.root')
            pdf_norm = pdf_norm_file.Get(options.set+'_'+options.year)

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
    MtwvMtPass     = TH2F("MtwvMtPass",     "mass of tw vs mass of top - Pass", 60, 50, 350, 70, 500, 4000 )
    if 'ttbar' in options.set: MtwvMtPassBadTpt     = TH2F("MtwvMtPassBadTpt",     "mass of tw vs mass of top - Pass - Bad top pt reweight", 60, 50, 350, 70, 500, 4000 )
    MtwvMtPassNotrig    = TH2F("MtwvMtPassNotrig",     "mass of tw vs mass of top - Pass - No trigger", 60, 50, 350, 70, 500, 4000 )
    MtwvMtFail     = TH2F("MtwvMtFail",     "mass of tw vs mass of top - Fail", 60, 50, 350, 70, 500, 4000 )
    MtwvMtFailSub  = TH2F("MtwvMtFailSub",     "mass of tw vs mass of top - FailSub", 60, 50, 350, 70, 500, 4000 )
    MtwvMtPass.Sumw2()
    if 'ttbar' in options.set: MtwvMtPassBadTpt.Sumw2()
    MtwvMtFail.Sumw2()
    MtwvMtFailSub.Sumw2()

    nev = TH1F("nev",   "nev",      1, 0, 1 )
    Mw = TH1F("Mw","m_{W} (GeV)",40,40,120)

    # lepVetoCount = TH1F('lepVetoCount','Lepton veto count',2,0,2)
    # lepVetoCount.GetXaxis().SetBinLabel(1,'In Semi-lep channels')
    # lepVetoCount.GetXaxis().SetBinLabel(2,'Not in Semi-lep channels')

    sigDecay = TH1F('sigDecay','sigDecay',11,0.5,11.5)
    sigDecay.GetXaxis().SetBinLabel(1,'Di-hadronic')
    sigDecay.GetXaxis().SetBinLabel(2,'Leptonic W')
    sigDecay.GetXaxis().SetBinLabel(3,'Leptonic top')
    sigDecay.GetXaxis().SetBinLabel(4,'All-had with lep b')
    sigDecay.GetXaxis().SetBinLabel(5,'All-had with lep b and vetoed')
    sigDecay.GetXaxis().SetBinLabel(6,'All-had with lep b and not vetoed')
    sigDecay.GetXaxis().SetBinLabel(7,'All-had vetoed')
    sigDecay.GetXaxis().SetBinLabel(8,'All-had lep-W veto')
    sigDecay.GetXaxis().SetBinLabel(9,'All-had lep-t veto')
    sigDecay.GetXaxis().SetBinLabel(10,'All-had not vetoed')
    sigDecay.GetXaxis().SetBinLabel(11,'Other')

    wmatchCount = TH1F('wmatchCount','W match count',1,0,1)
    wmatchCount.GetXaxis().SetBinLabel(1,'Number of times the W matching passed')

    if runOthers == True:
        if 'data' not in options.set:
            MtwvMtPassPDFup   = TH2F("MtwvMtPassPDFup", "mass of tw vs mass of top PDF up - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassPDFdown = TH2F("MtwvMtPassPDFdown",   "mass of tw vs mass of top PDF down - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassPDFup.Sumw2()
            MtwvMtPassPDFdown.Sumw2()

            MtwvMtPassPUup   = TH2F("MtwvMtPassPUup", "mass of tw vs mass of top PU up - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassPUdown = TH2F("MtwvMtPassPUdown",   "mass of tw vs mass of top PU down - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassPUup.Sumw2()
            MtwvMtPassPUdown.Sumw2()

            # if not wIsTtagged:
            MtwvMtPassTop3up   = TH2F("MtwvMtPassTop3up", "mass of tw vs mass of top sf up (merged) - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassTop3down = TH2F("MtwvMtPassTop3down",   "mass of tw vs mass of top sf down (merged) - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassTop3up.Sumw2()
            MtwvMtPassTop3down.Sumw2()

            MtwvMtPassTop2up   = TH2F("MtwvMtPassTop2up", "mass of tw vs mass of top sf up (semi-merged) - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassTop2down = TH2F("MtwvMtPassTop2down",   "mass of tw vs mass of top sf down (semi-merged) - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassTop2up.Sumw2()
            MtwvMtPassTop2down.Sumw2()

            MtwvMtPassTop1up   = TH2F("MtwvMtPassTop1up", "mass of tw vs mass of top sf up (not merged) - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassTop1down = TH2F("MtwvMtPassTop1down",   "mass of tw vs mass of top sf down (not merged) - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassTop1up.Sumw2()
            MtwvMtPassTop1down.Sumw2()

            MtwvMtPassScaleup   = TH2F("MtwvMtPassScaleup", "mass of tw vs mass of Q^2 scale up - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassScaledown = TH2F("MtwvMtPassScaledown",   "mass of tw vs mass of Q^2 scale down - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassScaleup.Sumw2()
            MtwvMtPassScaledown.Sumw2()

            MtwvMtPassSjbtagup   = TH2F("MtwvMtPassSjbtagup", "mass of tw vs mass of sjbtag sf up - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassSjbtagdown = TH2F("MtwvMtPassSjbtagdown",   "mass of tw vs mass of sjbtag sf down - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassSjbtagup.Sumw2()
            MtwvMtPassSjbtagdown.Sumw2()

            MtwvMtPassTrigup   = TH2F("MtwvMtPassTrigup", "mass of tw vs mass of top trig up - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassTrigdown = TH2F("MtwvMtPassTrigdown",   "mass of tw vs mass of top trig down - Pass", 60, 50, 350, 70, 500, 4000 )
            MtwvMtPassTrigup.Sumw2()
            MtwvMtPassTrigdown.Sumw2()

            if prefcorr:
                MtwvMtPassPrefireup = TH2F("MtwvMtPassPrefireup", "mass of tw vs mass of top prefire up - Pass", 60, 50, 350, 70, 500, 4000 )
                MtwvMtPassPrefiredown = TH2F("MtwvMtPassPrefiredown",   "mass of tw vs mass of top prefire down - Pass", 60, 50, 350, 70, 500, 4000 )
                MtwvMtPassPrefireup.Sumw2()
                MtwvMtPassPrefiredown.Sumw2()

            if 'ttbar' in options.set:
                MtwvMtPassTptAlphaup    = TH2F("MtwvMtPassTptAlphaup",  "mass of tw vs mass of top top pt reweight alpha up - Pass",  60, 50, 350, 70, 500, 4000 )
                MtwvMtPassTptAlphadown  = TH2F("MtwvMtPassTptAlphadown",    "mass of tw vs mass of top top pt reweight alpha down - Pass",60, 50, 350, 70, 500, 4000 )
                MtwvMtPassTptAlphaup.Sumw2()
                MtwvMtPassTptAlphadown.Sumw2()

                MtwvMtPassTptBetaup    = TH2F("MtwvMtPassTptBetaup",  "mass of tw vs mass of top top pt reweight beta up - Pass",  60, 50, 350, 70, 500, 4000 )
                MtwvMtPassTptBetadown  = TH2F("MtwvMtPassTptBetadown",    "mass of tw vs mass of top top pt reweight beta down - Pass",60, 50, 350, 70, 500, 4000 )
                MtwvMtPassTptBetaup.Sumw2()
                MtwvMtPassTptBetadown.Sumw2()


            if ('tW' in options.set or 'signal' in options.set or 'ttbar' in options.set) and not wIsTtagged:
                MtwvMtPassWup      = TH2F("MtwvMtPassWup",    "mass of tw vs mass of top w tag SF up - Pass", 60, 50, 350, 70, 500, 4000 )
                MtwvMtPassWdown    = TH2F("MtwvMtPassWdown",  "mass of tw vs mass of top w tag SF down - Pass",   60, 50, 350, 70, 500, 4000 )
                MtwvMtPassWup.Sumw2()
                MtwvMtPassWdown.Sumw2()

                MtwvMtPassExtrapUp = TH2F("MtwvMtPassExtrapUp", "mass of tw vs mass of top extrapolation uncertainty up - Pass", 60, 50, 350, 70, 500, 4000)
                MtwvMtPassExtrapDown = TH2F("MtwvMtPassExtrapDown", "mass of tw vs mass of top extrapolation uncertainty down - Pass", 60, 50, 350, 70, 500, 4000)
                MtwvMtPassExtrapUp.Sumw2()
                MtwvMtPassExtrapDown.Sumw2()

            # Fail
            MtwvMtFailPDFup   = TH2F("MtwvMtFailPDFup", "mass of tw vs mass of top PDF up - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailPDFdown = TH2F("MtwvMtFailPDFdown",   "mass of tw vs mass of top PDF up - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailPDFup.Sumw2()
            MtwvMtFailPDFdown.Sumw2()

            MtwvMtFailPUup   = TH2F("MtwvMtFailPUup", "mass of tw vs mass of top PU up - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailPUdown = TH2F("MtwvMtFailPUdown",   "mass of tw vs mass of top PU up - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailPUup.Sumw2()
            MtwvMtFailPUdown.Sumw2()

            MtwvMtFailTop3up   = TH2F("MtwvMtFailTop3up", "mass of tw vs mass of top sf up (merged) - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailTop3down = TH2F("MtwvMtFailTop3down",   "mass of tw vs mass of top sf up (merged) - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailTop3up.Sumw2()
            MtwvMtFailTop3down.Sumw2()

            MtwvMtFailTop2up   = TH2F("MtwvMtFailTop2up", "mass of tw vs mass of top sf up (semi-merged) - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailTop2down = TH2F("MtwvMtFailTop2down",   "mass of tw vs mass of top sf up (semi-merged) - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailTop2up.Sumw2()
            MtwvMtFailTop2down.Sumw2()

            MtwvMtFailTop1up   = TH2F("MtwvMtFailTop1up", "mass of tw vs mass of top sf up (not merged) - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailTop1down = TH2F("MtwvMtFailTop1down",   "mass of tw vs mass of top sf up (not merged) - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailTop1up.Sumw2()
            MtwvMtFailTop1down.Sumw2()

            MtwvMtFailScaleup   = TH2F("MtwvMtFailScaleup", "mass of tw vs mass of Q^2 scale up - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailScaledown = TH2F("MtwvMtFailScaledown",   "mass of tw vs mass of Q^2 scale down - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailScaleup.Sumw2()
            MtwvMtFailScaledown.Sumw2()

            MtwvMtFailSjbtagup   = TH2F("MtwvMtFailSjbtagup", "mass of tw vs mass of sjbtag sf up - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSjbtagdown = TH2F("MtwvMtFailSjbtagdown",   "mass of tw vs mass of sjbtag sf down - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSjbtagup.Sumw2()
            MtwvMtFailSjbtagdown.Sumw2()

            MtwvMtFailTrigup   = TH2F("MtwvMtFailTrigup", "mass of tw vs mass of top trig up - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailTrigdown = TH2F("MtwvMtFailTrigdown",   "mass of tw vs mass of top trig up - Fail", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailTrigup.Sumw2()
            MtwvMtFailTrigdown.Sumw2()

            if prefcorr:
                MtwvMtFailPrefireup = TH2F("MtwvMtFailPrefireup", "mass of tw vs mass of top prefire up - Pass", 60, 50, 350, 70, 500, 4000 )
                MtwvMtFailPrefiredown = TH2F("MtwvMtFailPrefiredown",   "mass of tw vs mass of top prefire down - Pass", 60, 50, 350, 70, 500, 4000 )
                MtwvMtFailPrefireup.Sumw2()
                MtwvMtFailPrefiredown.Sumw2()
            
            if 'ttbar' in options.set:
                MtwvMtFailTptAlphaup    = TH2F("MtwvMtFailTptAlphaup",  "mass of tw vs mass of top top pt reweight alpha up - Fail",  60, 50, 350, 70, 500, 4000 )
                MtwvMtFailTptAlphadown  = TH2F("MtwvMtFailTptAlphadown",    "mass of tw vs mass of top top pt reweight alpha down - Fail",60, 50, 350, 70, 500, 4000 )
                MtwvMtFailTptAlphaup.Sumw2()
                MtwvMtFailTptAlphadown.Sumw2()

                MtwvMtFailTptBetaup    = TH2F("MtwvMtFailTptBetaup",  "mass of tw vs mass of top top pt reweight beta up - Fail",  60, 50, 350, 70, 500, 4000 )
                MtwvMtFailTptBetadown  = TH2F("MtwvMtFailTptBetadown",    "mass of tw vs mass of top top pt reweight beta down - Fail",60, 50, 350, 70, 500, 4000 )
                MtwvMtFailTptBetaup.Sumw2()
                MtwvMtFailTptBetadown.Sumw2()

            if ('tW' in options.set or 'signal' in options.set or 'ttbar' in options.set) and not wIsTtagged:
                MtwvMtFailExtrapUp = TH2F("MtwvMtFailExtrapUp", "mass of tw vs mass of top extrapolation uncertainty up - Fail", 60, 50, 350, 70, 500, 4000)
                MtwvMtFailExtrapDown = TH2F("MtwvMtFailExtrapDown", "mass of tw vs mass of top extrapolation uncertainty down - Fail", 60, 50, 350, 70, 500, 4000)
                MtwvMtFailExtrapUp.Sumw2()
                MtwvMtFailExtrapDown.Sumw2()

                MtwvMtFailWup      = TH2F("MtwvMtFailWup",    "mass of tw vs mass of top w tag SF up - Fail", 60, 50, 350, 70, 500, 4000 )
                MtwvMtFailWdown    = TH2F("MtwvMtFailWdown",  "mass of tw vs mass of top w tag SF down - Fail",   60, 50, 350, 70, 500, 4000 )
                MtwvMtFailWup.Sumw2()
                MtwvMtFailWdown.Sumw2()

            # Subtraction of Fail the Pass events that change because of the top SF application
            MtwvMtFailSubPDFup   = TH2F("MtwvMtFailSubPDFup", "mass of tw vs mass of top PDF up - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubPDFdown = TH2F("MtwvMtFailSubPDFdown",   "mass of tw vs mass of top PDF down - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubPDFup.Sumw2()
            MtwvMtFailSubPDFdown.Sumw2()

            MtwvMtFailSubPUup   = TH2F("MtwvMtFailSubPUup", "mass of tw vs mass of top PU up - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubPUdown = TH2F("MtwvMtFailSubPUdown",   "mass of tw vs mass of top PU down - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubPUup.Sumw2()
            MtwvMtFailSubPUdown.Sumw2()

            MtwvMtFailSubTop3up   = TH2F("MtwvMtFailSubTop3up", "mass of tw vs mass of top sf up (merged) - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubTop3down = TH2F("MtwvMtFailSubTop3down",   "mass of tw vs mass of top sf down (merged) - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubTop3up.Sumw2()
            MtwvMtFailSubTop3down.Sumw2()

            MtwvMtFailSubTop2up   = TH2F("MtwvMtFailSubTop2up", "mass of tw vs mass of top sf up (semi-merged) - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubTop2down = TH2F("MtwvMtFailSubTop2down",   "mass of tw vs mass of top sf down (semi-merged) - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubTop2up.Sumw2()
            MtwvMtFailSubTop2down.Sumw2()

            MtwvMtFailSubTop1up   = TH2F("MtwvMtFailSubTop1up", "mass of tw vs mass of top sf up (not merged) - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubTop1down = TH2F("MtwvMtFailSubTop1down",   "mass of tw vs mass of top sf down (not merged) - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubTop1up.Sumw2()
            MtwvMtFailSubTop1down.Sumw2()

            MtwvMtFailSubScaleup   = TH2F("MtwvMtFailSubScaleup", "mass of tw vs mass of Q^2 scale up - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubScaledown = TH2F("MtwvMtFailSubScaledown",   "mass of tw vs mass of Q^2 scale down - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubScaleup.Sumw2()
            MtwvMtFailSubScaledown.Sumw2()

            MtwvMtFailSubSjbtagup   = TH2F("MtwvMtFailSubSjbtagup", "mass of tw vs mass of sjbtag sf up - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubSjbtagdown = TH2F("MtwvMtFailSubSjbtagdown",   "mass of tw vs mass of sjbtag sf down - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubSjbtagup.Sumw2()
            MtwvMtFailSubSjbtagdown.Sumw2()

            MtwvMtFailSubTrigup   = TH2F("MtwvMtFailSubTrigup", "mass of tw vs mass of top trig up - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubTrigdown = TH2F("MtwvMtFailSubTrigdown",   "mass of tw vs mass of top trig up - FailSub", 60, 50, 350, 70, 500, 4000 )
            MtwvMtFailSubTrigup.Sumw2()
            MtwvMtFailSubTrigdown.Sumw2()

            if prefcorr:
                MtwvMtFailSubPrefireup = TH2F("MtwvMtFailSubPrefireup", "mass of tw vs mass of top prefire up - Pass", 60, 50, 350, 70, 500, 4000 )
                MtwvMtFailSubPrefiredown = TH2F("MtwvMtFailSubPrefiredown",   "mass of tw vs mass of top prefire down - Pass", 60, 50, 350, 70, 500, 4000 )
                MtwvMtFailSubPrefireup.Sumw2()
                MtwvMtFailSubPrefiredown.Sumw2()
            
            if 'ttbar' in options.set:
                MtwvMtFailSubTptAlphaup    = TH2F("MtwvMtFailSubTptAlphaup",  "mass of tw vs mass of top top pt reweight alpha up - FailSub",  60, 50, 350, 70, 500, 4000 )
                MtwvMtFailSubTptAlphadown  = TH2F("MtwvMtFailSubTptAlphadown",    "mass of tw vs mass of top top pt reweight alpha down - FailSub",60, 50, 350, 70, 500, 4000 )
                MtwvMtFailSubTptAlphaup.Sumw2()
                MtwvMtFailSubTptAlphadown.Sumw2()

                MtwvMtFailSubTptBetaup    = TH2F("MtwvMtFailSubTptBetaup",  "mass of tw vs mass of top top pt reweight beta up - FailSub",  60, 50, 350, 70, 500, 4000 )
                MtwvMtFailSubTptBetadown  = TH2F("MtwvMtFailSubTptBetadown",    "mass of tw vs mass of top top pt reweight beta down - FailSub",60, 50, 350, 70, 500, 4000 )
                MtwvMtFailSubTptBetaup.Sumw2()
                MtwvMtFailSubTptBetadown.Sumw2()

            if ('tW' in options.set or 'signal' in options.set or 'ttbar' in options.set) and not wIsTtagged:
                MtwvMtFailSubExtrapUp = TH2F("MtwvMtFailSubExtrapUp", "mass of tw vs mass of top extrapolation uncertainty up - FailSub", 60, 50, 350, 70, 500, 4000)
                MtwvMtFailSubExtrapDown = TH2F("MtwvMtFailSubExtrapDown", "mass of tw vs mass of top extrapolation uncertainty down - FailSub", 60, 50, 350, 70, 500, 4000)
                MtwvMtFailSubExtrapUp.Sumw2()
                MtwvMtFailSubExtrapDown.Sumw2()

                MtwvMtFailSubWup      = TH2F("MtwvMtFailSubWup",    "mass of tw vs mass of top w tag SF up - FailSub", 60, 50, 350, 70, 500, 4000 )
                MtwvMtFailSubWdown    = TH2F("MtwvMtFailSubWdown",  "mass of tw vs mass of top w tag SF down - FailSub",   60, 50, 350, 70, 500, 4000 )
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

        Mtw_cut1    = TH1F("Mtw_cut1",  "mass of tw after pt cuts and dy cuts", 70, 500, 4000)
        Mtw_cut2    = TH1F("Mtw_cut2",  "mass of tw after tau21 cut", 70, 500, 4000)
        Mtw_cut3    = TH1F("Mtw_cut3",  "mass of tw after wmass cut", 70, 500, 4000)
        Mtw_cut4    = TH1F("Mtw_cut4", "mass of tw after tau32 cut", 70, 500, 4000)
        Mtw_cut5    = TH1F("Mtw_cut5", "mass of tw after sjbtag cut", 70, 500, 4000)
        Mtw_cut1.Sumw2()
        Mtw_cut2.Sumw2()
        Mtw_cut3.Sumw2()
        Mtw_cut4.Sumw2()
        Mtw_cut5.Sumw2()


    dumbTagPass = TH2F("dumbTagPass",     "mass of tw vs mass of top - Pass random tag", 60, 50, 350, 70, 500, 4000 )
    dumbTagFail = TH2F("dumbTagFail",     "mass of tw vs mass of top - Fail random tag", 60, 50, 350, 70, 500, 4000 )

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
        'PtreweightAlpha':array.array('d',[1.0]),
        'PtreweightBeta':array.array('d',[1.0]),
        'Extrap':array.array('d',[1.0]),
        'Total':array.array('d',[1.0]),
        'MtopW':array.array('d',[1.0]),
        'Mtop':array.array('d',[1.0]),
        'Ht':array.array('d',[1.0])
    }
    weightTree = Make_Trees(weightArrays,'weights')

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
    if 'data' not in options.set:
        runs_tree = file.Get("Runs")
        nevents_gen = 0
        
        for i in runs_tree:
            try:
                nevents_gen+=i.genEventCount
            except:
                nevents_gen+=i.genEventCount_

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
    tptpair = 0
    notptpair = 0

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

        if len(ak8JetsColl) < 2: continue

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

        # Separate into hemispheres the leading and subleading jets (also does jet ID check)
        Jetsh0,Jetsh1 = Hemispherize(ak8JetsColl)
        if (len(Jetsh1) < 1) or (len(Jetsh0) < 1): continue

        leadingJet = ak8JetsColl[Jetsh0[0]]
        subleadingJet = ak8JetsColl[Jetsh1[0]]

        eta_cut = (Cuts['eta'][0]<abs(leadingJet.eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(subleadingJet.eta)<Cuts['eta'][1])

        if eta_cut:
            doneAlready = False
            # For masses, nom has JECs and raw does not.
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
                        "SDmass":leadingJet.msoftdrop_nom, # Does not have PUPPI SD mass correction
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
                        "SDmass":subleadingJet.msoftdrop_nom,#raw if not wIsTtagged else subleadingJet.msoftdrop_nom, # Add PUPPI SD mass correction if not a top
                        "subJetIdx1":subleadingJet.subJetIdx1,
                        "subJetIdx2":subleadingJet.subJetIdx2,
                        "JEScorr":1.0
                    }

                    if 'data' not in options.set:
                        if options.JES != 'nom':
                            tVals['JEScorr'] = getattr(leadingJet,'corr_JESTotal'+JES)
                            wVals['JEScorr'] = getattr(subleadingJet,'corr_JESTotal'+JES)
                        tVals['JERcorr'] = getattr(leadingJet,'corr_JER'+JER)
                        wVals["JERcorr"] = getattr(subleadingJet,'corr_JER'+JER)

                        if options.region != 'ttbar':
                            wVals["JMScorr"] = getattr(subleadingJet,'corr_JMS'+JMS)
                            wVals["JMRcorr"] = getattr(subleadingJet,'msoftdrop_corr_JMR'+JMR)

                    #if options.region != 'ttbar':
                    #    wVals['PSDMC'] = getattr(subleadingJet,'msoftdrop_corr_PUPPI')

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
                        "SDmass":leadingJet.msoftdrop_nom,# if not wIsTtagged else leadingJet.msoftdrop_nom, # Add PUPPI SD mass correction if W
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
                        "SDmass":subleadingJet.msoftdrop_nom, # Does not have PUPPI SD mass correction
                        "subJetIdx1":subleadingJet.subJetIdx1,
                        "subJetIdx2":subleadingJet.subJetIdx2,
                        "JEScorr":1.0
                    }

                    if 'data' not in options.set:
                        if options.JES != 'nom':
                            wVals['JEScorr'] = getattr(leadingJet,'corr_JESTotal'+JES)
                            tVals['JEScorr'] = getattr(subleadingJet,'corr_JESTotal'+JES)
                        wVals['JERcorr'] = getattr(leadingJet,'corr_JER'+JER)
                        tVals["JERcorr"] = getattr(subleadingJet,'corr_JER'+JER)

                        if options.region != 'ttbar':
                            wVals["JMScorr"] = getattr(leadingJet,'corr_JMS'+JMS)
                            wVals["JMRcorr"] = getattr(leadingJet,'msoftdrop_corr_JMR'+JMR)

                    #if options.region != 'ttbar':
                    #    wVals["PSDMC"] = getattr(leadingJet,'msoftdrop_corr_PUPPI')

                elif hemis == 'hemis1' and doneAlready == True:
                    continue
                
                # Apply jet corrections
                #if not wIsTtagged: wVals['SDmass'] = wVals['SDmass']*wVals['PSDMC']
                if 'data' not in options.set:
                    wVals['pt'] = wVals['pt']*wVals['JEScorr']*wVals['JERcorr']
                    tVals['pt'] = tVals['pt']*tVals['JEScorr']*tVals['JERcorr']
                    tVals['SDmass'] = tVals['SDmass']*tVals['JEScorr']*tVals['JERcorr']
                    if not wIsTtagged:
                        wVals['SDmass'] = wVals['SDmass']*wVals['JMScorr']*wVals['JMRcorr']*wVals['JEScorr']*wVals['JERcorr']
                    else:
                        wVals['SDmass'] = wVals['SDmass']*wVals['JEScorr']*wVals['JERcorr']
                    

                # Make the lorentz vectors
                tjet = ROOT.Math.PtEtaPhiMVector(tVals["pt"],tVals["eta"],tVals["phi"],tVals["SDmass"])
                wjet = ROOT.Math.PtEtaPhiMVector(wVals["pt"],wVals["eta"],wVals["phi"],wVals["SDmass"])

                ht = tjet.Pt() + wjet.Pt()
                MtopW = (tjet+wjet).M()
                
                # Make and get all cuts
                MtopW_cut = MtopW > 1000.
                ht_cut = True#ht > 1000.
                Mtop_cut = tVals["SDmass"] > 50.0
                if wIsTtagged: Mtop_cut = Mtop_cut and wVals["SDmass"] > 50.0
                dy_val = abs(tjet.Rapidity()-wjet.Rapidity())
                wpt_cut = Cuts['wpt'][0]<wjet.Pt()<Cuts['wpt'][1]
                tpt_cut = Cuts['tpt'][0]<tjet.Pt()<Cuts['tpt'][1]
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
                    preselection = wpt_cut and tpt_cut and dy_cut and MtopW_cut and Mtop_cut and wmass_cut and tau21_cut and ht_cut
                
                    if wpt_cut and tpt_cut and dy_cut and MtopW_cut and tau21_cut and ht_cut:
                        Mw.Fill(wVals['SDmass'])

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
                        
                    # INDENT FIXED
                    w_sjbtag_cut = Cuts['deepbtag'][0]<= w_btagval<Cuts['deepbtag'][1]
                    preselection = wpt_cut and tpt_cut and dy_cut and MtopW_cut and Mtop_cut and wmass_cut and w_sjbtag_cut and w_tau32_cut and ht_cut

                    if runOthers and checkingFirstHemi:
                        if wpt_cut and tpt_cut and dy_cut:
                            Mtw_cut1.Fill(MtopW,norm_weight)
                            if w_sjbtag_cut and w_tau32_cut:
                                Mtw_cut2.Fill(MtopW,norm_weight)
                                if wmass_cut:
                                    Mtw_cut3.Fill(MtopW,norm_weight)

                if preselection: 
                    doneAlready = True
                    # lepveto, lepW_veto, lepT_veto, lepT_candidates, lepW_candidate_es, lepW_candidate_mus = LeptonVeto(event,options.year,lepSFfile)

                    # Get GenParticles for use below
                    if 'data' not in options.set:
                        GenParticles = Collection(event,'GenPart')
               
                    # if not lepveto:
                    #     inLepSel += 1
                    #     # continue
                    # else:
                    #     notInLepSel += 1

                    ###############################
                    # Weighting and Uncertainties #
                    ###############################

                    # Initialize event weight
                    weights = { 'PDF':{},
                                'Pileup':{},
                                'Topsf':{},
                                'TopsfPresel':{'nom':1,'up':1,'down':1},
                                'Q2':{},
                                # 'sjbsf':{},
                                'Wsf':{},
                                'Trigger':{},
                                'PtreweightAlpha':{},
                                'PtreweightBeta':{},
                                'Extrap':{}}
                    for k in weightArrays.keys(): weightArrays[k][0] = 1.0
                    
                    if 'data' not in options.set:
                        # PDF weight
                        if runOthers:
                            if 'signal' in options.set: weights['PDF']['up'], weights['PDF']['down'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),pdf_norm)
                            else: weights['PDF']['up'], weights['PDF']['down'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'))
                        
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
                            elif options.region == 'sideband': Wpurity = 'LP'
                                # if options.year == '16': Wpurity = 'LP'
                                # elif options.year != '16' and (Cuts['tau21LP'][0] < tau21val < Cuts['tau21LP'][1]): Wpurity = 'LP'
                                # else: Wpurity = False
                            else: Wpurity = False

                            if 'ttbar' in options.set and runOthers:
                                dummyvar,top_merged_particles = SFT_Lookup(wjet,ttagsffile,GenParticles,'tight')
                                wFakes.Fill(top_merged_particles+1)

                            # W matching
                            if ('tW' in options.set or 'signal' in options.set or 'ttbar' in options.set):#'tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                                if 'ttbar' in options.set: isTtbar = True
                                else: isTtbar = False
                                if WJetMatching(wjet,GenParticles,ttbar=isTtbar) and Wpurity != False:
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
                                extrap = ExtrapUncert_Lookup(wjet.Pt(),Wpurity,options.year)
                                weights['Extrap']['up'] = 1+extrap
                                weights['Extrap']['down'] = 1-extrap

                        # Trigger weight applied
                        if tname != 'none':
                            trig_weights = Trigger_Lookup( MtopW , TrigPlot1 )
                            weights['Trigger']['nom'] = trig_weights[0]
                            weights['Trigger']['up'] = trig_weights[1]
                            weights['Trigger']['down'] = trig_weights[2]

                        # Top pt reweighting
                        if options.ptreweight == "on" and 'ttbar' in options.set:
                            tpt_weights,pair_exists = PTW_Lookup(GenParticles,[tjet,wjet])
                            weights['PtreweightAlpha']['nom'] = tpt_weights['nom']
                            weights['PtreweightAlpha']['up'] = tpt_weights['alpha_up']
                            weights['PtreweightAlpha']['down'] = tpt_weights['alpha_down']
                            weights['PtreweightBeta']['up'] = tpt_weights['beta_up']
                            weights['PtreweightBeta']['down'] = tpt_weights['beta_down']
                            badtptreweight = exp(0.0615-0.0005*-100)        
                            if pair_exists: tptpair +=1
                            else: notptpair +=1

                        # Trigger pre-fire
                        if prefcorr:
                            # prefire_weights = prefire_correction.analyze(event)
                            weights['Prefire'] = {
                                'nom': inTree.readBranch('PrefireWeight'),
                                'up': inTree.readBranch('PrefireWeight_Up'),
                                'down': inTree.readBranch('PrefireWeight_Down')
                            }

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
                        top_merging_status = 0 # needs to be assigned to something but shouldn't matter since we don't use the template for anything
                        weights['Topsf']['nom'] = 1.0
                        weights['Topsf']['up'] =  1.0
                        weights['Topsf']['down'] = 1.0
                        # weights['sjbsf']['nom'] = 1.0
                        # weights['sjbsf']['up'] = 1.0
                        # weights['sjbsf']['down'] = 1.0

                    if wIsTtagged:
                        # Top tagging tau32+sjbtag scale factor 
                        if "QCD" not in options.set and 'data' not in options.set:
                            sftw,wtop_merging_status = SFT_Lookup(wjet,ttagsffile_wmass,GenParticles,'tight')#(wjet, ttagsffile, GenParticles, options.tau32)#, GenParticles)
                            weights['TopsfPresel'] = {}
                            weights['TopsfPresel']['nom'] = sftw[0]
                            weights['TopsfPresel']['up'] = sftw[1]
                            weights['TopsfPresel']['down'] = sftw[2]

                            # Subjet b tagging scale factor
                            # weights['sjbsf']['nom'] *= reader.eval_auto_bounds('central', 0, abs(wVals['eta']), wVals['pt'])
                            # weights['sjbsf']['up'] *= reader.eval_auto_bounds('up', 0, abs(wVals['eta']), wVals['pt'])
                            # weights['sjbsf']['down'] *= reader.eval_auto_bounds('down', 0, abs(wVals['eta']), wVals['pt'])

                        else:
                            wtop_merging_status = 0 # needs to be assigned to something but shouldn't matter since we don't use the template for anything
                            weights['TopsfPresel'] = {}
                            weights['TopsfPresel']['nom'] = 1.0
                            weights['TopsfPresel']['up'] =  1.0
                            weights['TopsfPresel']['down'] = 1.0
                            # weights['sjbsf']['nom'] = 1.0
                            # weights['sjbsf']['up'] = 1.0
                            # weights['sjbsf']['down'] = 1.0

                    if 'signal' in options.set:
                        chains,tree = AllHadIdentifier(GenParticles,count)

                        if chains['Hadronic W'] != False and chains['Hadronic top'] != False:
                            sigDecay.Fill(1)
                            if chains['Leptonic b'] != False:
                                sigDecay.Fill(4)
                                # if lepveto: sigDecay.Fill(6)
                                # else: sigDecay.Fill(5)
                            # if lepveto: 
                            #     sigDecay.Fill(10)
                            #     # if chains['Leptonic b'] == False:
                            #     #     tree.PrintTree(count,options=['pdgId','status','pt'])
                            # else: 
                            #     if lepT_veto and lepW_veto:
                            #         sigDecay.Fill(7)
                            #     elif lepT_veto and not lepW_veto:
                            #         sigDecay.Fill(8)
                            #     elif not lepT_veto and lepW_veto:
                            #         sigDecay.Fill(9)

                        elif chains['Hadronic W'] != False and chains['Leptonic top'] != False:
                            sigDecay.Fill(3)
                        elif chains['Hadronic top'] != False and chains['Leptonic W'] != False:
                            sigDecay.Fill(2)
                        else: sigDecay.Fill(11)

                    # Top sf - tricky!
                    sft_pass_strings = SFT_Variation(top_merging_status,wIsTtagged,-1 if not wIsTtagged else wtop_merging_status)
                    sft_sub_strings = SFT_Variation(-1,wIsTtagged,-1 if not wIsTtagged else wtop_merging_status)

                    if top_tag:
                        MtwvMtPass.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 
                        if 'ttbar' in options.set: MtwvMtPassBadTpt.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['PtreweightAlpha'])*badtptreweight)
                        MtwvMtPassNotrig.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Trigger']))
                        MtwvMtFailSub.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                        if runOthers:
                            if 'data' not in options.set:
                                ########
                                # Pass #
                                ########
                                MtwvMtPassPDFup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_up'))
                                MtwvMtPassPDFdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_down'))

                                MtwvMtPassPUup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_up'))
                                MtwvMtPassPUdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_down'))

                                MtwvMtPassTop1up.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_pass_strings[1]['up']))
                                MtwvMtPassTop1down.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_pass_strings[1]['down']))
                                MtwvMtPassTop2up.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_pass_strings[2]['up']))
                                MtwvMtPassTop2down.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_pass_strings[2]['down']))
                                MtwvMtPassTop3up.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_pass_strings[3]['up']))
                                MtwvMtPassTop3down.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_pass_strings[3]['down']))
                                
                                MtwvMtPassScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up'))
                                MtwvMtPassScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down'))

                                MtwvMtPassTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up'))
                                MtwvMtPassTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down'))

                                if prefcorr:
                                    MtwvMtPassPrefireup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Prefire_up'))
                                    MtwvMtPassPrefiredown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Prefire_down'))

                                ############
                                # Fail sub #
                                ############
                                MtwvMtFailSubPDFup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                MtwvMtFailSubPDFdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                MtwvMtFailSubPUup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                MtwvMtFailSubPUdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                sub1up=sub2up=sub3up=sub1down=sub2down=sub3down='nom'
                                if top_merging_status == 3: sub3up,sub3down = 'up','down'
                                if top_merging_status == 2: sub2up,sub2down = 'up','down'
                                if top_merging_status == 1: sub1up,sub1down = 'up','down'
                                MtwvMtFailSubTop1up.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[1]['up'],drop=['Topsf'])*(weights['Topsf'][sub1up]-1))
                                MtwvMtFailSubTop1down.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[1]['down'],drop=['Topsf'])*(weights['Topsf'][sub1down]-1))
                                MtwvMtFailSubTop2up.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[2]['up'],drop=['Topsf'])*(weights['Topsf'][sub2up]-1))
                                MtwvMtFailSubTop2down.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[2]['down'],drop=['Topsf'])*(weights['Topsf'][sub2down]-1))
                                MtwvMtFailSubTop3up.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[3]['up'],drop=['Topsf'])*(weights['Topsf'][sub3up]-1))
                                MtwvMtFailSubTop3down.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[3]['down'],drop=['Topsf'])*(weights['Topsf'][sub3down]-1))

                                MtwvMtFailSubScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                MtwvMtFailSubScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                MtwvMtFailSubTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                MtwvMtFailSubTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                if prefcorr:
                                    MtwvMtFailSubPrefireup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Prefire_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                    MtwvMtFailSubPrefiredown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Prefire_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                if ('tW' in options.set or 'signal' in options.set or 'ttbar' in options.set) and not wIsTtagged:
                                    MtwvMtPassWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up')) 
                                    MtwvMtPassWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down'))

                                    MtwvMtFailSubWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                    MtwvMtFailSubWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                    MtwvMtPassExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up'))
                                    MtwvMtPassExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down'))

                                    MtwvMtFailSubExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                    MtwvMtFailSubExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                                if 'ttbar' in options.set:
                                    MtwvMtPassTptAlphaup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightAlpha_up'))
                                    MtwvMtPassTptAlphadown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightAlpha_down')) 
                                    MtwvMtPassTptBetaup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightBeta_up',drop=['PtreweightAlpha']))
                                    MtwvMtPassTptBetadown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightBeta_down',drop=['PtreweightAlpha'])) 

                                    MtwvMtFailSubTptAlphaup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightAlpha_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                    MtwvMtFailSubTptAlphadown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightAlpha_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                                    MtwvMtFailSubTptBetaup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightBeta_up',drop=['Topsf','PtreweightAlpha'])*(weights['Topsf']['nom']-1))
                                    MtwvMtFailSubTptBetadown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightBeta_down',drop=['Topsf','PtreweightAlpha'])*(weights['Topsf']['nom']-1)) 

                    else:
                        ########
                        # Fail #
                        ########
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

                            MtwvMtFailTop1up.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[1]['up'],drop=['Topsf']))
                            MtwvMtFailTop1down.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[1]['down'],drop=['Topsf']))
                            MtwvMtFailTop2up.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[2]['up'],drop=['Topsf']))
                            MtwvMtFailTop2down.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[2]['down'],drop=['Topsf']))
                            MtwvMtFailTop3up.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[3]['up'],drop=['Topsf']))
                            MtwvMtFailTop3down.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,sft_sub_strings[3]['down'],drop=['Topsf']))
                            
                            MtwvMtFailScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up',drop=['Topsf']))
                            MtwvMtFailScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down',drop=['Topsf']))

                            MtwvMtFailTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up',drop=['Topsf']))
                            MtwvMtFailTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down',drop=['Topsf']))
                            
                            if prefcorr:
                                MtwvMtFailPrefireup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Prefire_up',drop=['Topsf']))
                                MtwvMtFailPrefiredown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Prefire_down',drop=['Topsf']))

                            if ('tW' in options.set or 'signal' in options.set or 'ttbar' in options.set) and not wIsTtagged:
                                MtwvMtFailWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up',drop=['Topsf'])) 
                                MtwvMtFailWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down',drop=['Topsf']))

                                MtwvMtFailExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up',drop=['Topsf']))
                                MtwvMtFailExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down',drop=['Topsf']))

                            if 'ttbar' in options.set:
                                MtwvMtFailTptAlphaup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightAlpha_up',drop=['Topsf']))
                                MtwvMtFailTptAlphadown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightAlpha_down',drop=['Topsf'])) 
                                MtwvMtFailTptBetaup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightBeta_up',drop=['Topsf','PtreweightAlpha']))
                                MtwvMtFailTptBetadown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PtreweightBeta_down',drop=['Topsf','PtreweightAlpha'])) 

                    # Fill weight tree
                    for k in weightArrays.keys():
                        if k not in ['Total','MtopW','Mtop','Ht'] and 'nom' in weights[k].keys(): weightArrays[k][0] = weights[k]['nom']
                        elif k not in ['Total','MtopW','Mtop','Ht'] and 'nom' not in weights[k].keys(): weightArrays[k][0] = 1.0
                        elif k == 'Total':
                            weightArrays[k][0] = 1.0
                            for w in weights.keys(): 
                                if 'nom' in weights[w]: weightArrays[k][0] *= weights[w]['nom']
                        elif k == 'MtopW':
                            weightArrays[k][0] = MtopW
                        elif k == 'Mtop':
                            weightArrays[k][0] = tVals["SDmass"]
                        elif k == 'Ht':
                            weightArrays[k][0] = ht
                    weightTree.Fill()
                
    # lepVetoCount.SetBinContent(1,inLepSel)
    # lepVetoCount.SetBinContent(2,notInLepSel)
    wmatchCount.SetBinContent(1,wmatchcount)
    nev.SetBinContent(1,count)          
    end = time.time()
    print '\n'
    print str((end-start)/60.) + ' min'

    print "Pair found: %s, No pair found: %s" % (tptpair,notptpair)

    # Correct the failing distribution from the top tag sf application in pass (subtract events that were gained/lost in pass)
    MtwvMtFail.Add(MtwvMtFailSub,-1)
    if runOthers and 'data' not in options.set:
        MtwvMtFailPDFup.Add(MtwvMtFailSubPDFup,-1)
        MtwvMtFailPDFdown.Add(MtwvMtFailSubPDFdown,-1)
        MtwvMtFailPUup.Add(MtwvMtFailSubPUup,-1)
        MtwvMtFailPUdown.Add(MtwvMtFailSubPUdown,-1)
        MtwvMtFailTop3up.Add(MtwvMtFailSubTop3up,-1)
        MtwvMtFailTop3down.Add(MtwvMtFailSubTop3down,-1)
        MtwvMtFailTop2up.Add(MtwvMtFailSubTop2up,-1)
        MtwvMtFailTop2down.Add(MtwvMtFailSubTop2down,-1)
        MtwvMtFailTop1up.Add(MtwvMtFailSubTop1up,-1)
        MtwvMtFailTop1down.Add(MtwvMtFailSubTop1down,-1)

        MtwvMtFailScaleup.Add(MtwvMtFailSubScaleup,-1)
        MtwvMtFailScaledown.Add(MtwvMtFailSubScaledown,-1)
        MtwvMtFailTrigup.Add(MtwvMtFailSubTrigup,-1)
        MtwvMtFailTrigdown.Add(MtwvMtFailSubTrigdown,-1)
        if prefcorr:
            MtwvMtFailPrefireup.Add(MtwvMtFailSubPrefireup,-1)
            MtwvMtFailPrefiredown.Add(MtwvMtFailSubPrefiredown,-1)
        if ('tW' in options.set or 'signal' in options.set or 'ttbar' in options.set) and not wIsTtagged:
            MtwvMtFailWup.Add(MtwvMtFailSubWup,-1)
            MtwvMtFailWdown.Add(MtwvMtFailSubWdown,-1)
            MtwvMtFailExtrapUp.Add(MtwvMtFailSubExtrapUp,-1)
            MtwvMtFailExtrapDown.Add(MtwvMtFailSubExtrapDown,-1)
        if 'ttbar' in options.set:
            MtwvMtFailTptAlphaup.Add(MtwvMtFailSubTptAlphaup,-1)
            MtwvMtFailTptAlphadown.Add(MtwvMtFailSubTptAlphadown,-1)
            MtwvMtFailTptBetaup.Add(MtwvMtFailSubTptBetaup,-1)
            MtwvMtFailTptBetadown.Add(MtwvMtFailSubTptBetadown,-1)


    f.cd()
    f.Write()
    f.Close()



    
