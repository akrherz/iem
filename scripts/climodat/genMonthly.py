import mx.DateTime
import constants

def safePrint(val, cols, prec):
    ''' Safe print function '''
    fmt = "%%%s.%sf" % (cols, prec)
    fmt2 = "%%%ss" % (cols,)
    if val == "M":
        return fmt2 % val
    return fmt % val

def write(monthly_rows, out, out2, out3, out4, station):
    s = constants.startts(station)
    e = constants._ENDTS
    YRCNT = constants.yrcnt(station)
    YEARS = e.year - s.year + 1
    interval = mx.DateTime.RelativeDateTime(months=+1)

    now = s
    db = {}
    while (now < e):
        db[now] = {"avg_high": "M", "avg_low": "M", "rain": "M"}
        now += interval

    for row in monthly_rows:
        ts = mx.DateTime.DateTime(row['year'], row['month'], 1)
        db[ts] = {'avg_high': row['avg_high'], 'avg_low': row['avg_low'],
                  'rain': row['sum_precip']}


    out.write("""# Monthly Average High Temperatures [F]
YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC   ANN
""")

    moTot = {}
    for mo in range(1,13):
        moTot[mo] = 0
    yrCnt = 0
    yrAvg = 0
    for yr in range(constants.startyear(station), constants._ENDYEAR):
        yrCnt += 1
        out.write("%4i" % (yr,) )
        yrSum = 0
        for mo in range(1, 13):
            ts = mx.DateTime.DateTime(yr, mo, 1)
            if (ts < constants._ARCHIVEENDTS):
                moTot[mo] += int(db[ts]["avg_high"])
                yrSum += int(db[ts]["avg_high"])
            out.write( safePrint( db[ts]["avg_high"], 6, 0) )
        if yr != constants._ARCHIVEENDTS.year:
            yrAvg += float(yrSum) / 12.0
            out.write("%6.0f\n" % ( float(yrSum) / 12.0, ) )
        else:
            out.write("      \n")

    out.write("MEAN")
    for mo in range(1,13):
        moAvg = moTot[mo] / float( YRCNT[mo])
        out.write("%6.0f" % (moAvg,) )

    out.write("%6.0f\n" % (yrAvg / (float(YEARS)),) )
  


    out2.write("""# Monthly Average Low Temperatures [F]
YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC   ANN
""")

    moTot = {}
    for mo in range(1,13):
        moTot[mo] = 0
    yrCnt = 0
    yrAvg = 0
    for yr in range(constants.startyear(station), constants._ENDYEAR):
        yrCnt += 1
        out2.write("%4i" % (yr,) )
        yrSum = 0
        for mo in range(1, 13):
            ts = mx.DateTime.DateTime(yr, mo, 1)
            if (ts < constants._ARCHIVEENDTS):
                moTot[mo] += int(db[ts]["avg_low"])
                yrSum += int(db[ts]["avg_low"])
            out2.write( safePrint( db[ts]["avg_low"], 6, 0) )
        if yr != constants._ARCHIVEENDTS.year:
            yrAvg += float(yrSum) / 12.0
            out2.write("%6.0f\n" % ( float(yrSum) / 12.0, ) )
        else:
            out2.write("     M\n")

    out2.write("MEAN")
    for mo in range(1,13):
        moAvg = moTot[mo] / float( YRCNT[mo])
        out2.write("%6.0f" % (moAvg,) )

    out2.write("%6.0f\n" % (yrAvg / float(YEARS),) )
  
    out3.write("""# Monthly Average Temperatures [F] (High + low)/2
YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC   ANN
""")

    moTot = {}
    for mo in range(1,13):
        moTot[mo] = 0
    yrCnt = 0
    yrAvg = 0
    for yr in range(constants.startyear(station), constants._ENDYEAR):
        yrCnt += 1
        out3.write("%4i" % (yr,) )
        yrSum = 0
        for mo in range(1, 13):
            ts = mx.DateTime.DateTime(yr, mo, 1)
            if (ts >= constants._ARCHIVEENDTS):
                out3.write("%6s" % ("M",))
                continue
            v = (float(db[ts]["avg_high"]) + float(db[ts]["avg_low"])) / 2.0
            if (ts < constants._ARCHIVEENDTS):
                moTot[mo] += v
                yrSum += v
            out3.write("%6.0f" % ( v, ) )
        if yr != constants._ARCHIVEENDTS.year:
            yrAvg += float(yrSum) / 12.0
            out3.write("%6.0f\n" % ( float(yrSum) / 12.0, ) )
        else:
            out3.write("     M\n")

    out3.write("MEAN")
    for mo in range(1,13):
        moAvg = moTot[mo] / float( YRCNT[mo] )
        out3.write("%6.0f" % (moAvg,) )

    out3.write("%6.0f\n" % (yrAvg / float(yrCnt),) )

    out4.write("""# Monthly Liquid Precip Totals [inches] (snow is melted)
YEAR   JAN   FEB   MAR   APR   MAY   JUN   JUL   AUG   SEP   OCT   NOV   DEC   ANN\n""")

    moTot = {}
    for mo in range(1,13):
        moTot[mo] = 0
    yrCnt = 0
    yrAvg = 0
    for yr in range(constants.startyear(station), constants._ENDYEAR):
        yrCnt += 1
        out4.write("%4i" % (yr,) )
        yrSum = 0
        for mo in range(1, 13):
            ts = mx.DateTime.DateTime(yr, mo, 1)
            if (ts < constants._ARCHIVEENDTS):
                moTot[mo] += db[ts]["rain"]
                yrSum += db[ts]["rain"]
            out4.write( safePrint( db[ts]["rain"], 6, 2) )
        yrAvg += float(yrSum) 
        out4.write("%6.2f\n" % ( float(yrSum), ) )
   
    out4.write("MEAN")
    for mo in range(1,13):
        moAvg = moTot[mo] / float( YRCNT[mo] )
        out4.write("%6.2f" % (moAvg,) )

    out4.write("%6.2f\n" % (yrAvg / float(YEARS -1) ,) )
