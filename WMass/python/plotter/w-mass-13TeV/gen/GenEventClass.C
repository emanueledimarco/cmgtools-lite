#define GenEventClass_cxx
#include "GenEventClass.h"
#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include <iostream>
#include <algorithm>


void GenEventClass::Loop(int maxentries)
{
//   In a ROOT session, you can do:
//      root> .L GenEventClass.C
//      root> GenEventClass t
//      root> t.GetEntry(12); // Fill t data members with entry number 12
//      root> t.Show();       // Show values of entry 12
//      root> t.Show(16);     // Read and show values of entry 16
//      root> t.Loop();       // Loop on all entries
//

//     This is the loop skeleton where:
//    jentry is the global entry number in the chain
//    ientry is the entry number in the current Tree
//  Note that the argument to GetEntry must be:
//    jentry for TChain::GetEntry
//    ientry for TTree::GetEntry and TBranch::GetEntry
//
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(jentry);       //read all branches
//by  b_branchname->GetEntry(ientry); //read only this branch
   if (fChain == 0) return;

   Long64_t nentries = fChain->GetEntries();
   std::cout << "Chain has " << nentries << " events. Will run with maxevents = " << maxentries << std::endl;

   bookHistograms();
   
   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      Long64_t ientry = LoadTree(jentry);
      if (ientry < 0) break;
      if (maxentries > 0 && jentry >= maxentries) break;
      nb = fChain->GetEntry(jentry);   nbytes += nb;
      if (nb<0) continue;

      if(jentry%10000==0) std::cout << "Processing event " << jentry << std::endl;

      std::vector<TLorentzVector> bareLeptonCollection = getBareLeptons();
      std::vector<TLorentzVector> dressedLeptonCollection = getDressedLeptons(TMath::Pi());
      TLorentzVector neutrino = getNeutrino();
      if (neutrino.Pt()<1e-6) continue;

      if(bareLeptonCollection.size()){

        TLorentzVector bareLepton    = bareLeptonCollection[0];
        TLorentzVector dressedLepton = dressedLeptonCollection[0];

        TLorentzVector preFSRLepton = getPreFSRLepton();
        h_prefsrlpt->Fill(preFSRLepton.Pt());
        h_prefsrleta->Fill(preFSRLepton.Eta());

        h_lpt->Fill(dressedLepton.Pt());
        h_leta->Fill(dressedLepton.Eta());
        h_lptDressOverPreFSR->Fill(dressedLepton.Pt()/preFSRLepton.Pt());

        h_barelpt->Fill(bareLepton.Pt());
        h_bareleta->Fill(bareLepton.Eta());
        h_lptBareOverDressed->Fill(bareLepton.Pt()/dressedLepton.Pt());

        h3d_lptBareOverDressed->Fill(fabs(preFSRLepton.Eta()),preFSRLepton.Pt(),bareLepton.Pt()/dressedLepton.Pt());

        TLorentzVector recw = dressedLepton + neutrino;
        h_wpt->Fill(recw.Pt());
        h_wy->Fill(recw.Rapidity());
        h_wmass->Fill(recw.M());

        TLorentzVector genw = getGenW();
        h_genwpt->Fill(genw.Pt());
        h_genwy->Fill(genw.Rapidity());
        h_genwmass->Fill(genw.M());        

        std::vector<TLorentzVector> photons = getFSRPhotons(dressedLepton,TMath::Pi());
        h_nfsr->Fill(photons.size());

        if(photons.size()>0) {
          TLorentzVector fsr_close = getClosestPhoton(photons,dressedLepton);
          TLorentzVector fsr_hard = getHardestPhoton(photons);

          h_fsrpt_close->Fill(fsr_close.Pt());
          h_fsrdr_close->Fill(fsr_close.DeltaR(dressedLepton));
          h_fsrpt_hard->Fill(fsr_hard.Pt());
          h_fsrdr_hard->Fill(fsr_hard.DeltaR(dressedLepton));
          h_fsrptfrac_hard->Fill(fsr_hard.Pt()/preFSRLepton.Pt());
          h3d_fsrdr_hard->Fill(fabs(preFSRLepton.Eta()),preFSRLepton.Pt(),fsr_hard.DeltaR(dressedLepton));
        } else {
          h_fsrpt_close->Fill(-1);
          h_fsrdr_close->Fill(-1);
          h_fsrpt_hard->Fill(-1);
          h_fsrdr_hard->Fill(-1);
          h_fsrptfrac_hard->Fill(-1);
          h3d_fsrdr_hard->Fill(preFSRLepton.Eta(),preFSRLepton.Pt(),-1);
        }
      } else {
        std::cout << jentry << "  no dressed lep!" << std::endl;
      }
   }
   writeHistograms();
   outFile_->Close();
}

TLorentzVector GenEventClass::getPreFSRLepton() {
  TLorentzVector lepton;
  // pre-FSR: it is the last lepton in the history with W as parent
  for (int igp=0; igp<GenParticle_; ++igp) {
    if (abs(GenParticle_pdgId[igp]) != fFlavor) continue;
    int motherIndex = GenParticle_parent[igp];
    if (motherIndex<0) continue;
    int motherId = GenParticle_pdgId[motherIndex];
    if (GenParticle_pdgId[igp]==motherId) continue;
    if (abs(motherId)!=24) continue;
    lepton.SetPtEtaPhiM(GenParticle_pt[igp], GenParticle_eta[igp], GenParticle_phi[igp], std::max(GenParticle_mass[igp],float(0.)));
    //break;
  }
  return lepton;
}

std::vector<TLorentzVector> GenEventClass::getBareLeptons() {

  std::vector<TLorentzVector> leptons;
  for (int igp=0; igp<GenParticle_; ++igp) {
    if (abs(GenParticle_pdgId[igp]) != fFlavor) continue;
    if (!isPromptFinalStateLepton(igp)) continue;
    TLorentzVector lepton;
    lepton.SetPtEtaPhiM(GenParticle_pt[igp], GenParticle_eta[igp], GenParticle_phi[igp], std::max(GenParticle_mass[igp],float(0.)));
    leptons.push_back(lepton);
  }

  sort(leptons.begin(), leptons.end(),
       [](const TLorentzVector& a, const TLorentzVector& b)
       {return a.Pt()>b.Pt();});
  
  return leptons;
}

std::vector<TLorentzVector> GenEventClass::getDressedLeptons(float cone) {

  std::vector<TLorentzVector> leptons = getBareLeptons();
  if(leptons.size()==0) return leptons;

  for (int igp=0; igp<GenParticle_; ++igp) {
    if (abs(GenParticle_pdgId[igp]) != 22) continue;
    if (!isPromptFinalStatePhoton(igp)) continue;
    TLorentzVector tmp_photon;
    tmp_photon.SetPtEtaPhiM(GenParticle_pt[igp], GenParticle_eta[igp], GenParticle_phi[igp], std::max(GenParticle_mass[igp],float(0.)));

    for(int il=0; il<(int)leptons.size(); ++il) {
      if(leptons[il].DeltaR(tmp_photon) > cone) continue;
      leptons[il] = leptons[il]+tmp_photon;
      break;
    }
  }

  return leptons;
  
}

TLorentzVector GenEventClass::getGenW() {
  TLorentzVector W;
  for (int igp=0; igp<GenParticle_; ++igp) {
    if (abs(GenParticle_pdgId[igp]) != 24) continue;
    W.SetPtEtaPhiM(GenParticle_pt[igp], GenParticle_eta[igp], GenParticle_phi[igp], std::max(GenParticle_mass[igp],float(0.)));
    break;
  }
  return W;
}

TLorentzVector GenEventClass::getNeutrino() {

    std::vector<TLorentzVector> nus;

    for (int igp=0; igp<GenParticle_; ++igp) {
      if (abs(GenParticle_pdgId[igp]) != fFlavor+1) continue;
      TLorentzVector nu;
      nu.SetPtEtaPhiM(GenParticle_pt[igp], GenParticle_eta[igp], GenParticle_phi[igp], std::max(GenParticle_mass[igp],float(0.)));
      nus.push_back(nu);
    }

    if (nus.size()==0) {
      // std::cout << "WARNING NO NEUTRINO FOUND FOR THIS EVENT. SKIPPING IT..." << std::endl;
      TLorentzVector zero(0,0,0,0);
      return zero;
    }

    sort(nus.begin(), nus.end(),
         [](const TLorentzVector& a, const TLorentzVector& b)
         {return a.Pt()>b.Pt();});

    return nus[0];
}

std::vector<TLorentzVector> GenEventClass::getFSRPhotons(TLorentzVector fourmom, float cone) {

  std::vector<TLorentzVector> photons;

  for (int igp=0; igp<GenParticle_; ++igp) {
    if (abs(GenParticle_pdgId[igp]) != 22) continue;
    if (!isPromptFinalStatePhoton(igp)) continue;
    TLorentzVector tmp_photon;
    tmp_photon.SetPtEtaPhiM(GenParticle_pt[igp], GenParticle_eta[igp], GenParticle_phi[igp], std::max(GenParticle_mass[igp],float(0.)));
    float dr = fourmom.DeltaR(tmp_photon);
    if(dr < cone) {
      photons.push_back(tmp_photon);
    }
  }
  return photons;
}

TLorentzVector GenEventClass::getClosestPhoton(std::vector<TLorentzVector> photons, TLorentzVector fourmom) {
  if (photons.size()==0) return TLorentzVector(0,0,0,0);
  if (photons.size()==1) return photons[0];
  sort(photons.begin(), photons.end(),
       [fourmom](const TLorentzVector& a, const TLorentzVector& b)
       {return a.DeltaR(fourmom)<b.DeltaR(fourmom);});
  return photons[0];
}

TLorentzVector GenEventClass::getHardestPhoton(std::vector<TLorentzVector> photons) {
  if (photons.size()==0) return TLorentzVector(0,0,0,0);
  if (photons.size()==1) return photons[0];
  sort(photons.begin(), photons.end(),
       [](const TLorentzVector& a, const TLorentzVector& b)
       {return a.Pt()>b.Pt();});
  return photons[0];
}

bool GenEventClass::isPromptFinalStatePhoton(int index) {
  if (GenParticle_status[index]!=1) return false;
  int motherIndex = GenParticle_parent[index];
  if (motherIndex<0) return false;
  int motherId = GenParticle_pdgId[motherIndex];
  if (abs(motherId)==24) return true;   // photos case with 3 particles vertex
  int grandmaIndex = GenParticle_parent[motherIndex];
  if (grandmaIndex<0) return false;
  int grandmaId = GenParticle_pdgId[grandmaIndex];
  return (abs(motherId)==fFlavor && abs(grandmaId)==24);
}

bool GenEventClass::isPromptFinalStateLepton(int index) {
  // look for a W ancestor in the history
  int motherIndex = index-1;
  while (motherIndex>=0) {
    int motherId = GenParticle_pdgId[motherIndex];
    if (abs(motherId)==24) break;
    motherIndex -= 1;
  }
  if (motherIndex<=0) return false;
  return GenParticle_status[index]==1;
}

void GenEventClass::bookHistograms() {

  outFile_ = new TFile(fOutfile, "RECREATE");    
  outFile_->cd();
  
  h_lpt  = new TH1F("lpt","lepton pt",1000,0,250);              histograms.push_back(h_lpt);
  h_leta = new TH1F("leta","lepton eta",1000,-5.,5.);           histograms.push_back(h_leta);
  h_prefsrlpt  = new TH1F("prefsrlpt","pre-FSR lepton pt",1000,0,250);      histograms.push_back(h_prefsrlpt);
  h_prefsrleta = new TH1F("prefsrleta","pre-FSR lepton eta",1000,-5.,5.);   histograms.push_back(h_prefsrleta);
  h_barelpt  = new TH1F("barelpt","bare lepton pt",1000,0,250);      histograms.push_back(h_barelpt);
  h_bareleta = new TH1F("bareleta","bare lepton eta",1000,-5.,5.);   histograms.push_back(h_bareleta);

  h_lptDressOverPreFSR  = new TH1F("lptDressOverPreFSR","dressed lepton pt over preFSR",1000,0.5,1.5);   histograms.push_back(h_lptDressOverPreFSR);

  h_wpt      = new TH1F("wpt","W pt",1000,0,150);              histograms.push_back(h_wpt);  
  h_wy       =  new TH1F("wy","W rapidity",1000,-6,6);         histograms.push_back(h_wy);
  h_wmass    =  new TH1F("wmass","W mass",1000,0,180);         histograms.push_back(h_wmass);
  h_genwpt   = new TH1F("genwpt","gen W pt",1000,0,150);       histograms.push_back(h_genwpt);  
  h_genwy    =  new TH1F("genwy","gen W rapidity",1000,-6,6);  histograms.push_back(h_genwy);
  h_genwmass =  new TH1F("genwmass","gen W mass",1000,0,180);  histograms.push_back(h_genwmass);

  h_nfsr = new TH1F("nfsr","n FSR photons",10,0,10);                     histograms.push_back(h_nfsr);
  h_fsrpt_close = new TH1F("fsrpt_close","FSR pt",5000,0,10);            histograms.push_back(h_fsrpt_close);
  h_fsrdr_close = new TH1F("fsrdr_close","FSR pt",5000,0,0.1);   histograms.push_back(h_fsrdr_close);
  h_fsrpt_hard = new TH1F("fsrpt_hard","FSR pt",5000,0,10);              histograms.push_back(h_fsrpt_hard);
  h_fsrdr_hard = new TH1F("fsrdr_hard","FSR deltaR",5000,0,0.1);     histograms.push_back(h_fsrdr_hard);

  h_fsrptfrac_hard = new TH1F("fsrptfrac_hard","fraction FSR pt / preFSR lepton pt",5000,0,0.1);      histograms.push_back(h_fsrptfrac_hard);

  float ptBins[8] = {0,10,20,30,40,50,100,6500};
  float etaBins[5] = {0,1,1.5,2.5,5};
  if (fFlavor==13) {
    const int nDrBins = 100; float drmin=0.0; float drmax=0.1; float drBinSize=(drmax-drmin)/float(nDrBins);
    float drBins[nDrBins+2];
    drBins[0]=-1; // this to keep the underflow - no radiation case 
    for(int b=0; b<nDrBins+1; ++b) drBins[b+1]=b*drBinSize;
    h3d_fsrdr_hard = new TH3F("h3d_fsrdr_hard","deltaR FSRhard-lep vs preFSR lep pt/eta",4,etaBins,7,ptBins,nDrBins+1,drBins);
  } else {
    const int nDrBins = 102;
    float drBins[nDrBins+2];
    drBins[0]=-1; // this to keep the underflow - no radiation case 
    float drBinSize1 = 2e-5;
    for(int b=0; b<51; ++b) drBins[b+1]=b*drBinSize1;
    float drBinSize2 = 1.8e-4;
    for(int b=0; b<51; ++b) drBins[b+52]=drBins[51]+(b+1)*drBinSize2;
    drBins[103] = 0.1;
    h3d_fsrdr_hard = new TH3F("h3d_fsrdr_hard","deltaR FSRhard-lep vs preFSR lep pt/eta",4,etaBins,7,ptBins,nDrBins+1,drBins);
  }

  const int nRatioBins = 41;
  float ratioBinEdges[nRatioBins+1];
  ratioBinEdges[0] = 0;
  ratioBinEdges[1] = 0.9;
  int lastEdge=1;
  for(int b=0;b<10;++b)  ratioBinEdges[lastEdge+b] = ratioBinEdges[lastEdge] + b*1e-2;     lastEdge += 9;
  for(int b=0;b<=21;++b) ratioBinEdges[lastEdge+b] = ratioBinEdges[lastEdge] + b*5e-4;     lastEdge += 21;
  for(int b=0;b<=10;++b)  ratioBinEdges[lastEdge+b] = ratioBinEdges[lastEdge] + b*1e-2;
  for(int b=0;b<nRatioBins+1;++b) std::cout << "b["<<b<<"] = " << ratioBinEdges[b] << "\t";
  std::cout << std::endl;

  h_lptBareOverDressed= new TH1F("h_lptBareOverDressed","bare over dressed pt",nRatioBins,ratioBinEdges);   histograms.push_back(h_lptBareOverDressed);
  h3d_lptBareOverDressed  = new TH3F("h3d_lptBareOverDressed","bare lepton pt over dressed",4,etaBins,7,ptBins,nRatioBins,ratioBinEdges);

}

void GenEventClass::writeHistograms() {
  outFile_->cd();
  for (int ih=0; ih<(int)histograms.size(); ++ih) {
    histograms[ih]->Write();
  }
  h3d_fsrdr_hard->Write();
  h3d_lptBareOverDressed->Write();
}

void GenEventClass::setOutfile(TString outfilepath){
  fOutfile = outfilepath;
}

void GenEventClass::setFlavor(int flavor) {
  fFlavor = flavor;
}
