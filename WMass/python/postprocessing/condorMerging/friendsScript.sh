#!/bin/bash

## make local directory
echo 'i am in this directory'
echo $PWD

echo ls of this directory:
ls ./

export localMergeDir=${PWD}/friends_${3}_chunk${4}
echo making directory ${localMergeDir}
mkdir -p ${localMergeDir}


echo moving to cmssw directory ${1}

cd $1
## do cmsenv and go back
eval `scramv1 runtime -sh`

echo 'moving back to localMergingDirectory'
cd ${localMergeDir}

echo 'will run the copy and running of friend trees'
eos cp -r ${2}/ .

echo done copying, this is the content of the localMergeDir:
ls ./


## run the actual command
export localOutDir=tmp_friends_out

echo running command: python ${1}/src/CMGTools/WMass/python/postprocessing/postproc_batch.py ./ ${localOutDir} -d ${3} -N ${5} -c ${4} --friend


mkdir -p ${localOutDir}
python ${1}/src/CMGTools/WMass/python/postprocessing/postproc_batch.py ./ ${localOutDir} -d ${3} -N ${5} -c ${4} --friend

echo 'making output directory (if it does not exist)'
echo eos mkdir -p ${6}
eos mkdir ${6}

echo this is in ${localOutDir}
ls  ${localOutDir}
#eos cp ${PWD}/${localOutDir}/tree_Friend_${3}.chunk${4}.root ${6}/
eos cp ${PWD}/${localOutDir}/tree_Friend_${3}*.root ${6}/

echo i think i am done...

