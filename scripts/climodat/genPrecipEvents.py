# Generate Precip Event records!
# Daryl Herzmann 3 Mar 2004
# 30 Mar 2004	This does not need to be modified for incremental uploads
# 22 Jul 2004	Rounding Error! :(

_REPORTID = "01"
import constants 

def go(mydb, rs, stationID):
  db = {}
  for i in range(1,54): # Store climateweek values
    db[i] = {}
    db[i]["maxval"] = 0
    db[i]["maxyr"] = 0
    db[i]["total"] = 0
    db[i]["events"] = 0
    db[i]["cat1"] = 0
    db[i]["cat2"] = 0
    db[i]["cat3"] = 0
    db[i]["cat4"] = 0
    db[i]["cat5"] = 0
    db[i]["totprec"] = [0]* (constants._ENDYEAR - constants.startyear(stationID))


  for i in range(len(rs)):
    climoweek = int(rs[i]["climoweek"])
    precip = float(rs[i]["precip"])
    yr = int(rs[i]['year'])
     # First we do the CATS
    if (precip >= 0.01 and precip <= 0.25):
      db[climoweek]["cat1"] += 1
    elif (precip >= 0.26 and precip <= 0.50):
      db[climoweek]["cat2"] += 1
    elif (precip >= 0.51 and precip <= 1.00):
      db[climoweek]["cat3"] += 1
    elif (precip >= 1.01 and precip <= 2.00):
      db[climoweek]["cat4"] += 1
    elif (precip >= 2.01):
      db[climoweek]["cat5"] += 1
     # Work the Max
    if (precip > 0):
      db[climoweek]["totprec"][yr - constants.startyear(stationID)] += precip
     # Add in for the total
    db[climoweek]["total"] += precip

  annEvents = 0
  maxVal = 0
  totRain = 0
  cat1 = 0
  cat2 = 0
  cat3 = 0
  cat4 = 0
  cat5 = 0
  for i in range(1,54):
    totEvents = db[i]["cat1"] + db[i]["cat2"] + db[i]["cat3"] + \
                db[i]["cat4"] + db[i]["cat5"]
    meanRain = db[i]["total"] / totEvents
    annEvents += totEvents
    maxVal = max( db[i]['totprec'] )
    maxyr = db[i]['totprec'].index(maxVal) + constants.startyear(stationID)
    cat1 += db[i]["cat1"]
    cat2 += db[i]["cat2"]
    cat3 += db[i]["cat3"]
    cat4 += db[i]["cat4"]
    cat5 += db[i]["cat5"]
    totRain += db[i]["total"]

    mydb.query("DELETE from r_precipevents WHERE stationid = '%s' and \
     climoweek = %s" % (stationID, i) )

    mydb.query("INSERT into r_precipevents(stationid, climoweek, maxval, maxyr, \
     meanval, cat1e, cat2e, cat3e, cat4e, cat5e) values ('%s', %s, %s, %s, \
     %4.2f, %s, %s, %s, %s, %s)" % (stationID, i, maxVal, maxyr, meanRain,\
     db[i]["cat1"], db[i]["cat2"], db[i]["cat3"], db[i]["cat4"], db[i]["cat5"]))


def write(mydb, stationID):
  import cweek, constants
  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)
  out.write("""\
# Based on climoweek periods, this report summarizes liquid precipitation.
#                                     Number of precip events - (% of total)
 CL                MAX         MEAN   0.01-    0.26-    0.51-    1.01-            TOTAL
 WK TIME PERIOD    VAL  YR     RAIN     0.25     0.50     1.00     2.00    >2.01  DAYS\n""")

  rs = mydb.query("SELECT * from r_precipevents WHERE stationid = '%s'" % \
   (stationID,) ).dictresult()

  annEvents = 0
  cat1t = 0
  cat2t = 0
  cat3t = 0
  cat4t = 0
  cat5t = 0
  maxRain = 0
  totRain = 0
  for i in range(len(rs)):
    cw = int(rs[i]["climoweek"])
    cat1 = rs[i]["cat1e"]
    cat2 = rs[i]["cat2e"]
    cat3 = rs[i]["cat3e"]
    cat4 = rs[i]["cat4e"]
    cat5 = rs[i]["cat5e"]
    cat1t += cat1
    cat2t += cat2
    cat3t += cat3
    cat4t += cat4
    cat5t += cat5
    maxval = rs[i]["maxval"]
    if (maxval > maxRain): maxRain = maxval
    meanval = rs[i]["meanval"]
    totEvents = cat1 + cat2 + cat3 + cat4 + cat5
    annEvents += totEvents
    totRain += ( totEvents * meanval)

    out.write("%3s %-13s %5.2f %i   %4.2f %4i(%2i) %4i(%2i) %4i(%2i) %4i(%2i) %4i(%2i)   %4i\n" \
      % (cw, cweek.cweek[cw], \
      maxval, rs[i]['maxyr'], meanval, \
      cat1, round((float(cat1) / float(totEvents)) * 100.0), \
      cat2, round((float(cat2) / float(totEvents)) * 100.0), \
      cat3, round((float(cat3) / float(totEvents)) * 100.0), \
      cat4, round((float(cat4) / float(totEvents)) * 100.0), \
      cat5, round((float(cat5) / float(totEvents)) * 100.0), totEvents) )


  out.write("%-17s %5.2f        %4.2f %4i(%2i) %4i(%2i) %4i(%2i) %4i(%2i) %4i(%2i)   %4i\n" \
    % ("ANNUAL TOTALS", maxRain, totRain / annEvents, \
     cat1t, (float(cat1t) / float(annEvents)) * 100, \
     cat2t, (float(cat2t) / float(annEvents)) * 100, \
     cat3t, (float(cat3t) / float(annEvents)) * 100, \
     cat4t, (float(cat4t) / float(annEvents)) * 100, \
     cat5t, (float(cat5t) / float(annEvents)) * 100, annEvents) )

  out.close()
