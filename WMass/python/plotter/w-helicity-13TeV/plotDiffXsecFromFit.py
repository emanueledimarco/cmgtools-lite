#!/usr/bin/env python

# python w-helicity-13TeV/plotDiffXsecFromFit.py fitresults_42.root -o plots/diffXsec/fitresults/diffXsec_2018_06_29_group10_absGenEta_moreEtaPtBin/ -c el -C plus -b cards/diffXsec_2018_06_29_group10_absGenEta_moreEtaPtBin/binningPtEta.txt -n
# use -t toys to run of toys

import ROOT, os
from array import array
from make_diff_xsec_cards import getArrayParsingString
from make_diff_xsec_cards import getArrayBinNumberFromValue
from make_diff_xsec_cards import getDiffXsecBinning
from make_diff_xsec_cards import templateBinning
from make_diff_xsec_cards import get_ieta_ipt_from_process_name

from utilities import util
utilities = util()

import sys
#sys.path.append(os.environ['CMSSW_BASE']+"/src/CMGTools/WMass/python/plotter/")
sys.path.append(os.getcwd() + "/plotUtils/")
from utility import *

ROOT.gStyle.SetOptStat(0)
#ROOT.gStyle.SetPadRightMargin(0.13)
ROOT.gROOT.SetBatch()

def getTH1fromTH2(h2D,h2Derr=0,unrollAlongX=True):  # unrollAlongX=True --> select rows, i.e. takes a stripe from x1 to xn at same y, then go to next stripe at next y
    nX = h2D.GetNbinsX()
    nY = h2D.GetNbinsY()
    nbins = nX * nY
    name = h2D.GetName() + "_unrollTo1D" 
    newh = ROOT.TH1D(name,h2D.GetTitle(),nbins,0.5,nbins+0.5)
    if 'TH2' not in h2D.ClassName(): raise RuntimeError, "Calling getTH1fromTH2 on something that is not TH2"
    for i in xrange(nX):
        for j in xrange(nY):
            if unrollAlongX:
                bin = 1 + i + j * nX
            else:
                bin = 1 + j + i * nY
            newh.SetBinContent(bin,h2D.GetBinContent(i+1,j+1))
            if h2Derr: newh.SetBinError(bin,h2Derr.GetBinContent(i+1,j+1))
            else:      newh.SetBinError(bin,h2D.GetBinError(i+1,j+1))
    return newh


if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] fitresults.root")
    parser.add_option('-t', '--type' , dest='type'  , default='hessian' , type='string', help='run the plot from which postfit? toys/scans/hessian')
    parser.add_option('-o','--outdir', dest='outdir', default='.', type='string', help='output directory to save things')
    parser.add_option('-s','--suffix', dest='suffix', default='', type='string', help='Suffix appended to folder name (e.g. hessian_<suffix>)')
    parser.add_option('-c','--channel', dest='channel', default='el', type='string', help='Channel (el, mu)')
    parser.add_option('-C','--charge', dest='charge', default='plus,minus', type='string', help='Charges to consider')
    parser.add_option('-b','--etaPtbinning', dest='etaPtbinning', default='[-2.5,-1.566,-1.4442,0,1.4442,1.566,2.5]*[30,35,40,45]', type='string', help='eta-pt binning for templates (will have to implement reading it from file). Use -b file=<name> to read binning from file <name>')
    parser.add_option('-n','--norm-width', dest='normWidth' , default=False , action='store_true',   help='if given, normalize cross section histograms dividing by bin width')
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_usage()
        quit()

    channel = options.channel
    if channel not in ["el","mu"]:
        print "Error: unknown channel %s (select 'el' or 'mu')" % channel
        quit()
        
    if options.type not in ["toys", "hessian", "scans"]:
        print 'ERROR: none of your types is supported. specify either "toys", "scans", or "hessian"'
        sys.exit()

    # get gen binning from file or directly from option
    binning = getDiffXsecBinning(options.etaPtbinning, "gen")
    #print binning
    etabinning = binning[0]
    ptbinning  = binning[1]

    charges = options.charge.split(',')

    canvas = ROOT.TCanvas("canvas","",800,700)

    for charge in charges:

        outname = options.outdir
        addStringToEnd(outname,"/",notAddIfEndswithMatch=True)
        outname = outname + options.type + ("" if not options.suffix else ("_"+options.suffix)) + "/" + charge + "/"
        createPlotDirAndCopyPhp(outname)

        print ""
        print "==> RUNNING FOR CHARGE ",charge
        chs = '+' if charge == 'plus' else '-' 
        adjustSettings_CMS_lumi()
        
        if options.type == 'toys':
            valuesAndErrors = utilities.getFromToys(args[0])
        elif options.type == 'scans':
            valuesAndErrors = utilities.getFromScans(args[0])
        elif options.type == 'hessian':
            valuesAndErrors = utilities.getFromHessian(args[0])

        #channel check
        channel = 'mu' if any(re.match('.*_mu_group_.*',param) for param in valuesAndErrors.keys()) else 'el'
        print "From the list of parameters it seems that you are plotting results for channel ",channel
        lepton = "electron" if channel == "el" else " muon"

        hmu = ROOT.TH2F("hmu",'signal strenght #mu: W{chs}'.format(chs=chs),len(etabinning)-1, array('d',etabinning), len(ptbinning)-1, array('d',ptbinning))
        hmu_err = ROOT.TH2F("hmu_err",'signal strenght uncertainty: W{chs}'.format(chs=chs),len(etabinning)-1, array('d',etabinning), len(ptbinning)-1, array('d',ptbinning))

        h_pmaskedexpnorm_mu = ROOT.TH2F("h_pmaskedexpnorm_mu",'normalized cross section: W{chs}'.format(chs=chs),
                                        len(etabinning)-1, array('d',etabinning), len(ptbinning)-1, array('d',ptbinning))
        h_pmaskedexpnorm_mu_err = ROOT.TH2F("h_pmaskedexpnorm_mu_err",'norm. cross section unc.: W{chs}'.format(chs=chs),
                                            len(etabinning)-1, array('d',etabinning), len(ptbinning)-1, array('d',ptbinning))

        h_pmaskedexp_mu = ROOT.TH2F("h_pmaskedexp_mu",'cross section: W{chs}'.format(chs=chs),
                                    len(etabinning)-1, array('d',etabinning), len(ptbinning)-1, array('d',ptbinning))
        h_pmaskedexp_mu_err = ROOT.TH2F("h_pmaskedexp_mu_err",'cross section unc.: W{chs}'.format(chs=chs),
                                        len(etabinning)-1, array('d',etabinning), len(ptbinning)-1, array('d',ptbinning))

        for key,val in valuesAndErrors.iteritems():
            if not "W{ch}".format(ch=charge) in key: continue 
            if "outliers" in key: continue
            etabinIndex,ptbinIndex = get_ieta_ipt_from_process_name(key)
            mean = val[0]
            err  = val[1]-mean
            if "pmaskedexpnorm" in key:
                h_pmaskedexpnorm_mu_err.SetBinContent(etabinIndex+1, ptbinIndex+1,err) 
                h_pmaskedexpnorm_mu    .SetBinContent(etabinIndex+1, ptbinIndex+1,mean) 
            elif "pmaskedexp" in key:
                h_pmaskedexp_mu_err.SetBinContent(etabinIndex+1, ptbinIndex+1,err) 
                h_pmaskedexp_mu    .SetBinContent(etabinIndex+1, ptbinIndex+1,mean) 
            else: 
                hmu_err.SetBinContent(etabinIndex+1, ptbinIndex+1,err)
                hmu    .SetBinContent(etabinIndex+1, ptbinIndex+1,mean)

        if options.normWidth:
            h_pmaskedexpnorm_mu_err.Scale(1.,"width")
            h_pmaskedexpnorm_mu.Scale(1.,"width")
            h_pmaskedexp_mu_err.Scale(1.,"width")
            h_pmaskedexp_mu.Scale(1.,"width")

        # infile = ROOT.TFile(args[0], 'read')
        # tree = infile.Get("fitresults")
        # entries = tree.GetEntries()
        # leaves  = tree.GetListOfLeaves()
        # for entry in range(entries):  # actually it is just 1 entry 
        #     tree.GetEntry(entry)
        #     for p in leaves:
        #         name = p.GetName()
        #         if not "W{ch}".format(ch=charge) in name: continue
        #         if any(x in name for x in ["_minos", "_In", "_gen"]): continue
        #         # name should be like Wplus_el_ieta_4_ipt_1_Wplus_el_group_6_mu
        #         etabinIndex,ptbinIndex = get_ieta_ipt_from_process_name(name)
        #         # eta and pt index start from 0, the corresponding histogram bin number is bin+1

        #         print "%s = %f" % (name, p.GetValue())
        #         # could ask whether name.endswith("_mu"), but this would depend on the argument passed to --POIMode in text2tf.py
        #         if "pmaskedexpnorm" in name: 
        #             if name.endswith("_err"): h_pmaskedexpnorm_mu_err.SetBinContent(etabinIndex+1, ptbinIndex+1,p.GetValue())
        #             else:                     h_pmaskedexpnorm_mu    .SetBinContent(etabinIndex+1, ptbinIndex+1,p.GetValue())
        #         elif "pmaskedexp" in name:
        #             if name.endswith("_err"): h_pmaskedexp_mu_err.SetBinContent(etabinIndex+1, ptbinIndex+1,p.GetValue())
        #             else:                     h_pmaskedexp_mu    .SetBinContent(etabinIndex+1, ptbinIndex+1,p.GetValue())
        #         else:
        #             if name.endswith("_err"): hmu_err.SetBinContent(etabinIndex+1, ptbinIndex+1,p.GetValue())
        #             else:                     hmu    .SetBinContent(etabinIndex+1, ptbinIndex+1,p.GetValue())
                
        xaxisTitle = 'gen %s |#eta|' % lepton
        yaxisTitle = 'gen %s p_{T} [GeV]' % lepton
        #zaxisTitle = "#mu::%.3g,%.3g" % (hmu.GetMinimum(), hmu.GetMaximum())

        zaxisTitle = "#mu::0.998,1.002"
        drawCorrelationPlot(hmu, 
                            xaxisTitle, yaxisTitle, zaxisTitle, 
                            hmu.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1,0.14,0.22,passCanvas=canvas)

        #zaxisTitle = "uncertainty on #mu::%.3g,%.3g" % (hmu_err.GetMinimum(), hmu_err.GetMaximum())
        #zaxisTitle = "uncertainty on #mu::0,%.3g" % (hmu_err.GetMaximum())
        zaxisTitle = "uncertainty on #mu::0,0.2"
        drawCorrelationPlot(hmu_err, 
                            xaxisTitle, yaxisTitle, zaxisTitle, 
                            hmu_err.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1,0.14,0.22,passCanvas=canvas)

        zaxisTitle = "d#sigma/d#etadp_{T} / #sigma_{tot} [1/GeV]::%.3g,%.3g" % (h_pmaskedexpnorm_mu.GetMinimum(), h_pmaskedexpnorm_mu.GetMaximum())
        drawCorrelationPlot(h_pmaskedexpnorm_mu, 
                            xaxisTitle, yaxisTitle, zaxisTitle, 
                            h_pmaskedexpnorm_mu.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1,0.14,0.22,passCanvas=canvas)

        zaxisTitle = "uncertainty on d#sigma/d#etadp_{T} / #sigma_{tot} [1/GeV]::%.3g,%.3g" % (h_pmaskedexpnorm_mu_err.GetMinimum(), h_pmaskedexpnorm_mu_err.GetMaximum())
        drawCorrelationPlot(h_pmaskedexpnorm_mu_err, 
                            xaxisTitle, yaxisTitle, zaxisTitle, 
                            h_pmaskedexpnorm_mu_err.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1,0.14,0.22,passCanvas=canvas)

        zaxisTitle = "d#sigma/d#etadp_{T} [pb/GeV]::%.3g,%.3g" % (h_pmaskedexp_mu.GetMinimum(), h_pmaskedexp_mu.GetMaximum())
        #zaxisTitle = "d#sigma/d#etadp_{T} [pb/GeV]::0,5"
        drawCorrelationPlot(h_pmaskedexp_mu, 
                            xaxisTitle, yaxisTitle, zaxisTitle, 
                            h_pmaskedexp_mu.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1,0.14,0.22,passCanvas=canvas)

        #zaxisTitle = "uncertainty on d#sigma/d#etadp_{T} [pb/GeV]::%.3g,%.3g" % (h_pmaskedexp_mu_err.GetMinimum(), h_pmaskedexp_mu_err.GetMaximum())
        zmin,zmax = getZaxisReasonableExtremesTH2(h_pmaskedexp_mu_err,maxZtoUse=10)
        #zaxisTitle = "uncertainty on d#sigma/d#etadp_{T} [pb/GeV]::%.3g,%.3g" % (zmin,zmax) 
        zaxisTitle = "uncertainty on d#sigma/d#etadp_{T} [pb/GeV]::0,10"
        drawCorrelationPlot(h_pmaskedexp_mu_err, 
                            xaxisTitle, yaxisTitle, zaxisTitle, 
                            h_pmaskedexp_mu_err.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1,0.14,0.22,passCanvas=canvas)

        h_pmaskedexp_mu_relErr = h_pmaskedexp_mu_err.Clone("h_pmaskedexp_mu_relErr")
        h_pmaskedexp_mu_relErr.Divide(h_pmaskedexp_mu)
        h_pmaskedexp_mu_relErr.SetTitle('W{chs}'.format(chs=chs))

        #zaxisTitle = "relative uncertainty on d#sigma/d#etadp_{T}::%.3g,%.3g" % (h_pmaskedexp_mu_relErr.GetMinimum(), h_pmaskedexp_mu_relErr.GetMaximum())
        zaxisTitle = "relative uncertainty on d#sigma/d#etadp_{T}::0.025,0.3" #% (h_pmaskedexp_mu_relErr.GetMinimum(), h_pmaskedexp_mu_relErr.GetMaximum())
        drawCorrelationPlot(h_pmaskedexp_mu_relErr, 
                            xaxisTitle, yaxisTitle, zaxisTitle, 
                            h_pmaskedexp_mu_relErr.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1,0.14,0.22,passCanvas=canvas)

        h_pmaskedexpnorm_mu_relErr = h_pmaskedexpnorm_mu_err.Clone("h_pmaskedexpnorm_mu_relErr")
        h_pmaskedexpnorm_mu_relErr.Divide(h_pmaskedexpnorm_mu)
        h_pmaskedexpnorm_mu_relErr.SetTitle('W{chs}'.format(chs=chs))

        zaxisTitle = "relative uncertainty on d#sigma/d#etadp_{T} / #sigma_{tot}::0.000,0.05" 
        zmin,zmax = getZaxisReasonableExtremesTH2(h_pmaskedexpnorm_mu_err,maxZtoUse=1)
        #zaxisTitle = "relative uncertainty on d#sigma/d#etadp_{T} / #sigma_{tot}::%.3g,%.3g"  % (zmin,zmax) 
        #zaxisTitle = "relative uncertainty on d#sigma/d#etadp_{T} / #sigma_{tot}::%.3g,%.3g" % (h_pmaskedexpnorm_mu_relErr.GetMinimum(), h_pmaskedexpnorm_mu_relErr.GetMaximum())
        drawCorrelationPlot(h_pmaskedexpnorm_mu_relErr, 
                            xaxisTitle, yaxisTitle, zaxisTitle, 
                            h_pmaskedexpnorm_mu_relErr.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1,0.14,0.22,passCanvas=canvas)

        # now drawing a TH1 unrolling TH2
        unrollAlongEta = False
        xaxisTitle = "template global bin"
        if unrollAlongEta:
            xaxisTitle = xaxisTitle + " = 1 + ieta + ipt * %d; ipt in [%d,%d], ieta in [%d,%d]" % (len(etabinning)-2,0,len(ptbinning)-2,0,len(etabinning)-2)
        else:
            xaxisTitle = xaxisTitle + " = 1 + ipt + ieta * %d; ipt in [%d,%d], ieta in [%d,%d]" % (len(ptbinning)-2,0,len(ptbinning)-2,0,len(etabinning)-2)
        h1D_pmaskedexp = getTH1fromTH2(h_pmaskedexp_mu, h_pmaskedexp_mu_err, unrollAlongX=unrollAlongEta)        
        drawSingleTH1(h1D_pmaskedexp,xaxisTitle,"d#sigma/d#etadp_{T} [pb/GeV]","unrolledXsec_pmaskedexp_{ch}_{fl}".format(ch= charge,fl=channel),
                      outname,labelRatioTmp="Rel.Unc.::0.9,1.1",draw_both0_noLog1_onlyLog2=1,canvasSize="3000,2000")

        h1D_pmaskedexp_norm = getTH1fromTH2(h_pmaskedexpnorm_mu, h_pmaskedexpnorm_mu_err, unrollAlongX=unrollAlongEta)        
        drawSingleTH1(h1D_pmaskedexp_norm,xaxisTitle,"d#sigma/d#etadp_{T} / #sigma_{tot} [1/GeV]","unrolledXsec_pmaskedexpnorm_{ch}_{fl}".format(ch= charge,fl=channel),
                      outname,labelRatioTmp="Rel.Unc.::0.9,1.1",draw_both0_noLog1_onlyLog2=1,canvasSize="3000,2000")


        #infile.Close()
