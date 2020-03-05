# Factorizes PDF weights from NanoAOD (for signal) into xsec (normalization) and acceptance (shape) pieces

import ROOT
from ROOT import *
import Bstar_Functions_local
from Bstar_Functions_local import *

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object,Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import InputTree
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.JetSysColl import JetSysColl, JetSysObj
from PhysicsTools.NanoAODTools.postprocessing.framework.preskimming import preSkim


# For normalization
# norm_up = sum(nom_i*wup_i)
# norm = sum(nom_i)
# norm_unc = norm_up/norm
# if nom_i = 1, norm_unc = sum(wup_i)/N

setnames = ['signalLH'+str(m) for m in range(1200,3200,200)] + ['signalRH'+str(m) for m in range(1200,3200,200)]

out = TFile.Open('pdf_norm_uncertainties_bstar.root','RECREATE')

for y in ['16','17','18']:
    for s in setnames:
        print s+y
        file = TFile.Open(Load_jetNano(s,y))


        ################################
        # Grab event tree from nanoAOD #
        ################################
        inTree = file.Get("Events")
        elist,jsonFiter = preSkim(inTree,None,'')
        inTree = InputTree(inTree,elist)
        treeEntries = inTree.entries

        sum_pdf_up = 0.
        sum_pdf_down = 0.
        count = 0.

        for entry in range(0,treeEntries):
            count   =   count + 1
            if 'condor' not in os.getcwd():
                if count > 1:
                    # current_event_time = time.time()
                    # event_time_sum += (current_event_time - last_event_time)
                    sys.stdout.write("%i / %i ... \r" % (count,(treeEntries)))
                    # sys.stdout.write("Avg time = %f " % (event_time_sum/count) )
                    sys.stdout.flush()
                    # last_event_time = current_event_time
            else:
                if count % 10000 == 0 :
                    print  '--------- Processing Event ' + str(count) +'   -- percent complete ' + str(100*count/(treeEntries)) + '% -- '

            # Grab the event
            event = Event(inTree, entry)
            pdf_up, pdf_down = PDF_Lookup(inTree.readBranch('LHEPdfWeight'))

            sum_pdf_up += pdf_up
            sum_pdf_down += pdf_down

        norm_up = sum_pdf_up/count
        norm_down = sum_pdf_down/count

        out.cd()
        hist_out = TH1I(s+y,s+y,2,0,2)
        hist_out.GetXaxis().SetBinLabel(1,'up')
        hist_out.GetXaxis().SetBinLabel(1,'down')
        hist_out.SetBinContent(1,norm_up)
        hist_out.SetBinContent(2,norm_down)

        hist_out.Write()

out.Close()

# Done in make_preselection
# For shape, nom_up_i = nom_i*wup_i/norm_unc