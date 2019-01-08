from PhysicsTools.Heppy.analyzers.core.AutoFillTreeProducer  import * 
import copy
from CMGTools.TTHAnalysis.analyzers.ntupleTypes import *
from CMGTools.WMass.analyzers.ntupleTypes import *

wmass_globalVariables = [

            NTupleVariable("Flag_badMuonMoriond2017",  lambda ev: ev.badMuonMoriond2017, int, help="bad muon found in event (Moriond 2017 filter)?"),
            NTupleVariable("Flag_badCloneMuonMoriond2017",  lambda ev: ev.badCloneMuonMoriond2017, int, help="clone muon found in event (Moriond 2017 filter)?"),
            NTupleVariable("badCloneMuonMoriond2017_maxPt",  lambda ev: max(mu.pt() for mu in ev.badCloneMuonMoriond2017_badMuons) if not ev.badCloneMuonMoriond2017 else 0, help="max pt of any clone muon found in event (Moriond 2017 filter)"),
            NTupleVariable("badNotCloneMuonMoriond2017_maxPt",  lambda ev: max((mu.pt() if mu not in ev.badCloneMuonMoriond2017_badMuons else 0) for mu in ev.badMuonMoriond2017_badMuons) if not ev.badMuonMoriond2017 else 0, help="max pt of any bad non-clone muon found in event (Moriond 2017 filter)"),


            NTupleVariable("rho",  lambda ev: ev.rho, float, help="kt6PFJets rho"),
            NTupleVariable("rhoCN",  lambda ev: ev.rhoCN, float, help="fixed grid rho central neutral"),
            NTupleVariable("nVert",  lambda ev: len(ev.goodVertices), int, help="Number of good vertices"), 
            ## NTupleVariable("nTrueInt",  lambda ev: ev.nTrueInteractions, mcOnly=True, int, help="Number of true interaction from MC"), 

            ## ------- lheHT, needed for merging HT binned samples 
            NTupleVariable("lheHT", lambda ev : getattr(ev,"lheHT",-999), mcOnly=True, help="H_{T} computed from quarks and gluons in Heppy LHEAnalyzer"),
            NTupleVariable("lheHTIncoming", lambda ev : getattr(ev,"lheHTIncoming",-999), mcOnly=True, help="H_{T} computed from quarks and gluons in Heppy LHEAnalyzer (only LHE status<0 as mothers)"),

            ##--------------------------------------------------            
            NTupleVariable("mZ1", lambda ev : ev.bestZ1[0], help="Best m(ll) SF/OS"),

            ##--------------------------------------------------
            NTupleVariable("puppimet_sumEt",       lambda ev : getattr(ev,'met_sumetpuppi'),       help="Puppi Sum E_{T}"),
            NTupleVariable("met_sumEt",            lambda ev : getattr(ev,'met_sumet'),            help="Puppi Sum E_{T}"),

]

wmass_globalObjects = {
    ##--------------------------------------------------
    "tkGenMet"     :   NTupleObject("tkGenMet",       fourVectorType,  mcOnly=True, help="Gen charged E_{T}^{miss} eta<2.4"),
    "tkGenMetInc"  :   NTupleObject("tkGenMetInc",    fourVectorType,  mcOnly=True, help="Gen charged E_{T}^{miss} eta<5"),
    "met"          :   NTupleObject("met",            fourVectorType, help="PF E_{T}^{miss}, after type 1 corrections"),
    "metpuppi"     :   NTupleObject("puppimet",       fourVectorType, help="Puppi E_{T}^{miss}"),
}

##------------------------------------------  
## PDFs
##------------------------------------------  

pdfsVariables = [
        NTupleVariable("x1", lambda ev: ev.pdf_x1, mcOnly=True, help="fraction of proton momentum carried by the first parton"),
        NTupleVariable("x2", lambda ev: ev.pdf_x2, mcOnly=True, help="fraction of proton momentum carried by the second parton"),
        NTupleVariable("id1", lambda ev: ev.pdf_id1, int, mcOnly=True, help="id of the first parton in the proton"),
        NTupleVariable("id2", lambda ev: ev.pdf_id2, int, mcOnly=True, help="id of the second parton in the proton"),
        ]

wmass_collections = {
            "selectedLeptons" : NTupleCollection("LepGood",  leptonTypeWMass, 8, help="Leptons after the preselection"),
            #"otherLeptons"    : NTupleCollection("LepOther", leptonTypeSusy, 8, help="Leptons after the preselection"),
            ##------------------------------------------------
            "cleanJets"       : NTupleCollection("Jet",     jetTypeSusyExtraLight, 15, help="Cental jets after full selection and cleaning, sorted by pt"),
            #"cleanJetsFwd"    : NTupleCollection("JetFwd",  jetTypeSusy,  6, help="Forward jets after full selection and cleaning, sorted by pt"),            
            #"fatJets"         : NTupleCollection("FatJet",  fatJetType,  15, help="AK8 jets, sorted by pt"),
            ##------------------------------------------------
            #"ivf"       : NTupleCollection("SV",     svType, 20, help="SVs from IVF"),
            ##------------------------------------------------
            "LHE_weights"    : NTupleCollection("LHEweight",  lightWeightsInfoType, 1000, mcOnly=True, help="LHE weight info"),
            ##------------------------------------------------
            #"genleps"         : NTupleCollection("genLep",     genParticleWithLinksType, 10, help="Generated leptons (e/mu) from W/Z decays"),                                                                                                
            #"gentauleps"      : NTupleCollection("genLepFromTau", genParticleWithLinksType, 10, help="Generated leptons (e/mu) from decays of taus from W/Z/h decays"),                                                                       
            #"gentaus"         : NTupleCollection("genTau",     genParticleWithLinksType, 10, help="Generated leptons (tau) from W/Z decays"),                            
            "generatorSummary" : NTupleCollection("GenPart", genParticleWithLinksType, 50 , mcOnly=True, help="Hard scattering particles, with ancestry and links"),
}

wmass_recoilVariables=[
    NTupleVariable('vx',                           lambda ev : getattr(ev,'vx'),    help='vertex x',          storageType='H'),
    NTupleVariable('vy',                           lambda ev : getattr(ev,'vy'),    help='vertex y',          storageType='H'),
    NTupleVariable('vz',                           lambda ev : getattr(ev,'vz'),    help='vertex z',          storageType='H'),
    NTupleVariable('mindz',                        lambda ev : getattr(ev,'mindz'),                        help='closest vertex dz', storageType='H'),
    NTupleVariable('htkmet_n',                     lambda ev : getattr(ev,'htkmet_n'),                     help='candidate multiplicity for tkmet', storageType='H'),
    NTupleVariable('htkmet_pt',                    lambda ev : getattr(ev,'htkmet_pt'),                    help='recoil pt for tkmet', storageType='H'),
    NTupleVariable('htkmet_phi',                   lambda ev : getattr(ev,'htkmet_phi'),                   help='recoil phi for tkmet', storageType='H'),
    NTupleVariable('htkmet_scalar_sphericity',     lambda ev : getattr(ev,'htkmet_scalar_sphericity'),     help='scalar sphericity |h|/hT for tkmet', storageType='H'),
    NTupleVariable('htkmet_scalar_ht',             lambda ev : getattr(ev,'htkmet_scalar_ht'),             help='hT for tkmet', storageType='H'),   
    NTupleVariable('htkmet_leadpt',                lambda ev : getattr(ev,'htkmet_leadpt'),                help='leading candidate pt for tkmet', storageType='H'),
    NTupleVariable('htkmet_leadphi',               lambda ev : getattr(ev,'htkmet_leadphi'),               help='leading candidate phi for tkmet', storageType='H'),
    NTupleVariable('htkmet_thrustMinor',           lambda ev : getattr(ev,'htkmet_thrustMinor'),           help='thrust minor for tkmet PCA', storageType='H'),
    NTupleVariable('htkmet_thrustMajor',           lambda ev : getattr(ev,'htkmet_thrustMajor'),           help='thrust major for tkmet PCA', storageType='H'),
    NTupleVariable('htkmet_thrust',                lambda ev : getattr(ev,'htkmet_thrust'),                help='thrust for tkmet PCA', storageType='H'),
    NTupleVariable('htkmet_oblateness',            lambda ev : getattr(ev,'htkmet_oblateness'),            help='oblateness for tkmet PCA', storageType='H'),
    NTupleVariable('htkmet_thrustTransverse',      lambda ev : getattr(ev,'htkmet_thrustTransverse'),      help='thrust transverse for tkmet PCA', storageType='H'),
    NTupleVariable('htkmet_thrustTransverseMinor', lambda ev : getattr(ev,'htkmet_thrustTransverseMinor'), help='thrust transverse minor for tkmet PCA', storageType='H'),
    NTupleVariable('htkmet_sphericity',            lambda ev : getattr(ev,'htkmet_sphericity'),            help='mom. tensor sphericity for tkmet', storageType='H'),
    NTupleVariable('htkmet_aplanarity',            lambda ev : getattr(ev,'htkmet_aplanarity'),            help='mom. tensor aplanarity for tkmet', storageType='H'),
    NTupleVariable('htkmet_C',                     lambda ev : getattr(ev,'htkmet_C'),                     help='mom. tensor C for tkmet', storageType='H'),
    NTupleVariable('htkmet_D',                     lambda ev : getattr(ev,'htkmet_D'),                     help='mom. tensor D for tkmet', storageType='H'),
    NTupleVariable('htkmet_detST',                 lambda ev : getattr(ev,'htkmet_detST'),                 help='transverse mom. tensor determinant for tkmet', storageType='H'),
    NTupleVariable('htkmet_rho',                   lambda ev : getattr(ev,'htkmet_rho'),                   help='median energy density for tkmet', storageType='H'),
    NTupleVariable('htkmet_tau1',                  lambda ev : getattr(ev,'htkmet_tau1'),                  help='1-jettinness for tkmet', storageType='H'),
    NTupleVariable('htkmet_tau2',                  lambda ev : getattr(ev,'htkmet_tau2'),                  help='2-jettinness for tkmet', storageType='H'),
    NTupleVariable('htkmet_tau3',                  lambda ev : getattr(ev,'htkmet_tau3'),                  help='3-jettinness for tkmet', storageType='H'),
    NTupleVariable('htkmet_tau4',                  lambda ev : getattr(ev,'htkmet_tau4'),                  help='4-jettinness for tkmet', storageType='H'),

    NTupleVariable('hnpv_tkmet_n',                     lambda ev : getattr(ev,'hnpv_tkmet_n'),                     help='candidate multiplicity for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_pt',                    lambda ev : getattr(ev,'hnpv_tkmet_pt'),                    help='recoil pt for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_phi',                   lambda ev : getattr(ev,'hnpv_tkmet_phi'),                   help='recoil phi for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_scalar_sphericity',     lambda ev : getattr(ev,'hnpv_tkmet_scalar_sphericity'),     help='scalar sphericity |h|/hT for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_scalar_ht',             lambda ev : getattr(ev,'hnpv_tkmet_scalar_ht'),             help='hT for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_dphi2tkmet',            lambda ev : getattr(ev,'hnpv_tkmet_dphi2tkmet'),            help='deltaPhi wrt to tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_leadpt',                lambda ev : getattr(ev,'hnpv_tkmet_leadpt'),                help='leading candidate pt for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_leadphi',               lambda ev : getattr(ev,'hnpv_tkmet_leadphi'),               help='leading candidate phi for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_thrustMinor',           lambda ev : getattr(ev,'hnpv_tkmet_thrustMinor'),           help='thrust minor for npv_tkmet PCA', storageType='H'),
    NTupleVariable('hnpv_tkmet_thrustMajor',           lambda ev : getattr(ev,'hnpv_tkmet_thrustMajor'),           help='thrust major for npv_tkmet PCA', storageType='H'),
    NTupleVariable('hnpv_tkmet_thrust',                lambda ev : getattr(ev,'hnpv_tkmet_thrust'),                help='thrust for npv_tkmet PCA', storageType='H'),
    NTupleVariable('hnpv_tkmet_oblateness',            lambda ev : getattr(ev,'hnpv_tkmet_oblateness'),            help='oblateness for npv_tkmet PCA', storageType='H'),
    NTupleVariable('hnpv_tkmet_thrustTransverse',      lambda ev : getattr(ev,'hnpv_tkmet_thrustTransverse'),      help='thrust transverse for npv_tkmet PCA', storageType='H'),
    NTupleVariable('hnpv_tkmet_thrustTransverseMinor', lambda ev : getattr(ev,'hnpv_tkmet_thrustTransverseMinor'), help='thrust transverse minor for npv_tkmet PCA', storageType='H'),
    NTupleVariable('hnpv_tkmet_sphericity',            lambda ev : getattr(ev,'hnpv_tkmet_sphericity'),            help='mom. tensor sphericity for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_aplanarity',            lambda ev : getattr(ev,'hnpv_tkmet_aplanarity'),            help='mom. tensor aplanarity for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_C',                     lambda ev : getattr(ev,'hnpv_tkmet_C'),                     help='mom. tensor C for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_D',                     lambda ev : getattr(ev,'hnpv_tkmet_D'),                     help='mom. tensor D for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_detST',                 lambda ev : getattr(ev,'hnpv_tkmet_detST'),                 help='transverse mom. tensor determinant for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_rho',                   lambda ev : getattr(ev,'hnpv_tkmet_rho'),                   help='median energy density for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_tau1',                  lambda ev : getattr(ev,'hnpv_tkmet_tau1'),                  help='1-jettinness for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_tau2',                  lambda ev : getattr(ev,'hnpv_tkmet_tau2'),                  help='2-jettinness for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_tau3',                  lambda ev : getattr(ev,'hnpv_tkmet_tau3'),                  help='3-jettinness for npv_tkmet', storageType='H'),
    NTupleVariable('hnpv_tkmet_tau4',                  lambda ev : getattr(ev,'hnpv_tkmet_tau4'),                  help='4-jettinness for npv_tkmet', storageType='H'),

    NTupleVariable('hclosest_tkmet_n',                     lambda ev : getattr(ev,'hclosest_tkmet_n'),                     help='candidate multiplicity for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_pt',                    lambda ev : getattr(ev,'hclosest_tkmet_pt'),                    help='recoil pt for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_phi',                   lambda ev : getattr(ev,'hclosest_tkmet_phi'),                   help='recoil phi for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_scalar_sphericity',     lambda ev : getattr(ev,'hclosest_tkmet_scalar_sphericity'),     help='scalar sphericity |h|/hT for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_scalar_ht',             lambda ev : getattr(ev,'hclosest_tkmet_scalar_ht'),             help='hT for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_dphi2tkmet',            lambda ev : getattr(ev,'hclosest_tkmet_dphi2tkmet'),            help='deltaPhi wrt to tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_leadpt',                lambda ev : getattr(ev,'hclosest_tkmet_leadpt'),                help='leading candidate pt for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_leadphi',               lambda ev : getattr(ev,'hclosest_tkmet_leadphi'),               help='leading candidate phi for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_thrustMinor',           lambda ev : getattr(ev,'hclosest_tkmet_thrustMinor'),           help='thrust minor for closest_tkmet PCA', storageType='H'),
    NTupleVariable('hclosest_tkmet_thrustMajor',           lambda ev : getattr(ev,'hclosest_tkmet_thrustMajor'),           help='thrust major for closest_tkmet PCA', storageType='H'),
    NTupleVariable('hclosest_tkmet_thrust',                lambda ev : getattr(ev,'hclosest_tkmet_thrust'),                help='thrust for closest_tkmet PCA', storageType='H'),
    NTupleVariable('hclosest_tkmet_oblateness',            lambda ev : getattr(ev,'hclosest_tkmet_oblateness'),            help='oblateness for closest_tkmet PCA', storageType='H'),
    NTupleVariable('hclosest_tkmet_thrustTransverse',      lambda ev : getattr(ev,'hclosest_tkmet_thrustTransverse'),      help='thrust transverse for closest_tkmet PCA', storageType='H'),
    NTupleVariable('hclosest_tkmet_thrustTransverseMinor', lambda ev : getattr(ev,'hclosest_tkmet_thrustTransverseMinor'), help='thrust transverse minor for closest_tkmet PCA', storageType='H'),
    NTupleVariable('hclosest_tkmet_sphericity',            lambda ev : getattr(ev,'hclosest_tkmet_sphericity'),            help='mom. tensor sphericity for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_aplanarity',            lambda ev : getattr(ev,'hclosest_tkmet_aplanarity'),            help='mom. tensor aplanarity for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_C',                     lambda ev : getattr(ev,'hclosest_tkmet_C'),                     help='mom. tensor C for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_D',                     lambda ev : getattr(ev,'hclosest_tkmet_D'),                     help='mom. tensor D for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_detST',                 lambda ev : getattr(ev,'hclosest_tkmet_detST'),                 help='transverse mom. tensor determinant for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_rho',                   lambda ev : getattr(ev,'hclosest_tkmet_rho'),                   help='median energy density for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_tau1',                  lambda ev : getattr(ev,'hclosest_tkmet_tau1'),                  help='1-jettinness for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_tau2',                  lambda ev : getattr(ev,'hclosest_tkmet_tau2'),                  help='2-jettinness for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_tau3',                  lambda ev : getattr(ev,'hclosest_tkmet_tau3'),                  help='3-jettinness for closest_tkmet', storageType='H'),
    NTupleVariable('hclosest_tkmet_tau4',                  lambda ev : getattr(ev,'hclosest_tkmet_tau4'),                  help='4-jettinness for closest_tkmet', storageType='H'),

    NTupleVariable('hpuppimet_n',                     lambda ev : getattr(ev,'hpuppimet_n'),                     help='candidate multiplicity for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_pt',                    lambda ev : getattr(ev,'hpuppimet_pt'),                    help='recoil pt for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_phi',                   lambda ev : getattr(ev,'hpuppimet_phi'),                   help='recoil phi for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_scalar_sphericity',     lambda ev : getattr(ev,'hpuppimet_scalar_sphericity'),     help='scalar sphericity |h|/hT for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_scalar_ht',             lambda ev : getattr(ev,'hpuppimet_scalar_ht'),             help='hT for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_dphi2tkmet',            lambda ev : getattr(ev,'hpuppimet_dphi2tkmet'),            help='deltaPhi wrt to tkmet', storageType='H'),
    NTupleVariable('hpuppimet_leadpt',                lambda ev : getattr(ev,'hpuppimet_leadpt'),                help='leading candidate pt for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_leadphi',               lambda ev : getattr(ev,'hpuppimet_leadphi'),               help='leading candidate phi for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_thrustMinor',           lambda ev : getattr(ev,'hpuppimet_thrustMinor'),           help='thrust minor for puppimet PCA', storageType='H'),
    NTupleVariable('hpuppimet_thrustMajor',           lambda ev : getattr(ev,'hpuppimet_thrustMajor'),           help='thrust major for puppimet PCA', storageType='H'),
    NTupleVariable('hpuppimet_thrust',                lambda ev : getattr(ev,'hpuppimet_thrust'),                help='thrust for puppimet PCA', storageType='H'),
    NTupleVariable('hpuppimet_oblateness',            lambda ev : getattr(ev,'hpuppimet_oblateness'),            help='oblateness for puppimet PCA', storageType='H'),
    NTupleVariable('hpuppimet_thrustTransverse',      lambda ev : getattr(ev,'hpuppimet_thrustTransverse'),      help='thrust transverse for puppimet PCA', storageType='H'),
    NTupleVariable('hpuppimet_thrustTransverseMinor', lambda ev : getattr(ev,'hpuppimet_thrustTransverseMinor'), help='thrust transverse minor for puppimet PCA', storageType='H'),
    NTupleVariable('hpuppimet_sphericity',            lambda ev : getattr(ev,'hpuppimet_sphericity'),            help='mom. tensor sphericity for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_aplanarity',            lambda ev : getattr(ev,'hpuppimet_aplanarity'),            help='mom. tensor aplanarity for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_C',                     lambda ev : getattr(ev,'hpuppimet_C'),                     help='mom. tensor C for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_D',                     lambda ev : getattr(ev,'hpuppimet_D'),                     help='mom. tensor D for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_detST',                 lambda ev : getattr(ev,'hpuppimet_detST'),                 help='transverse mom. tensor determinant for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_rho',                   lambda ev : getattr(ev,'hpuppimet_rho'),                   help='median energy density for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_tau1',                  lambda ev : getattr(ev,'hpuppimet_tau1'),                  help='1-jettinness for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_tau2',                  lambda ev : getattr(ev,'hpuppimet_tau2'),                  help='2-jettinness for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_tau3',                  lambda ev : getattr(ev,'hpuppimet_tau3'),                  help='3-jettinness for puppimet', storageType='H'),
    NTupleVariable('hpuppimet_tau4',                  lambda ev : getattr(ev,'hpuppimet_tau4'),                  help='4-jettinness for puppimet', storageType='H'),

    NTupleVariable('hinvpuppimet_n',                     lambda ev : getattr(ev,'hinvpuppimet_n'),                     help='candidate multiplicity for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_pt',                    lambda ev : getattr(ev,'hinvpuppimet_pt'),                    help='recoil pt for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_phi',                   lambda ev : getattr(ev,'hinvpuppimet_phi'),                   help='recoil phi for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_scalar_sphericity',     lambda ev : getattr(ev,'hinvpuppimet_scalar_sphericity'),     help='scalar sphericity |h|/hT for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_scalar_ht',             lambda ev : getattr(ev,'hinvpuppimet_scalar_ht'),             help='hT for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_dphi2tkmet',            lambda ev : getattr(ev,'hinvpuppimet_dphi2tkmet'),            help='deltaPhi wrt to tkmet', storageType='H'),
    NTupleVariable('hinvpuppimet_leadpt',                lambda ev : getattr(ev,'hinvpuppimet_leadpt'),                help='leading candidate pt for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_leadphi',               lambda ev : getattr(ev,'hinvpuppimet_leadphi'),               help='leading candidate phi for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_thrustMinor',           lambda ev : getattr(ev,'hinvpuppimet_thrustMinor'),           help='thrust minor for invpuppimet PCA', storageType='H'),
    NTupleVariable('hinvpuppimet_thrustMajor',           lambda ev : getattr(ev,'hinvpuppimet_thrustMajor'),           help='thrust major for invpuppimet PCA', storageType='H'),
    NTupleVariable('hinvpuppimet_thrust',                lambda ev : getattr(ev,'hinvpuppimet_thrust'),                help='thrust for invpuppimet PCA', storageType='H'),
    NTupleVariable('hinvpuppimet_oblateness',            lambda ev : getattr(ev,'hinvpuppimet_oblateness'),            help='oblateness for invpuppimet PCA', storageType='H'),
    NTupleVariable('hinvpuppimet_thrustTransverse',      lambda ev : getattr(ev,'hinvpuppimet_thrustTransverse'),      help='thrust transverse for invpuppimet PCA', storageType='H'),
    NTupleVariable('hinvpuppimet_thrustTransverseMinor', lambda ev : getattr(ev,'hinvpuppimet_thrustTransverseMinor'), help='thrust transverse minor for invpuppimet PCA', storageType='H'),
    NTupleVariable('hinvpuppimet_sphericity',            lambda ev : getattr(ev,'hinvpuppimet_sphericity'),            help='mom. tensor sphericity for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_aplanarity',            lambda ev : getattr(ev,'hinvpuppimet_aplanarity'),            help='mom. tensor aplanarity for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_C',                     lambda ev : getattr(ev,'hinvpuppimet_C'),                     help='mom. tensor C for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_D',                     lambda ev : getattr(ev,'hinvpuppimet_D'),                     help='mom. tensor D for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_detST',                 lambda ev : getattr(ev,'hinvpuppimet_detST'),                 help='transverse mom. tensor determinant for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_rho',                   lambda ev : getattr(ev,'hinvpuppimet_rho'),                   help='median energy density for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_tau1',                  lambda ev : getattr(ev,'hinvpuppimet_tau1'),                  help='1-jettinness for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_tau2',                  lambda ev : getattr(ev,'hinvpuppimet_tau2'),                  help='2-jettinness for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_tau3',                  lambda ev : getattr(ev,'hinvpuppimet_tau3'),                  help='3-jettinness for invpuppimet', storageType='H'),
    NTupleVariable('hinvpuppimet_tau4',                  lambda ev : getattr(ev,'hinvpuppimet_tau4'),                  help='4-jettinness for invpuppimet', storageType='H'),

    NTupleVariable('hgen_n',                     lambda ev : getattr(ev,'hgen_n'),                    mcOnly=True,  help='candidate multiplicity for gen', storageType='H'),
    NTupleVariable('hgen_pt',                    lambda ev : getattr(ev,'hgen_pt'),                   mcOnly=True,  help='recoil pt for gen', storageType='H'),
    NTupleVariable('hgen_phi',                   lambda ev : getattr(ev,'hgen_phi'),                  mcOnly=True,  help='recoil phi for gen', storageType='H'),
    NTupleVariable('hgen_scalar_sphericity',     lambda ev : getattr(ev,'hgen_scalar_sphericity'),    mcOnly=True,  help='scalar sphericity |h|/hT for gen', storageType='H'),
    NTupleVariable('hgen_scalar_ht',             lambda ev : getattr(ev,'hgen_scalar_ht'),            mcOnly=True,  help='hT for gen', storageType='H'),   
    NTupleVariable('hgen_leadpt',                lambda ev : getattr(ev,'hgen_leadpt'),               mcOnly=True,  help='leading candidate pt for gen', storageType='H'),
    NTupleVariable('hgen_leadphi',               lambda ev : getattr(ev,'hgen_leadphi'),              mcOnly=True,  help='leading candidate phi for gen', storageType='H'),
    NTupleVariable('hgen_thrustMinor',           lambda ev : getattr(ev,'hgen_thrustMinor'),          mcOnly=True,  help='thrust minor for gen PCA', storageType='H'),
    NTupleVariable('hgen_thrustMajor',           lambda ev : getattr(ev,'hgen_thrustMajor'),          mcOnly=True,  help='thrust major for gen PCA', storageType='H'),
    NTupleVariable('hgen_thrust',                lambda ev : getattr(ev,'hgen_thrust'),               mcOnly=True,  help='thrust for gen PCA', storageType='H'),
    NTupleVariable('hgen_oblateness',            lambda ev : getattr(ev,'hgen_oblateness'),           mcOnly=True,  help='oblateness for gen PCA', storageType='H'),
    NTupleVariable('hgen_thrustTransverse',      lambda ev : getattr(ev,'hgen_thrustTransverse'),     mcOnly=True,  help='thrust transverse for gen PCA', storageType='H'),
    NTupleVariable('hgen_thrustTransverseMinor', lambda ev : getattr(ev,'hgen_thrustTransverseMinor'),mcOnly=True,  help='thrust transverse minor for gen PCA', storageType='H'),
    NTupleVariable('hgen_sphericity',            lambda ev : getattr(ev,'hgen_sphericity'),           mcOnly=True,  help='mom. tensor sphericity for gen', storageType='H'),
    NTupleVariable('hgen_aplanarity',            lambda ev : getattr(ev,'hgen_aplanarity'),           mcOnly=True,  help='mom. tensor aplanarity for gen', storageType='H'),
    NTupleVariable('hgen_C',                     lambda ev : getattr(ev,'hgen_C'),                    mcOnly=True,  help='mom. tensor C for gen', storageType='H'),
    NTupleVariable('hgen_D',                     lambda ev : getattr(ev,'hgen_D'),                    mcOnly=True,  help='mom. tensor D for gen', storageType='H'),
    NTupleVariable('hgen_detST',                 lambda ev : getattr(ev,'hgen_detST'),                mcOnly=True,  help='transverse mom. tensor determinant for gen', storageType='H'),
    NTupleVariable('hgen_rho',                   lambda ev : getattr(ev,'hgen_rho'),                  mcOnly=True,  help='median energy density for gen', storageType='H'),
    NTupleVariable('hgen_tau1',                  lambda ev : getattr(ev,'hgen_tau1'),                 mcOnly=True,  help='1-jettinness for gen', storageType='H'),
    NTupleVariable('hgen_tau2',                  lambda ev : getattr(ev,'hgen_tau2'),                 mcOnly=True,  help='2-jettinness for gen', storageType='H'),
    NTupleVariable('hgen_tau3',                  lambda ev : getattr(ev,'hgen_tau3'),                 mcOnly=True,  help='3-jettinness for gen', storageType='H'),
    NTupleVariable('hgen_tau4',                  lambda ev : getattr(ev,'hgen_tau4'),                 mcOnly=True,  help='4-jettinness for gen', storageType='H'),
]

