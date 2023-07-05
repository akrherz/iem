"""Convert a NWS Text Product into a PNG

    /wx/afos/201612141916_ADMNFD.png
    Rewritten by apache to text2png?e=201612141916&pil=ADMNFD
"""
import datetime
from io import BytesIO

import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageOps
import pytz
from paste.request import parse_formvars
from pyiem.util import get_dbconn
from pymemcache.client import Client


def pt2px(pt):
    """Crude point to pixel work"""
    return int(round(pt * 96.0 / 72))


def text_image(content):
    """
    http://stackoverflow.com/questions/29760402
    """
    grayscale = "L"
    content = content.replace("\r", "").replace("\001", "")
    lines = content.split("\n")
    if len(lines) > 100:
        msg = f"...truncated {len(lines) - 100} lines..."
        lines = lines[:100]
        lines.append(msg)

    large_font = 20
    font_path = "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf"
    font = PIL.ImageFont.truetype(font_path, size=large_font)

    # make the background image based on the combination of font and lines
    max_width_line = max(lines, key=font.getlength)
    # max height is adjusted down because it's too large visually for spacing
    test_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    bbox = font.getbbox(test_string)
    max_height = bbox[3] - bbox[1]
    max_width = font.getlength(max_width_line)
    height = max_height * len(lines)  # perfect or a little oversized
    width = int(round(max_width + 40))  # a little oversized
    # A limit of PIL
    if (height * width) > 90_000_000:
        width, height = 1200, 1000
    image = PIL.Image.new(grayscale, (width, height), color=255)
    draw = PIL.ImageDraw.Draw(image)

    # draw each line of text
    vertical_position = 5
    horizontal_position = 5
    line_spacing = max_height + 2
    for line in lines:
        draw.text(
            (horizontal_position, vertical_position), line, fill=0, font=font
        )
        vertical_position += line_spacing
    # crop the text
    c_box = PIL.ImageOps.invert(image).getbbox()
    image = image.crop(c_box)
    buf = BytesIO()
    PIL.ImageOps.expand(image, border=5, fill="white").save(buf, format="PNG")
    return buf.getvalue()


def make_image(e, pil):
    """Do as I say"""
    pgconn = get_dbconn("afos")
    cursor = pgconn.cursor()
    valid = datetime.datetime.strptime(e, "%Y%m%d%H%M")
    valid = valid.replace(tzinfo=pytz.UTC)

    cursor.execute(
        "SELECT data from products WHERE pil = %s and entered = %s",
        (pil, valid),
    )
    content = ""
    if cursor.rowcount > 0:
        content = cursor.fetchone()[0]
    return text_image(content)


def application(environ, start_response):
    """Go Main Go"""
    form = parse_formvars(environ)
    e = form.get("e", "201612141916")[:12]
    pil = form.get("pil", "ADMNFD")[:6].replace(" ", "")
    key = f"{e}_{pil}.png"
    mc = Client("iem-memcached:11211")
    res = mc.get(key)
    if not res:
        res = make_image(e, pil)
        mc.set(key, res, 3600)
    mc.close()
    start_response("200 OK", [("Content-type", "image/png")])
    return [res]
