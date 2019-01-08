import sys, os
import ROOT, datetime, array
import re

from make_diff_xsec_cards import getArrayParsingString

# usage 
# create an MCA with many signal processes for different cuts
#
# python printBinnnedSignalMCA.py -o w-helicity-13TeV/wmass_e/mca-includes/ -n mca-80X-wenu-sigInclCharge_binned_eta_pt.txt -b "[x1,x2,x3,...]*[y1,y2,y3,...]" -x GenLepDressed_eta[0] -y GenLepDressed_pt[0] -c el
#
# for option -b, I have to implement using constant width binning, with format like the histogram creator for mcPlots.py

from optparse import OptionParser
parser = OptionParser(usage="%prog [options]")
parser.add_option('-o','--outdir', dest='outdir',   default='w-helicity-13TeV/wmass_e/mca-includes/', type='string', help='Output folder')
parser.add_option('-n','--name', dest='mcaName',   default='mca-80X-wenu-sigInclCharge_binned_eta_pt.txt', type='string', help='Name of output mca file')
parser.add_option('-c','--channel', dest='channel',   default='el', type='string', help='Channel (el or mu)')
parser.add_option('-x','--xvar', dest='xvar',   default='LepGood1_eta', type='string', help='Name of variable in x axis of the template')
parser.add_option('-y','--yvar', dest='yvar',   default='ptElFull(LepGood1_calPt,LepGood1_eta)', type='string', help='Name of variable in y axis of the template')
parser.add_option('-b','--binning', dest='binning', default='[-2.5,-2.1,-1.566,-1.4442,-1.0,-0.5,0,0.5,1.0,1.4442,1.566,2.1,2.5]*[30,33,36,39,42,45]', type='string', help='Gen binning (use same format as for histogram definition for mcPlots.py (to be implemented correctly)')
parser.add_option('-l','--leptonDef', dest='leptonDef',   default='preFSR', type='string', help='stable-particle lepton definition (preFSR or dressed)')
(options, args) = parser.parse_args()

outdir = options.outdir
if not outdir.endswith('/'):
    outdir += '/'
    
if not os.path.exists(outdir): 
    os.mkdirs(outdir)

print "Writing file %s%s " % (outdir,options.mcaName)
mcafile = open(outdir+options.mcaName,'w')
mcafile.write("## Binning\n")
mcafile.write("## %s\n\n" % options.binning)

binning = options.binning
genDecayId = 12 if options.channel == "el" else 14
genwVar = "prefsrw" if options.leptonDef == "preFSR" else "genw"

if options.binning:
    etabinning=binning.split('*')[0]    # this is like [a,b,c,...], and is of type string. We nedd to get an array                                                          
    ptbinning=binning.split('*')[1]
    etabinning = getArrayParsingString(etabinning)
    ptbinning = getArrayParsingString(ptbinning)
    ptVarCut = options.yvar
    etaVarCut = options.xvar
    nptbins = len(ptbinning)-1
    netabins = len(etabinning)-1
else:
    nptbins = 1
    netabins = 1

charges = [ "plus", "minus"]
flav=options.channel
if flav not in ["el","mu"]:
    print "Error in printBinnnedSignalMCA.py: unknown lepton flavour, use -c el|mu. Exit"
    exit(0)

#syst_suffix = ["_elescale_Up", "_elescale_Dn", "_lepeff_Up", "_lepeff_Dn"] 
#labels = ["lep scale Up", "lep scale Dn", "lep eff Up", "lep eff Dn"]  
#syst_label = dict(zip(syst_suffix, labels))
all_syst_suffix = [""]  # "" is for nominal
#################################
# keep only nominal sample in this MCA: lepton systematics are defined in the main MCA, that includes this one
#################################
# if flav == "el": 
#     all_syst_suffix.extend(syst_suffix)
# else:
#     print "----- Warning: muon scale systematics is not implemented yet -----"

for syst in all_syst_suffix:

    for charge in charges:

        if syst == "":
            print "Writing charge ",charge
            mcafile.write("## CHARGE %s\n\n" % charge)
            label = " Label=\"W%s\"" % ("+" if charge == "plus" else "-")
            weight = ""
        # else:
        #     print "Writing syst '%s' for charge %s" % (syst,charge)
        #     mcafile.write("## CHARGE %s   SYST %s \n\n" % (charge, syst))
        #     label = " Label=\"W%s %s\"" % ("+" if charge == "plus" else "-", syst_label[syst])
        #     varsys = "Up" if "_Up" in syst else "Dn" 
        #     if "lepeff" in syst:
        #         weight = " AddWeight=\"lepSFRel"+varsys+"(LepGood1_pdgId\,LepGood1_pt\,LepGood1_eta\,LepGood1_SF1\,LepGood1_SF2\,LepGood1_SF3\,LepGood1_SF4)\" "
        #     if "elescale" in syst: 
        #         weight = " FakeRate=\"w-helicity-13TeV/wmass_e/fr-includes/doSyst_lepScale"+varsys+"_xsec.txt\" "  
        #     weight += " , "  # note comma here, as other MCA flags follow

        chargeSignCut = ">" if charge == "plus" else "<"
        sigRegExpr = "WJetsToLNu_NLO*" if flav == "el" else "WJetsToLNu_*"        

        genCut = " && {gwv}_decayId == {decayId} && {gwv}_charge {chs} 0".format(gwv=genwVar,decayId=str(genDecayId),chs=chargeSignCut)

        for ipt in xrange(nptbins):
            for ieta in xrange(netabins):

                etacut = "%s>=%s && %s<%s" % (etaVarCut,etabinning[ieta],etaVarCut,etabinning[ieta+1])
                ptcut = "%s>=%s && %s<%s" % (ptVarCut,ptbinning[ipt],ptVarCut,ptbinning[ipt+1])
                fullcut = etacut + " && " + ptcut + genCut
                if flav == "el": 
                    fullcut = fullcut + " && LepGood1_mcMatchId*LepGood1_charge!=-24 "

                signalPrefix = "W{ch}_{fl}_ieta_{ieta}_ipt_{ipt}".format(ch=charge,fl=flav,ieta=ieta,ipt=ipt)
                line = "{sigPfx}{syst} : {sigRegExpr} : 3.*20508.9 : {cut} ; FillColor=ROOT.kRed+2 , {wgt} {lab} ".format(sigPfx=signalPrefix,
                                                                                                                          cut=fullcut,lab=label,
                                                                                                                          syst=syst,
                                                                                                                          sigRegExpr=sigRegExpr,
                                                                                                                          wgt=weight)
                if syst != "": line += ", SkipMe=True"
                mcafile.write(line+"\n")

        ##################################
        # now add bins outside range (could also split them somehow, for now there is just one template
        #########
        etacut = "%s>=%s" % (etaVarCut,etabinning[netabins])
        ptcut = "%s<%s || %s>=%s" % (ptVarCut,ptbinning[0],ptVarCut,ptbinning[nptbins])
        fullcut = "(" + etacut + " || " + ptcut + ")" + genCut
        if flav == "el": 
            fullcut = fullcut + " && LepGood1_mcMatchId*LepGood1_charge!=-24 "
                    
        line = "W{ch}_{fl}_outliers{syst} : {sigRegExpr} : 3.*20508.9 : {cut} ; FillColor=ROOT.kRed+2 , {wgt} {lab} ".format(ch=charge,fl=flav,
                                                                                                                             cut=fullcut,lab=label,
                                                                                                                             syst=syst,
                                                                                                                             sigRegExpr=sigRegExpr,
                                                                                                                             wgt=weight)
        if syst != "": line += ", SkipMe=True"
        mcafile.write(line+"\n")

        ############

        mcafile.write("\n\n")



mcafile.close()

