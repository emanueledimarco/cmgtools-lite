import sys, os
import ROOT, datetime, array
import re

from make_diff_xsec_cards import getArrayParsingString

# usage 
# create an MCA with many signal processes for different cuts
#
# python w-helicity-13TeV/printMCAforXsec.py -o w-helicity-13TeV/wmass_e/mca-includes/ -n mca-80X-wenu-sigInclCharge_gen_eta_pt_4xsec.txt -c el -l preFSR -w "WJetsToLNu_NLO*"
#
# use "WJetsToLNu_*" or a subset for muons



from optparse import OptionParser
parser = OptionParser(usage="%prog [options]")
parser.add_option('-o','--outdir', dest='outdir',   default='w-helicity-13TeV/wmass_e/mca-includes/', type='string', help='Output folder')
parser.add_option('-n','--name', dest='mcaName',   default='mca-80X-wenu-sigInclCharge_gen_eta_pt_4xsec.txt', type='string', help='Name of output mca file')
parser.add_option('-c','--channel', dest='channel',   default='el', type='string', help='Channel (el or mu)')
parser.add_option('-l','--leptonDef', dest='leptonDef',   default='preFSR', type='string', help='stable-particle lepton definition (preFSR or dressed)')
parser.add_option('-w','--wSample', dest='wSample',   default='WJetsToLNu_NLO*', type='string', help='Regular expression for the W samples to use, in mca style')
# parser.add_option('-x','--xvar', dest='xvar',   default='GenLepDressed_eta[0]', type='string', help='Name of variable in x axis of the template')
# parser.add_option('-y','--yvar', dest='yvar',   default='GenLepDressed_pt[0]', type='string', help='Name of variable in y axis of the template')
# parser.add_option(     '--xbin', dest='xbin',   default='500,-5.0,5.0', type='string', help='Inputs to define template x axis binning: format is nbins,min,max')
# parser.add_option(     '--ybin', dest='ybin',   default='180,10,100', type='string', help='Inputs to define template y axis binning: format is nbins,min,max')
(options, args) = parser.parse_args() 

outdir = options.outdir
if not outdir.endswith('/'):
    outdir += '/'
    
if not os.path.exists(outdir): 
    os.mkdirs(outdir)

print "Writing file %s%s " % (outdir,options.mcaName)
mcafile = open(outdir+options.mcaName,'w')

genDecayId = 12 if options.channel == "el" else 14
genwVar = "prefsrw" if options.leptonDef == "preFSR" else "genw"

charges = [ "plus", "minus"]
flav=options.channel

scaleVars = ['muR','muF',"muRmuF", "alphaS"] 
# scales are also done in bins of wpt
# let's consider 10 bins (using every other value of the following array, defined also in make_diff_xsec_cards.py)
wptbins = [0.0, 1.971, 2.949, 3.838, 4.733, 5.674, 6.684, 7.781, 8.979, 10.303, 11.777, 13.435, 15.332, 17.525, 20.115, 23.245, 27.173, 32.414, 40.151, 53.858, 13000.0]
for ipt in range(1,11): ## start from 1 to 10
    scaleVars.append("muR%s" % str(ipt))
    scaleVars.append("muF%s" % str(ipt))
    scaleVars.append("muRmuF%s" % str(ipt))

syst_suffix = []
for x in scaleVars:
    syst_suffix.append("%sUp" % x)
    syst_suffix.append("%sDn" % x)

#pdf
for i in range(60):
    syst_suffix.append("pdf%d" % int(i+1))
# for mW, the central value in MC is 80420, we choose up and down variation with dm = +/- 50 MeV
# mW
syst_suffix.append("mW_80370")
syst_suffix.append("mW_80470")

#labels = ["lep scale Up", "lep scale Dn"]  
#syst_label = dict(zip(syst_suffix, labels))
all_syst_suffix = [""]  # "" is for nominal
all_syst_suffix.extend(syst_suffix)


for syst in all_syst_suffix:

    for charge in charges:

        if syst == "":
            print "Writing charge ",charge
            mcafile.write("## CHARGE %s\n" % charge)
            label = " Label=\"W%s\"" % ("+" if charge == "plus" else "-")
        else:
            print "Writing syst '%s' for charge %s" % (syst,charge)
            mcafile.write("## CHARGE %s   SYST %s \n" % (charge, syst))
            label = " Label=\"W%s %s\"" % ("+" if charge == "plus" else "-", syst)

        chargeSignCut = ">" if charge == "plus" else "<"

        fullcut = "{gwv}_decayId == {decayId} && {gwv}_charge {chs} 0".format(gwv=genwVar,decayId=str(genDecayId),chs=chargeSignCut)

        line = "W{ch}_{fl}_{syst} : {Wsamples} : 3.*20508.9 : {cut}".format(ch=charge,fl=flav,cut=fullcut,syst=syst if syst != "" else "central", Wsamples=options.wSample)
        line += " ; FillColor=ROOT.kRed+2 , {lab} ".format(lab=label)
        if syst != "": 
            if "pdf" in syst:
                wgt = "hessWgt%d" % int(str(syst[3:]))   # syst is pdf1, pdf2, ...: get the integer number to build the weight
            elif "mW" in syst:
                massValue = syst[3:]
                wgt = "mass_{m}".format(m=massValue)
            else:
                if any(x in syst for x in ["muR","muF","muRmuF"]) and any (x.isdigit() for x in syst):
                    ptbin = ""
                    for i in syst:
                        if i.isdigit(): ptbin += i
                    ptbin = int(ptbin)
                    ptlow = str(wptbins[2*(ptbin-1)])
                    pthigh = str(wptbins[2*ptbin])
                    scale = syst.replace(str(ptbin),"")
                    wgt = 'TMath::Power(qcd_{sc}\,({wv}_pt >= {ptlo} && {wv}_pt < {pthi}))'.format(sc=scale,wv=genwVar,ptlo=ptlow,pthi=pthigh)
                else:
                    wgt = "qcd_%s" % syst
            line += ", AddWeight=\"{wgt}\"".format(wgt=wgt)

        mcafile.write(line+"\n")

    mcafile.write("\n")

mcafile.close()


#Wplus   : WJetsToLNu_NLO* : 3.*20508.9   : genw_decayId == 12 && genw_charge>0 && LepGood1_mcMatchId*LepGood1_charge!=-24 ; FillColor=ROOT.kRed+2 , Label="W+"
#Wminus  : WJetsToLNu_NLO* : 3.*20508.9   : genw_decayId == 12 && genw_charge<0 && LepGood1_mcMatchId*LepGood1_charge!=-24 ; FillColor=ROOT.kRed+2 , Label="W-"
