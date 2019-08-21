import ROOT
from ROOT import *

gStyle.SetOptStat(0)

years = ["16","17","18"]

c = TCanvas('c','c',1800,700)
c.Divide(3,1)

hists = {}
files = {}

for i,y in enumerate(years):
    c.cd(1+i)
    files[y] = TFile.Open("ttbar_"+y+".root")
    hists[y] = files[y].Get("prongCount").Clone("temp"+y)
    total = hists[y].Integral()

    print y

    for b in range(1,hists[y].GetNbinsX()+1):
        print "\t%s: %.2f " %(hists[y].GetXaxis().GetBinLabel(b),100.*hists[y].GetBinContent(b)/hists[y].Integral()) + '%'

    hists[y].SetTitle("Quarks in W-tagged tops jets in ttbar MC - "+y)

    hists[y].Draw("hist")

c.Print("summary_ttbar.png","png")
