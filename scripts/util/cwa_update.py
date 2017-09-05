"""Update postgis CWA table

It is unclear that this script is even needed anymore.
"""
from __future__ import print_function
import sys
import os
import urllib2
import zipfile

from osgeo import ogr
from osgeo import _ogr
import psycopg2
POSTGIS = psycopg2.connect(database='postgis', host='iemdb')


def Area(feat, *args):
    """
    Backport a feature from the future!
    """
    return _ogr.Geometry_GetArea(feat, *args)


def main():
    """Go Main!"""
    cursor = POSTGIS.cursor()

    # Get the name of the file we wish to download
    if len(sys.argv) != 2:
        print('ERROR: You need to specify the file date to download ')
        print('Example:  python cwa_update.py w_01ap14a')
        sys.exit(0)

    DATESTAMP = sys.argv[1]

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

    wfos = {}
    feat = lyr.GetNextFeature()
    countnoop = 0
    countnew = 0
    while feat is not None:
        wfo = feat.GetField('WFO')
        cwa = feat.GetField('CWA')

        geo = feat.GetGeometryRef()
        if not geo:
            feat = lyr.GetNextFeature()
            continue
        area = Area(geo)
        wkt = geo.ExportToWkt()

        if wfo in wfos:
            if area < wfos[wfo]:
                print(('Skipping %s [area: %s], since we had a '
                       'previously bigger one') % (wfo, area))
                feat = lyr.GetNextFeature()
                continue
        wfos[wfo] = area

        # OK, lets see if this UGC is new
        cursor.execute("""
            SELECT cwa from cwa where cwa = %s and
            the_geom = ST_Multi(ST_SetSRID(ST_GeomFromEWKT(%s),4326))
            """, (cwa, wkt))

        # NOOP
        if cursor.rowcount == 1:
            countnoop += 1
            feat = lyr.GetNextFeature()
            continue

        # Finally, insert the new geometry
        cursor.execute("""
        UPDATE cwa
        SET the_geom = ST_Multi(ST_SetSRID(ST_GeomFromEWKT(%s),4326))
        WHERE cwa = %s
        """, (wkt, cwa))
        countnew += 1
        feat = lyr.GetNextFeature()

    print('NOOP: %s UPDATED: %s' % (countnoop, countnew))

    cursor.close()
    POSTGIS.commit()
    POSTGIS.close()
    print('Done!')


if __name__ == '__main__':
    main()
