import ROOT, os, array

## usage
## python checkEtaAsymmetry.py -i <inputRootFile> -v <variableName>

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] ')
    parser.add_option('-i', '--infile'         , dest='infile'     , default=''      , type='string', help='input file with the plot and ratio')
    parser.add_option('-v', '--var'            , dest='var'        , default='eta'   , type='string', help='name of the plotted variable')
    parser.add_option('-o', '--outdir'         , dest='outdir'     , default=''      , type='string', help='output directory')
    parser.add_option('-p', '--postfix'        , dest='postfix'    , default=''      , type='string', help='postfix appended to plot name')
    (options, args) = parser.parse_args()

    #var = os.path.basename(options.infile).split('.')[0]
    
    ROOT.TH1.SetDefaultSumw2()  # better to call it explicitely when doing operations wth histograms

    inf = ROOT.TFile(options.infile,'read')

    sig, bkg = 0, 0
    bkgs = []
    lok = inf.GetListOfKeys()
    for k in lok:
        obj = k.ReadObj()
        if not obj:
            print "Warning: cannot read object. Exit"
            quit()
        if not obj.ClassName().startswith("TH1"): continue
        if not options.var in k.GetName(): 
            continue
        if options.var in k.GetName() and '_signal'     in k.GetName(): continue
        if options.var in k.GetName() and '_background' in k.GetName(): continue
        if options.var in k.GetName() and '_stack'      in k.GetName(): continue
        if options.var in k.GetName() and '_canvas'     in k.GetName(): continue
        if options.var in k.GetName() and k.GetName().endswith('_data'):
            data = inf.Get(options.var+'_data')
        else:
            bkgs.append(inf.Get(k.GetName()))
        
    bkg = bkgs [0]
    for b in bkgs[1:]:
        print b
        bkg.Add(b)

    ratio = data.Clone('ratio')
    ratio.Sumw2()
    ratio.Divide(bkg)

    nhalf = ratio.GetXaxis().GetNbins()/2

    binedges = []
    values = []; errors = []

    for ip in range(nhalf*2):
        values.append( ratio.GetBinContent(ip+1) )
        errors.append( ratio.GetBinError  (ip+1) )
        binedges.append( ratio.GetXaxis().GetBinLowEdge(ip+nhalf+1) )

    binedges = binedges[:nhalf+1]

    histleft  = ROOT.TH1F('hist_left' , '', len(binedges)-1, array.array('d',binedges) )
    histright = ROOT.TH1F('hist_right', '', len(binedges)-1, array.array('d',binedges) )
    histleft.SetTitle('data-MC ratio for +/- eta')

    for ib in range(nhalf):
        histleft.SetBinContent(ib+1, values[nhalf-ib-1])
        histleft.SetBinError  (ib+1, errors[nhalf-ib-1])

        histright.SetBinContent(ib+1, values[nhalf+ib])
        histright.SetBinError  (ib+1, errors[nhalf+ib])

    col1 = ROOT.kAzure-1
    col2 = ROOT.kOrange-1
    histleft  .SetMarkerStyle(20); histleft  .SetMarkerSize(1.2); histleft  .SetMarkerColor(col1); histleft  .SetLineColor(col1)
    histright .SetMarkerStyle(21); histright .SetMarkerSize(1.2); histright .SetMarkerColor(col2); histright .SetLineColor(col2)

    canv = ROOT.TCanvas('foob', 'data-MC ratio for +/- #eta', 800, 600)
    ROOT.gStyle.SetOptStat(0)

    histleft.Draw('pe')
    histright.Draw('same pe')
    histleft.GetYaxis().SetRangeUser(0.9, 1.1)
    histleft.GetYaxis().SetTitle('data/MC ratio')
    histleft.GetXaxis().SetTitle('#eta_{lepton}')

    leg = ROOT.TLegend(0.2, 0.7, 0.5, 0.9)
    leg.SetFillStyle(0)
    leg.SetLineWidth(0)
    leg.AddEntry(histleft , 'negative eta', 'pl')
    leg.AddEntry(histright, 'positive eta', 'pl')
    leg.Draw('same')

    line = ROOT.TLine()
    line.SetLineStyle(3)
    line.SetLineWidth(2)
    line.SetLineColor(ROOT.kBlack)
    line.DrawLine(binedges[0], 1., binedges[-1], 1.)

    outdir = options.outdir if options.outdir else os.path.dirname(options.infile)
    postfix = '_'+options.postfix if options.postfix else ''

    canv.SaveAs(outdir+'/'+options.var+'_asymmetry'+postfix+'.pdf')
    canv.SaveAs(outdir+'/'+options.var+'_asymmetry'+postfix+'.png')

