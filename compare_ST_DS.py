import ROOT
import os

alpha_path = '/uscms_data/d3/lcorcodi/BStar13TeV/CMSSW_10_2_13/src/2DAlphabet'
if not os.path.exists(alpha_path):
    alpha_path = '/home/lucas/CMS/2DAlphabet/'

for y in ['16','17','18']:
    f_normal = ROOT.TFile.Open(alpha_path+"dataSRTTv23UNBLIND_RH3800_PAS/SR%s/organized_hists.root"%y)
    f_DS = ROOT.TFile.Open(alpha_path+"ST_DS/SR%s/organized_hists.root"%y)

    for t in ['','B']:
        for h in ['pass','fail']:
            print "singletop_tW%s_%s_FULL_SR%s"%(t,h,y)
            h_normal = f_normal.Get("singletop_tW%s_%s_FULL_SR%s"%(t,h,y))
            h_DS = f_normal.Get("singletop_tW%s_%s_FULL_SR%s"%(t,h,y))

            h_normal.ProjectionY().Draw("hist")
            h_DS.ProjectionY().Draw("same hist")

            raw_input('')
