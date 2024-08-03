""".. title:: Autoplot Meta Data

This service is used internally by IEM autoplotting to drive the user
interface.

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import FIGSIZES_NAMES
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

from iemweb.autoplot import data as autoplot_data
from iemweb.autoplot import import_script


class Schema(CGIModel):
    """See how we are called."""

    p: int = Field(default=0, description="The autoplot index", ge=0, le=1000)


def get_timing(pidx: int) -> float:
    """Return an average plot generation time for this app"""
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(
            text(
                "SELECT avg(timing) from autoplot_timing where appid = :id "
                "and valid > (now() - '7 days'::interval)"
            ),
            {"id": pidx},
        )
        timing = res.fetchone()[0]
    return timing if timing is not None else -1


def do_json(pidx):
    """Do what needs to be done for JSON requests."""
    status = "200 OK"
    if pidx == 0:
        data = autoplot_data
    else:
        try:
            timing = get_timing(pidx)
        except Exception:
            timing = -1
        mod = import_script(pidx)
        data = mod.get_description()
        defaults = data.pop("defaults", {"_r": "t", "dpi": "100"})
        data["maptable"] = hasattr(mod, "geojson")
        data["highcharts"] = hasattr(mod, "get_highcharts")
        data["timing[secs]"] = timing

        # Setting to None disables
        if "_r" not in defaults or defaults["_r"] is not None:
            data["arguments"].append(
                dict(
                    type="select",
                    options=FIGSIZES_NAMES,
                    name="_r",
                    default=defaults.get("_r", "t"),
                    label="Image Pixel Size @100 DPI",
                )
            )
        data["arguments"].append(
            dict(
                type="int",
                name="dpi",
                default=defaults.get("dpi", "100"),
                label="Image Resolution (DPI) (50 to 500)",
            )
        )
    output = json.dumps(data)

    response_headers = [("Content-type", "application/json")]
    return output, status, response_headers


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey=lambda x: f"/autoplot/meta?p={x['p']}",
    memcacheexpire=300,
)
def application(environ, start_response):
    """Our Application!"""
    pidx = environ["p"]
    output, status, response_headers = do_json(pidx)

    start_response(status, response_headers)
    # json.dumps returns str, we need bytes here
    return output.encode()
