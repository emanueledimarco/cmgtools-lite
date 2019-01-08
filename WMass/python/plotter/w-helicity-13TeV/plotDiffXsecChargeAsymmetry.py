#!/bin/env python

# python w-helicity-13TeV/plotDiffXsecChargeAsymmetry.py -i cards/diffXsec_mu_2018_07_11_group10_coarseBin/ -o plots/diffXsec/chargeAsymmetry/muon/ -c mu -t toys/diffXsec_mu_2018_07_11_group10_coarseBin/toys_comb_WchargeAsymmetry.root -n

import ROOT, os, sys, re, array, math

from make_diff_xsec_cards import getDiffXsecBinning
from make_diff_xsec_cards import templateBinning

sys.path.append(os.getcwd() + "/plotUtils/")
from utility import *

ROOT.gROOT.SetBatch(True)

import utilities
utilities = utilities.util()


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
    parser = OptionParser(usage='%prog [options]')
    parser.add_option('-i','--input', dest='inputdir', default='', type='string', help='input directory with all the cards inside. It is used to get other information')
    parser.add_option('-o','--outdir', dest='outdir', default='', type='string', help='output directory to save things')
    parser.add_option('-t','--toyfile', dest='toyfile', default='.', type='string', help='Root file with toys.')
    parser.add_option('-c','--channel', dest='channel', default='', type='string', help='name of the channel (mu or el)')
    parser.add_option('-f','--friend', dest='friend', default='', type='string', help='Root file with friend tree containing total xsec (it does not include the outliers). Tree name is assumed to be "toyFriend"')
    parser.add_option('-n','--norm-width', dest='normWidth' , default=False , action='store_true',   help='Normalize cross section histograms dividing by bin width')
    parser.add_option(     '--hessian', dest='hessian' , default=False , action='store_true',   help='The file passed with -t is interpreted as hessian: will provide the central value of charge asymmetry but not the uncertainty, and will not plot the differential cross section')
    (options, args) = parser.parse_args()

    ROOT.TH1.SetDefaultSumw2()
    
    channel = options.channel
    if channel not in ["el","mu"]:
        print "Error: unknown channel %s (select 'el' or 'mu')" % channel
        quit()

    if options.outdir:
        outname = options.outdir
        addStringToEnd(outname,"/",notAddIfEndswithMatch=True)
        if options.hessian: outname = outname + "/hessian/"
        else              : outname = outname + "/toys/"
        createPlotDirAndCopyPhp(outname)
    else:
        print "Error: you should specify an output folder using option -o <name>. Exit"
        quit()

    if not options.toyfile:
        print "Error: you should specify a file containing the toys using option -t <name>. Exit"
        quit()


    if options.inputdir:
        if not options.inputdir.endswith("/"): options.inputdir += "/"
        basedir = os.path.basename(os.path.normpath(options.inputdir))
        binfile = options.inputdir + "binningPtEta.txt"
        if "_group" in basedir:
            tokens = basedir.split("_")
            for x in tokens:
                if "group" in x:
                    #ngroup = int("".join(str(s) for s in x if s.isdigit()))
                    ngroup = int(x.split("group")[1])
        else:
            ngroup = 1 
    else:
        print "Error: you should specify an input folder containing all the cards using option -i <name>. Exit"
        quit()

    etaPtBinningVec = getDiffXsecBinning(binfile, "gen")
    genBins  = templateBinning(etaPtBinningVec[0],etaPtBinningVec[1])
    netabins = genBins.Neta
    nptbins  = genBins.Npt

    lepton = "electron" if channel == "el" else "muon"
    Wchannel = "W #rightarrow %s#nu" % ("e" if channel == "el" else "#mu")

    hChAsymm = ROOT.TH2F("hChAsymm_{lep}".format(lep=lepton),"Charge asymmetry: {Wch}".format(Wch=Wchannel),
                         genBins.Neta, array('d',genBins.etaBins), genBins.Npt, array('d',genBins.ptBins))
    hChAsymmErr = ROOT.TH2F("hChAsymmErr_{lep}".format(lep=lepton),"Charge asymmetry uncertainty: {Wch}".format(Wch=Wchannel),
                            genBins.Neta, array('d',genBins.etaBins), genBins.Npt, array('d',genBins.ptBins))
    

    nbins = genBins.Neta * genBins.Npt
    binCount = 1        
    print "Now filling histograms with charge asymmetry"

    f = ROOT.TFile(options.toyfile, 'read')
    tree = f.Get('fitresults')
    if options.friend != "":
        tree.AddFriend('toyFriend',options.friend)

    for ieta in range(1,genBins.Neta+1):
        for ipt in range(1,genBins.Npt+1):
            #print "\rBin {num}/{tot}".format(num=binCount,tot=nbins),
            sys.stdout.write('Bin {num}/{tot}   \r'.format(num=binCount,tot=nbins))
            sys.stdout.flush()
            binCount += 1

            if options.hessian: 
                central = utilities.getDiffXsecAsymmetryFromHessian(channel,ieta-1,ipt-1,genBins.Neta,ngroup,options.toyfile)
            else:                
                central,up,down = utilities.getDiffXsecAsymmetryFromToysFast(channel,ieta-1,ipt-1,genBins.Neta,ngroup,
                                                                             nHistBins=2000, minHist=0., maxHist=1.0, tree=tree)
                #central,up,down = utilities.getDiffXsecAsymmetryFromToys(channel,ieta-1,ipt-1,genBins.Neta,ngroup,options.toyfile)
                error = up - central
                hChAsymm.SetBinError(ieta,ipt,error)         
                hChAsymmErr.SetBinContent(ieta,ipt,error)
            hChAsymm.SetBinContent(ieta,ipt,central)        
            


    setTDRStyle()

    canvas = ROOT.TCanvas("canvas","",800,700)

    xaxisTitle = 'gen %s |#eta|' % lepton
    yaxisTitle = 'gen %s p_{T} [GeV]' % lepton
    #zaxisTitle = "Asymmetry::%.3f,%.3f" % (hChAsymm.GetMinimum(),hChAsymm.GetMaximum())
    zaxisTitle = "Asymmetry::0.05,0.35"
    if channel == "el": zaxisTitle = "Asymmetry::0.05,0.35"
    drawCorrelationPlot(hChAsymm,
                        xaxisTitle, yaxisTitle, zaxisTitle,
                        hChAsymm.GetName(),
                        "ForceTitle",outname,1,1,False,False,False,1, canvasSize="700,625",leftMargin=0.14,rightMargin=0.22,passCanvas=canvas)

    if not options.hessian:

        zaxisTitle = "Asymmetry uncertainty::%.3f,%.3f" % (max(0,0.99*hChAsymmErr.GetMinimum()),min(0.10,1.01*hChAsymmErr.GetMaximum()))
        #zaxisTitle = "Asymmetry uncertainty::0,0.04" 
        drawCorrelationPlot(hChAsymmErr,
                            xaxisTitle, yaxisTitle, zaxisTitle,
                            hChAsymmErr.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1, canvasSize="700,625",leftMargin=0.14,rightMargin=0.22,passCanvas=canvas)

        hChAsymmRelErr = hChAsymmErr.Clone(hChAsymmErr.GetName().replace("AsymmErr","AsymmRelErr"))
        hChAsymmRelErr.Divide(hChAsymm)
        hChAsymmRelErr.SetTitle(hChAsymmErr.GetTitle().replace("uncertainty","rel. uncertainty"))
        zaxisTitle = "Asymmetry relative uncertainty::%.3f,%.3f" % (max(0,0.99*hChAsymmRelErr.GetBinContent(hChAsymmRelErr.GetMinimumBin())),
                                                                    min(0.12,1.01*hChAsymmRelErr.GetBinContent(hChAsymmRelErr.GetMaximumBin()))
                                                                    )
        zaxisTitle = "Asymmetry relative uncertainty::0.01,0.3" 
        drawCorrelationPlot(hChAsymmRelErr,
                            xaxisTitle, yaxisTitle, zaxisTitle,
                            hChAsymmRelErr.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1, canvasSize="700,625",leftMargin=0.14,rightMargin=0.22,passCanvas=canvas)


    else:
        print "You used option --hessian, so I will quit now."
        print "If you want to plot the differential cross section as well, you can directly use 'w-helicity-13TeV/plotDiffXsecFromFit.py'"
        quit()
        # stop here with hessian for now
        # for the hessian cross section you can use w-helicity-13TeV/plotDiffXsecFromFit.py


    for charge in ["plus","minus"]:

        xaxisTitle = 'gen %s |#eta|' % lepton  # it will be modified later, so I have to restore it here


        chargeSign = "+" if charge == "plus" else "-"

        hDiffXsec = ROOT.TH2F("hDiffXsec_{lep}_{ch}".format(lep=lepton,ch=charge),
                              "cross section: {Wch}".format(Wch=Wchannel.replace('W','W{chs}'.format(chs=chargeSign))),
                              genBins.Neta, array('d',genBins.etaBins), genBins.Npt, array('d',genBins.ptBins))
        hDiffXsecErr = ROOT.TH2F("hDiffXsecErr_{lep}_{ch}".format(lep=lepton,ch=charge),
                                 "cross section uncertainty: {Wch}".format(Wch=Wchannel.replace('W','W{chs}'.format(chs=chargeSign))),
                                 genBins.Neta, array('d',genBins.etaBins), genBins.Npt, array('d',genBins.ptBins))
        hDiffXsecNorm = ROOT.TH2F("hDiffXsecNorm_{lep}_{ch}".format(lep=lepton,ch=charge),
                                  "normalized cross section: {Wch}".format(Wch=Wchannel.replace('W','W{chs}'.format(chs=chargeSign))),
                                  genBins.Neta, array('d',genBins.etaBins), genBins.Npt, array('d',genBins.ptBins))
        hDiffXsecNormErr = ROOT.TH2F("hDiffXsecNormErr_{lep}_{ch}".format(lep=lepton,ch=charge),
                                     "normalized cross section uncertainty: {Wch}".format(Wch=Wchannel.replace('W','W{chs}'.format(chs=chargeSign))),
                                     genBins.Neta, array('d',genBins.etaBins), genBins.Npt, array('d',genBins.ptBins))

        nbins = genBins.Neta * genBins.Npt
        binCount = 1        
        print "Now filling histograms with differential cross section (charge = %s)" % charge


        denExpression = ""
        if options.friend != "":
            denExpression = "totxsec_" + charge
        else:
            denExpression = utilities.getDenExpressionForNormDiffXsec(channel, charge, genBins.Neta,genBins.Npt, ngroup)


        for ieta in range(1,genBins.Neta+1):
            for ipt in range(1,genBins.Npt+1):

                #print "\rBin {num}/{tot}".format(num=binCount,tot=nbins),
                sys.stdout.write('Bin {num}/{tot}   \r'.format(num=binCount,tot=nbins))
                sys.stdout.flush()
                binCount += 1

                # normalized cross section
                #central,up,down = utilities.getNormalizedDiffXsecFromToys(channel,charge,
                #                                                          ieta-1,ipt-1,genBins.Neta,genBins.Npt,
                #                                                          ngroup,options.toyfile,denExpression, options.friend)
                central,up,down = utilities.getNormalizedDiffXsecFromToysFast(channel,charge,
                                                                              ieta-1,ipt-1,genBins.Neta,genBins.Npt,
                                                                              ngroup,denExpression, nHistBins=1000, minHist=0., maxHist=0.1, tree=tree)


                error = up - central
                hDiffXsecNorm.SetBinContent(ieta,ipt,central)        
                hDiffXsecNorm.SetBinError(ieta,ipt,error)         
                hDiffXsecNormErr.SetBinContent(ieta,ipt,error)
                
                # unnormalized cross section
                central,up,down = utilities.getDiffXsecFromToysFast(channel,charge,ieta-1,ipt-1,genBins.Neta,genBins.Npt,ngroup,
                                                                    nHistBins=2000, minHist=0., maxHist=200., tree=tree)
                error = up - central
                hDiffXsec.SetBinContent(ieta,ipt,central)        
                hDiffXsec.SetBinError(ieta,ipt,error)         
                hDiffXsecErr.SetBinContent(ieta,ipt,error)




        if options.normWidth:
            hDiffXsec.Scale(1.,"width")
            hDiffXsecErr.Scale(1.,"width")
            hDiffXsecNorm.Scale(1.,"width")
            hDiffXsecNormErr.Scale(1.,"width")

        hDiffXsecRelErr = hDiffXsecErr.Clone(hDiffXsecErr.GetName().replace('XsecErr','XsecRelErr'))
        hDiffXsecRelErr.Divide(hDiffXsec)
        hDiffXsecRelErr.SetTitle(hDiffXsecErr.GetTitle().replace('uncertainty','rel.unc.'))

        hDiffXsecNormRelErr = hDiffXsecNormErr.Clone(hDiffXsecNormErr.GetName().replace('XsecNormErr','XsecNormRelErr'))
        hDiffXsecNormRelErr.Divide(hDiffXsecNorm)
        hDiffXsecNormRelErr.SetTitle(hDiffXsecNormErr.GetTitle().replace('uncertainty','rel.unc.'))

        # now starting to draw the cross sections

        if charge == "plus": zmin,zmax = 30,120
        else:                zmin,zmax = 25,95
        #zaxisTitle = "d#sigma / d#etadp_{T} [pb/GeV]::%.3f,%.3f" % (0.9*hDiffXsec.GetMinimum(),hDiffXsec.GetMaximum())
        zaxisTitle = "d#sigma / d#etadp_{T} [pb/GeV]::%.3f,%.3f" % (zmin,zmax)
        drawCorrelationPlot(hDiffXsec,
                            xaxisTitle, yaxisTitle, zaxisTitle,
                            hDiffXsec.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1, canvasSize="700,625",leftMargin=0.14,rightMargin=0.22,passCanvas=canvas)

        if charge == "plus": zmin,zmax = 0.5,4.5
        else:                zmin,zmax = 0.5,3.5
        zaxisTitle = "uncertainty on d#sigma / d#etadp_{T} [pb/GeV]::%.3f,%.3f" % (0.9*hDiffXsecErr.GetMinimum(),min(10,hDiffXsecErr.GetMaximum()))
        #zaxisTitle = "uncertainty on d#sigma / d#etadp_{T} [pb/GeV]::%.3f,%.3f" % (zmin,zmax)
        drawCorrelationPlot(hDiffXsecErr,
                            xaxisTitle, yaxisTitle, zaxisTitle,
                            hDiffXsecErr.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1, canvasSize="700,625",leftMargin=0.14,rightMargin=0.22,passCanvas=canvas)

        #zaxisTitle = "rel. uncertainty on d#sigma / d#etadp_{T}::%.3f,%.3f" % (0.9*hDiffXsecRelErr.GetMinimum(),hDiffXsecRelErr.GetMaximum())
        zaxisTitle = "rel. uncertainty on d#sigma / d#etadp_{T}::0.025,0.1"
        drawCorrelationPlot(hDiffXsecRelErr,
                            xaxisTitle, yaxisTitle, zaxisTitle,
                            hDiffXsecRelErr.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1, canvasSize="700,625",leftMargin=0.14,rightMargin=0.22,passCanvas=canvas)

        if charge == "plus": zmin,zmax = 0.008,0.028
        else:                zmin,zmax = 0.008,0.029
        #zaxisTitle = "d#sigma / d#etadp_{T} / #sigma_{tot}::%.3f,%.3f" % (0.9*hDiffXsecNorm.GetMinimum(),hDiffXsecNorm.GetMaximum())
        zaxisTitle = "d#sigma / d#etadp_{T} / #sigma_{tot}::%.3f,%.3f" % (zmin,zmax)
        drawCorrelationPlot(hDiffXsecNorm,
                            xaxisTitle, yaxisTitle, zaxisTitle,
                            hDiffXsecNorm.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1, canvasSize="700,625",leftMargin=0.14,rightMargin=0.22,passCanvas=canvas)

        if charge == "plus": zmin,zmax = 0.0,0.0015
        else:                zmin,zmax = 0.0,0.0015
        #zaxisTitle = "uncertainty on d#sigma / d#etadp_{T} / #sigma_{tot}::%.3f,%.3f" % (0.9*hDiffXsecNormErr.GetMinimum(),hDiffXsecNormErr.GetMaximum())
        zaxisTitle = "uncertainty on d#sigma / d#etadp_{T} / #sigma_{tot}::%.3f,%.3f" % (zmin,zmax)
        drawCorrelationPlot(hDiffXsecNormErr,
                            xaxisTitle, yaxisTitle, zaxisTitle,
                            hDiffXsecNormErr.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1, canvasSize="700,625",leftMargin=0.14,rightMargin=0.22,passCanvas=canvas)

        zaxisTitle = "rel. uncertainty on d#sigma / d#etadp_{T} / #sigma_{tot}::%.3f,%.3f" % (0.9*hDiffXsecNormRelErr.GetMinimum(),min(0.1,hDiffXsecNormRelErr.GetBinContent(hDiffXsecNormRelErr.GetMaximumBin())))
        #zaxisTitle = "rel. uncertainty on d#sigma / d#etadp_{T} / #sigma_{tot}::0,0.1"
        drawCorrelationPlot(hDiffXsecNormRelErr,
                            xaxisTitle, yaxisTitle, zaxisTitle,
                            hDiffXsecNormRelErr.GetName(),
                            "ForceTitle",outname,1,1,False,False,False,1, canvasSize="700,625",leftMargin=0.14,rightMargin=0.22,passCanvas=canvas)



######
        # now drawing a TH1 unrolling TH2
        unrollAlongEta = False
        xaxisTitle = "template global bin"
        if unrollAlongEta:
            xaxisTitle = xaxisTitle + " = 1 + ieta + ipt * %d; ipt in [%d,%d], ieta in [%d,%d]" % (netabins-1,0,nptbins-1,0,netabins-1)
        else:
            xaxisTitle = xaxisTitle + " = 1 + ipt + ieta * %d; ipt in [%d,%d], ieta in [%d,%d]" % (nptbins-1,0,nptbins-1,0,netabins-1)
        h1D_pmaskedexp = getTH1fromTH2(hDiffXsec, hDiffXsecErr, unrollAlongX=unrollAlongEta)        
        drawSingleTH1(h1D_pmaskedexp,xaxisTitle,"d#sigma/d#etadp_{T} [pb/GeV]",
                      "unrolledXsec_abs_{ch}_{fl}".format(ch= charge,fl=channel),
                      outname,labelRatioTmp="Rel.Unc.::0.9,1.1",draw_both0_noLog1_onlyLog2=1,canvasSize="3000,2000")

        h1D_pmaskedexp_norm = getTH1fromTH2(hDiffXsecNorm, hDiffXsecNormErr, unrollAlongX=unrollAlongEta)        
        drawSingleTH1(h1D_pmaskedexp_norm,xaxisTitle,"d#sigma/d#etadp_{T} / #sigma_{tot} [1/GeV]",
                      "unrolledXsec_norm_{ch}_{fl}".format(ch= charge,fl=channel),
                      outname,labelRatioTmp="Rel.Unc.::0.9,1.1",draw_both0_noLog1_onlyLog2=1,canvasSize="3000,2000")


