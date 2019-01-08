import ROOT, os, datetime, re, operator, math
from array import array
ROOT.gROOT.SetBatch(True)

## ===================================================================
## USAGE:
## needs as infile a toys.root with limit tree from toys
## takes a comma separated list of regular expressions as input via --params
## if no output directory is given, it will just plot the smaller correlation matrix
## if output directory is given, it will save it there as pdf and png

## example:
## python w-helicity-13TeV/subMatrix.py toys.root --params alph,muR,muF,.*Ybin.*2,pdf12,pdf56,pdf42 --outdir <output_directory> --type toys/hessian
## examples of common regexps:
## NORMs: 'norm_.*'
## PDFs: range [1,20]: '^pdf([1-9]|1[0-9])|20$'
## ===================================================================
#def SetCorrMatrixPalette():
#ROOT.gStyle.SetPalette()



def niceName(name):

    if '_Ybin' in name:
        nn  = '#mu: ' if '_mu_' in name else 'el: '
        nn += 'W+ ' if 'plus' in name else 'W- '
        nn += 'left ' if 'left' in name else 'right ' if 'right' in name else 'long '
        idx = -2 if ('masked' in name or name.endswith('mu')) else -1
        nn += name.split('_')[idx]
        if 'pmaskedexp' in name: nn += ' #sigma'
        if 'norm' in name: nn += '_{norm}'

        if 'eff_unc' in name:
            nn = '#epsilon_{unc}^{'+nn+'}'
        return nn
        
    else:
        return name
        

if __name__ == "__main__":

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPaintTextFormat('.3f')

    date = datetime.date.today().isoformat()

    from optparse import OptionParser
    parser = OptionParser(usage='%prog workspace.root toys.root [options] ')
    parser.add_option('-o','--outdir', dest='outdir',    default='', type='string', help='outdput directory to save the matrix')
    parser.add_option('-p','--params', dest='params',    default='', type='string', help='parameters for which you want to show the correlation matrix. comma separated list of regexps')
    parser.add_option('-t','--type'  , dest='type'  ,    default='toys', type='string', help='which type of input file: toys(default),scans, or hessian')
    parser.add_option(     '--suffix', dest='suffix',    default='', type='string', help='suffix for the correlation matrix')
    (options, args) = parser.parse_args()

    ROOT.TColor.CreateGradientColorTable(3,
                                      array ("d", [0.00, 0.50, 1.00]),
                                      ##array ("d", [1.00, 1.00, 0.00]),
                                      ##array ("d", [0.70, 1.00, 0.34]),
                                      ##array ("d", [0.00, 1.00, 0.82]),
                                      array ("d", [0.00, 1.00, 1.00]),
                                      array ("d", [0.34, 1.00, 0.65]),
                                      array ("d", [0.82, 1.00, 0.00]),
                                      255,  0.95)


    if not options.type in ['toys', 'scans', 'hessian']:
        print 'the given type needs to be either "toys", "scans", or "hessian"!!'
        sys.exit()

    if options.outdir:
        ROOT.gROOT.SetBatch()
        if not os.path.isdir(options.outdir):
            os.system('mkdir -p {od}'.format(od=options.outdir))
        os.system('cp {pf} {od}'.format(pf='/afs/cern.ch/user/g/gpetrucc/php/index.php',od=options.outdir))

    pois_regexps = list(options.params.split(','))
    print "Filtering POIs with the following regex: ",pois_regexps

    params = []; indices = []

    ## directly store the mean and RMS into a dictionary
    fitvals = {}; fiterrs = {}

    cov = {}; corr = {}

    ### GET LIST OF PARAMETERS THAT MATCH THE SPECIFIED OPTION IN THE TOYFILE
    if options.type == 'toys':
        toyfile = ROOT.TFile(args[0], 'read')
        _tree = toyfile.Get('fitresults')
        lol = _tree.GetListOfLeaves()

        for l in lol:
            ## skip a bunch of those we don't want
            if '_err'   in l.GetName(): continue
            if '_minos' in l.GetName(): continue
            if '_gen'   in l.GetName(): continue
            if '_In'    in l.GetName(): continue
            for poi in pois_regexps:
                if re.match(poi, l.GetName()):
                    ## draw the parameter into a histogram
                    _tree.Draw(l.GetName()+'>>h_'+l.GetName())
                    ## find that histogram and clone it
                    h = ROOT.gROOT.FindObject('h_'+l.GetName()).Clone()
                    ## store mean and rms into the dictionaries from before
                    fitvals[l.GetName()] = h.GetMean()
                    fiterrs[l.GetName()] = h.GetRMS()
                    ## also keep a list of the parameter names, for sorting
                    params.append(l.GetName())

    elif options.type == 'hessian':
        hessfile = ROOT.TFile(args[0],'read')
        suffix = 'channelpmaskedexpnorm'
        for e in hessfile.GetListOfKeys() :
            if 'channelnone' in e.GetName(): suffix = 'channelnone'
        corrmatrix = hessfile.Get('correlation_matrix_'+suffix)
        covmatrix  = hessfile.Get('covariance_matrix_'+suffix)
        for ib in range(1+corrmatrix.GetNbinsX()+1):
            for poi in pois_regexps:
                if re.match(poi, corrmatrix.GetXaxis().GetBinLabel(ib)):
                    ## store mean and rms into the dictionaries from before
                    ## also keep a list of the parameter names, for sorting
                    params .append(corrmatrix.GetXaxis().GetBinLabel(ib))
                    indices.append(ib)
            
    ## construct the covariances and the correlations in one go.
    for ip1, p1 in enumerate(params):
        for ip2, p2 in enumerate(params):
            if options.type == 'toys':
                var = '({x}-{x0})*({y}-{y0})'.format(x=p1,x0=fitvals[p1],y=p2,y0=fitvals[p2])
                _tree.Draw('{var}>>h_{x}_{y}'.format(var=var,x=p1,y=p2))
                h = ROOT.gROOT.FindObject('h_{x}_{y}'.format(x=p1,y=p2)).Clone()
                cov [(p1,p2)] = h.GetMean()
                corr[(p1,p2)] = cov[(p1,p2)]/(fiterrs[p1]*fiterrs[p2])
            elif options.type == 'hessian':
                cov [(p1,p2)] = covmatrix .GetBinContent(indices[ip1],indices[ip2])
                corr[(p1,p2)] = corrmatrix.GetBinContent(indices[ip1],indices[ip2])
        

    print "===> Build covariance matrix from this set of params: ", params

    p_tmp = set(params)
    params = list(p_tmp)

    ## sort the floatParams. alphabetically, except for pdfs, which are sorted by number
    params = sorted(params, key= lambda x: int(x.split('_')[-1]) if '_Ybin_' in x else 0)
    params = sorted(params, key= lambda x: int(x.replace('pdf','')) if 'pdf' in x else 0)
    params = sorted(params, key= lambda x: int(x.replace('muRmuF','')) if 'muRmuF' in x else 0)
    params = sorted(params, key= lambda x: int(x.replace('muR','')) if ''.join([j for j in x if not j.isdigit()]) == 'muR'  else 0)
    params = sorted(params, key= lambda x: int(x.replace('muF','')) if ''.join([j for j in x if not j.isdigit()]) == 'muF'  else 0)
            
    print "sorted params = ", params

    c = ROOT.TCanvas("c","",1200,800)
    c.SetGridx()
    c.SetGridy()
    #ROOT.gStyle.SetPalette(55)
    #ROOT.gStyle.SetNumberContours(200); # default is 20 (values on palette go from -1 to 1)

    c.SetLeftMargin(0.15)
    c.SetRightMargin(0.11)
    c.SetBottomMargin(0.15)

    ## make the new, smaller TH2F correlation matrix
    nbins = len(params)
    th2_sub = ROOT.TH2F('sub_corr_matrix', 'small correlation matrix', nbins, 0., nbins, nbins, 0., nbins)
    th2_sub.GetXaxis().SetTickLength(0.)
    th2_sub.GetYaxis().SetTickLength(0.)
    
    ## pretty nested loop. enumerate the tuples
    for i,x in enumerate(params):
        for j,y in enumerate(params):
            ## set it into the new sub-matrix
            th2_sub.SetBinContent(i+1, j+1, corr[(x,y)])
            ## set the labels correctly
            new_x = niceName(x)
            new_y = niceName(y)
            th2_sub.GetXaxis().SetBinLabel(i+1, new_x)
            th2_sub.GetYaxis().SetBinLabel(j+1, new_y)

    th2_sub.GetZaxis().SetRangeUser(-1, 1)
    ROOT.gStyle.SetPaintTextFormat('1.2f')
    if len(params)<30: th2_sub.Draw('colz text45')
    else: th2_sub.Draw('colz')

    paramsName = options.params.replace(',','AND').replace('.','').replace('*','').replace('$','').replace('^','').replace('|','').replace('[','').replace(']','')

    if options.outdir:
        for i in ['pdf', 'png']:
            suff = '' if not options.suffix else '_'+options.suffix
            c.SaveAs(options.outdir+'/smallCorrelation{suff}_{pn}.{i}'.format(suff=suff,i=i,pn=paramsName))
        os.system('cp {pf} {od}'.format(pf='/afs/cern.ch/user/g/gpetrucc/php/index.php',od=options.outdir))

