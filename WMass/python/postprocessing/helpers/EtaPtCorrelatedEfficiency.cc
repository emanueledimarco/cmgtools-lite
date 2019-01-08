#include "EtaPtCorrelatedEfficiency.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include <Eigen/Eigenvalues>
#include <TFile.h>
#include <TMath.h>
#include <fstream>
#include <cassert>

EtaPtCorrelatedEfficiency::EtaPtCorrelatedEfficiency(TH3D* histocov, TH2D* histoerf) {
  covhist_ = histocov;
  int ny = covhist_->GetNbinsY();
  int nz = covhist_->GetNbinsZ();
  assert(ny==nz);
  ndim_ = ny;
  erfhist_ = histoerf;
}

Eigen::MatrixXd EtaPtCorrelatedEfficiency::covariance(float eta) {
  Eigen::MatrixXd covMat(ndim_,ndim_);
  int etabin = std::max(1, std::min(covhist_->GetNbinsX(), covhist_->GetXaxis()->FindBin(eta)));
  for (int i=0; i<ndim_; ++i) {
    for (int j=0; j<ndim_; ++j) {
      covMat(i,j) = covhist_->GetBinContent(etabin,i+1,j+1);
    }
  }
  // std::cout << "covariance matrix = " << std::endl << covMat << std::endl;
  return covMat;
}

void EtaPtCorrelatedEfficiency::DoHessianShifts(float eta, int ipar, double *inpars, double *outpars) {

  // diagonalize the covariance matrix
  Eigen::MatrixXd covMat = covariance(eta);
  Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd> es(covMat);
  Eigen::VectorXd eigenv = es.eigenvalues();
  Eigen::MatrixXd transformation = es.eigenvectors();
  // std::cout << "Transformation = " << std::endl << transformation << std::endl;

  // transform the pars in the diagonal basis
  const unsigned int npars = transformation.rows();
  const unsigned int neigenvectors = transformation.cols(); 
  Eigen::VectorXd inparv(npars);
  for (unsigned int ipar=0; ipar<npars; ++ipar) {
    inparv[ipar] = inpars[ipar];
  }
  // std::cout << "inparv = " << std::endl << inparv << std::endl;
  Eigen::VectorXd diagbasisv = transformation.transpose()*inparv;
  // std::cout << "diagbasisv = " << std::endl << diagbasisv << std::endl;

  // shift one of them by the diagonal uncertainty (uncorrelated in this basis)
  diagbasisv[ipar] += sqrt(eigenv[ipar]);

  // transform the pars back in the original basis
  Eigen::VectorXd outparv = transformation*diagbasisv;
  for (unsigned int ieig=0; ieig<neigenvectors; ++ieig) {
    outpars[ieig] = outparv[ieig];
  }
  // std::cout << "outparv = " << std::endl << outparv << std::endl;
  return;
}

void EtaPtCorrelatedEfficiency::DoEffSyst(float eta, float pt, double *variations) {
  int etabin = std::max(1, std::min(erfhist_->GetNbinsX(), erfhist_->GetXaxis()->FindBin(eta)));
    
  double inpars[ndim_], outpars[ndim_];
  for (int ipar=0; ipar<ndim_; ++ipar) {
    inpars[ipar] = erfhist_->GetBinContent(etabin,ipar+1);
  }
  float nominaleff = inpars[0]*TMath::Erf((pt-inpars[1])/inpars[2]);
  
  for (int ipar=0; ipar<3; ++ipar) {
    DoHessianShifts(eta,ipar,inpars,outpars);
    variations[ipar] = outpars[0]*TMath::Erf((pt-outpars[1])/outpars[2]) - nominaleff;
  }
  return;
}
