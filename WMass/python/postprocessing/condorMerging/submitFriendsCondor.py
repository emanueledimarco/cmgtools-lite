import ROOT, commands, os, sys, optparse, datetime


## USAGE:
## ====================================
## python submitFriendsCondor.py -d <inputDirMainTrees> -o <outputDirFriends>

## the input directory must have all the main trees in it
## the output directory on eos does not necessarily have to exist

if __name__ == '__main__':

    parser = optparse.OptionParser(usage='usage: python %prog -d dirWithTrees -o targetDirForFriends ', version='%prog 1.0')
    parser.add_option('-d', '--directory' , type=str, default=''     , help='directory with the main trees inside. has to be given')
    parser.add_option('-N', '--nperjob'   , type=int, default=250000 , help='number of entries to process per job (default: %default)')
    parser.add_option('-o', '--targetdir' , type=str, default=''     , help='target directory for the output. has to be given')
    parser.add_option('-s', '--singleDS'  , type=str, default=''     , help='run only on signle datasets. comma separated list')
    parser.add_option('-p', '--pretend'   , action='store_true', default=False     , help='do everything except for submitting to the batch')
    (options, args) = parser.parse_args()

    if not options.targetdir:
        print 'no target directory given... exiting'
        sys.exit(0)
    if not options.directory:
        print 'no source directory given... exiting'
        sys.exit(0)

    cmsenv = os.environ['CMSSW_BASE']

    listOfDSs = []
    if options.singleDS:
        listOfDSs = options.singleDS.split(',')
        print 'doing only datasets:', listOfDSs

    dss = {}

    for isd,sd in enumerate(os.listdir(options.directory)):
        fp = options.directory+'/'+sd
        tmp_f = fp+'/treeProducerWMass/tree.root'
        
        ## a few checks to do to avoid random files in the directory
        if not os.path.isdir(fp): 
            continue
        if not os.path.isfile(tmp_f): 
            continue

        doDS = False
        if len(listOfDSs) > 0:
            for _ds in listOfDSs:
                if _ds == sd:
                    doDS = True
        else:
            doDS = True

        if not doDS:
            continue

        try:
            ## get the number of entries for each dataset
            tmp_f = ROOT.TFile(tmp_f, 'READ')
            tmp_t = tmp_f.Get('tree')
            tmp_n = tmp_t.GetEntries()

            dss[sd] = tmp_n

            tmp_f.Close()
        except:
            print 'something went wrong trying to get the number of events for sample', sd
            print 'i\'m moving on...'
            continue

    date = datetime.date.today().isoformat()
    condorSubmitCommands = []
    totalNumberOfJobs = 0
    for ds,nds in dss.items():
        n_chunks = int(nds/options.nperjob + (nds%options.nperjob > 0) ) ## this should definitely work, right?
        print 'for dataset {d} i will submit {n} chunks'.format(d=ds,n=n_chunks)
        tmp_condor_filename = 'logs/condor_friends_{ds}_{d}.condor'.format(ds=ds,d=date)
        tmp_condor = open(tmp_condor_filename,'w')
        tmp_condor.write('''Executable = friendsScript.sh
use_x509userproxy = $ENV(X509_USER_PROXY)
getenv      = True

environment = "LS_SUBCWD={here}"
request_memory = 4000
+MaxRuntime = 43200 \n\n'''.format(ds=ds, here=os.environ['PWD']))
        while n_chunks:
            totalNumberOfJobs += 1
            n_chunks -= 1 ## otherwise over counting...
            tmp_condor.write('arguments = {cmssw} {treedir} {ds} {chunk} {n} {td}\n'.format(cmssw=cmsenv,
                             treedir=os.path.abspath(options.directory+'/'+ds), 
                             ds=ds, 
                             chunk=n_chunks, 
                             n=options.nperjob,
                             td=options.targetdir)  )
            tmp_condor.write('''Log        = logs/log_condor_{ds}_chunk{ch}.log
Output     = logs/log_condor_{ds}_chunk{ch}.out
Error      = logs/log_condor_{ds}_chunk{ch}.error\n'''.format(ds=ds,ch=n_chunks))
            tmp_condor.write('queue 1\n\n')
        tmp_condor.close()
        condorSubmitCommands.append('condor_submit {cf}'.format(cf=tmp_condor_filename))

    print 'this will result in a total of {n} jobs'.format(n=totalNumberOfJobs)
    print 'submitting to condor...'
    for sc in condorSubmitCommands:
        print sc
        if not options.pretend:
            os.system(sc)
    print '...done'

        


