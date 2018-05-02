"""Ingest the SchoolNet data coming via the NWN socket feed

    1) Ingest data into per station per day text files
    2) Send wind alerts
"""
from __future__ import print_function
# Python Imports
import re
import time
import datetime
import telnetlib
import os
import shutil
import traceback
import logging
import smtplib
from io import StringIO
from email.mime.text import MIMEText

import psycopg2.extras
from pyiem.util import get_dbconn

# Local stuff
import nwnob  # @UnresolvedImport
import secret  # @UnresolvedImport

MESOSITE = get_dbconn('mesosite')
mcursor = MESOSITE.cursor(cursor_factory=psycopg2.extras.DictCursor)

logging.basicConfig(filename='/mesonet/data/logs/nwn.log', filemode='a')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# Load up locs
locs = {}
mcursor.execute("""
    SELECT nwn_id, id, ST_x(geom) as lon, ST_y(geom) as lat, name,
    network, wfo, county from stations
    WHERE network in ('KCCI', 'KELO', 'KIMT') and nwn_id is not null
    """)
for row in mcursor:
    locs[int(row['nwn_id'])] = {
        'nwsli': row['id'],
        'lat': row['lat'],
        'lon': row['lon'],
        'name': row['name'],
        'tv': row['network'],
        'routes': [row['network'], row['wfo'], 'EMAIL'],
        'county': row['county'],
    }
MESOSITE.close()

rejects = open("/mesonet/data/logs/rejects.log", 'w')

db = {}
_WIND_THRESHOLD = 58
_ARCHIVE_BASE = "/mesonet/ARCHIVE/raw/snet/"
_CURRENT_BASE = "/mesonet/data/current/"

txt2drct = {
 'N': 360, 'NNE': 25, 'NE': 45, 'ENE': 70,
 'E': 90, 'ESE': 115, 'SE': 135, 'SSE': 155,
 'S': 180, 'SSW': 205, 'SW': 225, 'WSW': 250,
 'W': 270, 'WNW': 295, 'NW': 315, 'NNW': 335}

_CURRENT_RE = ("[A-Z] ([0-9]?[0-9][0-9])\s+([0-2][0-9]:[0-9][0-9]) "
               "([0-1][0-9]/[0-3][0-9]/[0-9][0-9])\s+([A-Z]{1,3})\s+"
               "([0-9][0-9])(MPH|KTS) ([0-9][0-9][0-9])[F,K] ...F "
               "([0-9\-]{3})F ([0-9][0-9][0-9])% ([0-9]+.[0-9][0-9])"
               "([\"RFS]) ([0-9]+.[0-9][0-9])\"D ([0-9]+.[0-9][0-9])\"M")
_MAX_RE = ("[A-Z] ([0-9]?[0-9][0-9])\s+(Max)\s+([0-1][0-9]/[0-3][0-9]/"
           "[0-9][0-9])\s+([A-Z]{1,3})\s+([0-9][0-9])(MPH|KTS) "
           "([0-9][0-9][0-9])[F,K] ...F (...)F ([0-9][0-9][0-9])% "
           "([0-9]+.[0-9][0-9])([\"RFS]) ([0-9]+.[0-9][0-9])\"D "
           "([0-9]+.[0-9][0-9])\"M")
_MIN_RE = ("[A-Z] ([0-9]?[0-9][0-9])\s+(Min)\s+([0-1][0-9]/"
           "[0-3][0-9]/[0-9][0-9])\s+([A-Z]{1,3})\s+([0-9][0-9])(MPH|KTS) "
           "([0-9][0-9][0-9])[F,K] ...F (...)F ([0-9][0-9][0-9])% "
           "([0-9]+.[0-9][0-9])([\"RFS]) ([0-9]+.[0-9][0-9])\"D "
           "([0-9]+.[0-9][0-9])\"M")


def makeConnect():
    logger.info("\n ------ BEGIN makeConnect ------ \n")
    notConnected = True
    while notConnected:
        try:
            tn = telnetlib.Telnet('iem-nwnserver', 14996)
            tn.read_until(b"login> ", 10)
            tn.write("%s\r\n" % (secret.cfg['hubuser'],))
            tn.read_until(b"password> ", 10)
            tn.write("%s\r\n" % (secret.cfg['hubpass'],))
            notConnected = False
        except Exception as _exp:
            logger.exception("Error in makeConnect()")
            time.sleep(58)

    logger.info("\n -------END makeConnect ------ \n")
    return tn


def process(dataStr):
    goodLines = ""
    lines = re.split("\015\012", dataStr)

    for line in lines:
        tokens = re.findall(_CURRENT_RE, line)
        if len(tokens) == 1:
            stationID = int(tokens[0][0])
            if stationID not in db:
                db[stationID] = nwnob.nwnOB(stationID)
            db[stationID].valid = datetime.datetime.now()
            db[stationID].aDrctTxt.append(tokens[0][3].strip())
            db[stationID].aDrct.append(txt2drct[tokens[0][3].strip()])
            if tokens[0][5] == "KTS":
                db[stationID].aSPED.append(int(tokens[0][4]) / .868976)
            else:
                db[stationID].aSPED.append(int(tokens[0][4]))
            if tokens[0][7][:2] == "0-":
                db[stationID].tmpf = int(tokens[0][7][1:])
            else:
                db[stationID].tmpf = int(tokens[0][7])
            db[stationID].srad = int(tokens[0][6])
            db[stationID].relh = int(tokens[0][8])
            db[stationID].alti = float(tokens[0][9])
            db[stationID].ptend = tokens[0][10]
            db[stationID].pDay = float(tokens[0][11])
            db[stationID].pMonth = float(tokens[0][12])
            db[stationID].pRate = 0.00
#            db[stationID].valid = mx.DateTime.strptime( \
#                tokens[0][1] +" "+ tokens[0][2], "%H:%M %m/%d/%y")
            goodLines += line + "\n"
            continue

        tokens = re.findall(_MAX_RE, line)
        if len(tokens) == 1:
            stationID = int(tokens[0][0])
            if stationID not in db:
                db[stationID] = nwnob.nwnOB(stationID)
            if (tokens[0][7][:2] == "0-"):
                db[stationID].maxTMPF = int(tokens[0][7][1:])
            else:
                db[stationID].maxTMPF = int(tokens[0][7])

            if (tokens[0][5] == "KTS"):
                db[stationID].setGust(int(tokens[0][4]) / .868976)
            else:
                db[stationID].setGust(int(tokens[0][4]))
            db[stationID].maxDrctTxt = tokens[0][3]
            db[stationID].maxSRAD = int(tokens[0][6])
            db[stationID].maxALTI = float(tokens[0][9])
            db[stationID].maxRELH = int(tokens[0][8])
            db[stationID].maxLine = line
            goodLines += line + "\n"
            continue

        tokens = re.findall(_MIN_RE, line)
        if len(tokens) == 1:
            stationID = int(tokens[0][0])
            if stationID not in db:
                db[stationID] = nwnob.nwnOB(stationID)
            if (tokens[0][7][:2] == "0-"):
                db[stationID].minTMPF = int(tokens[0][7][1:])
            else:
                db[stationID].minTMPF = int(tokens[0][7])
            db[stationID].minALTI = float(tokens[0][9])
            db[stationID].minRELH = int(tokens[0][8])
            goodLines += line + "\n"
            db[stationID].minLine = line
            continue

        rejects.write("%s\n" % (line,))
    return goodLines


def archiveWriter():
    """archive writer"""
    for sid in db.keys():
        # No obs during this period
        if db[sid].valid is None:
            continue

        if db[sid].maxSPED is None:
            db[sid].maxSPED = 0
        mydir = "%s/%s" % (_ARCHIVE_BASE, db[sid].valid.strftime("%Y_%m/%d"))
        if not os.path.isdir(mydir):
            os.makedirs(mydir, 0o775)
        fp = "%s/%s.dat" % (mydir, sid)
        out = open(fp, 'a')
        out.write(("%s,%s,%02iMPH,%03iK,460F,%03iF,%03i%s,%5.2f"
                   "%s,%05.2f\"D,%05.2f\"M,%05.2f\"R,%s,\n") % (
            db[sid].valid.strftime("%H:%M,%m/%d/%y"), db[sid].drctTxt,
            db[sid].sped, db[sid].srad,
            db[sid].tmpf, db[sid].relh, "%", db[sid].alti, db[sid].ptend,
            db[sid].pDay, db[sid].pMonth, db[sid].pRate, db[sid].maxSPED))
        out.close()


def averageWinds():
    for sid in db.keys():
        db[sid].avgWinds()


def sendWindAlert(sid, alertSPED, alertDrctTxt, myThreshold):
    if sid in [904, 75, 907, 918, 9, 913, 924, 610, 619, 60]:
        return
    if sid not in locs:
        logger.info("\nCan't Alert ID: %s\n" % (sid,))
        return
    # Unreliable....
    if locs[sid]['tv'] == 'KIMT':
        return
    form = {}
    form["threshold"] = myThreshold
    form["sname"] = locs[sid]["name"]
    form["lat"] = locs[sid]["lat"]
    form["lon"] = locs[sid]["lon"]
    form["nwsli"] = locs[sid]["nwsli"]
    form["county"] = locs[sid]["county"]
    form["obts"] = db[sid].valid.strftime("%Y-%m-%d %I:%M %p")
    form["shortts"] = db[sid].valid.strftime("%I:%M %p")
    form["shefdate"] = db[sid].valid.strftime("%m%d")
    form["sheftime"] = db[sid].valid.strftime("%H%M")
    try:
        form["gustts"] = db[sid].maxSPED_ts.strftime("%I:%M %p")
    except Exception as _exp:
        form["gustts"] = "Unknown"
    form["tmpf"] = db[sid].tmpf
    form["dwpf"] = "None"
    form["pDay"] = db[sid].pDay
    form["gust"] = db[sid].maxSPED
    form["drct"] = db[sid].maxDrctTxt
    form["alertSPED"] = alertSPED
    form["alertDrctTxt"] = alertDrctTxt
    form["lastts"] = "Undefined"
    if db[sid].lvalid is None:
        form["lastts"] = db[sid].lvalid.strftime("%d %b %Y %I:%M %p")
    form["warning"] = ""
    if db[sid].sinceLastObInMinutes() > 10:
        form["warning"] = ("\n: WARNING: First ob since %s [ %s minutes ]. "
                           "Perhaps Offline?"
                           ) % (form["lastts"],
                                db[sid].sinceLastObInMinutes())

    # Need three blank lines for the SHEF header to be printed if needed
    report = """


.A %(nwsli)s %(shefdate)s  C DH%(sheftime)s/UG %(alertSPED)s
: IEM [%(route)s] Wind Gust Alert %(alertSPED)s MPH for %(sname)s
:    [Threshold: %(threshold)s MPH] %(warning)s
: Details:
:    Site:  %(sname)s  [%(nwsli)s] %(lat)s %(lon)s
:    Latest Observation @ %(obts)s
:    Alert Gust: %(alertSPED)s from the %(alertDrctTxt)s
:    Air Temp : %(tmpf)s [F]  Rain Today: %(pDay)s [inch]
:    Today's Max Gust:  %(gust)s MPH from the %(drct)s @ %(gustts)s
: All Wind Obs since last ob at: %(lastts)s
"""

    for i in range(len(db[sid].aSPED)):
        report += ":    %s MPH from the %s\n" % (db[sid].aSPED[i],
                                                 db[sid].aDrctTxt[i])

    for route in locs[sid]["routes"]:
        form["route"] = route
        fireLDM(report % form, route, sid)
        if len(route) == 3 and route == "DSM":
            form['route'] = "DMX"


def fireLDM(report, route, sid):
    """Fire LDM"""
    logger.info("Route! %s" % (route,))
    fname = "LOC%sSVRWX.dat" % (route,)
    fp = open("/tmp/"+fname, 'w')
    fp.write(report)
    fp.close()
    logger.info(report)
    try:
        # if (route != "KELO" and route != "KCCI"):
        os.system("/home/ldm/bin/pqinsert -p '%s' /tmp/%s" % (
                                        fname.replace('DMX', 'DSM'), fname))
    except Exception as _exp:
        logger.exception("Trouble inserting Alert!")

    # Save a copy of this alert!
    shutil.copy("/tmp/"+fname, "/mesonet/data/alerts/%s_%s_%s" % (
        datetime.datetime.now().strftime("%Y%m%d%H%M%S"), sid, fname))


def windGustAlert():
    for sid in db.keys():
        myThreshold = _WIND_THRESHOLD
        if sid in [84, 40, 9, 78, 49]:
            myThreshold += 7
        if sid in [49, 618, 1]:
            myThreshold += 40
        # If no obs during this period, no alerts
        # If no obs during this period, no alerts
        if db[sid].valid is None:
            continue

        # If the max gust is greater than the threshold, we consider
        if db[sid].maxSPED is not None and db[sid].maxSPED >= myThreshold:
            # We also need this maxGust to be greater than previously warned
            if (db[sid].windGustAlert is not None and
                    db[sid].maxSPED > db[sid].windGustAlert):
                # Set the value for the last alert generated!
                db[sid].windGustAlert = db[sid].maxSPED
                sendWindAlert(sid, db[sid].maxSPED, db[sid].maxDrctTxt,
                              myThreshold)
                continue
            # If the windGustAlert is None, then we should alert too
            if db[sid].windGustAlert is None:
                # Set the value for the last alert generated!
                db[sid].windGustAlert = db[sid].maxSPED
                sendWindAlert(sid, db[sid].maxSPED, db[sid].maxDrctTxt,
                              myThreshold)
                continue

        # We will always alert in this situation
        if (len(db[sid].aSPED) > 0) and (max(db[sid].aSPED) >= myThreshold):
            # We need to find the max wind speed direction
            for pos in range(len(db[sid].aSPED)):
                if (max(db[sid].aSPED) == db[sid].aSPED[pos]):
                    alertDrctTxt = db[sid].aDrctTxt[pos]
                    db[sid].maxDrctTxt = alertDrctTxt
                    db[sid].maxSPED_ts = db[sid].valid
            sendWindAlert(sid, max(db[sid].aSPED), alertDrctTxt, myThreshold)


def clearObs():
    for sid in db.keys():
        if db[sid].valid is not None:  # We got obs!
            db[sid].lvalid = db[sid].valid
            db[sid].valid = None
            db[sid].aSPED = []
            db[sid].aDrctTxt = []
            db[sid].aDrct = []


def main():
    """Go Main Go"""
    tn = makeConnect()
    counter = 1
    dryRun = 0
    dataStr = ""

    while counter > 0:
        if counter % 15 == 0:
            saveDB()
        dataStr = tn.read_very_eager()
        goodLines = process(dataStr)
        if len(goodLines) < 100:
            dryRun += 1
            logger.info("dryRun Set to: %s" % (dryRun,))
        else:
            dryRun = 0
        if dryRun > 2:
            logger.info(" ABORT ABORT")
            raise Exception("ZZZZZZZ")
        averageWinds()
        windGustAlert()
        logData(goodLines)
        archiveWriter()
        counter += 1
        time.sleep(58)
        # Run me last!
        clearObs()


def loadDB():
    """load db"""
    if not os.path.isfile("db.p"):
        return
    import pickle
    global db
    db = pickle.load(open('db.p'))


def saveDB():
    """save db"""
    import pickle
    pickle.dump(db, open('db.p', 'w'))


def logData(goodLines):
    try:
        now = datetime.datetime.now()
        f = open("/mesonet/data/logs/snet.log", 'a')
        f.write(goodLines)
        f.write("||" + str(now) + "||\n")
        f.close()
    except Exception as _exp:
        logger.exception("\nCould not write Log\n")


MAXEMAILS = 10

if __name__ == "__main__":
    loadDB()
    running = True
    while running:
        try:
            logger.info("GO MAIN GO!")
            main()
        except KeyboardInterrupt:
            saveDB()
            running = False
        except Exception as _exp:
            logger.exception("Uh oh!")

            io = StringIO()
            traceback.print_exc(file=io)

            msg = MIMEText("%s" % (io.getvalue(),))
            msg['subject'] = 'NWN ingest.py Traceback'
            msg['From'] = "ldm@mesonet.agron.iastate.edu"
            msg['To'] = "akrherz@iastate.edu"

            if MAXEMAILS > 0:
                s = smtplib.SMTP()
                s.connect()
                s.sendmail(msg["From"], msg["To"], msg.as_string())
                s.close()
            MAXEMAILS -= 1

    rejects.close()
