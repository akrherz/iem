"""placeholder for future work."""

from pyiem.webutil import iemapp


@iemapp()
def application(environ, start_response):
    """dev."""
    # We'd want to enforce that this works, so we are getting called rightly
    try:
        (_, _, network, station, _) = environ["SCRIPT_URL"].split("/")
    except Exception:
        network = "IA_ASOS"
        station = "DSM"
    start_response("200 OK", [("Content-Type", "text/html")])
    return [f"Hello World {network} {station}".encode("ascii")]
