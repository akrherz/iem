"""mod-wsgi service."""

from pathlib import Path

from TileCache.Service import Service

from iemweb.util import tms_handler

theService = {"app": None}


def application(environ: dict, start_response: callable):
    """Go service."""
    if not theService["app"]:
        cfgfile = Path(__file__).parent / "tilecache.cfg"
        theService["app"] = Service.load(cfgfile)
    return tms_handler(environ, start_response, theService["app"])
