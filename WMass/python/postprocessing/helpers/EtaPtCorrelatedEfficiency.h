#ifndef EtaPtCorrelatedEfficiency_h
#define EtaPtCorrelatedEfficiency_h

#include <Eigen/Dense>
#include <TH2F.h>
#include <TH3F.h>
#include <iostream>

class EtaPtCorrelatedEfficiency {
  
public:
  
  EtaPtCorrelatedEfficiency(TH3D* histocov, TH2D* histoerf);
  void DoEffSyst(float eta, float pt, double *variations);
  
protected:

  Eigen::MatrixXd covariance(float eta);
  void DoHessianShifts(float eta, int ipar, double *inpars, double *outpars);

  TH3D *covhist_;
  TH2D *erfhist_;
  int ndim_;

};
#endif
