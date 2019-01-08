#!/bin/env python

# Author: Marco Cipriani
# Mail: marco.cipriani@cern.ch
# cern user: mciprian

# This script basically run a command like the following to move jobs from a queue to another one 
# bjobs | grep PEND | grep cmscaf1nd |awk '{print $1}' | head -n 50 | xargs -n 1 bmod -q 2nd

# Usage
# python changeQueuePendingJobs.py -i cmscaf1nd -f 2nd -n 50
import sys,os
import subprocess

from optparse import OptionParser
parser = OptionParser(usage='%prog [options]')
parser.add_option('-d', '--dry-run'     , dest="dryRun"      , action="store_true", default=False, help="Do not run the command, just print it");
parser.add_option('-i','--initial-queue', dest='initialQueue', default='', type='string', help='Queue which jobs should be moved from') 
parser.add_option('-f','--final-queue'  , dest='finalQueue'  , default='', type='string', help='Queue which jobs should be moved to') 
parser.add_option('-n','--n-job'        , dest="nJob"        , default='0',type='int'   , help="Specify a number of jobs to be moved (default is all). If there are less pending jobs than this options's argument, all are moved");
(options, args) = parser.parse_args()

hostname = os.environ['HOSTNAME']
if not "lxplus" in hostname:
    print "Error: you need to be on lxplus to run this script. Exit"
    quit()

cmssw = os.environ['CMSSW_BASE']
if not cmssw:
    print "Error: you need to be inside a release to run this script. Did you forget to run cmsenv? Exit"
    quit()

if not options.initialQueue or not options.finalQueue:
    print "Error: you must specify both the initial and final queues. Exit"
    quit()

# use grep -e "<queue>": for queue 1nd, pass option -i " 1nd", otherwise also cmscaf1nd would match
countCmd = "bjobs | grep PEND | grep -e \" %s\" | wc -l" % options.initialQueue.strip()
countPendingJobs = subprocess.Popen([countCmd], stdout=subprocess.PIPE, shell=True);
nPendQueue = countPendingJobs.communicate()[0]
nPendQueue = int(nPendQueue)
print "-----------------------------------------------"
print "I see %d pending jobs on queue %s" % (nPendQueue, options.initialQueue)
print "-----------------------------------------------"
if nPendQueue == 0:
    print "There are no pending jobs in the queue you selected."
    quit()

if options.nJob > nPendQueue: options.nJob = nPendQueue

cmd = "bjobs | grep PEND | grep -e ' %s' | awk '{print $1}' | " % options.initialQueue.strip()
if options.nJob:
    cmd = cmd + "tail -n %s | " % options.nJob
cmd = cmd + "xargs -n 1 bmod -q %s" % options.finalQueue

print "============================"
print cmd
print "----------------------------"
print "I will move %s jobs from queue '%s' to '%s'" % (str(options.nJob) if options.nJob else "all", options.initialQueue.strip(), options.finalQueue.strip())
print "============================"
if not options.dryRun:
    os.system(cmd)
print "============================"
