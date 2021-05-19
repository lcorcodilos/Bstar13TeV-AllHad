import ROOT
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim

class addDAK8Producer(Module):
    def __init__(self,setname):
        self.setname = setname
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.DAK8File = ROOT.TFile.Open('root://cmseos.fnal.gov//store/user/lcorcodi/DeepAK8Results_tree/DAK8tree_'+self.setname+'.root')
        self.DAK8Tree = self.DAK8File.Get('DeepAK8')
        self.brlist_all = { 'jet_no':'ijet',
                            'binarized_score_top':'topScore',
                            'binarized_score_w':'wScore',
                            'pt':'pt',
                            'eta':'eta',
                            'phi':'phi'}
        
        self.out = wrappedOutputTree
        self.out.branch("DeepAK8_topScore",  "F", "nDeepAK8")
        self.out.branch("DeepAK8_wScore",  "F", "nDeepAK8")
        self.out.branch("DeepAK8_pt",  "F", "nDeepAK8")
        self.out.branch("DeepAK8_eta",  "F", "nDeepAK8")
        self.out.branch("DeepAK8_phi",  "F", "nDeepAK8")
        self.out.branch("DeepAK8_ijet",  "F", "nDeepAK8")
        self.out.branch("nDeepAK8", "I")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        # Get entry list for decorrelated values for given event
        self.DAK8Tree.Draw('>>elist','(nn_version=="Decorrelated")&&(event=='+str(event.event)+')',"entrylist")
        elist = ROOT.gDirectory.Get('elist')
        # Set the entry list for the DAK8 tree
        self.DAK8Tree.SetEntryList(elist)
        # Assign the length of our collection
        self.out.fillBranch("nDeepAK8",len(elist))

        # Fill each branch in the collection
        for branch in self.brlist_all.keys():
            out = []
            for e in range(len(elist)):
                self.DAK8Tree.GetEntry(self.DAK8Tree)
                out.append(getarr(self.DAK8Tree,branch))

            self.out.fillBranch("DeepAK8_"+self.brlist_all[branch],out)
        
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

addDAK8 = lambda : addDAK8Producer(setname) 