//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Mon Jul  9 17:46:32 2018 by ROOT version 6.06/01
// from TTree tree/treeProducerWMass
// found on file: /eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_2018-07-06-2l_triggerMatch_ELECTRONS/SingleElectron_Run2016C/treeProducerWMass/tree.root
//////////////////////////////////////////////////////////

#ifndef TnPNtuplesBase_h
#define TnPNtuplesBase_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TString.h>
#include <TH1F.h>

// Header file for the classes stored in the TTree if any.

class TnPNtuplesBase {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

  // Output tree and histos
  TH1F *h_entries;
  TH1F *h_selection;

  TFile *outFile_;
  TTree* outTree_;
  TDirectory *cddir;

  float tag_lep_pt, tag_lep_eta;
  int tag_lep_matchMC;
  float probe_lep_pt, probe_lep_eta, probe_sc_eta, probe_lep_phi;
  float probe_eleTrgPt, probe_muTrgPt, probe_tkMuTrgPt;
  int probe_lep_matchMC;
  int probe_lep_hltSafeId, probe_lep_customId, probe_lep_tightCharge, probe_lep_fullLepId;
  int probe_lep_alsoTag;
  float pair_mass;
  int nvtx;
  int thisEntry;
  float mypuw, totWeight;
  int mcTrue;

  // Declaration of leaf types
  UInt_t          run;
  UInt_t          lumi;
  ULong64_t       evt;
  Int_t           isData;
  Float_t         xsec;
  Float_t         puWeight;
  Float_t         nTrueInt;
  Float_t         genWeight;
  UInt_t          intLumi;
  Int_t           Flag_badMuonMoriond2017;
  Int_t           Flag_badCloneMuonMoriond2017;
  Float_t         badCloneMuonMoriond2017_maxPt;
  Float_t         badNotCloneMuonMoriond2017_maxPt;
  Float_t         rho;
  Float_t         rhoCN;
  Int_t           nVert;
  Float_t         mZ1;
  Float_t         puppimet_sumEt;
  Float_t         met_sumEt;
  Float_t         tkMetPVchs_sumEt;
  Float_t         tkMetPVLoose_sumEt;
  Float_t         tkMetPUPVLoose_sumEt;
  Float_t         tkMetPVTight_sumEt;
  Float_t         ntMet_sumEt;
  Float_t         ntCentralMet_sumEt;
  Float_t         tkMetPVchs_Count;
  Float_t         tkMetPVLoose_Count;
  Float_t         tkMetPUPVLoose_Count;
  Float_t         tkMetPVTight_Count;
  Float_t         ntMet_Count;
  Float_t         ntCentralMet_Count;
  Int_t           hbheFilterNew50ns;
  Int_t           hbheFilterNew25ns;
  Int_t           hbheFilterIso;
  Float_t         Flag_badChargedHadronFilter;
  Float_t         Flag_badMuonFilter;
  Float_t         met_trkPt;
  Float_t         met_trkPhi;
  Int_t           HLT_BIT_HLT_IsoMu20_v;
  Int_t           HLT_BIT_HLT_IsoMu20_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_IsoMu20_v_Prescale;
  Int_t           HLT_BIT_HLT_IsoTkMu20_v;
  Int_t           HLT_BIT_HLT_IsoTkMu20_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_IsoTkMu20_v_Prescale;
  Int_t           HLT_BIT_HLT_IsoMu22_v;
  Int_t           HLT_BIT_HLT_IsoMu22_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_IsoMu22_v_Prescale;
  Int_t           HLT_BIT_HLT_IsoTkMu22_v;
  Int_t           HLT_BIT_HLT_IsoTkMu22_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_IsoTkMu22_v_Prescale;
  Int_t           HLT_BIT_HLT_IsoMu24_v;
  Int_t           HLT_BIT_HLT_IsoMu24_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_IsoMu24_v_Prescale;
  Int_t           HLT_BIT_HLT_IsoTkMu24_v;
  Int_t           HLT_BIT_HLT_IsoTkMu24_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_IsoTkMu24_v_Prescale;
  Int_t           HLT_BIT_HLT_IsoMu22_eta2p1_v;
  Int_t           HLT_BIT_HLT_IsoMu22_eta2p1_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_IsoMu22_eta2p1_v_Prescale;
  Int_t           HLT_BIT_HLT_IsoTkMu22_eta2p1_v;
  Int_t           HLT_BIT_HLT_IsoTkMu22_eta2p1_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_IsoTkMu22_eta2p1_v_Prescale;
  Int_t           HLT_SingleMu;
  Int_t           HLT_SingleMu_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_Mu8_SameSign_v;
  Int_t           HLT_BIT_HLT_Mu17_Mu8_SameSign_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_Mu8_SameSign_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v;
  Int_t           HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu20_Mu10_SameSign_v;
  Int_t           HLT_BIT_HLT_Mu20_Mu10_SameSign_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu20_Mu10_SameSign_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v;
  Int_t           HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_Prescale;
  Int_t           HLT_DoubleMuSS;
  Int_t           HLT_DoubleMuSS_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu30_TkMu11_v;
  Int_t           HLT_BIT_HLT_Mu30_TkMu11_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu30_TkMu11_v_Prescale;
  Int_t           HLT_DoubleMuNoIso;
  Int_t           HLT_DoubleMuNoIso_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v;
  Int_t           HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v;
  Int_t           HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v;
  Int_t           HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;
  Int_t           HLT_MuEG;
  Int_t           HLT_MuEG_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele25_WPTight_Gsf_v;
  Int_t           HLT_BIT_HLT_Ele25_WPTight_Gsf_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele25_WPTight_Gsf_v_Prescale;
  Int_t           HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v;
  Int_t           HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_Prescale;
  Int_t           HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v;
  Int_t           HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_Prescale;
  Int_t           HLT_BIT_HLT_Ele27_WPTight_Gsf_v;
  Int_t           HLT_BIT_HLT_Ele27_WPTight_Gsf_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele27_WPTight_Gsf_v_Prescale;
  Int_t           HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v;
  Int_t           HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_Prescale;
  Int_t           HLT_BIT_HLT_Ele45_WPLoose_Gsf_v;
  Int_t           HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_Prescale;
  Int_t           HLT_SingleEl;
  Int_t           HLT_SingleEl_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v;
  Int_t           HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;
  Int_t           HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v;
  Int_t           HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;
  Int_t           HLT_DoubleEl;
  Int_t           HLT_DoubleEl_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled;
  Int_t           HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale;
  Int_t           HLT_DoubleMu;
  Int_t           HLT_DoubleMu_isUnprescaled;
  Int_t           Flag_hcalLaserEventFilter;
  Int_t           Flag_trkPOG_logErrorTooManyClusters;
  Int_t           Flag_EcalDeadCellTriggerPrimitiveFilter;
  Int_t           Flag_trkPOGFilters;
  Int_t           Flag_trackingFailureFilter;
  Int_t           Flag_CSCTightHaloFilter;
  Int_t           Flag_HBHENoiseFilter;
  Int_t           Flag_MuFlag_bad;
  Int_t           Flag_MuFlag_good;
  Int_t           Flag_HBHENoiseIsoFilter;
  Int_t           Flag_goodVertices;
  Int_t           Flag_trkPOG_manystripclus53X;
  Int_t           Flag_MuFlag_dup;
  Int_t           Flag_CSCTightHalo2016Filter;
  Int_t           Flag_ecalLaserCorrFilter;
  Int_t           Flag_trkPOG_toomanystripclus53X;
  Int_t           Flag_CSCTightHalo2015Filter;
  Int_t           Flag_eeBadScFilter;
  Int_t           Flag_globalTightHalo2016Filter;
  Float_t         leadNeutral_pt;
  Float_t         leadNeutral_eta;
  Float_t         leadNeutral_phi;
  Float_t         leadNeutral_mass;
  Float_t         met_jecUp_pt;
  Float_t         met_jecUp_eta;
  Float_t         met_jecUp_phi;
  Float_t         met_jecUp_mass;
  Float_t         met_jecUp_sumEt;
  Float_t         met_jecUp_rawPt;
  Float_t         met_jecUp_rawPhi;
  Float_t         met_jecUp_rawSumEt;
  Float_t         tkMetPVchs_pt;
  Float_t         tkMetPVchs_eta;
  Float_t         tkMetPVchs_phi;
  Float_t         tkMetPVchs_mass;
  Float_t         ntMet_pt;
  Float_t         ntMet_eta;
  Float_t         ntMet_phi;
  Float_t         ntMet_mass;
  Float_t         leadCharged_pt;
  Float_t         leadCharged_eta;
  Float_t         leadCharged_phi;
  Float_t         leadCharged_mass;
  Float_t         tkMetPVLoose_pt;
  Float_t         tkMetPVLoose_eta;
  Float_t         tkMetPVLoose_phi;
  Float_t         tkMetPVLoose_mass;
  Float_t         met_jecDown_pt;
  Float_t         met_jecDown_eta;
  Float_t         met_jecDown_phi;
  Float_t         met_jecDown_mass;
  Float_t         met_jecDown_sumEt;
  Float_t         met_jecDown_rawPt;
  Float_t         met_jecDown_rawPhi;
  Float_t         met_jecDown_rawSumEt;
  Float_t         tkMetPVTight_pt;
  Float_t         tkMetPVTight_eta;
  Float_t         tkMetPVTight_phi;
  Float_t         tkMetPVTight_mass;
  Float_t         met_pt;
  Float_t         met_eta;
  Float_t         met_phi;
  Float_t         met_mass;
  Float_t         ntCentralMet_pt;
  Float_t         ntCentralMet_eta;
  Float_t         ntCentralMet_phi;
  Float_t         ntCentralMet_mass;
  Float_t         tkMetPUPVLoose_pt;
  Float_t         tkMetPUPVLoose_eta;
  Float_t         tkMetPUPVLoose_phi;
  Float_t         tkMetPUPVLoose_mass;
  Float_t         puppimet_pt;
  Float_t         puppimet_eta;
  Float_t         puppimet_phi;
  Float_t         puppimet_mass;
  Int_t           nGenPart;
  Int_t           GenPart_motherId[25];   //[nGenPart]
  Int_t           GenPart_grandmotherId[25];   //[nGenPart]
  Int_t           GenPart_sourceId[25];   //[nGenPart]
  Float_t         GenPart_charge[25];   //[nGenPart]
  Int_t           GenPart_status[25];   //[nGenPart]
  Int_t           GenPart_isPromptHard[25];   //[nGenPart]
  Int_t           GenPart_pdgId[25];   //[nGenPart]
  Float_t         GenPart_pt[25];   //[nGenPart]
  Float_t         GenPart_eta[25];   //[nGenPart]
  Float_t         GenPart_phi[25];   //[nGenPart]
  Float_t         GenPart_mass[25];   //[nGenPart]
  Int_t           GenPart_motherIndex[25];   //[nGenPart]
  Int_t           nJet;
  Float_t         Jet_charge[14];   //[nJet]
  Float_t         Jet_ctagCsvL[14];   //[nJet]
  Float_t         Jet_ctagCsvB[14];   //[nJet]
  Float_t         Jet_area[14];   //[nJet]
  Float_t         Jet_qgl[14];   //[nJet]
  Float_t         Jet_ptd[14];   //[nJet]
  Float_t         Jet_axis2[14];   //[nJet]
  Int_t           Jet_mult[14];   //[nJet]
  Float_t         Jet_nLeptons[14];   //[nJet]
  Int_t           Jet_id[14];   //[nJet]
  Int_t           Jet_puId[14];   //[nJet]
  Float_t         Jet_btagCSV[14];   //[nJet]
  Float_t         Jet_btagCMVA[14];   //[nJet]
  Float_t         Jet_rawPt[14];   //[nJet]
  Float_t         Jet_corr_JECUp[14];   //[nJet]
  Float_t         Jet_corr_JECDown[14];   //[nJet]
  Float_t         Jet_corr[14];   //[nJet]
  Float_t         Jet_pt[14];   //[nJet]
  Float_t         Jet_eta[14];   //[nJet]
  Float_t         Jet_phi[14];   //[nJet]
  Float_t         Jet_mass[14];   //[nJet]
  Float_t         Jet_CorrFactor_L1[14];   //[nJet]
  Float_t         Jet_CorrFactor_L1L2[14];   //[nJet]
  Float_t         Jet_CorrFactor_L1L2L3[14];   //[nJet]
  Float_t         Jet_CorrFactor_L1L2L3Res[14];   //[nJet]
  Float_t         Jet_chHEF[14];   //[nJet]
  Float_t         Jet_neHEF[14];   //[nJet]
  Int_t           nLepGood;
  Int_t           LepGood_charge[50];   //[nLepGood]
  Int_t           LepGood_tightId[50];   //[nLepGood]
  Int_t           LepGood_hltId[50];   //[nLepGood]
  Int_t           LepGood_eleCutIdCSA14_25ns_v1[50];   //[nLepGood]
  Int_t           LepGood_eleCutIdCSA14_50ns_v1[50];   //[nLepGood]
  Int_t           LepGood_eleCutIdSpring15_25ns_v1[50];   //[nLepGood]
  Float_t         LepGood_dxy[50];   //[nLepGood]
  Float_t         LepGood_dz[50];   //[nLepGood]
  Float_t         LepGood_edxy[50];   //[nLepGood]
  Float_t         LepGood_edz[50];   //[nLepGood]
  Float_t         LepGood_ip3d[50];   //[nLepGood]
  Float_t         LepGood_sip3d[50];   //[nLepGood]
  Int_t           LepGood_convVeto[50];   //[nLepGood]
  Int_t           LepGood_lostHits[50];   //[nLepGood]
  Float_t         LepGood_relIso03[50];   //[nLepGood]
  Float_t         LepGood_relIso04[50];   //[nLepGood]
  Float_t         LepGood_miniRelIso[50];   //[nLepGood]
  Float_t         LepGood_relIsoAn04[50];   //[nLepGood]
  Int_t           LepGood_tightCharge[50];   //[nLepGood]
  Int_t           LepGood_mediumMuonId[50];   //[nLepGood]
  Int_t           LepGood_ICHEPsoftMuonId[50];   //[nLepGood]
  Int_t           LepGood_ICHEPmediumMuonId[50];   //[nLepGood]
  Int_t           LepGood_pdgId[50];   //[nLepGood]
  Float_t         LepGood_pt[50];   //[nLepGood]
  Float_t         LepGood_eta[50];   //[nLepGood]
  Float_t         LepGood_phi[50];   //[nLepGood]
  Float_t         LepGood_mass[50];   //[nLepGood]
  Float_t         LepGood_jetDR[50];   //[nLepGood]
  Float_t         LepGood_r9[50];   //[nLepGood]
  Float_t         LepGood_chIso04[50];   //[nLepGood]
  Float_t         LepGood_nhIso04[50];   //[nLepGood]
  Float_t         LepGood_phIso04[50];   //[nLepGood]
  Float_t         LepGood_softMuonId2016[50];   //[nLepGood]
  Float_t         LepGood_mediumMuonID2016[50];   //[nLepGood]
  Int_t           LepGood_tightChargeFix[50];   //[nLepGood]
  Int_t           LepGood_muonTrackType[50];   //[nLepGood]
  Int_t           LepGood_chargeConsistency[50];   //[nLepGood]
  Float_t         LepGood_ptErrTk[50];   //[nLepGood]
  Float_t         LepGood_ecalPFClusterIso[50];   //[nLepGood]
  Float_t         LepGood_hcalPFClusterIso[50];   //[nLepGood]
  Float_t         LepGood_dr03TkSumPt[50];   //[nLepGood]
  Float_t         LepGood_trackIso[50];   //[nLepGood]
  Float_t         LepGood_trackIso03[50];   //[nLepGood]
  Float_t         LepGood_etaSc[50];   //[nLepGood]
  Float_t         LepGood_energySc[50];   //[nLepGood]
  Float_t         LepGood_e5x5[50];   //[nLepGood]
  Float_t         LepGood_sigmaIetaIeta[50];   //[nLepGood]
  Float_t         LepGood_hcalOverEcal[50];   //[nLepGood]
  Float_t         LepGood_eSuperClusterOverP[50];   //[nLepGood]
  Float_t         LepGood_matchedTrgObjElePt[50];   //[nLepGood]
  Float_t         LepGood_matchedTrgObjEleDR[50];   //[nLepGood]
  Float_t         LepGood_matchedTrgObjMuPt[50];   //[nLepGood]
  Float_t         LepGood_matchedTrgObjMuDR[50];   //[nLepGood]
  Float_t         LepGood_matchedTrgObjTkMuPt[50];   //[nLepGood]
  Float_t         LepGood_matchedTrgObjTkMuDR[50];   //[nLepGood]
  Int_t           LepGood_customId[50];
  Float_t         LepGood_calPt[50];

  // List of branches
  TBranch        *b_run;   //!
  TBranch        *b_lumi;   //!
  TBranch        *b_evt;   //!
  TBranch        *b_isData;   //!
  TBranch        *b_xsec;   //!
  TBranch        *b_puWeight;   //!
  TBranch        *b_nTrueInt;   //!
  TBranch        *b_genWeight;   //!
  TBranch        *b_intLumi;   //!
  TBranch        *b_Flag_badMuonMoriond2017;   //!
  TBranch        *b_Flag_badCloneMuonMoriond2017;   //!
  TBranch        *b_badCloneMuonMoriond2017_maxPt;   //!
  TBranch        *b_badNotCloneMuonMoriond2017_maxPt;   //!
  TBranch        *b_rho;   //!
  TBranch        *b_rhoCN;   //!
  TBranch        *b_nVert;   //!
  TBranch        *b_mZ1;   //!
  TBranch        *b_puppimet_sumEt;   //!
  TBranch        *b_met_sumEt;   //!
  TBranch        *b_tkMetPVchs_sumEt;   //!
  TBranch        *b_tkMetPVLoose_sumEt;   //!
  TBranch        *b_tkMetPUPVLoose_sumEt;   //!
  TBranch        *b_tkMetPVTight_sumEt;   //!
  TBranch        *b_ntMet_sumEt;   //!
  TBranch        *b_ntCentralMet_sumEt;   //!
  TBranch        *b_tkMetPVchs_Count;   //!
  TBranch        *b_tkMetPVLoose_Count;   //!
  TBranch        *b_tkMetPUPVLoose_Count;   //!
  TBranch        *b_tkMetPVTight_Count;   //!
  TBranch        *b_ntMet_Count;   //!
  TBranch        *b_ntCentralMet_Count;   //!
  TBranch        *b_hbheFilterNew50ns;   //!
  TBranch        *b_hbheFilterNew25ns;   //!
  TBranch        *b_hbheFilterIso;   //!
  TBranch        *b_Flag_badChargedHadronFilter;   //!
  TBranch        *b_Flag_badMuonFilter;   //!
  TBranch        *b_met_trkPt;   //!
  TBranch        *b_met_trkPhi;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu20_v;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu20_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu20_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu20_v;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu20_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu20_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu22_v;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu22_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu22_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu22_v;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu22_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu22_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu24_v;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu24_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu24_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu24_v;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu24_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu24_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu22_eta2p1_v;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu22_eta2p1_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_IsoMu22_eta2p1_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu22_eta2p1_v;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu22_eta2p1_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_IsoTkMu22_eta2p1_v_Prescale;   //!
  TBranch        *b_HLT_SingleMu;   //!
  TBranch        *b_HLT_SingleMu_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_Mu8_SameSign_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_Mu8_SameSign_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_Mu8_SameSign_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu20_Mu10_SameSign_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu20_Mu10_SameSign_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu20_Mu10_SameSign_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_Prescale;   //!
  TBranch        *b_HLT_DoubleMuSS;   //!
  TBranch        *b_HLT_DoubleMuSS_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu30_TkMu11_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu30_TkMu11_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu30_TkMu11_v_Prescale;   //!
  TBranch        *b_HLT_DoubleMuNoIso;   //!
  TBranch        *b_HLT_DoubleMuNoIso_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;   //!
  TBranch        *b_HLT_MuEG;   //!
  TBranch        *b_HLT_MuEG_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele25_WPTight_Gsf_v;   //!
  TBranch        *b_HLT_BIT_HLT_Ele25_WPTight_Gsf_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele25_WPTight_Gsf_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v;   //!
  TBranch        *b_HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v;   //!
  TBranch        *b_HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Ele27_WPTight_Gsf_v;   //!
  TBranch        *b_HLT_BIT_HLT_Ele27_WPTight_Gsf_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele27_WPTight_Gsf_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v;   //!
  TBranch        *b_HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Ele45_WPLoose_Gsf_v;   //!
  TBranch        *b_HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_Prescale;   //!
  TBranch        *b_HLT_SingleEl;   //!
  TBranch        *b_HLT_SingleEl_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale;   //!
  TBranch        *b_HLT_DoubleEl;   //!
  TBranch        *b_HLT_DoubleEl_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled;   //!
  TBranch        *b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale;   //!
  TBranch        *b_HLT_DoubleMu;   //!
  TBranch        *b_HLT_DoubleMu_isUnprescaled;   //!
  TBranch        *b_Flag_hcalLaserEventFilter;   //!
  TBranch        *b_Flag_trkPOG_logErrorTooManyClusters;   //!
  TBranch        *b_Flag_EcalDeadCellTriggerPrimitiveFilter;   //!
  TBranch        *b_Flag_trkPOGFilters;   //!
  TBranch        *b_Flag_trackingFailureFilter;   //!
  TBranch        *b_Flag_CSCTightHaloFilter;   //!
  TBranch        *b_Flag_HBHENoiseFilter;   //!
  TBranch        *b_Flag_MuFlag_bad;   //!
  TBranch        *b_Flag_MuFlag_good;   //!
  TBranch        *b_Flag_HBHENoiseIsoFilter;   //!
  TBranch        *b_Flag_goodVertices;   //!
  TBranch        *b_Flag_trkPOG_manystripclus53X;   //!
  TBranch        *b_Flag_MuFlag_dup;   //!
  TBranch        *b_Flag_CSCTightHalo2016Filter;   //!
  TBranch        *b_Flag_ecalLaserCorrFilter;   //!
  TBranch        *b_Flag_trkPOG_toomanystripclus53X;   //!
  TBranch        *b_Flag_CSCTightHalo2015Filter;   //!
  TBranch        *b_Flag_eeBadScFilter;   //!
  TBranch        *b_Flag_globalTightHalo2016Filter;   //!
  TBranch        *b_leadNeutral_pt;   //!
  TBranch        *b_leadNeutral_eta;   //!
  TBranch        *b_leadNeutral_phi;   //!
  TBranch        *b_leadNeutral_mass;   //!
  TBranch        *b_met_jecUp_pt;   //!
  TBranch        *b_met_jecUp_eta;   //!
  TBranch        *b_met_jecUp_phi;   //!
  TBranch        *b_met_jecUp_mass;   //!
  TBranch        *b_met_jecUp_sumEt;   //!
  TBranch        *b_met_jecUp_rawPt;   //!
  TBranch        *b_met_jecUp_rawPhi;   //!
  TBranch        *b_met_jecUp_rawSumEt;   //!
  TBranch        *b_tkMetPVchs_pt;   //!
  TBranch        *b_tkMetPVchs_eta;   //!
  TBranch        *b_tkMetPVchs_phi;   //!
  TBranch        *b_tkMetPVchs_mass;   //!
  TBranch        *b_ntMet_pt;   //!
  TBranch        *b_ntMet_eta;   //!
  TBranch        *b_ntMet_phi;   //!
  TBranch        *b_ntMet_mass;   //!
  TBranch        *b_leadCharged_pt;   //!
  TBranch        *b_leadCharged_eta;   //!
  TBranch        *b_leadCharged_phi;   //!
  TBranch        *b_leadCharged_mass;   //!
  TBranch        *b_tkMetPVLoose_pt;   //!
  TBranch        *b_tkMetPVLoose_eta;   //!
  TBranch        *b_tkMetPVLoose_phi;   //!
  TBranch        *b_tkMetPVLoose_mass;   //!
  TBranch        *b_met_jecDown_pt;   //!
  TBranch        *b_met_jecDown_eta;   //!
  TBranch        *b_met_jecDown_phi;   //!
  TBranch        *b_met_jecDown_mass;   //!
  TBranch        *b_met_jecDown_sumEt;   //!
  TBranch        *b_met_jecDown_rawPt;   //!
  TBranch        *b_met_jecDown_rawPhi;   //!
  TBranch        *b_met_jecDown_rawSumEt;   //!
  TBranch        *b_tkMetPVTight_pt;   //!
  TBranch        *b_tkMetPVTight_eta;   //!
  TBranch        *b_tkMetPVTight_phi;   //!
  TBranch        *b_tkMetPVTight_mass;   //!
  TBranch        *b_met_pt;   //!
  TBranch        *b_met_eta;   //!
  TBranch        *b_met_phi;   //!
  TBranch        *b_met_mass;   //!
  TBranch        *b_ntCentralMet_pt;   //!
  TBranch        *b_ntCentralMet_eta;   //!
  TBranch        *b_ntCentralMet_phi;   //!
  TBranch        *b_ntCentralMet_mass;   //!
  TBranch        *b_tkMetPUPVLoose_pt;   //!
  TBranch        *b_tkMetPUPVLoose_eta;   //!
  TBranch        *b_tkMetPUPVLoose_phi;   //!
  TBranch        *b_tkMetPUPVLoose_mass;   //!
  TBranch        *b_puppimet_pt;   //!
  TBranch        *b_puppimet_eta;   //!
  TBranch        *b_puppimet_phi;   //!
  TBranch        *b_puppimet_mass;   //!
  TBranch        *b_nGenPart;   //!
  TBranch        *b_GenPart_motherId;   //!
  TBranch        *b_GenPart_grandmotherId;   //!
  TBranch        *b_GenPart_sourceId;   //!
  TBranch        *b_GenPart_charge;   //!
  TBranch        *b_GenPart_status;   //!
  TBranch        *b_GenPart_isPromptHard;   //!
  TBranch        *b_GenPart_pdgId;   //!
  TBranch        *b_GenPart_pt;   //!
  TBranch        *b_GenPart_eta;   //!
  TBranch        *b_GenPart_phi;   //!
  TBranch        *b_GenPart_mass;   //!
  TBranch        *b_GenPart_motherIndex;   //!
  TBranch        *b_nJet;   //!
  TBranch        *b_Jet_charge;   //!
  TBranch        *b_Jet_ctagCsvL;   //!
  TBranch        *b_Jet_ctagCsvB;   //!
  TBranch        *b_Jet_area;   //!
  TBranch        *b_Jet_qgl;   //!
  TBranch        *b_Jet_ptd;   //!
  TBranch        *b_Jet_axis2;   //!
  TBranch        *b_Jet_mult;   //!
  TBranch        *b_Jet_nLeptons;   //!
  TBranch        *b_Jet_id;   //!
  TBranch        *b_Jet_puId;   //!
  TBranch        *b_Jet_btagCSV;   //!
  TBranch        *b_Jet_btagCMVA;   //!
  TBranch        *b_Jet_rawPt;   //!
  TBranch        *b_Jet_corr_JECUp;   //!
  TBranch        *b_Jet_corr_JECDown;   //!
  TBranch        *b_Jet_corr;   //!
  TBranch        *b_Jet_pt;   //!
  TBranch        *b_Jet_eta;   //!
  TBranch        *b_Jet_phi;   //!
  TBranch        *b_Jet_mass;   //!
  TBranch        *b_Jet_CorrFactor_L1;   //!
  TBranch        *b_Jet_CorrFactor_L1L2;   //!
  TBranch        *b_Jet_CorrFactor_L1L2L3;   //!
  TBranch        *b_Jet_CorrFactor_L1L2L3Res;   //!
  TBranch        *b_Jet_chHEF;   //!
  TBranch        *b_Jet_neHEF;   //!
  TBranch        *b_nLepGood;   //!
  TBranch        *b_LepGood_charge;   //!
  TBranch        *b_LepGood_tightId;   //!
  TBranch        *b_LepGood_hltId;   //!
  TBranch        *b_LepGood_eleCutIdCSA14_25ns_v1;   //!
  TBranch        *b_LepGood_eleCutIdCSA14_50ns_v1;   //!
  TBranch        *b_LepGood_eleCutIdSpring15_25ns_v1;   //!
  TBranch        *b_LepGood_dxy;   //!
  TBranch        *b_LepGood_dz;   //!
  TBranch        *b_LepGood_edxy;   //!
  TBranch        *b_LepGood_edz;   //!
  TBranch        *b_LepGood_ip3d;   //!
  TBranch        *b_LepGood_sip3d;   //!
  TBranch        *b_LepGood_convVeto;   //!
  TBranch        *b_LepGood_lostHits;   //!
  TBranch        *b_LepGood_relIso03;   //!
  TBranch        *b_LepGood_relIso04;   //!
  TBranch        *b_LepGood_miniRelIso;   //!
  TBranch        *b_LepGood_relIsoAn04;   //!
  TBranch        *b_LepGood_tightCharge;   //!
  TBranch        *b_LepGood_mediumMuonId;   //!
  TBranch        *b_LepGood_ICHEPsoftMuonId;   //!
  TBranch        *b_LepGood_ICHEPmediumMuonId;   //!
  TBranch        *b_LepGood_pdgId;   //!
  TBranch        *b_LepGood_pt;   //!
  TBranch        *b_LepGood_eta;   //!
  TBranch        *b_LepGood_phi;   //!
  TBranch        *b_LepGood_mass;   //!
  TBranch        *b_LepGood_jetDR;   //!
  TBranch        *b_LepGood_r9;   //!
  TBranch        *b_LepGood_chIso04;   //!
  TBranch        *b_LepGood_nhIso04;   //!
  TBranch        *b_LepGood_phIso04;   //!
  TBranch        *b_LepGood_softMuonId2016;   //!
  TBranch        *b_LepGood_mediumMuonID2016;   //!
  TBranch        *b_LepGood_tightChargeFix;   //!
  TBranch        *b_LepGood_muonTrackType;   //!
  TBranch        *b_LepGood_chargeConsistency;   //!
  TBranch        *b_LepGood_ptErrTk;   //!
  TBranch        *b_LepGood_ecalPFClusterIso;   //!
  TBranch        *b_LepGood_hcalPFClusterIso;   //!
  TBranch        *b_LepGood_dr03TkSumPt;   //!
  TBranch        *b_LepGood_trackIso;   //!
  TBranch        *b_LepGood_trackIso03;   //!
  TBranch        *b_LepGood_etaSc;   //!
  TBranch        *b_LepGood_energySc;   //!
  TBranch        *b_LepGood_e5x5;   //!
  TBranch        *b_LepGood_sigmaIetaIeta;   //!
  TBranch        *b_LepGood_hcalOverEcal;   //!
  TBranch        *b_LepGood_eSuperClusterOverP;   //!
  TBranch        *b_LepGood_matchedTrgObjElePt;   //!
  TBranch        *b_LepGood_matchedTrgObjEleDR;   //!
  TBranch        *b_LepGood_matchedTrgObjMuPt;   //!
  TBranch        *b_LepGood_matchedTrgObjMuDR;   //!
  TBranch        *b_LepGood_matchedTrgObjTkMuPt;   //!
  TBranch        *b_LepGood_matchedTrgObjTkMuDR;   //!
  TBranch        *b_LepGood_customId;   //!
  TBranch        *b_LepGood_calPt;  //!

  TnPNtuplesBase(TTree *tree=0, TTree *ftree=0);
  virtual ~TnPNtuplesBase();

  virtual Int_t    Cut(Long64_t entry);
  virtual Int_t    GetEntry(Long64_t entry);
  virtual Long64_t LoadTree(Long64_t entry);
  virtual void     Init(TTree *tree);
  virtual void     Loop(int maxentries = -1);
  virtual Bool_t   Notify();
  virtual void     Show(Long64_t entry = -1);
  virtual void     setFlavor(int);
  virtual void     setOutfile(TString);
  virtual bool     isTagLepton(int);

  int fFlavor;
  TString fOutfile;

  void bookOutputTree();

  float puw2016_nTrueInt_36fb(int nTrueInt);
};

#endif

#ifdef TnPNtuplesBase_cxx
TnPNtuplesBase::TnPNtuplesBase(TTree *tree, TTree *ftree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_2018-07-06-2l_triggerMatch_MUONS/SingleMuon_Run2016C/treeProducerWMass/tree.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("/eos/user/m/mdunser/w-helicity-13TeV/trees/TREES_2018-07-06-2l_triggerMatch_MUONS/SingleMuon_Run2016C/treeProducerWMass/tree.root");
      }
      f->GetObject("tree",tree);

   }
   if (ftree) tree->AddFriend(ftree); 
   Init(tree);
}

TnPNtuplesBase::~TnPNtuplesBase()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t TnPNtuplesBase::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t TnPNtuplesBase::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void TnPNtuplesBase::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("run", &run, &b_run);
   fChain->SetBranchAddress("lumi", &lumi, &b_lumi);
   fChain->SetBranchAddress("evt", &evt, &b_evt);
   fChain->SetBranchAddress("isData", &isData, &b_isData);
   fChain->SetBranchAddress("xsec", &xsec, &b_xsec);
   fChain->SetBranchAddress("puWeight", &puWeight, &b_puWeight);
   fChain->SetBranchAddress("nTrueInt", &nTrueInt, &b_nTrueInt);
   fChain->SetBranchAddress("genWeight", &genWeight, &b_genWeight);
   fChain->SetBranchAddress("intLumi", &intLumi, &b_intLumi);
   fChain->SetBranchAddress("Flag_badMuonMoriond2017", &Flag_badMuonMoriond2017, &b_Flag_badMuonMoriond2017);
   fChain->SetBranchAddress("Flag_badCloneMuonMoriond2017", &Flag_badCloneMuonMoriond2017, &b_Flag_badCloneMuonMoriond2017);
   fChain->SetBranchAddress("badCloneMuonMoriond2017_maxPt", &badCloneMuonMoriond2017_maxPt, &b_badCloneMuonMoriond2017_maxPt);
   fChain->SetBranchAddress("badNotCloneMuonMoriond2017_maxPt", &badNotCloneMuonMoriond2017_maxPt, &b_badNotCloneMuonMoriond2017_maxPt);
   fChain->SetBranchAddress("rho", &rho, &b_rho);
   fChain->SetBranchAddress("rhoCN", &rhoCN, &b_rhoCN);
   fChain->SetBranchAddress("nVert", &nVert, &b_nVert);
   fChain->SetBranchAddress("mZ1", &mZ1, &b_mZ1);
   fChain->SetBranchAddress("puppimet_sumEt", &puppimet_sumEt, &b_puppimet_sumEt);
   fChain->SetBranchAddress("met_sumEt", &met_sumEt, &b_met_sumEt);
   fChain->SetBranchAddress("tkMetPVchs_sumEt", &tkMetPVchs_sumEt, &b_tkMetPVchs_sumEt);
   fChain->SetBranchAddress("tkMetPVLoose_sumEt", &tkMetPVLoose_sumEt, &b_tkMetPVLoose_sumEt);
   fChain->SetBranchAddress("tkMetPUPVLoose_sumEt", &tkMetPUPVLoose_sumEt, &b_tkMetPUPVLoose_sumEt);
   fChain->SetBranchAddress("tkMetPVTight_sumEt", &tkMetPVTight_sumEt, &b_tkMetPVTight_sumEt);
   fChain->SetBranchAddress("ntMet_sumEt", &ntMet_sumEt, &b_ntMet_sumEt);
   fChain->SetBranchAddress("ntCentralMet_sumEt", &ntCentralMet_sumEt, &b_ntCentralMet_sumEt);
   fChain->SetBranchAddress("tkMetPVchs_Count", &tkMetPVchs_Count, &b_tkMetPVchs_Count);
   fChain->SetBranchAddress("tkMetPVLoose_Count", &tkMetPVLoose_Count, &b_tkMetPVLoose_Count);
   fChain->SetBranchAddress("tkMetPUPVLoose_Count", &tkMetPUPVLoose_Count, &b_tkMetPUPVLoose_Count);
   fChain->SetBranchAddress("tkMetPVTight_Count", &tkMetPVTight_Count, &b_tkMetPVTight_Count);
   fChain->SetBranchAddress("ntMet_Count", &ntMet_Count, &b_ntMet_Count);
   fChain->SetBranchAddress("ntCentralMet_Count", &ntCentralMet_Count, &b_ntCentralMet_Count);
   fChain->SetBranchAddress("hbheFilterNew50ns", &hbheFilterNew50ns, &b_hbheFilterNew50ns);
   fChain->SetBranchAddress("hbheFilterNew25ns", &hbheFilterNew25ns, &b_hbheFilterNew25ns);
   fChain->SetBranchAddress("hbheFilterIso", &hbheFilterIso, &b_hbheFilterIso);
   fChain->SetBranchAddress("Flag_badChargedHadronFilter", &Flag_badChargedHadronFilter, &b_Flag_badChargedHadronFilter);
   fChain->SetBranchAddress("Flag_badMuonFilter", &Flag_badMuonFilter, &b_Flag_badMuonFilter);
   fChain->SetBranchAddress("met_trkPt", &met_trkPt, &b_met_trkPt);
   fChain->SetBranchAddress("met_trkPhi", &met_trkPhi, &b_met_trkPhi);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu20_v", &HLT_BIT_HLT_IsoMu20_v, &b_HLT_BIT_HLT_IsoMu20_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu20_v_isUnprescaled", &HLT_BIT_HLT_IsoMu20_v_isUnprescaled, &b_HLT_BIT_HLT_IsoMu20_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu20_v_Prescale", &HLT_BIT_HLT_IsoMu20_v_Prescale, &b_HLT_BIT_HLT_IsoMu20_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu20_v", &HLT_BIT_HLT_IsoTkMu20_v, &b_HLT_BIT_HLT_IsoTkMu20_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu20_v_isUnprescaled", &HLT_BIT_HLT_IsoTkMu20_v_isUnprescaled, &b_HLT_BIT_HLT_IsoTkMu20_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu20_v_Prescale", &HLT_BIT_HLT_IsoTkMu20_v_Prescale, &b_HLT_BIT_HLT_IsoTkMu20_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu22_v", &HLT_BIT_HLT_IsoMu22_v, &b_HLT_BIT_HLT_IsoMu22_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu22_v_isUnprescaled", &HLT_BIT_HLT_IsoMu22_v_isUnprescaled, &b_HLT_BIT_HLT_IsoMu22_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu22_v_Prescale", &HLT_BIT_HLT_IsoMu22_v_Prescale, &b_HLT_BIT_HLT_IsoMu22_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu22_v", &HLT_BIT_HLT_IsoTkMu22_v, &b_HLT_BIT_HLT_IsoTkMu22_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu22_v_isUnprescaled", &HLT_BIT_HLT_IsoTkMu22_v_isUnprescaled, &b_HLT_BIT_HLT_IsoTkMu22_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu22_v_Prescale", &HLT_BIT_HLT_IsoTkMu22_v_Prescale, &b_HLT_BIT_HLT_IsoTkMu22_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu24_v", &HLT_BIT_HLT_IsoMu24_v, &b_HLT_BIT_HLT_IsoMu24_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu24_v_isUnprescaled", &HLT_BIT_HLT_IsoMu24_v_isUnprescaled, &b_HLT_BIT_HLT_IsoMu24_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu24_v_Prescale", &HLT_BIT_HLT_IsoMu24_v_Prescale, &b_HLT_BIT_HLT_IsoMu24_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu24_v", &HLT_BIT_HLT_IsoTkMu24_v, &b_HLT_BIT_HLT_IsoTkMu24_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu24_v_isUnprescaled", &HLT_BIT_HLT_IsoTkMu24_v_isUnprescaled, &b_HLT_BIT_HLT_IsoTkMu24_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu24_v_Prescale", &HLT_BIT_HLT_IsoTkMu24_v_Prescale, &b_HLT_BIT_HLT_IsoTkMu24_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu22_eta2p1_v", &HLT_BIT_HLT_IsoMu22_eta2p1_v, &b_HLT_BIT_HLT_IsoMu22_eta2p1_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu22_eta2p1_v_isUnprescaled", &HLT_BIT_HLT_IsoMu22_eta2p1_v_isUnprescaled, &b_HLT_BIT_HLT_IsoMu22_eta2p1_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoMu22_eta2p1_v_Prescale", &HLT_BIT_HLT_IsoMu22_eta2p1_v_Prescale, &b_HLT_BIT_HLT_IsoMu22_eta2p1_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu22_eta2p1_v", &HLT_BIT_HLT_IsoTkMu22_eta2p1_v, &b_HLT_BIT_HLT_IsoTkMu22_eta2p1_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu22_eta2p1_v_isUnprescaled", &HLT_BIT_HLT_IsoTkMu22_eta2p1_v_isUnprescaled, &b_HLT_BIT_HLT_IsoTkMu22_eta2p1_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_IsoTkMu22_eta2p1_v_Prescale", &HLT_BIT_HLT_IsoTkMu22_eta2p1_v_Prescale, &b_HLT_BIT_HLT_IsoTkMu22_eta2p1_v_Prescale);
   fChain->SetBranchAddress("HLT_SingleMu", &HLT_SingleMu, &b_HLT_SingleMu);
   fChain->SetBranchAddress("HLT_SingleMu_isUnprescaled", &HLT_SingleMu_isUnprescaled, &b_HLT_SingleMu_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_Mu8_SameSign_v", &HLT_BIT_HLT_Mu17_Mu8_SameSign_v, &b_HLT_BIT_HLT_Mu17_Mu8_SameSign_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_Mu8_SameSign_v_isUnprescaled", &HLT_BIT_HLT_Mu17_Mu8_SameSign_v_isUnprescaled, &b_HLT_BIT_HLT_Mu17_Mu8_SameSign_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_Mu8_SameSign_v_Prescale", &HLT_BIT_HLT_Mu17_Mu8_SameSign_v_Prescale, &b_HLT_BIT_HLT_Mu17_Mu8_SameSign_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v", &HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v, &b_HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_isUnprescaled", &HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_Prescale", &HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_Prescale, &b_HLT_BIT_HLT_Mu17_Mu8_SameSign_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu20_Mu10_SameSign_v", &HLT_BIT_HLT_Mu20_Mu10_SameSign_v, &b_HLT_BIT_HLT_Mu20_Mu10_SameSign_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu20_Mu10_SameSign_v_isUnprescaled", &HLT_BIT_HLT_Mu20_Mu10_SameSign_v_isUnprescaled, &b_HLT_BIT_HLT_Mu20_Mu10_SameSign_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu20_Mu10_SameSign_v_Prescale", &HLT_BIT_HLT_Mu20_Mu10_SameSign_v_Prescale, &b_HLT_BIT_HLT_Mu20_Mu10_SameSign_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v", &HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v, &b_HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_isUnprescaled", &HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_Prescale", &HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_Prescale, &b_HLT_BIT_HLT_Mu20_Mu10_SameSign_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_DoubleMuSS", &HLT_DoubleMuSS, &b_HLT_DoubleMuSS);
   fChain->SetBranchAddress("HLT_DoubleMuSS_isUnprescaled", &HLT_DoubleMuSS_isUnprescaled, &b_HLT_DoubleMuSS_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu30_TkMu11_v", &HLT_BIT_HLT_Mu30_TkMu11_v, &b_HLT_BIT_HLT_Mu30_TkMu11_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu30_TkMu11_v_isUnprescaled", &HLT_BIT_HLT_Mu30_TkMu11_v_isUnprescaled, &b_HLT_BIT_HLT_Mu30_TkMu11_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu30_TkMu11_v_Prescale", &HLT_BIT_HLT_Mu30_TkMu11_v_Prescale, &b_HLT_BIT_HLT_Mu30_TkMu11_v_Prescale);
   fChain->SetBranchAddress("HLT_DoubleMuNoIso", &HLT_DoubleMuNoIso, &b_HLT_DoubleMuNoIso);
   fChain->SetBranchAddress("HLT_DoubleMuNoIso_isUnprescaled", &HLT_DoubleMuNoIso_isUnprescaled, &b_HLT_DoubleMuNoIso_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v", &HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled", &HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale", &HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v", &HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v, &b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled", &HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled, &b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_Prescale", &HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_Prescale, &b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_Prescale", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_Prescale, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v", &HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v, &b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled", &HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled, &b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_Prescale", &HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_Prescale, &b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v", &HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v, &b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled", &HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale", &HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale, &b_HLT_BIT_HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_MuEG", &HLT_MuEG, &b_HLT_MuEG);
   fChain->SetBranchAddress("HLT_MuEG_isUnprescaled", &HLT_MuEG_isUnprescaled, &b_HLT_MuEG_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele25_WPTight_Gsf_v", &HLT_BIT_HLT_Ele25_WPTight_Gsf_v, &b_HLT_BIT_HLT_Ele25_WPTight_Gsf_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele25_WPTight_Gsf_v_isUnprescaled", &HLT_BIT_HLT_Ele25_WPTight_Gsf_v_isUnprescaled, &b_HLT_BIT_HLT_Ele25_WPTight_Gsf_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele25_WPTight_Gsf_v_Prescale", &HLT_BIT_HLT_Ele25_WPTight_Gsf_v_Prescale, &b_HLT_BIT_HLT_Ele25_WPTight_Gsf_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v", &HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v, &b_HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_isUnprescaled", &HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_isUnprescaled, &b_HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_Prescale", &HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_Prescale, &b_HLT_BIT_HLT_Ele25_eta2p1_WPLoose_Gsf_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v", &HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v, &b_HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_isUnprescaled", &HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_isUnprescaled, &b_HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_Prescale", &HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_Prescale, &b_HLT_BIT_HLT_Ele25_eta2p1_WPTight_Gsf_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele27_WPTight_Gsf_v", &HLT_BIT_HLT_Ele27_WPTight_Gsf_v, &b_HLT_BIT_HLT_Ele27_WPTight_Gsf_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele27_WPTight_Gsf_v_isUnprescaled", &HLT_BIT_HLT_Ele27_WPTight_Gsf_v_isUnprescaled, &b_HLT_BIT_HLT_Ele27_WPTight_Gsf_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele27_WPTight_Gsf_v_Prescale", &HLT_BIT_HLT_Ele27_WPTight_Gsf_v_Prescale, &b_HLT_BIT_HLT_Ele27_WPTight_Gsf_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v", &HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v, &b_HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_isUnprescaled", &HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_isUnprescaled, &b_HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_Prescale", &HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_Prescale, &b_HLT_BIT_HLT_Ele27_eta2p1_WPLoose_Gsf_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele45_WPLoose_Gsf_v", &HLT_BIT_HLT_Ele45_WPLoose_Gsf_v, &b_HLT_BIT_HLT_Ele45_WPLoose_Gsf_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_isUnprescaled", &HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_isUnprescaled, &b_HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_Prescale", &HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_Prescale, &b_HLT_BIT_HLT_Ele45_WPLoose_Gsf_v_Prescale);
   fChain->SetBranchAddress("HLT_SingleEl", &HLT_SingleEl, &b_HLT_SingleEl);
   fChain->SetBranchAddress("HLT_SingleEl_isUnprescaled", &HLT_SingleEl_isUnprescaled, &b_HLT_SingleEl_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v", &HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v, &b_HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled", &HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale", &HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale, &b_HLT_BIT_HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v", &HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v, &b_HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled", &HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale", &HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale, &b_HLT_BIT_HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_DoubleEl", &HLT_DoubleEl, &b_HLT_DoubleEl);
   fChain->SetBranchAddress("HLT_DoubleEl_isUnprescaled", &HLT_DoubleEl_isUnprescaled, &b_HLT_DoubleEl_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v", &HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled", &HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale", &HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v", &HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled", &HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale", &HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v", &HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled", &HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale", &HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v", &HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled", &HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale", &HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale, &b_HLT_BIT_HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v", &HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled", &HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale", &HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale", &HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v", &HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled", &HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_isUnprescaled);
   fChain->SetBranchAddress("HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale", &HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale, &b_HLT_BIT_HLT_Mu23_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v_Prescale);
   fChain->SetBranchAddress("HLT_DoubleMu", &HLT_DoubleMu, &b_HLT_DoubleMu);
   fChain->SetBranchAddress("HLT_DoubleMu_isUnprescaled", &HLT_DoubleMu_isUnprescaled, &b_HLT_DoubleMu_isUnprescaled);
   fChain->SetBranchAddress("Flag_hcalLaserEventFilter", &Flag_hcalLaserEventFilter, &b_Flag_hcalLaserEventFilter);
   fChain->SetBranchAddress("Flag_trkPOG_logErrorTooManyClusters", &Flag_trkPOG_logErrorTooManyClusters, &b_Flag_trkPOG_logErrorTooManyClusters);
   fChain->SetBranchAddress("Flag_EcalDeadCellTriggerPrimitiveFilter", &Flag_EcalDeadCellTriggerPrimitiveFilter, &b_Flag_EcalDeadCellTriggerPrimitiveFilter);
   fChain->SetBranchAddress("Flag_trkPOGFilters", &Flag_trkPOGFilters, &b_Flag_trkPOGFilters);
   fChain->SetBranchAddress("Flag_trackingFailureFilter", &Flag_trackingFailureFilter, &b_Flag_trackingFailureFilter);
   fChain->SetBranchAddress("Flag_CSCTightHaloFilter", &Flag_CSCTightHaloFilter, &b_Flag_CSCTightHaloFilter);
   fChain->SetBranchAddress("Flag_HBHENoiseFilter", &Flag_HBHENoiseFilter, &b_Flag_HBHENoiseFilter);
   fChain->SetBranchAddress("Flag_MuFlag_bad", &Flag_MuFlag_bad, &b_Flag_MuFlag_bad);
   fChain->SetBranchAddress("Flag_MuFlag_good", &Flag_MuFlag_good, &b_Flag_MuFlag_good);
   fChain->SetBranchAddress("Flag_HBHENoiseIsoFilter", &Flag_HBHENoiseIsoFilter, &b_Flag_HBHENoiseIsoFilter);
   fChain->SetBranchAddress("Flag_goodVertices", &Flag_goodVertices, &b_Flag_goodVertices);
   fChain->SetBranchAddress("Flag_trkPOG_manystripclus53X", &Flag_trkPOG_manystripclus53X, &b_Flag_trkPOG_manystripclus53X);
   fChain->SetBranchAddress("Flag_MuFlag_dup", &Flag_MuFlag_dup, &b_Flag_MuFlag_dup);
   fChain->SetBranchAddress("Flag_CSCTightHalo2016Filter", &Flag_CSCTightHalo2016Filter, &b_Flag_CSCTightHalo2016Filter);
   fChain->SetBranchAddress("Flag_ecalLaserCorrFilter", &Flag_ecalLaserCorrFilter, &b_Flag_ecalLaserCorrFilter);
   fChain->SetBranchAddress("Flag_trkPOG_toomanystripclus53X", &Flag_trkPOG_toomanystripclus53X, &b_Flag_trkPOG_toomanystripclus53X);
   fChain->SetBranchAddress("Flag_CSCTightHalo2015Filter", &Flag_CSCTightHalo2015Filter, &b_Flag_CSCTightHalo2015Filter);
   fChain->SetBranchAddress("Flag_eeBadScFilter", &Flag_eeBadScFilter, &b_Flag_eeBadScFilter);
   fChain->SetBranchAddress("Flag_globalTightHalo2016Filter", &Flag_globalTightHalo2016Filter, &b_Flag_globalTightHalo2016Filter);
   fChain->SetBranchAddress("leadNeutral_pt", &leadNeutral_pt, &b_leadNeutral_pt);
   fChain->SetBranchAddress("leadNeutral_eta", &leadNeutral_eta, &b_leadNeutral_eta);
   fChain->SetBranchAddress("leadNeutral_phi", &leadNeutral_phi, &b_leadNeutral_phi);
   fChain->SetBranchAddress("leadNeutral_mass", &leadNeutral_mass, &b_leadNeutral_mass);
   fChain->SetBranchAddress("met_jecUp_pt", &met_jecUp_pt, &b_met_jecUp_pt);
   fChain->SetBranchAddress("met_jecUp_eta", &met_jecUp_eta, &b_met_jecUp_eta);
   fChain->SetBranchAddress("met_jecUp_phi", &met_jecUp_phi, &b_met_jecUp_phi);
   fChain->SetBranchAddress("met_jecUp_mass", &met_jecUp_mass, &b_met_jecUp_mass);
   fChain->SetBranchAddress("met_jecUp_sumEt", &met_jecUp_sumEt, &b_met_jecUp_sumEt);
   fChain->SetBranchAddress("met_jecUp_rawPt", &met_jecUp_rawPt, &b_met_jecUp_rawPt);
   fChain->SetBranchAddress("met_jecUp_rawPhi", &met_jecUp_rawPhi, &b_met_jecUp_rawPhi);
   fChain->SetBranchAddress("met_jecUp_rawSumEt", &met_jecUp_rawSumEt, &b_met_jecUp_rawSumEt);
   fChain->SetBranchAddress("tkMetPVchs_pt", &tkMetPVchs_pt, &b_tkMetPVchs_pt);
   fChain->SetBranchAddress("tkMetPVchs_eta", &tkMetPVchs_eta, &b_tkMetPVchs_eta);
   fChain->SetBranchAddress("tkMetPVchs_phi", &tkMetPVchs_phi, &b_tkMetPVchs_phi);
   fChain->SetBranchAddress("tkMetPVchs_mass", &tkMetPVchs_mass, &b_tkMetPVchs_mass);
   fChain->SetBranchAddress("ntMet_pt", &ntMet_pt, &b_ntMet_pt);
   fChain->SetBranchAddress("ntMet_eta", &ntMet_eta, &b_ntMet_eta);
   fChain->SetBranchAddress("ntMet_phi", &ntMet_phi, &b_ntMet_phi);
   fChain->SetBranchAddress("ntMet_mass", &ntMet_mass, &b_ntMet_mass);
   fChain->SetBranchAddress("leadCharged_pt", &leadCharged_pt, &b_leadCharged_pt);
   fChain->SetBranchAddress("leadCharged_eta", &leadCharged_eta, &b_leadCharged_eta);
   fChain->SetBranchAddress("leadCharged_phi", &leadCharged_phi, &b_leadCharged_phi);
   fChain->SetBranchAddress("leadCharged_mass", &leadCharged_mass, &b_leadCharged_mass);
   fChain->SetBranchAddress("tkMetPVLoose_pt", &tkMetPVLoose_pt, &b_tkMetPVLoose_pt);
   fChain->SetBranchAddress("tkMetPVLoose_eta", &tkMetPVLoose_eta, &b_tkMetPVLoose_eta);
   fChain->SetBranchAddress("tkMetPVLoose_phi", &tkMetPVLoose_phi, &b_tkMetPVLoose_phi);
   fChain->SetBranchAddress("tkMetPVLoose_mass", &tkMetPVLoose_mass, &b_tkMetPVLoose_mass);
   fChain->SetBranchAddress("met_jecDown_pt", &met_jecDown_pt, &b_met_jecDown_pt);
   fChain->SetBranchAddress("met_jecDown_eta", &met_jecDown_eta, &b_met_jecDown_eta);
   fChain->SetBranchAddress("met_jecDown_phi", &met_jecDown_phi, &b_met_jecDown_phi);
   fChain->SetBranchAddress("met_jecDown_mass", &met_jecDown_mass, &b_met_jecDown_mass);
   fChain->SetBranchAddress("met_jecDown_sumEt", &met_jecDown_sumEt, &b_met_jecDown_sumEt);
   fChain->SetBranchAddress("met_jecDown_rawPt", &met_jecDown_rawPt, &b_met_jecDown_rawPt);
   fChain->SetBranchAddress("met_jecDown_rawPhi", &met_jecDown_rawPhi, &b_met_jecDown_rawPhi);
   fChain->SetBranchAddress("met_jecDown_rawSumEt", &met_jecDown_rawSumEt, &b_met_jecDown_rawSumEt);
   fChain->SetBranchAddress("tkMetPVTight_pt", &tkMetPVTight_pt, &b_tkMetPVTight_pt);
   fChain->SetBranchAddress("tkMetPVTight_eta", &tkMetPVTight_eta, &b_tkMetPVTight_eta);
   fChain->SetBranchAddress("tkMetPVTight_phi", &tkMetPVTight_phi, &b_tkMetPVTight_phi);
   fChain->SetBranchAddress("tkMetPVTight_mass", &tkMetPVTight_mass, &b_tkMetPVTight_mass);
   fChain->SetBranchAddress("met_pt", &met_pt, &b_met_pt);
   fChain->SetBranchAddress("met_eta", &met_eta, &b_met_eta);
   fChain->SetBranchAddress("met_phi", &met_phi, &b_met_phi);
   fChain->SetBranchAddress("met_mass", &met_mass, &b_met_mass);
   fChain->SetBranchAddress("ntCentralMet_pt", &ntCentralMet_pt, &b_ntCentralMet_pt);
   fChain->SetBranchAddress("ntCentralMet_eta", &ntCentralMet_eta, &b_ntCentralMet_eta);
   fChain->SetBranchAddress("ntCentralMet_phi", &ntCentralMet_phi, &b_ntCentralMet_phi);
   fChain->SetBranchAddress("ntCentralMet_mass", &ntCentralMet_mass, &b_ntCentralMet_mass);
   fChain->SetBranchAddress("tkMetPUPVLoose_pt", &tkMetPUPVLoose_pt, &b_tkMetPUPVLoose_pt);
   fChain->SetBranchAddress("tkMetPUPVLoose_eta", &tkMetPUPVLoose_eta, &b_tkMetPUPVLoose_eta);
   fChain->SetBranchAddress("tkMetPUPVLoose_phi", &tkMetPUPVLoose_phi, &b_tkMetPUPVLoose_phi);
   fChain->SetBranchAddress("tkMetPUPVLoose_mass", &tkMetPUPVLoose_mass, &b_tkMetPUPVLoose_mass);
   fChain->SetBranchAddress("puppimet_pt", &puppimet_pt, &b_puppimet_pt);
   fChain->SetBranchAddress("puppimet_eta", &puppimet_eta, &b_puppimet_eta);
   fChain->SetBranchAddress("puppimet_phi", &puppimet_phi, &b_puppimet_phi);
   fChain->SetBranchAddress("puppimet_mass", &puppimet_mass, &b_puppimet_mass);
   fChain->SetBranchAddress("nGenPart", &nGenPart, &b_nGenPart);
   fChain->SetBranchAddress("GenPart_motherId", GenPart_motherId, &b_GenPart_motherId);
   fChain->SetBranchAddress("GenPart_grandmotherId", GenPart_grandmotherId, &b_GenPart_grandmotherId);
   fChain->SetBranchAddress("GenPart_sourceId", GenPart_sourceId, &b_GenPart_sourceId);
   fChain->SetBranchAddress("GenPart_charge", GenPart_charge, &b_GenPart_charge);
   fChain->SetBranchAddress("GenPart_status", GenPart_status, &b_GenPart_status);
   fChain->SetBranchAddress("GenPart_isPromptHard", GenPart_isPromptHard, &b_GenPart_isPromptHard);
   fChain->SetBranchAddress("GenPart_pdgId", GenPart_pdgId, &b_GenPart_pdgId);
   fChain->SetBranchAddress("GenPart_pt", GenPart_pt, &b_GenPart_pt);
   fChain->SetBranchAddress("GenPart_eta", GenPart_eta, &b_GenPart_eta);
   fChain->SetBranchAddress("GenPart_phi", GenPart_phi, &b_GenPart_phi);
   fChain->SetBranchAddress("GenPart_mass", GenPart_mass, &b_GenPart_mass);
   fChain->SetBranchAddress("GenPart_motherIndex", GenPart_motherIndex, &b_GenPart_motherIndex);
   fChain->SetBranchAddress("nJet", &nJet, &b_nJet);
   fChain->SetBranchAddress("Jet_charge", Jet_charge, &b_Jet_charge);
   fChain->SetBranchAddress("Jet_ctagCsvL", Jet_ctagCsvL, &b_Jet_ctagCsvL);
   fChain->SetBranchAddress("Jet_ctagCsvB", Jet_ctagCsvB, &b_Jet_ctagCsvB);
   fChain->SetBranchAddress("Jet_area", Jet_area, &b_Jet_area);
   fChain->SetBranchAddress("Jet_qgl", Jet_qgl, &b_Jet_qgl);
   fChain->SetBranchAddress("Jet_ptd", Jet_ptd, &b_Jet_ptd);
   fChain->SetBranchAddress("Jet_axis2", Jet_axis2, &b_Jet_axis2);
   fChain->SetBranchAddress("Jet_mult", Jet_mult, &b_Jet_mult);
   fChain->SetBranchAddress("Jet_nLeptons", Jet_nLeptons, &b_Jet_nLeptons);
   fChain->SetBranchAddress("Jet_id", Jet_id, &b_Jet_id);
   fChain->SetBranchAddress("Jet_puId", Jet_puId, &b_Jet_puId);
   fChain->SetBranchAddress("Jet_btagCSV", Jet_btagCSV, &b_Jet_btagCSV);
   fChain->SetBranchAddress("Jet_btagCMVA", Jet_btagCMVA, &b_Jet_btagCMVA);
   fChain->SetBranchAddress("Jet_rawPt", Jet_rawPt, &b_Jet_rawPt);
   fChain->SetBranchAddress("Jet_corr_JECUp", Jet_corr_JECUp, &b_Jet_corr_JECUp);
   fChain->SetBranchAddress("Jet_corr_JECDown", Jet_corr_JECDown, &b_Jet_corr_JECDown);
   fChain->SetBranchAddress("Jet_corr", Jet_corr, &b_Jet_corr);
   fChain->SetBranchAddress("Jet_pt", Jet_pt, &b_Jet_pt);
   fChain->SetBranchAddress("Jet_eta", Jet_eta, &b_Jet_eta);
   fChain->SetBranchAddress("Jet_phi", Jet_phi, &b_Jet_phi);
   fChain->SetBranchAddress("Jet_mass", Jet_mass, &b_Jet_mass);
   fChain->SetBranchAddress("Jet_CorrFactor_L1", Jet_CorrFactor_L1, &b_Jet_CorrFactor_L1);
   fChain->SetBranchAddress("Jet_CorrFactor_L1L2", Jet_CorrFactor_L1L2, &b_Jet_CorrFactor_L1L2);
   fChain->SetBranchAddress("Jet_CorrFactor_L1L2L3", Jet_CorrFactor_L1L2L3, &b_Jet_CorrFactor_L1L2L3);
   fChain->SetBranchAddress("Jet_CorrFactor_L1L2L3Res", Jet_CorrFactor_L1L2L3Res, &b_Jet_CorrFactor_L1L2L3Res);
   fChain->SetBranchAddress("Jet_chHEF", Jet_chHEF, &b_Jet_chHEF);
   fChain->SetBranchAddress("Jet_neHEF", Jet_neHEF, &b_Jet_neHEF);
   fChain->SetBranchAddress("nLepGood", &nLepGood, &b_nLepGood);
   fChain->SetBranchAddress("LepGood_charge", LepGood_charge, &b_LepGood_charge);
   fChain->SetBranchAddress("LepGood_tightId", LepGood_tightId, &b_LepGood_tightId);
   fChain->SetBranchAddress("LepGood_hltId", LepGood_hltId, &b_LepGood_hltId);
   fChain->SetBranchAddress("LepGood_eleCutIdCSA14_25ns_v1", LepGood_eleCutIdCSA14_25ns_v1, &b_LepGood_eleCutIdCSA14_25ns_v1);
   fChain->SetBranchAddress("LepGood_eleCutIdCSA14_50ns_v1", LepGood_eleCutIdCSA14_50ns_v1, &b_LepGood_eleCutIdCSA14_50ns_v1);
   fChain->SetBranchAddress("LepGood_eleCutIdSpring15_25ns_v1", LepGood_eleCutIdSpring15_25ns_v1, &b_LepGood_eleCutIdSpring15_25ns_v1);
   fChain->SetBranchAddress("LepGood_dxy", LepGood_dxy, &b_LepGood_dxy);
   fChain->SetBranchAddress("LepGood_dz", LepGood_dz, &b_LepGood_dz);
   fChain->SetBranchAddress("LepGood_edxy", LepGood_edxy, &b_LepGood_edxy);
   fChain->SetBranchAddress("LepGood_edz", LepGood_edz, &b_LepGood_edz);
   fChain->SetBranchAddress("LepGood_ip3d", LepGood_ip3d, &b_LepGood_ip3d);
   fChain->SetBranchAddress("LepGood_sip3d", LepGood_sip3d, &b_LepGood_sip3d);
   fChain->SetBranchAddress("LepGood_convVeto", LepGood_convVeto, &b_LepGood_convVeto);
   fChain->SetBranchAddress("LepGood_lostHits", LepGood_lostHits, &b_LepGood_lostHits);
   fChain->SetBranchAddress("LepGood_relIso03", LepGood_relIso03, &b_LepGood_relIso03);
   fChain->SetBranchAddress("LepGood_relIso04", LepGood_relIso04, &b_LepGood_relIso04);
   fChain->SetBranchAddress("LepGood_miniRelIso", LepGood_miniRelIso, &b_LepGood_miniRelIso);
   fChain->SetBranchAddress("LepGood_relIsoAn04", LepGood_relIsoAn04, &b_LepGood_relIsoAn04);
   fChain->SetBranchAddress("LepGood_tightCharge", LepGood_tightCharge, &b_LepGood_tightCharge);
   fChain->SetBranchAddress("LepGood_mediumMuonId", LepGood_mediumMuonId, &b_LepGood_mediumMuonId);
   fChain->SetBranchAddress("LepGood_ICHEPsoftMuonId", LepGood_ICHEPsoftMuonId, &b_LepGood_ICHEPsoftMuonId);
   fChain->SetBranchAddress("LepGood_ICHEPmediumMuonId", LepGood_ICHEPmediumMuonId, &b_LepGood_ICHEPmediumMuonId);
   fChain->SetBranchAddress("LepGood_pdgId", LepGood_pdgId, &b_LepGood_pdgId);
   fChain->SetBranchAddress("LepGood_pt", LepGood_pt, &b_LepGood_pt);
   fChain->SetBranchAddress("LepGood_eta", LepGood_eta, &b_LepGood_eta);
   fChain->SetBranchAddress("LepGood_phi", LepGood_phi, &b_LepGood_phi);
   fChain->SetBranchAddress("LepGood_mass", LepGood_mass, &b_LepGood_mass);
   fChain->SetBranchAddress("LepGood_jetDR", LepGood_jetDR, &b_LepGood_jetDR);
   fChain->SetBranchAddress("LepGood_r9", LepGood_r9, &b_LepGood_r9);
   fChain->SetBranchAddress("LepGood_chIso04", LepGood_chIso04, &b_LepGood_chIso04);
   fChain->SetBranchAddress("LepGood_nhIso04", LepGood_nhIso04, &b_LepGood_nhIso04);
   fChain->SetBranchAddress("LepGood_phIso04", LepGood_phIso04, &b_LepGood_phIso04);
   fChain->SetBranchAddress("LepGood_softMuonId2016", LepGood_softMuonId2016, &b_LepGood_softMuonId2016);
   fChain->SetBranchAddress("LepGood_mediumMuonID2016", LepGood_mediumMuonID2016, &b_LepGood_mediumMuonID2016);
   fChain->SetBranchAddress("LepGood_tightChargeFix", LepGood_tightChargeFix, &b_LepGood_tightChargeFix);
   fChain->SetBranchAddress("LepGood_muonTrackType", LepGood_muonTrackType, &b_LepGood_muonTrackType);
   fChain->SetBranchAddress("LepGood_chargeConsistency", LepGood_chargeConsistency, &b_LepGood_chargeConsistency);
   fChain->SetBranchAddress("LepGood_ptErrTk", LepGood_ptErrTk, &b_LepGood_ptErrTk);
   fChain->SetBranchAddress("LepGood_ecalPFClusterIso", LepGood_ecalPFClusterIso, &b_LepGood_ecalPFClusterIso);
   fChain->SetBranchAddress("LepGood_hcalPFClusterIso", LepGood_hcalPFClusterIso, &b_LepGood_hcalPFClusterIso);
   fChain->SetBranchAddress("LepGood_dr03TkSumPt", LepGood_dr03TkSumPt, &b_LepGood_dr03TkSumPt);
   fChain->SetBranchAddress("LepGood_trackIso", LepGood_trackIso, &b_LepGood_trackIso);
   fChain->SetBranchAddress("LepGood_trackIso03", LepGood_trackIso03, &b_LepGood_trackIso03);
   fChain->SetBranchAddress("LepGood_etaSc", LepGood_etaSc, &b_LepGood_etaSc);
   fChain->SetBranchAddress("LepGood_energySc", LepGood_energySc, &b_LepGood_energySc);
   fChain->SetBranchAddress("LepGood_e5x5", LepGood_e5x5, &b_LepGood_e5x5);
   fChain->SetBranchAddress("LepGood_sigmaIetaIeta", LepGood_sigmaIetaIeta, &b_LepGood_sigmaIetaIeta);
   fChain->SetBranchAddress("LepGood_hcalOverEcal", LepGood_hcalOverEcal, &b_LepGood_hcalOverEcal);
   fChain->SetBranchAddress("LepGood_eSuperClusterOverP", LepGood_eSuperClusterOverP, &b_LepGood_eSuperClusterOverP);
   fChain->SetBranchAddress("LepGood_matchedTrgObjElePt", LepGood_matchedTrgObjElePt, &b_LepGood_matchedTrgObjElePt);
   fChain->SetBranchAddress("LepGood_matchedTrgObjEleDR", LepGood_matchedTrgObjEleDR, &b_LepGood_matchedTrgObjEleDR);
   fChain->SetBranchAddress("LepGood_matchedTrgObjMuPt", LepGood_matchedTrgObjMuPt, &b_LepGood_matchedTrgObjMuPt);
   fChain->SetBranchAddress("LepGood_matchedTrgObjMuDR", LepGood_matchedTrgObjMuDR, &b_LepGood_matchedTrgObjMuDR);
   fChain->SetBranchAddress("LepGood_matchedTrgObjTkMuPt", LepGood_matchedTrgObjTkMuPt, &b_LepGood_matchedTrgObjTkMuPt);
   fChain->SetBranchAddress("LepGood_matchedTrgObjTkMuDR", LepGood_matchedTrgObjTkMuDR, &b_LepGood_matchedTrgObjTkMuDR);
   fChain->SetBranchAddress("LepGood_customId",LepGood_customId, &b_LepGood_customId);
   fChain->SetBranchAddress("LepGood_calPt",LepGood_calPt, &b_LepGood_calPt);
   Notify();
}

Bool_t TnPNtuplesBase::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void TnPNtuplesBase::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t TnPNtuplesBase::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef TnPNtuplesBase_cxx
