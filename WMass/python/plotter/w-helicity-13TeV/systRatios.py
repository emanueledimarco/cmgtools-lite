#!/usr/bin/env python
# USAGE: 
# PDFs: python systRatios.py -o plots -s 'pdf' cards_el el
# OTHER SYSTEMATICS: python systRatios.py -o plots -s 'muR,muF,muRmuF,alphaS,wptSlope' cards_el el

import ROOT, os, copy, re
from array import array
from testRolling import getbinning
from rollingFunctions import *

ROOT.gROOT.SetBatch()
##ROOT.gStyle.SetPalette(55)
ROOT.gStyle.SetPalette(ROOT.kTemperatureMap)
ROOT.gErrorIgnoreLevel = 100

canv = ROOT.TCanvas()

def plotUnrolledRatios(ratios2d,outdir,name):
    ROOT.gStyle.SetPadLeftMargin(0.13)
    ROOT.gStyle.SetPadRightMargin(0.07)
    ROOT.gStyle.SetPadBottomMargin(0.3);

    plotformat = (2400,600)
    c1 = ROOT.TCanvas("c1", "c1", plotformat[0], plotformat[1]); c1.Draw()
    c1.SetWindowSize(plotformat[0] + (plotformat[0] - c1.GetWw()), (plotformat[1] + (plotformat[1] - c1.GetWh())));

    ratios,rnorm,rline = doUnrolledRatios(ratios2d)

    lat = ROOT.TLatex()
    lat.SetNDC(); lat.SetTextFont(42)
    lat.DrawLatex(0.15, 0.92, '#bf{CMS} #it{Preliminary}')
    lat.DrawLatex(0.85, 0.92, '36 fb^{-1} (13 TeV)')
    for ext in ['pdf', 'png']:
        c1.SaveAs('{odir}/{name}_unrolled.{ext}'.format(odir=outdir,name=name,ext=ext))

def doUnrolledRatios(ratios2d):
    
    ratios = [unroll2Dto1D(r2,cropNegativeBins=False) for k,r2 in ratios2d.iteritems() if "TH2" in r2.ClassName()]

    unity = ratios[0].Clone("unity")
    rmax = 0

    for b in xrange(1,unity.GetNbinsX()+1):
        unity.SetBinContent(b, 0); unity.SetBinError(b, 0)
        for ratio in ratios:
            r = abs(ratio.GetBinContent(b))
            unity.SetBinError(b,max([r,abs(unity.GetBinError(b))]))
        rmax = max([rmax, unity.GetBinError(b)])
        rmin = -rmax

    unity.SetFillStyle(1001);
    unity.SetFillColor(ROOT.kCyan);
    unity.SetMarkerStyle(1);
    unity.SetMarkerColor(ROOT.kCyan);
    ROOT.gStyle.SetErrorX(0.5);
    unity.Draw("E2");
    unity.GetYaxis().SetRangeUser(1.2*rmin,1.2*rmax);
    unity.GetXaxis().SetTitleFont(42)
    unity.GetXaxis().SetTitleSize(0.14)
    unity.GetXaxis().SetTitleOffset(0.9)
    unity.GetXaxis().SetLabelFont(42)
    unity.GetXaxis().SetLabelSize(0.1)
    unity.GetXaxis().SetLabelOffset(0.007)
    unity.GetYaxis().SetNdivisions(505)
    unity.GetYaxis().SetTitleFont(42)
    unity.GetYaxis().SetTitleSize(0.14)
    unity.GetYaxis().SetLabelFont(42)
    unity.GetYaxis().SetLabelSize(0.11)
    unity.GetYaxis().SetLabelOffset(0.01)
    unity.GetYaxis().SetDecimals(True) 
    unity.GetYaxis().SetTitle('Syst./Nom.')
    unity.GetXaxis().SetTitle('unrolled lepton (#eta,p_{T}) bin')
    unity.GetYaxis().SetTitleOffset(0.40)
    line = ROOT.TLine(unity.GetXaxis().GetXmin(),1,unity.GetXaxis().GetXmax(),1)
    line.SetLineWidth(2);
    line.SetLineColor(58);
    line.Draw("L")
    for ir,ratio in enumerate(ratios):
        ratio.SetLineColor(ROOT.kRed + 2*ir)
        ratio.Draw("HIST SAME" if ratio.ClassName() != "TGraphAsymmErrors" else "PZ SAME");
    leg1 = ROOT.TLegend(0.45, 0.8, 0.7, 0.9)
    leg1.SetFillColor(0)
    leg1.SetShadowColor(0)
    leg1.SetLineColor(0)
    leg1.SetTextFont(42)
    leg1.SetTextSize(0.035*0.7/0.3)
    leg1.AddEntry(unity, "envelope unc.", "F")
    leg1.Draw()

    return (ratios, unity, line)


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] shapesdir channel")
    parser.add_option('-o','--outdir', dest='outdir', default='.', type='string', help='outdput directory to save the matrix')
    parser.add_option('-s','--syst', dest='systematics', default=None, type='string', help='systematics of which drawing the ratio (comma-separated list of)')
    parser.add_option(     '--no2Dplot', dest="no2Dplot", default=False, action='store_true', help="Do not plot templates (but you can still save them in a root file with option -s)");
    parser.add_option('-u','--unrolled', dest='unrolled', default=False, action='store_true', help='make the 1D ratios on the unrolled plot for all the listed systematics')
    (options, args) = parser.parse_args()
    channel = args[1]

    systs = [] if not options.systematics else options.systematics.split(',')
    print "Will consider these possible systematics: ",systs

    outname = options.outdir
    if not os.path.exists(outname):
        os.system("mkdir -p "+outname)
        if os.path.exists("/afs/cern.ch"): os.system("cp /afs/cern.ch/user/g/gpetrucc/php/index.php "+outname)

    nY = {}
    errors = []
    for charge in ['minus','plus']:
        print "===> RUNNING CHARGE = ",charge
        chs = '+' if charge == 'plus' else '-'
        shapesfile = "{indir}/W{flav}_{ch}_shapes.root".format(indir=args[0],flav=channel,ch=charge)
        infile = ROOT.TFile(shapesfile, 'read')
        keylist = infile.GetListOfKeys()
        siglist = list( i.GetName() for i in keylist if 'Ybin_' in i.GetName() )
        fulllist = list(i.GetName() for i in keylist)
        nY[charge+'_left']  = max( int(i.split('_')[-2]) for i in siglist if 'pdf' in i and 'left'  in i)
        nY[charge+'_right'] = max( int(i.split('_')[-2]) for i in siglist if 'pdf' in i and 'right' in i)
        nY[charge+'_long'] = max( int(i.split('_')[-2]) for i in siglist if 'pdf' in i and 'long' in i)
        nPDF = max( int(i.split('_')[-1].replace('pdf','').replace('Down','').replace('Up','')) for i in siglist if 'pdf' in i)

        bkgs = ['data_fakes','Flips','DiBosons','Top','TauDecaysW','Z']
        #bkgs = []#['data_fakes'] # other than W_{L,R}
        wlr = ['W{ch}_{p}_W{ch}_{p}_{flav}_Ybin_0'.format(ch=charge,p=pol,flav=channel) for pol in ['left','right', 'long'] ]
        procs=wlr+bkgs

        binninPtEtaFile = open(args[0]+'/binningPtEta.txt','r')
        bins = binninPtEtaFile.readlines()[1].split()[1]
        ## hack. easier
        etabins = list( float(i) for i in bins.replace(' ','').split('*')[0].replace('[','').replace(']','').split(',') )
        ptbins  = list( float(i) for i in bins.replace(' ','').split('*')[1].replace('[','').replace(']','').split(',') )
        nbinseta = len(etabins)-1
        nbinspt  = len( ptbins)-1
        binning = [nbinseta, etabins, nbinspt, ptbins]
        ## jobsdir = args[0]+'/jobs/'
        ## jobfile_name = 'W{ch}_left_{flav}_Ybin_4.sh'.format(ch=charge,flav=channel)
        ## tmp_jobfile = open(jobsdir+jobfile_name, 'r')
        ## tmp_line = tmp_jobfile.readlines()[-1].replace(', ',',').split()
        ## binning = getbinning(tmp_line)

        ratios={}
        for proc in procs:
            print "Making syst plots for process : ",proc," ..."
            pol = 'none'
            # central template
            if 'W{ch}'.format(ch=charge) in proc:
                pol = proc.split('_')[1]
                cp = charge+'_'+pol
                histo_central = infile.Get('x_W{ch}_{pol}_W{ch}_{pol}_{flav}_Ybin_0'.format(ch=charge,pol=pol,flav=channel))
                for iy in xrange(1,nY[cp]+1):
                    histo_central.Add(infile.Get('x_W{ch}_{pol}_W{ch}_{pol}_{flav}_Ybin_{i}'.format(ch=charge,pol=pol,flav=channel,i=iy)))
            else:
                histo_central = infile.Get('x_%s'%proc)
            # systematic templates
            for syst in systs:
                if 'pdf' in syst: # generic pdf means looping over all 60 Hessian variations
                    if not re.match('W{ch}|Z'.format(ch=charge),proc): continue # only W and Z have PDF variations
                    for ip in xrange(1,nPDF+1):
                        if 'W{ch}'.format(ch=charge) in proc:
                            histo_pdfi = infile.Get('x_W{ch}_{pol}_W{ch}_{pol}_{flav}_Ybin_0_pdf{ip}Up'.format(ch=charge,pol=pol,flav=channel,ip=ip))
                            for iy in xrange(1,nY[cp]+1):
                                histo_pdfi_iy = infile.Get('x_W{ch}_{pol}_W{ch}_{pol}_{flav}_Ybin_{iy}_pdf{ip}Up'.format(ch=charge,pol=pol,flav=channel,iy=iy,ip=ip))
                                if histo_pdfi_iy: histo_pdfi.Add(histo_pdfi_iy)
                            title2D = 'W{ch} {pol} : pdf {ip}'.format(ip=ip,pol=pol,ch=chs)
                            key = 'syst_W{ch}_{pol}_W{ch}_{pol}_{flav}_pdf{ip}'.format(ch=charge,pol=pol,flav=channel,ip=ip)
                        else:
                            histo_pdfi = infile.Get('x_{proc}_pdf{ip}Up'.format(proc=proc,ip=ip))
                            title2D = 'Z : pdf {ip}'.format(ip=ip)
                            key = 'syst_{proc}_{ch}_{flav}_pdf{ip}'.format(proc=proc,ch=charge,flav=channel,ip=ip)
                        if not histo_central.GetEntries() == histo_pdfi.GetEntries():
                            print 'WARNING/ERROR: THE CENTRAL HISTO AND PDF HISTO DO NOT HAVE THE SAME NUMBER OF ENTRIES'
                            print 'this just happened for {ch} and {pol} and pdf {syst}'.format(ch=charge, pol=pol, syst=ip)
                            errors.append('{ch}_{pol}_pdf{syst}'.format(ch=charge, pol=pol, syst=ip))
                        ratio_pdfi = copy.deepcopy(histo_pdfi)
                        ratio_pdfi.Divide(histo_central)
                        for ib in xrange(1, ratio_pdfi.GetNbinsX()+1):
                            ##ratio_pdfi.SetBinContent(ib, abs(1.-ratio_pdfi.GetBinContent(ib) if histo_central.GetBinContent(ib)>0 else 0))
                            ratio_pdfi.SetBinContent(ib, ratio_pdfi.GetBinContent(ib)-1. if histo_central.GetBinContent(ib)>0 else 0)
                        h2_backrolled_1 = dressed2D(ratio_pdfi,binning,title2D)
                        h2_backrolled_1.GetZaxis().SetRangeUser(-0.02,0.02)
                        ratios[key] = h2_backrolled_1
                else:
                    histo_syst = None
                    fullsyst = syst if any(sfx in syst for sfx in ['Up','Down']) else syst+"Up"
                    if 'W{ch}'.format(ch=charge) in proc:
                        for pol in [proc.split('_')[1]]:#'right', 'left']:
                            cp = charge+'_'+pol
                            hname = 'x_W{ch}_{pol}_W{ch}_{pol}_{flav}_Ybin_0_{syst}'.format(ch=charge,pol=pol,flav=channel,syst=fullsyst)
                            histo_syst = infile.Get(hname) if hname in keylist else None
                            for iy in xrange(1,nY[cp]+1):
                                hname_iy = 'x_W{ch}_{pol}_W{ch}_{pol}_{flav}_Ybin_{iy}_{syst}'.format(ch=charge,pol=pol,flav=channel,iy=iy,syst=fullsyst)
                                histo_syst_iy = infile.Get(hname_iy) if hname in keylist else None
                                if histo_syst_iy: histo_syst.Add(histo_syst_iy)
                            title2D = 'W{ch} {pol} : variation={syst}'.format(pol=pol,ch=chs,syst=syst)
                            key = 'syst_W{ch}_{pol}_W{ch}_{pol}_{flav}_{syst}'.format(ch=charge,pol=pol,flav=channel,syst=syst)
                    else:
                        hname = 'x_{proc}_{syst}'.format(proc=proc,syst=fullsyst)
                        print "Lookiig for shape ",hname
                        if hname in fulllist:
                            histo_syst = infile.Get(hname)
                        title2D = '{proc} : variation={syst}'.format(proc=proc,syst=syst)
                        key = 'syst_{proc}_{ch}_{flav}_{syst}'.format(proc=proc,ch=charge,flav=channel,syst=syst)
                    if histo_syst:
                        mydude = copy.deepcopy(histo_syst)
                        myvar  = copy.deepcopy(histo_central)
                        ratio = copy.deepcopy(histo_syst)
                        ratio.Divide(histo_central)
                        for ib in xrange(1, ratio.GetNbinsX()+1):
                            ##ratio.SetBinContent(ib, abs(1.-ratio.GetBinContent(ib) if histo_central.GetBinContent(ib)>0 else 0))
                            ratio.SetBinContent(ib, ratio.GetBinContent(ib)-1. if histo_central.GetBinContent(ib)>0 else 0)
                        h2_backrolled_1 = dressed2D(ratio,binning,title2D)
                        hmax = 0.05 if 'muF' in syst else 0.04
                        if 'effstat' in syst: hmax = 0.005
                        h2_backrolled_1.GetZaxis().SetRangeUser(-hmax,hmax)
                        ratios[key] = h2_backrolled_1
                        if not histo_central.GetEntries() == histo_syst.GetEntries():
                            print 'WARNING/ERROR: THE CENTRAL HISTO AND PDF HISTO DO NOT HAVE THE SAME NUMBER OF ENTRIES'
                            print 'this just happened for {ch} and {pol} and systematic {syst}'.format(ch=charge, pol=pol, syst=fullsyst)
                            print 'nentries of central:', histo_central.GetEntries()
                            print 'nentries of syst:   ', histo_syst.GetEntries()
                            errors.append('{ch}_{pol}_{syst}'.format(ch=charge, pol=pol, syst=fullsyst))

        if len(ratios):
            if not options.no2Dplot:
                canv = ROOT.TCanvas()
                for k,r in ratios.iteritems():
                    r.Draw('colz')
                    for ext in ['pdf', 'png']:
                        canv.SaveAs('{odir}/{name}.{ext}'.format(odir=outname,name=k,ext=ext))
     
            if options.unrolled:
                systNames = options.systematics.replace(',','AND').replace('.','').replace('*','').replace('$','').replace('^','').replace('|','').replace('[','').replace(']','')
                plotUnrolledRatios(ratios,outname,'{syst}_{ch}'.format(syst=systNames,ch=charge))


    if len(errors):
        print '=== WARNING === WARNING === WARNING ==='
        print 'ERRORS FOUND IN THESE SYSTEAMTICS'
        for err in errors:
            print err
