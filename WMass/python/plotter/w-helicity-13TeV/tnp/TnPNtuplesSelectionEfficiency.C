#ifndef TnPNtuplesSelectionEfficiency_cxx
#define TnPNtuplesSelectionEfficiency_cxx
#include "TnPNtuplesBase.C"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <iostream>
#include <TLorentzVector.h>

class TnPNtuplesSelectionEfficiency : public TnPNtuplesBase {
public:

  TnPNtuplesSelectionEfficiency(TTree *tree=0, TTree *ftree=0);
  virtual ~TnPNtuplesSelectionEfficiency();  

  void Loop(int maxentries = -1);
  bool isTagLepton(int);
  bool isLeptonInAcceptance(int jj);

protected:

};

#endif

#ifdef TnPNtuplesSelectionEfficiency_cxx
using namespace std;

TnPNtuplesSelectionEfficiency::TnPNtuplesSelectionEfficiency(TTree *tree, TTree *ftree) : TnPNtuplesBase(tree,ftree)
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

TnPNtuplesSelectionEfficiency::~TnPNtuplesSelectionEfficiency()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

bool TnPNtuplesSelectionEfficiency::isLeptonInAcceptance(int jj) {
  if(fFlavor == 11){
    if (abs(LepGood_pdgId[jj])!=11)                                      return false;
    if (LepGood_calPt[jj]<25)                                            return false;
    if (fabs(LepGood_etaSc[jj])>1.4442 && fabs(LepGood_etaSc[jj])<1.566) return false;
    if (fabs(LepGood_etaSc[jj])>2.5)                                     return false;
  }
  else {
    if (abs(LepGood_pdgId[jj])!=13)   return false;
    if (LepGood_calPt[jj]<25)         return false;
    if (fabs(LepGood_eta[jj])> 2.4)   return false;
  }
  return true;
}

bool TnPNtuplesSelectionEfficiency::isTagLepton(int jj){

  if(fFlavor == 11){
    if (abs(LepGood_pdgId[jj])!=11)                                  return false;
    if (LepGood_calPt[jj]<25)                                        return false;
    if (fabs(LepGood_eta[jj])>1.4442 && fabs(LepGood_eta[jj])<1.566) return false;
    if (fabs(LepGood_eta[jj])>2.5)                                   return false;
    if (LepGood_customId[jj] < 1)                                    return false;
    if (LepGood_hltId[jj] < 1)                                       return false;
    if (LepGood_tightChargeFix[jj] != 2 )                            return false;
  }

  else {
    if (abs(LepGood_pdgId[jj])!=13)   return false;
    if (LepGood_calPt[jj]<25)         return false;
    if (fabs(LepGood_eta[jj])> 2.4)   return false;
    if (LepGood_relIso04[jj] > 0.15)  return false;
    if (LepGood_mediumMuonId[jj] < 1) return false;
  }
  return true;

}

void TnPNtuplesSelectionEfficiency::Loop(int maxentries)
{
  // skim
  // HLT_SingleEL : HLT_SingleEl == 1
  // onelep : nLepGood == 1 && abs(LepGood1_pdgId)==11
  // fiducial : abs(LepGood1_eta)<1.4442 || abs(LepGood1_eta)>1.566
  // eleKin : ptElFull(LepGood1_calPt,LepGood1_eta) > 30 && abs(LepGood1_eta)<2.5
  // HLTid : LepGood1_hltId > 0
  // numSel : LepGood1_customId == 1
  
  // -----------------------

  bool doElectrons = (fFlavor == 11);
  if (doElectrons) std::cout << "running on electrons !!! " << std::endl;
  else             std::cout << "running on muons !!! " << std::endl;
  // -----------------------

  // Start of the program
  if (fChain == 0) return;
  Long64_t nentries = fChain->GetEntriesFast();
  Long64_t nbytes = 0, nb = 0;

  // Booking histos and tree with final variables
  bookOutputTree();

  // Vectors to store infos
  vector <float> cand_pt        = {};
  vector <float> cand_eta       = {};
  vector <float> cand_etaSc     = {};
  vector <float> cand_phi       = {};
  vector <float> cand_eleTrgPt  = {};
  vector <float> cand_muTrgPt   = {};
  vector <float> cand_tkMuTrgPt = {};
  vector <int>   cand_matchMC   = {};
  vector <int>   cand_hltSafeId = {};
  vector <int>   cand_customId  = {};
  vector <int>   cand_tightCharge = {};
  vector <int>   cand_fullLepId = {};
  vector <int>   cand_alsoTag   = {};
  vector <int>   cand_isZero    = {};

  // To compute the lumi weight
  float sigma=1921.8*3.;
  float count_getentries = doElectrons ? 123847915 : 99999999999;    // madgraph, ext1+ext2 //MARC THIS NUMBER IS WRONG FOR MUONS. doesn't matter, it's a constant
  float SetLumi=35.9;     


  // Loop over events
  std::cout << "Start looping over events" << endl;
  for (Long64_t jentry=0; jentry<nentries;jentry++) {
    Long64_t ientry = LoadTree(jentry);
    if (ientry < 0) break;
    if (maxentries > 0 && ientry >= maxentries) break;
    nb = fChain->GetEntry(jentry);   nbytes += nb;
    if (!(ientry%250000)) std::cout << ientry << endl;
    thisEntry = ientry;

    // To keep track of the total number of events
    h_entries->Fill(5);  

    // PU weight
    mypuw = 1.;
    if (!isData) mypuw = puw2016_nTrueInt_36fb(nTrueInt);
    
    // Lumi weight for MC only
    totWeight = 1.;
    if (!isData) totWeight = mypuw*genWeight*((sigma*SetLumi)/count_getentries)*(pow(10,3));  

    // Events breakdown  
    h_selection->Fill(0.);

    // 1) analysis cuts: fire the single lepton trigger  
    if ( doElectrons && !HLT_BIT_HLT_Ele27_WPTight_Gsf_v) continue;
    if (!doElectrons && !HLT_BIT_HLT_IsoMu24_v && !HLT_BIT_HLT_IsoTkMu24_v) continue; // require the tag to fire both to avoid bias

    h_selection->Fill(1.);
    
    // 2) at least one good vertex found
    nvtx = nVert;
    if (nvtx<1) continue;
    h_selection->Fill(2.);

    // 3) Gen level match, to be saved as additional info
    int numGenLevel=0;
    bool genLepFound = false;
    bool genPosFound = false;
    TLorentzVector myGenLep(0,0,0,0);  
    TLorentzVector myGenPos(0,0,0,0);  
    if (!isData) {   
      for(int ii=0; ii<nGenPart; ii++){
        int status = GenPart_status[ii];
        int pdgid  = GenPart_pdgId[ii];
        if ( abs(pdgid)==fFlavor && status==23 ) { // check if lepton is correct type and status 23
          if (GenPart_motherId[ii]==23){
            float ptgen  = GenPart_pt[ii];
            float etagen = GenPart_eta[ii];
            float phigen = GenPart_phi[ii];
            if (pdgid<0)  {
              myGenPos.SetPtEtaPhiM(ptgen, etagen, phigen, 0.);
              genPosFound = true;
            }
            if (pdgid>0) {
              myGenLep.SetPtEtaPhiM(ptgen, etagen, phigen, 0.);
              genLepFound = true;
            }
            numGenLevel++;
          } // end check motherid == Z
        } // end if pdgId && status
      } // end loop gen particles
    } // end MC only


    // 4) Tag and probe selection
    bool atLeastOneTag = false;
    std::vector<int> acceptLep;
    
    // leptons in the acceptance
    for(int jj=0; jj<nLepGood; jj++){
      if ( isLeptonInAcceptance(jj) ) acceptLep.push_back(jj);
    }

    // full selection for tags and probes
    //for (unsigned int iLep=0; iLep<acceptLep.size(); iLep++) {
    for (std::vector<int>::const_iterator ilep = acceptLep.begin(); ilep !=acceptLep.end(); ++ilep){ 
      //int theOrigIndex = acceptLep.at(iLep);
      int theOrigIndex = *ilep;

      // kine 
      float lepPt    = LepGood_calPt [theOrigIndex];     // calibrated pT for electrons and muons now
      float lepEta   = LepGood_eta   [theOrigIndex];
      float lepScEta = LepGood_etaSc [theOrigIndex];
      float lepPhi   = LepGood_phi   [theOrigIndex];

      // this lep
      TLorentzVector thisRecoLep(0,0,0,0);
      thisRecoLep.SetPtEtaPhiM(lepPt,lepEta,lepPhi,0);

      // Match with MC truth   
      int matchMC = 0;
      if (!isData) {  
        if(genLepFound && thisRecoLep.DeltaR(myGenLep)<0.3) matchMC = 1;  
        if(genPosFound && thisRecoLep.DeltaR(myGenPos)<0.3) matchMC = 1;  
      } 
      else {
        matchMC = 1;
      } // end check mcMatch

      // HLT Safe ID
      int hltSafeId = LepGood_hltId[theOrigIndex];
      
      // Full ID 
      int customId = LepGood_customId[theOrigIndex];

      // Tight Charge
      int tightCharge = LepGood_tightChargeFix[theOrigIndex];

      // Is this a tag:
      int isThisTag = 0;
      if (doElectrons){
        if (isTagLepton(theOrigIndex) && LepGood_matchedTrgObjElePt[theOrigIndex] > -1.) isThisTag =1;
      }
      else {
        if (isTagLepton(theOrigIndex) && (LepGood_matchedTrgObjMuPt[theOrigIndex] > -1. || LepGood_matchedTrgObjTkMuPt[theOrigIndex] > -1.) ) isThisTag =1;
      }
      if (isThisTag) atLeastOneTag = true;

      // Infos to be kept
      cand_pt          . push_back(lepPt);
      cand_eta         . push_back(lepEta);
      cand_etaSc       . push_back(lepScEta);
      cand_phi         . push_back(lepPhi);
      cand_eleTrgPt    . push_back(LepGood_matchedTrgObjElePt[theOrigIndex]);
      cand_muTrgPt     . push_back(LepGood_matchedTrgObjMuPt[theOrigIndex]);
      cand_tkMuTrgPt   . push_back(LepGood_matchedTrgObjTkMuPt[theOrigIndex]);
      cand_matchMC     . push_back(matchMC);
      cand_hltSafeId   . push_back(hltSafeId);
      cand_customId    . push_back(customId);
      cand_tightCharge . push_back(tightCharge);
      cand_fullLepId  . push_back(isTagLepton(theOrigIndex));
      cand_alsoTag     . push_back(isThisTag);

      if (theOrigIndex==0) cand_isZero.push_back(1);
      else cand_isZero.push_back(0);    
      
    } // end leptons in acceptance

    
    //--- 4) at least one tag candidate - should be there by definition of the skim
    if (!atLeastOneTag) {
      // cleaning vectors
      cand_pt          . clear();
      cand_eta         . clear();
      cand_etaSc       . clear();
      cand_phi         . clear();
      cand_eleTrgPt    . clear();
      cand_muTrgPt     . clear();
      cand_tkMuTrgPt   . clear();
      cand_matchMC     . clear();
      cand_hltSafeId   . clear();
      cand_customId    . clear();
      cand_tightCharge . clear();
      cand_fullLepId  . clear();
      cand_alsoTag     . clear();
      cand_isZero      . clear();
      continue;
    }
    h_selection->Fill(3.);    
  
    //--- 5) invariant mass and T&P pairs
    // first as tag  
    for(unsigned int iLep1=0; iLep1<cand_pt.size(); ++iLep1) {
      if (!cand_alsoTag[iLep1]) continue;
      TLorentzVector thisLep1(0,0,0,0);   
      thisLep1.SetPtEtaPhiM(cand_pt[iLep1],cand_eta[iLep1],cand_phi[iLep1],0);

      // second as probe 
      for(unsigned int iLep2=0; iLep2<cand_pt.size(); ++iLep2) {
        // if (cand_isZero[iLep2]) continue; # consider 2 candidates as possible probes with same minv, otherwise biases minv for high pt probe
        TLorentzVector thisLep2(0,0,0,0);
        thisLep2.SetPtEtaPhiM(cand_pt[iLep2],cand_eta[iLep2],cand_phi[iLep2],0);

        // invariant mass
        pair_mass = (thisLep1+thisLep2).M();
        if (pair_mass<60 || pair_mass>120) continue;

        // both matching mc truth?
        mcTrue = cand_matchMC[iLep1] && cand_matchMC[iLep2];
        
        // first as tag, second as probe
        tag_lep_pt             = cand_pt          [iLep1];
        tag_lep_eta            = cand_eta         [iLep1];
        tag_lep_matchMC        = cand_matchMC     [iLep1];

        probe_lep_pt           = cand_pt          [iLep2];
        probe_lep_eta          = cand_eta         [iLep2];
        probe_sc_eta           = cand_etaSc       [iLep2];
        probe_lep_phi          = cand_phi         [iLep2];
        probe_eleTrgPt         = cand_eleTrgPt    [iLep2];
        probe_muTrgPt          = cand_muTrgPt     [iLep2];
        probe_tkMuTrgPt        = cand_tkMuTrgPt   [iLep2];
        probe_lep_matchMC      = cand_matchMC     [iLep2];
        probe_lep_hltSafeId    = cand_hltSafeId   [iLep2];
        probe_lep_customId     = cand_customId    [iLep2];
        probe_lep_tightCharge  = cand_tightCharge [iLep2];
        probe_lep_fullLepId   = cand_fullLepId  [iLep2];
        probe_lep_alsoTag      = cand_alsoTag     [iLep2];
        
        // Tree filling
        outFile_->cd();
        cddir->cd();  
        outTree_->Fill();

      }  // probes
    }   // tags
  
    // cleaning vectors
    cand_pt          . clear();
    cand_eta         . clear();
    cand_etaSc       . clear();
    cand_phi         . clear();
    cand_matchMC     . clear();
    cand_hltSafeId   . clear();
    cand_customId    . clear();
    cand_tightCharge . clear();
    cand_fullLepId  . clear();
    cand_alsoTag     . clear();
    cand_isZero      . clear();
    cand_eleTrgPt    . clear();
    cand_muTrgPt     . clear();
    cand_tkMuTrgPt   . clear();

  }  // Loop over entries

  // Saving output tree and histos
  outFile_    -> cd();
  h_entries   -> Write();
  h_selection -> Write();
  cddir       -> cd();
  outTree_    -> Write();
  outFile_    -> Close();

} // Loop method

#endif
