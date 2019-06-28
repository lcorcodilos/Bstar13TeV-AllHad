import ROOT
from ROOT import *
gStyle.SetOptStat(0)
gROOT.SetBatch(kTRUE)

from optparse import OptionParser


parser = OptionParser()

parser.add_option('-r', '--region', metavar='F', type='string', action='store',
                default   =   'default',
                dest      =   'region',
                help      =   'default, sideband, ttbar')
parser.add_option('-t', '--tau32', metavar='F', type='string', action='store',
                default   =   'medium',
                dest      =   'tau32',
                help      =   'Cut strength (off, loose, medium, tight)')
parser.add_option('-y', '--year', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'year',
                help      =   'Year (16,17,18)')


(options, args) = parser.parse_args()

outfile = TFile("VarPlots/VarPlots"+options.year+'_tau32'+options.tau32+'_'+options.region+".root",'recreate')

# Setup some lists and a dict to loop over
sets = ['signalLH2000','QCD','ttbar']
signal_name = [s for s in sets if 'signal' in s][0]
colors = {'ttbar':kRed,
        'QCD':kYellow,
        signal_name:kBlue}
dists = ['PtTop','PtW','deltaY','PtTopW','EtaTop','EtaW','PhiTop','PhiW','dPhi','Tau21','MSDw','Tau32','SJbtag','MSDtop']

# Initialize a dictionary for organization of input histograms
infiles = {}

# Grab each set and distribution
for s in sets:
    year = options.year
    if 'signal' in s and year == '18': # temp hack since we don't have 17 or 18 signals...
        year = '17'
    infiles[s] = {'file':TFile.Open("rootfiles/TWvariables"+year+"_"+s+"_tau32"+options.tau32+'_'+options.region+".root")}
    f = infiles[s]['file']

    for d in dists:
        if d == 'deltaY':
            infiles[s][d] = f.Get('MtwvsdeltaY').ProjectionX().Clone()
        else:
            infiles[s][d] = f.Get(d).Clone()

        infiles[s][d].SetName(s+'_'+d)

# Make a Cnvas
c = TCanvas('c','c',800,700)

# For each distribution that we want to compare sets to...
for d in dists:
    if d in ['SJbtag','dPhi']:
        leg = TLegend(0.1,0.8,0.3,0.9)
    else:
        leg = TLegend(0.7,0.8,0.9,0.9)
    same = ''
    ymax = 0
    tot_bkg_int = 0

    # Make a stack of the backgrounds
    totbkg = THStack(d+'_totbkg','Total Bkg - '+d)

    # Get the total integral of backgrounds
    for s in sets:
        if 'signal' not in s:
            tot_bkg_int += infiles[s][d].Integral()

    # Plot each set
    for s in sets:
        infiles[s][d].SetMinimum(0.0)
        if 'signal' in s:
            infiles[s][d].SetLineColor(colors[s])
            infiles[s][d].SetLineWidth(2)
            legtype = 'l'
            infiles[s][d].Scale(1/infiles[s][d].Integral())

        else:
            infiles[s][d].SetLineColor(kBlack)
            infiles[s][d].SetLineWidth(1)
            infiles[s][d].SetFillColor(colors[s])
            legtype = 'fl'
            infiles[s][d].Scale(1/tot_bkg_int)
            totbkg.Add(infiles[s][d])

        leg.AddEntry(infiles[s][d],s,legtype)
            
    if totbkg.GetMaximum() >= infiles[signal_name][d].GetMaximum():
        if d in ['PhiW','PhiTop']:
            ymax = totbkg.GetMaximum()*1.4
        else:
            ymax = totbkg.GetMaximum()*1.1

    else:
        if d in ['PhiW','PhiTop']:
            ymax = infiles[signal_name][d].GetMaximum()*1.4
        else:
            ymax = infiles[signal_name][d].GetMaximum()*1.1

    infiles[signal_name][d].SetMaximum(ymax)
    infiles[signal_name][d].SetMinimum(0.0)
    infiles[signal_name][d].GetXaxis().SetTitle(infiles[signal_name][d].GetTitle())
    infiles[signal_name][d].SetTitle('')
    infiles[signal_name][d].Draw('hist')    # Have to draw this first because of weird THStack stuff
    totbkg.Draw('samehist')
    infiles[signal_name][d].Draw('samehist')

    gPad.RedrawAxis()
    leg.Draw()

    outfile.cd()
    c.Write()
    c.Print('VarPlots/'+d+options.year+'_tau32'+options.tau32+'_'+options.region+".pdf",'pdf')

