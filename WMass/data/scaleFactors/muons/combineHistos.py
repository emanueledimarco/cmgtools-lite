import ROOT, json, copy, array

bins_eta = [-2.4,-2.3,-2.2,-2.1,-2.0,-1.7,-1.6,-1.5,-1.4,-1.2,-0.8,-0.5,-0.3,-0.2,0.0, 0.2, 0.3, 0.5, 0.8, 1.2, 1.4, 1.5, 1.6, 1.7, 2.0, 2.1, 2.2, 2.3, 2.4]
bins_pt  = [20, 25, 30, 40, 50, 60, 120]



basedir = '/eos/cms/store/group/phys_muon/fernanpe/Efficiencies_LegacyReReco2016_final/'


for sf in ['ID','ISO']:
    if sf =='ISO': 
        rootfile = 'TnP_MC_NUM_TightRelIso_DEN_MediumID_PAR_pt_eta.root'
        fitdir   = 'TightIso4_NUM_TightRelIso_DEN_MediumID_PAR_pt_eta'
    else: 
        rootfile = 'TnP_MC_NUM_MediumID_DEN_genTracks_PAR_pt_eta.root'
        fitdir   = 'Medium_noIP_NUM_MediumID_DEN_genTracks_PAR_pt_eta'


    outfile = ROOT.TFile('efficiencies'+sf+'.root','recreate')
    
    for t in ['data', 'mc']:
        tc = 'DATA' if t == 'data' else 'MC'
        for rr in ['BF', 'GH']:
        
            efficiencies = ROOT.TH2F('eff'+sf+'_'+t+'_'+rr, 'efficiencies '+sf+' '+t+' '+rr, len(bins_eta)-1, array.array('d',bins_eta), len(bins_pt)-1, array.array('d',bins_pt))
            
            rrl = 'BCDEF' if rr == 'BF' else 'GH'
            
            for part in [1,2,3]:
                print basedir+'/Efficiency{sf}_{rrl}_part{p}/{tc}_{t}id_{rrl}/{rf}'.format(p=part,rrl=rrl,t=t,tc=tc,sf=sf,rf=rootfile)
                infile = ROOT.TFile(basedir+'/Efficiency{sf}_{rrl}_part{p}/{tc}_{t}id_{rrl}/{rf}'.format(p=part,rrl=rrl,t=t,tc=tc,sf=sf,rf=rootfile),'read')
                infile.cd()
            
                offset = 1 if part == 1 else 10 if part == 2 else 20
                
                for ieta in range(10 if part == 2 else 9): 
                    for ipt in range(len(bins_pt)-1): 
                        #print 'part', part, 'ieta', ieta, 'ipt', ipt
                        _dir = 'tpTree/{fitdir}/'.format(fitdir=fitdir)
                        if sf == 'ISO': 
                            _dir += 'eta_bin{ieta}__pt_bin{ipt}__Medium_pass__vpvPlusExpo'.format(ieta=ieta,ipt=ipt)
                        else: 
                            _dir += 'eta_bin{ieta}__pt_bin{ipt}__vpvPlusCMS'              .format(ieta=ieta,ipt=ipt)
                            if ipt > 2: 
                                _dir += 'beta0p2'
                            
                        fr = infile.Get(_dir+'/fitresults')
                        val = fr.floatParsFinal().find('efficiency').getVal()
                        err = fr.floatParsFinal().find('efficiency').getError()
                        #print val, ' +- ', err
                        
                        #print 'at part', part, 'filling eta bin number', offset+ieta
                        efficiencies.SetBinContent(offset+ieta, ipt+1, val)
                        efficiencies.SetBinError  (offset+ieta, ipt+1, err)
                infile.Close()
            outfile.cd()
            efficiencies.Write()
    
    outfile.Close()





