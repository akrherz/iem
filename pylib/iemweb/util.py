"""iemweb utility functions."""

from TileCache import InvalidTMSRequest
from TileCache.Service import wsgiHandler

from iemweb import error_log

MONTH_LOOKUP = {
    "jan": [1],
    "feb": [2],
    "mar": [3],
    "apr": [4],
    "may": [5],
    "jun": [6],
    "jul": [7],
    "aug": [8],
    "sep": [9],
    "oct": [10],
    "nov": [11],
    "dec": [12],
    "all": list(range(1, 13)),
    "water_year": list(range(1, 13)),
    "fall": [9, 10, 11],
    "winter": [12, 1, 2],
    "octmar": [10, 11, 12, 1, 2, 3],
    "spring": [3, 4, 5],
    "spring2": [4, 5, 6],
    "summer": [6, 7, 8],
    "gs": [5, 6, 7, 8, 9],
    "mjj": [5, 6, 7],
}


def get_ct(environ: dict) -> str:
    """Construct the content type based on our generalized patterns.

    Supported fmt/format values: json, geojson, csv, html, excel, zip.
    For json/geojson with a non-empty callback, return JavaScript for JSONP.
    """
    fmt = environ.get("fmt", environ.get("format", "json"))
    # If JSONP is requested, serve JavaScript
    if fmt in ("json", "geojson") and environ.get("callback"):
        return "application/javascript; charset=utf-8"
    if fmt == "geojson":
        return "application/vnd.geo+json; charset=utf-8"
    if fmt == "json":
        return "application/json; charset=utf-8"
    if fmt == "csv":
        return "text/csv; charset=utf-8"
    if fmt == "html":
        return "text/html"
    if fmt == "excel":
        return "application/vnd.ms-excel"
    if fmt == "zip":
        return "application/octet-stream"
    return "text/plain"


def tms_handler(environ: dict, start_response: callable, service: dict):
    """Handler for TMS requests and subsequent failures."""
    try:
        return wsgiHandler(environ, start_response, service)
    except InvalidTMSRequest:
        # Previously, we would tee these requests up for app firewall
        # now we just log them and send back a customized image
        # indicating that the request was invalid.
        error_log(
            environ,
            f"InvalidTMS  "
            f"'{environ.get('PATH_INFO')}' "
            f"Ref: {environ.get('HTTP_REFERER')}",
        )
        start_response("200 OK", [("Content-Type", "image/png")])
        with open("/opt/iem/htdocs/images/tms_error.png", "rb") as fh:
            return [fh.read()]


def month2months(month: str) -> list[int]:
    """
    Convert a month string to a list of months.

    Args:
        month (str): A month string commonly used by IEM apps

    Returns:
        list: A list of ints (months)
    """
    month = month.lower().strip()
    if month in MONTH_LOOKUP:
        return MONTH_LOOKUP[month]
    return [int(month)]
