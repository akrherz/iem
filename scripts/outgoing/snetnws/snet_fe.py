"""
 Script to take current SHEF obs and generate a METAR summary
"""
from twisted.python import log
log.startLogging( open('/mesonet/data/logs/snet_fe.log', 'a') )

import re, mx.DateTime
SCRIPT_TIME = mx.DateTime.now()
import subprocess
import tempfile
import os
import sys
import access
import network
import tracker
import mesonet
iemtracker = tracker.Engine()
nt = network.Table(("KCCI", "KELO", "KIMT"))
import iemdb
IEM = iemdb.connect("iem", bypass=True)




# Files we write
(tmpfp, tmpfname) = tempfile.mkstemp()
saofn = "%s.sao" % (tmpfname,)
csvfn = "%s.csv" % (tmpfname,)
kelocsvfn = "%s_kelo.csv" % (tmpfname,)
rr5fn = "%s_RR5.dat" % (tmpfname,)
locdsmfn = "%s_LOCDSM.dat" % (tmpfname,)
fsdrr5fn = "%s_FSD.dat" % (tmpfname,)
kimtrr5fn = "%s_kimt.dat" % (tmpfname,)

SAOFILE = open(saofn,'w')
CSVFILE = open(csvfn,'w')
KELOCSVFILE = open(kelocsvfn,'w')
DMXRR5 = open(rr5fn,'w')
LOCDSMRR5 = open(locdsmfn,'w')
FSDRR5 = open(fsdrr5fn,'w')
BADRR5 = open(kimtrr5fn,'w')

###
# Two dicts to hold information about precip accumulations
yrCntr = {}
moCntr = {}


#_______________________________________________________________
# writeHeader()
#   - function to simply write the header on the SAO file
#
def writeHeader():
    now = SCRIPT_TIME.gmtime()
    sDate = now.strftime("%d%H%M")

    SAOFILE.write("\001\015\015\012001\n")
    SAOFILE.write("SAUS43 KDMX "+sDate+"\015\015\012")
    SAOFILE.write("METAR\015\015\012")
    #DMXRR5.write("\001\015\015\012001\n")
    #DMXRR5.write("SRUS53 KDMX "+sDate+"\015\015\012")
    #DMXRR5.write("RR5DMX\015\015\012")

    now = SCRIPT_TIME + mx.DateTime.RelativeDateTime(minutes=+4)
    sDate = now.strftime("%m%d")
    hour = now.strftime("%H%M")

    DMXRR5.write("\n\n\n.B DMX "+sDate+" C DH"+str(hour)+"/TA/PPH/PPT/PPQ/PCIRP\n")
    DMXRR5.write(":Location ID   TempF / 1h prec / 3h prec / ...\n")
    DMXRR5.write(":                6h prec / pcirp\n")
    DMXRR5.write(":Iowa Environmental Mesonet - KCCI SchoolNet8\n")

    LOCDSMRR5.write("\n\n\n.B DMX "+sDate+" C DH"+str(hour)+"/TA/PCIRP\n")
    LOCDSMRR5.write(":Location ID   TempF / pcirp ...\n")
    LOCDSMRR5.write(":Iowa Environmental Mesonet - KCCI SchoolNet8\n")

    #FSDRR5.write("\n\n\n.B FSD "+sDate+" C DH"+str(hour)+"/TA/PPH/PPT/PPQ/PPD/PCIRP\n")
    FSDRR5.write("\n\n\n.B FSD "+sDate+" C DH"+str(hour)+"/TA/PPH/PPT/PPQ/PCIRP\n")
    FSDRR5.write(":Location ID   TempF / 1h prec / 3h prec / ...\n")
    #FSDRR5.write(":                6h prec / 1d prec / pcirp\n")
    FSDRR5.write(":                6h prec / pcirp\n")
    FSDRR5.write(":Iowa Environmental Mesonet - KELO WeatherNet\n")

 
#_______________________________________________________________
#   loadCounters()
#     - simply loads data from the counter.yr file.
#
def loadCounters():
    o = open("counter.yr").readlines()
    for i in range(len(o)):
      tokens = re.split(" ", o[i])
      sID = tokens[0]
      MOpcpn = tokens[1]
      YRpcpn = tokens[2]
      moCntr[sID] = float(MOpcpn)
      yrCntr[sID] = float(YRpcpn)
    if ( len(o) == 0):
      print "ERROR: counter.yr is null"

#_______________________________________________________________
#   writeCounter()
#     - write the counters back to the counter.yr file
#
def writeCounters():
  o = open("counter.yr","w")
  for key in moCntr.keys():
    MOelem = moCntr[key]
    if (MOelem < 0):
      MOelem = 0
    YRelem = yrCntr[key]
    if (YRelem < 0):
      YRelem = 0
    o.write("%s %.2f %.2f\n" % (key, MOelem, YRelem) )
  o.close()

def fetch_pmonth(obs, nwsli):
    if obs.has_key(nwsli):
        return obs[nwsli].data.get('pmonth',-1)
    return -1

def precip_diff(current, past):
    if current < 0 or past < 0:
        return None
    if current >= past:
        return current - past
    if past > current:
        return current
    log.msg("Precip diff logic fault! Current: %s Past: %s" % (current,past))
    return None

def pretty_tmpf(ob):
    val = ob.get('tmpf', None)
    if val is None:
        return 'M'
    if val < -60:
        return 'M'
    return "%.0f" % (val,)

def pretty_precip(val):
    if val is None:
        return 'M'
    if val < 0:
        return 'M'
    return "%.2f" % (val,)

def getm_c(ob, idx):
    val = ob.get(idx, None)
    if val is None:
        return 'M'
    valc = mesonet.f2c( val )
    if valc is None:
        return 'M'
    return '%.0f' % (valc,)

def doNetwork(_network, shef_fp, thres, qdict):
    """
    Process a schoolnet network and do various things
    @param network string network name
    @param shef_fp file pointer to shef product file
    @param thres time threshold we care about for alerting
    @param qdict dictionary of sites we don't care about
    """
    now = mx.DateTime.now()
    # Get Obs
    obs = access.get_network(_network, IEM)
    tophour_obs = access.get_network_recent(_network, IEM, now + mx.DateTime.RelativeDateTime(minute=0))
    hr3_obs = access.get_network_recent(_network, IEM, now + mx.DateTime.RelativeDateTime(hours=-3))
    hr6_obs = access.get_network_recent(_network, IEM, now + mx.DateTime.RelativeDateTime(hours=-6))

    # Check to see if we will be alerting for offline stuff
    dontmail = will_email(_network, obs, thres)
    if len(sys.argv) > 1:
        log.msg("Running in safe mode due to sys.argv")
        dontmail = True

    keys = obs.keys()
    keys.sort()
    for nwsli in keys:
        ob = obs[nwsli].data
        if ob['ts'] < thres:  
            iemtracker.doAlert(nwsli, ob, _network, '%ssnet' % (_network.lower(),) , dontmail)
            continue
        iemtracker.checkStation(nwsli, ob, _network, '%ssnet' % (_network.lower(),), dontmail)
        
        current_pmonth = fetch_pmonth(obs, nwsli)
        tophour_pmonth = fetch_pmonth(tophour_obs, nwsli)
        hr3_pmonth = fetch_pmonth(hr3_obs, nwsli)
        hr6_pmonth = fetch_pmonth(hr6_obs, nwsli)
        
        if not moCntr.has_key(nwsli):
            moCntr[nwsli] = 0.
            yrCntr[nwsli] = 0.
                    
        # reset
        if moCntr[nwsli] > current_pmonth: 
            yrCntr[nwsli] += current_pmonth
        moCntr[nwsli] = current_pmonth

        pcounter = yrCntr[nwsli] + current_pmonth

        # Compute offsets
        phour = precip_diff(current_pmonth, tophour_pmonth)
        p03i = precip_diff(current_pmonth, hr3_pmonth)
        p06i = precip_diff(current_pmonth, hr6_pmonth)
        pday = ob['pday']

        if qdict.get(nwsli, {}).get('precip', False) or network == 'KIMT':
            phour = None
            p03i = None
            p06i = None
            pcounter = None
            pday = None

        # Finally ready to write SHEF!
        shef_fp.write("%s %s / %4s / %4s / %4s / %5s : %s\n" % (nwsli,
                                pretty_tmpf(ob), pretty_precip(phour),
                                pretty_precip(p03i), pretty_precip(p06i),
                                pretty_precip(pcounter), 
                                ob.get('sname', 'Unknown')))
        if _network == 'KCCI':
                LOCDSMRR5.write("%s      %3s / %5s\n" % (nwsli,
                                pretty_tmpf(ob), pretty_precip(pcounter)))
        # CSV FILE!
        for fp in [CSVFILE, KELOCSVFILE]:
            if _network != 'KELO' and fp == KELOCSVFILE:
                continue
            fp.write("%s,%s,%s,%s,%i,%s,%s,%s,%s\n" % (nwsli,
                ob['ts'].gmtime().strftime("%Y/%m/%d %H:%M:%S"), getm_c(ob, 'tmpf'),
                getm_c(ob, 'dwpf'), ob['sknt'], ob['drct'], phour or 'M', pday or 'M', ob['pres']))

        if _network != 'KIMT':
            SAOFILE.write( obs[nwsli].metar() )





def will_email(_network, obs, thres):
    """
    Preemptive checking to make sure we don't email!
    """
    cnt_threshold = 25
    if (_network == 'KIMT'):
        cnt_threshold = 10
    cnt_offline = 0
    # First, look into the offline database to see how many active tickets
    icursor = IEM.cursor()
    icursor.execute("""SELECT count(*) as c from offline WHERE 
      network = %s and length(station) = 5""", (_network,) )
    row = icursor.fetchone()
    cnt_offline = row[0]

    log.msg("Portfolio says cnt_offline: %s %s" % (_network, cnt_offline))
    if cnt_offline > cnt_threshold:
        return True

    # Check obs
    cnt_offline = 0
    for nwsli in obs.keys():
        if obs[nwsli].data['ts'] < thres:
            cnt_offline += 1
    log.msg("IEMAccess says cnt_offline: %s %s" % (_network, cnt_offline))
    if cnt_offline > cnt_threshold:
        return True

    return False

def closeFiles():
    SAOFILE.write("\015\015\012\003")
    SAOFILE.close()
    DMXRR5.write(".END\n")
    DMXRR5.close()
    LOCDSMRR5.write(".END\n")
    LOCDSMRR5.close()
    FSDRR5.write(".END\n")
    FSDRR5.close()
    CSVFILE.close()
    KELOCSVFILE.close()

def post_process():
    """
    Last actions after we are done generating all these files :)
    """
    
    saoname = "IA.snet%s.sao" % (SCRIPT_TIME.gmtime().strftime("%d%H%M"),)
    cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % (saoname, saofn)
    subprocess.call( cmd, shell=True )
    os.unlink(saofn)

    cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('snet.csv', csvfn)
    subprocess.call( cmd, shell=True )
    os.unlink(csvfn)

    cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('kelo.csv', kelocsvfn)
    subprocess.call( cmd, shell=True )
    os.unlink(kelocsvfn)
    
    if SCRIPT_TIME.minute in [15,35]:
        cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('LOCDSMRR5DMX.dat', locdsmfn)
        subprocess.call( cmd, shell=True )
    if SCRIPT_TIME.minute in [55,]:
        cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('SUADSMRR5DMX.dat', rr5fn)
        subprocess.call( cmd, shell=True )
        cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('SUAFSDRR5FSD.dat', fsdrr5fn)
        subprocess.call( cmd, shell=True )
    os.unlink(locdsmfn)
    os.unlink(rr5fn)
    os.unlink(fsdrr5fn)
    os.unlink(kimtrr5fn)

def loadQC():
    """
    See which sites have flags against them
    """
    qdict = {}
    portfolio = iemdb.connect('portfolio', dbhost='meteor.geol.iastate.edu',
                              bypass=True)
    pcursor = portfolio.cursor()
    
    pcursor.execute("""
    select s_mid, sensor, status from tt_base WHERE sensor is not null 
    and status != 'CLOSED' and portfolio in ('kccisnet','kelosnet','kimtsnet')
    """)
    for row in pcursor:
        if not qdict.has_key(row[0]):
            qdict[row[0]] = {}
        if row[1].find("precip") > -1:
            qdict[row[0]]['precip'] = True
    
    pcursor.close()
    portfolio.close()
    return qdict

if __name__ == '__main__':
    qdict = loadQC()
    loadCounters()
    writeHeader()
    now = mx.DateTime.now()
    doNetwork('KCCI', DMXRR5, now - mx.DateTime.RelativeDateTime(minutes=60),
              qdict)
    doNetwork('KIMT', BADRR5, now - mx.DateTime.RelativeDateTime(minutes=60),
              qdict)
    doNetwork('KELO', FSDRR5, now - mx.DateTime.RelativeDateTime(minutes=300),
              qdict)

    writeCounters()
    closeFiles()
    post_process()
    iemtracker.send()
    log.msg("FINISH...")
