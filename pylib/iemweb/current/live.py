""".. title:: A Live Webcam Image

This service is a proxy to get a current webcam image.  There is about 15
seconds of caching to keep the remote webcam from getting runover.

Changelog
---------

- 2025-08-28: Implement pydantic validation

"""

from datetime import datetime
from io import BytesIO

import httpx
from PIL import Image, ImageDraw
from pydantic import Field
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.util import LOG, get_properties
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection


class MySchema(CGIModel):
    """See how we are called."""

    id: str = Field(
        "KCCI-027", description="The ID of the webcam", max_length=10
    )


@with_sqlalchemy_conn("mesosite")
def fetch(cid: str, conn: Connection | None = None):
    """Do work to get the content"""
    # Get camera metadata
    res = conn.execute(
        sql_helper("""
    SELECT ip, fqdn, online, name, port, is_vapix, scrape_url, network
    FROM webcams WHERE id = :cid
    """),
        {"cid": cid},
    )
    meta = None
    for row in res.mappings():
        meta = row
    if meta is None:
        return None
    if meta["scrape_url"] is not None or not meta["online"]:
        return None
    # Get IEM properties
    iemprops = get_properties()
    user = iemprops.get(f"webcam.{meta['network'].lower()}.user")
    passwd = iemprops.get(f"webcam.{meta['network'].lower()}.pass")
    # Construct URI
    uribase = "http://%s:%s/-wvhttp-01-/GetOneShot"
    if meta["is_vapix"]:
        uribase = "http://%s:%s/axis-cgi/jpg/image.cgi"
    uri = uribase % (
        meta["ip"] if meta["ip"] is not None else meta["fqdn"],
        meta["port"],
    )
    ham = (
        httpx.BasicAuth
        if cid
        in [
            "KCRG-010",
            "KCCI-027",
        ]
        else httpx.DigestAuth
    )
    try:
        resp = httpx.get(uri, auth=ham(user, passwd), timeout=15)
        resp.raise_for_status()
    except Exception as exp:
        LOG.info("fetch failed: %s %s", uri, exp)
        return None
    image = Image.open(BytesIO(resp.content))
    (width, height) = image.size
    # Draw black box
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, height - 12, width, height], fill="#000000")
    stamp = datetime.now().strftime("%d %b %Y %I:%M:%S %P")
    title = f"{meta['name']} - {meta['network']} Webcam Live Image at {stamp}"
    draw.text((5, height - 12), title)
    buf = BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()


@iemapp(
    content_type="image/jpeg",
    memcachekey=lambda environ: f"/current/live/{environ['id']}.jpg",
    memcacheexpire=15,
    help=__doc__,
    schema=MySchema,
)
def application(environ, start_response):
    """Do Fun Things"""
    imagedata = fetch(environ["id"])
    if imagedata is None:
        image = Image.new("RGB", (640, 480))
        draw = ImageDraw.Draw(image)
        draw.text((320, 240), "Sorry, failed to generate image :(")
        buf = BytesIO()
        image.save(buf, format="JPEG")
        imagedata = buf.getvalue()

    start_response("200 OK", [("Content-type", "image/jpeg")])
    return imagedata
