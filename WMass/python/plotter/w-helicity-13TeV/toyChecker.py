#!/usr/bin/env python
# python w-helicity-13TeV/toyChecker.py toys/diffXsec_el_2018_09_20_group10_legacySF/ -c -q cmscaf1nd > testResubToys.txt
# then
# cat testResubToys.txt | grep bsub | bash

import os.path
import sys,ROOT,os
ROOT.gROOT.SetBatch(True)

class CardsChecker:
    def __init__(self, toy_dir, options):
        self.toy_dir = toy_dir
        self.options = options
        self.sourceFiles = {}
        self.pycmd = {}
        for f in os.listdir(toy_dir+'/jobs/'):
            if not f.endswith('.sh'): 
                continue
            tmp_f = open(toy_dir+'/jobs/'+f, 'r')
            lines = tmp_f.readlines()
            for i in lines:
                if 'combinetf.py' in i: pycmds = i
            seed = pycmds.split(' --seed ')[1].split()[0]
            self.sourceFiles[seed] = f
        print '## Expecting {n} root files'.format(n=len(self.sourceFiles))

    def checkToys(self):
        resubcmds = {}
        for seed,source in self.sourceFiles.iteritems():
            f = "fitresults_" + str(seed) + ".root"
            if not os.path.exists(self.toy_dir+'/'+f) or os.path.getsize(self.toy_dir+'/'+f) < 1000.:
                if self.options.verbose>1: print '# file ',f,'  not present (or size < 1000) in ',self.toy_dir
                # submitting job with option -oo will overwrite old log file
                #print "%s  %s" % (seed, source)
                tmp_job_path = self.toy_dir+'/jobs/'+source
                tmp_log_path = self.toy_dir+'/logs/'+source.replace('.sh','.log')
                resubcmds[seed] = 'bsub -q {queue} -oo {log} {srcfile}'.format(queue=self.options.queue, 
                                                                               log=os.path.abspath(tmp_log_path), 
                                                                               srcfile=os.path.abspath(tmp_job_path))
        return resubcmds

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='%prog toydir')
    parser.add_option('-c', '--check-toys', dest='checkToys', default=False, action='store_true', help='Check if there are all the datacards and ROOT files');
    parser.add_option('-q', '--queue', dest='queue', type='string', default='1nd', help='choose the queue to submit batch jobs (default is 8nh)');
    parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int, help='Degree of verbosity (0=default prints only the resubmit commands)');
    (options, args) = parser.parse_args()

    if options.checkToys:
        toydir = args[0]
        if len(args)<1: print 'needed inputs: toys_dir '; quit()
        cc = CardsChecker(toydir, options)
        result = cc.checkToys()
        if len(result)==0: print 'All files are GOOD.'
        else: 
            keys = result.keys()
            keys.sort()
            for k in keys: print result[k]
            print '## in total have to resubmit {n} jobs'.format(n=len(result))

