"""..title :: Convert a NWS Text Product into a PNG

URLs like so: `/wx/afos/201612141916_ADMNFD.png` are rewritten to this app
like so: `text2png?e=201612141916&pil=ADMNFD`

Changelog
---------

- 2025-06-10: Migration to pydantic validation

Example Requests
----------------

View the Des Moines NWS Area Forecast Discussion as a PNG:

https://mesonet.agron.iastate.edu/wx/afos/text2png.py\
?e=202407100904&pil=AFDDMX

"""

from datetime import datetime, timezone
from io import BytesIO

import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageOps
from pydantic import Field
from pyiem.database import get_dbconn
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """Schema for the CGI app"""

    e: str = Field(
        default="201612141916",
        description="The valid time of the product in YYYYMMDDHHMM format",
        max_length=12,
        min_length=12,
        pattern=r"^[12][90]\d\d[01]\d[0-3]\d[0-2]\d[0-5]\d$",
    )
    pil: str = Field(
        default="ADMNFD",
        description="The AFOS Product Identifier, e.g., ADMNFD",
        max_length=6,
    )


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
    height = (max_height + 2) * len(lines)  # perfect or a little oversized
    width = round(max_width + 40)  # a little oversized
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
    valid = datetime.strptime(e, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)

    cursor.execute(
        "SELECT data from products WHERE pil = %s and entered = %s",
        (pil, valid),
    )
    content = ""
    if cursor.rowcount > 0:
        content = cursor.fetchone()[0]
    pgconn.close()
    return text_image(content)


def get_mckey(environ: dict) -> str:
    """Return the memcached key for this request"""
    e = environ["e"]
    pil = environ["pil"].replace(" ", "")
    return f"text2png_{e}_{pil}.png"


@iemapp(
    schema=Schema,
    help=__doc__,
    memcachekey=get_mckey,
    content_type="image/png",
)
def application(environ: dict, start_response):
    """Go Main Go"""
    e = environ["e"]
    pil = environ["pil"].replace(" ", "")
    res = make_image(e, pil)
    start_response("200 OK", [("Content-type", "image/png")])
    return res
