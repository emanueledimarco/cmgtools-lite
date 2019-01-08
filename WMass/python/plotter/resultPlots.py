import ROOT, optparse, os, re

## usage:
## python resultPlots.py --config results_config_mu.txt --outdir <outputdirectory> (--runtoys)

if __name__ == '__main__':
    parser = optparse.OptionParser(usage='usage: %prog [opts] ', version='%prog 1.0')
    parser.add_option('', '--config' , type='string'       , default=''    , help='config file with location of fitresults files')
    parser.add_option('', '--outdir' , type='string'       , default=''    , help='output directory with directory structure and plots')
    parser.add_option('', '--runtoys', action='store_true' , default=False , help='run also toys, not only hessian. takes longer')
    parser.add_option('', '--make'   , type='string'       , default='all' , help='run all (default) or only parts (nuis,rap,corr,syst,post,imp)')
    (options, args) = parser.parse_args()


    ## this loads the path for all the results in a config
    results = {}
    execfile(options.config, results)

    ## make the output directory first
    os.system('mkdir -p {od}'.format(od=options.outdir))

    ## get the channel from the filename of the config.txt
    muEl = 'mu' if 'mu' in options.config else 'el'

    ## check if running also toys
    toysHessian = ['hessian']
    if options.runtoys:
        toysHessian += ['toys']

    ## plot syst ratios
    ## ================================
    if options.make in ['all', 'syst']:
        print 'running systRatios for a few things'
        tmp_outdir = options.outdir+'/systRatios/'
        os.system('mkdir -p {od}'.format(od=tmp_outdir))
        os.system('cp ~mdunser/public/index.php {od}'.format(od=tmp_outdir))
        systs  = ['pdf', 'alphaS', 'mW']
        systs += ['muR'   +str(i) for i in range(1,11)]
        systs += ['muF'   +str(i) for i in range(1,11)]
        systs += ['muRmuF'+str(i) for i in range(1,11)]
        systs += ['CMS_We_FRe_continuous,CMS_We_FRe_slope','CMS_We_sig_lepeff']
        systs += [','+','.join(['FakesEtaUncorrelated%d'%i for i in xrange(1,11)])]
        for nuis in systs:
            os.system('python w-helicity-13TeV/systRatios.py --unrolled --outdir {od} -s {p} {d} {ch}'.format(od=tmp_outdir, p=nuis, d=results['cardsdir'], ch=muEl))

    ## plot correlation matrices
    ## ================================
    if options.make in ['all', 'corr']:
        print 'making correlation matrices'
        tmp_outdir = options.outdir+'/correlationMatrices/'
        os.system('mkdir -p {od}'.format(od=tmp_outdir))
        os.system('cp ~mdunser/public/index.php {od}'.format(od=tmp_outdir))
        for t in toysHessian:
            for tmp_file in [i for i in results.keys() if 'both_floatingPOIs_'+t in i]:
                tmp_suffix = '_'.join(tmp_file.split('_')[1:])
                nuisancesAndPOIs = ['pdf', 'muR,muF,muRmuF,alphaS,wpt', 'CMS_', 'ErfPar']
                if 'floatingPOIs' in results[tmp_file]: nuisancesAndPOIs += ['W{charge}_{pol}'.format(charge=charge,pol=pol) for charge in ['plus','minus'] for pol in ['left','right','long'] ]
                for nuis in nuisancesAndPOIs:
                    basecmd = 'python w-helicity-13TeV/subMatrix.py '
                    os.system(basecmd+' {inf} --outdir {od} --params {p} --type {t} --suffix {suf} '.format(od=tmp_outdir, t=t, p=nuis, inf=results[tmp_file], suf=tmp_suffix))

    ## plot rapidity spectra
    ## ================================
    if options.make in ['all', 'rap']:
        print 'plotting rapidity spectra'
        tmp_outdir = options.outdir+'/rapiditySpectra/'
        os.system('mkdir -p {od}'.format(od=tmp_outdir))
        os.system('cp ~mdunser/public/index.php {od}'.format(od=tmp_outdir))
        for t in toysHessian:
            for tmp_file in [i for i in results.keys() if 'both_floatingPOIs_'+t in i]:
                tmp_suffix = '_'.join(tmp_file.split('_')[1:])
                cmd  = 'python w-helicity-13TeV/plotYW.py '
                cmd += ' -C plus,minus --xsecfiles {xp},{xm} -y {cd}/binningYW.txt '.format(xp=results['xsecs_plus'],xm=results['xsecs_minus'],cd=results['cardsdir'])
                cmd += ' --infile {inf} --outdir {od} --type {t} --suffix {suf} '.format(od=tmp_outdir, t=t, suf=tmp_suffix, inf=results[tmp_file])
                os.system(cmd)
                print "===> plotting normalized xsecs..."
                cmd += ' --normxsec '
                os.system(cmd)

    ## plot postfit plots
    ## ================================
    if options.make in ['all', 'post']:
        print 'making postfit plots'
        for tmp_file in [i for i in results.keys() if 'postfit_' in i]:
            tmp_outdir = options.outdir+'/postFitPlots/'
            os.system('mkdir -p {od}'.format(od=tmp_outdir))
            os.system('cp ~mdunser/public/index.php {od}'.format(od=tmp_outdir))
            cmd  = 'python w-helicity-13TeV/postFitPlots.py --no2Dplot '
            cmd += ' {inf} {cd} --outdir {od} --suffix {suf} '.format(inf=results[tmp_file], cd=results['cardsdir'], od=tmp_outdir, suf=tmp_file.replace('postfit',''))
            os.system(cmd)
            for charge in ['plus','minus']:
                cmdpull = 'python w-helicity-13TeV/monsterPull.py -i {od}/plots_{suf}.root -d unrolled_{ch} --suffix {suf}'.format(od=tmp_outdir,suf=tmp_file.replace('postfit',''),ch=charge)
                os.system(cmdpull)

    ## plot impacts
    ## ================================
    if options.make in ['all','imp']:
        print 'making impact plots'
        tmp_outdir = options.outdir+'/impactPlots/'
        poisGroups = ['W{ch}.*{pol}.*'.format(ch=charge,pol=pol) for charge in ['plus','minus'] for pol in ['left','right','long']]
        singleNuisGroups = ['CMS.*','pdf.*','mu.*','ErfPar0.*','ErfPar1.*','ErfPar2.*']
        targets = ['mu','xsecnorm']
        for t in toysHessian:
            for tmp_file in [i for i in results.keys() if re.match('both_floatingPOIs_{toyhess}'.format(toyhess=t),i)]:
                tmp_suffix = '_'.join(tmp_file.split('_')[1:])
                for target in targets:
                    for poig in poisGroups:
                        print "RUNNING SINGLE NUISANCE IMPACTS..."
                        for nuis in singleNuisGroups:
                            cmd = 'python w-helicity-13TeV/impactPlots.py {fr} -o {od} --nuis {nuis} --pois {pois} --target {tg} --suffix {sfx}'.format(fr=results[tmp_file], od=tmp_outdir, nuis=nuis, pois=poig, tg=target, sfx=tmp_suffix)
                            print "running ",cmd
                            os.system(cmd)
                        # now do the groups of systematics
                        print "RUNNING GROUPED NUISANCE IMPACTS..."
                        cmd = 'python w-helicity-13TeV/impactPlots.py {fr} -o {od} --nuisgroups .* --pois {pois} --target {tg} --suffix {sfx}'.format(fr=results[tmp_file], od=tmp_outdir, pois=poig, tg=target, sfx=tmp_suffix)
                        print "running ",cmd
                        os.system(cmd)

    ## do this at the end, it takes the longest
    ## diff nuisances
    ## ================================
    if options.make in ['all', 'nuis']:
        print 'running diffNuisances'
        tmp_outdir = options.outdir+'/diffNuisances/'
        os.system('mkdir -p {od}'.format(od=tmp_outdir))
        os.system('cp ~emanuele/public/index.php {od}'.format(od=tmp_outdir))
        for t in toysHessian:
            for tmp_file in [i for i in results.keys() if re.match('both_(floating|fixed)POIs_{toyhess}'.format(toyhess=t),i)]:
                tmp_suffix = '_'.join(tmp_file.split('_')[1:])
                nuisancesAndPOIs = ['pdf', 'muR,muF,muRmuF,alphaS,wpt', 'CMS_', 'ErfPar']
                if 'floatingPOIs' in results[tmp_file]: nuisancesAndPOIs += ['W{charge}_{pol}.*_mu'.format(charge=charge,pol=pol) for charge in ['plus','minus'] for pol in ['left','right','long'] ]
                for nuis in nuisancesAndPOIs:
                    diffNuisances_cmd = 'python w-helicity-13TeV/diffNuisances.py --all --format "html,latex" --outdir {od} --pois {p}'.format(od=tmp_outdir, p=nuis)
                    os.system('{cmd} --infile {inf} --suffix {suf} --type {t} '.format(cmd=diffNuisances_cmd, inf=results[tmp_file], suf=tmp_suffix, t=t))
                    print '{cmd} --infile {inf} --suffix {suf} --type {t} '.format(cmd=diffNuisances_cmd, inf=results[tmp_file], suf=tmp_suffix, t=t)
