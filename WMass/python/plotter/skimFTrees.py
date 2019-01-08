import ROOT
import os, sys

# usage: python skimFTrees.py BIGTREE_DIR FTREE_DIR outdir
# for event variables: python skimFTrees.py skims /data1/emanuele/monox/TREES_25ns_1LEPSKIM_76X/friends skims/friends
# for scale factors: python skimFTrees.py skims /data1/emanuele/monox/TREES_25ns_1LEPSKIM_76X/friends skims/friends -f sfFriend -t "sf/t"

def _runIt(args,options,excludeProcesses=[]):
    (treedir,ftreedir,outdir,treename,ffilename) = args
    dsets = [d.replace(ffilename+'_','').replace('.root','') for d in os.listdir(sys.argv[2]) if ffilename in d]
    dsets = [d for d in dsets if d in os.listdir(treedir)]
    procsToExclude = []
    for p0 in excludeProcesses:
        for p in p0.split(","):
            procsToExclude.append(p)
    if len(excludeProcesses)>0: print "skimFTrees: exlude the following datasets: ", ", ".join(procsToExclude)

    for dset in dsets:
        if options.component and dset!=options.component: continue
        print "Skimming friend for component %s..." % dset
        skipMe = False
        for p in procsToExclude:
            if p in dset: skipMe = True
        if skipMe: continue
        print dset,
        fsel = ROOT.TFile.Open(treedir+'/'+dset+'/selection_eventlist.root')
        elist = fsel.elist
        f_f = ROOT.TFile.Open(ftreedir+'/'+ffilename+'_'+dset+'.root')
        t_f = f_f.Get(treename)
        # drop and keep branches
        if options.dropall: t_f.SetBranchStatus("*",0)
        for drop in options.drop: t_f.SetBranchStatus(drop,0)
        for keep in options.keep: t_f.SetBranchStatus(keep,1)
        t_f.SetEventList(elist)
        os.system('mkdir -p %s'%outdir)
        f2 = ROOT.TFile('%s/%s_%s.root'%(outdir,ffilename,dset),'recreate')
        f2.cd()
        #fdirname = [x for x in treename.split('/') if x!=''][0]
        #f2.mkdir(fdirname)
        #f2.cd(fdirname)
        t2 = t_f.CopyTree('1')
        f2.Write()
        print ': skimmed friend trees put in %s'%f2.GetName()
        f2.Close()
        f_f.Close()
        fsel.Close()

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] BIGTREE_DIR FTREE_DIR outdir")
    parser.add_option("-t", "--tree", dest="tree", type="string", default="Friends", help="Name of the friend tree")
    parser.add_option("-f", "--friend", dest="friend", type="string", default="tree_Friend", help="Prefix of the friend ROOT file name")
    parser.add_option("-x", "--exclude-process", dest="excludeProcess", action="append", default=[], help="exclude some processes with a given pattern (comma-separated patterns)")
    parser.add_option("-c", "--component", dest="component",   type="string", default=None, help="skim only this component");
    parser.add_option("-D", "--drop",  dest="drop", type="string", default=[], action="append",  help="Branches to drop, as per TTree::SetBranchStatus") 
    parser.add_option("--dropall",     dest="dropall", default=False, action="store_true",  help="Drop all the branches (to keep only the selected ones with keep)") 
    parser.add_option("-K", "--keep",  dest="keep", type="string", default=[], action="append",  help="Branches to keep, as per TTree::SetBranchStatus") 
    parser.add_option("-q", "--queue",   dest="queue",     type="string", default=None, help="Run jobs on lxbatch instead of locally");
    parser.add_option("--log", "--log-dir", dest="logdir", type="string", default=None, help="Directory of stdout and stderr");
    parser.add_option("--pretend",     dest="pretend", default=False, action="store_true",  help="Pretend to skim, don't actually do it") 
    (options, args) = parser.parse_args()
    if len(args)<3:
        print "Usage: program <BIGTREE_DIR> <FTREE_DIR> <outdir>"
        exit()

    allargs = (args + [options.tree,options.friend])

    print "Will write the selected friend trees to "+args[2]


    if options.queue:

        ## first make the log directory to put all the condor files
        writelog = ""
        logdir   = ""
        if not options.logdir: 
            print 'ERROR: must give a log directory to make the condor files!\nexiting...'
            exit()
        else:
            logdir = options.logdir.rstrip("/")
            if not os.path.exists(logdir):
                os.system("mkdir -p "+logdir)

        ## constructing the command and arguments to run in condor submit file
        runner = "%s/src/CMGTools/WMass/python/postprocessing/lxbatch_runner.sh" % os.environ['CMSSW_BASE']
        cmdargs = [x for x in sys.argv[1:] if x not in ['-q',options.queue]]
        strargs=''
        for a in cmdargs: # join do not preserve " or '
            if '-p' in a or '--pretend' in a:
                continue
            strargs += ' '+a+' '
        ## this is different for friends than main trees
        condor_fn = options.logdir+'/condor_ftrees.condor'
        condor_f = open(condor_fn,'w')
        condor_f.write('''Universe = vanilla
Executable = {runner}
use_x509userproxy = $ENV(X509_USER_PROXY)
Log        = {ld}/$(ProcId).log
Output     = {ld}/$(ProcId).out
Error      = {ld}/$(ProcId).error
getenv      = True
request_memory = 4000
+MaxRuntime = 43200\n
'''.format(runner=runner,ld=options.logdir))
        if os.environ['USER'] in ['mdunser', 'psilva']:
            condor_f.write('+AccountingGroup = "group_u_CMST3.all"\n')
        condor_f.write('\n')

        # for friends...
        (treedir,ftreedir,outdir,treename,ffilename) = allargs
        dsets = [d.replace(ffilename+'_','').replace('.root','') for d in os.listdir(sys.argv[2]) if ffilename in d]
        dsets = [d for d in dsets if d in os.listdir(treedir)]

        for d in dsets:

            print "\t component %-40s" % d
            componentPost = ' --component {c} '.format(c=d)
            condor_f.write('\narguments = {d} {cmssw} python {self} {cmdargs} {comp}\n'.format(d=os.getcwd(),
            cmssw = os.environ['CMSSW_BASE'], self=sys.argv[0], cmdargs=strargs, comp=componentPost))
            condor_f.write('queue 1\n\n')
        condor_f.close()
        cmd = 'condor_submit {sf}'.format(sf=condor_fn)
        if options.pretend: 
            print cmd
        else:
            os.system(cmd)
        exit()

    _runIt(allargs,options,options.excludeProcess)
