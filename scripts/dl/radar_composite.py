"""
 Cache NEXRAD composites for the website
"""
import urllib2
import os
import subprocess
import datetime
import time
import sys
import psycopg2
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

TMPFN = '/tmp/radar_composite_tmp.png'
opener = urllib2.build_opener()


def save(sectorName, file_name, dir_name, tstamp, bbox=None, routes='ac'):
    ''' Get an image and write it back to LDM for archiving '''
    layers = ("layers[]=n0q&layers[]=watch_by_county&layers[]=sbw&"
              "layers[]=uscounties")
    if sectorName == 'conus':
        layers = "layers[]=n0q&layers[]=watch_by_county&layers[]=uscounties"
    uri = "http://iem.local/GIS/radmap.php?sector=%s&ts=%s&%s" % (
                                            sectorName,tstamp, layers)
    if bbox is not None:
        uri = "http://iem.local/GIS/radmap.php?bbox=%s&ts=%s&%s" % (
                                            bbox,tstamp, layers)
    try:
        f = opener.open(uri)
    except:
        time.sleep(5)
        f = opener.open(uri)

    o = open(TMPFN, 'w')
    o.write( f.read() )
    o.close()

    cmd = ("/home/ldm/bin/pqinsert -p 'plot %s %s %s %s/n0r_%s_%s.png "
           +"png' %s") % (routes, tstamp, file_name, dir_name, tstamp[:8], 
                          tstamp[8:], TMPFN)
    subprocess.call(cmd, shell=True)

    os.unlink(TMPFN)


def runtime(ts):
    ''' Actually run for a time '''
    sts = ts.strftime("%Y%m%d%H%M")

    save('conus', 'uscomp.png', 'usrad', sts)
    save('iem', 'mwcomp.png', 'comprad', sts)
    for i in ['lot', 'ict', 'sd', 'hun']:
        save(i, '%scomp.png'%(i,), '%srad' %(i,), sts)

    # Now, we query for watches.
    pcursor.execute("""select sel, ST_xmax(geom), ST_xmin(geom), 
        ST_ymax(geom), ST_ymin(geom) from watches_current 
        ORDER by issued DESC""")
    for row in pcursor:
        xmin = float(row[2]) - 0.75 
        ymin = float(row[4]) - 0.75 
        xmax = float(row[1]) + 0.75 
        ymax = float(row[3]) + 1.5 
        bbox = "%s,%s,%s,%s" % (xmin,ymin,xmax,ymax)
        sel = row[0].lower()
        save('custom', '%scomp.png'%(sel,), '%srad'% (sel,), sts, bbox)

if __name__ == '__main__':
    ''' Go main go'''
    ts = datetime.datetime.utcnow()
    if len(sys.argv) == 6:
        ts = datetime.datetime( int(sys.argv[1]), int(sys.argv[2]),
            int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]) )
    runtime(ts)