#!/usr/bin/env python
# USAGE: 
# 1. if you have already the output of friendChunkCheck.sh -z fdir > zombies.txt
# ./scripts/friendChunkResub.py frienddir maintreedir zombies.txt -N 500000
# 2. if you don't have it
#  ./scripts/friendChunkResub.py frienddir maintreedir --run-checker -N 500000

import sys,os,re

if __name__ == "__main__":
    
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] dir_with_friend_trees dir_with_trees [checkedfile.txt]")
    parser.add_option("-c",      "--run-checker", dest="runChecker",  action='store_true', default=False, help="Run the script friendChunkCheck.sh");
    parser.add_option("-N", "--events",  dest="chunkSize", type="int",    default=1000000, help="Default chunk size when splitting trees");
    (options, args) = parser.parse_args()

    fdir = args[0]
    maindir = args[1]

    if options.runChecker:
        print "Running friendChunkCheck.sh now on ",fdir,". Will take time..."
        if len(args)==3:
            print "Can't run the checker if you pass the output file of a previous check (for safety)"
            sys.exit(1)
        bashCheckScript = '{cmssw}/src/CMGTools/WMass/python/postprocessing/scripts/friendChunkCheck.sh -z {frienddir} > tmpcheck.txt'.format(cmssw=os.environ['CMSSW_BASE'],
                                                                                                                                              frienddir=fdir)
        if os.path.isfile('tmpcheck.txt'):
            print "File tmpcheck.txt exists. It means you could be running friendChunkCheck.sh. If not, remove it, and run it again."
            sys.exit()
        else:
            os.system(bashCheckScript)
        print "Done. The list of files is in tmpcheck.txt."

    tmpfile = 'tmpcheck.txt' if len(args)<3 else args[2]
    txtfile=open(tmpfile,'r')
    for line in txtfile:
        l = line.rstrip()
        if not l.endswith('OK') and not l.startswith('#'):
            base = os.path.basename(l)
            tokens = base.split('.')
            dataset = '_'.join(tokens[0].split('_')[2:])
            chunk = tokens[1].split('chunk')[-1]
            #print "# resubmitting dataset = ",dataset," chunk ",chunk
            cmd = "python postproc_batch.py {maintreedir} {frienddir} --friend --log friends_log -N {nevents} -q 8nh -d {dataset} -c {chunk} --submit".format(maintreedir=maindir,frienddir=fdir,nevents=options.chunkSize,dataset=dataset,chunk=chunk)
            print cmd
