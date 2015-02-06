""" This is report 08 """

import constants


def write(cursor, out, station):
    out.write("""# OF DAYS EACH YEAR WHERE MIN >=32 F\n""")

    cursor.execute("""
        SELECT year, count(low) from %s WHERE
        station = '%s' and low >= 32 and day >= '%s-01-01'
        and year < %s GROUP by year
    """ % (constants.get_table(station), station,
           constants.startyear(station), constants._THISYEAR))
    tot = 0
    d = {}
    for row in cursor:
        tot += row["count"]
        d[row["year"]] = row["count"]

    mean = tot / float(cursor.rowcount)

    for year in range(constants.startyear(station), constants._THISYEAR):
        out.write("%s %3i\n" % (year, d.get(year, 0)))

    out.write("MEAN %3i\n" % (mean,))
