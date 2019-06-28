# make_cutflow.py
# Makes cutflow tables with efficiencies and outputs latex tables

import ROOT
from ROOT import *
import sys
import pprint
pp = pprint.PrettyPrinter(indent = 2)

# Function to spit out latex from a python dictionary
def dictToLatexTable(dict2convert,outfilename,roworder=[],columnorder=[],caption=''):
    # First set of keys are row, second are column
    if len(roworder) > 0:
        rows = roworder
    else:
        rows = dict2convert.keys()
        rows.sort()

    if len(columnorder) > 0:
        columns = columnorder
    else:
        columns = []
        for r in rows:
            thesecolumns = dict2convert[r].keys()
            for c in thesecolumns:
                if c not in columns:
                    columns.append(c)
        columns.sort()

    latexout = open(outfilename,'w')
    latexout.write('\\begin{table}[] \n')
    latexout.write('\\adjustbox{center}{')
    latexout.write('\\begin{tabular}{|c|'+len(columns)*'c'+'|} \n')
    latexout.write('\\hline \n')

    column_string = ' &'
    for c in columns:
        column_string += str(c)+'\t& '
    column_string = column_string[:-2]+'\\\ \n'
    latexout.write(column_string)

    latexout.write('\\hline \n')
    for r in rows:
        row_string = '\t'+r+'\t& '
        for c in columns:
            if c in dict2convert[r].keys():
                row_string += str(dict2convert[r][c])+'\t& '
            else:
                print 'Could not find key "'+c+'" in row '+r
                row_string += '- \t& '
        row_string = row_string[:-2]+'\\\ \n'
        latexout.write(row_string)

    latexout.write('\\hline \n')
    latexout.write('\\end{tabular} \n')
    latexout.write('} \n')  # close off adjustbox
    latexout.write('\\caption{'+caption+'} \n')
    latexout.write('\\end{table}')
    latexout.close()

# Command line arguments specific to Lucas' code
# Ex. `python make_cutflow sideband 16` 
region = sys.argv[1]
year = sys.argv[2]

# Captions for each Latex table 
captions = {
    "default16":"Signal selection, 2016",
    "default17":"Signal selection, 2017",
    "default18":"Signal selection, 2018 - note that signal yields are currently for 2016 signals",
    "sideband16":"Sideband selection, 2016",
    "sideband17":"Sideband selection, 2017",
    "sideband18":"Sideband selection, 2018 - note that signal yields are currently for 2016 signals",
    "ttbar16":"ttbar measurement region selection, 2016",
    "ttbar17":"ttbar measurement region selection, 2017",
    "ttbar18":"ttbar measurement region selection, 2018 - note that signal yields are currently for 2016 signals"
}

# Temporary hack - remove at some point
tempyear = '16'

# All of the processes 
columns = [
    "QCD",
    "$\\ttbar$",
    "$\\ttbar$ (semi-lep)",
    "W+jets",
    # "single top ($s$)",
    # "single top ($t$)",
    # "single top ($\\bar{t}$)",
    "single top ($tW$)",
    "single top ($\\bar{t}W$)",
    "$b^{*}$ 1200 GeV",
    "$b^{*}$ 2000 GeV",
    "$b^{*}$ 2800 GeV"
]

# The names of each cut in order (printed as the row titles)
rows = [
    '-',
    '$p_{t}$ and $|\\delta Y|$',
    '$\\tau_{21}$',
    '$m_{W}$',
    '$\\tau_{32}$',
    'Subjet b-tag'
]

# Where all of the information is actually stored - value for "column" key must match with one in the columns dictionary
# The "file" value is the file where your cutflow info is stored (I stored mine as distributions so I actually grab the whole
# distribution after N cuts and then integrate over it to get the total number of events that survive those N cuts)
infoDict = {
    "QCD": {
        "file":TFile.Open("rootfiles/TWpreselection"+year+"_QCD_tau32medium_"+region+".root"),
        "column":"QCD"
    },
    "ttbar": {
        "file":TFile.Open("rootfiles/TWpreselection"+year+"_ttbar_tau32medium_"+region+".root"),
        "column":"$\\ttbar$"
    },
    "ttbar_semilep": {
        "file":TFile.Open("rootfiles/TWpreselection"+year+"_ttbar_semilep_tau32medium_"+region+".root"),
        "column":"$\\ttbar$ (semi-lep)"
    },
    "Wjets": {
        "file":TFile.Open("rootfiles/TWpreselection"+year+"_Wjets_tau32medium_"+region+".root"),
        "column":"W+jets"
    },
    # "singletop_s": {
    #     "file":TFile.Open("rootfiles/TWpreselection"+year+"_singletop_s_tau32medium_"+region+".root"),
    #     "column":"single top ($s$)"
    # },
    # "singletop_t": {
    #     "file":TFile.Open("rootfiles/TWpreselection"+year+"_singletop_t_tau32medium_"+region+".root"),
    #     "column":"single top ($t$)"
    # },
    # "singletop_tB": {
    #     "file":TFile.Open("rootfiles/TWpreselection"+year+"_singletop_tB_tau32medium_"+region+".root"),
    #     "column":"single top ($\\bar{t}$)"
    # },
    "singletop_tW": {
        "file":TFile.Open("rootfiles/TWpreselection"+year+"_singletop_tW_tau32medium_"+region+".root"),
        "column":"single top ($tW$)"
    },
    "singletop_tWB": {
        "file":TFile.Open("rootfiles/TWpreselection"+year+"_singletop_tWB_tau32medium_"+region+".root"),
        "column":"single top ($\\bar{t}W$)"
    },
    "signalLH1200": {
        "file":TFile.Open("rootfiles/TWpreselection"+tempyear+"_signalLH1200_tau32medium_"+region+".root"),
        "column":"$b^{*}$ 1200 GeV"
    },
    "signalLH2000": {
        "file":TFile.Open("rootfiles/TWpreselection"+tempyear+"_signalLH2000_tau32medium_"+region+".root"),
        "column":"$b^{*}$ 2000 GeV"
    },
    "signalLH2800": {
        "file":TFile.Open("rootfiles/TWpreselection"+tempyear+"_signalLH2800_tau32medium_"+region+".root"),
        "column":"$b^{*}$ 2800 GeV"
    },

}

# Build the dictionary that turns into a LaTeX table
dictTable = {}
# For the rows...
for i,r in enumerate(rows):
    dictTable[r] = {} # Make the empty column
    for t in infoDict.keys(): # For each column

        # Skip over some stuff
        if year == '17' and t == 'singletop_s':
            continue
        if year == '16' and t == 'ttbar_semilep':
            continue

        # Grab the file
        file = infoDict[t]["file"]
        # Get the correct histogram name depending on the row - mine go: nev, Mtw_cut1, Mtw_cut2, ...
        if i == 0:
            histname = "nev"
        else:
            histname = "Mtw_cut"+str(i)

        # Add the integral of the histogram to the column
        dictTable[r][infoDict[t]["column"]] = int(round(file.Get(histname).Integral()))

# Prints the dictionary nicely if you want to double check it's correct
# pp.pprint(dictTable)

# This is what it would look like without the above for loop - short and elegant vs long and messy which is why I switched it!
# dictTable = {
#     '-': {
#         "QCD":int(round(QCD_file.Get("nev").Integral())),
#         "$\\ttbar$":int(round(ttbar_file.Get("nev").Integral())),
#         "W+jets":int(round(Wjets_file.Get("nev").Integral())),
#         "singletop (s-channel)":int(round(singletop_s_file.Get("nev").Integral())),
#         "singletop (t, top)":int(round(singletop_t_file.Get("nev").Integral())),
#         "singletop (t, anti-top)":int(round(singletop_tB_file.Get("nev").Integral())),
#         "singletop (tW, top)":int(round(singletop_tW_file.Get("nev").Integral())),
#         "singletop (tW, anti-top)":int(round(singletop_tWB_file.Get("nev").Integral())),
#         "$b^{*}_{LH}$ 1200 GeV":int(round(signalLH1200_file.Get("nev").Integral())),
#         "$b^{*}_{LH}$ 2000 GeV":int(round(signalLH2000_file.Get("nev").Integral())),
#         "$b^{*}_{LH}$ 2800 GeV":int(round(signalLH2800_file.Get("nev").Integral()))
#     },
#     '$p_{t}$ and $|\delta Y|$':{
#         "QCD":int(round(QCD_file.Get("Mtw_cut1").Integral())),
#         "$\\ttbar$":int(round(ttbar_file.Get("Mtw_cut1").Integral())),
#         "W+jets":int(round(Wjets_file.Get("Mtw_cut1").Integral())),
#         "singletop (s-channel)":int(round(singletop_s_file.Get("Mtw_cut1").Integral())),
#         "singletop (t, top)":int(round(singletop_t_file.Get("Mtw_cut1").Integral())),
#         "singletop (t, anti-top)":int(round(singletop_tB_file.Get("Mtw_cut1").Integral())),
#         "singletop (tW, top)":int(round(singletop_tW_file.Get("Mtw_cut1").Integral())),
#         "singletop (tW, anti-top)":int(round(singletop_tWB_file.Get("Mtw_cut1").Integral())),
#         "$b^{*}_{LH}$ 1200 GeV":int(round(signalLH1200_file.Get("Mtw_cut1").Integral())),
#         "$b^{*}_{LH}$ 2000 GeV":int(round(signalLH2000_file.Get("Mtw_cut1").Integral())),
#         "$b^{*}_{LH}$ 2800 GeV":int(round(signalLH2800_file.Get("Mtw_cut1").Integral()))
#     },
#     '$\\tau_{21}$':{
#         "QCD":int(round(QCD_file.Get("Mtw_cut2").Integral())),
#         "$\\ttbar$":int(round(ttbar_file.Get("Mtw_cut2").Integral())),
#         "W+jets":int(round(Wjets_file.Get("Mtw_cut2").Integral())),
#         "singletop (s-channel)":int(round(singletop_s_file.Get("Mtw_cut2").Integral())),
#         "singletop (t, top)":int(round(singletop_t_file.Get("Mtw_cut2").Integral())),
#         "singletop (t, anti-top)":int(round(singletop_tB_file.Get("Mtw_cut2").Integral())),
#         "singletop (tW, top)":int(round(singletop_tW_file.Get("Mtw_cut2").Integral())),
#         "singletop (tW, anti-top)":int(round(singletop_tWB_file.Get("Mtw_cut2").Integral())),
#         "$b^{*}_{LH}$ 1200 GeV":int(round(signalLH1200_file.Get("Mtw_cut2").Integral())),
#         "$b^{*}_{LH}$ 2000 GeV":int(round(signalLH2000_file.Get("Mtw_cut2").Integral())),
#         "$b^{*}_{LH}$ 2800 GeV":int(round(signalLH2800_file.Get("Mtw_cut2").Integral()))
#     },
#     '$m_{W}$':{
#         "QCD":int(round(QCD_file.Get("Mtw_cut3").Integral())),
#         "$\\ttbar$":int(round(ttbar_file.Get("Mtw_cut3").Integral())),
#         "W+jets":int(round(Wjets_file.Get("Mtw_cut3").Integral())),
#         "singletop (s-channel)":int(round(singletop_s_file.Get("Mtw_cut3").Integral())),
#         "singletop (t, top)":int(round(singletop_t_file.Get("Mtw_cut3").Integral())),
#         "singletop (t, anti-top)":int(round(singletop_tB_file.Get("Mtw_cut3").Integral())),
#         "singletop (tW, top)":int(round(singletop_tW_file.Get("Mtw_cut3").Integral())),
#         "singletop (tW, anti-top)":int(round(singletop_tWB_file.Get("Mtw_cut3").Integral())),
#         "$b^{*}_{LH}$ 1200 GeV":int(round(signalLH1200_file.Get("Mtw_cut3").Integral())),
#         "$b^{*}_{LH}$ 2000 GeV":int(round(signalLH2000_file.Get("Mtw_cut3").Integral())),
#         "$b^{*}_{LH}$ 2800 GeV":int(round(signalLH2800_file.Get("Mtw_cut3").Integral()))
#     },
#     '$\\tau_{32}$':{
#         "QCD":int(round(QCD_file.Get("Mtw_cut4").Integral())),
#         "$\\ttbar$":int(round(ttbar_file.Get("Mtw_cut4").Integral())),
#         "W+jets":int(round(Wjets_file.Get("Mtw_cut4").Integral())),
#         "singletop (s-channel)":int(round(singletop_s_file.Get("Mtw_cut4").Integral())),
#         "singletop (t, top)":int(round(singletop_t_file.Get("Mtw_cut4").Integral())),
#         "singletop (t, anti-top)":int(round(singletop_tB_file.Get("Mtw_cut4").Integral())),
#         "singletop (tW, top)":int(round(singletop_tW_file.Get("Mtw_cut4").Integral())),
#         "singletop (tW, anti-top)":int(round(singletop_tWB_file.Get("Mtw_cut4").Integral())),
#         "$b^{*}_{LH}$ 1200 GeV":int(round(signalLH1200_file.Get("Mtw_cut4").Integral())),
#         "$b^{*}_{LH}$ 2000 GeV":int(round(signalLH2000_file.Get("Mtw_cut4").Integral())),
#         "$b^{*}_{LH}$ 2800 GeV":int(round(signalLH2800_file.Get("Mtw_cut4").Integral()))
#     },
#     'Subjet b-tag':{
#         "QCD":int(round(QCD_file.Get("Mtw_cut5").Integral())),
#         "$\\ttbar$":int(round(ttbar_file.Get("Mtw_cut5").Integral())),
#         "W+jets":int(round(Wjets_file.Get("Mtw_cut5").Integral())),
#         "singletop (s-channel)":int(round(singletop_s_file.Get("Mtw_cut5").Integral())),
#         "singletop (t, top)":int(round(singletop_t_file.Get("Mtw_cut5").Integral())),
#         "singletop (t, anti-top)":int(round(singletop_tB_file.Get("Mtw_cut5").Integral())),
#         "singletop (tW, top)":int(round(singletop_tW_file.Get("Mtw_cut5").Integral())),
#         "singletop (tW, anti-top)":int(round(singletop_tWB_file.Get("Mtw_cut5").Integral())),
#         "$b^{*}_{LH}$ 1200 GeV":int(round(signalLH1200_file.Get("Mtw_cut5").Integral())),
#         "$b^{*}_{LH}$ 2000 GeV":int(round(signalLH2000_file.Get("Mtw_cut5").Integral())),
#         "$b^{*}_{LH}$ 2800 GeV":int(round(signalLH2800_file.Get("Mtw_cut5").Integral()))
#     }
# }

# for r in rows:
#     totalbkg = 0
#     for b in ['QCD','$\\ttbar$','singletop (s-channel)','singletop (t, top)',"singletop (t, anti-top)","singletop (tW, top)","singletop (tW, anti-top)"]:
#         try:
#             totalbkg += dictTable[r][b]
#         except:
#             continue
#     dictTable[r]["$\\frac{s}{b}$ (1200 GeV)"] = round(float(dictTable[r]["$b^{*}$ 1200 GeV"])/float(totalbkg),1)
#     dictTable[r]["$\\frac{s}{b}$ (2000 GeV)"] = round(float(dictTable[r]["$b^{*}$ 2000 GeV"])/float(totalbkg),1)
#     dictTable[r]["$\\frac{s}{b}$ (2800 GeV)"] = round(float(dictTable[r]["$b^{*}$ 2800 GeV"])/float(totalbkg),1)

dictToLatexTable(dictTable,'cutflow_'+region+year+'.tex',roworder=rows,columnorder=columns,caption=captions[region+year])
