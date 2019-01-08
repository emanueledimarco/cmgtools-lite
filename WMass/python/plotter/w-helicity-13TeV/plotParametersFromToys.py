#!/usr/bin/env python

## USAGE
## python plotParametersFromToys.py toys_wminus.root --pdir plots -c minus -f el [--param-family signalStrength -a diffXsec]
## use option ' -a diffXsec ' for differential cross section analysis
## It is better to use  option --param-family to specify a class of POIS, it is almost equivalent to  --parameters.

import ROOT, os, re, datetime
from sys import argv, stdout, stderr, exit
ROOT.gROOT.SetBatch(True)

import utilities
utilities = utilities.util()

# import few functions from plotUtils/utility.h
from sys import path as syspath
syspath.append(os.getcwd() + "/plotUtils/")
from utility import addStringToEnd,createPlotDirAndCopyPhp

from make_diff_xsec_cards import get_ieta_ipt_from_process_name


lat = ROOT.TLatex(); lat.SetNDC()

def plotPars(inputFile, pois=None, selectString='', maxPullsPerPlot=30, plotdir='./', suffix='', analysis='helicity', 
             excludeName=None, paramFamily=None,plotPull=False,
             channel='el', charge='plus',
             selection=""):
 
    

    chs = "+" if charge == "plus" else "-"

    isSignalStrength = False
        
    if paramFamily:
        if paramFamily == "pdf":
            pois="pdf.*"
            all_valuesAndErrors = utilities.getHistosFromToys(inputFile,getPull=plotPull,matchBranch=pois,excludeBranch=excludeName,selection=selection)
        elif paramFamily == "scale":
            pois="muR,muF,muRmuF,alphaS,wptSlope" 
            if channel == "el":
                pois += ",CMS_We_sig_lepeff,CMS_We_elescale,CMS_We_FRe_slope,CMS_We_FRe_continuous"
            else:
                pois += ",CMS_Wmu_sig_lepeff,CMS_Wmu_muscale,CMS_Wmu_FRmu_slope,CMS_Wmu_FR_continuous"
            all_valuesAndErrors = utilities.getHistosFromToys(inputFile,getPull=plotPull,matchBranch=pois,excludeBranch=excludeName,selection=selection)
        elif paramFamily == "signalStrength":
            pois="W{ch}.*_mu".format(ch=charge)
            isSignalStrength = True
            all_valuesAndErrors = utilities.getHistosFromToys(inputFile,200,0,2,getPull=plotPull,matchBranch=pois,excludeBranch=excludeName,selection=selection)
        elif paramFamily == "absxsec":
            pois="W{ch}.*_pmaskedexp".format(ch=charge)
            all_valuesAndErrors = utilities.getHistosFromToys(inputFile,1000,0,200,getPull=plotPull,matchBranch=pois,excludeBranch=excludeName,selection=selection)
    else:
        # warning: utilities.getHistosFromToys is working only for parameters centered around 0 (histogram is defined in -3,3)
        # this script will not work if using parameters with pmaskedexp
        if pois:
            if any (["pmaskedexp" in x for x in pois.split(",")]):
                print "Warning: current setup cannot work with parameters matching pmaskedexp: they are expected to be centered around 0. Exit"
                print "You might want to change behaviour of function utilities.getHistosFromToys to use those parameters as well" 
                exit(0)
        if any ([wc in poi for wc in ["Wplus","Wminus"] for poi in pois.split(",")]):
            all_valuesAndErrors = utilities.getHistosFromToys(inputFile,200,0,2,getPull=plotPull,matchBranch=pois,excludeBranch=excludeName,selection=selection)
            if not any("pmaskedexp" in poi for poi in pois.split(",")):
                isSignalStrength = True
        else:
            all_valuesAndErrors = utilities.getHistosFromToys(inputFile,getPull=plotPull,matchBranch=pois,excludeBranch=excludeName,selection=selection)
            

    print "From the list of parameters it seems that you are plotting results for channel ",channel
    print "pois = ", pois

    valuesAndErrors = {}

    excludedNames = excludeName.split(',') if excludeName else []

    if pois:
        poi_patts = pois.split(",")
        for ppatt in poi_patts:            
            for (k,v) in all_valuesAndErrors.iteritems():
                if any([re.match(x,k) for x in excludedNames]): continue
                if re.match(ppatt,k) and k not in valuesAndErrors: valuesAndErrors[k] = v
            #print valuesAndErrors.keys()

    params = valuesAndErrors.keys()
    print "----------------------------------"
    print "List of parameters:"
    print params
    print "----------------------------------"

    if any(re.match('pdf.*',x) for x in params):
        params = sorted(params, key = lambda x: int(x.split('pdf')[-1]), reverse=False)

    nPulls = 0
    pullLabelSize = 0.028
    pullSummaryMap = {}

    c = ROOT.TCanvas("c","",960,800)
    c.SetTickx(1)
    c.SetTicky(1)
    c.cd()
    c.SetLeftMargin(0.14)
    c.SetRightMargin(0.06)
    c.cd()

    if isSignalStrength:
        chi2title = "#chi^{2} for signal strength parameters"
        chi2distr = ROOT.TH1D("chi2distr",chi2title,20,0.0,2.0)

    for name in params:

        print "Making pull for parameter ",name
        # look in utilities.py for getHistosFromToys(: if plotting pull, the histogram is defined as (x-x_gen)x_err,
        # while valuesAndErrors[name][0] and valuesAndErrors[name][1] are defined as mean and rms of original histogram from x
        # if option getPull of getHistosFromToys is False, then there is no difference
        mean_p, sigma_p = (valuesAndErrors[name][0],valuesAndErrors[name][1]-valuesAndErrors[name][0])
        #mean_p, sigma_p = (valuesAndErrors[name][3].GetMean(),valuesAndErrors[name][3].GetStdDev())

        histo = valuesAndErrors[name][3]
        if isSignalStrength and histo.GetStdDev() > 0.05:
            histo.Rebin(2)
        histo.Draw()
        histo.GetXaxis().SetTitle(histo.GetTitle());        histo.GetYaxis().SetTitle("no toys (%d total)" % histo.Integral());         histo.SetTitle("")
        histo.GetYaxis().SetTitleOffset(1.05);     histo.GetXaxis().SetTitleOffset(0.9);        histo.GetYaxis().SetTitleSize(0.05);        histo.GetXaxis().SetTitleSize(0.05);        histo.GetXaxis().SetTitle(name)
     
        fitPull = histo.Integral()>0
        if fitPull:
            histo.Fit("gaus","Q")
            fit = histo.GetFunction("gaus")
            fit.SetLineColor(4)
            lat.DrawLatex(0.16, 0.8, 'mean:     {me:.3f}'.format(me=fit.GetParameter(1)))
            lat.DrawLatex(0.16, 0.7, 'err :     {er:.2f}'.format(er=fit.GetParameter(2)))
            lat.DrawLatex(0.16, 0.6, 'chi2/ndf: {cn:.2f}'.format(cn=fit.GetChisquare()/fit.GetNDF() if fit.GetNDF()>0 else 999))
            lat.DrawLatex(0.65, 0.8, 'mean:  {me:.3f}'.format(me=histo.GetMean()))
            lat.DrawLatex(0.65, 0.7, 'RMS :  {er:.2f}'.format(er=histo.GetStdDev()))

            if isSignalStrength:
                if fit.GetParameter(2) < 0.05:
                    histo.GetXaxis().SetRangeUser(0.8,1.2)        
                if fit.GetNDF()>0:
                    chi2distr.Fill(fit.GetChisquare()/fit.GetNDF()) 

        os.system('cp /afs/cern.ch/user/g/gpetrucc/php/index.php '+plotdir)
        distrdir = plotdir+'/pulldistr'
        createPlotDirAndCopyPhp(distrdir)
        for ext in ['png', 'pdf']:
            c.SaveAs("{pdir}/{name}_postfit_{ch}_{channel}{suffix}.{ext}".format(pdir=distrdir,name=name,ch=charge,suffix="_"+suffix,channel=channel,ext=ext))

        if fitPull:
            # tlatex = ROOT.TLatex(); tlatex.SetNDC(); 
            # tlatex.SetTextSize(0.11)
            # tlatex.SetTextColor(4);
            # tlatex.DrawLatex(0.65,0.80,"Mean    : %.3f #pm %.3f" % (histo.GetFunction("gaus").GetParameter(1),histo.GetFunction("gaus").GetParError(1)))
            # tlatex.DrawLatex(0.65,0.66,"Sigma   : %.3f #pm %.3f" % (histo.GetFunction("gaus").GetParameter(2),histo.GetFunction("gaus").GetParError(2)))
            
            # tlatex.SetTextSize(0.11);
            # tlatex.SetTextColor(1);
            # tlatex.DrawLatex(0.65,0.33,"Post-fit #pm #sigma_{#theta}: %.3f #pm %.3f" % (mean_P p), sigma_p))

            pullSummaryMap[name]=(histo.GetFunction("gaus").GetParameter(1),histo.GetFunction("gaus").GetParameter(2),
                                  histo.GetMean(),utilities.effSigma(histo))
            nPulls += 1
            
    if nPulls>0:
        
        if isSignalStrength:
            canvas_Chi2 = ROOT.TCanvas("canvas_Chi2","",700,700)
            canvas_Chi2.SetTickx(1)
            canvas_Chi2.SetTicky(1)
            chi2distr.Draw("Hist")
            chi2distr.GetXaxis().SetTitle("#chi^{2}")
            chi2distr.GetXaxis().SetTitleOffset(0.9)        
            chi2distr.GetXaxis().SetTitleSize(0.05)    
            chi2distr.GetYaxis().SetTitle("Events")
            chi2distr.GetYaxis().SetTitleOffset(1.05)     
            chi2distr.GetYaxis().SetTitleSize(0.05)       
            if chi2distr.GetEntries():
                overflow = 100. * chi2distr.GetBinContent(chi2distr.GetNbinsX() + 1) / chi2distr.GetEntries()  # use as XX %, multiplying by 100
            else:
                overflow = 0
            lat.DrawLatex(0.12, 0.8, 'W{ch} #rightarrow {lep}#nu'.format(ch=chs,lep="e" if channel == "el" else "#mu"))
            lat.DrawLatex(0.12, 0.7, 'mean:  {me:.3f}'.format(me=chi2distr.GetMean()))
            lat.DrawLatex(0.12, 0.6, 'RMS :  {er:.2f}'.format(er=chi2distr.GetStdDev()))
            lat.DrawLatex(0.12, 0.5, 'Overflow :  {of:.1f}%'.format(of=overflow))
            # following does not work, the stat box is disabled
            # chi2distr.SetStats(1)
            # canvas_Chi2.Update()
            # statBox = chi2distr.FindObject("stats")
            # if statBox:
            #     statBox.SetX1NDC(0.62)
            #     statBox.SetX2NDC(0.92)
            #     statBox.SetY1NDC(0.59)
            #     statBox.SetY2NDC(0.91)
            #     statBox.SetFillColor(0)
            #     statBox.SetFillStyle(0)
            #     statBox.SetBorderSize(0)
            #     statBox.Draw()
            # else:
            #     print "Warning: no stat box found for Chi^2" 
            for ext in ['png', 'pdf']:
                canvas_Chi2.SaveAs("{pdir}/chi2_{ch}_{channel}{suffix}.{ext}".format(pdir=distrdir,ch=charge,suffix="_"+suffix,channel=channel,ext=ext))
        

        print "Generating Pull Summaries...\n"
        nRemainingPulls = nPulls
        hc = ROOT.TCanvas("hc","",3000,2000); hc.SetGrid(0);
        pullPlots = 1;
        while nRemainingPulls > 0:
            nThisPulls = min(maxPullsPerPlot,nRemainingPulls)

            pull_rms      = ROOT.TH1F("pull_rms_{pp}".format(pp=str(pullPlots)) ,"", 3*nThisPulls+1,0,nThisPulls*3+1);
            pull_effsigma = ROOT.TH1F("pull_effsigma_{pp}".format(pp=str(pullPlots)) ,"", 3*nThisPulls+1,0,nThisPulls*3+1);
            pi=1
            sortedpulls = []
            if 'pdf' in pois:
                sortedpulls = sorted(pullSummaryMap.keys(), key=lambda k: int(k.split('pdf')[-1]))
            # following condition should not happen (parameter is not centered around 0)
            #elif 'masked' in pois:
            #elif any([x in pois for x in ["Wplus","Wminus"]]) and not "masked" in pois:
            elif isSignalStrength or paramFamily == "absxsec":
                keys = pullSummaryMap.keys()
                if analysis == "helicity":
                    keys_l = list(k for k in keys if 'left' in k)
                    keys_r = list(k for k in keys if 'right' in k)
                    norms_l = sorted(keys_l, key=lambda k: int(k.split('_')[-1]), reverse=False)
                    norms_r = sorted(keys_r, key=lambda k: int(k.split('_')[-1]), reverse=True)
                    sortedpulls = norms_r + norms_l
                else:
                    # differential xsection: get ieta, ipt index and use them as keys to sort
                    tmpkeys = [x for x in keys if "outliers" not in x]
                    sortedpulls = sorted(tmpkeys, key = lambda x: get_ieta_ipt_from_process_name(x))
                    for x in keys:
                        if "outliers" in x: sortedpulls.append(x) 
            else:
                sortedpulls = sorted(pullSummaryMap.keys(), key=lambda k: k[0])  # alphabetic order
            if len(sortedpulls)==0: break

            maxErr = 0;
            for name in sortedpulls:
                if pi>nThisPulls: break
                pull = pullSummaryMap[name]
                pull_rms     .SetBinContent(3*pi+0,pull[0]);  pull_rms     .SetBinError(3*pi+0,pull[1])
                pull_effsigma.SetBinContent(3*pi+1,pull[2]);  pull_effsigma.SetBinError(3*pi+1,pull[3])

                newname = name
                if isSignalStrength:
                    newname = "_".join(name.split("_")[:6])
                elif paramFamily == "absxsec":
                    newname = "_".join(name.split("_")[:6]) + "_xsec"
                pull_rms.GetXaxis().SetBinLabel(3*pi,newname)
                pull_rms.GetXaxis().SetTickSize(0.)
                
                max2=max(pull[1],pull[3])
                if max2>maxErr: maxErr=max2
                del pullSummaryMap[name]
                pi += 1
                nRemainingPulls -= 1

            #pull_rms .SetMarkerColor(46); pull_rms .SetLineColor(45); pull_rms .SetLineWidth(2); pull_rms .SetMarkerSize(1.0); pull_rms .SetMarkerStyle(21); 
            #pull_effsigma .SetMarkerColor(21); pull_effsigma .SetLineColor(24); pull_effsigma .SetLineWidth(2); pull_effsigma .SetMarkerSize(1.0); pull_effsigma .SetMarkerStyle(22)

            NmaxChar = 1
            for name in sortedpulls:
                NmaxChar = max(NmaxChar,len(name))
            if NmaxChar >= 8:
                hc.SetBottomMargin(0.2)  # hardcoded and not optimized I just looked at a random pull plot with the CMS_We_elescale and QCD scales parameters            

            pull_rms .SetMarkerColor(ROOT.kRed+2); 
            pull_rms .SetLineColor(ROOT.kRed); pull_rms .SetLineWidth(3); 
            pull_rms .SetMarkerSize(1.0);      pull_rms .SetMarkerStyle(21); 

            pull_effsigma .SetMarkerColor(ROOT.kBlack); 
            pull_effsigma .SetLineColor(ROOT.kGray+2);   pull_effsigma .SetLineWidth(3); 
            pull_effsigma .SetMarkerSize(1.0);           pull_effsigma .SetMarkerStyle(22)

            pull_rms.SetLabelSize(pullLabelSize)
            pull_rms.LabelsOption("v")
            yrange = 3. 
            if isSignalStrength and not plotPull:
                pull_rms.GetYaxis().SetRangeUser(0.9,1.1)
            else:
               pull_rms.GetYaxis().SetRangeUser(-yrange,yrange)
            if plotPull:
                pull_rms.GetYaxis().SetTitle("pull summary (n#sigma)")
            else:
                pull_rms.GetYaxis().SetTitle("POI summary")
            pull_rms.Draw("p")
            pull_effsigma.Draw("p same")

            line0 = ROOT.TLine(pull_rms.GetXaxis().GetXmin(), 0., pull_rms.GetXaxis().GetXmax(), 0.); line0.SetLineStyle(7)
            line0.Draw('same')

            leg = ROOT.TLegend(0.60, 0.70, 0.85, 0.90)
            leg.SetFillStyle(0)
            leg.SetBorderSize(0)
            leg.AddEntry(pull_rms,"Gaussian #sigma")
            leg.AddEntry(pull_effsigma,"Effective #sigma")
            leg.Draw("same")
            param_group=pois.replace('.*','').replace(',','_')
            for ext in ['png', 'pdf']:
                hc.SaveAs("{pdir}/pullSummaryToys_{params}_{igroup}_{ch}_{c}.{ext}".format(pdir=plotdir,ch=charge,suffix="_"+suffix,params=param_group,igroup=pullPlots,c=channel,ext=ext))
            pullPlots += 1


if __name__ == "__main__":

    ROOT.gROOT.SetBatch()
    ROOT.gStyle.SetOptStat(0)

    date = datetime.date.today().isoformat()

    from optparse import OptionParser
    parser = OptionParser(usage='%prog toys.root [options] ')
    parser.add_option(      '--parameters'  , dest='pois'     , default='pdf.*', type='string', help='comma separated list of regexp parameters to run. default is all parameters! Better to select parameters belonging to the same family, like, pdfs, qcd scales, signal strengths ...')
    parser.add_option(      '--param-family'  , dest='poisFamily'     , default=None, type='string', help='Parameter family: pdf, scale, signalStrength, absxsec')
    parser.add_option(      '--exclude-param'  , dest='excludeParam'     , default=None, type='string', help='Work as --parameters, but matches will be excluded from the list of parameters (e.g., can exclude a given pdf, pmaskednorm to match only pmasked and so on)')
    parser.add_option('-c', '--charge'      , dest='charge'  , default=''      , type='string', help='Specify charge (plus,minus)')
    parser.add_option('-f', '--flavour'     , dest='flavour'  , default=''      , type='string', help='Specify flavour (el,mu)')
    parser.add_option(      '--pdir'        , dest='plotdir'  , default='./'   , type='string', help='directory to save the likelihood scans')
    parser.add_option(      '--suffix'      , dest='suffix'   , default=''     , type='string', help='suffix to give to the plot files')
    parser.add_option('-a', '--analysis'    , dest='analysis' , default='helicity', type='string', help='Which analysis: helicity or diffXsec') 
    parser.add_option(      '--pull'    , dest="plotpull", action="store_true", default=False, help="When making the pull plot, get really the pull from histogram (define histogram using (x-x_gen)/x_err for parameter x");
    parser.add_option('-s',  '--selection'  , dest="selection", default="", help="Selection to apply when reading trees to make pull distributions");
    (options, args) = parser.parse_args()

    if len(args)<1: 
        print "need toyfile as argument. Exit."
        exit(0)

    if options.analysis not in ["helicity", "diffXsec"]:
        print "Warning: analysis not recognized, must be either \"helicity\" or \"diffXsec\""
        exit(0)

    if not options.flavour:
        print "Warning: you must specify lepton flavour. Use -f el|mu. Exit"
        exit(0)
    if not options.charge:
        print "Warning: you must specify lepton charge. Use -c plus|minus. Exit"
        exit(0)
        
    allowedPOIfamily = ["pdf", "scale", "signalStrength", "absxsec"]
    if options.poisFamily and not (options.poisFamily in allowedPOIfamily):
        print "Warning: POI family not recognized, must be one of %s" % ",".join(allowedPOIfamily)
        exit(0)



    outname = options.plotdir
    addStringToEnd(outname,"/",notAddIfEndswithMatch=True)
    outname = outname + options.charge + "/"
    createPlotDirAndCopyPhp(outname)

    toyfile = args[0]
    plotPars(toyfile,pois=options.pois,maxPullsPerPlot=30,plotdir=outname,suffix=options.suffix,analysis=options.analysis,
             excludeName=options.excludeParam,paramFamily=options.poisFamily,plotPull=options.plotpull,channel=options.flavour,charge=options.charge,
             selection=options.selection)

