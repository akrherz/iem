"""
 Need something to generate a kitchen sink report of Climate Data
"""
import constants
import sys
import datetime
import numpy as np

def setup_csv(yr):
    """ Setup the output file """
    out = open("/mesonet/share/climodat/ks/%s_monthly.csv" % (yr,), 'w')
    out.write("stationID,stationName,Latitude,Longitude,")
    for i in range(1,13):
        for v in ["MINT","MAXT","PREC"]:
            out.write("%02i_%s,C%02i_%s," % (i,v,i,v) )
    out.write("%i_MINT,CYR_MINT,%i_MAXT,CYR_MAXT,%i_PREC,CYR_PREC,\n" % (yr,
                                                                yr, yr))
    return out

def metadata(sid,csv):
    """ write metadata to csv file """
    csv.write("%s,%s,%s,%s," % (sid, constants.nt.sts[sid]["name"], 
                                constants.nt.sts[sid]["lat"], 
                                constants.nt.sts[sid]["lon"]))

def process(sid, csv, yr):
    """ Actually process a station for a csv file and year """
    ah = []
    al = []
    ap = []
    oh = []
    ol = []
    op = []
    for i in range(1,13):
        sql = """
        WITH yearly as (
            SELECT year, avg(high) as ah, avg(low) as al, 
            sum(precip) as sp from %s WHERE station = '%s' and month = %s
            GROUP by year)

        SELECT 
        avg(ah) as avg_high,
        avg(al) as avg_low,
        avg(sp) as avg_rain,
        max(case when year = %s then ah else null end) as ob_high,
        max(case when year = %s then al else null end) as ob_low,
        max(case when year = %s then sp else null end) as ob_rain
        from yearly
        """ % (constants.get_table(sid), sid, i, yr, yr, yr)
        rs = constants.mydb.query(sql).dictresult()
        avgHigh = rs[0]["avg_high"]
        avgLow = rs[0]["avg_low"]
        avgRain = rs[0]["avg_rain"]
        ah.append( avgHigh )
        al.append( avgLow )
        ap.append( avgRain )
        
        obHigh = rs[0]["ob_high"]
        obLow = rs[0]["ob_low"]
        obRain = rs[0]["ob_rain"]
        if obHigh is not None:
            oh.append( obHigh )
            ol.append( obLow )
            op.append( obRain )

        csv.write("%s,%s,%s,%s,%s,%s," % (obLow or 'M', avgLow, 
                                          obHigh or 'M', avgHigh, 
                                          obRain or 'M', avgRain))

    low = np.average(ol)
    high = np.average(oh)
    rain = np.sum(op)
    avg_low = np.average(al)
    avg_high = np.average(ah)
    avg_rain = np.sum(ap)
    csv.write("%s,%s,%s,%s,%s,%s," % (low, avg_low, high, avg_high, rain,
                                      avg_rain) )

    csv.write("\n")
    csv.flush()

def main(yr):
    """ main ! """
    csv = setup_csv(yr)
    for sid in constants.nt.sts.keys():
        #print "%s processing [%s] %s" % (yr, id, nt.sts[id]["name"])
        metadata(sid, csv)
        process(sid, csv, yr)

if __name__ == "__main__":
    # For what year are we running!
    if len(sys.argv) == 2:
        yr = int(sys.argv[1])
    else:
        yr = datetime.datetime.now().year
    main(yr)
    main(yr-1)
    #for yr in range(1893,1951):
    #  main(yr)
