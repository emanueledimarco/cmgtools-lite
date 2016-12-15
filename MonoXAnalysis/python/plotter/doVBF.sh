#! /bin/bash

uptothiscut="deta2j"
var4shape="mjj_fullsel"
var="mjj"
fitdir="mjj_mjj1000_deta3p5_dphijm2p0"  # name of dir that contains the output

lumi="12.9"
storeDir="VBF_shape_study_12p9fb"         # name of directory containing all the tests you would do. You can specify the luminosity used in the name
 

other_options_make_cards=""  # "1bin" for cut and count like test, otherwise keep empty for shape analysis with many bins

combinedir="/afs/cern.ch/work/m/mciprian/combine/CMSSW_7_4_7/src/HiggsAnalysis/CombinedLimit/myTest/${storeDir}/${fitdir}"  # dir where you run combine
plotterDirPath="${CMSSW_BASE}/src/CMGTools/MonoXAnalysis/python/plotter"
wwwPath="${HOME}/www/vbfHiggsToInv/80X/heppy"   # web cern directory to store outputs at the end

#analysis_addCut=" -A skim ICHEP_DATA 'run < 276811 || !isData'"
analysis_addCut=""
# -R deta2j deta2j 'abs(JetClean1_eta-JetClean2_eta) > 3.5'
# -R dphijm dphijm 'abs(dphijm) > 2.0 && abs(dphijm) < 3.15'
# -R mass2j mass2j 'mass_2(JetClean1_pt,JetClean1_eta,JetClean1_phi,0.,JetClean2_pt,JetClean2_eta,JetClean2_phi,0.) > 500'
#analysis_changeCut=" -R mass2j mass2j 'mass_2(JetClean1_pt,JetClean1_eta,JetClean1_phi,0.,JetClean2_pt,JetClean2_eta,JetClean2_phi,0.) > 500' -R deta2j deta2j 'abs(JetClean1_eta-JetClean2_eta) > 3.5' "
analysis_changeCut=" -R deta2j deta2j 'abs(JetClean1_eta-JetClean2_eta) > 3.5' -R dphijm dphijm 'abs(dphijm) > 2.0 && abs(dphijm) < 3.15' "
analysis_excludeCut=""
analysis_cutOptions=" ${analysis_changeCut} ${analysis_addCut} ${analysis_excludeCut} " # use this to pass options to analysis.py, such as -R, -X etc...
#analysis_cutOptions=""

test -d templates/ && rm -r templates/

# Warning
# when you launch a python script from bash, if you pass options that need more than 1 argument, such as -A and -R for analysis.py, do NOT do the following:
#script.py -A ${string_with 3arguments} -R ${string_with_3arguments}
# because ${string_with_3arguments} will be interpreted as a single argument passed to python
# Instead, you MUST do one of the following (it works, but probably there are other ways)
# 1) echo "script.py -A ${string_with 3arguments} -R ${string_with_3arguments}" | bash
# this will print the command as a string and redirect to bash, i.e, executing it
# 2) command="script.py -A ${string_with 3arguments} -R ${string_with_3arguments}" ; eval ${command}
# some people says eval is dangerous for security reason depending on what you pass to it ( ... bah! ...)

#vbfdm/analysis.py --fullControlRegions -d --pdir templates/ -U ${uptothiscut} -l ${lumi} -A skim ICHEP_DATA 'run < 276811 || !isData' -R deta2j deta2j 'abs(JetClean1_eta-JetClean2_eta) > 3.5'

# here we use echo "$command" | bash
echo "vbfdm/analysis.py --fullControlRegions --pdir templates/ -U ${uptothiscut} -l ${lumi} ${analysis_cutOptions}" | bash
echo "vbfdm/analysis.py --propSystToVar ${var4shape} -U ${uptothiscut} -l ${lumi} ${analysis_cutOptions}" | bash
echo "vbfdm/analysis.py --tF ${var4shape} -U ${uptothiscut} -l ${lumi} ${analysis_cutOptions}" | bash

# here we use eval $command
yieldsInSR_command="python mcAnalysis.py vbfdm/mca-80X-sync.txt vbfdm/vbfdm.txt -P /u2/emanuele/TREES_MET_80X_V4 --s2v -j 6 -G -F mjvars/t \"/u2/emanuele/TREES_MET_80X_V4/friends_SR/evVarFriend_{cname}.root\" --FMC sf/t \"/u2/emanuele/TREES_MET_80X_V4/friends/sfFriend_{cname}.root\" -W 'puw*SF_trigmetnomu*SF_BTag*SF_NLO_QCD*SF_NLO_EWK' -X trigger -f --xp 'data' -l ${lumi} ${analysis_cutOptions}"
echo "${yieldsInSR_command}" | bash  > templates/SRyields.txt
echo ""


source vbfdm/make_cards.sh templates/cards ${lumi} ${uptothiscut} ${var} all ${other_options_make_cards}

cd ${plotterDirPath}/templates/cards/${uptothiscut}/${var4shape}/125.0/
combineCards.py SR=vbfdm.card.txt ZM=zmumu.card.txt ZE=zee.card.txt WM=wmunu.card.txt WE=wenu.card.txt > comb.card.txt

mkdir -p ${combinedir}
cp ${plotterDirPath}/templates/cards/${uptothiscut}/${var4shape}/125.0/* ${combinedir}/

cd ${combinedir}
eval `scramv1 runtime -sh`
combine -M Asymptotic comb.card.txt --run expected 2>&1 >> log_combine.txt  # probably not all the output will be put in the file, don't know why
# appending more info in file doesn't work, still trying to understand it. For now, just put the output for limit (previous command)
#echo " " >> log_combine.txt 2>&1
#echo " " >> log_combine.txt 2>&1
combine -M MaxLikelihoodFit --saveNormalizations --saveShapes --saveWithUncertainties comb.card.txt #>> log_combine.txt 2>&1

cp ${combinedir}/* ${plotterDirPath}/templates/cards/${uptothiscut}/${var4shape}/125.0/

cd  ${plotterDirPath}/
eval `scramv1 runtime -sh`
source doAllRegionPostFit.sh ${uptothiscut} ${var4shape} ${lumi} "${analysis_cutOptions}"

mkdir -p ${wwwPath}/${storeDir}/${fitdir}/
cp -r templates/ ${wwwPath}/${storeDir}/${fitdir}/