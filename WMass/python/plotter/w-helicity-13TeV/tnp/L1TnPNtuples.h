//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Wed Oct 10 18:02:29 2018 by ROOT version 6.10/09
// from TTree tree/Event Summary
// found on file: SingleElectron_Run2016H-03Feb2017-v1.root
//////////////////////////////////////////////////////////

#ifndef L1TnPNtuples_h
#define L1TnPNtuples_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.
#include "Math/GenVector/LorentzVector.h"
#include "Math/GenVector/PxPyPzE4D.h"
#include "vector"
#include "vector"
#include "vector"

class L1TnPNtuples {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

  // Output tree and histos
  TFile *outFile_;
  TTree* outTree_;
  TDirectory *cddir;

  float tag_pt, tag_eta;
  float probe_pt, probe_eta;
  float pair_mass;
  int L1EGbx;

// Fixed size dimensions of array or collections stored in the TTree if any.
   static constexpr Int_t kMaxphoton_p4 = 9;
   static constexpr Int_t kMaxL1EG_p4 = 41;
   static constexpr Int_t kMaxL1Jet_p4 = 45;

   // Declaration of leaf types
   Long64_t        run;
   Long64_t        lumi;
   Long64_t        event;
   Int_t           bunchCrossing;
   Int_t           triggerRule;
 //ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> > *tag_electron;
   Double_t        fCoordinates_fX;
   Double_t        fCoordinates_fY;
   Double_t        fCoordinates_fZ;
   Double_t        fCoordinates_fT;
   Int_t           photon_p4_;
   Double_t        photon_p4_fCoordinates_fX[kMaxphoton_p4];   //[photon_p4_]
   Double_t        photon_p4_fCoordinates_fY[kMaxphoton_p4];   //[photon_p4_]
   Double_t        photon_p4_fCoordinates_fZ[kMaxphoton_p4];   //[photon_p4_]
   Double_t        photon_p4_fCoordinates_fT[kMaxphoton_p4];   //[photon_p4_]
   vector<float>   *photon_sieie;
   vector<float>   *photon_hoe;
   vector<float>   *photon_iso;
   vector<int>     *L1EG_bx;
   Int_t           L1EG_p4_;
   Double_t        L1EG_p4_fCoordinates_fX[kMaxL1EG_p4];   //[L1EG_p4_]
   Double_t        L1EG_p4_fCoordinates_fY[kMaxL1EG_p4];   //[L1EG_p4_]
   Double_t        L1EG_p4_fCoordinates_fZ[kMaxL1EG_p4];   //[L1EG_p4_]
   Double_t        L1EG_p4_fCoordinates_fT[kMaxL1EG_p4];   //[L1EG_p4_]
   vector<int>     *L1EG_iso;
   vector<int>     *L1Jet_bx;
   Int_t           L1Jet_p4_;
   Double_t        L1Jet_p4_fCoordinates_fX[kMaxL1Jet_p4];   //[L1Jet_p4_]
   Double_t        L1Jet_p4_fCoordinates_fY[kMaxL1Jet_p4];   //[L1Jet_p4_]
   Double_t        L1Jet_p4_fCoordinates_fZ[kMaxL1Jet_p4];   //[L1Jet_p4_]
   Double_t        L1Jet_p4_fCoordinates_fT[kMaxL1Jet_p4];   //[L1Jet_p4_]
   vector<int>     *L1GtBx;

   // List of branches
   TBranch        *b_run;   //!
   TBranch        *b_lumi;   //!
   TBranch        *b_event;   //!
   TBranch        *b_bunchCrossing;   //!
   TBranch        *b_triggerRule;   //!
   TBranch        *b_tag_electron_fCoordinates_fX;   //!
   TBranch        *b_tag_electron_fCoordinates_fY;   //!
   TBranch        *b_tag_electron_fCoordinates_fZ;   //!
   TBranch        *b_tag_electron_fCoordinates_fT;   //!
   TBranch        *b_photon_p4_;   //!
   TBranch        *b_photon_p4_fCoordinates_fX;   //!
   TBranch        *b_photon_p4_fCoordinates_fY;   //!
   TBranch        *b_photon_p4_fCoordinates_fZ;   //!
   TBranch        *b_photon_p4_fCoordinates_fT;   //!
   TBranch        *b_photon_sieie;   //!
   TBranch        *b_photon_hoe;   //!
   TBranch        *b_photon_iso;   //!
   TBranch        *b_L1EG_bx;   //!
   TBranch        *b_L1EG_p4_;   //!
   TBranch        *b_L1EG_p4_fCoordinates_fX;   //!
   TBranch        *b_L1EG_p4_fCoordinates_fY;   //!
   TBranch        *b_L1EG_p4_fCoordinates_fZ;   //!
   TBranch        *b_L1EG_p4_fCoordinates_fT;   //!
   TBranch        *b_L1EG_iso;   //!
   TBranch        *b_L1Jet_bx;   //!
   TBranch        *b_L1Jet_p4_;   //!
   TBranch        *b_L1Jet_p4_fCoordinates_fX;   //!
   TBranch        *b_L1Jet_p4_fCoordinates_fY;   //!
   TBranch        *b_L1Jet_p4_fCoordinates_fZ;   //!
   TBranch        *b_L1Jet_p4_fCoordinates_fT;   //!
   TBranch        *b_L1GtBx;   //!

   L1TnPNtuples(TTree *tree=0);
   virtual ~L1TnPNtuples();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
   virtual void     setOutfile(TString);

   TString fOutfile;
   void bookOutputTree();

};

#endif

#ifdef L1TnPNtuples_cxx
L1TnPNtuples::L1TnPNtuples(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("SingleElectron_Run2016H-03Feb2017-v1.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("SingleElectron_Run2016H-03Feb2017-v1.root");
      }
      TDirectory * dir = (TDirectory*)f->Get("SingleElectron_Run2016H-03Feb2017-v1.root:/ntuple");
      dir->GetObject("tree",tree);

   }
   Init(tree);
}

L1TnPNtuples::~L1TnPNtuples()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t L1TnPNtuples::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t L1TnPNtuples::LoadTree(Long64_t entry)
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

void L1TnPNtuples::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set object pointer
   photon_sieie = 0;
   photon_hoe = 0;
   photon_iso = 0;
   L1EG_bx = 0;
   L1EG_iso = 0;
   L1Jet_bx = 0;
   L1GtBx = 0;
   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("run", &run, &b_run);
   fChain->SetBranchAddress("lumi", &lumi, &b_lumi);
   fChain->SetBranchAddress("event", &event, &b_event);
   fChain->SetBranchAddress("bunchCrossing", &bunchCrossing, &b_bunchCrossing);
   fChain->SetBranchAddress("triggerRule", &triggerRule, &b_triggerRule);
   fChain->SetBranchAddress("fCoordinates.fX", &fCoordinates_fX, &b_tag_electron_fCoordinates_fX);
   fChain->SetBranchAddress("fCoordinates.fY", &fCoordinates_fY, &b_tag_electron_fCoordinates_fY);
   fChain->SetBranchAddress("fCoordinates.fZ", &fCoordinates_fZ, &b_tag_electron_fCoordinates_fZ);
   fChain->SetBranchAddress("fCoordinates.fT", &fCoordinates_fT, &b_tag_electron_fCoordinates_fT);
   fChain->SetBranchAddress("photon_p4", &photon_p4_, &b_photon_p4_);
   fChain->SetBranchAddress("photon_p4.fCoordinates.fX", photon_p4_fCoordinates_fX, &b_photon_p4_fCoordinates_fX);
   fChain->SetBranchAddress("photon_p4.fCoordinates.fY", photon_p4_fCoordinates_fY, &b_photon_p4_fCoordinates_fY);
   fChain->SetBranchAddress("photon_p4.fCoordinates.fZ", photon_p4_fCoordinates_fZ, &b_photon_p4_fCoordinates_fZ);
   fChain->SetBranchAddress("photon_p4.fCoordinates.fT", photon_p4_fCoordinates_fT, &b_photon_p4_fCoordinates_fT);
   fChain->SetBranchAddress("photon_sieie", &photon_sieie, &b_photon_sieie);
   fChain->SetBranchAddress("photon_hoe", &photon_hoe, &b_photon_hoe);
   fChain->SetBranchAddress("photon_iso", &photon_iso, &b_photon_iso);
   fChain->SetBranchAddress("L1EG_bx", &L1EG_bx, &b_L1EG_bx);
   fChain->SetBranchAddress("L1EG_p4", &L1EG_p4_, &b_L1EG_p4_);
   fChain->SetBranchAddress("L1EG_p4.fCoordinates.fX", L1EG_p4_fCoordinates_fX, &b_L1EG_p4_fCoordinates_fX);
   fChain->SetBranchAddress("L1EG_p4.fCoordinates.fY", L1EG_p4_fCoordinates_fY, &b_L1EG_p4_fCoordinates_fY);
   fChain->SetBranchAddress("L1EG_p4.fCoordinates.fZ", L1EG_p4_fCoordinates_fZ, &b_L1EG_p4_fCoordinates_fZ);
   fChain->SetBranchAddress("L1EG_p4.fCoordinates.fT", L1EG_p4_fCoordinates_fT, &b_L1EG_p4_fCoordinates_fT);
   fChain->SetBranchAddress("L1EG_iso", &L1EG_iso, &b_L1EG_iso);
   fChain->SetBranchAddress("L1Jet_bx", &L1Jet_bx, &b_L1Jet_bx);
   fChain->SetBranchAddress("L1Jet_p4", &L1Jet_p4_, &b_L1Jet_p4_);
   fChain->SetBranchAddress("L1Jet_p4.fCoordinates.fX", L1Jet_p4_fCoordinates_fX, &b_L1Jet_p4_fCoordinates_fX);
   fChain->SetBranchAddress("L1Jet_p4.fCoordinates.fY", L1Jet_p4_fCoordinates_fY, &b_L1Jet_p4_fCoordinates_fY);
   fChain->SetBranchAddress("L1Jet_p4.fCoordinates.fZ", L1Jet_p4_fCoordinates_fZ, &b_L1Jet_p4_fCoordinates_fZ);
   fChain->SetBranchAddress("L1Jet_p4.fCoordinates.fT", L1Jet_p4_fCoordinates_fT, &b_L1Jet_p4_fCoordinates_fT);
   fChain->SetBranchAddress("L1GtBx", &L1GtBx, &b_L1GtBx);
   Notify();
}

Bool_t L1TnPNtuples::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void L1TnPNtuples::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t L1TnPNtuples::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef L1TnPNtuples_cxx
