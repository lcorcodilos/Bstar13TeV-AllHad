import ROOT
import os
ROOT.gStyle.SetOptStat(0)

alpha_path = '/uscms_data/d3/lcorcodi/BStar13TeV/CMSSW_10_2_13/src/2DAlphabet'
if not os.path.exists(alpha_path):
    alpha_path = '/home/lucas/CMS/2DAlphabet/'

c = ROOT.TCanvas('c','c',1000,1000)
c.Divide(2,3)
i = 0
stuff = []
for y in ['16','17','18']:
    f_normal_name = alpha_path+"dataSRTTv23UNBLIND_RH3800_PAS/SR%s/organized_hists.root"%y
    f_DS_name = alpha_path+"ST_DS/SR%s/organized_hists.root"%y
    print f_normal_name
    print f_DS_name
    f_normal = ROOT.TFile.Open(f_normal_name)
    f_DS = ROOT.TFile.Open(f_DS_name)
    stuff.extend([f_normal,f_DS])

    for t in ['','B']:
        for h in ['pass']:
            i+=1
            c.cd(i)
            h_normal_name = "singletop_tW%s_%s_FULL_SR%s"%(t,h,y)
            h_DS_name = "singletop_tW%s_%s_FULL_SR%s"%(t,h,y)
            print h_normal_name
            print h_DS_name
            h_normal = f_normal.Get(h_normal_name)
            h_DS = f_DS.Get(h_DS_name)
            stuff.extend([h_normal,h_DS])

            ROOT.gPad.SetLogy()

            h_DS_projy = h_DS.ProjectionY('ST_tW%s %s %s - DS'%(t,h,y))
            h_DS_projy.SetTitle('ST_tW%s %s %s'%(t,h,y))
            h_DS_projy.SetLineColor(ROOT.kRed)
            h_DS_projy.Scale(1/h_DS_projy.Integral())
            h_DS_projy.SetMaximum(h_DS_projy.GetMaximum()*1.2)
            h_DS_projy.Draw("histe")

            h_normal_projy = h_normal.ProjectionY('ST_tW%s %s %s - normal'%(t,h,y))
            h_normal_projy.SetLineColor(ROOT.kBlue)
            h_normal_projy.Scale(1/h_normal_projy.Integral())
            h_normal_projy.SetMaximum(h_normal_projy.GetMaximum()*1.2)
            h_normal_projy.Draw("same pe")

            l = ROOT.TLegend(0.7,0.7,0.9,0.9)
            l.AddEntry(h_DS_projy,'tW%s DS'%t,'le')
            l.AddEntry(h_normal_projy,'tW%s'%t,'pe')
            l.Draw()
            stuff.extend([h_normal_projy,h_DS_projy,l])

raw_input('')
