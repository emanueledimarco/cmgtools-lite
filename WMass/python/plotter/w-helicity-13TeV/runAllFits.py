# USAGE: python runAllFits.py cards_el el
import os,sys

cardsdir = sys.argv[1]
channel = sys.argv[2]
if channel not in ['mu','el']:
    print "Channel must be either mu or el. Exiting."
    sys.exit()

pois = [' --POIMode none ','']
expected = [' -t 0 ',' -t -1 ']
BBBs = ['',' --binByBinStat --correlateXsecStat ']

for ipm,POImode in enumerate(pois):
    card = cardsdir+"/W{chan}_card_withXsecMask.hdf5".format(chan=channel) if len(POImode)==0 else cardsdir+'/W{chan}_card.hdf5'.format(chan=channel)
    doImpacts = ' --doImpacts ' if ipm==1 else ''
    for iexp,exp in enumerate(expected):
        saveHist = ' --saveHists --computeHistErrors ' #if (iexp==0 and ipm==1) else ''
        for ibbb,bbb in enumerate(BBBs):
            cmd = 'combinetf.py {poimode} {exp} {bbb} {saveh} {imp} {card}'.format(poimode=POImode, exp=exp, bbb=bbb, saveh=saveHist, imp=doImpacts, card=card)
            print "running ",cmd
            os.system(cmd)
            os.system('mv fitresults_123456789.root fitresults_poim{ipm}_exp{iexp}_bbb{ibbb}.root'.format(ipm=ipm, iexp=iexp, ibbb=ibbb))
            print "fit done. Moving to the next one."

            
