#!/bin/env python

# usage:
# make the single charge: ./mergeCardComponentsAbsY.py -b Wel -C plus,minus -i cards_el [--fp]
# make the W+ / W- comb:  ./mergeCardComponentsAbsY.py -b Wel --comb -i cards_el [--fp]
# [--fp] is used to make the meta file freezing ALL the rates (POIs). Use it to make the fit for PDFs only. When not used the xsecs are tracked via masked channel trick

import ROOT
import sys,os,re,json, copy, math
from rollingFunctions import roll1Dto2D, dressed2D, unroll2Dto1D
from array import array
import root_numpy
import utilities
utilities = utilities.util()

# to manage binning reading from file
from make_diff_xsec_cards import getDiffXsecBinning
from make_diff_xsec_cards import templateBinning

def correctScale(sys, p):
    if not re.match('.*mu(R|F).*',sys): return True
    match = re.match('x_W(plus|minus)_.*(plus|minus)(Up|Down)',sys)
    if match and match.group(1) != match.group(2): return False
    isCorrectScale = False
    if 'long'  in sys and 'long'  in p: isCorrectScale = True
    if 'left'  in sys and 'left'  in p: isCorrectScale = True
    if 'right' in sys and 'right' in p: isCorrectScale = True
    return isCorrectScale

def isExcludedNuisance(excludeNuisances=[], name=""):
    if len(excludeNuisances) and any(re.match(x,name) for x in excludeNuisances): 
        print ">>>>> Excluding nuisance: ", name
        return True
    else:
        return False

def get_iy_from_process_name(name):
    # name is something like  Wplus_right_Ybin_1
    if not "Ybin" in name:
        print "Error in get_iy_from_process_name(): 'Ybin' not found in %s. Exit" % name
        quit()
    tokens = name.split('_')
    for i,tkn in enumerate(tokens):
        #print "%d %s" % (i, tkn)                                                                                                                        
        if tkn == "Ybin": iy = int(tokens[i + 1])
    return iy


def getXsecs(processes, systs, ybins, lumi, infile):
    histo_file = ROOT.TFile(infile, 'READ')

    hists = []

    for process in processes:
        pol = 'left' if 'left' in process else 'right' if 'right' in process else 'long'

        cen_name = 'w'+charge+'_wy_central_W' +charge+'_'+pol
        cen_hist = histo_file.Get(cen_name)

        ybinnumber = int(process.split('_')[-1])
        yfirst = ybins[pol][ybinnumber]
        ylast  = ybins[pol][ybinnumber+1]

        # before searching the bin, sum epsilon to the y value being inspected
        # Root assigns the lower bin edge to the bin, while the upper bin edge is assigned to the adjacent bin. However, depending on the number y being used,
        # there can be a precision issue which might induce the selection of the wrong bin (since yfirst and yvalue are actually bin boundaries)
        epsilon = 0.00001
        istart = cen_hist.FindBin(yfirst + epsilon)
        iend   = cen_hist.FindBin(ylast + epsilon)

        ncen = cen_hist .Integral(istart, iend-1)

        tmp_hist = ROOT.TH1F('x_'+process,'x_'+process, 1, 0., 1.)
        ## normalize back to cross section
        tmp_hist.SetBinContent(1, ncen/lumi)

        hists.append(copy.deepcopy(tmp_hist))

        for sys in systs:

            # skipping the look for xsec for the theory systematics which belong only to Wtau
            if re.match('^muR\d+(minus|plus)|^muF\d+(minus|plus)|^muRmuF\d+(minus|plus)',sys): continue

            original_sys = sys
            if 'longmu' in sys or 'leftmu' in sys or 'rightmu' in sys:
                if not pol in sys: continue
                sys = sys.replace('long','').replace('right','').replace('left','')
                sys = sys.replace('minus','').replace('plus','')

            upn = sys+'Up' if not 'pdf' in sys else sys
            dnn = sys+'Dn' if not 'pdf' in sys else sys

            sys_upname = 'w'+charge+'_wy_'+upn+'_W'+charge+'_'+pol
            sys_dnname = 'w'+charge+'_wy_'+dnn+'_W'+charge+'_'+pol

            sys_up_hist = histo_file.Get(sys_upname)
            sys_dn_hist = histo_file.Get(sys_dnname)

            nup = sys_up_hist .Integral(istart, iend-1)
            ndn = sys_dn_hist .Integral(istart, iend-1)

            if 'pdf' in sys:
                ndn = 2.*ncen-nup ## or ncen/nup?

            tmp_hist_up = ROOT.TH1F('x_'+process+'_'+original_sys+'Up','x_'+process+'_'+original_sys+'Up', 1, 0., 1.)
            tmp_hist_up.SetBinContent(1, nup/lumi)
            tmp_hist_dn = ROOT.TH1F('x_'+process+'_'+original_sys+'Down','x_'+process+'_'+original_sys+'Dn', 1, 0., 1.)
            tmp_hist_dn.SetBinContent(1, ndn/lumi)
            hists.append(copy.deepcopy(tmp_hist_up))
            hists.append(copy.deepcopy(tmp_hist_dn))

    hist_data = ROOT.TH1F('x_data_obs', 'x_data_obs', 1, 0., 1.)
    hist_data.SetBinContent(1, 1.)
    hists.append(copy.deepcopy(hist_data))

    return hists


def mirrorShape(nominal,alternate,newname,alternateShapeOnly=False,use2xNomiIfAltIsZero=False):
    alternate.SetName("%sUp" % newname)
    if alternateShapeOnly:
        alternate.Scale(nominal.Integral()/alternate.Integral())
    mirror = nominal.Clone("%sDown" % newname)
    for b in xrange(1,nominal.GetNbinsX()+1):
        y0 = nominal.GetBinContent(b)
        yA = alternate.GetBinContent(b)
        # geometric mean
        # yM = y0
        # if yA != 0:
        #     yM = y0*y0/yA
        # elif yA == 0:
        #     if use2xNomiIfAltIsZero: 
        #         yM = 2. * y0
        #     else: 
        #         yM = 0
        # arithmetic mean
        yM = max(0,2*y0-yA)
        mirror.SetBinContent(b, yM)
    if alternateShapeOnly:
        # keep same normalization
        mirror.Scale(nominal.Integral()/mirror.Integral())
    return (alternate,mirror)

def cropHighSysts(h_nom,h_syst,maxSyst=0.05):
    for i in xrange(1,1+h_nom.GetNbinsX()):
        nom  = h_nom.GetBinContent(i)
        syst = h_syst.GetBinContent(i)
        if nom==0: 
            h_syst.SetBinContent(i, 0)
        elif syst/nom > (1 + maxSyst): 
            h_syst.SetBinContent(i, nom*(1+maxSyst))
        elif syst/nom < (1 - maxSyst):
            h_syst.SetBinContent(i, nom*(1-maxSyst))

def combCharges(options):
    suffix = 'card' if options.freezePOIs else 'card_withXsecMask'
    datacards=[]; channels=[]
    for charge in ['plus','minus']:
        datacards.append(os.path.abspath(options.inputdir)+"/"+options.bin+'_{ch}_card.txt'.format(ch=charge))
        channels.append('{bin}_{ch}'.format(bin=options.bin,ch=charge))
        maskedChannels = ['InAcc']
        if options.ybinsOutAcc:
            maskedChannels.append('OutAcc')
        if not options.freezePOIs:
            for mc in maskedChannels:
                datacards.append(os.path.abspath(options.inputdir)+"/"+options.bin+'_{ch}_xsec_{maskchan}_card.txt'.format(ch=charge,maskchan=mc))
                channels.append('{bin}_{ch}_xsec_{maskchan}'.format(bin=options.bin,ch=charge,maskchan=mc))

    if options.combineCharges and sum([os.path.exists(card) for card in datacards])==len(datacards):
        print "Cards for W+ and W- done. Combining them now..."
        combinedCard = os.path.abspath(options.inputdir)+"/"+options.bin+'_'+suffix+'.txt'
        ccCmd = 'combineCards.py --noDirPrefix '+' '.join(['{channel}={dcfile}'.format(channel=channels[i],dcfile=datacards[i]) for i,c in enumerate(channels)])+' > '+combinedCard
        if options.freezePOIs:
            # doesn't make sense to have the xsec masked channel if you freeze the rates (POIs) -- and doesn't work either
            txt2hdf5Cmd = 'text2hdf5.py {sp} {cf} --clipSystVariations {varmax}'.format(cf=combinedCard,sp="--sparse" if options.sparse else "",varmax=1.3)
        else:
            maskchan = [' --maskedChan {bin}_{charge}_xsec_{mc}'.format(bin=options.bin,charge=ch,mc=mc) for ch in ['plus','minus'] for mc in maskedChannels]
            txt2hdf5Cmd = 'text2hdf5.py {sp} {maskch} --X-allow-no-background {cf} --clipSystVariations {varmax}'.format(maskch=' '.join(maskchan),cf=combinedCard,sp="--sparse" if options.sparse else "",varmax=1.3)
            
        if len(options.postfix):
            txt2hdf5Cmd = txt2hdf5Cmd + " --postfix " + options.postfix

        ## here running the combine cards command first 
        print ccCmd
        os.system(ccCmd)
        ## here making the TF meta file
        print '--- will run text2hdf5 for the combined charges ---------------------'
        print txt2hdf5Cmd
        if not options.skip_text2hdf5:
            os.system(txt2hdf5Cmd)
        ## print out the command to run in combine
        metafilename=combinedCard.replace('.txt','_sparse.hdf5' if options.sparse else '.hdf5')
        if len(options.postfix):
            metafilename = metafilename.replace('.hdf5','_%s.hdf5' % options.postfix)

        if options.freezePOIs:
            combineCmd = 'combinetf.py --POIMode none -t -1 --binByBinStat --correlateXsecStat {metafile}'.format(metafile=metafilename)
        else:
            combineCmd = 'combinetf.py -t -1 --binByBinStat --correlateXsecStat {metafile}'.format(metafile=metafilename)
        print combineCmd


def putUncorrelatedFakes(infile,regexp,charge, outdir=None, isMu=True, etaBordersTmp=[], doType = 'eta', uncorrelateCharges=False, isHelicity = True):

    # for differential cross section I don't use the same option for inputs, so I pass it from outside
    indir = outdir if outdir != None else options.inputdir 

    # get eta-pt binning for both reco 
    etaPtBinningVec = getDiffXsecBinning(indir+'/binningPtEta.txt', "reco")  # this get two vectors with eta and pt binning
    recoBins = templateBinning(etaPtBinningVec[0],etaPtBinningVec[1])        # this create a class to manage the binnings
    binning = [recoBins.Neta, recoBins.etaBins, recoBins.Npt, recoBins.ptBins]
    etabins = recoBins.etaBins
    ptbins  = recoBins.ptBins

    flav = 'mu' if isMu else 'el'

    tmp_infile = ROOT.TFile(infile, 'read')

    doPt     = doType == 'ptslope' ## keep that from before
    doEta    = doType == 'eta'
    doPtNorm = doType == 'ptnorm'
    doUncorrChargeEta = doType == 'etacharge'
    if flav=='el' and isHelicity: doUncorrChargeEta = False # overwrite everything for ele
    if doUncorrChargeEta: uncorrelateCharges = True  # just in case one forgets

    typeName = 'PtSlope' if doPt else 'Eta' if doEta else 'PtNorm' if doPtNorm else 'EtaCharge' if doUncorrChargeEta else ''
    if not typeName:
        print 'YOU GAVE A WRONG OPTION TO THE UNCORRELATED FAKES FUNCTION'
        sys.exit()

    print 'putting uncorrelated fakes for type', doType
    
    outfile = ROOT.TFile('{od}/Fakes{sn}Uncorrelated_{flav}_{ch}.root'.format(od=indir, sn=typeName, flav=flav, ch=charge), 'recreate')

    ndone = 0

    var_up = None
    var_dn = None
    ## need to loop once for the pT uncorrelated. i'm sure there's a better way but i'm lazy
    if doPt:
        for k in tmp_infile.GetListOfKeys():
            tmp_name = k.GetName()
            if re.match('x_data_fakes_.*slope.*', tmp_name) and 'Up'   in tmp_name: var_up = tmp_name
            if re.match('x_data_fakes_.*slope.*', tmp_name) and 'Down' in tmp_name: var_dn = tmp_name
        if var_up == None or var_dn == None:
            print 'DID NOT FIND THE RIGHT KEY!!!'
            quit()

    for k in tmp_infile.GetListOfKeys():
        tmp_name = k.GetName()

        ## don't reweight any histos that don't match the regexp
        if not re.match(regexp, tmp_name): continue
        ## don't reweight any histos that are already variations of something else
        if 'Up' in tmp_name or 'Down' in tmp_name: continue

        #if ndone: continue
        ndone += 1

        ## now should be left with only the ones we are interested in
        print 'reweighting the fake contribution for uncorrelated bins in eta for process', tmp_name
        
        tmp_nominal = tmp_infile.Get(tmp_name)
        tmp_nominal_2d = dressed2D(tmp_nominal,binning, tmp_name+'backrolled')

        postfixForFlavourAndCharge = "mu" if isMu else "el"
        if uncorrelateCharges:
            postfixForFlavourAndCharge += charge

        if doPt:
            tmp_up = tmp_infile.Get(var_up)
            tmp_up_2d = dressed2D(tmp_up,binning, var_up+'backrolled')
            tmp_dn = tmp_infile.Get(var_dn)
            tmp_dn_2d = dressed2D(tmp_dn,binning, var_dn+'backrolled')

        ## get the border bins in eta for the uncorrelated nuisances in eta
        if doPt or doEta or doUncorrChargeEta:
            deltaEtaUnc = 0.5001 if isMu else 0.2001
            ## this is to add a large non closure overall in EB / EE separate (which adds to the +/-5% eta uncorrelated)
            if not isMu and doUncorrChargeEta:
                deltaEtaUnc = 1.5
            ## absolute eta borders:
            etaBorders = etaBordersTmp if len(etaBordersTmp) else [round(deltaEtaUnc*(i+1),1) for i in xrange(int(max(etabins)/deltaEtaUnc))] #+[max(etabins)]
            ## construct positive and negative eta borders symmetrically
            etaBorders = [-1.*i for i in etaBorders[::-1]] + [0.] + etaBorders
            borderBins = [1]
            ## now get the actual bin number of the border bins

            print "putUncorrelatedFakes: etaBorders = %s" % ",".join(str(x) for x in etaBorders)
            for i in etaBorders:
                borderBins.append(next(x[0] for x in enumerate(etabins) if x[1] > i))
            borderBins += [len(etabins)]
            print "putUncorrelatedFakes: borderBins = %s" % ",".join(str(x) for x in borderBins)

            if doUncorrChargeEta:
                chargeAsymSyst = 0.02 if isMu else 0.01
                scalings = [chargeAsymSyst for b in borderBins[:-1]]
            else:
                if isMu: 
                    factor = 0.046 # it used to be 0.05 for Eta, but now it is splitted in charge-correlated and charge-uncorrelated part
                    scalings = [factor for b in borderBins[:-1]]
                else:
                    scalings = []
                    for ib, borderBin in enumerate(borderBins[:-1]):
                        # slightly reducing these numbers, as now we have a part that is uncorrelated between charges
                        if   abs(etabins[borderBin]) < 0.21: scalings.append(0.005)
                        elif abs(etabins[borderBin]) < 0.41: scalings.append(0.005)
                        elif abs(etabins[borderBin]) < 1.01: scalings.append(0.03)
                        elif abs(etabins[borderBin]) < 1.51: scalings.append(0.05)
                        elif abs(etabins[borderBin]) < 1.71: scalings.append(0.05)
                        elif abs(etabins[borderBin]) < 2.00: scalings.append(0.02)
                        else:                                scalings.append(0.05)

        ## for ptnorm these are now pT borders, not eta borders
        elif doPtNorm:
            print 'this is ptbins', ptbins
            #ptBorders = [26, 32, 38, 45, 50, 56] if isMu else [30, 35, 40, 45, 50, 56]  # last pt bin for 2D xsec might be 56 or 55, now I am using 56
            ptBorders = [26, 29, 32, 35, 38, 41, 45] if isMu else [30, 35, 40, 45]                
            if not isHelicity:
                #ptBorders = [26, 30, 33, 36, 39, 42, 45] if isMu else [30, 33, 36, 39, 42, 45] 
                #ptBorders = [26, 30, 33, 36, 39, 42, 45] if isMu else [30, 36, 40.5, 45] 
                ptBorders = [26, 33, 36, 40.5, 45] if isMu else [30, 36, 40.5, 45] 
            if isMu and recoBins.ptBins[0] > 29.9:
                # just for tests on 2D xsec, where pT >= 30
                ptBorders = [30, 33, 36, 39, 42, 45]
            # now a tuning for 2D xsec binning, for which I have some pt bins after 45
            if ptbins[-1] > ptBorders[-1]:
                if ptBorders[-1] not in ptbins:  # in case I use different binning here
                    minPtDiff = 999
                    iptMin = 0
                    for ipt,ptval in enumerate(ptbins):
                        if ptval > 45 and abs(ptval - 45) < minPtDiff:
                            minPtDiff = abs(ptval - 45)
                            iptMin = ipt
                    ptBorders[-1] = ptbins[iptMin] # could be 45.5 or 46
                ptBorders.extend([50, 56])
            print 'this is ptBorders', ptBorders
            borderBins = []
            for i in ptBorders[:-1]:
                borderBins.append(next( x[0] for x in enumerate(ptbins) if x[1] > i))
            borderBins.append(len(ptbins))

            scalings = [0.30, 0.30, 0.25, 0.25, 0.15, 0.15, 0.25, 0.30] if isMu else [0.10, 0.10, 0.05, 0.20, 0.20]
            if not isHelicity:
                #scalings = [0.30, 0.30, 0.25, 0.25, 0.15, 0.15, 0.25, 0.30] if isMu else [0.10, 0.10, 0.10, 0.05, 0.05, 0.20, 0.20]
                #scalings = [0.30, 0.30, 0.25, 0.25, 0.15, 0.15, 0.25, 0.30] if isMu else [0.10, 0.10, 0.05, 0.20, 0.20]
                scalings = [0.30, 0.25, 0.25, 0.15, 0.25, 0.30] if isMu else [0.10, 0.10, 0.05, 0.20, 0.20]
            if isMu and recoBins.ptBins[0] > 29.9:
                scalings = [0.30, 0.25, 0.25, 0.15, 0.15, 0.25, 0.30]

        ## loop over all eta bins of the 2d histogram
        for ib, borderBin in enumerate(borderBins[:-1]):

            systName = 'Fakes{v}Uncorrelated'.format(v=typeName)
            outname_2d = tmp_nominal_2d.GetName().replace('backrolled','')+'_{sn}{ib}{flavch}2DROLLED'.format(sn=systName,ib=ib+1,flavch=postfixForFlavourAndCharge)
        
            tmp_scaledHisto_up = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Up'))
            tmp_scaledHisto_dn = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Down'))
            
            if doPt or doEta or doUncorrChargeEta:
                for ieta in range(borderBin,borderBins[ib+1]):
                    ## loop over all pT bins in that bin of eta (which is ieta)
                    for ipt in range(1,tmp_scaledHisto_up.GetNbinsY()+1):
                        if doEta or doUncorrChargeEta:
                            tmp_bincontent = tmp_scaledHisto_up.GetBinContent(ieta, ipt)
                            scaling = scalings[ib]
                            ## scale up and down with what we got from the histo
                            tmp_bincontent_up = tmp_bincontent*(1.+scaling)
                            tmp_bincontent_dn = tmp_bincontent*(1.-scaling)
                            tmp_scaledHisto_up.SetBinContent(ieta, ipt, tmp_bincontent_up)
                            tmp_scaledHisto_dn.SetBinContent(ieta, ipt, tmp_bincontent_dn)
                        if doPt:
                            ## for the pT binned ones set it to the up/down
                            tmp_scaledHisto_up.SetBinContent(ieta, ipt, tmp_up_2d.GetBinContent(ieta,ipt))
                            tmp_scaledHisto_dn.SetBinContent(ieta, ipt, tmp_dn_2d.GetBinContent(ieta,ipt))

            ## loop the other way around for the pT norm
            if doPtNorm:
                for ipt  in range(borderBin,borderBins[ib+1]):
                    ## loop over all pT bins in that bin of eta (which is ieta)
                    for ieta in range(1,tmp_scaledHisto_up.GetNbinsX()+1):
                        tmp_bincontent = tmp_scaledHisto_up.GetBinContent(ieta, ipt)
                        scaling = scalings[ib]
                        ## scale up and down with what we got from the histo
                        tmp_bincontent_up = tmp_bincontent*(1.+scaling)
                        tmp_bincontent_dn = tmp_bincontent*(1.-scaling)
                        tmp_scaledHisto_up.SetBinContent(ieta, ipt, tmp_bincontent_up)
                        tmp_scaledHisto_dn.SetBinContent(ieta, ipt, tmp_bincontent_dn)

            ## re-roll the 2D to a 1D histo
            tmp_scaledHisto_up_1d = unroll2Dto1D(tmp_scaledHisto_up, newname=tmp_scaledHisto_up.GetName().replace('2DROLLED',''))
            tmp_scaledHisto_dn_1d = unroll2Dto1D(tmp_scaledHisto_dn, newname=tmp_scaledHisto_dn.GetName().replace('2DROLLED',''))

            outfile.cd()
            tmp_scaledHisto_up_1d.Write()
            tmp_scaledHisto_dn_1d.Write()
    outfile.Close()
    ## print 'done with the reweightings for the uncorrelated fake systematics'

def putEffStatHistos(infile,regexp,charge, outdir=None, isMu=True):

    # for differential cross section I don't use the same option for inputs, so I pass it from outside
    indir = outdir if outdir != None else options.inputdir

    # this doesn't work for differential cross section because I have line 2 with the comment for gen binning
    # in all my scripts I developed some specific functions to read the binning, either reco or gen: here we only need reco
    # binninPtEtaFile = open(indir+'/binningPtEta.txt','r')
    # bins = binninPtEtaFile.readlines()[1].split()[1]
    # etabins = list( float(i) for i in bins.replace(' ','').split('*')[0].replace('[','').replace(']','').split(',') )
    # ptbins  = list( float(i) for i in bins.replace(' ','').split('*')[1].replace('[','').replace(']','').split(',') )
    # nbinseta = len(etabins)-1
    # nbinspt  = len( ptbins)-1
    # binning = [nbinseta, etabins, nbinspt, ptbins]

    # get eta-pt binning for both reco 
    etaPtBinningVec = getDiffXsecBinning(indir+'/binningPtEta.txt', "reco")  # this get two vectors with eta and pt binning
    recoBins = templateBinning(etaPtBinningVec[0],etaPtBinningVec[1])        # this create a class to manage the binnings
    binning = [recoBins.Neta, recoBins.etaBins, recoBins.Npt, recoBins.ptBins]
    etabins = recoBins.etaBins

    #basedir = '/afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/CMSSW_8_0_25/src/CMGTools/WMass/python/postprocessing/data/'
    basedir = '/afs/cern.ch/work/e/emanuele/wmass/heppy/CMSSW_8_0_25/src/CMGTools/WMass/python/postprocessing/data/'
    if isMu:
        flav = 'mu'
        if charge == 'plus':
            parfile_name = basedir+'/leptonSF/new2016_madeSummer2018/systEff_trgmu_plus_mu.root'
        else:
            parfile_name = basedir+'/leptonSF/new2016_madeSummer2018/systEff_trgmu_minus_mu.root'
    else:
        flav = 'el'
        parfile_name = basedir+'/leptonSF/new2016_madeSummer2018/systEff_trgel.root'

    parfile = ROOT.TFile(parfile_name, 'read')
    

    tmp_infile = ROOT.TFile(infile, 'read')

    outfile = ROOT.TFile(indir+'/ErfParEffStat_{flav}_{ch}.root'.format(ch=charge,flav=flav), 'recreate')

    ndone = 0
    for k in tmp_infile.GetListOfKeys():
        tmp_name = k.GetName()
        ## don't reweight any histos that don't match the regexp
        if not re.match(regexp, tmp_name): continue
        ## don't reweight any histos that are already variations of something else
        if 'Up' in tmp_name or 'Down' in tmp_name: continue
        if 'lepeff' in tmp_name: continue

        #if ndone: continue
        ndone += 1

        ## now should be left with only the ones we are interested in
        print 'reweighting erfpareffstat nuisances for process', tmp_name
        
        tmp_nominal = tmp_infile.Get(tmp_name)
        tmp_nominal_2d = dressed2D(tmp_nominal,binning, tmp_name+'backrolled')

        ## loop over the three parameters
        for npar in range(3):
            parhist = parfile.Get('p'+str(npar))
            ## loop over all eta bins of the 2d histogram
            for ieta in range(1,tmp_nominal_2d.GetNbinsX()+1):
                eta = tmp_nominal_2d.GetXaxis().GetBinCenter(ieta)

                outname_2d = tmp_nominal_2d.GetName().replace('backrolled','')+'_ErfPar{p}EffStat{eta}{flav}{ch}2DROLLED'.format(p=npar,eta=ieta,flav=flav,ch=charge)
            
                tmp_scaledHisto_up = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Up'))
                tmp_scaledHisto_dn = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Down'))
                
                ## loop over all pT bins in that bin of eta (which is ieta)
                for ipt in range(1,tmp_scaledHisto_up.GetNbinsY()+1):
                    tmp_bincontent = tmp_scaledHisto_up.GetBinContent(ieta, ipt)
                    ybincenter = tmp_scaledHisto_up.GetYaxis().GetBinCenter(ipt)
                    ## now get the content of the parameter variation!
                    phistxbin = parhist.GetXaxis().FindBin(eta)
                    phistybin = parhist.GetYaxis().FindBin(ybincenter)
                    tmp_scale = parhist.GetBinContent(parhist.GetXaxis().FindBin(eta),parhist.GetYaxis().FindBin(ybincenter))
                    scaling = math.sqrt(2.)*tmp_scale
                    ## scale electrons by sqrt(2) due to the input file being charge inclusive
                    if flav == 'el':
                        scaling *= math.sqrt(2)
                    ## scale up and down with what we got from the histo
                    tmp_bincontent_up = tmp_bincontent*(1.+scaling)
                    tmp_bincontent_dn = tmp_bincontent*(1.-scaling)
                    tmp_scaledHisto_up.SetBinContent(ieta, ipt, tmp_bincontent_up)
                    tmp_scaledHisto_dn.SetBinContent(ieta, ipt, tmp_bincontent_dn)

                ## re-roll the 2D to a 1D histo
                tmp_scaledHisto_up_1d = unroll2Dto1D(tmp_scaledHisto_up, newname=tmp_scaledHisto_up.GetName().replace('2DROLLED',''))
                tmp_scaledHisto_dn_1d = unroll2Dto1D(tmp_scaledHisto_dn, newname=tmp_scaledHisto_dn.GetName().replace('2DROLLED',''))

                outfile.cd()
                tmp_scaledHisto_up_1d.Write()
                tmp_scaledHisto_dn_1d.Write()
    outfile.Close()
    print 'done with the many reweightings for the erfpar effstat'

def putEffSystHistos(infile,regexp, doType='TnP', outdir=None, isMu=True, isHelicity=True, silentCrop=False):

    # for differential cross section I don't use the same option for inputs, so I pass it from outside
    indir = outdir if outdir != None else options.inputdir
    flav = 'mu' if isMu else 'el'

    # get eta-pt binning for reco 
    etaPtBinningVec = getDiffXsecBinning(indir+'/binningPtEta.txt', "reco")  # this get two vectors with eta and pt binning
    recoBins = templateBinning(etaPtBinningVec[0],etaPtBinningVec[1])        # this create a class to manage the binnings
    binning = [recoBins.Neta, recoBins.etaBins, recoBins.Npt, recoBins.ptBins]

    tmp_infile = ROOT.TFile(infile, 'read')

    ## get the binned correlated efficiency systematic
    pdgId = 13 if flav=='mu' else 11 
    syst_tnp = utilities.getExclusiveBinnedSyst(utilities.getEffSyst(pdgId))

    elel1tf = ROOT.TFile.Open("/afs/cern.ch/work/e/emanuele/wmass/heppy/CMSSW_8_0_25/src/CMGTools/WMass/python/postprocessing/data/leptonSF/new2016_madeSummer2018/l1EG_eff.root")
    l1hist = elel1tf.Get("l1EG_eff")

    outfile = ROOT.TFile(indir+'/{doType}EffSyst_{flav}.root'.format(doType=doType,flav=flav), 'recreate')

    ndone = 0
    for k in tmp_infile.GetListOfKeys():
        tmp_name = k.GetName()
        ## don't reweight any histos that don't match the regexp
        if not re.match(regexp, tmp_name): continue
        ## don't reweight any histos that are already variations of something else
        if 'Up' in tmp_name or 'Down' in tmp_name: continue
        if 'lepeff' in tmp_name: continue
        process = tmp_name.split('_')[1]

        #if ndone: continue
        ndone += 1

        ## now should be left with only the ones we are interested in
        print 'reweighting lepeff syst of type ', doType,' nuisances for process', tmp_name
        
        tmp_nominal = tmp_infile.Get(tmp_name)
        tmp_nominal_2d = dressed2D(tmp_nominal,binning, tmp_name+'backrolled')

        if doType=='TnP':
            etabins = [0,1,1.5,2.4] if isMu else [0.,1.,1.479,2.,2.5]
        elif doType=='L1PrefireEle':
            etabins = [-2.5,  -2.35, -2.2, -2.0, -1.5, 1.5, 2.0, 2.2, 2.35, 2.5]
            if not isHelicity:
                # 2D xsec has a different and coarser binning
                # btw, for now this function is only used for L1 prefire when doing 2D xsec
                # the rest is done in mergeRootComponentsDiffXsec.py 
                # should need also to account for L1 prefire changing a lot vs eta at high eta,
                # but uncertainty is flatter, so one can just get the xsec bin centers and look a the L1 bin
                etabins = [-2.4, -2.1, -1.9, -1.5, 1.5, 1.9, 2.1, 2.4]
        else:
            print "Error in putEffSystHistos(). Unknown value for doType argument. Abort"
            quit()

        ## make 1 uncorrelated nuisance per syst bin
        nsyst=0
        for isyst in range(len(etabins)-1):
            ## for the L1 prefire, do not add a systematic for the barrel
            if doType=='L1PrefireEle' and isyst==len(etabins)/2-1: continue

            outname_2d = tmp_nominal_2d.GetName().replace('backrolled','')+'_{p}EffSyst{eta}{flav}2DROLLED'.format(p=doType,eta=nsyst,flav=flav)                

            tmp_scaledHisto_up = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Up'))
            tmp_scaledHisto_dn = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Down'))
            
            etasyst_loweredge = etabins[isyst]
            etasyst_upperedge = etabins[isyst+1]
            etasyst = 0.5*(etasyst_loweredge+etasyst_upperedge)

            ## loop over all eta bins of the 2d histogram
            for ieta in range(1,tmp_nominal_2d.GetNbinsX()+1):
                eta = tmp_nominal_2d.GetXaxis().GetBinCenter(ieta)
                ## loop over all pT bins in that bin of eta (which is ieta)
                for ipt in range(1,tmp_scaledHisto_up.GetNbinsY()+1):
                    scaling = 0
                    ## TnP are on absEta, L1PrefireEle depend on the endcap side
                    #if (doType=='TnP' and etasyst_loweredge<=abs(eta)) or (doType=='L1PrefireEle' and etasyst_loweredge<=eta<etasyst_upperedge):
                    ybincenter = tmp_scaledHisto_up.GetYaxis().GetBinCenter(ipt)
                    if doType=='L1PrefireEle' and etasyst_loweredge<=eta<etasyst_upperedge:
                        ## now get the content of the variation histogram!
                        # be conservative, use eta with larger absvalue inside bin
                        # for 2D xsec last bin goes from 2.1 to 2.4, but prefire at eta=2.25 << prefire at eta=2.3999!
                        etapass = eta
                        if not isHelicity:
                            if etapass < 0: 
                                # add epsilon to stay inside bin (just in case)
                                etapass = etasyst_loweredge + 0.0001 
                            else: 
                                # subtract epsilon to stay inside bin (just in case)
                                etapass = etasyst_upperedge - 0.0001
                        sf,scaling = utilities.getL1SF(ybincenter,etapass,l1hist)
                        ## scale Z->electrons by sqrt(2) due to the second electron (assumes 100% correlation in eta, which is not fully true, attempt before reweighting by gen eta)
                        if process=='Z':
                            scaling *= math.sqrt(2)
                    elif doType=='TnP' and etasyst_loweredge<=abs(eta): 
                    #elif doType=='TnP' and ((etasyst<0 and eta<etasyst_upperedge) or (etasyst>0 and eta>etasyst_loweredge)):
                        scaling = syst_tnp.GetBinContent(syst_tnp.GetXaxis().FindFixBin(abs(eta)))
                    ## scale up and down with what we got from the histo
                    tmp_bincontent = tmp_scaledHisto_up.GetBinContent(ieta, ipt)
                    tmp_bincontent_up = tmp_bincontent*(1.+scaling)
                    tmp_bincontent_dn = tmp_bincontent*(1.-scaling)
                    tmp_scaledHisto_up.SetBinContent(ieta, ipt, tmp_bincontent_up)
                    tmp_scaledHisto_dn.SetBinContent(ieta, ipt, tmp_bincontent_dn)
     
            ## re-roll the 2D to a 1D histo
            tmp_scaledHisto_up_1d = unroll2Dto1D(tmp_scaledHisto_up, newname=tmp_scaledHisto_up.GetName().replace('2DROLLED',''), silent=silentCrop)
            tmp_scaledHisto_dn_1d = unroll2Dto1D(tmp_scaledHisto_dn, newname=tmp_scaledHisto_dn.GetName().replace('2DROLLED',''), silent=silentCrop)

            outfile.cd()
            tmp_scaledHisto_up_1d.Write()
            tmp_scaledHisto_dn_1d.Write()
            nsyst += 1
    outfile.Close()
    print 'done with the many reweightings for the correlated effsyst'

def addZOutOfAccPrefireSyst(infile,outdir=None):
    tmp_infile = ROOT.TFile(infile, 'read')

    tf    = ROOT.TFile.Open("/afs/cern.ch/work/e/emanuele/wmass/heppy/CMSSW_8_0_25/src/CMGTools/WMass/python/postprocessing/data/leptonSF/new2016_madeSummer2018/OutOfAcceptancePrefireDYUnc.root")
    histo = tf.Get("ZOutAccPrefireUnc")

    indir = outdir if outdir != None else options.inputdir
    outfile = ROOT.TFile(indir+'/ZOutOfAccPrefireSyst_el.root', 'recreate')

    # get eta-pt binning for reco 
    etaPtBinningVec = getDiffXsecBinning(indir+'/binningPtEta.txt', "reco")  # this get two vectors with eta and pt binning
    recoBins = templateBinning(etaPtBinningVec[0],etaPtBinningVec[1])        # this create a class to manage the binnings
    binning = [recoBins.Neta, recoBins.etaBins, recoBins.Npt, recoBins.ptBins]

    tmp_name = 'x_Z'
    tmp_nominal = tmp_infile.Get(tmp_name)
    tmp_nominal_2d = dressed2D(tmp_nominal,binning, tmp_name+'backrolled')

    for iside,sign in enumerate([-1,1]):
        outname_2d = tmp_nominal_2d.GetName().replace('backrolled','')+'_OutOfAccPrefireSyst{i}el2DROLLED'.format(i=iside)
        tmp_scaledHisto_up = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Up'))
        tmp_scaledHisto_dn = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Down'))

        ## loop over all eta bins of the 2d histogram
        for ieta in range(1,tmp_nominal_2d.GetNbinsX()+1):
            eta = tmp_nominal_2d.GetXaxis().GetBinCenter(ieta)
            ## loop over all pT bins in that bin of eta (which is ieta)
            for ipt in range(1,tmp_scaledHisto_up.GetNbinsY()+1):
                pt = tmp_nominal_2d.GetYaxis().GetBinCenter(ipt)
                scaling = 0
                if eta*sign>0:
                    scaling = histo.GetBinContent(histo.GetXaxis().FindFixBin(eta),histo.GetYaxis().FindFixBin(pt))
                ## scale up and down with what we got from the histo
                tmp_bincontent = tmp_scaledHisto_up.GetBinContent(ieta, ipt)
                tmp_bincontent_up = tmp_bincontent*(1.+scaling)
                tmp_bincontent_dn = tmp_bincontent*(1.-scaling)
                tmp_scaledHisto_up.SetBinContent(ieta, ipt, tmp_bincontent_up)
                tmp_scaledHisto_dn.SetBinContent(ieta, ipt, tmp_bincontent_dn)

        ## re-roll the 2D to a 1D histo
        tmp_scaledHisto_up_1d = unroll2Dto1D(tmp_scaledHisto_up, newname=tmp_scaledHisto_up.GetName().replace('2DROLLED',''))
        tmp_scaledHisto_dn_1d = unroll2Dto1D(tmp_scaledHisto_dn, newname=tmp_scaledHisto_dn.GetName().replace('2DROLLED',''))

        outfile.cd()
        tmp_scaledHisto_up_1d.Write()
        tmp_scaledHisto_dn_1d.Write()
    outfile.Close()
    print 'done with the reweighting for the Z OutOfAcc prefire syst'


def addSmoothFSRSyst(infile,regexp,charge,outdir=None,isMu=True,debug=False):
    indir = outdir if outdir != None else options.inputdir
    flav = 'mu' if isMu else 'el'

    # get eta-pt binning for reco 
    etaPtBinningVec = getDiffXsecBinning(indir+'/binningPtEta.txt', "reco")  # this get two vectors with eta and pt binning
    recoBins = templateBinning(etaPtBinningVec[0],etaPtBinningVec[1])        # this create a class to manage the binnings
    binning = [recoBins.Neta, recoBins.etaBins, recoBins.Npt, recoBins.ptBins]

    tmp_infile = ROOT.TFile(infile, 'read')
    outfile = ROOT.TFile(indir+'/SmoothFSRSyst_{flav}_{ch}.root'.format(flav=flav,ch=charge), 'recreate')
    
    for k in tmp_infile.GetListOfKeys():
        tmp_name = k.GetName()
        ## don't reweight any histos that don't match the regexp
        if not re.match(regexp, tmp_name): continue
        ## don't reweight any histos that are already variations of something else
        if 'Up' in tmp_name or 'Down' in tmp_name: continue
        process = tmp_name.split('_')[1]

        ## now should be left with only the ones we are interested in
        print 'smoothing FSR syst for process', tmp_name
        
        tmp_nominal = tmp_infile.Get(tmp_name)
        tmp_nominal_2d = dressed2D(tmp_nominal,binning, tmp_name+'backrolled')

        n_ptbins  = tmp_nominal_2d.GetNbinsY()
        n_etabins = tmp_nominal_2d.GetNbinsX()

        tmp_nominal_projPt = tmp_nominal_2d.ProjectionY(tmp_name+'_projPt',1,n_etabins,'e')

        tmp_nominal_up = tmp_infile.Get(tmp_name+'_fsrUp')
        tmp_nominal_up_2d = dressed2D(tmp_nominal_up,binning, tmp_nominal_up.GetName()+'backrolled')
        tmp_nominal_up_projPt = tmp_nominal_up_2d.ProjectionY(tmp_nominal_up.GetName()+'_projPt',1,n_etabins,'e')
        
        tmp_nominal_dn = tmp_infile.Get(tmp_name+'_fsrDown')
        tmp_nominal_dn_2d = dressed2D(tmp_nominal_dn,binning, tmp_nominal_dn.GetName()+'backrolled')
        tmp_nominal_dn_projPt = tmp_nominal_dn_2d.ProjectionY(tmp_nominal_dn.GetName()+'_projPt',1,n_etabins,'e')

        tmp_nominal_up_projPt.Divide(tmp_nominal_projPt)
        tmp_nominal_dn_projPt.Divide(tmp_nominal_projPt)

        if debug:
            c = ROOT.TCanvas('cfit','',600,600)
            tmp_nominal_up_projPt.SetLineColor(ROOT.kRed)
            tmp_nominal_dn_projPt.SetLineColor(ROOT.kBlue)
            tmp_nominal_up_projPt.Draw()
            tmp_nominal_dn_projPt.Draw("same")

        fitopt = 'S' if debug else 'SQ'
        fr_up = tmp_nominal_up_projPt.Fit('pol1',fitopt)
        pars_up = [fr_up.Parameter(i) for i in range(2)]

        fr_dn = tmp_nominal_dn_projPt.Fit('pol1',fitopt)
        pars_dn = [fr_dn.Parameter(i) for i in range(2)]

        if debug:
            c.SaveAs("fsr_syst_proj_%s.png" % tmp_name)

        ## create the new syst histogram with the pol1 results
        outname_2d = tmp_nominal_2d.GetName().replace('backrolled','')+'_smoothfsr'+flav
        tmp_scaledHisto_up = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Up'))
        tmp_scaledHisto_dn = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d+'Down'))

        ## loop over all eta bins of the 2d histogram 
        for ieta in range(1,n_etabins+1):
            for ipt in range(1,n_ptbins+1):
                pt = tmp_nominal_2d.GetYaxis().GetBinCenter(ipt)
                smooth_syst_up = pars_up[0] + pars_up[1]*pt
                smooth_syst_dn = pars_dn[0] + pars_dn[1]*pt
                tmp_scaledHisto_up.SetBinContent(ieta, ipt, tmp_nominal_2d.GetBinContent(ieta,ipt)*smooth_syst_up)
                tmp_scaledHisto_dn.SetBinContent(ieta, ipt, tmp_nominal_2d.GetBinContent(ieta,ipt)*smooth_syst_dn)

        ## re-roll the 2D to a 1D histo
        tmp_scaledHisto_up_1d = unroll2Dto1D(tmp_scaledHisto_up, newname=tmp_scaledHisto_up.GetName().replace('2DROLLED',''))
        tmp_scaledHisto_dn_1d = unroll2Dto1D(tmp_scaledHisto_dn, newname=tmp_scaledHisto_dn.GetName().replace('2DROLLED',''))

        outfile.cd()
        tmp_scaledHisto_up_1d.Write()
        tmp_scaledHisto_dn_1d.Write()
    outfile.Close()
    print 'done with the smoothing for the FSR systematic'


def addSmoothLeptonScaleSyst(infile,regexp,charge,isMu,alternateShapeOnly=False,outdir=None):

    indir = outdir if outdir != None else options.inputdir
    flav = 'mu' if isMu else 'el'

    # get eta-pt binning for reco 
    etaPtBinningVec = getDiffXsecBinning(indir+'/binningPtEta.txt', "reco")  # this get two vectors with eta and pt binning
    recoBins = templateBinning(etaPtBinningVec[0],etaPtBinningVec[1])        # this create a class to manage the binnings
    binning = [recoBins.Neta, recoBins.etaBins, recoBins.Npt, recoBins.ptBins]

    tmp_infile = ROOT.TFile(infile, 'read')
    outfile = ROOT.TFile(indir+'/SmoothScaleSyst_{flav}_{ch}.root'.format(flav=flav,ch=charge), 'recreate')

    dirWithInputSyst = '/afs/cern.ch/work/e/emanuele/wmass/heppy/CMSSW_8_0_25/src/CMGTools/WMass/python/postprocessing/data/leptonScale'
    muscale_syst_f = ROOT.TFile.Open(dirWithInputSyst+'/mu/muscales.root') if isMu else ROOT.TFile.Open(dirWithInputSyst+'/el/elscales_extended.root')
    ## use one histogram to map the binning -> array
    binning_histo = muscale_syst_f.Get('stathis_eig_plus_0')
    ## convert histograms to arrays to get it faster
    maxstats = 99 if isMu else 97
    systrange = [2,5] if isMu else [0,1]
    stathists = [root_numpy.hist2array(muscale_syst_f.Get('stathis_eig_{ch}_{istat}'.format(ch=charge,istat=idx))) for idx in range(maxstats)]
    systhists = [root_numpy.hist2array(muscale_syst_f.Get('systhist_{ch}_{isyst}'.format(ch=charge,isyst=idx))) for idx in range(systrange[0],systrange[1]+1)]

    ## stat error from re-generated stat. replicas (diagonalized) 
    ## then 4 systematic uncertainties fully correlated in the eta/pt plane
    ## for muons, keep the original rochester corr naming Syst2-Syst6
    offset = 2 if isMu else 0
    allsysts = ['Stat{idx}'.format(idx=i) for i in range(len(stathists))] + ['Syst{idx}'.format(idx=i+offset) for i in range(len(systhists))]
    allhists = stathists + systhists
    systsAndHists = zip(allsysts,allhists)

    for k in tmp_infile.GetListOfKeys():
        tmp_name = k.GetName()
        ## don't reweight any histos that don't match the regexp
        if not re.match(regexp, tmp_name): continue
        ## don't reweight any histos that are already variations of something else
        if 'Up' in tmp_name or 'Down' in tmp_name: continue
        process = tmp_name.split('_')[1]

        ## now should be left with only the ones we are interested in
        print 'reweighting ',flav,' scale syst of type for process', tmp_name
        
        tmp_nominal = tmp_infile.Get(tmp_name)
        tmp_nominal_2d = dressed2D(tmp_nominal,binning, tmp_name+'backrolled')
        n_ptbins = tmp_nominal_2d.GetNbinsY()


        for syst,hist in systsAndHists:
            if re.match('Syst',syst):
                syst_ptbins = [('',0,1000)] if isMu else [('pt0',0,42),('pt1',42,1000)]
                if isMu:
                    syst_etabins = [('eta0',-2.4,-2.1),('eta1',-2.1,0),('eta2',0,2.1),('eta3',2.1,2.4)] 
                else:
                    syst_etabins = [('eta0',-2.5,-2.1),('eta1',-2.1,-1.5),('eta2',-1.5,-1),('eta3',-1,0),('eta4',0,1),('eta5',1,1.5),('eta6',1.5,2.1),('eta7',2.1,2.5)]
            else:
                syst_ptbins = [('',0,1000)]
                syst_etabins = [('',0,10)]
            for systipt in syst_ptbins:
                for systieta in syst_etabins:
                    for shift_dir in ['Up','Down']:
                        # only syst3 for muons encodes the correlations by charge, looking at the input maps 
                        chargesyst = '' if ((isMu and syst=='Syst3') or re.match('Stat',syst)) else charge
                        outname_2d = tmp_nominal_2d.GetName().replace('backrolled','')+'_smooth{lep}scale{idx}{systieta}{systipt}{ch}{shiftdir}'.format(lep=flav,idx=syst,systieta=systieta[0],systipt=systipt[0],ch=chargesyst,shiftdir=shift_dir)
                        tmp_scaledHisto = copy.deepcopy(tmp_nominal_2d.Clone(outname_2d))
         
                        ## loop over all eta bins of the 2d histogram 
                        for ieta in range(1,tmp_nominal_2d.GetNbinsX()+1):
                            eta = tmp_nominal_2d.GetXaxis().GetBinCenter(ieta)
                            for ipt in range(2,tmp_nominal_2d.GetNbinsY()+1):
                                pt      = tmp_nominal_2d.GetYaxis().GetBinCenter(ipt)
                                if (systipt[1]<= pt < systipt[2]) and (systieta[1]<= eta < systieta[2]):
                                    ## assume uniform distribution within a bin
                                    etabin = max(1, min(binning_histo.GetNbinsX(), binning_histo.GetXaxis().FindFixBin(eta)))
                                    ptbin  = max(1, min(binning_histo.GetNbinsY(), binning_histo.GetYaxis().FindFixBin(pt)))
             
                                    pt_prev = tmp_nominal_2d.GetYaxis().GetBinCenter(ipt-1)
                                    nominal_val      = tmp_nominal_2d.GetBinContent(ieta,ipt)
                                    nominal_val_prev = tmp_nominal_2d.GetBinContent(ieta,ipt-1)
                                    pt_width      = tmp_nominal_2d.GetYaxis().GetBinWidth(ipt)
                                    pt_width_prev = tmp_nominal_2d.GetYaxis().GetBinWidth(ipt-1)
                 
                                    if isMu: scale_syst = 1-utilities.getRochesterUncertainty(charge,etabin-1,ptbin-1,hist,syst!='Syst3')
                                    else:    scale_syst = 1-utilities.getRochesterUncertainty(charge,etabin-1,ptbin-1,hist,False)
                                    if shift_dir=='Down': scale_syst = -1*scale_syst
             
                                    from_prev = scale_syst * pt_prev / pt_width_prev * max(0,nominal_val_prev)
                                    to_right  = scale_syst * pt      / pt_width      * max(0,nominal_val)
             
                                    tmp_scaledHisto.SetBinContent(ieta,ipt,max(0,nominal_val + from_prev - to_right))
                            ## since in the first bin we cannot foresee 2-neighbors migrations, let's assume same syst of bin i+1
                            tmp_scaledHisto.SetBinContent(ieta,1,tmp_scaledHisto.GetBinContent(ieta,2)/tmp_nominal_2d.GetBinContent(ieta,2)*tmp_nominal_2d.GetBinContent(ieta,1) if tmp_nominal_2d.GetBinContent(ieta,2) else 0)
                        ## re-roll the 2D to a 1D histo
                        tmp_scaledHisto_1d = unroll2Dto1D(tmp_scaledHisto, newname=tmp_scaledHisto.GetName().replace('2DROLLED',''))
                        if alternateShapeOnly:
                            tmp_scaledHisto_1d.Scale(tmp_nominal.Integral()/tmp_scaledHisto_1d.Integral())
                        cropHighSysts(tmp_nominal,tmp_scaledHisto_1d,maxSyst=0.05)                
                        outfile.cd()
                        tmp_scaledHisto_1d.Write()
    outfile.Close()
    print "done with the smooth ",flav," scale variations"


def writeChargeGroup(cardfile,signals,polarizations):
    maxiY = max([int(proc.split('_')[-1]) for proc in signals])
    for pol in polarizations:
        cardfile.write('\n')
        for y in xrange(maxiY+1):
            cardfile.write('W_{pol}_Ybin_{y} chargeGroup = Wplus_{pol}_Ybin_{y} Wminus_{pol}_Ybin_{y}\n'.format(pol=pol,y=y))

def writePolGroup(cardfile,signals,polarizations,grouping='polGroup'):
    maxiY = max([int(proc.split('_')[-1]) for proc in signals])
    for charge in ['plus','minus']:
        cardfile.write('\n')
        for y in xrange(maxiY+1):
            group = ' '.join(['W{charge}_{pol}_Ybin_{y}'.format(charge=charge,pol=pol,y=y) for pol in polarizations])
            cardfile.write('W{charge}_Ybin_{y} {grp} = {procs}\n'. format(charge=charge,y=y,grp=grouping,procs=group))

def writeRegGroup(cardfile,signals,polarizations,grouping='regGroup',bkgYBins=[]):
    print 'WRITING REGULARIZATION GROUPS!!!'
    maxiY = max([int(proc.split('_')[-1]) for proc in signals])
    for pol in polarizations:
        for charge in ['plus','minus']:
            cardfile.write('\n')
            slist = ''
            for i in xrange(maxiY+1):
                if i not in bkgYBins: 
                    slist += ' W{charge}_{pol}_Ybin_{i} '.format(charge=charge,pol=pol,i=i)
            cardfile.write('reg_W{charge}_{pol} {grp} = {procs}\n'. format(charge=charge,pol=pol,grp=grouping,procs=slist))

def writeChargeMetaGroup(cardfile,signals):
     maxiY = max([int(proc.split('_')[-1]) for proc in signals])
     cardfile.write('\n')
     for y in xrange(maxiY+1):
          cardfile.write('W_Ybin_{y} chargeMetaGroup = Wplus_Ybin_{y} Wminus_Ybin_{y}\n'.format(y=y))

# trick to store the longitudinal W postfit in the output tree
def writeLongGroup(cardfile,signals):
    maxiY = max([int(proc.split('_')[-1]) for proc in signals])
    for charge in ['plus','minus']:
        cardfile.write('\n')
        for y in xrange(maxiY+1):
            cardfile.write('W{charge}_long_Ybin_{y} sumGroup = W{charge}_long_Ybin_{y}\n'. format(charge=charge,y=y))

def cleanProcessName(name):
    tokens = name.split('_')
    uniquet = reduce(lambda l, x: l+[x] if x not in l else l, tokens, [])
    cleanName = '_'.join([t for t in uniquet if (t!='el' and t!='mu')])
    return cleanName

def writeXSecFile(outfile,tmp_sigprocs,theosyst,ybins,options,nominal):
    ## xsecfilname 
    lumiScale = 36000. if options.xsecMaskedYields else 36.0/35.9 # x-sec file done with 36. fb-1
    dirtheo = '/afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/CMSSW_8_0_25/src/CMGTools/WMass/data/theory/'
    theory_xsecs_file =  dirtheo+'/theory_cross_sections.root' if nominal else dirtheo+'/theory_cross_sections_2D_noWpTReweighting.root'
    hists = getXsecs(tmp_sigprocs, 
                     [i for i in theosyst.keys()],
                     ybins, 
                     lumiScale, 
                     theory_xsecs_file
                    )
    tmp_xsec_histfile_name = os.path.abspath(outfile.replace('_shapes','_shapes_xsec'))
    if not nominal: tmp_xsec_histfile_name = tmp_xsec_histfile_name.replace('_shapes_xsec','_shapes_xsec_baremc')
    tmp_xsec_hists = ROOT.TFile(tmp_xsec_histfile_name, 'recreate')
    for hist in hists:
        hist.Write()
    tmp_xsec_hists.Close()
    return tmp_xsec_histfile_name

W_MCANLO_over_DATA_fromZ = 0.958

if __name__ == "__main__":
    

    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] cards/card*.txt')
    parser.add_option('-m','--merge-root', dest='mergeRoot', default=False, action='store_true', help='Merge the root files with the inputs also')
    parser.add_option('-i','--input', dest='inputdir', default='', type='string', help='input directory with all the cards inside')
    parser.add_option('-b','--bin', dest='bin', default='ch1', type='string', help='name of the bin')
    parser.add_option('-C','--charge', dest='charge', default='plus,minus', type='string', help='process given charge. default is both')
    parser.add_option(     '--ybinsOutAcc', dest='ybinsOutAcc', type='string', default="", help='Define which Y bins are out-of-acceptance. With format 14,15 ')
    parser.add_option(     '--ybinsBkg', dest='ybinsBkg', type='string', default="10,11", help='Define which Y bins are to be considered as background. With format 14,15 ')
    parser.add_option(     '--ybinsBkgLnN', dest='ybinsBkgLnN', type='float', default=1.3, help='add a common lnN constraint to all the L,R components treated as bkg.')
    parser.add_option(     '--longSig'    , dest='longSig', default=False, action='store_true', help='Treat all bins for long as signal.')
    parser.add_option('-p','--POIs', dest='POIsToMinos', type='string', default=None, help='Decide which are the nuiscances for which to run MINOS (a.k.a. POIs). Default is all non fixed YBins. With format poi1,poi2 ')
    parser.add_option('--fp', '--freezePOIs'    , dest='freezePOIs'    , action='store_true'               , help='run tensorflow with --freezePOIs (for the pdf only fit)');
    parser.add_option(        '--long-lnN', dest='longLnN', type='float', default=1.3, help='add a common lnN constraint to all longitudinal components. It de-activates --longSig')
    parser.add_option(     '--sf'    , dest='scaleFile'    , default='', type='string', help='path of file with the scaling/unfolding')
    parser.add_option(     '--xsecMaskedYields', dest='xsecMaskedYields', default=False, action='store_true', help='use the xsec in the masked channel, not the expected yield')
    parser.add_option(     '--pdf-shape-only'   , dest='pdfShapeOnly' , default=False, action='store_true', help='Normalize the mirroring of the pdfs to central rate.')
    parser.add_option('-M','--minimizer'   , dest='minimizer' , type='string', default='GSLMultiMinMod', help='Minimizer to be used for the fit')
    parser.add_option(     '--comb'   , dest='combineCharges' , default=False, action='store_true', help='Combine W+ and W-, if single cards are done')
    parser.add_option('-s', '--sparse', dest='sparse' ,default=False, action='store_true',  help="Store normalization and systematics arrays as sparse tensors. It enables the homonymous option of text2hdf5.py")
    parser.add_option(      '--override-jetPt-syst', dest='overrideJetPtSyst' ,default=True, action='store_true',  help="If True, it rebuilds the Down variation for the jet pt syst on fake-rate using the mirrorShape() function defined here, which is different from the one in makeShapeCards.py")
    parser.add_option(       '--uncorrelate-fakes-by-charge', dest='uncorrelateFakesByCharge' , default=False, action='store_true', help='If True, nuisances for fakes are uncorrelated between charges (Eta, PtSlope, PtNorm)')
    parser.add_option(       '--exclude-nuisances', dest='excludeNuisances', default="", type="string", help="Pass comma-separated list of regular expressions to exclude some systematics")
    parser.add_option(       '--postfix',    dest='postfix', type="string", default="", help="Postfix for .hdf5 file created with text2hdf5.py when combining charges");
    parser.add_option(       '--no-text2hdf5'  , dest='skip_text2hdf5', default=False, action='store_true', help='when combining charges, skip running text2hdf5.py at the end')
    parser.add_option(       '--rescaleWBackToMCaNLO'   , dest='rescaleWBackToMCaNLO', default=False, action='store_true', help='Rescale the W process back to pure MC@NLO. NOT TO BE USED IF THE RESCALING WAS DONE AT THE WPT REWEIGHTING LEVEL ! ')
    (options, args) = parser.parse_args()
    
    if options.combineCharges:
        combCharges(options)
        sys.exit()

    from symmetrizeMatrixAbsY import getScales
    
    charges = options.charge.split(',')
    channel = 'mu' if 'mu' in options.bin else 'el'
    
    ## look for the maximum ybin bin number in each charge/helicity state
    binningFile = open(options.inputdir+'/binningYW.txt')
    binningYW = eval(binningFile.read())
    nbins = {}
    for i,j in binningYW.items():
        nbins[i] = len(j)-1

    print ""
    fixedYBins = []
    if options.ybinsOutAcc:
        fixedYBins = list(int(i) for i in options.ybinsOutAcc.split(','))
    print '---------------------------------'
    print 'I WILL MAKE THESE BINS OUT OF ACCEPTANCE IN THE FIT:'
    print fixedYBins
    print '---------------------------------'

    bkgYBins = []
    if options.ybinsBkg != '':
        bkgYBins = list(int(i) for i in options.ybinsBkg.split(','))
    print 'I WILL TREAT THESE BINS AS BACKGROUND IN THE FIT FOR ALL POLARIZATIONS:'
    print bkgYBins
    print '---------------------------------'
    
    if options.longLnN: options.longSig = False

    if options.longSig:
        print 'I WILL TREAT ALL BINS FOR LONGITUDINAL POLARIZATION AS SIGNAL'
        print '---------------------------------'

    if options.rescaleWBackToMCaNLO:
        print 'I WILL RESCALE THE W AND WTAU OF A FACTOR ',W_MCANLO_over_DATA_fromZ,'. THIS ASSUMES YOU HAVE NOT RESCALED IT IN THE REWEIGHTING IN THE DC MAKING PROCESS !'
        print '---------------------------------'

    excludeNuisances = []
    if len(options.excludeNuisances):
        excludeNuisances = options.excludeNuisances.split(",")
    excludeNuisances.append("CMS.*sig_lepeff")
    excludeNuisances.append("CMS.*_(ele|mu)scale\d")
    excludeNuisances.append("fsr")

    for charge in charges:
    
        outfile  = os.path.join(options.inputdir,options.bin+'_{ch}_shapes.root'.format(ch=charge))
        cardfile = os.path.join(options.inputdir,options.bin+'_{ch}_card.txt'   .format(ch=charge))

        ## marc putUncorrelatedFakes(outfile+'.noErfPar', 'x_data_fakes', charge, isMu= 'mu' in options.bin)
        ## marc putUncorrelatedFakes(outfile+'.noErfPar', 'x_data_fakes', charge, isMu= 'mu' in options.bin, doType = 'ptslope')
        ## marc putUncorrelatedFakes(outfile+'.noErfPar', 'x_data_fakes', charge, isMu= 'mu' in options.bin, doType = 'ptnorm' )
        ## marc sys.exit()
    
        ## prepare the relevant files. only the datacards and the correct charge
        allfiles = [os.path.join(dp, f) for dp, dn, fn in os.walk(options.inputdir,followlinks=True) for f in fn if (f.endswith('.card.txt') or f.endswith('.input.root'))]
        files = [f for f in allfiles if charge in f and not re.match('.*_pdf.*|.*muR.*|.*muF.*|.*alphaS.*|.*wptSlope.*|.*mW.*|.*ErfPar\dEffStat.*|.*_fsr.*',f) and f.endswith('.card.txt')]
        files = sorted(files, key = lambda x: int(x.rstrip('.card.txt').split('_')[-1]) if not any(bkg in x for bkg in ['bkg','Z_','TauDecaysW_']) else -1) ## ugly but works
    
        existing_bins = {'left': [], 'right': [], 'long': []}
        empty_bins = {'left': [], 'right': [], 'long': []}
    
        ybins = {}
        for pol in ['left','right','long']:
            cp = '{ch}_{pol}'.format(ch=charge,pol=pol)
            ybins[pol] = binningYW[cp]

            ## for b in xrange(len(ybins[pol])-1):
            ##     if b not in existing_bins[pol]:
            ##         if b not in empty_bins[pol]:
            ##             empty_bins[pol].append(b)
            ##             empty_bins[pol].append(nbins[cp]+1-b)

        longBKG = False
        tmpfiles = []
        for ifile,f in enumerate(files):
            basename = os.path.basename(f).split('.')[0]
            if basename.startswith('W{charge}'.format(charge=charge)): pol=basename.split('_')[1]
            else: pol='none' # bkg and data
            dir = os.path.dirname(f)
            bin = ''
            isEmpty = False
            with open(f) as file:
                for l in file.readlines():
                    if re.match('shapes.*',l):
                        rootfile = dir+'/'+l.split()[3]
                    if re.match('bin.*',l):
                        if len(l.split()) < 2: continue ## skip the second bin line if empty
                        bin = l.split()[1]
                        binn = int(bin.split('_')[-1]) if 'Ybin_' in bin else -1
                    rootfiles_syst = filter(lambda x: re.match('\S+{base}_sig_(pdf\d+|(long|left|right)muR\S+|(long|left|right)muF\S+|alphaS\S+|mW\S+|fsr)\.input\.root'.format(base=basename),x), allfiles)
                    if 'Z_' in f:
                        rootfiles_syst += filter(lambda x: re.match('\S+Z_{channel}_{charge}_dy_(pdf\d+|muR\S+|muF\S+|alphaS\S+)\.input\.root'.format(channel=channel,charge=charge),x), allfiles)
                    if 'TauDecaysW_' in f:
                        rootfiles_syst += filter(lambda x: re.match('\S+TauDecaysW_{channel}_{charge}_wtau_(pdf\d+|muR\S+|muF\S+|alphaS\S+)\.input\.root'.format(channel=channel,charge=charge),x), allfiles)
                    rootfiles_syst.sort()
                    if re.match('process\s+',l): 
                        if len(l.split()) > 1 and all(n.isdigit() for n in l.split()[1:]) : continue
                        if not pol in l:
                            if pol!='none' and binn not in empty_bins[pol]: 
                                if binn >= 0:
                                    empty_bins[pol].append(binn)
                                    empty_bins[pol].append(nbins[charge+'_'+pol]-binn)
                            isEmpty = True
                        processes = l.split()[1:]
                    if re.match('process\s+W.*long',l) and 'bkg' in f:
                        print "===> W long is treated as a background"
                        longBKG = True
            if options.mergeRoot:
                if pol=='none' or binn not in empty_bins[pol]:
                    print 'processing bin: {bin} for polarization: {pol}'.format(bin=bin,pol=pol)
                    nominals = {}
                    for irf,rf in enumerate([rootfile]+rootfiles_syst):
                        print '\twith nominal/systematic file: ',rf
                        tf = ROOT.TFile.Open(rf)
                        tmpfile = os.path.join(options.inputdir,'tmp_{pol}_{bin}_sys{sys}.root'.format(pol=pol,bin=bin,sys=irf))
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
                                    newprocname = p+'_'+bin if re.match('Wplus|Wminus',p) else p  # WARNING: the if else only affects "bin", not "p+'_'+bin"
                                    if longBKG and re.match('(Wplus_long|Wminus_long)',p): newprocname = p
                                    newname = name.replace(p,newprocname)
                                    newprocname = cleanProcessName(newprocname); newname = cleanProcessName(newname)
                                    ## ignore muscale systematics from the files.. hopefully.
                                    if any(musyst in newname for musyst in ['muscale0', 'muscale1', 'elescale']):
                                        continue
                                    if re.match('x_(Wplus|Wminus|TauDecaysW)_.*',newname) and options.rescaleWBackToMCaNLO:
                                        obj.Scale(W_MCANLO_over_DATA_fromZ)
                                    ### fix for a misnaming of the decorrelated QCD scales by charge. All have minus
                                    if re.match('x_Wplus_.*minus(Up|Dn)',newname):
                                        newname = newname.replace('minusDn','plusDn').replace('minusUp','plusUp')
                                    if irf==0:
                                        if newname not in plots:
                                            ############### special case to fix jet pt syst on FR
                                            if options.overrideJetPtSyst and 'data_fakes' in newname and 'awayJetPt' in newname:                                        
                                                if 'Down' in newname:
                                                    print "Skipping %s " % newname
                                                    print "Will be recreated mirroring the Up component here"
                                                    continue
                                                pfx = 'x_data_fakes'
                                                newname = newname[:-2] # remove Up from name                  
                                                nominalFakes = 0
                                                if pfx in nominals:
                                                    nominalFakes = nominals[pfx]
                                                else:
                                                    nominalFakes = tf.Get(pfx)
                                                    if not nominalFakes: 
                                                        print "Warning: couldn't read %s from file" % pfx
                                                        quit()
                                                (alternate,mirror) = mirrorShape(nominalFakes,obj,newname,alternateShapeOnly=True,use2xNomiIfAltIsZero=True)             
                                                for alt in [alternate,mirror]:
                                                    if alt.GetName() not in plots:
                                                        plots[alt.GetName()] = alt.Clone()
                                                        plots[alt.GetName()].Write()
                                            ############# end of fix for FR syst
                                            else:
                                                plots[newname] = obj.Clone(newname)
                                                nominals[newname] = obj.Clone(newname+"0")
                                                nominals[newname].SetDirectory(None)
                                                #print 'replacing old %s with %s' % (name,newname)
                                                plots[newname].Write()
                                    else:
                                        if any(sysname in newname for sysname in ['pdf','fsr']): # these changes by default shape and normalization. Each variation should be symmetrized wrt nominal
                                            pfx = '_'.join(newname.split("_")[:-2])
                                            if 'pdf' in newname:
                                                patt = re.compile('(pdf)(\d+)')
                                                tokens = patt.findall(newname)
                                                sysname = tokens[0][0]; isys = int(tokens[0][1])
                                                newname = "{pfx}_{sysname}{isys}".format(pfx=pfx,sysname=sysname,isys=isys)
                                                (alternate,mirror) = mirrorShape(nominals[pfx],obj,newname,options.pdfShapeOnly)
                                            else:
                                                tokens = newname.split("_"); pfx = '_'.join(tokens[:-2]); syst = tokens[-1]
                                                newname = "{pfx}_{syst}".format(pfx=pfx,syst=syst)
                                                (alternate,mirror) = mirrorShape(nominals[pfx],obj,newname,alternateShapeOnly=True)
                                            for alt in [alternate,mirror]:
                                                if alt.GetName() not in plots:
                                                    plots[alt.GetName()] = alt.Clone()
                                                    plots[alt.GetName()].Write()
                                        elif re.match('.*muR.*|.*muF.*|.*alphaS.*|.*mW.*',newname): # these changes by default shape and normalization
                                            tokens = newname.split("_"); pfx = '_'.join(tokens[:-2]); syst = tokens[-1].replace('Dn','Down')
                                            newname = "{pfx}_{syst}".format(pfx=pfx,syst=syst)
                                            if newname not in plots:
                                                plots[newname] = obj.Clone(newname)
                                                plots[newname].Write()
                        of.Close()
        if any(len(empty_bins[pol]) for pol in ['left','right']):
            print 'found a bunch of empty bins:', empty_bins

        if options.mergeRoot:
            haddcmd = 'hadd -f {of}.noErfPar {indir}/tmp_*.root'.format(of=outfile, indir=options.inputdir )
            os.system(haddcmd)
            os.system('rm {indir}/tmp_*.root'.format(indir=options.inputdir))

            print 'now putting the erfpar systematics into the file'
            putEffStatHistos(outfile+'.noErfPar', '(.*Wminus.*|.*Wplus.*|.*Z.*|.*TauDecaysW.*)', charge, isMu= 'mu' in options.bin)
            print 'now putting the correlated efficiency systematics into the file'
            putEffSystHistos(outfile+'.noErfPar', '(.*Wminus.*|.*Wplus.*|.*Z.*|.*TauDecaysW.*)', doType='TnP', isMu= 'mu' in options.bin)
            if 'el' in options.bin:
                putEffSystHistos(outfile+'.noErfPar', '(.*Wminus.*|.*Wplus.*|.*Z.*|.*TauDecaysW.*)', doType='L1PrefireEle', isMu=False)
                addZOutOfAccPrefireSyst(outfile+'.noErfPar')
         
            print 'now putting the uncorrelated eta variations for fakes'
            putUncorrelatedFakes(outfile+'.noErfPar', 'x_data_fakes', charge, isMu= 'mu' in options.bin, uncorrelateCharges=options.uncorrelateFakesByCharge)
            putUncorrelatedFakes(outfile+'.noErfPar', 'x_data_fakes', charge, isMu= 'mu' in options.bin, doType = 'ptslope', uncorrelateCharges=options.uncorrelateFakesByCharge)
            putUncorrelatedFakes(outfile+'.noErfPar', 'x_data_fakes', charge, isMu= 'mu' in options.bin, doType = 'ptnorm', uncorrelateCharges=options.uncorrelateFakesByCharge )
            
            if 'mu' in options.bin:
                putUncorrelatedFakes(outfile+'.noErfPar', 'x_data_fakes', charge, isMu=True, doType = 'etacharge', uncorrelateCharges=options.uncorrelateFakesByCharge )
            
            addSmoothLeptonScaleSyst(outfile+'.noErfPar', '(.*Wminus.*|.*Wplus.*|.*Z.*|.*TauDecaysW.*)', charge,isMu= 'mu' in options.bin)
            addSmoothFSRSyst(outfile+'.noErfPar', '(.*Wminus.*|.*Wplus.*)',charge,outdir=None,isMu= 'mu' in options.bin,debug=False)

            final_haddcmd = 'hadd -f {of} {indir}/ErfParEffStat_{flav}_{ch}.root {indir}/*Uncorrelated_{flav}_{ch}.root {indir}/*EffSyst_{flav}.root {indir}/SmoothScaleSyst_{flav}_{ch}.root {indir}/SmoothFSRSyst_{flav}_{ch}.root {of}.noErfPar '.format(of=outfile, ch=charge, indir=options.inputdir, flav=options.bin.replace('W','') )
            if 'el' in options.bin:
                final_haddcmd += options.inputdir + '/ZOutOfAccPrefireSyst_el.root'
            os.system(final_haddcmd)

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
                if re.match('.*_pdf.*|.*_mu(R|F).*|.*_(long|left|right)muR.*|.*_(long|left|right)muF.*|.*alphaS.*|.*mW.*',name):
                    if re.match('.*_muR\d+|.*_muF\d+',name) and name.startswith('x_Z_'): continue # patch: these are the wpT binned systematics that are filled by makeShapeCards but with 0 content
                    if syst not in theosyst: theosyst[syst] = [binWsyst]
                    else: theosyst[syst].append(binWsyst)
                if re.match('.*EffSyst.*|.*ErfPar\dEffStat.*|.*OutOfAccPrefireSyst.*|.*(Fakes|Z|TauDecaysW).*Uncorrelated.*|.*smooth(el|mu)scale\S+|.*smoothfsr.*',name):
                    if syst not in expsyst: expsyst[syst] = [binWsyst]
                    else: expsyst[syst].append(binWsyst)
        if len(theosyst): print "Found a bunch of theoretical shape systematics: ",theosyst.keys()
        else: print "You are running w/o theory systematics. Lucky you!"
        if len(expsyst): print "Found a bunch of experimental shape systematics: ",expsyst.keys()
        allsyst = theosyst.copy()
        allsyst.update(expsyst)
        pdfsyst = {k:v for k,v in theosyst.iteritems() if 'pdf' in k}
        qcdsyst = {k:v for k,v in theosyst.iteritems() if 'muR' in k or 'muF' in k}
        alssyst = {k:v for k,v in theosyst.iteritems() if 'alphaS' in k }
        wmodelsyst = {k:v for k,v in theosyst.iteritems() if 'mW' in k}
        effsyst = {k:v for k,v in expsyst.iteritems() if 'EffStat' in k}
    
        combineCmd="combineCards.py --noDirPrefix "
        for f in files:
            basename = os.path.basename(f).split(".")[0]
            binn = int(basename.split('_')[-1]) if 'Ybin_' in basename else 999
            binname = ''
            if re.match('Wplus|Wminus',basename): binname=basename
            elif re.match('Z.*{charge}'.format(charge=charge),basename): binname='Z'
            elif re.match('TauDecaysW.*{charge}'.format(charge=charge),basename): binname='TauDecaysW'
            else: binname='other'
            if not binn in empty_bins:
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
        with open(tmpcard) as file:    
            nmatchbin=0
            nmatchprocess=0
            for l in file.readlines():
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
                            if 'Wminus' in pseudobins[i] or 'Wplus' in pseudobins[i]:
                                realprocesses.append(pseudobins[i].replace('_el_','_').replace('_mu_','_'))
                            else:
                                realprocesses.append(pseudoprocesses[i])
                        combinedCard.write('bin            %s \n' % ' '.join([kpatt % options.bin for p in pseudoprocesses]))
                        #combinedCard.write('process        %s \n' % ' '.join([kpatt % p for p in realprocesses]))
                        ## marc combinedCard.write('process        %s \n' % ' '.join([kpatt % str(i+1) for i in xrange(len(pseudobins))]))
                        procids = []; procnames = []
                        pos = 1; neg =  0;
                        for i,proc in enumerate(realprocesses):
                            if 'left' in proc or 'right' in proc or ('long' in proc and not options.longLnN):
                                if "long" in proc and not options.longSig:
                                    procnames.append(proc)
                                    procids.append( str(pos)); 
                                    pos += 1
                                else:
                                    thisYbin = get_iy_from_process_name(proc)
                                    if thisYbin in bkgYBins:
                                        procnames.append(proc)
                                        procids.append( str(pos)); pos += 1
                                    else:
                                        procnames.append(proc)
                                        procids.append( str(neg)); neg -= 1
                            else:
                                procnames.append(proc)
                                procids.append( str(pos)); pos += 1
                        processNameLine = 'process        '
                        processIDLine   = 'process        '
                        for i,pid in enumerate(procids):
                            processNameLine += '       '+procnames[i]
                            processIDLine   += '       '+pid
                        processNameLine += ' \n'
                        processIDLine   += ' \n'
                        combinedCard.write(processNameLine)
                        combinedCard.write(processIDLine  )
    
                    nmatchprocess += 1
                if nmatchprocess==2: 
                    nmatchprocess +=1
                elif nmatchprocess>2:                     
                    pieces = [x.rstrip().lstrip() for x in l.split()]
                    if len(pieces) > 1 and any(pieces[1] == x for x in ["shape", "lnN"]) and isExcludedNuisance(excludeNuisances, pieces[0]): 
                        #print pieces[0]
                        pass
                    else:
                        combinedCard.write(l)
        
        os.system('rm {tmpcard}'.format(tmpcard=tmpcard))

        kpatt = " %7s "
        if not options.freezePOIs:
            if options.longLnN:
                for ybin in xrange(len(ybins['long'])-1):
                    longW_proc = 'W{ch}_long_Ybin_{yb}'.format(ch=charge,yb=ybin)
                    combinedCard.write('norm_'+longW_proc+'       lnN    ' + ' '.join([kpatt % (options.longLnN if longW_proc in x else '-') for x in realprocesses])+'\n')
            if options.ybinsBkgLnN:
                for ybfix in bkgYBins:
                    for pol in ['left','right']:
                        lrW_proc = 'W{ch}_{pol}_Ybin_{yb}'.format(ch=charge,pol=pol,yb=ybfix)
                        combinedCard.write('norm_'+lrW_proc+'       lnN    ' + ' '.join([kpatt % (options.ybinsBkgLnN if lrW_proc in x else '-') for x in realprocesses])+'\n')
        # if 'el' in options.bin:
        #     combinedCard.write('norm_fakes       lnN    ' + ' '.join([kpatt % ('1.2' if 'fakes' in x else '-') for x in realprocesses])+'\n')
    
        combinedCard = open(cardfile,'r')
        procs = []
        rates = []
        for l in combinedCard.readlines():
            ##if re.match("process\s+",l) and not re.match("process\s+\d",l): # my regexp qualities are bad... 
            if 'process' in l and 'Ybin' in l:
                procs = (l.rstrip().split())[1:]
            if re.match("rate\s+",l):
                rates = (l.rstrip().split())[1:]
            if len(procs) and len(rates): break
        ProcsAndRates = zip(procs,rates)
        ProcsAndRatesDict = dict(zip(procs,rates))
    
        efficiencies    = {}; efferrors    = {}
        efficiencies_LO = {}; efferrors_LO = {}
        if options.scaleFile:
            for pol in ['left','right']: 
                efficiencies   [pol] = [1./x for x in getScales(ybins[pol], charge, pol, os.path.abspath(options.scaleFile))]
                efferrors      [pol] = [   x for x in getScales(ybins[pol], charge, pol, os.path.abspath(options.scaleFile), returnError=True)] ## these errors are relative to the effs
                efficiencies_LO[pol] = [1./x for x in getScales(ybins[pol], charge, pol, os.path.abspath(options.scaleFile), doNLO=False)]
                efferrors_LO   [pol] = [   x for x in getScales(ybins[pol], charge, pol, os.path.abspath(options.scaleFile), doNLO=False, returnError=True)]
        combinedCard.close()

        combinedCard = open(cardfile,'a')
        POIs = []; fixedPOIs = []; allPOIs = []
        signal_procs = filter(lambda x: re.match('Wplus|Wminus',x), realprocesses)
        if longBKG: signal_procs = filter(lambda x: re.match('(?!Wplus_long|Wminus_long)',x), signal_procs)
        signal_procs.sort(key=lambda x: int(x.split('_')[-1]))
        signal_L = filter(lambda x: re.match('.*left.*',x),signal_procs)
        signal_R = filter(lambda x: re.match('.*right.*',x),signal_procs)
        signal_0 = filter(lambda x: re.match('.*long.*',x),signal_procs)
        
        hel_to_constrain = [signal_L,signal_R]
        tightConstraint = 0.50
        for hel in hel_to_constrain:
            for iy,helbin in enumerate(hel):
                pol = helbin.split('_')[1]
                index_procs = procs.index(helbin)
                if options.scaleFile:
                    lns = ' - '.join('' for i in range(index_procs+1))
                    lns += ' {effunc:.4f} '.format(effunc=1.+efferrors[pol][iy])
                    lns += ' - '.join('' for i in range(len(procs) - index_procs))
                    combinedCard.write('eff_unc_{hb}    lnN {lns}\n'.format(hb=helbin,lns=lns))
        for hel in hel_to_constrain:
            for iy,helbin in enumerate(hel):
                sfx = str(iy)
                pol = helbin.split('_')[1]
                rateNuis = tightConstraint
                normPOI = '{norm}_{n}'.format(norm='norm' if options.scaleFile else 'r', n=helbin)

                ## if we fit absolute rates, we need to get them from the process and plug them in below
                ## if we want to fit with the efficiency gen-reco, we need to add one efficiency parameter
                if options.scaleFile:
                    tmp_eff = efficiencies[pol][iy]
                    combinedCard.write('eff_{n}    rateParam * {n} \t {eff:.5f} [{dn:.5f},{up:.5f}]\n'.format(n=helbin,eff=tmp_eff,dn=(1-1E-04)*tmp_eff,up=(1+1E-04)*tmp_eff))
                    expRate0 = float(ProcsAndRatesDict[helbin])/tmp_eff
                    param_range_0 = '{r:15.1f} [{dn:.1f},{up:.1f}]'.format(r=expRate0,dn=(1-rateNuis)*expRate0,up=(1+rateNuis)*expRate0)
                    # remove the channel to allow ele/mu combination when fitting for GEN
                    helbin_nochan = helbin.replace('_{channel}_Ybin'.format(channel=channel),'_Ybin')
                    combinedCard.write('norm_{nc}  rateParam * {n} \t {pr}\n'.format(nc=helbin_nochan,n=helbin,pr=param_range_0))
                POIs.append(normPOI)
        combinedCard.close()

        ### Now write the final datacard
        combinedCardNew = open(cardfile+"_new",'w')
        combinedCard = open(cardfile,'r')

        ProcsAndRatesUnity = [] # used in case of scaling to GEN
        for (p,r) in ProcsAndRates:
            ProcsAndRatesUnity.append((p,'1') if ('left' in p or 'right' in p or 'long' in p) else (p,r))
        Wlong = [(p,r) for (p,r) in ProcsAndRates if re.match('W.*long',p)]
        WLeftOrRight = [(p,r) for (p,r) in ProcsAndRates if ('left' in p or 'right' in p)]

        for l in combinedCard.readlines():
            if re.match("rate\s+",l):
                if options.scaleFile: combinedCardNew.write('rate            %s \n' % ' '.join([kpatt % r for (p,r) in ProcsAndRatesUnity])+'\n')
                else: combinedCardNew.write('rate            %s \n' % ' '.join([kpatt % '-1' for (p,r) in ProcsAndRates])+'\n')
            ## don't write the original slope
            elif 'FR' in l.split()[0] and 'slope' in l.split()[0]: continue
            else: combinedCardNew.write(l)
        if options.scaleFile:
            eff_long = 1./getScales([ybins['left'][0],ybins['left'][-1]], charge, 'long', options.scaleFile)[0] # just take the eff on the total Y acceptance (should be 0,6)
            eff_left = 1./getScales([ybins[pol][0],ybins[pol][-1]], charge, 'left', options.scaleFile)[0]
            eff_right = 1./getScales([ybins[pol][0],ybins[pol][-1]], charge, 'right', options.scaleFile)[0]
            normWLong = sum([float(r) for (p,r) in Wlong])/eff_long # there should be only 1 Wlong/charge
            normWLeft = sum([float(r) for (p,r) in WLeftOrRight if 'left' in p])/eff_left
            normWRight = sum([float(r) for (p,r) in WLeftOrRight if 'right' in p])/eff_right
            combinedCardNew.write("eff_{nc}   rateParam * {n}    {eff:.5f} [{dn:.5f},{up:.5f}]\n".format(nc=Wlong[0][0].replace('_long','_%s_long' % channel),n=Wlong[0][0],
                                                                                                         eff=eff_long,dn=(1-1E-04)*eff_long,up=(1+1E-04)*eff_long))
            ## write the long yield here
            nl = normWLong; tc = tightConstraint
            combinedCardNew.write("norm_{n} rateParam * {n} {r:15.1f} [{dn:.1f},{up:.1f}]\n".format(n=Wlong[0][0],r=nl,dn=(1-tc)*nl,up=(1+tc)*nl))
            POIs.append('norm_{n}'.format(n=Wlong[0][0].replace('_long','_%s_long' % channel))) # at this stage, norm POIs have still the channel inside
        else:
            pass
            # POIs.append('r_{n}'.format(n=Wlong[0][0].replace('_long','_%s_long' % channel)))
    
        if options.scaleFile: ## make an efficiency nuisance group
            combinedCardNew.write('\nefficiencies group = '+' '.join([p.replace('norm','eff') for p in POIs])+'\n\n' )

        ## remove all the POIs that we want to fix
        # remove the channel to allow ele/mu combination when fitting for GEN
        POIs = [poi.replace('_{channel}_'.format(channel=channel),'_') for poi in  POIs]
        for poi in POIs:
            if 'right' in poi and any('Ybin_'+str(i) in poi for i in fixedYBins):
                fixedPOIs.append(poi)
            if 'left'  in poi and any('Ybin_'+str(i) in poi for i in fixedYBins):
                fixedPOIs.append(poi)
        floatPOIs = list(poi for poi in POIs if not poi in fixedPOIs)
        allPOIs = fixedPOIs+floatPOIs
        ## define the combine POIs, i.e. the subset on which to run MINOS
        minosPOIs = allPOIs if not options.POIsToMinos else options.POIsToMinos.split(',')

        ## make a group for the fixed rate parameters. ## this is maybe obsolete, and restricted only to absolute rate fitting
        if options.scaleFile:
            print 'adding a nuisance group for the fixed rateParams'
            if len(fixedPOIs): combinedCardNew.write('\nfixedY group = {fixed} '.format(fixed=' '.join(i.strip() for i in fixedPOIs)))
            combinedCardNew.write('\nallY group = {all} \n'.format(all=' '.join([i for i in allPOIs])))
        combinedCardNew.close() ## for some reason this is really necessary
        os.system("mv {cardfile}_new {cardfile}".format(cardfile=cardfile))
        
        combinedCard = open(cardfile,'a+')
        ## add the theory / experimental systematics 
        for sys,procs in allsyst.iteritems():
            if isExcludedNuisance(excludeNuisances, sys): continue
            systscale = '1.0' if sys!='alphaS' else '0.67' # one sigma corresponds to +-0.0015 (weights correspond to +-0.001) => variations correspond to 0.67sigma
            # there should be 2 occurrences of the same proc in procs (Up/Down). This check should be useless if all the syst jobs are DONE
            #combinedCard.write('%-15s   shape%s %s\n' % (sys,'NoProfile' if re.match('smoothelscale.*',sys) else '', (" ".join([systscale if p in procs and procs.count(p)==2 else '  -  ' for p,r in ProcsAndRates]))) )
            combinedCard.write('%-15s   shape %s\n' % (sys,(" ".join([systscale if p in procs and procs.count(p)==2 else '  -  ' for p,r in ProcsAndRates]))) )
        combinedCard.close() 

        cardlines = [line.rstrip('\n') for line in open(cardfile,'r')]
        finalsystnames = [line.split()[0] for line in cardlines if len(line.split())>1 and any(systtype in line.split()[1] for systtype in ['shape','lnN'])]

        combinedCard = open(cardfile,'a+')        
        combinedCard.write('\nluminosity group = CMS_lumi_13TeV\n')
        combinedCard.write('\npdfs group    = '+' '.join(filter(lambda x: re.match('pdf.*',x),finalsystnames))+'\n')
        combinedCard.write('\nQCDTheo group    = '+' '.join(filter(lambda x: re.match('.*muR.*|.*muF.*|alphaS',x),finalsystnames))+'\n')
        combinedCard.write('\nQEDTheo group    = '+' '.join(filter(lambda x: re.match('smoothfsr',x),finalsystnames))+'\n')
        combinedCard.write('\nlepScale group = '+' '.join(filter(lambda x: re.match('.*smooth(el|mu)scale\S+',x),finalsystnames))+'\n')
        combinedCard.write('\nEffStat group = '+' '.join(filter(lambda x: re.match('.*ErfPar\dEffStat.*',x),finalsystnames))+'\n') 
        combinedCard.write('\nEffSyst group = '+' '.join(filter(lambda x: re.match('.*EffSyst.*|.*OutOfAccPrefireSyst.*',x),finalsystnames))+'\n')
        combinedCard.write('\nFakes group = '+' '.join(filter(lambda x: re.match('Fakes.*Uncorrelated.*',x),finalsystnames) +
                                                       filter(lambda x: re.match('.*FR.*(_norm|lnN|continuous)',x),finalsystnames))+'\n')
        combinedCard.write('\nOtherBkg group = '+' '.join(filter(lambda x: re.match('CMS_DY|CMS_Top|CMS_VV|CMS_Tau|CMS_We_flips',x),finalsystnames))+'\n')
        combinedCard.write('\nOtherExp group = '+' '.join(filter(lambda x: re.match('CMS.*lepVeto|(Z|TauDecaysW).*Uncorrelated.*|CMS.*bkg_lepeff',x),finalsystnames))+'\n')

        # now make the custom groups for charge asymmetry, angular coefficients, inclusive xsecs, etc.
        ## first make a list of all the signal processes.
        ## then, some processes and/or polarizations might be removed
        tmp_sigprocs = [p for p in realprocesses if 'Wminus' in p or 'Wplus' in p]
        polarizations = ['left','right','long']
        # regGroups don't allow background bins inside
        polToRegularize = polarizations if options.longSig else ['left','right']
        
        print '============================================================================='
        print 'I WILL NOW WRITE CHARGE GROUPS AND ALL THAT STUFF FOR THE FOLLOWING PROCESSES'
        print tmp_sigprocs
        print '============================================================================='
        # in case long is missing, the sum groups will only sum WR and WL, while polGroup cannot be defined
        # also add one group / longitudinal component to save it in the output tree
        if not options.freezePOIs:
            writeLongGroup(combinedCard,tmp_sigprocs)
            writePolGroup(combinedCard,tmp_sigprocs,polarizations,grouping='polGroup')
            writePolGroup(combinedCard,tmp_sigprocs,polarizations,grouping='sumGroup')
            writeRegGroup(combinedCard,tmp_sigprocs,polToRegularize,grouping='regGroup',bkgYBins=bkgYBins)
            writeChargeGroup(combinedCard,tmp_sigprocs,polarizations)
            writeChargeMetaGroup(combinedCard,tmp_sigprocs)
        combinedCard.close()
            
        ## here we make a second datacard that will be masked. which for every process
        ## has a 1-bin histogram with the cross section for every nuisance parameter and
        ## every signal process inside
        ## The non-nominal one (bare MC@NLO w/o V-pT reweighting) is not used in the fit, 
        ## but used for plotting an alternative band
        tmp_xsec_histfile_name = writeXSecFile(outfile,tmp_sigprocs,theosyst,ybins,options,nominal=True)
        writeXSecFile(outfile,tmp_sigprocs,theosyst,ybins,options,nominal=False)

        maskedChannels = ['InAcc']
        if options.ybinsOutAcc: maskedChannels.append('OutAcc')
        maskedChannelsCards = {}
        for maskChan in maskedChannels:
            if maskChan=='InAcc': tmp_sigprocs_mcha = [p for p in tmp_sigprocs if not any('Ybin_%d'%fixb in p for fixb in fixedYBins)]
            else:                 tmp_sigprocs_mcha = [p for p in tmp_sigprocs if any('Ybin_%d'%fixb in p for fixb in fixedYBins)]
            ## long now signal tmp_sigprocs_mcha = [p for p in tmp_sigprocs if not 'long' in p]
            tmp_xsec_dc_name = os.path.join(options.inputdir,options.bin+'_{ch}_xsec_{acc}_card.txt'   .format(ch=charge,acc=maskChan))
            maskedChannelsCards['{bin}_{ch}_xsec_{mc}'.format(bin=options.bin,ch=charge,mc=maskChan)] = tmp_xsec_dc_name
            tmp_xsec_dc = open(tmp_xsec_dc_name, 'w')
            tmp_xsec_dc.write("imax 1\n")
            tmp_xsec_dc.write("jmax *\n")
            tmp_xsec_dc.write("kmax *\n")
            tmp_xsec_dc.write('##----------------------------------\n')
            tmp_xsec_dc.write("shapes *  *  %s %s\n" % (tmp_xsec_histfile_name, 'x_$PROCESS x_$PROCESS_$SYSTEMATIC'))
            tmp_xsec_dc.write('##----------------------------------\n')
            tmp_xsec_dc.write('bin {b}\n'.format(b=options.bin))
            tmp_xsec_dc.write('observation -1\n') ## don't know if that will work...
            tmp_xsec_dc.write('bin      {s}\n'.format(s=' '.join(['{b}'.format(b=options.bin) for p in tmp_sigprocs_mcha])))
            tmp_xsec_dc.write('process  {s}\n'.format(s=' '.join([p for p in tmp_sigprocs_mcha])))
            ###tmp_xsec_dc.write('process  {s}\n'.format(s=' '.join(str(i+1)  for i in range(len(tmp_sigprocs_mcha)))))
            tmp_xsec_dc.write('process  {s}\n'.format(s=' '.join(procids[procnames.index(pname)]  for pname in tmp_sigprocs_mcha)))
            tmp_xsec_dc.write('rate     {s}\n'.format(s=' '.join('-1' for i in range(len(tmp_sigprocs_mcha)))))
            tmp_xsec_dc.write('# --------------------------------------------------------------\n')
            for sys,procs in theosyst.iteritems():
                if 'wpt' in sys or 'EffStat' in sys: continue
                if isExcludedNuisance(excludeNuisances, sys): continue
                # do not use the muR,muF,muRmuF for signal, we have the wpt-binned ones
                ## marc if any(x in sys for x in ['muF', 'muR', 'muRmuF']):
                if any(x in sys for x in ['leftmuF', 'leftmuR', 'leftmuRmuF', 'rightmuF', 'rightmuR', 'rightmuRmuF','longmuF', 'longmuR', 'longmuRmuF', 'muR', 'muF', 'muRmuF']):
                    if not re.match(".*[1-9]+",sys): continue
                # there should be 2 occurrences of the same proc in procs (Up/Down). This check should be useless if all the syst jobs are DONE
                tmp_xsec_dc.write('%-15s   shape %s\n' % (sys,(" ".join(['1.0' if p in tmp_sigprocs_mcha and correctScale(sys,p) else '  -  ' for p in tmp_sigprocs_mcha]))) )
            tmp_xsec_dc.close()
            ## end of all the xsec construction of datacard and making the file

        ## command to make the workspace. should be done after combineCards.py!
        ## os.system('text2workspace.py --X-allow-no-signal -o {ws} {dc}'.format(ws=tmp_xsec_dc_name.replace('_card','_ws'), dc=tmp_xsec_dc_name))

        print "merged datacard in ",cardfile

        ws = cardfile.replace('_card.txt', '_ws.root')
        minimizerOpts = ' --cminDefaultMinimizerType '+options.minimizer
        if options.minimizer.startswith('GSLMultiMin'): # default is Mod version by Josh
            minimizerOpts += ' --cminDefaultMinimizerAlgo BFGS2 --cminDefaultMinimizerTolerance=0.001 --keepFailures '
        else: 
            minimizerOpts += ' --cminInitialHesse 1 --cminFinalHesse 1 --cminPreFit 1 '
        if options.scaleFile:
            txt2wsCmd = 'text2workspace.py {cf} -o {ws} --X-allow-no-signal --X-no-check-norm '.format(cf=cardfile, ws=ws)
            combineCmd = 'combine {ws} -M MultiDimFit -t -1 -m 999 --saveFitResult {minOpts} --redefineSignalPOIs {pois} --floatOtherPOIs=0 --freezeNuisanceGroups efficiencies,fixedY{pdfs}{scales}{alphas} -v 9'.format(ws=ws, pois=','.join(minosPOIs), pdfs=(',pdfs' if len(pdfsyst) else ''), scales=(',scales' if len(qcdsyst) else ''),alphas=(',alphaS' if len(alssyst) else ''),minOpts=minimizerOpts)
        else: 
            signals = ['W{charge}_{pol}_W{charge}_{pol}_{channel}_Ybin_{yb}'.format(charge=charge,pol=pol,channel=channel,yb=yb) for pol in ['left','right'] for yb in xrange(len(ybins[pol])-1) ]
            signals += ['W{charge}_long'.format(charge=charge)]
            multisig      = ' '.join(["--PO 'map=.*/{proc}$:r_{proc_nochan}[1,0,10]'".format(proc=proc,proc_nochan=proc.replace('_{channel}_'.format(channel=channel),'_')) for proc in signals])

            cardfile_xsec = cardfile.replace('_card.', '_card_withXsecMask.')
            chname = options.bin+'_{ch}'.format(ch=charge)
            chname_xsecs = [chname+'_xsec_{acc}'.format(acc=mc) for mc in maskedChannels]
            maskChansCombCards = ' '.join(['{chName}={cardfile}'.format(chName=k,cardfile=val) for k,val in maskedChannelsCards.iteritems()])
            ccCmd = 'combineCards.py --noDirPrefix {oc}={odc} {maskchan} > {out}'.format(oc=chname,odc=cardfile,maskchan=maskChansCombCards,out=cardfile_xsec)

            newws = cardfile_xsec.replace('_card','_ws').replace('.txt','.root')

            txt2wsCmd = 'text2workspace.py {cf} -o {ws} --X-allow-no-background --X-no-check-norm -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose {pos} --channel-masks '.format(cf=cardfile_xsec, ws=newws, pos=multisig)
            txt2wsCmd_noXsec = 'text2workspace.py {cf} -o {ws} --X-no-check-norm -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose {pos} '.format(cf=cardfile, ws=ws, pos=multisig)
            if options.freezePOIs:
                # doesn't make sense to have the xsec masked channel if you freeze the rates (POIs) -- and doesn't work either
                txt2hdf5Cmd = 'text2hdf5.py {sp} {cf} --clipSystVariations {varmax}'.format(cf=cardfile,sp="--sparse" if options.sparse else "",varmax=1.3)
            else:
                mcstr = '--maskedChan '+' --maskedChan '.join([k for k,val in maskedChannelsCards.iteritems()])
                txt2hdf5Cmd = 'text2hdf5.py {sp} {maskch} --X-allow-no-background {cf} --clipSystVariations {varmax}'.format(maskch=mcstr,cf=cardfile_xsec,sp="--sparse" if options.sparse else "",varmax=1.3)
            #combineCmd = 'combine {ws} -M MultiDimFit    -t -1 -m 999 --saveFitResult --keepFailures --cminInitialHesse 1 --cminFinalHesse 1 --cminPreFit 1       --redefineSignalPOIs {pois} --floatOtherPOIs=0 -v 9'.format(ws=ws, pois=','.join(['r_'+p for p in signals]))
            # combineCmd = 'combine {ws} -M MultiDimFit -t -1 -m 999 --saveFitResult {minOpts} --redefineSignalPOIs {pois} -v 9 --setParameters mask_{xc}=1 '.format(ws=newws, pois=','.join(['r_'+p for p in signals]),minOpts=minimizerOpts, xc=chname_xsec)
        ## here running the combine cards command first
        print ccCmd
        os.system(ccCmd)

        # following part is obsolete and doesn't work, because we define the groups with both charges, so text2hdf5.py will crash
        # anyway, I don't think we will ever run the fit on a single charge again
        # let's keep it but skip it for now
        if False:
            ## then running the t2w command afterwards
            # print txt2wsCmd
            # print '-- will NOT run text2workspace -----------------------'
            # os.system(txt2wsCmd)
            # print "NOT doing the noXsec workspace..."
            # os.system(txt2wsCmd_noXsec)
            ## here making the TF meta file
            print '--- will run text2hdf5 ---------------------'
            print "running ",txt2hdf5Cmd
            os.system(txt2hdf5Cmd)
            ## print out the command to run in combine
            if options.freezePOIs:
                combineCmd = 'combinetf.py --POIMode none -t -1 --binByBinStat --correlateXsecStat {metafile}'.format(metafile=cardfile_xsec.replace('.txt','_sparse.hdf5' if options.sparse else '.hdf5'))
            else:
                combineCmd = 'combinetf.py -t -1 --binByBinStat --correlateXsecStat {metafile}'.format(metafile=cardfile_xsec.replace('.txt','_sparse.hdf5' if options.sparse else '.hdf5'))
            print combineCmd
        # end of loop over charges

