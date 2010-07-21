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

BASE_URL = "http://motherlode.ucar.edu/thredds/ncss/grid/fmrc/NCEP/"
URLS = {
 'NAM' : "NAM/CONUS_12km/conduit/runs/NCEP-NAM-CONUS_12km-conduit_RUN_%Y-%m-%dT%H:00:00Z",
 'GFS' : "GFS/Global_0p5deg/runs/NCEP-GFS-Global_0p5deg_RUN_%Y-%m-%dT%H:00:00Z",
 'RUC' : "RUC2/CONUS_20km/pressure/runs/NCEP-RUC2-CONUS_20km-pressure_RUN_%Y-%m-%dT%H:00:00Z",
}
VLOOKUP = {
 'sbcape': {'NAM': 'Convective_available_potential_energy_surface',
            'GFS': 'Convective_available_potential_energy_surface',
            'RUC': 'Convective_available_potential_energy_surface'},
 'sbcin': {'NAM': 'Convective_inhibition_surface',
           'GFS': 'Convective_inhibition_surface',
           'RUC': 'Convective_inhibition_surface'},
 'pwater': {'NAM': 'Precipitable_water',
            'GFS': 'Precipitable_water',
            'RUC': 'Precipitable_water'},
 'precipcon': {'RUC': 'Convective_precipitation',
            'NAM': 'Convective_precipitation',
            'GFS': 'Convective_precipitation',
           },
 'precipnon': {'RUC': 'Large_scale_precipitation_non-convective',
            'NAM': None,
            'GFS': None
           },
 'precip': {'RUC': None,
            'NAM': 'Total_precipitation',
            'GFS': 'Total_precipitation',
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
        print 'HTTP ERROR'
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
        pwater = row[ VLOOKUP['pwater'][model] ]
        precipcon = row[ VLOOKUP['precipcon'][model] ]
        if model == "RUC":
            precip = float(row[ VLOOKUP['precipcon'][model] ]) + float(row[ VLOOKUP['precipnon'][model] ])
        else:
            precip = row[ VLOOKUP['precip'][model] ]
        fts = mx.DateTime.strptime(row['date'], '%Y-%m-%dT%H:%M:%SZ')
        sql = """INSERT into model_gridpoint_%s(station, model, runtime, 
              ftime, sbcape, sbcin, pwater, precipcon, precip) 
              VALUES ('%s','%s', '%s+00',
              '%s+00', %s, %s, %s, %s, %s)""" % ( ts.year, station, model,
              ts.strftime("%Y-%m-%d %H:%M"), fts.strftime("%Y-%m-%d %H:%M"),
              sbcape, sbcin, pwater, precipcon, precip)
        dbconn.query( sql )

if __name__ == '__main__':
    gts = mx.DateTime.gmt()
    if gts.hour % 6 == 0:
        ts = gts - mx.DateTime.RelativeDateTime(hours=6,minute=0,second=0)
        for id in table.sts.keys():
            run("GFS", "K"+id, table.sts[id]['lon'], table.sts[id]['lat'], ts)
            run("NAM", "K"+id, table.sts[id]['lon'], table.sts[id]['lat'], ts)
    for id in table.sts.keys():
        ts = gts - mx.DateTime.RelativeDateTime(hours=2,minute=0,second=0)
        run("RUC", "K"+id, table.sts[id]['lon'], table.sts[id]['lat'], ts)
