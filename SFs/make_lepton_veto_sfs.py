import ROOT
from ROOT import *

def SFcalc(name,data,mc):
    print 'Making '+name
    if '16' in name:
        lumis = {'BCDEF':19691, # split lumis used for weighted average of muon SFs
                 'GH':16227}

    if type(data) == dict:
        needsAvg = True
        outhist = data[data.keys()[0]].Clone()
    else:
        needsAvg = False
        outhist = data.Clone()
    outhist.Reset()

    for ix in range(1,outhist.GetNbinsX()+1):
        for iy in range(1,outhist.GetNbinsY()+1):
            if needsAvg:
                this_eff_data = 0
                for k in data.keys():
                    this_eff_data += data[k].GetBinContent(ix,iy)*lumis[k]
                this_eff_data /= sum(v for v in lumis.values())

                this_eff_mc = 0
                for k in mc.keys():
                    this_eff_mc += mc[k].GetBinContent(ix,iy)*lumis[k]
                this_eff_mc /= sum(v for v in lumis.values())

            else: 
                this_eff_data = data.GetBinContent(ix,iy)
                this_eff_mc = mc.GetBinContent(ix,iy)
            
            if 1-this_eff_mc > 0:
                this_sf = (1-this_eff_data)/(1-this_eff_mc)
            elif this_eff_mc == 1 and this_eff_data == 1:
                this_sf = 1
            else:
                print 'WARNING: MC eff = 1 and Data eff < 1. Setting veto sf to zero for bin '+ix+', '+iy
                this_sf = 0

            outhist.SetBinContent(ix,iy,this_sf)

    outhist.SetName(name)
    outhist.SetTitle(name)

    return outhist

if __name__ == "__main__":
    # Open up all of the files
    eff_files = {}
    for year in ['16','17','18']:
        eff_files[year] = {
            'electron':{},
            'muon':{
                'ISO':{},
                'ID':{}
            }
        }

        if year == '16': 
            # mu is eta, pt
            eff_files[year]['electron']['data_file'] = TFile.Open('2016LegacyReReco_ElectronTight.root')
            eff_files[year]['electron']['mc_file'] = TFile.Open('2016LegacyReReco_ElectronTight.root')
            eff_files[year]['muon']['ISO']['data_file'] = {'BCDEF':TFile.Open('2016_Muon_RunBCDEF_data_ISO.root'), 
                                                              'GH':TFile.Open('2016_Muon_RunGH_data_ISO.root')}
            eff_files[year]['muon']['ISO']['mc_file'] = {'BCDEF':TFile.Open('2016_Muon_RunBCDEF_mc_ISO.root'), 
                                                            'GH':TFile.Open('2016_Muon_RunGH_mc_ISO.root')}
            eff_files[year]['muon']['ID']['data_file'] = {'BCDEF':TFile.Open('2016_Muon_RunBCDEF_data_ID.root'), 
                                                             'GH':TFile.Open('2016_Muon_RunGH_data_ID.root')}
            eff_files[year]['muon']['ID']['mc_file'] = {'BCDEF':TFile.Open('2016_Muon_RunBCDEF_mc_ID.root'), 
                                                           'GH':TFile.Open('2016_Muon_RunGH_mc_ID.root')}
        
            eff_files[year]['electron']['data'] = eff_files[year]['electron']['data_file'].Get('EGamma_EffData2D')
            eff_files[year]['electron']['mc'] = eff_files[year]['electron']['mc_file'].Get('EGamma_EffMC2D')
            eff_files[year]['muon']['ISO']['data'] = {k:f.Get('NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt') for k,f in eff_files[year]['muon']['ISO']['data_file'].items()}
            eff_files[year]['muon']['ISO']['mc'] = {k:f.Get('NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt') for k,f in eff_files[year]['muon']['ISO']['mc_file'].items()}
            eff_files[year]['muon']['ID']['data'] = {k:f.Get('NUM_TightID_DEN_genTracks_eta_pt') for k,f in eff_files[year]['muon']['ID']['data_file'].items()}
            eff_files[year]['muon']['ID']['mc'] = {k:f.Get('NUM_TightID_DEN_genTracks_eta_pt') for k,f in eff_files[year]['muon']['ID']['mc_file'].items()}

        else: 
            # mu is pt, abs(eta)
            eff_files[year]['electron']['data_file'] = TFile.Open('20'+year+'_ElectronTight.root')
            eff_files[year]['electron']['mc_file'] = TFile.Open('20'+year+'_ElectronTight.root')
            eff_files[year]['muon']['ISO']['data_file'] = TFile.Open('20'+year+'_Muon_data_ISO.root')
            eff_files[year]['muon']['ISO']['mc_file'] = TFile.Open('20'+year+'_Muon_mc_ISO.root')
            eff_files[year]['muon']['ID']['data_file'] = TFile.Open('20'+year+'_Muon_data_ID.root')
            eff_files[year]['muon']['ID']['mc_file'] = TFile.Open('20'+year+'_Muon_mc_ID.root')

            eff_files[year]['electron']['data'] = eff_files[year]['electron']['data_file'].Get('EGamma_EffData2D')
            eff_files[year]['electron']['mc'] = eff_files[year]['electron']['mc_file'].Get('EGamma_EffMC2D')
            eff_files[year]['muon']['ISO']['data'] = eff_files[year]['muon']['ISO']['data_file'].Get('NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta')
            eff_files[year]['muon']['ISO']['mc'] = eff_files[year]['muon']['ISO']['mc_file'].Get('NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta')
            if year == '18':
                eff_files[year]['muon']['ID']['data'] = eff_files[year]['muon']['ID']['data_file'].Get('NUM_TightID_DEN_TrackerMuons_pt_abseta')
                eff_files[year]['muon']['ID']['mc'] = eff_files[year]['muon']['ID']['mc_file'].Get('NUM_TightID_DEN_TrackerMuons_pt_abseta')
            else:
                eff_files[year]['muon']['ID']['data'] = eff_files[year]['muon']['ID']['data_file'].Get('NUM_TightID_DEN_genTracks_pt_abseta')
                eff_files[year]['muon']['ID']['mc'] = eff_files[year]['muon']['ID']['mc_file'].Get('NUM_TightID_DEN_genTracks_pt_abseta')


    # Book a new file
    out = TFile.Open('bstar_lep_veto_sfs.root','RECREATE')

    # Now loop over booked histograms and fill
    for year in eff_files.keys():
        for l in eff_files[year].keys():
            if l == 'electron':
                this_data = eff_files[year]['electron']['data']
                this_mc = eff_files[year]['electron']['mc']
                this_hist = SFcalc(year+'_Electron_veto_sf',this_data,this_mc)

                out.cd()
                this_hist.Write()

            elif l == 'muon':
                for i in eff_files[year]['muon'].keys():
                    this_data = eff_files[year]['muon'][i]['data']
                    this_mc = eff_files[year]['muon'][i]['mc']
                    this_hist = SFcalc(year+'_Muon_'+i+'_veto_sf',this_data,this_mc)

                    out.cd()
                    this_hist.Write()


    out.Close()