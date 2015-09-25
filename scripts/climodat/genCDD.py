"""
Cooling Degree days
"""

import mx.DateTime
import constants


def ccdd(high, low, base):
    cdd = 0
    try:
        a = float(int(high) + int(low)) / 2.00
    except:
        return 0
    if a > base:
        cdd = a - base

    return cdd


def write(monthly_rows, out, station):
    """ write out this report """
    YRCNT = constants.yrcnt(station)
    out.write("""# THESE ARE THE MONTHLY COOLING DEGREE DAYS (base=65) %s-%s FOR STATION  %s
YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    SEP    OCT    NOV    DEC
""" % (constants.startyear(station), constants._ENDYEAR, station))

    db = {}
    db60 = {}
    for row in monthly_rows:
        mo = mx.DateTime.DateTime(row['year'], row['month'], 1)
        db[mo] = row["cdd65"]
        db60[mo] = row["cdd60"]

    moTot = {}
    moTot60 = {}
    for mo in range(1, 13):
        moTot[mo] = 0
        moTot60[mo] = 0

    second = """# THESE ARE THE MONTHLY COOLING DEGREE DAYS (base=60) %s-%s FOR STATION  %s
YEAR    JAN    FEB    MAR    APR    MAY    JUN    JUL    AUG    SEP    OCT    NOV    DEC\n""" % (
            constants.startyear(station), constants._ENDYEAR, station)
    yrCnt = 0
    for yr in range(constants.startyear(station), constants._ENDYEAR):
        yrCnt += 1
        out.write("%4i" % (yr,))
        second += "%4i" % (yr,)
        for mo in range(1, 13):
            ts = mx.DateTime.DateTime(yr, mo, 1)
            if (ts >= constants._ARCHIVEENDTS):
                out.write("%7s" % ("M",))
                second += "%7s" % ("M",)
                continue
            if (ts < constants._ARCHIVEENDTS):
                moTot[mo] += db[ts]
                moTot60[mo] += db60[ts]
            out.write("%7.0f" % (db[ts],))
            second += "%7.0f" % (db60[ts],)
        out.write("\n")
        second += "\n"

    out.write("MEAN")
    second += "MEAN"
    for mo in range(1, 13):
        out.write("%7.0f" % (float(moTot[mo]) / float(YRCNT[mo])))
        second += "%7.0f" % (float(moTot60[mo]) / float(YRCNT[mo]))
    out.write("\n")
    second += "\n"
    out.write(second)
