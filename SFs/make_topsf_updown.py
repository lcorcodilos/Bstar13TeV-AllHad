import ROOT
from ROOT import *

oldTopsfFile = TFile.Open("SF-deepak8.root")
newTopsfFile = TFile("TopSFs.root","RECREATE")

sf_names = ['fj_decorr_nn_toploosesyst','fj_decorr_nn_topmediumsyst','fj_decorr_nn_toptightsyst','fj_decorr_nn_topvery_tightsyst',
			'fj_nn_toploosesyst','fj_nn_topmediumsyst','fj_nn_toptightsyst','fj_nn_topvery_tightsyst']

for sf in sf_names:
	nom = oldTopsfFile.Get(sf)
	up = TGraph()
	up.SetName(sf+'_up')
	down = TGraph()
	down.SetName(sf+'_down')

	for i in range(nom.GetN()):
		up.SetPoint(i,nom.GetX()[i],nom.GetY()[i]+nom.GetErrorY(i))
		down.SetPoint(i,nom.GetX()[i],nom.GetY()[i]-nom.GetErrorY(i))

	newTopsfFile.cd()
	nom.Write()
	up.Write()
	down.Write()

newTopsfFile.Close()