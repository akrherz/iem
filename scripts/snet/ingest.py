
# Python Imports
import re, sys, time, telnetlib, string, math, os, shutil
import traceback
import logging
import smtplib, StringIO
from email.MIMEText import MIMEText

# 3rd Party
import mx.DateTime

# Local stuff
import nwnOB
import secret

from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']

logging.basicConfig(filename='/mesonet/data/logs/nwn.log',filemode='a')
logger=logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# Write a PID File
o = open("ingest.pid",'w')
o.write("%s" % ( os.getpid(),) )
o.close()

# Load up locs
locs = {}
rs = mesosite.query("""SELECT *, x(geom) as lon, y(geom) as lat from 
     stations WHERE network in ('KCCI', 'KELO', 'KIMT')""").dictresult()
for i in range(len(rs)):
    locs[ int(rs[i]['nwn_id']) ] = {
        'nwsli': rs[i]['id'],
        'lat': rs[i]['lat'],
        'lon': rs[i]['lon'],
        'name': rs[i]['name'],
        'tv' : rs[i]['network'],
        'routes': [rs[i]['network'], rs[i]['wfo'], 'EMAIL'],
        'county': rs[i]['county'],
    }


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

_CURRENT_RE = "[A-Z] ([0-9]?[0-9][0-9])\s+([0-2][0-9]:[0-9][0-9]) ([0-1][0-9]/[0-3][0-9]/[0-9][0-9])\s+([A-Z]{1,3})\s+([0-9][0-9])(MPH|KTS) ([0-9][0-9][0-9])[F,K] ...F (...)F ([0-9][0-9][0-9])% ([0-9]+.[0-9][0-9])([\"RFS]) ([0-9]+.[0-9][0-9])\"D ([0-9]+.[0-9][0-9])\"M"
_MAX_RE = "[A-Z] ([0-9]?[0-9][0-9])\s+(Max)\s+([0-1][0-9]/[0-3][0-9]/[0-9][0-9])\s+([A-Z]{1,3})\s+([0-9][0-9])(MPH|KTS) ([0-9][0-9][0-9])[F,K] ...F (...)F ([0-9][0-9][0-9])% ([0-9]+.[0-9][0-9])([\"RFS]) ([0-9]+.[0-9][0-9])\"D ([0-9]+.[0-9][0-9])\"M"
_MIN_RE = "[A-Z] ([0-9]?[0-9][0-9])\s+(Min)\s+([0-1][0-9]/[0-3][0-9]/[0-9][0-9])\s+([A-Z]{1,3})\s+([0-9][0-9])(MPH|KTS) ([0-9][0-9][0-9])[F,K] ...F (...)F ([0-9][0-9][0-9])% ([0-9]+.[0-9][0-9])([\"RFS]) ([0-9]+.[0-9][0-9])\"D ([0-9]+.[0-9][0-9])\"M"



def makeConnect():
    logger.info("\n ------ BEGIN makeConnect ------ \n")
    notConnected = 0
    while (notConnected == 0):
        try:
            tn = telnetlib.Telnet('127.0.0.1',14996)
            #tn = telnetlib.Telnet('129.186.26.186',14998)
            tn.read_until("login> ", 10)
            tn.write("%s\r\n" % (secret.cfg['hubuser'],) )
            tn.read_until("password> ", 10)
            tn.write("%s\r\n" % (secret.cfg['hubpass'],) )
            notConnected = 1
        except:
            logger.exception("Error in makeConnect()")
            time.sleep(58)
  
    logger.info("\n -------END makeConnect ------ \n")
    return tn

def process(dataStr):
    goodLines = ""
    lines = re.split("\015\012", dataStr)

    for line in lines:
        tokens = re.findall(_CURRENT_RE, line)
        if ( len(tokens) == 1):
            stationID = int(tokens[0][0])
            if (not db.has_key(stationID)):
                db[stationID] = nwnOB.nwnOB(stationID)
            db[stationID].valid = mx.DateTime.now()
            db[stationID].aDrctTxt.append(string.strip(tokens[0][3]))
            db[stationID].aDrct.append(txt2drct[string.strip(tokens[0][3])])
            if (tokens[0][5] == "KTS"):
                db[stationID].aSPED.append( int(tokens[0][4]) / .868976 )
            else:
                db[stationID].aSPED.append( int(tokens[0][4]) )
            if (tokens[0][7][:2] == "0-"):
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
            goodLines += line +"\n"
            continue

        tokens = re.findall(_MAX_RE, line)
        if ( len(tokens) == 1):
            stationID = int(tokens[0][0])
            if (not db.has_key(stationID)):
                db[stationID] = nwnOB.nwnOB(stationID)
            if (tokens[0][7][:2] == "0-"):
                db[stationID].maxTMPF = int(tokens[0][7][1:])
            else:
                db[stationID].maxTMPF = int(tokens[0][7])

            if (tokens[0][5] == "KTS"):
                db[stationID].setGust( int(tokens[0][4]) / .868976 )
            else:
                db[stationID].setGust( int(tokens[0][4]) )
            db[stationID].maxDrctTxt = tokens[0][3]
            db[stationID].maxSRAD = int(tokens[0][6])
            db[stationID].maxALTI = float(tokens[0][9])
            db[stationID].maxRELH = int(tokens[0][8])
            db[stationID].maxLine = line
            goodLines += line +"\n"
            continue

        tokens = re.findall(_MIN_RE, line)
        if ( len(tokens) == 1):
            stationID = int(tokens[0][0])
            if (not db.has_key(stationID)):
                db[stationID] = nwnOB.nwnOB(stationID)
            if (tokens[0][6][:2] == "0-"):
                db[stationID].minTMPF = int(tokens[0][6][1:])
            else:
                db[stationID].minTMPF = int(tokens[0][6])
            db[stationID].minALTI = float(tokens[0][8])
            if (tokens[0][7][:2] == "0-"):
              db[stationID].minRELH = int(tokens[0][7][1:])
            else:
              db[stationID].minRELH = int(tokens[0][7])
            goodLines += line +"\n"
            db[stationID].minLine = line
            continue

        rejects.write("%s\n" % (line,) )
    return goodLines

def archiveWriter():
    for id in db.keys():
        #logger.write("WRITE ID: %s\n"% (id,) )
        # No obs during this period
        if (db[id].valid == None): continue

        if (db[id].maxSPED == None): db[id].maxSPED = 0
        dir = "%s/%s" % (_ARCHIVE_BASE, db[id].valid.strftime("%Y_%m/%d") )
        if (not os.path.isdir(dir)):
            os.makedirs(dir, 0775)
        fp = "%s/%s.dat" % (dir, id)
        out = open(fp, 'a')
        out.write("%s,%s,%02iMPH,%03iK,460F,%03iF,%03i%s,%5.2f%s,%05.2f\"D,%05.2f\"M,%05.2f\"R,%s,\n" % ( db[id].valid.strftime("%H:%M,%m/%d/%y"), db[id].drctTxt, \
        db[id].sped, db[id].srad, \
        db[id].tmpf, db[id].relh, "%", db[id].alti, db[id].ptend, \
        db[id].pDay, db[id].pMonth, db[id].pRate, db[id].maxSPED ) )
        out.close()

def test():
    for stationID in db.keys():
        print stationID, db[stationID].sped, db[stationID].aSPED, db[stationID].aDrctTxt, db[stationID].drctTxt, db[stationID].valid, db[stationID].maxSPED, db[stationID].maxSPED_ts
    print "----"

def averageWinds():
    for id in db.keys():
        db[id].avgWinds()

def sendWindAlert(id, alertSPED, alertDrctTxt, myThreshold):
    if id in [904, 75, 907, 918, 9, 913]:
        return
    if (not locs.has_key(id)):
        logger.info("\nCan't Alert ID: %s\n" % (id,) )
        return
    form = {}
    form["threshold"] = myThreshold
    form["sname"] = locs[id]["name"]
    form["lat"] = locs[id]["lat"]
    form["lon"] = locs[id]["lon"]
    form["nwsli"] = locs[id]["nwsli"]
    form["county"] = locs[id]["county"]
    form["obts"] = db[id].valid.strftime("%Y-%m-%d %I:%M %p")
    form["shortts"] = db[id].valid.strftime("%I:%M %p")
    form["shefdate"] = db[id].valid.strftime("%m%d")
    form["sheftime"] = db[id].valid.strftime("%H%M")
    try:
        form["gustts"] = db[id].maxSPED_ts.strftime("%I:%M %p")
    except:
        form["gustts"] = "Unknown"
    form["tmpf"] = db[id].tmpf
    form["dwpf"] = "None"
    form["pDay"] = db[id].pDay
    form["gust"] = db[id].maxSPED
    form["drct"] = db[id].maxDrctTxt
    form["alertSPED"] = alertSPED
    form["alertDrctTxt"] = alertDrctTxt
    form["lastts"] = "Undefined"
    if (db[id].lvalid != None):
        form["lastts"] = db[id].lvalid.strftime("%d %b %Y %I:%M %p")
    form["warning"] = ""
    if ( db[id].sinceLastObInMinutes() > 10):
        form["warning"] = "\n: WARNING: First ob since %s [ %s minutes ]. Perhaps Offline?" % (form["lastts"], db[id].sinceLastObInMinutes(), )

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

    for i in range(len(db[id].aSPED)):
        report += ":    %s MPH from the %s\n" % (db[id].aSPED[i], db[id].aDrctTxt[i])

    for route in locs[id]["routes"]:
        form["route"] = route
        fireLDM(report % form, route, id)
        if (len(route) == 3):
            if (route == "DSM"):
                form['route'] = "DMX"


def fireLDM(report, route, id):
    logger.info("Route! %s" % (route,))
    fname = "LOC%sSVRWX.dat" % (route,)
    fp = open("/tmp/"+fname, 'w')
    fp.write(report)
    fp.close()
    logger.info( report )
    try:
        #if (route != "KELO" and route != "KCCI"):
        os.system("/home/ldm/bin/pqinsert -p '%s' /tmp/%s" %(fname,fname) )
    except:
        logger.exception("Trouble inserting Alert!")

    # Save a copy of this alert!
    shutil.copy("/tmp/"+fname, "alerts/%s_%s_%s" \
                % (mx.DateTime.now().strftime("%Y%m%d%H%M%S"), id, fname) )

#==================================================
def windGustAlert():
    for id in db.keys():
        myThreshold = _WIND_THRESHOLD
        if (id == 84 or id == 40 or id == 9 or id == 78 or id == 49):
            myThreshold += 7
        if (id == 49 or id == 618 or id == 1):
            myThreshold += 40
        # If no obs during this period, no alerts
        # If no obs during this period, no alerts
        if (db[id].valid == None): continue

        # If the max gust is greater than the threshold, we consider
        if (db[id].maxSPED != None and db[id].maxSPED >= myThreshold):
            # We also need this maxGust to be greater than previously warned
            if (db[id].windGustAlert != None and \
            db[id].maxSPED > db[id].windGustAlert):
                # Set the value for the last alert generated!
                db[id].windGustAlert = db[id].maxSPED
                sendWindAlert(id, db[id].maxSPED, db[id].maxDrctTxt, myThreshold)
                continue
            # If the windGustAlert is None, then we should alert too
            if (db[id].windGustAlert == None):
                # Set the value for the last alert generated!
                db[id].windGustAlert = db[id].maxSPED
                sendWindAlert(id, db[id].maxSPED, db[id].maxDrctTxt, myThreshold)
                continue

        # We will always alert in this situation
        if (len(db[id].aSPED) > 0) and (max(db[id].aSPED) >= myThreshold):
            # We need to find the max wind speed direction
            for pos in range(len(db[id].aSPED)):
                if (max(db[id].aSPED) == db[id].aSPED[pos]):
                    alertDrctTxt = db[id].aDrctTxt[pos]
                    db[id].maxDrctTxt = alertDrctTxt
                    db[id].maxSPED_ts = db[id].valid
            sendWindAlert(id, max(db[id].aSPED), alertDrctTxt, myThreshold)



def clearObs():
    for id in db.keys():
        if (db[id].valid != None): # We got obs!
            db[id].lvalid = db[id].valid
            db[id].valid = None
            db[id].aSPED = []
            db[id].aDrctTxt = []
            db[id].aDrct = []

def main():
    tn = makeConnect()
    counter = 1
    dryRun = 0
    dataStr = ""

    while (counter > 0):
        #s = mx.DateTime.now()
        if (counter % 15 == 0):
            saveDB()
        dataStr = tn.read_very_eager()
        goodLines = process(dataStr)
        if (len(goodLines) < 100):
            dryRun += 1
            logger.info("dryRun Set to: %s" % (dryRun,) )
        else:
            dryRun = 0
        if (dryRun > 2):
            logger.info(" ABORT ABORT")
            raise "ZZZZZZZ"
        averageWinds()
        windGustAlert()
        #test()
        #archiveWriter()
        logData(goodLines)
        archiveWriter()
        counter += 1
        time.sleep(58)
        # Run me last!
        clearObs()
        #e = mx.DateTime.now()
        #logger.warn("%s -- %s" % (counter, (e -s) / 1.000) )

def loadDB():
    if not os.path.isfile("db.p"):
        return
    import pickle
    global db
    db = pickle.load( open('db.p') )

def saveDB():
    import pickle
    pickle.dump(db, open('db.p', 'w'))

def logData(goodLines):
    try:
        now = mx.DateTime.now()
        f = open("/mesonet/data/logs/snet.log", 'a')
        f.write( goodLines )
        f.write("||"+ str( now ) +"||\n")
        f.close()
    except:
        logger.exception("\nCould not write Log\n")


MAXEMAILS = 10

if (__name__ == "__main__"):
    loadDB()
    running = 1
    while(running):
        try:
            logger.info("GO MAIN GO!")
            main()
        except KeyboardInterrupt:
            saveDB()
            running = 0
        except:
            logger.exception("Uh oh!")

            io = StringIO.StringIO()
            traceback.print_exc(file=io)

            msg = MIMEText("%s"% (io.getvalue(),) )
            msg['subject'] = 'NWN ingest.py Traceback'
            msg['From'] = "ldm@mesonet.agron.iastate.edu"
            msg['To'] = "akrherz@iastate.edu"

            if (MAXEMAILS > 0):
                s = smtplib.SMTP()
                s.connect()
                s.sendmail(msg["From"], msg["To"], msg.as_string())
                s.close()
            MAXEMAILS -= 1



    rejects.close()

