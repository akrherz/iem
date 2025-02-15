"""mod-wsgi service."""

import os

from pyiem.database import get_sqlalchemy_conn
from sqlalchemy import text

# https://github.com/akrherz/tilecache
from TileCache import InvalidTMSRequest
from TileCache.Service import Service, wsgiHandler

tilecachepath, wsgi_file = os.path.split(__file__)
cfgfiles = os.path.join(tilecachepath, "tilecache.cfg")
theService = {"app": None}


def application(environ, start_response):
    """Go service."""
    if not theService["app"]:
        theService["app"] = Service.load(cfgfiles)
    try:
        return wsgiHandler(environ, start_response, theService["app"])
    except InvalidTMSRequest:
        with get_sqlalchemy_conn("mesosite") as conn:
            conn.execute(
                text("""
                insert into weblog(client_addr, uri, referer, http_status,
                x_forwarded_for)
                VALUES (:addr, :uri, :ref, :status, :for)
                """),
                {
                    "addr": environ.get(
                        "HTTP_X_FORWARDED_FOR", environ.get("REMOTE_ADDR")
                    )
                    .split(",")[0]
                    .strip(),
                    "uri": environ.get("PATH_INFO"),
                    "ref": environ.get("HTTP_REFERER"),
                    "status": 404,
                    "for": environ.get("HTTP_X_FORWARDED_FOR"),
                },
            )
            conn.commit()
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Invalid TMS request"]
