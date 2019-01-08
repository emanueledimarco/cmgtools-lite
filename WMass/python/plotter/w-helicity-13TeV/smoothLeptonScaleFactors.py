#!/bin/env python

# Latest commands (check input file name)

# muons

# python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/tnp/egm_tnp_analysis/results/muFullData_RecoToSelection_etaBins0p1/selectionMu/egammaEffi.txt_EGM2D.root -o ~/www/wmass/13TeV/scaleFactors_Final/muon/recoToSelection_pt_25_55_eta0p1/ -c mu -n smoothEfficiency.root --muonRecoToSel

# python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/tnp/egm_tnp_analysis/results/muFullData_trigger_fineBin_noMu50/triggerMu/egammaEffi.txt_EGM2D.root -o ~/www/wmass/13TeV/scaleFactors_Final/muon/trigger_pt_25_55_eta0p1_forceAlwaysErf_noMu50/ -c mu -n smoothEfficiency.root -t
# old file /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/tnp/egm_tnp_analysis/results/muFullData_trigger_fineBin_noMu50/triggerMu/egammaEffi.txt_EGM2D.root


# electrons

# python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/tnp/egm_tnp_analysis/results/elFullData/triggerEl/egammaEffi.txt_EGM2D.root -o ~/www/wmass/13TeV/scaleFactors_Final/electron/trigger/ -c el -n smoothEfficiency.root -t -r 30 55


################################
# Exaples (obsolete)
################################

# muon trigger scale factors
#    python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/user/m/mdunser/public/triggerTnP_muons_fullData.root -o ~/www/wmass/13TeV/scaleFactors/muon/trigger/ -c mu -n smoothEfficiency.root -t

# muon isolation (replace ISO with ID for ID scale factors)
#    python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/CMSSW_8_0_25/src/CMGTools/WMass/data/scaleFactors/muons/efficienciesISO.root -o ~/www/wmass/13TeV/scaleFactors/muon/efficiency_ISO_GH/ -c mu -n smoothEfficiency.root -e GH -v ISO

# electron trigger
#    python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/e/emanuele/wmass/heppy/CMSSW_8_0_25/src/CMGTools/WMass/python/postprocessing/data/leptonSF/new2016_madeSummer2018/electrons_trigger_pt30to55.root -o ~/www/wmass/13TeV/scaleFactors/electron/trigger/ -c el -n smoothEfficiency.root -t

################################
################################


import ROOT, os, sys, re, array, math

sys.path.append(os.getcwd() + "/plotUtils/")
from utility import *

ROOT.gROOT.SetBatch(True)

import utilities
utilities = utilities.util()

def getReducedChi2andLabel(func):
    if func.GetNDF():
        reducedChi2 = func.GetChisquare() / func.GetNDF()
        lineChi2 = "#chi^{{2}} = {chi2:.2g} / {ndf}".format(chi2=func.GetChisquare(),ndf=int(func.GetNDF()))
    else:
        reducedChi2 = 0
        lineChi2 = "BAD! #chi^{{2}} = {chi2:.2g} / {ndf}".format(chi2=func.GetChisquare(),ndf=int(func.GetNDF()))

    return float(reducedChi2),lineChi2


def makeSFweightedAverage(f1, f2, w1, w2, hname, hnewname, uncertaintyRule="max"):

    # uncertaintyRule can be max, weight, diff
    # max takes the largest of the two uncertainties as the uncertainty on the mean
    # weight compute the usual uncertainty on the weighted mean
    # diff takes 1/2 of the difference as uncertainty (so the difference is the full error bars)

    tf = ROOT.TFile.Open(f1)        
    h1 =   tf.Get(hname).Clone(hname+"_1")
    if (h1 == 0):
        print "Error in makeSFweightedAverage(): could not retrieve histogram from input file %s. Exit" % f1
        quit()
    h1.SetDirectory(0)
    tf.Close()

    tf = ROOT.TFile.Open(f2)        
    h2 =   tf.Get(hname).Clone(hname+"_2")
    if (h2 == 0):
        print "Error in makeSFweightedAverage(): could not retrieve histogram from input file %s. Exit" % f2
        quit()
    h2.SetDirectory(0)
    tf.Close()

    #if not ROOT.TH1.CheckConsistency(h1,h2):
    #    print "Error in makeSFweightedAverage(): input histograms are not consistent. Exit"
    #    quit()
    xbins = h1.GetXaxis().GetXbins()
    ybins = [h1.GetYaxis().GetBinLowEdge(i) for i in range(1,h1.GetNbinsY()+2)]
    #ybins = h1.GetYaxis().GetXbins() # does not work, maybe because it has 500 elements and the maximum allowed is 255
    #print "nybins = %d" % h1.GetNbinsY()
    #print "xbins = %s (%d bins)" % (",".join(str(x) for x in xbins),len(xbins)-1)
    #print "ybins = %s" % ",".join(str(x) for x in ybins)
    hnew = ROOT.TH2D(hnewname,"",len(xbins)-1,array('d',xbins),len(ybins)-1,array('d',ybins))
    #hnew.SetDirectory(0)

    hnew.GetZaxis().SetTitle(h1.GetZaxis().GetTitle())
    hnew.SetTitle(h1.GetTitle())

    for ix in range(1,hnew.GetNbinsX()+1):
        for iy in range(1,hnew.GetNbinsY()+1):
            val1 = h1.GetBinContent(ix,iy)
            val2 = h2.GetBinContent(ix,iy)
            err1 = h1.GetBinError(ix,iy)
            err2 = h2.GetBinError(ix,iy)
            newval = (w1*val1 + w2*val2)/(w1+w2)
            if uncertaintyRule == "max":
                newerr = max(err1,err2)
            elif uncertaintyRule == "weight":
                newerr = math.sqrt(w1**2 * err1**2 + w2**2 * err2**2)/(w1+w2)
            elif uncertaintyRule == "diff":
                newerr = 0.5 * abs(val1-val2)
            else:
                print "Error in makeSFweightedAverage(): unknown uncertainty rule %s. Exit" % uncertaintyRule
                quit()
            hnew.SetBinContent(ix,iy,newval)
            hnew.SetBinError(ix,iy,newerr)

    return hnew

def copyHisto(h1, h2):

    if h1.GetDimension() != h2.GetDimension():
        print "Error in copyHisto(): histograms have different dimensions. Dim(h1)=%d  Dim(h2)=%d. Exit" % (h1.GetDimension(),h2.GetDimension())
        quit()

    if h1.GetDimension() == 1:
        for ix in range(h2.GetNbinsX()+2):
                h1.SetBinContent(ix,h2.GetBinContent(ix,iy))
                h1.SetBinError(ix,h2.GetBinError(ix,iy))
    elif h1.GetDimension() == 2:
        for ix in range(h2.GetNbinsX()+2):
            for iy in range(h2.GetNbinsY()+2):
                h1.SetBinContent(ix,iy,h2.GetBinContent(ix,iy))
                h1.SetBinError(ix,iy,h2.GetBinError(ix,iy))
    else:
        print "Error in copyHisto(): function not implemented for dimension > 2. Exit"
        quit()        


def fitTurnOn(hist, key, outname, mc, channel="el", hist_chosenFunc=0, drawFit=True, 
              isIso=False, isTrigger=False, isFullID=False, isMuonRecoToSel=False,
              fitRange=None,
              hist_reducedChi2=0,
              hist_ErfParam_vs_eta=0,
              hist_ErfCovMatrix_vs_eta=0  # TH3, eta on x and cov matrix in yz
              ):

    forcePol3 = False
    forceErfByKey = True  # if True, force the Erf specifyin gin which bin it should happen
    doOnlyErf = True
    excludeErfPlusLine = True # patch, Erf+line was useful with weird efficiencies, but if possible, a simple Erf is more meaningful

    originalMaxPt = hist.GetXaxis().GetBinLowEdge(1+hist.GetNbinsX())

    #drawFit = False
    # isIso is mainly for muons, for which ID ad ISO are separate

    isEle = True if channel == "el" else False
    if isEle: isMuonRecoToSel == False
    if not isEle: isFullID = False
    #print "isEle",str(isEle)
    #mc = "MC" if isMC else "Data"
    outdir = "{out}{mc}/".format(out=outname,mc=mc)
    createPlotDirAndCopyPhp(outdir)

    canvas = ROOT.TCanvas("canvas_%s_%s" % (mc,key),"",700,700)
    canvas.SetTickx(1)
    canvas.SetTicky(1)
    canvas.cd()
    canvas.SetLeftMargin(0.14)
    canvas.SetBottomMargin(0.12)
    canvas.SetRightMargin(0.06)
    canvas.cd()                           

    setTDRStyle()

    hist.SetLineColor(ROOT.kBlack)
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetMarkerStyle(20)
    hist.SetMarkerSize(1)

    hist.GetXaxis().SetTitle("%s p_{T} [GeV]" % ("electron" if channel == "el" else "muon"))
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.04)

    if fitRange != None:
        if fitRange[0] >= 0 and fitRange[1] >= 0:
            hist.GetXaxis().SetRangeUser(fitRange[0], fitRange[1])
        elif fitRange[0] >= 0:
            hist.GetXaxis().SetRangeUser(fitRange[0], hist.GetXaxis().GetBinLowEdge(1+hist.GetNbinsX()))
        elif fitRange[1] >= 0:
            hist.GetXaxis().SetRangeUser(hist.GetXaxis().GetBinLowEdge(1),fitRange[1])

    if mc == "SF":
        hist.GetYaxis().SetTitle("Data/MC scale factor")
    else:
        hist.GetYaxis().SetTitle("{mc} efficiency".format(mc=mc))
    hist.GetYaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetLabelSize(0.04)
    if isTrigger or isFullID or isMuonRecoToSel: hist.GetYaxis().SetRangeUser(0.98*hist.GetMinimum(), 1.02* hist.GetMaximum())
    else: 
        diff = hist.GetMaximum() - hist.GetMinimum()
        hist.GetYaxis().SetRangeUser(hist.GetMinimum() - diff, diff + hist.GetMaximum())
    #hist.GetYaxis().SetRangeUser(0.3,1.2)
    hist.SetStats(0)
    hist.Draw("EP")

    if isTrigger or isFullID or isMuonRecoToSel:
        fitopt = "QMFS+"  
        maxFitRange = hist.GetXaxis().GetBinLowEdge(1+hist.GetNbinsX())
        minFitRange = hist.GetXaxis().GetBinLowEdge(1)
        if fitRange != None:
            if "R" not in fitopt:
                fitopt = "R" + fitopt
            if fitRange[1] > 0:
                maxFitRange = fitRange[1]
            if fitRange[0] > 0:
                minFitRange = fitRange[0]        
    else:
        fitopt = "RQMFS+"
        maxFitRange = 120 #if isIso else 60
        minFitRange = 20
        #print "check"
        if "R" not in fitopt:
            fitopt = "R" + fitopt
        if fitRange != None:
            if fitRange[1] > 0:
                maxFitRange = fitRange[1]
            if fitRange[0] > 0:
                minFitRange = fitRange[0]        

    # here I decide to override the range of some fits to be able to use Erf (the graph is still drawn in the full range, because the TH1 range is already set above)
    # in case I ovverride the range for all bins with the option fitRange, the range here is still overriden, but the X axis setting is modified according to the option
    if isTrigger and not isEle:
        if mc == "Data":
            if any(key == x for x in [9]):
                maxFitRange = 45
            elif any(key == x for x in [14]):
                maxFitRange = 50
        elif mc == "MC":
            if any(key == x for x in [9]):
                maxFitRange = 45
            # elif any(key == x for x in [6, 7,8,33,39,43,46]):  # these are ok-ish even without this tuning, I might just force the Erf
            #     maxFitRange = 48


    ###################
    # fits
    ####################
    # Erf define here: https://root.cern.ch/doc/v608/namespaceTMath.html#a44e82992cba4684280c72679f0f39adc
    # Erf(x) = (2/sqrt(pi)) Integral(exp(-t^2))dt between 0 and x 
    tf1_erf = ROOT.TF1("tf1_erf","[0]*TMath::Erf((x-[1])/[2])",minFitRange,maxFitRange) 
    tf1_erf.SetParameter(0,1.0)
    tf1_erf.SetParameter(1,38)
    if not isEle and isIso and key == 6: tf1_erf.SetParameter(1,30)
    tf1_erf.SetParameter(2,3.0)
    tf1_erf.SetLineWidth(2)
    tf1_erf.SetLineColor(ROOT.kOrange+1)

    tf1_ln = ROOT.TF1("tf1_ln","[0]*TMath::Log([2]*x-[1])",minFitRange,maxFitRange)
    tf1_ln.SetParameter(0,1)
    tf1_ln.SetParameter(1,30)
    tf1_ln.SetParameter(2,1)
    tf1_ln.SetLineWidth(2)
    tf1_ln.SetLineColor(ROOT.kBlue)

    # tf1_ln2 = ROOT.TF1("tf1_ln2","[0]*TMath::Log([2]*x-[1]) + [3] + [4]*x",minFitRange,maxFitRange)
    # tf1_ln2.SetParameter(0,1)
    # tf1_ln2.SetParameter(1,30)
    # tf1_ln2.SetParameter(2,1)
    # tf1_ln2.SetParameter(3,0)    
    # tf1_ln2.SetParameter(4,0); tf1_ln2.SetParLimits(4,0, 1e12) 
    # tf1_ln2.SetLineWidth(2)
    # tf1_ln2.SetLineColor(ROOT.kOrange+1)

    tf1_pol1 = ROOT.TF1("tf1_pol1","pol1",minFitRange,maxFitRange)
    tf1_pol1.SetLineWidth(2)
    tf1_pol1.SetLineColor(ROOT.kBlue)

    tf1_pol2 = ROOT.TF1("tf1_pol2","pol2",minFitRange,maxFitRange)
    tf1_pol2.SetLineWidth(2)
    tf1_pol2.SetLineColor(ROOT.kGreen+2)

    tf1_pol3 = ROOT.TF1("tf1_pol3","pol3",minFitRange,originalMaxPt) # with pol3 use always the maximum pt
    tf1_pol3.SetLineWidth(2)
    tf1_pol3.SetLineColor(ROOT.kCyan+1)

    # tf1_sqrt = ROOT.TF1("tf1_sqrt","[0]*TMath::Sqrt([2]*x-[1])",minFitRange,maxFitRange)
    # tf1_sqrt.SetParameter(0,1)
    # tf1_sqrt.SetParameter(1,30)
    # tf1_sqrt.SetParameter(2,1)
    # tf1_sqrt.SetLineWidth(2)
    # tf1_sqrt.SetLineColor(ROOT.kOrange+2)

    # tf1_exp = ROOT.TF1("tf1_exp","[0] - [3]*TMath::Exp([1]*x-[2])",minFitRange,maxFitRange)
    # tf1_exp.SetParameter(0,1)
    # tf1_exp.SetParameter(1,-5);    tf1_exp.SetParLimits(1,-1e12,0.0) # negative
    # tf1_exp.SetParameter(2,30)
    # tf1_exp.SetParameter(3,1); #    tf1_exp.SetParLimits(3,0,10) # positive
    # tf1_exp.SetLineWidth(2)
    # tf1_exp.SetLineColor(ROOT.kOrange+1)

    tf1_erf2 = ROOT.TF1("tf1_erf2","[0]*TMath::Erf((x-[1])/[2]) + [4] + [3]*x",minFitRange,maxFitRange) 
    tf1_erf2.SetParameter(0,1.0); #tf1_erf2.SetParLimits(0,0.1,1e12)
    tf1_erf2.SetParameter(1,32)
    tf1_erf2.SetParameter(2,3.0)

    # tune Erf+line
    if isTrigger:
        if isEle:
            if mc =="Data":
                if key == 29:
                    tf1_erf2.SetParameter(1,31)
            elif mc == "MC":
                if any(key == x for x in [20,29]):
                    tf1_erf2.SetParameter(1,31)                
                elif key == 12:
                    tf1_erf2.SetParameter(1,30.545)
                    tf1_erf2.SetParameter(2,5.0)
                elif key == 17:
                    tf1_erf2.SetParameter(1,31.2)
        else:
            tf1_erf2.SetParameter(1,30)
            if mc == "Data":
                # with narrow pt range [26,45]
                # if key == 27:
                #     tf1_erf2.SetParameter(1,32)
                # # elif key == 13:
                # #     tf1_erf2.SetParameter(1,29.5)
                # elif any(key == x for x in [11,14,26]):
                #     tf1_erf2.SetParameter(1,29.5)
                # elif any(key == x for x in [10]):
                #     tf1_erf2.SetParameter(1,30.5)
                #     tf1_erf2.SetParameter(2,4.0)
                # elif key == 23:
                #     tf1_erf2.SetParameter(1,31.2)
                #     tf1_erf2.SetParameter(2,4.0)
                # elif key == 13:
                #     tf1_erf2.SetParameter(1,29.65)
                #     tf1_erf2.SetParameter(2,4.0)                
                # with broader pt range [24,55]
                # if key == 27:
                #     tf1_erf2.SetParameter(1,32)
                # # elif key == 13:
                # #     tf1_erf2.SetParameter(1,29.5)
                # elif any(key == x for x in [11,14,26]):
                #     tf1_erf2.SetParameter(1,29.5)
                # elif any(key == x for x in [10]):
                #     tf1_erf2.SetParameter(1,30.5)
                #     tf1_erf2.SetParameter(2,4.0)
                # elif key == 23:
                #     tf1_erf2.SetParameter(1,31.2)
                #     tf1_erf2.SetParameter(2,4.0)
                if key == 13:
                    tf1_erf2.SetParameter(1,26.4)
                    tf1_erf2.SetParameter(2,4.0)
                elif key == 26:
                    tf1_erf2.SetParameter(1,26.35)
                    tf1_erf2.SetParameter(2,4.0)
                    #forcePol3 = True
            if mc == "MC":
                if any(key == x for x in [0,8,26,27,37]):
                    tf1_erf2.SetParameter(1,29.5)
                elif key == 33:
                    tf1_erf2.SetParameter(1,27)
    # tune Erf
    if isTrigger:
        if isEle:
            # if mc =="Data":
            #     if key == 29:
            #         tf1_erf2.SetParameter(1,31)
            # elif mc == "MC":
            #     if any(key == x for x in [20,29]):
            #         tf1_erf2.SetParameter(1,31)                
            #     elif key == 12:
            #         tf1_erf2.SetParameter(1,30.545)
            #         tf1_erf2.SetParameter(2,5.0)
            #     elif key == 17:
            #         tf1_erf2.SetParameter(1,31.2)
            pass
        else:            
            # old tuning, then files changed
            # if mc == "Data":
            #     if any(key == x for x in [8,11,25,26,29,34]):
            #         tf1_erf.SetParameter(1,32)
            #     elif any(key == x for x in [9,23,28]):
            #         tf1_erf.SetParameter(1,27)
            #         tf1_erf.SetParameter(2,2.0)
            # if mc == "MC":
            #     if any(key == x for x in [3,9,23,25,26,28]):
            #         tf1_erf.SetParameter(1,32)
            pass
            if mc == "Data":
                pass
            #    if any(key == x for x in [1,39]):
            #        tf1_erf.SetParameter(1,32)
                #elif any(key == x for x in [9,23,28]):
                #    tf1_erf.SetParameter(1,27)
                #    tf1_erf.SetParameter(2,2.0)
            elif mc == "MC":
                if any(key == x for x in [33]):
                    tf1_erf.SetParameter(1,30)
                    tf1_erf.SetParameter(2,5.0)

    if isFullID:
        if mc == "Data":
            if key == 0:
                tf1_erf.SetParameter(1,32)
                tf1_erf.SetParameter(2,3.0)
            #elif any(key == x for x in [8,11,25,26,29,34]):
            #    tf1_erf.SetParameter(1,32)
        elif mc == "MC":
            if key == 37:
                tf1_erf.SetParameter(1,32)
                tf1_erf.SetParameter(2,3.0)
            #elif any(key == x for x in [8,11,25,26,29,34]):
            #    tf1_erf.SetParameter(1,32)


    if isMuonRecoToSel:
        if mc == "Data":
            #if key == 17:
            #    tf1_erf.SetParameter(1,32)
            #    tf1_erf.SetParameter(2,3.0)            
            if any(key == x for x in [5,17,42]):
                tf1_erf.SetParameter(1,32)      
                tf1_erf.SetParameter(2,3.0)
        elif mc == "MC":
            if key == 23:
                tf1_erf.SetParameter(1,32)                
            elif any(key == x for x in [5,42]):
                tf1_erf.SetParameter(1,32)

    tf1_erf2.SetParameter(3,0.0); #tf1_erf2.SetParLimits(3,0,1e12)
    tf1_erf2.SetParameter(4,0)
    tf1_erf2.SetLineWidth(2)
    tf1_erf2.SetLineColor(ROOT.kRed+1)

    erf_fitresPtr = None

    # fit and draw (if required)
    if isTrigger or isFullID or isMuonRecoToSel:
        erf_fitresPtr = hist.Fit(tf1_erf,fitopt)        
        # hist.Fit(tf1_ln2,fitopt)   
        fitoptOther = fitopt
        if doOnlyErf:
            fitoptOther = "0" + fitopt # fit but do not draw
        hist.Fit(tf1_ln,fitoptOther)
        hist.Fit(tf1_erf2,fitoptOther)        
        # hist.Fit(tf1_sqrt,fitoptOther)        
        # hist.Fit(tf1_exp,fitoptOther)        
        hist.Fit(tf1_pol2,fitoptOther)        
        hist.Fit(tf1_pol3,fitopt)        
    else:
        #if isIso or isMuonRecoToSel: hist.Fit(tf1_erf,fitopt)        
        if isIso: erf_fitresPtr = hist.Fit(tf1_erf,fitopt)        
        else:
            tf1_pol3.SetLineColor(ROOT.kRed+1)
            hist.Fit(tf1_pol1,fitopt)        
            hist.Fit(tf1_pol2,fitopt)        
            hist.Fit(tf1_pol3,fitopt)        
            # TSpline
            xval = []
            yval = []
            for i in range(1,hist.GetNbinsX()+1):
                xval.append(hist.GetBinCenter(i))
                yval.append(hist.GetBinContent(i))
            #spl = ROOT.TSpline3("spline3",array('d',xval),array('d',yval),len(xval),"b1e1")
            spl = ROOT.TSpline3(hist,"b1e1")
            spl.SetLineWidth(2)
            spl.SetLineColor(ROOT.kRed+3)
            spl.Draw("pclsame")

    if mc in ["Data","MC"] and erf_fitresPtr != None:
        fitstatus = int(erf_fitresPtr)
        #print "fit status: ", str(fitstatus)
        #print "fit status: ", str(erf_fitresPtr.Status())
        # status is 0 if all is ok (if option M was used, might be 4000 in case the improve command of Minuit failed, but it is ok)
        # without M the fit sometimes fails and should be tuned by hand (option M does it in some case)
        if fitstatus != 0 and fitstatus != 4000: print "##### WARNING: FIT HAS STATUS --> ", str(fitstatus)
        cov = erf_fitresPtr.GetCovarianceMatrix()
        #cov.Print()
        #print "%s" % str(erf_fitresPtr.CovMatrix(1,1))
        #print "Covariance matrix status = ", str(erf_fitresPtr.CovMatrixStatus())
        # covariance matrix status code using Minuit convention : =0 not calculated, =1 approximated, =2 made pos def , =3 accurate 
        if erf_fitresPtr.CovMatrixStatus() != 3: print "##### WARNING: COVARIANCE MATRIX HAS STATUS --> ", str(erf_fitresPtr.CovMatrixStatus())
        if hist_ErfCovMatrix_vs_eta: 
            # erf has 3 parameters
            for i in range(3):
                for j in range(3):
                    hist_ErfCovMatrix_vs_eta.SetBinContent(key+1,i+1,j+1,erf_fitresPtr.CovMatrix(i,j))
            

    upLeg = 0.45 if isEle else 0.15 if isIso else 0.4
    if doOnlyErf:
        upLeg = 0.4
    leg = ROOT.TLegend(0.5, 0.2, 0.9, upLeg)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    legEntry = {}
    legEntry[tf1_erf2.GetName()] = "Erf[x] + ax + b"
    legEntry[tf1_erf.GetName()]  = "Erf[x]"
    legEntry[tf1_pol2.GetName()] = "pol2"
    legEntry[tf1_pol3.GetName()] = "pol3"
    legEntry[tf1_ln.GetName()]   = "a ln(bx + c)"
    legEntry[tf1_pol1.GetName()] = "pol1"

    if isTrigger or isFullID or isMuonRecoToSel:
        # if not isFullID: leg.AddEntry(tf1_erf2, "Erf[x] + ax + b", 'LF')
        # else           : leg.AddEntry(combpol2, "2 pol2", 'LF')
        if not doOnlyErf:
            leg.AddEntry(tf1_erf2, "Erf[x] + ax + b", 'LF')
            leg.AddEntry(tf1_ln,  "a ln(bx + c)", "LF")
            #leg.AddEntry(tf1_ln2, "a ln(bx + c) + dx + e", "LF")
            #leg.AddEntry(tf1_sqrt,"a #sqrt{bx +c} +cx", "LF")
            leg.AddEntry(tf1_erf, "Erf[x]", 'LF')
            #leg.AddEntry(tf1_exp, "a - exp(-bx -c) +dx", "LF")
            leg.AddEntry(tf1_pol2,"pol2", "LF")
            leg.AddEntry(tf1_pol3,"pol3", "LF")
        else:
            leg.AddEntry(tf1_erf, "Erf[x]", 'LF')
            leg.AddEntry(tf1_pol3,"pol3", "LF")
    else:
        if isIso: leg.AddEntry(tf1_erf, "Erf[x]", 'LF')
        else:
            leg.AddEntry(tf1_pol1,"pol1", "LF")
            leg.AddEntry(tf1_pol2,"pol2", "LF")
            leg.AddEntry(tf1_pol3,"pol3", "LF")
            leg.AddEntry(spl,"spline", "LF")
    leg.Draw('same')
    ###################
    # fits
    ####################

    canvas.RedrawAxis("sameaxis")

    setTDRStyle()
    ROOT.gStyle.SetOptTitle(1)  # use histogram title with binning as canvas title

    # for ext in ["pdf","png"]:
    #     if mc == "SF":
    #         canvas.SaveAs("{out}ScaleFactorVsPt_{mc}_{ch}_eta{b}.{ext}".format(out=outdir,mc=mc,ch=channel,b=key,ext=ext))            
    #     else:
    #         canvas.SaveAs("{out}effVsPt_{mc}_{ch}_eta{b}.{ext}".format(out=outdir,mc=mc,ch=channel,b=key,ext=ext))            

    if isTrigger or isFullID or isMuonRecoToSel:
        fit_erf =  hist.GetFunction(tf1_erf.GetName())
        fit_pol2 = hist.GetFunction(tf1_pol2.GetName())
        fit_pol3 = hist.GetFunction(tf1_pol3.GetName())
        fit_erf2 =  hist.GetFunction(tf1_erf2.GetName())
        fit_ln =   hist.GetFunction(tf1_ln.GetName())
        #fit_ln2 = hist.GetFunction(tf1_ln2.GetName())
        #fit_sqrt = hist.GetFunction(tf1_sqrt.GetName())
        #fit_exp = hist.GetFunction(tf1_exp.GetName())
    else:
        if isIso: fit_erf = hist.GetFunction(tf1_erf.GetName())
        else:
            fit_pol1 = hist.GetFunction(tf1_pol1.GetName())
            fit_pol2 = hist.GetFunction(tf1_pol2.GetName())
            fit_pol3 = hist.GetFunction(tf1_pol3.GetName())

    functions = {}
    if isTrigger or isFullID or isMuonRecoToSel:
        functions[tf1_erf.GetName()] = fit_erf
        functions[tf1_pol2.GetName()] = fit_pol2
        functions[tf1_pol3.GetName()] = fit_pol3
        functions[tf1_ln.GetName()] = fit_ln
        #functions[tf1_ln2.GetName()] = fit_ln2
        #functions[tf1_sqrt.GetName()] = fit_sqrt
        functions[tf1_erf2.GetName()] = fit_erf2
        #functions[tf1_exp.GetName()] = fit_exp
    else:
        if isIso: functions[tf1_erf.GetName()] = fit_erf
        else:
            functions[tf1_pol1.GetName()] = fit_pol1
            functions[tf1_pol2.GetName()] = fit_pol2
            functions[tf1_pol3.GetName()] = fit_pol3

    lat = ROOT.TLatex()
    line = ""
    lineChi2 = ""
    lat.SetNDC();
    lat.SetTextSize(0.045);
    lat.SetTextFont(42);
    lat.SetTextColor(1);
    xmin = 0.20 
    yhi = 0.85
    reducedChi2 = 0

    #if isEle==False and (isIso or isMuonRecoToSel):
    if isEle==False and (isIso):
        retFunc = fit_erf
    else:
        chi2 = 1000000.0
        funcMinChi2 = 0
        for name,f in functions.iteritems():        
            if doOnlyErf and  name != tf1_erf.GetName(): continue
            if excludeErfPlusLine and name == tf1_erf2.GetName(): continue
            #print "Name: %s func %s" % (name, f) 
            if f.GetNDF() == 0: continue
            if name == tf1_pol3.GetName(): continue
            if f.GetChisquare() < chi2: 
                chi2 = f.GetChisquare()
                funcMinChi2 = f
        #print "Function %s had the best Chi2/Ndof: %.3f/%d among non-pol3" % (funcMinChi2.GetName(),funcMinChi2.GetChisquare(),funcMinChi2.GetNDF())
        #print "pol3 Chi2/Ndof: %.3f/%d" % (fit_pol3.GetChisquare(),fit_pol3.GetNDF())

        if funcMinChi2 == 0:
            print "="*20
            print "Warning: no function had more than 0 degrees of freedom. Returning pol2 function"
            print "="*20
            #return fit_pol3
            line = "Best fit: pol2 (forced)"
            retFunc = fit_pol2
        else:
            if forcePol3:
                retFunc = fit_pol3
            else:
                nChi2Sigma = abs(funcMinChi2.GetChisquare()-funcMinChi2.GetNDF())/math.sqrt(2.0*funcMinChi2.GetNDF())  # Chi2 variance is 2*Ndof
                nChi2Sigma_pol3 = abs(fit_pol3.GetChisquare()-fit_pol3.GetNDF())/math.sqrt(2.0*fit_pol3.GetNDF()) if fit_pol3.GetNDF() else 999

                # pol3 will generally fit very well also in case of weird points
                # for good looking points, pol3 might be better because it can change curvature, while other functions cannot (which would be more physical)
                # allow non-pol3 fit to have Chi2 within 2 standard deviation from the expected one
                # in this case choose that value, otherwise use the one closer to expected Chisquare
                if nChi2Sigma < 3:  
                    retFunc = funcMinChi2
                elif nChi2Sigma_pol3 < nChi2Sigma:
                    retFunc = fit_pol3
                else:
                    retFunc = funcMinChi2                

            line = "Best fit: " + legEntry[retFunc.GetName()] + (" (forced)" if forcePol3 else "")

        #return funcMinChi2

    if forceErfByKey:
        if isTrigger and not isEle:
            pass
            if mc == "Data":
                pass
                #if any(key == x for x in [14,24]):
                #    retFunc = fit_erf
                #    line = "Best fit: Erf[x] (forced)"
            elif mc == "MC":
                if any(key == x for x in [10]):  # these are ok-ish even without this tuning, I might just force the Erf
                    retFunc = fit_erf
                    line = "Best fit: Erf[x] (forced)"
        elif isTrigger and isEle:
            if retFunc.GetName() != fit_erf.GetName():
                retFunc = fit_erf
                line = "Best fit: Erf[x] (forced)"
  

    reducedChi2,lineChi2 = getReducedChi2andLabel(retFunc)
    if hist_reducedChi2: hist_reducedChi2.Fill(reducedChi2)
    if hist_chosenFunc: hist_chosenFunc.Fill(retFunc.GetName(),1)    
            
    lat.DrawLatex(xmin,yhi,line);
    lat.DrawLatex(xmin,yhi-0.05,lineChi2);
    for ext in ["pdf","png"]:
        if mc == "SF":
            canvas.SaveAs("{out}ScaleFactorVsPt_{mc}_{ch}_eta{b}.{ext}".format(out=outdir,mc=mc,ch=channel,b=key,ext=ext))            
        else:
            canvas.SaveAs("{out}effVsPt_{mc}_{ch}_eta{b}.{ext}".format(out=outdir,mc=mc,ch=channel,b=key,ext=ext))                            

    if hist_ErfParam_vs_eta and retFunc.GetName() == tf1_erf.GetName():  
        # key is the eta bin number, but starts from 0, so add 1
        hist_ErfParam_vs_eta.SetBinContent(key+1,1,retFunc.GetParameter(0))
        hist_ErfParam_vs_eta.SetBinError(key+1,1,retFunc.GetParError(0))
        hist_ErfParam_vs_eta.SetBinContent(key+1,2,retFunc.GetParameter(1))
        hist_ErfParam_vs_eta.SetBinError(key+1,2,retFunc.GetParError(1))
        hist_ErfParam_vs_eta.SetBinContent(key+1,3,retFunc.GetParameter(2))
        hist_ErfParam_vs_eta.SetBinError(key+1,3,retFunc.GetParError(2))

    return retFunc
        
        # get pol2 parameters (parameter number 0,1,2 correspond to constant term, x, x^2 respectively)
        #return fit.GetParameter(0),fit.GetParError(0),fit.GetParameter(1),fit.GetParError(1),fit.GetParameter(2),fit.GetParError(2)    
        #return fit_pol2


def smoothSpline(hist, key, outname, channel="el", drawFit=True):

    #drawFit = False

    isEle = True if channel == "el" else False
    outdir = "{out}spline/".format(out=outname)
    createPlotDirAndCopyPhp(outdir)

    canvas = ROOT.TCanvas("canvas_%s" % key,"",700,700)
    canvas.SetTickx(1)
    canvas.SetTicky(1)
    canvas.cd()
    canvas.SetLeftMargin(0.14)
    canvas.SetBottomMargin(0.12)
    canvas.SetRightMargin(0.06)
    canvas.cd()                           

    setTDRStyle()

    hist.SetLineColor(ROOT.kBlack)
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetMarkerStyle(20)
    hist.SetMarkerSize(1)

    hist.GetXaxis().SetTitle("%s p_{T} [GeV]" % ("electron" if channel == "el" else "muon"))
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.04)
    hist.GetYaxis().SetTitle("Correction")
    hist.GetYaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetLabelSize(0.04)
    miny = 0.95*hist.GetMinimum() if hist.GetMinimum() > 0 else 1.1*hist.GetMinimum()
    hist.GetYaxis().SetRangeUser(miny, 1.05* hist.GetMaximum())
    #hist.GetYaxis().SetRangeUser(0.3,1.2)
    hist.SetStats(0)
    hist.Draw("EP")

    # TSpline
    xval = []
    yval = []
    for i in range(1,hist.GetNbinsX()+1):
        xval.append(hist.GetBinCenter(i))
        yval.append(hist.GetBinContent(i))
    #spl = ROOT.TSpline3("spline3",array('d',xval),array('d',yval),len(xval),"b1e1")
    spl = ROOT.TSpline3(hist,"b1e1")
    spl.SetLineWidth(2)
    spl.SetLineColor(ROOT.kRed+1)
    spl.Draw("pclsame")

    leg = ROOT.TLegend(0.5, 0.2, 0.9, 0.45 if isEle else 0.3 if isIso else 0.4)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.AddEntry(spl, "spline", 'LF')

    for ext in ["pdf","png"]:
        canvas.SaveAs("{out}CorrectionFactorVsPt_{ch}_eta{b}.{ext}".format(out=outdir,ch=channel,b=key,ext=ext))            

    return spl

def smoothSomeFile(fname,hname,outname,outfilename,channel,widthPt):

    tf = ROOT.TFile.Open(fname)        
    hist = tf.Get(hname)
    if (hist == 0):
        print "Error: could not retrieve hist from input file %s. Exit" % options.inputfile
        quit()
    hist.SetDirectory(0)
    tf.Close()

    etabins = hist.GetXaxis().GetXbins()
    ptbins  = hist.GetYaxis().GetXbins()
    hist.SetTitle("")
    histSmooth = ROOT.TH2D("histSmooth","",
                           len(etabins)-1,array('d',etabins),
                           int(math.ceil(hist.GetYaxis().GetBinLowEdge(1+hist.GetNbinsY()) - hist.GetYaxis().GetBinLowEdge(1))/widthPt), # bins of 0.2 GeV
                           hist.GetYaxis().GetBinLowEdge(1),hist.GetYaxis().GetBinLowEdge(1+hist.GetNbinsY())        
                           )

    histpt = {}
    for x in range(1,hist.GetNbinsX()+1):
        bin = x-1
        histpt[bin] = ROOT.TH1D("histpt_{b}".format(b=str(bin)),
                                "%.4g <= #eta < %.4g" % (hist.GetXaxis().GetBinLowEdge(x), hist.GetXaxis().GetBinLowEdge(x+1)),
                                len(ptbins)-1,array('d',ptbins)
                                )
        for y in range(1,hist.GetNbinsY()+1):
            histpt[bin].SetBinContent(y,hist.GetBinContent(x,y))         
            histpt[bin].SetBinError(y,hist.GetBinError(x,y))
            
    bestFit_hist = {}
    for key in histpt:

        spline = smoothSpline(histpt[key],key,outname,channel=channel)
        for ipt in range(1,histSmooth.GetNbinsY()+1):
            ptval = histSmooth.GetYaxis().GetBinCenter(ipt)
            histSmooth.SetBinContent(key+1,ipt, spline.Eval(ptval))

    
    setTDRStyle()
    lepton = "electron" if channel == "el" else "muon"
    drawCorrelationPlot(hist,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Original value::-0.2,1.2",
                        "original_{hn}".format(hn=hname),"ForceTitle",outname,1,1,False,False,False,1,palette=55)
    drawCorrelationPlot(histSmooth,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Smoothed value::-0.2,1.2",
                        "smooth_{hn}".format(hn=hname),"ForceTitle",outname,1,1,False,False,False,1,palette=55)

    tf = ROOT.TFile.Open(outname+outfilename,'recreate')
    histSmooth.Write()
    hist.Write("histOriginal")
    tf.Close()
    print ""
    print "Created file %s" % (outname+outfilename)
    print ""

        
if __name__ == "__main__":
            
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options]')
    parser.add_option('-i','--input', dest='inputfile', default='', type='string', help='input root file with TH2. Not needed when using --make-weighted-average')
    parser.add_option('-o','--outdir', dest='outdir', default='', type='string', help='output directory to save things')
    parser.add_option('-n','--outfilename', dest='outfilename', default='', type='string', help='Name of output file to save fit results')
    parser.add_option('-c','--channel', dest='channel', default='', type='string', help='name of the channel (mu or el)')
    parser.add_option('-e','--era',     dest='era',     default='', type='string', help='For muons: select data era GtoH or BtoF as -e GH or -e BF')
    parser.add_option('-v','--var',     dest='variable',default='', type='string', help='For muons: select variable: ISO or ID')
    parser.add_option('-r','--range',     dest='range', type="float", nargs=2, default=(-1, -1), help='Pt range fo the fit: pass two values for min and max. If one of the (or both) is negative, the corresponding histogram range is used')
    parser.add_option('-w','--width-pt',     dest='widthPt',default='0.2', type='float', help='Pt bin width for the smoothed histogram')
    parser.add_option('-t','--trigger', dest='isTriggerScaleFactor',action="store_true", default=False, help='Says if using trigger scale factors (electron and muon share the same root file content)')
    parser.add_option(     '--muonRecoToSel', dest='isMuonRecoToSel',action="store_true", default=False, help='Says if using muon reco->selection scale factors')
    parser.add_option(     '--residualPtCorr', dest='isResidualPtCorrScaleFactor',action="store_true", default=False, help='For electrons: pt correction residual scale factor')
    parser.add_option(     '--fullID', dest='isFullIDScaleFactor',action="store_true", default=False, help='For electrons: says if using fullID scale factor')
    parser.add_option(     '--save-TF1', dest='saveTF1',action="store_true", default=False, help='Save TF1 as well, not just TH2 with many bins (note that they are not saved when making averages between eras')
    parser.add_option(     '--make-weighted-average', dest='isWeightedAverage',action="store_true", default=False, help='To be used if you are averaging the scale factors (must use other options to pass the inputs. For example, muons have two sets of ID and ISO scale factors for different eras')
    parser.add_option(    '--files-average', dest='filesAverage',default='', type='string', help='Comma separated list of two files')
    parser.add_option(    '--weights-average', dest='weightsAverage',default='', type='string', help='Comma separated list of two weights (can be luminosity for era BF and GH, they are 19.91/fb and 16.30/fb respectively)')
    parser.add_option(    '--average-uncertainty-mode', dest='averageUncertaintyMode',default='max', type='string', help='Can be max, weight, diff (see function makeSFweightedAverage)')
    parser.add_option(    '--hists-average', dest='histsAverage',default='', type='string', help='Comma separated list of histograms to average (pass names, one for each average, it is assumed the names in each file are the same)')
    (options, args) = parser.parse_args()


    ROOT.TH1.SetDefaultSumw2()

    if options.isTriggerScaleFactor:
        if options.era or options.variable:
            print "Error: option -t is incompatible with -e and -v. Exit"
            quit()
        if options.isFullIDScaleFactor:
            print "Error: option -t is incompatible with --fullID. Exit"
            quit()
    
    channel = options.channel
    if channel not in ["el","mu"]:
        print "Error: unknown channel %s (select 'el' or 'mu')" % channel
        quit()
    isEle = True if channel == "el" else False
    lepton = "electron" if channel == "el" else "muon"

    if options.isMuonRecoToSel:
        if channel == "el":
            print "Error: option --muonRecoToSel is only for muons. Exit"
            quit()
        else:
            if options.era or options.variable:
                print "Error: option --muonRecoToSel is incompatible with -e and -v. Exit"
                quit()

    if not isEle:
        if not options.isTriggerScaleFactor and not options.isMuonRecoToSel:
            print "Warning: you didn't use option -t and --muonRecoToSel, so I assume these are not trigger scale factors or for full reco->sel"
            if not options.isWeightedAverage:
                if options.era not in ["BF","GH"]:
                    print "Error: you should specify a data range for muons using option -e BF|GH. Exit"                                
                    quit()                                                          
            elif options.era:
                print "Error: option --make-weighted-average is incompatible with -e. Exit"                                
                quit()                                                          

            if options.variable not in ["ID","ISO",]:
                print "Error: you should specify a variable with option -v ID|ISO. Exit"                                
                quit()                                    
        if options.isFullIDScaleFactor:
            print "Error: option --fullID is only for electrons. Exit"
            quit()


    if options.outdir:
        outname = options.outdir
        addStringToEnd(outname,"/",notAddIfEndswithMatch=True)
        createPlotDirAndCopyPhp(outname)
    else:
        print "Error: you should specify an output folder using option -o <name>. Exit"
        quit()

    if not options.outfilename:
        print "Error: you should specify an output file name using option -n <name>. Exit"
        quit()
    outfilename = ".".join(options.outfilename.split('.')[:-1]) + "_{lep}".format(lep="electrons" if channel=="el" else "muons")
    if options.era: outfilename = outfilename + "_" + options.era
    if options.isWeightedAverage: outfilename = outfilename + "_full2016"
    if options.variable: outfilename = outfilename + "_" + options.variable
    if options.isTriggerScaleFactor: outfilename = outfilename + "_trigger"
    if options.isFullIDScaleFactor: outfilename = outfilename + "_fullID"
    if options.isMuonRecoToSel: outfilename = outfilename + "_recoToSel"
    if options.isResidualPtCorrScaleFactor: outfilename = outfilename + "_residualPtCorr"
    outfilename += ".root"

    #########################################    
    #########################################    
    if options.isResidualPtCorrScaleFactor:
        if options.inputfile:
            smoothSomeFile(options.inputfile,"plot_dm_diff",outname,outfilename,channel,options.widthPt)  # generic function to smooth stuff
        else:
            print "Error: you should specify an input file using option -i <name>. Exit"
            quit()

        quit()
    #########################################    
    #########################################    
    if options.isWeightedAverage:

        hists = options.histsAverage.split(",")
        f1,f2 = options.filesAverage.split(",")
        w1,w2 = list(float(x) for x in options.weightsAverage.split(","))
        hlist = {}
        for h in hists:
            hScaleFactorAverage = makeSFweightedAverage(f1,f2,w1,w2,str(h),"new_"+str(h),uncertaintyRule=options.averageUncertaintyMode)
            hScaleFactorAverage.SetDirectory(0)
            hlist[str(h)] = hScaleFactorAverage
        tf = ROOT.TFile.Open(outname+outfilename,'recreate')
        for k in hlist:
            hlist[k].Write(k)            
            zaxisName = hlist[k].GetZaxis().GetTitle()
            if options.variable == "ID" and "scaleFactor" in k:
                zaxisName += "::0.98,1.01"
            drawCorrelationPlot(hlist[k],"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),zaxisName,
                                "combinedFull2016_{n}".format(n=k),"ForceTitle",outname,1,1,False,False,False,1,palette=55)
        tf.Close()
        print ""
        print "Created file %s" % (outname+outfilename)
        print ""
        quit()
    #########################################    
    #########################################    

    hmc = 0
    hdata = 0
    hsf = 0
    if options.inputfile:
        tf = ROOT.TFile.Open(options.inputfile)        
        if options.isTriggerScaleFactor or options.isFullIDScaleFactor or options.isMuonRecoToSel:
            hmc =   tf.Get("EGamma_EffMC2D")
            hdata = tf.Get("EGamma_EffData2D")
            hsf = tf.Get("EGamma_SF2D")
            if (hsf == 0):
                print "Error: could not retrieve hsf from input file %s. Exit" % options.inputfile
                quit()
        elif not isEle:            
            hmc   = tf.Get("eff%s_mc_%s" % (options.variable,options.era))
            hdata = tf.Get("eff%s_data_%s" % (options.variable,options.era))            
        else:
            print "Error: you are doing electrons, but you didn't specify option -t for trigger or --fullID for full ID. This setup is currently not implemented. Exit"
            quit()

        if (hmc == 0 or hdata == 0):
            print "Error: could not retrieve hdata or hmc from input file %s. Exit" % options.inputfile
            quit()
        else:
            hmc.SetDirectory(0)
            hdata.SetDirectory(0)
            if isEle or options.isTriggerScaleFactor: hsf.SetDirectory(0)
        tf.Close()
    else:
        print "Error: you should specify an input file using option -i <name>. Exit"
        quit()
        

    etabins = hdata.GetXaxis().GetXbins()
    ptbins = hdata.GetYaxis().GetXbins()
    #etaBinHisto = ROOT.TH1F("etaBinEdges","The x axis of this histogram has the eta binning",len(etabins)-1,array('d',etabins))
        
    # for muons must create original scale factor as well, unless it was trigger (which also have the SF in the input file)
    if isEle or options.isTriggerScaleFactor:
        pass
    else:
        hsf = ROOT.TH2D("hsf","",
                        len(etabins)-1,array('d',etabins),
                        len(ptbins)-1,array('d',ptbins)
                        )
        copyHisto(hsf,hdata)  
        hsf.Divide(hmc)

    hist_ErfParam_vs_eta_data = ROOT.TH2D("hist_ErfParam_vs_eta_data","parameters: [0]*TMath::Erf((x-[1])/[2])",len(etabins)-1,array('d',etabins),3,-0.5,2.5)    
    hist_ErfParam_vs_eta_mc   = ROOT.TH2D("hist_ErfParam_vs_eta_mc"  ,"parameters: [0]*TMath::Erf((x-[1])/[2])",len(etabins)-1,array('d',etabins),3,-0.5,2.5)    
    dummybins = [-0.5, 0.5, 1.5, 2.5]
    Ndummy = len(dummybins) - 1
    hist_ErfCovMatrix_vs_eta_data = ROOT.TH3D("hist_ErfCovMatrix_vs_eta_data","Covariance matrix: eta on X",
                                              len(etabins)-1,array('d',etabins),Ndummy,array('d',dummybins),Ndummy,array('d',dummybins))
    hist_ErfCovMatrix_vs_eta_mc = ROOT.TH3D("hist_ErfCovMatrix_vs_eta_mc","Covariance matrix: eta on X",
                                            len(etabins)-1,array('d',etabins),Ndummy,array('d',dummybins),Ndummy,array('d',dummybins))

    hist_chosenFunc = ROOT.TH1D("chosenFitFunc","Best fit function for each eta bin",5,0,5)
    hist_chosenFunc.GetXaxis().SetBinLabel(1,"tf1_erf")
    hist_chosenFunc.GetXaxis().SetBinLabel(2,"tf1_erf2")
    if isEle or options.isTriggerScaleFactor:        
        hist_chosenFunc.GetXaxis().SetBinLabel(3,"tf1_ln")
    else:
        hist_chosenFunc.GetXaxis().SetBinLabel(3,"tf1_pol1")
    hist_chosenFunc.GetXaxis().SetBinLabel(4,"tf1_pol2")
    hist_chosenFunc.GetXaxis().SetBinLabel(5,"tf1_pol3")

    hist_reducedChi2_data = ROOT.TH1D("reducedChi2_data","Reduced #chi^{2}",20,0,2) # will not have many entries (~100 depending on how many eta bins)
    hist_reducedChi2_data.StatOverflows() # use underflow and overflow to compute mean and RMS
    hist_reducedChi2_MC = ROOT.TH1D("reducedChi2_MC","Reduced #chi^{2}",20,0,2) # will not have many entries (~100 depending on how many eta bins)
    hist_reducedChi2_MC.StatOverflows() # use underflow and overflow to compute mean and RMS

    ######################
    # to make ratio
    ######################
    ratioData =  ROOT.TH2D("dataEfficiencyRatio","Original/smooth Data efficiency ratio",
                           len(etabins)-1,array('d',etabins),
                           len(ptbins)-1,array('d',ptbins)
                           )
    ratioMC =  ROOT.TH2D("mcEfficiencyRatio","Original/smooth MC efficiency ratio",
                           len(etabins)-1,array('d',etabins),
                           len(ptbins)-1,array('d',ptbins)
                           )
    ratioSF =  ROOT.TH2D("scaleFactorRatio","Original/smooth scale factor ratio",
                         len(etabins)-1,array('d',etabins),
                         len(ptbins)-1,array('d',ptbins)
                         )
    copyHisto(ratioData,hdata)
    copyHisto(ratioMC,hmc)
    copyHisto(ratioSF,hsf)

    ######################
    # These histograms will contain the parameters of the function used to smooth the efficiencies
    ######################
    # currently not used anymore

    # hdataSmoothEff = ROOT.TH2D("hdataSmoothEff","Data efficiency: fit parameters --> a_{0} + a_{1}*x + a_{2}*x^{2}",
    #                            len(etabins)-1,array('d',etabins),
    #                            3,0.5,3.5
    #                            )
    # hmcSmoothEff = ROOT.TH2D("hmcSmoothEff","MC efficiency: fit parameters --> a_{0} + a_{1}*x + a_{2}*x^{2}",
    #                          len(etabins)-1,array('d',etabins),
    #                          3,0.5,3.5
    #                          )

    #############
    # these will be used to check the smoothed efficiency
    ###############
    hdataSmoothCheck = ROOT.TH2D("hdataSmoothCheck","Data smoothed efficiency",
                                 len(etabins)-1,array('d',etabins),
                                 int(math.ceil(hdata.GetYaxis().GetBinLowEdge(1+hdata.GetNbinsY()) - hdata.GetYaxis().GetBinLowEdge(1))/options.widthPt), # bins of 0.2 GeV
                                 hdata.GetYaxis().GetBinLowEdge(1),hdata.GetYaxis().GetBinLowEdge(1+hdata.GetNbinsY())
                                 )
    hmcSmoothCheck = ROOT.TH2D("hmcSmoothCheck","MC smoothed efficiency",
                               len(etabins)-1,array('d',etabins),
                               int(math.ceil(hmc.GetYaxis().GetBinLowEdge(1+hmc.GetNbinsY()) - hmc.GetYaxis().GetBinLowEdge(1))/options.widthPt),
                               hmc.GetYaxis().GetBinLowEdge(1),hmc.GetYaxis().GetBinLowEdge(1+hmc.GetNbinsY())
                               )
    hsfSmoothCheck = ROOT.TH2D("hsfSmoothCheck","Data/MC smoothed scale factor",
                               len(etabins)-1,array('d',etabins),
                               int(math.ceil(hdata.GetYaxis().GetBinLowEdge(1+hdata.GetNbinsY()) - hdata.GetYaxis().GetBinLowEdge(1))/options.widthPt),
                               hdata.GetYaxis().GetBinLowEdge(1),hdata.GetYaxis().GetBinLowEdge(1+hdata.GetNbinsY())
                               )
    hdataSmoothCheck_origBinPt = ROOT.TH2D("hdataSmoothCheck_origBinPt","Data smoothed efficiency",
                                           len(etabins)-1,array('d',etabins),
                                           len(ptbins)-1,array('d',ptbins)
                                           )
    hmcSmoothCheck_origBinPt = ROOT.TH2D("hmcSmoothCheck_origBinPt","MC smoothed efficiency",
                                         len(etabins)-1,array('d',etabins),
                                         len(ptbins)-1,array('d',ptbins)
                                         )
    hsfSmoothCheck_origBinPt = ROOT.TH2D("hsfSmoothCheck_origBinPt","Data/MC smoothed scale factor",
                                         len(etabins)-1,array('d',etabins),
                                         len(ptbins)-1,array('d',ptbins)
                                         )

    # hmc and hdata have eta on X and pt on Y
    # we select slices at constant eta and fit along pt with some function
    # let's select an error function 

    hmcpt = {}
    for x in range(1,hmc.GetNbinsX()+1):
        bin = x-1
        hmcpt[bin] = ROOT.TH1D("hmcpt_{b}".format(b=str(bin)),
                               "MC: %.4g <= #eta < %.4g" % (hmc.GetXaxis().GetBinLowEdge(x), hmc.GetXaxis().GetBinLowEdge(x+1)),
                               len(ptbins)-1,array('d',ptbins)
                               )
        for y in range(1,hmc.GetNbinsY()+1):
            hmcpt[bin].SetBinContent(y,hmc.GetBinContent(x,y))         
            #hmcpt[bin].SetBinError(y,hmc.GetBinError(x,y))  # no error on MC, have to assign a random value to fit
            hmcpt[bin].SetBinError(y,hdata.GetBinError(x,y))  # use half the corresponding uncertainty on data (any value which is smaller would do)

    hdatapt = {}
    for x in range(1,hdata.GetNbinsX()+1):
        bin = x-1
        hdatapt[bin] = ROOT.TH1D("hdatapt_{b}".format(b=str(bin)),
                                 "Data: %.4g <= #eta < %.4g" % (hdata.GetXaxis().GetBinLowEdge(x), hdata.GetXaxis().GetBinLowEdge(x+1)),
                                 len(ptbins)-1,array('d',ptbins)
                                 )
        for y in range(1,hdata.GetNbinsY()+1):
            hdatapt[bin].SetBinContent(y,hdata.GetBinContent(x,y))         
            hdatapt[bin].SetBinError(y,hdata.GetBinError(x,y))
            #hdatapt[bin].SetBinError(y,0.01)

    hsfpt = {}
    for x in range(1,hsf.GetNbinsX()+1):
        bin = x-1
        hsfpt[bin] = ROOT.TH1D("hsfpt_{b}".format(b=str(bin)),
                               "Data/MC: %.4g <= #eta < %.4g" % (hsf.GetXaxis().GetBinLowEdge(x), hsf.GetXaxis().GetBinLowEdge(x+1)),
                               len(ptbins)-1,array('d',ptbins)
                               )
        for y in range(1,hsf.GetNbinsY()+1):
            hsfpt[bin].SetBinContent(y,hsf.GetBinContent(x,y))         
            hsfpt[bin].SetBinError(y,hsf.GetBinError(x,y)) 

    ###########################
    # first MC
    ###########################
    bestFit_MC = {}
    for key in hmcpt:

        #fitpol2 = fitTurnOn(hmcpt[key],key,outname, "MC",channel=channel,hist_chosenFunc=hist_chosenFunc,isTrigger=options.isTriggerScaleFactor)
        # for pol2 only
        # for ipar in range(3):
        #     hmcSmoothEff.SetBinContent(key+1,fitpol2.GetParameter(ipar))
        #     hmcSmoothEff.SetBinError(key+1,fitpol2.GetParError(ipar))
        # a0,a1,a2 = fitpol2.GetParameter(0),fitpol2.GetParameter(1),fitpol2.GetParameter(2)
        bestFitFunc = fitTurnOn(hmcpt[key],key,outname, "MC",channel=channel,hist_chosenFunc=hist_chosenFunc, 
                                isIso=True if options.variable=="ISO" else False,
                                isTrigger=options.isTriggerScaleFactor,
                                isFullID=options.isFullIDScaleFactor,
                                isMuonRecoToSel=options.isMuonRecoToSel,
                                fitRange=options.range, hist_reducedChi2=hist_reducedChi2_MC,
                                hist_ErfParam_vs_eta=hist_ErfParam_vs_eta_mc,
                                hist_ErfCovMatrix_vs_eta=hist_ErfCovMatrix_vs_eta_mc)
        bestFit_MC["smoothFunc_MC_ieta%d" % key] = bestFitFunc
        for ipt in range(1,hmcSmoothCheck.GetNbinsY()+1):
            ptval = hmcSmoothCheck.GetYaxis().GetBinCenter(ipt)
            #hmcSmoothCheck.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)
            hmcSmoothCheck.SetBinContent(key+1,ipt, bestFitFunc.Eval(ptval))
        for ipt in range(1,hmcSmoothCheck_origBinPt.GetNbinsY()+1):
            ptval = hmcSmoothCheck_origBinPt.GetYaxis().GetBinCenter(ipt)
            #hmcSmoothCheck_origBinPt.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)
            hmcSmoothCheck_origBinPt.SetBinContent(key+1,ipt, bestFitFunc.Eval(ptval))

    ###########################
    # now data
    ###########################
    bestFit_Data = {}
    for key in hdatapt:

        # fitpol2 = fitTurnOn(hdatapt[key],key,outname,"Data",channel=channel,hist_chosenFunc=hist_chosenFunc)
        # for ipar in range(3):
        #     hdataSmoothEff.SetBinContent(key+1,fitpol2.GetParameter(ipar))
        #     hdataSmoothEff.SetBinError(key+1,fitpol2.GetParError(ipar))
        # a0,a1,a2 = fitpol2.GetParameter(0),fitpol2.GetParameter(1),fitpol2.GetParameter(2)
        # for ipt in range(1,hdataSmoothCheck.GetNbinsY()+1):
        #     ptval = hdataSmoothCheck.GetYaxis().GetBinCenter(ipt)
        #     hdataSmoothCheck.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)
        # for ipt in range(1,hdataSmoothCheck_origBinPt.GetNbinsY()+1):
        #     ptval = hdataSmoothCheck_origBinPt.GetYaxis().GetBinCenter(ipt)
        #     hdataSmoothCheck_origBinPt.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)

        bestFitFunc = fitTurnOn(hdatapt[key],key,outname, "Data",channel=channel,hist_chosenFunc=hist_chosenFunc, 
                                isIso=True if options.variable=="ISO" else False,
                                isTrigger=options.isTriggerScaleFactor,
                                isFullID=options.isFullIDScaleFactor,
                                isMuonRecoToSel=options.isMuonRecoToSel,
                                fitRange=options.range, hist_reducedChi2=hist_reducedChi2_data,
                                hist_ErfParam_vs_eta=hist_ErfParam_vs_eta_data,
                                hist_ErfCovMatrix_vs_eta=hist_ErfCovMatrix_vs_eta_data)
        bestFit_Data["smoothFunc_Data_ieta%d" % key] = bestFitFunc
        for ipt in range(1,hdataSmoothCheck.GetNbinsY()+1):
            ptval = hdataSmoothCheck.GetYaxis().GetBinCenter(ipt)
            #hdataSmoothCheck.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)
            hdataSmoothCheck.SetBinContent(key+1,ipt, bestFitFunc.Eval(ptval))
        for ipt in range(1,hdataSmoothCheck_origBinPt.GetNbinsY()+1):
            ptval = hdataSmoothCheck_origBinPt.GetYaxis().GetBinCenter(ipt)
            #hdataSmoothCheck_origBinPt.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)
            hdataSmoothCheck_origBinPt.SetBinContent(key+1,ipt, bestFitFunc.Eval(ptval))

    ###########################
    # now data/MC
    ###########################
    bestFit_SF = {}
    for key in hsfpt:

        # fitpol2 = fitTurnOn(hsfpt[key],key,outname,"SF",channel=channel,hist_chosenFunc=hist_chosenFunc)
        # for ipar in range(3):
        #     hsfSmoothEff.SetBinContent(key+1,fitpol2.GetParameter(ipar))
        #     hsfSmoothEff.SetBinError(key+1,fitpol2.GetParError(ipar))
        # a0,a1,a2 = fitpol2.GetParameter(0),fitpol2.GetParameter(1),fitpol2.GetParameter(2)
        # for ipt in range(1,hsfSmoothCheck.GetNbinsY()+1):
        #     ptval = hsfSmoothCheck.GetYaxis().GetBinCenter(ipt)
        #     hsfSmoothCheck.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)
        # for ipt in range(1,hsfSmoothCheck_origBinPt.GetNbinsY()+1):
        #     ptval = hsfSmoothCheck_origBinPt.GetYaxis().GetBinCenter(ipt)
        #     hsfSmoothCheck_origBinPt.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)

        # do not fill control histogram when fitting scale factors (these fits are not really used, sf are actually obtained dividing the fitted efficiencies)
        bestFitFunc = fitTurnOn(hsfpt[key],key,outname, "SF",channel=channel,hist_chosenFunc=0, 
                                isIso=True if options.variable=="ISO" else False,
                                isTrigger=options.isTriggerScaleFactor,
                                isFullID=options.isFullIDScaleFactor,
                                isMuonRecoToSel=options.isMuonRecoToSel,
                                fitRange=options.range, hist_reducedChi2=0)
        bestFit_SF["smoothFunc_SF_ieta%d" % key] = bestFitFunc
        for ipt in range(1,hsfSmoothCheck.GetNbinsY()+1):
            ptval = hsfSmoothCheck.GetYaxis().GetBinCenter(ipt)
            #hsfSmoothCheck.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)
            hsfSmoothCheck.SetBinContent(key+1,ipt, bestFitFunc.Eval(ptval))
        for ipt in range(1,hsfSmoothCheck_origBinPt.GetNbinsY()+1):
            ptval = hsfSmoothCheck_origBinPt.GetYaxis().GetBinCenter(ipt)
            #hsfSmoothCheck_origBinPt.SetBinContent(key+1,ipt, a0 + a1 * ptval + a2 * ptval * ptval)
            hsfSmoothCheck_origBinPt.SetBinContent(key+1,ipt, bestFitFunc.Eval(ptval))

    #################################
    # start to make plots
    #################################
    zaxisRange = "0.4,1.1" if isEle else "0.96,1.01"
    zaxisRangeSF = zaxisRange
    if not isEle:
        if options.isTriggerScaleFactor: 
            zaxisRange = "0.70,1.01"
            zaxisRangeSF = "0.84,1.01"
        if options.isMuonRecoToSel:
            zaxisRange = "0.7,1.01"
            zaxisRangeSF = "0.86,1.01"
    else:
        if options.isTriggerScaleFactor: 
            zaxisRangeSF = "0.55,1.05"
        if options.isFullIDScaleFactor:
            zaxisRange = "0.2,0.9"
            zaxisRangeSF = "0.7,1.05"
        

    if options.variable == "ISO":
        zaxisRange = "0.85,1.01"

    canvas = ROOT.TCanvas("canvas","",700,625)

    # for muons, plot also official scale factors
    if not isEle and not options.isTriggerScaleFactor and not options.isMuonRecoToSel:        
        tf = ROOT.TFile.Open("official_muon_ScaleFactors_2016/Run{era}_SF_{var}.root".format(era=options.era,var=options.variable))        
        if options.variable == "ISO":
            hsf_official = tf.Get("NUM_TightRelIso_DEN_MediumID_eta_pt")
        else:
            hsf_official = tf.Get("NUM_MediumID_DEN_genTracks_eta_pt")
        if (hsf_official == 0):
            print "Error: could not retrieve hsf_official from input file %s. Exit" % options.inputfile
            quit()
        hsf_official.SetDirectory(0)
        tf.Close()
        drawCorrelationPlot(hsf_official,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Official data/MC scale factor::%s" % zaxisRangeSF,
                            "input_official_scaleFactor,","",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)

    # plot original histograms

    drawCorrelationPlot(hmc,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"MC efficiency::%s" % zaxisRange,
                        "inputEfficiency_MC","",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hdata,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data efficiency::%s" % zaxisRange,
                        "inputEfficiency_Data","",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hsf,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data/MC scale factor::%s" % zaxisRangeSF,
                        "inputScaleFactor","",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)

    # get a smoothed version of those input histograms
    drawCorrelationPlot(hmc,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"MC efficiency::%s" % zaxisRange,
                        "inputEfficiency_MC_smooth","",outname,1,1,True,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hdata,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data efficiency::%s" % zaxisRange,
                        "inputEfficiency_Data_smooth","",outname,1,1,True,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hsf,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data/MC scale factor::%s" % zaxisRangeSF,
                        "inputScaleFactor_smooth","",outname,1,1,True,False,False,1,palette=55,passCanvas=canvas)


    # now the new ones

    # make a sanity check plot: fill eta-pt with smoothed efficiency
    drawCorrelationPlot(hmcSmoothCheck,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"MC smoothed efficiency::%s" % zaxisRange,
                        "smoothEfficiency_MC","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hdataSmoothCheck,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data smoothed efficiency::%s" % zaxisRange,
                        "smoothEfficiency_Data","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hsfSmoothCheck,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data/MC smoothed scale factor::%s" % zaxisRangeSF,
                        "smoothScaleFactorDirectly","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)

    # scale factor: data/MC
    scaleFactor = ROOT.TH2D("scaleFactor","Scale factor",
                            len(etabins)-1,array('d',etabins),
                            int(math.ceil((hdata.GetYaxis().GetBinLowEdge(1+hdata.GetNbinsY()) - hdata.GetYaxis().GetBinLowEdge(1))/options.widthPt)),
                            hdata.GetYaxis().GetBinLowEdge(1),hdata.GetYaxis().GetBinLowEdge(1+hdata.GetNbinsY())
                            )

    copyHisto(scaleFactor, hdataSmoothCheck)
    scaleFactor.Divide(hmcSmoothCheck)
    scaleFactor.SetMinimum(scaleFactor.GetBinContent(scaleFactor.GetMinimumBin()))
    scaleFactor.SetMaximum(scaleFactor.GetBinContent(scaleFactor.GetMaximumBin()))
    drawCorrelationPlot(scaleFactor,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data/MC scale factor::%s" % zaxisRangeSF,
                        "smoothScaleFactor","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)

    #################################
    # plot also with oiginal binning
    ################################
    
    # divide before drawing the denominator, whose axis settings are modified by drawCorrelationPlot and seems to affect the ratio as well if divided afterwards
    ratioData.Divide(hdataSmoothCheck_origBinPt)
    ratioMC.Divide(hmcSmoothCheck_origBinPt)

    drawCorrelationPlot(hmcSmoothCheck_origBinPt,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"MC smoothed efficiency::%s" % zaxisRange,
                        "smoothEfficiency_MC_origBinPt","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hdataSmoothCheck_origBinPt,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data smoothed efficiency::%s" % zaxisRange,
                        "smoothEfficiency_Data_origBinPt","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hsfSmoothCheck_origBinPt,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data/MC smoothed scale factor::%s" % zaxisRangeSF,
                        "smoothScaleFactorDirectly_origBinPt","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)

    # scale factor: data/MC
    scaleFactor_origBinPt = ROOT.TH2D("scaleFactor_origBinPt","Scale factor",
                                      len(etabins)-1,array('d',etabins),
                                      len(ptbins)-1,array('d',ptbins)
                                      )
    copyHisto(scaleFactor_origBinPt, hdataSmoothCheck_origBinPt)
    scaleFactor_origBinPt.Divide(hmcSmoothCheck_origBinPt)
    scaleFactor_origBinPt.SetMinimum(scaleFactor_origBinPt.GetBinContent(scaleFactor_origBinPt.GetMinimumBin()))
    scaleFactor_origBinPt.SetMaximum(scaleFactor_origBinPt.GetBinContent(scaleFactor_origBinPt.GetMaximumBin()))

    # to make ratio, divide before passing to function, to avoid changes in the histogram
    ratioSF.Divide(scaleFactor_origBinPt)

    #scaleFactor_origBinPt.GetZaxis().SetTitle("Data/MC scale factor")
    drawCorrelationPlot(scaleFactor_origBinPt,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data/MC scale factor::%s" % zaxisRangeSF,
                        "smoothScaleFactor_origBinPt","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)


    ######################
    # finally SF(smooth)/SF(original)
    ######################
    drawCorrelationPlot(ratioData,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"Data efficiency ratio (original/smooth)::0.98,1.02",
                        "dataEfficiencyRatio","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(ratioMC,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"MC efficiency ratio (original/smooth)::0.98,1.02",
                        "mcEfficiencyRatio","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(ratioSF,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),"scale factor ratio (original/smooth)::0.98,1.02",
                        "scaleFactorRatio","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)


    ######################
    # See the difference between smoothing Data and MC efficiency and taking the ratio or smoothing directly the efifciency ratio
    ######################    
    ratioSF_smoothNumDen_smoothRatio = ROOT.TH2D("ratioSF_smoothNumDen_smoothRatio","SF ratio: smooth eff or ratio directly",
                                                 len(etabins)-1,array('d',etabins),
                                                 len(ptbins)-1,array('d',ptbins)
                                                 )

    copyHisto(ratioSF_smoothNumDen_smoothRatio,scaleFactor_origBinPt)
    ratioSF_smoothNumDen_smoothRatio.Divide(hsfSmoothCheck_origBinPt)
    drawCorrelationPlot(ratioSF_smoothNumDen_smoothRatio,"{lep} #eta".format(lep=lepton),"{lep} p_{{T}} [GeV]".format(lep=lepton),
                        "SF ratio: smooth eff or ratio directly::0.98,1.02",
                        "ratioSF_smoothNumDen_smoothRatio","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)

    ##############
    # Erf[x] parameter and error for data and MC efficiency
    drawCorrelationPlot(hist_ErfParam_vs_eta_data,"{lep} #eta".format(lep=lepton),"Erf[x] parameter number",
                        "parameter value",
                        "hist_ErfParam_vs_eta_data","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hist_ErfParam_vs_eta_mc,"{lep} #eta".format(lep=lepton),"Erf[x] parameter number",
                        "parameter value",
                        "hist_ErfParam_vs_eta_mc","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas)
    drawCorrelationPlot(hist_ErfParam_vs_eta_data,"{lep} #eta".format(lep=lepton),"Erf[x] parameter number",
                        "parameter uncertainty",
                        "hist_ErfParamError_vs_eta_data","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas,plotError=True)
    drawCorrelationPlot(hist_ErfParam_vs_eta_mc,"{lep} #eta".format(lep=lepton),"Erf[x] parameter number",
                        "parameter uncertainty",
                        "hist_ErfParamError_vs_eta_mc","ForceTitle",outname,1,1,False,False,False,1,palette=55,passCanvas=canvas,plotError=True)

    
    c = ROOT.TCanvas("c","",700,700)
    c.SetTickx(1)
    c.SetTicky(1)
    c.cd()
    c.SetLeftMargin(0.14)
    c.SetRightMargin(0.06)
    c.cd()
    hist_chosenFunc.Scale(1./hist_chosenFunc.Integral())
    hist_chosenFunc.GetXaxis().SetTitleOffset(1.2)
    hist_chosenFunc.GetXaxis().SetTitleSize(0.05)
    hist_chosenFunc.GetXaxis().SetLabelSize(0.06)
    #hist_chosenFunc.GetXaxis().LabelsOption("v")
    hist_chosenFunc.GetYaxis().SetTitle("Fraction of events")
    hist_chosenFunc.GetYaxis().SetTitleOffset(1.15)
    hist_chosenFunc.GetYaxis().SetTitleSize(0.05)
    hist_chosenFunc.GetYaxis().SetLabelSize(0.04)
    hist_chosenFunc.Draw("HE")
    for ext in ["png","pdf"]:
        c.SaveAs("{out}bestFitFunction_{ch}.{ext}".format(out=outname,ch=channel,ext=ext))

    # now the chi2 histogram
    # put overflow in last bin
    # but get number of entries before (same as integral since we used Fill() without weights)
    entries_MC = hist_reducedChi2_MC.GetEntries()
    entries_data = hist_reducedChi2_data.GetEntries()

    lastBin = hist_reducedChi2_data.GetNbinsX()
    hist_reducedChi2_data.SetBinContent(lastBin, hist_reducedChi2_data.GetBinContent(lastBin) + hist_reducedChi2_data.GetBinContent(1+lastBin) )
    hist_reducedChi2_data.SetBinError(lastBin, math.sqrt( hist_reducedChi2_data.GetBinError(lastBin)*hist_reducedChi2_data.GetBinError(lastBin) 
                                                     + hist_reducedChi2_data.GetBinError(1+lastBin)*hist_reducedChi2_data.GetBinError(1+lastBin) ) 
                                 )
    lastBin = hist_reducedChi2_MC.GetNbinsX()
    hist_reducedChi2_MC.SetBinContent(lastBin, hist_reducedChi2_MC.GetBinContent(lastBin) + hist_reducedChi2_MC.GetBinContent(1+lastBin) )
    hist_reducedChi2_MC.SetBinError(lastBin, math.sqrt( hist_reducedChi2_MC.GetBinError(lastBin)*hist_reducedChi2_MC.GetBinError(lastBin) 
                                                     + hist_reducedChi2_MC.GetBinError(1+lastBin)*hist_reducedChi2_MC.GetBinError(1+lastBin) ) 
                                 )

    tmpmin,tmpmax = getMinMaxHisto(hist_reducedChi2_MC, sumError=True)
    tmpmin1,maxY = getMinMaxHisto(hist_reducedChi2_data, sumError=True)
    maxY = max(tmpmax,maxY)
    maxY = 1.5 * maxY

    hist_reducedChi2_data.GetXaxis().SetTitleOffset(1.2)
    hist_reducedChi2_data.SetLineWidth(2)
    hist_reducedChi2_data.SetLineColor(ROOT.kRed+2)
    hist_reducedChi2_data.SetFillColor(ROOT.kRed+2)
    hist_reducedChi2_data.SetFillStyle(3003)
    hist_reducedChi2_data.GetXaxis().SetTitleSize(0.05)
    hist_reducedChi2_data.GetXaxis().SetLabelSize(0.06)
    hist_reducedChi2_data.GetYaxis().SetTitleOffset(1.15)
    hist_reducedChi2_data.GetYaxis().SetTitleSize(0.05)
    hist_reducedChi2_data.GetYaxis().SetLabelSize(0.04)
    hist_reducedChi2_data.GetYaxis().SetTitle("Events")
    hist_reducedChi2_data.GetYaxis().SetRangeUser(0,maxY)
    hist_reducedChi2_data.GetXaxis().SetTitle("#chi^{2} / NDF")
    hist_reducedChi2_data.Draw("HE")
    lat = ROOT.TLatex()
    line1 = "entries = {0}".format(int(entries_data))
    #line1 = "entries = {integ:.1f}".format(integ=hist_reducedChi2_data.Integral())
    line2 = "mean    = {:.2f}".format(hist_reducedChi2_data.GetMean())
    line3 = "rms     = {:.2f}".format(hist_reducedChi2_data.GetStdDev())
    lat.SetNDC();
    lat.SetTextSize(0.045);
    lat.SetTextFont(42);
    lat.SetTextColor(ROOT.kRed+2);
    xmin = 0.20 
    yhi = 0.85
    lat.DrawLatex(xmin,yhi,"data")
    lat.DrawLatex(xmin,yhi-0.05,line1)
    lat.DrawLatex(xmin,yhi-0.1,line2)
    lat.DrawLatex(xmin,yhi-0.15,line3)

    hist_reducedChi2_MC.SetLineWidth(2)
    hist_reducedChi2_MC.SetLineColor(ROOT.kBlack)
    hist_reducedChi2_MC.SetFillColor(ROOT.kGray)
    #hist_reducedChi2_MC.SetFillStyle(3004)
    hist_reducedChi2_MC.Draw("HE SAME")
    #######################
    # redraw some stuff that might be covered by FillColor
    histCopy = hist_reducedChi2_MC.DrawCopy("HE SAME")
    histCopy.SetFillColor(0)
    histCopy.SetFillStyle(0)
    hist_reducedChi2_data.Draw("HE SAME")
    c.RedrawAxis("sameaxis")
    #################
    line1 = "entries = {0}".format(int(entries_MC))
    #line1 = "entries = {integ:.1f}".format(integ=hist_reducedChi2_MC.Integral())
    line2 = "mean    = {:.2f}".format(hist_reducedChi2_MC.GetMean())
    line3 = "rms     = {:.2f}".format(hist_reducedChi2_MC.GetStdDev())
    lat.SetNDC();
    lat.SetTextSize(0.045);
    lat.SetTextFont(42);
    lat.SetTextColor(ROOT.kBlack);
    xmin = xmin + 0.4
    lat.DrawLatex(xmin,yhi,"MC")
    lat.DrawLatex(xmin,yhi-0.05,line1)
    lat.DrawLatex(xmin,yhi-0.1,line2)
    lat.DrawLatex(xmin,yhi-0.15,line3)

    for ext in ["png","pdf"]:
        c.SaveAs("{out}reducedChi2_{ch}.{ext}".format(out=outname,ch=channel,ext=ext))


    # before saving things, assign an uncertainty from the original input (will need to devise a better way to estimate them)
    # following histograms have same eta-pt binning
    for ix in range(1,hdataSmoothCheck.GetNbinsX()+1):
        for iy in range(1,hdataSmoothCheck.GetNbinsY()+1):
            ieta = hdata.GetXaxis().FindFixBin(hdataSmoothCheck.GetXaxis().GetBinCenter(ix))
            ipt = hdata.GetYaxis().FindFixBin(hdataSmoothCheck.GetYaxis().GetBinCenter(ix))
            hdataSmoothCheck.SetBinError(ix,iy,hdata.GetBinError(ieta,ipt))
            hmcSmoothCheck.SetBinError(ix,iy,hdata.GetBinError(ieta,ipt))
            scaleFactor.SetBinError(ix,iy,hsf.GetBinError(ieta,ipt))

    ###########################
    # Now save things
    ###########################
    tf = ROOT.TFile.Open(outname+outfilename,'recreate')
    # hdataSmoothEff.Write()    
    # hmcSmoothEff.Write()    
    hdataSmoothCheck.Write()
    hmcSmoothCheck.Write()
    scaleFactor.Write()
    hsf.Write("scaleFactorOriginal")
    hdata.Write("efficiencyDataOriginal")
    hmc.Write("efficiencyMCOriginal")
    hist_ErfParam_vs_eta_data.Write("hist_ErfParam_vs_eta_data")
    hist_ErfParam_vs_eta_mc.Write("hist_ErfParam_vs_eta_mc")
    hist_ErfCovMatrix_vs_eta_data.Write("hist_ErfCovMatrix_vs_eta_data")
    hist_ErfCovMatrix_vs_eta_mc.Write("hist_ErfCovMatrix_vs_eta_mc")
    if options.saveTF1:
        for key in bestFit_MC:
            bestFit_MC[key].Write(key)
        for key in bestFit_Data:
            bestFit_Data[key].Write(key)
    tf.Close()
    print ""
    print "Created file %s" % (outname+outfilename)
    print ""

                               
         
