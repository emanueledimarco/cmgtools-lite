import ROOT, os
from optparse import OptionParser


if __name__ == "__main__":

    parser = OptionParser(usage="usage: %prog [options] -i inputDirectory -c condorSubmitFile")
    parser.add_option('-i', '--indir' , dest='indir' , default='', type='string', help='directory with the root files')
    parser.add_option('-c', '--condor', dest='condor', default='', type='string', help='condor file with all jobs')
    (options, args) = parser.parse_args()

    if not options.indir or not options.condor:
        print ' you have to give at least an input directory and a condor submission file.'
        parser.print_usage()
        print '... exiting'
        exit(1)

    rootfiles = [os.path.abspath(options.indir+'/'+i) for i in os.listdir(options.indir) if '.root' in i]

    rerunList = []
    goodList  = []

    for rf in rootfiles:
        tmp_f = ROOT.TFile(rf, 'read')
        lok = tmp_f.GetListOfKeys()
        var = tmp_f.GetName().split('/')[-1].replace('.root','')
        allGood = True
        
        hasAll = 0
        for k in lok:
            if not var in k.GetName():
                continue
            if 'long'  in k.GetName():
                hasAll += 1
            if 'right' in k.GetName():
                hasAll += 1
            if 'left'  in k.GetName():
                hasAll += 1

        if hasAll < 3:
            allGood = False

        if not allGood:
            print 'bad variation', var, 'has number of keys', hasAll
            rerunList.append(var)
        else:
            goodList.append(var)

        tmp_f.Close()
            
        
    print 'found {n} good files'.format(n=len(goodList))
    print 'found {n} bad  files'.format(n=len(rerunList))

    cf = open(options.condor,'r')
    rl = cf.readlines()
    cf.close()

    newcf = open(cf.name.replace('.condor','_resub.condor'), 'w')

    for line in rl:
        writeLine = True
        if 'queue 1' in line:
            writeLine = False
        if not len(line.strip()):
            writeLine = False

        for var in goodList:
            sl = line.split()
            if '--sP' in line and sl[sl.index('--sP')+1] == var:
                writeLine = False

        if writeLine:
            newcf.write(line)
            if 'arguments' in line:
                newcf.write('queue 1\n\n')

    newcf.close()
    
    print newcf.name
