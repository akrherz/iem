#!/usr/bin/env python
"""Generate a 'Live' webcam image on demand

URIs look like so:
    /current/live.py?id=KCRG-006
    /current/live/KCRG-006.jpg
"""
import cgi
from io import BytesIO
import traceback
import datetime

import memcache
from PIL import Image, ImageDraw
import requests
from requests.auth import HTTPDigestAuth
from pyiem.util import get_properties, get_dbconn, ssw


def fetch(cid):
    """Do work to get the content"""
    # Get camera metadata
    pgconn = get_dbconn('mesosite')
    cursor = pgconn.cursor()
    cursor.execute("""
        SELECT ip, fqdn, online, name, port, is_vapix, scrape_url, network
        from webcams WHERE id = %s
        """, (cid,))
    if cursor.rowcount != 1:
        return
    (ip, fqdn, online, name, port, is_vapix, scrape_url, network
     ) = cursor.fetchone()
    pgconn.close()
    if scrape_url is not None or not online:
        return
    # Get IEM properties
    iemprops = get_properties()
    user = iemprops.get('webcam.%s.user' % (network.lower(),))
    passwd = iemprops.get('webcam.%s.pass' % (network.lower(),))
    # Construct URI
    uribase = "http://%s:%s/-wvhttp-01-/GetOneShot"
    if is_vapix:
        uribase = "http://%s:%s/axis-cgi/jpg/image.cgi"
    uri = uribase % (ip if ip is not None else fqdn, port)
    req = requests.get(uri, auth=HTTPDigestAuth(user, passwd), timeout=15)
    if req.status_code != 200:
        return
    image = Image.open(BytesIO(req.content))
    (width, height) = image.size
    # Draw black box
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, height - 12, width, height], fill="#000000")
    stamp = datetime.datetime.now().strftime("%d %b %Y %I:%M:%S %P")
    title = "%s - %s Webcam Live Image at %s" % (name, network, stamp)
    draw.text((5, height - 12), title)
    buf = BytesIO()
    image.save(buf, format='JPEG')
    return buf.getvalue()


def workflow(cid):
    """The necessary workflow for this camera ID"""
    mckey = "/current/live/%s.jpg" % (cid,)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(mckey)
    if res:
        return res
    try:
        res = fetch(cid)
    except Exception as _exp:  # noqa
        return None
    if res is not None:
        # Set for 15 seconds
        mc.set(mckey, res, 15)
    return res


def main():
    """Do Fun Things"""
    form = cgi.FieldStorage()
    cid = form.getfirst('id', 'KCCI-016')[:10]  # Default to ISU Ames
    imagedata = workflow(cid)
    if imagedata is None:
        # TOOD: make a sorry image
        image = Image.new('RGB', (640, 480))
        draw = ImageDraw.Draw(image)
        draw.text((320, 240), 'Sorry, failed to generate image :(')
        buf = BytesIO()
        image.save(buf, format='JPEG')
        imagedata = buf.getvalue()

    ssw("Content-type: image/jpeg\n\n")
    ssw(imagedata)


if __name__ == '__main__':
    try:
        main()
    except Exception as exp:  # noqa
        traceback.print_exc()
