"""Handle Apache proxy errors."""

from http.client import responses as HTTP_RESPONSES

from pyiem.util import utc
from pyiem.webutil import TELEMETRY, error_log, write_telemetry


def application(environ, start_response):
    """Handle Apache proxy errors."""
    status_code = int(environ.get("REDIRECT_STATUS", 200))
    error_log(environ, f"{status_code} {environ.get('REQUEST_URI')}")
    ip = environ.get("REMOTE_ADDR")
    write_telemetry(
        TELEMETRY(
            timing=0,
            status_code=status_code,
            client_addr=ip,
            app=environ.get("REDIRECT_SCRIPT_URL"),
            request_uri=environ.get("REQUEST_URI"),
            vhost=environ.get("HTTP_HOST"),
            valid=utc(),
        )
    )

    status = f"{status_code} {HTTP_RESPONSES.get(status_code, 'Unknown')}"
    headers = [("Content-type", "text/plain")]
    start_response(status, headers)
    return [b"An error occurred, please try again later."]
