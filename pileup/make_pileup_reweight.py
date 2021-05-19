#######################################################
# make_pileup_reweight.py - Lucas Corcodilos, 10/5/18 #
#######################################################

import ROOT
from ROOT import *
import sys
sys.path.append('../')

from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event

import Bstar_Functions_local
from Bstar_Functions_local import *

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-s', '--set', metavar='F', type='string', action='store',
                    default   =   '',
                    dest      =   'set',
                    help      =   'dataset (ie data,ttbar etc)')
parser.add_option('-y', '--year', metavar='F', type='string', action='store',
                    default   =   '',
                    dest      =   'year',
                    help      =   'Year 16,17,18')
(options, args) = parser.parse_args()

# Setup output file and npv histograms
outfile = TFile('PileUp_Ratio_'+options.set+options.year+'.root','RECREATE')
outfile.cd()

# Pick out the proper data to develop a ratio with
if options.year == '16':
    print 'Using 2016 pileup file'
    data_file = TFile.Open('../PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/PileupData_GoldenJSON_Full2016.root')
elif options.year == '17':
    print 'Using 2017 pileup file'
    data_file = TFile.Open('../PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/pileup_Cert_294927-306462_13TeV_PromptReco_Collisions17_withVar.root')
elif options.year == '18':
    print 'Using 2018 pileup file'
    data_file = TFile.Open('PileupData_latestJSON_2018.root')

dataPU = data_file.Get('pileup')
dataPUup = data_file.Get('pileup_plus')
dataPUdown = data_file.Get('pileup_minus')

# dataPU.Sumw2()
# dataPUup.Sumw2()
# dataPUdown.Sumw2()

# Make the ones for options.set
npvtruehistUW       = ROOT.TH1F("npvtruehistUW", "npvtruehistUW",  dataPU.GetNbinsX(), dataPU.GetXaxis().GetXmin(), dataPU.GetXaxis().GetXmax() )
npvtruehistUW.Sumw2()

npvhistUW           = ROOT.TH1F("npvhistUW",     "npvhistUW",  dataPU.GetNbinsX(), dataPU.GetXaxis().GetXmin(), dataPU.GetXaxis().GetXmax() )
npvhistUW.Sumw2()

# Open up the nanoAOD
file_string = Load_jetNano(options.set,options.year)
inFile = TFile.Open(file_string)

inTree = inFile.Get("Events")
inTree = InputTree(inTree,None)
treeEntries = inTree.entries

# Begin looping over entries
count = 0
for entry in range(treeEntries):
    count   =   count + 1
    if count % 100000 == 0 :
        print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/treeEntries) + '% -- '

    event = Event(inTree, entry)

    # Fill booked histograms
    npvtruehistUW.Fill(inTree.readBranch('Pileup_nTrueInt'))
    npvhistUW.Fill(inTree.readBranch('Pileup_nPU'))

# Write out the histograms 
outfile.cd()
npvtruehistUW.Write()
npvhistUW.Write()


# Normalize everything
dataPU.Scale(1./dataPU.Integral())
dataPUup.Scale(1./dataPUup.Integral())
dataPUdown.Scale(1./dataPUdown.Integral())

npvtruehistUW.Scale(1./npvtruehistUW.Integral())
npvhistUW.Scale(1./npvhistUW.Integral())

outfile.cd()

# Clone, divide, and write the six different shapes
pileup_reweight_true = dataPU.Clone("Pileup_true_Ratio")
pileup_reweight_true.Divide(npvtruehistUW)
pileup_reweight_true.Write()

pileup_reweight_true_up = dataPUup.Clone("Pileup_true_Ratio_up")
pileup_reweight_true_up.Divide(npvtruehistUW)
pileup_reweight_true_up.Write()

pileup_reweight_true_down = dataPUdown.Clone("Pileup_true_Ratio_down")
pileup_reweight_true_down.Divide(npvtruehistUW)
pileup_reweight_true_down.Write()

pileup_reweight = dataPU.Clone("Pileup_Ratio")
pileup_reweight.Divide(npvhistUW)
pileup_reweight.Write()

pileup_reweight_up = dataPUup.Clone("Pileup_Ratio_up")
pileup_reweight_up.Divide(npvhistUW)
pileup_reweight_up.Write()

pileup_reweight_down = dataPUdown.Clone("Pileup_Ratio_down")
pileup_reweight_down.Divide(npvhistUW)
pileup_reweight_down.Write()

dataPU.SetName('data_nom')
dataPUup.SetName('data_up')
dataPUdown.SetName('data_down')

dataPU.Write()
dataPUup.Write()
dataPUdown.Write()

npvtruehistUW.Write()
npvhistUW.Write()
