#!/usr/bin/env python
# python w-helicity-13TeV/DatacardsChecker.py -c cards/helicity_2018_03_06_testpdf

import sys,ROOT,os
ROOT.gROOT.SetBatch(True)

class CardsChecker:
    def __init__(self, card_dir, options):
        self.card_dir = card_dir
        self.options = options
        self.datacards = {}
        self.cardinputs = {}
        self.pycmd = {}
        retrydirs = [d for d in os.listdir(card_dir) if 'retry' in d]
        itry = len(retrydirs)+1
        self.resub_card_dir='{cdir}/retry_{i}'.format(cdir=card_dir,i=itry)
        os.mkdir(self.resub_card_dir)
        for f in os.listdir(card_dir+'/jobs/'):
            if not f.endswith('.sh'): 
                continue
            if "dummy_exec" in f: continue
            key = f.replace('.sh','')
            tmp_f = open(card_dir+'/jobs/'+f, 'r')
            lines = tmp_f.readlines()
            tmp_f.close()
            self.headerlines =[i for i in lines if not 'python ' in i]
            pycmds =[i for i in lines if 'python ' in i]
            for cmd in pycmds:
                tmp_name = cmd.split(' -o ')[1].split()[0]
                f_txt = tmp_name+'.card.txt'
                f_root = tmp_name+'.input.root'
                self.datacards[tmp_name] = f_txt
                self.cardinputs[tmp_name] = f_root
                #self.pycmd[tmp_name] = cmd.replace(' --od %s'%card_dir,' --od %s'%self.resub_card_dir)
                self.pycmd[tmp_name] = cmd
        self.resubPythonCommands = set()
        print '## Expecting {n} cards and rootfiles'.format(n=len(self.datacards))
        print '## Will put the new cards into ',self.resub_card_dir

    def makeResubFileLSF(self, key):
        resubdir = self.resub_card_dir+'/jobs/'
        os.system('mkdir -p '+resubdir)
        tmp_file_name = resubdir+'/'+key+'_resub.sh'
        tmp_file = open(tmp_file_name,'w')
        
        for i in self.headerlines:
            tmp_file.write(i)
        tmp_file.write(self.pycmd[key])
        tmp_file.close()
        return tmp_file_name

    def makeCondorFile(self, jobdir, srcFiles, splitdir=False):
        dummy_exec = open(jobdir+'/dummy_exec.sh','w')
        dummy_exec.write('#!/bin/bash\n')
        dummy_exec.write('bash $*\n')
        dummy_exec.close()
     
        condor_file_name = jobdir+'/condor_submit.condor'
        condor_file = open(condor_file_name,'w')
        if splitdir:
            os.system("mkdir -p {jd}/logs/".format(jd=self.resub_card_dir))
            os.system("mkdir -p {jd}/errs/".format(jd=self.resub_card_dir))
            os.system("mkdir -p {jd}/outs/".format(jd=self.resub_card_dir))
            # write new logs overwriting the original ones for failed jobs
            logdir = self.resub_card_dir + "/logs/"
            outdirCondor = self.resub_card_dir + "/outs/"
            errdir = self.resub_card_dir + "/errs/"
            condor_file.write('''Universe = vanilla
Executable = {de}
use_x509userproxy = $ENV(X509_USER_PROXY)
Log        = {ld}/$(ProcId).log   
Output     = {od}/$(ProcId).out   
Error      = {ed}/$(ProcId).error
getenv      = True
environment = "LS_SUBCWD={here}"
next_job_start_delay = 1
request_memory = 4000
+MaxRuntime = {rt}\n
'''.format(de=os.path.abspath(dummy_exec.name), ld=os.path.abspath(logdir), od=os.path.abspath(outdirCondor), ed=os.path.abspath(errdir), 
           rt=int(options.runtime*3600), here=os.environ['PWD'] ) )
        else:
            condor_file.write('''Universe = vanilla
Executable = {de}
use_x509userproxy = $ENV(X509_USER_PROXY)
Log        = {jd}/$(ProcId).log
Output     = {jd}/$(ProcId).out
Error      = {jd}/$(ProcId).error
getenv      = True
environment = "LS_SUBCWD={here}"
next_job_start_delay = 1
request_memory = 4000
+MaxRuntime = {rt}\n
'''.format(de=os.path.abspath(dummy_exec.name), jd=os.path.abspath(jobdir), rt=int(options.runtime*3600), here=os.environ['PWD'] ) )

        if os.environ['USER'] in ['mdunser', 'psilva']:
            condor_file.write('+AccountingGroup = "group_u_CMST3.all"\n\n\n')
        for sf in srcFiles:
            condor_file.write('arguments = {sf} \nqueue 1 \n\n'.format(sf=os.path.abspath(sf)))
        condor_file.close()
        return condor_file_name

    def checkCards(self):
        resubcmds = {}
        card_subdirs = [d for d in os.listdir(self.card_dir) if 'part' in d]
        for key,dc in self.datacards.iteritems():
            if not any([os.path.exists(self.card_dir+'/'+subdc+'/'+dc) for subdc in card_subdirs]): 
                if self.options.verbose>1: 
                    print '# datacard ',dc,' is not present in ',self.card_dir
                if options.useLSF:
                    resubfile = self.makeResubFileLSF(key)
                    os.system('chmod u+x '+os.path.abspath(resubfile))
                    resubcmds[key] = 'bsub -q {queue} -o {log} {srcfile}'.format(
                        queue=self.options.queue, log=os.path.abspath(resubfile.replace('.sh','.log')), srcfile=os.path.abspath(resubfile))
                else:
                    self.resubPythonCommands.add(self.pycmd[key])

        tmp_f = open('clean_badcards.sh','w')
        card_subdir = {} 
        for key,f in self.cardinputs.iteritems():
            f_ok = True
            for subdc in card_subdirs:
                if os.path.exists(self.card_dir+'/'+subdc+'/'+f):
                    card_subdir[key] = subdc
            if key not in card_subdir:
                if self.options.verbose>1: print '# input root file ',f,' is not present in ',self.card_dir
                f_ok = False
            elif os.path.getsize(self.card_dir+'/'+card_subdir[key]+'/'+f) < 1000.:
                print '# WARNING found a input root file below 1kB:', self.card_dir+'/'+card_subdir[key]+'/'+f
                txt = ''.join(f.split('.')[-3])+'.card.txt'
                tmp_f.write('rm {dir}/{subdir}/{ftxt}\n'.format(dir=self.card_dir,subdir=card_subdir[key],ftxt=txt))
                tmp_f.write('rm {dir}/{subdir}/{froot}\n'.format(dir=self.card_dir,subdir=card_subdir[key],froot=f))
                f_ok = False
            else: 
                if self.options.checkZombies:
                    tfile = ROOT.TFile.Open(self.card_dir+'/'+card_subdir[key]+'/'+f)
                    if not tfile or tfile.IsZombie():
                        if self.options.verbose>1: print '# ',f, ' is Zombie'
                        f_ok = False
                    elif tfile.GetNkeys() == 0:
                        if self.options.verbose>1: print '# WARNING',f, ' has no keys inside!!'
                        f_ok = False

            if not f_ok: 
                if options.useLSF:
                    resubfile = self.makeResubFileLSF(key)
                    os.system('chmod u+x '+os.path.abspath(resubfile))
                    resubcmds[key] = 'bsub -q {queue} -o {log} {srcfile}'.format(
                        queue=self.options.queue, log=os.path.abspath(resubfile.replace('.sh','.log')), srcfile=os.path.abspath(resubfile))
                else:
                    self.resubPythonCommands.add(self.pycmd[key])
        tmp_f.close()
        if not options.useLSF:
            reslist = list(self.resubPythonCommands)
            nj = len(reslist)
            print 'number of python jobs to resubmit', nj
        
            if not nj%options.grouping:
                njobs = int(nj/options.grouping)
            else: njobs = int(nj/options.grouping) + 1

            resubdir = self.resub_card_dir+'/jobs/'
            os.system('mkdir -p '+resubdir)
            srcfiles = []
            for ij in range(njobs):
                tmp_srcfile_name = resubdir+'/resubjob_{i}.sh'.format(i=ij)
                tmp_srcfile = open(tmp_srcfile_name, 'w')
                for hl in self.headerlines:
                    tmp_srcfile.write(hl)
                tmp_n = options.grouping
                while len(reslist) and tmp_n:
                    tmp_pycmd = reslist[0]
                    tmp_srcfile.write(tmp_pycmd)
                    reslist.remove(tmp_pycmd)
                    tmp_n -= 1
                tmp_srcfile.close()
                srcfiles.append(tmp_srcfile_name)
            cf = self.makeCondorFile(resubdir,srcfiles,splitdir=self.options.splitdir)
            resubcmds[0] = 'condor_submit {rf} '.format(rf = cf)
            
        return resubcmds

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='%prog dir channel (el,mu) [nRapBins] [nPdfBins]')
    parser.add_option('-c', '--check-cards', dest='checkCards', default=False, action='store_true', help='Check if there are all the datacards and ROOT files');
    parser.add_option('-z', '--check-zombies', dest='checkZombies', default=False, action='store_true', help='Check if all the ROOT files are sane');
    parser.add_option('-q', '--queue', dest='queue', type='string', default='1nd', help='choose the queue to submit batch jobs (default is 8nh)');
    parser.add_option('-v', '--verbose', dest='verbose', default=0, type=int, help='Degree of verbosity (0=default prints only the resubmit commands)');
    parser.add_option('-l', '--useLSF', default=False, action='store_true', help='Force use of LSF instead of condor. Default: condor');
    parser.add_option('-r', '--runtime', default=12, type=int,  help='New runtime for condor resubmission in hours. default None: will take the original one.');
    parser.add_option('-g', '--grouping', default=10, type=int,  help='Group resubmit commands into groups of size N');
    parser.add_option(      '--splitdir', dest='splitdir', default=False, action='store_true', help='Use thsi option if .log, .err, .out files of condor are put in separate folders (needed for diff.xsec, might become useful for helciity as well)');
    (options, args) = parser.parse_args()

    if options.checkCards:
        carddir = args[0]
        if len(args)<1: print 'needed inputs: datacards_dir '; quit()
        cc = CardsChecker(carddir, options)
        result = cc.checkCards()
        if len(result)==0: print 'All cards are GOOD.'
        else: 
            keys = result.keys()
            keys.sort()
            for k in keys: 
                print result[k]
            print '## in total have to resubmit {n} jobs'.format(n=len(result))
            print 'piping all the commands in resubmit.sh'
            tmp_f = open('resubmit.sh','w')
            for k in keys: 
                tmp_f.write(result[k]+'\n')
            tmp_f.close()
            

