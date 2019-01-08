#define TnPNtuplesBase_cxx
#include "TnPNtuplesBase.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <iostream>
#include <TLorentzVector.h>

using namespace std;

void TnPNtuplesBase::setFlavor(int flavor){
  fFlavor = flavor;
}

void TnPNtuplesBase::setOutfile(TString outfilepath){
  fOutfile = outfilepath;
}

bool TnPNtuplesBase::isTagLepton(int jj){
  return true;
}

void TnPNtuplesBase::Loop(int maxentries) {} // Loop method

// Histos booking
void TnPNtuplesBase::bookOutputTree() 
{
  outFile_ = new TFile(fOutfile, "RECREATE");    
  outFile_->cd();

  cddir = outFile_->mkdir("IDIsoToHLT");
  cddir->cd();    

  std::cout << "Booking output tree" << endl;
  outTree_ = new TTree("fitter_tree", "fitter_tree");

  outTree_->Branch("tag_lep_pt"             , &tag_lep_pt             , "tag_lep_pt/F");
  outTree_->Branch("tag_lep_eta"            , &tag_lep_eta            , "tag_lep_eta/F");
  outTree_->Branch("tag_lep_matchMC"        , &tag_lep_matchMC        , "tag_lep_matchMC/I");
  outTree_->Branch("probe_lep_pt"           , &probe_lep_pt           , "probe_lep_pt/F");
  outTree_->Branch("probe_lep_eta"          , &probe_lep_eta          , "probe_lep_eta/F");
  outTree_->Branch("probe_sc_eta"           , &probe_sc_eta           , "probe_sc_eta/F");
  outTree_->Branch("probe_lep_phi"          , &probe_lep_phi          , "probe_lep_phi/F");

  outTree_->Branch("probe_eleTrgPt"         , &probe_eleTrgPt         , "probe_eleTrgPt/F");
  outTree_->Branch("probe_muTrgPt"          , &probe_muTrgPt          , "probe_muTrgPt/F");
  outTree_->Branch("probe_tkMuTrgPt"        , &probe_tkMuTrgPt        , "probe_tkMuTrgPt/F");

  outTree_->Branch("probe_lep_matchMC"      , &probe_lep_matchMC      , "probe_lep_matchMC/I");
  outTree_->Branch("probe_lep_hltSafeId"    , &probe_lep_hltSafeId    , "probe_lep_hltSafeId/I");
  outTree_->Branch("probe_lep_customId"     , &probe_lep_customId     , "probe_lep_customId/I");
  outTree_->Branch("probe_lep_tightCharge"  , &probe_lep_tightCharge  , "probe_lep_tightCharge/I");
  outTree_->Branch("probe_lep_fullLepId"    , &probe_lep_fullLepId    , "probe_lep_fullLepId/I");
  outTree_->Branch("probe_lep_alsoTag"      , &probe_lep_alsoTag      , "probe_lep_alsoTag/I");
  outTree_->Branch("pair_mass"              , &pair_mass              , "pair_mass/F");
  outTree_->Branch("nvtx"                   , &nvtx                   , "nvtx/I");
  outTree_->Branch("thisEntry"              , &thisEntry              , "thisEntry/I");
  outTree_->Branch("mypuw"                  , &mypuw                  , "mypuw/F");
  outTree_->Branch("totWeight"              , &totWeight              , "totWeight/F");
  outTree_->Branch("mcTrue"                 , &mcTrue                 , "mcTrue/I");

  std::cout << "Booking output histos for event breakdown" << endl;
  h_entries   = new TH1F("h_entries"  , "h_entries"  , 10,   0., 10.);
  h_selection = new TH1F("h_selection", "h_selection",  6, -0.5, 5.5);
  h_entries->Sumw2();
  h_selection->Sumw2();
}

// To compute the pileup weight
float TnPNtuplesBase::puw2016_nTrueInt_36fb(int nTrueInt) 
{ 
  float _puw2016_nTrueInt_36fb[100] = {0.3505407355600995, 0.8996968628890968, 1.100322319466069, 0.9562526765089195, 1.0366251229154624, 1.0713954619016586, 0.7593488199769544, 0.47490309461978414, 0.7059895997695581, 0.8447022252423783, 0.9169159386164522, 1.0248924033173097, 1.0848877947714115, 1.1350984224561655, 1.1589888429954602, 1.169048420382294, 1.1650383018054549, 1.1507200023444994, 1.1152571438041776, 1.0739529436969637, 1.0458014000030829, 1.032500407707141, 1.0391236062781293, 1.041283620738903, 1.0412963370894526, 1.0558823002770783, 1.073481674823461, 1.0887053272606795, 1.1041701696801014, 1.123218903738397, 1.1157169321377927, 1.1052520327174429, 1.0697489590429388, 1.0144652740600584, 0.9402657069968621, 0.857142825520793, 0.7527112615290031, 0.6420618248685722, 0.5324755829715156, 0.4306470627563325, 0.33289171600176093, 0.24686361729094983, 0.17781595237914027, 0.12404411884835284, 0.08487088505600057, 0.056447805688061216, 0.03540829360547507, 0.022412461576677457, 0.013970541270658443, 0.008587896629717911, 0.004986410514292661, 0.00305102303701641, 0.001832072556146534, 0.0011570757619737708, 0.0008992999249003301, 0.0008241241729452477, 0.0008825716073180279, 0.001187003960081393, 0.0016454104270429153, 0.0022514113879764414, 0.003683196037880878, 0.005456695951503178, 0.006165248770884191, 0.007552675218762607, 0.008525338219226993, 0.008654690499815343, 0.006289068906974821, 0.00652551838513972, 0.005139581024893171, 0.005115751962934923, 0.004182527768384693, 0.004317593022028565, 0.0035749335962533355, 0.003773660372937113, 0.002618732319396435, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0};

  if (nTrueInt<100) return _puw2016_nTrueInt_36fb[nTrueInt]; 
  else return 0; 
}
