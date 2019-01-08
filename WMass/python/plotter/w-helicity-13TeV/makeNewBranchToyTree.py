#!/bin/env python

# python w-helicity-13TeV/makeNewBranchToyTree.py -i toys/diffXsec_mu_2018_09_25_group10_legacySF/comb_WchargeAsymmetry/toys_comb_WchargeAsymmetry.root -c mu


import ROOT, os, sys, re, array, math
from array import array

from make_diff_xsec_cards import getDiffXsecBinning
from make_diff_xsec_cards import templateBinning

sys.path.append(os.getcwd() + "/plotUtils/")
from utility import *

ROOT.gROOT.SetBatch(True)

import utilities
utilities = utilities.util()

if __name__ == "__main__":


    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options]')
    parser.add_option('-i','--inputfile', dest='infile', default='', type='string', help='input root file with toys')
    parser.add_option('-o','--outdir', dest='outdir', default='SAME', type='string', help='output directory to save things (same folder as input toy file if SAME')
    parser.add_option('-t','--tree', dest='tree', default='fitresults', type='string', help='name of tree inside file')
    #parser.add_option('-c','--channel', dest='channel', default='', type='string', help='name of the channel (mu or el)')
    parser.add_option('-n','--name', dest='name', default='toyFriend.root', type='string', help='name of output file')
    #parser.add_option('-v','--verbose', dest='verbose', default=False, action="store_true", type='string', help='Verbose mode, will print event number')
    (options, args) = parser.parse_args()

    ROOT.TH1.SetDefaultSumw2()
    
    # channel = options.channel
    # if channel not in ["el","mu"]:
    #     print "Error: unknown channel %s (select 'el' or 'mu')" % channel
    #     quit()

    if options.outdir:
        outname = options.outdir
        if outname == "SAME":
            outname = os.path.dirname(options.infile) + "/"
        else:
            addStringToEnd(outname,"/",notAddIfEndswithMatch=True)        
            createPlotDirAndCopyPhp(outname)
    else:
        print "Error: you should specify an output folder using option -o <name>. Exit"
        quit()

    if not options.infile:
        print "Error: you should specify a file containing the toys using option -i <name>. Exit"
        quit()


    fin = ROOT.TFile(options.infile, 'read')
    tree = fin.Get(options.tree)
    if not tree:
        print "Error: could not read tree in file"
        quit()
    lok  = tree.GetListOfLeaves()


    fout = ROOT.TFile( outname+options.name, 'recreate' )    
    t = ROOT.TTree( 'toyFriend', 'friend tree for toys' )
    totxsec_plus  = array( 'f', [ 0. ] )
    totxsec_minus = array( 'f', [ 0. ] )

    t.Branch( 'totxsec_plus' , totxsec_plus , 'totxsec_plus/F' )
    t.Branch( 'totxsec_minus', totxsec_minus, 'totxsec_minus/F' )

    # for i in range(tree.GetEntries()):
    #     totxsec_plus[0]  = -1. * i
    #     totxsec_minus[0] = i
    #     #print "%.1f  %.1f" % (totxsec_plus[0], totxsec_minus[0])
    #     fillStatus = t.Fill()
    #     #print "fillStatus = %d" % fillStatus

    lok_pruned = []
    for p in lok:
        pname = p.GetName()
        if not pname.endswith("_pmaskedexp"): continue
        if "outliers" in pname: continue  # use only bins inside acceptance for the total xsec (it only exists for diff.xsec in pt-|eta|)              
        lok_pruned.append(p)

    print "I filtered {fin} elements out of {init}".format(fin=str(len(lok_pruned)),init=str(len(lok)))

    nEvents = tree.GetEntries()
    for i,ev in enumerate(tree):

        sum_plus = 0
        sum_minus = 0
        sys.stdout.write('Event {num}/{tot}   \r'.format(num=i,tot=nEvents))
        sys.stdout.flush()

        # loop on leaves (branches)
        for p in lok_pruned:  
            pname = p.GetName()
            #if not pname.endswith("_pmaskedexp"): continue
            #if "outliers" in pname: continue  # use only bins inside acceptance for the total xsec (it only exists for diff.xsec in pt-|eta|)
            #print "pname = %s" % pname
            if "plus"    in pname: sum_plus += getattr(ev, pname)
            elif "minus" in pname: sum_minus += getattr(ev, pname)
            #Wplus_{ch}_ieta_{ieta}_ipt_{ipt}_Wplus_{ch}_group_{ig}_pmaskedexp example for POI's name for diff.xsec
        totxsec_plus[0] = sum_plus
        totxsec_minus[0] = sum_minus
        t.Fill()

    # fout.Write()
    t.Write()    
    fout.Close()

    fin.Close()
