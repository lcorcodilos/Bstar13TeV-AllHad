import glob, ROOT

for fname in glob.glob('/eos/uscms/store/user/lcorcodi/bstar_nano/rootfiles/*QCD*.root'):
    f = ROOT.TFile.Open(fname)
    t = f.Get('Runs')
    nevents = 0
    for i in range(t.GetEntries()): 
        t.GetEntry(i)
        # print '%s %s' %(i,t.genEventCount_)
        nevents += t.genEventCount_
    print ('%s %s'%(fname.split('/')[-1],nevents))