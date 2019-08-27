import ROOT
from ROOT import *
from collections import OrderedDict
from Bstar_Functions import LoadCuts,LoadConstants,Load_jetNano
import GenParticleChecker
from GenParticleChecker import GenParticleTree,GenParticleObj
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
import math,json

class bstar():
    """docstring for bstar"""
    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.config = openJSON(self.options.config)
        self.config_name = self.options.config.split('.json')[0]
    
        # Check for ttMR
        if self.options.region == 'ttbar':
            self.wIsTtagged = True
            print 'W side will be top tagged'
        else: self.wIsTtagged = False

        # Check for data
        if 'data' in self.options.set: self.isData = True
        else: self.isData = False

        # Load cuts and constants
        self.cuts = LoadCuts(self.options.region,self.options.year)
        self.constants = LoadConstants(self.options.year)

        # Check for non-standard lumi weighting
        if self.config['qcdweight']:
            print 'Will use QCD weighting for this run'
            self.lumi = self.constants['qcd_lumi']
        else: self.lumi = self.constants['lumi']

        # Temp year for when 17 stuff is used for 18
        self.tempyear = options.year
        if options.year == '18': self.tempyear = '17'
        
        self.GetInput()
        self.SplitJobs()
        self.SetNames()
        
        if not self.isData:
            self.ttagsffile = TFile.Open('SFs/20'+self.tempyear+'TopTaggingScaleFactors_NoMassCut.root')
            self.lepSFfile = TFile.Open('SFs/bstar_lep_veto_sfs.root')
            TrigFile = TFile.Open("trigger/trigger_studies/Triggerweight_data"+self.options.year+"_pre_"+self.pretrig_name+".root")
            TrigPlot = TrigFile.Get('TriggerWeight_'+self.trig_name+'_Ht')
            self.trigplot = TrigPlot.Clone()

        self.outfile = TFile.Open(self.output_name,'RECREATE')

    #############################
    # Run bookkeeping functions #
    #############################

    def SetNames(self):
        self.btagtype = 'btagDeepB'
        self.trig_name = self.config['trigger'][self.options.year]
        self.pretrig_name = self.config['pretrigger'][self.options.year]

        # JECs
        self.runOthers = True
        self.jec_string = ''
        if self.options.JES!='nom':
            self.jec_string = '_JES' + '-' + options.JES
            self.runOthers = False
        if self.options.JER!='nom':
            self.jec_string = '_JER' + '-' + options.JER
            self.runOthers = False
        if self.options.JMS!='nom':
            self.jec_string = '_JMS' + '-' + options.JMS
            self.runOthers = False
        if self.options.JMR!='nom':
            self.jec_string = '_JMR' + '-' + options.JMR
            self.runOthers = False

        self.ttagstring = 'tau32'+self.config["tau32"]

        if self.njobs!=1:   self.output_name = 'TW'+self.name+self.options.year+'_'+self.options.set+"_job"+str(self.ijob)+"of"+str(self.njobs)+'_'+self.config_name+self.jec_string+'_'+self.options.region+'.root'
        else:               self.output_name = 'TW'+self.name+self.options.year+'_'+self.options.set+'_'+self.config_name+self.jec_string+'_'+self.options.region+'.root'

        print self.output_name

    def GetInput(self):
        ###############################
        # Grab root file that we want #
        ###############################
        file_string = Load_jetNano(self.options.set,self.options.year)
        self.infile = TFile.Open(file_string)

        ################################
        # Grab event tree from nanoAOD #
        ################################
        inTree = self.infile.Get("Events")
        elist,jsonFiter = preSkim(inTree,None,'')
        self.inTree = InputTree(inTree,elist)
        self.treeEntries = self.inTree.entries

    def SplitJobs(self):
        self.njobs=int(self.options.njobs)
        if self.njobs != 1:
            self.ijob=int(self.options.job)
            print "Running over " +str(self.njobs)+ " jobs"
            print "This will process job " +str(self.ijob)

            self.evInJob = int(self.treeEntries/self.njobs)
            
            self.lowBinEdge = evInJob*(ijob-1)
            self.highBinEdge = evInJob*ijob

            if ijob == self.njobs:
                self.highBinEdge = self.treeEntries

        else:
            print "Running over all events"
            self.lowBinEdge = 0
            self.highBinEdge = self.treeEntries

        print "Range of events: (" + str(self.lowBinEdge) + ", " + str(self.highBinEdge) + ")"

    def SetNCuts(self,ncuts):
        return [0]*ncuts

    def FillCutflow(self,index):
        self.cutflow[index]+=1
    def GetCutflow(self,index):
        return self.cutflow[index]

    ######################
    # Correction loaders #
    ######################    

    def SjbtagSFReader(self):
        # Prep for deepcsv b-tag
        # From https://twiki.cern.ch/twiki/bin/view/CMS/BTagCalibration
        gSystem.Load('libCondFormatsBTauObjects') 
        gSystem.Load('libCondToolsBTau') 
        if self.options.year == '16':
            calib = BTagCalibration('DeepCSV', 'SFs/DeepCSV_2016LegacySF_V1.csv')
        elif self.options.year == '17':
            calib = BTagCalibration('DeepCSV', 'SFs/subjet_DeepCSV_94XSF_V4_B_F.csv')
        elif self.options.year == '18':
            calib = BTagCalibration('DeepCSV', 'SFs/DeepCSV_102XSF_V1.csv')
            
        v_sys = getattr(ROOT, 'vector<string>')()
        v_sys.push_back('up')
        v_sys.push_back('down')

        self.sjbtag_reader = BTagCalibrationReader(
            0,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
            "central",      # central systematic type
            v_sys,          # vector of other sys. types
        )   

        self.sjbtag_reader.load(
            calib, 
            0,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
            "incl"      # measurement type
        ) 

        return self.sjbtag_reader

    def WtagSF(self,purity,GenParticles,ttbar=False):
        # W matching
        if WJetMatching(wjet,GenParticles,ttbar=ttbar) and purity != False:
            wtagsf = self.constants['wtagsf_'+purity]
            wtagsfsig = self.constants['wtagsfsig_'+purity]

        else:
            wtagsf = 1.0
            wtagsfsig = 0.0

        return wtagsf,wtagsfsig

    #######################
    # Correction appliers #
    #######################

    def TriggerEff(self, ht):
        Weight = 1.0
        Weightup = 1.0
        Weightdown = 1.0
        if ht < 2000.0:
            bin0 = self.trigplot.FindBin(ht) 
            jetTriggerWeight = self.trigplot.GetBinContent(bin0)
            # Check that we're not in an empty bin in the fully efficient region
            if jetTriggerWeight == 0:
                if self.trigplot.GetBinContent(bin0-1) == 1.0 and self.trigplot.GetBinContent(bin0+1) == 1.0:
                    jetTriggerWeight = 1.0
                elif self.trigplot.GetBinContent(bin0-1) > 0 or self.trigplot.GetBinContent(bin0+1) > 0:
                    jetTriggerWeight = (self.trigplot.GetBinContent(bin0-1)+self.trigplot.GetBinContent(bin0+1))/2.

            Weight = jetTriggerWeight
            deltaTriggerEff  = 0.5*(1.0-jetTriggerWeight)
            Weightup  =   min(1.0,jetTriggerWeight + deltaTriggerEff)
            Weightdown  =   max(0.0,jetTriggerWeight - deltaTriggerEff)
            
        return [Weight,Weightup,Weightdown]

    def WPurity(self,tau21val):
        # Determine purity for scale factor
        if self.options.region == 'default': Wpurity = 'HP'
        elif self.options.region == 'sideband':
            if self.options.year == '16': Wpurity = 'LP'
            elif self.options.year != '16' and (self.cuts['tau21LP'][0] < tau21val < self.cuts['tau21LP'][1]): 
                Wpurity = 'LP'
            else: Wpurity = False
        else: Wpurity = False

        return Wpurity

    def ExtrapUncert(self,pt,purity):
        # Quick way to get extrapolation uncertainty
        if self.options.year == '16':
            if purity == 'HP':    x = 0.085
            elif purity == 'LP':  x = 0.039
            elif purity == False: return 0
            extrap_uncert = x*log(pt/200)
            return extrap_uncert
        elif year == '17' or year == '18':
            if pt > 350 and pt < 600: return 0.13
            else:
                if purity == 'HP':    x = 0.085
                elif purity == 'LP':  x = 0.039
                elif purity == False: return 0
                extrap_uncert = x*log(pt/200)
                return extrap_uncert

    def TopTagSF(self,jet,wp,genparticles):
        if wp == 'loose': workpoint = 'wp3'
        elif wp == 'medium': workpoint = 'wp4'
        elif wp == 'tight': workpoint = 'wp5'

        # Build the tree of gen particles that we care about
        particle_tree = GenParticleTree()
        tops = []
        Ws = []
        quarks = []
        prongs = [] # Final particles we'll check
        for i,p in enumerate(genparticles):
            # Internal class info
            this_gen_part = GenParticleObj(i,p)
            this_gen_part.SetStatusFlags()
            this_gen_part.SetPDGName(abs(this_gen_part.pdgId))
            
            # Add particles to tree and keep track of them in external lists
            if abs(this_gen_part.pdgId) == 6 and this_gen_part.vect.DeltaR(jet)<0.8:# and this_gen_part.status == 62: # 22 means intermediate part of hardest subprocess, only other to appear is 62 (outgoing subprocess particle with primordial kT included)
                particle_tree.AddParticle(this_gen_part)
                tops.append(this_gen_part)

            elif abs(this_gen_part.pdgId) == 24:# and this_gen_part.status == 22: # 22 means intermediate part of hardest subprocess, only other to appear is 52 (outgoing copy of recoiler, with changed momentum)
                particle_tree.AddParticle(this_gen_part)
                Ws.append(this_gen_part)

            elif abs(this_gen_part.pdgId) >= 1 and abs(this_gen_part.pdgId) <= 5 and this_gen_part.status == 23:
                particle_tree.AddParticle(this_gen_part)
                quarks.append(this_gen_part)

            elif this_gen_part.vect.DeltaR(jet)<0.8:
                particle_tree.AddParticle(this_gen_part)

        for W in Ws:
            # If parent is a top that matches with the jet
            wParent = particle_tree.GetParent(W)
            if wParent != False:
                if abs(wParent.pdgId) == 6 and wParent.DeltaR(jet) < 0.8:
                    # Loop over the daughters of the W
                    this_W = W
                    # Skip down chain of W's to last one
                    if len(particle_tree.GetChildren(this_W)) == 1 and particle_tree.GetChildren(this_W)[0].pdgId == W.pdgId:
                        this_W = particle_tree.GetChildren(this_W)[0]
                    
                    for c in particle_tree.GetChildren(this_W):
                        if abs(c.pdgId) >= 1 and abs(c.pdgId) <= 5:
                            # Append daughter quarks to prongs
                            prongs.append(c)

        for q in quarks:
            # if bottom      and     has a parent              and   parent is a top                          and    the top matches to the jet
            if abs(q.pdgId) == 5:
                bottomParent = particle_tree.GetParent(q)
                # if parent exists
                if bottomParent != False:
                    # if parent is a top matched to the jet
                    if abs(bottomParent.pdgId) == 6 and bottomParent.DeltaR(jet) < 0.8:
                        prongs.append(q)

        # Now that we have the prongs, check how many are merged
        merged_particles = 0
        if len(prongs) < 3: # you've either tagged a QCD jet and can't match to a gen top or the W decayed leptonically so don't apply a SF in either case
            # if len(prongs) == 1: 
            #     particle_tree.PrintTree(ievent,['idx','status'],wp,jet)
            #     raw_input(prongs[0].idx)
            return [1,1,1],-len(prongs)-1


        for p in prongs:
            if p.DeltaR(jet) < 0.8:
                merged_particles += 1

        if merged_particles == 3:
            hnom = self.ttagsffile.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_nominal')
            hup = self.ttagsffile.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_up')
            hdown = self.ttagsffile.Get('PUPPI_'+workpoint+'_btag/sf_mergedTop_down')
        elif merged_particles == 2:
            hnom = self.ttagsffile.Get('PUPPI_'+workpoint+'_btag/sf_semimerged_nominal')
            hup = self.ttagsffile.Get('PUPPI_'+workpoint+'_btag/sf_semimerged_up')
            hdown = self.ttagsffile.Get('PUPPI_'+workpoint+'_btag/sf_semimerged_down')
        elif merged_particles == 1:
            hnom = self.ttagsffile.Get('PUPPI_'+workpoint+'_btag/sf_notmerged_nominal')
            hup = self.ttagsffile.Get('PUPPI_'+workpoint+'_btag/sf_notmerged_up')
            hdown = self.ttagsffile.Get('PUPPI_'+workpoint+'_btag/sf_notmerged_down')
        else:
            return [1,1,1],-len(prongs)-1

        if jet.Perp() > 5000:
            sfbin_nom = hnom.GetNbinsX()
            sfbin_up = hup.GetNbinsX()
            sfbin_down = hdown.GetNbinsX()
        else:
            sfbin_nom = hnom.FindFixBin(jet.Perp())
            sfbin_up = hup.FindFixBin(jet.Perp())
            sfbin_down = hdown.FindFixBin(jet.Perp())

        nom = hnom.GetBinContent(sfbin_nom)
        up = hup.GetBinContent(sfbin_up)
        down = hdown.GetBinContent(sfbin_down)

        return [nom,up,down],merged_particles

    
    def TriggerBit(self,tree):
        passt = False
        for t in self.trig_name.split('OR'):
            try: 
                if tree.readBranch(t):
                    passt = True
            except:
                continue

        return passt

    #####################
    # Cutting functions #
    #####################
    def Hemispherize(self,jetCollection):
        Jetsh1 = []
        Jetsh0 = []
        for ijet in range(0,len(jetCollection)):
            if abs(deltaPhi(jetCollection[0].phi,jetCollection[ijet].phi))>TMath.Pi()/2.0:
                Jetsh1.append(ijet)
            else:
                Jetsh0.append(ijet)

        return Jetsh0,Jetsh1


    def Wtag(self,jet): # `jet` of type CandidateJet
        tag = Tag()

        if not jet.tau1 > 0: tag.SetBool(False)
        else:
            tau21_cut =  self.cuts['tau21'][0]<=(jet.tau2/jet.tau1)<self.cuts['tau21'][1]
            mass_cut = self.cuts['wmass'][0]<=jet.SDmass<self.cuts['wmass'][1]
            tag.SetVals({"nsubjetiness":{"val":jet.tau2/jet.tau1,"bool":tau21_cut},"mass":{"val":jet.SDmass,"bool":mass_cut}})
            
            if tau21_cut and wmass_cut: tag.SetBool(True)
            else: tag.SetBool(False)
                
        return tag

    def Toptag(self,jet,tau32wp): # `jet` of type CandidateJet
        tag = Tag()
        
        if not jet.tau2 > 0: tag.SetBool(False)
        else:
            mass_cut = self.cuts['tmass'][0]<=jet.SDmass<self.cuts['tmass'][1]
            tau32_cut = self.cuts['tau32'+tau32wp][0] <= jet.tau3/jet.tau2 < self.cuts['tau32'+tau32wp][1]
            tag.SetVals({'nsubjetiness':{"val":jet.tau3/jet.tau2,"bool":tau32_cut},'mass':{"val":jet.SDmass,"bool":mass_cut}})

            if mass_cut and tau32_cut: tag.SetBool(True)
            else: tag.SetBool(False)

        return tag

    def SJbtag(self,jet,subjetcoll): # `jet` of type CandidateJet
        tag = Tag()

        idx1_bad = (jet.subJetIdx1 < 0) or (jet.subJetIdx1 >= len(subjetcoll))
        idx2_bad = (jet.subJetIdx2 < 0) or (jet.subJetIdx2 >= len(subjetcoll))

        # if both negative, throw away event
        if idx1_bad and idx2_bad: tag.SetBool(False) 
        # if idx2 not negative or bad index, use that
        elif idx1_bad and not idx2_bad: val = getattr(subjetcoll[jet.subJetIdx2],'btagDeepB')
        # if idx1 not negative, use that
        elif not idx1_bad and idx2_bad: val = getattr(subjetcoll[jet.subJetIdx1],'btagDeepB')
        # if idx1 not negative, use that
        elif not idx1_bad and not idx2_bad: val = max(getattr(subjetcoll[jet.subJetIdx1],'btagDeepB'),getattr(subjetcoll[jet.subJetIdx1],'btagDeepB'))

        sbjtag_cut = self.cuts['deepbtag'][0]<=val<=self.cuts['deepbtag'][1]
        tag.SetVal({"sjbtag":{"val":val,"bool":sbjtag_cut}}) 

        if sbjtag_cut: tag.SetBool(True)
        else: tag.SetBool(False)

        return tag

    def JetID(self,nanojetobj): #
        jetid = True
        if (nanojetobj.jetId & 1 == 0):    # if not loose
            if (nanojetobj.jetId & 2 == 0): # and if not tight - Need to check here because loose is always false in 2017
                jetid = False                      # move on
        return jetid

    def Filters(self,tree):
        filters = [tree.readBranch('Flag_goodVertices'),
                   tree.readBranch('Flag_HBHENoiseFilter'),
                   tree.readBranch('Flag_HBHENoiseIsoFilter'),
                   tree.readBranch('Flag_globalTightHalo2016Filter'),
                   tree.readBranch('Flag_EcalDeadCellTriggerPrimitiveFilter'),
                   tree.readBranch('Flag_eeBadScFilter'),
                   tree.readBranch('Flag_ecalBadCalibFilter')]

        for thisFilter in filters:
            if thisFilter == 0:
                return False
        
        return True

#######################
# External functions #
#######################

# Function stolen from https://stackoverflow.com/questions/9590382/forcing-python-json-module-to-work-with-ascii
def openJSON(f):
    return json.load(open(f,'r'), object_hook=ascii_encode_dict) 

def ascii_encode_dict(data):    
    ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x 
    return dict(map(ascii_encode, pair) for pair in data.items())

class CandidateJet():
    """docstring for CandidateJet"""
    def __init__(self, nanojetobj, isData):
        self.nanojetobj = nanojetobj
        self.vect = TLorentzVector()

        self.tau1 = nanojetobj.tau1
        self.tau2 = nanojetobj.tau2,
        self.tau3 = nanojetobj.tau3,
        self.phi = nanojetobj.phi,
        self.mass = nanojetobj.mass_nom,
        self.pt = nanojetobj.pt_nom, # This will just have JER and JES corrections
        self.eta = nanojetobj.eta,
        self.SDmass = nanojetobj.msoftdrop_nom, 
        self.subJetIdx1 = nanojetobj.subJetIdx1,
        self.subJetIdx2 = nanojetobj.subJetIdx2,

        self.vect.SetPtEtaPhiM(self.pt,self.eta,self.phi,self.SDmass)

    def ApplyJetCorrections(self,corrlist):
        for c in corrlist:
            if c == 'JESnom': _SetJES('nom')
            elif c =='JESup': _SetJES('up')
            elif c =='JESdown': _SetJES('down')

            elif c =='JERnom': self._SetJER('nom')
            elif c =='JERup': self._SetJER('up')
            elif c =='JERdown': self._SetJER('down')

            elif c =='JMSnom': self._SetJMS('nom')
            elif c =='JMSup': self._SetJMS('up')
            elif c =='JMSdown': self._SetJMS('down')

            elif c =='JMRnom': self._SetJMR('nom')
            elif c =='JMRup': self._SetJMR('up')
            elif c =='JMRdown': self._SetJMR('down')

        self.pt = self.pt * self.JEScorr * self.JERcorr
        self.SDmass = self.SDmass * self.JEScorr * self.JERcorr * self.JMScorr * self.JMRcorr

        self.vect.SetPtEtaPhiM(self.pt,self.eta,self.phi,self.SDmass)

    def _SetJES(self,variation):
        if variation == 'nom': self.JEScorr = 1.0
        else: self.JEScorr = getattr(nanojetobj,'corr_JES_Total'+variation.capitalize())

    def _SetJER(self,variation):
        if variation == 'nom': self.JERcorr = 1.0
        else: self.JERcorr = getattr(nanojetobj,'corr_JER_'+variation)

    def _SetJMS(self,variation):
        if variation == 'nom': self.JMScorr = 1.0
        else: self.JMScorr = getattr(nanojetobj,'corr_JMS_'+variation)

    def _SetJMR(self,variation):
        if variation == 'nom': self.JMRcorr = 1.0
        else: self.JMRcorr =  getattr(nanojetobj,'groomed_corr_JMR_'+variation)

    
class Tag():
    """docstring for Tag"""
    def __init__(self):
        self.bool = None
        self.vals = None
        self.SF = None

    def SetBool(self,inbool):
        self.bool = inbool
    def GetBool(self):
        return self.bool
    def SetVals(self,valuedict):
        self.vals = valuedict
    def GetVals(self):
        return self.vals
    def SetSF(self,sf):
        self.SF = sf
    def GetSF(self):
        return self.SF

    def __add__(self,other):
        newtag = Tag()
        newtag.SetBool(self.bool and other.bool)
        newtag.SetVals({k: v for d in [self.vals, other.vals] for k, v in d.items()})
        if self.SF == None and other.SF == None: pass
        elif self.SF != None and other.SF == None: newtag.SetSF(self.SF)
        elif self.SF == None and other.SF != None: newtag.SetSF(other.SF)
        elif self.SF != None and self.SF != None: newtag.SetSF(self.SF * other.SF)

        return newtag

class Counter(object):
    """docstring for Counter"""
    def __init__(self, bintitles):  #bintitles must be an OrderedDict with key = alias and value = bin title
        super(Counter, self).__init__()
        if type(bintitles) != OrderedDict: raise Exception("Variable bintitles is not of type OrderedDict")
        self.bintitles = bintitles.values()
        self.binalias = bintitles.keys()
        self.nbins = len(self.bintitles)
        self.countdict = {}
        for a in self.binalias:
            self.countdict[a] = 0
       
    def GetHist(self,name,histtitle=''):
        hist = TH1F(name, histtitle if histtitle != '' else name, self.nbins,0,self.nbins)
        for i in range(self.nbins): 
            hist.GetXaxis().SetBinLabel(i+1,self.bintitles[i])
            hist.SetBinContent(i+1,self.countdict[self.binalias[i]])
        self.hist = hist
        return hist

    def Set(self,key,value):
        self.countdict[key] = value
    def Get(self,key):  
        return self.countdict[key]
    def PlusOne(self,key):
        self.countdict[key] += 1 


# This does the W jet matching requirement by looking up the deltaR separation
# of the daughter particle from the W axis. If passes, return 1.
def WJetMatching(wjetVect,genparticles,ttbar=False):
    # Build the tree of gen particles that we care about
    particle_tree = GenParticleTree()
    Ws = []
    quarks = []
    tops = []
    prongs = [] # Final particles we'll check

    for i,p in enumerate(genparticles):
        # Internal class info
        this_gen_part = GenParticleObj(i,p)
        this_gen_part.SetStatusFlags()
        this_gen_part.SetPDGName(abs(this_gen_part.pdgId))
        
        # Add particles to tree and keep track of them in external lists
        if abs(this_gen_part.pdgId) == 24:# and this_gen_part.status == 22: # 22 means intermediate part of hardest subprocess, only other to appear is 52 (outgoing copy of recoiler, with changed momentum)
            particle_tree.AddParticle(this_gen_part)
            Ws.append(this_gen_part)
        elif abs(this_gen_part.pdgId) >= 1 and abs(this_gen_part.pdgId) <= 5 and this_gen_part.status == 23:
            particle_tree.AddParticle(this_gen_part)
            quarks.append(this_gen_part)
        elif ttbar and abs(this_gen_part.pdgId) == 5:
            particle_tree.AddParticle(this_gen_part)
            tops.append(this_gen_part)

    for q in quarks:
        # if parent is a w and 
        if particle_tree.GetParent(q) and abs(particle_tree.GetParent(q).pdgId) == 24 and particle_tree.GetParent(q).vect.DeltaR(wjetVect) < 0.8 and q.vect.DeltaR(wjetVect) < 0.8:
            prongs.append(q)

    if len(prongs) == 2:
        if not ttbar: return True
        else:
            wParent = particle_tree.GetParent(prongs[0])
            if abs(particle_tree.GetParent(wParent).pdgId) == 6:
                topParent = particle_tree.GetParent(wParent)
                for c in particle_tree.GetChildren(topParent):
                    if abs(c.pdgId) == 5 and c.vect.DeltaR(wjetVect) > 0.8:
                        return True
                    else: return False
            else: return False

    else: return False   




