import ROOT, commands, os, sys, optparse

parser = optparse.OptionParser(usage='usage: %prog [opts] ', version='%prog 1.0')
parser.add_option('-p', '--part'     , type=int, default=0 , help='number of the part we\'re doing')
parser.add_option(      '--skipCheck',           default=False, help='skip check of the file\'s integrity [%default]', action='store_true')
parser.add_option('-d', '--dirs'     , type=str, default='', help='comma separated list of the directories to copy and run hadd on')
parser.add_option('-o', '--targetdir', type=str, default='', help='target directory for the output')
(options, args) = parser.parse_args()


dirsToCopy = options.dirs.split(',')

## copy the directories into the nodes folder
print 'STATUS: copying the directory structure onto worker node'
for d in dirsToCopy:
    os.system('cp -r {d} . '.format(d=d))

if not options.skipCheck:

    ## running cmgListChunks to check for incomplete directories
    print 'STATUS: checking for failed directories with cmgListChunksToResub'
    missing = commands.getoutput('cmgListChunksToResub -q HTCondor ./ ')

    ## make a list of incomplete directories and remove those
    print 'STATUS: removing the chunks that don not have a file'
    missingChunks = [i.split()[-1] for i in missing.split('\n') if 'Chunk' in i]

    print 'found missing chunks and will remove them:'
    for i in missingChunks:
        print '\t\t removing chunk', i
        cmd= 'rm -rf {i}'.format(i=i)
        os.system('{c}'.format(c=cmd))
    
else:
    print 'STATUS: No check of the integrity has been performed: i trust you did it before calling me'

## get the files from eos
print 'STATUS: getting the files from eos and putting them in place'

prod = 'treeProducerWMass'
cmds = []

for i in os.listdir('./'):
    if not 'Chunk' in i: continue
    tmp_filelocation = open(i+'/'+prod+'/tree.root.url')
    tmp_filelocation = tmp_filelocation.readlines()[0]
    tmp_file = tmp_filelocation.replace('\n','')
    cmds.append('eos cp {tf} {i}/{p}/tree.root'.format(tf=tmp_file, i=i, p=prod))

for ic,cmd in enumerate(cmds):
    print 'at copy {i} of {j}'.format(i=ic+1,j=len(cmds))
    os.system('{c}'.format(c=cmd))
        
## running haddChunks.py

print 'STATUS: running haddChunks command:'
haddCmd = 'haddChunks.py -c ./'
os.system('{hc}'.format(hc=haddCmd))

## renaming the output directory and copying to target directory
print 'STATUS: renaming the output directory and copying (with xrdcopy) the output back to eos'

dirname = [i for i in os.listdir('./') if not 'Chunk' in i and os.path.isdir(i) ][0] ## this should be the only directory in here now
newdirname = dirname+'_part{p}'.format(p=options.part)
os.system('mv {d} {nd}'.format(d=dirname, nd=newdirname))
os.system('eos cp -r {pwd}/{nd}/ {td}/'.format(pwd=os.environ['PWD'], nd=newdirname, td=options.targetdir))

## writing a little summary
print 'STATUS: done merging, will write summary'
summary_fn = 'mergeSummary_{nd}.txt'.format(nd=newdirname)
summary = open(summary_fn,'w')
summary.write('## this part {nd}\n'.format(nd=newdirname))
summary.write('## merged the following chunks:\n')
for i in dirsToCopy:
    summary.write(i+'\n')
summary.close()

os.system('eos cp {s} {td}'.format(s=summary_fn,td=options.targetdir))

print 'STATUS: DONE!'
