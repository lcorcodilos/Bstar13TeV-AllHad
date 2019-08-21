import subprocess
import glob

input_subs16 = {
    "ttbar":"/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT700":"/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT700ext":"/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT2000ext":"/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT1500ext":"/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "QCDHT1000ext":"/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext1-v1/NANOAODSIM",
    "dataB2":"/JetHT/Run2016B_ver2-Nano1June2019_ver2-v2/NANOAOD",
    "dataC":"/JetHT/Run2016C-Nano1June2019-v1/NANOAOD",
    "dataD":"/JetHT/Run2016D-Nano1June2019-v1/NANOAOD",
    "dataE":"/JetHT/Run2016E-Nano1June2019-v1/NANOAOD",
    "dataF":"/JetHT/Run2016F-Nano1June2019-v1/NANOAOD",
    "dataG":"/JetHT/Run2016G-Nano1June2019-v1/NANOAOD",
    "dataH":"/JetHT/Run2016H-Nano1June2019-v1/NANOAOD",
    "WjetsHT600":"/WJetsToQQ_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_tW":"/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_tWB":"/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_t":"/ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_tB":"/ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM",
    "singletop_s":"/ST_s-channel_4f_InclusiveDecays_13TeV-amcatnlo-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM"
    # "signalLH1200":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalLH1400":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalLH1600":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalLH1800":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalLH2000":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalLH2200":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalLH2400":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalLH2600":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalLH2800":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalLH3000":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH1200":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH1400":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH1600":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH1800":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH2000":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH2200":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH2400":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH2600":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH2800":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root",
    # "signalRH3000":"/store/user/lcorcodi/BStarNanoAODv4_16/BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/Bstar_private2_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_NANOAODv4/*/0000/*.root"
}
input_subs17 = {
    "ttbar":"/TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "ttbar-semilep":"/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "QCDHT700":"/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "dataB":"/JetHT/Run2017B-Nano1June2019-v1/NANOAOD",
    "dataC":"/JetHT/Run2017C-Nano1June2019-v1/NANOAOD",
    "dataD":"/JetHT/Run2017D-Nano1June2019-v1/NANOAOD",
    "dataE":"/JetHT/Run2017E-Nano1June2019-v1/NANOAOD",
    "dataF":"/JetHT/Run2017F-Nano1June2019-v1/NANOAOD",

    "singletop_tW":"/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "singletop_tWB":"/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "singletop_t":"/ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "singletop_tB":"/ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "WjetsHT800":"/WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "WjetsHT600":"/WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "WjetsHT400":"/WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    
    "signalLH1200":"/BstarToTW_M-1200_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "signalLH1400":"/BstarToTW_M-1400_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH1600":"/BstarToTW_M-1600_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH1800":"/BstarToTW_M-1800_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH2000":"/BstarToTW_M-2000_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH2200":"/BstarToTW_M-2200_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM",
    "signalLH2400":"/BstarToTW_M-2400_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH2600":"/BstarToTW_M-2600_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalLH2800":"/BstarToTW_M-2800_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM",
    "signalLH3000":"/BstarToTW_M-3000_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    
    "signalRH1200":"/BstarToTW_M-1200_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "signalRH1400":"/BstarToTW_M-1400_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "signalRH1600":"/BstarToTW_M-1600_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH1800":"/BstarToTW_M-1800_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH2000":"/BstarToTW_M-2000_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH2200":"/BstarToTW_M-2200_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "signalRH2400":"/BstarToTW_M-2400_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM",
    "signalRH2600":"/BstarToTW_M-2600_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH2800":"/BstarToTW_M-2800_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
    "signalRH3000":"/BstarToTW_M-3000_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM"
}
input_subs18 = {
    "ttbar":"/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "ttbar-semilep":"/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "QCDHT700":"/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "QCDHT1000":"/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "QCDHT1500":"/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "QCDHT2000":"/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "dataA":"/JetHT/Run2018A-Nano1June2019-v2/NANOAOD",
    "dataB":"/JetHT/Run2018B-Nano1June2019-v2/NANOAOD ",
    "dataC1":"/JetHT/Run2018C-Nano1June2019-v1/NANOAOD",
    "dataC2":"/JetHT/Run2018C-Nano1June2019-v2/NANOAOD",
    "dataD":"/JetHT/Run2018D-Nano1June2019_ver2-v1/NANOAOD",

    "singletop_tW":"/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19_ext1-v1/NANOAODSIM",
    "singletop_tWB":"/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19_ext1-v1/NANOAODSIM",
    "singletop_t":"/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "singletop_tB":"/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "singletop_s":"/ST_s-channel_4f_hadronicDecays_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19_ext1-v1/NANOAODSIM",
    "WjetsHT400":"/WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "WjetsHT600":"/WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "WjetsHT800":"/WJetsToQQ_HT-800toInf_qc19_3j_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    
    "signalLH1200":"/BstarToTW_M-1200_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalLH1400":"/BstarToTW_M-1400_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalLH1600":"/BstarToTW_M-1600_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalLH1800":"/BstarToTW_M-1800_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalLH2000":"/BstarToTW_M-2000_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalLH2200":"/BstarToTW_M-2200_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalLH2400":"/BstarToTW_M-2400_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalLH2600":"/BstarToTW_M-2600_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalLH2800":"/BstarToTW_M-2800_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalLH3000":"/BstarToTW_M-3000_LH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    
    "signalRH1200":"/BstarToTW_M-1200_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalRH1400":"/BstarToTW_M-1400_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalRH1600":"/BstarToTW_M-1600_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalRH1800":"/BstarToTW_M-1800_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalRH2000":"/BstarToTW_M-2000_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalRH2200":"/BstarToTW_M-2200_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalRH2400":"/BstarToTW_M-2400_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalRH2600":"/BstarToTW_M-2600_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalRH2800":"/BstarToTW_M-2800_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM",
    "signalRH3000":"/BstarToTW_M-3000_RH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19-v1/NANOAODSIM"

}

executables = []

# loj = open('../../treeMaker.listOfJobs','w')

year = 16
executables.append('rm release_summary.txt')
for input_subs in [input_subs16,input_subs17,input_subs18]:
    for i in sorted(input_subs.keys()):
        executables.append('(echo "'+i+' 20'+str(year)+'" ; dasgoclient -query "release dataset='+input_subs[i]+'") >> release_summary.txt')
        # loj.write("python tardir/bstarTreeMaker.py "+i+'\n')

    year += 1

    for s in executables:
        print s
        subprocess.call([s],shell=True)

