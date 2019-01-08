import optparse, subprocess, ROOT, datetime, math, array, copy, os, itertools
import numpy as np

#doPUreweighting = True
doPUandSF = False

def submitFRrecursive(ODIR, name, cmd, dryRun=False):
    outdir=ODIR+"/jobs/"
    if not os.path.isdir(outdir): 
        os.system('mkdir -p '+outdir)
    os.system('cp ${{HOME}}/index.php {od}/../'.format(od=outdir))
    os.system('cp ${{HOME}}/resubFRs.py {od}/../../'.format(od=outdir))
    srcfile = outdir+name+".sh"
    logfile = outdir+name+".log"
    srcfile_op = open(srcfile,"w")
    srcfile_op.write("#! /bin/sh\n")
    srcfile_op.write("ulimit -c 0\n")
    srcfile_op.write("cd {cmssw};\neval $(scramv1 runtime -sh);\ncd {d};\n".format( 
            d = os.getcwd(), cmssw = os.environ['CMSSW_BASE']))
    srcfile_op.write(cmd+'\n')
    os.system("chmod a+x "+srcfile)
    bsubcmd = "bsub -q 1nd -o {logfile} {srcfile}\n".format(d=os.getcwd(), logfile=logfile, srcfile=srcfile)
    if dryRun: 
        print "[DRY-RUN]: ", bsubcmd
    else: os.system(bsubcmd)

def submitIt(ODIR, name, cmd, dryRun=True):
    outdir=ODIR+"/jobs/"
    if not os.path.isdir(outdir): 
        os.system('mkdir -p '+outdir)
    srcfile = outdir+name+".sh"
    srcfile_op = open(srcfile,"w")
    srcfile_op.write("#! /bin/sh\n")
    srcfile_op.write("ulimit -c 0\n")
    srcfile_op.write("cd {cmssw};\neval $(scramv1 runtime -sh);\ncd {d};\n".format( 
            d = os.getcwd(), cmssw = os.environ['CMSSW_BASE']))
    srcfile_op.write(cmd+'\n')
    srcfile_op.close()
    os.system("chmod a+x "+srcfile)

    condorf_name = srcfile.replace('.sh','.condor')
    condorf_op = open(condorf_name,'w')
    condorf_op.write('''Universe = vanilla
Executable = {scriptName}
use_x509userproxy = $ENV(X509_USER_PROXY)
Log        = {od}{name}.log
Output     = {od}{name}.out
Error      = {od}{name}.error
getenv      = True

request_memory = 4000
+MaxRuntime = 14400
+AccountingGroup = "group_u_CMST3.all"
queue 1\n
 '''.format(scriptName=os.path.abspath(srcfile), name=name, od=outdir ) )
    condorf_op.close()
    subcmd = 'condor_submit {cf} '.format(cf=condorf_name)
    if dryRun: 
        print "[DRY-RUN]: ", subcmd
    else: os.system(subcmd)

def submitItLSF(ODIR, name, cmd, dryRun=True): #GO,name,plots=[],noplots=[],opts=None):
    outdir=ODIR+"/jobs/"
    if not os.path.isdir(outdir): 
        os.system('mkdir -p '+outdir)
    srcfile = outdir+name+".sh"
    logfile = outdir+name+".log"
    srcfile_op = open(srcfile,"w")
    srcfile_op.write("#! /bin/sh\n")
    srcfile_op.write("ulimit -c 0\n")
    srcfile_op.write("cd {cmssw};\neval $(scramv1 runtime -sh);\ncd {d};\n".format( 
            d = os.getcwd(), cmssw = os.environ['CMSSW_BASE']))
    srcfile_op.write(cmd+'\n')
    os.system("chmod a+x "+srcfile)
    bsubcmd = "bsub -q 8nh -o {logfile} {srcfile}\n".format(d=os.getcwd(), logfile=logfile, srcfile=srcfile)
    if dryRun: 
        print "[DRY-RUN]: ", bsubcmd
    else: os.system(bsubcmd)

def printAggressive(s):
    print '='.join('' for i in range(len(s)+1))
    print s
    print '='.join('' for i in range(len(s)+1))

def readScaleFactor(path, process, reterr = False):
    infile = open(path,'r')
    lines = infile.readlines()
    
    for line in lines:
        if 'Process {proc} scaled by'.format(proc=process) in line:
            scale = float(line.split()[4])
            scaleerr = float(line.split()[-1])
    if not reterr:
        return scale
    else:
        return scale, scaleerr

def readFakerate(path, process):
    infile = open(path,'r')
    lines = infile.readlines()
    index = 999
    for ind,line in enumerate(lines):
        if process in line and '===' in line:
            index = ind
    frs = []; errs = []
    for il, line in enumerate(lines):
        if il < index+3: continue
        if len(line)==1: break
        frs.append(float(line.split()[2]))
        down = float(line.split()[3].replace('--','-'))
        up   = float(line.split()[4].replace('++','+').replace('+-','+'))
        errs.append( (abs(down)+abs(up))/2.)
    ##fr  = float(lines[index+3].split()[2])
    ##err = (abs(float(lines[index+3].split()[3])) + abs(float(lines[index+3].split()[4])) )/2.
    print 'process:', process, 'this is frs:', frs 
    return frs, errs

def runefficiencies(trees, friends, targetdir, fmca, fcut, ftight, fxvar, enabledcuts, disabledcuts, scaleprocesses, compareprocesses, showratio, extraopts = ''):
    
    if not type(trees)==list: trees = [trees]
    treestring = ' '.join(' -P '+ t for t in list(trees))
    cmd  = ' mcEfficiencies.py --s2v -f -j 6 -l {lumi} -o {td} {trees} {fmca} {fcut} {ftight} {fxvar}'.format(lumi=lumi, td=targetdir, trees=treestring, fmca=fmca, fcut=fcut, ftight=ftight, fxvar=fxvar)
    if friends:
        #cmd += ' --Fs {friends}'.format(friends=friends)
        #cmd += ' -F mjvars/t {friends}/friends_evVarFriend_{{cname}}.root --FMC sf/t {friends}/friends_sfFriend_{{cname}}.root  '.format(friends=friends)
        cmd += ' -F Friends {friends}/tree_Friend_{{cname}}.root'.format(friends=friends)
    # not needed here cmd += ' --mcc ttH-multilepton/mcc-eleIdEmu2.txt --mcc dps-ww/mcc-tauveto.txt '
    ## cmd += ' --obj treeProducerWMassEle ' ## the tree is called 'treeProducerWMassEle' not 'tree'
    cmd += ' --groupBy cut '
    if doPUandSF and not '-W ' in extraopts: cmd += ' -W puw2016_nTrueInt_36fb(nTrueInt)*LepGood_effSF[0] '
    cmd += ''.join(' -E ^'+cut for cut in enabledcuts )
    cmd += ''.join(' -X ^'+cut for cut in disabledcuts)
    cmd += ' --compare {procs}'.format(procs=(','.join(compareprocesses)  ))
    if scaleprocesses:
        for proc,scale in scaleprocesses.items():
            cmd += ' --scale-process {proc} {scale} '.format(proc=proc, scale=scale)
    showrat   = ''
    if showratio:
        showrat = ' --showRatio '
    cmd += showrat
    if extraopts:
        cmd += ' '+extraopts

    print 'running: python', cmd
    subprocess.call(['python']+cmd.split())#+['/dev/null'],stderr=subprocess.PIPE)


def runplots(trees, friends, targetdir, fmca, fcut, fplots, enabledcuts, disabledcuts, processes, scaleprocesses, fitdataprocess, plotlist, showratio, extraopts = '', invertedcuts = [], submitit = False, name = ''):
    
    if not type(trees)==list: trees = [trees]
    treestring = ' '.join(' -P '+ t for t in list(trees))
    cmd  = ' mcPlots.py --s2v -f -j 6 -l {lumi} --pdir {td} {trees} {fmca} {fcut} {fplots}'.format(lumi=lumi, td=targetdir, trees=treestring, fmca=fmca, fcut=fcut, fplots=fplots)
    if friends:
        cmd += ' -F Friends {friends}/tree_Friend_{{cname}}.root'.format(friends=friends)
    cmd += ''.join(' -E ^'+cut for cut in enabledcuts )
    cmd += ''.join(' -X ^'+cut for cut in disabledcuts)
    if plotlist:
        cmd += ' --sP '+','.join(plot for plot in plotlist)
        cmd += ' -o '+targetdir+'/'+'_AND_'.join(plot for plot in plotlist)+'.root'
    else:
        cmd += ' -o '+targetdir+'/ALL.root'
    cmd += ' -p '+','.join(processes)
    if invertedcuts:
        cmd += ''.join(' -I ^'+cut for cut in invertedcuts )
    if doPUandSF and not '-W ' in extraopts: cmd += ' -W puw2016_nTrueInt_36fb(nTrueInt)*LepGood_effSF[0] '
    if fitdataprocess:
        cmd+= ' --fitData '
        cmd+= ''.join(' --flp '+proc for proc in fitdataprocess)
    if scaleprocesses:
        for proc,scale in scaleprocesses.items():
            cmd += ' --scale-process {proc} {scale} '.format(proc=proc, scale=scale)
    showrat   = ''
    if showratio:
        showrat = ' --showRatio '
    cmd += showrat
    if extraopts:
        cmd += ' '+extraopts

    if not submitit:
        print 'running: python', cmd
        subprocess.call(['python']+cmd.split())#+['/dev/null'],stderr=subprocess.PIPE)
    elif submitit == 'return':
        return 'python '+cmd
    else:
        submitIt(targetdir, name, 'python '+cmd, False)


def scaleClosure(recalculate):
    print '=========================================='
    print '2l closure tests for muon momentum scale ='
    print '=========================================='
    trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_recoLeptons_and_triggerMatch_latest/'
    friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_recoLeptons_and_triggerMatch_latest/friends/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/scaleClosure/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )

    fmca      = 'w-helicity-13TeV/wmass_mu/dy/mca.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/dy/cuts.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/dy/plots.txt'

    enable    = []
    disable   = []
    processes = ['Z', 'data']
    fittodata = []
    scalethem = {}

    ## trigger sf reweighting
    #trgString = 'triggerSF_2l(LepGood_matchedTrgObjMuPt[0],LepGood_matchedTrgObjTkMuPt[0],LepGood_matchedTrgObjMuPt[1],LepGood_matchedTrgObjTkMuPt[1],LepGood_SF1[0],LepGood_SF1[1])'
    trgString = '1.'

    selSF = '_get_muonSF_recoToSelection(LepGood_pdgId[0],LepGood_pt[0],LepGood_eta[0])*_get_muonSF_recoToSelection(LepGood_pdgId[1],LepGood_pt[1],LepGood_eta[1])'

    ## trigger+id/iso+puw
    extraoptsbase  = ' -W puw2016_nTrueInt_36fb(nTrueInt)*'+trgString+'*'+selSF+' '
    extraoptsbase += ' --maxRatioRange 0.9 1.1 --fixRatioRange --fitData --flp Z '

    mllvar = 'mll'

    makeplots = [mllvar]
    showratio = True

    binningpt  = [26,30,35,40,45]
    binningeta = [0., 1., 1.5, 2.0, 2.4]#-2.4,-1.6, -0.8, 0., 0.8, 1.6, 2.4]


    for n,((e,eta),(p,pt)) in enumerate(itertools.product(enumerate(binningeta[:-1]),enumerate(binningpt[:-1]))):

        etaptstring = 'ETA'+'To'.join(str(i).replace('-','m').replace('.','p') for i in [eta, binningeta[e+1]] )
        etaptstring+= 'PT' +'To'.join(str(i).replace('-','m').replace('.','p') for i in [pt , binningpt [p+1]] )
        tmp_td   = targetdir+'/'+etaptstring

        ## this is some weird recursive magic to submit this to the batch
        if opts.submitFR:
            abspath = os.path.abspath('.')
            tmp_cmd = 'python '+abspath+'/runWHelicity_mu_13TeV.py --scaleClosure --recalculate --doBin {n} {pf} '.format(n=n, pf=('' if not postfix else '--postfix '+postfix))
            submitFRrecursive(tmp_td, 'scalejob_{n}'.format(n=n), tmp_cmd)
            continue
        if opts.doBin > -1:
            if not n == opts.doBin: continue
        ## end weird magic

        ## submit the jobs to the batch

        eta1_var = 'abs(LepGood1_eta)'
        eta2_var = 'abs(LepGood2_eta)'

        ## make the binning in pT and eta
        extraopts  = extraoptsbase+' -A alwaystrue ETA{e} ({ev1}>={e1}&&{ev1}<{e2})||({ev2}>={e1}&&{ev2}<{e2}) '.format(e=e, e1=eta, e2=binningeta[e+1], ev1=eta1_var, ev2=eta2_var)
        extraopts +=               ' -A alwaystrue PT{p}  (LepGood1_pt>={p1}&&LepGood1_pt<{p2})||(LepGood2_pt>={p1}&&LepGood2_pt<{p2}) '.format(p=p, p1=pt , p2=binningpt [p+1])
        if recalculate: runplots(trees, friends, tmp_td, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, True, extraopts)

    ## do the postprocessing here, i.e. deriving the scales
    if not opts.submitFR and opts.doBin < 0:


        means_mc     = []; widths_mc     = []
        means_da     = []; widths_da     = []
        means_err_mc = []; widths_err_mc = []
        means_err_da = []; widths_err_da = []
        binlabels = []

        scaleCorr2D    = ROOT.TH2D('scales_corrections_2d_muons'  ,'scale corrections to apply in 2d', len(binningeta)-1, array.array('d', binningeta), len(binningpt)-1, array.array('d',binningpt))
        scaleCorr2D.GetXaxis().SetTitle('|#eta_{#mu}|')
        scaleCorr2D.GetYaxis().SetTitle('p_{T}')


        for n,((e,eta),(p,pt)) in enumerate(itertools.product(enumerate(binningeta[:-1]),enumerate(binningpt[:-1]))):
            #if n: continue
            print '============================================================'
            print '== at bin with eta', eta, ' and pt', pt
            print '============================================================'

            etaptstring = 'ETA'+'To'.join(str(i).replace('-','m').replace('.','p') for i in [eta, binningeta[e+1]] )
            etaptstring+= 'PT' +'To'.join(str(i).replace('-','m').replace('.','p') for i in [pt , binningpt [p+1]] )
            tmp_file = targetdir+'/'+etaptstring+'/'+mllvar+'.root'

            #binlabels.append( 'p_{{T}}: [{p1},{p2}] , |#eta|: [{e1},{e2}]'.format(p1=pt,p2=binningpt[p+1],e1=eta,e2=binningeta[e+1]) )
            binlabels.append( '{p1}-{p2} GeV'.format(p1=pt,p2=binningpt[p+1]))

            f = ROOT.TFile(tmp_file, 'read')

            if f.IsZombie(): 
                print '============================================================'
                print '============================================================'
                print '============================================================'
                print 'THIS BIN IS FUCKED!!!!!! ', eta, pt
                print '============================================================'
                print '============================================================'
                print '============================================================'
                continue
            
            
            mll_data = f.Get(mllvar+'_data')
            mll_mc   = f.Get(mllvar+'_Z'   )
            
            
            ## Declare observable mll
            x   = ROOT.RooRealVar('mll','mll', 80., 100.)
            ral = ROOT.RooArgList(x)
            
            dh_da  = ROOT.RooDataHist('dh_da', 'dh_da', ral, mll_data)
            dh_mc  = ROOT.RooDataHist('dh_mc', 'dh_mc', ral, mll_mc)
            
            frame = x.frame(ROOT.RooFit.Title('Z mass'))

            dacolor = ROOT.kGray+3; mccolor = ROOT.kAzure-2

            dh_da.plotOn(frame,ROOT.RooFit.MarkerColor(dacolor),ROOT.RooFit.MarkerSize(0.9),ROOT.RooFit.MarkerStyle(21))
            dh_mc.plotOn(frame,ROOT.RooFit.MarkerColor(mccolor),ROOT.RooFit.MarkerSize(0.9),ROOT.RooFit.MarkerStyle(20))
            #dh.statOn(frame)
            
            lat = ROOT.TLatex()
            lat.SetNDC()
            lat.SetTextSize(0.03)
            
            for t in ['data', 'mc']:
                w = ROOT.RooWorkspace('w')
                getattr(w,'import')(x)
                getattr(w,'import')(dh_da if t=='data' else dh_mc)

                #w.factory('BreitWigner::breitwigner(mll, bw_mean_{t}[91.1876,90.,93.], bw_width_{t}[2.495,1.8,2.7])'.format(t=t) )
                w.factory('BreitWigner::breitwigner(mll, bw_mean_{t}[91.1876], bw_width_{t}[2.495])'.format(t=t) )
                #w.factory('Gaussian::gauss1(mll, gauss1_mean_{t}[0.0,-5.,5.], gaus1_sigma_{t}[0.3,0.,10.])'.format(t=t) )
                #w.factory('Exponential::exp1(mll, exp1_c_{t}[0.0,-10.,10.])'.format(t=t) )
                w.factory('CBShape::cb(mll,cb_mean_{t}[0.,-3.,3.],cb_sigma_{t}[1.5,0.1,10.],cb_alpha_{t}[3.,0.5,8.],cb_n_{t}[1.,0.1,100.])'.format(t=t))
                #w.factory('Voigtian::finalpdf(mll, voigt_mean_{t}[90.,85.,95.], voigt_width_{t}[1.,0.,5.], voigt_sigma_{t}[0.3,0.,5.])'.format(t=t) )
                #w.factory('Gaussian::gauss2(mll, gauss2_mean_{t}[91.,80.,100.], gaus2_sigma_{t}[1.0,0.,10.])'.format(t=t) )
                #w.factory('SUM::sumgauss(gauss1, gauss2)')
                #w.factory('FCONV::completepdf(mll, breitwigner, gauss1)')
                w.factory('FCONV::finalpdf(mll, breitwigner, cb)')
                #w.factory('SUM::finalpdf(breitwigner, cb)')
                #w.factory('SUM::notfinalpdf(completepdf, gauss2)')
                #w.factory('SUM::finalpdf(notfinalpdf, gauss2)')
                #w.factory('SUM::finalpdf(mll, voigt, exp1)')
                #w.factory('SUM::finalpdf(frac_1[0.,1e4]*voigt, frac2[0.,1e4]*exp1)')


                #w.Print()

                ##w.factory('SUM::mll_{t}(mll_n1{t}[0,1e5]*Gaussian::gauss{t}(mll,mean{t},sigma{t}),mll_n2[0,1e5]*::exp2{t}({vartree},met_c1{t}))'.format(var=var, vartree=vartr    ee, t=t))
                ## mean  = ROOT.RooRealVar('mean' +'_'+t, 'mean' +'_'+t, 95.0, 70.0, 120.0)
                ## width = ROOT.RooRealVar('width'+'_'+t, 'width'+'_'+t,  5.0,  0.0,  20.0)
                ## sigma = ROOT.RooRealVar('sigma'+'_'+t, 'sigma'+'_'+t,  5.0,  0.0,  20.0)
                ## 
                ## voigt = ROOT.RooVoigtian('voigt_'+t,'voigt_'+t, x, mean, width, sigma)
                
                #filters = voigt.fitTo(dh_da if t=='data' else dh_mc) #,'qr')
                #filters = w.pdf('finalpdf').fitTo(dh_da if t=='data' else dh_mc, ROOT.RooFit.Optimize(0)) #,'qr')
                filters = w.pdf('finalpdf').fitTo(w.data((dh_da if t=='data' else dh_mc).GetName()) , ROOT.RooFit.SumW2Error(0) ) ##, ROOT.RooFit.Strategy(2), ROOT.RooFit.Minimizer('Minuit2'), ROOT.RooFit.Optimize(1))

                if t == 'data':
                    mean_da  = w.var('cb_mean_data').getVal()
                    width_da = w.var('cb_sigma_data').getVal()
                    mean_err_da  = w.var('cb_mean_data').getError()
                    width_err_da = w.var('cb_sigma_data').getError()
                    means_da .append( mean_da )
                    widths_da.append( width_da)
                    means_err_da .append( mean_err_da )
                    widths_err_da.append( width_err_da )
                else:
                    mean_mc  = w.var('cb_mean_mc').getVal()
                    width_mc = w.var('cb_sigma_mc').getVal()
                    mean_err_mc  = w.var('cb_mean_mc').getError()
                    width_err_mc = w.var('cb_sigma_mc').getError()
                    means_mc .append( mean_mc  )
                    widths_mc.append( width_mc )
                    means_err_mc .append( mean_err_mc )
                    widths_err_mc.append( width_err_mc )

            
            
                #voigt.plotOn(frame,ROOT.RooFit.LineColor(4)) # this will show fit overlay on canvas 
                w.pdf('finalpdf').plotOn(frame,ROOT.RooFit.LineColor(dacolor if t=='data' else mccolor)) # this will show fit overlay on canvas 

                # w.pdf('finalpdf').paramOn(frame)                         # this will display the fit parameters on canvas

                del w

            
            bin2dx = scaleCorr2D.GetXaxis().FindBin(eta)
            bin2dy = scaleCorr2D.GetYaxis().FindBin(pt )
            scaleCorr2D.SetBinContent(e+1, p+1, (mean_da-mean_mc)/91.1876/math.sqrt(2) )
            scaleCorr2D.SetBinError  (e+1, p+1, (mean_err_da-mean_err_mc)/91.1876/math.sqrt(2) )
                
            #filters->Print('v');
            #
            #Draw all frames on a canvas
            c = ROOT.TCanvas()
            c.cd()
            ROOT.gPad.SetLeftMargin(0.15)
                       
            frame.GetXaxis().SetTitle('Z mass (in GeV/c^{2})')
            frame.GetXaxis().SetTitleOffset(1.2)
            binsize = mll_data.GetBinWidth(1)
            frame.Draw()
            
            lat.SetTextColor(ROOT.kBlack)
            lat.SetTextSize(0.03)
            lat.DrawLatex(0.70, 0.86-(0.0), 'mean  (cb) data: {v:.4f}'.format(v=mean_da ))
            lat.DrawLatex(0.70, 0.82-(0.0), 'width (cb) data: {v:.4f}'.format(v=width_da))

            lat.DrawLatex(0.70, 0.72-(0.0), 'mean  (cb) MC: {v:.4f}'.format(v=mean_mc ))
            lat.DrawLatex(0.70, 0.68-(0.0), 'width (cb) MC: {v:.4f}'.format(v=width_mc))

            lat.SetTextSize(0.04)
            lat.SetTextColor(ROOT.kGreen+1)
            #lat.DrawLatex(0.18, 0.84-(0.0), '(m_{{Z}}^{{data}}-m_{{Z}}^{{MC}})/m_{{Z}}^{{true}}: {v:.3f} #times10^{{-3}}'.format(v=1000.*(mean_da-mean_mc)/91.1876))
            lat.DrawLatex(0.18, 0.84-(0.0), '#mu^{{CB}}_{{data}}-#mu^{{CB}}_{{MC}}: {v:.3f} #times10^{{-3}}'.format(v=1000.*(mean_da-mean_mc)))
            ## print 'THIS IS THE VALUE!!!!', mean_da-mean_mc

            lat.SetTextColor(ROOT.kBlack)
            lat.DrawLatex(0.18, 0.76-(0.0), '{e0} < #eta_{{#mu}} < {e1}'   .format(e0=eta,e1=binningeta[e+1]))
            lat.DrawLatex(0.18, 0.71-(0.0), '{p0} < p_{{T}}^{{#mu}} < {p1}'.format(p0=pt ,p1=binningpt [p+1]))

            c.SaveAs(targetdir+'/mll_fit_'+etaptstring+'.pdf')
            c.SaveAs(targetdir+'/mll_fit_'+etaptstring+'.png')

        outfile = ROOT.TFile('scale_correction_nonclosure_mu.root','recreate')
        outfile.cd()
        scaleCorr2D.Write()
        outfile.Close()
        cc = ROOT.TCanvas()
        cc.cd()
        ROOT.gStyle.SetOptStat(0)
        scaleCorr2D.Draw("colz text")
        cc.SaveAs(targetdir+'/scale_correction_nonclosure.pdf')
        cc.SaveAs(targetdir+'/scale_correction_nonclosure.png')
        

        c1 = ROOT.TCanvas()
        c1.Divide(1,2)

        scaleSummary_da = ROOT.TH1F('scalessummary_da','summary of scales data', 3*len(means_mc), 0, len(means_mc))
        scaleSummary_mc = ROOT.TH1F('scalessummary_mc','summary of scales mc  ', 3*len(means_mc), 0, len(means_mc))

        scaleClosure    = ROOT.TH1F('scales_closure'  ,'closure of scale'      ,   len(means_mc), 0, len(means_mc))
        scaleClosure.SetMarkerColor(mccolor); scaleClosure.SetLineColor(mccolor);scaleClosure.SetLineWidth(2); scaleClosure.SetMarkerSize(1.0); scaleClosure.SetMarkerStyle(20)
        scaleClosure.GetYaxis().SetTitle('(#mu_{CB}^{data}-#mu_{CB}^{MC})/m_{true}')

        residualResolution = ROOT.TH1F('residualResolution','residual resolution corrections', 3*len(means_mc), 0, len(means_mc))

        ROOT.gStyle.SetOptStat(0)

        for n,val in enumerate(means_mc):
            scaleSummary_mc.SetBinContent(3*n+2, val         )
            scaleSummary_da.SetBinContent(3*n+3, means_da[n] )
            scaleSummary_mc.SetBinError  (3*n+2, widths_mc[n])
            scaleSummary_da.SetBinError  (3*n+3, widths_da[n])

            residualResolution.SetBinContent(3*n+2, math.sqrt(widths_da[n]**2-widths_mc[n]**2) if widths_da[n]**2 > widths_mc[n]**2 else 0.)
            residualResolution.SetBinError  (3*n+2, 0.1)

            scaleClosure.SetBinContent(n+1, (means_da[n]-val)/91.1876/math.sqrt(2) )
            scaleClosure.SetBinError  (n+1, (means_err_da[n]-means_err_mc[n])/91.1876/math.sqrt(2))
            scaleClosure.GetXaxis().SetBinLabel(n+1, binlabels[n])

        scaleSummary_da.SetMarkerColor(dacolor); scaleSummary_da.SetLineColor(dacolor);scaleSummary_da.SetLineWidth(2); scaleSummary_da.SetMarkerSize(1.0); scaleSummary_da.SetMarkerStyle(20)
        scaleSummary_mc.SetMarkerColor(mccolor); scaleSummary_mc.SetLineColor(mccolor);scaleSummary_mc.SetLineWidth(2); scaleSummary_mc.SetMarkerSize(1.0); scaleSummary_mc.SetMarkerStyle(20)
        scaleSummary_da.GetYaxis().SetTitle('#mu_{CB} #pm #sigma_{CB} ')
        scaleSummary_da.GetXaxis().SetTitle('bin')

        print 'THIS IS LENGTH OF MEANS', len(means_mc)

        scaleSummary_da.GetYaxis().SetRangeUser(-2., 2.)

        c1.cd(1)
        scaleSummary_da.Draw('p')
        scaleSummary_mc.Draw('p same')

        line = ROOT.TLine()
        line.SetLineStyle(2)
        line.SetLineWidth(2)
        line.DrawLine(0, 0., scaleSummary_da.GetXaxis().GetXmax(), 0.)
        line.SetLineStyle(3)
        line.DrawLine(0, -1., scaleSummary_da.GetXaxis().GetXmax(), -1.)
        line.DrawLine(0,  1., scaleSummary_da.GetXaxis().GetXmax(),  1.)

        c1.cd(2)
        residualResolution.GetYaxis().SetRangeUser(0., 1.)
        residualResolution.GetYaxis().SetTitle('#sqrt{#sigma_{CB,data}^{2} - #sigma_{CB,MC}^{2}}')
        residualResolution.GetXaxis().SetTitle('bin')

        residualResolution.SetMarkerColor(ROOT.kBlack)
        residualResolution.SetMarkerSize (1.0)
        residualResolution.SetMarkerStyle(20)
        residualResolution.Draw('pe')

        meanCorr = sum( ( (math.sqrt(widths_da[k]**2-widths_mc[k]**2) if widths_da[k]**2 > widths_mc[k]**2 else 0. )for k,i in enumerate(means_mc)) )/len(means_da)
        line.SetLineStyle(2)
        line.DrawLine(0, meanCorr,  scaleSummary_da.GetXaxis().GetXmax(), meanCorr)
        lat .DrawLatex(0.15, 0.75, 'mean residual resolution correction: {v:.2f}'.format(v=meanCorr))

        c1.SaveAs(targetdir+'/summary_scales.pdf')
        c1.SaveAs(targetdir+'/summary_scales.png')

        c1.Clear()
        #ROOT.gStyle.SetPadLeftMargin(0.15)
        #ROOT.gStyle.SetPadBottomMargin(0.25)
        yrange = 0.002
        scaleClosure.Draw('pe')
        scaleClosure.GetYaxis().SetRangeUser(-1.*yrange,yrange)
        line.DrawLine(1.*(len(binningpt)-1), -1*yrange, 1.*(len(binningpt)-1), yrange)
        line.DrawLine(2.*(len(binningpt)-1), -1*yrange, 2.*(len(binningpt)-1), yrange)
        line.DrawLine(3.*(len(binningpt)-1), -1*yrange, 3.*(len(binningpt)-1), yrange)
        lat.DrawLatex(0.12, 0.8, '0.0 < |#eta| < 1.0')
        lat.DrawLatex(0.32, 0.8, '1.0 < |#eta| < 1.5')
        lat.DrawLatex(0.52, 0.8, '1.5 < |#eta| < 2.0')
        lat.DrawLatex(0.72, 0.8, '2.0 < |#eta| < 2.4')

        c1.SaveAs(targetdir+'/closure_scale.pdf')
        c1.SaveAs(targetdir+'/closure_scale.png')


        

    #runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)

def sfClosure2l():
    print '=========================================='
    print '2l closure tests for the trigger SFs etc.'
    print '=========================================='
    trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_triggerMatch_latest/'
    friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_triggerMatch_latest/friends/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/sfClosure/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )

    fmca      = 'w-helicity-13TeV/wmass_mu/dy/mca.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/dy/cuts.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/dy/plots.txt'

    enable    = ['mllZ', 'onlyl1fired']
    disable   = []
    processes = ['Z', 'data']
    fittodata = []
    scalethem = {}
    trgString = 'triggerSF_2l(LepGood_matchedTrgObjMuPt[0],LepGood_matchedTrgObjTkMuPt[0],LepGood_matchedTrgObjMuPt[1],LepGood_matchedTrgObjTkMuPt[1],LepGood_SF1[0],LepGood_SF1[1])'
    #trgString = '1.'
    extraopts = ' -W puw2016_nTrueInt_36fb(nTrueInt)*'+trgString+'*LepGood_SF2[0]*LepGood_SF3[0]*LepGood_SF2[1]*LepGood_SF3[1] --maxRatioRange 0.9 1.1 --fixRatioRange --fitData --flp Z '
    makeplots = ['ptl1', 'ptl2', 'analysisetal1', 'analysisetal2', 'mll']
    showratio = True
    runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)

def simplePlot():
    print '=========================================='
    print 'running simple plots'
    print '=========================================='
    #trees     = ['/eos/cms/store/group/phys_tracking/elisabetta/WSkims/']
    #trees     = ['/eos/user/m/mdunser/w-helicity-13TeV/trees/trees_all_skims/']
    #friends   = '/eos/user/m/mdunser/w-helicity-13TeV/friends/friends_SFs_pu_awayJet-2017-12-11/'
    #trees     = ['/eos/user/m/mdunser/w-helicity-13TeV/trees/trees_all_skims/']
    #friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/trees_all_skims/friends/'
    ## trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/'
    ## friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/friends/'
    trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_recoLeptons_and_triggerMatch_latest/'
    friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_recoLeptons_and_triggerMatch_latest/friendsNEWSCALE/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/simple_plots/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )

    ## fmca      = 'w-helicity-13TeV/wmass_mu/simple/mca_simple.txt'
    ## fcut      = 'w-helicity-13TeV/wmass_mu/simple/cuts_simple.txt'
    ## fplots    = 'w-helicity-13TeV/wmass_mu/simple/plots.txt'
    fmca      = 'w-helicity-13TeV/wmass_mu/dy/mca.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/dy/cuts.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/dy/plots.txt'

    enable    = []
    disable   = []
    processes = ['Z', 'data']#, 'data_fakes']#, 'data_fakes']
    fittodata = []#'data_fakes']
    scalethem = {}#'W': 0.978, 'Z': 0.822, 'data_fakes': 1.299}
    #extraopts = ' -W puw*LepGood_sf1[0]*LepGood_sf2[0]*LepGood_sf3[0] --maxRatioRange 0.8 1.2 --fixRatioRange '
    #extraopts = ' -W puw2016_nTrueInt_36fb(nTrueInt)*LepGood_sf2[0]*LepGood_sf3[0] --maxRatioRange 0.9 1.1 --fixRatioRange '#--scaleSigToData --sp data_fakes '
    trgString = 'triggerSF_2l_histo(LepGood_pt[0],LepGood_eta[0],LepGood_matchedTrgObjMuPt[0],LepGood_matchedTrgObjTkMuPt[0],LepGood_pt[1],LepGood_eta[1],LepGood_matchedTrgObjMuPt[1],LepGood_matchedTrgObjTkMuPt[1])'

    ## trgString = '1.'#'triggerSF_2l_histo(LepGood_pt[0],LepGood_eta[0],LepGood_matchedTrgObjMuPt[0],LepGood_matchedTrgObjTkMuPt[0],LepGood_pt[1],LepGood_eta[1],LepGood_matchedTrgObjMuPt[1],LepGood_matchedTrgObjTkMuPt[1])'
    #trgString  ='triggerSF_2l_byCharge(LepGood_pt[0],LepGood_eta[0],LepGood_matchedTrgObjMuPt[0],LepGood_matchedTrgObjTkMuPt[0],LepGood_charge[0],1)'
    #trgString +='*triggerSF_2l_byCharge(LepGood_pt[1],LepGood_eta[1],LepGood_matchedTrgObjMuPt[1],LepGood_matchedTrgObjTkMuPt[1],LepGood_charge[1],1)'

    selectionString = '_get_muonSF_recoToSelection(LepGood_pdgId[0],LepGood_pt[0],LepGood_eta[0])*_get_muonSF_recoToSelection(LepGood_pdgId[1],LepGood_pt[1],LepGood_eta[1])'
    #trgString = '1.'
    extraopts = ' -W puw2016_nTrueInt_36fb(nTrueInt)*'+trgString+'*'+selectionString+' --maxRatioRange 0.8 1.2 --fixRatioRange --fitData --flp Z '
    ##makeplots = ['ptlep', 'analysisetalep']#1', 'analysisetal2', 'ptl1', 'ptl2']#'ptl1', 'analysisetal1'] #'mtl1tk', 'etal1', 'ptl1']#'nVert', 'ptl1', 'etal1', 'mtl1tk', 'mtl1pf', 'tkmet', 'pfmet']
    ##extraopts += ' -A alwaystrue onlyplus (LepGood_eta-10.*(LepGood_charge<0))>-2.5 '
    makeplots = ['ptlepscaleUp', 'ptlepscaleDn']#'analysisetalep', 'ptlep']
    showratio = True
    runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)
    
def plots1l():
    print '=========================================='
    print 'running plots for 1l'
    print '=========================================='
    ## old skims trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/'
    ## old skims friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/friends/'
    ## originals trees     = '/eos/cms/store/cmst3/group/wmass/w-helicity-13TeV/trees/SKIMS_muons_latest/'
    ## originals friends   = '/eos/cms/store/cmst3/group/wmass/w-helicity-13TeV/trees/SKIMS_muons_latest/friends/'
    trees     = '/afs/cern.ch/work/m/mdunser/public/wmassTrees/SKIMS_muons_latest/'
    friends   = '/afs/cern.ch/work/m/mdunser/public/wmassTrees/SKIMS_muons_latest/friends/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/plots-1l/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )

    fmca      = 'w-helicity-13TeV/wmass_mu/simple/mca_simple.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/simple/cuts_simple.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/simple/plots.txt'

    enable    = []#'mtl1pf40max']
    disable   = []#'mtl1pf40min']
    processes = ['W', 'data', 'Top', 'DiBosons', 'Z', 'fakes_data', 'TauDecaysW'] #'QCD'
    #processes = ['data_awayJetPt45', 'data_FRmu_slope_Up', 'data_FRmu_continuous_Up']
    fittodata = []
    scalethem = {}
    trgString = '1.'#triggerSF_1l_histo(LepGood_calPt[0],LepGood_eta[0])'

    ## sfString = 'LepGood_SF1[0]*LepGood_SF3[0]'
    ## sfString = '_get_muonSF_selectionToTrigger(13,LepGood_pt[0],LepGood_eta[0])*_get_muonSF_recoToSelection(13,LepGood_pt[0],LepGood_eta[0])'
    sfString = 'LepGood_SF1[0]*LepGood_SF2[0]'
    #extraopts = ' -W puw2016_nTrueInt_36fb(nTrueInt)*'+trgString+'*'+selectionString+' --maxRatioRange 0.9 1.1 --fixRatioRange '
    #extraopts = ' -W puw2016_nTrueInt_36fb(nTrueInt)*_get_muonSF_recoToSelection(13,LepGood_pt[0],LepGood_eta[0])*triggerSF_1l_histo(LepGood_pt[0],LepGood_eta[0]) --maxRatioRange 0.9 1.1 --fixRatioRange '
    extraopts = ' -W puw2016_nTrueInt_36fb(nTrueInt)*'+sfString+' --maxRatioRange 0.9 1.1 --fixRatioRange --verywide '
    makeplots = ['unrolled']#'ptl1scale', 'ptl1scaleUp', 'ptl1scaleDn']#, 'analysisetal1'] #'mtl1tk', 'etal1', 'ptl1']#'nVert', 'ptl1', 'etal1', 'mtl1tk', 'mtl1pf', 'tkmet', 'pfmet']
    showratio = True
    runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)
    
def wptBinsScales(i):
    wptbins = [0.0, 1.971, 2.949, 3.838, 4.733, 5.674, 6.684, 7.781, 8.979, 10.303, 11.777, 13.435, 15.332, 17.525, 20.115, 23.245, 27.173, 32.414, 40.151, 53.858, 13000.0]
    if len(wptbins)<2*i:
        print 'you are asking too much from the wpt binning for decorrelation of scales'
        print '    length is {l} and you are asking for bin {i}'.format(l=len(wptbins),i=i)
    ptlo = wptbins[2*(i-1)]
    pthi = wptbins[2*i]
    return [ptlo, pthi]

def makePDFvariations():
    print '=========================================='
    print 'running pdf variations of the abs(Y)'
    print '=========================================='
    ## produces the AN version trees     = ['/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_1muskim/']
    ## produces the AN version friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_1muskim/friends/'
    ## tmptmp trees     = ['/eos/cms/store/cmst3/group/wmass/w-helicity-13TeV/ntuplesRecoil/TREES_SIGNAL_1l_recoil_fullTrees/']
    ## tmptmp friends   = '/eos/cms/store/cmst3/group/wmass/w-helicity-13TeV/ntuplesRecoil/TREES_SIGNAL_1l_recoil_fullTrees/friends/'
    trees     = ['/eos/cms/store/cmst3/group/wmass/w-helicity-13TeV/ntuplesRecoil/TREES_SIGNAL_1l_recoil_skim_1genmu/']
    friends   = '/eos/cms/store/cmst3/group/wmass/w-helicity-13TeV/ntuplesRecoil/TREES_SIGNAL_1l_recoil_skim_1genmu/friends/'
    #targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/absY_pdfVariations/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/theory_variations/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )

    fmca      = 'w-helicity-13TeV/wmass_mu/mca-includes/mca-80X-wmunu-sig.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/helicityTemplates/cuts.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/helicityTemplates/plots.txt'

    enable    = []
    disable   = []
    fittodata = []
    scalethem = {}
    showratio = False


    ## there are too many. make a smarter condor file and submit that with spawning and just one out/error/log file
    outdir=targetdir+"/jobs/"
    if not os.path.isdir(outdir): 
        os.system('mkdir -p '+outdir)
    srcfile = outdir+'/dummy_exec.sh'
    srcfile_op = open(srcfile,"w")
    srcfile_op.write('#!/bin/sh\n')
    srcfile_op.write('ulimit -c 0\n')
    srcfile_op.write('cd {cmssw};\neval $(scramv1 runtime -sh);\ncd {d};\n$*\n'.format( 
            d = os.getcwd(), cmssw = os.environ['CMSSW_BASE']))
    srcfile_op.close()
    os.system('chmod a+x '+srcfile)

    condorf_name = srcfile.replace('.sh','.condor')
    condorf_op = open(condorf_name,'w')
    condorf_op.write('''Universe = vanilla
Executable = {scriptName}
use_x509userproxy = $ENV(X509_USER_PROXY)
Log        = {of}.log
Output     = {of}.out
Error      = {of}.error
getenv      = True

request_memory = 4000
+MaxRuntime = 14400
+AccountingGroup = "group_u_CMST3.all"
 '''.format(scriptName=os.path.abspath(srcfile), of=os.path.abspath(srcfile).replace('.sh','') ) )

    cmds = []

    for ch in ['plus', 'minus']:
        processes = ['W{ch}_left'.format(ch=ch), 'W{ch}_right'.format(ch=ch), 'W{ch}_long'.format(ch=ch)]
        for i in range(1,61):
            extraopts = " --plotmode=nostack -W hessWgt{i} ".format(i=i)
            makeplots = ['w{ch}_wy_pdf{i}'.format(ch=ch,i=i)]
            cmds.append(runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, [], 'return', '{ch}_pdf{i}'.format(ch=ch,i=i)))
        for sys, var in itertools.product(['muR','muF', 'muRmuF', 'alphaS', 'mW'],['Up', 'Dn']):
            sv = sys+var

            if sys == 'mW': ## mW variation here
                extraopts = " --plotmode=nostack -W mass_{newmass} ".format(newmass = '80470' if var == 'Up' else '80370')
                makeplots = ['w{ch}_wy_{sv}'.format(ch=ch,sv=sv)]
                cmds.append(runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, [], 'return', '{ch}_{sv}'.format(ch=ch,sv=sv)))

            elif 'muR' in sys or 'muF' in sys: ## here run the 1-10 and the fully correlated in W-pT
                for ipt in range(0,11):
                    if not ipt:
                        extraopts = " --plotmode=nostack -W qcd_{sv} ".format(sv=sv)
                        makeplots = ['w{ch}_wy_{sv}'.format(ch=ch,sv=sv)]
                        cmds.append(runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, [], 'return', '{ch}_{sv}'.format(ch=ch,sv=sv)))
                    else:
                        newsv = sys+str(ipt)+var
                        ptcut = wptBinsScales(ipt)
                        wgtstr = 'TMath::Power(qcd_{sv},(prefsrw_pt>={ptlo}&&prefsrw_pt<{pthi}))'.format(sv=sv,ptlo=ptcut[0],pthi=ptcut[1])
                        extraopts = ' --plotmode=nostack -W {ws} '.format(ws=wgtstr)
                        makeplots = ['w{ch}_wy_{sv}'.format(ch=ch,sv=newsv)]
                        cmds.append(runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, [], 'return', '{ch}_{sv}'.format(ch=ch,sv=newsv)))

            else: ## this leaves alphaS here
                extraopts = " --plotmode=nostack -W qcd_{sv} ".format(sv=sv)
                makeplots = ['w{ch}_wy_{sv}'.format(ch=ch,sv=sv)]
                cmds.append(runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, [], 'return', '{ch}_{sv}'.format(ch=ch,sv=sv)))


    for ch in ['plus', 'minus']:
        processes = ['W{ch}_left'.format(ch=ch), 'W{ch}_right'.format(ch=ch), 'W{ch}_long'.format(ch=ch)]
        extraopts = ' --plotmode=nostack -W 1. '
        makeplots = ['w{ch}_wy_central'.format(ch=ch)]
        cmds.append(runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, [], 'return', '{ch}_central'.format(ch=ch)))

    for c in cmds:
        condorf_op.write('\narguments = {c}\nqueue 1\n'.format(c=c))
    condorf_op.close()
    print 'wrote condor file', os.path.abspath(condorf_name)
    
def compareScales():
    print '=========================================='
    print 'comparing W-pT central and qcd scales up/down'
    print '=========================================='
    trees     = ['/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_1muskim/']
    friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_1muskim/friends/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/qcdScales/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )

    fmca      = 'w-helicity-13TeV/wmass_mu/mca-includes/mca-80X-wmunu-sig-forscales.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/helicityTemplates/cuts.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/helicityTemplates/plots.txt'

    doW = False
    doZ = True
    if doW:
        for ch in ['both']:#'plus', 'minus', 'both']:
            enable    = ['w'+ch]
            disable   = []
            processes = ['W{ch}_{iv}'.format(ch=ch, iv=i) for i in ['central', 'wptSlopeUp', 'wptSlopeDn' , 'qcdUp', 'qcdDn', 'muRUp', 'muRDn', 'muFUp', 'muFDn'] ]
            fittodata = []
            scalethem = {}
            extraopts = ' --maxRatioRange 0.9 1.1 --fixRatioRange --plotmode=nostack -W 1. --ratioDen W{ch}_central --ratioNums {allp} '.format(ch=ch,allp=','.join(processes) )
            makeplots = ['w{ch}_wpt'.format(ch=ch), 'ptl1', 'etal1']
            showratio = True
            runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, [])

        ## enable    = ['wboth']
        ## disable   = []
        ## processes = ['Wboth_{iv}'.format(iv=i) for i in ['central', 'qcdUp', 'qcdDn', 'muRUp', 'muRDn', 'muFUp', 'muFDn'] ]
        ## fittodata = []
        ## scalethem = {}
        ## extraopts = ' --maxRatioRange 0.9 1.1 --fixRatioRange --plotmode=nostack -W 1. --ratioDen Wboth_central --ratioNums {allp} '.format(allp=','.join(processes) )
        ## makeplots = ['ptl1', 'etal1']
        ## showratio = True
        ## runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, [])

    if doZ:
        for ch in ['both']:
            enable    = []
            disable   = ['muons']
            processes = ['Z{ch}_{iv}'.format(ch=ch, iv=i) for i in ['central', 'qcdUp', 'qcdDn', 'muRUp', 'muRDn', 'muFUp', 'muFDn'] ]
            fittodata = []
            scalethem = {}
            extraopts = ' --maxRatioRange 0.9 1.1 --fixRatioRange --plotmode=nostack -W 1. --ratioDen Z{ch}_central --ratioNums {allp} '.format(ch=ch,allp=','.join(processes) )
            makeplots = ['ptl1', 'etal1']
            showratio = True
            runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, [])
    
def fakesDataMC():
    print '=========================================='
    print 'running fake closure/validation plots'
    print '=========================================='
    trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/'
    friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/friends/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/fakes-dataMC/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )
    fmca      = 'w-helicity-13TeV/wmass_mu/mca-wmu-helicity.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/cuts_wmu.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/FRfast/plots.txt'

    enable    = []
    disable   = []
    processes = ['data', 'Wincl', 'data_fakes', 'Top', 'DiBosons', 'Z']
    fittodata = []#'data_fakes']
    scalethem = {}
    extraopts = '  -W 1. --maxRatioRange 0.9 1.1 --fixRatioRange  ' #--fitData '
    makeplots = ['ptl1', 'analysisetal1']#'mtl1pf', 'pfmet']#mtl1pf', 'pfmet']#'ptl1', 'etal1', 'mtl1pf', 'pfmet']
    showratio = True
    runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)

    
def fakeClosure():
    print '=========================================='
    print 'running fake closure/validation plots'
    print '=========================================='
    trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/'
    friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/friends/'
    fmca      = 'w-helicity-13TeV/wmass_mu/simple/mca_simple.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/FRfast/cuts_fr_closure.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/FRfast/plots.txt'

    for fakes in ['QCD', 'fakes_data', 'fakes_data_awayJetPt45', 'fakes_data_awayJetPt40']:
        postfix = opts.postfix+'-'+fakes
        targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/fakesClosure/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )
        enable    = []
        disable   = []
        processes = [fakes, 'data', 'W', 'Top', 'DiBosons', 'Z', 'TauDecaysW']
        fittodata = []
        scalethem = {}
        sfString = '_get_muonSF_selectionToTrigger(13,LepGood_pt[0],LepGood_eta[0])*_get_muonSF_recoToSelection(13,LepGood_pt[0],LepGood_eta[0])'
        extraopts  = ' -W "puw2016_nTrueInt_36fb(nTrueInt)*'+sfString+'" --maxRatioRange 0.7 1.3 --fixRatioRange '
        #extraopts += ' --ratioDen fakes_data --ratioNums fakes_data,fakes_data_awayJetPt45,fakes_data_awayJetPt40,QCD --plotmode=nostack ' #--fitData '
        makeplots = ['ptl1', 'etal1']
        showratio = True
        for plot in makeplots:
            mp = [plot]
            runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, mp, showratio, extraopts, submitit=True, name=fakes+'_'+plot)

def makeGenRecoEfficiencies(LO):
    print '=========================================='
    print 'making the unfolding efficiencies from gen to reco'
    print '=========================================='

    fcut      = 'w-helicity-13TeV/wmass_mu/helicityTemplates/cuts.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/helicityTemplates/plots.txt'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/unfoldingGenRecoEfficiencies/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )

    if LO:
        trees     = '/eos/cms/store/group/dpg_ecal/comm_ecal/localreco/TREES_1LEP_80X_V3_NoSkim4/'
        friends   = trees+'/friends/'
        fmca      = 'w-helicity-13TeV/wmass_mu/mca-includes/mca-80X-wmunu-sig-LO.txt'

    else:
        trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_1muskim/'
        friends   = trees+'/friends/'
        fmca      = 'w-helicity-13TeV/wmass_mu/mca-includes/mca-80X-wmunu-sig.txt'

    for ch in ['plus', 'minus']:
        processes = ['W{c}_left'.format(c=ch), 'W{c}_right'.format(c=ch), 'W{c}_long'.format(c=ch)]
        disable   = []
        fittodata = []
        scalethem = {}
    
        for rg in ['reco', 'gen']:
            if rg == 'reco':
                enable = ['w'+ch, 'recoCuts']
                extraopts = ' -W puw2016_nTrueInt_36fb(nTrueInt)*LepGood_effSF[0] --plotmode=nostack'
            else:
                enable = ['w'+ch]
                extraopts = ' -W 1.0 --plotmode=nostack' ## don't use lepSF for GEN, but use puW
    
            makeplots = ['w{ch}_wy{r}'.format(ch=ch,r='_reco' if rg == 'reco' else '')]

            if LO:
                makeplots = [i+'_LO' for i in makeplots]
    
            showratio = False
            runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)
    
def fractionReweighting():
    print '=========================================='
    print 'running templates for signal or background '
    print '=========================================='

    doSignal = True

    if doSignal:
        ## trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_1muskim/'
        ## friends   = trees+'/friends/'
        trees     = '/eos/cms/store/cmst3/group/wmass/w-helicity-13TeV/ntuplesRecoil/TREES_SIGNAL_1l_recoil_skim_1genmu/'
        friends   = trees+'/friends/'
        targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/helicityTemplates/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )
        fmca      = 'w-helicity-13TeV/wmass_mu/mca-includes/mca-80X-wmunu-sig.txt'
        fcut      = 'w-helicity-13TeV/wmass_mu/helicityTemplates/cuts.txt'
        fplots    = 'w-helicity-13TeV/wmass_mu/helicityTemplates/plots.txt'

        for ch in ['plus', 'minus']:
            enable    = ['w'+ch]
            disable   = []
            processes = ['W{c}_left'.format(c=ch), 'W{c}_right'.format(c=ch), 'W{c}_long'.format(c=ch)]
            fittodata = []
            scalethem = {}
            #makeplots = ['w{ch}_wyVsEta'.format(ch=ch)]#, 'etaPt', 'etaPtYgen', 'mtwtk', 'etal1', 'ptl1', 'etal1gen', 'ptl1gen', 'wpt']#, 'etaPtY']
            plots = ['wy', 'wyVsEta', 'etaPt', 'etaPtYgen', 'mtwtk', 'etal1', 'ptl1', 'etal1gen', 'ptl1gen', 'wpt', 'etaPtY']
            makeplots = ['w{ch}_'.format(ch=ch)+ i for i in plots]#, 'etaPt', 'etaPtYgen', 'mtwtk', 'etal1', 'ptl1', 'etal1gen', 'ptl1gen', 'wpt']#, 'etaPtY']
            extraopts = ' -W 1. --plotmode=nostack'

            showratio = False
            runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)
    else:
        trees     = ['/eos/user/m/mdunser/w-helicity-13TeV/trees/trees_all_skims/']
        friends   =  '/eos/user/m/mdunser/w-helicity-13TeV/trees/trees_all_skims/friends/'
        targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/templates-bkg/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )
        fmca      = 'w-helicity-13TeV/wmass_mu/mca-wmu-helicity.txt'
        fcut      = 'w-helicity-13TeV/wmass_mu/cuts_simple.txt'
        fplots    = 'w-helicity-13TeV/wmass_mu/simple/plots.txt'

        enable    = []
        disable   = []
        processes = ['data_fakes', 'Top', 'Z', 'DiBosons', 'QCD']
        fittodata = []
        scalethem = {}
        extraopts = ' -W 1. --plotmode=nostack '
        makeplots = ['etaPt']

        showratio = False
        runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)
    
def dyComparison():
    print '=========================================='
    print 'running checks on DY '
    print '=========================================='
    trees     = ['/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_2l_skim_latest/']
    friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_2l_skim_latest/friends/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/dy-dataMC/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )
    fmca      = 'w-helicity-13TeV/wmass_mu/dy/mca.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/dy/cuts.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/dy/plots.txt'

    enable    = []
    disable   = []
    processes = ['data', 'Z']## very small:, 'Top', 'DiBosons']
    fittodata = ['Z']
    scalethem = {}
    extraopts = ' -W puw2016_nTrueInt_36fb(nTrueInt)*LepGood_sf1[1]*LepGood_sf2[0]*LepGood_sf3[0]*LepGood_sf2[1]*LepGood_sf3[1] --maxRatioRange 0.9 1.1 --fixRatioRange '##*LepGood_sf1[0]*LepGood_sf2[0]*LepGood_sf3[0]*LepGood_sf2[1]*LepGood_sf3[1] '
    makeplots = ['ptl1','ptl2']#ptl1', 'etal1', 'ptl2', 'etal2', 'mll']
    showratio = True
    runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)

def muonFlipRate():
    print '=========================================='
    print 'running checks on DY '
    print '=========================================='
    trees     = '/eos/cms/store/group/dpg_ecal/comm_ecal/localreco/TREES_1LEP_80X_V3/'
    friends   = trees+'/friends/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/fliprate-muon/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )
    fmca      = 'w-helicity-13TeV/wmass_mu/dy/mca.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/dy/cuts.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/dy/plots.txt'

    enable    = []
    disable   = []
    processes = ['Z', 'data']
    fittodata = []
    scalethem = {}
    extraopts = ' -A alwaystrue samesign LepGood1_pdgId*LepGood2_pdgId==169 '
    makeplots = ['mll']
    showratio = True
    runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts)

def flipTests():
    print '=========================================='
    print 'running some muon flip tests'
    print '=========================================='
    trees     = '/eos/cms/store/group/dpg_ecal/comm_ecal/localreco/TREES_1LEP_80X_V3_NoSkim5/'
    friends   = trees+'/friends/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/muon-flips/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )
    fmca      = 'w-helicity-13TeV/wmass_mu/mca-includes/mca-80X-wmunu-sigincl.txt'
    fcut      = 'w-helicity-13TeV/wmass_mu/cuts_wmu.txt'
    fplots    = 'w-helicity-13TeV/wmass_mu/simple/plots.txt'

    enable    = []
    disable   = []
    invert    = []
    processes = ['Wincl']
    fittodata = []
    scalethem = {}
    extraopts = ' -A  mtl1pf40 flips LepGood1_mcMatchId*LepGood1_charge<0  -A alwaystrue tightChargeFix LepGood1_tightChargeFix==2 -A alwaystrue Wmuondecay abs(genw_decayId)==14 '
    makeplots = ['ptVsEta']
    showratio = False
    runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, invert)

    
def fakeShapes():
    print '=========================================='
    print 'running fake shape plots'
    print '=========================================='
    trees     = ['/afs/cern.ch/work/m/mdunser/public/wHelicityTrees/TREES_1LEP_53X_V2/']
    friends   = '/eos/cms/store/cmst3/group/susy/emanuele/wmass/trees/TREES_1LEP_53X_V2/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/fakes-sanity/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )
    fmca      = 'w-helicity/FR/mca_fr_closure.txt'
    fcut      = 'w-helicity/FR/cuts_fr_closure.txt'
    fplots    = 'w-helicity/FR/plots_fr_closure.txt'

    enable    = []
    disable   = ['muonTightIso']
    invert    = []
    processes = ['data', 'wjets', 'qcd', 'singleTop', 'ttjets', 'diboson', 'dyjets']
    fittodata = ['qcd']
    scalethem = {}
    extraopts = ' --maxRatioRange 0. 2. '
    makeplots = ['l1reliso03',]# 'mtl1tk', 'pfmet', 'ptl1', 'etal1']
    showratio = True
    runplots(trees, friends, targetdir, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, makeplots, showratio, extraopts, invert)



def makeFakeRatesFast(recalculate):
    ## old trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_1muskim/'
    ## old friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_1muskim/friends/'
    trees     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/'
    friends   = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/friends/'
    targetdir = '/afs/cern.ch/user/m/mdunser/www/private/w-helicity-13TeV/fakerates/{date}{pf}/'.format(date=date, pf=('-'+postfix if postfix else '') )

    fmca   = 'w-helicity-13TeV/wmass_mu/FRfast/mca_fr.txt' 
    fcut   = 'w-helicity-13TeV/wmass_mu/FRfast/cuts_fr.txt'
    fplots = 'w-helicity-13TeV/wmass_mu/FRfast/plots.txt'       
    ftight = 'w-helicity-13TeV/wmass_mu/FRfast/tightCut.txt'    
    processes = ['QCD', 'WandZ', 'data']
    compprocs = ['QCD', 'WandZ', 'data', 'data_sub']
    fittodata = ['QCD', 'WandZ']
    makeplots = ['mtl1pf', 'reliso04'] #'reliso03'] ## the first plot here is the one from which the scale factors are derived!!!
    
    import sys
    sys.path.append('w-helicity-13TeV/wmass_mu/')
    import make_cards_mu
    
    #binning = [25,30,35,40,50,100] ## from xvars.txt
    ## binning = [25,27,29,31,33,35,37,39,41,43,45,48,51,54,60,65] ## from xvars.txt
    ## binningeta = eval(make_cards_mu.etabinning) ## the binning is a list in form of a string
    binning = [24, 27, 30, 33, 36, 39, 42, 45, 48, 53, 60, 70] ## from xvars.txt
    binningeta = [-2.4 + i*0.1 for i in range(49) ]
    binningeta = [float('{a:.3f}'.format(a=i)) for i in binningeta]
    h_name  = 'fakerate_mu'; h_title = 'fakerates muons'

    h_fakerate_data = ROOT.TH2F(h_name+'_data',h_title+' - data', len(binning)-1, array.array('f',binning), len(binningeta)-1, array.array('f',binningeta))
    h_fakerate_mc   = ROOT.TH2F(h_name+'_qcd' ,h_title+' - qcd' , len(binning)-1, array.array('f',binning), len(binningeta)-1, array.array('f',binningeta))
    h_fakerate_data .Sumw2()
    h_fakerate_mc   .Sumw2()
    h_fakerate_data .GetZaxis().SetRangeUser(0.01,0.7)
    h_fakerate_mc   .GetZaxis().SetRangeUser(0.01,0.7)
    h_fakerate_data .GetXaxis().SetTitle('p_{T} mu'); h_fakerate_data .GetYaxis().SetTitle('#eta mu')
    h_fakerate_mc   .GetXaxis().SetTitle('p_{T} mu'); h_fakerate_mc   .GetYaxis().SetTitle('#eta mu')

    h_name  = 'promptrate_mu'; h_title = 'promptrates muons'
    h_promptrate_data = ROOT.TH2F(h_name+'_data',h_title+' - data', len(binning)-1, array.array('f',binning), len(binningeta)-1, array.array('f',binningeta))
    h_promptrate_mc   = ROOT.TH2F(h_name+'_qcd' ,h_title+' - qcd' , len(binning)-1, array.array('f',binning), len(binningeta)-1, array.array('f',binningeta))
    h_promptrate_data .Sumw2()
    h_promptrate_mc   .Sumw2()
    h_promptrate_data .GetZaxis().SetRangeUser(0.5,1.0)
    h_promptrate_mc   .GetZaxis().SetRangeUser(0.5,1.0)
    h_promptrate_data .GetXaxis().SetTitle('p_{T} mu'); h_promptrate_data .GetYaxis().SetTitle('#eta mu')
    h_promptrate_mc   .GetXaxis().SetTitle('p_{T} mu'); h_promptrate_mc   .GetYaxis().SetTitle('#eta mu')

    ## add MT cut to the eff plot!
    fakerates = {}; promptrates = {}
    scales = {}
    printAggressive('STARTING FAKE RATES...!')
    for j,eta in enumerate(binningeta[:-1]):

        etastring = 'To'.join(str(i).replace('-','m').replace('.','p') for i in [eta, binningeta[j+1]] )
        tmp_td = targetdir+'/'+etastring

        ## this is some weird recursive magic to submit this to the batch
        if opts.submitFR:
            abspath = os.path.abspath('.')
            tmp_cmd = 'python '+abspath+'/runWHelicity_mu_13TeV.py --fr --recalculate --doBin {j} {pf}'.format(j=j,pf='--postfix '+opts.postfix if opts.postfix else '')
            submitFRrecursive(tmp_td, 'frjob_{j}'.format(j=j), tmp_cmd)
            continue
        if opts.doBin > -1:
            if not j == opts.doBin: continue
        ## end weird magic

        scalethem = {}
        enable    = []
        disable   = ['muonTightIso']
        newplots = [('mu_'+plot) for plot in makeplots]
        extraopts = ' -A alwaystrue ETA{eta} LepGood1_eta>={e1}&&LepGood1_eta<{e2} '.format(eta=etastring, e1=eta, e2=binningeta[j+1]) ## no whitespaces in the cutstring here!!
        extraopts+= ' -W {wgt} '.format(wgt=make_cards_mu.WEIGHTSTRING.replace("'",""))
        if recalculate: runplots(trees, friends, tmp_td, fmca, fcut, fplots, enable, disable, processes, scalethem, fittodata, newplots, True, extraopts)
        printAggressive('DONE MAKING THE PLOTS TO DERIVE THE EWK SCALE FACTORS!')
        scales['qcd_{eta}'  .format(eta=etastring)] = readScaleFactor(tmp_td+'/mu_{plot}.txt'.format(plot=makeplots[0]), 'QCD')
        scales['wandz_{eta}'.format(eta=etastring)] = readScaleFactor(tmp_td+'/mu_{plot}.txt'.format(plot=makeplots[0]), 'WandZ')
        enable  = ['mtl1pf40max']## IMPORTANT
        disable = ['muonTightIso']
        scalethem = {'QCD'  : scales['qcd_{eta}'  .format(eta=etastring)],
                     'WandZ': scales['wandz_{eta}'.format(eta=etastring)]}
        fxvar  = 'w-helicity-13TeV/wmass_mu/FRfast/xvars.txt'
        ## reproduce plots with MT and MET included
        printAggressive('SCALING THE PROCESSES BY FACTORS')
        print scalethem
        if recalculate: runplots(trees, friends, tmp_td+'/mTCutIncluded/', fmca, fcut, fplots, enable, disable, processes, scalethem, [], newplots, True, extraopts) ## don't fit to data anymore
        extraopts += ' --ratioRange 0 2 --sp QCD '
        if recalculate: runefficiencies(trees, friends, tmp_td+'/fr_mu_{eta}'.format(eta=etastring), fmca, fcut, ftight, fxvar, enable, disable, scalethem, compprocs, True, extraopts)
        fakerates['fr_mu_qcd_{eta}'.format(eta=etastring)] = readFakerate(tmp_td+'/fr_mu_{eta}.txt'.format(eta=etastring),'QCD')
        fakerates['fr_mu_dat_{eta}'.format(eta=etastring)] = readFakerate(tmp_td+'/fr_mu_{eta}.txt'.format(eta=etastring),'Data - EWK')

        promptrates['fr_mu_qcd_{eta}'.format(eta=etastring)] = readFakerate(tmp_td+'/fr_mu_{eta}.txt'.format(eta=etastring),'WandZ')
        promptrates['fr_mu_dat_{eta}'.format(eta=etastring)] = readFakerate(tmp_td+'/fr_mu_{eta}.txt'.format(eta=etastring),'WandZ')

        print len(binning), binning
        print len(fakerates['fr_mu_dat_{eta}'.format(eta=etastring)][0]), fakerates['fr_mu_dat_{eta}'.format(eta=etastring)][0]
        for i in range(len(fakerates['fr_mu_dat_{eta}'.format(eta=etastring)][0])):
            h_fakerate_data.SetBinContent(i+1,j+1, fakerates['fr_mu_dat_{eta}'.format(eta=etastring)][0][i])
            h_fakerate_data.SetBinError  (i+1,j+1, fakerates['fr_mu_dat_{eta}'.format(eta=etastring)][1][i])
            h_fakerate_mc  .SetBinContent(i+1,j+1, fakerates['fr_mu_qcd_{eta}'.format(eta=etastring)][0][i])
            h_fakerate_mc  .SetBinError  (i+1,j+1, fakerates['fr_mu_qcd_{eta}'.format(eta=etastring)][1][i])
            h_promptrate_data.SetBinContent(i+1,j+1, promptrates['fr_mu_dat_{eta}'.format(eta=etastring)][0][i])
            h_promptrate_data.SetBinError  (i+1,j+1, promptrates['fr_mu_dat_{eta}'.format(eta=etastring)][1][i])
            h_promptrate_mc  .SetBinContent(i+1,j+1, promptrates['fr_mu_qcd_{eta}'.format(eta=etastring)][0][i])
            h_promptrate_mc  .SetBinError  (i+1,j+1, promptrates['fr_mu_qcd_{eta}'.format(eta=etastring)][1][i])

    if not opts.submitFR and opts.doBin < 0:
        h_fakerate_data_frUp = h_fakerate_data.Clone(h_fakerate_data.GetName()+'_frUp')
        h_fakerate_mc_frUp   = h_fakerate_mc  .Clone(h_fakerate_mc  .GetName()+'_frUp')
        h_fakerate_data_frUp.Scale(1.1)
        h_fakerate_mc_frUp  .Scale(1.1)

        h_fakerate_data_frDn = h_fakerate_data.Clone(h_fakerate_data.GetName()+'_frDn')
        h_fakerate_mc_frDn   = h_fakerate_mc  .Clone(h_fakerate_mc  .GetName()+'_frDn')
        h_fakerate_data_frDn.Scale(0.9)
        h_fakerate_mc_frDn  .Scale(0.9)

        ROOT.gROOT.SetBatch()
        ROOT.gStyle.SetOptStat(0)
        canv = ROOT.TCanvas()
        #canv.SetLogx()
        ROOT.gStyle.SetPaintTextFormat(".3f")
        h_fakerate_data.Draw('colz text45 e')
        canv.SaveAs(targetdir+'fakerate_mu_data_{date}.png'.format(date=date))
        canv.SaveAs(targetdir+'fakerate_mu_data_{date}.pdf'.format(date=date))
        h_fakerate_mc  .Draw('colz text45 e')
        canv.SaveAs(targetdir+'fakerate_mu_qcd_{date}.png'.format(date=date))
        canv.SaveAs(targetdir+'fakerate_mu_qcd_{date}.pdf'.format(date=date))
        h_promptrate_data.Draw('colz text45 e')
        canv.SaveAs(targetdir+'promptrate_mu_data_{date}.png'.format(date=date))
        canv.SaveAs(targetdir+'promptrate_mu_data_{date}.pdf'.format(date=date))
        h_promptrate_mc  .Draw('colz text45 e')
        canv.SaveAs(targetdir+'promptrate_mu_qcd_{date}.png'.format(date=date))
        canv.SaveAs(targetdir+'promptrate_mu_qcd_{date}.pdf'.format(date=date))
        outfile = ROOT.TFile('w-helicity-13TeV/wmass_mu/fakerateMap_mu_{date}{pf}.root'.format(date=date,pf=('_'+postfix if postfix else '')),'RECREATE')
        h_fakerate_data.Write()
        h_fakerate_mc  .Write()
        h_fakerate_data_frUp.Write()
        h_fakerate_mc_frUp  .Write()
        h_fakerate_data_frDn.Write()
        h_fakerate_mc_frDn  .Write()
        outfile.Close()

        outfile = ROOT.TFile('w-helicity-13TeV/wmass_mu/promptrateMap_mu_{date}{pf}.root'.format(date=date,pf=('_'+postfix if postfix else '')),'RECREATE')
        h_promptrate_data.Write()
        h_promptrate_mc  .Write()
        #h_promptrate_data_frUp.Write()
        #h_promptrate_mc_frUp  .Write()
        #h_promptrate_data_frDn.Write()
        #h_promptrate_mc_frDn  .Write()
        outfile.Close()
        
        print scales
        print fakerates
        print promptrates

        h_fr_smoothed_data = ROOT.TH2F('fakerates_smoothed_data'  ,' fakerates - smoothed data'  , len(binningeta)-1, array.array('f',binningeta), 2, array.array('f',[0., 1., 2.]))
        h_pr_smoothed_data = ROOT.TH2F('promptrates_smoothed_data',' promptrates - smoothed data', len(binningeta)-1, array.array('f',binningeta), 2, array.array('f',[0., 1., 2.]))
        #h_fr_smoothed_mc   = ROOT.TH2F(h_name+'_qcd' ,h_title+' - qcd' , len(binning)-1, array.array('f',binning), len(binningeta)-1, array.array('f',binningeta))

        h_fr_smoothed_data_offset = ROOT.TH2F('fakerates_smoothed_data_offset'  ,' fakerates - offset'  , len(binningeta)-1, array.array('f',binningeta), 1, array.array('f',[0., 1.]))
        h_fr_smoothed_data_slope  = ROOT.TH2F('fakerates_smoothed_data_slope'   ,' fakerates - slope '  , len(binningeta)-1, array.array('f',binningeta), 1, array.array('f',[0., 1.]))
        h_pr_smoothed_data_offset = ROOT.TH2F('promptrates_smoothed_data_offset'  ,' promptrates - offset'  , len(binningeta)-1, array.array('f',binningeta), 1, array.array('f',[0., 1.]))
        h_pr_smoothed_data_slope  = ROOT.TH2F('promptrates_smoothed_data_slope'   ,' promptrates - slope '  , len(binningeta)-1, array.array('f',binningeta), 1, array.array('f',[0., 1.]))


        for j,eta in enumerate(binningeta[:-1]):


            print 'GETTING AND FITTING THE FR FROM', etastring

            etastring = 'To'.join(str(i).replace('-','m').replace('.','p') for i in [eta, binningeta[j+1]] )
            tmp_td = targetdir+'/'+etastring

            graph_file= ROOT.TFile(tmp_td+'/fr_mu_{eta}'.format(eta=etastring), 'read')

            mg = ROOT.TMultiGraph(); pols = []
            for rate in ['pr', 'fr']:

                pol0 = ROOT.TF1("{r}_pol0_{eta}".format(r=rate,eta=etastring), "[0]        ", 25., 50.)
                pol1 = ROOT.TF1("{r}_pol1_{eta}".format(r=rate,eta=etastring), "[1]*x + [0]", 25., 50.)


                if rate == 'fr':
                    graph = graph_file.Get('muonTightIso_pt_fine_binned_data_sub')
                    pol0.SetLineColor(ROOT.kGreen); pol0.SetLineWidth(2)
                    pol1.SetLineColor(ROOT.kRed-3); pol1.SetLineWidth(2)
                    ## pol0.SetParLimits(1, 0.1, 0.8)
                    ## pol1.SetParLimits(1, -0.1  , 0.8)
                    ## pol1.SetParLimits(0,  0.1  , 1.1)

                else:
                    graph = graph_file.Get('muonTightIso_pt_fine_binned_WandZ')
                    graph.SetLineColor(ROOT.kRed); graph.SetMarkerColor(ROOT.kRed)
                    pol0.SetLineColor(ROOT.kBlue)   ; pol0.SetLineWidth(2)
                    pol1.SetLineColor(ROOT.kAzure-3); pol1.SetLineWidth(2)
                    ## pol0.SetParLimits(1, 0.1, 1.1)
                    ## pol1.SetParLimits(1, -0.1  , 0.1)
                    ## pol1.SetParLimits(0,  0.1  , 1.1)

                print 'this is graph', graph
                mg.Add(copy.deepcopy(graph))

                graph.Fit("{r}_pol0_{eta}".format(r=rate,eta=etastring), "M", "", 25., 50.)
                graph.Fit("{r}_pol1_{eta}".format(r=rate,eta=etastring), "M", "", 25., 50.)

                ## pol0_chi2 = pol0.GetChisquare(); pol0_ndf = pol0.GetNDF()
                ## pol1_chi2 = pol1.GetChisquare(); pol1_ndf = pol1.GetNDF()

                ## print 'pol0', pol0
                ## print 'pol1', pol1
                ## print 'pol0_ndf for etastring:', pol0_ndf, etastring
                ## print 'pol1_ndf for etastring:', pol1_ndf, etastring

                ## rchi2_0 = pol0_chi2/pol0_ndf
                ## rchi2_1 = pol1_chi2/pol1_ndf

                ## bestfunc = pol0 if rchi2_0 < rchi2_1 else pol1
                ## worstfun = pol0 if rchi2_0 > rchi2_1 else pol1

                ## print '{r} and {eta}: chi2 of pol0 = {chi0}/{ndf0} = {red0}'.format(r=rate,eta=etastring,chi0=pol0_chi2,ndf0=pol0_ndf, red0=rchi2_0)
                ## print '{r} and {eta}: chi2 of pol1 = {chi1}/{ndf1} = {red1}'.format(r=rate,eta=etastring,chi1=pol1_chi2,ndf1=pol1_ndf, red1=rchi2_1)

                ## print 'the better function is {func}'.format(func=bestfunc.GetName())

                ## #print '{eta}: compared to {func}         .   value={val:.3f}'.format(eta=eta, func = worstfun.GetName(), val=worstfun.GetChisquare()/worstfun.GetNDF())

                bestfunc = pol1
                
                etabin = j+1 #if eta == 'barrel' else 2
                
                if rate == 'fr':
                    h_fr_smoothed_data.SetBinContent(etabin, 1, bestfunc.GetParameter(0))
                    h_fr_smoothed_data.SetBinError  (etabin, 1, bestfunc.GetParError (0))

                    h_fr_smoothed_data.SetBinContent(etabin, 2, bestfunc.GetParameter(1) if bestfunc.GetNpar() > 1 else 0.)
                    h_fr_smoothed_data.SetBinError  (etabin, 2, bestfunc.GetParError (1) if bestfunc.GetNpar() > 1 else 0.)

                    h_fr_smoothed_data_offset.SetBinContent(etabin, 1, bestfunc.GetParameter(0))
                    h_fr_smoothed_data_offset.SetBinError  (etabin, 1, bestfunc.GetParError (0))

                    h_fr_smoothed_data_slope .SetBinContent(etabin, 1, bestfunc.GetParameter(1) if bestfunc.GetNpar() > 1 else 0.)
                    h_fr_smoothed_data_slope .SetBinError  (etabin, 1, bestfunc.GetParError (1) if bestfunc.GetNpar() > 1 else 0.)

                else:
                    h_pr_smoothed_data.SetBinContent(etabin, 1, bestfunc.GetParameter(0))
                    h_pr_smoothed_data.SetBinError  (etabin, 1, bestfunc.GetParError (0))

                    h_pr_smoothed_data.SetBinContent(etabin, 2, bestfunc.GetParameter(1) if bestfunc.GetNpar() > 1 else 0.)
                    h_pr_smoothed_data.SetBinError  (etabin, 2, bestfunc.GetParError (1) if bestfunc.GetNpar() > 1 else 0.)

                    h_pr_smoothed_data_offset.SetBinContent(etabin, 1, bestfunc.GetParameter(0))
                    h_pr_smoothed_data_offset.SetBinError  (etabin, 1, bestfunc.GetParError (0))

                    h_pr_smoothed_data_slope .SetBinContent(etabin, 1, bestfunc.GetParameter(1) if bestfunc.GetNpar() > 1 else 0.)
                    h_pr_smoothed_data_slope .SetBinError  (etabin, 1, bestfunc.GetParError (1) if bestfunc.GetNpar() > 1 else 0.)


                pols.append(copy.deepcopy(pol0))
                pols.append(copy.deepcopy(pol1))
                mg.Add(copy.deepcopy(graph))

            #graph.Draw('ape')
            mg.Draw('ape')
            mg.GetYaxis().SetRangeUser(0., 1.0)
            for p in pols:
                p.Draw('same')
            ##pol1.Draw('same')
            canv.SaveAs(targetdir+'fakeAndPromptRate_fit_data_{eta}.png'.format(eta=etastring))
            canv.SaveAs(targetdir+'fakeAndPromptRate_fit_data_{eta}.pdf'.format(eta=etastring))
        
        h_fr_smoothed_data.Draw("colz text45")
        h_fr_smoothed_data.GetZaxis().SetRangeUser(0.0, 0.6)
        h_fr_smoothed_data.GetXaxis().SetTitle('#eta_{#mu}')
        h_fr_smoothed_data.GetXaxis().SetTitleSize(0.045)
        h_fr_smoothed_data.GetXaxis().SetLabelSize(0.05)
        h_fr_smoothed_data.GetYaxis().SetLabelSize(0.08)
        h_fr_smoothed_data.GetYaxis().SetBinLabel(1, 'offset')
        h_fr_smoothed_data.GetYaxis().SetBinLabel(2, 'slope')
        canv.SaveAs(targetdir+'fakerate_smoothed_data_{date}.png'.format(date=date))
        canv.SaveAs(targetdir+'fakerate_smoothed_data_{date}.pdf'.format(date=date))

        canvtemp = ROOT.TCanvas()
        canvtemp.Divide(1,2)
        canvtemp.cd(1)
        h_fr_smoothed_data_slope .Draw("colz text45 e")
        h_fr_smoothed_data_slope.GetZaxis().SetRangeUser(0.0, 0.01)
        canvtemp.cd(2)
        h_fr_smoothed_data_offset.Draw("colz text45 e")
        h_fr_smoothed_data_offset.GetZaxis().SetRangeUser(0.0, 0.6)
        canvtemp.SaveAs(targetdir+'fakerate_smoothed_data_{date}_twopanels.png'.format(date=date))
        canvtemp.SaveAs(targetdir+'fakerate_smoothed_data_{date}_twopanels.pdf'.format(date=date))

        canvtemp.cd(1)
        h_fr_smoothed_data_slope .Draw("colz text45 e")
        h_fr_smoothed_data_slope.GetZaxis().SetRangeUser(0.0, 0.01)
        canvtemp.cd(2)
        h_fr_smoothed_data_offset.Draw("colz text45 e")
        h_fr_smoothed_data_offset.GetZaxis().SetRangeUser(0.0, 0.8)
        canvtemp.SaveAs(targetdir+'promptrate_smoothed_data_{date}_twopanels.png'.format(date=date))
        canvtemp.SaveAs(targetdir+'promptrate_smoothed_data_{date}_twopanels.pdf'.format(date=date))

        
        canv.cd()

        
        canv.cd()
        h_pr_smoothed_data.Draw("colz text45")
        h_pr_smoothed_data.GetZaxis().SetRangeUser(0.00, 1.0)
        h_pr_smoothed_data.GetXaxis().SetTitle('#eta_{#mu}')
        h_pr_smoothed_data.GetXaxis().SetTitleSize(0.045)
        h_pr_smoothed_data.GetXaxis().SetLabelSize(0.05)
        h_pr_smoothed_data.GetYaxis().SetLabelSize(0.08)
        h_pr_smoothed_data.GetYaxis().SetBinLabel(1, 'offset')
        h_pr_smoothed_data.GetYaxis().SetBinLabel(2, 'slope')
        canv.SaveAs(targetdir+'promptrate_smoothed_data_{date}.png'.format(date=date))
        canv.SaveAs(targetdir+'promptrate_smoothed_data_{date}.pdf'.format(date=date))
        
        outfile = ROOT.TFile('w-helicity-13TeV/wmass_mu/frAndPr_fit_mu_{date}{pf}.root'.format(date=date,pf=('_'+postfix if postfix else '')),'RECREATE')
        h_fr_smoothed_data.Write()
        h_pr_smoothed_data.Write()
        outfile.Close()
    

        #python mcEfficiencies.py -f -j 4 -l $TRIGLUMI --s2v -P $ELFRTREES dps-ww/elFR/mca_elFR.txt dps-ww/elFR/cuts_elFR.txt dps-ww/elFR/tightCut.txt dps-ww/elFR/xvar${pt}.txt --sp QCD --scale-process QCD $QCDSCALE --scale-process WandZ $WZSCALE -o ~/www/private/dps-ww/${DATE}-elFR${POSTFIX}/${eta}_${pt}/fr_el_${eta}_${pt} --groupBy cut --compare QCD,data,data_sub,total,WandZ --showRatio --ratioRange 0 3 --mcc ttH-multilepton/mcc-eleIdEmu2.txt -X pt${negpt} -X eta${negeta} -X lepMVAtight ;# --sP lpt${pt} # -E mtw1 


if __name__ == '__main__':
    parser = optparse.OptionParser(usage='usage: %prog [opts] ', version='%prog 1.0')
    parser.add_option('--pf'        , '--postfix'    , dest='postfix'      , type='string'       , default=''    , help='postfix for running each module')
    parser.add_option('-d'          , '--date'       , dest='date'         , type='string'       , default=''    , help='run with specified date instead of today')
    parser.add_option('-l'          , '--lumi'       , dest='lumi'         , type='float'        , default=0.    , help='change lumi by hand')
    parser.add_option('--simple'    ,                  dest='simple'       , action='store_true' , default=False , help='make simple plot')
    parser.add_option('--sFR'       ,                  dest='sFR'          , action='store_true' , default=False , help='make simple FR plots')
    parser.add_option('--fr'        , '--fakerates'  , dest='runFR'        , action='store_true' , default=False , help='run fakerates for muons')
    parser.add_option('--rec'       , '--recalculate'  , dest='recalculate'        , action='store_true' , default=False , help='recalculate fakerates')
    parser.add_option('--submitFR'  , '--submitFR'  , dest='submitFR'        , action='store_true' , default=False , help='submit the fakerates to the batch')
    parser.add_option('--doBin'     ,                 dest='doBin'         , type='int', default=-999 , help='submit exactly this bin of the FR calculation to the batch')
    parser.add_option('--pr'        , '--promptrates', dest='runPR'        , action='store_true' , default=False , help='run promptrates for muons')
    parser.add_option('--fs'        , '--fakeshapes' , dest='fakeShapes'   , action='store_true' , default=False , help='run fake shapes')
    parser.add_option('--fc'        , '--fakeclosure', dest='fakeClosure'   , action='store_true' , default=False , help='run fake closure')
    parser.add_option('--fdm'       , '--fakesDataMC', dest='fakesDataMC'   , action='store_true' , default=False , help='run fakes data MC comparison')
    parser.add_option('--mt'        , '--makeTemplates', dest='makeTemplates', action='store_true' , default=False , help='make templates')
    parser.add_option('--dy'        , '--dyComparison' , dest='dyComparison' , action='store_true' , default=False , help='make dy comparisons')
    parser.add_option('--pdf'       , '--pdfVariations', dest='pdfVariations', action='store_true' , default=False , help='make plots with pdf variations')
    parser.add_option('--unfold'    , '--unfoldEffs'   , dest='unfoldEff'    , action='store_true' , default=False , help='make unfolding efficiencies gen-reco')
    parser.add_option('--unfoldLO'  , '--unfoldLO'   , dest='unfoldLO'    , action='store_true' , default=False , help='make unfolding for LO')
    parser.add_option('--compareScales', '--scales'   , dest='compareScales'    , action='store_true' , default=False , help='compare qcd scales')
    parser.add_option('--sf'        , '--sfClosure'   , dest='sfClosure'    , action='store_true' , default=False , help='make 2l sf closure')
    parser.add_option('--sc'        , '--scaleClosure', dest='scaleClosure' , action='store_true' , default=False , help='make 2l muon momentum scale closure test')
    parser.add_option('--plots1l'   , dest='plots1l' , action='store_true' , default=False , help='make plots for 1lepton region(s)')
    (opts, args) = parser.parse_args()

    global date, postfix, lumi, date
    postfix = opts.postfix
    lumi = 36.0 if not opts.lumi else opts.lumi
    date = datetime.date.today().isoformat()
    if opts.date:
        date = opts.date

    if opts.simple:
        print 'making simple plots'
        simplePlot()
    if opts.sFR:
        print 'making simple FR plots'
        simpleFRPlot()
    if opts.runFR:
        print 'running the fakerates for muons'
        makeFakeRatesFast(opts.recalculate)
    if opts.runPR:
        print 'running the promptrates for muons'
        makePromptRates()
    if opts.fakeShapes:
        print 'running the fakeshapes for muons'
        fakeShapes()
    if opts.fakeClosure:
        print 'running the fakes closure for muons'
        fakeClosure()
    if opts.fakesDataMC:
        print 'running the fakes data-mc comparison'
        fakesDataMC()
    if opts.makeTemplates:
        print 'make helicity templates'
        fractionReweighting()
    if opts.dyComparison:
        print 'running the dy comparisons'
        dyComparison()
    if opts.pdfVariations:
        print 'making pdf variations'
        makePDFvariations()
    if opts.unfoldEff:
        print 'making unfolding efficiencies'
        makeGenRecoEfficiencies(opts.unfoldLO)
    if opts.compareScales:
        print 'making comparison of qcd scales'
        compareScales()
    if opts.sfClosure:
        print 'sf closure'
        sfClosure2l()
    if opts.scaleClosure:
        print 'muon scale closure'
        scaleClosure(opts.recalculate)
    if opts.plots1l:
        print 'plots for 1l region(s)'
        plots1l()
