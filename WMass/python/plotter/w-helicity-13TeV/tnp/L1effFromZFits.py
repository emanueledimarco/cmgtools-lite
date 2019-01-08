#!/usr/bin/env python
import sys, os
import numpy as np
from math import *
from array import array
from CMGTools.WMass.plotter.mcPlots import doSpam,SAFE_COLOR_LIST

## safe batch mode
import sys
import ROOT
ROOT.gROOT.SetBatch(True)

SAFE_STYLE_LIST = [ROOT.kOpenCircle,ROOT.kOpenSquare,ROOT.kOpenTriangleUp,ROOT.kOpenDiamond,ROOT.kOpenTriangleDown]

def doTinyCmsPrelimStandalone(textLeft="_default_",textRight="_default_",hasExpo=False,textSize=0.033,lumi=None, xoffs=0, options=None):
    if textLeft  == "_default_": textLeft  = "#bf{CMS} #it{Preliminary}"
    if textRight == "_default_": textRight = "%(lumi) (13 TeV)"
    if lumi      == None       : lumi      = 35.9
    if   lumi > 3.54e+1: lumitext = "%.0f fb^{-1}" % lumi
    elif lumi > 3.54e+0: lumitext = "%.1f fb^{-1}" % lumi
    elif lumi > 3.54e-1: lumitext = "%.2f fb^{-1}" % lumi
    elif lumi > 3.54e-2: lumitext = "%.0f pb^{-1}" % (lumi*1000)
    elif lumi > 3.54e-3: lumitext = "%.1f pb^{-1}" % (lumi*1000)
    else               : lumitext = "%.2f pb^{-1}" % (lumi*1000)
    lumitext = "%.1f fb^{-1}" % lumi
    textLeft = textLeft.replace("%(lumi)",lumitext)
    textRight = textRight.replace("%(lumi)",lumitext)
    if textLeft not in ['', None]:
        doSpam(textLeft, (.28 if hasExpo else .17)+xoffs, .955, .60+xoffs, .995, align=12, textSize=textSize)
    if textRight not in ['', None]:
        doSpam(textRight,.68+xoffs, .955, .99+xoffs, .995, align=12, textSize=textSize)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] num.root den.root")
    parser.add_option("-o", "--outdir"    ,  type='string'    , default='./'  ,  help="save the files in this outdir")
    (options, args) = parser.parse_args()

    print "len = ",len(args)
    print "args = ",args
    if len(args) != 2:
        print "You must provide two tables: num and denom"
        exit(0)
    else: 
        print "using {num} (BX=-1) and {den} (BX=0) files".format(num=args[0],den=args[1])

    ROOT.gROOT.ProcessLine(".x ~/cpp/tdrstyle.cc")
    ROOT.gStyle.SetOptFit(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)

    outFileName = "{out}/l1EG_eff.root".format(out=options.outdir)
    effFile = ROOT.TFile.Open(outFileName,'recreate')

    tfbxm1 = ROOT.TFile.Open(args[0])
    hm1 = tfbxm1.Get('bxm1_f_signal')
    tfbx0 = ROOT.TFile.Open(args[1])
    h0 = tfbx0.Get('bx0_f_signal')
    nbinspt, nbinseta = (h0.GetNbinsY(), h0.GetNbinsX())
    ptmin, ptmax = (h0.GetYaxis().GetBinLowEdge(1),h0.GetYaxis().GetBinUpEdge(nbinspt))
    ptbins  = [h0.GetYaxis().GetBinLowEdge(ipt+1) for ipt in xrange(h0.GetNbinsY()+1)]
    etabins = [h0.GetXaxis().GetBinLowEdge(ieta+1) for ieta in xrange(h0.GetNbinsX()+1)]

    effFile.cd()
    eff_th2 = ROOT.TH2D("l1EG_eff","",120,-3.0,3.0,len(ptbins)-1,array('d',ptbins))
    
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(1);

    for ipt in xrange(len(ptbins)-1):
        iptmin, iptmax = (h0.GetYaxis().GetBinLowEdge(ipt+1),h0.GetYaxis().GetBinUpEdge(ipt+1))
        print "IPT bin = {pt}, range = ({ptmin},{ptmax})...".format(pt=ipt,ptmin=iptmin,ptmax=iptmax)
        h0_eta = ROOT.TH1D("bx0_eta_ipt%d" % ipt, "",len(etabins)-1,array('f',etabins))
        hm1_eta = h0_eta.Clone("bxm1_eta_ipt%d" % ipt)
        for ieta in xrange(nbinseta):
            h0_eta.SetBinContent(ieta+1,h0.GetBinContent(ieta+1,ipt+1))
            hm1_eta.SetBinContent(ieta+1,hm1.GetBinContent(ieta+1,ipt+1))
        
        h0_eta.Add(hm1_eta)
     
        pEff_eta = ROOT.TEfficiency(hm1_eta,h0_eta)
        pEff_eta.SetStatisticOption(ROOT.TEfficiency.kFCP);
     
        c1 = ROOT.TCanvas("c1","",600,600)

        pEff_eta.SetTitle(";#eta;BX-1 probability")
        pEff_eta.Draw("AP")    
        ROOT.gPad.Update()
        graph = pEff_eta.GetPaintedGraph()
        graph.SetMinimum(0.0)
        graph.SetMaximum(1.0)
        xminfit,xmaxfit = (1.5,3.0) if ipt==0 else (2.2,3.0)
        func_plus  = ROOT.TF1("func_plus"  , "expo", xminfit, xmaxfit);
        func_minus = ROOT.TF1("func_minus" , "expo",-xmaxfit,-xminfit);
        graph.Fit('func_plus','R','sames')
        graph.Fit('func_minus','RS+','sames')
     
        x=ROOT.Double(0); ymin = ROOT.Double(0);  ymax = ROOT.Double(0);
        graph.GetPoint(0,x,ymin)
        graph.GetPoint(graph.GetN()-1,x,ymax)
     
        ROOT.gPad.Update(); 
        doTinyCmsPrelimStandalone(lumi=35.9)
        for ext in ['pdf','png']:
            c1.SaveAs("{out}/l1eff_vseta_pt{ptmin:.0f}_{ptmax:.0f}.{ext}".format(out=options.outdir,ptmin=iptmin,ptmax=iptmax,ext=ext))
     
        for ieta in xrange(120):
            hi = eff_th2.GetXaxis().GetBinUpEdge(ieta+1)
            center = eff_th2.GetXaxis().GetBinCenter(ieta+1)
            if hi < -1.5:
                prefireProb = min(ymin,func_minus(center))
            elif hi < 1.5:
                prefireProb = 0
            else:
                prefireProb = min(ymax,func_plus(center))
            eff_th2.SetBinContent(ieta+1, ipt+1, 1.0-prefireProb)
            point = h0.GetXaxis().FindFixBin(center)
            eff_th2.SetBinError(ieta+1, ipt+1, graph.GetErrorY(point-1))

    eff_th2.Write()
    effFile.Close()
     
    print "Smoothed pre-fire SF saved in ",outFileName
