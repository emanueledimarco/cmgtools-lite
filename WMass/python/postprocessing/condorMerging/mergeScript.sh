#!/bin/bash

## make local directory
echo 'i am in this directory'
echo $PWD

echo ls of this directory:
ls ./

export localMergeDir=${PWD}/mergeDirPart${2}
echo making directory ${localMergeDir}
mkdir -p ${localMergeDir}


echo moving to cmssw directory ${1}

cd $1
## do cmsenv and go back
eval `scramv1 runtime -sh`

echo 'moving back to localMergingDirectory'
cd ${localMergeDir}

echo 'making output directory (if it does not exist)'
echo mkdir -p $4
##mkdir -p $4
eos mkdir $4


skipCheckOPT=""
if [ "$5" == "True" ]; then
    skipCheckOPT="--skipCheck"
fi

echo 'will run the full merge python script'
python ../fullMergeTrees.py -p $2 -d $3 -o $4 ${skipCheckOPT}
