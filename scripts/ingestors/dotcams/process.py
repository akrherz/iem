"""
 Need something to make sense of a bunch of downloaded images....
 Vid-000512014-00-03-2009-12-17-17-42.jpg
           Site Identifier
               CameraID (may have more than one camera in the future)
                  ViewID
                     GMT Timestamp....
"""
import sys
FTP_PASS = None
if FTP_PASS is None:
    print "FIX PASSWORD!"
    sys.exit()

import os, mx.DateTime, glob, re
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype('veramono.ttf', 10)
import subprocess
import iemdb
import mesonet
import psycopg2.extras
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor(cursor_factory=psycopg2.extras.DictCursor)
gmt = mx.DateTime.gmt()

# we work from here
os.chdir("/mesonet/data/dotcams")

# Every three hours, clean up after ourselves :)
if gmt.hour % 3 == 0 and gmt.minute < 5:
    os.system("/usr/sbin/tmpwatch 6 165.206.203.34/rwis_images")

# Make dictionary of webcams we are interested in
cameras = {}
mcursor.execute("SELECT * from webcams WHERE network = 'IDOT'")
for row in mcursor:
  cameras[ row['id'] ] = row


p = subprocess.Popen("wget --timeout=20 -m --ftp-user=rwis --ftp-password=%s \
           ftp://165.206.203.34/rwis_images/*%s-??.jpg" % (FTP_PASS,
           gmt.strftime("%d-%H")), shell=True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
stdout, stderr = p.communicate()
lines = stderr.split("\n")
for line in lines:
    # Look for RETR (.*)
    tokens = re.findall("RETR Vid-000512([0-9]{3})-([0-9][0-9])-([0-9][0-9])-([0-9]{4})-([0-9][0-9])-([0-9][0-9])-([0-9][0-9])-([0-9][0-9]).jpg", line)
    if len(tokens) == 0:
        continue

    t = tokens[0]
    cid = "IDOT-%s-%s" % (t[0], t[2])
    gmt = mx.DateTime.DateTime( int(t[3]), int(t[4]), int(t[5]),
                             int(t[6]), int(t[7]) )
    now = gmt.localtime()
    if not cameras.has_key(cid):
        print "Unknown CameraID: %s" % (cid,)
        cameras[ cid ] = {'pan0': 0, 'name': 'unknown'}

    # Hard coded...
    d = cameras[ cid ]
    drct = d['pan0']
    drctTxt = mesonet.drct2dirTxt( drct )

    # Create 320x240 variant
    fp = "165.206.203.34/rwis_images/Vid-000512%s.jpg" % ("-".join(t),)
    try:
        i0 = Image.open( fp )
        i320 = i0.resize((320, 240), Image.ANTIALIAS)
    except:
        print "ERROR: ", fp
        os.unlink( fp )
        continue

    draw = ImageDraw.Draw(i0)
    str = "(%s) %s %s" % (drctTxt, d['name'], now.strftime("%-2I:%M:%S %p - %d %b %Y") )
    (w, h) = font.getsize(str)
    draw.rectangle( [5,475-h,5+w,475], fill="#000000" )
    draw.text((5,475-h), str, font=font)
  
    # Save 640x480
    i0.save("%s-640x480.jpg" % (cid,) )
  
    draw = ImageDraw.Draw(i320)
    str = "(%s) %s %s" % (drctTxt, d['name'], now.strftime("%-2I:%M:%S %p - %d %b %Y") )
    (w, h) = font.getsize(str)
    draw.rectangle( [5,235-h,5+w,235], fill="#000000" )
    draw.text((5,235-h), str, font=font)
  
    # Save 640x480
    i320.save("%s-320x240.jpg" % (cid,) )
    del(i0)
    del(i320)

    # Insert into LDM
    cmd = "/home/ldm/bin/pqinsert -p 'webcam c %s camera/stills/%s.jpg camera/%s/%s_%s.jpg jpg' %s-320x240.jpg" % (gmt.strftime("%Y%m%d%H%M"), cid, cid, cid, gmt.strftime("%Y%m%d%H%M"), cid)
    print cmd
    subprocess.call(cmd, shell=True)
    cmd = "/home/ldm/bin/pqinsert -p 'webcam ac %s camera/640x480/%s.jpg camera/%s/%s_%s.jpg jpg' %s-640x480.jpg" % (gmt.strftime("%Y%m%d%H%M"), cid, cid, cid, gmt.strftime("%Y%m%d%H%M"), cid )
    subprocess.call(cmd, shell=True)
    
    
    # Insert into webcam log please
    sql = """INSERT into camera_log (cam, valid, drct) VALUES 
             ('%s', '%s', %s)""" % (cid, now.strftime("%Y-%m-%d %H:%M"),
             drct)
    mcursor.execute( sql )
    
    sql = "DELETE from camera_current WHERE cam = '%s'" % (cid,)
    mcursor.execute(sql)
    
    sql = """INSERT into camera_current(cam, valid, drct) values ('%s','%s',%s)
    """ % (cid, now.strftime('%Y-%m-%d %H:%M'), drct)
    mcursor.execute(sql)
  
mcursor.close()
MESOSITE.commit()
MESOSITE.close()

