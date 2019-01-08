#define L1TnPNtuples_cxx
#include "L1TnPNtuples.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <TLorentzVector.h>
#include <iostream>

// Histos booking
void L1TnPNtuples::bookOutputTree() 
{
  outFile_ = new TFile(fOutfile, "RECREATE");    
  outFile_->cd();

  cddir = outFile_->mkdir("L1EG");
  cddir->cd();

  std::cout << "Booking output tree" << endl;
  outTree_ = new TTree("fitter_tree", "fitter_tree");

  outTree_->Branch("tag_pt"             , &tag_pt             , "tag_pt/F");
  outTree_->Branch("tag_eta"            , &tag_eta            , "tag_eta/F");
  outTree_->Branch("probe_pt"           , &probe_pt           , "probe_pt/F");
  outTree_->Branch("probe_eta"          , &probe_eta          , "probe_eta/F");
  outTree_->Branch("L1EG_bx"            , &L1EGbx             , "L1EG_bx/I");
  outTree_->Branch("pair_mass"          , &pair_mass          , "pair_mass/F");
}

void L1TnPNtuples::setOutfile(TString outfilepath){
  fOutfile = outfilepath;
}

void L1TnPNtuples::Loop()
{
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntriesFast();
   Long64_t nbytes = 0, nb = 0;

   // Booking histos and tree with final variables
   bookOutputTree();

   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;
      // if (Cut(ientry) < 0) continue;
      if (!(ientry%10000)) std::cout << ientry << endl;
      
      TLorentzVector tag_ele_p4(fCoordinates_fX,fCoordinates_fY,fCoordinates_fZ,fCoordinates_fT);

      for (int iEG=0; iEG<L1EG_p4_; ++iEG) {
        TLorentzVector probe_p4(L1EG_p4_fCoordinates_fX[iEG],L1EG_p4_fCoordinates_fY[iEG],L1EG_p4_fCoordinates_fZ[iEG],L1EG_p4_fCoordinates_fT[iEG]);
        if (probe_p4.Pt() < 15)                continue;
        if ((*L1EG_iso)[iEG] == 0)             continue;
        if (probe_p4.DeltaR(tag_ele_p4) < 0.3) continue;
        float mass = (probe_p4 + tag_ele_p4).M();
        if (mass < 35 || mass > 145) continue; 

        tag_pt     = tag_ele_p4.Pt();
        tag_eta    = tag_ele_p4.Eta();
        probe_pt   = probe_p4.Pt();
        probe_eta  = probe_p4.Eta();
        pair_mass  = mass;
        L1EGbx     = (*L1EG_bx)[iEG];

        // fill tree for all the combinations
        outFile_->cd();
        cddir->cd();  
        outTree_->Fill();
        //  std::cout << "candidate iEG = " << iEG << " ==> mass = " << mass << std::endl;
      } // loop over the probes
   } // Loop over entries
  // Saving output tree and histos
  outFile_    -> cd();
  cddir       -> cd();
  outTree_    -> Write();
  outFile_    -> Close();

}
