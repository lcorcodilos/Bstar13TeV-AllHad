import ROOT, math
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(ROOT.kInvertedDarkBodyRadiator)

old = '../temp/bs_rootfiles/TWpreselection%s_data_tau32medium_default.root'
new = 'rootfiles/TWpreselection%s_data_tau32medium_default.root'

c = ROOT.TCanvas('c','c',1000,800)
c.Divide(2,2)

i = 0
stuff = []
for y in ['17','18']:
    f_old = ROOT.TFile.Open(old%y)
    f_new = ROOT.TFile.Open(new%y)
    stuff.extend([f_old,f_new])

    for hname in ['MtwvMtPass','MtwvMtFail']:
        i+=1
        h_old = f_old.Get(hname)
        h_new = f_new.Get(hname)
        stuff.extend([h_old,h_new])

        print ('%s %s: %s'%(hname.replace('MtwvMt',''),y,h_new.Integral()/h_old.Integral()))
        h_ratio = h_old.Clone()
        h_ratio.Add(h_new,-1)
        # h_ratio.Divide(h_new)
        for ix in range(1,h_ratio.GetNbinsX()+1):
            for iy in range(1,h_ratio.GetNbinsY()+1):
                if h_new.GetBinContent(ix,iy) != 0:
                    h_ratio.SetBinContent(ix,iy,h_ratio.GetBinContent(ix,iy)/math.sqrt(h_new.GetBinContent(ix,iy)))
                else:
                    h_ratio.SetBinContent(ix,iy,0)#-1*h_ratio.GetBinContent(ix,iy))

        h_ratio.GetZaxis().SetTitle('(old-new)/#sqrt{new}')
        h_ratio.SetMaximum(3.0)
        h_ratio.SetTitle('%s 20%s'%(hname,y))
        h_ratio.SetTitleOffset(0.3)
        stuff.append(h_ratio)
        c.cd(i)
        ROOT.gPad.SetRightMargin(0.15)
        h_ratio.Draw('colz')

raw_input('')