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

from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.JetSysColl import JetSysColl, JetSysObj



# import FatJetNNHelper
# from FatJetNNHelper import *

import pickle
from optparse import OptionParser
from collections import OrderedDict
import copy
import math
from math import sqrt
import sys, array, os
import time
import pprint
pp = pprint.PrettyPrinter(indent = 2)

import Bstar_Functions
from Bstar_Functions import *

from bstar_class import bstar, CandidateJet, Counter

if __name__ == "__main__":
    
    parser = OptionParser()

    parser.add_option('-s', '--set', metavar='F', type='string', action='store',
                    default   =   'data',
                    dest      =   'set',
                    help      =   'dataset (ie data,ttbar etc)')
    parser.add_option('-c', '--config', metavar='F', type='string', action='store',
                    default   =   '',
                    dest      =   'config',
                    help      =   'Configuration json')
    parser.add_option('-r', '--region', metavar='F', type='string', action='store',
                    default   =   'default',
                    dest      =   'region',
                    help      =   'default, sideband, ttbar')
    parser.add_option('-y', '--year', metavar='FILE', type='string', action='store',
                    default   =   '',
                    dest      =   'year',
                    help      =   'Year (16,17,18)')
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
    parser.add_option('-j', '--job', metavar='FILE', type='string', action='store',
                    default   =   '',
                    dest      =   'job',
                    help      =   'Job number')
    parser.add_option('-n', '--njobs', metavar='FILE', type='string', action='store',
                    default   =   '',
                    dest      =   'njobs',
                    help      =   'Number of jobs')


    (options, args) = parser.parse_args()

    bstar = bstar('preselection',options)
   
    Cuts = bstar.cuts

    ###################
    # Book histograms #
    ###################
    base_string = 'MtwvMt'
    discr_strings = ['Pass','Fail','FailSub']
    syst_strings = ['PDF','PU','Top','Scale','Sjbtag','Trig','Tpt','W','Extrap']
    var_strings = ['up','down']

    hists = {}
    bstar.outfile.cd()
    for d in discr_strings:
        histname = base_string+d
        hists[histname] = TH2F(histname, histname, 60, 50, 350, 35, 500, 4000 )
        hists[histname].Sumw2()
        if bstar.runOthers and not bstar.isData:
            for s in syst_strings:
                for v in var_strings:
                    histname = histname+v
                    hists[histname] = TH2F(histname, histname, 60, 50, 350, 35, 500, 4000 )
                    hists[histname].Sumw2()


    if bstar.runOthers:
        nev = TH1F("nev",   "nev",      1, 0, 1 )
        lepVetoBins = OrderedDict()
        lepVetoBins['inLepSel'] = 'In Semi-lep channels'
        lepVetoBins['notInLepSel'] = 'Not in Semi-lep channels'
        lepVetoCount = Counter(lepVetoBins)
        
        if not bstar.isData:
            cut_titles = OrderedDict()
            cut_titles['pt'] = 'p_{T}',
            cut_titles['ht'] = 'h_{T}',
            cut_titles['MtopW'] = 'm_{tW}',
            cut_titles['dy'] = '|\Delta y|',
            cut_titles['preseljet_mass'] = 'Preselection jet mass'
            cut_titles['preseljet_nsubjetiness'] = 'Preselection jet N_{subjetiness}',
            if bstar.wIsTtagged: cut_titles['preseljet_sjbtag'] = 'Preselection jet subjet b tag'
            # cut_titles['alphajet_mass'] = 'Alphabet jet mass',
            cut_titles['alphajet_nsubjetiness'] = 'Alphabet jet mass N_{subjetiness}',
            cut_titles['alphajet_sjbtag'] = 'Alphabet jet subjet b tag'
            
            cutflow = Counter(cut_titles)

            if not bstar.wIsTtagged and 'ttbar' in options.set:
                wFakesBins = OrderedDict()
                wFakesBins[False] = 'Not an isolated daughter W of a top'
                wFakesBins[True] = 'Isolated daughter W of a top'
                wFakes = Counter(wFakesBins)

            TopMerging_titles = OrderedDict()
            TopMerging_titles[-3] = 'Only two prongs found'
            TopMerging_titles[-2] = 'Only one prong found'
            TopMerging_titles[-1] = 'Zero prongs found'
            TopMerging_titles[0] = '0 prongs in jet'
            TopMerging_titles[1] = '1 merged particle'
            TopMerging_titles[2] = '2 merged particle'
            TopMerging_titles[3] = '3 merged particle'
            TopMerging = Counter(TopMerging_titles)

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


    #############################
    # Get process normalization #
    #############################
    norm_weight = 1
    if 'data' not in options.set:
        runs_tree = bstar.infile.Get("Runs")
        nevents_gen = 0
        
        for i in runs_tree:
            nevents_gen+=i.genEventCount

        xsec = bstar.constants[options.set.replace('ext','')+'_xsec']
        norm_weight = bstar.lumi*xsec/float(nevents_gen)

    count = 0

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
                sys.stdout.write("%i / %i ... \r" % (count,(highBinEdge-lowBinEdge)))
                sys.stdout.flush()
        else:
            if count % 10000 == 0 : print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(highBinEdge-lowBinEdge)) + '% -- '

        # Grab the event
        event = Event(inTree, entry)

        # Apply triggers first
        if bstar.isData: 
            if not bstar.TriggerBit(inTree): continue

        # Have to grab Collections for each collection of interest
        # -- collections are for types of objects where there could be multiple values for a single event
        ak8JetsColl = Collection(event, 'FatJet')
        subJetsColl = Collection(event, 'SubJet')

        # Now jetID which (in binary #s) is stored with bit1 as loose, bit2 as tight, and filters (after grabbing jet collections)
        if len(ak8JetsColl) > 1:
            for i in range(2):
                if not bstar.JetID(ak8JetsColl[i]): continue

        # Now filters/flags
        if not bstar.Filters(inTree): continue
        
        # Separate into hemispheres the leading and subleading jets
        Jetsh0,Jetsh1 = bstar.Hemispherize(ak8JetsColl)

        if (len(Jetsh1) < 1): continue

        leadingJet, subleadingJet = ak8JetsColl[Jetsh0[0]], ak8JetsColl[Jetsh1[0]]

        doneAlready = False
        for hemis in ['hemis0','hemis1']:
            if hemis == 'hemis0':
                checkingFirstHemi = True
                preseljet = CandidateJet(leadingJet,bstar.isData)
                alphajet = CandidateJet(subleadingJet,bstar.isData)
                
            elif hemis == 'hemis1' and doneAlready == False:
                checkingFirstHemi = False
                preseljet = CandidateJet(subleadingJet,bstar.isData)
                alphajet = CandidateJet(leadingJet,bstar.isData)
                
            elif hemis == 'hemis1' and doneAlready == True:
                continue

            if not bstar.isData:
                alphajet.ApplyJetCorrections(['JES'+options.JES,'JER'+options.JER])

                if bstar.wIsTtagged:   preseljet.ApplyJetCorrections(['JES'+options.JES,'JER'+options.JER])
                else:                  preseljet.ApplyJetCorrections(['JES'+options.JES,'JER'+options.JER,'JMS'+options.JMS,'JMR'+options.JMR])

            ht = preseljet.pt + alphajet.pt
            MtopW = (preseljet.vect+alphajet.vect).M()
            
            # Make and get all cuts
            MtopW_cut = MtopW > 1000.
            ht_cut = ht > 1000.
            eta_cut = (Cuts['eta'][0]<abs(alphajet.eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(preseljet.eta)<Cuts['eta'][1])
            wpt_cut = Cuts['wpt'][0]<preseljet.pt<Cuts['wpt'][1]
            tpt_cut = Cuts['tpt'][0]<alphajet.pt<Cuts['tpt'][1]
            dy_cut = Cuts['dy'][0]<=abs(alphajet.vect.Rapidity()-preseljet.vect.Rapidity())<Cuts['dy'][1]
            
            # If tagging regular W as a top
            if bstar.wIsTtagged: preseljet_tag = bstar.Toptag(preseljet,'tight') + bstar.SJbtag(preseljet,subJetsColl)
            # Standard W tag
            else: preseljet_tag = bstar.Wtag(preseljet)

            tag_vals = preseljet_tag.GetVals()
            preselection = wpt_cut and tpt_cut and dy_cut and MtopW_cut and ht_cut and preseljet_tag.GetBool()
            
            if runOthers and checkingFirstHemi:
                if wpt_cut and tpt_cut:
                    cutflow.PlusOne('pt')
                    if ht_cut:
                        cutflow.PlusOne('ht')
                        if MtopW_cut:
                            cutflow.PlusOne('MtopW')
                            if dy_cut:
                                cutflow.PlusOne('dy')
                                if tag_vals['mass']['bool']:
                                    cutflow.PlusOne('preseljet_mass')
                                    if tag_vals['nsubjetiness']['bool']:
                                        cutflow.PlusOne('preseljet_nsubjetiness') 
                                        if wIsTtagged and tag_vals['sjbtag']['bool']:
                                            cutflow.PlusOne('preseljet_sjbtag') 


            if preselection: 
                doneAlready = True
                lepveto,lepvetoSF = LeptonVeto(event,options.year,lepSFfile)

                if not lepveto:
                    lepVetoCount.PlusOne('inLepSel')
                    continue
                else: lepVetoCount.PlusOne('notInLepSel')

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
                
                if not bstar.isData:
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

                    # W tagging SF and uncertainties on everything but ttbar and QCD
                    if not wIsTtagged and 'QCD' not in options.set:
                        # Get the purity
                        Wpurity = bstar.WPurity(preseljet_tag.GetVals['nsubjetiness']['val'])
                        # If this is ttbar MC, look for a parent gen top to the tagged and check if there's a b quark inside (apply SF if the jet is just a W coming form a top)
                        if 'ttbar' in options.set: 
                            wtagsf,wtagsfsig = WtagSF(Wpurity,GenParticles,ttbar=True)
                            if wtagsf == 1.0 and wtagsfsig == 0.0: wFakes.PlusOne(False)
                            else: wFakes.PlusOne(True)

                        elif 'ttbar' in options.set: wtagsf,wtagsfsig = bstar.WtagSF(Wpurity,GenParticles,ttbar=False)
 
                        weights['Wsf']['nom'] = wtagsf
                        weights['Wsf']['up'] = (wtagsf + wtagsfsig)
                        weights['Wsf']['down'] = (wtagsf - wtagsfsig)

                        # Get the extrapolation uncertainty if we found a real SF
                        if wtagsf != 1.0 and wtagsfsig != 0.0:
                            extrap = bstar.ExtrapUncert(preseljet.pt,Wpurity)
                            weights['Extrap']['up'] = 1+extrap
                            weights['Extrap']['down'] = 1-extrap

                    # Trigger weight applied
                    if bstar.config['trigger'][options.year] != 'off':
                        weights['Trigger']['nom'] = bstar.TriggerEff( ht , trigplot )[0]
                        weights['Trigger']['up'] = bstar.TriggerEff( ht , trigplot )[1]
                        weights['Trigger']['down'] = bstar.TriggerEff( ht , trigplot )[2]

                    # Top pt reweighting
                    if 'ttbar' in options.set:
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
                alphajet_tag = bstar.Toptag(alphajet,bstar.config['tau32']) + bstar.SJbtag(alphajet,subJetsColl)

                if runOthers and checkingFirstHemi:
                    if alphajet_tag['nsubjetiness']['bool']:
                        cutflow.PlusOne('alphajet_nsubjetiness')
                        if alphajet_tag['sjbtag']['bool']:
                            cutflow.PlusOne('alphajet_sjbtag')

                if alphajet_tag.GetBool():
                    # Top tagging tau32+sjbtag scale factor 
                    if "QCD" not in options.set and not bstar.isData:
                        sft,top_merging_status = bstar.TopTagSF(alphajet,bstar.config['tau32'],GenParticles)
                        if runOthers: TopMerging.PlusOne(top_merging_status)
                        weights['Topsf']['nom'] = sft[0]
                        weights['Topsf']['up'] = sft[1]
                        weights['Topsf']['down'] = sft[2]

                    else:
                        weights['Topsf']['nom'] = 1.0
                        weights['Topsf']['up'] =  1.0
                        weights['Topsf']['down'] = 1.0

                    if wIsTtagged:
                        # Top tagging tau32+sjbtag scale factor 
                        if "QCD" not in options.set and not bstar.isData:
                            sft,wtop_merging_status = SFT_Lookup(preseljet,'tight',GenParticles)
                            weights['Topsf']['nom'] *= sft[0]
                            weights['Topsf']['up'] *= sft[1]
                            weights['Topsf']['down'] *= sft[2]

                        else:
                            weights['Topsf']['nom'] = 1.0
                            weights['Topsf']['up'] =  1.0
                            weights['Topsf']['down'] = 1.0

                    MtwvMtPass.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'nominal')) 
                    MtwvMtFailSub.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                    if runOthers and not bstar.isData:
                        MtwvMtPassPDFup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'PDF_up'))
                        MtwvMtPassPDFdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'PDF_down'))

                        MtwvMtPassPUup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Pileup_up'))
                        MtwvMtPassPUdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Pileup_down'))

                        MtwvMtPassTopup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Topsf_up'))
                        MtwvMtPassTopdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Topsf_down'))

                        MtwvMtPassScaleup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Q2_up'))
                        MtwvMtPassScaledown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Q2_down'))

                        MtwvMtPassTrigup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Trigger_up'))
                        MtwvMtPassTrigdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Trigger_down'))

                        MtwvMtFailSubPDFup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'PDF_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                        MtwvMtFailSubPDFdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'PDF_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                        MtwvMtFailSubPUup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Pileup_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                        MtwvMtFailSubPUdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Pileup_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                        MtwvMtFailSubTopup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])*(weights['Topsf']['up']-1))
                        MtwvMtFailSubTopdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])*(weights['Topsf']['down']-1))

                        MtwvMtFailSubScaleup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Q2_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                        MtwvMtFailSubScaledown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Q2_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                        MtwvMtFailSubTrigup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Trigger_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                        MtwvMtFailSubTrigdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Trigger_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                        if not wIsTtagged and 'QCD' not in options.set:
                            MtwvMtPassWup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Wsf_up')) 
                            MtwvMtPassWdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Wsf_down'))

                            MtwvMtPassExtrapUp.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Extrap_up'))
                            MtwvMtPassExtrapDown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Extrap_down'))

                            MtwvMtFailSubWup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Wsf_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                            MtwvMtFailSubWdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Wsf_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                            MtwvMtFailSubExtrapUp.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Extrap_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                            MtwvMtFailSubExtrapDown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Extrap_down',drop=['Topsf'])*(weights['Topsf']['nom']-1))

                        if 'ttbar' in options.set:
                            MtwvMtPassTptup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Ptreweight_up'))
                            MtwvMtPassTptdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Ptreweight_down')) 

                            MtwvMtFailSubTptup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Ptreweight_up',drop=['Topsf'])*(weights['Topsf']['nom']-1))
                            MtwvMtFailSubTptdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Ptreweight_down',drop=['Topsf'])*(weights['Topsf']['nom']-1)) 

                else:
                    MtwvMtFail.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])) 

                    if flatTag() < 0.1:
                        dumbTagPass.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])) 
                    else:
                        dumbTagFail.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf'])) 

                    if runOthers and not bstar.isData:
                        MtwvMtFailPDFup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'PDF_up',drop=['Topsf']))
                        MtwvMtFailPDFdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'PDF_down',drop=['Topsf']))

                        MtwvMtFailPUup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Pileup_up',drop=['Topsf']))
                        MtwvMtFailPUdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Pileup_down',drop=['Topsf']))

                        MtwvMtFailTopup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf']))
                        MtwvMtFailTopdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'nominal',drop=['Topsf']))

                        MtwvMtFailScaleup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Q2_up',drop=['Topsf']))
                        MtwvMtFailScaledown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Q2_down',drop=['Topsf']))

                        MtwvMtFailTrigup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Trigger_up',drop=['Topsf']))
                        MtwvMtFailTrigdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Trigger_down',drop=['Topsf']))
                        
                        if not wIsTtagged and 'QCD' not in options.set:
                            MtwvMtFailWup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Wsf_up',drop=['Topsf'])) 
                            MtwvMtFailWdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Wsf_down',drop=['Topsf']))

                            MtwvMtFailExtrapUp.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Extrap_up',drop=['Topsf']))
                            MtwvMtFailExtrapDown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Extrap_down',drop=['Topsf']))

                        if 'ttbar' in options.set:
                            MtwvMtFailTptup.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Ptreweight_up',drop=['Topsf']))
                            MtwvMtFailTptdown.Fill(alphajet.SDmass,MtopW,norm_weight*Weightify(weights,'Ptreweight_down',drop=['Topsf'])) 

    bstar.outfile.cd()
    if bstar.runOthers:   
        if not bstar.isData:
            lepVetoCount.GetHist('lepVetoCount',histtitle='True hadronic events that are accepted or rejected by the semi-leptonic channel veto').Write()
            TopMerging.GetHist('TopMerging',histtitle='Merge status of top tagged jets').Write()
            cutflow.GetHist('cutflow').Write()
            if not bstar.wIsTtagged and 'ttbar' in options.set:
                wFakes.GetHist('wFakes',histtitle='Status of ttbar MC tops that are tagged as W').Write()
        
    nev.SetBinContent(1,count)          
    end = time.time()
    print '\n'
    print str((end-start)/60.) + ' min'

    # Correct the failing distribution from the top tag sf application in pass (subtract events that were gained/lost in pass)
    MtwvMtFail.Add(MtwvMtFailSub,-1)
    if runOthers and not bstar.isData:
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
        if not wIsTtagged and 'QCD' not in options.set:
            MtwvMtFailWup.Add(MtwvMtFailSubWup,-1)
            MtwvMtFailWdown.Add(MtwvMtFailSubWdown,-1)
            MtwvMtFailExtrapUp.Add(MtwvMtFailSubExtrapUp,-1)
            MtwvMtFailExtrapDown.Add(MtwvMtFailSubExtrapDown,-1)
        if 'ttbar' in options.set:
            MtwvMtFailTptup.Add(MtwvMtFailSubTptup,-1)
            MtwvMtFailTptdown.Add(MtwvMtFailSubTptdown,-1)


    bstar.outfile.Write()
    bstar.outfile.Close()  
