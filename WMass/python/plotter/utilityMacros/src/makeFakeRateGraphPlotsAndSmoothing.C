#include "../interface/utility.h"

// see https://root.cern.ch/doc/master/classTGraphPainter.html
// for Graph painting options in root

const static int smoothPolinDegree = 2; 
static const Double_t ptMin_fitRangeData = (smoothPolinDegree == 2) ? 30 : 32;
const static Bool_t excludePoints_Data = false;
static const Double_t ptMin_excludeRangeData = 37; // used only if excludePoints_Data = true
static const Double_t ptMax_excludeRangeData = 50;  // used only if excludePoints_Data = true

const static Bool_t addfitpol2 = false;  // will also fit with a pol2 and draw (this is needed only when smoothPolinDegree = 1)
// when I search for a bin given the boundary, the lower boundary should belong to the bin, the upper not, but rounding could ruin this logic 
// so I add an epsilon
const static Double_t epsilon = 0.0001;  

using namespace std;

// rebin pt like this for W and Z or sum (should be a subsample of bin boundaries array before rebinning (taken directly from histograms)
// the higher the index, the less granular is the array
static const vector<Double_t> ptBinBoundariesQCD_1 = {30,34,38,42,46,50,54,60,65};
static const vector<Double_t> ptBinBoundariesQCD_2 = {30,35,40,45,50,57,65};
//static const vector<Double_t> ptBinBoundariesQCD_3 = {30,36,42,48,54,60,65};
static const vector<Double_t> ptBinBoundariesQCD_3 = {30,38,46,54,60,65};
static const vector<Double_t> ptBinBoundariesEWK_1 = {30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,46,48,50,52,54,57,60,65};
static const vector<Double_t> ptBinBoundariesEWK_2 = {30,32,34,36,38,40,42,44,46,48,50,52,54,57,60,65};
static const vector<Double_t> ptBinBoundariesData_1 = {30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,46,48,50,52,54,57,60,65};
static const vector<Double_t> ptBinBoundariesData_2 = {30,32,34,36,38,40,42,44,46,48,50,52,54,57,60,65};
static const vector<Double_t> ptBinBoundariesData_3 = {30,31,32,33,34,35,36,37,38,40,42,44,46,48,50,52,54,57,60,65};
//static const vector<Double_t> ptBinBoundariesData_3 = {30,31,32,33,34,35,36,37,38,40,42,44,46,48,50,52,54,57,60,65};


vector<Double_t> etaBoundariesGlobal;

TH2D* frSmoothParameter_data = nullptr;
TH2D* frSmoothParameter_data_fitNarrowRange = nullptr;
TH2D* frSmoothParameter_qcd = nullptr;
TH2D* frSmoothParameter_w = nullptr;
TH2D* frSmoothParameter_z = nullptr;
TH2D* frSmoothParameter_ewk = nullptr;
TH2D* frSmoothParameter_top_vv = nullptr;
TH2D* frSmoothParameter_wz = nullptr;
TH2D* frSmoothParameter_data_subScaledUpEWKMC = nullptr;
TH2D* frSmoothParameter_data_subScaledDownEWKMC = nullptr;

// define some factors to rescale some MC before subtracting to data. These must be taken from outside this script
map <string,Double_t> scaleFactor;

// the core of this macro is makeFakeRateGraphPlotsAndSmoothing(), which is at the bottom of this code and calls all the rest

//============================================

void plotFRparamRelUncertainty(TH2* h2 = nullptr, 
			       const string& outDir = "", 
			       const string& xAxisName = "",
			       const string& yAxisName = "",
			       const string& zAxisName = "", 
			       const string& canvasName = "") 
{

  TH2* h2relUnc = (TH2*) h2->Clone("relUnc");

  for (Int_t i = 1; i <= h2relUnc->GetNbinsX(); i++) {

    for (Int_t j = 1; j <= h2relUnc->GetNbinsX(); j++) {
      
      Double_t var = h2relUnc->GetBinContent(i,j);
      var = (var == 0) ? 0 : fabs(h2relUnc->GetBinError(i,j)/var);
      if (var > 1) var = 1;
      h2relUnc->SetBinContent(i,j,var);

    }

  }
    

  drawCorrelationPlot(h2relUnc, 
		      xAxisName,
		      yAxisName,
		      zAxisName,
		      canvasName,
		      "", outDir, 1,1, false,false,false,1);


}

//============================================

void fillTH2fromTH3zrange(TH2* h2 = nullptr, const TH3* h3 = nullptr, const Int_t zbinLow = 1, const Int_t zbinHigh = 1) {

  // assume TH2 is a slice of TH3 with same binning
  Double_t error = 0;

  for (Int_t ix = 1; ix <= h2->GetNbinsX(); ++ix) {

    for (Int_t iy = 1; iy <= h2->GetNbinsY(); ++iy) {
            
      h2->SetBinContent(ix,iy,h3->IntegralAndError(ix,ix,iy,iy,zbinLow,zbinHigh,error));
      h2->SetBinError(ix,iy,error);

    }
    
  }

}

//============================================

void fillFakeRateTH2(TH2* h2 = nullptr, const Int_t etaBin = 0, const TH1* hpass = nullptr, const TH1* hntot = nullptr) {

  // the TH1 passed to this function might have less xbins than TH2, becasue TH2 has the original bins of pt in the input root file
  // TH1 might have been rebinned, but since the new binning is a subset of the original, we can just fill two or more consecutive bins of TH2 with same values

  TH1* ratio = (TH1*) hpass->Clone("ratio");
  ratio->Divide(hntot);

  Double_t pt = 0.0;

  for (Int_t ipt = 1; ipt < h2->GetNbinsX(); ++ipt) {
    
    pt = h2->GetXaxis()->GetBinCenter(ipt);
    h2->SetBinContent(ipt,etaBin,ratio->GetBinContent(ratio->GetXaxis()->FindFixBin(pt)));

  }

}


//============================================


void fillFakeRateTH2smooth(TH2* h2 = nullptr, const TH2* h2fit = nullptr) {

  // the TH1 passed to this function might have less xbins than TH2, because TH2 has the original bins of pt in the input root file
  // TH1 might have been rebinned, but since the new binning is a subset of the original, we can just fill two or more consecutive bins of TH2 with same values

  Double_t offset = 0.0;
  Double_t slope  = 0.0;
  Double_t concavity = 0.0;
  Double_t pt = 0.0;

  for (Int_t ipt = 1; ipt <= h2->GetNbinsX(); ++ipt) {

    for (Int_t ieta = 1; ieta <= h2->GetNbinsY(); ++ieta) {

      pt = h2->GetXaxis()->GetBinCenter(ipt);
      offset = h2fit->GetBinContent(ieta, 1);
      slope = h2fit->GetBinContent(ieta, 2);
      if (smoothPolinDegree > 1) concavity = h2fit->GetBinContent(ieta, 3);
      h2->SetBinContent(ipt,ieta, std::max(0.0, offset + slope * pt + concavity * pt * pt));
      
    }

  }

}


//============================================

void fillTH1fromTH2bin(TH1* h1 = nullptr, const TH2* h2 = nullptr, const Bool_t constantX = 1, const Int_t binFixed = 1) {

  // assume TH1 is a slice of TH2 with same binning
  Int_t nbins = constantX ? h2->GetNbinsY() : h2->GetNbinsX();
  Int_t xbin = 0;
  Int_t ybin = 0;

  for (Int_t ix = 1; ix <= nbins; ++ix) {

    if (constantX) {
      xbin = binFixed;
      ybin = ix;
    } else {
      ybin = binFixed;
      xbin = ix;
    }
    h1->SetBinContent(ix, h2->GetBinContent(xbin,ybin));
    h1->SetBinError(  ix, h2->GetBinError(xbin,ybin));
    
  }

}


//============================================

// following part is for the smoothing of the fake rate

//============================================

TFitResultPtr fitGraph(TGraph* gr_tmp = NULL, 
		       const Bool_t isEB = true,
		       const string& xAxisNameTmp = "xAxis", 
		       const string& yAxisNameTmp = "yAxis", 
		       const string& canvasName = "default",
		       const string& outDir = "./",
		       const string& legEntry = "",
		       const vector<Double_t>& legCoord = {0.5,0.15,0.9,0.35},
		       const Double_t lumi = -1.0,
		       const Bool_t isData = true,
		       const Bool_t isPromptRate = false,
		       const Double_t nSigmaVarInPlot = 1.0,
		       const Bool_t saveCanvas = true,
		       TFitResultPtr* fitPtr_fitNarrowRange = nullptr,
		       const Bool_t excludePoints = false,
		       const Double_t excludeRange_min = -1,  // used only if excludePoints = true
		       const Double_t excludeRange_max = -1
		       ) 
{

  string xAxisName = "";
  Double_t xmin = 0;
  Double_t xmax = 0;
  Bool_t setXAxisRangeFromUser = getAxisRangeFromUser(xAxisName, xmin, xmax, xAxisNameTmp);

  string yAxisName = "";
  Double_t ymin = 0;
  Double_t ymax = 0;
  Bool_t setYAxisRangeFromUser = getAxisRangeFromUser(yAxisName, ymin, ymax, yAxisNameTmp);

  createPlotDirAndCopyPhp(outDir);

  // override function above
  Int_t n = gr_tmp->GetN();
  Double_t* x = gr_tmp->GetX();
  Double_t* xerrup = gr_tmp->GetEXhigh();
  Double_t* xerrdn = gr_tmp->GetEXlow();
  Double_t* y = gr_tmp->GetY();
  Double_t* yerrup = gr_tmp->GetEYhigh();
  Double_t* yerrdn = gr_tmp->GetEYlow();
  Int_t loc = TMath::LocMax(n,y);
  Double_t tmax = y[loc]+yerrup[loc];
  loc = TMath::LocMin(n,y);
  Double_t tmin = y[loc]-yerrdn[loc];
  Double_t ydiff = tmax - tmin;

  ymin = std::max(0.0, tmin - 0.5 * ydiff);
  ymax = std::min(1.4, tmax + 1.0 * ydiff);

  // create a new graph excluding points in a given range
  TGraphAsymmErrors* gr = nullptr;
  TGraphAsymmErrors* gr_excl = nullptr;
  if (smoothPolinDegree == 1 and excludePoints) {
    gr = new TGraphAsymmErrors();
    gr_excl = new TGraphAsymmErrors();
    Int_t ip_good = 0;
    Int_t ip_excl = 0;
    for (Int_t ip = 0; ip < n; ++ip) {
      if ( (x[ip] < excludeRange_min) or (x[ip] > excludeRange_max) ) {
	gr->SetPoint(ip_good,x[ip],y[ip]);
	gr->SetPointError(ip_good,xerrdn[ip],xerrup[ip],yerrdn[ip],yerrup[ip]);
	ip_good++;
      } else {
	gr_excl->SetPoint(ip_excl,x[ip],y[ip]);
        gr_excl->SetPointError(ip_excl,xerrdn[ip],xerrup[ip],yerrdn[ip],yerrup[ip]);
	ip_excl++;
      }
    }    
  } else gr = (TGraphAsymmErrors*) gr_tmp;
  

  string polN = string(Form("pol%d",smoothPolinDegree));
  // see fit options here: https://root.cern.ch/doc/master/classTGraph.html#aa978c8ee0162e661eae795f6f3a35589
  Double_t xMaxFit = isPromptRate ? 65 : 60;
  Double_t xMinFit = isData ? ptMin_fitRangeData : 30;
  TF1 * f1 = new TF1("f1",polN.c_str(),xMinFit,xMaxFit);
  TF1 * f2 = new TF1("f2",polN.c_str(),xMinFit,50);
  // TF1 * f1 = new TF1("f1","[0] * (x - 25.) + [1]",25,60);
  // TF1 * f2 = new TF1("f2","[0] * (x - 25.) + [1]",30,46);

  TF1 * pol2 = new TF1("pol2","pol2",xMinFit,60); // used when one wants to overlay pol2 to fits made with pol1 (addfitpol2 = True and smoothPolinDegree = 1)

  Double_t maxslope = isData ? 0.0005 : 0.015;  // was used only to fix parameters, but better not doing it

  // avoid fixing the parameters, at least if using pol2, but it is not needed even for pol1: the risk is to overconstrain the fit, leading to absurd uncertainties

  if (isEB) {

    if (isPromptRate) {

      //f1->SetParLimits(0,0.0,1.5);
      //f1->SetParLimits(1,-0.02,maxslope);
      //f2->SetParLimits(0,0.0,1.5);
      //f2->SetParLimits(1,-0.02,maxslope);      
      if (smoothPolinDegree > 1) {
  	f1->SetParameters(0.95,0.0,0.0);
  	f2->SetParameters(0.95,0.0,0.0);
  	//f1->SetParLimits(2,-0.05,0.05);
  	//f2->SetParLimits(2,-0.05,0.05);
      } else {
  	f1->SetParameters(0.95,0.0);
  	f2->SetParameters(0.95,0.0);
      }

    } else {

      //f1->SetParLimits(0,0.0,1.0);
      //f1->SetParLimits(1,-0.03,maxslope);
      //f2->SetParLimits(0,0.0,1.0);
      //f2->SetParLimits(1,-0.03,maxslope);
      if (smoothPolinDegree > 1) {
  	f1->SetParameters(0.8,0.0,0.0);
  	f2->SetParameters(0.8,0.0,0.0);
  	//f1->SetParLimits(2,-0.05,0.05);
  	//f2->SetParLimits(2,-0.05,0.05);
      } else {
  	f1->SetParameters(0.8,0.0);
  	f2->SetParameters(0.8,0.0);
      }

    }

  } else {

    if (isPromptRate) {

      //f1->SetParLimits(0,0.0,1.5);
      //f1->SetParLimits(1,-0.02,maxslope);
      //f2->SetParLimits(0,0.0,1.5);
      //f2->SetParLimits(1,-0.02,maxslope);      

      if (smoothPolinDegree > 1) {
  	f1->SetParameters(0.8,0.0,0.0);	
  	//f1->SetParLimits(2,-0.02,0.02);
  	f2->SetParameters(0.8,0.0,0.0);	
  	//f2->SetParLimits(2,-0.02,0.02);
      } else {
  	f1->SetParameters(0.8,0.0);
  	f2->SetParameters(0.8,0.0); 
      }

    } else {
   
      //f1->SetParLimits(0,0.0,1.5);
      //f1->SetParLimits(1,-0.03,maxslope);
      //f2->SetParLimits(0,0.0,1.5);
      //f2->SetParLimits(1,-0.03,maxslope);      

      if (smoothPolinDegree > 1) {
  	f1->SetParameters(0.3,0.0,0.0);	
  	//f1->SetParLimits(2,-0.02,0.02);
  	f2->SetParameters(0.3,0.0,0.0);	
  	//f2->SetParLimits2(2,-0.01,0.01);
      } else {
  	f1->SetParameters(0.3,0.0);
  	f2->SetParameters(0.3,0.0); 
      }

    }

  }

  TFitResultPtr fitres = gr->Fit("f1","EMFRS+"); // fit with straigth line
  TFitResultPtr fitres2 = gr->Fit("f2",(smoothPolinDegree > 1) ? "EMFRS+" : "0EMFRS+"); // fit with straigth line in narrow range, but don't draw
  TF1 *linefit = gr->GetFunction("f1");
  linefit->SetLineWidth(3);
  Double_t xminfit = 0.0;
  Double_t xmaxfit = 0.0;
  linefit->GetRange(xminfit,xmaxfit);

  TF1 * linefit_p0up = new TF1("linefit_p0up",polN.c_str(),xminfit,xmaxfit);
  linefit_p0up->SetNpx(10000);
  linefit_p0up->SetParameter(0, linefit->GetParameter(0)+nSigmaVarInPlot*linefit->GetParError(0));
  linefit_p0up->SetParameter(1, linefit->GetParameter(1));
  if (smoothPolinDegree > 1) linefit_p0up->SetParameter(2, linefit->GetParameter(2));
  TF1 * linefit_p0dn = new TF1("linefit_p0dn",polN.c_str(),xminfit,xmaxfit);
  linefit_p0dn->SetNpx(10000);
  linefit_p0dn->SetParameter(0, linefit->GetParameter(0)-nSigmaVarInPlot*linefit->GetParError(0));
  linefit_p0dn->SetParameter(1, linefit->GetParameter(1));
  if (smoothPolinDegree > 1) linefit_p0dn->SetParameter(2, linefit->GetParameter(2));

  linefit_p0up->SetLineColor(kGreen+1);
  linefit_p0dn->SetLineColor(kGreen+1);
  linefit_p0up->SetLineWidth(3);
  linefit_p0dn->SetLineWidth(3);

  // for slope (in case of pol1 only), try scaling slope up and offset down or viceversa, otherwise the fit goes out of the points
  TF1 * linefit_p1up = new TF1("linefit_p1up",polN.c_str(),xminfit,xmaxfit);
  linefit_p1up->SetNpx(10000);
  linefit_p1up->SetParameter(0, linefit->GetParameter(0)-nSigmaVarInPlot*linefit->GetParError(0));
  linefit_p1up->SetParameter(1, linefit->GetParameter(1)+nSigmaVarInPlot*linefit->GetParError(1));
  TF1 * linefit_p1dn = new TF1("linefit_p1dn",polN.c_str(),xminfit,xmaxfit);
  linefit_p1dn->SetNpx(10000);
  linefit_p1dn->SetParameter(0, linefit->GetParameter(0)+nSigmaVarInPlot*linefit->GetParError(0));
  linefit_p1dn->SetParameter(1, linefit->GetParameter(1)-nSigmaVarInPlot*linefit->GetParError(1));

  linefit_p1up->SetLineColor(kBlue);
  linefit_p1dn->SetLineColor(kBlue);
  linefit_p1up->SetLineWidth(3);
  linefit_p1dn->SetLineWidth(3);


  TF1 *linefit2 = nullptr;
  if (smoothPolinDegree > 1) {
    linefit2 = gr->GetFunction("f2");
    linefit2->SetLineWidth(3);
    linefit2->SetLineColor(kBlue);
  }
  // Double_t xminfit2 = 0.0;
  // Double_t xmaxfit2 = 0.0;
  // linefit2->GetRange(xminfit2,xmaxfit2);
  // TF1 * linefit2_p0up = new TF1("linefit2_p0up",polN.c_str(),xminfit2,xmaxfit2);
  // linefit2_p0up->SetNpx(10000);
  // linefit2_p0up->SetParameter(0, linefit2->GetParameter(0)+nSigmaVarInPlot*linefit2->GetParError(0));
  // linefit2_p0up->SetParameter(1, linefit2->GetParameter(1));
  // if (smoothPolinDegree > 1) linefit2_p0up->SetParameter(2, linefit2->GetParameter(2));
  // TF1 * linefit2_p0dn = new TF1("linefit2_p0dn",polN.c_str(),xminfit2,xmaxfit2);
  // linefit2_p0dn->SetNpx(10000);
  // linefit2_p0dn->SetParameter(0, linefit2->GetParameter(0)-nSigmaVarInPlot*linefit2->GetParError(0));
  // linefit2_p0dn->SetParameter(1, linefit2->GetParameter(1));
  // if (smoothPolinDegree > 1) linefit2_p0dn->SetParameter(2, linefit2->GetParameter(2));

  // linefit2_p0up->SetLineColor(kOrange+2);
  // linefit2_p0dn->SetLineColor(kOrange+2);
  // linefit2_p0up->SetLineWidth(3);
  // linefit2_p0dn->SetLineWidth(3);

  TF1 *pol2fit = nullptr;
  TFitResultPtr fitrespol2 = 0;
  if (addfitpol2) {
    fitrespol2 = gr->Fit("pol2", "EMFRS+"); // fit with pol2
    pol2fit = gr->GetFunction("pol2");
    pol2fit->SetLineWidth(3);
    if (smoothPolinDegree == 1 and excludePoints) pol2fit->SetLineColor(kGreen+2);
    else               pol2fit->SetLineColor(kAzure+2);
  }

  TCanvas* canvas = new TCanvas("canvas","",700,700);
  canvas->cd();
  canvas->SetFillColor(0);
  canvas->SetGrid();
  canvas->SetRightMargin(0.06);
  canvas->cd();

  //  TLegend leg (0.5,0.15,0.9,0.15+0.05*nGraphs);
  TLegend leg (legCoord[0],legCoord[1],legCoord[2],legCoord[3]);
  leg.SetFillColor(0);
  leg.SetFillStyle(0);
  leg.SetBorderSize(0);

  gr->SetMarkerStyle(20);
  gr->SetMarkerColor(kBlack);
  gr->SetLineColor(kBlack);
  gr->SetFillColor(kBlack);
  gr->SetLineWidth(2);
  gr->Draw("ap");  
  leg.AddEntry(gr,legEntry.c_str(),"PLE");
  if (smoothPolinDegree == 1 and excludePoints) {
    //gr_tmp->Draw("p same"); // draw all points, but not all of them were used for the fit
    gr_excl->SetMarkerColor(kRed+1);
    gr_excl->SetMarkerStyle(47);
    gr_excl->SetMarkerSize(3);
    gr_excl->SetLineColor(kRed+1);
    gr_excl->SetFillColor(kRed+1);
    gr_excl->SetLineWidth(2);
    gr_excl->Draw("p same");
    leg.AddEntry(gr_excl,"excluded points","PLE");
  }

  if (smoothPolinDegree == 1) {
    leg.AddEntry(linefit,Form("fit: %.2g %s %.2g #upoint x",fitres->Parameter(0),((fitres->Parameter(1) > 0) ? "+":"-"), fabs(fitres->Parameter(1))),"L");
    //leg.AddEntry(linefit2,Form("fit: %.2g %s %.2g #upoint x",fitres2->Parameter(0),((fitres2->Parameter(1) > 0) ? "+":"-"), fabs(fitres2->Parameter(1))),"L");
    leg.AddEntry(linefit_p0dn,"offset up/down (1#sigma)","L");
    leg.AddEntry(linefit_p1dn,"slope  up/down (1#sigma)","L");
    // draw envelope
    linefit_p0up->Draw("Lsame");
    linefit_p0dn->Draw("Lsame");
    linefit_p1up->Draw("Lsame");
    linefit_p1dn->Draw("Lsame");
  } else {
    leg.AddEntry(linefit,"fit: pol2","L");
    leg.AddEntry(linefit2,"fit: pol2 narrow range","L");
  }

  leg.Draw("same");
  // linefit_p0up->Print();
  // Double_t *params = linefit_p0up->GetParameters();
  // cout << "p0 = " << params[0] << "    p1 = " << params[1] << endl;
  // linefit_p0dn->Print();
  // params = linefit_p0dn->GetParameters();
  // cout << "p0 = " << params[0] << "    p1 = " << params[1] << endl;

  gr->GetXaxis()->SetTitleSize(0.05);
  gr->GetXaxis()->SetLabelSize(0.04);
  gr->GetYaxis()->SetTitleOffset(1.15);
  gr->GetYaxis()->SetTitleSize(0.05);
  gr->GetYaxis()->SetLabelSize(0.04);
  gr->GetXaxis()->SetTitle(xAxisName.c_str());
  gr->GetYaxis()->SetTitle(yAxisName.c_str());
  if (setXAxisRangeFromUser) gr->GetXaxis()->SetRangeUser(xmin,xmax);
  if (setYAxisRangeFromUser) gr->GetYaxis()->SetRangeUser(ymin,ymax);

  TLegend legpol2(0.6,0.8,0.9,0.9);
  if (addfitpol2) {
    legpol2.SetFillColor(0);
    legpol2.SetFillStyle(0);
    legpol2.SetBorderSize(0);
    legpol2.AddEntry(pol2fit,"fit: pol2","L");
    legpol2.Draw("same");    
  }

  //  CMS_lumi(canvas,Form("%.1f",lumi));
  if (lumi < 0) CMS_lumi(canvas,"",true,false);
  else CMS_lumi(canvas,Form("%.1f",lumi),true,false);
  setTDRStyle();

  canvas->RedrawAxis("sameaxis");

  if (saveCanvas) {
    canvas->SaveAs((outDir+canvasName+".png").c_str());
    canvas->SaveAs((outDir+canvasName+".pdf").c_str());
  }

  delete canvas;

  if (isData && fitPtr_fitNarrowRange != nullptr) *fitPtr_fitNarrowRange = fitres2;

  return fitres;
  // else return fitres; // for QCD or other MC, it makes much more sense to use graph in full range, because we don't have to worry about prompt lepton rate at high pt
  // also, for QCD the binning is tipically much less granular, so the fit in the narrow range would have just 4 points

}

//=======================================================================

// following part is for the plotting the fake rate

//=====================================================================


void doFakeRateGraphPlots(const string& inputFileName = "", 
			  const string& outDir = "",
			  const string& histPrefix = "fakeRateNumerator_el_vs_pt_granular",
			  const vector<Int_t> ptBinIndexQCD = {1},  // should be a number for each eta bin (if only one is given, use it for all)
			  const vector<Int_t> ptBinIndexEWK = {1},  // should be a number for each eta bin (if only one is given, use it for all)
			  const vector<Int_t> ptBinIndexData = {1}, 
			  const Bool_t showMergedEWK = true,
			  const Double_t inputLuminosity = -1,
			  const Bool_t isEB = true,
			  const string& plotPostFix = "",
			  const Int_t etaBinNumber = 0,
			  const Bool_t scan_vs_eta = false,
			  const Double_t etaLow = 0.0, // used only if scan_vs_eta = true
			  const Double_t etaHigh = 2.5, // used only if scan_vs_eta = true
			  const Bool_t hasSignedEta = true,
			  const Bool_t noDrawQCD = false,
			  const Bool_t showMergedWZ = true,   // overriden if showMergedEWK=true, else it draws W and Z together
			  const Bool_t showTopVV = true, // to show Top+DiBoson with W and Z (or W+Z). Overriden if showMergedEWK=true
			  const Double_t subtrEWK_nSigma = 1			  
		  ) 
{

  gROOT->SetBatch(kTRUE);
  TH1::SetDefaultSumw2(); //all the following histograms will automatically call TH1::Sumw2()                  
  cout << endl;

  Int_t etaBinTH1 = etaBinNumber+1;

  vector<Double_t> ptBinBoundariesData;
  if (ptBinIndexData.size() == 1) {
    if      (ptBinIndexData[0] == 1) ptBinBoundariesData = ptBinBoundariesData_1;
    else if (ptBinIndexData[0] == 2) ptBinBoundariesData = ptBinBoundariesData_2;
    else if (ptBinIndexData[0] == 3) ptBinBoundariesData = ptBinBoundariesData_3;
  } else {
    if      (ptBinIndexData[etaBinNumber] == 1) ptBinBoundariesData = ptBinBoundariesData_1;
    else if (ptBinIndexData[etaBinNumber] == 2) ptBinBoundariesData = ptBinBoundariesData_2;
    else if (ptBinIndexData[etaBinNumber] == 3) ptBinBoundariesData = ptBinBoundariesData_3;
  }

  vector<Double_t> ptBinBoundariesEWK;
  if (ptBinIndexEWK.size() == 1) {
    if      (ptBinIndexEWK[0] == 1) ptBinBoundariesEWK = ptBinBoundariesEWK_1;
    else if (ptBinIndexEWK[0] == 2) ptBinBoundariesEWK = ptBinBoundariesEWK_2;
  } else {
    if      (ptBinIndexEWK[etaBinNumber] == 1) ptBinBoundariesEWK = ptBinBoundariesEWK_1;
    else if (ptBinIndexEWK[etaBinNumber] == 2) ptBinBoundariesEWK = ptBinBoundariesEWK_2;
  }

  vector<Double_t> ptBinBoundariesQCD;
  if (ptBinIndexQCD.size() == 1) {
    if      (ptBinIndexQCD[0] == 1) ptBinBoundariesQCD = ptBinBoundariesQCD_1;
    else if (ptBinIndexQCD[0] == 2) ptBinBoundariesQCD = ptBinBoundariesQCD_2;
  } else {
    if      (ptBinIndexQCD[etaBinNumber] == 1) ptBinBoundariesQCD = ptBinBoundariesQCD_1;
    else if (ptBinIndexQCD[etaBinNumber] == 2) ptBinBoundariesQCD = ptBinBoundariesQCD_2;
  }


  TGraphAsymmErrors* fr_data = nullptr;
  TGraphAsymmErrors* fr_data_subEWKMC = nullptr;
  TGraphAsymmErrors* fr_data_subScaledUpEWKMC = nullptr;
  TGraphAsymmErrors* fr_data_subScaledDownEWKMC = nullptr;
  TGraphAsymmErrors* fr_w = nullptr;
  TGraphAsymmErrors* fr_z = nullptr;
  TGraphAsymmErrors* fr_vv = nullptr;
  TGraphAsymmErrors* fr_top = nullptr;
  TGraphAsymmErrors* fr_qcd = nullptr;
  TGraphAsymmErrors* fr_ewk = nullptr; // all EWK
  TGraphAsymmErrors* fr_top_vv = nullptr; // Top+DiBosons
  TGraphAsymmErrors* fr_wz = nullptr; // W+Z

  string detId = isEB ? "EB" : "EE";
  string yrange = isEB ? "0.25,1.4" : "0,1.4";  // range for plotting all graphs
  vector <Double_t> legCoord = {0.15,0.65,0.60,0.9};

  cout << "Will save plots in " << outDir << endl;
  createPlotDirAndCopyPhp(outDir);
  adjustSettings_CMS_lumi(outDir);

  vector<string> processes = {"data", "data_sub", "QCD", "W", "Z", "DiBosons", "Top"};

  vector<TH1*> hpass;
  vector<TH1*> hntot;
  TH3* h3tmp = nullptr;
  vector<TGraph*> gr;

  TH1* hpass_ewk_scaledUp = nullptr;
  TH1* hntot_ewk_scaledUp = nullptr;
  TH1* hpass_ewk_scaledDown = nullptr;
  TH1* hntot_ewk_scaledDown = nullptr;

  TH1* hpass_data_subtr_scaledUpEWK = nullptr;
  TH1* hntot_data_subtr_scaledUpEWK = nullptr;
  TH1* hpass_data_subtr_scaledDownEWK = nullptr;
  TH1* hntot_data_subtr_scaledDownEWK = nullptr;

  TH1* hpass_ewk = nullptr;
  TH1* hntot_ewk = nullptr;

  TH1* hpass_top_vv = nullptr;
  TH1* hntot_top_vv = nullptr;

  TH1* hpass_wz = nullptr;
  TH1* hntot_wz = nullptr;

  // // these 2D histograms are not in the file as a TH3D, we must create them summing/subtracting the inputs
  // TH2* hpass2D_ewk = nullptr;
  // TH2* hntot2D_ewk = nullptr;
  // TH2* hpass2D_data_subScaledEWKMC = nullptr;
  // TH2* hntot2D_data_subScaledEWKMC = nullptr;

  ///////////////////////////////////////
  // open file with inputs
  //
  TFile* inputFile = new TFile(inputFileName.c_str(),"READ");
  if (!inputFile || inputFile->IsZombie()) {
    cout << "Error: file not opened. Exit" << endl;
    exit(EXIT_FAILURE);
  }
  inputFile->cd();

  UInt_t nBins = 0;
  UInt_t nBinsQCD = ptBinBoundariesQCD.size()-1;  
  UInt_t nBinsEWK = ptBinBoundariesEWK.size()-1;  
  UInt_t nBinsData = ptBinBoundariesData.size()-1;  
  Double_t ptMin = 0.0;
  Double_t ptMax = 0.0;

  vector<TH1*> pt_num_proc;
  vector<TH1*> pt_den_proc;
  vector<string> leg_pt_proc;

  for (UInt_t j = 0; j < processes.size(); ++j) {

    string h3Name = Form("%s_%s",histPrefix.c_str(), processes[j].c_str());

    h3tmp = (TH3*) getObjectCloneFromFile(inputFile,h3Name);
    checkNotNullPtr(h3tmp, h3Name);
    h3tmp->SetDirectory(0);

    nBins = h3tmp->GetNbinsX();
    Double_t* ptBins = (Double_t*) h3tmp->GetXaxis()->GetXbins()->GetArray();
    //Double_t* ptBins = ptBins_tmp;
    ptMin = ptBins[0];
    ptMax = ptBins[nBins];

    // do this only once
    if (etaBinNumber == 0 && scan_vs_eta) {

      // if (j == 0) {
      // 	hpass2D_ewk = new TH2D("hpass2D_ewk","",
      // 			       nBins, ptBins,
      // 			       h3tmp->GetNbinsY(), (Double_t*) h3tmp->GetYaxis()->GetXbins()->GetArray());
      // 	hntot2D_ewk = new TH2D("hntot2D_ewk","",
      // 			       nBins, ptBins,
      // 			       h3tmp->GetNbinsY(), (Double_t*) h3tmp->GetYaxis()->GetXbins()->GetArray());
      // 	hpass2D_data_subScaledEWKMC = new TH2D("hpass2D_data_subScaledEWKMC","",
      // 					       nBins, ptBins,
      // 					       h3tmp->GetNbinsY(), (Double_t*) h3tmp->GetYaxis()->GetXbins()->GetArray());
      // 	hntot2D_data_subScaledEWKMC = new TH2D("hntot2D_data_subScaledEWKMC","",
      // 					       nBins, ptBins,
      // 					       h3tmp->GetNbinsY(), (Double_t*) h3tmp->GetYaxis()->GetXbins()->GetArray());
      // }

      string outDir_num_den = outDir + "/num_den_yields/" + processes[j] + "/";
      createPlotDirAndCopyPhp(outDir_num_den);

      // pt vs eta
      TH2D* hpass2D = new TH2D(Form("hpass2D_%s",processes[j].c_str()),"",
			       nBins, ptBins, 
			       h3tmp->GetNbinsY(), (Double_t*) h3tmp->GetYaxis()->GetXbins()->GetArray());
      TH2D* hntot2D = new TH2D(Form("hntot2D_%s",processes[j].c_str()),"",
			       nBins, ptBins, 
			       h3tmp->GetNbinsY(), (Double_t*) h3tmp->GetYaxis()->GetXbins()->GetArray());
	  
      fillTH2fromTH3zrange(hntot2D,h3tmp,1,2);
      fillTH2fromTH3zrange(hpass2D,h3tmp,2,2);
      // if (processes[j] == "W" or processes[j] == "Z" or processes[j] == "Top" or processes[j] == "DiBosons") {
      // 	hpass2D_ewk->	
      // }
      hpass2D->SetMinimum(0.0);
      hntot2D->SetMinimum(0.0);

      // for QCD only, draw FR graphs in 4 bins, 2 in EB and 2 in EE
      // just to see how FR should be, there is no stat to do it for all the bins
      // also, merge positive and negative bins to gain in stat, I don't expect differences between negative and positive side 
      if (processes[j] == "QCD") {

	// use this binnning: ptBinBoundariesQCD_1
	string outdirQCD = outDir + "/QCD_FR_MC/";
	createPlotDirAndCopyPhp(outdirQCD);
	vector<Double_t> qcdEta = {0.0, 1.0, 1.4442, 1.566, 2.1, 2.5};
	vector<string> qcdEtaStr = {"0p0", "1p0", "1p4442", "1p566", "2p1", "2p5"};
	Double_t error = 0.0;

	for (UInt_t iqcd = 0; iqcd < qcdEta.size()-1; ++iqcd) {

	  TH1D* hQCD_MC_FR_pass = new TH1D("hQCD_MC_FR_pass","",nBins, ptBins);
	  TH1D* hQCD_MC_FR_ntot = new TH1D("hQCD_MC_FR_ntot","",nBins, ptBins);
	  for (Int_t ix = 1; ix <= h3tmp->GetNbinsX(); ++ix) {
	    Int_t binQCDEtalow  = h3tmp->GetYaxis()->FindBin(qcdEta[iqcd]+epsilon);
	    Int_t binQCDEtahigh = h3tmp->GetYaxis()->FindBin(qcdEta[iqcd+1]+epsilon) - 1;  
	    hQCD_MC_FR_pass->SetBinContent(ix,h3tmp->IntegralAndError(ix,ix,binQCDEtalow,binQCDEtahigh,2,2,error)); 
	    hQCD_MC_FR_pass->SetBinError(ix,error);
	    hQCD_MC_FR_ntot->SetBinContent(ix,h3tmp->IntegralAndError(ix,ix,binQCDEtalow,binQCDEtahigh,1,2,error)); 
	    hQCD_MC_FR_ntot->SetBinError(ix,error);
	  }
	  // now neg eta
	  TH1D* hQCD_MC_FR_negEta_pass = new TH1D("hQCD_MC_FR_negEta_pass","",nBins, ptBins);
	  TH1D* hQCD_MC_FR_negEta_ntot = new TH1D("hQCD_MC_FR_negEta_ntot","",nBins, ptBins);
	  for (Int_t ix = 1; ix <= h3tmp->GetNbinsX(); ++ix) {
	    Int_t binQCDEtalow  = h3tmp->GetYaxis()->FindBin(-1.*qcdEta[iqcd+1]+epsilon);
	    Int_t binQCDEtahigh = h3tmp->GetYaxis()->FindBin(-1.*qcdEta[iqcd]+epsilon) - 1;  
	    hQCD_MC_FR_negEta_pass->SetBinContent(ix,h3tmp->IntegralAndError(ix,ix,binQCDEtalow,binQCDEtahigh,2,2,error)); 
	    hQCD_MC_FR_negEta_pass->SetBinError(ix,error);
	    hQCD_MC_FR_negEta_ntot->SetBinContent(ix,h3tmp->IntegralAndError(ix,ix,binQCDEtalow,binQCDEtahigh,1,2,error)); 
	    hQCD_MC_FR_negEta_ntot->SetBinError(ix,error);
	  }
	  // sum negative eta and make ratio
	  hQCD_MC_FR_pass->Add(hQCD_MC_FR_negEta_pass);
	  hQCD_MC_FR_ntot->Add(hQCD_MC_FR_negEta_ntot);
	  // rebin to coarser pt binning
	  hQCD_MC_FR_pass = (TH1D*) hQCD_MC_FR_pass->Rebin(ptBinBoundariesQCD_3.size()-1, "", ptBinBoundariesQCD_3.data());
	  hQCD_MC_FR_ntot = (TH1D*) hQCD_MC_FR_ntot->Rebin(ptBinBoundariesQCD_3.size()-1, "", ptBinBoundariesQCD_3.data());
	  // get FR by computing the ratio	  
	  TGraphAsymmErrors* gr_fr_QCD_MC = new TGraphAsymmErrors(hQCD_MC_FR_pass, hQCD_MC_FR_ntot, "cl=0.683 b(1,1) mode"); 
	  hQCD_MC_FR_pass->Divide(hQCD_MC_FR_ntot); 
	  drawSingleTH1(hQCD_MC_FR_pass,
			"electron p_{T} [GeV]", "Fake rate (QCD MC)::0,1.2", Form("fr_QCDMC_abseta_%s_%s",qcdEtaStr[iqcd].c_str(),qcdEtaStr[iqcd+1].c_str()),
			outdirQCD,Form("%.4g < |#eta| < %.4g",qcdEta[iqcd],qcdEta[iqcd+1]), inputLuminosity, 1, true, 1, "HIST", gr_fr_QCD_MC);
	  // delete stuff, will be redefined in next item of the loop on qcdEta
	  delete hQCD_MC_FR_pass;
	  delete hQCD_MC_FR_ntot;
	  delete hQCD_MC_FR_negEta_pass;
	  delete hQCD_MC_FR_negEta_ntot;
	  delete gr_fr_QCD_MC;
	}

      }
      // end of QCD only stuff

      TH2D* hFR2D = (TH2D*) hpass2D->Clone(Form("hFR2D_%s",processes[j].c_str()));
      if (!hFR2D->Divide(hntot2D)) {	  
	cout << "Error in doing hFR2D->Divide(hntot2D). Exiting" << endl;
	exit(EXIT_FAILURE);
      }

      string etaYaxisName = hasSignedEta ? "electron #eta" : "electron |#eta|";
      string ptXaxisName = "electron p_{T} [GeV]";

      drawCorrelationPlot(hpass2D, 
			  ptXaxisName,
			  etaYaxisName,
			  "Events (fake-rate numerator)",
			  Form("events_FRnumerator_%s",processes[j].c_str()),
			  "", outDir_num_den, 1, 1, false,false,false,1,0.12,0.24);
      drawCorrelationPlot(hntot2D, 
			  ptXaxisName,
			  etaYaxisName,
			  "Events (fake-rate denominator)",
			  Form("events_FRdenominator_%s",processes[j].c_str()),
			  "", outDir_num_den, 1, 1, false,false,false,1,0.12,0.24);

      // hFR2D->SetMinimum(0.0);
      // hFR2D->SetMaximum(1.0);
      drawCorrelationPlot(hFR2D, 
			  ptXaxisName,
			  etaYaxisName,
			  "Fake-rate::0,1.0",
			  Form("fakeRate_pt_vs_eta_%s",processes[j].c_str()),
			  "", outDir_num_den, 1, 1, false,false,false,1);

      delete hpass2D;
      delete hntot2D;
      delete hFR2D;

      
    }

    // if binning is 0.1,0.2,0.3,... and I look for range 0.1->0.2, search bin with 0.1+epsilon, then bin with 0.2+epsilon and subtract 1 bin from the latter
    // epsilon is a security number to avoid that due to float precision, the edge is assigned to wrong bin (lower boundary should belong to it, upper should not)
    Int_t binYlow  = scan_vs_eta ?  h3tmp->GetYaxis()->FindBin(etaLow+epsilon)       : 0;
    Int_t binYhigh = scan_vs_eta ? (h3tmp->GetYaxis()->FindBin(etaHigh+epsilon) - 1) : (1 + h3tmp->GetNbinsY());  
    // In binYhigh, if scan_vs_eta is true we subtract -1 because the lower edge of a bin belong to that bin
    // Therefore, if we want FR from 0.0 to 0.3 and the histogram is binned like 0.0,0.1,0.2,0.3,0.4,...
    // h3tmp->GetYaxis()->FindBin(0.0) return bin=1, because 0.0 is the lower edge of bin=1 and belongs to it
    // h3tmp->GetYaxis()->FindBin(0.3) would return bin=4 for the same reason, but we just want to sum bins from bin=1 to bin=3 (included)
    // if scan_vs_eta = false, use the integral in all the Y axis range (including underflows and overflows), unless we specify differently

    hpass.push_back( new TH1D(Form("%s_pass",processes[j].c_str()),"", nBins, ptBins) );
    hntot.push_back( new TH1D(Form("%s_ntot",processes[j].c_str()),"", nBins, ptBins) );
    if (hpass_ewk == nullptr && hntot_ewk == nullptr) {
      hpass_ewk = new TH1D("ewk_pass","", nBinsEWK, ptBinBoundariesEWK.data());
      hntot_ewk = new TH1D("ewk_ntot","", nBinsEWK, ptBinBoundariesEWK.data());
    }
    if (hpass_top_vv == nullptr && hntot_top_vv == nullptr) {
      hpass_top_vv = new TH1D("top_vv_pass","", nBinsEWK, ptBinBoundariesEWK.data());
      hntot_top_vv = new TH1D("top_vv_ntot","", nBinsEWK, ptBinBoundariesEWK.data());
    }
    if (hpass_wz == nullptr && hntot_wz == nullptr) {
      hpass_wz = new TH1D("wz_pass","", nBinsEWK, ptBinBoundariesEWK.data());
      hntot_wz = new TH1D("wz_ntot","", nBinsEWK, ptBinBoundariesEWK.data());
    }
    if (hpass_ewk_scaledUp == nullptr && hntot_ewk_scaledUp == nullptr) {
      // will be subtracted from data
      hpass_ewk_scaledUp = new TH1D("ewk_scaledUp_pass","", nBins, ptBins);
      hntot_ewk_scaledUp = new TH1D("ewk_scaledUp_ntot","", nBins, ptBins);
    }
    if (hpass_ewk_scaledDown == nullptr && hntot_ewk_scaledDown == nullptr) {
      // will be subtracted from data
      hpass_ewk_scaledDown = new TH1D("ewk_scaledDown_pass","", nBins, ptBins);
      hntot_ewk_scaledDown = new TH1D("ewk_scaledDown_ntot","", nBins, ptBins);
    }
    if (hpass_data_subtr_scaledUpEWK == nullptr && hntot_data_subtr_scaledUpEWK == nullptr) {
      // will be subtracted from data
      hpass_data_subtr_scaledUpEWK = new TH1D("data_subtr_scaledUpEWK_pass","", nBins, ptBins);
      hntot_data_subtr_scaledUpEWK = new TH1D("data_subtr_scaledUpEWK_ntot","", nBins, ptBins);
    }
    if (hpass_data_subtr_scaledDownEWK == nullptr && hntot_data_subtr_scaledDownEWK == nullptr) {
      // will be subtracted from data
      hpass_data_subtr_scaledDownEWK = new TH1D("data_subtr_scaledDownEWK_pass","", nBins, ptBins);
      hntot_data_subtr_scaledDownEWK = new TH1D("data_subtr_scaledDownEWK_ntot","", nBins, ptBins);
    }

    Double_t error = 0.0;
    for (Int_t ix = 1; ix <= h3tmp->GetNbinsX(); ++ix) {
      hpass.back()->SetBinContent(ix,h3tmp->IntegralAndError(ix,ix,binYlow,binYhigh,2,2,error)); // bin 1 along Z for fail, 2 for pass (from 2 to 2 selects only bin 2)
      hpass.back()->SetBinError(ix,error);
      hntot.back()->SetBinContent(ix,h3tmp->IntegralAndError(ix,ix,binYlow,binYhigh,1,2,error)); // bin 1 along Z for fail, 2 for pass (from 1 to 2 selects both bins)
      hntot.back()->SetBinError(ix,error);
    }

    // this is to draw pt distributions for some processes
    // do it before rebinning
    // if (processes[j] == "data" or processes[j] == "data_sub" or processes[j] == "W" or processes[j] == "Z" or processes[j] == "Top" or processes[j] == "DiBosons") {
    if (processes[j] != "QCD") {
      if (processes[j] == "data_sub") leg_pt_proc.push_back("data - EWK MC");
      else leg_pt_proc.push_back(processes[j]);
      // create 2 new histograms to store pt
      pt_num_proc.push_back( new TH1D(Form("pt_num_%s",processes[j].c_str()),"", nBins, ptBins) );
      pt_den_proc.push_back( new TH1D(Form("pt_den_%s",processes[j].c_str()),"", nBins, ptBins) );
      // fill them copying hpass and hntot (so they are two different and independent objects)
      copyHisto(pt_num_proc.back(),hpass.back());
      copyHisto(pt_den_proc.back(),hntot.back());
    }


    if (processes[j] == "QCD") {
      hpass.back() = hpass.back()->Rebin(nBinsQCD,"",ptBinBoundariesQCD.data());
      hntot.back() = hntot.back()->Rebin(nBinsQCD,"",ptBinBoundariesQCD.data());
    } else if (processes[j] == "W" || processes[j] == "Z") {
      hpass_ewk_scaledUp->Add(hpass.back(), 1.+ subtrEWK_nSigma*scaleFactor[processes[j]]);   
      hntot_ewk_scaledUp->Add(hntot.back(), 1.+ subtrEWK_nSigma*scaleFactor[processes[j]]);  
      hpass_ewk_scaledDown->Add(hpass.back(), 1. - subtrEWK_nSigma*scaleFactor[processes[j]]);   
      hntot_ewk_scaledDown->Add(hntot.back(), 1. - subtrEWK_nSigma*scaleFactor[processes[j]]);  
      hpass.back() = hpass.back()->Rebin(nBinsEWK,"",ptBinBoundariesEWK.data());
      hntot.back() = hntot.back()->Rebin(nBinsEWK,"",ptBinBoundariesEWK.data());
      hpass_ewk->Add(hpass.back());
      hntot_ewk->Add(hntot.back());
      hpass_wz->Add(hpass.back());
      hntot_wz->Add(hntot.back());
    } else if (processes[j] == "Top" || processes[j] == "DiBosons") {
      hpass_ewk_scaledUp->Add(hpass.back(), 1.+ subtrEWK_nSigma*scaleFactor[processes[j]]);   
      hntot_ewk_scaledUp->Add(hntot.back(), 1.+ subtrEWK_nSigma*scaleFactor[processes[j]]);  
      hpass_ewk_scaledDown->Add(hpass.back(), 1. - subtrEWK_nSigma*scaleFactor[processes[j]]);   
      hntot_ewk_scaledDown->Add(hntot.back(), 1. - subtrEWK_nSigma*scaleFactor[processes[j]]);  
      hpass.back() = hpass.back()->Rebin(nBinsEWK,"",ptBinBoundariesEWK.data());
      hntot.back() = hntot.back()->Rebin(nBinsEWK,"",ptBinBoundariesEWK.data());
      hpass_ewk->Add(hpass.back());
      hntot_ewk->Add(hntot.back());
      hpass_top_vv->Add(hpass.back());
      hntot_top_vv->Add(hntot.back());
    } else if (processes[j] == "data" || processes[j] == "data_sub") {
      if (processes[j] == "data") {
	hpass_data_subtr_scaledUpEWK->Add(hpass.back());
	hntot_data_subtr_scaledUpEWK->Add(hntot.back());
	hpass_data_subtr_scaledDownEWK->Add(hpass.back());
	hntot_data_subtr_scaledDownEWK->Add(hntot.back());
      }
      hpass.back() = hpass.back()->Rebin(nBinsData,"",ptBinBoundariesData.data());
      hntot.back() = hntot.back()->Rebin(nBinsData,"",ptBinBoundariesData.data());
    }


    if (processes[j] == "W") {

      fr_w = new TGraphAsymmErrors(hpass.back(), hntot.back(), "cl=0.683 b(1,1) mode");

    } else if (processes[j] == "Z") {

      fr_z = new TGraphAsymmErrors(hpass.back(), hntot.back(), "cl=0.683 b(1,1) mode");

    } else if (processes[j] == "DiBosons") {

      fr_vv = new TGraphAsymmErrors(hpass.back(), hntot.back(), "cl=0.683 b(1,1) mode");

    } else if (processes[j] == "Top") {

      fr_top = new TGraphAsymmErrors(hpass.back(), hntot.back(), "cl=0.683 b(1,1) mode");

    } else if (processes[j] == "data_sub") {

      fr_data_subEWKMC = new TGraphAsymmErrors(hpass.back(), hntot.back(), "cl=0.683 b(1,1) mode"); 

    } else if (processes[j] == "QCD") {

      fr_qcd = new TGraphAsymmErrors(hpass.back(), hntot.back(), "cl=0.683 b(1,1) mode"); 

    } else if (processes[j] == "data") {

      fr_data = new TGraphAsymmErrors(hpass.back(), hntot.back(), "cl=0.683 b(1,1) mode");
	
    } 

  }

 
  // now draw pt distribution
  string outDirPt = outDir + "/pt_distribution/";
  createPlotDirAndCopyPhp(outDirPt);
  draw_nTH1(pt_num_proc, 
	    Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), 
	    "Events/bin [GeV^{-1 }]", 
	    Form("ele_pt_%s_%s_numerator",detId.c_str(),plotPostFix.c_str()), 
	    outDirPt, leg_pt_proc, "", inputLuminosity, 1, false, false);
  draw_nTH1(pt_den_proc, 
	    Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), 
	    "Events/bin [GeV^{-1 }]", 
	    Form("ele_pt_%s_%s_denominator",detId.c_str(),plotPostFix.c_str()), 
	    outDirPt, leg_pt_proc, "", inputLuminosity, 1, false, false);	    

  // now create new FR as (data - EWK') where EWK' is the scaled EWK
  hpass_data_subtr_scaledUpEWK->Add(hpass_ewk_scaledUp,-1);  
  hntot_data_subtr_scaledUpEWK->Add(hntot_ewk_scaledUp,-1);  
  hpass_data_subtr_scaledDownEWK->Add(hpass_ewk_scaledDown,-1);  
  hntot_data_subtr_scaledDownEWK->Add(hntot_ewk_scaledDown,-1);

  // now rebin to the desired binning
  hpass_data_subtr_scaledUpEWK   = hpass_data_subtr_scaledUpEWK->Rebin(nBinsData,"",ptBinBoundariesData.data());
  hntot_data_subtr_scaledUpEWK   = hntot_data_subtr_scaledUpEWK->Rebin(nBinsData,"",ptBinBoundariesData.data());
  hpass_data_subtr_scaledDownEWK = hpass_data_subtr_scaledDownEWK->Rebin(nBinsData,"",ptBinBoundariesData.data());
  hntot_data_subtr_scaledDownEWK = hntot_data_subtr_scaledDownEWK->Rebin(nBinsData,"",ptBinBoundariesData.data());

  fr_data_subScaledUpEWKMC = new TGraphAsymmErrors(hpass_data_subtr_scaledUpEWK, hntot_data_subtr_scaledUpEWK, "cl=0.683 b(1,1) mode"); 
  fr_data_subScaledDownEWKMC = new TGraphAsymmErrors(hpass_data_subtr_scaledDownEWK, hntot_data_subtr_scaledDownEWK, "cl=0.683 b(1,1) mode"); 

  vector<Int_t> colorList = {kBlack, kRed};
  vector<string> legendEntries = {"data", "data - EWK MC"};
  gr.push_back( fr_data );
  gr.push_back( fr_data_subEWKMC );

  if (not noDrawQCD) {
    gr.push_back( fr_qcd );
    colorList.push_back(kGreen+2);
    legendEntries.push_back("QCD MC");
  }


  fr_ewk = new TGraphAsymmErrors(hpass_ewk, hntot_ewk, "cl=0.683 b(1,1) mode");
  fr_top_vv = new TGraphAsymmErrors(hpass_top_vv, hntot_top_vv, "cl=0.683 b(1,1) mode");
  fr_wz = new TGraphAsymmErrors(hpass_wz, hntot_wz, "cl=0.683 b(1,1) mode");

  // settings for the canvas with all the graphs
  if (showMergedEWK) {
    gr.push_back(fr_ewk);
    colorList.push_back(kBlue);
    legendEntries.push_back("EWK MC (prompt rate)");
    gr.push_back(fr_data_subScaledUpEWKMC);
    colorList.push_back(kGreen+2);
    legendEntries.push_back(Form("data - (1 + %.1g #sigma) EWK MC",subtrEWK_nSigma));
    gr.push_back(fr_data_subScaledDownEWKMC);
    colorList.push_back(kGreen+3);
    legendEntries.push_back(Form("data - (1 - %.1g #sigma) EWK MC",subtrEWK_nSigma));
  } else {
    if (showMergedWZ) {
      gr.push_back(fr_wz);
      colorList.push_back(kBlue);
      legendEntries.push_back("W,Z MC (prompt rate)");
    } else {
      gr.push_back(fr_w);
      gr.push_back(fr_z);
      colorList.push_back(kBlue);
      colorList.push_back(kAzure+2);    
      legendEntries.push_back("W MC (prompt rate)");
      legendEntries.push_back("Z MC (prompt rate)");
    }
    if (showTopVV) {
      gr.push_back(fr_top_vv);
      if (noDrawQCD) colorList.push_back(kOrange+2);
      else               colorList.push_back(kPink);
      legendEntries.push_back("Top,VV MC (prompt rate)");
    }
    gr.push_back(fr_data_subScaledUpEWKMC);
    if (noDrawQCD) colorList.push_back(kGreen+2);
    else           colorList.push_back(kOrange+7);
    legendEntries.push_back(Form("data - (1 + %.1g #sigma) EWK MC",subtrEWK_nSigma));
    gr.push_back(fr_data_subScaledDownEWKMC);
    if (noDrawQCD) colorList.push_back(kGreen+3);
    else           colorList.push_back(kOrange+8);
    legendEntries.push_back(Form("data - (1 - %.1g #sigma) EWK MC",subtrEWK_nSigma));
  }

  drawGraphCMS(gr, 
	       Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), 
	       Form("Fake Rate::%s",yrange.c_str()), 
	       Form("fakerateComparison_%s_%s",detId.c_str(),plotPostFix.c_str()), 
	       outDir, legendEntries, legCoord,inputLuminosity,false,"", colorList);
  
  //////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////

  // ranges for the fit plot
  // currently overriden inside the fucntion to plot the fit
  // keep for reference
  string yrange_data  = isEB ? "0.5,1.0" : "0.1,0.4";
  string yrange_qcdmc = isEB ? "0.0,1.2" : "0.0,0.8";
  string yrange_w     = isEB ? "0.8,1.2" : "0.4,1.2";
  string yrange_z     = isEB ? "0.8,1.2" : "0.4,1.2";
  string yrange_ewk   = isEB ? "0.8,1.2" : "0.4,1.2";
  vector <Double_t> legCoordFit = {0.12,0.7,0.60,0.9};

  string outDirFits = outDir + "/fits/";
  createPlotDirAndCopyPhp(outDirFits);

  TFitResultPtr ptr_data_fitNarrowRange = nullptr;
  TFitResultPtr ptr_data = fitGraph(fr_data_subEWKMC, isEB, Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), Form("Fake Rate::%s",yrange_data.c_str()), Form("fr_data_subEWKMC_%s_%s",detId.c_str(),plotPostFix.c_str()), outDirFits+"data/", "data - EWK MC", legCoordFit,inputLuminosity,true, false, 1.0, true, &ptr_data_fitNarrowRange, 
				    excludePoints_Data,ptMin_excludeRangeData,ptMax_excludeRangeData);

  TFitResultPtr ptr_data_subScaledUpEWKMC = fitGraph(fr_data_subScaledUpEWKMC, isEB, Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), Form("Fake Rate::%s",yrange_data.c_str()), Form("fr_data_subScaledUpEWKMC_%s_%s",detId.c_str(),plotPostFix.c_str()), outDirFits+"data_subScaledUpEWKMC/", Form("data - (1 + %.1g #sigma) EWK MC",subtrEWK_nSigma), legCoordFit,inputLuminosity,true, false, 1.0, true, nullptr, excludePoints_Data,ptMin_excludeRangeData,ptMax_excludeRangeData);

  TFitResultPtr ptr_data_subScaledDownEWKMC = fitGraph(fr_data_subScaledDownEWKMC, isEB, Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), Form("Fake Rate::%s",yrange_data.c_str()), Form("fr_data_subScaledDownEWKMC_%s_%s",detId.c_str(),plotPostFix.c_str()), outDirFits+"data_subScaledDownEWKMC/", Form("data - (1 - %.1g #sigma) EWK MC",subtrEWK_nSigma), legCoordFit,inputLuminosity,true, false, 1.0, true, nullptr, excludePoints_Data,ptMin_excludeRangeData,ptMax_excludeRangeData);

  // fit is Y=a*X+b
  // bin n.1 is for b (first parameter of pol1), bin n.2 is for a 

  for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {  
    frSmoothParameter_data->SetBinContent(etaBinTH1,ipar+1,ptr_data->Parameter(ipar)); // param. number from 0, bin number from 1
    frSmoothParameter_data->SetBinError(etaBinTH1,ipar+1,ptr_data->ParError(ipar));
  }

  // fit is Y=a*X+b
  // bin n.1 is for b (first parameter of pol1), bin n.2 is for a 
  for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {  
    frSmoothParameter_data_fitNarrowRange->SetBinContent(etaBinTH1,ipar+1,ptr_data_fitNarrowRange->Parameter(ipar));
    frSmoothParameter_data_fitNarrowRange->SetBinError(etaBinTH1,ipar+1,ptr_data_fitNarrowRange->ParError(ipar));
  }

  for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {  
    frSmoothParameter_data_subScaledUpEWKMC->SetBinContent(etaBinTH1,ipar+1,ptr_data_subScaledUpEWKMC->Parameter(ipar));
    frSmoothParameter_data_subScaledUpEWKMC->SetBinError(etaBinTH1,ipar+1,ptr_data_subScaledUpEWKMC->ParError(ipar));
  }
  for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {  
    frSmoothParameter_data_subScaledDownEWKMC->SetBinContent(etaBinTH1,ipar+1,ptr_data_subScaledDownEWKMC->Parameter(ipar));
    frSmoothParameter_data_subScaledDownEWKMC->SetBinError(etaBinTH1,ipar+1,ptr_data_subScaledDownEWKMC->ParError(ipar));
  }

  TFitResultPtr ptr_w = nullptr;
  TFitResultPtr ptr_z = nullptr;
  TFitResultPtr ptr_ewk = nullptr;
  TFitResultPtr ptr_top_vv = nullptr;
  TFitResultPtr ptr_wz = nullptr;


  ptr_ewk = fitGraph(fr_ewk, isEB, Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), Form("Prompt Rate::%s",yrange_ewk.c_str()), Form("fr_ewk_%s_%s",detId.c_str(),plotPostFix.c_str()), outDirFits+"ewk/", "EWK MC (prompt rate)", legCoordFit,inputLuminosity,false, true, 1.0, true);
  // fit is Y=a*X+b
  // bin n.1 is for b (first parameter of pol1), bin n.2 is for a 
  for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {      
    frSmoothParameter_ewk->SetBinContent(etaBinTH1,ipar+1,ptr_ewk->Parameter(ipar));
    frSmoothParameter_ewk->SetBinError(etaBinTH1,ipar+1,ptr_ewk->ParError(ipar));
  }
  
  if (not showMergedEWK) {

    if (showMergedWZ) {
      
      ptr_wz = fitGraph(fr_wz, isEB, Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), Form("Prompt Rate::%s",yrange_ewk.c_str()), Form("fr_wz_%s_%s",detId.c_str(),plotPostFix.c_str()), outDirFits+"wz/", "W,Z MC (prompt rate)", legCoordFit,inputLuminosity,false, true, 1.0, false);
      // fit is Y=a*X+b
      // bin n.1 is for b (first parameter of pol1), bin n.2 is for a 
      for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {      
	frSmoothParameter_wz->SetBinContent(etaBinTH1,ipar+1,ptr_wz->Parameter(ipar));
	frSmoothParameter_wz->SetBinError(etaBinTH1,ipar+1,ptr_wz->ParError(ipar));
      }
      
    } else {

      ptr_w = fitGraph(fr_w, isEB, Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), Form("Prompt Rate::%s",yrange_w.c_str()), Form("fr_w_%s_%s",detId.c_str(),plotPostFix.c_str()), outDirFits+"w/", "W MC (prompt rate)", legCoordFit,inputLuminosity,false, true, 1.0, false);
      // fit is Y=a*X+b
      // bin n.1 is for b (first parameter of pol1), bin n.2 is for a 
      for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {        
	frSmoothParameter_w->SetBinContent(etaBinTH1,ipar+1,ptr_w->Parameter(ipar));
	frSmoothParameter_w->SetBinError(etaBinTH1,ipar+1,ptr_w->ParError(ipar));
      }

      ptr_z = fitGraph(fr_z, isEB, Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), Form("Prompt Rate::%s",yrange_z.c_str()), Form("fr_z_%s_%s",detId.c_str(),plotPostFix.c_str()), outDirFits+"z/", "Z MC (prompt rate)", legCoordFit,inputLuminosity,false, true, 1.0, false);
      // fit is Y=a*X+b
      // bin n.1 is for b (first parameter of pol1), bin n.2 is for a 
      for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {  
	frSmoothParameter_z->SetBinContent(etaBinTH1,ipar+1,ptr_z->Parameter(ipar));
	frSmoothParameter_z->SetBinError(etaBinTH1,ipar+1,ptr_z->ParError(ipar));
      }

    }

    if (showTopVV) {
      
      ptr_top_vv = fitGraph(fr_top_vv, isEB, Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), Form("Prompt Rate::%s",yrange_ewk.c_str()), Form("fr_top_vv_%s_%s",detId.c_str(),plotPostFix.c_str()), outDirFits+"top_vv/", "Top,VV MC (prompt rate)", legCoordFit,inputLuminosity,false, true, 1.0, false);
      // fit is Y=a*X+b
      // bin n.1 is for b (first parameter of pol1), bin n.2 is for a 
      for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {      
	frSmoothParameter_top_vv->SetBinContent(etaBinTH1,ipar+1,ptr_top_vv->Parameter(ipar));
	frSmoothParameter_top_vv->SetBinError(etaBinTH1,ipar+1,ptr_top_vv->ParError(ipar));
      }
      
    }

  }  


  TFitResultPtr ptr_qcd = nullptr;

  if (not noDrawQCD) {
    
    ptr_qcd = fitGraph(fr_qcd, isEB, Form("electron p_{T} [GeV]::%f,%f",ptMin,ptMax), Form("Fake Rate::%s",yrange_qcdmc.c_str()), Form("fr_qcd_%s_%s",detId.c_str(),plotPostFix.c_str()), outDirFits+"qcd/", "QCD MC            ", legCoordFit,inputLuminosity,false, false, false);

    for (UInt_t ipar = 0; ipar < ptr_data->NPar(); ++ipar) {  
      frSmoothParameter_qcd->SetBinContent(etaBinTH1,ipar+1,ptr_qcd->Parameter(ipar));
      frSmoothParameter_qcd->SetBinError(etaBinTH1,ipar+1,ptr_qcd->ParError(ipar));
    }

  }
  //////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////

  inputFile->Close();
  delete inputFile;

}

//================================================================
void makeFakeRateGraphPlotsAndSmoothing(const string& inputFilePath = "www/wmass/13TeV/fake-rate/test/testFRv8/fr_06_11_2018_eta_pt_granular_mT40_35p9fb_signedEta_subtrAllMC_L1EGprefire_jetPt30_Zveto_newSkim/el/comb/",
					//const string& outDir_tmp = "SAME", 
					const string& outDir_tmp = "www/wmass/13TeV/fake-rate/electron/FR_graphs_tests/fr_06_11_2018_eta_pt_granular_mT40_35p9fb_signedEta_subtrAllMC_L1EGprefire_jetPt30_Zveto_newSkim_fitPol2/", 
					const string& outfileTag = "fr_06_11_2018_eta_pt_granular_mT40_35p9fb_signedEta_subtrAllMC_L1EGprefire_jetPt30_Zveto_newSkim",
					const string& histPrefix = "fakeRateNumerator_el_vs_etal1_pt_granular",
					const Bool_t isMuon = false, 
					const Bool_t showMergedEWK = true, // even if it is false, this is added in the final output root file
					const Bool_t saveToFile = false,  // whether to save is WMass/data/fakerate/ (if false, save in current folder)
					//const TString& etaBinBoundariesList = "-2.5,-2.3,-2.1,-1.9,-1.7,-1.479,-1.2,-0.9,-0.6,-0.3,0.0,0.3,0.6,0.9,1.2,1.479,1.7,1.9,2.1,2.3,2.5",  // important to use dots also for 1.0
					//const TString& etaBinBoundariesList = "0.0,1.0,1.479,1.8,2.1,2.5",
					const TString& etaBinBoundariesList = "-2.5,-2.4,-2.3,-2.2,-2.1,-2.0,-1.9,-1.8,-1.7,-1.566,-1.4442,-1.3,-1.2,-1.1,-1.0,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4442,1.566,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5",
					const vector<Int_t> ptBinIndexQCD = {2},  // should be a number for each eta bin (if only one is given, use it for all)
					const vector<Int_t> ptBinIndexEWK = {2},  // should be a number for each eta bin (if only one is given, use it for all)
					const vector<Int_t> ptBinIndexData = {3},  // should be a number for each eta bin (if only one is given, use it for all)
					const Double_t inputLuminosity = 35.9, // -1 in case luminosity should not be printed
					const Bool_t scan_vs_eta = true, // see below
					const Bool_t hasSignedEta = true, // see below
					const Bool_t noDrawQCD = true,
					const Bool_t showMergedWZ = true,   // overriden if showMergedEWK=true, else it draws W and Z together
					const Bool_t showTopVV = true, // to show Top+DiBoson with W and Z (or W+Z). Overriden if showMergedEWK=true
					const Double_t subtrEWK_nSigma = 1.0  // pass how many cross section sigmas should be used to subtract the EWK processes from data 
					//const Bool_t addTopVVtoWZ = true  // will not draw W,Z and Top,VV separately, but altogether
			   ) 
{

  // if scan_vs_eta is true, it means there is just one root file (fr_sub_eta_0p0_2p5.root or fr_sub_eta_m2p5_2p5.root)
  // The TH3 inside are pt vs eta vs passID (instead of mt or whatever other variable), where eta has bins of 0.1 from 0 to 2.5
  // Therefore, one can produce FR in whatever binning of eta (given by etaBinBoundariesList)
  // hasSignedEta is used to decide whether the input file has 0p0_2p5 or m2p5_2p5 in its name

  if (isMuon) {
    cout << "Warning: at the moment this macro has hardcoded parts for electrons. Usage with muons must be implemented! Exit." << endl;
    exit(EXIT_FAILURE);
  }


  TObjArray* array = etaBinBoundariesList.Tokenize(",");
  vector<Double_t> etaBoundaries;
  vector<string> etaBoundariesString;

  for (Int_t j = 0; j < array->GetEntries(); j++) {
    TString str = ((TObjString *) array->At(j))->String();
    etaBoundariesString.push_back(string(str.Data()));
    etaBoundaries.push_back(stod(etaBoundariesString.back()));
    size_t pos_dot = etaBoundariesString.back().find(".");  // find position of dot
    size_t pos_sign = etaBoundariesString.back().find("-");  // find position of minus sign
    etaBoundariesString.back().replace(pos_dot,1,"p"); // replace dot with p
    if (pos_sign != string::npos) etaBoundariesString.back().replace(pos_sign,1,"m"); // replace dot with p
  }


  cout << "Eta bins boundaries: ";
  for (UInt_t i = 0; i < etaBoundaries.size(); i++) {
    cout << etaBoundaries[i] << " ";
  }
  cout << endl;
  cout << "Eta bins boundaries (string): ";
  for (UInt_t i = 0; i < etaBoundariesString.size(); i++) {
    cout << etaBoundariesString[i] << " ";
  }
  cout << endl;

  etaBoundariesGlobal = etaBoundaries;
  Int_t NetaBins = (Int_t) etaBoundaries.size() - 1;
  vector<Double_t> parNumberBoundaries = {-0.5,0.5,1.5,2.5}; // bin center is 0 or 1 for a 2 parameter fit (we used a straight line to fit FR, so we have 2 parameters)
  string hParamTitle = "pol2 fit parameters (offset, slope, concavity) vs eta";
  if (smoothPolinDegree == 1) {
    parNumberBoundaries.pop_back();
    hParamTitle = "pol1 fit parameters (offset, slope) vs eta";
  }
  Int_t Nparam = (Int_t) parNumberBoundaries.size() - 1;
  

  // use cross section uncertainty
  // might want to use an eta-dependent factor for W
  scaleFactor["W"] = 0.038;
  scaleFactor["Z"] = 0.04;
  scaleFactor["Top"] = 0.09;
  scaleFactor["DiBosons"] = 0.05;
  //scaleFactor["QCD"] = 0.9;


  frSmoothParameter_data = new TH2D("frSmoothParameter_data",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());
  frSmoothParameter_data_fitNarrowRange = new TH2D("frSmoothParameter_data_fitNarrowRange",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());
  frSmoothParameter_data_subScaledUpEWKMC = new TH2D("frSmoothParameter_data_subScaledUpEWKMC",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());
  frSmoothParameter_data_subScaledDownEWKMC = new TH2D("frSmoothParameter_data_subScaledDownEWKMC",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());
  frSmoothParameter_qcd = new TH2D("frSmoothParameter_qcd",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());
  frSmoothParameter_w = new TH2D("frSmoothParameter_w",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());
  frSmoothParameter_z = new TH2D("frSmoothParameter_z",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());
  frSmoothParameter_ewk = new TH2D("frSmoothParameter_ewk",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());
  frSmoothParameter_top_vv = new TH2D("frSmoothParameter_top_vv",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());
  frSmoothParameter_wz = new TH2D("frSmoothParameter_wz",hParamTitle.c_str(),NetaBins,etaBoundaries.data(),Nparam,parNumberBoundaries.data());

  string outDir = (outDir_tmp == "SAME") ? (inputFilePath + "FR_graphs/") : outDir_tmp;

  for (Int_t i = 0; i < NetaBins; i++) {

    string etabinPostFix = "eta_" + etaBoundariesString[i] + "_" + etaBoundariesString[i+1];
    //string fr_fQCD_file = "fr_sub_" + etabinPostFix + "_fQCD.root";

    string specialEtaBinPostFix = "";
    if (scan_vs_eta) {
      if (hasSignedEta) specialEtaBinPostFix = "eta_m2p5_2p5";
      else              specialEtaBinPostFix = "eta_0p0_2p5";
    }

    string fr_fQCD_file = "fr_sub_" + (scan_vs_eta ? specialEtaBinPostFix : etabinPostFix) + ".root";

    //Bool_t isEB = (etaBoundaries[i] < 1.479) ? true : false; 
    Bool_t isEB = false;
    if (etaBoundaries[i] < 1.479 && etaBoundaries[i] >= 0) isEB = true; 
    if (etaBoundaries[i] >= -1.479 && etaBoundaries[i] <= 0) isEB = true; 

    doFakeRateGraphPlots(inputFilePath + fr_fQCD_file,
			 outDir,
			 histPrefix,
			 ptBinIndexQCD,
			 ptBinIndexEWK,
			 ptBinIndexData,
			 showMergedEWK,
			 inputLuminosity,
			 isEB,
			 etabinPostFix,
			 i,
			 scan_vs_eta,etaBoundaries[i],etaBoundaries[i+1],hasSignedEta,
			 noDrawQCD,
			 showMergedWZ,
			 showTopVV,
			 subtrEWK_nSigma
			 ); 

  }

  cout << "etaBoundariesGlobal.size()-1, etaBoundariesGlobal.data() " << etaBoundariesGlobal.size()-1 << "   " << etaBoundariesGlobal.data() << endl;

  // following works only if you are in the CMSSW_BASE area where you have CMGTools/WMass/...
  char* cmsswPath;
  cmsswPath = getenv ("CMSSW_BASE");
  if (cmsswPath == NULL) {
    cout << "Error in makeFakeRateSmoothing(): environment variable CMSSW_BASE not found. Exit" << endl;
    exit(EXIT_FAILURE);
  }
  char* currentPath_ptr;
  currentPath_ptr = getenv ("PWD");
  string currentPath = string(currentPath_ptr);

  string frSmoothFileName = "";

  if (saveToFile && currentPath.find("src/CMGTools/WMass") != string::npos) {
    frSmoothFileName += Form("%s/src/CMGTools/WMass/data/fakerate/",cmsswPath);
  } else {
    if (not saveToFile) {
      cout << endl;
      cout << endl;
      cout << "##############" << endl;
      cout << "### WARNING: " << endl;
      cout << "### Not saving smoothed FR fit parameters to file in CMGTools/WMass/data/fakerate/ because saveToFile option is false." << endl;
      cout << "### Output file will be produced in current directory." << endl;
      cout << "##############" << endl;
      cout << endl;
    } else {
      cout << "Warning: current working path doesn't match 'src/CMGTools/WMass'." << endl;
      cout << "Output file will be produced in current directory" << endl;
    }
  }

  frSmoothFileName += (isMuon ? "fakeRateSmoothed_mu" : "fakeRateSmoothed_el");
  if (outfileTag != "") frSmoothFileName = frSmoothFileName + "_" + outfileTag;
  frSmoothFileName = frSmoothFileName + ".root";

  TFile* frSmoothFile = new TFile(frSmoothFileName.c_str(),"RECREATE");
  if (!frSmoothFile || frSmoothFile->IsZombie()) {
    cout << "Error: file not opened. Exit" << endl;
    exit(EXIT_FAILURE);
  }

  frSmoothFile->cd();

  // fill TH2 (pt vs |eta|) with smoothed fake rate
  string etaYaxisName = hasSignedEta ? "electron #eta" : "electron |#eta|";
  
  TH2D* fr_pt_eta_data = new TH2D("fr_pt_eta_data",Form("fake rate for data;electron p_{T};%s",etaYaxisName.c_str()), 
				  70, 30, 65, NetaBins, etaBoundaries.data());
  TH2D* fr_pt_eta_data_fitNarrowRange = new TH2D("fr_pt_eta_data_fitNarrowRange",Form("fake rate for data;electron p_{T};%s",etaYaxisName.c_str()), 
				  70, 30, 65, NetaBins, etaBoundaries.data());
  TH2D* fr_pt_eta_data_subScaledUpEWKMC = new TH2D("fr_pt_eta_data_subScaledUpEWKMC",Form("fake rate for data;electron p_{T};%s",etaYaxisName.c_str()), 
				  70, 30, 65, NetaBins, etaBoundaries.data());
  TH2D* fr_pt_eta_data_subScaledDownEWKMC = new TH2D("fr_pt_eta_data_subScaledDownEWKMC",Form("fake rate for data;electron p_{T};%s",etaYaxisName.c_str()), 
				  70, 30, 65, NetaBins, etaBoundaries.data());
  TH2D* fr_pt_eta_qcd  = new TH2D("fr_pt_eta_qcd",Form("fake rate for QCD MC;electron p_{T};%s",etaYaxisName.c_str()), 
				  70, 30, 65, NetaBins, etaBoundaries.data());
  TH2D* fr_pt_eta_w    = new TH2D("fr_pt_eta_w",Form("prompt rate for W MC;electron p_{T};%s",etaYaxisName.c_str()), 
				  70, 30, 65, NetaBins, etaBoundaries.data());
  TH2D* fr_pt_eta_z    = new TH2D("fr_pt_eta_z",Form("prompt rate for Z MC;electron p_{T};%s",etaYaxisName.c_str()), 
				  70, 30, 65, NetaBins, etaBoundaries.data());
  TH2D* fr_pt_eta_ewk  = new TH2D("fr_pt_eta_ewk",Form("prompt rate for EWK MC;electron p_{T};%s",etaYaxisName.c_str()), 
				  70, 30, 65, NetaBins, etaBoundaries.data());
  TH2D* fr_pt_eta_top_vv  = new TH2D("fr_pt_eta_top_vv",Form("prompt rate for Top,VV MC;electron p_{T};%s",etaYaxisName.c_str()), 
				     70, 30, 65, NetaBins, etaBoundaries.data());
  TH2D* fr_pt_eta_wz  = new TH2D("fr_pt_eta_wz",Form("prompt rate for W,Z MC;electron p_{T};%s",etaYaxisName.c_str()), 
				 70, 30, 65, NetaBins, etaBoundaries.data());

  cout << "Creating TH2 fr_pt_eta_* with smoothed fake or prompt rate (pT vs |eta|)" << endl;
  cout << endl;
  fillFakeRateTH2smooth(fr_pt_eta_data, frSmoothParameter_data);
  fillFakeRateTH2smooth(fr_pt_eta_data_fitNarrowRange, frSmoothParameter_data_fitNarrowRange);
  fillFakeRateTH2smooth(fr_pt_eta_data_subScaledUpEWKMC, frSmoothParameter_data_subScaledUpEWKMC);
  fillFakeRateTH2smooth(fr_pt_eta_data_subScaledDownEWKMC, frSmoothParameter_data_subScaledDownEWKMC);
  if (not noDrawQCD) fillFakeRateTH2smooth(fr_pt_eta_qcd, frSmoothParameter_qcd);
  fillFakeRateTH2smooth(fr_pt_eta_ewk, frSmoothParameter_ewk);
  if (not showMergedEWK) {
    if (showMergedWZ) {
      fillFakeRateTH2smooth(fr_pt_eta_wz, frSmoothParameter_wz);    
    } else {
      fillFakeRateTH2smooth(fr_pt_eta_w, frSmoothParameter_w);
      fillFakeRateTH2smooth(fr_pt_eta_z, frSmoothParameter_z);
    }
    if (showTopVV) {
      fillFakeRateTH2smooth(fr_pt_eta_top_vv, frSmoothParameter_top_vv);
    }
  }

  string outDirSmooth = outDir + "/smooth/";
  createPlotDirAndCopyPhp(outDirSmooth);
  // draw some TH2
  drawCorrelationPlot(fr_pt_eta_data, 
		      fr_pt_eta_data->GetXaxis()->GetTitle(),
		      fr_pt_eta_data->GetYaxis()->GetTitle(),
		      "fake rate",
		      "smoothed_fakeRate_pt_vs_eta_data",
		      "", outDirSmooth, 1,1, false,false,false,1);
  drawCorrelationPlot(fr_pt_eta_data, 
		      fr_pt_eta_data->GetXaxis()->GetTitle(),
		      fr_pt_eta_data->GetYaxis()->GetTitle(),
		      "fake rate::0,1.0",
		      "smoothed_fakeRate_pt_vs_eta_data_wideZaxis",
		      "", outDirSmooth, 1,1, false,false,false,1);
  // drawCorrelationPlot(fr_pt_eta_data_fitNarrowRange, 
  // 		      fr_pt_eta_data_fitNarrowRange->GetXaxis()->GetTitle(),
  // 		      fr_pt_eta_data_fitNarrowRange->GetYaxis()->GetTitle(),
  // 		      "fake rate::0,1.0",
  // 		      "smoothed_fakeRate_pt_vs_eta_data_fitNarrowRange",
  // 		      "", outDirSmooth, 1,1, false,false,false,1);
  drawCorrelationPlot(fr_pt_eta_data_subScaledUpEWKMC, 
		      fr_pt_eta_data_subScaledUpEWKMC->GetXaxis()->GetTitle(),
		      fr_pt_eta_data_subScaledUpEWKMC->GetYaxis()->GetTitle(),
		      "fake rate::0,1.0",
		      "smoothed_fakeRate_pt_vs_eta_data_subScaledUpEWKMC",
		      "", outDirSmooth, 1,1, false,false,false,1);
  drawCorrelationPlot(fr_pt_eta_data_subScaledDownEWKMC, 
		      fr_pt_eta_data_subScaledDownEWKMC->GetXaxis()->GetTitle(),
		      fr_pt_eta_data_subScaledDownEWKMC->GetYaxis()->GetTitle(),
		      "fake rate::0,1.0",
		      "smoothed_fakeRate_pt_vs_eta_data_subScaledDownEWKMC",
		      "", outDirSmooth, 1,1, false,false,false,1);
  drawCorrelationPlot(fr_pt_eta_ewk, 
		      fr_pt_eta_ewk->GetXaxis()->GetTitle(),
		      fr_pt_eta_ewk->GetYaxis()->GetTitle(),
		      "prompt rate",
		      "smoothed_promptRate_pt_vs_eta_ewk",
		      "", outDirSmooth, 1,1, false,false,false,1);
  if (not showMergedEWK) {
    if (showMergedWZ) {
      drawCorrelationPlot(fr_pt_eta_wz, 
			  fr_pt_eta_wz->GetXaxis()->GetTitle(),
			  fr_pt_eta_wz->GetYaxis()->GetTitle(),
			  "prompt rate",
			  "smoothed_promptRate_pt_vs_eta_wz",
			  "", outDirSmooth, 1,1, false,false,false,1);

    } else {
      drawCorrelationPlot(fr_pt_eta_w, 
			  fr_pt_eta_w->GetXaxis()->GetTitle(),
			  fr_pt_eta_w->GetYaxis()->GetTitle(),
			  "prompt rate",
			  "smoothed_promptRate_pt_vs_eta_w",
			  "", outDirSmooth, 1,1, false,false,false,1);
      drawCorrelationPlot(fr_pt_eta_z, 
			  fr_pt_eta_z->GetXaxis()->GetTitle(),
			  fr_pt_eta_z->GetYaxis()->GetTitle(),
			  "prompt rate",
			  "smoothed_promptRate_pt_vs_eta_z",
			  "", outDirSmooth, 1,1, false,false,false,1);
    }
    if (showTopVV) {
      drawCorrelationPlot(fr_pt_eta_top_vv, 
			  fr_pt_eta_top_vv->GetXaxis()->GetTitle(),
			  fr_pt_eta_top_vv->GetYaxis()->GetTitle(),
			  "prompt rate",
			  "smoothed_promptRate_pt_vs_eta_top_vv",
			  "", outDirSmooth, 1,1, false,false,false,1);
    }

  }

  if (not noDrawQCD) 
    drawCorrelationPlot(fr_pt_eta_qcd, 
			fr_pt_eta_qcd->GetXaxis()->GetTitle(),
			fr_pt_eta_qcd->GetYaxis()->GetTitle(),
			"fake rate",
			"smoothed_fakeRate_pt_vs_eta_qcd",
			"", outDirSmooth, 1,1, false,false,false,1);


  cout << endl;
  cout << "Plotting TH2 with FR parameters" << endl;

  string relUncYaxisTitle = "0 offset : 1 slope";
  if (smoothPolinDegree > 1) relUncYaxisTitle += " : 2 concavity";  

  string outDirParam = outDir+"/paramValues/";
  createPlotDirAndCopyPhp(outDirParam);

  string suffixRange = (smoothPolinDegree > 1) ? "::-0.5,2.5" : "::-0.5,1.5";
  drawCorrelationPlot(frSmoothParameter_data, 
		      fr_pt_eta_data->GetYaxis()->GetTitle(), relUncYaxisTitle+suffixRange, "parameter value", 
		      "smoothed_fakeRate_pt_vs_eta_data_paramValue",
		      "", outDirParam, 1,1, false,false,false,1);
  drawCorrelationPlot(frSmoothParameter_data_subScaledUpEWKMC, 
		      fr_pt_eta_data->GetYaxis()->GetTitle(), relUncYaxisTitle+suffixRange, "parameter value", 
		      "smoothed_fakeRate_pt_vs_eta_data_subScaledUpEWKMC_paramValue",
		      "", outDirParam, 1,1, false,false,false,1);
  drawCorrelationPlot(frSmoothParameter_data_subScaledDownEWKMC, 
		      fr_pt_eta_data->GetYaxis()->GetTitle(), relUncYaxisTitle+suffixRange, "parameter value", 
		      "smoothed_fakeRate_pt_vs_eta_data_subScaledDownEWKMC_paramValue",
		      "", outDirParam, 1,1, false,false,false,1);
  drawCorrelationPlot(frSmoothParameter_ewk, 
		      fr_pt_eta_data->GetYaxis()->GetTitle(), relUncYaxisTitle+suffixRange, "parameter value", 
		      "smoothed_promptRate_pt_vs_eta_ewk_paramValue",
		      "", outDirParam, 1,1, false,false,false,1);


  TH1D* frSmoothParameter_data_slope = new TH1D("frSmoothParameter_data_slope","",NetaBins, etaBoundaries.data());
  TH1D* frSmoothParameter_data_subScaledDownEWKMC_slope = new TH1D("frSmoothParameter_data_subScaledDownEWKMC_slope","",NetaBins, etaBoundaries.data());
  TH1D* frSmoothParameter_data_subScaledUpEWKMC_slope = new TH1D("frSmoothParameter_data_subScaledUpEWKMC_slope","",NetaBins, etaBoundaries.data());
  TH1D* frSmoothParameter_ewk_slope = new TH1D("frSmoothParameter_data_subScaledUpEWKMC_slope","",NetaBins, etaBoundaries.data());
  fillTH1fromTH2bin(frSmoothParameter_data_slope, frSmoothParameter_data, false, 2);
  fillTH1fromTH2bin(frSmoothParameter_data_subScaledUpEWKMC_slope, frSmoothParameter_data_subScaledUpEWKMC, false, 2);
  fillTH1fromTH2bin(frSmoothParameter_data_subScaledDownEWKMC_slope, frSmoothParameter_data_subScaledDownEWKMC, false, 2);
  fillTH1fromTH2bin(frSmoothParameter_ewk_slope, frSmoothParameter_ewk, false, 2);

  drawSingleTH1(frSmoothParameter_data_slope,fr_pt_eta_data->GetYaxis()->GetTitle(),"Slope","smoothed_fakeRate_slope_vs_eta_data",
		outDirParam,"FR nominal",inputLuminosity,1,false,1);
  drawSingleTH1(frSmoothParameter_data_subScaledUpEWKMC_slope,fr_pt_eta_data->GetYaxis()->GetTitle(),"Slope","smoothed_fakeRate_slope_vs_eta_data_subScaledUpEWKMC",
		outDirParam,"FR (EWK +1#sigma)",inputLuminosity,1,false,1);
  drawSingleTH1(frSmoothParameter_data_subScaledDownEWKMC_slope,fr_pt_eta_data->GetYaxis()->GetTitle(),"Slope","smoothed_fakeRate_slope_vs_eta_data_subScaledDownEWKMC",
		outDirParam,"FR (EWK -1#sigma)",inputLuminosity,1,false,1);
  drawSingleTH1(frSmoothParameter_ewk_slope,fr_pt_eta_data->GetYaxis()->GetTitle(),"Slope","smoothed_fakeRate_slope_vs_eta_ewk",
		outDirParam,"PR (all EWK)",inputLuminosity,1,false,1);

  cout << endl;
  cout << "Plotting TH2 with relative uncertainty on FR parameters" << endl;


  string outDirUncertainty = outDir+"/paramUncertainty/";
  createPlotDirAndCopyPhp(outDirUncertainty);

  plotFRparamRelUncertainty(frSmoothParameter_data,outDirUncertainty,fr_pt_eta_data->GetYaxis()->GetTitle(),relUncYaxisTitle+suffixRange,"relative uncertainty", "smoothed_fakeRate_pt_vs_eta_data_relUnc");
  //plotFRparamRelUncertainty(frSmoothParameter_data_fitNarrowRange,outDirUncertainty,fr_pt_eta_data->GetYaxis()->GetTitle(),relUncYaxisTitle+suffixRange,"relative uncertainty", "smoothed_fakeRate_pt_vs_eta_data_fitNarrowRange_relUnc");
  plotFRparamRelUncertainty(frSmoothParameter_data_subScaledUpEWKMC,outDirUncertainty,fr_pt_eta_data->GetYaxis()->GetTitle(),relUncYaxisTitle+suffixRange,"relative uncertainty", "smoothed_fakeRate_pt_vs_eta_data_subScaledUpEWKMC_relUnc");
  plotFRparamRelUncertainty(frSmoothParameter_data_subScaledDownEWKMC,outDirUncertainty,fr_pt_eta_data->GetYaxis()->GetTitle(),relUncYaxisTitle+suffixRange,"relative uncertainty", "smoothed_fakeRate_pt_vs_eta_data_subScaledDownEWKMC_relUnc");
  plotFRparamRelUncertainty(frSmoothParameter_ewk,outDirUncertainty,fr_pt_eta_data->GetYaxis()->GetTitle(),relUncYaxisTitle+suffixRange,"relative uncertainty", "smoothed_promptRate_pt_vs_eta_ewk_relUnc");


  // parameters of linear fit
  cout << endl;
  cout << "Writing TH2 frSmoothParameter_* with linear fit parameters in file" << endl;
  frSmoothParameter_data->Write();
  //frSmoothParameter_data_fitNarrowRange->Write();
  frSmoothParameter_data_subScaledUpEWKMC->Write();
  frSmoothParameter_data_subScaledDownEWKMC->Write();
  if (not noDrawQCD) frSmoothParameter_qcd->Write();
  frSmoothParameter_ewk->Write();
  if (not showMergedEWK) {
    if (showMergedWZ) {
      frSmoothParameter_wz->Write();
    } else {
      frSmoothParameter_w->Write();
      frSmoothParameter_z->Write();
    }
    if (showTopVV) {
      frSmoothParameter_top_vv->Write();
    }
  }
  // fake or prompt rate points (no errors)
  cout << "Writing TH2 fr_pt_eta_* with smoothed fake or prompt rate in file" << endl;
  fr_pt_eta_data->Write();
  //fr_pt_eta_data_fitNarrowRange->Write();
  fr_pt_eta_data_subScaledUpEWKMC->Write();
  fr_pt_eta_data_subScaledDownEWKMC->Write();
  if (not noDrawQCD) fr_pt_eta_qcd->Write();
  fr_pt_eta_ewk->Write();
  if (not showMergedEWK) {
    if (showMergedWZ) {
      fr_pt_eta_wz->Write();     
    } else {
      fr_pt_eta_w->Write();
      fr_pt_eta_z->Write();
    }
    if (showTopVV) {
      fr_pt_eta_top_vv->Write();
    }
  }

  frSmoothFile->Close();


  cout << endl;
  cout << endl;
  cout << "Created file " << frSmoothFileName << endl;
  system(Form("cp %s %s",frSmoothFileName.c_str(),outDir.c_str()));
  cout << "File also copied in " << outDir << endl;
  cout << endl;


  delete frSmoothFile;

}
