#!/usr/bin/env python
# USAGE: python w-helicity-13TeV/testRolling.py cards/XXX el -o plots/fit/templates2D
# el is for electrons, mu for muons

import ROOT, os, re
from array import array
from CMGTools.TTHAnalysis.plotter.histoWithNuisances import *
from CMGTools.WMass.plotter.mcPlots import doShadedUncertainty

import utilities
utilities = utilities.util()

def getbinning(splitline):
    bins = splitline[5]
    if '*' in bins:
        etabins = list( float(i) for i in bins.replace(' ','').split('*')[0].replace('\'[','').replace(']','').split(',') )
        ptbins  = list( float(i) for i in bins.replace(' ','').split('*')[1].replace('[','').replace(']\'','').split(',') )
        nbinseta = len(etabins)-1
        nbinspt  = len( ptbins)-1
        binning = [nbinseta, etabins, nbinspt, ptbins]
    else:
        bins = bins.replace('\'','')
        nbinseta = int( bins.split(',')[0] )
        nbinspt  = int( bins.split(',')[3] )
        etamin   = float( bins.split(',')[1] )
        etamax   = float( bins.split(',')[2] )
        ptmin    = float( bins.split(',')[4] )
        ptmax    = float( bins.split(',')[5] )
    return binning

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadRightMargin(0.13)

def roll1Dto2D(h1d, histo):  #,h2dname):#,plotfile,options):
    for i in xrange(1,h1d.GetNbinsX()+1):
        xbin = i % histo.GetNbinsX()
        if not xbin: xbin = xbin+histo.GetNbinsX()
        ybin = i / histo.GetNbinsX() + (1 if i%histo.GetNbinsX() else 0)
        val = h1d.GetBinContent(i)
        histo.SetBinContent(xbin,ybin,h1d.GetBinContent(i))
    return histo

def unroll2Dto1D(h):
    nbins = h.GetNbinsX() * h.GetNbinsY()
    goodname = h.GetName()
    h.SetName(goodname+"_oldbinning")
    newh = ROOT.TH1D(goodname,h.GetTitle(),nbins,0.5,nbins+0.5)
    newh.Sumw2()
    if 'TH2' not in h.ClassName(): raise RuntimeError, "Calling rebin2Dto1D on something that is not TH2"
    for i in xrange(h.GetNbinsX()):
        for j in xrange(h.GetNbinsY()):
            bin = 1 + i + j*h.GetNbinsX()
            newh.SetBinContent(bin,h.GetBinContent(i+1,j+1))
            newh.SetBinError(bin,h.GetBinError(i+1,j+1))
    for bin in range(1,nbins+1):
        if newh.GetBinContent(bin)<0:
            print 'Warning: cropping to zero bin %d in %s (was %f)'%(bin,newh.GetName(),newh.GetBinContent(bin))
            newh.SetBinContent(bin,0)
    newh.SetLineWidth(h.GetLineWidth())
    newh.SetLineStyle(h.GetLineStyle())
    newh.SetLineColor(h.GetLineColor())
    return newh

def dressed2D(h1d,binning,name,title=''):
    if len(binning) == 4:
        n1 = binning[0]; bins1 = array('d', binning[1])
        n2 = binning[2]; bins2 = array('d', binning[3])
        h2_1 = ROOT.TH2F(name, title, n1, bins1, n2, bins2 )
    else:
        n1 = binning[0]; min1 = binning[1]; max1 = binning[2]
        n2 = binning[3]; min2 = binning[4]; max2 = binning[5]
        h2_1 = ROOT.TH2F(name, title, n1, min1, max1, n2, min2, max2)
    #h2_backrolled_1 = roll1Dto2D(h1_1, h2_1 )
    h2_backrolled_1 = roll1Dto2D(h1d, h2_1 )
    h2_backrolled_1 .GetXaxis().SetTitle('lepton #eta')
    h2_backrolled_1 .GetYaxis().SetTitle('lepton p_{T} (GeV)')
    h2_backrolled_1 .GetZaxis().SetRangeUser(0.01*h2_backrolled_1.GetMaximum(),1.1*h2_backrolled_1.GetMaximum())
    return h2_backrolled_1

def doRatioHists(data,total,maxRange,fixRange=False,ylabel="Data/pred.",yndiv=505,doWide=False,showStatTotLegend=False,textSize=0.035):
    ratio = data.Clone("data_div"); 
    ratio.Divide(total)

    unity = total.Clone("sim_div");
    
    rmin, rmax =  1,1
    for b in xrange(1,unity.GetNbinsX()+1):
        e,n = unity.GetBinError(b), unity.GetBinContent(b)
        unity.SetBinContent(b, 1 if n > 0 else 0)
        unity.SetBinError(b, e/n if n > 0 else 0)
        rmin = min([ rmin, 1-2*e/n if n > 0 else 1])
        rmax = max([ rmax, 1+2*e/n if n > 0 else 1])
    for b in xrange(1,unity.GetNbinsX()+1):
        if ratio.GetBinContent(b) == 0: continue
        rmin = min([ rmin, ratio.GetBinContent(b) - 2*ratio.GetBinError(b) ]) 
        rmax = max([ rmax, ratio.GetBinContent(b) + 2*ratio.GetBinError(b) ])  
    if rmin < maxRange[0] or fixRange: rmin = maxRange[0]; 
    if rmax > maxRange[1] or fixRange: rmax = maxRange[1];
    if (rmax > 3 and rmax <= 3.4): rmax = 3.4
    if (rmax > 2 and rmax <= 2.4): rmax = 2.4
    unity.SetFillStyle(1001);
    unity.SetFillColor(ROOT.kCyan);
    unity.SetMarkerStyle(1);
    unity.SetMarkerColor(ROOT.kCyan);
    ROOT.gStyle.SetErrorX(0.5);
    unity.Draw("E2");
    unity.GetYaxis().SetRangeUser(rmin,rmax);
    unity.GetXaxis().SetTitleFont(42)
    unity.GetXaxis().SetTitleSize(0.14)
    unity.GetXaxis().SetTitleOffset(0.9)
    unity.GetXaxis().SetLabelFont(42)
    unity.GetXaxis().SetLabelSize(0.1)
    unity.GetXaxis().SetLabelOffset(0.007)
    unity.GetYaxis().SetNdivisions(505)
    unity.GetYaxis().SetTitleFont(42)
    unity.GetYaxis().SetTitleSize(0.14)
    offset = 0.32 if doWide else 0.62
    unity.GetYaxis().SetTitleOffset(offset)
    unity.GetYaxis().SetLabelFont(42)
    unity.GetYaxis().SetLabelSize(0.11)
    unity.GetYaxis().SetLabelOffset(0.007)
    unity.GetYaxis().SetDecimals(True) 
    unity.GetYaxis().SetTitle(ylabel)
    total.GetXaxis().SetLabelOffset(999) ## send them away
    total.GetXaxis().SetTitleOffset(999) ## in outer space
    total.GetYaxis().SetTitleSize(0.06)
    total.GetYaxis().SetTitleOffset(0.75 if doWide else 1.48)
    total.GetYaxis().SetLabelSize(0.05)
    total.GetYaxis().SetLabelOffset(0.007)
    #$ROOT.gStyle.SetErrorX(0.0);
    line = ROOT.TLine(unity.GetXaxis().GetXmin(),1,unity.GetXaxis().GetXmax(),1)
    line.SetLineWidth(2);
    line.SetLineColor(58);
    line.Draw("L")
    ratio.Draw("E SAME" if ratio.ClassName() != "TGraphAsymmErrors" else "PZ SAME");
    leg1 = ROOT.TLegend(0.45, 0.8, 0.7, 0.9)
    leg1.SetFillColor(0)
    leg1.SetShadowColor(0)
    leg1.SetLineColor(0)
    leg1.SetTextFont(42)
    leg1.SetTextSize(0.035*0.7/0.3)
    leg1.AddEntry(unity, "total unc.", "F")
    leg1.Draw()

    return (ratio, unity, line)

def getNormSysts(channel):
    systs = {}
    sysfile = "{cmsswbase}/src/CMGTools/WMass/python/plotter/w-helicity-13TeV/wmass_{ch}/systsEnv.txt".format(cmsswbase=os.environ['CMSSW_BASE'],ch='e' if channel=='el' else 'mu')
    for line in open(sysfile, 'r'):
        if re.match("\s*#.*", line): continue
        line = re.sub("#.*","",line).strip()
        if len(line) == 0: continue
        field = [f.strip() for f in line.split(':')]
        if len(field) == 4 or field[4] == "lnN":
            (name, procmap, binmap, amount) = field[:4]
            if name not in systs: systs[name] = []
            systs[name].append((re.compile(procmap+"$"),amount))
    return systs

ROOT.gROOT.SetBatch()

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] shapesdir channel")
    parser.add_option('-o','--outdir', dest='outdir', default='.', type='string', help='output directory to save the matrix')
    parser.add_option(     '--noplot', dest="noplot", default=False, action='store_true', help="Do not plot templates (but you can still save them in a root file with option -s)");
    parser.add_option('-s','--save', dest='outfile_templates', default='templates_2D', type='string', help='pass name of output file to save 2D histograms (charge is automatically appended before extension). No need to specify extension, .root is automatically addedx')
    parser.add_option(     '--fitres', dest='fitresult', default=None, type='string', help='if given, uses the contents of fitresults to scale the templates to post-fit result')
    groupJobs=5 # used in make_helicity_cards.py

    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.print_usage()
        quit()
    channel = args[1]

    ybinfile = args[0]+'/binningYW.txt'
    ybinfile = open(ybinfile, 'r')
    ybins = eval(ybinfile.read())
    ybinfile.close()
    
    if options.fitresult:
        print "Scaling the templates to the post-fit results in: ",options.fitresult
        valuesAndErrors = utilities.getFromHessian(options.fitresult)
        allNuisances = utilities.getFromHessian(options.fitresult,keepGen=True)

    outname = options.outdir
    if not os.path.exists(outname):
        os.system("mkdir -p "+outname)
        if os.path.exists("/afs/cern.ch"): os.system("cp /afs/cern.ch/user/g/gpetrucc/php/index.php "+outname)

    for charge in ['plus','minus']:
        shapesfile = "{indir}/W{flav}_{ch}_shapes.root".format(indir=args[0],flav=channel,ch=charge)
        infile = ROOT.TFile(shapesfile, 'read')
        print ""
        print "==> RUNNING FOR CHARGE ",charge

        outfile_templates = options.outfile_templates
        if outfile_templates.endswith(".root"):
            outfile_templates = outfile_templates.replace(".root","_%s.root" % str(charge))
        else:
            outfile_templates = outfile_templates + "_" + str(charge) + ".root"

        full_outfileName = outname + "/" + outfile_templates
        outfile = ROOT.TFile(full_outfileName, 'recreate')
        print "Will save 2D templates in file --> " + full_outfileName

        systs = getNormSysts(channel)

        # doing signal
        total_sig = {}
        canv = ROOT.TCanvas()
        for pol in ['right', 'left', 'long']:
            print "\tPOLARIZATION ",pol
            chpol = '{ch}_{pol}'.format(ch=charge,pol=pol)
            nYbins=len(ybins[chpol])-1
            #for ybin in range(1):
            for ybin in range(nYbins): 

                group = ybin/groupJobs + 1
                jobind = min(groupJobs * group - 1,nYbins-1)
                line = ybin%groupJobs
                

                jobsdir = args[0]+'/jobs/'
                jobfile_name = 'W{ch}_{pol}_{flav}_Ybin_{b}.sh'.format(ch=charge,pol=pol,flav=channel,b=jobind)
                tmp_jobfile = open(jobsdir+jobfile_name, 'r')
                lineno = (-groupJobs+line)*2 + 1 # white lines
                if ybin==nYbins-1: lineno = -1 # not general hack!!!
                tmp_line = tmp_jobfile.readlines()[lineno].split()
                ymin = list(i for i in tmp_line if '(genw_y)>' in i)[0].replace('\'','').split('>')[-1]
                ymax = list(i for i in tmp_line if '(genw_y)<' in i)[0].replace('\'','').split('<')[-1]
                
                binning = getbinning(tmp_line)

                chs = '+' if charge == 'plus' else '-' 
                h1_1 = infile.Get('x_W{ch}_{pol}_W{ch}_{pol}_{flav}_Ybin_{ybin}'.format(ch=charge,pol=pol,flav=channel,ybin=ybin))
                name2D = 'W{ch}_{pol}_W{ch}_{pol}_{flav}_Ybin_{ybin}'.format(ch=charge,pol=pol,flav=channel,ybin=ybin)
                title2D = 'W{ch} {pol} : |Y_{{W}}| #in [{ymin},{ymax}]'.format(ymin=ymin,ymax=ymax,pol=pol,ybin=ybin,ch=chs)
                h2_backrolled_1 = dressed2D(h1_1,binning,name2D,title2D)
                if options.fitresult:
                    scale = valuesAndErrors[name2D+'_mu']
                    print "scaling for {h} = {val:.3f} +/- {err:.3f} ".format(h=name2D,val=scale[0],err=scale[1]-scale[0])
                    h2_backrolled_1.Scale(scale[0])
                if ybin==0:
                    total_sig["W"+chpol] = h2_backrolled_1.Clone('W{ch}_{pol}_{flav}'.format(ch=charge,pol=pol,flav=channel))
                else:
                    total_sig["W"+chpol].Add(h2_backrolled_1)
                total_sig["W"+chpol].SetDirectory(None)
                h2_backrolled_1.Draw('colz')
                h2_backrolled_1.Write(name2D)
                if not options.noplot:
                    for ext in ['pdf', 'png']:
                        canv.SaveAs('{odir}/W{ch}_{pol}_W{ch}_{flav}_Ybin_{ybin}_PFMT40_absY.{ext}'.format(odir=outname,ch=charge,flav=channel,pol=pol,ybin=ybin,ext=ext))
            total_sig["W"+chpol].Draw('colz')
            total_sig["W"+chpol].Write(total_sig["W"+chpol].GetName())
            if options.fitresult: # this is wrong, not assuming correlations. FIXME when we have the full info in the fit. Assume 100% correlation of syst among all hel bins
                totalsyst2 = 0 
                for name in systs.keys():
                    for entry in systs[name]:
                        procmap,amount = entry[:2]
                        if re.match(procmap, 'W'):
                            kappa = float(amount)
                            totalsyst2 += abs(allNuisances[name][1]-allNuisances[name][0])*(kappa-1)**2
                totalsyst = sqrt(totalsyst2)
                for xb in xrange(1,total_sig["W"+chpol].GetNbinsX()+1):
                    for yb in xrange(1,total_sig["W"+chpol].GetNbinsY()+1):
                        total_sig["W"+chpol].SetBinError(xb,yb, hypot(total_sig["W"+chpol].GetBinError(xb,yb), totalsyst*total_sig["W"+chpol].GetBinContent(xb,yb)))

            if not options.noplot:
                for ext in ['pdf', 'png']:
                    canv.SaveAs('{odir}/W{ch}_{pol}_{flav}_TOTALSIG_PFMT40_absY.{ext}'.format(odir=outname,ch=charge,flav=channel,pol=pol,ext=ext))


        # do backgrounds now
        procs=["Flips","Z","Top","DiBosons","TauDecaysW","data_fakes","W{ch}_long".format(ch=charge),"data_obs"]
        titles=["charge flips","DY","Top","di-bosons","W#to#tau#nu","QCD","W{ch}_long".format(ch=charge),"data"]
        bkg_and_data = {}
        for i,p in enumerate(procs):
            h1_1 = infile.Get('x_{p}'.format(p=p))
            if not h1_1: continue # muons don't have Flips components
            h2_backrolled_1 = dressed2D(h1_1,binning,p,titles[i])
            # postfit mu not implemented for bkgs, only apply post-fit systematic uncertainty, not changing the central value
            if options.fitresult and p!='data_obs':
                variation = 0
                totalsyst2 = 0 # this is wrong, not assuming correlations. FIXME when we have the full info in the fit
                for name in systs.keys():
                    for entry in systs[name]:
                        procmap,amount = entry[:2]
                        if re.match(procmap, p): 
                            kappa = float(amount)
                            variation += allNuisances[name][0]*(kappa-1)
                            totalsyst2 += abs(allNuisances[name][1]-allNuisances[name][0])*(kappa-1)**2
                h2_backrolled_1.Scale(1+variation)
                totalsyst = sqrt(totalsyst2)
                print "scaling for {h} = {val:.3f} +/- {err:.3f} ".format(h=p,val=1+variation,err=totalsyst)
                for xb in xrange(1,h2_backrolled_1.GetNbinsX()+1):
                    for yb in xrange(1,h2_backrolled_1.GetNbinsY()+1):
                        h2_backrolled_1.SetBinError(xb,yb, hypot(h2_backrolled_1.GetBinError(xb,yb), totalsyst*h2_backrolled_1.GetBinContent(xb,yb)))
            bkg_and_data[p] = h2_backrolled_1
            bkg_and_data[p].SetDirectory(None)
            h2_backrolled_1.Draw('colz')
            h2_backrolled_1.Write(str(p))
            if not options.noplot:
                for ext in ['pdf', 'png']:
                    canv.SaveAs('{odir}/{proc}_{ch}_{flav}_PFMT40_absY.{ext}'.format(odir=outname,proc=p,ch=charge,flav=channel,ext=ext))
            
        outfile.Close()
    

        # now draw the 1D projections
        if options.fitresult:
            all_procs = total_sig.copy()
            all_procs.update(bkg_and_data)
     
            colors = {'Wplus_long' : ROOT.kGray+1,   'Wplus_left' : ROOT.kBlue-1,   'Wplus_right' : ROOT.kGreen+1,
                      'Wminus_long': ROOT.kYellow+1, 'Wminus_left': ROOT.kViolet-1, 'Wminus_right': ROOT.kAzure+1,
                      'Top'        : ROOT.kGreen+2,  'DiBosons'   : ROOT.kViolet+2, 'TauDecaysW'  : ROOT.kPink,       
                      'Z'          : ROOT.kAzure+2,  'Flips'      : ROOT.kGray+1,   'data_fakes'  : ROOT.kGray+2 }
                              
            for projection in ['X','Y']:
                hdata = all_procs['data_obs'].ProjectionX("x_total",0,-1,"e") if projection=='X' else all_procs['data_obs'].ProjectionY("y_total",0,-1,"e")
                htot = hdata.Clone('x_data_obs'); htot.Reset(); htot.Sumw2()
                stack = ROOT.THStack("x_stack","")
                
                legWidth=0.18; textSize=0.035
                (x1,y1,x2,y2) = (.75-legWidth, .60, .90, .91)
                leg = ROOT.TLegend(x1,y1,x2,y2)
                leg.SetFillColor(0)
                leg.SetFillColorAlpha(0,0.6)
                leg.SetShadowColor(0)
                leg.SetLineColor(0)
                leg.SetBorderSize(0)
                leg.SetTextFont(42)
                leg.SetTextSize(textSize)
     
                for proc in all_procs:
                    if proc=='data_obs': continue
                    proj1d = all_procs[proc].ProjectionX(all_procs[proc].GetName()+"_px",0,-1,"e") if  projection=='X' else all_procs[proc].ProjectionY(all_procs[proc].GetName()+"_py",0,-1,"e")
                    proj1d.SetFillColor(colors[proc])
                    stack.Add(proj1d)
                    htot.Add(proj1d)                    
                    leg.AddEntry(proj1d,proc,'F')
                
                doRatio=True
                htot.GetYaxis().SetRangeUser(0, 1.8*max(htot.GetMaximum(), hdata.GetMaximum()))
             
         
                ## Prepare split screen
                c1 = ROOT.TCanvas("c1", "c1", 600, 750); c1.Draw()
                c1.SetWindowSize(600 + (600 - c1.GetWw()), (750 + (750 - c1.GetWh())));
                p1 = ROOT.TPad("pad1","pad1",0,0.29,1,0.99);
                p1.SetBottomMargin(0.03);
                p1.Draw();
                p2 = ROOT.TPad("pad2","pad2",0,0,1,0.31);
                p2.SetTopMargin(0);
                p2.SetBottomMargin(0.3);
                p2.SetFillStyle(0);
                p2.Draw();
                p1.cd();
                ## Draw absolute prediction in top frame
                htot.Draw("HIST")
                #htot.SetLabelOffset(9999.0);
                #htot.SetTitleOffset(9999.0);
                stack.Draw("HIST F SAME")
                hdata.SetMarkerColor(ROOT.kBlack)
                hdata.SetMarkerStyle(ROOT.kFullCircle)
                hdata.Draw("E SAME")
                htot.Draw("AXIS SAME")
                totalError = doShadedUncertainty(htot)            
                leg.Draw()
         
                p2.cd()
                rdata,rnorm,rline = doRatioHists(hdata, htot, maxRange=[0.90,1.10], fixRange=True)
                c1.cd()
                for ext in ['pdf', 'png']:
                    c1.SaveAs('{odir}/projection{proj}_{ch}_{flav}_PFMT40_absY.{ext}'.format(odir=outname,proj=projection,ch=charge,flav=channel,ext=ext))
        
