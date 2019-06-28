import ROOT
from ROOT import *
import optimize_cut
from optimize_cut import optimizeCut
import sys

year = sys.argv[1]

# Scan over cuts and signal points and plot optimzation points

plane = TH2F('deltaYopt','|#Delta Y|'+' optimization plane',20,0,20,21,0,21)
plane.GetXaxis().SetTitle('Mass point (GeV)')
plane.GetYaxis().SetTitle('Cut point')

ixbin = 1
for hand in ['LH','RH']:
    for signal in range(1200,3200,200):
        if year != '16' and hand == 'LH' and signal == 2800:
            ixbin+=1
            continue
        iybin = 1
        for cut in range(1000,3100,100):
            if cut >= signal or (cut+600)<signal:
                iybin+=1
            else:
                optimalPoint = optimizeCut('deltaY-'+str(cut), hand+str(signal), year)
                plane.SetBinContent(ixbin,iybin,optimalPoint)
                iybin += 1
        ixbin += 1
            
ixbin = 1
for hand in ['LH','RH']:
    for signal in range(1200,3200,200):
        plane.GetXaxis().SetBinLabel(ixbin, hand+str(signal))
        ixbin += 1

iybin = 1
for cut in range(1000,3100,100):
    plane.GetYaxis().SetBinLabel(iybin, str(cut))
    iybin += 1

plane.GetZaxis().SetTitle('|#Delta Y| optimization point')
plane.GetXaxis().SetTitleOffset(1.2)
plane.SetMaximum(2.0)
plane.SetMinimum(0.6)


# gROOT.SetBatch(kFALSE)
cPlane = TCanvas('cPlane','cPlane',900,700)
cPlane.cd()
cPlane.SetRightMargin(0.2)
plane.Draw('colz text')

cPlane.Print('optimization_studies/deltaYopt_'+year+'.pdf','pdf')