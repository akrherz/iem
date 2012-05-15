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
    standard iterative here....
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
# Partitioned by month of the year, 'ANN' represents the entire year
""")

    for c in range(len(CATS)):
        out.write("""\
YEAR %4.2f JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC ANN
""" % (CATS[c],))
        for yr in range(startyear, constants._ENDYEAR): 
            out.write("%s %4.2f " % (yr, CATS[c]))
            for mo in range(1,13):
                out.write("%3.0f " % (data[mo, yr-startyear,c],))
            out.write("%3.0f\n" % (data[0,yr-startyear,c],))
    out.close()
