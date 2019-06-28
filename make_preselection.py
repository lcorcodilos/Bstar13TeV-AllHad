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
    parser.add_option('-d', '--deepak8', metavar='F', type='string', action='store',
                    default   =   'off',
                    dest      =   'deepak8',
                    help      =   'Cut strength (off, (MD)loose, (MD)medium, (MD)tight, (MD)very_tight)')
    parser.add_option('-t', '--tau32', metavar='F', type='string', action='store',
                    default   =   'off',
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
                    default   =   'nominal',
                    dest      =   'JES',
                    help      =   'nominal, up, or down')
    parser.add_option('-R', '--JER', metavar='F', type='string', action='store',
                    default   =   'nominal',
                    dest      =   'JER',
                    help      =   'nominal, up, or down')
    parser.add_option('-a', '--JMS', metavar='F', type='string', action='store',
                    default   =   'nominal',
                    dest      =   'JMS',
                    help      =   'nominal, up, or down')
    parser.add_option('-b', '--JMR', metavar='F', type='string', action='store',
                    default   =   'nominal',
                    dest      =   'JMR',
                    help      =   'nominal, up, or down')
    parser.add_option('-u', '--ptreweight', metavar='F', type='string', action='store',
                    default   =   'on',
                    dest      =   'ptreweight',
                    help      =   'on or off')
    parser.add_option('-n', '--num', metavar='F', type='string', action='store',
                    default   =   'all',
                    dest      =   'num',
                    help      =   'job number')
    parser.add_option('-j', '--jobs', metavar='F', type='string', action='store',
                    default   =   '1',
                    dest      =   'jobs',
                    help      =   'number of jobs')
    parser.add_option('-q', '--qcdweight', action='store_true',
                    default   =   False,
                    dest      =   'qcdweight',
                    help      =   'Use QCD weighting')


    (options, args) = parser.parse_args()

    # Prep for deepcsv b-tag if deepak8 is off
    # From https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration
    if options.deepak8 == 'off':
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

    if options.region == 'ttbar' and options.deepak8 == 'off':
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
        pretrig_string = 'HLT_IsoMu27'
    btagtype = 'btagDeepB'

    # if tname == 'HLT_PFHT900ORHLT_PFHT800ORHLT_AK8PFJet450':
    #     tnamestr = 'nominal'
    # else:
    #     tnamestr = tname

    # JECs
    runOthers = True
    if options.set == 'data':
        JEC_name = ''
        JMC_name = ''
    else:
        JEC_name = '_nom'
        JMC_name = '_nom'
    mod = ''
    if options.JES!='nominal':
        mod = '_JES' + '_' + options.JES
        JMC_name = '_jesTotal'+options.JES.capitalize()
        JEC_name = '_jesTotal'+options.JES.capitalize()
        runOthers = False
    if options.JER!='nominal':
        mod = '_JER' + '_' + options.JER
        JMC_name = '_nom'
        JEC_name = '_jer'+options.JER.capitalize()
        runOthers = False
    if options.JMS!='nominal':
        mod = '_JMS' + '_' + options.JMS
        JMC_name = '_jms'+options.JMS.capitalize()
        JEC_name = '_nom'
        runOthers = False
    if options.JMR!='nominal':
        mod = '_JMR' + '_' + options.JMR
        JMC_name = '_jmr'+options.JMR.capitalize()
        JEC_name = '_nom'
        runOthers = False

    # if options.year == '16':
    #     jetcoll = "FatJet"#"CustomAK8Puppi"
    # elif options.year == '17':
    jetcoll = "FatJet"

    print 'Jet collection is '+jetcoll

    if options.deepak8 == 'off' and options.tau32 == 'off':
        print 'ERROR: tau32 and deepak8 both off. Please turn one on. Quitting...'
        quit()
    elif options.deepak8 != 'off':
        ttagstring = 'DAK8'+options.deepak8+qcdweight_string
    elif options.tau32 != 'off':
        ttagstring = 'tau32'+options.tau32+qcdweight_string

    ######################################
    # Setup grid production if necessary #
    ######################################

    #If running on the grid we access the script within a tarred directory
    di = ""
    # if options.grid == 'on':
    #     di = "tardir/"
    #     sys.path.insert(0, 'tardir/')

    # gROOT.Macro(di+"rootlogon.C")

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
    if options.set != 'data':
        
        print "Triggerweight_data"+options.year+"_pre_"+pretrig_string+".root"
        print 'TriggerWeight_'+tname+'_Ht'
        TrigFile = TFile.Open("trigger/Triggerweight_data"+options.year+"_pre_"+pretrig_string+".root")
        TrigPlot = TrigFile.Get('TriggerWeight_'+tname+'_Ht')
        TrigPlot1 = TrigPlot.Clone()
        
        # PileFile = TFile.Open("pileup/PileUp_Ratio_ttbar"+options.year+".root")
        # PilePlots = {
        #     "nom": PileFile.Get("Pileup_Ratio"),
        #     "up": PileFile.Get("Pileup_Ratio_up"),
        #     "down": PileFile.Get("Pileup_Ratio_down")}
        
        if options.deepak8 != 'off':
            if 'MD' in options.deepak8:
                ttagsfPlots = {
                    "nom": TFile.Open('TopSFs.root').Get('fj_decorr_nn_top'+options.deepak8[2:]+'syst'),
                    "up": TFile.Open('TopSFs.root').Get('fj_decorr_nn_top'+options.deepak8[2:]+'syst_up'),
                    "down": TFile.Open('TopSFs.root').Get('fj_decorr_nn_top'+options.deepak8[2:]+'syst_down')
                }
            else:
                ttagsfPlots = {
                    "nom": TFile.Open('TopSFs.root').Get('fj_nn_top'+options.deepak8+'syst'),
                    "up": TFile.Open('TopSFs.root').Get('fj_nn_top'+options.deepak8+'syst_up'),
                    "down": TFile.Open('TopSFs.root').Get('fj_nn_top'+options.deepak8+'syst_down')
                }

        else:
            ttagsffile = TFile.Open('SFs/20'+tempyear+'TopTaggingScaleFactors_NoMassCut.root')

    puppiCorrFile = TFile.Open("SFs/puppiCorr.root")
    puppiGenCorr = puppiCorrFile.Get('puppiJECcorr_gen')
    puppiRecoCorr_cen = puppiCorrFile.Get("puppiJECcorr_reco_0eta1v3")
    puppiRecoCorr_for = puppiCorrFile.Get("puppiJECcorr_reco_1v3eta2v5")


    #############################
    # Make new file for storage #
    #############################
    if jobs!=1:
        f = TFile( "TWpreselection"+options.year+"_"+options.set+"_job"+options.num+"of"+options.jobs+"_"+ttagstring+mod+'_'+options.region+".root", "recreate" )
    else:
        f = TFile( "TWpreselection"+options.year+"_"+options.set+"_"+ttagstring+mod+'_'+options.region+".root", "recreate" )
    f.cd()

    
    ###################
    # Book histograms #
    ###################
    MtwvMtPass     = TH2F("MtwvMtPass",     "mass of tw vs mass of top - Pass", 60, 50, 350, 35, 500, 4000 )
    MtwvMtFail     = TH2F("MtwvMtFail",     "mass of tw vs mass of top - Fail", 60, 50, 350, 35, 500, 4000 )
    MtwvMtPass.Sumw2()
    MtwvMtFail.Sumw2()

    nev = TH1F("nev",   "nev",      1, 0, 1 )

    if runOthers == True:
        if options.set != 'data':
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

            MtwvMtPassWup      = TH2F("MtwvMtPassWup",    "mass of tw vs mass of top w tag SF up - Pass", 60, 50, 350, 35, 500, 4000 )
            MtwvMtPassWdown    = TH2F("MtwvMtPassWdown",  "mass of tw vs mass of top w tag SF down - Pass",   60, 50, 350, 35, 500, 4000 )
            MtwvMtPassWup.Sumw2()
            MtwvMtPassWdown.Sumw2()

            MtwvMtPassTptup    = TH2F("MtwvMtPassTptup",  "mass of tw vs mass of top top pt reweight up - Pass",  60, 50, 350, 35, 500, 4000 )
            MtwvMtPassTptdown  = TH2F("MtwvMtPassTptdown",    "mass of tw vs mass of top top pt reweight down - Pass",60, 50, 350, 35, 500, 4000 )
            MtwvMtPassTptup.Sumw2()
            MtwvMtPassTptdown.Sumw2()

            if options.region != 'ttbar':
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

            MtwvMtFailWup      = TH2F("MtwvMtFailWup",    "mass of tw vs mass of top w tag SF up - Fail", 60, 50, 350, 35, 500, 4000 )
            MtwvMtFailWdown    = TH2F("MtwvMtFailWdown",  "mass of tw vs mass of top w tag SF down - Fail",   60, 50, 350, 35, 500, 4000 )
            MtwvMtFailWup.Sumw2()
            MtwvMtFailWdown.Sumw2()

            MtwvMtFailTptup    = TH2F("MtwvMtFailTptup",  "mass of tw vs mass of top top pt reweight up - Fail",  60, 50, 350, 35, 500, 4000 )
            MtwvMtFailTptdown  = TH2F("MtwvMtFailTptdown",    "mass of tw vs mass of top top pt reweight down - Fail",60, 50, 350, 35, 500, 4000 )
            MtwvMtFailTptup.Sumw2()
            MtwvMtFailTptdown.Sumw2()

            if options.region != 'ttbar':
                MtwvMtFailExtrapUp = TH2F("MtwvMtFailExtrapUp", "mass of tw vs mass of top extrapolation uncertainty up - Fail", 60, 50, 350, 35, 500, 4000)
                MtwvMtFailExtrapDown = TH2F("MtwvMtFailExtrapDown", "mass of tw vs mass of top extrapolation uncertainty down - Fail", 60, 50, 350, 35, 500, 4000)
                MtwvMtFailExtrapUp.Sumw2()
                MtwvMtFailExtrapDown.Sumw2()

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

        if options.deepak8 != 'off':
            dak8Top      = TH1F("dak8Top",        "DAK8 Tagging Value for Top",          20, 0.0, 1.0 )
            dak8Top_vs_mt = TH2F('dak8Top_vs_mt', "DAK8 Top vs M_{t}",          30, 50, 350, 20,0,1.0)
            dak8Top_vs_mt_slice1 = TH2F('dak8Top_vs_mt_slice1', "DAK8 Top vs M_{t}, 900 < M_{res} < 1100",          30, 50, 350, 20,0,1.0)
            dak8Top_vs_mt_slice2 = TH2F('dak8Top_vs_mt_slice2', "DAK8 Top vs M_{t}, 1100 < M_{res} < 2400",          30, 50, 350, 20,0,1.0)
            dak8Top_vs_mt_slice3 = TH2F('dak8Top_vs_mt_slice3', "DAK8 Top vs M_{t}, M_{res} >2400",          30, 50, 350, 20,0,1.0)
            

            dak8Top.Sumw2()
            dak8Top_vs_mt.Sumw2()
            dak8Top_vs_mt_slice1.Sumw2()
            dak8Top_vs_mt_slice2.Sumw2()
            dak8Top_vs_mt_slice3.Sumw2()

        else:
            Tau32       = TH1F('Tau32',     'N-subjetiness Top',    20,0,1.0)
            SJbtag      = TH1F('SJbtag',    'Subjet b-tag (DeepCSV)', 20,0,1.0)
            Tau32.Sumw2()
            SJbtag.Sumw2()


    dumbTagPass = TH2F("dumbTagPass",     "mass of tw vs mass of top - Pass random tag", 60, 50, 350, 35, 500, 4000 )
    dumbTagFail = TH2F("dumbTagFail",     "mass of tw vs mass of top - Fail random tag", 60, 50, 350, 35, 500, 4000 )

    dumbTagPass.Sumw2()
    dumbTagFail.Sumw2()


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

    ##############
    # Begin Loop #
    ##############
    start = time.time()
    last_event_time = start
    event_time_sum = 0
    for entry in range(lowBinEdge,highBinEdge):
        count   =   count + 1
        # if count > 1:
            # current_event_time = time.time()
            # event_time_sum += (current_event_time - last_event_time)
        # sys.stdout.write("%i / %i ... \r" % (count,(highBinEdge-lowBinEdge)))
            # sys.stdout.write("Avg time = %f " % (event_time_sum/count) )
        # sys.stdout.flush()
            # last_event_time = current_event_time
        if count % 10000 == 0 :
            print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(highBinEdge-lowBinEdge)) + '% -- '

        # Grab the event
        event = Event(inTree, entry)

        # Apply triggers first
        if options.set == 'data':
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
        if options.deepak8 == 'off':
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
        filters = [inTree.readBranch(f) for f in LoadFilters()]

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
                        "mass":getattr(leadingJet,'mass'),
                        "pt":getattr(leadingJet,'pt'+JEC_name), # This will just have JER and JES corrections
                        "eta":leadingJet.eta,
                        "SDmass":getattr(leadingJet,'msoftdrop'), # Use raw msoftdrop for now for top (eventually need it with just JES applied and JMS and JMR factored out)
                        "subJetIdx1":leadingJet.subJetIdx1,
                        "subJetIdx2":leadingJet.subJetIdx2
                    }
                    wVals = {
                        "tau1":subleadingJet.tau1,
                        "tau2":subleadingJet.tau2,
                        "tau3":subleadingJet.tau3,
                        "phi":subleadingJet.phi,
                        "mass_raw":subleadingJet.mass,
                        "mass":getattr(subleadingJet,'mass'+JMC_name),
                        "pt":getattr(subleadingJet,'pt'+JEC_name), # This will just have JER and JES corrections
                        "eta":subleadingJet.eta,
                        "SDmass":getattr(subleadingJet,'msoftdrop'+JMC_name), # Currently missing PUPPI SD mass correction - has JMS, JMR, JES
                        "subJetIdx1":subleadingJet.subJetIdx1,
                        "subJetIdx2":subleadingJet.subJetIdx2
                    }


                elif hemis == 'hemis1' and doneAlready == False:
                    checkingFirstHemi = False
                    wVals = {
                        "tau1":leadingJet.tau1,
                        "tau2":leadingJet.tau2,
                        "tau3":leadingJet.tau3,
                        "phi":leadingJet.phi,
                        "mass_raw":leadingJet.mass,
                        "mass":getattr(leadingJet,'mass'+JMC_name),
                        "pt":getattr(leadingJet,'pt'+JEC_name), # This will just have JER and JES corrections
                        "eta":leadingJet.eta,
                        "SDmass":getattr(leadingJet,'msoftdrop'+JMC_name), # Never use the raw version from NanoAOD - need to apply correction from getCorrectedPuppiSDmass
                        "subJetIdx1":leadingJet.subJetIdx1,
                        "subJetIdx2":leadingJet.subJetIdx2,
                    }
                    tVals = {
                        "tau1":subleadingJet.tau1,
                        "tau2":subleadingJet.tau2,
                        "tau3":subleadingJet.tau3,
                        "phi":subleadingJet.phi,
                        "mass":getattr(subleadingJet,'mass'),
                        "pt":getattr(subleadingJet,'pt'+JEC_name), # This will just have JER and JES corrections
                        "eta":subleadingJet.eta,
                        "SDmass":getattr(subleadingJet,'msoftdrop'), # Use raw msoftdrop for now for top (eventually need it with just JES applied and JMS and JMR factored out)
                        "subJetIdx1":subleadingJet.subJetIdx1,
                        "subJetIdx2":subleadingJet.subJetIdx2
                    }

                elif hemis == 'hemis1' and doneAlready == True:
                    continue

                # Apply PUPPI+SD mass correction - need to feed raw pt before JECs
                # wjet_noSD = TLorentzVector()
                # wjet_noSD.SetPtEtaPhiM(wVals["pt_raw"],wVals["eta"],wVals["phi"],wVals["mass_raw"])
                # wVals["SDmass"] = getCorrectedPuppiSDmass(wjet_noSD, subJetsColl, puppiGenCorr, puppiRecoCorr_cen, puppiRecoCorr_for)

                # Make the lorentz vectors
                tjet = TLorentzVector()
                tjet.SetPtEtaPhiM(tVals["pt"],tVals["eta"],tVals["phi"],tVals["SDmass"])

                wjet = TLorentzVector()
                wjet.SetPtEtaPhiM(wVals["pt"],wVals["eta"],wVals["phi"],wVals["SDmass"])

                ht = tjet.Perp() + wjet.Perp()
                MtopW = (tjet+wjet).M()
                
                # Make and get all cuts
                dy_val = abs(tjet.Rapidity()-wjet.Rapidity())
                wpt_cut = Cuts['wpt'][0]<wjet.Perp()<Cuts['wpt'][1]
                tpt_cut = Cuts['tpt'][0]<tjet.Perp()<Cuts['tpt'][1]
                dy_cut = Cuts['dy'][0]<=dy_val<Cuts['dy'][1]
                
                # if runOthers:
                #     deltaRap.Fill(dy_val)
                #     Pt1presel.Fill(leadingJet.pt)
                #     Pt2presel.Fill(subleadingJet.pt)

                # Standard W tag
                if options.region != 'ttbar':
                    if wVals['tau1'] > 0:
                        tau21val = wVals['tau2']/wVals['tau1']
                    else:
                        continue

                    tau21_cut =  Cuts['tau21'][0]<=tau21val<Cuts['tau21'][1]

                    wmass_cut = Cuts['wmass'][0]<=wVals["SDmass"]<Cuts['wmass'][1]

                    preselection = wpt_cut and tpt_cut and dy_cut and wmass_cut and tau21_cut
                
                    if wpt_cut and tpt_cut and dy_cut:
                        if runOthers and checkingFirstHemi: Mtw_cut1.Fill(MtopW,norm_weight)
                        if tau21_cut:
                            if runOthers and checkingFirstHemi: Mtw_cut2.Fill(MtopW,norm_weight)
                            if wmass_cut:
                                if runOthers and checkingFirstHemi: Mtw_cut3.Fill(MtopW,norm_weight)

                # If tagging regular W as a top
                else:
                    wmass_cut = Cuts['tmass'][0]<=wVals["SDmass"]<Cuts['tmass'][1]

                    if options.deepak8 != 'off':
                        if 'MD' in options.deepak8:
                            w_cut = Cuts['DeepAK8_top_'+options.deepak8[2:]][0]<=wVals['dak8_top']<Cuts['DeepAK8_top_'+options.deepak8[2:]][1]
                        else:
                            w_cut = Cuts['DeepAK8_top_'+options.deepak8][0]<=wVals['dak8_top']<Cuts['DeepAK8_top_'+options.deepak8][1]
                        preselection = wpt_cut and tpt_cut and dy_cut and wmass_cut and w_cut

                    else:
                        if wVals['tau2'] > 0:
                            w_tau32val = wVals['tau3']/wVals['tau2']
                        else:
                            continue
                        w_tau32_cut = Cuts['tau32tight'][0]<=w_tau32val<Cuts['tau32tight'][1]

                        if (wVals['subJetIdx1'] < 0) or (wVals['subJetIdx1'] >= len(subJetsColl)):
                            if (wVals['subJetIdx2'] < 0) or (wVals['subJetIdx2'] >= len(subJetsColl)):  # if both negative, throw away event
                                continue
                            else:   # if idx2 not negative or bad index, use that
                                w_btagval = getattr(subJetsColl[wVals['subJetIdx2']],btagtype)

                        else:
                            if (wVals['subJetIdx2'] < 0) or (wVals['subJetIdx2'] >= len(subJetsColl)): # if idx1 not negative, use that
                                w_btagval = getattr(subJetsColl[wVals['subJetIdx1']],btagtype)
                            # if both not negative, use largest
                            else:
                                # print str(wVals['subJetIdx1']) +' '+str(len(subJetsColl))
                                # print str(wVals['subJetIdx2']) +' '+str(len(subJetsColl))
                                w_btagval = max(getattr(subJetsColl[wVals['subJetIdx1']],btagtype), getattr(subJetsColl[wVals['subJetIdx2']],btagtype))
                        
                        # if options.year == '16':
                        #     w_sjbtag_cut = Cuts['sjbtag'][0]<= w_btagval<Cuts['sjbtag'][1]
                        # else:
                        w_sjbtag_cut = Cuts['deepbtag'][0]<= w_btagval<Cuts['deepbtag'][1]

                        preselection = wpt_cut and tpt_cut and dy_cut and wmass_cut and w_sjbtag_cut and w_tau32_cut

                    if wpt_cut and tpt_cut and dy_cut:
                        if runOthers and checkingFirstHemi: Mtw_cut1.Fill(MtopW,norm_weight)
                        if w_sjbtag_cut and w_tau32_cut:
                            if runOthers and checkingFirstHemi: Mtw_cut2.Fill(MtopW,norm_weight)
                            if wmass_cut:
                                if runOthers and checkingFirstHemi: Mtw_cut3.Fill(MtopW,norm_weight)

                if preselection: 
                    doneAlready = True
                    # Get GenParticles for use below
                    if options.set != 'data':
                        GenParticles = Collection(event,'GenPart')

                    ###############################
                    # Weighting and Uncertainties #
                    ###############################

                    # Initialize event weight
                    weights = { 'PDF':{},
                                'Pileup':{},
                                'Topsf':{},
                                'Q2':{},
                                'sjbsf':{},
                                'Wsf':{},
                                'Trigger':{},
                                'Ptreweight':{},
                                'Extrap':{}}

                    
                    if options.set!="data":
                        # PDF weight
                        weights['PDF']['up'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'up')
                        weights['PDF']['down'] = PDF_Lookup(inTree.readBranch('LHEPdfWeight'),'down')

                        # Q2 Scale
                        weights['Q2']['up'] = inTree.readBranch('LHEScaleWeight')[8]
                        weights['Q2']['down'] = inTree.readBranch('LHEScaleWeight')[0]

                        # Pileup reweighting applied
                        if options.pileup == 'on':
                            weights['Pileup']['nom'] = inTree.readBranch('puWeight')
                            weights['Pileup']['up'] = inTree.readBranch('puWeightUp')
                            weights['Pileup']['down'] = inTree.readBranch('puWeightDown')

                        # Top tagging DAK8 scale factor 
                        if "QCD" not in options.set and options.deepak8 != 'off':
                            sftdeep = SFTdeep_Lookup(tVals['pt'],ttagsfPlots)
                            weights['Topsf']['nom'] = sftdeep[0]
                            weights['Topsf']['up'] = sftdeep[1]
                            weights['Topsf']['down'] = sftdeep[2]
                        # Top tagging tau32+sjbtag scale factor 
                        elif "QCD" not in options.set and options.deepak8 == 'off':
                            sft = SFT_Lookup(tjet,ttagsffile,GenParticles,options.tau32)
                            weights['Topsf']['nom'] = sft[0]
                            weights['Topsf']['up'] = sft[1]
                            weights['Topsf']['down'] = sft[2]

                            # Subjet b tagging scale factor
                            weights['sjbsf']['nom'] = reader.eval_auto_bounds('central', 0, abs(tVals['eta']), tVals['pt'])
                            weights['sjbsf']['up'] = reader.eval_auto_bounds('up', 0, abs(tVals['eta']), tVals['pt'])
                            weights['sjbsf']['down'] = reader.eval_auto_bounds('down', 0, abs(tVals['eta']), tVals['pt'])


                        if wIsTtagged:
                            # Top tagging DAK8 scale factor 
                            if "QCD" not in options.set and options.deepak8 != 'off':
                                sftdeep = SFTdeep_Lookup(wVals['pt'],ttagsfPlots)
                                weights['Topsf']['nom'] *= sftdeep[0]
                                weights['Topsf']['up'] *= sftdeep[1]
                                weights['Topsf']['down'] *= sftdeep[2]
                            # Top tagging tau32+sjbtag scale factor 
                            elif "QCD" not in options.set and options.deepak8 == 'off':
                                sft = SFT_Lookup(wjet,ttagsffile,GenParticles,'tight')#(wjet, ttagsffile, GenParticles, options.tau32)#, GenParticles)
                                weights['Topsf']['nom'] *= sft[0]
                                weights['Topsf']['up'] *= sft[1]
                                weights['Topsf']['down'] *= sft[2]

                                # Subjet b tagging scale factor
                                weights['sjbsf']['nom'] *= reader.eval_auto_bounds('central', 0, abs(wVals['eta']), wVals['pt'])
                                weights['sjbsf']['up'] *= reader.eval_auto_bounds('up', 0, abs(wVals['eta']), wVals['pt'])
                                weights['sjbsf']['down'] *= reader.eval_auto_bounds('down', 0, abs(wVals['eta']), wVals['pt'])

                        if not wIsTtagged:
                            # Determine purity for scale factor
                            if options.region == 'default':
                                Wpurity = 'HP'
                            elif options.region == 'sideband':
                                if options.year == '16':
                                    Wpurity = 'LP'
                                elif options.year != '16' and (Cuts['tau21LP'][0] < tau21val < Cuts['tau21LP'][1]):
                                    Wpurity = 'LP'
                                else:
                                    Wpurity = False
                            else:
                                Wpurity = False

                            # W matching
                            if ('tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                                if WJetMatching(GenParticles) == 1 and Wpurity != False:
                                    wtagsf = Cons['wtagsf_'+Wpurity]
                                    wtagsfsig = Cons['wtagsfsig_'+Wpurity]

                                    weights['Wsf']['nom'] = wtagsf
                                    weights['Wsf']['up'] = (wtagsf + wtagsfsig)
                                    weights['Wsf']['down'] = (wtagsf - wtagsfsig)

                                # Get the extrapolation uncertainty
                                extrap = ExtrapUncert_Lookup(wjet.Perp(),Wpurity,options.year)
                                weights['Extrap']['up'] = 1+extrap
                                weights['Extrap']['down'] = 1-extrap

                        # Trigger weight applied
                        if tname != 'none' and options.set!='data' :
                            weights['Trigger']['nom'] = Trigger_Lookup( ht , TrigPlot1 )[0]
                            weights['Trigger']['up'] = Trigger_Lookup( ht , TrigPlot1 )[1]
                            weights['Trigger']['down'] = Trigger_Lookup( ht , TrigPlot1 )[2]

                            # if weights['Trigger']['nom'] < 1.:
                            #     print 'Nom: %.3f \t Up: %.3f \t Down: %.3f'%(weights['Trigger']['nom'],weights['Trigger']['up'],weights['Trigger']['down'])
                            # if weights['Trigger']['nom'] == 0:
                            #     print ht


                        # Top pt reweighting
                        if options.ptreweight == "on" and options.set.find('ttbar') != -1:
                            weights['Ptreweight']['nom'] = PTW_Lookup(GenParticles)
                            weights['Ptreweight']['up'] = 1.5*PTW_Lookup(GenParticles)
                            weights['Ptreweight']['down'] = 0.5*PTW_Lookup(GenParticles)
                    

                    ####################################
                    # Split into top tag pass and fail #
                    ####################################
                    if options.deepak8 == 'off':
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
                            
                        # if options.year == '16':
                        #     sjbtag_cut = Cuts['sjbtag'][0]<= btagval<Cuts['sjbtag'][1]
                        # else:
                        sjbtag_cut = Cuts['deepbtag'][0]<= btagval<Cuts['deepbtag'][1]
                            

                        top_tag = sjbtag_cut and tau32_cut

                        if tau32_cut:
                            if runOthers and checkingFirstHemi: Mtw_cut4.Fill(MtopW,norm_weight)
                            if sjbtag_cut:
                                if runOthers and checkingFirstHemi: Mtw_cut5.Fill(MtopW,norm_weight)

                    else:
                        if 'MD' in options.deepak8:
                            top_tag = Cuts['DeepAK8_top_'+options.deepak8[2:]][0]<tVals['dak8_top']<Cuts['DeepAK8_top_'+options.deepak8[2:]][1]
                        else:
                            top_tag = Cuts['DeepAK8_top_'+options.deepak8][0]<tVals['dak8_top']<Cuts['DeepAK8_top_'+options.deepak8][1]
    
                    # if runOthers:
                    #     if options.deepak8 != 'off':
                    #         dak8Top.Fill(tVals['dak8_top'],norm_weight*Weightify(weights, 'nominal'))
                    #         dak8Top_vs_mt.Fill(tjet.M(),tVals['dak8_top'],norm_weight*Weightify(weights,'nominal'))
                    #         if MtopW > 900 and MtopW < 1100:
                    #             dak8Top_vs_mt_slice1.Fill(tjet.M(),tVals['dak8_top'],norm_weight*Weightify(weights,'nominal'))
                    #         elif MtopW > 1100 and MtopW < 2400:
                    #             dak8Top_vs_mt_slice2.Fill(tjet.M(),tVals['dak8_top'],norm_weight*Weightify(weights,'nominal'))
                    #         elif MtopW > 2400:
                    #             dak8Top_vs_mt_slice3.Fill(tjet.M(),tVals['dak8_top'],norm_weight*Weightify(weights,'nominal'))

                        # else:
                            # Tau32.Fill(tau32val,norm_weight*Weightify(weights, 'nominal'))
                            # SJbtag.Fill(btagval,norm_weight*Weightify(weights, 'nominal'))

                    if top_tag:

                        MtwvMtPass.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 

                        if runOthers:
                            if options.set != 'data':
                                MtwvMtPassPDFup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_up'))
                                MtwvMtPassPDFdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_down'))

                                MtwvMtPassPUup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_up'))
                                MtwvMtPassPUdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_down'))

                                MtwvMtPassTopup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_up'))
                                MtwvMtPassTopdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_down'))

                                MtwvMtPassScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up'))
                                MtwvMtPassScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down'))

                                MtwvMtPassSjbtagup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_up'))
                                MtwvMtPassSjbtagdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_down'))

                                MtwvMtPassTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up'))
                                MtwvMtPassTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down'))

                                if ('tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                                    MtwvMtPassWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up')) 
                                    MtwvMtPassWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down'))

                                    MtwvMtPassExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up'))
                                    MtwvMtPassExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down'))

                                MtwvMtPassTptup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_up'))
                                MtwvMtPassTptdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_down')) 

                            # EtaTop.Fill(tjet.Eta(),norm_weight*Weightify(weights,'nominal'))
                            # EtaW.Fill(wjet.Eta(),norm_weight*Weightify(weights,'nominal'))
                            
                            # PtTop.Fill(tjet.Perp(),norm_weight*Weightify(weights,'nominal'))
                            # PtW.Fill(wjet.Perp(),norm_weight*Weightify(weights,'nominal'))
                            # PtTopW.Fill((tjet+wjet).Perp(),norm_weight*Weightify(weights,'nominal'))
                            
                            # PhiTop.Fill(tjet.Phi(),norm_weight*Weightify(weights,'nominal'))
                            # PhiW.Fill(wjet.Phi(),norm_weight*Weightify(weights,'nominal'))
                            # dPhi.Fill(abs(tjet.Phi()-wjet.Phi()),norm_weight*Weightify(weights,'nominal'))


                    else:
                        MtwvMtFail.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 

                        if flatTag() < 0.1:
                            dumbTagPass.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 
                        else:
                            dumbTagFail.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'nominal')) 

                        if runOthers and options.set != 'data':
                            MtwvMtFailPDFup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_up'))
                            MtwvMtFailPDFdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'PDF_down'))

                            MtwvMtFailPUup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_up'))
                            MtwvMtFailPUdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Pileup_down'))

                            MtwvMtFailTopup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_up'))
                            MtwvMtFailTopdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Topsf_down'))

                            MtwvMtFailScaleup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_up'))
                            MtwvMtFailScaledown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Q2_down'))

                            MtwvMtFailSjbtagup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_up'))
                            MtwvMtFailSjbtagdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'sjbsf_down'))

                            MtwvMtFailTrigup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_up'))
                            MtwvMtFailTrigdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Trigger_down'))
                            
                            if ('tW' in options.set or 'signal' in options.set) and not wIsTtagged:
                                MtwvMtFailWup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_up')) 
                                MtwvMtFailWdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Wsf_down'))

                                MtwvMtFailExtrapUp.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_up'))
                                MtwvMtFailExtrapDown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Extrap_down'))

                            MtwvMtFailTptup.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_up'))
                            MtwvMtFailTptdown.Fill(tjet.M(),MtopW,norm_weight*Weightify(weights,'Ptreweight_down')) 

                  
    nev.SetBinContent(1,count)          
    end = time.time()
    print '\n'
    print str((end-start)/60.) + ' min'
    f.cd()
    f.Write()
    f.Close()



    
