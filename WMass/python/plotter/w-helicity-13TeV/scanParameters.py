import ROOT, os, datetime, re, operator, math, copy
import utilities
import array
#from joshuncs import uncs_josh
uncs_josh = eval(open('joshsuncs.py','r').read())

utilities = utilities.util()

def getCleanedError(self, graph):
    fname = graph.GetName()+'_fit'
    tf1 = ROOT.TF1(fname, 'a*(x-1)^2')
    graph.Fit(fname)
    tmp_fit = graph.GetFunction(fname)
    return (best, sol1, sol2)

def noOffsetGraph(graph, func):
    newgraph = graph.Clone(graph.GetName()+'_noOffset')
    utilities.graphStyle(newgraph, color=ROOT.kMagenta+1)
    minpoint = -1.*func.GetParameter(1) / (2.*func.GetParameter(2))
    fmin = func.Eval(minpoint)

    print 'found minimum at', fmin
    
    for ip in range(1,newgraph.GetN()+1):
        x, y = ROOT.Double(), ROOT.Double()
        newgraph.GetPoint(ip, x, y)
        newgraph.SetPoint(ip, x, y-fmin)

    return newgraph
        

def getCleanedGraph(infile, par, norm, n_iter, treename='limit'):
    f = ROOT.TFile(infile,'read')
    tree = f.Get(treename)
    vals = []
    normval = norm if norm else 1.
    for ev in tree:
        ##if 2.*ev.deltaNLL > 15: continue
        if norm == 1. and abs(getattr(ev, par) - norm) > 0.07: continue
        if abs(2.*ev.deltaNLL) < 0.0001: continue
        vals.append( [getattr(ev, par)/normval, 2.*ev.deltaNLL] )
    vals = sorted(vals)

    n_iter = int(n_iter)
    
    for i in range(n_iter):
    #while(n_iter):
        if len(vals) < 10: break
        print 'at iteration', i
        graph = ROOT.TGraph(len(vals), array.array('d', [x[0] for x in vals]), array.array('d', [y[1] for y in vals]) )
        ## if not i:
        ##     fname = graph.GetName()+'_fit0'
        ##     tf1 = ROOT.TF1(fname, '[0]*(x-1)^2')
        ##     graph.Fit(fname)
        ##     ff = graph.GetFunction(fname)
        ##     
        ## else:
        graph.Fit('pol2', 'rob')
        ff = graph.GetFunction('pol2')

        distances = []
        for v1,v2 in vals:
            distances.append(abs(ff.Eval(v1) - v2))
        im = distances.index(max(distances))
        distances.pop(im)
        vals.pop(im)

        #graph = ROOT.TGraph(len(vals), array.array('d', [x[0] for x in vals]), array.array('d', [y[1] for y in vals]) )
        #n_iter -= 1

    graph.SetName(par+'_graph_it{i:.0f}'.format(i=i))
    utilities.graphStyle(graph, rangeY=[-3., 15.] )

    return graph

def cleanGraphNew(infile, par, norm, treename='limit'):
    f = ROOT.TFile(infile,'read')
    tree = f.Get(treename)
    vals = []
    expectedSlope = []
    normval = norm if norm else 1.

    for ev in tree:
        #if 2.*ev.deltaNLL > 10: continue
        if abs(2.*ev.deltaNLL) < 0.0001: continue
        vals.append( [getattr(ev, par)/normval, 2.*ev.deltaNLL] )

    vals = sorted(vals)
    
    graph = ROOT.TGraph(len(vals), array.array('d', [x[0] for x in vals]), array.array('d', [y[1] for y in vals]) )

    realSlope = []
    
    newys = []
    newxs = []

    for i in range(graph.GetN()):

        if not i or i == graph.GetN()+1: continue


        x0,y0 = ROOT.Double(), ROOT.Double()
        x1,y1 = ROOT.Double(), ROOT.Double()
        x2,y2 = ROOT.Double(), ROOT.Double()

        before = graph.GetPoint(i-1, x0, y0)
        point  = graph.GetPoint(i  , x1, y1)
        after  = graph.GetPoint(i+1, x2, y2)


        if (x1-x0) and  (x2-x1):
            slopeL = (y1 - y0)/(x1-x0)
            slopeR = (y2 - y1)/(x2-x1)
        else:
            slopeL = 0.
            slopeR = 0.

        avgSlope = (slopeL+slopeR)/2.

        realSlope    .append(avgSlope)
        expectedSlope.append(x1)
        #print 'at point {i} expecting slope {x1:.2f} finding: {x2:.2f}           ratio: {foo:.3f}'.format(i=i, x1=x1, x2=avgSlope, foo=x1/avgSlope if avgSlope else 0.)
        print 'at point {i} found {y0:.2f} {y1:.2f} {y2:.2f}'.format(i=i,y0=y0,y1=y1,y2=y2)

        newy = (y0+y1+y2)/3.
        newys.append(newy)
        newxs.append(x1)

    newgraph = ROOT.TGraph(len(newys), array.array('d', newxs), array.array('d', newys) )

    return copy.deepcopy(newgraph)

    #print 'this is the real slope: ', realSlope
    #print 'this is the expected  : ', expectedSlope

## ===================================================================
## USAGE:
## needs the combine command available
## takes a comma separated list of regular expressions as input via --scan-parameters

## example:
##
## python w-helicity-13TeV/scanParameters.py -i <combine_ws> --scan-parameters CMS_lumi_13TeV,norm.*Ybin.*12 --outdir <dir> --npoints 25 --points-per-job 5
##
## has option --pretend to not submit, just print the commands
##
## once this is done, you can run the postprocessing with the same command, and two more options
## this command will hadd the single files into one scan_par.root file. then it will plot all the scans
## into the specified webdir. the hadd is not done if the scan_par.root file already exists (unless forced with --overwrite)
##
## python w-helicity-13TeV/scanParameters.py -i <combine_ws> --scan-parameters CMS_lumi_13TeV,norm.*Ybin.*12 --outdir <dir>                                 --postprocess --webdir <dir>
##
## ===================================================================


jobstring  = '''#!/bin/sh
ulimit -c 0 -S
ulimit -c 0 -H
set -e
cd CMSSWBASE
export SCRAM_ARCH=slc6_amd64_gcc530
eval `scramv1 runtime -sh`
cd OUTDIR
COMBINESTRING

'''

if __name__ == "__main__":

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPaintTextFormat('.3f')

    date = datetime.date.today().isoformat()

    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] ')
    parser.add_option('-i', '--infile'         , dest='infile'     , default=''   , type='string', help='workspace converted from datacard')
    parser.add_option('-o', '--outdir'         , dest='outdir'     , default=''   , type='string', help='outdput directory to make jobs and run combine in.')
    parser.add_option('-n', '--npoints'        , dest='npoints'    , default=50   , type='int'   , help='total number of points to run on scan')
    parser.add_option(      '--points-per-job' , dest='ppj'        , default=5    , type='int'   , help='points of the scan to run per job')
    parser.add_option(      '--scan-parameters', dest='pois'       , default=''   , type='string', help='comma separated list of regexp parameters to run. default is all parameters!')
    parser.add_option(      '--suffix'         , dest='suffix'     , default=''   , type='string', help='suffix')
    parser.add_option('-q', '--queue'          , dest='queue'      , default='8nh', type='string', help='use this queue. default 8nh')
    parser.add_option('-p', '--pretend'        , dest='pretend'    , action='store_true'         , help='only pretend. print commands, don\'t submit')
    parser.add_option('-v', '--verbose'        , dest='verbose'    , action='store_true'         , help='verbosity level 10. this leads to large outputs.')
    parser.add_option(      '--postprocess'    , dest='postprocess', action='store_true'         , help='hadd all files in the output directories')
    parser.add_option(      '--overwrite'      , dest='overwrite'  , action='store_true'         , help='overwrite the hadding')
    parser.add_option(      '--webdir'         , dest='webdir'     , default=''   , type='string', help='web directory to save the likelihood scans')
    (options, args) = parser.parse_args()

    if not options.outdir[-1] == '/':
        options.outdir += '/'
    absopath  = os.path.abspath(os.path.dirname(options.outdir))
    absinfile = os.path.abspath(options.infile)

    if not options.outdir:
        print 'ERROR: give at least an output directory. there will be a YUGE number of jobs!'
    else:
        if not os.path.isdir(absopath):
            print 'making a directory and running in it'
            os.system('mkdir -p {od}'.format(od=absopath))


    jobdir = absopath+'/jobs/'
    if not os.path.isdir(jobdir):
        os.system('mkdir {od}'.format(od=jobdir))

    infile = ROOT.TFile(absinfile, 'read')
    ws = infile.Get('w')

    ## get all the nuisance parameters from the workspace
    #nuisances = w.set('nuisances')
    pars = ws.allVars()
    pars = ROOT.RooArgList(pars)
    ## this has to be a loop over a range... doesn't work otherwise
    parameters = []
    all_parameters = []
    pois_regexps = list(options.pois.split(','))

    ## get the parameters to scan from the list of allVars and match them
    ## to the given regexp
    for i in range(len(pars)):
        tmp_name = pars[i].GetName()
        if '_In' in tmp_name: ## those are the input parameters
            continue
        if tmp_name in ['CMS_th1x', 'r']: ## don't want those
            continue
        all_parameters.append(tmp_name)
        for poi in pois_regexps:
            if re.match(poi, tmp_name): 
                parameters.append(pars[i].GetName())


    if not options.postprocess:

        for par in parameters:
            pardir = absopath+'/'+par+'/'
            os.system('mkdir -p '+pardir)
            print 'at parameter {p} running {n} points'.format(p=par, n=options.npoints)
            tmp_val = ws.var(par).getVal()
            tmp_dn = 0.9*tmp_val if tmp_val else -1.15
            tmp_up = 1.1*tmp_val if tmp_val else  1.15
            firstpoint = 0
            while firstpoint <= options.npoints-1:
                lastpoint = min(firstpoint+options.ppj-1,options.npoints-1)
                cmd_base  = 'combine {ws} -M MultiDimFit -t -1 --algo grid --points {np} '.format(ws=absinfile,np=options.npoints)
                cmd_base += ' --cminDefaultMinimizerType GSLMultiMinMod --cminDefaultMinimizerAlgo BFGS2 '
                cmd_base += ' --setParameterRanges "{p}={dn:.2f},{up:.2f}" '.format(p=par,dn=tmp_dn,up=tmp_up)
                cmd_base += ' -P {par} --floatOtherPOIs=1 '.format(par=par)
                ## cmd_base += ' --keepFailures ' ## don't want this anymore ... ?!
                cmd_base += ' -n _{name}_point{n}To{nn} '.format(name=par,n=firstpoint,nn=lastpoint)
                cmd_base += ' --firstPoint {n} --lastPoint {nn} '.format(n=firstpoint,nn=lastpoint)
                ##  masking_par = '_'.join(['mask']+os.path.basename(options.infile).split('_')[:2]+['xsec'])
                ##  cmd_base += ' --setParameters {mp}=1 '.format(mp=masking_par)
                #cmd_base += ' --redefineSignalPOIs '+','.join( [i for i in all_parameters if 'norm_' in i] )
                cmd_base += ' --expectSignal=1 '
                if options.verbose:
                    cmd_base += ' -v 10 '

                ## make new file for evert parameter and point
                job_file_name = jobdir+'/job_{p}_point{n:.0f}To{nn:.0f}.sh'.format(p=par,n=firstpoint,nn=lastpoint)
                tmp_file = open(job_file_name, 'w')

                ## fill the whole shebang in there
                tmp_filecont = jobstring
                tmp_filecont = tmp_filecont.replace('COMBINESTRING', cmd_base)
                tmp_filecont = tmp_filecont.replace('CMSSWBASE', os.environ['CMSSW_BASE']+'/src/')
                tmp_filecont = tmp_filecont.replace('OUTDIR', pardir)
                tmp_file.write(tmp_filecont)
                tmp_file.close()
                os.system('chmod u+x {f}'.format(f=job_file_name))

                ## submit the jobs!
                cmd_submit  = 'bsub -q {q} '.format(q=options.queue)
                cmd_submit += ' -o {of} '.format(of=job_file_name.replace('.sh','.log'))
                cmd_submit += ' {jf} '.format(jf=job_file_name)

                if not options.pretend:
                    os.system(cmd_submit)
                else:
                    print cmd_submit

                firstpoint = lastpoint+1

    ## end the submission, now move to what to do during postprocessing
    else:
        ROOT.gROOT.SetBatch()
        lat = ROOT.TLatex()
        lat.SetNDC(); lat.SetTextSize(0.04)
        c1 = ROOT.TCanvas('foo','bar',800,800)
        if not os.path.isdir(options.webdir):
            os.system('mkdir -p {wd} '.format(wd=options.webdir))
            os.system('cp /afs/cern.ch/user/g/gpetrucc/php/index.php '+options.webdir)
        uncertainties      = []
        uncertainties_josh = []
        
        for ip,par in enumerate(parameters):
            ## first hadd all the point files into one scan file named scan_<par>.root
            pardir = absopath+'/'+par+'/'
            print 'at parameter {p} doing some postprocessing'.format(p=par)
            fs = list([f for f in os.listdir(pardir) if 'higgs' in f])
            fs = sorted(fs, key= lambda x: int(x.split('.')[0].split('_')[-1].replace('point','').split('To')[0]))
            fs = list([pardir+f for f in fs])
            
            ofn = '{pd}/scan_{p}.root'.format(pd=pardir,p=par)

            ## run the hadd command only if the file doesn't exist or specified by user
            if not os.path.isfile(ofn) or options.overwrite:
                cmd_hadd = 'hadd -f {ofn} {fs}'.format(ofn=ofn, fs = ' '.join(fs))
                os.system(cmd_hadd)

            ## get the central value to normalize the norm parameters
            tmp_val = ws.var(par).getVal()

            ## make some plots of the likelihood scans
            ##tmp_graph = utilities.getGraph(ofn, par, norm=tmp_val)
            tmp_graph = getCleanedGraph(ofn, par, norm=tmp_val, n_iter=5)
            tmp_graph.Draw('ap')


            ## draw a line at 2.*deltaNLL = 1.
            tmp_line = ROOT.TLine(tmp_graph.GetXaxis().GetXmin(), 1., tmp_graph.GetXaxis().GetXmax(), 1.)
            tmp_line.SetLineStyle(7); tmp_line.SetLineWidth(2);
            tmp_line.Draw('same')
            tmp_line0 = ROOT.TLine(tmp_graph.GetXaxis().GetXmin(), 0., tmp_graph.GetXaxis().GetXmax(), 0.)
            tmp_line0.SetLineStyle(1); tmp_line0.SetLineWidth(2);
            tmp_line0.Draw('same')

            ## graph with offest
            tmp_graph.Fit('pol2', 'rob')
            tmp_fit = tmp_graph.GetFunction('pol2')
            tmp_fit.SetLineColor(ROOT.kAzure-4)
            (best, sol1, sol2) = utilities.solvePol2(tmp_fit.GetParameter(2), tmp_fit.GetParameter(1), tmp_fit.GetParameter(0)-1)

            ## correct for the offset of the graph
            tmp_graph_nooffset = noOffsetGraph(copy.deepcopy(tmp_graph), tmp_fit)

            ## look for the minimum point in x and offset by that number
            minpoint = -1.*tmp_fit.GetParameter(1) / (2.*tmp_fit.GetParameter(2))
            tmp_fit_nooffset = tmp_fit.Clone(tmp_fit.GetName()+'_nooffset')
            tmp_fit_nooffset.SetParameter(0, tmp_fit_nooffset.GetParameter(0)-tmp_fit.Eval(minpoint))
            tmp_fit_nooffset.SetLineColor(ROOT.kYellow+1)
            tmp_fit_nooffset.SetLineWidth(2)

            mg = ROOT.TMultiGraph()
            mg.Add(tmp_graph)
            mg.Add(tmp_graph_nooffset)
            mg.Draw('ap')
            mg.GetYaxis().SetRangeUser(-3., 10.)
            mg.GetYaxis().SetTitle(tmp_graph.GetYaxis().GetTitle())
            mg.GetXaxis().SetRangeUser(tmp_graph.GetXaxis().GetXmin(), tmp_graph.GetXaxis().GetXmax())
            ##if 'r_W' in par:
            ##    mg.GetXaxis().Set
            tmp_line.Draw('same')
            tmp_line0.Draw('same')
            tmp_fit_nooffset.Draw('same')
            (best, sol1, sol2) = utilities.solvePol2(tmp_fit_nooffset.GetParameter(2), tmp_fit_nooffset.GetParameter(1), tmp_fit_nooffset.GetParameter(0)-1)
            
            print 'solutions for nooffest graph', sol1, sol2
            

            lat.DrawLatex(0.35, 0.85, '#hat{{#mu}}_{{0}}: {best:.3f}'.format(best=best))
            lat.DrawLatex(0.35, 0.80, '-1 #sigma {sol1:.3f}'.format(sol1=sol1))
            lat.DrawLatex(0.35, 0.75, '+1 #sigma {sol2:.3f}'.format(sol2=sol2))
    
            uncertainties     .append( (par, (abs(sol1-tmp_val)+abs(sol2-tmp_val))/2. ) )  ## take the average of the uncertainty left and right
            uncertainties_josh.append( (par, uncs_josh[par] ) )

            tmp_linel = ROOT.TLine(sol1, 1., sol1, 0.)
            tmp_linel.SetLineStyle(3); tmp_line.SetLineWidth(2);
            tmp_linel.Draw('same')

            tmp_liner = ROOT.TLine(sol2, 1., sol2, 0.)
            tmp_liner.SetLineStyle(3); tmp_line.SetLineWidth(2);
            tmp_liner.Draw('same')

            if not options.webdir:
                print 'ERROR: specify a directory to save the plots!'
                sys.exit() ## sys isn't even loaded, so this will most definitely fail
            ## save the plots in the specified webdir
            c1.SaveAs(options.webdir+'/'+os.path.basename(ofn).replace('.root','.pdf'))
            c1.SaveAs(options.webdir+'/'+os.path.basename(ofn).replace('.root','.png'))


        ROOT.gROOT.SetBatch(0)
        c12 = ROOT.TCanvas()
        
        
        pdfunc_scans = ROOT.TGraph(len(uncertainties), array.array('d', [i for i,j in enumerate(uncertainties)]), array.array('d', [j[1] for j in uncertainties     ]))
        pdfunc_josh  = ROOT.TGraph(len(uncertainties), array.array('d', [i for i,j in enumerate(uncertainties)]), array.array('d', [j[1] for j in uncertainties_josh]))

        hist_uncs = ROOT.TH1F('hist_uncs', 'postfit', len(uncertainties), 0., len(uncertainties))
        hist_uncs_josh= ROOT.TH1F('hist_uncs_josh', 'hist_uncs_josh', len(uncertainties), 0., len(uncertainties))
        for i,j in enumerate(uncertainties):
            hist_uncs      .SetBinContent(i+1,j[1])
            hist_uncs_josh .SetBinContent(i+1,uncertainties_josh[i][1])
            hist_uncs      .SetBinError(i+1,0.)
            hist_uncs_josh .SetBinError(i+1,0.)
            hist_uncs      .GetXaxis().SetBinLabel(i+1,j[0] if not 'r_' in j[0] else 'r_'+'_'.join(j[0].split('_')[3:]))
            hist_uncs_josh .GetXaxis().SetBinLabel(i+1,j[0] if not 'r_' in j[0] else 'r_'+'_'.join(j[0].split('_')[3:]))
        
        hist_uncs.SetMarkerColor(38); hist_uncs.SetMarkerSize(1.0); hist_uncs.SetMarkerStyle(20)
        hist_uncs_josh.SetMarkerColor(46); hist_uncs_josh.SetMarkerSize(1.0); hist_uncs_josh.SetMarkerStyle(21)

        hist_uncs.Draw('p')
        hist_uncs_josh.Draw('p same')

        hist_uncs.GetYaxis().SetRangeUser(0., 1.0)
        
        #utilities.graphStyle(pdfunc_scans, style=20, color=38, size=1.0, titleY='pdf postfit unc.', rangeY=0)
        #utilities.graphStyle(pdfunc_josh , style=21, color=46, size=1.0, titleY='pdf postfit unc.', rangeY=0)
        #
        #mg2 = ROOT.TMultiGraph()
        #mg2.Add(pdfunc_scans)
        #mg2.Add(pdfunc_josh)

        #mg2.Draw('ap')

        #mg2_hist = mg2.GetHistogram()
        #for i,j in enumerate(uncertainties):
        #    mg2_hist.GetXaxis().SetBinLabel(mg2_hist.GetXaxis().FindBin(i), j[0])

        #mg2_hist.Draw('axis same')

        #
        #mg2.GetXaxis().SetTitle('pdf index')
        #mg2.GetYaxis().SetTitle('postfit uncertainty')
        #mg2.GetYaxis().SetRangeUser(0., 1.3)
        #
        leg = ROOT.TLegend(0.8, 0.9, 0.9, 1.)
        leg.SetFillStyle(0)
        leg.AddEntry(hist_uncs, 'from scans'     , 'p')
        leg.AddEntry(hist_uncs_josh, 'from tensorflow', 'p')
        leg.Draw('same')
        c12.SaveAs(options.webdir+'/postfit_uncertainty_comparison_{foob}.pdf'.format(foob=options.pois.replace(',','_').replace('.','').replace('*','')))
        c12.SaveAs(options.webdir+'/postfit_uncertainty_comparison_{foob}.png'.format(foob=options.pois.replace(',','_').replace('.','').replace('*','')))

    
        

        
