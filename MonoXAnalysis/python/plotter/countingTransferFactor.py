#!/usr/bin/env python
from CMGTools.MonoXAnalysis.plotter.mcAnalysis import *
import re, sys, copy


class countingTransferFactor:
    def __init__(self,args,optionsSR,optionsCR,CR):
        self.mca_SR  = MCAnalysis(args[0],optionsSR)
        self.cuts_SR = CutsFile(args[1],optionsSR)
        self.mca_CR  = MCAnalysis(args[2],optionsCR)
        self.cuts_CR = CutsFile(args[3],optionsCR)

        self.numProc = args[4]
        self.denProc = args[5]
        self.CR = args[6]

    def getTF(self):
        report_SR = self.mca_SR.getYields(self.cuts_SR)
        report_CR = self.mca_CR.getYields(self.cuts_CR)

        tf = report_SR[self.numProc][-1][1][0] / report_CR[self.denProc][-1][1][0]
        tf_err = tf * sqrt( pow(report_SR[self.numProc][-1][1][1]/report_SR[self.numProc][-1][1][0],2) + pow(report_CR[self.denProc][-1][1][1]/report_CR[self.denProc][-1][1][0],2) )
        self.N_SR =  report_SR[self.numProc][-1][1][0]
        print "==> Transfer factor ", self.numProc, "(SR) / ", self.denProc," (CR) = ",  tf, " +/- ", tf_err
        return (tf,tf_err)

    def writeTFToFile(self,filename,numtag,dentag,option):
        tfcard = open(filename,option)
        transferf = self.getTF()
        if option == 'w': tfcard.write("N_%s_SR = %d\n" % (numtag,self.N_SR) ) # this is used as initial value, from MC (but it is not used, since the uncertainty is lnU and the rate will depend only on the CRs yields
        tfcard.write("alpha_%s_%s_%s = %f +/- %f\n" % (numtag,dentag,self.CR,transferf[0],transferf[1]) )

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] mcSR.txt cutsSR.txt mcCR.txt cutsCR.txt numProc denProc CR")
    addMCAnalysisOptions(parser)
    parser.add_option("--P_SR", "--path_SR",           dest="path_SR",        type="string", default="./",      help="path to directory with input trees and pickle files (./)") 
    parser.add_option("--F_SR", "--add-friend_SR",    dest="friendTrees_SR",  action="append", default=[], nargs=2, help="Add a friend tree (treename, filename). Can use {name}, {cname} patterns in the treename") 
    parser.add_option("--FMC_SR", "--add-friend-mc_SR",    dest="friendTreesMC_SR",  action="append", default=[], nargs=2, help="Add a friend tree (treename, filename) to MC only. Can use {name}, {cname} patterns in the treename") 
    parser.add_option("--W_SR", "--weightString_SR",   dest="weightString_SR", type="string", default="1", help="Use weight (in MC events)")
    parser.add_option("--P_CR", "--path_CR",           dest="path_CR",        type="string", default="./",      help="path to directory with input trees and pickle files (./)") 
    parser.add_option("--F_CR", "--add-friend_CR",    dest="friendTrees_CR",  action="append", default=[], nargs=2, help="Add a friend tree (treename, filename). Can use {name}, {cname} patterns in the treename") 
    parser.add_option("--FMC_CR", "--add-friend-mc_CR",    dest="friendTreesMC_CR",  action="append", default=[], nargs=2, help="Add a friend tree (treename, filename) to MC only. Can use {name}, {cname} patterns in the treename") 
    parser.add_option("--W_CR", "--weightString_CR",   dest="weightString_CR", type="string", default="1", help="Use weight (in MC events)");
    parser.add_option("-w", "--write-to-file",   dest="writeToFile", type="string", default="", help="Destination txt file");
    parser.add_option("-o", "--write-option",   dest="writeOption", type="string", default="w", help="Recreate (w) or append (a)");
    (options, args) = parser.parse_args()
    options.weight = True
    options.final  = True

    options_SR = copy.deepcopy(options)
    options_SR.path = options.path_SR
    options_SR.friendTrees = options.friendTrees_SR
    options_SR.friendTreesMC = options.friendTreesMC_SR
    options_SR.weightString = options.weightString_SR
    
    options_CR = copy.deepcopy(options)
    options_CR.path = options.path_CR
    options_CR.friendTrees = options.friendTrees_CR
    options_CR.friendTreesMC = options.friendTreesMC_CR
    options_CR.weightString = options.weightString_CR

    tfcalc = countingTransferFactor(args,options_SR,options_CR,args[6])
    tfcalc.writeTFToFile(options.writeToFile,args[4],args[5],options.writeOption)
