""".. title:: Autoplot Meta Data

This service is used internally by IEM autoplotting to drive the user
interface.

"""

import importlib
from contextlib import suppress
from types import ModuleType

from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import BadWebRequest
from pyiem.reference import FIGSIZES_NAMES

from iemweb.autoplot import data as autoplot_data
from iemweb.autoplot.description import describe


def get_timing(pidx: int) -> float:
    """Return an average plot generation time for this app"""
    timing = -1.0
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(
            sql_helper(
                "SELECT avg(timing) from autoplot_timing where appid = :id "
                "and valid > (now() - '7 days'::interval)"
            ),
            {"id": pidx},
        )
        row = res.fetchone()
        if row is not None:
            timing = row[0]
    return timing if timing is not None else -1


def find_title(pidx: int) -> str:
    """Figure out the title of this autoplot, le sigh."""
    for section in autoplot_data["plots"]:
        for option in section["options"]:
            if option["id"] == pidx:
                return option["label"]
    return "Autoplot Title Unset?"


def import_script(p: int) -> ModuleType:
    """Import the script for the given product ID"""
    s = ""
    if p >= 200:
        s = "200"
    elif p >= 100:
        s = "100"
    # We used to reload the module here each time, but in local dev we are
    # cycling the mod_wsgi process every request and in prod, \_o_/
    try:
        return importlib.import_module(f"iemweb.autoplot.scripts{s}.p{p}")
    except ModuleNotFoundError as exp:
        raise BadWebRequest("Invalid autoplot id") from exp


def get_scriptmod_and_meta(pidx: int) -> tuple[ModuleType, dict]:
    """Do what needs to be done for JSON requests."""
    timing = -1
    with suppress(Exception):
        timing = get_timing(pidx)
    mod = import_script(pidx)
    data = describe(mod)
    data["title"] = find_title(pidx)
    defaults = data.pop("defaults", {"_r": "t", "dpi": "100"})
    data["maptable"] = hasattr(mod, "geojson")
    data["highcharts"] = hasattr(mod, "get_highcharts")
    data["raster"] = hasattr(mod, "get_raster")
    data["timing[secs]"] = timing

    # Setting to None disables
    if "_r" not in defaults or defaults["_r"] is not None:
        data["arguments"].append(
            {
                "type": "select",
                "options": FIGSIZES_NAMES,
                "name": "_r",
                "default": defaults.get("_r", "t"),
                "label": "Image Pixel Size @100 DPI",
            }
        )
    data["arguments"].append(
        {
            "type": "int",
            "name": "dpi",
            "default": defaults.get("dpi", "100"),
            "label": "Image Resolution (DPI) (50 to 500)",
        }
    )
    return mod, data
