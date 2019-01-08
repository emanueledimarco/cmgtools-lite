#!/usr/bin/env python

from shutil import copyfile
import re, sys, os, os.path, subprocess, json, ROOT
import numpy as np
from array import array

from CMS_lumi import *

#########################################################################

def addStringToEnd(name, matchToAdd, notAddIfEndswithMatch=False):
    if notAddIfEndswithMatch and name.endswith(matchToAdd):
        return name
    elif not name.endswith(matchToAdd):
        return name + matchToAdd

#########################################################################

def getZaxisReasonableExtremesTH2(h,nSigma=3,minZtoUse=None,maxZtoUse=None):

    htmp = ROOT.TH1D("htmp","",1000,h.GetMinimum(),h.GetMaximum())
    nbins = h.GetNbinsX() * h.GetNbinsY()    
    for ibin in range (1,nbins+1):
        val = h.GetBinContent(ibin)
        canFill = True
        if minZtoUse != None:
            if val < minZtoUse: canFill = False
        if maxZtoUse != None:
            if val > maxZtoUse: canFill = False
        if canFill: htmp.Fill(val)

    mean = htmp.GetMean()
    stddev = htmp.GetStdDev()
    retmin = max(h.GetMinimum(),mean - nSigma*stddev)
    retmax = min(h.GetMaximum(),mean + nSigma*stddev)
    return retmin,retmax


#########################################################################

def getMinMaxHisto(h, excludeEmpty=True, sumError=True):
    
    dim = h.GetDimension()
    nbins = 0
    if   dim == 1: nbins = h.GetNbinsX()
    elif dim == 2: nbins = h.GetNbinsX() * h.GetNbinsY()
    elif dim == 3: nbins = h.GetNbinsX() * h.GetNbinsY() * h.GetNbinsZ()
    else:
        print "Error in getMaxHisto(): dim = %d is not supported. Exit" % dim
        quit()

    maxval = 0
    minval = 0
    firstValidBin = -1
    for ibin in range (1,nbins+1):
        tmpmax = h.GetBinContent(ibin)
        tmpmin = h.GetBinContent(ibin)
        if excludeEmpty and tmpmin == 0.0: continue
        if firstValidBin < 0: 
            #print "ibin %d:   tmpmin,tmpmax = %.2f, %.2f" % (ibin,tmpmin,tmpmax)
            firstValidBin = ibin
        if sumError:
            tmpmin -= h.GetBinError(ibin)
            tmpmax += h.GetBinError(ibin)
        if firstValidBin > 0 and ibin == firstValidBin:
            #the first time we pick a non empty bin, we set min and max to the histogram content in that bin
            minval = tmpmin
            maxval = tmpmax
            #print "#### ibin %d:   min,max = %.2f, %.2f" % (ibin,minval,maxval)
        else:
            minval = min(minval,tmpmin)
            maxval = max(maxval,tmpmax)
        #print "ibin %d:   min,max = %.2f, %.2f" % (ibin,minval,maxval)
    
    return minval,maxval

#########################################################################


def createPlotDirAndCopyPhp(outdir):
    if outdir != "./":
        if not os.path.exists(outdir):
            os.system("mkdir -p "+outdir)
            if os.path.exists("/afs/cern.ch"): os.system("cp /afs/cern.ch/user/g/gpetrucc/php/index.php "+outdir)
    

#########################################################################

def getAxisRangeFromUser(axisNameTmp="", 
                         separator="::", 
                         rangeSeparator=","
                         ):
  
    setXAxisRangeFromUser = False;
    fields = axisNameTmp.split(separator)
    axisName = fields[0]
    
    if len(fields) > 1:
        setXAxisRangeFromUser = True;
        xmin = float(fields[1].split(rangeSeparator)[0])
        xmax = float(fields[1].split(rangeSeparator)[1])
    else:
        xmin = 0
        xmax = 0
        
    return axisName,setXAxisRangeFromUser,xmin,xmax


#########################################################################

def adjustSettings_CMS_lumi():

    ## dummy function to be called before using any other fucntion calling CMS_lumi
    ## for some reason, the settings of the very first plot are screwed up.
    ## To fix this issue, it is enough to call it to a dummy plot
    dummy = ROOT.TH1D("dummy","",10,0,10)
    for i in range(1,1+dummy.GetNbinsX()):
        dummy.SetBinContent(i,i)
    dummy.GetXaxis().SetTitle("x axis")
    dummy.GetYaxis().SetTitle("y axis")
    cdummy = ROOT.TCanvas("cdummy","",600,600)
    dummy.Draw("HE")
    CMS_lumi(cdummy,"",True,False)
    setTDRStyle()        
    ## no need to save the canvas    


#########################################################################

# function to draw 2D histograms, can also plot profile along X on top
def drawCorrelationPlot(h2D_tmp,
                        labelXtmp="xaxis", labelYtmp="yaxis", labelZtmp="zaxis",
                        canvasName="default", plotLabel="", outdir="./",
                        rebinFactorY=0,
                        rebinFactorX=0,
                        smoothPlot=True,
                        drawProfileX=True,
                        scaleToUnitArea=True,
                        draw_both0_noLog1_onlyLog2=0,
                        leftMargin=0.16,
                        rightMargin=0.20,
                        nContours=50,
                        palette=57,
                        canvasSize="700,625",
                        passCanvas=None,
                        bottomMargin=0.1,
                        plotError=False):


    # if h2D.GetName() == "scaleFactor_origBinPt":
    #     print "="*20
    #     print "Check: hist %s: Z axis title = %s" % (h2D.GetName(),labelZtmp)
    #     print "="*20

    ROOT.TH1.SetDefaultSumw2()
    adjustSettings_CMS_lumi()

    if (rebinFactorX): 
        if isinstance(rebinFactorX, int): h2D_tmp.RebinY(rebinFactorX)
        else:                             h2D_tmp.RebinY(len(rebinFactorX)-1,"",array('d',rebinFactorX)) # case in which rebinFactorX is a list of bin edges

    if (rebinFactorY): 
        if isinstance(rebinFactorY, int): h2D_tmp.RebinY(rebinFactorY)
        else:                             h2D_tmp.RebinY(len(rebinFactorY)-1,"",array('d',rebinFactorY)) # case in which rebinFactorX is a list of bin edges

    if plotError:
        herr = h2D_tmp.Clone(h2D_tmp.GetName()+"_err")
        herr.Reset("ICESM")
        for i in range(1,herr.GetNbinsX()+1):
            for j in range(1,herr.GetNbinsY()+1):
                herr.SetBinContent(i,j,h2D_tmp.GetBinError(i,j))
        h2D = herr
    else:
        h2D = h2D_tmp


    ROOT.gStyle.SetPalette(palette)  # 55:raibow palette ; 57: kBird (blue to yellow, default) ; 107 kVisibleSpectrum ; 77 kDarkRainBow 
    ROOT.gStyle.SetNumberContours(nContours) # default is 20 

    labelX,setXAxisRangeFromUser,xmin,xmax = getAxisRangeFromUser(labelXtmp)
    labelY,setYAxisRangeFromUser,ymin,ymax = getAxisRangeFromUser(labelYtmp)
    labelZ,setZAxisRangeFromUser,zmin,zmax = getAxisRangeFromUser(labelZtmp)
    
    cw,ch = canvasSize.split(',')
    #canvas = ROOT.TCanvas("canvas",h2D.GetTitle() if plotLabel == "ForceTitle" else "",700,625)    
    canvas = passCanvas if passCanvas != None else ROOT.TCanvas("canvas","",int(cw),int(ch))
    canvas.SetLeftMargin(leftMargin)
    canvas.SetRightMargin(rightMargin)
    canvas.SetBottomMargin(bottomMargin)
    canvas.cd()

    addStringToEnd(outdir,"/",notAddIfEndswithMatch=True)
    createPlotDirAndCopyPhp(outdir)
    # normalize to 1
    if (scaleToUnitArea): h2D.Scale(1./h2D.Integral())

    h2DGraph = 0

    h2DPlot = 0
    if (not smoothPlot): h2DPlot = h2D
    else:
        h2DGraph = ROOT.TGraph2D()
        h2DGraph.SetNpx(300)
        h2DGraph.SetNpy(300)
        nPoint = 0
        for iBinX in range (1,1+h2D.GetNbinsX()):
            for iBinY in range(1,1+h2D.GetNbinsY()):
                h2DGraph.SetPoint(nPoint,h2D.GetXaxis().GetBinCenter(iBinX),h2D.GetYaxis().GetBinCenter(iBinY),h2D.GetBinContent(iBinX,iBinY))
                nPoint += 1
            

        h2DPlot = h2DGraph.GetHistogram()
  
    h2DPlot.GetXaxis().SetTitle(labelX)
    h2DPlot.GetYaxis().SetTitle(labelY)
    h2DPlot.GetXaxis().SetTitleSize(0.05)
    h2DPlot.GetXaxis().SetLabelSize(0.04)
    h2DPlot.GetXaxis().SetTitleOffset(0.95) # 1.1 goes outside sometimes, maybe depends on root version or canvas width
    h2DPlot.GetYaxis().SetTitleSize(0.05)
    h2DPlot.GetYaxis().SetLabelSize(0.04)
    h2DPlot.GetYaxis().SetTitleOffset(1.1)
    h2DPlot.GetZaxis().SetTitleSize(0.05)
    h2DPlot.GetZaxis().SetLabelSize(0.04)
    h2DPlot.GetZaxis().SetTitleOffset(1.2)

    h2DPlot.GetZaxis().SetTitle(labelZ) 
    h2DPlot.Draw("colz")
    if (setXAxisRangeFromUser): h2DPlot.GetXaxis().SetRangeUser(xmin,xmax)
    if (setYAxisRangeFromUser): h2DPlot.GetYaxis().SetRangeUser(ymin,ymax)
    if (setZAxisRangeFromUser): h2DPlot.GetZaxis().SetRangeUser(zmin,zmax)


    # if h2D.GetName() == "scaleFactor_origBinPt":
    #     print "="*20
    #     print "Check: hist %s: Z axis title = %s" % (h2DPlot.GetName(),h2DPlot.GetZaxis().GetTitle())
    #     print "="*20

    # attempt to make Z axis title farther depending on how many digits are printed
    maxZaxisVal = h2DPlot.GetBinContent(h2DPlot.GetMaximumBin())
    if (setZAxisRangeFromUser): maxZaxisVal = zmax

    if maxZaxisVal >= 1.0:
        rootYear = int(str(ROOT.gROOT.GetVersionDate())[:4])        
        if (rootYear > 2016):
            h2DPlot.GetZaxis().SetMaxDigits(3)
        else:
            print "Warning in drawCorrelationPlot: TAxis::SetMaxDigits() not implemented for ROOT versions before 2017 (rough estimate)"
            print "Will not exit, but instruction will be neglected"
        if maxZaxisVal > 9999.:
            h2DPlot.GetZaxis().SetTitleOffset(h2DPlot.GetZaxis().GetTitleOffset()+0.15)
            print "Changing title offset by 0.15"
    else:
        i = 1
        tryNext = True
        while (tryNext and i < 6):
            tmpVal = maxZaxisVal * pow(10,i)
            if tmpVal >= 1.0: tryNext = False 
            else: i += 1
        if i > 1:            
            print "Max Z axis < 1, will try to adjust distance of Z axis title to Z axis"
            print "i = %d: will move Z axis offset by 0.45" % i
            # for numbers like 0.025 or with more 0 after ., make increase distance between Z axis title and the Z axis
            h2DPlot.GetZaxis().SetTitleOffset(h2DPlot.GetZaxis().GetTitleOffset()+0.45)

    h2DProfile = 0
    if drawProfileX:
        h2DProfile = h2D.ProfileX("%s_pfx" %h2D.GetName())
        h2DProfile.SetMarkerColor(ROOT.kBlack)
        h2DProfile.SetMarkerStyle(20)
        h2DProfile.SetMarkerSize(1)
        h2DProfile.Draw("EPsame")
        
    # not yet implemented
    if not plotLabel == "ForceTitle": CMS_lumi(canvas,"",True,False)
    setTDRStyle()
    #print ">>>>>>>>>>>>>> check <<<<<<<<<<<<<<<<<<<"

    if plotLabel == "ForceTitle":
        ROOT.gStyle.SetOptTitle(1)        

    #h2DPlot.GetZaxis().SetMaxDigits(1)  #for N>99, should use scientific notation, I'd like to make it work only with negative exponential but haven't succeeded yet
    # canvas.Modified()
    # canvas.Update()

    leg = ROOT.TLegend(0.39,0.75,0.89,0.95)
    leg.SetFillStyle(0)
    leg.SetFillColor(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(62)
    if plotLabel not in ["", "ForceTitle"]: leg.AddEntry(0,plotLabel,"")
    if drawProfileX: leg.AddEntry(0,"Correlation = %.2f" % h2DPlot.GetCorrelationFactor(),"")
    leg.Draw("same")

    if (draw_both0_noLog1_onlyLog2 == 0 or draw_both0_noLog1_onlyLog2 == 1):
        for ext in ['png', 'pdf']:
            canvas.SaveAs('{od}/{cn}.{ext}'.format(od=outdir, cn=canvasName, ext=ext))
        
    if (draw_both0_noLog1_onlyLog2 == 0 or draw_both0_noLog1_onlyLog2 == 2):
        canvas.SetLogz()
        for ext in ['png', 'pdf']:
            canvas.SaveAs('{od}/{cn}_logZ.{ext}'.format(od=outdir, cn=canvasName, ext=ext))
        canvas.SetLogz(0)


##########################################################


def drawSingleTH1(h1,
                  labelXtmp="xaxis", labelYtmp="yaxis",
                  canvasName="default", outdir="./",
                  rebinFactorX=0,
                  draw_both0_noLog1_onlyLog2=0,                  
                  leftMargin=0.12,
                  rightMargin=0.04,
                  labelRatioTmp="Rel.Unc.::0.5,1.5",
                  drawStatBox=False,
                  legendCoords="0.15,0.35,0.3,0.45",  # x1,x2,y1,y2
                  canvasSize="600,700",  # use X,Y to pass X and Y size     
                  lowerPanelHeight = 0.3,  # number from 0 to 1, 0.3 means 30% of space taken by lower panel. 0 means do not draw lower panel with relative error
                  drawLineLowerPanel="lumi. uncertainty::0.026" # if not empty, draw band at 1+ number after ::, and add legend with title
                  ):

    if (rebinFactorX): 
        if isinstance(rebinFactorX, int): h1.Rebin(rebinFactorX)
        # case in which rebinFactorX is a list of bin edges
        else:                             h1.Rebin(len(rebinFactorX)-1,"",array('d',rebinFactorX)) 

    xAxisName,setXAxisRangeFromUser,xmin,xmax = getAxisRangeFromUser(labelXtmp)
    yAxisName,setYAxisRangeFromUser,ymin,ymax = getAxisRangeFromUser(labelYtmp)
    yRatioAxisName,setRatioYAxisRangeFromUser,yminRatio,ymaxRatio = getAxisRangeFromUser(labelRatioTmp)

    addStringToEnd(outdir,"/",notAddIfEndswithMatch=True)
    createPlotDirAndCopyPhp(outdir)

    cw,ch = canvasSize.split(',')
    #canvas = ROOT.TCanvas("canvas",h2D.GetTitle() if plotLabel == "ForceTitle" else "",700,625)
    canvas = ROOT.TCanvas("canvas","",int(cw),int(ch))
    canvas.SetTickx(1)
    canvas.SetTicky(1)
    canvas.cd()
    canvas.SetLeftMargin(leftMargin)
    canvas.SetRightMargin(rightMargin)
    canvas.cd()

    pad2 = 0
    if lowerPanelHeight: 
        canvas.SetBottomMargin(lowerPanelHeight)
        pad2 = ROOT.TPad("pad2","pad2",0,0.,1,0.9)
        pad2.SetTopMargin(1-lowerPanelHeight)
        pad2.SetRightMargin(rightMargin)
        pad2.SetLeftMargin(leftMargin)
        pad2.SetFillColor(0)
        pad2.SetGridy(1)
        pad2.SetFillStyle(0)


    frame = h1.Clone("frame")
    frame.GetXaxis().SetLabelSize(0.04)
    frame.SetStats(0)

    h1.SetLineColor(ROOT.kBlack)
    h1.SetMarkerColor(ROOT.kBlack)
    h1.SetMarkerStyle(20)
    h1.SetMarkerSize(0)

    #ymax = max(ymax, max(h1.GetBinContent(i)+h1.GetBinError(i) for i in range(1,h1.GetNbinsX()+1)))
    # if min and max were not set, set them based on histogram content
    if ymin == ymax == 0.0:
        ymin,ymax = getMinMaxHisto(h1,excludeEmpty=True,sumError=True)    
        #print "Histo: %s     minY,maxY = %.2f, %.2f" % (h1.GetName(),ymin,ymax)

    print "#### WARNING ####"
    print "Hardcoding ymin = 0 in function drawSingleTH1(): change it if it is not what you need"
    print "#################"
    ymin = 0 # hardcoded

    if lowerPanelHeight:
        h1.GetXaxis().SetLabelSize(0)
        h1.GetXaxis().SetTitle("")  
    else:
        h1.GetXaxis().SetTitle(xAxisName)
        h1.GetXaxis().SetTitleOffset(1.2)
        h1.GetXaxis().SetTitleSize(0.05)
        h1.GetXaxis().SetLabelSize(0.04)
    h1.GetYaxis().SetTitle(yAxisName)
    h1.GetYaxis().SetTitleOffset(1.15)
    h1.GetYaxis().SetTitleSize(0.05)
    h1.GetYaxis().SetLabelSize(0.04)
    h1.GetYaxis().SetRangeUser(ymin * 0.9, ymax * 1.1)
    if setXAxisRangeFromUser: h1.GetXaxis().SetRangeUser(xmin,xmax)
    h1.Draw("HIST")
    h1err = h1.Clone("h1err")
    h1err.SetFillColor(ROOT.kRed+2)
    #h1err.SetFillStyle(3001)
    h1err.SetFillStyle(3002)
    #h1err.SetFillStyle(3005)
    h1err.Draw("E2same")
    #h1.Draw("HIST same")

    legcoords = [float(x) for x in legendCoords.split(',')]
    lx1,lx2,ly1,ly2 = legcoords[0],legcoords[1],legcoords[2],legcoords[3]
    leg = ROOT.TLegend(lx1,ly1,lx2,ly2)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.AddEntry(h1,"Value","L")
    leg.AddEntry(h1err,"Uncertainty","F")
    leg.Draw("same")
    canvas.RedrawAxis("sameaxis")

    if drawStatBox:
        ROOT.gPad.Update()
        ROOT.gStyle.SetOptStat(1110)
        ROOT.gStyle.SetOptFit(1102)
    else:
        h1.SetStats(0)

  # TPaveText *pvtxt = NULL;
  # if (yAxisName == "a.u.") {
  #   pvtxt = new TPaveText(0.6,0.6,0.95,0.7, "BR NDC")
  #   pvtxt.SetFillColor(0)
  #   pvtxt.SetFillStyle(0)
  #   pvtxt.SetBorderSize(0)
  #   pvtxt.AddText(Form("norm num/den = %.2f +/- %.2f",IntegralRatio,ratioError))
  #   pvtxt.Draw()
  # }

    #if lumi < 0: CMS_lumi(canvas,"",false,false)
    #else: CMS_lumi(canvas,Form("%.1f",lumi),false,false)
    setTDRStyle()

    if lowerPanelHeight:
        pad2.Draw()
        pad2.cd()

        frame.Reset("ICES")
        if setRatioYAxisRangeFromUser: frame.GetYaxis().SetRangeUser(yminRatio,ymaxRatio)
        #else:                          
        #frame.GetYaxis().SetRangeUser(0.5,1.5)
        frame.GetYaxis().SetNdivisions(5)
        frame.GetYaxis().SetTitle(yRatioAxisName)
        frame.GetYaxis().SetTitleOffset(1.15)
        frame.GetYaxis().SetTitleSize(0.05)
        frame.GetYaxis().SetLabelSize(0.04)
        frame.GetYaxis().CenterTitle()
        frame.GetXaxis().SetTitle(xAxisName)
        if setXAxisRangeFromUser: frame.GetXaxis().SetRangeUser(xmin,xmax)
        frame.GetXaxis().SetTitleOffset(1.2)
        frame.GetXaxis().SetTitleSize(0.05)

        ratio = h1.Clone("ratio")
        den_noerr = h1.Clone("den_noerr")
        for iBin in range (1,den_noerr.GetNbinsX()+1):
            den_noerr.SetBinError(iBin,0.)

        ratio.Divide(den_noerr)
        ratio.SetFillColor(ROOT.kGray)
        #den_noerr.SetFillColor(ROOT.kGray)
        frame.Draw()
        ratio.SetMarkerSize(0)
        ratio.SetMarkerStyle(0) # important to remove dots at y = 1
        ratio.Draw("E2same")
    
        line = ROOT.TF1("horiz_line","1",ratio.GetXaxis().GetBinLowEdge(1),ratio.GetXaxis().GetBinLowEdge(ratio.GetNbinsX()+1))
        line.SetLineColor(ROOT.kRed)
        line.SetLineWidth(2)
        line.Draw("Lsame")

        if drawLineLowerPanel:
            legEntry,yline = drawLineLowerPanel.split('::')
            line2 = ROOT.TF1("horiz_line_2",str(1+float(yline)),ratio.GetXaxis().GetBinLowEdge(1),ratio.GetXaxis().GetBinLowEdge(ratio.GetNbinsX()+1))
            line3 = ROOT.TF1("horiz_line_3",str(1-float(yline)),ratio.GetXaxis().GetBinLowEdge(1),ratio.GetXaxis().GetBinLowEdge(ratio.GetNbinsX()+1))
            line2.SetLineColor(ROOT.kBlue)
            line2.SetLineWidth(2)
            line2.Draw("Lsame")
            line3.SetLineColor(ROOT.kBlue)
            line3.SetLineWidth(2)
            line3.Draw("Lsame")
            leg2 = ROOT.TLegend(0.15,0.22,0.35,0.32)
            leg2.SetFillColor(0)
            leg2.SetFillStyle(0)
            leg2.SetBorderSize(0)
            leg2.AddEntry(line2,legEntry,"L")
            leg2.Draw("same")

        
        pad2.RedrawAxis("sameaxis")


    if draw_both0_noLog1_onlyLog2 != 2:
        canvas.SaveAs(outdir + canvasName + ".png")
        canvas.SaveAs(outdir + canvasName + ".pdf")

    if draw_both0_noLog1_onlyLog2 != 1:        
        if yAxisName == "a.u.": 
            h1.GetYaxis().SetRangeUser(max(0.0001,h1.GetMinimum()*0.8),h1.GetMaximum()*100)
        else:
            h1.GetYaxis().SetRangeUser(max(0.001,h1.GetMinimum()*0.8),h1.GetMaximum()*100)
        canvas.SetLogy()
        canvas.SaveAs(outdir + canvasName + "_logY.png")
        canvas.SaveAs(outdir + canvasName + "_logY.pdf")
        canvas.SetLogy(0)
        
          
  
