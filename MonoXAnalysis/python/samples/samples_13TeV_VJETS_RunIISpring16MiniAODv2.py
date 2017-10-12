import PhysicsTools.HeppyCore.framework.config as cfg
import os

### common MC samples
from CMGTools.RootTools.samples.samples_13TeV_RunIISpring16MiniAODv2 import *

from CMGTools.RootTools.samples.ComponentCreator import ComponentCreator
kreator = ComponentCreator()

ZGamma_Signal_740TeV = kreator.makeMCComponent("ZGamma_Signal_740TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_740_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_770TeV = kreator.makeMCComponent("ZGamma_Signal_770TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_770_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_850TeV = kreator.makeMCComponent("ZGamma_Signal_850TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_850_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_1000TeV = kreator.makeMCComponent("ZGamma_Signal_1000TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_1000_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_1150TeV = kreator.makeMCComponent("ZGamma_Signal_1150TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_1150_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_1300TeV = kreator.makeMCComponent("ZGamma_Signal_1300TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_1300_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_1900TeV = kreator.makeMCComponent("ZGamma_Signal_1900TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_1900_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_2050TeV = kreator.makeMCComponent("ZGamma_Signal_2050TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_2050_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_2450TeV = kreator.makeMCComponent("ZGamma_Signal_2450TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_2450_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_2850TeV = kreator.makeMCComponent("ZGamma_Signal_2850TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_2850_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_3250TeV = kreator.makeMCComponent("ZGamma_Signal_3250TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_3250_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)
ZGamma_Signal_3650TeV = kreator.makeMCComponent("ZGamma_Signal_3650TeV","/GluGluSpin0ToZGamma_ZToQQ_W_0-p-014_M_3650_TuneCUEP8M1_13TeV_pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM", "CMS", ".*root", 1.)

VGamma_signal=[
ZGamma_Signal_740TeV, 
ZGamma_Signal_770TeV,  
ZGamma_Signal_850TeV,   
ZGamma_Signal_1000TeV,  
ZGamma_Signal_1150TeV, 
ZGamma_Signal_1300TeV,  
ZGamma_Signal_1900TeV,  
ZGamma_Signal_2050TeV,  
ZGamma_Signal_2450TeV,  
ZGamma_Signal_2850TeV,  
ZGamma_Signal_3250TeV,  
ZGamma_Signal_3650TeV  
]

GJets = GJetsDR04HT
VV_VGamma = VJetsQQHT


myTT = kreator.makeMCComponent("myTT", "/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM", "CMS", ".*root",  832.16)
myST_s = kreator.makeMCComponent("mySTs","/ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM", "CMS", ".*root", 47.13)
mySTtW = kreator.makeMCComponent("mySTtW", "/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM", "CMS", ".*root", 35.6)
mySTtW_anti  = kreator.makeMCComponent("mySTtW_anti", "/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM", "CMS", ".*root", 35.6)
myWJets_100_200  = kreator.makeMCComponent("myWJets_100_200", "/WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM", "CMS", ".*root", 1630.27)
myWJets_200_400  = kreator.makeMCComponent("myWJets_200_400", "/WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM", "CMS", ".*root",  435.6)
myWJets_400_600  = kreator.makeMCComponent("myWJets_400_600", "/WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM", "CMS", ".*root", 56.17)
myWJets_600_800  = kreator.makeMCComponent("myWJets_600_800", "/WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM", "CMS", ".*root", 15.01)
myWJets_800_1200  = kreator.makeMCComponent("myWJets_800_1200", "/WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM", "CMS", ".*root", 6.36)
myWJets_1200_2500  = kreator.makeMCComponent("myWJets_1200_2500", "/WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM", "CMS", ".*root", 2.01)
myWJets_2500_Inf  = kreator.makeMCComponent("myWJets_2500_Inf", "/WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM", "CMS", ".*root", 37)

myWW = kreator.makeMCComponent("myWW", "/WWToLNuQQ_13TeV-powheg/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM", "CMS", ".*root", 43.5)
myWZ = kreator.makeMCComponent("myWZ", "/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/MINIAODSIM", "CMS", ".*root", 10.7)
myZZ = kreator.makeMCComponent("myZZ", "/ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM", "CMS", ".*root", 3.2)


lastWTagging=[
myTT,
myST_s,
mySTtW,
mySTtW_anti,
myWJets_100_200,
myWJets_200_400,
myWJets_400_600,
myWJets_600_800,
myWJets_800_1200,
myWJets_1200_2500,
myWJets_2500_Inf,
myWW,
myWZ,
myZZ,
]
