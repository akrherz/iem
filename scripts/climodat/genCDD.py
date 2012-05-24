"""
Cooling Degree days
"""

_REPORTID = "19"

def ccdd(high, low, base):
    cdd = 0
    try:
        a = float(int(high) + int(low)) / 2.00
    except:
        return 0
    if a > base:
        cdd = a - base

    return cdd  

def go(mydb, rs, stationID, updateAll=False):
    import mx.DateTime, constants
    if updateAll:
        s = constants.startts(stationID)
    else:
        s = constants._ENDTS - mx.DateTime.RelativeDateTime(years=1)
    e = constants._ENDTS
    interval = mx.DateTime.RelativeDateTime(months=+1)

    now = s
    db = {}
    db60 = {}
    while (now < e):
        db[now] = 0
        db60[now] = 0
        now += interval

    for i in range(len(rs)):
        ts = mx.DateTime.strptime( rs[i]["day"] , "%Y-%m-%d")
        if ts < s:
            continue
        mo = ts + mx.DateTime.RelativeDateTime(day=1)
        db[mo] += ccdd(rs[i]["high"], rs[i]["low"], 65.0)
        db60[mo] += ccdd(rs[i]["high"], rs[i]["low"], 60.0)

    for mo in db.keys():
        mydb.query("""UPDATE r_monthly SET cdd = %s, cdd60 = %s WHERE 
          station = '%s' and monthdate = '%s' """ % (db[mo], db60[mo],
                                    stationID, mo.strftime("%Y-%m-%d") ) )

def write(mydb, stationID):
    import mx.DateTime, constants
    YRCNT = constants.yrcnt(stationID)
    out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
    constants.writeheader(out, stationID)
    out.write("""# THESE ARE THE MONTHLY COOLING DEGREE DAYS (base=65) %s-%s FOR STATION  %s
YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    SEP    OCT    NOV    DEC\n""" % (
            constants.startyear(stationID), constants._ENDYEAR, stationID,) )

    rs = mydb.query("""SELECT * from r_monthly WHERE station = '%s'""" % (
                                        stationID,) ).dictresult()
    db = {}
    db60 = {}
    for i in range(len(rs)):
        mo = mx.DateTime.strptime( rs[i]["monthdate"], "%Y-%m-%d")
        db[mo] = rs[i]["cdd"]
        db60[mo] = rs[i]["cdd60"]

    moTot = {}
    moTot60 = {}
    for mo in range(1,13):
        moTot[mo] = 0
        moTot60[mo] = 0

    second = """# THESE ARE THE MONTHLY COOLING DEGREE DAYS (base=60) %s-%s FOR STATION  %s
YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    SEP    OCT    NOV    DEC\n""" % (
            constants.startyear(stationID), constants._ENDYEAR, stationID,)
    yrCnt = 0
    for yr in range(constants.startyear(stationID), constants._ENDYEAR):
        yrCnt += 1
        out.write("%4i" % (yr,) )
        second += "%4i" % (yr,)
        for mo in range(1, 13):
            ts = mx.DateTime.DateTime(yr, mo, 1)
            if (ts >= constants._ARCHIVEENDTS):
                out.write("%7s" % ("M",) )
                second += "%7s" % ("M",)
                continue
            if (ts < constants._ARCHIVEENDTS):
                moTot[mo] += db[ts]
                moTot60[mo] += db60[ts]
            out.write("%7.0f" % (db[ts],) )
            second += "%7.0f" % (db60[ts],)
        out.write("\n")
        second += "\n"

    out.write("MEAN")
    second += "MEAN"
    for mo in range(1, 13):
        out.write("%7.0f" % ( float(moTot[mo]) / float( YRCNT[mo] ) ) )
        second += "%7.0f" % ( float(moTot60[mo]) / float( YRCNT[mo] ) ) 
    out.write("\n")
    second += "\n"
    out.write(second)
    out.close()

