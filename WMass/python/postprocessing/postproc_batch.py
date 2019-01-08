#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from glob import glob
import re, pickle, math
from CMGTools.WMass.postprocessing.framework.postprocessor import PostProcessor

## USAGE:

## to run locally:
# python postproc_batch.py -N 250000  <directoryWithTrees> <targetDirectoryForFriends>  --friend  

## if you want to submit to condor, add:
## --log friends_log/ --submit  --runtime 240 (optional, default 480 minutes)

## if you insist on running on LSF, instead add:
## --log friends_log/ --submit --env lxbatch --queue 1nd (optional, default 8nh)

DEFAULT_MODULES = [("CMGTools.WMass.postprocessing.examples.puWeightProducer", "puWeight,puWeight2016BF"),
                   ("CMGTools.WMass.postprocessing.examples.lepSFProducer","lep2016SF"),
                   ("CMGTools.WMass.postprocessing.examples.lepVarProducer","eleRelIsoEA,lepQCDAwayJet,eleCalibrated"),
                   ("CMGTools.WMass.postprocessing.examples.jetReCleaner","jetReCleaner"),
                   ("CMGTools.WMass.postprocessing.examples.genFriendProducer","genQEDJets"),
                   ("CMGTools.WMass.postprocessing.examples.recoilTrainExtra","recoilTrainExtra"),
                   ]

def writeCondorCfg(srcfile, flavour=None, maxRunTime=None):
    #base=''.join(srcfile.split('.')[:-1])
    base = os.path.splitext(srcfile)[0]
    print "srcfile = ",srcfile,"  base = ",base
    maxruntime="-t" # time in minutes
    if maxRunTime:
        if flavour:
            print "Can't set both flavour and maxruntime"
            sys.exit(1)
        maxruntime = str(60 * int(maxRunTime))
    job_desc = """Universe = vanilla
Executable = {scriptName}
use_x509userproxy = $ENV(X509_USER_PROXY)
Log        = {pid}.log
Output     = {pid}.out
Error      = {pid}.error
getenv      = True
environment = "LS_SUBCWD={here}"
request_memory = 4000
""".format(scriptName=srcfile,
           pid=base,
           here=os.environ['PWD'])
    if flavour:
        job_desc += '+JobFlavour = "%s"\n' % flavour
    if maxruntime!="":
        job_desc += '+MaxRuntime = %s\n' % maxruntime
    if os.environ['USER'] in ['mdunser', 'psilva']:
        job_desc += '+AccountingGroup = "group_u_CMST3.all"\n'
    job_desc += 'queue 1\n'

    jobdesc_file = base+'.condor'
    with open(jobdesc_file,'w') as outputfile:
        outputfile.write(job_desc)
        outputfile.close()
    return jobdesc_file

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] inputDir outputDir")
    parser.add_option("-J", "--json",  dest="json", type="string", default=None, help="Select events using this JSON file")
    parser.add_option("-C", "--cut",  dest="cut", type="string", default=None, help="Cut string")
    parser.add_option("-b", "--branch-selection",  dest="branchsel", type="string", default=None, help="Branch selection")
    parser.add_option("--friend",  dest="friend", action="store_true", default=True, help="Produce friend trees in output (current default is to produce full trees)")
    parser.add_option("--full",  dest="friend", action="store_false",  default=False, help="Produce full trees in output (this is the current default)")
    parser.add_option("--noout",  dest="noOut", action="store_true",  default=False, help="Do not produce output, just run modules")
    parser.add_option("--justcount",   dest="justcount", default=False, action="store_true",  help="Just report the number of selected events") 
    parser.add_option("-I", "--import", dest="imports",  type="string", default=[], action="append", nargs=2, help="Import modules (python package, comma-separated list of ");
    parser.add_option("-z", "--compression",  dest="compression", type="string", default=("LZMA:9"), help="Compression: none, or (algo):(level) ")
    parser.add_option("-d", "--dataset", dest="datasets",  type="string", default=[], action="append", help="Process only this dataset (or dataset if specified multiple times)");
    parser.add_option(      "--dataset-rgx", dest="datasetsRgx",  type="string", default=None, help="Process only datasets that match this regexp (or comma-separated list of regexp)");
    parser.add_option("-c", "--chunk",   dest="chunks",    type="int",    default=[], action="append", help="Process only these chunks (works only if a single dataset is selected with -d)");
    parser.add_option("-N", "--events",  dest="chunkSize", type="int",    default=1000000, help="Default chunk size when splitting trees");
    parser.add_option("-p", "--pretend", dest="pretend",   action="store_true", default=False, help="Don't run anything");
    parser.add_option("-j", "--jobs",    dest="jobs",      type="int",    default=1, help="Use N threads");
    parser.add_option("-q", "--queue",   dest="queue",     type="string", default='8nh', help="Run jobs on lxbatch instead of locally");
    parser.add_option("-r", "--runtime",    type=int, default=480, help="Condor runtime. In minutes.");
    parser.add_option("-s", "--submit",    action='store_true', default=False, help="Submit the jobs to lsf/condor.");
    parser.add_option("-t", "--tree",    dest="tree",      default='treeProducerWMass', help="Pattern for tree name");
    parser.add_option("--log", "--log-dir", dest="logdir", type="string", default=None, help="Directory of stdout and stderr");
    parser.add_option("--env",   dest="env", type="string", default="condor", help="Give the environment on which you want to use the batch system (lsf,condor). Default: condor");
    parser.add_option("--run",   dest="runner",  type="string", default="lxbatch_runner.sh", help="Give the runner script (default: lxbatch_runner.sh)");
    parser.add_option("--mconly", dest="mconly",  action="store_true", default=False, help="Run only on MC samples");
    parser.add_option("--signals", dest="signals", default="WJetsToLNu,DYJetsToLL", help="declare signals (CSV list) [%default]",type='string');
    parser.add_option("-m", "--modules", dest="modules",  type="string", default=[], action="append", help="Run only these modules among the imported ones");
    parser.add_option(      "--moduleList", dest="moduleList",  type="string", default='DEFAULT_MODULES', help="use this list as a starting point for the modules to run [%default]")

    (options, args) = parser.parse_args()

    if options.friend:
        if options.cut or options.json: raise RuntimeError("Can't apply JSON or cut selection when producing friends")

    if len(args) != 2 or not os.path.isdir(args[0]):
        parser.print_help()
        sys.exit(1)
    if len(options.chunks) != 0 and len(options.datasets) != 1:
        print "must specify a single dataset with -d if using -c to select chunks"
        sys.exit(1)

    treedir = args[0]; outdir=args[1]; args = args[2:]

    jobs = []
    for D in glob(treedir+"/*"):
        treename = "tree"
        fname    = "%s/%s/tree.root" % (D,options.tree)
        pckfile  = "%s/skimAnalyzerCount/SkimReport.pck" % (D)
        if (not os.path.exists(fname)) and os.path.exists("%s/%s/tree.root" % (D,options.tree)):
            treename = "tree"
            fname    = "%s/%s/tree.root" % (D,options.tree)
     
        if (not os.path.exists(fname)) and (os.path.exists("%s/%s/tree.root.url" % (D,options.tree)) ):
            treename = "tree"
            fname    = "%s/%s/tree.root" % (D,options.tree)
            fname    = open(fname+".url","r").readline().strip()
     
        if os.path.exists(fname) or (os.path.exists("%s/%s/tree.root.url" % (D,options.tree))):
            short = os.path.basename(D)
            if options.datasets != []:
                if short not in options.datasets: continue
            if options.datasetsRgx != None:
                regexps = options.datasetsRgx.split(',')
                if not any(re.match(rgx,short) for rgx in regexps): continue
            data = any(x in short for x in "DoubleMu DoubleEG MuEG MuonEG SingleMuon SingleElectron".split())
            if data and options.mconly: continue
            ## construct proper xrootd file path
            prepath = ''
            if not 'root:/' in fname:
                if   '/eos/user/'      in fname: prepath = 'root://eosuser.cern.ch//'
                elif '/eos/cms/store/' in fname: prepath = 'root://eoscms.cern.ch//'
            fname = prepath+fname
            ## fname is now xrootd compatible
            ROOT.gEnv.SetValue("TFile.AsyncReading", 1);
            
            ## open the file
            #f = ROOT.TFile.Open(fname);
            f = ROOT.TFile.Open(fname+"?readaheadsz=65535");

            ## get the counters from the histograms
            histo_count        = f.Get('Count')
            histo_sumgenweight = f.Get('SumGenWeights')
            n_count        = histo_count       .GetBinContent(1)
            n_sumgenweight = (histo_sumgenweight.GetBinContent(1) if histo_sumgenweight else n_count)

            sample_nevt = n_count if n_sumgenweight == n_count else n_sumgenweight
            ## done. but as of now sample_nevt is not used...

            t = f.Get(treename)
            entries = t.GetEntries()
            f.Close()
            chunk = options.chunkSize
            if entries < chunk:
                print "  ",os.path.basename(D),("  DATA" if data else "  MC")," single chunk"
                jobs.append((short,fname,sample_nevt,"_Friend_%s"%short,data,xrange(entries),-1))
            else:
                nchunk = int(math.ceil(entries/float(chunk)))
                print "  ",os.path.basename(D),("  DATA" if data else "  MC")," %d chunks" % nchunk
                for i in xrange(nchunk):
                    if options.chunks != []:
                        if i not in options.chunks: continue
                    r = xrange(int(i*chunk),min(int((i+1)*chunk),entries))
                    jobs.append((short,fname,sample_nevt,"_Friend_%s.chunk%d" % (short,i),data,r,i))

    print "\n"
    print "I have %d taks to process" % len(jobs)

    print 'I\'m using the following list of modules',options.moduleList
    imports = globals()[options.moduleList] + options.imports
    if options.submit:
        import os, sys

        writelog = ""
        logdir   = ""
        if options.logdir: 
            logdir = os.environ['PWD']+'/'+options.logdir
            logdir = logdir.rstrip("/")
            if not os.path.exists(logdir):
                os.system("mkdir -p "+logdir)

        runner = ""
        super = ""
        if options.env == "lxbatch":
            runner = options.runner
            super  = "bsub -q {queue}".format(queue = options.queue)
        elif  options.env == "condor":
            runner = options.runner
        else:
            print "ERROR. Scheduler ",options.env," not implemented. Choose either 'lsf' or 'condor'."
            sys.exit(1)

        basecmd = "{dir}/{runner} {dir} {cmssw} python {self} -N {chunkSize} -t {tree} --signals {signals} --moduleList {moduleList} {data} {output}".format(
                    dir = os.getcwd(), runner=runner, cmssw = os.environ['CMSSW_BASE'], 
                    self=sys.argv[0], chunkSize=options.chunkSize, tree=options.tree, signals=options.signals, moduleList=options.moduleList, data=treedir, output=outdir)

        friendPost = ""
        if options.friend: 
            friendPost += " --friend " 
        for (name,fin,sample_nevt,fout,data,range,chunk) in jobs:
            if chunk != -1:
                if options.logdir: 
                    writelog = ""
                    if options.env == "lxbatch":
                        writelog = "-o {logdir}/{data}_{chunk}.out -e {logdir}/{data}_{chunk}.err".format(logdir=logdir, data=name, chunk=chunk)
                if options.env == 'lxbatch':
                    cmd = "{super} {writelog} {base} -d {data} -c {chunk} {post}".format(super=super, writelog=writelog, base=basecmd, data=name, chunk=chunk, post=friendPost)
                elif options.env == 'condor':
                    condor_exec="{logdir}/{data}_{chunk}.sh".format(logdir=logdir, data=name, chunk=chunk)
                    os.system("echo '#!/bin/bash' > {condor_exec} ; echo {base} -d {data} -c {chunk} {post} >> {condor_exec} ; chmod u+x {condor_exec}".format(base=basecmd, data=name, chunk=chunk, post=friendPost, condor_exec=condor_exec))
                    condor_jobdesc = writeCondorCfg(condor_exec,maxRunTime=options.runtime)
                    cmd = 'condor_submit ' + condor_jobdesc
            else:
                if options.logdir: writelog = "-o {logdir}/{data}.out -e {logdir}/{data}.err".format(logdir=logdir, data=name)
                if options.env == 'lxbatch':
                    cmd = "echo \"{base} -d {data} {post}\" | {super} {writelog}".format(super=super, writelog=writelog, base=basecmd, data=name, chunk=chunk, post=friendPost)
                elif options.env == 'condor':
                    condor_exec="{logdir}/{data}.sh".format(logdir=logdir, data=name)
                    os.system("echo '#!/bin/bash' > {condor_exec} ; echo {base} -d {data} {post} >> {condor_exec} ; chmod u+x {condor_exec}".format(base=basecmd, data=name, post=friendPost, condor_exec=condor_exec))
                    condor_jobdesc = writeCondorCfg(condor_exec,maxRunTime=options.runtime)
                    cmd = 'condor_submit ' + condor_jobdesc
                print "{base} -d {data}".format(base=basecmd, data=name, chunk=chunk)
            print cmd
            if not options.pretend:
                os.system(cmd)

        exit()

    maintimer = ROOT.TStopwatch()
    def _runIt(myargs):
        (dataset,fin,sample_nevt,fout,data,range,chunk) = myargs
        modules = []
        for mod, names in imports: 
            import_module(mod)
            obj = sys.modules[mod]
            selnames = names.split(",")
            for name in dir(obj):
                if name[0] == "_": continue
                if name in selnames:
                    print "Modules to run: ",options.modules,"  name = ",name
                    if len(options.modules) and name not in options.modules: continue
                    print "Loading %s from %s " % (name, mod)
                    print "Running on dataset = ",dataset
                    signal = any(x in dataset for x in options.signals.split(','))
                    if name=='genQEDJets' and not signal: continue
                    modules.append(getattr(obj,name)())
        if options.noOut:
            if len(modules) == 0: 
                raise RuntimeError("Running with --noout and no modules does nothing!")
        ppargs=[fin]+args
        p=PostProcessor(outdir,ppargs,options.cut,options.branchsel,modules,options.compression,options.friend,fout,options.json,options.noOut,options.justcount,range)
        p.run()

    if options.jobs > 0:
        from multiprocessing import Pool
        pool = Pool(options.jobs)
        pool.map(_runIt, jobs) if options.jobs > 0 else [_runIt(j) for j in jobs]
    else:
        ret = dict(map(_runIt, jobs))
