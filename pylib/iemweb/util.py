"""iemweb utility functions."""

from datetime import datetime

from TileCache import InvalidTMSRequest
from TileCache.Service import wsgiHandler

from iemweb import error_log


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
    if month in ["all", "water_year"]:
        months = list(range(1, 13))
    elif month == "fall":
        months = [9, 10, 11]
    elif month == "winter":
        months = [12, 1, 2]
    elif month == "octmar":
        months = [10, 11, 12, 1, 2, 3]
    elif month == "spring":
        months = [3, 4, 5]
    elif month == "spring2":
        months = [4, 5, 6]
    elif month == "summer":
        months = [6, 7, 8]
    elif month == "gs":
        months = [5, 6, 7, 8, 9]
    elif month == "mjj":
        months = [5, 6, 7]
    else:
        fmt = "%b" if len(month) == 3 else "%m"
        months = [datetime.strptime(f"2000-{month}-01", f"%Y-{fmt}-%d").month]
    return months
