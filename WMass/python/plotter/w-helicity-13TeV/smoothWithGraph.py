import ROOT, copy
from array import array
import os

import sys
sys.path.append(os.getcwd() + "/plotUtils/")
from utility import *

ROOT.gROOT.SetBatch(True)

## usage
## python smoothWithGraph.py -i <infile> -o <outdir> -h <histNameToSmooth>

# Warning: TGraph2D is a graph, so one sets x,y of its points and assign a Z. The constructor with TH2 used the TH2 bin centers to define the points
# Now, the binning of the TH2 returned by GetHistogram() has the bin boundaries on the x,y points (not the bin centers as in the original TH2)
# So, we have to find a way to get a histogram whose binning is consistent with the input
# Indeed, the TH2 returned by the graphs is created with the same number of bins of the input TH2, but slightly narrower axis range (and probably uniform binning)
# This results in an output histogram not consistent with the input (cannot divide, or add for example)

#-------------------------

def printBins(hist2d,text=""):

    nbinsX = hist2d.GetNbinsX()
    nbinsY = hist2d.GetNbinsY()
    print "-"*30
    print text
    print "bin X {n}   {low:.3g}  {high:.3g}".format(n=str(nbinsX),
                                                     low=hist2d.GetXaxis().GetBinLowEdge(1),
                                                     high=hist2d.GetXaxis().GetBinLowEdge(1+nbinsX)
                                                     )
    print "bin Y {n}   {low:.3g}  {high:.3g}".format(n=str(nbinsY),
                                                     low=hist2d.GetYaxis().GetBinLowEdge(1),
                                                     high=hist2d.GetYaxis().GetBinLowEdge(1+nbinsY)
                                                     )
    print "-"*30

#-------------------------


if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] ')
    parser.add_option('-i', '--infile'         , dest='infile'     , default=''      , type='string', help='input file with the plot and ratio')
    parser.add_option('-o', '--outdir'         , dest='outdir'     , default=''      , type='string', help='output directory')
    parser.add_option('-n', '--name'           , dest='name'       , default='smoothGraph.root'      , type='string', help='output file name')
    parser.add_option(      '--hist'           , dest='hist'       , default='scaleFactor'      , type='string', help='name of histogram to smooth')
    (options, args) = parser.parse_args()

    ROOT.TH1.SetDefaultSumw2()

    if not options.outdir:
        print "Error: you need to specify an output folder with option -o. Abort"
        quit()       

    outdir = options.outdir
    if not outdir.endswith('/'): outdir += "/"
    createPlotDirAndCopyPhp(outdir)
    os.system("cp /afs/cern.ch/user/m/mciprian/public/index.php %s" % outdir)
    outfileName = outdir + options.name

    infile = ROOT.TFile(options.infile, 'read')
    if not infile:
        print "Error: could not open file %s. Abort" % options.infile
        quit()       

    hist2d = infile.Get(options.hist)
    if not hist2d:
        print "Error: could not retrieve histogram %s. Abort" % options.hist
        quit()
    hist2d.SetDirectory(0)

    printBins(hist2d,"Input")

    xarray = array('d', hist2d.GetXaxis().GetXbins())
    # don't know why I can't get y binning as I did for X axis. Darn you ROOT!
    # yarray = array('d', hist2d.GetYaxis().GetXbins())
    # print yarray
    tmparray = []
    for i in range(1,hist2d.GetNbinsY()+2):
        tmparray.append(round(hist2d.GetYaxis().GetBinLowEdge(i),4))
    yarray = array('d', tmparray)

    print "="*30
    print "Input X binning"
    print xarray
    print "-"*30
    print "Input Y binning"
    print yarray
    print "="*30

    # xarray might not be uniform, so if we want more granularity, we must build the new binning bin by bin
    binSplitFactor = 3  # 3 is good enough, with more splitting, the smooth affects only a narrower strip between two bins
    newxarray = []
    for i in range(len(xarray)-1):
        width = xarray[i+1]-xarray[i]
        for j in range(binSplitFactor):
            newxarray.append(round(xarray[i] + float(j)*width/float(binSplitFactor), 4))
    newxarray.append(xarray[-1])
    #print newxarray   # I suggest you print once in life to see what happens

    # do also a manual smoothing interpolating with a line (so modyfing the two sub-bins at the borders of the original bin)
    h2HandSmooth = ROOT.TH2D("h2HandSmooth","",len(newxarray)-1, array('d',newxarray), len(yarray)-1, yarray)
    # now fill it from the input (which is coarser)
    for ix in range(1,1+h2HandSmooth.GetNbinsX()):
        for iy in range(1,1+h2HandSmooth.GetNbinsY()):
            xval = h2HandSmooth.GetXaxis().GetBinCenter(ix)
            yval = h2HandSmooth.GetYaxis().GetBinCenter(iy)
            hist2xbin = hist2d.GetXaxis().FindFixBin(xval)
            hist2ybin = hist2d.GetYaxis().FindFixBin(yval)
            h2HandSmooth.SetBinContent(ix,iy,hist2d.GetBinContent(hist2xbin,hist2ybin))
            h2HandSmooth.SetBinError(ix,iy,hist2d.GetBinError(hist2xbin,hist2ybin))
            # now interpolate eta
            if ix == 1 or ix == h2HandSmooth.GetNbinsX(): continue # do not modify the outer bins
            etabinID = ix%binSplitFactor  # which sub-bin inside the bin (if binSplitFactor=3, can be 1,2,0 for first, second and third sub-bin)
            if  etabinID == 1:   
                # if sub-bin on the left, take this -1/3 of the difference between this and the previous (computed in the central sub-bin)
                thisVal = hist2d.GetBinContent(hist2xbin,hist2ybin)
                otherVal = hist2d.GetBinContent(hist2xbin-1,hist2ybin)
                val = thisVal - 1. * (thisVal - otherVal) / 3.
                h2HandSmooth.SetBinContent(ix,iy,val)
            elif etabinID == 0:
                # if sub-bin on the right, take this -1/3 of the difference between this and the following (computed in the central sub-bin)
                thisVal = hist2d.GetBinContent(hist2xbin,hist2ybin)
                otherVal = hist2d.GetBinContent(hist2xbin+1,hist2ybin)
                val = thisVal - 1. * (thisVal - otherVal) / 3.
                h2HandSmooth.SetBinContent(ix,iy,val)



    h2new = ROOT.TH2D("Graph2D_from_"+hist2d.GetName()+"_smoothedByGraph","",len(newxarray)-1, array('d',newxarray), len(yarray)-1, yarray)
    # now fill it from the input (which is coarser)
    for ix in range(1,1+h2new.GetNbinsX()):
        for iy in range(1,1+h2new.GetNbinsY()):
            xval = h2new.GetXaxis().GetBinCenter(ix)
            yval = h2new.GetYaxis().GetBinCenter(iy)
            hist2xbin = hist2d.GetXaxis().FindFixBin(xval)
            hist2ybin = hist2d.GetYaxis().FindFixBin(yval)
            h2new.SetBinContent(ix,iy,hist2d.GetBinContent(hist2xbin,hist2ybin))
            h2new.SetBinError(ix,iy,hist2d.GetBinError(hist2xbin,hist2ybin))

    minz = h2new.GetMinimum()
    maxz = h2new.GetMaximum()


    graph2d = ROOT.TGraph2D()  # create it empty, will set the points later
    graph2d.SetNpx(len(newxarray)-1) # more granular in eta with respect to input
    graph2d.SetNpy(len(yarray)-1)  # pt has already 0.2 GeV granularity (to check, but was the default behaviour to produce the input histogram)

    nPoint = 0
    for iBinX in range (1,1+h2new.GetNbinsX()):
        for iBinY in range(1,1+h2new.GetNbinsY()):
            graph2d.SetPoint(nPoint,h2new.GetXaxis().GetBinCenter(iBinX),h2new.GetYaxis().GetBinCenter(iBinY),h2new.GetBinContent(iBinX,iBinY))
            nPoint += 1    

    graphFrom_h2new = graph2d.GetHistogram() ## have to call this, otherwise root will freak out
    graphFrom_h2new.SetName("fromGraph")
    # now, this graph is not really smoothed, as h2new was just the same version of the input but with more bins: all new bins inside the the same original bin
    # have the same value, so effectively the only slight smoothing happens on the borders on the input bins, which results in a smoothed histogram almost equal
    # to the input
    # One can add more bins to the graphs, see below

    printBins(graphFrom_h2new,"Output of graph smoothing")
    printBins(h2new,"Output of h2new")
    
    # here we refill h2new with the smoothed histogram (there might be some unwanted border effects)
    for ix in range(1,1+h2new.GetNbinsX()):
        for iy in range(1,1+h2new.GetNbinsY()):
            xval = h2new.GetXaxis().GetBinCenter(ix)
            yval = h2new.GetYaxis().GetBinCenter(iy)
            xbin = graphFrom_h2new.GetXaxis().FindFixBin(xval)
            ybin = graphFrom_h2new.GetYaxis().FindFixBin(yval)            
            h2new.SetBinContent(ix,iy,graphFrom_h2new.GetBinContent(xbin,ybin))
    # ok, but now if one draws h2new, a white band will appear for x = lastbinX and y = lastbinX
    # this is because graphFrom_h2new has slightly shorter axis ranges, so the very last bin of h2new is missed on both x and y axis
    # one possibility is to assign the value of the last filled bin
    # let's do it
    for ix in range(1,1+h2new.GetNbinsX()):
        for iy in range(1,1+h2new.GetNbinsY()):
            if (ix == h2new.GetNbinsX() and iy == h2new.GetNbinsY()):
                h2new.SetBinContent(ix,iy,h2new.GetBinContent(ix-1, iy-1))
            if (iy == h2new.GetNbinsY()):
                h2new.SetBinContent(ix,iy,h2new.GetBinContent(ix, iy-1))
            if (ix == h2new.GetNbinsX()):
                h2new.SetBinContent(ix,iy,h2new.GetBinContent(ix-1, iy))
    # this will be the histogram to be saved as output
    

    # now I test the TGraph2D constructor which uses the TH2 as input, but I add more points along x
    histcopy = copy.deepcopy(hist2d)
    histcopy.SetName(histcopy.GetName()+'_smoothedByGraph_Constructor_moreBinsX')
    graph2d_v2 = ROOT.TGraph2D(histcopy)  
    xbinsize = 0.025
    graph2d_v2.SetNpx ( int((graph2d_v2.GetXmax() - graph2d_v2.GetXmin())/xbinsize) )    # note that the graph2d_v2 borders have already changed with respect to the input
    #print "%.3f    %.3f" % (graph2d_v2.GetXmin(),graph2d_v2.GetXmax())
    h2smooth = graph2d_v2.GetHistogram()  # retrieve histogram, will have more bins along x than input
    ###################
            

    # let's draw some histograms to see how they look like
    xAxisTitle = hist2d.GetXaxis().GetTitle()
    yAxisTitle = hist2d.GetYaxis().GetTitle()
    zAxisTitle = hist2d.GetZaxis().GetTitle() + "::{minz:.3f},{maxz:.3f}".format(minz=minz,maxz=maxz)

    adjustSettings_CMS_lumi()
    canvas2D = ROOT.TCanvas("canvas","",800,700)
    drawCorrelationPlot(hist2d,xAxisTitle,yAxisTitle,zAxisTitle,
                        hist2d.GetName(),"",outdir,0,0,False,False,False,1,palette=55,passCanvas=canvas2D)
    drawCorrelationPlot(graphFrom_h2new,xAxisTitle,yAxisTitle,zAxisTitle,
                        graphFrom_h2new.GetName(),"",outdir,0,0,False,False,False,1,palette=55,passCanvas=canvas2D)
    drawCorrelationPlot(h2new,xAxisTitle,yAxisTitle,zAxisTitle,
                        h2new.GetName(),"",outdir,0,0,False,False,False,1,palette=55,passCanvas=canvas2D)
    drawCorrelationPlot(h2smooth,xAxisTitle,yAxisTitle,zAxisTitle,
                        h2smooth.GetName(),"",outdir,0,0,False,False,False,1,palette=55,passCanvas=canvas2D)
    drawCorrelationPlot(h2HandSmooth,xAxisTitle,yAxisTitle,zAxisTitle,
                        h2HandSmooth.GetName(),"",outdir,0,0,False,False,False,1,palette=55,passCanvas=canvas2D)



    # create output, let's just save what we really need
    outfile = ROOT.TFile(outfileName, 'recreate')    
    outfile.cd()
    #graphFrom_h2new.Write()
    h2new.Write()
    hist2d.Write()
    #h2smooth.Write()
    h2HandSmooth.Write()
    outfile.Close()

