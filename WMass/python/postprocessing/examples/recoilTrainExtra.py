import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True
from math import *

from CMGTools.WMass.postprocessing.framework.datamodel import Collection,Object
from CMGTools.WMass.postprocessing.framework.eventloop import Module
from CMGTools.WMass.postprocessing.examples.genFriendProducer import SimpleVBoson
from PhysicsTools.HeppyCore.utils.deltar import deltaR,deltaPhi
     
class RecoilTrainExtraProducer(Module):
    """
    Analyzes the event recoil and derives the corrections in pt and phi to bring the estimators to the true vector boson recoil.
    """
    def __init__(self):
        self.llMassWindow=(91.,15.)
        self.baseRecoil='tkmet'

    def beginJob(self):
        """actions taken start of the job"""
        pass

    def endJob(self):
        """actions taken end of the job"""
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        """actions taken at the start of the file"""

        #start by calling init readers
        self.initReaders(inputTree)

        #define output
        self.out = wrappedOutputTree    
        self.vars=['isGood','isGenW','isGenZ','isW','isZ','visgenpt','visgenphi','vispt','visphi','lne1','e2']
        for v in self.vars:
            self.out.branch(v, 'F')

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        """actions taken at the end of the file"""
        pass

    def initReaders(self,tree): # this function gets the pointers to Value and ArrayReaders and sets them in the C++ worker class                                 
        try:
            self.nGenPart = tree.valueReader("nGenPart")
            for var in ["pt","eta","phi","mass","pdgId","status"] : 
                setattr(self,"GenPart_"+var, tree.arrayReader("GenPart_"+var))
        except:
            print '[eventRecoilAnalyzer][Warning] Unable to attach to generator-level particles, only reco info will be made available'
        self._ttreereaderversion = tree._ttreereaderversion

    def getParticleLevelVectorBoson(self,event):

        """computes the MC truth for this event"""

        #nothing to do for data :)
        if event.isData : return None,None

        #dressed leptons
        dressedLepIds=[]
        dressedLeps=[]            
        for i in xrange(0,self.out._branches["nGenLepDressed"].buff[0]):
            pt=self.out._branches["GenLepDressed_pt"].buff[i]
            eta=self.out._branches["GenLepDressed_eta"].buff[i]
            if pt<20: continue
            if abs(eta)>2.5 : continue
            dressedLeps.append( ROOT.TLorentzVector(0,0,0,0) )
            dressedLeps[-1].SetPtEtaPhiM( pt,
                                          eta,
                                          self.out._branches["GenLepDressed_phi"].buff[i],
                                          self.out._branches["GenLepDressed_mass"].buff[i] )
            dressedLepIds.append( self.out._branches["GenLepDressed_pdgId"].buff[i] )

        #neutrino sum
        nuSum=ROOT.TLorentzVector(0,0,0,0)
        ngenNu = self.out._branches["nGenPromptNu"].buff[0]
        for i in xrange(0,ngenNu):
            p4=ROOT.TLorentzVector(0,0,0,0)
            p4.SetPtEtaPhiM( self.out._branches["GenPromptNu_pt"].buff[i],
                             self.out._branches["GenPromptNu_eta"].buff[i],
                             self.out._branches["GenPromptNu_phi"].buff[i],
                             self.out._branches["GenPromptNu_mass"].buff[i] )
            nuSum+=p4
        
        #build the boson
        if len(dressedLeps)==0: return None
        V=SimpleVBoson(legs=[dressedLeps[0],nuSum],pdgId=24)
        try:
            candZ=SimpleVBoson(legs=[dressedLeps[0],dressedLeps[1]],pdgId=23)
            if abs(dressedLepIds[0])==abs(dressedLepIds[1]):
                if abs(candZ.mll()-self.llMassWindow[0])<self.llMassWindow[1] :
                    V=candZ
        except:
            pass
        return V

    def getRecoLevelVectorBoson(self,event):

        """tries to reconstruct a W or a Z from the selected leptons"""
        
        lepColl = Collection(event, "LepGood")       
        if len(lepColl)==0: return None
        
        nuSum=ROOT.TLorentzVector(0,0,0,0)
        V=SimpleVBoson(legs=[lepColl[0].p4(),nuSum],pdgId=24)

        #apply trigger+offline selection cuts
        #FIXME: for now it's bound to muon final states
        passTrigger=True
        if event.HLT_BIT_HLT_IsoMu24_v==0 and event.HLT_BIT_HLT_IsoTkMu24_v==0: 
            passTrigger=False
        passKin=True 
        if lepColl[0].pt<25 or abs(lepColl[0].eta)>2.5:
            passKin=False
        passId = True 
        if lepColl[0].tightId==0 or lepColl[0].relIso03>0.05:
            passId=False
            
        #check if a Z can be constructed instead
        try:
            candZ=SimpleVBoson(legs=[lepColl[0].p4(),lepColl[1].p4()],pdgId=23)
            if abs(lepColl[0].pdgId)==abs(lepColl[1].pdgId):
                if abs(candZ.mll()-self.llMassWindow[0])<self.llMassWindow[1] :
                    V=candZ

                    #apply trigger+offline selection cuts
                    #FIXME: for now it's bound to muon final states
                    if lepColl[1].pt<20 or abs(lepColl[1].eta)>2.5:
                        passKin=False
                    if lepColl[1].tightId==0 or lepColl[1].relIso03>0.05:
                        passId=False                    
        except:
            pass

        #if not passing the cuts return None
        passSel=True if (passTrigger and passKin and passId) else False
        if not passSel: return None

        return V

    
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        if event._tree._ttreereaderversion > self._ttreereaderversion:
            self.initReaders(event._tree)        
        
        isGood=True

        hpt  = getattr(event,'h{0}_pt'.format(self.baseRecoil))
        hphi = getattr(event,'h{0}_phi'.format(self.baseRecoil))
        
        #MC truth
        gen_V=self.getParticleLevelVectorBoson(event)
        if gen_V:
            self.out.fillBranch('isGenW',1. if gen_V.pdgId==24 else 0.)
            self.out.fillBranch('isGenZ',1. if gen_V.pdgId==23 else 0.)

            #regression targets
            pt,phi=gen_V.pt(),gen_V.legs[0].Phi()
            if gen_V.pdgId==24 : phi=gen_V.phi()
            self.out.fillBranch('visgenpt', pt)
            self.out.fillBranch('visgenphi',phi)            
            self.out.fillBranch('lne1', log(gen_V.pt()/(hpt+1e-3)))
            self.out.fillBranch('e2',   ROOT.TVector2.Phi_mpi_pi(phi-hphi))
        else:
            self.out.fillBranch('isGenW',   0.)
            self.out.fillBranch('isGenZ',   0.)
            self.out.fillBranch('visgenpt', 0.)
            self.out.fillBranch('visgenphi',0.)            
            self.out.fillBranch('lne1',     0.)
            self.out.fillBranch('e2',       0.)
            isGood=False

        #selected leptons at reco level
        rec_V=self.getRecoLevelVectorBoson(event)
        if rec_V:
            self.out.fillBranch('isW',1. if rec_V.pdgId==24 else 0.)
            self.out.fillBranch('isZ',1. if rec_V.pdgId==23 else 0.)
            self.out.fillBranch('vispt',rec_V.pt())
            self.out.fillBranch('visphi',rec_V.legs[0].Phi() if rec_V.pdgId==24 else rec_V.phi())
        else:
            self.out.fillBranch('isW',0.)
            self.out.fillBranch('isZ',0.)
            self.out.fillBranch('vispt',0.)
            self.out.fillBranch('visphi',0.)
            isGood=False

        self.out.fillBranch('isGood',1. if isGood else 0.)
        
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
recoilTrainExtra = lambda : RecoilTrainExtraProducer()
