#!/bin/env python

# python w-helicity-13TeV/mergeCardComponentsDiffXsec.py -i cards/diffXsec_2018_05_24_diffXsec_GenPtEtaSigBin/ -b Wel -C plus -m --eta-range-bkg 1.44 1.57 --sig-out-bkg

####################
###################
# TO BE UPDATED
##################
##################

import ROOT
import sys,os,re,json,copy

from mergeCardComponentsAbsY import mirrorShape
from make_diff_xsec_cards import getArrayParsingString
from make_diff_xsec_cards import getGlobalBin
from make_diff_xsec_cards import getDiffXsecBinning
from make_diff_xsec_cards import get_ieta_ipt_from_process_name

#from mergeCardComponentsAbsY import getXsecs    # for now it is reimplemented here
def getXsecs_etaPt(processes, systs, etaPtBins, infile):  # in my case here, the histograms already have the cross section in pb, no need to divide by lumi

    #print "Inside getXsecs_etaPt"
    # etaPtBins is a list of 4 things: Netabins, etabins, Nptbins,ptbins

    histo_file = ROOT.TFile(infile, 'READ')
    hists = []

    for process in processes:

        etabins = etaPtBins[1]
        ptbins = etaPtBins[3]

        charge = "plus" if "plus" in process else "minus"
        # check if gen eta binning starts from negative value (probably we will stick to |eta|, but just in case)
        etavar = "absetal1" if (float(etabins[0]) >= 0.0) else "etal1" 
        cen_name = 'gen_ptl1_'+etavar+'_W'+charge+'_mu_central' 
        cen_hist = histo_file.Get(cen_name)  # this is a TH2
        useEleXsec = False
        if not cen_hist:
            cen_name = cen_name.replace("_mu_","_el_")
            cen_hist = histo_file.Get(cen_name)
            useEleXsec = True
        #print cen_name

        if not cen_hist:
            print "Error in getXsecs_etaPt(): histogram %s not found in file %s. Exit" % (cen_name, infile)
            quit()

        # before searching the bin, sum epsilon to the y value being inspected
        # Root assigns the lower bin edge to the bin, while the upper bin edge is assigned to the adjacent bin. However, depending on the number y being used,
        # there can be a precision issue which might induce the selection of the wrong bin (since yfirst and yvalue are actually bin boundaries)
        # It seems odd, but I noticed that with the fake rate graphs (I was getting events migrating between adjacent eta bins)
        epsilon = 0.00001

        # process has the form: Wplus_el_ieta_3_ipt_0_Wplus_el_group_0, where the number after group is not relevant (does not coincide with absolute bin number)
        # as it can be the same for many processes
        # one should use ieta and ipt, which identifies the template bin (first index is 0, not 1)
        # generally, ieta,ipt in name should correspond to 2D histogram X and Y bins (after adding 1)
        # However, one could use different definition for the gen level binning (used to cut and define a signal process) and the reco level one (defining the TH2)

        if "outliers" in process:
            # cross section for outliers = Integral(all) - integral(acceptance)
            totxsec = cen_hist.Integral(0, cen_hist.GetNbinsX()+1, 0, cen_hist.GetNbinsY()+1)
            ieta_low_acc = cen_hist.GetXaxis().FindFixBin(etabins[0]+epsilon)
            ieta_high_acc = cen_hist.GetXaxis().FindFixBin(etabins[-1]+epsilon) -1
            ipt_low_acc = cen_hist.GetYaxis().FindFixBin(ptbins[0]+epsilon)
            ipt_high_acc = cen_hist.GetYaxis().FindFixBin(ptbins[-1]+epsilon) -1
            xsecAccept = cen_hist.Integral(ieta_low_acc, ieta_high_acc, ipt_low_acc, ipt_high_acc)
            ncen = totxsec - xsecAccept 
        else:
            ieta,ipt = get_ieta_ipt_from_process_name(process)
            etafirst = etabins[ieta]
            etalast  = etabins[ieta+1]
            ptfirst = ptbins[ipt]
            ptlast  = ptbins[ipt+1]            
            # caution, we are using TH2, the logic below is slightly different than for TH1        
            istart_eta = cen_hist.GetXaxis().FindFixBin(etafirst + epsilon)
            iend_eta   = cen_hist.GetXaxis().FindFixBin(etalast + epsilon)
            istart_pt  = cen_hist.GetYaxis().FindFixBin(ptfirst + epsilon)
            iend_pt    = cen_hist.GetYaxis().FindFixBin(ptlast + epsilon)
            ncen = cen_hist.Integral(istart_eta, iend_eta-1, istart_pt,iend_pt-1)

        tmp_hist = ROOT.TH1F('x_'+process,'x_'+process, 1, 0., 1.)
        ## normalize back to cross section
        tmp_hist.SetBinContent(1, ncen)

        hists.append(copy.deepcopy(tmp_hist))

        for sys in systs:

            # scales muR, muF, muRmuF in bins of pt are named like muR_wpt1Up, where the number after wpt goes from 1 to 10
            upn = sys+'Up' if not 'pdf' in sys else sys
            dnn = sys+'Dn' if not 'pdf' in sys else sys

            if useEleXsec:
                sys_upname = 'gen_ptl1_'+etavar+'_W'+charge+'_el_'+upn
                sys_dnname = 'gen_ptl1_'+etavar+'_W'+charge+'_el_'+dnn
            else:
                sys_upname = 'gen_ptl1_'+etavar+'_W'+charge+'_mu_'+upn
                sys_dnname = 'gen_ptl1_'+etavar+'_W'+charge+'_mu_'+dnn

            sys_up_hist = histo_file.Get(sys_upname)
            sys_dn_hist = histo_file.Get(sys_dnname)

            if not sys_up_hist:
                print "Error in getXsecs_etaPt(): histogram %s not found in file %s" % (sys_upname, infile)
                quit()
            if not sys_dn_hist:
                print "Error in getXsecs_etaPt(): histogram %s not found in file %s" % (sys_dnname, infile)
                quit()

            if "outliers" in process:
                totxsec = sys_up_hist.Integral(0, sys_up_hist.GetNbinsX()+1, 0, sys_up_hist.GetNbinsY()+1)
                xsecAccept = sys_up_hist.Integral(ieta_low_acc, ieta_high_acc, ipt_low_acc, ipt_high_acc)
                nup = totxsec - xsecAccept
                totxsec = sys_dn_hist.Integral(0, sys_dn_hist.GetNbinsX()+1, 0, sys_dn_hist.GetNbinsY()+1)
                xsecAccept = sys_dn_hist.Integral(ieta_low_acc, ieta_high_acc, ipt_low_acc, ipt_high_acc)
                ndn = totxsec - xsecAccept
            else:
                nup = sys_up_hist.Integral(istart_eta, iend_eta-1, istart_pt,iend_pt-1)
                ndn = sys_dn_hist.Integral(istart_eta, iend_eta-1, istart_pt,iend_pt-1)

            if 'pdf' in sys:
                ndn = ncen*ncen/nup # ndn = 2.*ncen-nup ## or ncen/nup?  # FIXME: this should be decided and motivated
                # I think we should be consistent with the histogram definition, which uses the ratio, but if central and up differs by an epsilon it doesn't matter

            tmp_hist_up = ROOT.TH1F('x_'+process+'_'+sys+'Up','x_'+process+'_'+sys+'Up', 1, 0., 1.)
            tmp_hist_up.SetBinContent(1, nup)
            tmp_hist_dn = ROOT.TH1F('x_'+process+'_'+sys+'Down','x_'+process+'_'+sys+'Dn', 1, 0., 1.)
            tmp_hist_dn.SetBinContent(1, ndn)
            hists.append(copy.deepcopy(tmp_hist_up))
            hists.append(copy.deepcopy(tmp_hist_dn))

    hist_data = ROOT.TH1F('x_data_obs', 'x_data_obs', 1, 0., 1.)
    hist_data.SetBinContent(1, 1.)
    hists.append(copy.deepcopy(hist_data))

    return hists


def combCharges(options):
    suffix = 'card' if options.freezePOIs else 'card_withXsecMask'
    datacards=[]; channels=[]
    for charge in ['plus','minus']:
        datacards.append(os.path.abspath(options.inputdir)+"/"+options.bin+'_{ch}_card.txt'.format(ch=charge))
        channels.append('{bin}_{ch}'.format(bin=options.bin,ch=charge))
        if not options.freezePOIs:
            datacards.append(os.path.abspath(options.inputdir)+"/"+options.bin+'_{ch}_xsec_card.txt'.format(ch=charge))
            channels.append('{bin}_{ch}_xsec'.format(bin=options.bin,ch=charge))

    if options.combineCharges and sum([os.path.exists(card) for card in datacards])==len(datacards):
        print "Cards for W+ and W- done. Combining them now..."
        combinedCard = os.path.abspath(options.inputdir)+"/"+options.bin+'_'+suffix+'.txt'
        ccCmd = 'combineCards.py '+' '.join(['{channel}={dcfile}'.format(channel=channels[i],dcfile=datacards[i]) for i,c in enumerate(channels)])+' > '+combinedCard
        ## here running the combine cards command first 
        print ccCmd
        os.system(ccCmd)
        ## here making the TF meta file
        if options.freezePOIs:
            # doesn't make sense to have the xsec masked channel if you freeze the rates (POIs) -- and doesn't work either
            txt2hdf5Cmd = 'text2hdf5.py --sparse {cf}'.format(cf=combinedCard)
        else:
            maskchan = [' --maskedChan {bin}_{charge}_xsec'.format(bin=options.bin,charge=ch) for ch in ['plus','minus']]
            txt2hdf5Cmd = 'text2hdf5.py --sparse {maskch} --X-allow-no-background {cf}'.format(maskch=' '.join(maskchan),cf=combinedCard)
        print "The following command makes the .hdf5 file used by combine"
        print txt2hdf5Cmd
        if not options.skip_text2hdf5:
            print '--- will run text2hdf5 for the combined charges ---------------------'
            os.system(txt2hdf5Cmd)
            ## print out the command to run in combine
            combineCmd = 'combinetf.py -t -1 --binByBinStat --correlateXsecStat {metafile}'.format(metafile=combinedCard.replace('.txt','_sparse.hdf5'))
            if options.freezePOIs:
                combineCmd += " --POIMode none"
            print "Use the following command to run combine (add --seed <seed> to specify the seed, if needed)"
            print combineCmd

    else:
        print "It looks like at least one of the datacards for a single charge is missing. I cannot make the combination."

if __name__ == "__main__":
    

    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options]')
    parser.add_option('-m','--merge-root', dest='mergeRoot', default=False, action='store_true', help='Merge the root files with the inputs also')
    parser.add_option('-i','--input', dest='inputdir', default='', type='string', help='input directory with all the cards inside')
    parser.add_option('-b','--bin', dest='bin', default='Wel', type='string', help='name of the bin (Wmu or Wel)')
    parser.add_option('-C','--charge', dest='charge', default='plus,minus', type='string', help='process given charge. default is both')
    parser.add_option(     '--lumiLnN'    , dest='lumiLnN'    , default=-9.9, type='float', help='Log-normal constraint to be added to all the fixed MC processes')
    parser.add_option(     '--zXsecLnN'   , dest='zLnN'       , default=-9.9, type='float', help='Log-normal constraint to be added to all the fixed Z processes')
    parser.add_option(     '--wXsecLnN'   , dest='wLnN'       , default=0.038, type='float', help='Log-normal constraint to be added to all the fixed W processes or considered as background')
    parser.add_option(     '--sig-out-bkg', dest='sig_out_bkg' , default=False, action='store_true', help='Will treat signal bins corresponding to outliers as background processes')
    parser.add_option(     '--pdf-shape-only', dest='pdfShapeOnly' , default=False, action='store_true', help='Normalize the mirroring of the pdfs to central rate.')
    parser.add_option('--fp','--freezePOIs'  , dest='freezePOIs'   , default=False, action='store_true', help='run tensorflow with --freezePOIs (for the pdf only fit)')
    parser.add_option(       '--no-text2hdf5'  , dest='skip_text2hdf5', default=False, action='store_true', help='skip running text2hdf5.py at the end')
    parser.add_option(   '--eta-range-bkg', dest='eta_range_bkg', action="append", type="float", nargs=2, default=[], help='Will treat signal templates with gen level eta in this range as background in the datacard. Takes two float as arguments (increasing order) and can specify multiple times. They should match bin edges and a bin is not considered as background if at least one edge is outside this range')
    parser.add_option(   '--pt-range-bkg', dest='pt_range_bkg', action="append", type="float", nargs=2, default=[], help='Will treat signal templates with gen level pt in this range as background in the datacard. Takes two float as arguments (increasing order) and can specify multiple times. They should match bin edges and a bin is not considered as background if at least one edge is outside this range')
    parser.add_option(     '--comb-charge'          , dest='combineCharges' , default=False, action='store_true', help='Combine W+ and W-, if single cards are done. It ignores some options, since it is executed immediately and quit right afterwards')
    #parser.add_option(     '--comb-channel'         , dest='combineChannels' , default=False, action='store_true', help='Combine electrons and muons for a given charge, if single cards are done')
    parser.add_option(      '--override-jetPt-syst', dest='overrideJetPtSyst' ,default=True, action='store_true',  help="If True, it rebuilds the Down variation for the jet pt syst on fake-rate using the mirrorShape() function defined here, which is different from the one in makeShapeCards.py")
    parser.add_option( '--xsecMaskedYields', dest='xsecMaskedYields', default=False, action='store_true', help='use the xsec in the masked channel, not the expected yield')
    #parser.add_option('-s', '--sparse', dest='sparse' ,default=True, action='store_true', help="Store normalization and systematics arrays as sparse tensors. It enables the homonymous option of text2hdf5.py")
    (options, args) = parser.parse_args()
    
    from symmetrizeMatrixAbsY import getScales

    if not options.inputdir:
        print "Error: you must use option -i to specify the name of folder with cards. Exit"
        quit()

    #if options.combineCharges and options.combineChannels:
    #    print "ERROR: you are trying to combine both charges and channels, which is not supported. Exit"
    #    quit()

    cmssw = os.environ['CMSSW_VERSION']
    if cmssw != "":
        if cmssw == "CMSSW_8_0_25":
            print "ERROR: you must be in CMSSW_10_X to run this command and use combine with tensorflow. Exit"
            print "If X < 3, remember to do 'source /afs/cern.ch/user/b/bendavid/work/cmspublic/pythonvenv/tensorflowfit_10x/bin/activate'"
            quit()
    else:
        print "ERROR: need to set cmssw environment. Run cmsenv from CMSSW_10_X to run this command and use combine with tensorflow. Exit"
        print "If X < 3, remember to do 'source /afs/cern.ch/user/b/bendavid/work/cmspublic/pythonvenv/tensorflowfit_10x/bin/activate'"
        quit()

    if options.combineCharges:
        combCharges(options)
        print "I combined the datacards for both charges."
        quit()

    charges = options.charge.split(',')
    if options.bin not in ["Wmu", "Wel"]:
        print "ERROR: option -b only support 'Wmu' or 'Wel'. Exit"
        quit()
    channel = 'mu' if 'mu' in options.bin else 'el'
    Wcharge = ["Wplus","Wminus"]

    # get gen eta pt binning from file
    etaPtBinningFile = options.inputdir + "/binningPtEta.txt"
    with open(etaPtBinningFile) as f:
        content = f.readlines()
    for x in content:
        if str(x).startswith("gen"):
            etaPtBinning = (x.split("gen:")[1]).strip()
        else:
            continue
    etabinning = etaPtBinning.split('*')[0]    # this is like [a,b,c,...], and is of type string. We nedd to get an array                     
    ptbinning  = etaPtBinning.split('*')[1]
    etabinning = getArrayParsingString(etabinning,makeFloat=True)
    ptbinning  = getArrayParsingString(ptbinning,makeFloat=True)
    binning = [len(etabinning)-1, etabinning, len(ptbinning)-1, ptbinning]

    etaBinIsBackground = []  # will store a bool to assess whether the given ieta index is considered as background
    for bin in range(len(etabinning)-1):
        etaBinIsBackground.append(False)

    etaRangesBkg = options.eta_range_bkg

    if len(etaRangesBkg):
        hasEtaRangeBkg = True
        print "Signal bins with gen eta in the following ranges will be considered as background processes"
        print options.eta_range_bkg            
        for index in range(len(etabinning)-1):
            for pair in etaRangesBkg:
            #print pair
                if etabinning[index] >= pair[0] and etabinning[index+1] <= pair[1]:
                    etaBinIsBackground[index] = True
    else:
        hasEtaRangeBkg = False


    ptBinIsBackground = []  # will store a bool to assess whether the given ipt index is considered as background
    for bin in range(len(ptbinning)-1):
        ptBinIsBackground.append(False)

    ptRangesBkg = options.pt_range_bkg

    if len(ptRangesBkg):
        hasPtRangeBkg = True
        print "Signal bins with gen pt in the following ranges will be considered as background processes"
        print options.pt_range_bkg            
        for index in range(len(ptbinning)-1):
            for pair in ptRangesBkg:
            #print pair
                if ptbinning[index] >= pair[0] and ptbinning[index+1] <= pair[1]:
                    ptBinIsBackground[index] = True
    else:
        hasPtRangeBkg = False


    for charge in charges:
    
        outfile  = os.path.join(options.inputdir,options.bin+'_{ch}_shapes.root'.format(ch=charge))
        cardfile = os.path.join(options.inputdir,options.bin+'_{ch}_card.txt'   .format(ch=charge))
    
        ## prepare the relevant files. only the datacards and the correct charge
        files = ( f for f in os.listdir(options.inputdir) if f.endswith('.card.txt') )
        files = ( f for f in files if charge in f and not re.match('.*_pdf.*|.*_muR.*|.*_muF.*|.*alphaS.*|.*wptSlope.*|.*Effstat.*|.*mW.*',f) )
        files = sorted(files, key = lambda x: int(x.rstrip('.card.txt').split('_')[-1]) if not any(bkg in x for bkg in ['bkg','Z_']) else -1) ## ugly but works
        files = list( ( os.path.join(options.inputdir, f) for f in files ) )
        
    
        tmpfiles = []
        for ifile,f in enumerate(files):
            basename = os.path.basename(f).split('.')[0]
            dirf = os.path.dirname(f)
            bin = ''
            isEmpty = False
            with open(f) as thisfile:
                for l in thisfile.readlines():
                    if re.match('shapes.*',l):
                        rootfile = dirf+'/'+l.split()[3]
                    if re.match('bin.*',l):
                        if len(l.split()) < 2: continue ## skip the second bin line if empty
                        bin = l.split()[1]
                    rootfiles_syst = filter(lambda x: re.match('{base}_sig_(pdf\d+|muR\S+|muF\S+|alphaS\S+|wptSlope\S+|ErfPar\dEffStat\d+|mW\S+)\.input\.root'.format(base=basename),x), os.listdir(options.inputdir))
                    if ifile==0:
                        rootfiles_syst += filter(lambda x: re.match('Z_{channel}_{charge}_dy_(pdf\d+|muR\S+|muF\S+|alphaS\S+\S+)\.input\.root'.format(channel=channel,charge=charge),x), os.listdir(options.inputdir))
                    rootfiles_syst = [dirf+'/'+x for x in rootfiles_syst]
                    rootfiles_syst.sort()
                    if re.match('process\s+',l): 
                        if len(l.split()) > 1 and all(n.isdigit() for n in l.split()[1:]) : continue
                        processes = l.split()[1:]
 
            if options.mergeRoot:
                print 'processing bin: {bin}'.format(bin=bin)
                nominals = {}
                for irf,rf in enumerate([rootfile]+rootfiles_syst):
                    #print '\twith nominal/systematic file: ',rf
                    tf = ROOT.TFile.Open(rf)
                    tmpfile = os.path.join(options.inputdir,'tmp_{bin}_sys{sys}.root'.format(bin=bin,sys=irf))
                    of=ROOT.TFile(tmpfile,'recreate')
                    tmpfiles.append(tmpfile)
                    # remove the duplicates also
                    plots = {}
                    for e in tf.GetListOfKeys() :
                        name=e.GetName()
                        obj=e.ReadObj()
                        if name.endswith('data_obs') and 'data' not in basename: continue
                        if (not re.match('Wplus|Wminus',os.path.basename(f))) and 'data_obs' in name: obj.Clone().Write()
                        for p in processes:
                            if p in name:
                                newprocname = p+'_'+bin if re.match('Wplus|Wminus',p) else p
                                newname = name.replace(p,newprocname)
                                if irf==0:
                                    if newname not in plots:                                        
                                        ############### special case to fix jet pt syst on FR
                                        # if options.overrideJetPtSyst and 'data_fakes' in newname and 'awayJetPt' in newname:                       
                                        #     if 'Down' in newname:
                                        #         print "Skipping %s " % newname
                                        #         print "Will be recreated mirroring the Up component here"
                                        #         continue
                                        #     # this syst was made with alternateShape. However, the mirroring algorithm in makeShapeCards.py is different    
                                        #     # and produces a strange result on the mirrored image (which it calls 'Down')                                         
                                        #     # so here we take 'Up' and overwrite 'Down'                        
                                        #     # the old 'Down' will not be written                                                                            
                                        #     print "#####  CHECKPOINT  --> %s #####" % newname
                                        #     # the syst might have been evaluated before the nominal, so nominals["x_data_fakes"] might not exist yet
                                        #     pfx = 'x_data_fakes'
                                        #     newname = newname[:-2] # remove Up                           
                                        #     nominalFakes = 0
                                        #     if pfx in nominals:
                                        #         nominalFakes = nominals[pfx]
                                        #     else:
                                        #         nominalFakes = tf.Get(pfx)
                                        #         if not nominalFakes: 
                                        #             print "Warning: couldn't read %s from file" % pfx
                                        #             quit()
                                        #     (alternate,mirror) = mirrorShape(nominalFakes,obj,newname,alternateShapeOnly=False,use2xNomiIfAltIsZero=True)             
                                        #     for alt in [alternate,mirror]:
                                        #         if alt.GetName() not in plots:
                                        #             plots[alt.GetName()] = alt.Clone()
                                        #             plots[alt.GetName()].Write()
                                        if 'awayJetPt' in newname:                       
                                            # tmp patch to exclude this histogram
                                            continue
                                        else:
                                            plots[newname] = obj.Clone(newname)
                                            nominals[newname] = obj.Clone(newname+"0")
                                            nominals[newname].SetDirectory(None)
                                            #print 'replacing old %s with %s' % (name,newname)
                                            plots[newname].Write()                                    
                                else:
                                    #if 'pdf' in newname: # these changes by default shape and normalization. Each variation should be symmetrized wrt nominal
                                    if any(sysname in newname for sysname in ['pdf','Effstat']): # these changes by default shape and normalization. Each variation should be symmetrized wrt nominal
                                        sysname = 'pdf' if 'pdf' in newname else 'Effstat'
                                        tokens = newname.split("_"); pfx = '_'.join(tokens[:-2]); pdf = tokens[-1]
                                        ipdf = int(pdf.split('pdf')[-1])
                                        newname = "{pfx}_{sysname}{ipdf}".format(pfx=pfx,sysname=sysname,ipdf=ipdf)
                                        (alternate,mirror) = mirrorShape(nominals[pfx],obj,newname,options.pdfShapeOnly)
                                        for alt in [alternate,mirror]:
                                            if alt.GetName() not in plots:
                                                plots[alt.GetName()] = alt.Clone()
                                                plots[alt.GetName()].Write()
                                    elif re.match('.*_muR.*|.*_muF.*|.*alphaS.*|.*wptSlope.*|.*mW.*',newname): # these changes by default shape and normalization
                                        tokens = newname.split("_"); pfx = '_'.join(tokens[:-2]); syst = tokens[-1].replace('Dn','Down')
                                        newname = "{pfx}_{syst}".format(pfx=pfx,syst=syst)
                                        if 'wptSlope' in newname: # this needs to be scaled not to change normalization
                                            obj.Scale(nominals[pfx].Integral()/obj.Integral())
                                        if newname not in plots:
                                            plots[newname] = obj.Clone(newname)
                                            plots[newname].Write()
                    of.Close()

        if options.mergeRoot:
            haddcmd = 'hadd -f {of} {indir}/tmp_*.root'.format(of=outfile, indir=options.inputdir )
            #print 'would run this now: ', haddcmd
            #sys.exit()
            os.system(haddcmd)
            os.system('rm {indir}/tmp_*.root'.format(indir=options.inputdir))
            print "Merging of shape.root file finished.\n"

        print "Now trying to get info on theory uncertainties..."
        theosyst = {}
        expsyst = {}
        tf = ROOT.TFile.Open(outfile)
        for e in tf.GetListOfKeys() :
            name=e.GetName()
            if name.endswith("Up") or name.endswith("Down"):
                if name.endswith("Up"): name = re.sub('Up$','',name)
                if name.endswith("Down"): name = re.sub('Down$','',name)
                syst = name.split('_')[-1]
                binWsyst = '_'.join(name.split('_')[1:-1])
                if re.match('.*_pdf.*|.*_muR.*|.*_muF.*|.*alphaS.*|.*wptSlope.*|.*mW.*',name):
                    if syst not in theosyst: theosyst[syst] = [binWsyst]
                    else: theosyst[syst].append(binWsyst)
                if re.match('.*EffStat.*',name):
                    if syst not in expsyst: expsyst[syst] = [binWsyst]
                    else: expsyst[syst].append(binWsyst)
        pdfsyst = {k:v for k,v in theosyst.iteritems() if 'pdf' in k}
        qcdsyst = {k:v for k,v in theosyst.iteritems() if 'muR' in k or 'muF' in k}
        alssyst = {k:v for k,v in theosyst.iteritems() if 'alphaS' in k }
        wmodelsyst = {k:v for k,v in theosyst.iteritems() if 'wptSlope' in k or 'mW' in k}
        sortedpdfkeys = sorted(pdfsyst.keys(),key= lambda x: int(x.strip('pdf')))
        sortednonpdfkeys = sorted([x for x in theosyst.keys() if "pdf" not in x]) 
        sortedsystkeys = sortedpdfkeys + sortednonpdfkeys

        allsyst = theosyst.copy()
        allsyst.update(expsyst)

        if len(theosyst): print "Found a bunch of theoretical systematics: ",sortedsystkeys
        else: print "You are running w/o theory systematics. Lucky you!"

        effsyst = {k:v for k,v in expsyst.iteritems() if 'Effstat' in k}        
        if len(expsyst): print "Found a bunch of experimental sysematics: ",expsyst.keys()

        allsortedsystkeys = sortedsystkeys + [x for x in expsyst.keys()]

        combineCmd="combineCards.py "
        for f in files:
            basename = os.path.basename(f).split(".")[0]
            binname = ''
            if re.match('Wplus|Wminus',basename): binname=basename
            elif re.match('Z.*{charge}'.format(charge=charge),basename): binname='Z'
            else: binname='other'
            combineCmd += " %s=%s " % (binname,f)
        tmpcard = os.path.join(options.inputdir,'tmpcard.txt')
        combineCmd += ' > {tmpcard}'.format(tmpcard=tmpcard)
        #sys.exit()
        os.system(combineCmd)
    
        combinedCard = open(cardfile,'w')
        combinedCard.write("imax 1\n")
        combinedCard.write("jmax *\n")
        combinedCard.write("kmax *\n")
        combinedCard.write('##----------------------------------\n') 
        realprocesses = [] # array to preserve the sorting
        with open(tmpcard) as file_tmpcard:    
            nmatchbin=0
            nmatchprocess=0
            rateWritten=False
            for l in file_tmpcard.readlines():
                if re.match("shapes.*other",l):
                    variables = l.split()[4:]
                    combinedCard.write("shapes *  *  %s %s\n" % (os.path.abspath(outfile)," ".join(variables)))
                    combinedCard.write('##----------------------------------\n')
                if re.match("bin",l) and nmatchbin==0: 
                    nmatchbin=1
                    combinedCard.write('bin   %s\n' % options.bin) 
                    bins = l.split()[1:]
                if re.match("observation",l): 
                    yields = l.split()[1:]
                    observations = dict(zip(bins,yields))
                    combinedCard.write('observation %s\n' % observations['other'])
                    combinedCard.write('##----------------------------------\n')
                if re.match("bin",l) and nmatchbin==1:
                    pseudobins = l.split()[1:]
                if re.match("process",l):
                    if nmatchprocess==0:
                        pseudoprocesses = l.split()[1:]
                        klen = 7
                        kpatt = " %%%ds "  % klen
                        for i in xrange(len(pseudobins)):
                            # as it was implemented, I think this is always equal to pseudoprocesses[i], because there is no charge in pseudobins
                            # pseudobins is the number of the bin ( <= 0 for signal, > 0 for backgrounds) 
                            realprocesses.append(pseudoprocesses[i]+"_"+pseudobins[i] if any(x in pseudobins[i] for x in Wcharge) else pseudoprocesses[i])
                        combinedCard.write('bin            %s \n' % ' '.join([kpatt % options.bin for p in pseudoprocesses]))
                        combinedCard.write('process        %s \n' % ' '.join([kpatt % p for p in realprocesses]))
                        # going to write the number for the process: negative or 0 for signal, positive for the rest
                        procBin = {}
                        ibkg = 1
                        isig = 0
                        for p in realprocesses:
                            if any(wcharge in p for wcharge in Wcharge):
                                # some bins might be treated as background
                                if "outliers" in p:
                                    if options.sig_out_bkg:
                                        procBin[p] = ibkg
                                        ibkg += 1
                                    else:
                                        procBin[p] = isig
                                        isig += -1
                                else:
                                    if hasEtaRangeBkg or hasPtRangeBkg:
                                        etabinIndex,ptbinIndex = get_ieta_ipt_from_process_name(p)
                                        # now check if this eta or pt bin belongs to region which should be considered as background
                                        # if yes, increase the background bin index counter; if not, use the signal index as usual
                                        if etaBinIsBackground[etabinIndex] or ptBinIsBackground[ptbinIndex]:
                                            procBin[p] = ibkg
                                            ibkg += 1
                                        else:
                                            procBin[p] = isig
                                            isig += -1              
                                    else:
                                        procBin[p] = isig
                                        isig += -1 
                            else:
                                procBin[p] = ibkg
                                ibkg += 1
                        #combinedCard.write('process        %s \n' % ' '.join([kpatt % str(i+1) for i in xrange(len(pseudobins))]))
                        combinedCard.write('process        %s \n' % ' '.join([kpatt % procBin[p] for p in realprocesses]))
                    nmatchprocess += 1
                if re.match("rate",l):
                    klen = 7
                    kpatt = " %%%ds "  % klen
                    combinedCard.write('rate        %s \n' % ' '.join([kpatt % "-1" for p in realprocesses]))
                    rateWritten=True
                if nmatchprocess>=2 and rateWritten and not re.match("rate",l):  # when evaluating rate line above, here l is still that one!
                    # copy all the rest after rate from the temporary card
                    combinedCard.write(l)
            # now luminosity uncertainty and CMS_W, in case  they are not in systfile 
            if options.lumiLnN > 0:
                lumipar = "{0:.3f}".format(1.0 + options.lumiLnN) #"1.026"  # 2.6% 
                combinedCard.write(('%-23s lnN' % "CMS_lumi_13TeV") + ' '.join([kpatt % ("-" if "data" in key else lumipar) for key in realprocesses]) + "\n")
            # not needed because it will be measured
            Wxsec   = "{0:.3f}".format(1.0 + options.wLnN)    #"1.038"  # 3.8%
            #combinedCard.write(('%-23s lnN' % "CMS_W") + ' '.join([kpatt % (Wxsec if any(x in key for x in Wcharge) else "-"    ) for key in realprocesses]) + "\n")
            # if some signal bins are treated as background, assign 3.8% norm uncertainty
            if hasPtRangeBkg or hasEtaRangeBkg:
                combinedCard.write(('%-23s lnN' % "CMS_Wbkg") + ' '.join([kpatt % (Wxsec if (any(x in key for x in Wcharge) and procBin[p] > 0) else "-") for key in realprocesses]) + "\n")
            if options.zLnN > 0:
                Zxsec   = "{0:.3f}".format(1.0 + options.zLnN)    #"1.038"  # 3.8%
                combinedCard.write(('%-23s lnN' % "CMS_DY") + ' '.join([kpatt % (Zxsec if key == "Z" else "-" ) for key in realprocesses]) + "\n")

        os.system('rm {tmpcard}'.format(tmpcard=tmpcard))
        
        kpatt = " %7s "
    
        combinedCard = open(cardfile,'r')
        procs = []
        rates = []
        for l in combinedCard.readlines():
            if re.match("process\s+",l) and not re.match("process\s+\d",l): # my regexp qualities are bad... 
                procs = (l.rstrip().split())[1:]
            if re.match("rate\s+",l):
                rates = (l.rstrip().split())[1:]
            if len(procs) and len(rates): break
        ProcsAndRates = zip(procs,rates)
        ProcsAndRatesDict = dict(zip(procs,rates))
    
        combinedCard.close()

        combinedCard = open(cardfile,'a')
        POIs = []; fixedPOIs = []; allPOIs = []
        # following two lines currently not used anywhere
        signal_procs = filter(lambda x: re.match('Wplus|Wminus',x), realprocesses)
        signal_procs.sort(key=lambda x: int(x.split('_')[-1]))
        

        ## add the PDF systematics                                                         
        #for sys,procs in theosyst.iteritems():
        for sys in allsortedsystkeys:
            # there should be 2 occurrences of the same proc in procs (Up/Down). This check should be useless if all the syst jobs are DONE                      
            procs = allsyst[sys]
            combinedCard.write('%-15s   shape %s\n' % (sys,(" ".join(['1.0' if p in procs and procs.count(p)==2 else '  -  ' for p,r in ProcsAndRates]))) )
        if len(allsortedsystkeys):
            combinedCard.write('\npdfs group = '+' '.join([sys for sys in sortedpdfkeys])+'\n')
            combinedCard.write('\nscales group = '+' '.join([sys for sys,procs in qcdsyst.iteritems()])+'\n')
            combinedCard.write('\nalphaS group = '+' '.join([sys for sys,procs in alssyst.iteritems()])+'\n')
            combinedCard.write('\nwmodel group = '+' '.join([sys for sys,procs in wmodelsyst.iteritems()])+'\n')
            combinedCard.write('\nEffstat group = '+' '.join([sys for sys,procs in effsyst.iteritems()])+'\n')
        combinedCard.close()


        ## here we make a second datacard that will be masked. which for every process                                               
        ## has a 1-bin histogram with the cross section for every nuisance parameter and                                             
        ## every signal process inside                                                                                               

        ## first make a list of all the signal processes
        tmp_sigprocs = [p for p in realprocesses if 'Wminus' in p or 'Wplus' in p]
 
        ## xsecfilename                                                                                                                                                    
        xsecfile = '/afs/cern.ch/work/m/mciprian/public/whelicity_stuff/xsection_genAbsEtaPt_preFSR_mu_pt1_eta0p1_etaGap_yields.root'
        if options.xsecMaskedYields:
            xsecfile = "/afs/cern.ch/work/m/mciprian/public/whelicity_stuff/xsection_genAbsEtaPt_preFSR_mu_pt1_eta0p1_etaGap_xsecPb.root"
        hists = getXsecs_etaPt(tmp_sigprocs,
                               [i for i in sortedsystkeys if not 'wpt' in i], # wptslope is not used anymore, anyway, do not pass it
                               binning,
                               # no need to pass a luminosity, histograms in xsection_genEtaPt.root are already divided by it (xsec in pb)
                               # 35.9 if channel == 'mu' else 30.9,  
                               xsecfile
                               )
        tmp_xsec_histfile_name = os.path.abspath(outfile.replace('_shapes','_shapes_xsec'))
        tmp_xsec_hists = ROOT.TFile(tmp_xsec_histfile_name, 'recreate')
        for hist in hists:
            hist.Write()
        tmp_xsec_hists.Close()

        tmp_xsec_dc_name = os.path.join(options.inputdir,options.bin+'_{ch}_xsec_card.txt'   .format(ch=charge))
        tmp_xsec_dc = open(tmp_xsec_dc_name, 'w')
        tmp_xsec_dc.write("imax 1\n")
        tmp_xsec_dc.write("jmax *\n")
        tmp_xsec_dc.write("kmax *\n")
        tmp_xsec_dc.write('##----------------------------------\n')
        tmp_xsec_dc.write("shapes *  *  %s %s\n" % (tmp_xsec_histfile_name, 'x_$PROCESS x_$PROCESS_$SYSTEMATIC'))
        tmp_xsec_dc.write('##----------------------------------\n')
        tmp_xsec_dc.write('bin {b}\n'.format(b=options.bin))
        tmp_xsec_dc.write('observation -1\n') ## don't know if that will work...                                                     
        tmp_xsec_dc.write('bin      {s}\n'.format(s=' '.join(['{b}'.format(b=options.bin) for p in tmp_sigprocs])))
        tmp_xsec_dc.write('process  {s}\n'.format(s=' '.join([p for p in tmp_sigprocs])))
        ###tmp_xsec_dc.write('process  {s}\n'.format(s=' '.join([str(i+1)  for i in range(len(tmp_sigprocs))]))) 
        tmp_xsec_dc.write('process  {s}\n'.format(s=' '.join([str(procBin[pname])  for pname in tmp_sigprocs])))
        tmp_xsec_dc.write('rate     {s}\n'.format(s=' '.join('-1' for i in range(len(tmp_sigprocs)))))
        tmp_xsec_dc.write('# --------------------------------------------------------------\n')

        # for sys,procs in theosyst.iteritems():          
        for sys in sortedsystkeys: # this is only theoretical systs
            if 'wpt' in sys: continue
            if 'EffStat' in sys: continue  # just in case
            # there should be 2 occurrences of the same proc in procs (Up/Down). This check should be useless if all the syst jobs are DONE                      
            tmp_xsec_dc.write('%-15s   shape %s\n' % (sys,(" ".join(['1.0' if p in tmp_sigprocs  else '  -  ' for p in tmp_sigprocs]))) )
        tmp_xsec_dc.close()

        ## end of all the xsec construction of datacard and making the file                                                               

        # need to run this command
        #combineCards.py Wel_plus=Wel_plus_card.txt Wel_plus_xsec=Wel_plus_xsec_card.txt > Wel_plus_card_withXsecMask.txt
        # text2tf.py Wel_plus_card_withXsecMask.txt --maskedChan Wel_plus_xsec --X-allow-no-background

        print "\nmerged datacard in ",cardfile
        print "datacard with xsection in ",tmp_xsec_dc_name
        cardfile_xsec = cardfile.replace('_card', '_card_withXsecMask')
        chname = options.bin+'_{ch}'.format(ch=charge)
        chname_xsec = chname+'_xsec'
        ccCmd = 'combineCards.py {oc}={odc} {xc}={xdc} > {out}'.format(oc=chname,odc=cardfile,xc=chname_xsec,xdc=tmp_xsec_dc_name,out=cardfile_xsec)
        if options.freezePOIs:
            # doesn't make sense to have the xsec masked channel if you freeze the rates (POIs) -- and doesn't work either            
            txt2hdf5Cmd = 'text2hdf5.py --sparse {cf}'.format(cf=combinedCard)
        else:
            # masked channel has no background, I need to use option --X-allow-no-background
            txt2hdf5Cmd = 'text2hdf5.py --sparse --maskedChan {maskch} --X-allow-no-background {cf}'.format(maskch=chname_xsec,cf=cardfile_xsec)

        print "\nNow merging the two"
        print ccCmd
        os.system(ccCmd)
        ## then running the text2hdf5 command afterwards     
        print "\nThe following is the command to run text2hdf5.py"
        print "\n" + txt2hdf5Cmd
        if not options.skip_text2hdf5:
            print '-- Now running text2hdf5 (might take time) ---------------------'
            print 'text2hdf5.py has some default options that might affect the result. You are invited to check them'
            os.system(txt2hdf5Cmd)
 
        if options.freezePOIs:
            combineCmd = 'combinetf.py --POIMode none -t -1 --binByBinStat --correlateXsecStat {metafile}'.format(metafile=cardfile_xsec.replace('.txt','_sparse.hdf5'))
        else:
            combineCmd = 'combinetf.py -t -1 --binByBinStat --correlateXsecStat {metafile}'.format(metafile=cardfile_xsec.replace('.txt','_sparse.hdf5'))
        print "Printing command to run combine."
        print combineCmd

########################################
    # end of loop over charges
########################################

    print "##############################"
    print "#########  THE END!  #########"
    print "##############################"

