import ROOT
from ROOT import *
import GenParticleChecker
from GenParticleChecker import GenParticleTree,GenParticleObj
import Bstar_Functions_local
from Bstar_Functions_local import *
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
# from PhysicsTools.NanoAODTools.postprocessing.tools import *
# from PhysicsTools.NanoAODTools.postprocessing.modules.jme.JetSysColl import JetSysColl, JetSysObj
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim

import sys

year = sys.argv[1]
file_string = Load_jetNano('ttbar',year)
file = TFile.Open(file_string)
Cuts = LoadCuts('default',year)


################################
# Grab event tree from nanoAOD #
################################
inTree = file.Get("Events")
elist,jsonFiter = preSkim(inTree,None,'')
inTree = InputTree(inTree,elist)
treeEntries = inTree.entries

##############
# Begin Loop #
##############
start = time.time()
last_event_time = start
event_time_sum = 0

threeProngsInJet = 0
bAndQOutsideJet = 0
doubleQOutsideJet = 0
qOutsideJet = 0
bOutsideJet = 0
noneInJet = 0
error = 0
notATopJet = 0
count = 0
pass_count = 0

out_f = TFile.Open('wtag_studies/ttbar_'+year+'.root','RECREATE')
out_f.cd()
prongCount = TH1F('prongCount','prongCount',8,0,8)
prongCount.GetXaxis().SetBinLabel(1,'Not a top jet')
prongCount.GetXaxis().SetBinLabel(2,'Error')
prongCount.GetXaxis().SetBinLabel(3,'None in jet')
prongCount.GetXaxis().SetBinLabel(4,'b and q outside jet')
prongCount.GetXaxis().SetBinLabel(5,'Two qs outside jet')
prongCount.GetXaxis().SetBinLabel(6,'b outside jet')
prongCount.GetXaxis().SetBinLabel(7,'q outside jet')
prongCount.GetXaxis().SetBinLabel(8,'b and two qs in jet')

deltaR_q = TH1F("deltaR_q","deltaR_q",20,0,2.0)
deltaR_b = TH1F("deltaR_b","deltaR_b",20,0,2.0)

for entry in range(treeEntries):
    count   =   count + 1
    if 'condor' not in os.getcwd():
        if count > 1:
            # current_event_time = time.time()
            # event_time_sum += (current_event_time - last_event_time)
            sys.stdout.write("%i / %i ... \r" % (count,treeEntries))
            # sys.stdout.write("Avg time = %f " % (event_time_sum/count) )
            sys.stdout.flush()
            # last_event_time = current_event_time
    else:
        if count % 10000 == 0 :
            print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(highBinEdge-lowBinEdge)) + '% -- '

    # Grab the event
    event = Event(inTree, entry)

    ak8JetsColl = Collection(event, 'FatJet')
    genparticles = Collection(event,'GenPart')

    # Separate into hemispheres the leading and subleading jets
    Jetsh0,Jetsh1 = Hemispherize(ak8JetsColl)

    if (len(Jetsh1) < 1):
        continue

    leadingJet = ak8JetsColl[Jetsh0[0]]
    subleadingJet = ak8JetsColl[Jetsh1[0]]
    jet1,jet2 = TLorentzVector(),TLorentzVector()
    jet1.SetPtEtaPhiM(leadingJet.pt,leadingJet.eta,leadingJet.phi,leadingJet.msoftdrop_raw)
    jet2.SetPtEtaPhiM(subleadingJet.pt,subleadingJet.eta,subleadingJet.phi,subleadingJet.msoftdrop_raw)

    # Make and get all cuts
    dy_val = abs(jet1.Rapidity()-jet2.Rapidity())
    pt_cut = Cuts['wpt'][0]<jet2.Perp()<Cuts['wpt'][1] and Cuts['tpt'][0]<jet1.Perp()<Cuts['tpt'][1]
    dy_cut = Cuts['dy'][0]<=dy_val<Cuts['dy'][1]
    eta_cut = (Cuts['eta'][0]<abs(leadingJet.eta)<Cuts['eta'][1]) and (Cuts['eta'][0]<abs(subleadingJet.eta)<Cuts['eta'][1])

    if pt_cut and dy_cut and eta_cut:
        pass_count +=1
        # if pass_count > 1000: quit()
        for t in [[leadingJet,jet1],[subleadingJet,jet2]]:
            j = t[0]
            j_tlv = t[1]
            if j.tau1 > 0: tau21val = j.tau2/j.tau1
            else: continue

            tau21_cut =  Cuts['tau21'][0]<=tau21val<Cuts['tau21'][1]
            wmass_cut = Cuts['wmass'][0]<=j_tlv.M()<Cuts['wmass'][1]

            if tau21_cut and wmass_cut:
                # Woo we have a W (tag)!              

                # Build the tree of gen particles that we care about
                particle_tree = GenParticleTree()
                tops = []
                Ws = []
                quarks = []
                qprongs = [] # Final particles we'll check
                bprongs = []
                allparticlesinjet = []
                for i,p in enumerate(genparticles):
                    # Internal class info
                    this_gen_part = GenParticleObj(i,p)
                    this_gen_part.SetStatusFlags()
                    this_gen_part.SetPDGName(abs(this_gen_part.pdgId))
                    
                    # Add particles to tree and keep track of them in external lists
                    if abs(this_gen_part.pdgId) == 6:# and this_gen_part.status == 62: # 22 means intermediate part of hardest subprocess, only other to appear is 62 (outgoing subprocess particle with primordial kT included)
                        particle_tree.AddParticle(this_gen_part)
                        tops.append(this_gen_part)

                    elif abs(this_gen_part.pdgId) == 24:# and this_gen_part.status == 22: # 22 means intermediate part of hardest subprocess, only other to appear is 52 (outgoing copy of recoiler, with changed momentum)
                        particle_tree.AddParticle(this_gen_part)
                        Ws.append(this_gen_part)

                    elif abs(this_gen_part.pdgId) >= 1 and abs(this_gen_part.pdgId) <= 5 and this_gen_part.status == 23:
                        particle_tree.AddParticle(this_gen_part)
                        quarks.append(this_gen_part)

                    # elif this_gen_part.vect.DeltaR(j_tlv)<0.8:
                    #     particle_tree.AddParticle(this_gen_part)
                    #     allparticlesinjet.append(this_gen_part)

                # particle_tree.PrintTree(entry,options=[],jet=j_tlv)

                found_top = False
                for t in tops:
                    if t.vect.DeltaR(j_tlv)<0.8: found_top = True

                if not found_top: 
                    notATopJet+=1
                    continue

                for W in Ws:
                    # If parent is a top that matches with the jet
                    wParent = particle_tree.GetParent(W)
                    if wParent != False and abs(wParent.pdgId) == 6 and wParent.DeltaR(j_tlv) < 0.8 and wParent.pt > 200:
                        # Loop over the daughters of the W
                        this_W = W
                        # Skip down chain of W's to last one
                        if len(particle_tree.GetChildren(this_W)) == 1 and particle_tree.GetChildren(this_W)[0].pdgId == W.pdgId:
                            this_W = particle_tree.GetChildren(this_W)[0]
                        
                        for c in particle_tree.GetChildren(this_W):
                            if abs(c.pdgId) >= 1 and abs(c.pdgId) <= 5:
                                deltaR_q.Fill(c.DeltaR(j_tlv))
                                # Append daughter quarks to prongs
                                if c.DeltaR(j_tlv)<0.8:qprongs.append(c)
                                    
                                    

                for q in quarks:
                    # if bottom     
                    if abs(q.pdgId) == 5:
                        bottomParent = particle_tree.GetParent(q)
                        # if parent exists and is a top matched to the jet
                        if bottomParent != False and abs(bottomParent.pdgId) == 6 and bottomParent.DeltaR(j_tlv) < 0.8 and bottomParent.pt > 200:
                            deltaR_b.Fill(q.DeltaR(j_tlv))

                            if q.DeltaR(j_tlv) < 0.8: bprongs.append(q)
                            # print "bprongs now %s long. \n\tpdgId = %s \n\tdeltaR = %.3f \n\tpt = %.3f \n\t idx = %s"%(len(bprongs),bottomParent.pdgId,bottomParent.DeltaR(j_tlv),bottomParent.pt,bottomParent.idx)

                # Now that we have the prongs, check how many are merged
                if len(bprongs) == 1:
                    if len(qprongs) == 2: threeProngsInJet +=1
                    elif len(qprongs) == 1: qOutsideJet +=1
                    elif len(qprongs) == 0: doubleQOutsideJet +=1
                    else: 
                        print "Something has gone terribly wrong. There was 1 bottom found but %s other quarks found!" %(len(qprongs))
                        error += 1
                    
                elif len(bprongs) == 0:
                    if len(qprongs) == 2: bOutsideJet +=1
                    elif len(qprongs) == 1: bAndQOutsideJet +=1
                    elif len(qprongs) == 0: noneInJet +=1
                    else: 
                        print "Something has gone terribly wrong. There was no bottom found but %s other quarks found!" %(len(qprongs))
                        error += 1

                else:
                    print "Something has gone terribly wrong. There are %s b quarks found!" %(len(bprongs))
                    error += 1

prongCount.SetBinContent(1,notATopJet)
prongCount.SetBinContent(2,error)
prongCount.SetBinContent(3,noneInJet)
prongCount.SetBinContent(4,bAndQOutsideJet)
prongCount.SetBinContent(5,doubleQOutsideJet)
prongCount.SetBinContent(6,bOutsideJet)
prongCount.SetBinContent(7,qOutsideJet)
prongCount.SetBinContent(8,threeProngsInJet)

out_f.cd()
out_f.Write()
out_f.Close()