#!/bin/bash


# MUON

echo ""
echo ""
#python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/user/m/mdunser/public/triggerTnP_muons_fullData.root -o ~/www/wmass/13TeV/scaleFactors/muon/trigger/ -c mu -n smoothEfficiency.root -t

#python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/tnp/egm_tnp_analysis/results/muFullData/triggerMu/egammaEffi.txt_EGM2D.root -o ~/www/wmass/13TeV/scaleFactors/muon/trigger_extPt/ -c mu -n smoothEfficiency.root -t 

python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/tnp/egm_tnp_analysis/results/muFullData_trigger/triggerMu/egammaEffi.txt_EGM2D.root -o ~/www/wmass/13TeV/scaleFactors/muon/trigger_extPt_25_55/ -c mu -n smoothEfficiency.root -t 

echo ""
echo ""

# this should have ID+iso together, without separating eras. It would therefore substitute the following ID and ISO scale factors for muons
# python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/tnp/egm_tnp_analysis/results/muFullData_RecoToSelection/selectionMu/egammaEffi.txt_EGM2D.root -o ~/www/wmass/13TeV/scaleFactors/muon/recoToSelection_pt25to55/ -c mu -n smoothEfficiency.root --muonRecoToSel

python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/tnp/egm_tnp_analysis/results/muFullData_RecoToSelection/selectionMu/egammaEffi.txt_EGM2D.root -o ~/www/wmass/13TeV/scaleFactors/muon/recoToSelection_pt25to55/ -c mu -n smoothEfficiency.root --muonRecoToSel

echo ""
echo ""
python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/CMSSW_8_0_25/src/CMGTools/WMass/data/scaleFactors/muons/efficienciesISO.root -o ~/www/wmass/13TeV/scaleFactors/muon/efficiency_ISO_GH/ -c mu -n smoothEfficiency.root -e GH -v ISO

echo ""
echo ""
python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/CMSSW_8_0_25/src/CMGTools/WMass/data/scaleFactors/muons/efficienciesISO.root -o ~/www/wmass/13TeV/scaleFactors/muon/efficiency_ISO_BF/ -c mu -n smoothEfficiency.root -e BF -v ISO

echo ""
echo ""
python w-helicity-13TeV/smoothLeptonScaleFactors.py -o ~/www/wmass/13TeV/scaleFactors/muon/efficiency_ISO_full2016/ -c mu -n smoothEfficiency.root -v ISO --make-weighted-average --files-average "/afs/cern.ch/user/m/mciprian/www/wmass/13TeV/scaleFactors/muon/efficiency_ISO_GH/smoothEfficiency_muons_GH_ISO.root,/afs/cern.ch/user/m/mciprian/www/wmass/13TeV/scaleFactors/muon/efficiency_ISO_GH/smoothEfficiency_muons_GH_ISO.root" --weights-average "19.91,16.30" --hists-average "hdataSmoothCheck,hmcSmoothCheck,scaleFactor,scaleFactorOriginal" --average-uncertainty-mode max

echo ""
echo ""
python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/CMSSW_8_0_25/src/CMGTools/WMass/data/scaleFactors/muons/efficienciesID.root -o ~/www/wmass/13TeV/scaleFactors/muon/efficiency_ID_GH/ -c mu -n smoothEfficiency.root -e GH -v ID

echo ""
echo ""
python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/m/mdunser/public/cmssw/w-helicity-13TeV/CMSSW_8_0_25/src/CMGTools/WMass/data/scaleFactors/muons/efficienciesID.root -o ~/www/wmass/13TeV/scaleFactors/muon/efficiency_ID_BF/ -c mu -n smoothEfficiency.root -e BF -v ID

echo ""
echo ""
python w-helicity-13TeV/smoothLeptonScaleFactors.py -o ~/www/wmass/13TeV/scaleFactors/muon/efficiency_ID_full2016/ -c mu -n smoothEfficiency.root -v ID --make-weighted-average --files-average "/afs/cern.ch/user/m/mciprian/www/wmass/13TeV/scaleFactors/muon/efficiency_ID_GH/smoothEfficiency_muons_GH_ID.root,/afs/cern.ch/user/m/mciprian/www/wmass/13TeV/scaleFactors/muon/efficiency_ID_GH/smoothEfficiency_muons_GH_ID.root" --weights-average "19.91,16.30" --hists-average "hdataSmoothCheck,hmcSmoothCheck,scaleFactor,scaleFactorOriginal" --average-uncertainty-mode max

echo ""

# ELECTRON

echo ""
echo ""
python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/e/emanuele/wmass/heppy/CMSSW_8_0_25/src/CMGTools/WMass/python/postprocessing/data/leptonSF/new2016_madeSummer2018/electrons_trigger_pt30to55.root -o ~/www/wmass/13TeV/scaleFactors/electron/trigger_extPt/ -c el -n smoothEfficiency.root -t

echo ""
echo ""
#python w-helicity-13TeV/smoothLeptonScaleFactors.py -i electron_fullID_scaleFactor/egammaEffi.txt_EGM2D.root -o ~/www/wmass/13TeV/scaleFactors/electron/fullID/ -c el -n smoothEfficiency.root --fullID

#python w-helicity-13TeV/smoothLeptonScaleFactors.py -i electron_fullID_scaleFactor/egammaEffi.txt_EGM2D_extPt.root -o ~/www/wmass/13TeV/scaleFactors/electron/fullID_extPt/ -c el -n smoothEfficiency.root --fullID

python w-helicity-13TeV/smoothLeptonScaleFactors.py -i /afs/cern.ch/work/e/emanuele/wmass/heppy/CMSSW_8_0_25/src/CMGTools/WMass/python/postprocessing/data/leptonSF/new2016_madeSummer2018/electrons_fullID_V2_pt25to55.root -o ~/www/wmass/13TeV/scaleFactors/electron/fullID_pt_25_55/ -c el -n smoothEfficiency.root --fullID

echo ""
echo ""
