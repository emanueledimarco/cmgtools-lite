#!/usr/bin/env python
from shutil import copyfile
import re, sys, os, os.path, subprocess, json, ROOT
import numpy as np

# work only if make_helicity_cards.py has a __main__, otherwise it copies everything (not good, it copies also the body)
# from make_helicity_cards import getMcaIncl
# from make_helicity_cards import writePdfSystsToMCA
# from make_helicity_cards import writeQCDScaleSystsToMCA
# from make_helicity_cards import writePdfSystsToSystFile
# from make_helicity_cards import submitBatch

NPDFSYSTS=60 # Hessian variations of NNPDF 3.0
pdfsysts=[] # array containing the PDFs signal variations
qcdsysts=[] # array containing the QCD scale signal variations
etaeffsysts=[] # array containing the uncorrelated efficiency systematics vs eta 

# new function
def getArrayParsingString(inputString, verbose=False, makeFloat=False):
    # convert string [a,b,c,...] to list of a b c ...
    tmp = inputString.replace('[','').replace(']','')
    tmp = tmp.split(',')
    if verbose:
        print "Input:",inputString
        print "Output:",tmp
    if makeFloat:
        ret = [float(x) for x in tmp]
    else:
        ret = tmp
    return ret

# new function
def getGlobalBin(ix, iy, nbinsX, binFrom0=True):
    # ix goes from 0 to nbinsX-1, like the value returned by "for ix in xrange(nbinsX)"
    # same is expected for iy
    # If this is the case, global bin starts from 0
    #However, if binFrom0=False, it is expected that the bins start from 1 (like those of a TH1) and the globalbin that is returned will start from 1 as well
    if binFrom0:
        return (ix + iy * nbinsX)
    else:
        return (ix-1 + (iy-1) * nbinsX) + 1  # trasform ix,iy in [1,N] to ix',iy' in [0,N-1], get global bin and sum 1 so that it starts from 1

def getXYBinsFromGlobalBin(globalbin, nbinsX, binFrom0=True):
    # global bin goes from 0 to nbinX*nbinsY-1 
    # returned x(y) is a number from 0 to nbinsX(Y) -1
    # however, if that is not the convention, then binFrom0 must be set to False: this manages the case where the global bin starts from 1 and the returned ix and iy will start from 1 as well
    tmp = globalbin if binFrom0 else (globalbin-1)
    iy = int(tmp/nbinsX)
    ix = tmp % nbinsX
    if not binFrom0:
        ix = ix + 1
        iy = iy + 1
    return ix,iy

def getArrayBinNumberFromValue(binEdgesArray,val):
    # assumes values in binEdgesArray are ordered in increasing order
    # we follow ROOT convention: when evaluating bin=ibin, upper edge belongs to ibin+1, lower edge belongs to ibin
    # return -2 for overflow, -1 for underflow, a number in [0,len(binEdgesArray)-1] otherwise
    ret = -2
    if val < binEdgesArray[0]: return -1
    for bin in range(len(binEdgesArray)-1):
        if val < binEdgesArray[bin+1]:
            ret = bin
            break
    return ret


def get_ieta_ipt_from_process_name(name):
    # name is something like  Wplus_el_ieta_1_ipt_14_Wplus_el_group_18
    if not all([x in name for x in ["ieta","ipt"]]):
        print "Error in get_ieta_ipt_from_process_name(): 'ieta' or 'ipt' not found in %s. Exit" % name
        quit()
    tokens = name.split('_')
    for i,tkn in enumerate(tokens):
        #print "%d %s" % (i, tkn)                                                                                                                        
        if tkn == "ieta": ieta = int(tokens[i + 1])
        if tkn == "ipt":  ipt  = int(tokens[i + 1])
    return ieta,ipt



class templateBinning:
    def __init__(self,etaBins=[],ptBins=[]):
        self.etaBins = etaBins
        self.ptBins = ptBins
        self.Neta = len(etaBins)-1
        self.Npt  = len(ptBins)-1

    def printBin(self):
        print "###########################"
        print "Binning: eta-pt on x-y axis"
        print "eta bins: %s" % str(self.Neta)
        print "pt  bins: %s" % str(self.Npt)


def getDiffXsecBinning(inputBins, whichBins="reco"):

    # whichBins can be reco or gen
    if whichBins not in ["reco", "gen"]:
        print "Error in function getDiffXsecBinning(): whichBins must be 'reco' or 'gen'. Exit" 
        exit()

    # case in which we are passing a file containing the binning and not directly the binning itself
    if inputBins.startswith("file=") or "binningPtEta.txt" in inputBins:
        etaPtbinningFile = inputBins.replace("file=","")
        with open(etaPtbinningFile) as f:
            content = f.readlines()
        for x in content:
            if str(x).startswith(whichBins):
                tmpbinning = (x.split(whichBins+":")[1]).strip()
            else:
                continue
        etabinning = tmpbinning.split('*')[0]    # this is like [a,b,c,...], and is of type string. We nedd to get an array  
        ptbinning  = tmpbinning.split('*')[1]
    else:
        etabinning = inputBins.split('*')[0]    # this is like [a,b,c,...], and is of type string. We nedd to get an array  
        ptbinning  = inputBins.split('*')[1]
    etabinning = getArrayParsingString(etabinning,makeFloat=True)
    ptbinning  = getArrayParsingString(ptbinning,makeFloat=True)
    #binning = [len(etabinning)-1, etabinning, len(ptbinning)-1, ptbinning] 
    binning = [etabinning, ptbinning] 
    #print binning
    return binning


def wptBinsScales(i):
    wptbins = [0.0, 1.971, 2.949, 3.838, 4.733, 5.674, 6.684, 7.781, 8.979, 10.303, 11.777, 13.435, 15.332, 17.525, 20.115, 23.245, 27.173, 32.414, 40.151, 53.858, 13000.0]
    #if len(wptbins)<2*i:
    #    print 'you are asking too much from the wpt binning for decorrelation of scales'
    factor = 2 # use any 2 bins instead of changing the array
    ptlo = wptbins[factor * (i-1)]
    pthi = wptbins[factor * i]
    return [ptlo, pthi]


def getCondorTime(qstr):
    retval = ''
    if   qstr == '1nh':
        retval = 3600
    elif qstr == '8nh':
        retval = 28800
    elif qstr == '1nd' or qstr == 'cmscaf1nd':
        retval = 24*3600
    elif qstr == '2nd':
        retval = 48*3600
    elif qstr == '1nw':
        retval = 7*24*3600
    else:
        retval = int(qstr)*60*60
    return int(retval)


def getMcaIncl(mcafile,incl_mca='incl_sig'):
    incl_file=''
    mcaf = open(mcafile,'r')
    for l in mcaf.readlines():
        if re.match("\s*#.*", l): continue
        tokens = [t.strip() for t in l.split(':')]
        if len(tokens)<2: continue
        if tokens[0]==incl_mca and "+" in tokens[1]:
            options_str = [t.strip() for t in (l.split(';')[1]).split(',')]
            for o in options_str:
                if "IncludeMca" in o: 
                    incl_file = o.split('=')[1]
            break
    return incl_file

def writePdfSystsToMCA(mcafile,odir,vec_weight="hessWgt",syst="pdf",incl_mca='incl_sig',append=False):
    open("%s/systEnv-dummy.txt" % odir, 'a').close()
    incl_file=getMcaIncl(mcafile,incl_mca)
    if len(incl_file)==0: 
        print "Warning! '%s' include directive not found. Not adding pdf systematics samples to MCA file" % incl_mca
        return
    if append:
        filename = "%s/mca_systs.txt" % odir
        if not os.path.exists(filename): os.system('cp {mca_orig} {mca_syst}'.format(mca_orig=mcafile,mca_syst=filename))
    for i in range(1,NPDFSYSTS+1):
        postfix = "_{proc}_{syst}{idx}".format(proc=incl_mca.split('_')[1],syst=syst,idx=i)
        mcafile_syst = open(filename, 'a') if append else open("%s/mca%s.txt" % (odir,postfix), "w")
        mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="'+vec_weight+str(i)+'", PostFix="'+postfix+'" \n')
        pdfsysts.append(postfix)
    print "written ",syst," systematics relative to ",incl_mca

def writeQCDScaleSystsToMCA(mcafile,odir,syst="qcd",incl_mca='incl_sig',scales=[],append=False):
    open("%s/systEnv-dummy.txt" % odir, 'a').close()
    incl_file=getMcaIncl(mcafile,incl_mca)
    if len(incl_file)==0: 
        print "Warning! '%s' include directive not found. Not adding QCD scale systematics!"
        return
    if append:
        filename = "%s/mca_systs.txt" % odir
        if not os.path.exists(filename): os.system('cp {mca_orig} {mca_syst}'.format(mca_orig=mcafile,mca_syst=filename))    
    for scale in scales:
        for idir in ['Up','Dn']:
            postfix = "_{proc}_{syst}{idir}".format(proc=incl_mca.split('_')[1],syst=scale,idir=idir)
            mcafile_syst = open(filename, 'a') if append else open("%s/mca%s.txt" % (odir,postfix), "w")
            # this is now obsolete, now using the QCD scales in bins of wpt for signal only
            if scale == "wptSlope":
                sign  =  1 if idir == 'Dn' else -1
                asign = -1 if idir == 'Dn' else  1
                offset = 0.05; slope = 0.005;
                fstring = "wpt_slope_weight({wv}_pt\,{off:.3f}\,{slo:.3f})".format(wv=options.wvar,off=1.+asign*offset, slo=sign*slope)
                mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="'+fstring+'", PostFix="'+postfix+'" \n')
                qcdsysts.append(postfix)
            elif scale == "mW":
                ## central mass is 80419 MeV, the closest we have to that is 80420. will scale +- 50 MeV, i.e. 80470 for Up and 80370 for Dn
                fstring = "mass_80470" if idir == 'Up' else "mass_80370"
                mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="'+fstring+'", PostFix="'+postfix+'" \n')
                qcdsysts.append(postfix)
            else: ## alphaS and qcd scales are treated equally here. but they are different from the w-pT slope
                mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="qcd_'+scale+idir+'", PostFix="'+postfix+'" \n')
                qcdsysts.append(postfix)
            # for signal only, split scales in wpt
            if incl_mca == 'incl_sig':
                if 'muR' in scale or 'muF' in scale:
                    for ipt in range(1,11): ## start from 1 to 10
                        ## have to redo the postfix for these
                        postfix = "_{proc}_{syst}{ipt}{idir}".format(proc=incl_mca.split('_')[1],syst=scale,idir=idir,ipt=ipt)
                        mcafile_syst = open(filename, 'a') if append else open("%s/mca%s.txt" % (odir,postfix), "w")
                        ptcut = wptBinsScales(ipt)
                        wgtstr = 'TMath::Power(qcd_{sc}{idir}\,({wv}_pt>={ptlo}&&{wv}_pt<{pthi}))'.format(sc=scale,idir=idir,wv=options.wvar,ptlo=ptcut[0],pthi=ptcut[1])
                        mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="'+wgtstr+'", PostFix="'+postfix+'" \n')
                        qcdsysts.append(postfix)
            
    print "written ",syst," systematics relative to ",incl_mca

# def writeEfficiencyStatErrorSystsToMCA(mcafile,odir,channel,syst="EffStat",incl_mca='incl_sig',append=False):
#     open("%s/systEnv-dummy.txt" % odir, 'a').close()
#     incl_file=getMcaIncl(mcafile,incl_mca)
#     if len(incl_file)==0: 
#         print "Warning! '%s' include directive not found. Not adding pdf systematics samples to MCA file" % incl_mca
#         return
#     if append:
#         filename = "%s/mca_systs.txt" % odir
#         if not os.path.exists(filename): os.system('cp {mca_orig} {mca_syst}'.format(mca_orig=mcafile,mca_syst=filename))
#     etalo = -2.5 if channel=='el' else -2.4
#     deta = 0.1; nbins = int(2*abs(etalo)/deta)
#     for i in range(0,nbins):
#         etamin=etalo + i*deta; etamax=etalo + (i+1)*deta;
#         # 3 parameters used in the Erf fit vs pt per eta bin
#         for ipar in xrange(3):
#             postfix = "_{proc}_ErfPar{ipar}{syst}{idx}".format(proc=incl_mca.split('_')[1],syst=syst,ipar=ipar,idx=i+1)
#             mcafile_syst = open(filename, 'a') if append else open("%s/mca%s.txt" % (odir,postfix), "w")
#             weightFcn = 'effSystEtaBins({ipar}\,LepGood1_pdgId\,LepGood1_eta\,LepGood1_pt\,{emin:.1f}\,{emax:.1f})'.format(ipar=ipar,emin=etamin,emax=etamax)
#             mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="'+weightFcn+'", PostFix="'+postfix+'" \n')
#             etaeffsysts.append(postfix)
#     print "written ",syst," systematics relative to ",incl_mca

def writeEfficiencyStatErrorSystsToMCA_diffXsec(mcafile,odir,channel,syst="EffStat",incl_mca='incl_sig',append=False,genEtaBins=None):
# templates for diff xsec are sparse. For each signal process there is a single eta bin (actually 2, one on each eta side) that is not empty
# these reco bins might have the neighboring two with few events due to eta resolution, but the fractions is so small that they could be neglected
# so, while for helicity 3xN variations (N =50 or 48, it is the number of reco eta bins) are defined for each signal process (which is a |Yw| bin), 
# for the diff xsec it is better to have only 3*2 variations for each signal process (might become 3x6 if also the 2 neighboring eta bins are considered)
# In this case, defining the MCA such that it includes the nominal one is not feasible, because this would create the 3*50 variations.
# Therefore, I need to create here a new MCA file for the EffStat systematics

# I need to consider all the reco bins associated to a gen bin (the binning might be different)
# Let's assume the reco binning in eta is always 0.1 granular for simplicity (the EB-EE gap might non follow the convention, though)

    print "="*20
    print "Preparing MCA files for EffStat systematics"
    print "-"*20

    open("%s/systEnv-dummy.txt" % odir, 'a').close()
    incl_file=getMcaIncl(mcafile,incl_mca)
    if len(incl_file)==0: 
        print "Warning! '%s' include directive not found. Not adding EffStat systematics samples to MCA file" % incl_mca
        return
    if append:
        filename = "%s/mca_systs.txt" % odir
        if not os.path.exists(filename): os.system('cp {mca_orig} {mca_syst}'.format(mca_orig=mcafile,mca_syst=filename))
    etalo = -2.5 if channel=='el' else -2.4
    # avoid case where gen bins is in [0,2.4] for electrons but the template extends up to 2.5, for muons it is easier
    if genEtaBins[-1] == 2.4: etalo = -2.4 
    deta = 0.1
    nbins = int(2*(abs(etalo)+0.001)/deta) # sum an epsilon to etalow before division, to avoid rounding effects
    print "nbins = %s" % str(nbins)

    for i in range(0,nbins):
        etamin = etalo + i*deta 
        etamax = etamin + deta;
        # 3 parameters used in the Erf fit vs pt per eta bin

        # get the gen bin number that contains the reco bins considered here
        # note that the gen bins in eta cannot be more granular than deta 
        # indeed, it would not make sense that reco binning is less granular than the gen, and the reco will never be more granular than 0.1 in eta
        genbin = getArrayBinNumberFromValue(genEtaBins,abs((etamax+etamin)/2.)) 
        ietaMatch = "_ieta_"+str(genbin)+"_"
        print "eff. bin [%.1f, %.1f] --> ietaMatch = %s" %  (etamin,etamax,ietaMatch)

        # might implement the variation for the neighboring bins as well

        for ipar in xrange(3):
            postfix = "_{proc}_ErfPar{ipar}{syst}{idx}".format(proc=incl_mca.split('_')[1],syst=syst,ipar=ipar,idx=i+1)
            mcafile_syst = None
            try:
                mcafile_syst = open(filename, 'a') if append else open("%s/mca%s.txt" % (odir,postfix), "w")
            finally:
                if mcafile_syst is not None:
                    weightFcn = 'effSystEtaBins({ipar}\,LepGood1_pdgId\,LepGood1_eta\,LepGood1_pt\,{emin:.1f}\,{emax:.1f})'.format(ipar=ipar,emin=etamin,emax=etamax)
                    etaeffsysts.append(postfix)
                    # incl_file is something like "w-helicity-13TeV/wmass_e/mca-includes/mca-80X-wenu-sigInclCharge_binned_eta_pt.txt"
                    # must remove the " to use the path
                    incl_file_path = incl_file.replace('"','') 
                    with open(incl_file_path, "r") as fileMCA:   
                        for line in fileMCA:
                            if line.startswith("W"):
                                line  = line.rstrip('\n')  # remove newline at the end
                                procName = line.split(":")[0]
                                procName = procName.strip()
                                if "outliers" in procName or ietaMatch in procName:
                                    #ieta,ipt = get_ieta_ipt_from_process_name(procName) # only for non-outliers
                                    # same line but different process name and one additional weight
                                    newline = procName+postfix + " : " + ":".join(line.split(":")[1:]) + ', AddWeight="' + weightFcn + '"\n'
                                    newline = line.replace(procName,procName+postfix) + ', AddWeight="' + weightFcn + '"\n'
                                    mcafile_syst.write(newline)
                    mcafile_syst.close()
                else:
                    raise RuntimeError, "Could not open file mcafile_syst in writeEfficiencyStatErrorSystsToMCA_diffXsec()"

    print "written ",syst," systematics relative to ",incl_mca
    print "="*20


##############

def writePdfSystsToSystFile(filename,sample="W.*",syst="CMS_W_pdf"):
    SYSTFILEALL=('.').join(filename.split('.')[:-1])+"-all.txt"
    copyfile(filename,SYSTFILEALL)
    systfile=open(SYSTFILEALL,"a")
    for i in range(NPDFSYSTS/2):
        systfile.write(syst+str(i+1)+"  : "+sample+" : .* : pdf"+str(i+1)+" : templates\n")
    print "written pdf syst configuration to ",SYSTFILEALL
    return SYSTFILEALL


def submitBatch(dcname,outdir,mkShCardsCmd,options):
    srcfile=outdir+"/jobs/"+dcname+".sh"
    logfile=outdir+"/logs/"+dcname+".log"
    srcfile_op = open(srcfile,"w")
    srcfile_op.write("#! /bin/sh\n")
    srcfile_op.write("ulimit -c 0 -S\n")
    srcfile_op.write("ulimit -c 0 -H\n")
    srcfile_op.write("cd {cmssw};\neval $(scramv1 runtime -sh);\ncd {dir};\n".format( 
            dir = os.getcwd(), cmssw = os.environ['CMSSW_BASE']))
    srcfile_op.write(mkShCardsCmd)
    os.system("chmod a+x "+srcfile)
    cmd = "bsub -q {queue} -o {dir}/{logfile} {dir}/{srcfile}\n".format(
        queue=options.queue, dir=os.getcwd(), logfile=logfile, srcfile=srcfile)
    if options.dryRun: print cmd
    else: os.system(cmd)

# currently not used
def makeCondorFile(srcFile):
    condor_file = open(srcFile.replace('.sh','.condor'),'w')
    condor_file.write('''Universe = vanilla
Executable = {scriptName}
use_x509userproxy = $ENV(X509_USER_PROXY)
Log        = {pid}.log
Output     = {pid}.out
Error      = {pid}.error
getenv      = True
environment = "LS_SUBCWD={here}"
next_job_start_delay = 1
request_memory = 4000
+MaxRuntime = {rt}
queue 1\n
'''.format(scriptName=srcFile, pid=srcFile.replace('.sh',''), rt=getCondorTime(options.queue), here=os.environ['PWD'] ) )
    if os.environ['USER'] in ['mdunser', 'psilva']:
        condor_file.write('+AccountingGroup = "group_u_CMST3.all"\n')
    condor_file.close()


def getShFile(jobdir, name):
    tmp_srcfile_name = jobdir+'/job_{i}.sh'.format(i=name)
    tmp_srcfile = open(tmp_srcfile_name, 'w')
    tmp_srcfile.write("#! /bin/bash\n")
    tmp_srcfile.write("ulimit -c 0 -S\n")
    tmp_srcfile.write("ulimit -c 0 -H\n")
    tmp_srcfile.write("cd {cmssw};\neval $(scramv1 runtime -sh);\ncd {d};\n".format( d= os.getcwd(), cmssw = os.environ['CMSSW_BASE']))
    return tmp_srcfile_name, tmp_srcfile



if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] mc.txt cuts.txt var bins systs.txt outdir ")
    parser.add_option("-q", "--queue",    dest="queue",     type="string", default=None, help="Run jobs on lxbatch instead of locally");
    parser.add_option("-l", "--lumi",    dest="integratedLuminosity",     type="float", default=35.9, help="Integrated luminosity");
    parser.add_option("--dry-run", dest="dryRun",    action="store_true", default=False, help="Do not run the job, only print the command");
    parser.add_option("-s", "--signal-cards",  dest="signalCards",  action="store_true", default=False, help="Make the signal part of the datacards");
    parser.add_option("-b", "--bkgdata-cards", dest="bkgdataCards", action="store_true", default=False, help="Make the background and data part of the datacards");
    parser.add_option("-W", "--weight", dest="weightExpr", default="1", help="Event weight expression (default 1)");
    parser.add_option("-P", "--path", dest="path", type="string",default=None, help="Path to directory with input trees and pickle files");
    parser.add_option("-C", "--channel", dest="channel", type="string", default='el', help="Channel. either 'el' or 'mu'");
    parser.add_option(      "--gen-binning", dest="genBinning", type="string", default='', help="Pass gen |eta|-pt binning: format is [0,1.5,2.5]*[30,35,40,45]");
    parser.add_option("--groupSignalBy", dest="groupSignalBy", type="int", default='0', help="Group signal bins in bunches of N (pass N as argument). Default is 0, meaning not using this option. This option will reduce the number of chunk datacard for signal,but jobs will last for longer");
    parser.add_option("--not-unroll2D", dest="notUnroll2D", action="store_true", default=False, help="Do not unroll the TH2Ds in TH1Ds needed for combine (to make 2D plots)");
    parser.add_option("--pdf-syst", dest="addPdfSyst", action="store_true", default=False, help="Add PDF systematics to the signal (need incl_sig directive in the MCA file)");
    parser.add_option("--qcd-syst", dest="addQCDSyst", action="store_true", default=False, help="Add QCD scale systematics to the signal (need incl_sig directive in the MCA file)");
    parser.add_option("--xsec-sigcard-binned", dest="xsec_sigcard_binned",   action="store_true", default=False, help="When doing differential cross-section, will make 1 signal card for each 2D template bin (default is False because the number of cards easily gets huge)");
    parser.add_option("--useLSF", action='store_true', default=False, help="force use LSF. default is using condor");
    parser.add_option('-w', "--wvar", type="string", default='prefsrw', help="Choose between genw (for dressed lepton) and prefsrw (preFSR lepton)");  
    parser.add_option("--usePickle", dest="usePickle", action="store_true", default=False, help="Read Sum Weights from Pickle file (needed only if using old samples that did not have the histogram inside). By default, the histogram is used"); 
    (options, args) = parser.parse_args()

    if len(sys.argv) < 6:
        parser.print_usage()
        quit()

    if options.genBinning == "":
        print "Warning: need to pass binning for gen |eta|-pt. Use option --gen-binning. Exit"
        quit()

    FASTTEST=''
    #FASTTEST='--max-entries 1000 '
    T=options.path
    print "\n"
    print "Used trees from: ",T
    J=2
    MCA = args[0]
    CUTFILE = args[1]
    fitvar = args[2]
    binning = args[3]
    SYSTFILE = args[4]

    genBinning = options.genBinning
    #print "MCA: ",MCA
    luminosity = options.integratedLuminosity

    if not os.path.exists("cards/"):
        os.makedirs("cards/")
    outdir="cards/"+args[5]

    if not os.path.exists(outdir): 
        os.makedirs(outdir)
    if options.queue :
        if not os.path.exists(outdir+"/jobs"): 
            os.mkdir(outdir+"/jobs")                    
            os.mkdir(outdir+"/mca")
        if not os.path.exists(outdir+"/logs"):
            os.mkdir(outdir+"/logs")
        if not os.path.exists(outdir+"/outs"):
            os.mkdir(outdir+"/outs")
        if not os.path.exists(outdir+"/errs"):
            os.mkdir(outdir+"/errs")

    # copy some cfg for bookkeeping
    os.system("cp %s %s" % (CUTFILE, outdir))
    os.system("cp %s %s" % (MCA, outdir))

    ## save template binning (eta on X, pt on y axis)
    ptEta_binfile = open(outdir+'/binningPtEta.txt','w')
    ptEta_binfile.write("#Template binning: eta-pt on x-y axis\n")
    ptEta_binfile.write("#Gen binning   : |eta|-pt on x-y axis\n")
    ptEta_binfile.write("reco: "+binning+"\n")
    ptEta_binfile.write("gen: "+genBinning+"\n")
    ptEta_binfile.write('\n')
    ptEta_binfile.close()

    etabinning=genBinning.split('*')[0]    # this is like [a,b,c,...], and is of type string. We nedd to get an array
    ptbinning=genBinning.split('*')[1]
    etabinning = getArrayParsingString(etabinning)
    ptbinning = getArrayParsingString(ptbinning)
    nptbins = len(ptbinning)-1
    netabins = len(etabinning)-1
    nGenCategories = (netabins)*(nptbins)
    print "There are %d * %d = %d gen |eta|*pt signal categories for each charge" % (netabins,nptbins,nGenCategories)
    
    if options.addPdfSyst:
        # write the additional systematic samples in the MCA file
        writePdfSystsToMCA(MCA,outdir+"/mca") # on W + jets 
        writePdfSystsToMCA(MCA,outdir+"/mca",incl_mca='incl_dy') # on DY + jets
        # write the complete systematics file (this was needed when trying to run all systs in one job)
        # SYSTFILEALL = writePdfSystsToSystFile(SYSTFILE)
    if options.addQCDSyst:
        scales = ['muR','muF',"muRmuF", "alphaS"]
        #writeQCDScaleSystsToMCA(MCA,outdir+"/mca",scales=scales+["wptSlope", "mW"])
        writeQCDScaleSystsToMCA(MCA,outdir+"/mca",scales=scales+["mW"])  # no more wpt inclusive, now we have the QCD scales in bins of wpt
        writeQCDScaleSystsToMCA(MCA,outdir+"/mca",scales=scales,incl_mca='incl_dy')        

    writeEfficiencyStatErrorSystsToMCA_diffXsec(MCA,outdir+"/mca",options.channel,genEtaBins=[float(x) for x in etabinning])

    ARGS=" ".join([MCA,CUTFILE,"'"+fitvar+"' "+"'"+binning+"'",SYSTFILE])
    BASECONFIG=os.path.dirname(MCA)
    if options.queue:
        ARGS = ARGS.replace(BASECONFIG,os.getcwd()+"/"+BASECONFIG)
    OPTIONS=" -P "+T+" --s2v -j "+str(J)+" -l "+str(luminosity)+" -f --obj tree "+FASTTEST
    if not os.path.exists(outdir): os.makedirs(outdir)
    OPTIONS+=" -F Friends '{P}/friends/tree_Friend_{cname}.root' "
    if not options.notUnroll2D:
        OPTIONS+=" --2d-binning-function unroll2Dto1D "
    if options.usePickle:
        OPTIONS+=" --usePickle "

    if options.queue:
        import os, sys
        basecmd = "bsub -q {queue} {dir}/lxbatch_runner.sh {dir} {cmssw} python {self}".format(
                    queue = options.queue, dir = os.getcwd(), cmssw = os.environ['CMSSW_BASE'], self=sys.argv[0]
                )

    ngroup = 0
    if options.groupSignalBy:
        ngroup = int(options.groupSignalBy)
        # below, subtract 1 because nGenCategories starts from 1 (minimum 1 gen bin, but for the following algorithm it should start from 0)
        # then add 1 because xrange excludes the last index
        loopBins = int((nGenCategories-1)/ngroup)+1 
        print "They will be grouped in bunches of %d (%d groups)" % (ngroup, loopBins)
    elif options.xsec_sigcard_binned:
        loopBins = nGenCategories
    else:
        loopBins = 1

    ## previous lines were meant to distinguish the case where the signal template is made all at once (a single TH2) or dividing into each bin
    ## The former requires just one job and create one datacard and one shape.root file, but then I need a way to allow each bin
    ## of the TH2 to float independently of the other (with some constraints), a kind of bin-by-uncertainty
    ## The former treat all bins as the rapidity bin in the helicity fit, but the number of bins here can be huge (let alone the PDf variations ...)
    ## Another way is to make signal cards grouping bins in bunches with some criteria
    ## this is enabled by option.groupSignalBy
    ## In this case, I set loopBins so to loop from 0 to int(nGenCategories/ngroup) 

    POSCUT=" -A alwaystrue positive 'LepGood1_charge>0' "
    NEGCUT=" -A alwaystrue negative 'LepGood1_charge<0' "
    fullJobList = []

    if options.signalCards:

        print "MAKING SIGNAL PART: "

        # this is a special case, each var has its own MCA file, which manages both charges, outliers and so on
        # for the same reason, it must be done one time only, so just for ibin == 0
        if len(etaeffsysts):
            for ivar, var in enumerate(etaeffsysts):

                if "EffStat" in var:

                    IARGS = ARGS.replace(MCA,"{outdir}/mca/mca{syst}.txt".format(outdir=outdir,syst=var))
                    IARGS = IARGS.replace(SYSTFILE,"{outdir}/mca/systEnv-dummy.txt".format(outdir=outdir))
                    #print "Running the systematic: ",var
                    if not os.path.exists(outdir): os.makedirs(outdir)
                    if options.queue and not os.path.exists(outdir+"/jobs"): os.mkdir(outdir+"/jobs")

                    dcname = "W_{channel}{syst}".format(channel=options.channel,syst=var)
                    BIN_OPTS=OPTIONS + " -W '" + options.weightExpr + "'" + " -o "+dcname+" --asimov --od "+outdir
                    if options.queue:
                        mkShCardsCmd = "python {dir}/makeShapeCards.py {args} \n".format(dir = os.getcwd(), args = IARGS+" "+BIN_OPTS)
                        if options.useLSF:
                            submitBatch(dcname,outdir,mkShCardsCmd,options)
                        else:
                            fullJobList.append(mkShCardsCmd)
                    else:
                        cmd = "python makeShapeCards.py "+IARGS+" "+BIN_OPTS
                        if options.dryRun: print cmd
                        else:
                            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                            out, err = p.communicate() 
                            result = out.split('\n')
                            for lin in result:
                                if not lin.startswith('#'):
                                    print(lin)

                ######  if not EffStat go on with the rest


        # we will use a trick to make the outliers (gen bins outside the reco template)
        # in the loop below ibin should be in range(loopBins): we actually do it up to loopBins+1 and treat the last one in a special way
        # In this way, when ibin == loopBins we know we are considering the outliers

        for ibin in xrange(loopBins + 1):
            wsyst = ['']+[x for x in pdfsysts+qcdsysts if 'sig' in x]
            for ivar,var in enumerate(wsyst):
                
                for charge in ['plus','minus']:
                    antich = 'plus' if charge == 'minus' else 'minus'
                    # ivar == 0 --> nominal, root file should also contain lepton scale systematic if implemented
                    # ivar != 0 --> shape systematics: pdf, qcd scales, wptSlope, etc...
                    if ivar==0: 
                        IARGS = ARGS
                    else: 
                        IARGS = ARGS.replace(MCA,"{outdir}/mca/mca{syst}.txt".format(outdir=outdir,syst=var))
                        IARGS = IARGS.replace(SYSTFILE,"{outdir}/mca/systEnv-dummy.txt".format(outdir=outdir))
                        #print "Running the systematic: ",var
                    if not os.path.exists(outdir): os.makedirs(outdir)
                    if options.queue and not os.path.exists(outdir+"/jobs"): os.mkdir(outdir+"/jobs")
                    syst = '' if ivar==0 else var

                    # scale, lepEff, ... added to signal, with ivar==0, otherwise eclude (I don't want elescale variation on pdfs)
                    if options.channel == "el":
                        scaleXP = "" if ivar == 0 else ",.*_elescale_.*,.*_lepeff_.*"  # note comma in the beginning
                        flips = ",Flips"
                    else:
                        scaleXP = "" if ivar == 0 else ",.*_muscale_.*,.*_lepeff_.*"  # note comma in the beginning
                        flips = ""
                    xpsel=' --xp "W{antich}.*{flips},Z,Top,DiBosons,TauDecaysW,data.*{xpScale}" --asimov '.format(antich=antich,xpScale=scaleXP,flips=flips)      
                    recoChargeCut = POSCUT if charge=='plus' else NEGCUT

                    if ibin == loopBins:
                        # do outliers
                        
                        #print "Making card for pt<%s || pt>=%s || |eta|>=%s and signal process with charge %s " % (ptbinning[0],ptbinning[nptbins],
                        #                                                                                           etabinning[netabins],charge)
                        # caution with ending .* in regular expression: pt bin = 1 will match 11,12,... as well
                        # here we don't need regular expression there is just one bin
                        if ivar == 0:
                            if options.channel == "el":
                                lepscale = ",W{charge}_{channel}_outliers_elescale.*,W{charge}_{channel}_outliers_lepeff_.*".format(charge=charge, channel=options.channel)
                            else:
                                lepscale = ",W{charge}_{channel}_outliers_muscale.*,W{charge}_{channel}_outliers_lepeff_.*".format(charge=charge, channel=options.channel)
                            selectedSigProcess = ' -p W{charge}_{channel}_outliers{lepscale}  '.format(charge=charge, channel=options.channel,lepscale=lepscale)  
                        else:
                            if "EffStat" in syst:
                                # EffStat systematics are not applied to any bins, there is a specific MCA. For the outliers, it is always applied
                                # but let's not define the card from here
                                pass
                            else:
                                selectedSigProcess = ' -p W{charge}_{channel}_outliers{syst}  '.format(charge=charge, channel=options.channel,syst=syst)  

                        ##dcname = "W{charge}_{channel}_ieta_{ieta}_ipt_{ipt}{syst}".format(charge=charge, channel=options.channel,syst=syst)
                        ## keep same logic as before for the datacard name
                        dcname = "W{charge}_{channel}_outliers_group_{gr}{syst}".format(charge=charge,channel=options.channel,gr=ibin,syst=syst)


                    else:
                        # do bins inside the gen binning

                        if options.groupSignalBy:
                            # if we are here, loopBins is not the number of bins in 2D template
                            # rather, it is the number of groups with ngroup bins each (+1 because xrange will exclude the last number)
                            # to get the ieta,ipt we must obtain again the real globalbin number
                            # the cut for this bin is directly in the MCA file (in the process definition)
                            selectedSigProcess = ' -p '
                            for n in xrange(ngroup):
                                tmpGlobalBin = n + ibin * ngroup
                                ieta,ipt = getXYBinsFromGlobalBin(tmpGlobalBin,netabins)
                                signalPrefix = "W{charge}_{channel}_ieta_{ieta}_ipt_{ipt}".format(charge=charge, channel=options.channel,ieta=ieta,ipt=ipt)

                                # caution with ending .* in regular expression: pt bin = 1 will match 11,12,... as well
                                # consider elescale separately (for systematics, i.e. ivar!=0, it is excluded with --xp)
                                if ivar == 0:
                                    if options.channel == "el":
                                        lepscale = "{sigPfx}_elescale.*,{sigPfx}_lepeff.*,".format(sigPfx=signalPrefix)
                                    else:
                                        lepscale = "{sigPfx}_muscale.*,{sigPfx}_lepeff.*,".format(sigPfx=signalPrefix)
                                    selectedSigProcess += '{sigPfx},{lepscale}'.format(sigPfx=signalPrefix,lepscale=lepscale)
                                else:
                                    selectedSigProcess += '{sigPfx}{syst},'.format(sigPfx=signalPrefix,syst=syst)
                            if selectedSigProcess.endswith(','):
                                selectedSigProcess = selectedSigProcess[:-1]  # remove comma at the end
                            selectedSigProcess += " "    # add some space to separate this option to possible following commands
                            dcname = "W{charge}_{channel}_group_{gr}{syst}".format(charge=charge, channel=options.channel,gr=ibin,syst=syst)

                        elif options.xsec_sigcard_binned:
                            # would be equivalent to options.groupSignalBy == 1
                            # might be removed at some point
                            ieta,ipt = getXYBinsFromGlobalBin(ibin,netabins)
                            signalPrefix = "W{charge}_{channel}_ieta_{ieta}_ipt_{ipt}".format(charge=charge, channel=options.channel,ieta=ieta,ipt=ipt)

                            #print "Making card for %s<=pt<%s, %s<=|eta|<%s and signal process with charge %s " % (ptbinning[ipt],ptbinning[ipt+1],
                            #                                                                                    etabinning[ieta],etabinning[ieta+1],
                            #                                                                                    charge)
                            ##########################
                            # I don't need anymore to change the cut, because I am already running with an mca file having one process for each bin
                            # (the cut is in the process definition inside the mca)
                            # ptcut=" -A alwaystrue pt%d '%s>=%s && %s<%s' " % (ipt,ptVarCut,ptbinning[ipt],ptVarCut,ptbinning[ipt+1])
                            # etacut=" -A alwaystrue eta%d '%s>=%s && %s<%s' " % (ieta,etaVarCut,etabinning[ieta],etaVarCut,etabinning[ieta+1])
                            # recoChargeCut += (ptcut + etacut)

                            # caution with ending .* in regular expression: pt bin = 1 will match 11,12,... as well
                            # here we don't need regular expression there is just one bin
                            if ivar == 0:
                                if options.channel == "el":
                                    lepscale = ",{sigPfx}_elescale.*,{sigPfx}_lepEff.*".format(sigPfx=signalPrefix)
                                else:
                                    lepscale = ",{sigPfx}_muscale.*,{sigPfx}_lepEff.*".format(sigPfx=signalPrefix)
                                selectedSigProcess = ' -p {sigPfx}{lepscale}  '.format(sigPfx=signalPrefix,lepscale=lepscale)  
                            else:
                                selectedSigProcess = ' -p {sigPfx}{syst}  '.format(sigPfx=signalPrefix,syst=syst)  

                            ##dcname = "W{charge}_{channel}_ieta_{ieta}_ipt_{ipt}{syst}".format(charge=charge, channel=options.channel,ieta=ieta,ipt=ipt,syst=syst)
                            ## keep same logic as before for the datacard name
                            dcname = "W{charge}_{channel}_group_{gr}{syst}".format(charge=charge,channel=options.channel,gr=ibin,syst=syst)
                        else:
                            dcname = "W{charge}_{channel}_group_{gr}{syst}".format(charge=charge, channel=options.channel,gr=ibin,syst=syst)

                    # end of -> if ibin == loopBins:
                    ####################

                    BIN_OPTS=OPTIONS + " -W '" + options.weightExpr + "'" + " -o "+dcname+" --od "+outdir + xpsel + selectedSigProcess + recoChargeCut
                    if options.queue:
                        mkShCardsCmd = "python {dir}/makeShapeCards.py {args} \n".format(dir = os.getcwd(), args = IARGS+" "+BIN_OPTS)
                        if options.useLSF:
                            submitBatch(dcname,outdir,mkShCardsCmd,options)
                        else:
                            fullJobList.append(mkShCardsCmd)
                    else:
                        cmd = "python makeShapeCards.py "+IARGS+" "+BIN_OPTS
                        if options.dryRun: print cmd
                        else:
                            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                            out, err = p.communicate() 
                            result = out.split('\n')
                            for lin in result:
                                if not lin.startswith('#'):
                                    print(lin)


    if options.bkgdataCards:
        print "MAKING BKG and DATA PART:\n"
        for charge in ['plus','minus']:
            xpsel=' --xp "W.*" ' 
            if len(pdfsysts+qcdsysts)>1: # 1 is the nominal 
                xpsel+=' --xp "Z" '
            chargecut = POSCUT if charge=='plus' else NEGCUT
            dcname = "bkg_and_data_{channel}_{charge}".format(channel=options.channel, charge=charge)
            BIN_OPTS=OPTIONS + " -W '" + options.weightExpr + "'" + " -o "+dcname+" --od "+outdir + xpsel + chargecut
            if options.queue:
                mkShCardsCmd = "python {dir}/makeShapeCards.py {args} \n".format(dir = os.getcwd(), args = ARGS+" "+BIN_OPTS)
                if options.useLSF:
                    submitBatch(dcname,outdir,mkShCardsCmd,options)
                else:
                    fullJobList.append(mkShCardsCmd)
            else:
                cmd = "python makeShapeCards.py "+ARGS+" "+BIN_OPTS
                if options.dryRun: print cmd
                else:
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                    out, err = p.communicate() 
                    result = out.split('\n')
                    for lin in result:
                        if not lin.startswith('#'):
                            print(lin)

    if options.bkgdataCards and len(pdfsysts+qcdsysts)>1:
        dysyst = ['']+[x for x in pdfsysts+qcdsysts if 'dy' in x]
        for ivar,var in enumerate(dysyst):
            for charge in ['plus','minus']:
                antich = 'plus' if charge == 'minus' else 'minus'
                if ivar==0: 
                    IARGS = ARGS
                else: 
                    IARGS = ARGS.replace(MCA,"{outdir}/mca/mca{syst}.txt".format(outdir=outdir,syst=var))
                    IARGS = IARGS.replace(SYSTFILE,"{outdir}/mca/systEnv-dummy.txt".format(outdir=outdir))
                    print "Running the DY with systematic: ",var
                print "Making card for DY process with charge ", charge
                chcut = POSCUT if charge=='plus' else NEGCUT
                xpsel=' --xp "[^Z]*" --asimov '
                syst = '' if ivar==0 else var
                dcname = "Z_{channel}_{charge}{syst}".format(channel=options.channel, charge=charge,syst=syst)
                BIN_OPTS=OPTIONS + " -W '" + options.weightExpr + "'" + " -o "+dcname+" --od "+outdir + xpsel + chcut
                if options.queue:
                    mkShCardsCmd = "python {dir}/makeShapeCards.py {args} \n".format(dir = os.getcwd(), args = IARGS+" "+BIN_OPTS)
                    if options.useLSF:
                        submitBatch(dcname,outdir,mkShCardsCmd,options)
                    else:
                        fullJobList.append(mkShCardsCmd)
                else:
                    cmd = "python makeShapeCards.py "+IARGS+" "+BIN_OPTS
                    if options.dryRun: print cmd
                    else:
                        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                        out, err = p.communicate() 
                        result = out.split('\n')
                        for lin in result:
                            if not lin.startswith('#'):
                                print(lin)


# this part is for condor
    if not options.useLSF and len(fullJobList):
        reslist = list(fullJobList)

        ## analysis too large protection             
        reslistnew = []
        npart = 0
        for ic, pc in enumerate(reslist):
            nc = pc.replace('--od {od}'.format(od=outdir), '--od {od}/part{n}'.format(od=outdir,n=npart))
            reslistnew.append(nc)
            if not (ic+1)%6000:
                npart += 1

        reslist = reslistnew


        ## split the list into non-bkg and bkg_and_data
        bkglist = [i for i in reslist if     'bkg_and_data' in i]
        reslist = [i for i in reslist if not 'bkg_and_data' in i]

        nj = len(reslist)
        print 'full number of python commands to submit', nj+len(bkglist)
        #print '   ... grouping them into bunches of', options.groupJobs

        njobs = nj
        # if not nj%options.groupJobs:
        #     njobs = int(nj/options.groupJobs)
        # else: 
        #     njobs = int(nj/options.groupJobs) + 1

        jobdir = outdir+'/jobs/'
        logdir = outdir+'/logs/'
        outdirCondor = outdir+'/outs/'
        errdir = outdir+'/errs/'
        os.system('mkdir -p '+jobdir)
        subcommands = []

        sourcefiles = []
        ## a bit awkward, but this keeps the bkg and data jobs separate. do the backgrounds first
        for ib in bkglist:
            pm = 'plus' if 'positive' in ib else 'minus'
            tmp_srcfile_name, tmp_srcfile = getShFile(jobdir, 'bkg_'+pm)
            tmp_srcfile.write(ib)
            tmp_srcfile.close()
            sourcefiles.append(tmp_srcfile_name)
            #makeCondorFile(tmp_srcfile_name)
            #subcommands.append( 'condor_submit {rf} '.format(rf = tmp_srcfile_name.replace('.sh','.condor')) )

        ## now do the others.
        for ij in range(njobs):
            tmp_srcfile_name, tmp_srcfile = getShFile(jobdir, ij)
            #tmp_n = options.groupJobs
            #while len(reslist) and tmp_n:
            one = True  # I might decide to group commands
            while len(reslist) and one:
                tmp_pycmd = reslist[0]
                tmp_srcfile.write(tmp_pycmd)
                reslist.remove(tmp_pycmd)
                one = False
            tmp_srcfile.close()
            sourcefiles.append(tmp_srcfile_name)
            #makeCondorFile(tmp_srcfile_name)
            #subcommands.append( 'condor_submit {rf} '.format(rf = tmp_srcfile_name.replace('.sh','.condor')) )

        dummy_exec = open(jobdir+'/dummy_exec.sh','w')
        dummy_exec.write('#!/bin/bash\n')
        dummy_exec.write('bash $*\n')
        dummy_exec.close()

        condor_file_name = jobdir+'/condor_submit.condor'
        condor_file = open(condor_file_name,'w')
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
           rt=getCondorTime(options.queue), here=os.environ['PWD'] ) )
        if os.environ['USER'] in ['mdunser', 'psilva']:
            condor_file.write('+AccountingGroup = "group_u_CMST3.all"\n\n\n')
        for sf in sourcefiles:
            condor_file.write('arguments = {sf} \nqueue 1 \n\n'.format(sf=os.path.abspath(sf)))
        condor_file.close()

        #print 'i have {n} jobs to submit!'.format(n=len(subcommands))
        if options.dryRun:
            print 'running dry, printing the commands...'
            print 'condor_submit ',condor_file_name
            #for cmd in subcommands:
            #    print cmd
        else:
            print 'submitting for real...'
            os.system('condor_submit {cfn}'.format(cfn=condor_file_name))
            ##sigDyBkg = '_signal' if options.signalCards else '_background'
            ##pipefilename = args[5]+'_submission{t}.sh'.format(t=sigDyBkg)
            ##pipefile = open(pipefilename, 'w')
            ##print 'piping all the commands in file', pipefilename
            ##for cmd in subcommands:
            ##    pipefile.write(cmd+'\n')
            ##pipefile.close()
            ##os.system('bash '+pipefilename)

    print 'done'
