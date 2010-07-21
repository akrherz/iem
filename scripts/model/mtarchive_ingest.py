# Mine grid point extracted values for our good and the good of the IEM
# Use Unidata's motherlode server :)

import sys
sys.path.insert(0, "../lib")
import db, network
table = network.Table( ['AWOS', 'IA_ASOS'] )
dbconn = db.connect('mos')
dbconn.query("SET TIME ZONE 'GMT'")

import csv, urllib2
import mx.DateTime

BASE_URL = "http://mtarchive.geol.iastate.edu/thredds/ncss/grid/mtarchive/"
URLS = {
 'NAM' : "%Y/%m/%d/gempak/model/%Y%m%d%H_eta211.gem",
 'GFS' : "%Y/%m/%d/gempak/model/%Y%m%d%H_avn211.gem",
}
VLOOKUP = {
 'sbcape': {'NAM': 'CAPE_NONE',
            'GFS': 'CAPE_NONE',
            'RUC': ''},
 'sbcin': {'NAM': 'CINS_NONE',
           'GFS': 'CINS_NONE',
           'RUC': ''},
 'pwater': {'NAM': 'PWTR_NONE',
            'GFS': 'PWTR_NONE',
            'RUC': ''},
 'precip': {'RUC': None,
            'NAM': 'P06M_NONE',
            'GFS': 'P06M_NONE',
           },
}

def run(model, station, lon, lat, ts):
    """
    Ingest the model data for a given Model, stationid and timestamp
    """

    vstring = ""
    for v in VLOOKUP:
        if VLOOKUP[v][model] is not None:
            vstring += "var=%s&" % (VLOOKUP[v][model],)

    url = "%s%s?%slatitude=%s&longitude=%s&temporal=all&vertCoord=&accept=csv&point=true" % (BASE_URL, ts.strftime( URLS[model] ), vstring, lat, lon)
    try:
        fp = urllib2.urlopen( url )
    except:
        return

    sql = """DELETE from model_gridpoint_%s WHERE station = '%s' and 
          model = '%s' and runtime = '%s+00' """ % (ts.year, station,
          model,ts.strftime("%Y-%m-%d %H:%M") )
    dbconn.query( sql )

    r = csv.DictReader( fp )
    for row in r:
        for k in row.keys():
            row[ k[:k.find("[")] ] = row[k]
        sbcape = row[ VLOOKUP['sbcape'][model] ]
        sbcin = row[ VLOOKUP['sbcin'][model] ]
        if row[ VLOOKUP['pwater'][model]] == "NaN":
            pwater = "Null"
        else:
            pwater = row[ VLOOKUP['pwater'][model] ]
        if row[ VLOOKUP['precip'][model]] == "NaN":
            precip = "Null"
        else:
            precip = float(row[ VLOOKUP['precip'][model] ])
        if precip < 0:
            precip = "Null"
        fts = mx.DateTime.strptime(row['date'], '%Y-%m-%dT%H:%M:%SZ')
        sql = """INSERT into model_gridpoint_%s(station, model, runtime, 
              ftime, sbcape, sbcin, pwater, precipcon, precip) 
              VALUES ('%s','%s', '%s+00',
              '%s+00', %s, %s, %s, %s, %s)""" % ( ts.year, station, model,
              ts.strftime("%Y-%m-%d %H:%M"), fts.strftime("%Y-%m-%d %H:%M"),
              sbcape, sbcin, pwater, "Null", precip)
        dbconn.query( sql )

if __name__ == '__main__':
    gts = mx.DateTime.DateTime(2005,3,27,12)
    for id in table.sts.keys():
        run("GFS", "K"+id, table.sts[id]['lon'], table.sts[id]['lat'], gts)
        run("NAM", "K"+id, table.sts[id]['lon'], table.sts[id]['lat'], gts)
