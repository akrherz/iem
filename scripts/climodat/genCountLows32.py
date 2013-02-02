# Count mininum lows

import constants

def write(mydb, out, station):
    out.write("""# OF DAYS EACH YEAR WHERE MIN >=32 F\n""")

    rs = mydb.query("""SELECT year, count(low) from %s WHERE 
    station = '%s' and low >= 32 and day >= '%s-01-01' 
    and year < %s GROUP by year""" % (constants.get_table(station), 
                                      station, 
                                      constants.startyear(station), 
                                      constants._THISYEAR) ).dictresult()
    tot = 0
    d = {}
    for yr in range(constants.startyear(station), constants._THISYEAR):
        d[yr] = 0
    for i in range(len(rs)):
        tot += int(rs[i]["count"])
        d[ int(rs[i]["year"]) ] = int(rs[i]["count"])

    mean = tot / len(rs)

    for yr in range(constants.startyear(station), constants._THISYEAR):
        out.write("%s %3i\n" % (yr, d[yr]))


    out.write("MEAN %3i\n" % (mean,) )
  
