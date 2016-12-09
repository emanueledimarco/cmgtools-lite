import ROOT

class MECalculator:
    def __init__(self,comTeV,hmass):
        self._MEMs = ROOT.MEMCalculatorsWrapper(comTeV,hmass)
        self.KDs = {}

    def PtEtaPhiM_4v(self,pt,eta,phi,m):
        tlv = ROOT.TLorentzVector()
        tlv.SetPtEtaPhiM(pt,eta,phi,m)
        return ROOT.TLorentzVector(tlv.X(),tlv.Y(),tlv.Z(),tlv.T())

    def fillMEs(self,higgsPt3v,vbfjets,otherjets=[]):
        
        self.hPt=higgsPt3v
        self.vbfjets=vbfjets
        self.otherjets=otherjets
        alljets = vbfjets + otherjets
        zJets = 0
        for j in alljets: zJets += (self.PtEtaPhiM_4v(j.pt,j.eta,j.phi,j.mass)).Z()
        self.longBoost = -1*zJets

        # build the dummy 4 leptons 
        lp4s = ROOT.std.vector(ROOT.TLorentzVector)()
        lp4s.push_back(self.PtEtaPhiM_4v(self.hPt.Pt(),0.0,self.hPt.Phi(),0)) # 1. HPT (MET)
        lp4s.push_back(ROOT.TLorentzVector(0,0,self.longBoost,abs(self.longBoost))) # 2. assumption of longitudinal Higgs boost recoiling against jets
        # dummy zero-momentum 2 leptons
        lp4s.push_back(self.PtEtaPhiM_4v(0.01,0.0,ROOT.TMath.Pi()-self.hPt.Phi(),0)) # 3. null, opposite to MET
        lp4s.push_back(ROOT.TLorentzVector(0,0,0.01,0.01)) # 4. null, in the longitudinal direction
        # dummy pdgIds
        ids  = [ 13     for l in range(4) ]
        
        # jets
        jp4s = ROOT.std.vector(ROOT.TLorentzVector)()
        for j in self.vbfjets:
            jp4s.push_back(self.PtEtaPhiM_4v(j.pt,j.eta,j.phi,0.0))
            
        # calc KDs
        for KD in self._MEMs.computeNew(lp4s[0],ids[0], lp4s[1],ids[1], lp4s[2],ids[2], lp4s[3],ids[3], jp4s):
            self.KDs[KD.first] = KD.second
            
        # calc mixed discriminant
        if len(self.vbfjets)==2:
            PgPq2 =  (1/self.vbfjets[0].qgl - 1 if self.vbfjets[0].qgl > 0 else 1) * (1/self.vbfjets[1].qgl - 1 if self.vbfjets[1].qgl > 0 else 1)
            self.KDs["PgPq2"] = PgPq2
            self.KDs["D_VBF2J"] = 1/(1 + (1./self.KDs["D_HJJ^VBF"] - 1.) * pow(PgPq2, 1./3)) if PgPq2 > 0 else -99

        
