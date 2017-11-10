"""Need something to generate a kitchen sink report of Climate Data"""
import constants
import psycopg2.extras
from pyiem.util import get_dbconn

pgconn = get_dbconn('coop')
cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def setupCSV():
    out = open("/mesonet/share/climodat/ks/yearly.csv", 'w')
    out.write("stationID,stationName,Latitude,Longitude,")
    for i in range(1893, constants._ENDYEAR):
        for v in ["MINT", "MAXT", "PREC"]:
            out.write("%02i_%s," % (i, v))
    out.write("CYR_MINT,CYR_MAXT,CYR_PREC,\n")
    return out


def metadata(sid, csv):
    csv.write("%s,%s,%s,%s," % (sid, constants.nt.sts[sid]["name"],
                                constants.nt.sts[sid]["lat"],
                                constants.nt.sts[sid]["lon"]))


def process(sid, csv):
    # Fetch Yearly Totals
    cursor.execute("""
        SELECT year, round(avg(high)::numeric,1) as avg_high,
        round(avg(low)::numeric,1) as avg_low,
        round(sum(precip)::numeric,2) as rain from %s
        WHERE station = '%s' and year >= %s GROUP by year ORDER by year ASC
    """ % (constants.get_table(sid), sid, constants.startyear(sid)))

    data = {}
    for row in cursor:
        year = row["year"]
        data[year] = {'oHigh': row["avg_high"], 'oLow': row["avg_low"],
                      'oRain': row["rain"]}

    for i in range(1893, constants._ENDYEAR):
        if i not in data:
            data[i] = {'oHigh': "M", 'oLow': "M", 'oRain': "M"}
        csv.write("%s,%s,%s," % (data[i]['oLow'], data[i]['oHigh'],
                                 data[i]['oRain']))

    # Need to do climate stuff
    # Then climate
    cursor.execute("""
        SELECT round(avg(high)::numeric,1) as avg_high,
        round(avg(low)::numeric,1) as avg_low,
        round(sum(precip)::numeric,2) as rain from %s WHERE station = '%s'
    """ % (constants.climatetable(sid), sid))
    row = cursor.fetchone()
    aHigh = row["avg_high"]
    aLow = row["avg_low"]
    aRain = row["rain"]
    csv.write("%s,%s,%s," % (aLow, aHigh, aRain))

    csv.write("\n")
    csv.flush()


def main():
    csv = setupCSV()
    keys = constants.nt.sts.keys()
    keys.sort()
    for sid in keys:
        metadata(sid, csv)
        process(sid, csv)


if __name__ == "__main__":
    main()
