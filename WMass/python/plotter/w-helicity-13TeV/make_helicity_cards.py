#!/usr/bin/env python
from shutil import copyfile
import re, sys, os, os.path, subprocess, json, ROOT
import numpy as np
# import some parameters from wmass_parameters.py, they are also used by other scripts
from wmass_parameters import *


def wptBinsScales(i):
    wptbins = [0.0, 1.971, 2.949, 3.838, 4.733, 5.674, 6.684, 7.781, 8.979, 10.303, 11.777, 13.435, 15.332, 17.525, 20.115, 23.245, 27.173, 32.414, 40.151, 53.858, 13000.0]
    if len(wptbins)<2*i:
        print 'you are asking too much from the wpt binning for decorrelation of scales'
    ptlo = wptbins[2*(i-1)]
    pthi = wptbins[2*i]
    return [ptlo, pthi]
    

def getCondorTime(qstr):
    retval = ''
    if   qstr == '1nh':
        retval = 3600
    elif qstr == '8nh':
        retval = 28800
    elif qstr == '1nd':
        retval = 24*3600
    elif qstr == '2nd':
        retval = 48*3600
    elif qstr == '1nw':
        retval = 7*24*3600
    else:
        retval = int(qstr)*60*60
    return int(retval)

def intermediateBinning(diff):

    n25 = int(diff/0.25)

    rest = diff - n25*0.25

    if any([np.isclose(rest,0.2), np.isclose(rest,0.15)]):
        bins = [rest]
        bins += [0.25 for i in range(n25)]
    elif rest < 0.15:
        bins = [0.25 for i in range(n25-1)] + [0.25+rest]

    return bins

## infile should be the reco/gen efficiency file of the electrons
def makeYWBinning(infile, cutoff=5000):
    
    histo_file = ROOT.TFile(infile, 'READ')
    
    yw_binning = {}
    
    for ch in ['plus', 'minus']:
        for pol in ['left', 'right', 'long']:
            cp = '{ch}_{pol}'.format(ch=ch,pol=pol)
            yw_binning[cp] = [i*0.15 for i in range(11)]
            hname = 'w{ch}_abswy_reco_W{ch}_{pol}'.format(ch=ch,pol=pol)
            histo = histo_file.Get(hname)
            nlast = 0.
            for ibin in reversed(range(1,histo.GetNbinsX()+1)):
                if not nlast > cutoff:
                    nlast += histo.GetBinContent(ibin)
                else:
                    ilast = ibin
                    ylast = histo.GetXaxis().GetBinUpEdge(ilast)
                    diffTo1p5 = ylast - 1.5
                    intermediate_binning = intermediateBinning(diffTo1p5)
                    for i in intermediate_binning:
                        yw_binning[cp] += [yw_binning[cp][-1]+i]
                    yw_binning[cp] += [histo.GetXaxis().GetXmax()]
                    yw_binning[cp] = [float('{n:.2f}'.format(n=n)) for n in yw_binning[cp] ]
                    break
    
    return yw_binning

def makeFixedYWBinning():
    yw_binning = {}
    
    for ch in ['plus', 'minus']:
        for pol in ['left', 'right', 'long']:
            cp = '{ch}_{pol}'.format(ch=ch,pol=pol)
            yw_binning[cp]  = [float('{n:.2f}'.format(n=    i*0.20)) for i in range(16) ] + [6.0]
            
    return yw_binning
            


NPDFSYSTS=60 # Hessian variations of NNPDF 3.0
pdfsysts=[] # array containing the PDFs signal variations
qcdsysts=[] # array containing the QCD scale signal variations
etaeffsysts=[] # array containing the uncorrelated efficiency systematics vs eta

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
            elif 'muR' in scale or 'muF' in scale:
                if options.signalCards:
                    for ipt in range(1,11): ## start from 1 to 10
                        ## have to redo the postfix for these
                        postfix = "_{proc}_{syst}{ipt}{idir}".format(proc=incl_mca.split('_')[1],syst=scale,idir=idir,ipt=ipt)
                        mcafile_syst = open(filename, 'a') if append else open("%s/mca%s.txt" % (odir,postfix), "w")
                        ptcut = wptBinsScales(ipt)
                        wgtstr = 'TMath::Power(qcd_{sc}{idir}\,({wv}_pt>={ptlo}&&{wv}_pt<{pthi}))'.format(sc=scale,idir=idir,wv=options.wvar,ptlo=ptcut[0],pthi=ptcut[1])
                        mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="'+wgtstr+'", PostFix="'+postfix+'" \n')
                        qcdsysts.append(postfix)
                else:
                    ## for the Z only do the unnumbered ones
                    postfix = "_{proc}_{syst}{idir}".format(proc=incl_mca.split('_')[1],syst=scale,idir=idir)
                    mcafile_syst = open(filename, 'a') if append else open("%s/mca%s.txt" % (odir,postfix), "w")
                    wgtstr = 'qcd_{sc}{idir}'.format(sc=scale,idir=idir)
                    mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="'+wgtstr+'", PostFix="'+postfix+'" \n')
                    qcdsysts.append(postfix)
            else: ## alphaS and qcd scales are treated equally here. but they are different from the w-pT slope
                mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="qcd_'+scale+idir+'", PostFix="'+postfix+'" \n')
                qcdsysts.append(postfix)
    print "written ",syst," systematics relative to ",incl_mca

def writeEfficiencyStatErrorSystsToMCA(mcafile,odir,channel,syst="EffStat",incl_mca='incl_sig',append=False):
    open("%s/systEnv-dummy.txt" % odir, 'a').close()
    incl_file=getMcaIncl(mcafile,incl_mca)
    if len(incl_file)==0: 
        print "Warning! '%s' include directive not found. Not adding pdf systematics samples to MCA file" % incl_mca
        return
    if append:
        filename = "%s/mca_systs.txt" % odir
        if not os.path.exists(filename): os.system('cp {mca_orig} {mca_syst}'.format(mca_orig=mcafile,mca_syst=filename))
    etalo = -2.5 if channel=='el' else -2.4001
    deta = 0.1; nbins = int(2*abs(etalo)/deta)
    for i in range(0,nbins):
        etamin=etalo + i*deta; etamax=etalo + (i+1)*deta;
        # 3 parameters used in the Erf fit vs pt per eta bin
        for ipar in xrange(3):
            postfix = "_{proc}_ErfPar{ipar}{syst}{idx}".format(proc=incl_mca.split('_')[1],syst=syst,ipar=ipar,idx=i+1)
            mcafile_syst = open(filename, 'a') if append else open("%s/mca%s.txt" % (odir,postfix), "w")
            weightFcn = 'effSystEtaBins({ipar}\,LepGood1_pdgId\,LepGood1_eta\,LepGood1_pt\,{emin:.1f}\,{emax:.1f})'.format(ipar=ipar,emin=etamin,emax=etamax)
            mcafile_syst.write(incl_mca+postfix+'   : + ; IncludeMca='+incl_file+', AddWeight="'+weightFcn+'", PostFix="'+postfix+'" \n')
            etaeffsysts.append(postfix)
    print "written ",syst," systematics relative to ",incl_mca

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
    logfile=outdir+"/jobs/"+dcname+".log"
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
request_memory = 4000
+MaxRuntime = {rt}
queue 1\n
'''.format(scriptName=srcFile, pid=srcFile.replace('.sh',''), rt=getCondorTime(options.queue), here=os.environ['PWD'] ) )
    if os.environ['USER'] in ['mdunser', 'psilva']:
        condor_file.write('+AccountingGroup = "group_u_CMST3.all"\n')
    condor_file.close()

from optparse import OptionParser
parser = OptionParser(usage="%prog [options] mc.txt cuts.txt var bins systs.txt outdir ")
parser.add_option("-q", "--queue",    dest="queue",     type="string", default=None, help="Run jobs on lxbatch instead of locally");
parser.add_option("-l", "--lumi",    dest="integratedLuminosity",     type="float", default=35.9, help="Integrated luminosity");
parser.add_option("--dry-run", dest="dryRun",    action="store_true", default=False, help="Do not run the job, only print the command");
parser.add_option("--long-bkg", dest="longBkg",    action="store_true", default=False, help="Treat the longitudinal polarization as one background template.");
parser.add_option("-s", "--signal-cards",  dest="signalCards",  action="store_true", default=False, help="Make the signal part of the datacards");
parser.add_option("-b", "--bkgdata-cards", dest="bkgdataCards", action="store_true", default=False, help="Make the background and data part of the datacards");
parser.add_option("-W", "--weight", dest="weightExpr", default="-W 1", help="Event weight expression (default 1)");
parser.add_option("-P", "--path", dest="path", type="string",default=None, help="Path to directory with input trees and pickle files");
parser.add_option("-C", "--channel", dest="channel", type="string", default='el', help="Channel. either 'el' or 'mu'");
parser.add_option("--not-unroll2D", dest="notUnroll2D", action="store_true", default=False, help="Do not unroll the TH2Ds in TH1Ds needed for combine (to make 2D plots)");
parser.add_option("--pdf-syst", dest="addPdfSyst", action="store_true", default=False, help="Add PDF systematics to the signal (need incl_sig directive in the MCA file)");
parser.add_option("--qcd-syst", dest="addQCDSyst", action="store_true", default=False, help="Add QCD scale systematics to the signal (need incl_sig directive in the MCA file)");
parser.add_option("--useLSF", action='store_true', default=False, help="force use LSF. default is using condor");
parser.add_option('-g', "--group-jobs", dest="groupJobs", type=int, default=20, help="group signal jobs so that one job runs multiple makeShapeCards commands");
parser.add_option('-w', "--wvar", type="string", default='prefsrw', help="switch between genw and prefsrw. those are the only options (default %default)");
(options, args) = parser.parse_args()

if not options.wvar in ['genw', 'prefsrw']:
    print 'the W variable has to be either "genw" or "prefsrw". exiting...'
    quit()

if len(sys.argv) < 6:
    parser.print_usage()
    quit()

signal_helicities = ['left', 'right']
if not options.longBkg:
    signal_helicities += ['long']

print 'these are signal helicities', signal_helicities

FASTTEST=''
#FASTTEST='--max-entries 1000 '
T=options.path
print "used trees from: ",T
J=2
MCA = args[0]
CUTFILE = args[1]
fitvar = args[2]
binning = args[3]
SYSTFILE = args[4]

luminosity = options.integratedLuminosity

if not os.path.exists("cards/"):
    os.makedirs("cards/")
outdir="cards/"+args[5]

if not os.path.exists(outdir): os.mkdir(outdir)
if options.queue and not os.path.exists(outdir+"/jobs"): 
    os.mkdir(outdir+"/jobs")
    os.mkdir(outdir+"/mca")

# copy some cfg for bookkeeping
os.system("cp %s %s" % (CUTFILE, outdir))
os.system("cp %s %s" % (MCA, outdir))

## save template binning (eta on X, pt on y axis)                                                                                                                       
ptEta_binfile = open(outdir+'/binningPtEta.txt','w')
ptEta_binfile.write("#Template binning: eta-pt on x-y axis\n")
ptEta_binfile.write("reco: "+binning+"\n")
ptEta_binfile.write('\n')
ptEta_binfile.close()

if options.addPdfSyst:
    # write the additional systematic samples in the MCA file
    writePdfSystsToMCA(MCA,outdir+"/mca") # on W + jets 
    writePdfSystsToMCA(MCA,outdir+"/mca",incl_mca='incl_dy') # on DY + jets
    # write the complete systematics file (this was needed when trying to run all systs in one job)
    # SYSTFILEALL = writePdfSystsToSystFile(SYSTFILE)
if options.addQCDSyst:
    scales = ['muR','muF',"muRmuF", "alphaS"]
    writeQCDScaleSystsToMCA(MCA,outdir+"/mca",scales=scales+["wptSlope", "mW"])
    writeQCDScaleSystsToMCA(MCA,outdir+"/mca",scales=scales,incl_mca='incl_dy')

# not needed if we fit eta/pt. Will be needed if we fit another variable correlated with eta/pt
# writeEfficiencyStatErrorSystsToMCA(MCA,outdir+"/mca",options.channel)

ARGS=" ".join([MCA,CUTFILE,"'"+fitvar+"' "+"'"+binning+"'",SYSTFILE])
BASECONFIG=os.path.dirname(MCA)
## use rel paths if options.queue:
## use rel paths     ARGS = ARGS.replace(BASECONFIG,os.getcwd()+"/"+BASECONFIG)
OPTIONS=" -P "+T+" --s2v -j "+str(J)+" -l "+str(luminosity)+" -f --obj tree "+FASTTEST
if not os.path.exists(outdir): os.makedirs(outdir)
OPTIONS+=" -F Friends '{P}/friends/tree_Friend_{cname}.root' "
if not options.notUnroll2D:
    OPTIONS+=" --2d-binning-function unroll2Dto1D "

if options.queue:
    import os, sys
    basecmd = "bsub -q {queue} {dir}/lxbatch_runner.sh {dir} {cmssw} python {self}".format(
                queue = options.queue, dir = os.getcwd(), cmssw = os.environ['CMSSW_BASE'], self=sys.argv[0]
            )

POSCUT=" -A alwaystrue positive 'LepGood1_charge>0' "
NEGCUT=" -A alwaystrue negative 'LepGood1_charge<0' "
fullJobList = set()
if options.signalCards:
    WYBinsEdges = makeFixedYWBinning()
    ybinfile = open(outdir+'/binningYW.txt','w')
    ybinfile.write(json.dumps(WYBinsEdges))
    #ybinfile.writelines(' '.join(str(i) for i in WYBinsEdges))
    ybinfile.close()
    print "MAKING SIGNAL PART: WYBinsEdges = ",WYBinsEdges
    wsyst = ['']+[x for x in pdfsysts+qcdsysts+etaeffsysts if 'sig' in x]
    for ivar,var in enumerate(wsyst):
        for helicity in signal_helicities:
            ## marc antihel = 'right' if helicity == 'left' else 'left'
            antihel = ['right', 'long'] if helicity == 'left' else ['left','long'] if helicity == 'right' else ['right','left']
            for charge in ['plus', 'minus']:
                antich = 'plus' if charge == 'minus' else 'minus'
                YWbinning = WYBinsEdges['{ch}_{hel}'.format(ch=charge,hel=helicity)]
                if ivar==0: 
                    IARGS = ARGS
                else: 
                    IARGS = ARGS.replace(MCA,"{outdir}/mca/mca{syst}.txt".format(outdir=outdir,syst=var))
                    IARGS = IARGS.replace(SYSTFILE,"{outdir}/mca/systEnv-dummy.txt".format(outdir=outdir))
                    print "Running the systematic: ",var
                job_group =  [] ## group
                for iy in xrange(len(YWbinning)-1):
                    print "Making card for {yl}<=abs({wv}_y)<{yh} and signal process with charge {ch} ".format(yl=YWbinning[iy],wv=options.wvar,yh=YWbinning[iy+1],ch=charge)
                    ycut=" -A alwaystrue YW{iy} 'abs({wv}_y)>={yl} && abs({wv}_y)<{yh}' ".format(iy=iy,wv=options.wvar,yl=YWbinning[iy],yh=YWbinning[iy+1])
                    ycut += POSCUT if charge=='plus' else NEGCUT
                    ## marc excl_long_signal  = '' if not options.longBkg else ',W{ch}_long.*'.format(ch=charge)
                    ## marc xpsel=' --xp "W{antich}.*,W{ch}_{antihel}.*,Flips,Z,Top,DiBosons,TauDecaysW{longbkg},data.*" --asimov '.format(antich=antich,ch=charge,antihel=antihel,longbkg = excl_long_signal)
                    excl_antihel = ','.join('W'+charge+'_'+ah+'.*' for ah in antihel)
                    xpsel=' --xp "W{antich}.*,{ahel},Flips,Z,Top,DiBosons,TauDecaysW,data.*" --asimov '.format(antich=antich,ch=charge,ahel=excl_antihel)
                    if not os.path.exists(outdir): os.mkdir(outdir)
                    if options.queue and not os.path.exists(outdir+"/jobs"): os.mkdir(outdir+"/jobs")
                    syst = '' if ivar==0 else var
                    dcname = "W{charge}_{hel}_{channel}_Ybin_{iy}{syst}".format(charge=charge, hel=helicity, channel=options.channel,iy=iy,syst=syst)
                    BIN_OPTS=OPTIONS + " -W '" + options.weightExpr + "'" + " -o "+dcname+" --od "+outdir + xpsel + ycut
                    if options.queue:
                        mkShCardsCmd = "python makeShapeCards.py {args} \n".format(dir = os.getcwd(), args = IARGS+" "+BIN_OPTS)
                        ## here accumulate signal jobs if running with long. make long+right+left one job
                        ## marcmarc if not options.longBkg and WYBinsEdges['{ch}_{hel}'.format(ch=charge,hel=antihel[0])]
                        if not options.longBkg:
                            job_group.append(mkShCardsCmd)
                            if len(job_group) == options.groupJobs or iy == len(YWbinning)-2:
                                if options.useLSF: 
                                    submitBatch(dcname,outdir,'\n'.join(job_group),options)
                                else:
                                    pass
                                    ## passing this submitCondor(dcname,outdir,'\n'.join(job_group),options)
                                job_group = []
                        else:
                            if options.useLSF:
                                submitBatch(dcname,outdir,mkShCardsCmd,options)
                            else:
                                pass
                                ## passing this now too submitCondor(dcname,outdir,mkShCardsCmd,options)
                        fullJobList.add(mkShCardsCmd)
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
        xpsel=' --xp "W.*" ' if not options.longBkg else ' --xp "W{ch}_left,W{ch}_right,W{ach}.*" '.format(ch=charge, ach='minus' if charge=='plus' else 'plus')
        if len(pdfsysts+qcdsysts)>1: # 1 is the nominal 
            xpsel+=' --xp "Z" '
        chargecut = POSCUT if charge=='plus' else NEGCUT
        dcname = "bkg_and_data_{channel}_{charge}".format(channel=options.channel, charge=charge)
        BIN_OPTS=OPTIONS + " -W '" + options.weightExpr + "'" + " -o "+dcname+" --od "+outdir + xpsel + chargecut
        if options.queue:
            mkShCardsCmd = "python makeShapeCards.py {args} \n".format(dir = os.getcwd(), args = ARGS+" "+BIN_OPTS)
            if options.useLSF:
                submitBatch(dcname,outdir,mkShCardsCmd,options)
            else:
                ## passing this now submitCondor(dcname,outdir,mkShCardsCmd,options)
                pass
            fullJobList.add(mkShCardsCmd)
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
                mkShCardsCmd = "python makeShapeCards.py {args} \n".format(dir = os.getcwd(), args = IARGS+" "+BIN_OPTS)
                if options.useLSF:
                    submitBatch(dcname,outdir,mkShCardsCmd,options)
                else:
                    ## passing this now submitCondor(dcname,outdir,mkShCardsCmd,options)
                    pass
                fullJobList.add(mkShCardsCmd)
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

def getShFile(jobdir, name):
    tmp_srcfile_name = jobdir+'/job_{i}.sh'.format(i=name)
    tmp_srcfile = open(tmp_srcfile_name, 'w')
    tmp_srcfile.write("#! /bin/sh\n")
    tmp_srcfile.write("ulimit -c 0 -S\n")
    tmp_srcfile.write("ulimit -c 0 -H\n")
    tmp_srcfile.write("cd {cmssw};\neval $(scramv1 runtime -sh);\ncd {d};\n".format( d= os.getcwd(), cmssw = os.environ['CMSSW_BASE']))
    return tmp_srcfile_name, tmp_srcfile

if len(fullJobList):
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
    print '   ... grouping them into bunches of', options.groupJobs
    
    if not nj%options.groupJobs:
        njobs = int(nj/options.groupJobs)
    else: 
        njobs = int(nj/options.groupJobs) + 1
    
    jobdir = outdir+'/jobs/'
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
        tmp_n = options.groupJobs
        while len(reslist) and tmp_n:
            tmp_pycmd = reslist[0]
            tmp_srcfile.write(tmp_pycmd)
            reslist.remove(tmp_pycmd)
            tmp_n -= 1
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
Log        = {jd}/$(ProcId).log
Output     = {jd}/$(ProcId).out
Error      = {jd}/$(ProcId).error
getenv      = True
environment = "LS_SUBCWD={here}"
request_memory = 4000
+MaxRuntime = {rt}\n
'''.format(de=os.path.abspath(dummy_exec.name), jd=os.path.abspath(jobdir), rt=getCondorTime(options.queue), here=os.environ['PWD'] ) )
    if os.environ['USER'] in ['mdunser', 'psilva']:
        condor_file.write('+AccountingGroup = "group_u_CMST3.all"\n\n\n')
    for sf in sourcefiles:
        condor_file.write('arguments = {sf} \nqueue 1 \n\n'.format(sf=os.path.abspath(sf)))
    condor_file.close()

    print 'i have {n} jobs to submit!'.format(n=len(subcommands))
    if options.dryRun:
        print 'running dry, printing the commands...'
        print 'condor_submit ',condor_file_name
        #for cmd in subcommands:
        #    print cmd
    else:
        print 'submitting for real...'
        os.system('condor_submit '+condor_file_name)
        ##sigDyBkg = '_signal' if options.signalCards else '_background'
        ##pipefilename = args[5]+'_submission{t}.sh'.format(t=sigDyBkg)
        ##pipefile = open(pipefilename, 'w')
        ##print 'piping all the commands in file', pipefilename
        ##for cmd in subcommands:
        ##    pipefile.write(cmd+'\n')
        ##pipefile.close()
        ##os.system('bash '+pipefilename)
print 'done'
