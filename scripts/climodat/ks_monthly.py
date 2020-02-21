"""
 Need something to generate a kitchen sink report of Climate Data
"""
import sys
import datetime

import numpy as np
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn

nt = NetworkTable(
    (
        "IACLIMATE",
        "ILCLIMATE",
        "INCLIMATE",
        "OHCLIMATE",
        "MICLIMATE",
        "KYCLIMATE",
        "WICLIMATE",
        "MNCLIMATE",
        "SDCLIMATE",
        "NDCLIMATE",
        "NECLIMATE",
        "KSCLIMATE",
        "MOCLIMATE",
    )
)
pgconn = get_dbconn("coop", user="nobody")
cursor = pgconn.cursor()


def setup_csv(yr):
    """ Setup the output file """
    out = open("/mesonet/share/climodat/ks/%s_monthly.csv" % (yr,), "w")
    out.write("stationID,stationName,Latitude,Longitude,")
    for i in range(1, 13):
        for v in ["MINT", "MAXT", "PREC"]:
            out.write("%02i_%s,C%02i_%s," % (i, v, i, v))
    out.write(
        ("%i_MINT,CYR_MINT,%i_MAXT,CYR_MAXT,%i_PREC,CYR_PREC,\n")
        % (yr, yr, yr)
    )
    return out


def metadata(sid, csv):
    """ write metadata to csv file """
    csv.write(
        "%s,%s,%s,%s,"
        % (sid, nt.sts[sid]["name"], nt.sts[sid]["lat"], nt.sts[sid]["lon"])
    )


def process(sid, csv, yr):
    """ Actually process a station for a csv file and year """
    ah = []
    al = []
    ap = []
    oh = []
    ol = []
    op = []
    for i in range(1, 13):
        sql = """
        WITH yearly as (
            SELECT year, avg(high) as ah, avg(low) as al,
            sum(precip) as sp from alldata_%s
            WHERE station = '%s' and month = %s
            GROUP by year)

        SELECT
        avg(ah) as avg_high,
        avg(al) as avg_low,
        avg(sp) as avg_rain,
        max(case when year = %s then ah else null end) as ob_high,
        max(case when year = %s then al else null end) as ob_low,
        max(case when year = %s then sp else null end) as ob_rain
        from yearly
        """ % (
            sid[:2],
            sid,
            i,
            yr,
            yr,
            yr,
        )
        cursor.execute(sql)
        row = cursor.fetchone()
        avgHigh = row[0]
        avgLow = row[1]
        avgRain = row[2]
        ah.append(float(avgHigh))
        al.append(float(avgLow))
        ap.append(float(avgRain))

        obHigh = row[3]
        obLow = row[4]
        obRain = row[5]
        if obHigh is not None:
            oh.append(float(obHigh))
            ol.append(float(obLow))
            op.append(float(obRain))

        csv.write(
            "%s,%s,%s,%s,%s,%s,"
            % (
                obLow or "M",
                avgLow,
                obHigh or "M",
                avgHigh,
                obRain or "M",
                avgRain,
            )
        )

    low = np.average(ol)
    high = np.average(oh)
    rain = np.sum(op)
    avg_low = np.average(al)
    avg_high = np.average(ah)
    avg_rain = np.sum(ap)
    csv.write(
        "%s,%s,%s,%s,%s,%s," % (low, avg_low, high, avg_high, rain, avg_rain)
    )

    csv.write("\n")
    csv.flush()


def main(yr):
    """ main ! """
    csv = setup_csv(yr)
    for sid in nt.sts:
        metadata(sid, csv)
        process(sid, csv, yr)


def frontend(argv):
    """A frontend to main."""
    if len(argv) == 2:
        yr = int(argv[1])
    else:
        yr = datetime.datetime.now().year
    main(yr)
    main(yr - 1)


if __name__ == "__main__":
    frontend(sys.argv)
