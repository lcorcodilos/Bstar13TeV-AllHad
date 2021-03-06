# 2017 version which uses central NanoAOD rather than JHitos
import pickle
import subprocess,glob

# Just grabbing the basic centrally produced nanoAOD so this will be different from the 2016 version
input_subs = {
    "ttbar":"/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7_ext1-v1/NANOAODSIM",
    "ttbar-semilep":"/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7_ext1-v1/NANOAODSIM",
    "QCDHT700":"/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "QCDHerwig":"/QCD_Pt-15to7000_TuneCH3_Flat_13TeV_herwig7/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "dataB":"/JetHT/Run2017B-Nano25Oct2019-v1/NANOAOD",
    "dataC":"/JetHT/Run2017C-Nano25Oct2019-v1/NANOAOD",
    "dataD":"/JetHT/Run2017D-Nano25Oct2019-v1/NANOAOD",
    "dataE":"/JetHT/Run2017E-Nano25Oct2019-v1/NANOAOD",
    "dataF":"/JetHT/Run2017F-Nano25Oct2019-v1/NANOAOD",

    "singletop_tW":"/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "singletop_tWB":"/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "singletop_t":"/ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "singletop_tB":"/ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "WjetsHT800":"/WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "WjetsHT600":"/WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "WjetsHT400":"/WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    
    "signalLH1200":"/BstarToTW_M-1200_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH1400":"/BstarToTW_M-1400_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH1600":"/BstarToTW_M-1600_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH1800":"/BstarToTW_M-1800_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH2000":"/BstarToTW_M-2000_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH2200":"/BstarToTW_M-2200_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH2400":"/BstarToTW_M-2400_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH2600":"/BstarToTW_M-2600_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH2800":"/BstarToTW_M-2800_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_V2_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH3000":"/BstarToTW_M-3000_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH3200":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-3200_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    "signalLH3400":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-3400_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    "signalLH3600":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-3600_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    "signalLH3800":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-3800_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    "signalLH4000":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-4000_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    #"signalLH4200":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-4200_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    
    "signalRH1200":"/BstarToTW_M-1200_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH1400":"/BstarToTW_M-1400_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH1600":"/BstarToTW_M-1600_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH1800":"/BstarToTW_M-1800_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH2000":"/BstarToTW_M-2000_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH2200":"/BstarToTW_M-2200_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH2400":"/BstarToTW_M-2400_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH2600":"/BstarToTW_M-2600_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH2800":"/BstarToTW_M-2800_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH3000":"/BstarToTW_M-3000_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_V2_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH3200":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-3200_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    "signalRH3400":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-3400_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    "signalRH3600":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-3600_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    "signalRH3800":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-3800_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root",
    "signalRH4000":"/store/user/lcorcodi/NanoAODv6/BstarToTW_M-4000_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/200630_17*/0000/*.root"
}
executables = []

# Remove files first
print 'rm *_loc.txt'
subprocess.call(['rm *_loc.txt'],shell=True)

f_release = open('release.txt','w')
f_release.close()
for i in input_subs.keys():
    if '/store/user/' in input_subs[i]:
        files = glob.glob('/eos/uscms'+input_subs[i])
        out = open(i+'_loc.txt','w')
        for f in files:
            out.write(f.replace('/eos/uscms','root://cmsxrootd.fnal.gov/')+'\n')
        out.close()
    else:
        executables.append('dasgoclient -query "file dataset='+input_subs[i]+'" > '+i+'_loc.txt')
        executables.append('echo '+input_subs[i]+' >> release.txt')
        executables.append('dasgoclient -query "release dataset='+input_subs[i]+'" >> release.txt')
for s in executables:
    print s
    subprocess.call([s],shell=True)


