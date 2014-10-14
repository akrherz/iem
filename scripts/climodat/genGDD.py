# GDD module
# Daryl Herzmann 4 Mar 2004

import mx.DateTime
import constants
import numpy as np


def write(monthly_rows, out, station):
    out.write("# GROWING DEGREE DAYS FOR 4 BASE TEMPS FOR STATION ID %s\n" % (
                                                    station,) )

    monthly = [0]*13
    for i in range(13):
        monthly[i] = {'40': [],
                      '48': [],
                      '50': [],
                      '52': []
                      }

    db = {}
    for row in monthly_rows:
        ts = mx.DateTime.DateTime( int(row['year']), int(row['month']), 1)
        db[ts] = {40: float(row["gdd40"]), 
                  48: float(row["gdd48"]), 
                  50: float(row["gdd50"]), 
                  52: float(row["gdd52"])}
        monthly[ts.month]['40'].append(float(row['gdd40']))
        monthly[ts.month]['48'].append(float(row['gdd48']))
        monthly[ts.month]['50'].append(float(row['gdd50']))
        monthly[ts.month]['52'].append(float(row['gdd52']))


    modMonth(station, out, db, monthly, 3, 4, "MARCH", "APRIL")
    modMonth(station, out, db, monthly, 5, 6, "MAY", "JUNE")
    modMonth(station, out, db, monthly, 7, 8, "JULY", "AUGUST")
    modMonth(station, out, db, monthly, 9, 10, "SEPTEMBER", "OCTOBER")

def modMonth(stationID, out, db, monthly, mo1, mo2, mt1, mt2):
    out.write("""\n               %-12s                %-12s
     ****************************  *************************** 
 YEAR  40-86  48-86  50-86  52-86   40-86  48-86  50-86  52-86  
     ****************************  *************************** \n""" \
   % (mt1, mt2))
    s = constants.startts(stationID)
    e = constants._ARCHIVEENDTS
    interval = mx.DateTime.RelativeDateTime(years=+1)
    now = s
    while (now < e):
        m1 = now + mx.DateTime.RelativeDateTime(month=mo1)
        m2 = now + mx.DateTime.RelativeDateTime(month=mo2)
        if (m1 >= constants._ARCHIVEENDTS):
            db[m1] = {40: 'M', 48: 'M', 50: 'M', 52: 'M'}
        if (m2 >= constants._ARCHIVEENDTS):
            db[m2] = {40: 'M', 48: 'M', 50: 'M', 52: 'M'}
        out.write("%5i%7s%7s%7s%7s%7s%7s%7s%7s\n" % (now.year, 
                db[m1][40], db[m1][48], db[m1][50], db[m1][52], 
                db[m2][40], db[m2][48], db[m2][50], db[m2][52]) )
        now += interval

    out.write("     ****************************  ****************************\n")
    out.write(" MEAN%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f\n" % (
            np.average(monthly[mo1]["40"]),
            np.average(monthly[mo1]["48"]),
            np.average(monthly[mo1]["50"]),
            np.average(monthly[mo1]["52"]),
            np.average(monthly[mo2]["40"]),
            np.average(monthly[mo2]["48"]),
            np.average(monthly[mo2]["50"]),
            np.average(monthly[mo2]["52"])))
    out.write(" STDV%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f%7.1f\n" % (
            np.std(monthly[mo1]["40"]),
            np.std(monthly[mo1]["48"]),
            np.std(monthly[mo1]["50"]),
            np.std(monthly[mo1]["52"]),
            np.std(monthly[mo2]["40"]),
            np.std(monthly[mo2]["48"]),
            np.std(monthly[mo2]["50"]),
            np.std(monthly[mo2]["52"])))
