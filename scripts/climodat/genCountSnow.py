# Generate A counting of rainfall events
# Daryl Herzmann 16 Mar 2005

import constants
import datetime
import numpy as np


def write(monthly_rows, out, station):
    out.write("""# NUMBER OF SNOWY DAYS PER MONTH PER YEAR
# Days with a trace of snowfall reported are not included
YEAR   JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC ANN
""")

    db = {}
    monthly = [0]*13
    for i in range(13):
        monthly[i] = []

    for row in monthly_rows:
        ts = datetime.datetime(row['year'], row['month'], 1)
        db[ts] = row["snow_days"]
        monthly[ts.month].append(row['snow_days'])

    for yr in range(constants.startyear(station), constants._ENDYEAR):
        tot = 0
        out.write("%s   " % (yr,))
        for mo in range(1, 13):
            ts = datetime.datetime(yr, mo, 1)
            cnt = db.get(ts, None)
            if ts >= constants._ARCHIVEENDTS or cnt is None:
                out.write("%3s " % ("M",))
                continue

            out.write("%3i " % (cnt,))
            tot += cnt
        out.write("%3i\n" % (tot,))

    out.write("STDDEV ")
    for mo in range(1, 13):
        out.write("%3.0f " % (np.std(monthly[mo]),))
    out.write("%3.0f\n" % (0,))
    out.write("AVG    ")
    for mo in range(1, 13):
        out.write("%3.0f " % (np.average(monthly[mo]),))
    out.write("%3.0f\n" % (0,))
