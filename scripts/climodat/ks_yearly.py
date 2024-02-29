"""Need something to generate a kitchen sink report of Climate Data

Called from climodat/run.sh
"""

import datetime

from pyiem.database import get_dbconnc
from pyiem.network import Table as NetworkTable

pgconn, cursor = get_dbconnc("coop")

ENDYEAR = datetime.date.today().year


def metadata(nt, sid, csv):
    """write metadata"""
    entry = nt.sts[sid]
    csv.write(f"{sid},{entry['name']},{entry['lat']},{entry['lon']},")


def process(sid, csv):
    """Process"""
    # Fetch Yearly Totals
    cursor.execute(
        """
        SELECT year, round(avg(high)::numeric,1) as avg_high,
        round(avg(low)::numeric,1) as avg_low,
        round(sum(precip)::numeric,2) as rain,
        round(sum(gdd50(high, low))::numeric, 0) as gdd50,
        round(sum(sdd86(high, low))::numeric, 0) as sdd86
        from alldata
        WHERE station = %s GROUP by year ORDER by year ASC
    """,
        (sid,),
    )

    data = {}
    for row in cursor:
        year = row["year"]
        data[year] = {
            "oHigh": row["avg_high"],
            "oLow": row["avg_low"],
            "oRain": row["rain"],
            "oGDD": row["gdd50"],
            "oSDD": row["sdd86"],
        }
    years = 0
    for i in range(1893, ENDYEAR):
        if i not in data:
            data[i] = {
                "oHigh": "M",
                "oLow": "M",
                "oRain": "M",
                "oGDD": "M",
                "oSDD": "M",
            }
        years += 1
        entry = data[i]
        csv.write(
            f"{entry['oLow']},{entry['oHigh']},{entry['oRain']},"
            f"{entry['oGDD']},{entry['oSDD']},"
        )

    # Need to do climate stuff
    # Then climate
    cursor.execute(
        """
        SELECT round(avg(high)::numeric,1) as avg_high,
        round(avg(low)::numeric,1) as avg_low,
        sum(precip) as rain,
        sum(gdd50(high, low)) as gdd50,
        sum(sdd86(high, low)) as sdd86
        from alldata WHERE station = %s
    """,
        (sid,),
    )
    row = cursor.fetchone()
    aHigh = row["avg_high"]
    aLow = row["avg_low"]
    aRain = row["rain"]
    rr = float(aRain) / float(years)
    gr = float(row["gdd50"]) / float(years)
    sr = float(row["sdd86"]) / float(years)
    csv.write(f"{aLow},{aHigh},{rr:.2f},{gr:.2f},{sr:.2f},")

    csv.write("\n")
    csv.flush()


def main():
    """Go Main Go"""
    nt = NetworkTable("IACLIMATE")
    keys = list(nt.sts.keys())
    keys.sort()
    fn = "/mesonet/share/climodat/ks/yearly.csv"
    with open(fn, "w", encoding="ascii") as fp:
        fp.write("stationID,stationName,Latitude,Longitude,")
        for i in range(1893, ENDYEAR):
            for v in ["MINT", "MAXT", "PREC", "GDD50", "SDD86"]:
                fp.write(f"{i:02.0f}_{v},")
        fp.write("CYR_MINT,CYR_MAXT,CYR_PREC,CYR_GDD50,CYR_SDD86,\n")
        for sid in keys:
            metadata(nt, sid, fp)
            process(sid, fp)


if __name__ == "__main__":
    main()
