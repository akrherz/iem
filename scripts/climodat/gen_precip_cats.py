"""
Precipitation categories by year
"""


_REPORTID = "28"
import constants
import numpy
import mx.DateTime
CATS = numpy.array([0.01,0.5,1.,2.,3.,4.])

def write(mydb, rs, stationID):
    """
    standard interative here....
    """
    startyear = constants.startyear(stationID)
    years = constants._ENDYEAR - startyear
    # 0.01, 0.5, 1, 2, 3, 4
    data = numpy.zeros( (13, years+1, 6), 'i')
    for i in range(len(rs)):
        precip = float(rs[i]["precip"])
        if precip <= 0:
            continue
        offset = int(rs[i]['year']) - startyear
        data[0, offset,:] += numpy.where(precip >= CATS, 1, 0)
        data[int(rs[i]['month']), offset,:] += numpy.where(precip >= CATS, 1, 0)


    out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
    constants.writeheader(out, stationID)
    out.write("""\
# Number of days per year with precipitation at or above threshold [inch]
# Partitioned by month of the year, 'ALL' represents the entire year
YEAR MON %4.2f %4.2f %4.2f %4.2f %4.2f %4.2f
""" % (CATS[0], CATS[1], CATS[2], CATS[3], CATS[4], CATS[5]))
 
    for mo in range(13):
        lbl = "ALL"
        if mo > 0:
            lbl = mx.DateTime.DateTime(2000,mo,1).strftime("%b").upper()
        for yr in range(startyear, constants._ENDYEAR):
            out.write("%s %s %5.0f %4.0f %4.0f %4.0f %4.0f %4.0f\n" % (yr, lbl,
                data[mo, yr-startyear,0], data[mo, yr-startyear,1],data[mo, yr-startyear,2],
                data[mo, yr-startyear,3],data[mo, yr-startyear,4],data[mo, yr-startyear,5]))

        minv = numpy.min(data[mo,:-1,:],0)
        out.write("MIN  %s %5.0f %4.0f %4.0f %4.0f %4.0f %4.0f\n" % (lbl, minv[0], minv[1],
                                                           minv[2], minv[3],
                                                           minv[4], minv[5]))
        avgv = numpy.average(data[mo,:-1,:],0)
        out.write("AVG  %s %5.1f %4.1f %4.1f %4.1f %4.1f %4.1f\n" % (lbl, avgv[0], avgv[1],
                                                           avgv[2], avgv[3],
                                                           avgv[4], avgv[5]))
        maxv = numpy.max(data[mo,:-1,:],0)
        out.write("MAX  %s %5.0f %4.0f %4.0f %4.0f %4.0f %4.0f\n" % (lbl, maxv[0], maxv[1],
                                                           maxv[2], maxv[3],
                                                           maxv[4], maxv[5]))
    out.close()
