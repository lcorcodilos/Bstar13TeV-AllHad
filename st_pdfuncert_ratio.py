import ROOT, math, array
ROOT.gStyle.SetOptStat(0)

def mean(hist):
    bin_sum = 0
    nbins = 0
    for ix in range(1,hist.GetNbinsX()+1):
        for iy in range(1,hist.GetNbinsY()+1):
            if hist.GetBinContent(ix,iy) > 0:
                bin_sum += hist.GetBinContent(ix,iy)
                nbins+=1
    return bin_sum/nbins

def std_dev(hist):
    m = mean(hist)
    nbins = 0
    sumsquares = 0
    for ix in range(1,hist.GetNbinsX()+1):
        for iy in range(1,hist.GetNbinsY()+1):
            if hist.GetBinContent(ix,iy) > 0:
                sumsquares += (hist.GetBinContent(ix,iy)-m)**2
                nbins+=1

    pre_sqrt = sumsquares/(nbins-1)
    return math.sqrt(pre_sqrt)


def copyHistWithNewXbins(thisHist,newXbins,copyName):
    # Make a copy with the same Y bins but new X bins
    ybins = []
    for iy in range(1,thisHist.GetNbinsY()+1):
        ybins.append(thisHist.GetYaxis().GetBinLowEdge(iy))
    ybins.append(thisHist.GetYaxis().GetXmax())

    ybins_array = array.array('f',ybins)
    ynbins = len(ybins_array)-1

    xbins_array = array.array('f',newXbins)
    xnbins = len(xbins_array)-1 

    # Use copyName with _temp to avoid overwriting if thisHist has the same name
    # We can do this at the end but not before we're finished with thisHist
    hist_copy = ROOT.TH2F(copyName+'_temp',copyName+'_temp',xnbins,xbins_array,ynbins,ybins_array)
    hist_copy.Sumw2()
    
    hist_copy.GetXaxis().SetName(thisHist.GetXaxis().GetName())
    hist_copy.GetYaxis().SetName(thisHist.GetYaxis().GetName())

    # Loop through the old bins
    for ybin in range(1,ynbins+1):
        # print 'Bin y: ' + str(binY)
        for xbin in range(1,xnbins+1):
            new_bin_content = 0
            new_bin_errorsq = 0
            new_bin_min = hist_copy.GetXaxis().GetBinLowEdge(xbin)
            new_bin_max = hist_copy.GetXaxis().GetBinUpEdge(xbin)

            # print '\t New bin x: ' + str(newBinX) + ', ' + str(newBinXlow) + ', ' + str(newBinXhigh)
            for old_xbin in range(1,thisHist.GetNbinsX()+1):
                if thisHist.GetXaxis().GetBinLowEdge(old_xbin) >= new_bin_min and thisHist.GetXaxis().GetBinUpEdge(old_xbin) <= new_bin_max:
                    # print '\t \t Old bin x: ' + str(oldBinX) + ', ' + str(thisHist.GetXaxis().GetBinLowEdge(oldBinX)) + ', ' + str(thisHist.GetXaxis().GetBinUpEdge(oldBinX))
                    # print '\t \t Adding content ' + str(thisHist.GetBinContent(oldBinX,binY))
                    new_bin_content += thisHist.GetBinContent(old_xbin,ybin)
                    new_bin_errorsq += thisHist.GetBinError(old_xbin,ybin)**2

            # print '\t Setting content ' + str(newBinContent) + '+/-' + str(sqrt(newBinErrorSq))
            if new_bin_content > 0:
                hist_copy.SetBinContent(xbin,ybin,new_bin_content)
                hist_copy.SetBinError(xbin,ybin,math.sqrt(new_bin_errorsq))

    # Will now set the copyName which will overwrite thisHist if it has the same name
    hist_copy.SetName(copyName)
    hist_copy.SetTitle(copyName)

    return hist_copy

def copyHistWithNewYbins(thisHist,newYbins,copyName):
    # Make a copy with the same X bins but new Y bins
    xbins = []
    for ix in range(1,thisHist.GetNbinsX()+1):
        xbins.append(thisHist.GetXaxis().GetBinLowEdge(ix))
    xbins.append(thisHist.GetXaxis().GetXmax())

    xbins_array = array.array('f',xbins)
    xnbins = len(xbins_array)-1

    ybins_array = array.array('f',newYbins)
    ynbins = len(ybins_array)-1

    # Use copyName with _temp to avoid overwriting if thisHist has the same name
    # We can do this at the end but not before we're finished with thisHist
    hist_copy = ROOT.TH2F(copyName+'_temp',copyName+'_temp',xnbins,xbins_array,ynbins,ybins_array)
    hist_copy.Sumw2()
    
    hist_copy.GetXaxis().SetName(thisHist.GetXaxis().GetName())
    hist_copy.GetYaxis().SetName(thisHist.GetYaxis().GetName())

    # Loop through the old bins
    for xbin in range(1,xnbins+1):
        # print 'Bin y: ' + str(binY)
        for ybin in range(1,ynbins+1):
            new_bin_content = 0
            new_bin_errorsq = 0
            new_bin_min = hist_copy.GetYaxis().GetBinLowEdge(ybin)
            new_bin_max = hist_copy.GetYaxis().GetBinUpEdge(ybin)

            # print '\t New bin x: ' + str(newBinX) + ', ' + str(newBinXlow) + ', ' + str(newBinXhigh)
            for old_ybin in range(1,thisHist.GetNbinsY()+1):
                if thisHist.GetYaxis().GetBinLowEdge(old_ybin) >= new_bin_min and thisHist.GetYaxis().GetBinUpEdge(old_ybin) <= new_bin_max:
                    # print '\t \t Old bin x: ' + str(oldBinX) + ', ' + str(thisHist.GetXaxis().GetBinLowEdge(oldBinX)) + ', ' + str(thisHist.GetXaxis().GetBinUpEdge(oldBinX))
                    # print '\t \t Adding content ' + str(thisHist.GetBinContent(oldBinX,binY))
                    new_bin_content += thisHist.GetBinContent(xbin,old_ybin)
                    new_bin_errorsq += thisHist.GetBinError(xbin,old_ybin)**2

            # print '\t Setting content ' + str(newBinContent) + '+/-' + str(sqrt(newBinErrorSq))
            if new_bin_content > 0:
                hist_copy.SetBinContent(xbin,ybin,new_bin_content)
                hist_copy.SetBinError(xbin,ybin,math.sqrt(new_bin_errorsq))

    # Will now set the copyName which will overwrite thisHist if it has the same name
    hist_copy.SetName(copyName)
    hist_copy.SetTitle(copyName)

    return hist_copy

def GetBinning(hist):
    xbins = []
    for ix in range(1,hist.GetNbinsX()+1):
        xbins.append(hist.GetBinLowEdge(ix))
    xbins.append(hist.GetXaxis().GetBinUpEdge(hist.GetNbinsY()))

    ybins = []
    for iy in range(1,hist.GetNbinsY()+1):
        ybins.append(hist.GetBinLowEdge(iy))
    ybins.append(hist.GetYaxis().GetBinUpEdge(hist.GetNbinsY()))

    return xbins,ybins

def remapToUnity(hist):
    # Map to [-0.5,0.5]
    ybins = array.array('d',[(hist.GetYaxis().GetBinLowEdge(b)-hist.GetYaxis().GetXmin())/(hist.GetYaxis().GetXmax()-hist.GetYaxis().GetXmin()) for b in range(1,hist.GetNbinsY()+1)]+[1])
    xbins = array.array('d',[(hist.GetXaxis().GetBinLowEdge(b)-hist.GetXaxis().GetXmin())/(hist.GetXaxis().GetXmax()-hist.GetXaxis().GetXmin()) for b in range(1,hist.GetNbinsX()+1)]+[1])

    remap = ROOT.TH2F(hist.GetName()+'_unit',hist.GetName()+'_unit',hist.GetNbinsX(),xbins,hist.GetNbinsY(),ybins)
    remap.Sumw2()

    for xbin in range(hist.GetNbinsX()+1):
        for ybin in range(hist.GetNbinsY()+1):
            remap.SetBinContent(xbin,ybin,hist.GetBinContent(xbin,ybin))
            remap.SetBinError(xbin,ybin,hist.GetBinError(xbin,ybin))

    return remap

c = ROOT.TCanvas('c','c',1600,1000)
c.Divide(3,2)

i = 1
keep = []
for s in ['ttbar','ttbar-semilep']:
    for y in ['16','17','18']:
        if y == '16' and s == 'ttbar-semilep': 
            i+=1
            continue
        f = ROOT.TFile.Open('rootfiles/TWpreselection%s_%s_tau32medium_default.root'%(y,s))

        h_nom_needsy = copyHistWithNewXbins(f.Get('MtwvMtPass'),[65,85,105,125,145,165,185,205,225,245,265,285],'MtwvMtPass_xrebinned')
        h_up_needsy = copyHistWithNewXbins(f.Get('MtwvMtPassPDFup'),[65,85,105,125,145,165,185,205,225,245,265,285],'MtwvMtPassPDFup_xrebinned')

        h_nom = copyHistWithNewYbins(h_nom_needsy,[1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500,2600,2800,3000,3300,3600,4000],'MtwvMtPass_final')
        h_up = copyHistWithNewYbins(h_up_needsy,[1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500,2600,2800,3000,3300,3600,4000],'MtwvMtPassPDFup_final')

        h_nom = remapToUnity(h_nom)
        h_up = remapToUnity(h_up)

        h_rat = h_up.Clone('%s_%s_ratio'%(y,s))
        h_rat.Divide(h_nom)

        h_fit = ROOT.TF2('%s_%s_fit'%(y,s),'[0]+[1]*y',h_rat.GetXaxis().GetXmin(),h_rat.GetXaxis().GetXmax(),h_rat.GetYaxis().GetXmin(),h_rat.GetYaxis().GetXmax())
        fr = h_rat.Fit(h_fit,'SN0')
        print '%s,%s: slope = %.2f +/- %.2f, intercept = %.2f +/- %.2f' %(y,s,fr.Parameter(1), fr.ParError(1), fr.Parameter(0), fr.ParError(0))

        h_mean = mean(h_rat)
        h_stddev = std_dev(h_rat)
        s_tex = 't#bar{t} all-had' if s == 'ttbar' else 't#bar{t} semi-lep'#s if s =='tW' else '#bar{t}W'
        if y == '16' and s == 'ttbar': s_tex = 't#bar{t} inclusive'
        h_rat.SetTitle('%s - %s - slope = %.2f +/- %.2f, intercept =  %.2f +/- %.2f'%(s_tex,y,fr.Parameter(1), fr.ParError(1), fr.Parameter(0), fr.ParError(0)))
        h_rat.SetMinimum(0.8)
        h_rat.SetMaximum(1.2)

        c.cd(i)
        h_rat.Draw('colz')
        i+=1
        keep.extend([f,h_nom,h_up,h_rat])

raw_input('')