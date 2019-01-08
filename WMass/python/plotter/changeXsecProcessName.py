#!/bin/env python

# python changeXsecProcessName.py cards/diffXsec_2018_06_25_group5_coarsebin/Wel_plus_card_withXsecMask.txt Wel_plus_xsec -m _el_ -n _lep_ -o combinedElMuDiffXsec/test/diffXsec_2018_06_25_group5_coarsebin/

# can pass datacard and bin with CHARGE in name instead of plus|minus and use option --pattern CHARGE=plus,minus to loop on both charges, each time substituting CHARGE in datacard and bin with the given charge
# E.g.:
# python changeXsecProcessName.py cards/diffXsec_2018_06_25_group5_coarsebin/Wel_CHARGE_card_withXsecMask.txt Wel_CHARGE_xsec -m _el_ -n _lep_ -o combinedElMuDiffXsec/test/diffXsec_2018_06_25_group5_coarsebin/ --pattern CHARGE=plus,minus

# This script will copy card 'datacard' into a new folder, changing names of some processes associated to bin 'bin'
# The process's name is changed substituting options.match with options.newmatch if options.match is in the name
# Same for the shape file related to bin 'bin'
# Other shape files are copied in the same folder, so that it can be used to run combine without messing up the original folder
# All the needed inputs are taken from 'datacard'

import ROOT
import sys,os,re,json,copy

from optparse import OptionParser
parser = OptionParser(usage='%prog [options] datacard bin')
parser.add_option('-o','--output'  , dest='outputdir', default='', type='string', help='Output folder')
#parser.add_option('-b','--bin'     , dest='binname'  , default='', type='string', help='Bin name whose process will be changed')
parser.add_option('-m','--match'   , dest='match'    , default='', type='string', help='Match in process name to be changed')
parser.add_option('-n','--newmatch', dest='newmatch' , default='', type='string', help='New match to change match in process name')
parser.add_option(     '--pattern', dest='pattern' , default='', type='string', help='See comment above inside the script. Eg.: --pattern CHARGE=plus,minus')
(options, args) = parser.parse_args()

if len(args) < 2:
    parser.print_usage()
    exit()

if options.pattern:
    pattern = options.pattern.split("=")[0] 
    charges = options.pattern.split("=")[1].split(',')
else:
    charges = ["dummy"]

for charge in charges:

    if options.pattern:
        print ""
        print ""
        print "="*20
        print "Charge: %s" % charge
        print "="*20
        datacard = str(args[0]).replace(pattern,charge)
        bin = str(args[1]).replace(pattern,charge)
    else:
        datacard = str(args[0])
        bin = str(args[1])
    #bin = options.binname

    if options.match and options.newmatch:
        print "-------------------------------------------"
        print "I will change process name for bin %s" % bin
        print "I will substitute keyword '%s' with '%s'" % (options.match, options.newmatch)
        print "-------------------------------------------"
    else:
        print "Error: you must use options -m <match> and -n <newmatch>. Exit"
        quit()

    if options.outputdir:
        outdir = options.outputdir + ("/" if not options.outputdir.endswith('/') else "")
        if not os.path.exists(outdir):
            os.system("mkdir -p "+outdir)
    else:
        print "Warning: you should pass an output directory to save stuff. Use option -o <outdir>. Exit"
        quit()

    dcname = os.path.basename(datacard)
    #print datacard
    #print dcname
    #print outdir

    # I don't need to change name of datacard. I should have both Wel_<bla> adn Wmu_<bla> and then combine them with combineCards.py
    # Same for the xsection root files (but the names of histograms inside those files for electrons and muons will be the same)
    # if any(dcname.startswith(x) for x in ["Wel_","Wmu_"]):
    #     newdcname = "Wlep" + '_'.join(dcname.split('_')[1:])
    #     dctag = dcname.split('_')[0]
    # else:
    #     print "Warning: I was expecting the datacard name to start with 'Wel_' or 'Wmu_'."
    #     print "Datacard name: %s " % dcname
    #     print "Exit"
    #     quit()

    shapefile = ""
    otherShapesFiles = []
    # get shape file from datacard
    with open(datacard) as thisfile:
        for l in thisfile.readlines():        
            if re.match('shapes.*',l):
                #print l
                shapebin = l.split()[2]
                if shapebin == bin:
                    shapefile = l.split()[3]
                else:
                    otherShapesFiles.append(l.split()[3])

    print "-------------------------------------------"
    print "Copying the following shape files in folder '%s'" % outdir
    print "They were not modified"
    for i,rf in enumerate(otherShapesFiles):
        print "%d: %s" % (i,rf)
        os.system("cp %s %s" % (rf,outdir))
    print "-------------------------------------------"

    if len(shapefile) == 0:
        print "*************************************"
        print "Warning: bin '%s' not found in datacard '%s'" % (bin, datacard)
        print "Please check. Exit"
        print "*************************************"
        quit()


    #newshapefile = outdir + os.path.basename(shapefile).replace(dctag,"Wlep")
    newshapefile = outdir + os.path.basename(shapefile)
    #print newshapefile
    #print os.path.abspath(newshapefile)

    # create new shape file copying content and changing some names according to input options
    tf = ROOT.TFile.Open(shapefile)
    newtf = ROOT.TFile.Open(newshapefile,'recreate')
    for e in tf.GetListOfKeys() :
        name=e.GetName()
        obj=e.ReadObj()
        if re.match(".*"+options.match,name): 
            #print "Changing histogram name in file %s" % os.path.basename(newshapefile)
            obj.Clone(name.replace(options.match,options.newmatch)).Write(name.replace(options.match,options.newmatch))
        else:
            obj.Clone().Write()    
    newtf.Close()
    print "-------------------------------------------"
    print "Created new root file: %s" % newshapefile
    print "-------------------------------------------"

    # now create new datacard with modified lines according to input options
    #newdatacard = outdir + dcname.replace(dctag,"Wlep")
    newdatacard = outdir + dcname
    newdcfile = open(newdatacard,'w')
    nBinLineIncard = 1
    nProcessLineIncard = 1
    binNames = []
    processNames = []
    with open(datacard) as thisfile:
        for l in thisfile.readlines():        
            if re.match('shapes.*',l):
                tokens = l.split()
                if tokens[2] == bin: 
                    newdcfile.write(l.replace(tokens[3],os.path.abspath(newshapefile)))
                else: 
                    # other shapes were copied, so change the absolute path to the new folder
                    newOtherShapeFile = os.path.abspath(outdir+os.path.basename(tokens[3]))
                    newdcfile.write(l.replace(tokens[3],newOtherShapeFile))        
            elif re.match('bin.*',l):
                if nBinLineIncard == 1: nBinLineIncard += 1
                else:                   binNames = l.split()[1:]
                newdcfile.write(l)
            elif re.match('process.*',l):
                if nProcessLineIncard == 1:
                    processNames = l.split()[1:]
                    nProcessLineIncard += 1
                    newprocessLine = "process" + " "*10
                    for i,x in enumerate(binNames):
                        pname = processNames[i].replace(options.match,options.newmatch) if x == bin else processNames[i]
                        newprocessLine = newprocessLine + "   " + pname
                    newdcfile.write(newprocessLine+"\n")
                else:
                    newdcfile.write(l)
            else:
                newdcfile.write(l)
    newdcfile.write('\n') 
    newdcfile.close()
    print "-------------------------------------------"
    print "Created new datacard: %s" % newdatacard
    print "-------------------------------------------"


