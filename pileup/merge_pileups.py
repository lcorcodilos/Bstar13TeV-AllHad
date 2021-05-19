import ROOT
from ROOT import *

out = TFile('PileupData_latestJSON_2018.root','recreate')

fnom = TFile.Open('PileUp_data18True_nom.root')
fup = TFile.Open('PileUp_data18True_up.root')
fdown = TFile.Open('PileUp_data18True_down.root')

hnom = fnom.Get('pileup')
hup = fup.Get('pileup').Clone('pileup_plus')
hdown = fdown.Get('pileup').Clone('pileup_minus')

out.cd()
hnom.Write()
hup.Write()
hdown.Write()

out.Close()
fnom.Close()
fup.Close()
fdown.Close()
