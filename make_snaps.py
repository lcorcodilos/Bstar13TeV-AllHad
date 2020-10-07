import ROOT
ROOT.ROOT.EnableImplicitMT(8)

rdfv3 = ROOT.ROOT.RDataFrame("Events","NanoVersionTesting_2017_RH2800/v3/*.root")
rdfv3_LH2800 = ROOT.ROOT.RDataFrame("Events","NanoVersionTesting_2017_RH2800/v3_LH2800/*.root")
rdfv6 = ROOT.ROOT.RDataFrame("Events","NanoVersionTesting_2017_RH2800/v6/*.root")

for rdf in [rdfv3,rdfv3_LH2800,rdfv6]:
    branchList = ROOT.vector('string')()
    branchList.clear()
    for c in rdf.GetColumnNames():
        if 'FatJet' in c or 'SubJet' in c: branchList.push_back(c)

    if rdf == rdfv3: name = 'v3.root'
    elif rdf == rdfv6: name = 'v6.root'
    elif rdf == rdfv3_LH2800: name = 'v3_LH2800.root'
    rdf.Snapshot("Events","NanoVersionTesting_2017_RH2800/"+name,branchList)