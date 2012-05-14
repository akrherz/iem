"""
Precipitation categories by year
"""


_REPORTID = "28"
import constants
import numpy
CATS = numpy.array([0.01,0.5,1.,2.,3.,4.])

def write(mydb, rs, stationID):
    """
    standard interative here....
    """
    startyear = constants.startyear(stationID)
    years = constants._ENDYEAR - startyear
    # 0.01, 0.5, 1, 2, 3, 4
    data = numpy.zeros( (years+1, 6), 'i')
    for i in range(len(rs)):
        precip = float(rs[i]["precip"])
        if precip <= 0:
            continue
        offset = int(rs[i]['year']) - startyear
        data[offset,:] += numpy.where(precip >= CATS, 1, 0)


    out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
    constants.writeheader(out, stationID)
    out.write("""\
# Number of days per year with precipitation at or above threshold
YEAR %4.2f %4.2f %4.2f %4.2f %4.2f %4.2f
""" % (CATS[0], CATS[1], CATS[2], CATS[3], CATS[4], CATS[5]))
 
    for yr in range(startyear, constants._ENDYEAR+1):
        out.write("%s %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f\n" % (yr,
                data[yr-startyear,0], data[yr-startyear,1],data[yr-startyear,2],
                data[yr-startyear,3],data[yr-startyear,4],data[yr-startyear,5]))

    minv = numpy.min(data[:-1,:],0)
    out.write("MIN  %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f\n" % (minv[0], minv[1],
                                                       minv[2], minv[3],
                                                       minv[4], minv[5]))
    avgv = numpy.average(data[:-1,:],0)
    out.write("AVG  %4.1f %4.1f %4.1f %4.1f %4.1f %4.1f\n" % (avgv[0], avgv[1],
                                                       avgv[2], avgv[3],
                                                       avgv[4], avgv[5]))
    maxv = numpy.max(data[:-1,:],0)
    out.write("MAX  %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f\n" % (maxv[0], maxv[1],
                                                       maxv[2], maxv[3],
                                                       maxv[4], maxv[5]))
    out.close()
