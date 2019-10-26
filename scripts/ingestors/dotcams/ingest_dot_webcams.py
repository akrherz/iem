"""
 Need something to make sense of a bunch of downloaded images....
 Vid-000512014-00-03-2009-12-17-17-42.jpg
           Site Identifier
               CameraID (may have more than one camera in the future)
                  ViewID
                     GMT Timestamp....
"""
from __future__ import print_function

# stdlib
import os
import datetime
import re
import subprocess

# third party
from PIL import Image, ImageDraw, ImageFont
import psycopg2.extras
import pytz
import pyiem.util as util

FONT = ImageFont.truetype("veramono.ttf", 10)


def do_imagework(cameras, cid, tokens, now):
    """Process the images"""
    # Hard coded...
    drct = cameras[cid]["pan0"]
    drct_text = util.drct2text(drct)

    # Create 320x240 variant
    fn = "165.206.203.34/rwis_images/Vid-000512%s.jpg" % ("-".join(tokens),)
    try:
        i0 = Image.open(fn)
        i320 = i0.resize((320, 240), Image.ANTIALIAS)
    except Exception:
        if os.path.isfile(fn):
            os.unlink(fn)
        return

    draw = ImageDraw.Draw(i0)
    text = "(%s) %s %s" % (
        drct_text,
        cameras[cid]["name"],
        now.strftime("%-2I:%M:%S %p - %d %b %Y"),
    )
    (width, height) = FONT.getsize(text)
    draw.rectangle([5, 475 - height, 5 + width, 475], fill="#000000")
    draw.text((5, 475 - height), text, font=FONT)

    # Save 640x480
    i0.save("%s-640x480.jpg" % (cid,))

    draw = ImageDraw.Draw(i320)
    text = "(%s) %s %s" % (
        drct_text,
        cameras[cid]["name"],
        now.strftime("%-2I:%M:%S %p - %d %b %Y"),
    )
    (width, height) = FONT.getsize(text)
    draw.rectangle([5, 235 - height, 5 + width, 235], fill="#000000")
    draw.text((5, 235 - height), text, font=FONT)

    # Save 640x480
    i320.save("%s-320x240.jpg" % (cid,))
    del i0
    del i320
    return drct


def process(tokens, cameras, mcursor):
    """Process this line from what we downloaded"""
    cid = "IDOT-%s-%s" % (tokens[0], tokens[2])
    gmt = datetime.datetime(
        int(tokens[3]), int(tokens[4]), int(tokens[5]), int(tokens[6]), int(tokens[7])
    )
    gmt = gmt.replace(tzinfo=pytz.utc)
    now = gmt.astimezone(pytz.timezone("America/Chicago"))
    if cid not in cameras:
        print("ingest_dot_webcams.py unknown CameraID: %s" % (cid,))
        cameras[cid] = {"pan0": 0, "name": "unknown"}

    drct = do_imagework(cameras, cid, tokens, now)
    if drct is None:
        return
    # Insert into LDM
    cmd = (
        "/home/ldm/bin/pqinsert -p 'webcam c %s camera/stills/%s.jpg "
        "camera/%s/%s_%s.jpg jpg' %s-320x240.jpg"
        ""
    ) % (gmt.strftime("%Y%m%d%H%M"), cid, cid, cid, gmt.strftime("%Y%m%d%H%M"), cid)
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    proc.communicate()

    cmd = (
        "/home/ldm/bin/pqinsert -p 'webcam ac %s camera/640x480/%s.jpg "
        "camera/%s/%s_%s.jpg jpg' %s-640x480.jpg"
        ""
    ) % (gmt.strftime("%Y%m%d%H%M"), cid, cid, cid, gmt.strftime("%Y%m%d%H%M"), cid)
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    proc.communicate()

    # Insert into webcam log please
    sql = """INSERT into camera_log (cam, valid, drct) VALUES
             (%s, %s, %s)"""
    args = (cid, now, drct)
    mcursor.execute(sql, args)

    mcursor.execute(
        """
        UPDATE camera_current SET valid = %s, drct = %s WHERE cam = %s
    """,
        (now, drct, cid),
    )
    if mcursor.rowcount == 0:
        print(("ingest_dot_webcams adding camera_current entry for cam: %s") % (cid,))
        mcursor.execute(
            """
            INSERT into camera_current(cam, valid, drct) values (%s,%s,%s)
        """,
            (cid, now, drct),
        )


def main():
    """Go Main Go"""
    pgconn = util.get_dbconn("mesosite")
    mcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    props = util.get_properties()
    ftp_pass = props["rwis_ftp_password"]
    utc = datetime.datetime.utcnow()

    # we work from here
    os.chdir("/mesonet/data/dotcams")

    # Every three hours, clean up after ourselves :)
    if utc.hour % 3 == 0 and utc.minute < 5:
        subprocess.call("/usr/sbin/tmpwatch 6 165.206.203.34/rwis_images", shell=True)

    # Make dictionary of webcams we are interested in
    cameras = {}
    mcursor.execute("SELECT * from webcams WHERE network = 'IDOT'")
    for row in mcursor:
        cameras[row["id"]] = row

    proc = subprocess.Popen(
        (
            "wget --timeout=20 -m --ftp-user=rwis "
            "--ftp-password=%s "
            "ftp://165.206.203.34/rwis_images/*.jpg"
        )
        % (ftp_pass,),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _stdout, stderr = proc.communicate()
    stderr = stderr.decode("utf-8")
    lines = stderr.split("\n")
    for line in lines:
        # Look for RETR (.*)
        tokens = re.findall(
            (
                "RETR Vid-000512([0-9]{3})-([0-9][0-9])-([0-9][0-9])"
                "-([0-9]{4})-([0-9][0-9])-([0-9][0-9])-([0-9][0-9])-"
                "([0-9][0-9]).jpg"
            ),
            line,
        )
        if not tokens:
            continue
        process(tokens[0], cameras, mcursor)

    mcursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
