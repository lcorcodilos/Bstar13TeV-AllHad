'''Prints out the NanoAOD branch info for LHEPdfWeight
Ex. python getPdfs.py myNanoFile.root
'''

import ROOT
import sys

filename = sys.argv[1]

f = ROOT.TFile.Open(filename)
f.Get("Events").Print("LHEPdfWeight*")
