

###################################################################
##                               ##
## Name: Tagrate_Maker_B.py                      ##
## Author: Kevin Nash                        ##
## Date: 5/28/2015                       ##
## Purpose: This program takes the root files created by     ##
##          TBTrigger.py and divides the histograms to create    ##
##      trigger turn on curves               ##
##                               ##
###################################################################

import os
import array
import glob
import math
import ROOT
import sys
from array import *
from ROOT import *
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
parser.add_option('-d', '--disc', metavar='F', type='string', action='store',
                  default   =   'ttags',
                  dest      =   'disc',
                  help      =   'empty, untrig, or ttags')

parser.add_option('-t', '--tname', metavar='F', type='string', action='store',
                  default   =   'HLT_PFHT800,HLT_PFHT900,HLT_PFJet450', #For 2017 use 'HLT_PFHT780'
                  dest      =   'tname',
                  help      =   'trigger name')
parser.add_option('-p', '--pret', metavar='F', type='string', action='store',
                  default   =   'HLT_Mu50',#'HLT_PFHT475',
                  dest      =   'pret',
                  help      =   'pretrigger name')

(options, args) = parser.parse_args()


leg = TLegend(0.0, 0.0, 1.0, 1.0)
leg.SetFillColor(0)
leg.SetBorderSize(0)

tnameOR = ''
tname = options.tname.split(',')
for iname in range(0,len(tname)):
    tnameOR+=tname[iname]
    if iname!=len(tname)-1:
        tnameOR+='OR'



Trigfile = ROOT.TFile( "Triggerweight_"+options.set+options.year+options.disc+'_pre_'+options.pret+".root", "recreate" )
# for ifile in range(0,len(trigs)) :

infile = ROOT.TFile("TWTrigger"+options.set+options.year+tnameOR+'_pre_'+options.pret+".root")

HT = infile.Get('Ht'+options.disc)
HTpre = infile.Get('Htpre'+options.disc)
HT.Rebin(5)
HTpre.Rebin(5)

pres = [
    infile.Get('Htpre'+options.disc),
    infile.Get('Respre')
    ]
posts = [
    infile.Get('Ht'+options.disc),
    infile.Get('Res')
    ] 
titles = [
    ';p_{T_{jet1}} + p_{T_{jet2}} (GeV);Efficiency',
    ';M_{jet1+jet2} (GeV);Efficiency'
    ]
ranges = [
    [300,2000],
    [400,4000]]
name = ['Ht','Res']

print tnameOR
print 'Full integral: ' + str(HT.Integral()/HTpre.Integral())
print 'Partial integral: ' + str(HT.Integral(HT.FindBin(550),HT.FindBin(2000))/HTpre.Integral(HT.FindBin(550),HT.FindBin(2000)))

for h in range(0,len(posts)):
    # Create the outfiles that will store fit and sigma data for use later
    c1 = TCanvas('c1', '', 700, 500)
    HT = posts[h]
    HTpre = pres[h]

    TR = HT.Clone()
    TR.Divide(TR,HTpre,1.0,1.0,'B')

    leg.AddEntry(TR , tnameOR.replace('OR',' OR '), 'p')

    # Tline = TLine(600.0, 0.5, 820.0, 1.01)
    # Tline.SetLineColor(kRed)
    # Tline.SetLineStyle(2)
    c1.cd()
    
    TR.SetLineColor(1)
    TR.SetMarkerColor(1)
    TR.SetMaximum(1.01)
    TR.SetMinimum(0.2)
    TR.GetXaxis().SetRangeUser(ranges[h][0],ranges[h][1])
    TR.SetStats(0)
    TR.SetTitle(titles[h])
    TR.SetMarkerStyle(8)

    TR.Draw("p")

    gPad.SetLeftMargin(.15)
    gPad.SetBottomMargin(.17) 
    TR.GetYaxis().SetTitleOffset(0.8)

    Trigfile.cd()
    TR.Write("TriggerWeight_"+tnameOR+'_'+name[h])
    # c3 = TCanvas('c3', '', 700, 500)
    # TR.Draw("")
    c1.Print('plots/Trigger'+options.year+'_'+tnameOR+options.disc+'_'+name[h]+'_'+options.pret+'.root', 'root')
    c1.Print('plots/Trigger'+options.year+'_'+tnameOR+options.disc+'_'+name[h]+'_'+options.pret+'.pdf', 'pdf')

    # #Tline.Draw()
    # c1.Print('plots/Trigger_TEMP'+options.disc+'.root', 'root')
    # c1.Print('plots/Trigger_TEMP'+options.disc+'.pdf', 'pdf')

    # cLeg = TCanvas('cLeg', '', 700, 200)
    # leg.Draw()
    # cLeg.Print('plots/Trigger_TEMP_legend.pdf'+options.disc, 'pdf')







