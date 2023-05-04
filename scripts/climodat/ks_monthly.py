"""
 Need something to generate a kitchen sink report of Climate Data
"""
import datetime
import os
import sys

import numpy as np
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn
from tqdm import tqdm

nt = NetworkTable("IACLIMATE")
pgconn = get_dbconn("coop")
cursor = pgconn.cursor()


def metadata(sid, csv):
    """write metadata to csv file"""
    entry = nt.sts[sid]
    csv.write(f"{sid},{entry['name']},{entry['lat']},{entry['lon']},")


def fmt(val):
    """Prettier."""
    if val is None or val == "M":
        return "M"
    return f"{val:.2f}"


def process(sid, csv, yr):
    """Actually process a station for a csv file and year"""
    ah = []
    al = []
    ap = []
    agdd = []
    asdd = []
    oh = []
    ol = []
    op = []
    ogdd = []
    osdd = []
    for i in range(1, 13):
        cursor.execute(
            f"""
        WITH yearly as (
            SELECT year, avg(high) as ah, avg(low) as al,
            sum(precip) as sp,
            sum(gdd50(high, low)) as sgdd50,
            sum(sdd86(high, low)) as ssdd86
            from alldata_{sid[:2]} WHERE station = %s and month = %s
            GROUP by year)

        SELECT
        avg(ah) as avg_high,
        avg(al) as avg_low,
        avg(sp) as avg_rain,
        avg(sgdd50) as avg_gdd50,
        avg(ssdd86) as avg_sdd86,
        max(case when year = %s then ah else null end) as ob_high,
        max(case when year = %s then al else null end) as ob_low,
        max(case when year = %s then sp else null end) as ob_rain,
        max(case when year = %s then sgdd50 else null end) as ob_gdd50,
        max(case when year = %s then ssdd86 else null end) as ob_sdd86
        from yearly
            """,
            (sid, i, yr, yr, yr, yr, yr),
        )
        row = cursor.fetchone()
        avgHigh = row[0]
        avgLow = row[1]
        avgRain = row[2]
        avgGDD = row[3]
        avgSDD = row[4]
        ah.append(float(avgHigh))
        al.append(float(avgLow))
        ap.append(float(avgRain))
        agdd.append(float(avgGDD))
        asdd.append(float(avgSDD))

        obHigh = row[5]
        obLow = row[6]
        obRain = row[7]
        obGDD = row[8]
        obSDD = row[9]
        if obHigh is not None:
            oh.append(float(obHigh))
            ol.append(float(obLow))
            op.append(float(obRain))
            ogdd.append(float(obGDD))
            osdd.append(float(obSDD))

        csv.write(
            f"{fmt(obLow)},{fmt(avgLow)},{fmt(obHigh)},{fmt(avgHigh)},"
            f"{fmt(obRain)},{fmt(avgRain)},{fmt(obGDD)},{fmt(avgGDD)},"
            f"{fmt(obSDD)},{fmt(avgSDD)},"
        )

    low = np.average(ol)
    high = np.average(oh)
    rain = np.sum(op)
    gdd = np.sum(ogdd)
    sdd = np.sum(osdd)
    avg_low = np.average(al)
    avg_high = np.average(ah)
    avg_rain = np.sum(ap)
    avg_gdd = np.sum(agdd)
    avg_sdd = np.sum(asdd)
    csv.write(
        f"{fmt(low)},{fmt(avg_low)},{fmt(high)},{fmt(avg_high)},{fmt(rain)},"
        f"{fmt(avg_rain)},{fmt(gdd)},{fmt(avg_gdd)},{fmt(sdd)},{fmt(avg_sdd)},"
    )

    csv.write("\n")
    csv.flush()


def main(yr):
    """main !"""
    mydir = "/mesonet/share/climodat/ks"
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    with open(f"{mydir}/{yr}_monthly.csv", "w", encoding="utf-8") as fh:
        fh.write("stationID,stationName,Latitude,Longitude,")
        for i in range(1, 13):
            for v in ["MINT", "MAXT", "PREC", "GDD50", "SDD86"]:
                fh.write(f"{i:02.0f}_{v},C{i:02.0f}_{v},")
        fh.write(
            f"{yr}_MINT,CYR_MINT,{yr}_MAXT,CYR_MAXT,{yr}_PREC,CYR_PREC,"
            f"{yr}_GDD50,CYR_GDD50,{yr}_SDD86,CYR_SDD86\n"
        )
        for sid in tqdm(nt.sts, disable=not sys.stdout.isatty()):
            metadata(sid, fh)
            process(sid, fh, yr)


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
