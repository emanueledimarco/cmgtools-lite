#!/bin/env python
# USAGE: python plotYW.py --type toys --infile toys_wplus.root -y cards_el/binningYW.txt -C plus -o plots --xsecfiles Wel_plus_shapes_xsec.root [--normxsec]
#
# When run on the W+ W- combined fit it also makes charge asymmetry plot:
# python plotYW.py --type toys --infile toys_wboth.root -y cards_el/binningYW.txt -C plus,minus -o plots --xsecfiles Wel_plus_shapes_xsec.root,Wel_minus_shapes_xsec.root

import ROOT, datetime, array, os, math, re
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")

import utilities
utilities = utilities.util()


class valueClass:
    def __init__(self, name):
        self.name = name

        self.pol = 'left' if 'left' in self.name else 'right' if 'right' in self.name else 'long'
        self.isleft  = self.pol == 'left'
        self.isright = self.pol == 'right'
        self.islong  = self.pol == 'long'

        self.charge = 'plus' if 'plus' in name else 'minus'
        self.ch     = '+' if 'plus' in name else '-'
        if 'asymmetry' in name:
            self.charge = self.ch = ''

        self.color  = ROOT.kBlue-9 if self.isleft else ROOT.kOrange-4 if self.isright else ROOT.kGray+1
        self.colorf = ROOT.kBlue-3 if self.isleft else ROOT.kOrange-3 if self.isright else ROOT.kGray+3

        ## here all the arrays that will contain the values and errors etc.
        self.val       = array.array('f', []); self.ehi       = array.array('f', []); self.elo       = array.array('f', []);
        self.val_fit   = array.array('f', []); self.ehi_fit   = array.array('f', []); self.elo_fit   = array.array('f', []);
        self.relv      = array.array('f', []); self.relhi     = array.array('f', []); self.rello     = array.array('f', []);
        self.relv_fit  = array.array('f', []); self.relhi_fit = array.array('f', []); self.rello_fit = array.array('f', []);
        self.rap       = array.array('f', []); self.rlo       = array.array('f', []); self.rhi       = array.array('f', []);

    def makeGraphs(self):
        if len(self.val):
            self.graph = ROOT.TGraphAsymmErrors(len(self.val), self.rap, self.val, self.rlo, self.rhi, self.elo, self.ehi)
            self.graph.SetName('graph'+self.pol)
        if len(self.relv): 
            self.graph_rel= ROOT.TGraphAsymmErrors(len(self.relv), self.rap, self.relv, self.rlo, self.rhi, self.rello, self.relhi)
            self.graph_rel.SetName('graph'+self.pol+'_rel')
        if len(self.val_fit):
            self.graph_fit = ROOT.TGraphAsymmErrors(len(self.val_fit), self.rap, self.val_fit, self.rlo, self.rhi, self.elo_fit, self.ehi_fit)
            self.graph_fit.SetName('graph'+self.pol+'_fit')
        if len(self.relv_fit):
            self.graph_fit_rel = ROOT.TGraphAsymmErrors(len(self.relv_fit), self.rap, self.relv_fit, self.rlo, self.rhi, self.rello_fit, self.relhi_fit)
            self.graph_fit_rel.SetName('graph'+self.pol+'_fit_rel')
        
        self.graphStyle()
        if len(self.relv) and len(self.relv_fit): self.makeMultiGraphRel()

    def makeMultiGraphRel(self):
        self.mg = ROOT.TMultiGraph()
        self.mg.SetTitle() ## no title 'W^{{{ch}}}: {p}'.format(ch=self.ch,p=self.pol))
        self.mg.Add(self.graph_rel,'P2')
        self.mg.Add(self.graph_fit_rel)

    def graphStyle(self):
        if hasattr(self,'graph'):
            self.graph.SetLineColor(self.color)
            self.graph.SetFillColor(self.color)
            self.graph.SetFillStyle(3002)
        if hasattr(self,'graph_fit'):
            self.graph_fit.SetLineWidth(2)
            self.graph_fit.SetMarkerSize(0.7)
            self.graph_fit.SetMarkerStyle(20)
            self.graph_fit.SetMarkerColor(self.colorf)
            self.graph_fit.SetLineColor(self.colorf)
        if hasattr(self,'graph_rel'):
            self.graph_rel.SetLineWidth(5)
            self.graph_rel.SetLineColor(self.color)
            self.graph_rel.SetFillColor(self.color)
            self.graph_rel.SetFillStyle(3002)
        if hasattr(self,'graph_fit_rel'):
            self.graph_fit_rel.SetLineWidth(2)
            self.graph_fit_rel.SetLineColor(self.colorf)
            self.graph_fit_rel.SetMarkerSize(0.7)
            self.graph_fit_rel.SetMarkerStyle(20)
            self.graph_fit_rel.SetMarkerColor(self.colorf)

def plotValues(values,charge,options):
        c2 = ROOT.TCanvas('foo','', 800, 800)
        c2.GetPad(0).SetTopMargin(0.09)
        c2.GetPad(0).SetBottomMargin(0.15)
        c2.GetPad(0).SetLeftMargin(0.16)
        c2.GetPad(0).SetRightMargin(0.03)

        ch = '+' if charge == 'plus' else '-'
        if charge == 'asymmetry': ch = ''
        date = datetime.date.today().isoformat()
        normstr = 'norm' if (options.normxsec and charge!='asymmetry') else ''

        lat = ROOT.TLatex()
        lat.SetNDC(); lat.SetTextFont(42)
        ## the four graphs exist now. now starting to draw them
        ## ===========================================================
        if sum(hasattr(values[pol],'graph') and hasattr(values[pol],'graph_fit') for pol in ['left','right','long'])==3:
            leg = ROOT.TLegend(0.60, 0.50, 0.90, 0.90)
            leg.SetFillStyle(0)
            leg.SetBorderSize(0)
            leg.AddEntry(values['left'] .graph     , 'W^{{{ch}}}_{{left}} (PDF unc.)'  .format(ch=ch) , 'f')
            leg.AddEntry(values['left'] .graph_fit , 'W^{{{ch}}}_{{left}} (fit)'       .format(ch=ch) , 'pl')
            leg.AddEntry(values['right'].graph     , 'W^{{{ch}}}_{{right}} (PDF unc.)' .format(ch=ch) , 'f')
            leg.AddEntry(values['right'].graph_fit , 'W^{{{ch}}}_{{right}} (fit)'      .format(ch=ch) , 'pl')
            leg.AddEntry(values['long'] .graph     , 'W^{{{ch}}}_{{long}} (PDF unc.)'  .format(ch=ch) , 'f')
            leg.AddEntry(values['long'] .graph_fit , 'W^{{{ch}}}_{{long}} (fit)'       .format(ch=ch) , 'pl')
     
            values['left'].graph.SetTitle('W {ch}: Y_{{W}}'.format(ch=ch))
                
            mg = ROOT.TMultiGraph()
            mg.Add(values['left'] .graph,'P2')
            mg.Add(values['right'].graph,'P2')
            mg.Add(values['long'] .graph,'P2')
            mg.Add(values['left'] .graph_fit)
            mg.Add(values['right'].graph_fit)
            mg.Add(values['long'] .graph_fit)
     
            mg.Draw('Pa')
            mg.GetXaxis().SetRangeUser(0.,6.)
            mg.GetXaxis().SetTitle('|Y_{W}|')
            if options.normxsec: 
                mg.GetYaxis().SetTitle('d#sigma/dy/#sigma_{tot}')
                mg.GetYaxis().SetRangeUser(-0.05,0.8)
            else: 
                mg.GetYaxis().SetTitle('d#sigma/dy (pb)')
                mg.GetYaxis().SetRangeUser(-200,3500)
            mg.GetXaxis().SetTitleSize(0.06)
            mg.GetXaxis().SetLabelSize(0.04)
            mg.GetYaxis().SetTitleSize(0.06)
            mg.GetYaxis().SetLabelSize(0.04)
            mg.GetYaxis().SetTitleOffset(1.2)
     
            leg.Draw('same')
            lat.DrawLatex(0.16, 0.92, '#bf{CMS} #it{Preliminary}')
            lat.DrawLatex(0.65, 0.92, '36 fb^{-1} (13 TeV)')
     
            for ext in ['png', 'pdf']:
                c2.SaveAs('{od}/genAbsY{norm}_pdfs_{ch}{suffix}_{t}.{ext}'.format(od=options.outdir, norm=normstr, ch=charge, suffix=options.suffix, ext=ext,t=options.type))

        ## now make the relative error plot:
        ## ======================================
        if sum(hasattr(values[pol],'mg') for pol in ['left','right','long'])==3:
            c2.Clear()
            c2.Divide(1,3)
     
            line = ROOT.TF1("horiz_line","0" if charge=='asymmetry' else '1',0.0,3.0);
            line.SetLineColor(ROOT.kBlack);
            line.SetLineWidth(2);

            yaxrange = {}
            if charge=='asymmetry':
                yaxtitle = 'W charge asymmetry'
                yaxrange['left'] = (0, 0.4); yaxrange['right'] = (-0.4, 0.4); yaxrange['long'] = (-1, 1)
            else:
                yaxtitle = '#frac{d#sigma/dy/#sigma_{tot}}{d#sigma^{exp}/dy/#sigma^{exp}_{tot}}' if options.normxsec else '#frac{d#sigma/dy}{d#sigma^{exp}/dy}'
                yaxrange['left'] = (0.70, 1.30); yaxrange['right'] = (0.70, 1.30); yaxrange['long'] = (-1., 3.0)
     
            legs = []
            pad_height, pad_width = 0.30, 0.85
            offset_top = 0.06

            pads = []
            for  ih,hel in enumerate(['left','right','long']):
                pad = ROOT.TPad('p'+str(ih), 'p'+str(ih), 0.00, 1.-offset_top-(ih+1)*pad_height, 1.00, 1.-offset_top-ih*pad_height)
                pad.SetRightMargin(0.03)
                pad.SetLeftMargin (0.12)
                pad.SetTopMargin(0.03)
                pad.SetBottomMargin(0.03)
                if ih ==2:
                    pad.SetBottomMargin(0.12)
        
                pad.Draw()
                pads.append(pad)
    

            for  ih,hel in enumerate(['left','right','long']):
     
                pads[ih].cd()
                values[hel].mg.Draw('Pa')
                ## x axis fiddling
                values[hel].mg.GetXaxis().SetRangeUser(0., 3.)
                values[hel].mg.GetXaxis().SetTitleSize(0.00)
                if not ih == 2:
                    values[hel].mg.GetXaxis().SetLabelSize(0.00)
                else:
                    values[hel].mg.GetXaxis().SetLabelSize(0.10)
                ## y axis fiddling
                values[hel].mg.GetYaxis().SetTitleOffset(0.45)
                values[hel].mg.GetYaxis().SetTitleSize(0.10)
                values[hel].mg.GetYaxis().SetLabelSize(0.08)
                values[hel].mg.GetYaxis().SetTitle(yaxtitle)
                values[hel].mg.GetYaxis().SetRangeUser(yaxrange[hel][0],yaxrange[hel][1])

                legx1, legx2, legy1, legy2 = 0.2, 0.7, 0.65, 0.9

                leg = ROOT.TLegend(legx1, legx2, legy1, legy2)
                leg.SetNColumns(2); leg.SetFillStyle(0); leg.SetBorderSize(0)
                leg.AddEntry(values[hel].graph_fit_rel , 'W^{{{ch}}} {h} (fit)'      .format(h=hel,ch=ch) , 'pl')
                leg.AddEntry(values[hel].graph_rel     , 'W^{{{ch}}} {h} (PDF unc.)' .format(h=hel,ch=ch) , 'f')

     
                leg.Draw('same')
                legs.append(leg) ## maybe this helps? lo and behold, pyROOT magic. this line is needed
                line.Draw("Lsame");
                pads[ih].RedrawAxis("sameaxis");
     
     
            c2.cd()
            lat.DrawLatex(0.12, 0.94, '#bf{CMS} #it{Preliminary}')
            lat.DrawLatex(0.65, 0.94, '36 fb^{-1} (13 TeV)')
            lat.SetTextSize(0.04)
            lat.DrawLatex(0.90, 0.03, '|Y_{W}|')
            for ext in ['png', 'pdf']:
                c2.SaveAs('{od}/genAbsY{norm}_pdfs_{ch}{suffix}_relative_{t}.{ext}'.format(od=options.outdir, norm=normstr, ch=charge, suffix=options.suffix, ext=ext,t=options.type))

NPDFs = 60
LUMINOSITY = 35900

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser(usage='%prog ybinfile workspace.root toys.root [options] ')
    parser.add_option('-i', '--infile'      , dest='infile'   , default=''            , type='string', help='workspace converted from datacard')
    parser.add_option('-y', '--ybinfile'    , dest='ybinfile' , default=''            , type='string', help='file with the yw binning')

    parser.add_option('-t', '--type'        , dest='type'     , default='toys'        , type='string', help='run the plot from which postfit? toys/scans/hessian')
    parser.add_option(      '--toyfile'     , dest='toyfile'  , default=''            , type='string', help='file that has the toys')
    parser.add_option(      '--scandir'     , dest='scandir'  , default=''            , type='string', help='directory with all the scans')
    parser.add_option(      '--hessfile'    , dest='hessfile' , default=''            , type='string', help='file that contains the hessian errors in a dictionary')
    parser.add_option(      '--xsecfiles'    , dest='xsecfiles' , default=None          , type='string', help='files that contains the expected x sections with variations (one per charge,comma separated in the same order of the charges) ')
    parser.add_option('-C', '--charge'      , dest='charge'   , default='plus,minus'  , type='string', help='process given charge. default is both')
    parser.add_option('-o', '--outdir'      , dest='outdir'   , default='.'           , type='string', help='outdput directory to save the plots')
    parser.add_option(      '--suffix'      , dest='suffix'   , default=''            , type='string', help='suffix for the correlation matrix')
    parser.add_option('-n', '--normxsec'    , dest='normxsec' , default=False         , action='store_true',   help='if given, plot the differential xsecs normalized to the total xsec')
    (options, args) = parser.parse_args()


    if not os.path.isdir(options.outdir):
        os.system('mkdir {od}'.format(od=options.outdir))
        if os.path.exists("/afs/cern.ch"): os.system("cp /afs/cern.ch/user/g/gpetrucc/php/index.php {od}".format(od=options.outdir))

    if options.ybinfile:
        ybinfile = options.ybinfile
    else:
        ybinfile = os.path.dirname(os.path.abspath(options.infile))+'/binningYW.txt'


    ## get the central values and uncertainties depending on the type given:

    ## if --type=toys   , we expect a toyfile
    ## if --type=scans  , we expect a scan directory
    ## if --type=hessian, we expect a hessian file

    if   options.type == 'toys':
        valuesAndErrors = utilities.getFromToys(options.infile)
    elif options.type == 'scans':
        valuesAndErrors = utilities.getFromScans(options.infile)
    elif options.type == 'hessian':
        valuesAndErrors = utilities.getFromHessian(options.infile)
    else:
        print 'ERROR: none of your types is supported. specify either "toys", "scans", or "hessian"'
        sys.exit()

    channel = 'mu' if any(re.match('.*_mu_Ybin_.*', param) for param in valuesAndErrors.keys()) else 'el'
    print "From the list of parameters it seems that you are plotting results for channel ",channel

    ybinfile = open(ybinfile, 'r')
    ybins = eval(ybinfile.read())
    ybinfile.close()

    ## calculate the bin widths for the rapidity bins
    ybinwidths = {}
    for k,v in ybins.items():
        tmplist = list(abs(i - v[v.index(i)+1]) for i in v[:-1])
        ybinwidths[k] = [float('{n:.2f}'.format(n=i)) for i in tmplist]


    charges = options.charge.split(',')
    xsecfiles = options.xsecfiles.split(',')
    xsec_nominal_allCharges = {}; xsec_systematics_allCharges = {}
    for ic,charge in enumerate(charges):

        ##file_pdfs = os.environ['CMSSW_BASE']+'/src/CMGTools/WMass/data/pdfs_prefit/pdf_variations_prefit.root'
        base = "/afs/cern.ch/work/e/emanuele/wmass/heppy/CMSSW_8_0_25/"
        file_pdfs = base+'/src/CMGTools/WMass/data/pdfs_prefit/pdf_variations_prefit.root'
        ## this gets the pdf central variation binned in the correct format
        nominal = utilities.getRebinned(ybins,charge,file_pdfs, 0)
        xsec_nominal = utilities.getXSecFromShapes(ybins,charge,xsecfiles[ic],channel, 0)
        xsec_nominal_allCharges[charge] = xsec_nominal

        shape_syst = {}
        value_syst = {}
        for pol in ['left','right', 'long']:
            histos = []
            values = []
            for ip in xrange(1,NPDFs+1):
                # print "Loading polarization %s, histograms for pdf %d" % (pol,ip)
                ## this gets the pdf variations after correctly rebinning the YW
                pdf = utilities.getRebinned(ybins,charge,file_pdfs,ip)
                xsec_pdf = utilities.getXSecFromShapes(ybins,charge,xsecfiles[ic],channel,ip)
                histos.append(pdf[pol])
                values.append(xsec_pdf[pol])
            shape_syst[pol] = histos
            value_syst[pol] = values

        systematics = {}
        xsec_systematics = {}
        for pol in ['left','right', 'long']:
            #print "===> Running pol = ",pol
            systs=[]
            xsec_systs=[]
            for iy,y in enumerate(ybinwidths['{ch}_{pol}'.format(ch=charge,pol=pol if not pol=='long' else 'right')]):
                #print "\tBin iy=%d,y=%f = " % (iy,y)
                nom = nominal[pol][iy]
                xsec_nom = xsec_nominal[pol][iy]
                totUp=0; xsec_totUp=0
                for ip,pdf in enumerate(shape_syst[pol]):
                    xsec_pdf = value_syst[pol][ip]
                    # debug
                    relsyst = abs(nom-pdf[iy])/nom
                    xsec_relsyst = abs(xsec_nom-xsec_pdf[iy])/xsec_nom if xsec_nom else 0.0
                    if relsyst>0.20:
                        print "SOMETHING WENT WRONG WITH THIS PDF: %d HAS RELATIVE SYST = %f. SKIPPING !" % (ip,relsyst)
                    else:
                        totUp += math.pow(relsyst*nom,2)
                    xsec_totUp += math.pow(xsec_relsyst*xsec_nom,2)
                totUp = math.sqrt(totUp)
                xsec_totUp = math.sqrt(xsec_totUp)
                # print "Rel systematic for Y bin %d = +/-%.3f" % (iy,totUp/nom)
                # print "\tRel systematic on xsec for Y bin %d = +/-%.3f" % (iy,xsec_totUp/xsec_nom if xsec_nom else 0.)
                systs.append(totUp)
                xsec_systs.append(xsec_totUp)
            systematics[pol]=systs
            xsec_systematics[pol]=xsec_systs
        xsec_systematics_allCharges[charge] = xsec_systematics

        nOuterBinsToExclude = 2  ### EDM hardcoded: out of acceptance Y bins

        allValues = {}
        for pol in ['left','right', 'long']:
            cp = '{ch}_{pol}'.format(ch=charge,pol=pol)
            MAXYFORNORM = ybins[cp][-nOuterBinsToExclude-1] # exclude the outermost 2 bins which has huge error due to acceptance
            normsigmaIn = sum([xsec_nominal[allpol][iy] for allpol in ['left','right', 'long'] for iy,y in enumerate(ybins[cp][:-1]) if abs(y)<MAXYFORNORM])
            normsigmaOut = sum([xsec_nominal[allpol][iy] for allpol in ['left','right', 'long'] for iy,y in enumerate(ybins[cp][:-1]) if abs(y)>=MAXYFORNORM])
            print "total xsec up to |Y|<{maxy} = {sigma:.3f} (pb)".format(maxy=MAXYFORNORM,sigma=normsigmaIn)
            print "total xsec beyond |Y|>{maxy} = {sigma:.3f} (pb)".format(maxy=MAXYFORNORM,sigma=normsigmaOut)

            tmp_val = valueClass('values_'+charge+'_'+pol)

            for iy,y in enumerate(ybinwidths['{ch}_{pol}'.format(ch=charge,pol=pol)]):
                normsigma = normsigmaIn if abs(ybins[cp][iy])<MAXYFORNORM else normsigmaOut
                parname = 'W{charge}_{pol}_W{charge}_{pol}_{ch}_Ybin_{iy}'.format(charge=charge,pol=pol,ch=channel,iy=iy)

                tmp_val.val.append(xsec_nominal[pol][iy]/ybinwidths[cp][iy])
                tmp_val.ehi.append(xsec_systematics[pol][iy]/ybinwidths[cp][iy])
                tmp_val.elo.append(xsec_systematics[pol][iy]/ybinwidths[cp][iy]) # symmetric for the expected
                if options.normxsec:
                    tmp_val.val[-1] = tmp_val.val[-1]/normsigma
                    tmp_val.ehi[-1] = tmp_val.ehi[-1]/normsigma
                    tmp_val.elo[-1] = tmp_val.elo[-1]/normsigma

                tmp_val.relv. append(1.);
                tmp_val.rello.append(systematics[pol][iy]/nominal[pol][iy])
                tmp_val.relhi.append(systematics[pol][iy]/nominal[pol][iy]) # symmetric for the expected
                
                scale = 1.
                if options.normxsec:
                    if   options.type == 'toys': 
                        xsec_fit = utilities.getNormalizedXsecFromToys(ybins,charge,pol,channel,iy,options.infile,MAXYFORNORM)
                    elif options.type == 'hessian':
                        xsec_fit = valuesAndErrors[parname+'_pmaskedexpnorm']
                    else:
                        print "--normxsec not implemented yet for scans."
                        sys.exit()
                else:
                    xsec_fit = valuesAndErrors[parname+'_pmaskedexp']
                    scale = LUMINOSITY

                tmp_val.val_fit.append(xsec_fit[0]/ybinwidths[cp][iy]/scale)
                tmp_val.elo_fit.append(abs(xsec_fit[0]-xsec_fit[1])/ybinwidths[cp][iy]/scale)
                tmp_val.ehi_fit.append(abs(xsec_fit[0]-xsec_fit[2])/ybinwidths[cp][iy]/scale)

                units = '' if options.normxsec else '(pb)'
                print "par = {parname}, expected sigma = {sigma:.3f} {units}   fitted = {val:.3f} + {ehi:.3f} - {elo:.3f} {units}".format(parname=parname,
                                                                                                                                          sigma=tmp_val.val[-1],units=units,
                                                                                                                                          val=tmp_val.val_fit[-1],ehi=tmp_val.ehi_fit[-1],elo=tmp_val.elo_fit[-1])

                if options.normxsec:
                    rfit = tuple([xs/xsec_nominal[pol][iy]*normsigma for xs in xsec_fit]) # rescale the fit xsec by the expected xsec in that bin
                else:
                    rfit = valuesAndErrors[parname+'_mu'] # r values: contain all the common norm uncertainties (lumi, eff...)

                tmp_val.relv_fit .append(rfit[0])
                tmp_val.rello_fit.append(abs(rfit[0]-rfit[1]))
                tmp_val.relhi_fit.append(abs(rfit[0]-rfit[2]))

                tmp_val.rap.append((ybins[cp][iy]+ybins[cp][iy+1])/2.)
                tmp_val.rlo.append(abs(ybins[cp][iy]-tmp_val.rap[-1]))
                tmp_val.rhi.append(abs(ybins[cp][iy]-tmp_val.rap[-1]))

            tmp_val.makeGraphs()

            allValues[pol] = tmp_val

        plotValues(allValues,charge,options)

    if len(charges)>1:
        print "Making charge asymmetry plots now..."
        asymmetryValues = {}
        
        for pol in ['left','right', 'long']:
            cp = 'plus_'+pol
            tmp_val = valueClass('asymmetry_'+pol)
            for iy,y in enumerate(ybinwidths[cp]):
                
                ch_sum  = xsec_nominal_allCharges['plus'][pol][iy] + xsec_nominal_allCharges['minus'][pol][iy]
                ch_diff = xsec_nominal_allCharges['plus'][pol][iy] - xsec_nominal_allCharges['minus'][pol][iy]
                asy_val = ch_diff / ch_sum
                # the following is not completely correct, since it doesn't account correlations in exp. uncertainties
                err_sum = math.hypot(xsec_systematics_allCharges['plus'][pol][iy],xsec_systematics_allCharges['minus'][pol][iy])
                asy_err = asy_val * math.hypot(err_sum/ch_sum,err_sum/ch_diff)
                tmp_val.relv .append(asy_val)
                tmp_val.relhi.append(asy_err)
                tmp_val.rello.append(asy_err)

                asy_fit = utilities.getAsymmetryFromToys(pol,channel,iy,options.infile)
                tmp_val.relv_fit .append(asy_fit[0])
                tmp_val.rello_fit.append(abs(asy_fit[0]-asy_fit[1]))
                tmp_val.relhi_fit.append(abs(asy_fit[0]-asy_fit[2]))

                tmp_val.rap.append((ybins[cp][iy]+ybins[cp][iy+1])/2.)
                tmp_val.rlo.append(abs(ybins[cp][iy]-tmp_val.rap[-1]))
                tmp_val.rhi.append(abs(ybins[cp][iy]-tmp_val.rap[-1]))

            tmp_val.makeGraphs()
            asymmetryValues[pol] = tmp_val
        
        plotValues(asymmetryValues,'asymmetry',options)
