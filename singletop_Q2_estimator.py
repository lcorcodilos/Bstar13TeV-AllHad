import ROOT
from ROOT import TFile

for s in ['tW','tWB']:
    for r in ['default','sideband','ttbar']:
        nom_file = TFile.Open('rootfiles/TWpreselection16_singletop_'+s+'_tau32medium_'+r+'.root')
        up_file = TFile.Open('rootfiles/TWpreselection16_singletop_'+s+'-scaleup_tau32medium_'+r+'.root')
        down_file = TFile.Open('rootfiles/TWpreselection16_singletop_'+s+'-scaledown_tau32medium_'+r+'.root')

        # for p in ['Pass','Fail']:
        nom_pass = nom_file.Get('MtwvMtPass')
        up_pass = up_file.Get('MtwvMtPass')
        down_pass = down_file.Get('MtwvMtPass')
        nom_fail = nom_file.Get('MtwvMtFail')
        up_fail = up_file.Get('MtwvMtFail')
        down_fail = down_file.Get('MtwvMtFail')

        nom = nom_pass.Integral()+nom_fail.Integral()
        up = up_pass.Integral()+up_fail.Integral()
        down = down_pass.Integral()+down_fail.Integral()

        up_err = abs(nom-up)/nom
        down_err = abs(nom-down)/nom

        print '%s,%s = +%.2f/-%.2f' % (s,r,up_err,down_err)

            # nom_py = nom.ProjectionY('nom_py')
            # up_py = up.ProjectionY('up_py')
            # down_py = down.ProjectionY('down_py')

            # nom_py.Rebin(2)
            # up_py.Rebin(2)
            # down_py.Rebin(2)

            # nom_py.SetMaximum(150)

            # nom_py.SetLineColor(ROOT.kBlack)
            # nom_py.SetFillColor(ROOT.kYellow)
            # nom_py.SetTitle('%s,%s,%s'%(s,r,p))
            # up_py.SetLineColor(ROOT.kRed)
            # down_py.SetLineColor(ROOT.kBlue)
            
            # nom_py.Draw('hist')
            # up_py.Draw('samehist')
            # down_py.Draw('samehist')

            # raw_input('')
