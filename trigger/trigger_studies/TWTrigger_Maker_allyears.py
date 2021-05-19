

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

import os, array, glob, math, ROOT, sys
sys.path.append('../../')
import CMS_lumi, tdrstyle
from array import *
from ROOT import *
from optparse import OptionParser

gROOT.SetBatch(True)

parser = OptionParser()

parser.add_option('-s', '--set', metavar='F', type='string', action='store',
                default   =   'data',
                dest      =   'set',
                help      =   'dataset (ie data,ttbar etc)')
# parser.add_option('-y', '--y', metavar='F', type='string', action='store',
#                 default   =   '16',
#                 dest      =   'year',
#                 help      =   '16, 17')
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

tdrstyle.setTDRStyle()
gStyle.SetLegendFont(42)
gStyle.SetErrorX(0)
gStyle.SetEndErrorSize(5)
leg = TLegend(0.65, 0.65, 0.85, 0.9)
leg.SetFillColor(0)
leg.SetBorderSize(0)

# tname = ''
# tname = options.tname.split(',')
# for iname in range(0,len(tname)):
#     tname+=tname[iname]
#     if iname!=len(tname)-1:
#         tname+='OR'

c1 = TCanvas('c1', '', 700, 500)
stuff = []
colors = [kBlack,kGreen+2,kOrange-3]
Tline = TLine(1200.0, 0.75, 1200, 1.01)
Tline.SetLineColor(kBlack)
Tline.SetLineStyle(2)
Tarrow = TArrow(1200,0.8,1700,0.8)
Tarrow.SetLineColor(kBlack)

for i,y in enumerate(['16','17','18']):

    # Trigger
    if y == '16':
        tname = 'HLT_PFHT800ORHLT_PFHT900ORHLT_PFJet450'
        pretrig_string = 'HLT_Mu50'
        # btagtype = 'btagCSVV2'
    elif y == '17' or y == '18':
        tname = 'HLT_PFHT1050ORHLT_PFJet500ORHLT_AK8PFJet380_TrimMass30ORHLT_AK8PFJet400_TrimMass30'
        pretrig_string = 'HLT_Mu50'

    if options.disc != '': disc_string = '_'+options.disc
    else: disc_string = ''
    # Trigfile = ROOT.TFile( "Triggerweight"+options.year+"_"+options.set+disc_string+'_pre_'+pretrig_string+".root", "recreate" )
    infile = ROOT.TFile("TWTrigger"+y+'_'+options.set+'_'+tname+'_pre_'+pretrig_string+".root")
    pres = infile.Get('Res'+disc_string+'_pre')
    posts = infile.Get('Res'+disc_string) 

    stuff.extend([infile,pres,posts])

    titles = ';m_{jj} [GeV];Efficiency'
    ranges = [0,4000]
    name = 'Res'

    print tname + '_' + name
    print 'Full integral: ' + str(posts.Integral()/pres.Integral())
    print 'Partial integral: ' + str(posts.Integral(posts.FindBin(1500),posts.FindBin(4000))/pres.Integral(pres.FindBin(1500),pres.FindBin(4000)))


    # Create the outfiles that will store fit and sigma data for use later
    
    HT = posts
    HTpre = pres

    TR = HT.Clone()
    stuff.append(TR)
    TR.Divide(TR,HTpre,1.0,1.0,'B')

    for x in range(1,TR.GetNbinsX()+1):
        if TR.GetBinContent(x) <= 0 and TR.GetBinCenter(x) >= 2000:
            TR.SetBinContent(x,1)
        TR.SetBinError(x,0.5*(1-TR.GetBinContent(x)))

    leg.AddEntry(TR , '20'+y+' data', 'pe')#tname.replace('OR',' OR '), 'p')

    c1.cd()
    
    TR.SetLineColor(colors[i])
    TR.SetMarkerColor(colors[i])
    TR.SetMaximum(1.01)
    TR.SetMinimum(0.75)
    TR.GetXaxis().SetRangeUser(ranges[0],ranges[1])
    TR.SetStats(0)
    TR.GetXaxis().SetTitleSize(0.05)
    TR.GetYaxis().SetTitleSize(0.05)
    TR.SetTitle(titles)
    
    TR.SetMarkerStyle(8)
    TR.SetMarkerSize(0.6)
    TR.GetXaxis().SetLabelSize(0.05)
    TR.GetYaxis().SetLabelSize(0.05)

    gPad.SetLeftMargin(.15)
    gPad.SetBottomMargin(.17) 
    gPad.SetRightMargin(.07)
    TR.GetYaxis().SetTitleOffset(1.05)
    TR.GetXaxis().SetTitleOffset(1.05)

    TR.Draw("same p e1")
    TR_err = TR.Clone()
    TR_err.SetMarkerSize(0)
    TR_err.SetMarkerStyle(1)
    TR_err.Draw("same e1")
    # Trigfile.cd()
    if y == '16': TR_16 = TR

TR_16.Draw('same p e1')
# Tline.SetMarkerStyle(0)
Tline.Draw()
Tarrow.Draw()

leg.AddEntry(Tline,'m_{jj} selection','l')
leg.Draw()
CMS_lumi.cmsTextSize = 1.1
CMS_lumi.extraText = ''
CMS_lumi.lumiTextSize = 0.9
CMS_lumi.cmsTextOffset = 0.24
CMS_lumi.relPosX = 0.03
CMS_lumi.relPosY = 0.05
CMS_lumi.CMS_lumi(c1, 2, 11)
c1.Print('plots_paper/Trigger_'+options.set+'_'+tname+disc_string+'_'+name+'.root', 'root')
c1.Print('plots_paper/Trigger_'+options.set+'_'+tname+disc_string+'_'+name+'.pdf', 'pdf')
