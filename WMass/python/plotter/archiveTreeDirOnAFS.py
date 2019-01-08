#!/usr/bin/env python
# USAGE: python archiveTreeDirOnAFS.py EOSDIR AFSDIR

import os, subprocess
from optparse import OptionParser

if __name__ == "__main__":

    usage="%prog [options] eosdir afsdir"
    
    parser = OptionParser(usage=usage)
    parser.add_option("-t", dest="treeproducername", type='string', default="treeProducerWMass", help='Name of the tree producer module')
    parser.add_option("-f", dest="friendtreedir", type='string', default="friends", help='String identifying friend trees directory')
    parser.add_option("-T", dest="treename", type='string', default="tree.root", help='Name of the tree file')
    (options, args) = parser.parse_args()
    if len(args)<2: raise RuntimeError, 'Expecting at least two arguments'
    
    eosdir = args[0]
    afsdir = args[1]
    
    treedir = os.path.basename(eosdir)
    if not os.path.isdir(afsdir):
            rsync = "rsync -avz --exclude '*.root' {source} {destination}".format(source=eosdir,destination=afsdir)
            print "Giving rsync command: ",rsync
            os.system(rsync)
    
    alldsets = os.listdir(eosdir)
    dsets = [d for d in alldsets if options.friendtreedir not in d and '.txt' not in d]
    friends = os.listdir(eosdir+'/'+options.friendtreedir)
    
    for d in dsets:
            url = "root://eoscms.cern.ch/{eosdir}/{dataset}/{treeproducername}/{treename}\n".format(eosdir=eosdir,dataset=d,treeproducername=options.treeproducername,treename=options.treename)
            furl = open('{afsdir}/{treedir}/{dataset}/{treeproducername}/{treename}.url'.format(afsdir=afsdir,treedir=treedir,dataset=d,treeproducername=options.treeproducername,treename=options.treename),'w')
            furl.write(url)
            furl.close()
    for f in friends:
            friendurl = 'root://eoscms.cern.ch/{eosdir}/{frienddir}/{friendfile}\n'.format(eosdir=eosdir,frienddir=options.friendtreedir,friendfile=f)
            furl = open('{afsdir}/{treedir}/{frienddir}/{friendfile}.url'.format(afsdir=afsdir,treedir=treedir,frienddir=options.friendtreedir,friendfile=f),'w')
            furl.write(friendurl)
            furl.close()
            
    print "AFS tree structure in {afsdir}/{treedir}".format(afsdir=afsdir,treedir=treedir)
