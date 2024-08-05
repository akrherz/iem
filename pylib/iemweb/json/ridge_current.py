""".. title:: IEM RIDGE Current Metadata

Return to `JSON Services </json/>`_

Documentation for /json/ridge_current.py
----------------------------------------

The IEM processes a number of NWS Level III products into a geo-referenced
PNG format.  This service provides a metadata overview of the most recent
images for a given product.

Example Usage
-------------

Provide the most recent N0B product metadata:

https://mesonet.agron.iastate.edu/json/ridge_current.py?product=N0B

"""

import glob
import json

from pydantic import Field
from pyiem.reference import ISO8601
from pyiem.util import LOG, utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    product: str = Field(
        "N0B", description="Radar product to aggregate", max_length=3
    )


def run(product):
    """Actually run for this product"""

    res = {
        "generation_time_utc": utc().strftime(ISO8601),
        "product": product,
        "meta": [],
    }

    for fn in glob.glob(
        f"/mesonet/ldmdata/gis/images/4326/ridge/???/{product}_0.json"
    ):
        try:
            with open(fn, encoding="utf-8") as fh:
                j = json.load(fh)
            res["meta"].append(j["meta"])
        except Exception as exp:
            LOG.info(exp)

    return json.dumps(res)


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey=lambda x: f"/json/ridge_current_{x['product']}.json",
    memcacheexpire=30,
)
def application(environ, start_response):
    """Answer request."""
    product = environ["product"].upper()

    res = run(product)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res
