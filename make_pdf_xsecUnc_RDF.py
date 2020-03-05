import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from JHUanalyzer.Analyzer.analyzer import analyzer,openJSON,CutflowHist
from JHUanalyzer.Analyzer.Cscripts import CommonCscripts, CustomCscripts
commonc = CommonCscripts()
customc = CustomCscripts()

# parser = OptionParser()

# parser.add_option('-i', '--input', metavar='F', type='string', action='store',
#                 default   =   '',
#                 dest      =   'input',
#                 help      =   'A root file or text file with multiple root file locations to analyze')
# parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
#                 default   =   'output.root',
#                 dest      =   'output',
#                 help      =   'Output file name.')
# parser.add_option('-c', '--config', metavar='FILE', type='string', action='store',
#                 default   =   'config.json',
#                 dest      =   'config',
#                 help      =   'Configuration file in json format that is interpreted as a python dictionary')

# (options, args) = parser.parse_args()

setnames = ['signalLH'+str(m) for m in range(1200,3200,200)] + ['signalRH'+str(m) for m in range(1200,3200,200)]

out_f = ROOT.TFile('pdf_norm_uncertainties_bstar.root',"RECREATE")
out_f.cd()

first = True
for y in ['16','17','18']:
    for s in setnames:
        start_time = time.time()
        print '%s, %s' %(s,y)
        a = analyzer('NanoAOD'+y+'_lists_bstar/'+s+'_loc.txt')
        # if '_loc.txt' in options.input: setname = options.input.split('/')[-1].split('_loc.txt')[0]
        # else: setname = ''

        if first: 
            customc.Import("pdfweights","JHUanalyzer/Corrections/pdfweights.cc")
            a.SetCFunc(customc.pdfweights)

        a.SetVar("Pdfweight",'analyzer::PDFweight(LHEPdfWeight)')
        a.SetVar("Pdfweight_up",'Pdfweight[0]')
        a.SetVar("Pdfweight_down",'Pdfweight[1]')

        mean_pdf_up = a.DataFrame.Mean("Pdfweight_up")
        mean_pdf_down = a.DataFrame.Mean("Pdfweight_down")

        pdf_up = mean_pdf_up.GetValue()
        pdf_down = mean_pdf_up.GetValue()

        hist_out = ROOT.TH1F(s+'_'+y,s+'_'+y,2,0,2)
        hist_out.GetXaxis().SetBinLabel(1,'up')
        hist_out.GetXaxis().SetBinLabel(2,'down')
        hist_out.SetBinContent(1,pdf_up)
        hist_out.SetBinContent(2,pdf_down)
        hist_out.Write()

        print "Total time: "+str((time.time()-start_time)/60.) + ' min'

        first = False

out_f.Close()


