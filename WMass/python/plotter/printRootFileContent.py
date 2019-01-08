#!/usr/bin/env python  

from shutil import copyfile
import re, sys, os, os.path, subprocess, json, ROOT
import numpy as np

from optparse import OptionParser
parser = OptionParser(usage="%prog [options] infile.root")
parser.add_option('-c', '--class',          dest='className',      default='', type='string', help='Filter output based on the object class (e.g. -c TH1D)')
parser.add_option('-x', '--exclude-regexp', dest='exclude_regexp', default='', type='string', help='Like option -r, but will reject object if name matches')
parser.add_option('-f', '--output-format',  dest='output_format',  default='all', type='string', help='Print type, name and (for histograms only) integral (all, default); just name (name)')
parser.add_option('-s', '--silent'  ,       dest='silent',         default=False, action='store_true', help='Silent mode: just print summary, not all entries')
parser.add_option('-i', '--inherith',       dest='inherit',        default='', type='string', help='Filter output based on whether the object class inheriths from this (e.g. -i TH1 will match all root histogram objects)')  
parser.add_option('-r', '--regexp',         dest='regexp',         default='', type='string', help='Filter output passing a regular expression to be matched in the object name')
(options, args) = parser.parse_args()

if len(sys.argv) < 1:
    parser.print_usage()
    quit()

tf = ROOT.TFile.Open(args[0],"READ")
nRead = 0
nNullIntegral = 0

if not options.silent:
    print "-"*50
    if options.output_format == "all":    
        print "{: <10} {: <20}    {y} ".format("Class","name",y="integral(histogram only)")
    elif options.output_format == "name":
        print "name"
    print "-"*50
        
for k in tf.GetListOfKeys() :
    name=k.GetName()
    if len(options.regexp) and not re.match(options.regexp,name): continue
    if len(options.exclude_regexp) and re.match(options.exclude_regexp,name): continue
    obj=k.ReadObj()
    if len(options.className) and obj.ClassName() != options.className: continue
    if len(options.inherit) and not obj.InheritsFrom(options.inherit): continue
    nRead += 1
    integral = obj.Integral() if (obj.ClassName().startswith("TH") and obj.InheritsFrom("TH1")) else -1
    if integral == 0.0: nNullIntegral += 1
    if not options.silent:
        if options.output_format == "all":
            #print "%s   %s   %s" % (obj.ClassName(), name, str(integral) if integral >= 0 else "")
            print "{: <10} {: <20}    {y} ".format(obj.ClassName(), name, y=str(integral) if integral >= 0 else "")
        elif options.output_format == "name":
            print "%s" % name

print "########################################"
print "########################################"
print " Summary"
print "----------------------------------------"
print "There were %d keys in the file" % tf.GetNkeys()
print "There were %d keys passing filters" % nRead
print "There were %d histograms with integral = 0" % nNullIntegral
    


