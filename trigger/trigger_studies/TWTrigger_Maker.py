

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
                default   =   '',
                dest      =   'disc',
                help      =   'empty, untrig, or ttags')
# parser.add_option('-t', '--tname', metavar='F', type='string', action='store',
#                   default   =   'HLT_PFHT800,HLT_PFHT900,HLT_PFJet450', #For 2017 use ''
#                   dest      =   'tname',
#                   help      =   'trigger name')
# parser.add_option('-p', '--pret', metavar='F', type='string', action='store',
#                   default   =   'HLT_Mu50',#'HLT_PFHT475',
#                   dest      =   'pret',
#                   help      =   'pretrigger name')

(options, args) = parser.parse_args()

leg = TLegend(0.0, 0.0, 1.0, 1.0)
leg.SetFillColor(0)
leg.SetBorderSize(0)

# tname = ''
# tname = options.tname.split(',')
# for iname in range(0,len(tname)):
#     tname+=tname[iname]
#     if iname!=len(tname)-1:
#         tname+='OR'

# Trigger
if options.year == '16':
    tname = 'HLT_PFHT800ORHLT_PFHT900ORHLT_PFJet450'
    pretrig_string = 'HLT_Mu50'
    # btagtype = 'btagCSVV2'
elif options.year == '17' or options.year == '18':
    tname = 'HLT_PFHT1050ORHLT_PFJet500'
    pretrig_string = 'HLT_Mu50'

if options.disc != '': disc_string = '_'+options.disc
else: disc_string = ''
Trigfile = ROOT.TFile( "Triggerweight"+options.year+"_"+options.set+disc_string+'_pre_'+pretrig_string+".root", "recreate" )
infile = ROOT.TFile("TWTrigger"+options.year+'_'+options.set+'_'+tname+'_pre_'+pretrig_string+".root")

pres = [
    infile.Get('Ht_pre'),
    infile.Get('Res'+disc_string+'_pre')
    ]
posts = [
    infile.Get('Ht'),
    infile.Get('Res'+disc_string)
    ] 
titles = [
    ';p_{T_{jet1}} + p_{T_{jet2}} (GeV);Efficiency',
    ';M_{jet1+jet2} (GeV);Efficiency'
    ]
ranges = [
    [400,4000],
    [400,4000]]
name = ['Ht','Res']

for h in range(0,len(posts)):
    print tname + '_' + name[h]
    print 'Full integral: ' + str(posts[h].Integral()/pres[h].Integral())
    print 'Partial integral: ' + str(posts[h].Integral(posts[h].FindBin(600),posts[h].FindBin(2000))/pres[h].Integral(pres[h].FindBin(600),pres[h].FindBin(2000)))


    # Create the outfiles that will store fit and sigma data for use later
    c1 = TCanvas('c1', '', 700, 500)
    HT = posts[h]
    HTpre = pres[h]

    TR = HT.Clone()
    TR.Divide(TR,HTpre,1.0,1.0,'B')

    for x in range(1,TR.GetNbinsX()+1):
        TR.SetBinError(x,0.5*(1-TR.GetBinContent(x)))

    leg.AddEntry(TR , tname.replace('OR',' OR '), 'p')

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
    TR.SetMarkerSize(0.5)

    TR.Draw("pe")

    gPad.SetLeftMargin(.15)
    gPad.SetBottomMargin(.17) 
    TR.GetYaxis().SetTitleOffset(0.8)

    Trigfile.cd()
    TR.Write("TriggerWeight_"+tname+'_'+name[h])
    # c3 = TCanvas('c3', '', 700, 500)
    # TR.Draw("")
    c1.Print('plots/Trigger'+options.year+'_'+tname+disc_string+'_'+name[h]+'_'+pretrig_string+'.root', 'root')
    c1.Print('plots/Trigger'+options.year+'_'+tname+disc_string+'_'+name[h]+'_'+pretrig_string+'.pdf', 'pdf')

    # #Tline.Draw()
    # c1.Print('plots/Trigger_TEMP'+options.disc+'.root', 'root')
    # c1.Print('plots/Trigger_TEMP'+options.disc+'.pdf', 'pdf')

    # cLeg = TCanvas('cLeg', '', 700, 200)
    # leg.Draw()
    # cLeg.Print('plots/Trigger_TEMP_legend.pdf'+options.disc, 'pdf')







