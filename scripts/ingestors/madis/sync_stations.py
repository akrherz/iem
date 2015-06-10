"""
Extract station data from file and update any new stations we find, please
"""
import netCDF4
import psycopg2
import sys
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = MESOSITE.cursor()

fn = sys.argv[1]
nc = netCDF4.Dataset(fn)

stations   = nc.variables["stationId"]
names   = nc.variables["stationName"]
providers  = nc.variables["dataProvider"]
latitudes  = nc.variables["latitude"]
longitudes  = nc.variables["longitude"]
elevations  = nc.variables["elevation"]


MY_PROVIDERS = [
 "AKDOT", 
 "CODOT", 
 "DEDOT",
 "FLDOT",
 "GADOT", 
 "INDOT", 
 "KSDOT", 
 "KYTC-RWIS", 
 "KYMN",
 "MEDOT", 
 "MDDOT", 
 "MNDOT", 
 "NEDOR", 
 "NHDOT", 
 "NDDOT",
 "NVDOT",
 "OHDOT", 
 "WIDOT",
 "WVDOT", 
 "WYDOT",  
 "VADOT", 
 "VTDOT",
 "MesoWest",
]
VTWAC = ['UVM01', 'UVM02', 'UVM03', 'UVM04', 'UVM05', 'VEC01', 'VTW01']

def provider2network(p):
    """ Convert a MADIS network ID to one that I use, here in IEM land"""
    if p in ['KYMN']:
        return p
    if p == 'MesoWest':
        return 'VTWAC'
    return '%s_RWIS' % (p[:2],)

for recnum in range(len(providers)):
    thisProvider = providers[recnum].tostring().replace('\x00','')
    if thisProvider not in MY_PROVIDERS:
        continue
    stid = stations[recnum].tostring().replace('\x00','')
    if thisProvider == 'MesoWest' and stid not in VTWAC:
        continue
    name = names[recnum].tostring().replace("'", "").replace('\x00','').replace('\xa0', ' ')
    network = provider2network(thisProvider)
    mcursor.execute("""SELECT * from stations where id = %s and network = %s""",
                    (stid, network))
    if mcursor.rowcount > 0:
        continue
    print 'Adding network: %s station: %s %s' % (network, stid, name)
    sql = """INSERT into stations(id, network, synop, country, plot_name,
    name, state, elevation, online, geom, metasite) VALUES ('%s', '%s', 9999, 'US',
    '%s', '%s', '%s', %s, 't', 'SRID=4326;POINT(%s %s)', 'f')""" % (stid,
    network, name, name, network[:2], elevations[recnum], longitudes[recnum],
    latitudes[recnum])
    mcursor.execute(sql)
nc.close()
mcursor.close()
MESOSITE.commit()
MESOSITE.close()
