#! /bin/bash

# lumi = 35.9/fb if using run2016 B to H, otherwise it is 19.3
# check in mca file which MC is being used for Z, amc@NLO, madgraph or powheg
# selection and mca of fake rate to see how plots look like

# This script prints the commands to produce plots or send jobs to manage the production 

echo ""
plotterPath="${CMSSW_BASE}/src/CMGTools/WMass/python/plotter"

#####################################################
# some selections (other customizable options start below)
# cuts are added after eleKin selection step (check in the cut file, could use also a dummy step like alwaystrue)
#####################################################

#ptcorr="ptElFull(LepGood1_pt,LepGood1_eta,LepGood1_phi,LepGood1_r9,run,isData,evt)"
#ptcorr="LepGood1_calPt"
ptcorr="ptElFull(LepGood1_calPt,LepGood1_eta)"

inEB=" -A eleKin EB 'abs(LepGood1_eta) < 1.479' "
inEE=" -A eleKin EE 'abs(LepGood1_eta) > 1.479' "

not_pass_tightWP="-A eleKin not-fullTightID 'LepGood1_tightId < 3 || if3(abs(LepGood1_eta)<1.479,LepGood1_relIso04EA > 0.0588 || abs(LepGood1_dz) > 0.1 || abs(LepGood1_dxy) > 0.05, LepGood1_relIso04EA > 0.0571 || abs(LepGood1_dz) > 0.2 || abs(LepGood1_dxy) > 0.1) || LepGood1_lostHits > 1 || LepGood1_convVeto == 0'"

not_pass_mediumWP="-A eleKin not-fullMediumID 'LepGood1_tightId < 2 || if3(abs(LepGood1_eta)<1.479,LepGood1_relIso04EA > 0.0695 || abs(LepGood1_dz) > 0.1 || abs(LepGood1_dxy) > 0.05, LepGood1_relIso04EA > 0.0821 || abs(LepGood1_dz) > 0.2 || abs(LepGood1_dxy) > 0.1) || LepGood1_lostHits > 1 || LepGood1_convVeto == 0'"

not_pass_mediumWP_iso0p2="-A eleKin not-fullMediumID 'LepGood1_tightId < 2 || if3(abs(LepGood1_eta)<1.479,LepGood1_relIso04EA > 0.2 || abs(LepGood1_dz) > 0.1 || abs(LepGood1_dxy) > 0.05, LepGood1_relIso04EA > 0.2 || abs(LepGood1_dz) > 0.2 || abs(LepGood1_dxy) > 0.1) || LepGood1_lostHits > 1 || LepGood1_convVeto == 0'"

not_pass_mediumWP_iso0p15="-A eleKin not-fullMediumID 'LepGood1_tightId < 2 || if3(abs(LepGood1_eta)<1.479,LepGood1_relIso04EA > 0.15 || abs(LepGood1_dz) > 0.1 || abs(LepGood1_dxy) > 0.05, LepGood1_relIso04EA > 0.15 || abs(LepGood1_dz) > 0.2 || abs(LepGood1_dxy) > 0.1) || LepGood1_lostHits > 1 || LepGood1_convVeto == 0'"

not_pass_looseWP="-A eleKin not-fullLooseID 'LepGood1_tightId < 1 || if3(abs(LepGood1_eta)<1.479,LepGood1_relIso04EA > 0.0994 || abs(LepGood1_dz) > 0.1 || abs(LepGood1_dxy) > 0.05, LepGood1_relIso04EA > 0.107 || abs(LepGood1_dz) > 0.2 || abs(LepGood1_dxy) > 0.1) || LepGood1_lostHits > 1 || LepGood1_convVeto == 0'"

not_pass_looseWP_iso0p2="-A eleKin not-fullLooseID 'LepGood1_tightId < 1 || if3(abs(LepGood1_eta)<1.479,LepGood1_relIso04EA > 0.2 || abs(LepGood1_dz) > 0.1 || abs(LepGood1_dxy) > 0.05, LepGood1_relIso04EA > 0.2 || abs(LepGood1_dz) > 0.2 || abs(LepGood1_dxy) > 0.1) || LepGood1_lostHits > 1 || LepGood1_convVeto == 0'"

# use bult-in functions in functions.cc, which automatically select EB or EE, manage cuts and so on
#FRnumSel=" -A eleKin FRnumSel 'pass_FakerateNumerator2016((abs(LepGood1_eta)<1.479),LepGood1_tightId,LepGood1_dxy,LepGood1_dz,LepGood1_lostHits,LepGood1_convVeto,LepGood1_relIso04EA)' "
#notFRnumSel="-A eleKin failFRnumSel 'pass_FakerateApplicationRegion2016(abs(LepGood1_eta)<1.479,LepGood1_tightId,LepGood1_dxy,LepGood1_dz,LepGood1_lostHits,LepGood1_convVeto,LepGood1_relIso04EA)' "

# use variables in friend trees, which were filled with the conditions to pass the ID+iso (the one we decided to use at the moment)
FRnumSel=" -A eleKin FRnumSel 'LepGood1_customId == 1 && LepGood1_tightChargeFix == 2' "  #looseID + iso<0.2 in EB, medium ID in EE
#FRnumSel=" -A eleKin FRnumSel 'pass_FakerateNumerator_loose2016(fabs(LepGood1_eta)<1.479,LepGood1_tightId,LepGood1_dxy,LepGood1_dz,LepGood1_lostHits,LepGood1_convVeto,LepGood1_relIso04EA)' "
#FRnumSel=" -A eleKin FRnumSel 'pass_FakerateNumerator_medium2016(fabs(LepGood1_eta)<1.479,LepGood1_tightId,LepGood1_dxy,LepGood1_dz,LepGood1_lostHits,LepGood1_convVeto,LepGood1_relIso04EA)' "

notFRnumSel="-A eleKin failFRnumSel 'LepGood1_customId == 0 || LepGood1_tightChargeFix != 2' " #looseID + iso<0.2 in EB, medium ID in EE
#notFRnumSel="-A eleKin failFRnumSel ' !pass_FakerateNumerator_loose2016(fabs(LepGood1_eta)<1.479,LepGood1_tightId,LepGood1_dxy,LepGood1_dz,LepGood1_lostHits,LepGood1_convVeto,LepGood1_relIso04EA)' "
#notFRnumSel="-A eleKin failFRnumSel ' !pass_FakerateNumerator2016(fabs(LepGood1_eta)<1.479,LepGood1_tightId,LepGood1_dxy,LepGood1_dz,LepGood1_lostHits,LepGood1_convVeto,LepGood1_relIso04EA)' "

#Wsel="-A eleKin WregionSel 'ptElFull(LepGood1_calPt,LepGood1_eta) > 30 && ptElFull(LepGood1_calPt,LepGood1_eta) < 45'"
Wsel="-A eleKin WregionSel 'ptElFull(LepGood1_calPt,LepGood1_eta) > 30'"
#HLT27sel="-R HLT_SingleEL HLT_Ele27 'HLT_BIT_HLT_Ele27_WPTight_Gsf_v == 1'"

mtCutApplControlRegion="-A eleKin pfmt 'mt_2(met_pt,met_phi,${ptcorr},LepGood1_phi) < 30'"
mtCutApplSignalRegion="-A eleKin pfmt 'mt_2(met_pt,met_phi,${ptcorr},LepGood1_phi) > 40'"
mtCutApplSignalRegion=""
metCutApplSignalRegion="-A eleKin met30 'met_pt > 30'"
#WselFull="-A eleKin WregionSel 'ptElFull(LepGood1_calPt,LepGood1_eta) > 30 && ptElFull(LepGood1_calPt,LepGood1_eta) < 45 && mt_2(met_pt,met_phi,${ptcorr},LepGood1_phi) > 40' -A eleKin fiducial 'abs(LepGood1_eta)<1.4442 || abs(LepGood1_eta)>1.566' "
fiducial=" -A eleKin fiducial 'abs(LepGood1_eta)<=1.4442 || abs(LepGood1_eta)>=1.566' "
json_L1_HLT27=" -A eleKin json 'isGoodRunLS(isData,run,lumi)' "
ptMin=" -A eleKin ptMin 'ptElFull(LepGood1_calPt,LepGood1_eta) >= XX' "
ptMax=" -A eleKin ptMax 'ptElFull(LepGood1_calPt,LepGood1_eta) <= XX' "
mtMin=" -A eleKin pfmt 'mt_2(met_pt,met_phi,${ptcorr},LepGood1_phi) >= XX' "
mtMax=" -A eleKin pfmt 'mt_2(met_pt,met_phi,${ptcorr},LepGood1_phi) <= XX' "
WselFull=" ${mtMin/XX/40} ${ptMax/XX/45} ${fiducial} "
WselAllpt=" ${mtMin/XX/40} ${fiducial} "
mtMinSmear=" -A eleKin pfmt_smear 'mt_2(getSmearedVar(met_pt,0.2,evt,isData),met_phi,${ptcorr},LepGood1_phi) >= XX' "

##############################################################
##############################################################

# Here we have some options to be customized

##################################
##################################
# Some general options
##################################
# luminosity settings
lumi_full2016="35.9" # this is the value reported in https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM
lumi_full2016_json="31.3" # 31.351 with brilcalc using option --normtag:
lumi_2016BF="19.7" # to be checked, but we will never use it probably
useDataGH="y"
useJson="n"
#useWinclusive="n" # do not distinguish W, W->tau, flips, not it is set for each region
luminosity=""
if [[ "${useDataGH}" == "y" ]]; then
    luminosity="${lumi_full2016}"
    if [[ "${useJson}" == "y" ]]; then
	luminosity="${lumi_full2016_json}"
    fi
else
    luminosity="${lumi_2016BF}"
fi

#useHLTpt27="y" # already in selection txt file
runBatch="y"
queueForBatch="cmscaf1nd"
nameTag="_testTreeAFS" 
#nameTag="_varStudy"
useLessMC="n"
useSkimmedTrees="y" # skimmed samples are on both pccmsrm28 and eos 
usePtCorrForScaleFactors="n" # y: use corrected pt for scale factor weight; n: use LepGood_pt (which is what would have been used if the scale factors where in a friend tree)
# eta bin boundaries to divide regions in eta
#etaBinBoundaries=("0.0" "1.479" "2.1" "2.5")
#etaBinBoundaries=("0.0" "1.479" "2.5")
#etaBinBoundaries=("0.0" "0.2" "0.4" "0.6" "0.8" "1.0" "1.2" "1.4442" "1.566" "1.7" "1.9" "2.1" "2.3" "2.5")
#etaBinBoundaries=("2.1" "2.3")
etaBinBoundaries=("0.0" "2.5")
#etaBinBoundaries=("0.0" "1.0" "1.479" "2.1" "2.5")
#etaBinBoundaries=("0.0" "1.0")
today=`date +"%d_%m_%Y"`
batchDirName="plots_${today}${nameTag}"  # name of directory to create inside jobsLog
##################################
##################################
# MCA files
##################################
if [[ "${useLessMC}" == "y" ]]; then
    mcafile="mca-80X_forPlots_lessMC.txt"
else
    mcafile="mca-80X_forPlots.txt"
fi
cutfile="qcd1l_SRtrees.txt" # we start from it and add or remove cuts
plotfile="test_plots.txt"
# following 2 are used depending on the used trees because the samples are named differently
mcafileFRskim="mca-80X_V5_FRskim.txt"  # with the above mcafile this should not be needed anymore
#mcafileTINY="mca-80X_V5_TINY.txt"      # with the above mcafile this should not be needed anymore
mcafileFRclosureMC="mca-80X-qcdClosureTest.txt"  # for FR closure test based on MC
#
##################################
##################################
# Some MCA options
##################################
# QCD and data_fakes are tipically exclusive (unless one wants to compare them)
# they are excluded depending on whether the fake rate is used or not
#excludeprocesses="data,Z_LO,W_LO,Top,DiBosons,TauDecaysW,WFlips"
excludeprocesses="Z_LO,W_LO" # decide whether to use NLO (amc@NLO) or LO (MadGraph) MC, non both! In case you can add other samples (Top, Dibosons) to speed up things
#selectprocesses="W"
#selectprocesses="QCD"
#selectplots=""  # if empty it uses all plots in cfg file
#selectplots="nJetClean,ptl1,etal1,pfmet,tkmet,ele1ID,awayJet_pt,wpt_tk,ele1dxy"  # if empty it uses all plots in cfg file
#selectplots="ptl1,etal1,pfmet,trkmt_trkmetEleCorr,pfmt,wpt_tk,nJetClean,ele1Iso04,ele1ID"  # if empty it uses all plots in cfg file
#selectplots="trkmt_trkmetEleCorr_dy,trkmetEleCorr_dy"
#selectplots="etal1_binFR"
#selectplots="unrolled"
selectplots="etal1_binFR"
#selectplots="ptl1_wmass,pfmt_wmass"
#selectplots="ptl1,ptl1noCorr"
#selectplots="ptl1__etal1_binFR"
#selectplots="ptl1_granBin"
#selectplots="trkmt_trkmetEleCorr_dy"
#selectplots="mass_jet_ele"
#selectplots="ptl1,pfmt,awayJet_pt,awayJet_eta,mass_jet_ele"
#selectplots="awayJet_eta,mt_jet_ele,dphiLepAwayJet,detaLepAwayJet"
#selectplots="ptl1noCorr_granBin"
#selectplots="dphiLepPFMET,diffPt_lepPFMET,diffPt_lepPFMET_v2"
#maxentries="150000" # max int number is > 2*10^9
maxentries=""  # all events if ""
#
##################################
##################################
# to scale all mC to data use option --scaleBkgToData <arg> many tmes for every process 
# you also need not to have any process defined as signal
#scaleAllMCtoData="" # if "", nothing is added to mcPlots.py command
#scaleAllMCtoData="--fitData" # keep commented, it is now set independently for each region 
#scaleAllMCtoData=" --scaleBkgToData QCD --scaleBkgToData W --scaleBkgToData Z --scaleBkgToData Top --scaleBkgToData DiBosons " # does not seem to work as expected
plottingMode="" # stack (default), nostack, norm (can leave "" for stack, otherwise " --plotmode <arg> ")

#ratioPlotDataOptions=" --plotmode norm --contentAxisTitle 'arbitrary units' "
ratioPlotDataOptions="--showRatio --maxRatioRange 0.8 1.2 --fixRatioRange " #--ratioDen background --ratioNums data,data_noJson --ratioYLabel 'data/MC' --sp data_noJson --noStackSig --showIndivSigs"
ratioPlotDataOptions_MCclosureTest="--showRatio --maxRatioRange 0.0 2.0 --fixRatioRange --ratioDen QCD --ratioNums QCDandEWK_fullFR,QCD_fakes --ratioYLabel 'FR/QCD' "

#############################
# Now we declare some dictionary in bash
# Note that the key should not have spaces between square brakets and quotes, otherwise the spaces are interpreted as part of the key
# this is important if you loop on the keys like the following (which is the recommended way):
# for region in "${!regionKey[@]}"; do something with dictionary; done
# In this case the quotes around ${!regionKey[@]} should remove the spaces, i.e. the keys would not match anymore if you declared things as regionKey[  "key"]
#
# Also, it seems that without =() at the end of declaration we add some empty keys
###############################
#echo "#CHECKPOINT 1"
declare -A regionKey=()
declare -A runRegion=()
declare -A regionName=()
declare -A skimTreeDir=()
declare -A outputDir=()
declare -A regionCuts=()
#declare -A processManager=()
declare -A qcdFromFR=()
declare -A scaleMCdata=()   
#############################
# Note:
# ---------------------------
# regionName must be unique because it distinguishes the output folder, which is currently built using regionName and outputDir
# FIXME: change the logic of the output folder naming convention
#############################
#############################
# COMPUTATION REGION
#----------------------------
regionKey["FRcompRegion"]="FRcompRegion"
runRegion["FRcompRegion"]="n"
regionName["FRcompRegion"]="FR_computation_region"
skimTreeDir["FRcompRegion"]="TREES_1LEP_80X_V3_FRELSKIM_V9"
#skimTreeDir["FRcompRegion"]="TREES_1LEP_80X_V3_WENUSKIM_V5_TINY"
outputDir["FRcompRegion"]="full2016data_${today}"
regionCuts["FRcompRegion"]=" ${mtMax/XX/40}  ${ptMin/XX/30}"  #${fiducial}"  " -A eleKin pfmt 'mt_2(met_pt,met_phi,${ptcorr},LepGood1_phi) < 40' " 
#processManager["FRcompRegion"]=" --xp W,WFlips,TauDecaysW "
qcdFromFR["FRcompRegion"]="n"
scaleMCdata["FRcompRegion"]=" -p data,QCD,W,Z,Top,DiBosons --canvasSize 800 600 "
#
#############################
#############################
# COMPUTATION REGION (numerator)
#----------------------------
regionKey["FRcompNumRegion"]="FRcompNumRegion"
runRegion["FRcompNumRegion"]="n"
regionName["FRcompNumRegion"]="FR_computationNumerator_region"
skimTreeDir["FRcompNumRegion"]="TREES_1LEP_80X_V3_FRELSKIM_V5"
outputDir["FRcompNumRegion"]="full2016data_${today}"
regionCuts["FRcompNumRegion"]=" -A eleKin pfmet20 'met_pt < 20' ${FRnumSel}"
#processManager["FRcompNumRegion"]=" --xp W,WFlips,TauDecaysW "
qcdFromFR["FRcompNumRegion"]="n"
scaleMCdata["FRcompNumRegion"]=""
#
#############################
#############################
# FR validation REGION
#----------------------------
regionKey["FRcheckRegion"]="FRcheckRegion"
runRegion["FRcheckRegion"]="y"
regionName["FRcheckRegion"]="FR_check_region"
#skimTreeDir["FRcheckRegion"]="TREES_electrons_1l_V6_TINY"
skimTreeDir["FRcheckRegion"]="TREE_4_XSEC_AFS"
outputDir["FRcheckRegion"]="full2016data_${today}"
regionCuts["FRcheckRegion"]=" -X nJet30 ${FRnumSel} ${fiducial} ${ptMax/XX/45} ${mtMax/XX/30}"
#processManager["FRcheckRegion"]=" --xp W,WFlips,TauDecaysW "
qcdFromFR["FRcheckRegion"]="y"
scaleMCdata["FRcheckRegion"]=" -p data,Wincl,EWK_bkg,TauDecaysW,data_fakes --scaleSigToData --sp data_fakes  " # --fitData
#
# --noLegendRatioPlot --canvasSize 3000 750 --setTitleYoffset 0.3
#
#############################
#############################
# APPLICATION REGION
#----------------------------
regionKey["FRapplRegion"]="FRapplRegion"
runRegion["FRapplRegion"]="n"
regionName["FRapplRegion"]="FR_application_region"
skimTreeDir["FRapplRegion"]="TREES_electrons_1l_V6_TINY"
outputDir["FRapplRegion"]="full2016data_${today}"
regionCuts["FRapplRegion"]=" -X nJet30 ${notFRnumSel} ${fiducial} "
#processManager["FRapplRegion"]=" --xp W,WFlips,TauDecaysW "
qcdFromFR["FRapplRegion"]="n"
scaleMCdata["FRapplRegion"]=" -p data,W,EWK_bkg_Full,QCD "
#
#############################
#############################
# WMASS SIGNAL REGION
#----------------------------
regionKey["WmassSignalRegion"]="WmassSignalRegion"
runRegion["WmassSignalRegion"]="n"
regionName["WmassSignalRegion"]="wmass_signal_region"
skimTreeDir["WmassSignalRegion"]="TREES_1LEP_80X_V3_WENUSKIM_V5"
outputDir["WmassSignalRegion"]="full2016data_${today}"
regionCuts["WmassSignalRegion"]=" -X nJet30 ${WselFull} ${FRnumSel} "
#processManager["WmassSignalRegion"]=" --xp Wincl "
qcdFromFR["WmassSignalRegion"]="y"
scaleMCdata["WmassSignalRegion"]="--fitData"
#
#############################
#############################
# WHELICITY SIGNAL REGION (avoid possibly all kinematic selections)
#----------------------------
regionKey["WhelicitySignalRegion"]="WhelicitySignalRegion"
runRegion["WhelicitySignalRegion"]="y"
regionName["WhelicitySignalRegion"]="whelicity_signal_region"
#skimTreeDir["WhelicitySignalRegion"]="TREES_1LEP_80X_V3_WSKIM_NEW" 
#skimTreeDir["WhelicitySignalRegion"]="TREES_electrons_1l_V6_TINY" 
skimTreeDir["WhelicitySignalRegion"]="TREE_4_XSEC_AFS" 
outputDir["WhelicitySignalRegion"]="full2016data_${today}"
regionCuts["WhelicitySignalRegion"]=" -X nJet30  ${fiducial} ${ptMax/XX/45} ${FRnumSel} ${mtMin/XX/40}" # "${WselAllPt} ${WselFull}" "${mtMinSmear/XX/40}"
qcdFromFR["WhelicitySignalRegion"]="y"
scaleMCdata["WhelicitySignalRegion"]=" -p data,W,data_fakes,Z,TauDecaysW,Top,DiBosons,WFlips  "
#scaleMCdata["WhelicitySignalRegion"]=" -p data_fakes  "
#scaleMCdata["WhelicitySignalRegion"]=" -p W  "
#--noLegendRatioPlot --canvasSize 3000 750 --setTitleYoffset 0.3" #--scaleSigToData --sp data_fakes " # --pg 'EWK := Wincl,Z,Top,Dibosons'
#
# data_fakes,Z,TauDecaysW,Top,DiBosons,WFlips
# 
#############################
#############################
# SIGNAL REGION before FR numerator (avoid possibly all kinematic selections, so to see what we get with the trigger)
#----------------------------
regionKey["SignalRegionDenominator"]="SignalRegionDenominator"
runRegion["SignalRegionDenominator"]="n"
regionName["SignalRegionDenominator"]="signal_region_denominator"
skimTreeDir["SignalRegionDenominator"]="TREES_1LEP_80X_V3_WENUSKIM_V5"
outputDir["SignalRegionDenominator"]="full2016data_${today}"
regionCuts["SignalRegionDenominator"]=" -X nJet30 ${mtMax/XX/40} ${FRnumSel} ${fiducial}"
#processManager["SignalRegionDenominator"]=" --xp Wincl "
qcdFromFR["SignalRegionDenominator"]="n"
scaleMCdata["SignalRegionDenominator"]=""
#
#############################
#############################
# FR closure in computation REGION
#----------------------------
regionKey["FRclosureCompRegion"]="FRclosureCompRegion"
runRegion["FRclosureCompRegion"]="n"
regionName["FRclosureCompRegion"]="FR_computationClosure_region"
skimTreeDir["FRclosureCompRegion"]="TREES_1LEP_80X_V3_FRELSKIM_V8" #"TREES_1LEP_80X_V3_WENUSKIM_V5_TINY"
outputDir["FRclosureCompRegion"]="full2016data_${today}"
regionCuts["FRclosureCompRegion"]=" ${mtMax/XX/40} ${FRnumSel} ${fiducial}"
#processManager["FRclosureCompRegion"]=" --xp W,WFlips,TauDecaysW "
qcdFromFR["FRclosureCompRegion"]="y"
scaleMCdata["FRclosureCompRegion"]=" -p data,data_fakes,Wincl,Z,Top,DiBosons "  # --scaleSigToData --sp data_fakes
#
#############################
#############################
# FR closure test with MC
#----------------------------
regionKey["FRclosureMC"]="FRclosureMC"
runRegion["FRclosureMC"]="n"
regionName["FRclosureMC"]="FR_ClosureTest_MC"
skimTreeDir["FRclosureMC"]="TREES_1LEP_80X_V3_WENUSKIM_V5_TINY"
outputDir["FRclosureMC"]="full2016data_${today}"
regionCuts["FRclosureMC"]=" -X nJet30 ${FRnumSel} ${WselFull} ${fiducial}"
#processManager["FRclosureMC"]=" --xp Wincl "
qcdFromFR["FRclosureMC"]="y"
scaleMCdata["FRclosureMC"]=""
#
#############################
#############################
# Some random plots, they are here to exploit the batch submission
#----------------------------
regionKey["TestPlots"]="TestPlots"
runRegion["TestPlots"]="n"
regionName["TestPlots"]="TestPlots"
skimTreeDir["TestPlots"]="TREES_electrons_1l_V6_TINY"
outputDir["TestPlots"]="sigRegion_${today}"
regionCuts["TestPlots"]=" -X nJet30  ${fiducial} ${mtMin/XX/40} ${FRnumSel} ${ptMax/XX/50}"
#processManager["TestPlots"]="  "
qcdFromFR["TestPlots"]="y"   # this is not used for this regino key
scaleMCdata["TestPlots"]=" -p W_nomi,W_mWup50,W_mWdn50 --canvasSize 900 600 --noErrorBarsOnRatio "
#----------------------------------
mcafileTest="mca-includes/mca-data-legacy2016_eras.txt"
#cutfileTest="wenu_80X.txt"
#optionsTest=" --plotmode nostack --xp data -p 'data_noJson,data_withJson' "
mcafileTest="${mcafile}" # "mca-80X-wchargeTest.txt" #${mcafile}"  #"mca-80X_V5_TINY_testJson.txt"
cutfileTest="${cutfile}"
#mcafileTest="mca-testFRnormSyst.txt"
ratioPlotDataOptions_TestPlots=" --showRatio --maxRatioRange 0.99 1.01 --fixRatioRange --ratioDen W_nomi --ratioNums W_mWup50,W_mWdn50 --ratioYLabel 'Var./Nomi.'"
#optionsTest=" --sp 'data_noJson' --xp 'data_withJson' --noStackSig  --showIndivSigs"  # --showIndivSigShapes or --showIndivSigs or --showSigShape
#ratioPlotDataOptions_TestPlots=" "
#optionsTest=" --sp 'dataAll' --plotmode norm -X json --noLegendRatioPlot"  # --showIndivSigShapes or --showIndivSigs or --showSigShape
#ratioPlotDataOptions_TestPlots=" --showRatio --maxRatioRange 0.5 1.5 --fixRatioRange --ratioDen data_fakes --ratioNums data_fakes_normUp,data_fakes_normDn --ratioYLabel 'var/nomi'"
optionsTest=" --plotmode norm --noLegendRatioPlot --noErrorBandOnRatio --contentAxisTitle 'arbitrary units' --legendFontSize 0.06"  # --showIndivSigShapes or --showIndivSigs or --showSigShape
#
#############################



######################################################
######################################################
######################################################
# end of settings to be changed by user
#----------------------------------------
######################################################
######################################################
######################################################


host=`echo "$HOSTNAME"`
if [[ "${runBatch}" == "y" ]]; then
    if [[ ${host} != *"lxplus"* ]]; then
	echo "Error! You must be on lxplus to run on batch queues. Do ssh -XY lxplus and work from a release."
	return 0
    fi
fi

mypath="$PWD"

evalScram="eval \`scramv1 runtime -sh\`"
batchFolder="${mypath}/jobsLog/${batchDirName}"
mkdir -p ${batchFolder}/src
mkdir -p ${batchFolder}/log
baseBatchScript="${batchFolder}/baseBatchScript.sh"
batchFileName="${batchFolder}/src/PLOTREGION_ETABIN.sh"  # PLOTREGION and ETABIN will be changed to proper names later in the script depending on region
###############################################
# now we build base script to submit batch jobs
# it will be used later to create script to submit batch jobs
###############################################
cat > ${baseBatchScript} <<EOF
#! /bin/bash

cd ${mypath}
${evalScram}

EOF
###############################################
ptForScaleFactors="LepGood1_pt"
if [[ "${usePtCorrForScaleFactors}" == "y" ]]; then
    echo "Will use corrected pt instead of LepGood1_pt to compute the trigger/efficiency scale factors"
    ptForScaleFactors="${ptcorr}"
fi

dataOption=""
MCweightOption=""
FR_MCweigthOption=""
if [[ "${useDataGH}" == "y" ]]; then
    # no more SF4: now L1 prefiring is automatically used for electrons
    echo "# Using all data from 2016"
    #dataOption=" --pg 'data := data_B,data_C,data_D,data_E,data_F,data_G,data_H' "
    #MCweigthOption=" -W 'puw2016_nTrueInt_36fb(nTrueInt)*trgSF_We(LepGood1_pdgId,${ptForScaleFactors},LepGood1_eta,2)*leptonSF_We(LepGood1_pdgId,${ptForScaleFactors},LepGood1_eta)' "
    MCweigthOption=" -W 'puw2016_nTrueInt_36fb(nTrueInt)*lepSF(LepGood1_pdgId,LepGood1_pt,LepGood1_eta,LepGood1_SF1,LepGood1_SF2,LepGood1_SF3)' "
    #MCweigthOption=" -W '1' "
    #MCweigthOption=" -W 'puw2016_nTrueInt_36fb(nTrueInt)*LepGood_SF1[0]*LepGood_SF2[0]*LepGood_SF3[0]' "
    #MCweigthOption=" -W 'puw2016_nTrueInt_36fb(nTrueInt)*LepGood_SF1[0]*_get_electronSF_anyWP_v2(LepGood1_pt,LepGood1_eta)' "
    #FR_MCweigthOption=" -W 'puw2016_nTrueInt_36fb(nTrueInt)*eleSF_HLT(LepGood1_pt,LepGood1_eta)*eleSF_GSFReco(LepGood1_pt,LepGood1_eta)*eleSF_FullID(LepGood1_pt,LepGood1_eta)*eleSF_Clustering(LepGood1_pt,LepGood1_eta)' "		
    FR_MCweigthOption=" -W 'puw2016_nTrueInt_36fb(nTrueInt)*lepSF(LepGood1_pdgId,LepGood1_pt,LepGood1_eta,LepGood1_SF1,LepGood1_SF2,LepGood1_SF3)'"
else 
    #MCweigthOption=" -W 'puw2016_nTrueInt_BF(nTrueInt)*trgSF_We(LepGood1_pdgId,${ptForScaleFactors},LepGood1_eta,2)*leptonSF_We(LepGood1_pdgId,${ptForScaleFactors},LepGood1_eta)' "
    MCweigthOption=" -W 'puw2016_nTrueInt_BF(nTrueInt)*LepGood_SF1[0]*LepGood_SF2[0]*LepGood_SF3[0]' "
    FR_MCweigthOption=" -W 'puw2016_nTrueInt_BF(nTrueInt)*LepGood_SF1[0]' "
fi

##############################
## WARNING ##
# to use a python command with options froma bash script, do
# command="python [args] [options]"
# echo "${command}" | bash
# otherwise the parsing of the option parameters is not done correctly


commonCommand="python ${plotterPath}/mcPlots.py -f -l ${luminosity} --s2v --tree treeProducerWMass --obj tree --lspam '#bf{CMS} #it{Preliminary}' --legendWidth 0.25 --legendFontSize 0.05 ${plotterPath}/w-helicity-13TeV/wmass_e/${mcafile} ${plotterPath}/w-helicity-13TeV/wmass_e/${cutfile} ${plotterPath}/w-helicity-13TeV/wmass_e/${plotfile} ${dataOption} ${plottingMode} --noCms "

# if [[ "X${scaleAllMCtoData}" != "X" ]]; then
#     commonCommand="${commonCommand} ${scaleAllMCtoData} "
# fi

if [[ "X${maxentries}" != "X" ]]; then
    commonCommand="${commonCommand} --max-entries ${maxentries} "
fi

if [[ "${runBatch}" != "y" ]]; then
    commonCommand="${commonCommand} -j 8 "
else
    commonCommand="${commonCommand} -j 4 "
fi


if [[ "X${excludeprocesses}" != "X" ]]; then
    commonCommand="${commonCommand} --xp ${excludeprocesses}"
fi

# add ratio plot only if not excluding data
if [[ "${excludeprocesses}" != *"data"* ]]; then
    commonCommand="${commonCommand} ${ratioPlotDataOptions} "
fi

# if [[ "${useWinclusive}" == "y" ]]; then
#     commonCommand="${commonCommand} --xp W,WFlips,TauDecaysW "
# else
#   commonCommand="${commonCommand} --xp Wincl "
# fi

if [[ "X${selectplots}" != "X" ]]; then
    commonCommand="${commonCommand} --sP ${selectplots}"
fi

if [[ "X${selectprocesses}" != "X" ]]; then
    commonCommand="${commonCommand} -p ${selectprocesses}"
fi

if [[ "${useHLTpt27}" == "y" ]]; then
    commonCommand="${commonCommand} ${HLT27sel}"
fi

nEtaBoundaries="${#etaBinBoundaries[@]}"
let "nEtaBins_minus1=${nEtaBoundaries}-2"


# with ! we expand the keys, not the values of the dictionary
for region in "${!regionKey[@]}"; 
do

    #echo "#>>>>>>>> $region"

    if [[ "${runRegion[${region}]}" == "y" ]]; then

        # echo "key: ${region}"
	thisRegionKey="${regionKey[${region}]}"
        # runThisRegion="${runRegion[${region}]}"
	thisRegionName="${regionName[${region}]}"
        # cutThisRegion="${regionCuts[${region}]}"
        # skimtreeThisRegion="${skimTreeDir[$region]}"
        outputdirThisRegion="${outputDir[$region]}${nameTag}"
        # echo "runThisRegion: ${runThisRegion}"
        # echo "thisRegionName: ${thisRegionName}"
        # echo "cutThisRegion: ${cutThisRegion}"
        # echo "skimtreeThisRegion: ${skimtreeThisRegion}"
        # echo "outputdirThisRegion: ${outputdirThisRegion}"

	echo "#----------------------------------"
	echo "# Doing ${thisRegionKey}"
	echo "#----------------------------------"

	if [[ "${useSkimmedTrees}" == "y" ]]; then
	    treedir="${skimTreeDir[${region}]}" 
	else 
	    treedir="TREES_1LEP_80X_V3"
	fi

	treepath="" # set below depending on where we are
	if [[ ${host} == *"pccmsrm28"* ]]; then
	    treepath="/u2/emanuele/wmass/" # from pccmsrm28 
	elif [[ ${host} == *"lxplus"* ]]; then
	    treepath="/eos/cms/store/group/dpg_ecal/comm_ecal/localreco"
	fi

	if [[ "${treedir}" == "TREES_1LEP_80X_V3_FRELSKIM_V9" ]]; then		
	    treepath="/eos/cms/store/cmst3/group/wmass/mciprian/"
	fi

	if [[ "${treedir}" == "TREES_1LEP_80X_V3_WSKIM_NEW" ]]; then		
	    treepath="/eos/cms/store/cmst3/group/wmass/mciprian/"
	fi

	if [[ "${treedir}" == "TREES_1LEP_80X_V3_SIGSKIM_WENU_FULLSEL_NOMT" ]]; then		
	    treepath="/eos/cms/store/cmst3/group/wmass/mciprian/"
	fi

	if [[ "${treedir}" == "TREES_electrons_1l_V6_TINY" ]]; then		
	    treepath="/eos/cms/store/cmst3/group/wmass/w-helicity-13TeV/trees/"
	fi

	if [[ "${treedir}" == "TREE_4_XSEC_AFS" ]]; then		
	    treepath="/afs/cern.ch/work/m/mciprian/w_mass_analysis/heppy/CMSSW_8_0_25/src/CMGTools/WMass/python/plotter/"
	fi


	#treeAndFriend=" -P ${treepath}/${treedir}/ -F Friends ${treepath}/${treedir}/friends/tree_Friend_{cname}.root -F Friends ${treepath}/${treedir}/friends/tree_FRFriend_{cname}.root --FMC Friends ${treepath}/${treedir}/friends/tree_TrgFriend_{cname}.root "
	treeAndFriend=" -P ${treepath}/${treedir}/ -F Friends ${treepath}/${treedir}/friends/tree_Friend_{cname}.root "

	regionCommand="${commonCommand} ${treeAndFriend} ${regionCuts[${region}]} ${scaleMCdata[${region}]} " #${processManager[${region}]} "

        #########
	# closure test on MC requires some special parameters

	if [[ "${regionKey[${region}]}" == "FRclosureMC" ]]; then       
	    
	    regionCommand="${regionCommand/${mcafile}/${mcafileFRclosureMC}}"
	    regionCommand="${regionCommand/${ratioPlotDataOptions}/}"  # remove ratio plot options
	    regionCommand="${regionCommand} --sp QCD --sp QCDandEWK_fullFR --noStackSig --showIndivSigs --rebin 4 ${ratioPlotDataOptions_MCclosureTest}"		

	elif [[ "${regionKey[${region}]}" == "TestPlots" ]]; then       
	    
	    regionCommand="${regionCommand/${mcafile}/${mcafileTest}}"
	    regionCommand="${regionCommand/${cutfile}/${cutfileTest}}"
	    regionCommand="${regionCommand/${ratioPlotDataOptions}/}"  # remove ratio plot options (add new one later, to avoid problems in case match is not found
	    regionCommand="${regionCommand} ${optionsTest} ${ratioPlotDataOptions_TestPlots}"

	else

	    if [[ "${qcdFromFR[${region}]}" == "y" ]]; then
		regionCommand="${regionCommand} --xp QCD"    
	    else
		regionCommand="${regionCommand} --xp data_fakes"
	    fi

	    # if [[ "${useWinclusive}" != "y" ]]; then
	    # 	if [[ "${skimTreeDir[${region}]}" == "TREES_1LEP_80X_V3_WENUSKIM_V5_TINY" ]]; then
	    # 	    #regionCommand="${regionCommand/${mcafile}/${mcafileTINY}}"
	    # 	    regionCommand="${regionCommand} --xp Wincl"	
	    # 	elif [[ "${skimTreeDir[${region}]}" == *"TREES_1LEP_80X_V3_FRELSKIM_V"* ]]; then
	    # 	    #regionCommand="${regionCommand/${mcafile}/${mcafileFRskim}}"
	    # 	    regionCommand="${regionCommand} --xp W,TauDecaysW,WFlips"	
	    # 	else
	    # 	    regionCommand="${regionCommand} --xp Wincl"		
	    # 	fi
	    # fi

	fi

	if [[ "${treedir}" == "TREES_1LEP_80X_V3_FRELSKIM_V9" ]]; then		
	    regionCommand="${regionCommand} ${FR_MCweigthOption} "
	    regionCommand="${regionCommand/${mcafile}/${mcafileFRskim}}"
	    #regionCommand="${regionCommand/MCweigthOption/FR_MCweigthOption}"  # remove scale factor 2 and 3 (keep only trigger)
	else
	    regionCommand="${regionCommand} ${MCweigthOption}"
	fi

	thisBatchFileName="${batchFileName/PLOTREGION/${thisRegionKey}}"

	for i in `seq 0 ${nEtaBins_minus1}`;
	do

	    echo ""
	    etalow="${etaBinBoundaries[$i]/./p}"
	    etahigh="${etaBinBoundaries[($i+1)]/./p}"
	    etabin="eta_${etalow}_${etahigh}"
	    srcBatchFileName="${thisBatchFileName/ETABIN/${etabin}}"
	    logPatternToChange="${batchFolder}/src/"
	    logPatternToPut="${batchFolder}/log/"
	    logBatchFileName="${srcBatchFileName/${logPatternToChange}/${logPatternToPut}}" # change folder from /src/ to /log/
	    logBatchFileName="${logBatchFileName/.sh/.log}"
            #echo "${etabin}"
	    #echo "${thisBatchFileName}"
	    cp ${baseBatchScript} ${srcBatchFileName}

	    etaRangeCut=" -A eleKin ${etabin} 'abs(LepGood1_eta) >= ${etaBinBoundaries[$i]} && abs(LepGood1_eta) <= ${etaBinBoundaries[($i+1)]}' "
	    regionCommand_eta="${regionCommand} --pdir ${plotterPath}/plots/distribution/${treedir}/${thisRegionName}/${outputdirThisRegion}/${etabin}/ ${etaRangeCut}" 
	    echo "${regionCommand_eta}" >> ${srcBatchFileName}
	    echo "" >> ${srcBatchFileName}
	    ######
	    # echo "corefiles=\`ls core.* 2&>1\`" >> ${srcBatchFileName}
	    # echo "for file in \${corefiles}" >> ${srcBatchFileName}
	    # echo "do" >> ${srcBatchFileName}
	    # echo "    rm ${mypath}/core.*" >> ${srcBatchFileName}
	    # echo "done" >> ${srcBatchFileName}
	    cat >> ${srcBatchFileName} <<EOF

if ls ${mypath}/core.* 1> /dev/null 2>&1; then
    echo "Found core.* files in ${mypath}/."
    echo "Removing them!"
    rm ${mypath}/core.*
else
    echo "No core.* files found in ${mypath}/"
fi

EOF

	    #echo "rm ${mypath}/core.*" >> ${srcBatchFileName}

	    if [[ "${runBatch}" == "y" ]]; then
		commandBatch="bsub -q ${queueForBatch} -oo ${logBatchFileName}  \"source ${srcBatchFileName}\" "
		echo "${commandBatch}"
	    #echo "${commandBatch}" | bash
	    else
		echo "${regionCommand_eta}"
	    fi
	done

	echo ""
	echo ""
	echo ""

    fi

done

echo ""
echo ""
