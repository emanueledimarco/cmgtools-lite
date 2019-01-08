import ROOT, os
ROOT.gROOT.SetBatch(True)

## USAGE:
## python leptonTnP.py -i /eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_recoLeptons_and_triggerMatch_latest/ -c mu -o indir

## option -o indir : saves the output trees in the input directory. if none given it saves it where it's run
## option -c       : has to be mu or el
## option -a       : either "trigger" or "selection"


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] mc.txt cuts.txt treeDir outputDirSkims ")
    parser.add_option("-c", "--channel"   ,  dest="channel", type='string', default='mu',  help="run tnp ntuples for muons/electrons. default mu")
    parser.add_option("-i", "--indir"     ,  dest="indir"  , type='string', default=''  ,  help="directory with the trees")
    parser.add_option("-m", "--maxentries",  type='int'    , default=-1  ,  help="run only these many entries.")
    parser.add_option("-o", "--outdir"    ,  type='string'    , default='./'  ,  help="save the files in this outdir")
    parser.add_option("-a", "--analyzer"  ,  dest="analyzer", type='string', default='trigger',  help="run tnp ntuples for trigger/selection. default trigger")
    (options, args) = parser.parse_args() 


    if options.outdir == 'indir':
        options.outdir = options.indir

    for sd in os.listdir(options.indir):
        treefile = '/'.join([options.indir,sd,'treeProducerWMass','tree.root'])
        if not os.path.isfile(treefile): continue

        if (options.channel == 'el' and 'SingleMu' in sd): continue
        if (options.channel == 'mu' and 'SingleEl' in sd): continue

        print 'runing on file', treefile

        tmp_file = ROOT.TFile(treefile, 'read')
        tmp_tree = tmp_file.Get('tree')
        
        ## make the instance of the worker
        ##if 'el' in options.channel or 'mu' in options.channel:
        ## friends now also for muons!
        ffile = options.indir+'/friends/tree_Friend_'+sd+'.root'
        tmp_friend_file = ROOT.TFile(ffile)
        tmp_friend_tree = tmp_friend_file.Get('Friends')
        ##else: 
        ##    tmp_friend_tree = None
    
        if options.analyzer=='trigger'     : 
            print 'compiling trigger ntuple producer'
            ROOT.gROOT.ProcessLine(".L TnPNtuplesTriggerEfficiency.C+" )
            tnp_worker = ROOT.TnPNtuplesTriggerEfficiency(tmp_tree,tmp_friend_tree)
        elif options.analyzer=='selection' : 
            print 'compiling selection ntuple producer'
            ROOT.gROOT.ProcessLine(".L TnPNtuplesSelectionEfficiency.C+" )
            tnp_worker = ROOT.TnPNtuplesSelectionEfficiency(tmp_tree,tmp_friend_tree)
        else: 
            print "analyzer can be either trigger/selection."
            exit(1)

        if 'mu' in options.channel:
            tnp_worker.setFlavor(13)
        else: 
            tnp_worker.setFlavor(11)

        tnp_worker.setOutfile(options.outdir+'/'+options.analyzer+'TnP_'+os.path.basename(sd)+'_{ch}.root'.format(ch=options.channel))
        tnp_worker.Loop(options.maxentries)
    
        del tnp_worker ## this segfaults otherwise

