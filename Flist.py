import sys
import glob
import os

if __name__ == "__main__":
    saveout = sys.stdout
    
    mySetDict = {
            'dataB':'JetHT/JetHT_Run2016B-05Feb2018_ver1-v1_jetNano_v0p1/',
            'dataB2':'JetHT/JetHT_Run2016B-05Feb2018_ver2-v1_jetNano_v0p1/',
            'dataC':'JetHT/JetHT_Run2016C-05Feb2018-v1_jetNano_v0p1/',
            'dataD':'JetHT/JetHT_Run2016D-05Feb2018-v1_jetNano_v0p1/',
            'dataE':'JetHT/JetHT_Run2016E-05Feb2018-v1_jetNano_v0p1/',
            'dataF':'JetHT/JetHT_Run2016F-05Feb2018-v1_jetNano_v0p1/',
            'dataG':'JetHT/JetHT_Run2016G-05Feb2018-v1_jetNano_v0p1/',
            'dataH':'JetHT/JetHT_Run2016H-05Feb2018_ver2-v1_jetNano_v0p1/',
            'dataH2':'JetHT/JetHT_Run2016H-05Feb2018_ver3-v1_jetNano_v0p1/',
            
            'ttbar':'TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_jetNano_v0p1/',

            'QCDHT500':'QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
            'QCDHT500ext':'QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/',
            'QCDHT700':'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
            'QCDHT700ext':'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/',
            'QCDHT1000':'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
            'QCDHT1000ext':'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/',
            'QCDHT1500':'QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
            'QCDHT1500ext':'QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/',
            'QCDHT2000':'QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1/',
            'QCDHT2000ext':'QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_jetNano_v0p1_ext/',

            'singletop_tB':'ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin/ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin_jetNano_v0p1/',
            'singletop_t':'ST_t-channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin/ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin_jetNano_v0p1/',
            'singletop_tWB':'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4_jetNano_v0p1/',
            'singletop_tW':'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4_jetNano_v0p1/',
            
            'signalLH1200':'BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalLH1400':'BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalLH1600':'BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalLH1800':'BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalLH2000':'BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalLH2200':'BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalLH2400':'BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalLH2600':'BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalLH2800':'BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalLH3000':'BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            
            'signalRH1200':'BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalRH1400':'BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalRH1600':'BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalRH1800':'BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalRH2000':'BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalRH2200':'BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalRH2400':'BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalRH2600':'BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalRH2800':'BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/',
            'signalRH3000':'BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_jetNano_v0p1/'
            }

    if not os.path.exists('DAK8csvFileLists'):
        os.makedirs('DAK8csvFileLists')

    base_dir = '/eos/uscms/store/user/lcorcodi/DeepAK8Results/'
    

    for i in mySetDict.keys():
        Outf1   =   open("DAK8csvFileLists/Files_"+i+".txt", "w")
        DeepAK8_csv_location = mySetDict[i]
        
        print base_dir+DeepAK8_csv_location+'*/*/output_94X*.csv'
        file_strings = glob.glob(base_dir+DeepAK8_csv_location+'*/*/output_94X*.csv')

        sys.stdout = Outf1
        for f in file_strings:
            fs = f.replace('/eos/uscms','root://cmsxrootd.fnal.gov//')
            print fs
        sys.stdout = saveout

        Outf1.close()


