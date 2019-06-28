import pickle

input_subs = {
        #"dataB": {  # "das": "/JetHT/Run2016B-05Feb2018_ver1-v1/NANOAOD",
        #            # "requestName": "JetHT_Run2016B-05Feb2018_ver1-v1_bstar_v0p1" },       
        #"dataB2": { # "das": "/JetHT/Run2016B-05Feb2018_ver2-v1/NANOAOD",
        #            # "requestName": "JetHT_Run2016B-05Feb2018_ver2-v1_bstar_v0p1" },       
        #"dataC": {  # "das": "/JetHT/Run2016C-05Feb2018-v1/NANOAOD",
        #            # "requestName": "JetHT_Run2016C-05Feb2018-v1_bstar_v0p1" },       
        #"dataD": {  # "das": "/JetHT/Run2016D-05Feb2018-v1/NANOAOD",
        #            # "requestName": "JetHT_Run2016D-05Feb2018-v1_bstar_v0p1" },       
        #"dataE": {  # "das": "/JetHT/Run2016E-05Feb2018-v1/NANOAOD",
        #            # "requestName": "JetHT_Run2016E-05Feb2018-v1_bstar_v0p1" },       
        #"dataF": {  # "das": "/JetHT/Run2016F-05Feb2018-v1/NANOAOD",
        #            # "requestName": "JetHT_Run2016F-05Feb2018-v1_bstar_v0p1" },       
        #"dataG": {  # "das": "/JetHT/Run2016G-05Feb2018-v1/NANOAOD",
        #            # "requestName": "JetHT_Run2016G-05Feb2018-v1_bstar_v0p1" },       
        #"dataH": {  # "das": "/JetHT/Run2016H-05Feb2018_ver2-v1/NANOAOD",
        #            # "requestName": "JetHT_Run2016H-05Feb2018_ver2-v1_bstar_v0p1" },       
        #"dataH2": {  # "das": "/JetHT/Run2016H-05Feb2018_ver3-v1/NANOAOD",
        #            # "requestName": "JetHT_Run2016H-05Feb2018_ver3-v1_bstar_v0p1" },      

        "ttbar": {  # "das": "/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                    # "requestName": "TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_bstar_v0p1",
                    # "Nevents": 75311946,
                    "xsec": 831.76},       

        "singletop_t": {# "das": "/ST_t-channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                        # "requestName": "ST_t-channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin_bstar_v0p1",
                        # "Nevents": 5993676,
                        "xsec": 136.02},  

        "singletop_tB": {   # "das": "/ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                            # "requestName": "ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin_bstar_v0p1",
                            # "Nevents": 3928063,
                            "xsec": 80.95}, 

        "singletop_tW": {   # "das": "/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                            # "requestName": "ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4_bstar_v0p1",
                            # "Nevents": 992024,
                            "xsec": 35.85}, 

        "singletop_tWB": {  # "das": "/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                            # "requestName": "ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M2T4_bstar_v0p1",
                            # "Nevents": 998276,
                            "xsec": 35.85},

        "QCDHT500": {   # "das": "/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                        # "requestName": "QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_bstar_v0p1",
                        # "Nevents": 18929951,
                        "xsec": 31630},     
        "QCDHT700": {   # "das": "/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                        # "requestName": "QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_bstar_v0p1",
                        # "Nevents": 15629253,
                        "xsec": 6802},
        "QCDHT1000": {  # "das": "/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                        # "requestName": "QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_bstar_v0p1",
                        # "Nevents": 4767100,
                        "xsec": 1206},
        "QCDHT1500": {  # "das": "/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                        # "requestName": "QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_bstar_v0p1",
                        # "Nevents": 3970819,
                        "xsec": 120.4},
        "QCDHT2000": {  # "das": "/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
                        # "requestName": "QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_bstar_v0p1",
                        # "Nevents": 1991645,
                        "xsec": 25.25}#,


        # "signalLH1200": {# "das": "/BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-1200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 1.944},  
        # "signalLH1400": {# "das": "/BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-1400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.7848},  
        # "signalLH1600": {# "das": "/BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-1600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.3431},
        # "signalLH1800": {# "das": "/BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-1800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.1588},
        # "signalLH2000": {# "das": "/BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.07711},  
        # "signalLH2200": {# "das": "/BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2200_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 97000,
        #                 "xsec": 0.03881},  
        # "signalLH2400": {# "das": "/BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2400_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.02015},  
        # "signalLH2600": {# "das": "/BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2600_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.01073},  
        # "signalLH2800": {# "das": "/BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2800_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.005829},  
        # "signalLH3000": {# "das": "/BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-3000_LH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.003234},  
        

        # "signalRH1200": {# "das": "/BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-1200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 1.936},  
        # "signalRH1400": {# "das": "/BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-1400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 99800,
        #                 "xsec": 0.7816},  
        # "signalRH1600": {# "das": "/BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-1600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 99200,
        #                 "xsec": 0.3416},  
        # "signalRH1800": {# "das": "/BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-1800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 97600,
        #                 "xsec": 0.1583},  
        # "signalRH2000": {# "das": "/BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.07675},  
        # "signalRH2200": {# "das": "/BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2200_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.03864},  
        # "signalRH2400": {# "das": "/BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2400_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.02008},  
        # "signalRH2600": {# "das": "/BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2600_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.01068},  
        # "signalRH2800": {# "das": "/BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-2800_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.005814},  
        # "signalRH3000": {# "das": "/BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM",
        #                 # "requestName": "BstarToTW_M-3000_RH_TuneCUETP8M1_13TeV-madgraph-pythia8_bstar_v0p1",
        #                 # "Nevents": 100000,
        #                 "xsec": 0.003224}  
}

# for i in input_subs.keys(): 
    # input_subs[i]['location'] = "/store/user/lcorcodi/JHitos16/"+input_subs[i]['das'].split('/')[1]+'JHitos16-v0p1_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1/'

pickle.dump(input_subs,open('JHitos17Info.p','wb'))
