import os
from datetime import datetime

PROG         = 'w-helicity-13TeV/make_helicity_cards.py'
BASECONFIG   = 'w-helicity-13TeV/wmass_mu'
MCA          = BASECONFIG+'/mca-wmu-helicity.txt'
CUTFILE      = BASECONFIG+'/cuts_wmu.txt'
SYSTFILE     = BASECONFIG+'/systsEnv.txt'
#TREEPATH     = '/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_latest_new_1muskim/'
#TREEPATH     = '/eos/cms/store/cmst3/group/wmass/w-helicity-13TeV/trees/SKIMS_muons_latest/'
TREEPATH     = '/afs/cern.ch/work/m/mdunser/public/wmassTrees/SKIMS_muons_latest/'
QUEUE        = '2nd'
VAR          = '\'ptMuFull(LepGood1_calPt,LepGood1_eta):LepGood1_eta\''

## old variable binning in eta
## old binning binsEta = list(i*0.1 for i in range(1,11)) + list(1.+0.15*i for i in range(1,9))
## old binning negstring = '[-2.4,'+','.join(reversed(  list(str(-1.*i) for i in binsEta) ))
## old binning posstring =     ','.join(           list(str(    i) for i in binsEta) )+',2.4]'
## old binning etabinning= negstring+',0.,'+posstring

binningeta = [-2.4 + i*0.1 for i in range(49) ]
binningeta = [float('{a:.3f}'.format(a=i)) for i in binningeta]

etabinning = '['+','.join('{a:.1f}'.format(a=i) for i in binningeta)+']'

## variable binning in pt
ptbinning = '['+','.join(str(i) for i in range(26,46))+']'

BINNING      = '\''+etabinning+'*'+ptbinning+'\''
WEIGHTSTRING = ' \'puw2016_nTrueInt_36fb(nTrueInt)*LepGood_SF1[0]*LepGood_SF2[0]\' '
OUTDIR       = 'helicity_%s' % datetime.now().strftime('%Y_%m_%d')

components=[' -b ', ' -s ']
components=[' -b ']
    

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options]')
    parser.add_option('-d', '--dry-run', dest='dryRun',   action='store_true', default=False, help='Do not run the job, only print the command');
    parser.add_option('-s', '--suffix', dest='suffix', type='string', default=None, help='Append a suffix to the default outputdir (helicity_<date>)');
    parser.add_option("--syst", dest="addSyst", action="store_true", default=False, help="Add PDF systematics to the signal (need incl_sig directive in the MCA file)");
    parser.add_option("--long-bkg", dest="longBkg",    action="store_true", default=False, help="Treat the longitudinal polarization as one background template.");
    parser.add_option("--genw", action="store_true", default=False, help="use genw (dressed leptons) instead of prefsrw.");
    (options, args) = parser.parse_args()
    
    if options.suffix: OUTDIR += ('_%s' % options.suffix)

    for c in components:
        cmd='python ' + ' '.join([PROG,MCA,CUTFILE,VAR,BINNING,SYSTFILE,OUTDIR,'-C mu']) + \
            (' -W %s ' % WEIGHTSTRING) + (' -P %s ' % TREEPATH) + (' -q %s ' % QUEUE) + c
        if options.dryRun: cmd += '  --dry-run '
        if options.addSyst: cmd += '  --pdf-syst --qcd-syst '
        if options.longBkg: cmd += ' --long-bkg '
        if not options.genw: cmd += ' --wvar prefsrw '
        cmd += ' -g 5 '
        os.system(cmd)
