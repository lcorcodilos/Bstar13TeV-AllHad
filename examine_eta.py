import ROOT
from ROOT import *
gROOT.SetBatch(kTRUE)
gStyle.SetOptStat(0)

def setPad(pad,top=False,bottom=False):
    if top:
        pad.SetBottomMargin(0.0)
        pad.SetTopMargin(0.1)
    elif bottom:
        pad.SetBottomMargin(0.2)
        pad.SetTopMargin(0.0)
    else:
        pad.SetBottomMargin(0.0)
        pad.SetTopMargin(0.0)
    
    pad.SetLeftMargin(0.16)
    pad.SetRightMargin(0.05)
    
    pad.Draw()


##################################
# Build nice dict to store stuff #
##################################

main_dict = {
    16:{
        "QCD":{
            "file":TFile.Open('rootfiles/TWvariables16'+'_QCD_tau32loose_default.root')
        },
        "data":{
            "file":TFile.Open('rootfiles/TWvariables16'+'_data_tau32loose_default.root')
        }
    },
    17:{
        "QCD":{
            "file":TFile.Open('rootfiles/TWvariables17'+'_QCD_tau32loose_default.root')
        },
        "data":{
            "file":TFile.Open('rootfiles/TWvariables17'+'_data_tau32loose_default.root')
        }
    },
    18:{
        "QCD":{
            "file":TFile.Open('rootfiles/TWvariables18'+'_QCD_tau32loose_default.root')
        },
        "data":{
            "file":TFile.Open('rootfiles/TWvariables18'+'_data_tau32loose_default.root')
        }
    }
}

for y in main_dict.keys():
    for m in range(1200,3200,200):
        m_str = str(m)
        for h in ['LH','RH']:
            if (y == 18) or (m == 2800 and h == 'LH' and y ==17):
                continue
            main_dict[y]['signal'+h+m_str] = {
                "file":TFile.Open('rootfiles/TWvariables'+str(y)+'_signal'+h+m_str+'_tau32loose_default.root') 
            }

for y in main_dict.keys():
    for p in main_dict[y].keys():
        main_dict[y][p]['dEta'] = main_dict[y][p]['file'].Get('dEta')
        main_dict[y][p]['dEta'].Scale(1/main_dict[y][p]['dEta'].Integral())

main_dict['diff1617'] = {}
main_dict['diff1618'] = {}
main_dict['diff1718'] = {}

for p in ['QCD','data','signalLH1600','signalLH2600']:
    main_dict['diff1617'][p] = main_dict[16][p]['dEta'].Clone()
    main_dict['diff1617'][p].Add(main_dict[17][p]['dEta'],-1)
    main_dict['diff1617'][p].Divide(main_dict[16][p]['dEta'])

    if 'signal' not in p:
        main_dict['diff1618'][p] = main_dict[16][p]['dEta'].Clone()
        main_dict['diff1618'][p].Add(main_dict[18][p]['dEta'],-1)
        main_dict['diff1618'][p].Divide(main_dict[16][p]['dEta'])

        main_dict['diff1718'][p] = main_dict[17][p]['dEta'].Clone()      
        main_dict['diff1718'][p].Add(main_dict[18][p]['dEta'],-1)
        main_dict['diff1718'][p].Divide(main_dict[17][p]['dEta'])
        

#################
# Start drawing #
#################

c = TCanvas('c','c',1200,1200)
c.Divide(2,2)

ipad = 1
color = [kRed,kOrange,kBlue]
leg=[]
zeroLine = TLine(0, 0.0, 2.5, 0)
zeroLine.SetLineColor(kBlack)
for p in ['QCD','data','signalLH1600','signalLH2600']:
    c.cd(ipad)
    icolor = 0
    leg.append(TLegend(0.7,0.7,0.95,0.9))

    # Add diff plots to bottom
    main = TPad('mainpad','main',0, 0.3, 1, 1)
    sub = TPad('subpad','sub',0, 0, 1, 0.3)
    setPad(main,top=True)
    setPad(sub,bottom=True)

    # Determine max
    ymax = 0
    for y in [16,17,18]:
        if ('signal' in p and y == 18) or (p == 'signalLH2800' and y ==17):
            continue
        if main_dict[y][p]['dEta'].GetMaximum() > ymax:
            ymax = main_dict[y][p]['dEta'].GetMaximum()
    ymax = ymax * 1.1

    # Draw on main pad first
    main.cd()
    for y in [16,17,18]:
        if ('signal' in p and y == 18) or (p == 'signalLH2800' and y ==17):
            continue

        main_dict[y][p]['dEta'].SetMaximum(ymax)
        main_dict[y][p]['dEta'].SetFillColorAlpha(color[icolor],0.3)
        main_dict[y][p]['dEta'].SetTitle(p)
        main_dict[y][p]['dEta'].SetLineColor(kBlack)
        leg[ipad-1].AddEntry(main_dict[y][p]['dEta'],'20'+str(y),'fl')

        if y == 16: main_dict[y][p]['dEta'].Draw('hist')
        else: main_dict[y][p]['dEta'].Draw('samehist')

        icolor+=1


    # Now draw on diff/sub pad
    sub.cd()

    for i,diff in enumerate(['diff1617','diff1618','diff1718']):
        if ('signal' in p and '18' in diff) or (p == 'signalLH2800' and '17' in diff):
            continue

        main_dict[diff][p].SetMarkerStyle(20+i)
        main_dict[diff][p].SetMarkerColor(color[i])
        main_dict[diff][p].SetLineColorAlpha(kWhite,0.0) # Get rid of error bars

        main_dict[diff][p].SetTitle('')
        main_dict[diff][p].GetXaxis().SetLabelSize(0.09)
        main_dict[diff][p].GetYaxis().SetLabelSize(0.07)
        main_dict[diff][p].GetYaxis().SetTitle("(Year A - Year B)/Year A")
        main_dict[diff][p].GetYaxis().SetTitleSize(0.07)
        # main_dict[diff][p].GetYaxis().SetTitleOffset(1.1)


        if i == 0: main_dict[diff][p].Draw('p')
        else: main_dict[diff][p].Draw('same p')

        if diff == 'diff1617': leg[ipad-1].AddEntry(main_dict[diff][p],'(2016 - 2017)/2016','p')
        elif diff == 'diff1618': leg[ipad-1].AddEntry(main_dict[diff][p],'(2016 - 2018)/2016','p')
        elif diff == 'diff1718': leg[ipad-1].AddEntry(main_dict[diff][p],'(2017 - 2018)/2017','p')

    sub.cd()
    zeroLine.Draw()

    main.RedrawAxis()
    leg[ipad-1].Draw()
    ipad+=1

c.Print('eta_test.pdf','pdf')