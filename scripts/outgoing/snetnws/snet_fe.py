"""
 Script to take current SHEF obs and generate a METAR summary
"""
import datetime
import pytz
import subprocess
import tempfile
import os
from pyiem.datatypes import temperature
from pyiem.network import Table as NetworkTable
from pyiem.tracker import TrackerEngine
import psycopg2

SCRIPT_TIME = datetime.datetime.utcnow()
SCRIPT_TIME = SCRIPT_TIME.replace(tzinfo=pytz.timezone("UTC"))
SCRIPT_TIME = SCRIPT_TIME.astimezone(pytz.timezone("America/Chicago"))
NT = NetworkTable(("KCCI", "KELO", "KIMT"))
IEM = psycopg2.connect(database="iem", host='iemdb')
PORTFOLIO = psycopg2.connect(database='portfolio', host='iemdb')

# Files we write
(tmpfp, tmpfname) = tempfile.mkstemp()
# Close out the above to prevent tmpfname from sticking around
os.close(tmpfp)
os.unlink(tmpfname)
saofn = "%s.sao" % (tmpfname,)
csvfn = "%s.csv" % (tmpfname,)
kelocsvfn = "%s_kelo.csv" % (tmpfname,)
rr5fn = "%s_RR5.dat" % (tmpfname,)
locdsmfn = "%s_LOCDSM.dat" % (tmpfname,)
fsdrr5fn = "%s_FSD.dat" % (tmpfname,)
kimtrr5fn = "%s_kimt.dat" % (tmpfname,)

SAOFILE = open(saofn, 'w')
CSVFILE = open(csvfn, 'w')
KELOCSVFILE = open(kelocsvfn, 'w')
DMXRR5 = open(rr5fn, 'w')
LOCDSMRR5 = open(locdsmfn, 'w')
FSDRR5 = open(fsdrr5fn, 'w')
BADRR5 = open(kimtrr5fn, 'w')

###
# Two dicts to hold information about precip accumulations
yrCntr = {}
moCntr = {}


def f2c(thisf):
    return 5.00/9.00 * (thisf - 32.00)


def metar_tmpf(tmpf):
    """
    Convert a temperature in F to something metar wants
    """
    if tmpf is None:
        return 'MM'
    tmpc = f2c(tmpf)
    if tmpc < 0:
        return 'M%02.0f' % (0 - tmpc,)
    return '%02.0f' % (tmpc,)


def metar_tmpf_tgroup(tmpf):
    """
    Convert a temperature in F to something metar wants
    """
    if tmpf is None:
        return '////'
    tmpc = f2c(tmpf)
    if tmpc < 0:
        return '1%03.0f' % (0 - (tmpc*10.0),)
    return '0%03.0f' % ((tmpc*10.0),)


def metar(ob):
    """
    Return a METAR representation of this observation :)
    """
    # First up, is the ID, which needs to be 3 or 4 char :(
    mid = ob.get('id')
    if len(mid) > 4:
        mid = 'Q%s' % (mid[1:4])
    # Metar Time
    mtrts = ob['valid'].astimezone(pytz.timezone("UTC")).strftime("%d%H%MZ")
    # Wind Direction
    mdir = ob.get('drct', 0)
    if mdir == 360:
        mdir = 0
    mwind = "%03i%02iKT" % (mdir, ob.get('sknt', 0))
    # Temperature
    mtmp = "%s/%s" % (metar_tmpf(ob.get('tmpf')),
                      metar_tmpf(ob.get('dwpf')))
    # Altimeter
    malti = "A%04i" % (ob.get('pres', 0) * 100.0,)
    # Remarks
    tgroup = "T%s%s" % (metar_tmpf_tgroup(ob.get('tmpf')),
                        metar_tmpf_tgroup(ob.get('dwpf')))
    # Phour
    phour = "P%04i" % (ob.get('p01i', 0), )
    # Pday
    pday = "7%04i" % (ob.get('pday', 0), )
    return "%s %s %s %s RMK %s %s %s %s=\015\015\012" % (mid, mtrts, mwind,
                                                         mtmp, malti, tgroup,
                                                         phour, pday)


def writeHeader():
    now = SCRIPT_TIME.astimezone(pytz.timezone("UTC"))
    sDate = now.strftime("%d%H%M")

    SAOFILE.write("\001\015\015\012001\n")
    SAOFILE.write("SAUS43 KDMX "+sDate+"\015\015\012")
    SAOFILE.write("METAR\015\015\012")

    # NB: why are we doing this addition of four minutes
    now = SCRIPT_TIME + datetime.timedelta(minutes=4)
    sDate = now.strftime("%m%d")
    hour = now.strftime("%H%M")

    DMXRR5.write("\n\n\n.B DMX "+sDate+" C DH"+hour+"/TA/PPH/PPT/PPQ/PCIRP\n")
    DMXRR5.write(":Location ID   TempF / 1h prec / 3h prec / ...\n")
    DMXRR5.write(":                6h prec / pcirp\n")
    DMXRR5.write(":Iowa Environmental Mesonet - KCCI SchoolNet8\n")

    LOCDSMRR5.write("\n\n\n.B DMX "+sDate+" C DH"+hour+"/TA/PCIRP\n")
    LOCDSMRR5.write(":Location ID   TempF / pcirp ...\n")
    LOCDSMRR5.write(":Iowa Environmental Mesonet - KCCI SchoolNet8\n")

    FSDRR5.write("\n\n\n.B FSD "+sDate+" C DH"+hour+"/TA/PPH/PPT/PPQ/PCIRP\n")
    FSDRR5.write(":Location ID   TempF / 1h prec / 3h prec / ...\n")
    FSDRR5.write(":                6h prec / pcirp\n")
    FSDRR5.write(":Iowa Environmental Mesonet - KELO WeatherNet\n")


def loadCounters():
    """ Open the precip_counter.txt """
    # Default to zero
    for sid in NT.sts.keys():
        moCntr[sid] = 0.0
        yrCntr[sid] = 0.0
    if not os.path.isfile("precip_counter.txt"):
        return
    for line in open('precip_counter.txt'):
        tokens = line.split()
        if len(tokens) != 3:
            continue
        sid = tokens[0]
        moCntr[sid] = float(tokens[1])
        yrCntr[sid] = float(tokens[2])


def writeCounters():
    """ write out the precip counters for the next run! """
    o = open("precip_counter", "w")
    for key in moCntr.keys():
        MOelem = moCntr[key]
        if (MOelem < 0):
            MOelem = 0
        YRelem = yrCntr[key]
        if (YRelem < 0):
            YRelem = 0
        o.write("%s %.2f %.2f\n" % (key, MOelem, YRelem))
    o.close()


def fetch_pmonth(obs, nwsli):
    if nwsli in obs:
        return obs[nwsli].get('pmonth', -1)
    return -1


def precip_diff(current, past):
    if current < 0 or past < 0:
        return None
    if current >= past:
        return current - past
    if past > current:
        return current
    print("Precip diff logic fault! Current: %s Past: %s" % (current, past))
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
    valc = temperature(val, 'F').value('C')
    if valc is None:
        return 'M'
    return '%.0f' % (valc,)


def get_network(_network):
    """get data"""
    obs = {}
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
    SELECT c.*, s.*, t.id, t.name as sname
    from current c, summary s, stations t WHERE
    t.iemid = s.iemid and s.iemid = c.iemid and t.network = '%s' and
    s.day = 'TODAY' ORDER by random()
    """ % (_network, ))
    for row in cursor:
        obs[row['id']] = row
    cursor.close()
    return obs


def get_network_recent(_network, valid):
    """Return a dictionary of observations for this network at time

    Args:
      _network (str): network to fetch data for
      valid (datetime): timestamp of interest

    Returns:
      dictionary of observations with NWSLI as the key
    """
    obs = {}
    cursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # We order by valid DESC so that the last observation into the dictionary
    # is the closest to this valid timestamp
    cursor.execute("""
    SELECT c.*, t.id from current_log c JOIN stations t ON (t.iemid = c.iemid)
    WHERE t.network = %s and
    c.valid BETWEEN %s and %s::timestamptz + '%s minutes'::interval
    ORDER by valid DESC
    """, (_network, valid.strftime("%Y-%m-%d %H:%M"),
          valid.strftime("%Y-%m-%d %H:%M"), 10))
    for row in cursor:
        obs[row['id']] = row
    cursor.close()
    return obs


def doNetwork(_network, shef_fp, thres, qdict):
    """
    Process a schoolnet network and do various things
    @param network string network name
    @param shef_fp file pointer to shef product file
    @param thres time threshold we care about for alerting
    @param qdict dictionary of sites we don't care about
    """
    now = datetime.datetime.now()
    # Get Obs
    obs = get_network(_network)
    tophour_obs = get_network_recent(_network, now.replace(minute=0))
    hr3_obs = get_network_recent(_network, now + datetime.timedelta(hours=-3))
    hr6_obs = get_network_recent(_network, now + datetime.timedelta(hours=-6))

    tracker = TrackerEngine(IEM.cursor(), PORTFOLIO.cursor(), 10)
    mynet = NetworkTable(_network)
    tracker.process_network(obs, '%ssnet' % (_network.lower(), ), mynet, thres)
    tracker.send_emails()

    keys = obs.keys()
    keys.sort()
    for nwsli in keys:
        ob = obs[nwsli]
        if ob['valid'] < thres:
            continue

        current_pmonth = fetch_pmonth(obs, nwsli)
        tophour_pmonth = fetch_pmonth(tophour_obs, nwsli)
        hr3_pmonth = fetch_pmonth(hr3_obs, nwsli)
        hr6_pmonth = fetch_pmonth(hr6_obs, nwsli)

        if nwsli not in moCntr:
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

        if qdict.get(nwsli, {}).get('precip', False) or _network == 'KIMT':
            phour = None
            p03i = None
            p06i = None
            pcounter = None
            pday = None

        # Finally ready to write SHEF!
        shef_fp.write(("%s %s / %4s / %4s / %4s / %5s : %s\n"
                       "") % (nwsli, pretty_tmpf(ob), pretty_precip(phour),
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
            utc = ob['valid'].astimezone(pytz.timezone("UTC"))
            fp.write(("%s,%s,%s,%s,%i,%s,%s,%s,%s\n"
                      "") % (nwsli, utc.strftime("%Y/%m/%d %H:%M:%S"),
                             getm_c(ob, 'tmpf'), getm_c(ob, 'dwpf'),
                             ob['sknt'], ob['drct'], phour or 'M',
                             pday or 'M', ob['pres']))

        if _network != 'KIMT':
            SAOFILE.write(metar(obs[nwsli]))


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
    now = SCRIPT_TIME.astimezone(pytz.timezone("UTC"))
    saoname = "IA.snet%s.sao" % (now.strftime("%d%H%M"),)
    cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % (saoname, saofn)
    subprocess.call(cmd, shell=True)
    os.unlink(saofn)

    cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('snet.csv', csvfn)
    subprocess.call(cmd, shell=True)
    os.unlink(csvfn)

    cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('kelo.csv', kelocsvfn)
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    p.stdout.read()
    os.unlink(kelocsvfn)

    if SCRIPT_TIME.minute in [15, 35]:
        cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('LOCDSMRR5DMX.dat',
                                                     locdsmfn)
        subprocess.call(cmd, shell=True)
    if SCRIPT_TIME.minute == 55:
        cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('SUADSMRR5DMX.dat',
                                                     rr5fn)
        subprocess.call(cmd, shell=True)
        cmd = "/home/ldm/bin/pqinsert -p '%s' %s" % ('SUAFSDRR5FSD.dat',
                                                     fsdrr5fn)
        subprocess.call(cmd, shell=True)
    # print locdsmfn
    # print rr5fn
    # print fsdrr5fn
    # print kimtrr5fn
    os.unlink(locdsmfn)
    os.unlink(rr5fn)
    os.unlink(fsdrr5fn)
    os.unlink(kimtrr5fn)


def loadQC():
    """
    See which sites have flags against them
    """
    qdict = {}
    pcursor = PORTFOLIO.cursor()

    pcursor.execute("""
    select s_mid, sensor, status from tt_base WHERE sensor is not null
    and status != 'CLOSED' and portfolio in ('kccisnet','kelosnet','kimtsnet')
    """)
    for row in pcursor:
        if row[0] not in qdict:
            qdict[row[0]] = {}
        if row[1].find("precip") > -1:
            qdict[row[0]]['precip'] = True

    pcursor.close()
    return qdict


def main():
    """Go"""
    qdict = loadQC()
    loadCounters()
    writeHeader()
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.timezone("UTC"))
    doNetwork('KCCI', DMXRR5, now - datetime.timedelta(minutes=60),
              qdict)
    doNetwork('KIMT', BADRR5, now - datetime.timedelta(minutes=180),
              qdict)
    doNetwork('KELO', FSDRR5, now - datetime.timedelta(minutes=300),
              qdict)

    writeCounters()
    closeFiles()
    post_process()
    # Commit postgres cursors
    PORTFOLIO.commit()
    PORTFOLIO.close()
    IEM.commit()
    IEM.close()

if __name__ == '__main__':
    main()
