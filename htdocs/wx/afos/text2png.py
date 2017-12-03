#!/usr/bin/env python
"""Convert a NWS Text Product into a PNG

    /wx/afos/201612141916_ADMNFD.png
    Rewritten by apache to text2png?e=201612141916&pil=ADMNFD
"""
import cgi
import sys
import datetime

import memcache
import pytz
from pyiem.util import get_dbconn


def pt2px(pt):
    """Crude point to pixel work"""
    return int(round(pt * 96.0 / 72))


def text_image(content):
    """
    http://stackoverflow.com/questions/29760402
    """
    import PIL.ImageFont
    import PIL.ImageDraw
    import PIL.ImageOps
    import cStringIO
    grayscale = 'L'
    content = content.replace("\r\r\n", "\n").replace("\001", "")
    lines = content.split("\n")

    large_font = 20
    font_path = "/usr/share/fonts/liberation/LiberationMono-Regular.ttf"
    font = PIL.ImageFont.truetype(font_path, size=large_font)

    # make the background image based on the combination of font and lines
    max_width_line = max(lines, key=lambda s: font.getsize(s)[0])
    # max height is adjusted down because it's too large visually for spacing
    test_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    max_height = pt2px(font.getsize(test_string)[1])
    max_width = pt2px(font.getsize(max_width_line)[0])
    height = max_height * len(lines)  # perfect or a little oversized
    width = int(round(max_width + 40))  # a little oversized
    image = PIL.Image.new(grayscale, (width, height), color=255)
    draw = PIL.ImageDraw.Draw(image)

    # draw each line of text
    vertical_position = 5
    horizontal_position = 5
    line_spacing = int(round(max_height * 0.8))  # reduced spacing seems better
    for line in lines:
        draw.text((horizontal_position, vertical_position),
                  line, fill=0, font=font)
        vertical_position += line_spacing
    # crop the text
    c_box = PIL.ImageOps.invert(image).getbbox()
    image = image.crop(c_box)
    buf = cStringIO.StringIO()
    image.save(buf, format='PNG')
    return buf.getvalue()


def make_image(e, pil):
    """Do as I say"""
    pgconn = get_dbconn('afos', user='nobody')
    cursor = pgconn.cursor()
    valid = datetime.datetime.strptime(e, '%Y%m%d%H%M')
    valid = valid.replace(tzinfo=pytz.utc)

    cursor.execute("""
        SELECT data from products WHERE pil = %s and entered = %s
    """, (pil, valid))
    content = ""
    if cursor.rowcount > 0:
        content = cursor.fetchone()[0]
    return text_image(content)


def main():
    form = cgi.FieldStorage()
    e = form.getfirst('e', '201612141916')[:12]
    pil = form.getfirst('pil', 'ADMNFD')[:6].replace(" ", "")
    key = "%s_%s.png" % (e, pil)
    mc = memcache.Client(['iem-memcached:11211'], debug=0)
    res = mc.get(key)
    if not res:
        res = make_image(e, pil)
        mc.set(key, res, 3600)
    sys.stdout.write("Content-type: image/png\n\n")
    sys.stdout.write(res)


if __name__ == '__main__':
    main()
