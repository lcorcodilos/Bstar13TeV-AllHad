import ROOT, array, time, sys, subprocess, glob
from ROOT import *
import pickle, os
from optparse import OptionParser
import Bstar_Functions_local
from Bstar_Functions_local import *

gROOT.SetBatch(kTRUE)


parser = OptionParser()

parser.add_option('-s', '--set', metavar='F', type='string', action='store',
                default   =   'singletop_tW',
                dest      =   'set',
                help      =   'Set name (will find all files with matching string)')
# parser.add_option('-y', '--year', metavar='F', type='string', action='store',
#                 default   =   '',
#                 dest      =   'year',
#                 help      =   'Year')
parser.add_option('-c', '--config', metavar='F', type='string', action='store',
                default   =   'configs/input_dataBsUnblind17.json',
                dest      =   'config',
                help      =   'Location of config from which to get binning for axes')
# parser.add_option('-m', '--mod', metavar='F', type='string', action='store',
#                 default   =   '',
#                 dest      =   'mod',
#                 help      =   'Modification to QCD name')
parser.add_option('-n', '--newOnly', action='store_true',
                default   =   False,
                dest      =   'newOnly',
                help      =   'Only produce smoothed histograms that do not exist already')


(options, args) = parser.parse_args()


# Setup
config = openJSON(options.config)
xname = 'mt'#'mh'
yname = 'mtw'#'mred'
rho_list = [2,3,4]

files = glob.glob('rootfiles/TWpreselection*%s*.root'%(options.set))

for fname in files:
    print 'Smoothing %s'%fname
    if options.newOnly and os.path.exists(fname.replace('preselection','smooth')):
        continue
    out = TFile.Open(fname.replace('preselection','smooth'),'RECREATE')
    f = TFile.Open(fname)
    all_hists = f.GetListOfKeys()
    for k in all_hists:
        kname = k.GetName()
        if 'MtwvMt' not in kname: continue
        print '\t%s'%kname
        h = f.Get(kname)
        if h.Integral() <= 0: continue
        for r in rho_list:
            h_smooth = smooth(h,r,5,config,nevents = 10000000,scale=1)
        out.cd()
        h_smooth.Write()

    out.Close()
    f.Close()