import ROOT
import os, array
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from CMGTools.WMass.postprocessing.framework.datamodel import Collection
from CMGTools.WMass.postprocessing.framework.eventloop import Module
from PhysicsTools.HeppyCore.utils.deltar import deltaPhi
from math import *

class SimpleVBoson:
    def __init__(self,legs,pdgId=24):
        self.pdgId=pdgId
        self.legs = legs
        if len(legs)<2:
            print "ERROR: making a VBoson w/ < 2 legs!"
        self.pt1 = legs[0].Pt()
        self.pt2 = legs[1].Pt()
        self.dphi = self.legs[0].DeltaPhi(self.legs[1])        
        self.deta = self.legs[0].Eta()-self.legs[1].Eta()
        self.px1 = legs[0].Px(); self.py1 = legs[0].Py();
        self.px2 = legs[1].Px(); self.py2 = legs[1].Py();
    def pt(self):
        return (self.legs[0]+self.legs[1]).Pt()
    def phi(self):
        return (self.legs[0]+self.legs[1]).Phi()
    def y(self):
        return (self.legs[0]+self.legs[1]).Rapidity()
    def mt(self):
        return sqrt(2*self.pt1*self.pt2*(1-cos(self.dphi)))
    def ux(self):
        return (-self.px1-self.px2)
    def uy(self):
        return (-self.py1-self.py2)    
    def mll(self):
        return sqrt(2*self.pt1*self.pt2*(cosh(self.deta)-cos(self.dphi)))

class KinematicVars:
    def __init__(self,beamE=6500):
        self.beamE = beamE
    def CSFrame(self,dilepton):
        pMass = 0.938272
        sign = np.sign(dilepton.Z())
        proton1 = ROOT.TLorentzVector(0.,0.,sign*self.beamE,hypot(self.beamE,pMass));  proton2 = ROOT.TLorentzVector(0.,0.,-sign*self.beamE,hypot(self.beamE,pMass))
        proton1.Boost(-dilepton.BoostVector()); proton2.Boost(-dilepton.BoostVector())
        CSAxis = (proton1.Vect().Unit()-proton2.Vect().Unit()).Unit()
        yAxis = (proton1.Vect().Unit()).Cross((proton2.Vect().Unit()));
        yAxis = yAxis.Unit();
        xAxis = yAxis.Cross(CSAxis);
        xAxis = xAxis.Unit();
        return (xAxis,yAxis,CSAxis)
    def cosThetaCS(self,lplus,lminus):
        dilep = lplus + lminus
        boostedLep = ROOT.TLorentzVector(lminus)
        boostedLep.Boost(-dilep.BoostVector())
        csframe = self.CSFrame(dilep)
        return cos(boostedLep.Angle(csframe[2]))
    def cosTheta2D(self,w,lep):
        boostedLep = ROOT.TLorentzVector(lep)
        neww = ROOT.TLorentzVector()
        neww.SetPxPyPzE(w.Px(),w.Py(),0.,w.E())
        boostedLep.Boost(-neww.BoostVector())
        cost2d = (boostedLep.Px()*w.Px() + boostedLep.Py()*w.Py()) / (boostedLep.Pt()*w.Pt())
        return cost2d
    def cosThetaCM(self,lplus,lminus):
        dilep = lplus + lminus
        boostedLep = ROOT.TLorentzVector(lminus)
        boostedLep.Boost(-dilep.BoostVector())
        modw = sqrt(dilep.X()*dilep.X() + dilep.Y()*dilep.Y() + dilep.Z()*dilep.Z())
        modm = sqrt(boostedLep.X()*boostedLep.X() + boostedLep.Y()*boostedLep.Y() + boostedLep.Z()*boostedLep.Z())
        cos = (dilep.X()*boostedLep.X() + dilep.Y()*boostedLep.Y() + dilep.Z()*boostedLep.Z())/modw/modm
        return cos
    def phiCS(self,lplus,lminus):
        dilep = lplus + lminus
        boostedLep = ROOT.TLorentzVector(lminus)
        boostedLep.Boost(-dilep.BoostVector())
        csframe = self.CSFrame(dilep)
        phi = atan2((boostedLep.Vect()*csframe[1]),(boostedLep.Vect()*csframe[0]))
        if(phi<0): return phi + 2*ROOT.TMath.Pi()
        else: return phi

class GenQEDJetProducer(Module):
    def __init__(self,deltaR,beamEn=7000.):
        self.beamEn=beamEn
        self.deltaR = deltaR
        self.vars = ("pt","eta","phi","mass","pdgId")
        self.genwvars = ("charge","pt","mass","y","costcs","phics","decayId")
        ## if "genQEDJetHelper_cc.so" not in ROOT.gSystem.GetLibraries():
        ##     print "Load C++ Worker"
        ##     ROOT.gROOT.ProcessLine(".L %s/src/CMGTools/WMass/python/postprocessing/helpers/genQEDJetHelper.cc+" % os.environ['CMSSW_BASE'])
        ## else:
        ##     print "genQEDJetHelper_cc.so found in ROOT libraries"
        ## self._worker = ROOT.GenQEDJetHelper(deltaR)
        self.pdfWeightOffset = 9 #index of first mc replica weight (careful, this should not be the nominal weight, which is repeated in some mc samples).  The majority of run2 LO madgraph_aMC@NLO samples with 5fs matrix element and pdf would use index 10, corresponding to pdf set 263001, the first alternate mc replica for the nominal pdf set 263000 used for these samples
        self.nMCReplicasWeights = 100 #number of input weights (100 for NNPDF 3.0)
        self.nHessianWeights = 60 #number of output weights
        self.massWeights = range(80300, 80505, 5) #masses in MeV
        if "PDFWeightsHelper_cc.so" not in ROOT.gSystem.GetLibraries():
            ROOT.gROOT.ProcessLine(".include /cvmfs/cms.cern.ch/slc6_amd64_gcc530/external/eigen/3.2.2/include")
            ROOT.gROOT.ProcessLine(".L %s/src/CMGTools/WMass/python/postprocessing/helpers/PDFWeightsHelper.cc+" % os.environ['CMSSW_BASE'])
        mc2hessianCSV = "%s/src/CMGTools/WMass/python/postprocessing/data/gen/NNPDF30_nlo_as_0118_hessian_60.csv" % os.environ['CMSSW_BASE']
        self._pdfHelper = ROOT.PDFWeightsHelper()
        self._pdfHelper.Init(self.nMCReplicasWeights,self.nHessianWeights,mc2hessianCSV)
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.initReaders(inputTree) # initReaders must be called in beginFile
        self.out = wrappedOutputTree
        self.out.branch("weightGen", "F")
        self.out.branch("gammaMaxDR", "F")
        self.out.branch("gammaRelPtOutside", "F")
        self.out.branch("partonId1", "I")
        self.out.branch("partonId2", "I")
        self.out.branch("nGenLepDressed", "I")
        self.out.branch("nGenPreFSR", "I")
        self.out.branch("nGenPromptNu", "I")
        for V in self.vars:
            self.out.branch("GenLepDressed_"+V, "F", lenVar="nGenLepDressed")
            self.out.branch("GenLepPreFSR_"+V, "F", lenVar="nGenLepPreFSR")
            self.out.branch("GenPromptNu_"+V, "F", lenVar="nGenPromptNu")
        for V in self.genwvars:
            self.out.branch("genw_"+V, "F")
            self.out.branch("prefsrw_"+V, "F")
        for N in range(1,self.nHessianWeights+1):
            self.out.branch("hessWgt"+str(N), "H")
        for scale in ['muR','muF',"muRmuF","alphaS"]:
            for idir in ['Up','Dn']:
                self.out.branch("qcd_{scale}{idir}".format(scale=scale,idir=idir), "H")
        for imass in self.massWeights:
            self.out.branch("mass_{mass}".format(mass=imass), "F")
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def initReaders(self,tree): # this function gets the pointers to Value and ArrayReaders and sets them in the C++ worker class
        ## marc try:
        ## marc     self.nGenPart = tree.valueReader("nGenPart")
        ## marc     for B in ("pt","eta","phi","mass","pdgId","isPromptHard","motherId","status") : setattr(self,"GenPart_"+B, tree.arrayReader("GenPart_"+B))
        ## marc     self._worker.setGenParticles(self.nGenPart,self.GenPart_pt,self.GenPart_eta,self.GenPart_phi,self.GenPart_mass,self.GenPart_pdgId,self.GenPart_isPromptHard,self.GenPart_motherId,self.GenPart_status)
        ## marc     #self.nLHEweight = tree.valueReader("nLHEweight")
        ## marc     #self.LHEweight_wgt = tree.arrayReader("LHEweight_wgt")
        ## marc except:
        ## marc     print '[genFriendProducer][Warning] Unable to attach to generator-level particles (data only?). No info will be produced'
        self._ttreereaderversion = tree._ttreereaderversion # self._ttreereaderversion must be set AFTER all calls to tree.valueReader or tree.arrayReader

    def mcRep2Hess(self,lheweights):
        nomlhew = lheweights[0]
        inPdfW = np.array(lheweights[self.pdfWeightOffset:self.pdfWeightOffset+self.nMCReplicasWeights],dtype=float)
        outPdfW = np.array([0 for i in xrange(self.nHessianWeights)],dtype=float)
        self._pdfHelper.DoMC2Hessian(nomlhew,inPdfW,outPdfW)
        pdfeigweights = [wgt/nomlhew for wgt in outPdfW.tolist()]
        return pdfeigweights

    def qcdScaleWgtIdx(self,mur="0",muf="0"):
        # mapping from https://indico.cern.ch/event/459797/contribution/2/attachments/1181555/1800214/mcaod-Feb15-2016.pdf
        idx_map={}
        idx_map[("0","0")]   = 0
        idx_map[("0","Up")]  = 1
        idx_map[("0","Dn")]  = 2
        idx_map[("Up","0")]  = 3
        idx_map[("Up","Up")] = 4
        idx_map[("Up","Dn")] = 5
        idx_map[("Dn","0")]  = 6
        idx_map[("Dn","Up")] = 7
        idx_map[("Dn","Dn")] = 8
        if (mur,muf) not in idx_map: raise Exception('Scale variation muR={mur},muF={muf}'.format(mur=mur,muf=muf))
        return idx_map[(mur,muf)]

    def bwWeight(self,genMass,imass):
        # default mass calculated from MG5 inputs
        # width calculated with MG5_aMC_v2_6_3_2 loop_sm-ckm_no_b_mass for w+ > all all --> 2.05 +/- 7.65e-06 (GeV)
        (m0,gamma) = (80419.,2050.0) # MeV
        s_hat = pow(genMass,2)
        return (pow(s_hat - m0*m0,2) + pow(gamma*m0,2)) / (pow(s_hat - imass*imass,2) + pow(gamma*imass,2))

    def getNeutrino(self):
        nus = []
        for p in self.genParts:
            if abs(p.pdgId) in [12, 14, 16] : ##and p.isPromptFinalState > 0: ## requiring isPromptFinalState results in 12% of events without neutrino
                nus.append(p)

        ##nus = sorted(nus, key = lambda x: x.pt)
        nus.sort(key = lambda x: x.pt, reverse=True)

        if len(nus) < 1:
            return 0, 0

        nu = nus[0]
        nuvec = ROOT.TLorentzVector()
        nuvec.SetPtEtaPhiM(nu.pt, nu.eta, nu.phi, nu.mass if nu.mass > 0. else 0.)

        return nuvec, nu.pdgId

    def getDressedLeptons(self, strictlyPrompt=True, cone=0.1):

        leptons = []
        for p in self.genParts:
            if not abs(p.pdgId) in [11,13,15] : continue
            if strictlyPrompt:
                if abs(p.pdgId) in [11, 13] and not p.isPromptFinalState : continue
                if abs(p.pdgId) == 15       and not p.isPromptDecayed : continue
            lepton = ROOT.TLorentzVector()
            lepton.SetPtEtaPhiM(p.pt, p.eta, p.phi, p.mass if p.mass >= 0. else 0.)
            leptons.append( [lepton, p.pdgId] )

        #leptons = sorted(leptons, key = lambda x: x[0].Pt() )
        leptons.sort(key = lambda x: x[0].Pt(), reverse=True )

        if len(leptons) ==0: 
            return leptons
            ##print 'ERROR: DID NOT FIND A LEPTON FOR DRESSING !!!!!'

        for p in self.genParts:
            if not abs(p.pdgId)==22: continue
            if strictlyPrompt and not p.isPromptFinalState: continue
            tmp_photon = ROOT.TLorentzVector()
            tmp_photon.SetPtEtaPhiM(p.pt, p.eta, p.phi, p.mass if p.mass >= 0. else 0.)

            #first match in cone
            for il in xrange(0,len(leptons)):
                if leptons[il][0].DeltaR(tmp_photon) > cone: continue
                leptons[il][0] = leptons[il][0]+tmp_photon
                break

        return leptons
    
    def getPreFSRLepton(self):
        
        lepInds = []
        for ip,p in enumerate(self.genParts):
            if abs(p.pdgId) in [11, 13] and p.fromHardProcessFinalState:
                lepInds.append( (p, ip) )
            if abs(p.pdgId) == 15       and p.fromHardProcessDecayed:
                lepInds.append( (p, ip) )

        if len(lepInds) < 1:
            return 0, 0

        lepInds.sort( key = lambda x: x[0].pt, reverse=True) ## sort by pT

        lep = lepInds[0][0]
        ind = lepInds[0][1]

        ## return hardest lepton by default
        finallep = lep

        ## see if there's a mother with same pdgId and lastBeforeFSR
        while (self.genParts[int(lep.motherIndex)].pdgId == lep.pdgId):
            if self.genParts[int(lep.motherIndex)].lastBeforeFSR:
                finallep = self.genParts[int(lep.motherIndex)]
                break
            ind = int(lep.motherIndex)
            lep = self.genParts[ind]
            if lep.motherIndex < 0:
                break

        lepton = ROOT.TLorentzVector()
        lepton.SetPtEtaPhiM(finallep.pt, finallep.eta, finallep.phi, finallep.mass)

        return lepton, finallep.pdgId
            
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #nothing to do if this is data
        if event.isData: return True

        try:
            lhe_wgts      = Collection(event, 'LHEweight')
        except:
            lhe_wgts = 0
        self.genParts = Collection(event, 'GenPart')

        #this is a stupid check if variables are present. do this on the first gen particle
        makeWs = False
        for ip,p in enumerate(self.genParts):
            if ip:
                break
            if hasattr(p, 'isPromptFinalState'):
                makeWs = True
            

        if event._tree._ttreereaderversion > self._ttreereaderversion: # do this check at every event, as other modules might have read further branches
            self.initReaders(event._tree)

        ## check if the proper Ws can be made
        dressedLeptonCollection             = self.getDressedLeptons(strictlyPrompt=makeWs)
        dressedLepton, dressedLeptonPdgId   = dressedLeptonCollection[0] if len(dressedLeptonCollection) else (0,0)
        (preFSRLepton , preFSRLeptonPdgId ) = self.getPreFSRLepton()     if makeWs else (0,0)
        (neutrino     , neutrinoPdgId     ) = self.getNeutrino()         if makeWs else (0,0)

        if hasattr(event,"genWeight"):
            self.out.fillBranch("weightGen", getattr(event, "genWeight"))
            self.out.fillBranch("partonId1", getattr(event, "id1") if hasattr(event, 'id1') else -999)
            self.out.fillBranch("partonId2", getattr(event, "id2") if hasattr(event, 'id2') else -999)
        else:
            self.out.fillBranch("weightGen", -999.)
            self.out.fillBranch("partonId1", -999 )
            self.out.fillBranch("partonId2", -999 )

        #always produce the dressed lepton collection
        if len(dressedLeptonCollection)>0:
            retL={}
            leptonsToTake = range(0,1 if makeWs else len(dressedLeptonCollection))
            retL["pt"]    = [dressedLeptonCollection[i][0].Pt() for i in leptonsToTake ]
            retL["eta"]   = [dressedLeptonCollection[i][0].Eta() for i in leptonsToTake ]
            retL["phi"]   = [dressedLeptonCollection[i][0].Phi() for i in leptonsToTake ]
            retL["mass"]  = [dressedLeptonCollection[i][0].M() if dressedLeptonCollection[i][0].M() >= 0. else 0. for i in leptonsToTake]
            retL["pdgId"] = [dressedLeptonCollection[i][1] for i in leptonsToTake ]
            self.out.fillBranch("nGenLepDressed", leptonsToTake[-1])
            for V in self.vars:
                self.out.fillBranch("GenLepDressed_"+V, retL[V])

        #W-specific
        if neutrino:
            retN={}
            retN["pt"]    = [neutrino.Pt()  ]
            retN["eta"]   = [neutrino.Eta() ]
            retN["phi"]   = [neutrino.Phi() ]
            retN["mass"]  = [neutrino.M() if neutrino.M() >= 0. else 0.  ] ## weird protection... also already checked. but better safe than sorry
            retN["pdgId"] = [neutrinoPdgId  ]
            self.out.fillBranch("nGenPromptNu", 1)
            for V in self.vars:
                self.out.fillBranch("GenPromptNu_"+V, retN[V])
            #self.out.fillBranch("GenPromptNu_pdgId", [pdgId for pdgId in nuPdgIds])            

            if dressedLepton:
                genw = dressedLepton + neutrino
                self.out.fillBranch("genw_charge" , float(-1*np.sign(dressedLeptonPdgId)))
                self.out.fillBranch("genw_pt"     , genw.Pt())
                self.out.fillBranch("genw_y"      , genw.Rapidity())
                self.out.fillBranch("genw_mass"   , genw.M())
                kv = KinematicVars(self.beamEn)
                # convention for phiCS: use l- direction for W-, use neutrino for W+
                (lplus,lminus) = (neutrino,dressedLepton) if dressedLeptonPdgId<0 else (dressedLepton,neutrino)
                self.out.fillBranch("genw_costcs" , kv.cosThetaCS(lplus, lminus))
                self.out.fillBranch("genw_phics"  , kv.phiCS     (lplus, lminus))
                self.out.fillBranch("genw_decayId", abs(neutrinoPdgId))
                for imass in self.massWeights:
                    self.out.fillBranch("mass_{mass}".format(mass=imass), self.bwWeight(genMass=genw.M()*1000,imass=imass))

            if preFSRLepton:
                retP={}
                retP["pt"]    = [preFSRLepton.Pt()  ]
                retP["eta"]   = [preFSRLepton.Eta() ]
                retP["phi"]   = [preFSRLepton.Phi() ]
                retP["mass"]  = [preFSRLepton.M()   if preFSRLepton.M() >= 0. else 0.]
                retP["pdgId"] = [preFSRLeptonPdgId  ]
                self.out.fillBranch("nGenLepPreFSR", 1)
                for V in self.vars:
                    self.out.fillBranch("GenLepPreFSR_"+V, retP[V])

                prefsrw = preFSRLepton + neutrino
                self.out.fillBranch("prefsrw_charge" , float(-1*np.sign(preFSRLeptonPdgId)))
                self.out.fillBranch("prefsrw_pt"     , prefsrw.Pt())
                self.out.fillBranch("prefsrw_y"      , prefsrw.Rapidity())
                self.out.fillBranch("prefsrw_mass"   , prefsrw.M())
                kv = KinematicVars(self.beamEn)
                # convention for phiCS: use l- direction for W-, use neutrino for W+
                (lplus,lminus) = (neutrino,preFSRLepton) if preFSRLeptonPdgId<0 else (preFSRLepton,neutrino)
                self.out.fillBranch("prefsrw_costcs" , kv.cosThetaCS(lplus, lminus))
                self.out.fillBranch("prefsrw_phics"  , kv.phiCS     (lplus, lminus))
                self.out.fillBranch("prefsrw_decayId", abs(neutrinoPdgId))
                for imass in self.massWeights:
                    self.out.fillBranch("mass_{mass}".format(mass=imass), self.bwWeight(genMass=prefsrw.M()*1000,imass=imass))

            ## remove these variables to save space
            #self.out.fillBranch("genw_mt"   , sqrt(2*lplus.Pt()*lminus.Pt()*(1.-cos(deltaPhi(lplus.Phi(),lminus.Phi())) )))
            #self.out.fillBranch("genw_eta",genw.Eta())
            #self.out.fillBranch("genw_phi",genw.Phi())
            #self.out.fillBranch("genw_costcm",kv.cosThetaCM(lplus,lminus))
            #self.out.fillBranch("genw_cost2d",kv.cosTheta2D(genw,dressedLeptons[0]))
        else: ## no neutrino found!
            ##if not len(dressedLeptons): 
            ##    print '================================'
            ##    print 'no dressed leptons found!'
            ##    print 'no dressed leptons fround :lumi:evt: {a}:{b}:{c}'.format(a=getattr(event, "run"),b=getattr(event, "lumi"),c=getattr(event, "evt"))
            ##else:
            ##    print '================================'
            ##    print 'no neutrinos found, in run:lumi:evt: {a}:{b}:{c}'.format(a=getattr(event, "run"),b=getattr(event, "lumi"),c=getattr(event, "evt"))
            for V in self.genwvars:
                self.out.fillBranch("genw_"+V   , -999)
                self.out.fillBranch("prefsrw_"+V, -999)
            for imass in self.massWeights:
                self.out.fillBranch("mass_{mass}".format(mass=imass), 1.)

        if lhe_wgts:
            lheweights = [w.wgt for w in lhe_wgts]
            # not there anymore lhewgtIDs  = [w.id  for w in lhe_wgts]
            # not there anymore if not lhewgtIDs[self.pdfWeightOffset]%10 ==1:
                # not there anymore print 'ERROR/WARNING: the LHE weight with offset {n} does not seem to be the first replica!!!!'.format(n=self.pdfWeightOffset)
            hessWgt = self.mcRep2Hess(lheweights) ## give all the lhe weights. the 0th entry is the nominal one
            for N in range(1,self.nHessianWeights+1):
                self.out.fillBranch("hessWgt"+str(N), hessWgt[N-1])
            qcd0Wgt=lheweights[self.qcdScaleWgtIdx()]
            for ii,idir in enumerate(['Up','Dn']):
                self.out.fillBranch("qcd_muR{idir}"   .format(idir=idir), lheweights[self.qcdScaleWgtIdx(mur=idir)]/qcd0Wgt)
                self.out.fillBranch("qcd_muF{idir}"   .format(idir=idir), lheweights[self.qcdScaleWgtIdx(muf=idir)]/qcd0Wgt)
                self.out.fillBranch("qcd_muRmuF{idir}".format(idir=idir), lheweights[self.qcdScaleWgtIdx(mur=idir,muf=idir)]/qcd0Wgt) # only correlated variations are physical
                self.out.fillBranch("qcd_alphaS{idir}".format(idir=idir), lheweights[-1-ii]/lheweights[0]) # alphaS is at the end of the pdf variations. 0.119 is last, 0.117 next-to-last

        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

genQEDJets14TeV = lambda : GenQEDJetProducer(deltaR=0.1,beamEn=7000.)
genQEDJets = lambda : GenQEDJetProducer(deltaR=0.1,beamEn=6500.)

