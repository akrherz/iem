"""
My purpose in life is to take the NWS AWIPS Geodata Zones Shapefile and
dump them into the PostGIS database!  I was bootstraped like so:

python zones_update.py z_16mr06 2006 03 16
python zones_update.py z_11mr07 2007 03 11
python zones_update.py z_31my07 2007 05 31
python zones_update.py z_01au07 2007 08 01
python zones_update.py z_5sep07 2007 09 05
python zones_update.py z_25sep07 2007 09 25
python zones_update.py z_01ap08 2008 04 01
python zones_update.py z_09se08 2008 09 09
python zones_update.py z_03oc08 2008 10 03
python zones_update.py z_07my09 2009 05 07
python zones_update.py z_15jl09 2009 07 15
python zones_update.py z_22jl09 2009 07 22
python zones_update.py z_04au11 2011 08 04
python zones_update.py z_13oc11 2011 10 13
python zones_update.py z_31my11 2011 05 31
python zones_update.py z_15de11 2011 12 15
python zones_update.py z_23fe12 2012 02 23
python zones_update.py z_03ap12 2012 04 03
python zones_update.py z_12ap12 2012 04 12
python zones_update.py z_07jn12 2012 06 07
python zones_update.py z_11oc12 2012 10 11
python zones_update.py z_03de13a 2013 12 03
python zones_update.py z_05fe14a 2014 02 05

"""
from __future__ import print_function
import sys
import os
import datetime
import urllib2
import zipfile

from osgeo import ogr
from osgeo import _ogr
import psycopg2
import pytz


def Area(feat, *args):
    """
    Backport a feature from the future!
    """
    return _ogr.Geometry_GetArea(feat, *args)


def main(argv):
    """Go Main Go"""
    pgconn = psycopg2.connect(database='postgis', host='iemdb')
    cursor = pgconn.cursor()

    # Get the name of the file we wish to download
    if len(argv) != 5:
        print('ERROR: You need to specify the file date to download and date')
        print('Example:  python zones_update.py z_01dec10 2010 12 01')
        sys.exit(0)

    DATESTAMP = argv[1]
    TS = datetime.datetime(int(argv[2]), int(argv[3]), int(argv[4]))
    TS = TS.replace(tzinfo=pytz.timezone("UTC"))

    # Change Directory to /tmp, so that we can rw
    os.chdir('/tmp')

    zipfn = "%s.zip" % (DATESTAMP,)
    if not os.path.isfile(zipfn):
        url = urllib2.Request(('http://www.weather.gov/geodata/catalog/wsom/'
                               'data/%s') % (zipfn,))
        print('Downloading %s ...' % (zipfn,))
        o = open(zipfn, 'wb')
        o.write(urllib2.urlopen(url).read())
        o.close()

    print('Unzipping')
    zipfp = zipfile.ZipFile(zipfn, 'r')
    shpfn = None
    for name in zipfp.namelist():
        print('    Extracting %s' % (name,))
        o = open(name, 'wb')
        o.write(zipfp.read(name))
        o.close()
        if name[-3:] == 'shp':
            shpfn = name

    print('Processing')
    # Now we are ready to dance!
    f = ogr.Open(shpfn)
    lyr = f.GetLayer(0)

    ugcs = {}
    GEO_TYP = 'Z'
    feat = lyr.GetNextFeature()
    countnoop = 0
    countnew = 0
    while feat is not None:
        if zipfn[:2] in ('mz', 'oz', 'hz'):
            state = ""
            name = feat.GetField("NAME")
            cwa = feat.GetField('WFO')
            ugc = feat.GetField("ID")
            zone = ugc[-3:]
        else:
            state = feat.GetField('STATE')
            zone = feat.GetField('ZONE')
            cwa = feat.GetField('CWA')
            name = feat.GetField('NAME')
            ugc = "%s%s%s" % (state, GEO_TYP, zone)
        if state is None or zone is None:
            print(("Nulls: State [%s] Zone [%s] Name [%s]"
                   ) % (state, zone, name))
            feat = lyr.GetNextFeature()
            continue

        geo = feat.GetGeometryRef()
        if not geo:
            feat = lyr.GetNextFeature()
            continue
        area = Area(geo)

        # This is tricky. We want to have our multipolygon have its
        # biggest polygon first in the multipolygon.
        # This will allow some plotting simplification
        # later as we will only consider the first polygon
        thismaxa = 0
        idx = []
        for i in range(geo.GetGeometryCount()):
            _g = geo.GetGeometryRef(i)
            if Area(_g) > thismaxa:
                thismaxa = Area(_g)
                idx.insert(0, i)
            else:
                idx.append(i)

        newgeo = ogr.Geometry(ogr.wkbMultiPolygon)
        for i in idx:
            _g = geo.GetGeometryRef(i)
            if _g.GetGeometryName() == "LINEARRING":
                _n = ogr.Geometry(ogr.wkbPolygon)
                _n.AddGeometry(_g)
                _g = _n
            newgeo.AddGeometry(_g)

        wkt = newgeo.ExportToWkt()

        if ugc in ugcs:
            if area < ugcs[ugc]:
                print(('Skipping %s [area: %.5f], since we had a previously '
                       'bigger one') % (ugc, area))
                feat = lyr.GetNextFeature()
                continue
        ugcs[ugc] = area

        if wkt.find("EMPTY") > 0:
            print(('UGC: %s resulted in empty multipolygon, listing polygons'
                   ) % (ugc,))
            for i in range(geo.GetGeometryCount()):
                _g = geo.GetGeometryRef(i)
                print("%s %s %s" % (i, _g.GetGeometryName(), Area(_g)))
            sys.exit()

        # OK, lets see if this UGC is new
        cursor.execute("""SELECT ugc from ugcs where ugc = %s
            and end_ts is null and name = %s and
            geom = ST_Multi(ST_SetSRID(ST_GeomFromEWKT(%s),4326)) and
            wfo = %s
            """, (ugc, name, wkt, cwa))

        # NOOP
        if cursor.rowcount == 1:
            countnoop += 1
            feat = lyr.GetNextFeature()
            continue

        # Go find the previous geom and truncate the time
        cursor.execute("""
            UPDATE ugcs SET end_ts = %s WHERE ugc = %s and end_ts is null
            """, (TS, ugc))

        # Finally, insert the new geometry
        cursor.execute("""
        INSERT into ugcs (ugc, name, state, begin_ts, wfo, geom)
        VALUES (%s, %s, %s, %s, %s,
        ST_Multi(ST_SetSRID(ST_GeomFromEWKT(%s),4326)))
        """, (ugc, name, state, TS, cwa, wkt))
        countnew += 1
        feat = lyr.GetNextFeature()

    print('NOOP: %s NEW: %s' % (countnoop, countnew))

    cursor.execute("""UPDATE ugcs SET simple_geom = ST_Simplify(geom, 0.01)""")
    cursor.execute("""UPDATE ugcs SET centroid = ST_Centroid(geom)""")

    cursor.execute("""
     update ugcs SET geom = st_makevalid(geom) where end_ts is null
     and not st_isvalid(geom)
    """)
    print("    Fixed %s entries that were ST_Invalid()" % (cursor.rowcount, ))

    cursor.close()
    pgconn.commit()
    pgconn.close()
    print('Done!')


if __name__ == '__main__':
    main(sys.argv)
