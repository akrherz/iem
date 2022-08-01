"""Need something to generate a kitchen sink report of Climate Data"""
import datetime

import psycopg2.extras
from pyiem.util import get_dbconn
from pyiem.network import Table as NetworkTable

pgconn = get_dbconn("coop")
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

ENDYEAR = datetime.date.today().year


def setupcsv():
    """setup output file"""
    out = open("/mesonet/share/climodat/ks/yearly.csv", "w")
    out.write("stationID,stationName,Latitude,Longitude,")
    for i in range(1893, ENDYEAR):
        for v in ["MINT", "MAXT", "PREC", "GDD50", "SDD86"]:
            out.write("%02i_%s," % (i, v))
    out.write("CYR_MINT,CYR_MAXT,CYR_PREC,CYR_GDD50,CYR_SDD86,\n")
    return out


def metadata(nt, sid, csv):
    """write metadata"""
    csv.write(
        "%s,%s,%s,%s,"
        % (sid, nt.sts[sid]["name"], nt.sts[sid]["lat"], nt.sts[sid]["lon"])
    )


def process(sid, csv):
    """Process"""
    table = "alldata_%s" % (sid[:2],)
    # Fetch Yearly Totals
    cursor.execute(
        f"""
        SELECT year, round(avg(high)::numeric,1) as avg_high,
        round(avg(low)::numeric,1) as avg_low,
        round(sum(precip)::numeric,2) as rain,
        round(sum(gdd50(high, low))::numeric, 0) as gdd50,
        round(sum(sdd86(high, low))::numeric, 0) as sdd86
        from {table}
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
        csv.write(
            "%s,%s,%s,%s,%s,"
            % (
                data[i]["oLow"],
                data[i]["oHigh"],
                data[i]["oRain"],
                data[i]["oGDD"],
                data[i]["oSDD"],
            )
        )

    # Need to do climate stuff
    # Then climate
    cursor.execute(
        f"""
        SELECT round(avg(high)::numeric,1) as avg_high,
        round(avg(low)::numeric,1) as avg_low,
        sum(precip) as rain,
        sum(gdd50(high, low)) as gdd50,
        sum(sdd86(high, low)) as sdd86
        from {table} WHERE station = %s
    """,
        (sid,),
    )
    row = cursor.fetchone()
    aHigh = row["avg_high"]
    aLow = row["avg_low"]
    aRain = row["rain"]
    csv.write(
        "%s,%s,%.2f,%.2f,%.2f,"
        % (
            aLow,
            aHigh,
            float(aRain) / float(years),
            float(row["gdd50"]) / float(years),
            float(row["sdd86"]) / float(years),
        )
    )

    csv.write("\n")
    csv.flush()


def main():
    """Go Main Go"""
    nt = NetworkTable("IACLIMATE")
    csv = setupcsv()
    keys = list(nt.sts.keys())
    keys.sort()
    for sid in keys:
        metadata(nt, sid, csv)
        process(sid, csv)


if __name__ == "__main__":
    main()
