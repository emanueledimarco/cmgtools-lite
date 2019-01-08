#! /bin/bash

# this script is a wrapper for the commands used to compute and pack the fake rate
# it should be run from lxplus to use ntuples on eos (the skimmed ntuples are on pccmsrm28), the check is made below

#
plotterPath="${CMSSW_BASE}/src/CMGTools/WMass/python/plotter"
lumi_full2016="35.9" # this is the value reported in https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM
lumi_full2016_json="31.3" # 31.351 with brilcalc using option --normtag:
lumi_2016BF="19.7"  # to be checked, but we will never use it probably 
#
######################
# options to set
######################
#--------------------------
# choose the dataset to use (2016 B to F or 2016 B to H)
useSignedEta="y" # distinguish bins of positive and negative rapidity (if passing binning with just positive values below, it will just skip the negative, so you are actually using half statistics)
useFull2016dataset="y"
useJson="n"
useSkimmedTrees="y" 
usePickle="n" # add option --usePickle when running mcAnalysis.py, some old ntuples miss the histogram with the SumWeights
#--------------------------
mtRanges="0,25,25,120"  # can stay as it is, was used with the 2-mT-region method, unless I change the fake rate script, leave it as it is: it is a dummy option
ptDefinition="pt_granular"  # pt_coarse, pt_granular (first is mainly for QCD MC)
#ptDefinition="pt_coarse"
#-------------------------

if [[ "${useFull2016dataset}" == "y" ]]; then
    lumi="${lumi_full2016}"
    if [[ "${useJson}" == "y" ]]; then
	lumi="${lumi_full2016_json}"
    fi
else
    lumi="${lumi_2016BF}"
fi


istest="y"
# following option testdir is used only if istest is 'y'
today=`date +"%d_%m_%Y"`
testdir="testFRv8/fr_${today}_eta_${ptDefinition}_mT40_${lumi/./p}fb_signedEta_subtrAllMC_L1EGprefire_jetPt30_Zveto_newSkim"
######################
######################
# additional options to be passed to w-helicity-13TeV/make_fake_rates_data.py
# can pass a new cut as you would do with mcPlots.py 
#addOption=" -A eleKin pfmet 'met_pt<20' -R HLT_SingleEL HLT_Ele27 'HLT_BIT_HLT_Ele27_WPTight_Gsf_v == 1'"
#addOption=" -A eleKin pfmet 'met_pt<20' -A eleKin tightcharge 'LepGood1_tightChargeFix == 2'"
#addOption=" -A eleKin pfmet 'met_pt<20' -A eleKin pfmtLess40 'mt_2(met_pt,met_phi,ptElFull(LepGood1_calPt,LepGood1_eta),LepGood1_phi) < 40'"
#addOption=" -A eleKin pfmet 'met_pt<20' -A eleKin awayJetPt 'LepGood_awayJet_pt > 45' "
#addOption=" -A eleKin pfmet 'met_pt<20' "
#addOption=" -A eleKin json 'isGoodRunLS(isData,run,lumi)' -A eleKin pfmtLess40 'mt_2(met_pt,met_phi,ptElFull(LepGood1_calPt,LepGood1_eta),LepGood1_phi) < 40' "
#addOption=" -A eleKin pfmtLess40 'mt_2(met_pt,met_phi,ptElFull(LepGood1_calPt,LepGood1_eta),LepGood1_phi) < 40' -A eleKin awayJetPt 'LepGood_awayJet_pt > 45' "
addOption=" -A eleKin pfmtLess40 'mt_2(met_pt,met_phi,ptElFull(LepGood1_calPt,LepGood1_eta),LepGood1_phi) < 40' -A eleKin zveto 'fabs(100 - mass_2(LepGood_awayJet_pt,LepGood_awayJet_eta,LepGood_awayJet_phi,0,ptElFull(LepGood1_calPt,LepGood1_eta),LepGood1_eta,LepGood1_phi,0.000511)) > 10' "
# for the Z veto, see plots here:
# http://mciprian.web.cern.ch/mciprian/wmass/13TeV/distribution/TREES_1LEP_80X_V3_FRELSKIM_V8/FR_computation_region/full2016data_01_11_2018_FRvarNotNorm/


if [[ "${useJson}" == "y" ]]; then
    addOption="${addOption} -A eleKin json 'isGoodRunLS(isData,run,lumi)'"
fi

# check we are on lxplus  
host=`echo "$HOSTNAME"`
# if [[ "${useSkimmedTrees}" == "y" ]]; then
#     if [[ ${host} != *"pccmsrm28"* ]]; then
# 	echo "Error! You must be on pccmsrm28 to use skimmed ntuples. Do ssh -XY pccmsrm28 and work from a release."
# 	return 0
#     fi
# elif [[ ${host} != *"lxplus"* ]]; then
#   echo "Error! You must be on lxplus. Do ssh -XY lxplus and work from a release."
#   return 0
# fi

srtreeoption=""

if [[ "${istest}" == "y" ]]; then
    testoption=" --test ${testdir}/ "
fi

cmdComputeFR="python ${plotterPath}/w-helicity-13TeV/make_fake_rates_data.py --qcdmc  ${testoption} --fqcd-ranges ${mtRanges} --pt ${ptDefinition} --lumi ${lumi}"
if [[ "${useFull2016dataset}" == "y" ]]; then
    cmdComputeFR="${cmdComputeFR} --full2016data "
fi

if [[ "${useSkimmedTrees}" == "y" ]]; then
    cmdComputeFR="${cmdComputeFR} --useSkim "
fi

if [[ "${usePickle}" == "y" ]]; then
    cmdComputeFR="${cmdComputeFR} --usePickle "
fi

if [[ "${useSignedEta}" == "y" ]]; then
    cmdComputeFR="${cmdComputeFR} --useSignedEta "
fi

if [[ "X${addOption}" != "X" ]]; then
    cmdComputeFR="${cmdComputeFR} --addOpts \"${addOption}\" "
fi

echo "Running: ${cmdComputeFR}"
echo "${cmdComputeFR} > commands4fakeRate.sh" | bash
#echo "${cmdComputeFR} > commands4fakeRate.sh" | bash
echo "The commands used for fake-rate are stored in commands4fakeRate.sh"
cat commands4fakeRate.sh | grep python | bash  # here we really run the commands saved in commands4fakeRate.sh
echo "Copying commands4fakeRate.sh in ${plotterPath}/plots/fake-rate/test/${testdir}"
cp commands4fakeRate.sh ${plotterPath}/plots/fake-rate/test/${testdir}
