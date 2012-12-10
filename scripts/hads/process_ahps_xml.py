"""
 Ingest the rich metadata found within the AHPS2 website!
"""
from twisted.words.xish import xpath, domish
import urllib2
import iemdb
import sys
mesosite = iemdb.connect('mesosite')
mcursor = mesosite.cursor()
mcursor2 = mesosite.cursor()

def process_site( nwsli, network ):
    
    url = "http://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=%s&output=xml" % (nwsli,)
    
    elementStream = domish.elementStream()
    roots = []
    results = []
    elementStream.DocumentStartEvent = roots.append
    elementStream.ElementEvent = lambda elem: roots[0].addChild(elem)
    elementStream.DocumentEndEvent = lambda: results.append(roots[0])
    try:
        xml = urllib2.urlopen(url).read()
    except:
        print "DOWNLOAD ERROR"
        print url
        return
    try:
        elementStream.parse(xml)
    except:
        print "XML ERROR"
        print url
        return
    
    elem = results[0]
    
    nodes = xpath.queryForNodes('/site/sigstages', elem)
    
    sigstages = nodes[0]
    data = {'id': nwsli, 'network': network}
    for s in sigstages.children:
        val = str(s)
        if val == '':
            val = None
        data['sigstage_%s' %(s.name,)] =  val

    if not data.has_key('sigstage_low'):
        print 'No Data', nwsli, network
        return

    print data
    mcursor2.execute("""UPDATE stations SET sigstage_low = %(sigstage_low)s,
    sigstage_action = %(sigstage_action)s, sigstage_bankfull = %(sigstage_bankfull)s,
    sigstage_flood = %(sigstage_flood)s, sigstage_moderate = %(sigstage_moderate)s,
    sigstage_major = %(sigstage_major)s, sigstage_record = %(sigstage_record)s
    WHERE id = %(id)s and network = %(network)s """, data)
        
network = sys.argv[1]
mcursor.execute("""SELECT id, network from stations where network = %s""", 
                (network,))
for row in mcursor:
    process_site(row[0], row[1])
mcursor.close()
mcursor2.close()
mesosite.commit()
mesosite.close()