import ROOT, os, glob, sys
ROOT.gROOT.SetBatch(True)

## USAGE:
## python leptonTnP.py -i /eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_2018-07-06-2l_triggerMatch_MUONS/ -o indir

## option -o indir : saves the output trees in the input directory. if none given it saves it where it's run


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] mc.txt cuts.txt treeDir outputDirSkims ")
    parser.add_option("-o", "--outdir"    ,  type='string'    , default='./'  ,  help="save the files in this outdir")
    (options, args) = parser.parse_args() 

    files = [
        'SingleElectron_Run2016C-03Feb2017-v1.root',
        'SingleElectron_Run2016D-03Feb2017-v1.root',
        'SingleElectron_Run2016E-03Feb2017-v1.root',
        'SingleElectron_Run2016F-03Feb2017-v1.root',
        'SingleElectron_Run2016G-03Feb2017-v1.root',
        'SingleElectron_Run2016H-03Feb2017-v1.root',
        ]

    for ntuple in files:
        if not os.path.isfile(ntuple): continue

        print 'runing on file', ntuple

        tmp_file = ROOT.TFile(ntuple, 'read')
        tmp_tree = tmp_file.Get('ntuple/tree')
        
        ## make the instance of the worker
    
        ROOT.gROOT.ProcessLine(".L L1TnPNtuples.C+" )
        tnp_worker = ROOT.L1TnPNtuples(tmp_tree)
        tnp_worker.setOutfile(options.outdir+'/TnP_'+os.path.basename(ntuple))
        tnp_worker.Loop()

        del tnp_worker ## this segfaults otherwise

