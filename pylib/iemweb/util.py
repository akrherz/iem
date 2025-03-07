"""iemweb utility functions."""

from datetime import datetime

from pyiem.database import get_sqlalchemy_conn, sql_helper
from TileCache import InvalidTMSRequest
from TileCache.Service import wsgiHandler


def tms_handler(environ: dict, start_response: callable, service: dict):
    """Handler for TMS requests and subsequent failures."""
    try:
        return wsgiHandler(environ, start_response, service)
    except InvalidTMSRequest:
        with get_sqlalchemy_conn("mesosite") as conn:
            conn.execute(
                sql_helper("""
                insert into weblog(client_addr, uri, referer, http_status,
                x_forwarded_for, domain)
                VALUES (:addr, :uri, :ref, :status, :for, :domain)
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
                    "domain": environ.get("HTTP_HOST"),
                },
            )
            conn.commit()
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Invalid TMS request"]


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
