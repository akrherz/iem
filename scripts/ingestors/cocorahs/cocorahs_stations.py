"""
Hit cocorah's website API for a listing of stations and add entries for
anything new found
"""
import urllib2
import sys
import psycopg2
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = MESOSITE.cursor()

state = sys.argv[1]

req = urllib2.Request(("http://data.cocorahs.org/cocorahs/export/"
                       "exportstations.aspx?State=%s&Format=CSV"
                       "&country=usa") % (state,))
data = urllib2.urlopen(req, timeout=30).readlines()

# Find current stations
stations = []
sql = """
    SELECT id from stations WHERE network = '%sCOCORAHS' and ST_y(geom) > 0
    and name is not null and name != '' """ % (state,)
mcursor.execute(sql)
for row in mcursor:
    stations.append(row[0])

# Process Header
header = {}
h = data[0].split(",")
for i in range(len(h)):
    header[h[i]] = i

if 'StationNumber' not in header:
    sys.exit(0)

for row in data[1:]:
    cols = row.split(", ")
    sid = cols[header["StationNumber"]]
    if sid in stations:
        continue

    name = cols[header["StationName"]].strip().replace("'", ' ')
    cnty = cols[header["County"]].strip().replace("'", ' ')
    lat = float(cols[header["Latitude"]].strip())
    lon = float(cols[header["Longitude"]].strip())

    if lat < 10 or lon > -60 or name == '':
        continue

    print(("ADD COCORAHS SID:%s Name:%s County:%s %.3f %.3f"
           ) % (sid, name, cnty, lat, lon))

    sql = """
        INSERT into stations(id, synop, name, state, country, network,
        online, geom, county, plot_name , metasite)
        VALUES ('%s', 99999, '%s', '%s', 'US', '%sCOCORAHS', 't',
        'SRID=4326;POINT(%s %s)', '%s', '%s', 'f')
        """ % (sid, name, state, state, lon, lat, cnty, name)
    try:
        mcursor = MESOSITE.cursor()
        mcursor.execute(sql)
        mcursor.close()
        MESOSITE.commit()
    except:
        mcursor.close()
        MESOSITE.commit()
        mcursor = MESOSITE.cursor()
        sql = """
            UPDATE stations SET geom = 'SRID=4326;POINT(%s %s)',
            name = '%s', plot_name = '%s'
            WHERE id = '%s' and network = '%sCOCORAHS'
        """ % (lon, lat, name, name, sid, state)
        mcursor.execute(sql)
        mcursor.close()
        MESOSITE.commit()
