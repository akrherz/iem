"""
  Process the IFC precip data!  Here's the file header
# file name: H99999999_I0007_G_15MAR2013_154000.out
# Rainrate map [mm/hr] 
# number of columns: 1741
# number of rows: 1057
# grid: LATLON 
# upper-left LATLONcorner(x,y): 6924 5409
# xllcorner [lon]: -97.154167
# yllcorner [lat]: 40.133331
# cellsize [dec deg]: 0.004167
# no data value: -99.0

http://s-iihr57.iihr.uiowa.edu/feeds/IFC7ADV/latest.dat
http://s-iihr57.iihr.uiowa.edu/feeds/IFC7ADV/H99999999_I0007_G_15MAR2013_154500.out
"""
BASEURL = "http://s-iihr57.iihr.uiowa.edu/feeds/IFC7ADV"

import datetime
import urllib2
import subprocess
import numpy
import Image
import nmq
import tempfile
import os

def get_file( now ):
    """ Download the file, save to /tmp and return fn """
    fn = now.strftime("H99999999_I0007_G_%d%b%Y_%H%M00").upper()
    uri = "%s/%s.out" % (BASEURL, fn)
    try:
        req = urllib2.Request(uri)
        data = urllib2.urlopen(req).read()
    except:
        #print "Download %s failed" % (uri,)
        return None
    tmpfn = tempfile.mktemp()
    o = open(tmpfn, 'w')
    o.write( data )
    o.close()
    return tmpfn

def to_raster(tmpfn, now):
    """ Convert the raw data into a RASTER Image 
    5 inch rain per hour is ~ 125 mm/hr, so over 5min that is 10 mm
    Index 255 is missing
    0 is zero
    1 is 0.1 mm
    254 is 25.4 mm 
    """
    data = numpy.loadtxt(tmpfn, skiprows=10)
    imgdata = (data * 10.0 / 12.0) # mm/hr to mm/5min
    imgdata = numpy.where(imgdata < 0, 255, imgdata)
    png = Image.fromarray( numpy.uint8(imgdata) )
    png.putpalette( nmq.make_colorramp() )
    png.save('%s.png' % (tmpfn,))
    del png
    # Make worldfile
    o = open("%s.wld" %(tmpfn,), 'w')
    o.write("""0.004167%s
0.00%s
0.00%s
-0.004167%s
44.53785
-89.89942""" % (nmq.random_zeros(), nmq.random_zeros(), nmq.random_zeros(),
                 nmq.random_zeros()))
    o.close()

def ldm(tmpfn, now):
    """ Send stuff to ldm """
    pq = "/home/ldm/bin/pqinsert"
    pqstr = "%s -p 'plot ac %s gis/images/4326/ifc/p05m.wld GIS/ifc/p05m_%s.wld wld' %s.wld" % (
                    pq, now.strftime("%Y%m%d%H%M"), now.strftime("%Y%m%d%H%M"), 
                    tmpfn )
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = "%s -p 'plot ac %s gis/images/4326/ifc/p05m.png GIS/ifc/p05m_%s.png png' %s.png" % (
                    pq, now.strftime("%Y%m%d%H%M"), now.strftime("%Y%m%d%H%M"), 
                    tmpfn )
    subprocess.call(pqstr, shell=True)


def cleanup(tmpfn):
    os.remove(tmpfn)
    for suffix in ['png', 'wld']:
        os.remove("%s.%s" % (tmpfn, suffix))

def do_time( now ):
    # Fetch file
    tmpfn = get_file( now )
    if tmpfn is None:
        return
    
    to_raster(tmpfn, now)

    ldm(tmpfn, now)

    #print 'COMMENT ME OUT!'
    #print tmpfn
    #os.system('xv %s.png' % (tmpfn,))

    cleanup( tmpfn )

def main():
    """ main method """
    now = datetime.datetime.utcnow()
    now = now.replace(second=0,microsecond=0)
    # Round back to the nearest 5 minute, plus 10
    delta = now.minute % 5 + 15
    now = now - datetime.timedelta(minutes=delta)

    do_time( now )
    # Do we need to rerun a previous hour
    now = now - datetime.timedelta(minutes=60)
    fn = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ifc/p05m_%Y%m%d%H%M.png")
    if not os.path.isfile(fn):
        #print "Rerunning %s due to missing file %s" % (now, fn)
        do_time( now )

if __name__ == '__main__':
    main()