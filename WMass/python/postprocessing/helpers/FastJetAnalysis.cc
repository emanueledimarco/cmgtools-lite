#ifndef CMGTools_WMassTools_FastJetAnalysis_h
#define CMGTools_WMassTools_FastJetAnalysis_h

#include <iostream>
#include <vector>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include <TLorentzVector.h>

// system include files
#include <memory>
#include "TLorentzVector.h"
#include "TVector3.h"
#include "fastjet/ClusterSequenceArea.hh"
#include "fastjet/contrib/Njettiness.hh"
#include "fastjet/tools/JetMedianBackgroundEstimator.hh"
#include <DataFormats/Math/interface/deltaR.h>

using namespace fastjet;

class FastJetAnalysis {

public:

  FastJetAnalysis(int ntaus=4) { taus_.resize(ntaus); reset(); };
  ~FastJetAnalysis() {};

  void reset() { 
    pList_.clear(); 
    for(size_t i=0; i<taus_.size(); i++) 
      taus_[i]=-1; 
    rho_=-1;
  }

  void add(float px, float py, float pz, float en) {
    fastjet::PseudoJet p4(px,py,pz,en);
    pList_.push_back(p4);
  }

  void run(float rapmax=2.5){

    if(pList_.size()==0) return;

    //n-jettiness
    fastjet::contrib::NormalizedMeasure normalizedMeasure(1.0,0.4);
    fastjet::contrib::Njettiness routine(fastjet::contrib::Njettiness::onepass_kt_axes,normalizedMeasure);
    for(size_t i=0; i<taus_.size(); i++)
      taus_[i]=routine.getTau(float(i+1),pList_);

    //rho    
    Selector sel_rapmax = SelectorAbsRapMax(rapmax);
    JetDefinition jet_def_for_rho(kt_algorithm,0.5);
    AreaDefinition area_def(active_area,GhostedAreaSpec(rapmax + 1.));
    JetMedianBackgroundEstimator bge(sel_rapmax, jet_def_for_rho, area_def);
    bge.set_particles(pList_);
    rho_=bge.rho();
  }

  const float &tau(int i) { return taus_[i-1]; }
  const float &rho()      { return rho_; }
 
private:
  std::vector<fastjet::PseudoJet> pList_;
  std::vector<float> taus_;
  float rho_;

};

#endif
