#!/bin/env python

# python w-helicity-13TeV/makeFakeRateNormNuisanceHisto.py -o ../../data/fakerate/fakeRatenormWeight_etaPt_el.root -c el

import ROOT, os, sys, re, math
from array import array

ROOT.gROOT.SetBatch(True)

if __name__ == "__main__":


    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options]')
    parser.add_option('-o','--outfile', dest='outfile', default='.', type='string', help='output file to save things. Any non existing folder will be created')
    parser.add_option('-c','--channel', dest='channel', default='mu', type='string', help='name of the channel (mu or el)')
    (options, args) = parser.parse_args()

    ROOT.TH1.SetDefaultSumw2()
    
    
    channel = options.channel
    if channel not in ["el","mu"]:
        print "Error: unknown channel %s (select 'el' or 'mu')" % channel
        quit()

    if options.outfile:
        outname = os.path.dirname(options.outfile)
        if not outname.endswith('/'): outname = outname + "/"
        if outname != "./":
            os.system("mkdir -p %s" % outname)
    else:
        print "Error: you should specify an output file using option -o <name>. Exit"
        quit()

    if os.path.isfile(options.outfile):
        print "Warning: going to overwrite existing file '%s' ." % os.path.abspath(options.outfile)
        print "Do you want to proceed? [y/n]" 
        if raw_input()!='y':
            print 'Aborting'
            exit()

    ptBinEdges = [25, 30, 35, 40, 45, 50]
    nuis_vs_eta = {}
    if channel == "el":
        etaBinEdges = [0.0, 0.8, 1.4442, 1.566, 2.1, 2.5]  
        nuis_vs_eta[0] = 0.1
        nuis_vs_eta[1] = 0.2
        nuis_vs_eta[2] = 0.0
        nuis_vs_eta[3] = 0.3
        nuis_vs_eta[4] = 0.3
    else:
        etaBinEdges = [0.0, 0.6, 1.2, 1.8, 2.4]  
        nuis_vs_eta[0] = 0.1
        nuis_vs_eta[1] = 0.2
        nuis_vs_eta[2] = 0.3
        nuis_vs_eta[3] = 0.3

    lepton = "electron" if channel == "el" else "muon"

    of=ROOT.TFile(os.path.abspath(options.outfile),'recreate')

    hname = "hFRnormNuis_{lep}".format(lep=lepton)
    hFRnormNuis = ROOT.TH2F(hname,"fake rate normalization lnN nuisance",
                            len(etaBinEdges)-1, array('d',etaBinEdges), len(ptBinEdges)-1, array('d',ptBinEdges))
    
    for ieta in range(1, hFRnormNuis.GetNbinsX()+1):
        for ipt in range(1,hFRnormNuis.GetNbinsY()+1):
            hFRnormNuis.SetBinContent(ieta,ipt,nuis_vs_eta[ieta-1])                    

    hFRnormNuis.Write()
    of.Close()

    print "Created root file: %s " % os.path.abspath(options.outfile)
    print "Saved histogram %s inside" % hname



