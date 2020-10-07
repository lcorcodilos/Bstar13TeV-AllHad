
##################################################################
##                                                              ##
## Name: Bstar_Functions.py                                     ##
## Author: Kevin Nash                                           ##
## Date: 5/13/2015                                              ##
## Purpose: This contains all functions used by the             ##
##      analysis.  A method is generally placed here if         ##
##      it is called more than once in reproducing all          ##
##      analysis results.  The functions contained here         ##
##      Are capable of tuning the analysis - such as changing   ##
##      cross sections, updating lumi, changing file            ##
##      locations, etc. with all changes propegating            ##
##      to all relevant files automatically.                    ##
##                                                              ##
##################################################################

import os
import glob
import math
from random import random
from math import sqrt, exp, log
import ROOT
import sys
import time
import subprocess
import cppyy
import pickle
from ROOT import *
from PhysicsTools.NanoAODTools.postprocessing.tools import *
import GenParticleChecker
from GenParticleChecker import GenParticleTree,GenParticleObj

#This is the most impostant Function.  Correct information here is essential to obtaining valid results.
#In order we have Luminosity, top tagging scale factor, cross sections for wprime right,left,mixed,ttbar,qcd, and singletop and their corresponding event numbers
#If I wanted to access the left handed W' cross section at 1900 GeV I could do Xsecl1900 = LoadConstants()['xsec_wpl']['1900']
def LoadConstants(year):
    out = {
        'QCDHT700_xsec':6802,
        'QCDHT1000_xsec':1206,
        'QCDHT1500_xsec':120.4,
        'QCDHT2000_xsec':25.25,
        'QCDHerwig_xsec':346.2,
        'singletop_s_xsec':10.32,
        'singletop_t_xsec':136.02,
        'singletop_tW_xsec':35.85,
        'singletop_tW-scaleup_xsec':35.85,
        'singletop_tW-scaledown_xsec':35.85,
        'singletop_tWB-scaleup_xsec':35.85,
        'singletop_tWB-scaledown_xsec':35.85,
        'singletop_tB_xsec':80.95,
        'singletop_tWB_xsec':35.85,
        'WjetsHT400_xsec':315.6,
        'WjetsHT600_xsec':68.57,
        'WjetsHT800_xsec':34.9,
        'signalLH1200_xsec':1.0,
        'signalLH1400_xsec':1.0,
        'signalLH1600_xsec':0.1,
        'signalLH1800_xsec':0.1,
        'signalLH2000_xsec':0.1,
        'signalLH2200_xsec':0.01,
        'signalLH2400_xsec':0.01,
        'signalLH2600_xsec':0.01,
        'signalLH2800_xsec':0.01,
        'signalLH3000_xsec':0.001,
        'signalLH3200_xsec':0.001,
        'signalLH3400_xsec':0.001,
        'signalLH3600_xsec':0.001,
        'signalLH3800_xsec':0.0001,
        'signalLH4000_xsec':0.0001,
        'signalRH1200_xsec':1.0,
        'signalRH1400_xsec':1.0,
        'signalRH1600_xsec':0.1,
        'signalRH1800_xsec':0.1,
        'signalRH2000_xsec':0.1,
        'signalRH2200_xsec':0.01,
        'signalRH2400_xsec':0.01,
        'signalRH2600_xsec':0.01,
        'signalRH2800_xsec':0.01,
        'signalRH3000_xsec':0.001,
        'signalRH3200_xsec':0.001,
        'signalRH3400_xsec':0.001,
        'signalRH3600_xsec':0.001,
        'signalRH3800_xsec':0.0001,
        'signalRH4000_xsec':0.0001,
        'TprimeRH1200_xsec':0.001,
        'TprimeRH1300_xsec':0.001,
        'TprimeRH1400_xsec':0.001,
        'TprimeRH1500_xsec':0.001,
        'TprimeRH1600_xsec':0.001,
        'TprimeRH1700_xsec':0.001,
        'TprimeRH1800_xsec':0.001,
        'TprimeLH1200_xsec':0.001,
        'TprimeLH1300_xsec':0.001,
        'TprimeLH1400_xsec':0.001,
        'TprimeLH1500_xsec':0.001,
        'TprimeLH1600_xsec':0.001,
        'TprimeLH1700_xsec':0.001,
        'TprimeLH1800_xsec':0.001,
        'BprimeRH1200_xsec':0.001,
        'BprimeRH1300_xsec':0.001,
        'BprimeRH1400_xsec':0.001,
        'BprimeRH1500_xsec':0.001,
        'BprimeRH1600_xsec':0.001,
        'BprimeRH1700_xsec':0.001,
        'BprimeRH1800_xsec':0.001,
        'BprimeLH1200_xsec':0.001,
        'BprimeLH1300_xsec':0.001,
        'BprimeLH1400_xsec':0.001,
        'BprimeLH1500_xsec':0.001,
        'BprimeLH1600_xsec':0.001,
        'BprimeLH1700_xsec':0.001,
        'BprimeLH1800_xsec':0.001
    }
    if year == '16':
        out['lumi'] = 35917.213466
        out['qcd_lumi'] = 5466.09
        out['ttbar_xsec'] = 831.76
        out['wtagsf_HP'] = 1.0 # HP = High purity
        out['wtagsfsig_HP'] = 0.06
        out['wtagsf_LP'] = 0.96 # LP = Low purity
        out['wtagsfsig_LP'] = 0.11
            
    elif year == '17':
        out['lumi'] = 41521.427777
        out['qcd_lumi'] = 7016.29
        out['wtagsf_HP'] = 0.97 # HP = High purity
        out['wtagsfsig_HP'] = 0.06
        out['wtagsf_LP'] = 1.14 # LP = Low purity
        out['wtagsfsig_LP'] = 0.29
        out['ttbar_xsec'] = 377.96 #uncertainty +4.8%-6.1%
        out['ttbar-semilep_xsec'] = 365.34
            
    elif year == '18':
        out['lumi'] = 59692.687741#59692.687741,
        out['qcd_lumi'] = 7080.08
        out['wtagsf_HP'] = 0.980# HP = High purity
        out['wtagsfsig_HP'] = 0.027
        out['wtagsf_LP'] = 1.120# LP = Low purity
        out['wtagsfsig_LP'] = 0.275

    return out
    
def LoadCuts(region,year):
    cuts = {
        'wpt':[400.0,float("inf")],
        'tpt':[400.0,float("inf")],
        'dy':[0.0,1.6],
        'tmass':[105.0,220.0],
        'wmass':[65.0,105.0],
        'tau32loose':[0.0,0.8],
        'tau32medium':[0.0,0.65],
        'tau32tight':[0.0,0.54],
        'eta':[0.0,2.4]}

    if year == '16':
        cuts['deepbtag'] = [0.2217,1.0]
        
        if region == 'default':
            cuts['tau21'] = [0.0,0.4]

        elif region == 'sideband':
            cuts['tau21'] = [0.4,1.0]

        # elif region == 'ttbar':
            # continue

    if year == '17':
        cuts['deepbtag'] = [0.1522,1.0]

        if region == 'default':
            cuts['tau21'] = [0.0,0.45]
            cuts['tau21LP'] = [0.45,0.75]

        elif region == 'sideband':
            cuts['tau21'] = [0.45,0.75]
            cuts['tau21LP'] = [0.45,0.75]

        # elif region == 'ttbar':
        #     continue

    if year == '18':
        cuts['deepbtag'] = [0.1241,1.0]

        if region == 'default':
            cuts['tau21'] = [0.0,0.45]
            cuts['tau21LP'] = [0.45,0.75]

        elif region == 'sideband':
            cuts['tau21'] = [0.45,1.0]
            cuts['tau21LP'] = [0.45,0.75]

        # elif region == 'ttbar':
        #     continue

    return cuts

#This function loads up Ntuples based on what type of set you want to analyze.  
#This needs to be updated whenever new Ntuples are produced (unless the file locations are the same).
def Load_jetNano(string,year):
    print 'running on ' + string 

    return 'root://cmseos.fnal.gov//store/user/lcorcodi/bstar_nano/rootfiles/'+string+'_bstar'+year+'.root'

def DeltaR(v1,v2): Math.VectorUtil.DeltaR(v1,v2)

def PDF_Lookup(pdfs,hessian=False):
    if len(pdfweights) == 0:
        raise ValueError('LHEPDFWeight vector empty')
        # return 1,1

    if hessian:
        # Computes sqrt of sum of differences squared
        pdfweights = []
        base_eigenvector = pdfweights[0]
        for ipdf in range(1,pdfs.GetSize()):
            pdfweights.append(pdfs[ipdf])

        sumsquares = 0
        for pdf in pdfweights:
            sumsquares = sumsquares + (pdf-base_eigenvector)**2

        stddev = sqrt(sumsquares)

    else:
        # Computes the std dev of the pdf weights to estimate the up and down uncertainty for each set (event)
        pdfweights = []
        for ipdf in range(pdfs.GetSize()):
            pdfweights.append(pdfs[ipdf])

        pdfavg =  reduce(lambda x, y: x + y, pdfweights) / len(pdfweights)
        sumsquares = 0
        for pdf in pdfweights:
            sumsquares = sumsquares + (pdf-pdfavg)**2
        stddev = sqrt(sumsquares / (len(pdfweights)-1))

    lower = min(13.0,1.0+stddev)
    upper =  max(-12.0,1.0-stddev)

    return lower,upper 

def Trigger_Lookup( H , TRP ):
    Weight = 1.0
    Weightup = 1.0
    Weightdown = 1.0
    if H < 2000.0:
        bin0 = TRP.FindBin(H) 
        jetTriggerWeight = TRP.GetBinContent(bin0)
        # Check that we're not in an empty bin in the fully efficient region
        if jetTriggerWeight == 0:
            if TRP.GetBinContent(bin0-1) == 1.0 and TRP.GetBinContent(bin0+1) == 1.0:
                jetTriggerWeight = 1.0
            elif TRP.GetBinContent(bin0-1) > 0 or TRP.GetBinContent(bin0+1) > 0:
                jetTriggerWeight = (TRP.GetBinContent(bin0-1)+TRP.GetBinContent(bin0+1))/2.

        Weight = jetTriggerWeight
        deltaTriggerEff  = 0.5*(1.0-jetTriggerWeight)
        Weightup  =   min(1.0,jetTriggerWeight + deltaTriggerEff)
        Weightdown  =   max(0.0,jetTriggerWeight - deltaTriggerEff)

    return [Weight,Weightup,Weightdown]


# def SFTdeep_Lookup( pttop, plots ):
#     nom = plots['nom'].Eval(pttop)
#     up = plots['up'].Eval(pttop)
#     down = plots['down'].Eval(pttop)
#     return [nom,up,down]

class myGenParticle:
    def __init__ (self, index, genpart):
        self.idx = index
        self.genpart = genpart
        self.status = genpart.status
        self.pdgId = genpart.pdgId
        self.vect = ROOT.Math.PtEtaPhiMVector(genpart.pt,genpart.eta,genpart.phi,genpart.mass)
        self.motherIdx = genpart.genPartIdxMother

def SFT_Lookup(jet, file, genparticles, wp,ievent=1):    
    if wp == 'tight':
        workpoint = 'wp3'
    elif wp == 'medium':
        workpoint = 'wp4'
    elif wp == 'loose':
        workpoint = 'wp5'

    # Build the tree of gen particles that we care about
    particle_tree = GenParticleTree()
    tops = []
    Ws = []
    quarks = []
    prongs = [] # Final particles we'll check
    for i,p in enumerate(genparticles):
        # Internal class info
        this_gen_part = GenParticleObj(i,p)
        this_gen_part.SetStatusFlags()
        this_gen_part.SetPDGName(abs(this_gen_part.pdgId))
        
        # Add particles to tree and keep track of them in external lists
        if abs(this_gen_part.pdgId) == 6 and this_gen_part.DeltaR(jet)<0.8:# and this_gen_part.status == 62: # 22 means intermediate part of hardest subprocess, only other to appear is 62 (outgoing subprocess particle with primordial kT included)
            particle_tree.AddParticle(this_gen_part)
            tops.append(this_gen_part)

        elif abs(this_gen_part.pdgId) == 24:# and this_gen_part.status == 22: # 22 means intermediate part of hardest subprocess, only other to appear is 52 (outgoing copy of recoiler, with changed momentum)
            particle_tree.AddParticle(this_gen_part)
            Ws.append(this_gen_part)

        elif abs(this_gen_part.pdgId) >= 1 and abs(this_gen_part.pdgId) <= 5 and this_gen_part.status == 23:
            particle_tree.AddParticle(this_gen_part)
            quarks.append(this_gen_part)

        elif this_gen_part.DeltaR(jet)<0.8:
            particle_tree.AddParticle(this_gen_part)

    for W in Ws:
        # If parent is a top that matches with the jet
        wParent = particle_tree.GetParent(W)
        if wParent != False:
            if abs(wParent.pdgId) == 6 and wParent.DeltaR(jet) < 0.8:
                # Loop over the daughters of the W
                this_W = W
                # Skip down chain of W's to last one
                if len(particle_tree.GetChildren(this_W)) == 1 and particle_tree.GetChildren(this_W)[0].pdgId == W.pdgId:
                    this_W = particle_tree.GetChildren(this_W)[0]
                
                for c in particle_tree.GetChildren(this_W):
                    if abs(c.pdgId) >= 1 and abs(c.pdgId) <= 5:
                        # Append daughter quarks to prongs
                        prongs.append(c)

    for q in quarks:
        # if bottom      and     has a parent              and   parent is a top                          and    the top matches to the jet
        if abs(q.pdgId) == 5:
            bottomParent = particle_tree.GetParent(q)
            # if parent exists
            if bottomParent != False:
                # if parent is a top matched to the jet
                if abs(bottomParent.pdgId) == 6 and bottomParent.DeltaR(jet) < 0.8:
                    prongs.append(q)

    # Now that we have the prongs, check how many are merged
    merged_particles = 0
    if len(prongs) < 3: # you've either tagged a QCD jet and can't match to a gen top or the W decayed leptonically so don't apply a SF in either case
        # if len(prongs) == 1: 
        #     particle_tree.PrintTree(ievent,['idx','status'],wp,jet)
        #     raw_input(prongs[0].idx)
        return [1,1,1],-len(prongs)-1


    for p in prongs:
        if p.DeltaR(jet) < 0.8:
            merged_particles += 1

    if merged_particles == 3:
        hnom = file.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_nominal')
        hup = file.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_up')
        hdown = file.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_down')
    elif merged_particles == 2:
        hnom = file.Get('PUPPI_'+workpoint+'_btag/sf_semimerged_nominal')
        hup = file.Get('PUPPI_'+workpoint+'_btag/sf_semimerged_up')
        hdown = file.Get('PUPPI_'+workpoint+'_btag/sf_semimerged_down')
    elif merged_particles == 1:
        hnom = file.Get('PUPPI_'+workpoint+'_btag/sf_notmerged_nominal')
        hup = file.Get('PUPPI_'+workpoint+'_btag/sf_notmerged_up')
        hdown = file.Get('PUPPI_'+workpoint+'_btag/sf_notmerged_down')
    else:
        return [1,1,1],-len(prongs)-1

    if jet.Pt() > 5000:
        sfbin_nom = hnom.GetNbinsX()
        sfbin_up = hup.GetNbinsX()
        sfbin_down = hdown.GetNbinsX()
    else:
        sfbin_nom = hnom.FindFixBin(jet.Pt())
        sfbin_up = hup.FindFixBin(jet.Pt())
        sfbin_down = hdown.FindFixBin(jet.Pt())

    nom = hnom.GetBinContent(sfbin_nom)
    up = hup.GetBinContent(sfbin_up)
    down = hdown.GetBinContent(sfbin_down)

    del particle_tree

    return [nom,up,down],merged_particles

def SFT_Variation(top_merging_status,wIsTtagged,wtop_merging_status):
    out = {
            1:{"up":"nominal", "down":"nominal"},
            2:{"up":"nominal", "down":"nominal"},
            3:{"up":"nominal", "down":"nominal"}
        }

    new_alphatop_key = top_merging_status if (top_merging_status > 0) else "none"
    new_preseltop_key = wtop_merging_status if (wIsTtagged and wtop_merging_status > 0) else "none" 
    
    # Simple case where we couldn't determine merging for either
    if new_alphatop_key == "none" and new_preseltop_key == "none": 
        return out
    # If one is "none"
    elif new_alphatop_key == "none":
        out[new_preseltop_key]['up'] = 'TopsfPresel_up'
        out[new_preseltop_key]['down'] = 'TopsfPresel_down'
    # If the other is "none"
    elif new_preseltop_key == "none":
        out[new_alphatop_key]['up'] = 'Topsf_up'
        out[new_alphatop_key]['down'] = 'Topsf_down'
    # If neither is "none"
    else:
        # If they are the same
        if new_alphatop_key == new_preseltop_key:
            out[new_preseltop_key]['up'] = ['Topsf_up','TopsfPresel_up']
            out[new_preseltop_key]['down'] = ['Topsf_down','TopsfPresel_down']
        # If they are different
        else:
            out[new_preseltop_key]['up'] = 'TopsfPresel_up'
            out[new_preseltop_key]['down'] = 'TopsfPresel_down'
            out[new_alphatop_key]['up'] = 'Topsf_up'
            out[new_alphatop_key]['down'] = 'Topsf_down'

    return out


# def SFT_Lookup_MERGEDONLY( jet, file , wp ):
#     if wp == 'loose':
#         workpoint = 'wp3'
#     elif wp == 'medium':
#         workpoint = 'wp4'
#     elif wp == 'tight':
#         workpoint = 'wp5'

#     hnom = file.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_nominal')
#     hup = file.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_up')
#     hdown = file.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_down')
#     if jet.Perp() > 5000:
#         sfbin_nom = hnom.GetNbinsX()
#         sfbin_up = hup.GetNbinsX()
#         sfbin_down = hdown.GetNbinsX()
#     else:
#         sfbin_nom = hnom.FindFixBin(jet.Perp())
#         sfbin_up = hup.FindFixBin(jet.Perp())
#         sfbin_down = hdown.FindFixBin(jet.Perp())

#     nom = hnom.GetBinContent(sfbin_nom)
#     up = hup.GetBinContent(sfbin_up)
#     down = hdown.GetBinContent(sfbin_down)

#     return [nom,up,down]

#This looks up the ttbar pt reweighting scale factor when making ttrees
def PTW_Lookup( GP, jets ):
    genTpt = None
    genTBpt = None 

    wTPt = {}
    wTbarPt = {}
    sfs = {}
    for k in ['nom','alpha_up','alpha_down','beta_up','beta_down']:
        wTPt[k] = None
        wTbarPt[k] = None
        sfs[k] = None

    # For all gen particles
    for ig in GP :
        if ig.pdgId == -6 and ig.statusFlags & (1 << 13): 
            antitop_lv = ROOT.Math.PtEtaPhiMVector(ig.pt,ig.eta,ig.phi,ig.mass)
            if DeltaR(antitop_lv,jets[0]) <0.8 or DeltaR(antitop_lv,jets[1]) <0.8:
                genTBpt = ig.pt
        elif ig.pdgId == 6 and ig.statusFlags & (1 << 13): 
            top_lv = ROOT.Math.PtEtaPhiMVector(ig.pt,ig.eta,ig.phi,ig.mass)
            if DeltaR(top_lv,jets[0]) <0.8 or DeltaR(top_lv,jets[1]) <0.8:
                genTpt = ig.pt 

    if (genTpt == None) or (genTBpt == None):pair_exists = False
    else: pair_exists = True
    
    if genTpt == None: 
        for k in wTPt.keys(): wTPt[k] = 1.0
    else: 
        wTPt['nom'] = exp(0.0615-0.0005*genTpt)
        wTPt['alpha_up'] = exp(1.5*0.0615-0.0005*genTpt)
        wTPt['alpha_down'] = exp(0.5*0.0615-0.0005*genTpt)
        wTPt['beta_up'] = exp(0.0615-1.5*0.0005*genTpt)
        wTPt['beta_down'] = exp(0.0615-0.5*0.0005*genTpt)

    if genTBpt == None:
        for k in wTbarPt.keys(): wTbarPt[k] = 1.0
    else:
        wTbarPt['nom'] = exp(0.0615-0.0005*genTBpt)
        wTbarPt['alpha_up'] = exp(1.5*0.0615-0.0005*genTBpt)
        wTbarPt['alpha_down'] = exp(0.5*0.0615-0.0005*genTBpt)
        wTbarPt['beta_up'] = exp(0.0615-1.5*0.0005*genTBpt)
        wTbarPt['beta_down'] = exp(0.0615-0.5*0.0005*genTBpt)

    for k in sfs.keys():
        sfs[k] = sqrt(wTPt[k]*wTbarPt[k])
    return sfs,pair_exists


# This does the W jet matching requirement by looking up the deltaR separation
# of the daughter particle from the W axis. If passes, return 1.
def WJetMatching(wjetVect,genparticles,ttbar=False):
    import GenParticleChecker
    from GenParticleChecker import GenParticleTree,GenParticleObj
    
    # Build the tree of gen particles that we care about
    particle_tree = GenParticleTree()
    
    if not ttbar:
        Ws = []
        quarks = []
        prongs = [] # Final particles we'll check
        for i,p in enumerate(genparticles):
            # Internal class info
            this_gen_part = GenParticleObj(i,p)
            this_gen_part.SetStatusFlags()
            this_gen_part.SetPDGName(abs(this_gen_part.pdgId))
            
            # Add particles to tree and keep track of them in external lists
            if abs(this_gen_part.pdgId) == 24:# and this_gen_part.status == 22: # 22 means intermediate part of hardest subprocess, only other to appear is 52 (outgoing copy of recoiler, with changed momentum)
                particle_tree.AddParticle(this_gen_part)
                Ws.append(this_gen_part)

            elif abs(this_gen_part.pdgId) >= 1 and abs(this_gen_part.pdgId) <= 5:
                particle_tree.AddParticle(this_gen_part)
                quarks.append(this_gen_part)

        for q in quarks:
            # if parent is a w and 
            if particle_tree.GetParent(q) and abs(particle_tree.GetParent(q).pdgId) == 24 and particle_tree.GetParent(q).DeltaR(wjetVect) < 0.8 and q.DeltaR(wjetVect) < 0.8:
                prongs.append(q)

        if len(prongs) == 2:
            return True
        else:
            return False   
    
    # If ttbar MC
    else:
        tops = []
        Ws = []
        quarks = []
        qprongs = [] # Final particles we'll check
        bprongs = []
        for i,p in enumerate(genparticles):
            # Internal class info
            this_gen_part = GenParticleObj(i,p)
            this_gen_part.SetStatusFlags()
            this_gen_part.SetPDGName(abs(this_gen_part.pdgId))
            
            # Add particles to tree and keep track of them in external lists
            if abs(this_gen_part.pdgId) == 6:# and this_gen_part.status == 62: # 22 means intermediate part of hardest subprocess, only other to appear is 62 (outgoing subprocess particle with primordial kT included)
                particle_tree.AddParticle(this_gen_part)
                tops.append(this_gen_part)

            elif abs(this_gen_part.pdgId) == 24:# and this_gen_part.status == 22: # 22 means intermediate part of hardest subprocess, only other to appear is 52 (outgoing copy of recoiler, with changed momentum)
                particle_tree.AddParticle(this_gen_part)
                Ws.append(this_gen_part)

            elif abs(this_gen_part.pdgId) >= 1 and abs(this_gen_part.pdgId) <= 5 and this_gen_part.status == 23:
                particle_tree.AddParticle(this_gen_part)
                quarks.append(this_gen_part)

        found_top = False
        for t in tops:
            if t.DeltaR(wjetVect)<0.8: found_top = True

        if not found_top: return False

        for W in Ws:
            # If parent is a top that matches with the jet
            wParent = particle_tree.GetParent(W)
            if wParent != False and abs(wParent.pdgId) == 6 and wParent.DeltaR(wjetVect) < 0.8 and wParent.pt > 200:
                # Loop over the daughters of the W
                this_W = W
                # Skip down chain of W's to last one
                if len(particle_tree.GetChildren(this_W)) == 1 and particle_tree.GetChildren(this_W)[0].pdgId == W.pdgId:
                    this_W = particle_tree.GetChildren(this_W)[0]
                
                for c in particle_tree.GetChildren(this_W):
                    if abs(c.pdgId) >= 1 and abs(c.pdgId) <= 5:
                        # Append daughter quarks to prongs
                        if c.DeltaR(wjetVect)<0.8:qprongs.append(c)
                            
        for q in quarks:
            # if bottom     
            if abs(q.pdgId) == 5:
                bottomParent = particle_tree.GetParent(q)
                # if parent exists and is a top matched to the jet
                if bottomParent != False and abs(bottomParent.pdgId) == 6 and bottomParent.DeltaR(wjetVect) < 0.8 and bottomParent.pt > 200:
                    if q.DeltaR(wjetVect) < 0.8: bprongs.append(q)

        # Now that we have the prongs, check how many are merged Ws with no b in jet            
        if len(bprongs) == 0 and len(qprongs) == 2:
            return True
        else:
            return False

# def getCorrectedPuppiSDmass(fatjetVect, subjetsCollection, puppisd_corrGEN, puppisd_corrRECO_cen, puppisd_corrRECO_for):
#     # Lookup with PUPPI AK8 Jet pt and eta (with JECs) but apply to uncorrected SD mass which is reconstructed by summing subjet 4-vectors
#     genCorr  = 1.
#     recoCorr = 1.
#     totalWeight = 1.

#     genCorr =  puppisd_corrGEN.Eval( fatjetVect.Perp() );
    
#     if abs(fatjetVect.Eta()) <= 1.3:
#         recoCorr = puppisd_corrRECO_cen.Eval( fatjetVect.Perp() )
#     else:
#         recoCorr = puppisd_corrRECO_for.Eval( fatjetVect.Perp() )

#     totalWeight = genCorr * recoCorr

#     uncorrectedFatJetVect = TLorentzVector()
#     for subjet in subjets:
#         subjet_vect = TLorentzVector()
#         subjet_vect = SetPtEtaPhiM(subjet.pt, subjet.eta, subjet.phi, subjet.msoftdrop)
#         if subjet_vect.DeltaR(fatjetVect) < 0.8:
#             uncorrectedFatJetVect += subjet_vect

#     return uncorrectedFatJetVect.M() * totalWeight

def jetIDChecker(jetObj):
    jetID = jetObj.jetId
    if (jetID & 1 == 0):    # if not loose
        if (jetID & 2 == 0): # and if not tight - Need to check here because loose is always false in 2017
            return False                      # move on
        else:
            return True
    else:
        return True

def Hemispherize(jetCollection):
    Jetsh1 = []
    Jetsh0 = []
    for ijet in range(0,len(jetCollection)):
        if abs(deltaPhi(jetCollection[0].phi,jetCollection[ijet].phi))>TMath.Pi()/2.0:
            if jetIDChecker(jetCollection[ijet]): Jetsh1.append(ijet)
        else:
            if jetIDChecker(jetCollection[ijet]): Jetsh0.append(ijet)

    return Jetsh0,Jetsh1

def Weightify(wd,outnames,drop=[]):
    final_w = 1.0
    corrections = [corr for corr in wd.keys() if 'nom' in wd[corr].keys() and corr not in drop]

    if type(outnames) == str: outnames = [outnames]

    # If nominal, apply all corrections
    if outnames[0] == 'nominal':
        for c in corrections:
            final_w = final_w*wd[c]['nom']
        return final_w

    # If not nominal, apply the variation of the correction and all other nominal corrections
    for outname in outnames:
        final_w *= wd[outname.split('_')[0]][outname.split('_')[1]]
    for c in corrections:
        if c not in [o.split('_')[0] for o in outnames]:
            final_w = final_w*wd[c]['nom']
   
    return final_w

def LeptonVeto(event, year, sf_file):
    from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event

    ak4jetColl = Collection(event, 'Jet')
    electronColl = Collection(event, 'Electron')
    muonColl = Collection(event, 'Muon')

    # Leptonic W selection
    # * 1 isolated lepton
    #    * pt > 53 GeV
    #    * |eta| < 2.4  
    #    * tight muon (rel. iso < .15) or tight isolated electron
    # * veto on additional leptons --> Can ignore this because all had shouldn't have any events with more than candidate lepton either
    #    * pt > 30GeV
    #    * |eta| < 2.4 
    #    * veto id electrons or loose id muons)
    # * deltaR (lepton, ak4jets) > 0.4
    # * MET > 50 GeV
    # * ST (sum of all jet pt + lepton pt + MET) > 400 GeV
    # * 1 HOTVR Jet pt > 200 GeV, |eta| < 2.5
    # * deltaPhi (lepton, MET) < pi/2
    # * 1 medium deep csv btag
    # * deltaR (lepton, b-jet) > 2.0
    # * 1 HOTVR top tag
    # * reconstruction chi^2 < 30

    # Construct list of candidates es and mus
    lepW_additional_leps = [e for e in electronColl if e.pt > 30 and abs(e.eta) < 2.4]+[mu for mu in muonColl if mu.pt > 30 and abs(mu.eta) < 2.4]
    lepW_candidate_es = [e for e in electronColl if e.pt > 53 and abs(e.eta) < 2.4]
    lepW_candidate_mus = [mu for mu in muonColl if mu.pt > 53 and abs(mu.eta) < 2.4]

    lep_sf = 1

    # If you're able to make the cut on pt and eta alone, don't change SF and just give false for lepW selection
    if len(lepW_candidate_es) == 0 and len(lepW_candidate_mus) == 0:
        lepW_veto = True
    # If there are additional leptons in the event:
    elif len(lepW_additional_leps) > 1:
        lepW_veto = True
    # If you need to check lepton IDs...
    else:
        # Check electrons
        for ie,e in enumerate(lepW_candidate_es):
            # Check if it passes veto
            if e.cutBased != 4:
                lepW_candidate_es.pop(ie)
                lep_sf *= SFe_Lookup(year,sf_file,e.pt,e.eta)
            
        if len(lepW_candidate_es) > 0:
            lepW_veto = False

        # Check muons
        else:
            for im,m in enumerate(lepW_candidate_mus):
                # If tight ID and Iso, we'll toss it
                if not mu.tightId:
                    lepW_candidate_mus.pop(im)
                    lep_sf *= SFmu_Lookup(year,'ID',sf_file,mu.pt,mu.eta)
                elif mu.pfRelIso04_all > .15:
                    lepW_candidate_mus.pop(im)
                    lep_sf *= SFmu_Lookup(year,'ISO',sf_file,mu.pt,mu.eta)

            if len(lepW_candidate_mus) > 0:
                lepW_veto = False
            else:
                lepW_veto = True

    # Leptonic Top selection
    # * 1 unisolated Tight Lepton  
    #    * (Muon : pt>53 GeV , |eta| < 2.4; Electron :  pt>30 GeV , |eta| < 2.4) 
    #    * with 2D cut (deltaR(lepton,closedAK4jet)>0.4 or PTrel >15 GeV )
    # * 1 AK8jet : 
    #    * pt>200GeV
    #    * |eta| < 2.4
    #    * 60GeV < prunedmass < 105GeV 
    #    * tau21 < 0.6
    # * At least one AK4jet :
    #    * pt>30 GeV
    #    * |eta| < 2.4
    #    * deltaR(AK4jet,AK8jet)>0.8
    #    * b-tagging:CSVv2> 0.8484
    # * MET >80 GeV and AK8 jet pt>950 GeV for Muon channel
    # * MET>240GeV and AK8 jet pt>750 GeV for Electron channel.

    lepT_candidates = [e for e in electronColl if e.pt > 30 and abs(e.eta) < 2.4] + [mu for mu in electronColl if mu.pt > 53 and abs(e.eta) < 2.4]

    if len(lepT_candidates) == 0:
        lepT_veto = True

    else:
        for il,l in enumerate(lepT_candidates):
            if l.jetIdx != -1:
                closestAK4 = ak4jetColl[l.jetIdx]
                closestAK4_LV = ROOT.Math.PtEtaPhiMVector(closestAK4.pt, closestAK4.eta, closestAK4.phi, closestAK4.mass)
                l_LV = ROOT.Math.PtEtaPhiMVector(l.pt, l.eta, l.phi, l.mass)
            else:
                closestAK4_LV = None
            deltaRcut = DeltaR(l_LV,closestAK4_LV) > 0.4 if closestAK4_LV != None else False

            if not deltaRcut:
                if hasattr(l,'jetPtRelv2'):
                    if l.jetPtRelv2 < 15: 
                        lepT_candidates.pop(il)
                else:
                    lepT_candidates.pop(il)

        if len(lepT_candidates) > 0:
            lepT_veto = False
        else:
            lepT_veto = True

    lep_veto = lepW_veto and lepT_veto

    return lep_veto, lepW_veto, lepT_veto, lepT_candidates, lepW_candidate_es, lepW_candidate_mus#lep_sf

# Check if jet is an all-hadronic b* decay
def AllHadIdentifier(genparticles,lepveto):
    import GenParticleChecker
    from GenParticleChecker import GenParticleTree,GenParticleObj
    
    # Build the tree of gen particles that we care about
    particle_tree = GenParticleTree()
    bstars = []
    Ws = []
    tops = []
    quarks = []
    leptons = []
    prongs = [] # Final particles we'll check
    for i,p in enumerate(genparticles):
        # Internal class info
        this_gen_part = GenParticleObj(i,p)
        this_gen_part.SetStatusFlags()
        this_gen_part.SetPDGName(abs(this_gen_part.pdgId))
        
        # Add particles to tree and keep track of them in external lists
        if abs(this_gen_part.pdgId) == 24:# and this_gen_part.status == 22: # 22 means intermediate part of hardest subprocess, only other to appear is 52 (outgoing copy of recoiler, with changed momentum)
            particle_tree.AddParticle(this_gen_part)
            Ws.append(this_gen_part)

        # tops
        elif abs(this_gen_part.pdgId) == 6:
            particle_tree.AddParticle(this_gen_part)
            tops.append(this_gen_part)

        # b*
        elif abs(this_gen_part.pdgId) == 1005 and this_gen_part.status == 62:
            particle_tree.AddParticle(this_gen_part)
            bstars.append(this_gen_part)

        # leptons
        elif abs(this_gen_part.pdgId) in range(11,17):
            particle_tree.AddParticle(this_gen_part)
            leptons.append(this_gen_part)

        # quarks
        elif abs(this_gen_part.pdgId) in range(1,6):# and this_gen_part.status == 23:
            particle_tree.AddParticle(this_gen_part)
            quarks.append(this_gen_part)

        else: particle_tree.AddParticle(this_gen_part)

    pchain = {  'Hadronic W':particle_tree.FindChain('1005>24>1:5'),
                'Hadronic top':particle_tree.FindChain('1005>6>24>1:5'),
                'Leptonic W':particle_tree.FindChain('1005>24>11:16'),
                'Leptonic top':particle_tree.FindChain('1005>6>24>11:16'),
                'Leptonic b':particle_tree.FindChain('1005>6>5>11:16')}
    
    # if pchain['Hadronic W'] != False and pchain['Hadronic top'] != False and pchain['Leptonic b'] != False and not lepveto:
    #     particle_tree.PrintTree(ievent,options=['pdgId','status','vect:Pt'])
    #     raw_input('waiting')

    return pchain,particle_tree

    # if pchain['Hadronic W'] != False and pchain['Hadronic top'] != False and pchain['Leptonic b'] != False: return True
    # else: return False

def SFe_Lookup(year,sf_file,pt,eta):
    sf_hist = sf_file.Get(year+'_Electron_veto_sf')
    return sf_hist.GetBinContent(sf_hist.GetXaxis().FindBin(eta),sf_hist.GetYaxis().FindBin(pt))

def SFmu_Lookup(year,ISOorID,sf_file,pt,eta):
    sf_hist = sf_file.Get(year+'_Muon_'+ISOorID+'_veto_sf')
    if year == "16":
        return sf_hist.GetBinContent(sf_hist.GetXaxis().FindBin(eta),sf_hist.GetYaxis().FindBin(pt))
    else:
        return sf_hist.GetBinContent(sf_hist.GetXaxis().FindBin(pt),sf_hist.GetYaxis().FindBin(abs(eta)))


#This is just a quick function to automatically make a tree
#This is used right now to automatically output branches used to validate the cuts used in a run
def Make_Trees(Floats,name="Tree"):
    t = TTree(name, name);
    print "Booking trees"
    for F in Floats.keys():
        t.Branch(F, Floats[F], F+"/D")
    return t

# Quick way to get extrapolation uncertainty
def ExtrapUncert_Lookup(pt,purity,year):
    if year == '16':
        if purity == 'HP':
            x = 0.085
        elif purity == 'LP':
            x = 0.039
        elif purity == False:
            return 0
        extrap_uncert = x*log(pt/200)
        return extrap_uncert
    elif year == '17' or year == '18':
        if pt > 350 and pt < 600:
            return 0.13
        else:
            if purity == 'HP':
                x = 0.085
            elif purity == 'LP':
                x = 0.039
            elif purity == False:
                return 0
            extrap_uncert = x*log(pt/200)
            return extrap_uncert

def dictToLatexTable(dict2convert,outfilename,roworder=[],columnorder=[],caption=''):
    # First set of keys are row, second are column
    if len(roworder) > 0:
        rows = roworder
    else:
        rows = dict2convert.keys()
        rows.sort()

    if len(columnorder) > 0:
        columns = columnorder
    else:
        columns = []
        for r in rows:
            thesecolumns = dict2convert[r].keys()
            for c in thesecolumns:
                if c not in columns:
                    columns.append(c)
        columns.sort()

    latexout = open(outfilename,'w')
    latexout.write('\\begin{table}[] \n')
    latexout.write('\\adjustbox{center}{')
    latexout.write('\\begin{tabular}{|c|'+len(columns)*'c'+'|} \n')
    latexout.write('\\hline \n')

    column_string = ' &'
    for c in columns:
        column_string += str(c)+'\t& '
    column_string = column_string[:-2]+'\\\ \n'
    latexout.write(column_string)

    latexout.write('\\hline \n')
    for r in rows:
        row_string = '\t'+r+'\t& '
        for c in columns:
            if c in dict2convert[r].keys():
                row_string += str(dict2convert[r][c])+'\t& '
            else:
                print 'Could not find key "'+c+'" in row '+r
                row_string += '- \t& '
        row_string = row_string[:-2]+'\\\ \n'
        latexout.write(row_string)

    latexout.write('\\hline \n')
    latexout.write('\\end{tabular} \n')
    latexout.write('} \n')  # close off adjustbox
    latexout.write('\\caption{'+caption+'} \n')
    latexout.write('\\end{table}')
    latexout.close()

#Makes the blue pull plots
def Make_Pull_plot( DATA,BKG,BKGUP,BKGDOWN ):
    pull = DATA.Clone("pull")
    pull.Add(BKG,-1)
    sigma = 0.0
    FScont = 0.0
    BKGcont = 0.0
    for ibin in range(1,pull.GetNbinsX()+1):
        FScont = DATA.GetBinContent(ibin)
        BKGcont = BKG.GetBinContent(ibin)
        if FScont>=BKGcont:
            FSerr = DATA.GetBinErrorLow(ibin)
            BKGerr = abs(BKGUP.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        if FScont<BKGcont:
            FSerr = DATA.GetBinErrorUp(ibin)
            BKGerr = abs(BKGDOWN.GetBinContent(ibin)-BKG.GetBinContent(ibin))
        sigma = sqrt(FSerr*FSerr + BKGerr*BKGerr)
        if FScont == 0.0:
            pull.SetBinContent(ibin, 0.0 )  
        else:
            if sigma != 0 :
                pullcont = (pull.GetBinContent(ibin))/sigma
                pull.SetBinContent(ibin, pullcont)
            else :
                pull.SetBinContent(ibin, 0.0 )
    return pull


# Built to wait for condor jobs to finish and then check that they didn't fail
# The script that calls this function will quit if there are any job failures
# listOfJobs input should be whatever comes before '.listOfJobs' for the set of jobs you submitted
def WaitForJobs( listOfJobs ):
    # Runs grep to count the number of jobs - output will have non-digit characters b/c of wc
    preNumberOfJobs = subprocess.check_output('grep "python" '+listOfJobs+'.listOfJobs | wc -l', shell=True)
    commentedNumberOfJobs = subprocess.check_output('grep "# python" '+listOfJobs+'.listOfJobs | wc -l', shell=True)

    # Get rid of non-digits and convert to an int
    preNumberOfJobs = int(filter(lambda x: x.isdigit(), preNumberOfJobs))
    commentedNumberOfJobs = int(filter(lambda x: x.isdigit(), commentedNumberOfJobs))
    numberOfJobs = preNumberOfJobs - commentedNumberOfJobs

    finishedJobs = 0
    # Rudementary progress bar
    while finishedJobs < numberOfJobs:
        # Count how many output files there are to see how many jobs finished
        # the `2> null.txt` writes the stderr to null.txt instead of printing it which means
        # you don't have to look at `ls: output_*.log: No such file or directory`
        finishedJobs = subprocess.check_output('ls output_*.log 2> null.txt | wc -l', shell=True)
        finishedJobs = int(filter(lambda x: x.isdigit(), finishedJobs))
        sys.stdout.write('\rProcessing ' + str(listOfJobs) + ' - ')
        # Print the count out as a 'progress bar' that refreshes (via \r)
        sys.stdout.write("%i / %i of jobs finished..." % (finishedJobs,numberOfJobs))
        # Clear the buffer
        sys.stdout.flush()
        # Sleep for one second
        time.sleep(1)


    print 'Jobs completed. Checking for errors...'
    numberOfTracebacks = subprocess.check_output('grep -i "Traceback" output*.log | wc -l', shell=True)
    numberOfSyntax = subprocess.check_output('grep -i "Syntax" output*.log | wc -l', shell=True)

    numberOfTracebacks = int(filter(lambda x: x.isdigit(), numberOfTracebacks))
    numberOfSyntax = int(filter(lambda x: x.isdigit(), numberOfSyntax))

    # Check there are no syntax or traceback errors
    # Future idea - check output file sizes
    if numberOfTracebacks > 0:
        print str(numberOfTracebacks) + ' job(s) failed with traceback error'
        quit()
    elif numberOfSyntax > 0:
        print str(numberOfSyntax) + ' job(s) failed with syntax error'
        quit()
    else:
        print 'No errors!'

# Scales the up and down pdf uncertainty distributions to the nominal value to isolate the shape uncertainty
def PDFShapeUncert(nominal, up, down):
    upShape = up.Clone("Mtw")
    downShape = down.Clone("Mtw")
    upShape.Scale(nominal.Integral()/up.Integral())
    downShape.Scale(nominal.Integral()/down.Integral())

    return upShape, downShape

# Creates ratios between the events in up/down PDF distributions to nominal distribution and
# used the ratio to derive up/down xsec values for the given mass point
def PDFNormUncert(nominal, up, down, xsec_nominal):
    ratio_up = up.Integral()/nominal.Integral()
    ratio_down = down.Integral()/nominal.Integral()

    xsec_up = ratio_up*xsec_nominal
    xsec_down = ratio_down*xsec_nominal

    return xsec_up, xsec_down

# def DAK8_crosscheck(fromDAK8,fromEvent):
#     # Inputs are two lists of [pt, eta, phi]
    
#     for i in range(len(fromDAK8)):
#         if fromDAK8[i] != fromEvent[i]:

#             diff = abs(fromDAK8[i]-fromEvent[i])
#             if i == 2: # if phi
#                 if abs(fromDAK8[i]-fromEvent[i]) > math.pi:
#                     diff = 2*math.pi - abs(fromDAK8[i]-fromEvent[i])
                 

#             disc = diff/(abs(fromDAK8[i])/2+abs(fromEvent[i])/2)
            
#             if disc > 0.05 and i != 0:
#                 return False
#             elif disc > 0.1:
#                 return False

#     return True


def flatTag():
    r = random()
    return r


def linTag(a=1.):
    r = random()
    # Derived by inverting Integral(mx+b,{x,0,x})
    lin = a*math.sqrt(r)
    # norm = (a/3)

    # print quad

    return lin#/norm

def quadTag(a=1.):
    r = random()
    # Derived by inverting Integral(ax^2+bx+c,{x,0,x})
    onethird = 1./3.
    quad = a*math.pow(r,onethird)

    return quad
