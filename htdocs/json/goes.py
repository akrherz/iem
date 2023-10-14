"""
Return JSON metadata for GOES Imagery
"""
import datetime
import glob
import json
import os

from pyiem.util import html_escape
from pyiem.webutil import iemapp

BIRDS = ["EAST", "WEST"]
PRODUCTS = ["WV", "VIS", "IR"]


def parse_time(text):
    """
    Convert ISO something into a datetime
    """
    try:
        if len(text) == 17:
            date = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%MZ")
        elif len(text) == 20:
            date = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
        else:
            date = datetime.datetime.utcnow()
    except Exception:
        date = datetime.datetime.utcnow()
    return date


def find_scans(root, bird, product, start_gts, end_gts):
    """Find GOES SCANs"""
    if bird not in BIRDS or product not in PRODUCTS:
        return
    now = start_gts.replace(hour=0, minute=0, second=0)
    while now < end_gts:
        mydir = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/sat/awips211")
        if os.path.isdir(mydir):
            os.chdir(mydir)
            filenames = glob.glob(f"GOES_{bird}_{product}_*.wld")
            filenames.sort()
            for filename in filenames:
                ts = datetime.datetime.strptime(
                    filename[:-4].split("_")[3], "%Y%m%d%H%M"
                )
                if ts >= start_gts and ts <= end_gts:
                    root["scans"].append(ts.strftime("%Y-%m-%dT%H:%M:00Z"))
        now += datetime.timedelta(hours=24)


def list_files(fields):
    """
    List available GOES files based on the form request
    """
    bird = fields.get("bird", "EAST").upper()
    product = fields.get("product", "VIS").upper()

    # default to a four hour period
    utc0 = datetime.datetime.utcnow()
    utc1 = utc0 - datetime.timedelta(hours=4)

    start_gts = parse_time(
        fields.get("start", utc1.strftime("%Y-%m-%dT%H:%MZ"))
    )
    end_gts = parse_time(fields.get("end", utc0.strftime("%Y-%m-%dT%H:%MZ")))
    root = {"scans": []}
    find_scans(root, bird, product, start_gts, end_gts)

    return root


@iemapp()
def application(environ, start_response):
    """Answer request."""
    operation = environ.get("operation", "list")
    callback = environ.get("callback")
    headers = []
    data = ""
    if callback is not None:
        data = f"{html_escape(callback)}("
    if operation == "list":
        data += json.dumps(list_files(environ))
    if callback is not None:
        data += ")"
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
