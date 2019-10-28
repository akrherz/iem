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
        for v in ["MINT", "MAXT", "PREC"]:
            out.write("%02i_%s," % (i, v))
    out.write("CYR_MINT,CYR_MAXT,CYR_PREC,\n")
    return out


def metadata(nt, sid, csv):
    """write metadata"""
    csv.write(
        "%s,%s,%s,%s,"
        % (sid, nt.sts[sid]["name"], nt.sts[sid]["lat"], nt.sts[sid]["lon"])
    )


def process(nt, sid, csv):
    """Process"""
    table = "alldata_%s" % (sid[:2],)
    # Fetch Yearly Totals
    cursor.execute(
        """
        SELECT year, round(avg(high)::numeric,1) as avg_high,
        round(avg(low)::numeric,1) as avg_low,
        round(sum(precip)::numeric,2) as rain from """
        + table
        + """
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
        }

    for i in range(1893, ENDYEAR):
        if i not in data:
            data[i] = {"oHigh": "M", "oLow": "M", "oRain": "M"}
        csv.write(
            "%s,%s,%s," % (data[i]["oLow"], data[i]["oHigh"], data[i]["oRain"])
        )

    # Need to do climate stuff
    # Then climate
    cursor.execute(
        """
        SELECT round(avg(high)::numeric,1) as avg_high,
        round(avg(low)::numeric,1) as avg_low,
        round(sum(precip)::numeric,2) as rain from """
        + table
        + """
        WHERE station = %s
    """,
        (sid,),
    )
    row = cursor.fetchone()
    aHigh = row["avg_high"]
    aLow = row["avg_low"]
    aRain = row["rain"]
    csv.write("%s,%s,%s," % (aLow, aHigh, aRain))

    csv.write("\n")
    csv.flush()


def main():
    """Go Main Go"""
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
    csv = setupcsv()
    keys = list(nt.sts.keys())
    keys.sort()
    for sid in keys:
        metadata(nt, sid, csv)
        process(nt, sid, csv)


if __name__ == "__main__":
    main()
