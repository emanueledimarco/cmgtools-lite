import ROOT


infile = 'wmass_mu/frAndPr_fit_mu_2018-09-19.root'
f = ROOT.TFile(infile,'read')

outfile = ROOT.TFile(infile.replace('.root','')+'_finerETA.root', 'recreate')

for rate in ['fakerates', 'promptrates']:

    f.cd()

    h_offsetSlope = f.Get(rate+'_smoothed_data')
    
    nbinsx = h_offsetSlope.GetNbinsX()
    xmin = h_offsetSlope.GetXaxis().GetXmin()
    xmax = h_offsetSlope.GetXaxis().GetXmax()
    nbinsy = h_offsetSlope.GetNbinsY()
    
    ROOT.gStyle.SetOptStat(0)
    
    
    h_offsetSlope_finer = ROOT.TH2D(h_offsetSlope.GetName()+'_interpolated', h_offsetSlope.GetName()+'_interpolated', nbinsx*3, xmin, xmax, 2, 0, 1)
    
    for iy in range(1,nbinsy+1):
        for ix_orig, ix_new in enumerate(range(2,nbinsx*3+1,3)): ## hope that works...
    
            thisbincon = h_offsetSlope.GetBinContent(ix_orig+1, iy)
            thisbinerr = h_offsetSlope.GetBinError  (ix_orig+1, iy)
    
            nextbincon = h_offsetSlope.GetBinContent(ix_orig+2, iy)
            nextbinerr = h_offsetSlope.GetBinError  (ix_orig+2, iy)
    
            prevbincon = h_offsetSlope.GetBinContent(ix_orig  , iy)
            prevbinerr = h_offsetSlope.GetBinError  (ix_orig  , iy)
    
            avgcon_right = (thisbincon + nextbincon) / 2.
            avgerr_right = (thisbinerr + nextbinerr) / 2.
    
            avgcon_left  = (thisbincon + prevbincon) / 2.
            avgerr_left  = (thisbinerr + prevbinerr) / 2.
    
            h_offsetSlope_finer.SetBinContent(ix_new, iy, thisbincon)
            h_offsetSlope_finer.SetBinError  (ix_new, iy, thisbinerr)
    
            h_offsetSlope_finer.SetBinContent(ix_new-1, iy, avgcon_left )
            h_offsetSlope_finer.SetBinError  (ix_new-1, iy, avgerr_left )
    
            h_offsetSlope_finer.SetBinContent(ix_new+1, iy, avgcon_right)
            h_offsetSlope_finer.SetBinError  (ix_new+1, iy, avgerr_right)
    
            if ix_orig == 0:
                h_offsetSlope_finer.SetBinContent(ix_new-1, iy, thisbincon)
                h_offsetSlope_finer.SetBinError  (ix_new-1, iy, thisbinerr)
            if ix_orig == nbinsx-1:
                h_offsetSlope_finer.SetBinContent(ix_new+1, iy, thisbincon)
                h_offsetSlope_finer.SetBinError  (ix_new+1, iy, thisbinerr)
                
    if 'fake' in rate:
        h_offsetSlope      .GetZaxis().SetRangeUser(0., 0.7)
        h_offsetSlope_finer.GetZaxis().SetRangeUser(0., 0.7)
    else:
        h_offsetSlope      .GetZaxis().SetRangeUser(0., 1.0)
        h_offsetSlope_finer.GetZaxis().SetRangeUser(0., 1.0)

    outfile.cd()
    h_offsetSlope      .Write()
    h_offsetSlope_finer.Write()

outfile.Close()
