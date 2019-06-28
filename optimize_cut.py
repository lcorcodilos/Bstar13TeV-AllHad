import math, sys
import ROOT
from ROOT import *

gStyle.SetOptStat(0)
gStyle.SetLegendFillColor(0)
gROOT.SetBatch(kTRUE)

def setPad(pad,top=False,bottom=False):
    if top:
        pad.SetBottomMargin(0.03)
        pad.SetTopMargin(0.1)
    elif bottom:
        pad.SetBottomMargin(0.2)
        pad.SetTopMargin(0.0)
    else:
        pad.SetBottomMargin(0.0)
        pad.SetTopMargin(0.0)
    
    pad.SetLeftMargin(0.16)
    pad.SetRightMargin(0.05)
    
    pad.Draw()


def optimizeCut(histToOptimize,signalToOptimize, year):
    sigyear = year
    if year == '18':
        sigyear = '17'

    files = {
        'signal'+signalToOptimize: TFile.Open('rootfiles/TWvariables'+sigyear+'_signal'+signalToOptimize+'_tau32medium_default.root'),
        'QCD': TFile.Open('rootfiles/TWvariables'+year+'_QCD_tau32medium_default.root'),
        'ttbar': TFile.Open('rootfiles/TWvariables'+year+'_ttbar_tau32medium_default.root'),
        'singletop_tW': TFile.Open('rootfiles/TWvariables'+year+'_singletop_tW_tau32medium_default.root'),
        'singletop_tWB': TFile.Open('rootfiles/TWvariables'+year+'_singletop_tWB_tau32medium_default.root')
    }

    hists = {}
    for f in files.keys():
        if 'deltaY' in histToOptimize:
            mtwcut = int(histToOptimize.split('-')[1])
            thish = files[f].Get('MtwvsdeltaY')
            cutbin = thish.GetYaxis().FindBin(mtwcut)
            hists[f] = thish.ProjectionX(f+'_deltaY',cutbin,-1)

        else:
            hists[f] = files[f].Get(histToOptimize)

    # Optimize the user defined variable
    hists['TotalBkg'] = hists['QCD'].Clone('TotalBkg')
    hists['TotalBkg'].Add(hists['ttbar'])
    hists['TotalBkg'].Add(hists['singletop_tW'])
    hists['TotalBkg'].Add(hists['singletop_tWB'])

    cDists = TCanvas('cDists','cDists',800,700)
    cDists.cd()
    hists['TotalBkg'].SetLineColor(kBlack)
    hists['signal'+signalToOptimize].SetLineColor(kBlue)
    hists['TotalBkg'].DrawNormalized('histe')
    hists['signal'+signalToOptimize].DrawNormalized('samehist')


    # Now do cumulative
    hists['TotalBkg_cumulative'] = hists['TotalBkg'].GetCumulative()
    hists['signal'+signalToOptimize+'_cumulative'] = hists['signal'+signalToOptimize].GetCumulative()
    hists['SoverSqrtB'] = hists['signal'+signalToOptimize+'_cumulative'].Clone('SoverSqrtB')

    for i in range(1,hists['SoverSqrtB'].GetNbinsX()+1):
        thisbincontent = hists['SoverSqrtB'].GetBinContent(i)
        if hists['TotalBkg_cumulative'].GetBinContent(i) > 0:
            newbincontent = thisbincontent/math.sqrt(hists['TotalBkg_cumulative'].GetBinContent(i))
        else:
            newbincontent = 0
        hists['SoverSqrtB'].SetBinContent(i,newbincontent)

    print 'Maximum at ' +str(hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin()))

    cCumulative = TCanvas('cCumulative','cCumulative',800,700)
    cCumulative.cd()

    main = TPad(histToOptimize+'_main',histToOptimize+'_main',0, 0.33, 1, 1)
    sub = TPad(histToOptimize+'_sub',histToOptimize+'_sub',0, 0, 1, 0.3)
    setPad(main,top=True)
    setPad(sub,bottom=True)

    main.cd()

    hists['TotalBkg_cumulative'].SetLineColor(kBlack)
    hists['signal'+signalToOptimize+'_cumulative'].SetLineColor(kBlue)

    leg = TLegend(0.05,0.7,0.4,0.9)
    hists['TotalBkg_cumulative'].DrawNormalized('histe')
    hists['signal'+signalToOptimize+'_cumulative'].DrawNormalized('samehist')
    leg.AddEntry(hists['TotalBkg_cumulative'],'Total Background from MC','l')
    leg.AddEntry(hists['signal'+signalToOptimize+'_cumulative'],'Total Signal '+signalToOptimize+' from MC','l')


    hists['SoverSqrtB'].SetLineColor(kBlue)
    hists['SoverSqrtB'].SetTitle(";"+hists['TotalBkg'].GetXaxis().GetTitle()+";S/#sqrt{B}")
    hists['SoverSqrtB'].SetStats(0)

    LS = .08

    thismax = hists['SoverSqrtB'].GetMaximum()

    hists['SoverSqrtB'].GetYaxis().SetRangeUser(-1.1*thismax,1.1*thismax)
    hists['SoverSqrtB'].GetYaxis().SetTitleOffset(0.4)
    hists['SoverSqrtB'].GetXaxis().SetTitleOffset(0.9)
                 
    hists['SoverSqrtB'].GetYaxis().SetLabelSize(LS)
    hists['SoverSqrtB'].GetYaxis().SetTitleSize(LS)
    hists['SoverSqrtB'].GetYaxis().SetNdivisions(306)
    hists['SoverSqrtB'].GetXaxis().SetLabelSize(LS)
    hists['SoverSqrtB'].GetXaxis().SetTitleSize(LS)

    hists['SoverSqrtB'].GetXaxis().SetTitle(hists['TotalBkg'].GetXaxis().GetTitle())
    hists['SoverSqrtB'].GetYaxis().SetTitle("S/#sqrt{B}")
    sub.cd()
    # hists['SoverSqrtB'].GetXaxis().SetBinLabel(hists['SoverSqrtB'].GetMaximumBin(), "Max at "+str(hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin())))
    hists['SoverSqrtB'].Draw('hist')
    main.RedrawAxis()
    leg.Draw()

    # Highlight max bin and label it with value
    print 'TArrow %s %s %s %s'%(
        hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin()),
        hists['SoverSqrtB'].GetMaximum(),
        hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin()),
        0.0,
        )


    arrowToMax = TArrow(
        hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin()),
        hists['SoverSqrtB'].GetMaximum(),
        hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin()),
        0,
        )

    zeroLine = TLine(
        0,
        hists['SoverSqrtB'].GetXaxis().GetXmin(),
        hists['SoverSqrtB'].GetXaxis().GetXmax(),
        0)
    zeroLine.SetLineColor(kBlack)
    # 

    arrowLabel = TPaveLabel(
        hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin()),
        hists['SoverSqrtB'].GetMaximum()*-0.8,
        hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin()+10),
        hists['SoverSqrtB'].GetMaximum()*-0.3,
        "Max "+str(hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin()))
        )

    arrowToMax.SetLineColor(kBlack)
    arrowToMax.SetLineWidth(2)
    sub.cd()
    zeroLine.Draw()
    arrowToMax.Draw()
    arrowLabel.Draw()

    cCumulative.Print('optimization_studies/'+histToOptimize+'_'+signalToOptimize+'_'+year+'.pdf','pdf')

    return hists['SoverSqrtB'].GetBinCenter(hists['SoverSqrtB'].GetMaximumBin())